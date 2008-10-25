"""Integrates distutils/setuptools with Paver."""

import re
import os
import sys
import distutils
from fnmatch import fnmatchcase
from distutils.util import convert_path
from distutils import dist

try:
    import setuptools
    import pkg_resources
    has_setuptools = True
except ImportError:
    has_setuptools = False

# our commands can have '.' in them, so we'll monkeypatch this
# expression
dist.command_re = re.compile (r'^[a-zA-Z]([a-zA-Z0-9_\.]*)$')

# this has to come after the setuptools import to make sure
# we get the setuptools Distribution class
from distutils.core import Distribution as _Distribution
    
from paver.runtime import *
from paver import runtime

__ALL__ = ['find_package_data', "setup"]


class _cmddict(dict):
    """Provides lookup for distutils commands, preferring Paver Tasks."""
    def __init__(self, *args, **kw):
        dict.__init__(self, *args, **kw)
        
        # the _distutils_name_map holds the mapping
        # from a short command name to the long name
        # that is used if a pavement overrides the command.
        self._distutils_name_map = dict()
    
    def __setitem__(self, key, value):
        """Ensure that Paver Tasks have precedence over distutils commands"""
        if isinstance(value, Task):
            # we store both long names and short names
            nkey = value.longname
            
            # don't do this for things defined in pavement.py
            if not nkey.startswith("paver.defaults"):
                dict.__setitem__(self, nkey, value.distutils_command)
                
            value = value.distutils_command
        
        if key in self:
            current = self[key]
            # tasks get priority, so if it's a task, change the
            # other one
            if hasattr(current, 'task_obj'):
                key = self._replacement_name(key, value)
            else:
                nkey = self._replacement_name(key, current)
                self[nkey] = current
        dict.__setitem__(self, key, value)
    
    def _replacement_name(self, key, cmdobj):
        """Get the long name form"""
        # task cmdobj will have a long name property
        if hasattr(cmdobj, "longname"):
            return cmdobj.longname
        
        if cmdobj.__module__.endswith(key):
            # rather than using something like
            # setuptools.command.sdist.sdist
            # we'll use the more pleasant
            # setuptools.command.sdist
            nkey = cmdobj.__module__
        else:
            nkey = "%s.%s" % (cmdobj.__module__, key)
            
        self._distutils_name_map[key] = nkey
            
        return nkey

    def update(self, d):
        """Slower than normal dict.update, but ensures the behavior
        is correct for overridden commands."""
        for key, value in d.items():
            self[key] = value

class Distribution(_Distribution):
    """Subclass of the distutils (or setuptools) Distribution. This is the
    driver for the build process."""
    _running_distutils = False
    _current_namespace = None
    
    def __init__(self, *args, **kw):
        runtime.dist = self
        _Distribution.__init__(self, *args, **kw)
        self.cmdclass = _cmddict()
        self._update_command_list()
        self._current_namespace = []

    def _update_command_list(self):
        """Add in setuptools commands and Paver Tasks."""
        if has_setuptools:
            for ep in pkg_resources.iter_entry_points('distutils.commands'):
                try:
                    cmdclass = ep.load(False) # don't require extras, we're not running
                    self.cmdclass[ep.name] = cmdclass
                except:
                    # on the Mac, at least, installing from the tarball
                    # via zc.buildout fails due to a problem in the
                    # py2app command
                    info("Could not load entry point: %s", ep)
        _Distribution.get_command_list(self)
        self.cmdclass.update(runtime.TASKS)
        for value in self.cmdclass.values():
            if hasattr(value, 'task_obj'):
                value._handle_dependencies()
        
    def get_command_obj(self, command, create=1):
        # when in the distutils context, make sure we
        # only return distutils commands. Distutils
        # commands expect this behavior and don't understand Paver
        # overrides.
        if self._running_distutils:
            command = self.cmdclass._distutils_name_map.get(command, command)
        return _Distribution.get_command_obj(self, command, create)
    
    def get_option_dict(self, command):
        return self.command_options.setdefault(command, Bunch())
    
    def run_command(self, command, more_options=None):
        if "=" in command:
            key, value = command.split("=")
            runtime.options.setdotted(key, value)
            return
        
        if self.have_run.get(command):
            return
        
        runtime.options.dry_run = self.dry_run
        
        ns = self._current_namespace
        
        cmd_obj = self.get_command_obj(command)
        
        # special handling for Tasks. Command line options
        # need to get passed into the options for the task.
        if hasattr(cmd_obj, "task_obj"):
            
            options = self.get_option_dict(command)
            ns.append(options)
            task_options = runtime.options.setdefault(command, Bunch())
            for key, value in options.items():
                # the options as set by distutils are a tuple
                # like ('command-line', value)
                task_options[key] = value[1]
                
            # by default, we will give preference to a section
            # matching the name of the command that's running.
            # everything will be searchable though.
            if more_options:
                runtime.options.order(more_options, command, add_rest=True)
            else:
                runtime.options.order(command, add_rest=True)
            cmd_obj.run()
            ns.pop()
            self.have_run[command] = 1
            return
        
        # if a distutils command is a dependent of a task
        # its command line options are inherited.
        # maybe extend this later to allow the inheritance
        # of pavement options.
        if ns:
            self._set_command_options(cmd_obj, ns[-1])
        
        # switch cmdclass to distutils context so that
        # command lookups by name will only return 
        # distutils commands
        self._running_distutils = True
        cmd_obj.ensure_finalized()
        info("---> %s", command)
        cmd_obj.run()
        self._running_distutils = False
        self.have_run[command] = 1
    
    def _parse_command_opts(self, parser, args):
        command = args[0]
        if '=' in command:
            self.commands.append(command)
            return args[1:]
        cmdclass = self.cmdclass.get(command)
        if cmdclass and hasattr(cmdclass, "task_obj"):
            task = cmdclass.task_obj
            if task.consume_args:
                options.args = args[1:]
                self.commands.append(command)
                return []
        return _Distribution._parse_command_opts(self, parser, args)
    

# find_package_data is an Ian Bicking creation.

# Provided as an attribute, so you can append to these instead
# of replicating them:
standard_exclude = ('*.py', '*.pyc', '*~', '.*', '*.bak', '*.swp*')
standard_exclude_directories = ('.*', 'CVS', '_darcs', './build',
                                './dist', 'EGG-INFO', '*.egg-info')

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
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
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
                if os.path.isfile(os.path.join(fn, '__init__.py')):
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

if has_setuptools:
    __ALL__.extend(["find_packages"])
    
    from setuptools import find_packages
    
    setup = setuptools.setup
else:
    import distutils.core
    
    setup = distutils.core.setup
