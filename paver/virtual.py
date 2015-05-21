"""Tasks for managing virtualenv environments."""
from paver.easy import task, options, dry, debug, BuildFailure
from paver.release import setup_meta

VIRTUALENV_MISSING_ERROR = "`virtualenv` is needed to use paver's virtualenv tasks, please install the package."

try:
    import virtualenv as venv
except ImportError:
    has_virtualenv = False
else:
    has_virtualenv = True

_pip_then_easy_install_tmpl = """
    try:
        subprocess.call(
            [join(%(bin_dir_var)s, 'pip'), 'install']
            + %(cmd_options)r
            + %%(packages)r
        )
    except OSError:
        subprocess.call(
            [join(%(bin_dir_var)s, 'easy_install')]
            + %(cmd_options)r
            + %%(packages)r
        )
"""
_easy_install_tmpl = """
    subprocess.call(
        [join(%(bin_dir_var)s, 'easy_install')]
        + %(cmd_options)r
        + %%(packages)r
    )
"""
def _create_bootstrap(script_name, packages_to_install, paver_command_line,
                      install_paver=True, more_text="", dest_dir='.',
                      no_site_packages=None, system_site_packages=None,
                      unzip_setuptools=False, distribute=None, index_url=None, trusted_host=None,
                      no_index=False, find_links=None, prefer_easy_install=False):
    # configure package installation template
    install_cmd_options = []
    if index_url:
        install_cmd_options.extend(['--index-url', index_url])
    if trusted_host:
        install_cmd_options.extend(['--trusted-host', trusted_host])
    if no_index:
        install_cmd_options.extend(['--no-index'])
    if find_links:
        for link in find_links:
            install_cmd_options.extend(
                ['--find-links', link])
    install_cmd_tmpl = (_easy_install_tmpl if prefer_easy_install
                        else _pip_then_easy_install_tmpl)
    confd_install_cmd_tmpl = (install_cmd_tmpl %
        {'bin_dir_var': 'bin_dir', 'cmd_options': install_cmd_options})
    # make copy to local scope to add paver to packages to install
    packages_to_install = packages_to_install[:]
    if install_paver:
        packages_to_install.insert(0, 'paver==%s' % setup_meta['version'])
    install_cmd = confd_install_cmd_tmpl % {'packages': packages_to_install}

    options = ""
    # if deprecated 'no_site_packages' was specified and 'system_site_packages'
    # wasn't, set it from that value
    if system_site_packages is None and no_site_packages is not None:
        system_site_packages = not no_site_packages
    if system_site_packages is not None:
        options += ("    options.system_site_packages = %s\n" %
                    bool(system_site_packages))
    if unzip_setuptools:
        options += "    options.unzip_setuptools = True\n"
    if distribute is not None:
        options += "    options.use_distribute = %s\n" % bool(distribute)
    options += "\n"

    extra_text = """def adjust_options(options, args):
    args[:] = ['%s']
%s
def after_install(options, home_dir):
    if sys.platform == 'win32':
        bin_dir = join(home_dir, 'Scripts')
    else:
        bin_dir = join(home_dir, 'bin')
%s""" % (dest_dir, options, install_cmd)
    if paver_command_line:
        command_list = list(paver_command_line.split())
        extra_text += "    subprocess.call([join(bin_dir, 'paver'),%s)" % repr(command_list)[1:]

    extra_text += more_text
    if has_virtualenv:
        bootstrap_contents = venv.create_bootstrap_script(extra_text)
    else:
        raise BuildFailure(VIRTUALENV_MISSING_ERROR)
    fn = script_name

    debug("Bootstrap script extra text: " + extra_text)
    def write_script():
        open(fn, "w").write(bootstrap_contents)
    dry("Write bootstrap script %s" % fn, write_script)


def _boostrap_constraint():
    try:
        import virtualenv as venv
    except ImportError:
        raise BuildFailure(VIRTUALENV_MISSING_ERROR)


@task
def bootstrap():
    """Creates a virtualenv bootstrap script.
    The script will create a bootstrap script that populates a
    virtualenv in the current directory. The environment will
    have paver, the packages of your choosing and will run
    the paver command of your choice.

    This task looks in the virtualenv options for:

    script_name
        name of the generated script
    packages_to_install
        packages to install with pip/easy_install. The version of paver that
        you are using is included automatically. This should be a list of
        strings.
    paver_command_line
        run this paver command line after installation (just the command
        line arguments, not the paver command itself).
    dest_dir
        the destination directory for the virtual environment (defaults to
        '.')
    no_site_packages
        don't give access to the global site-packages dir to the virtual
        environment (default; deprecated)
    system_site_packages
        give access to the global site-packages dir to the virtual
        environment
    unzip_setuptools
        unzip Setuptools when installing it (defaults to False)
    distribute
        use Distribute instead of Setuptools. Set environment variable
        VIRTUALENV_DISTRIBUTE to make it the default.
    index_url
        base URL of Python Package Index
    trusted_host
        specify whether the given index_url is a trusted host to avoid
        deprecated warnings
    no_index
        ignore package index (only looking at find_links URL(s) instead)
    find_links
        additional URL(s) to search for packages. This should be a list of
        strings.
    prefer_easy_install
        prefer easy_install to pip for package installation if both are
        installed (defaults to False)
    """
    vopts = options.virtualenv
    _create_bootstrap(vopts.get("script_name", "bootstrap.py"),
                      vopts.get("packages_to_install", []),
                      vopts.get("paver_command_line", None),
                      dest_dir=vopts.get("dest_dir", '.'),
                      no_site_packages=vopts.get("no_site_packages", None),
                      system_site_packages=vopts.get("system_site_packages",
                                                     None),
                      unzip_setuptools=vopts.get("unzip_setuptools", False),
                      distribute=vopts.get("distribute", None),
                      index_url=vopts.get("index_url", None),
                      trusted_host=vopts.get("trusted_host", None),
                      no_index=vopts.get("no_index", False),
                      find_links=vopts.get("find_links", []),
                      prefer_easy_install=vopts.get("prefer_easy_install",
                                                    False))
bootstrap.paver_constraint = _boostrap_constraint

def virtualenv(dir):
    """Run decorated task in specified virtual environment."""
    def inner(func):
        func = task(func)
        func.use_virtualenv = True
        func.virtualenv_dir = dir
        return func
    return inner
