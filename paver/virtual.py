"""Tasks for managing virtualenv environments."""
from paver.easy import task, options, dry, debug
from paver.release import setup_meta

try:
    import virtualenv as venv
except ImportError:
    has_virtualenv = False
else:
    has_virtualenv = True

_easy_install_tmpl = "    subprocess.call([join(%s, 'easy_install'), '%s'])\n"
def _create_bootstrap(script_name, packages_to_install, paver_command_line,
                      install_paver=True, more_text="", dest_dir='.',
                      no_site_packages=False, unzip_setuptools=False):
    if install_paver:
        paver_install = (_easy_install_tmpl %
                    ('bin_dir', 'paver==%s' % setup_meta['version']))
    else:
        paver_install = ""

    options = """

    options.no_site_packages = %s
    if hasattr(options,"system_site_packages"):
        options.system_site_packages = %s
        """%(bool(no_site_packages),not bool(no_site_packages))

    if unzip_setuptools:
        if options:
            options += "\n"
        options += "    options.unzip_setuptools = True"
    if options:
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
        extra_text += _easy_install_tmpl % ('bin_dir', package)
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
        environment (defaults to False)
    unzip_setuptools
        unzip Setuptools when installing it (defaults to False)
    """
    vopts = options.virtualenv
    _create_bootstrap(vopts.get("script_name", "bootstrap.py"),
                      vopts.get("packages_to_install", []),
                      vopts.get("paver_command_line", None),
                      dest_dir=vopts.get("dest_dir", '.'),
                      no_site_packages=vopts.get("no_site_packages", False),
                      unzip_setuptools=vopts.get("unzip_setuptools", False))
bootstrap.paver_constraint = _boostrap_constraint

def virtualenv(dir):
    """Run decorated task in specified virtual environment."""
    def inner(func):
        func = task(func)
        func.use_virtualenv = True
        func.virtualenv_dir = dir
        return func
    return inner
