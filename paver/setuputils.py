"""Integrates distutils/setuptools with Paver."""

import re
import os
import sys
from os.path import *
from fnmatch import fnmatchcase
from distutils.util import convert_path
from distutils import log
try:
    from setuptools import dist
except ImportError:
    from distutils import dist
from distutils.errors import DistutilsModuleError
_Distribution = dist.Distribution


from paver.options import Bunch

try:
    import setuptools
    import pkg_resources
    has_setuptools = True
except ImportError:
    has_setuptools = False

# our commands can have '.' in them, so we'll monkeypatch this
# expression
dist.command_re = re.compile (r'^[a-zA-Z]([a-zA-Z0-9_\.]*)$')

from paver import tasks

__ALL__ = ['find_package_data']

# find_package_data is an Ian Bicking creation.

# Provided as an attribute, so you can append to these instead
# of replicating them:
standard_exclude = ('*.py', '*.pyc', '*~', '.*', '*.bak', '*.swp*')
standard_exclude_directories = ('.*', 'CVS', '_darcs', './build',
                                './dist', 'EGG-INFO', '*.egg-info')

def _dispatch_setuptools_install(distribution, command_name):
    """
    setuptools hack:
    - setuptools check where is `install` command called from:
    - if it's not called directly (case of paver), use `install` from distutils
        (no deps handling)
    - if it's called directly, it handles `install_requires` deps as well
        (which is what we want, but what we do not get... until this hack)
    """
    cmd = distribution.get_command_obj(command_name)
    if hasattr(cmd, 'do_egg_install'):
        cmd.do_egg_install()
    else:
        print >> sys.stderr, "Setuptools install-dependencies hack failed"
        distribution.run_command(command_name)

# storage of extra dispatchers for distutils/setuptools commands
_extra_command_dispatch = {
    'setuptools.command.install.install': _dispatch_setuptools_install,
}

def find_package_data(
    where='.', package='',
    exclude=standard_exclude,
    exclude_directories=standard_exclude_directories,
    only_in_packages=True,
    show_ignored=False):
    """
    Return a dictionary suitable for use in ``package_data``
    in a distutils ``setup.py`` file.

    The dictionary looks like::

        {'package': [files]}

    Where ``files`` is a list of all the files in that package that
    don't match anything in ``exclude``.

    If ``only_in_packages`` is true, then top-level directories that
    are not packages won't be included (but directories under packages
    will).

    Directories matching any pattern in ``exclude_directories`` will
    be ignored; by default directories with leading ``.``, ``CVS``,
    and ``_darcs`` will be ignored.

    If ``show_ignored`` is true, then all the files that aren't
    included in package data are shown on stderr (for debugging
    purposes).

    Note patterns use wildcards, or can be exact paths (including
    leading ``./``), and all searching is case-insensitive.
    
    This function is by Ian Bicking.
    """

    out = {}
    stack = [(convert_path(where), '', package, only_in_packages)]
    while stack:
        where, prefix, package, only_in_packages = stack.pop(0)
        for name in os.listdir(where):
            fn = join(where, name)
            if isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        if show_ignored:
                            print >> sys.stderr, (
                                "Directory %s ignored by pattern %s"
                                % (fn, pattern))
                        break
                if bad_name:
                    continue
                if isfile(join(fn, '__init__.py')):
                    if not package:
                        new_package = name
                    else:
                        new_package = package + '.' + name
                    stack.append((fn, '', new_package, False))
                else:
                    stack.append((fn, prefix + name + '/', package, only_in_packages))
            elif package or not only_in_packages:
                # is a file
                bad_name = False
                for pattern in exclude:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        if show_ignored:
                            print >> sys.stderr, (
                                "File %s ignored by pattern %s"
                                % (fn, pattern))
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix+name)
    return out

class DistutilsTask(tasks.Task):
    def __init__(self, distribution, command_name, command_class):
        name_sections = str(command_class).split(".")
        if name_sections[-2] == name_sections[-1]:
            del name_sections[-2]
        self.name = ".".join(name_sections)
        self.__name__ = self.name
        self.distribution = distribution
        self.command_name = command_name
        self.shortname = _get_shortname(command_name)
        self.command_class = command_class
        self.option_names = set()
        self.needs = []
        self.might_call = []
        self._parser = None
        self.share_options_with = []

        self.user_options = command_class.user_options
        self.negative_opt = getattr(command_class, "negative_opt", {})
        # Parse distutils config files.
        distribution.parse_config_files()
        
    def __call__(self, *args, **kw):
        options = tasks.environment.options.get(self.shortname, {})
        opt_dict = self.distribution.get_option_dict(self.command_name)
        for (name, value) in options.items():
            opt_dict[name.replace('-', '_')] = ("command line", value)

        # see if we don't have extra dispatcher for command
        if str(self.command_class) in _extra_command_dispatch:
            _extra_command_dispatch[str(self.command_class)](self.distribution, self.command_name)
        else:
            self.distribution.run_command(self.command_name)
        
    @property
    def description(self):
        return self.command_class.description
        
def _get_shortname(taskname):
    dotindex = taskname.rfind(".")
    if dotindex > -1:
        command_name = taskname[dotindex+1:]
    else:
        command_name = taskname
    return command_name
    
class DistutilsTaskFinder(object):
    def get_task(self, taskname):
        dist = _get_distribution()
        command_name = _get_shortname(taskname)
        try:
            command_class = dist.get_command_class(command_name)
        except DistutilsModuleError:
            return None
        return DistutilsTask(dist, command_name, command_class)
        
    def get_tasks(self):
        dist = _get_distribution()
        if has_setuptools:
            for ep in pkg_resources.iter_entry_points('distutils.commands'):
                try:
                    cmdclass = ep.load(False) # don't require extras, we're not running
                    dist.cmdclass[ep.name] = cmdclass
                except:
                    # on the Mac, at least, installing from the tarball
                    # via zc.buildout fails due to a problem in the
                    # py2app command
                    tasks.environment.info("Could not load entry point: %s", ep)
        dist.get_command_list()
        return set(DistutilsTask(dist, key, value) 
            for key, value in dist.cmdclass.items())

def _get_distribution():
    try:
        return tasks.environment.distribution
    except AttributeError:
        dist = _Distribution(attrs=tasks.environment.options.get('setup', {}))
        tasks.environment.distribution = dist
        dist.script_name = tasks.environment.pavement_file
        return dist

def install_distutils_tasks():
    """Makes distutils and setuptools commands available as Paver tasks."""
    env = tasks.environment
    if not hasattr(env, "_distutils_tasks_installed"):
        env.task_finders.append(DistutilsTaskFinder())
        env._distutils_tasks_installed = True

def setup(**kw):
    """Updates options.setup with the keyword arguments provided,
    and installs the distutils tasks for this pavement. You can
    use paver.setuputils.setup as a direct replacement for
    the distutils.core.setup or setuptools.setup in a traditional
    setup.py."""
    install_distutils_tasks()
    setup_section = tasks.environment.options.setdefault("setup", Bunch())
    setup_section.update(kw)

def _error(message, *args):
    """Displays an error message to the user."""
    tasks.environment.error(message, *args)

def _info(message, *args):
    """Displays a message to the user. If the quiet option is specified, the
    message will not be displayed."""
    tasks.environment.info(message, *args)

def _debug(message, *args):
    """Displays a message to the user, but only if the verbose flag is
    set."""
    tasks.environment.debug(message, *args)

def _base_log(level, message, *args):
    """Displays a message at the given log level"""
    tasks.environment._log(level, message, args)
    
# monkeypatch the distutils logging to go through Paver's logging
log.log = _base_log
log.debug = _debug
log.info = _info
log.warn = _error
log.error = _error
log.fatal = _error


if has_setuptools:
    __ALL__.extend(["find_packages"])
    
    from setuptools import find_packages
else:
    import distutils.core
    
