"""Tasks for managing virtualenv environments."""
from paver.easy import task, options, dry, debug
from paver.release import setup_meta

try:
    import virtualenv as venv
except ImportError:
    has_virtualenv = False
else:
    has_virtualenv = True

_easy_install_tmpl = (
    "    subprocess.call([join(%s, 'easy_install'), %s'%%s'])\n")
def _create_bootstrap(script_name, packages_to_install, paver_command_line,
                      install_paver=True, more_text="", dest_dir='.',
                      no_site_packages=None, system_site_packages=None,
                      unzip_setuptools=False, index_url=None, find_links=None):
    # configure easy install template
    easy_install_options = []
    if index_url:
        easy_install_options.extend(["--index-url", index_url])
    if find_links:
        easy_install_options.extend(
            ["--find-links", " ".join(find_links)])
    easy_install_options = (
        easy_install_options
        and "'%s', " % "', '".join(easy_install_options) or '')
    confd_easy_install_tmpl = (_easy_install_tmpl %
                               ('bin_dir',  easy_install_options))
    if install_paver:
        paver_install = (confd_easy_install_tmpl %
                         ('paver==%s' % setup_meta['version']))
    else:
        paver_install = ""

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
    options += "\n"

    extra_text = """def adjust_options(options, args):
    args[:] = ['%s']
%s
def after_install(options, home_dir):
    if sys.platform == 'win32':
        bin_dir = join(home_dir, 'Scripts')
    else:
        bin_dir = join(home_dir, 'bin')
%s""" % (dest_dir, options, paver_install)
    for package in packages_to_install:
        extra_text += _confd_easy_install_tmpl % package
    if paver_command_line:
        command_list = list(paver_command_line.split())
        extra_text += "    subprocess.call([join(bin_dir, 'paver'),%s)" % repr(command_list)[1:]

    extra_text += more_text
    bootstrap_contents = venv.create_bootstrap_script(extra_text)
    fn = script_name

    debug("Bootstrap script extra text: " + extra_text)
    def write_script():
        open(fn, "w").write(bootstrap_contents)
    dry("Write bootstrap script %s" % fn, write_script)


def _boostrap_constraint():
    try:
        import virtualenv as venv
    except ImportError:
        from paver.runtime import PaverImportError
        raise PaverImportError("`virtualenv` is needed to use paver's virtualenv tasks")


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
        packages to install with easy_install. The version of paver that
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
    index_url
        base URL of Python Package Index
    find_links
        additional URL(s) to search for packages. This should be a list of
        strings.
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
                      index_url=vopts.get("index_url", None),
                      find_links=vopts.get("find_links", []))
bootstrap.paver_constraint = _boostrap_constraint

def virtualenv(dir):
    """Run decorated task in specified virtual environment."""
    def inner(func):
        func = task(func)
        func.use_virtualenv = True
        func.virtualenv_dir = dir
        return func
    return inner
