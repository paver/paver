"""Helper functions and data structures used by pavements."""

import os
import subprocess
from distutils.core import Command
from distutils import log

__all__ = ["Bunch", "TASKS", "task", "Task", "needs", "dry", "error",
           "info", "debug", "call_task", "require_keys", "sh", "options",
           "BuildFailure", "path", 'cmdopts', "consume_args"]

class Bunch(dict):
    """A dictionary that provides attribute-style access."""

    def __repr__(self):
        keys = self.keys()
        keys.sort()
        args = ', '.join(['%s=%r' % (key, self[key]) for key in keys])
        return '%s(%s)' % (self.__class__.__name__, args)
    
    def __getitem__(self, key):
        item = dict.__getitem__(self, key)
        if callable(item):
            return item()
        return item

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    __setattr__ = dict.__setitem__

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name)

class Namespace(Bunch):
    """A Bunch that will search dictionaries contained within to find a value.
    The search order is set via the order() method. See the order method for
    more information about search order.
    """
    def __init__(self, d=None, **kw):
        self._sections = []
        self._ordering = None
        self.update(d, **kw)
    
    def order(self, *keys, **kw):
        """Set the search order for this namespace. The arguments
        should be the list of keys in the order you wish to search,
        or a dictionary/Bunch that you want to search.
        Keys that are left out will not be searched. If you pass in
        no arguments, then the default ordering will be used. (The default
        is to search the global space first, then in the order in
        which the sections were created.)
        
        If you pass in a key name that is not a section, that
        key will be silently removed from the list.
        
        Keyword arguments are:
        
        add_rest=False
            put the sections you list at the front of the search
            and add the remaining sections to the end
        """
        if not keys:
            self._ordering = None
            return
        
        order = []
        for item in keys:
            if isinstance(item, dict) or item in self._sections:
                order.append(item)
        
        if kw.get('add_rest'):
            # this is not efficient. do we care? probably not.
            for item in self._sections:
                if item not in order:
                    order.append(item)
        self._ordering = order
        
    def clear(self):
        self._ordering = None
        self._sections = []
        super(Namespace, self).clear()
    
    def setdotted(self, key, value):
        """Sets a namespace key, value pair where the key
        can use dotted notation to set sub-values. For example,
        the key "foo.bar" will set the "bar" value in the "foo"
        Bunch in this Namespace. If foo does not exist, it is created
        as a Bunch. If foo is a value, a BuildFailure will be
        raised."""
        segments = key.split(".")
        obj = self
        segment = segments.pop(0)
        while segments:
            if segment not in obj:
                obj[segment] = Bunch()
            obj = obj[segment]
            if not isinstance(obj, dict):
                raise BuildFailure("In setting option '%s', %s was already a value"
                                   % (key, segment))
            segment = segments.pop(0)
        obj[segment] = value
    
    def __setitem__(self, key, value):
        if isinstance(value, dict):
            self._sections.insert(0, key)
        super(Namespace, self).__setitem__(key, value)
    
    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default
    
    def __getitem__(self, key):
        order = self._ordering
        if order is None:
            order = self._sections
        try:
            return super(Namespace, self).__getitem__(key)
        except KeyError:
            pass
        for section in order:
            if isinstance(section, dict):
                try:
                    return section[key]
                except KeyError:
                    pass
            else:
                try:
                    return self[section][key]
                except KeyError:
                    pass
        raise KeyError("Key %s not found in namespace" % key)
    
    def __setattr__(self, key, value):
        if key.startswith("_"):
            object.__setattr__(self, key, value)
        else:
            self[key] = value
    
    def __delitem__(self, key):
        try:
            index = self._sections.index(key)
            del self._sections[index]
        except ValueError:
            pass
        super(Namespace, self).__delitem__(key)
    
    def update(self, d=None, **kw):
        """Update the namespace. This is less efficient than the standard 
        dict.update but is necessary to keep track of the sections that we'll be
        searching."""
        items = []
        if d:
            # look up keys even though we call items
            # because that's what the dict.update
            # doc says
            if hasattr(d, 'keys'):
                items.extend(list(d.items()))
            else:
                items.extend(list(d))
        items.extend(list(kw.items()))
        for key, value in items:
            self[key] = value
    
    __call__ = update
    
    def setdefault(self, key, default):
        if not key in self:
            self[key] = default
            return default
        return self[key]
            

TASKS = dict()
options = Namespace(dry_run=False)

# our custom Distribution subclass goes here
dist = None

# contains both long and short names
_ALL_TASKS = dict()

def task(func):
    """Specifies that this function is a task.
    
    Note that this decorator does not actually replace the function object.
    It just keeps track of the task and sets an is_task flag on the
    function object."""
    task = Task(func)
    name = task.name
    
    # the last task with a specific name has its short name added
    if name in TASKS:
        t = TASKS[name]
        if t != task:
            TASKS[t.longname] = t
            t.displayname = t.longname
    TASKS[name] = task
    _ALL_TASKS[name] = task
    _ALL_TASKS[task.longname] = task
    func.is_task = True
    return func

def needs(req):
    """Specifies tasks upon which this task depends.
    
    req can be a string or a list of strings with the names
    of the tasks. You can call this decorator multiple times
    and the various requirements are added on.
    
    The requirements are called in the order presented in the
    list."""
    def entangle(func):
        if hasattr(func, "needs"):
            needs_list = func.needs
        else:
            needs_list = []
            func.needs = needs_list
        if isinstance(req, basestring):
            needs_list.append(req)
        elif isinstance(req, (list, tuple)):
            needs_list.extend(req)
        else:
            raise PavementError("'needs' decorator requires a list or string "
                                "but got %s" % req)
        return func
    return entangle

def cmdopts(options):
    """Sets the command line options that can be set for this task.
    This uses the same format as the distutils command line option
    parser. It's a list of tuples, each with three elements:
    long option name, short option, description.
    
    If the long option name ends with '=', that means that the
    option takes a value. Otherwise the option is just boolean.
    All of the options will be stored in the options dict with
    the name of the task. Each value that gets stored in that
    dict will be stored with a key that is based on the long option
    name (the only difference is that - is replaced by _)."""
    def entangle(func):
        func.options = options
        return func
    return entangle

def consume_args(func):
    """Any command line arguments that appear after this task on the
    command line will be placed in options.args."""
    func.consume_args = True
    return func

def call_task(task_name, options=None):
    """Calls the desired task, including any tasks upon which that task
    depends. options is an optional dictionary that will be added
    to the option lookup search order.
    
    You can always call a task directly by calling the function directly.
    But, if you do so the dependencies aren't called. call_task ensures
    that these are called.
    
    Note that call_task will only call the task `once` during a given
    build as long as the options remain the same. If the options are
    changed, the task will be called again."""
    dist.run_command(task_name, options)

def require_keys(keys):
    """A set of dotted-notation keys that must be present in the
    options for this task to be relevant.
    
    """
    def operate(func):
        k = keys
        if isinstance(k, basestring):
            k = [k]
        try:
            keylist = func.required_keys
        except AttributeError:
            keylist = set()
            func.required_keys = keylist
        keylist.update(k)
        return func
    return operate

class Task(object):
    """Keeps track of the metadata for a function that is used as a 
    pavement task. Also provides the bridge to distutils.
    """
    _command_class = None
    
    def __init__(self, func):
        self.func = func
        self.displayname = self.name
        
    @property
    def distutils_command(self):
        """Get the distutils Command class for this task."""
        if self._command_class:
            return self._command_class
        
        
        class cmd(Command):
            """Generated distutils Command class."""
            task_obj = self
            longname = self.longname
            user_options = self.options
            description = self.description
            
            def initialize_options(self):
                for option in cmd.user_options:
                    longopt = option[0].replace("-", "_")
                    if longopt.endswith("="):
                        setattr(self, longopt[:-1], None)
                    else:
                        setattr(self, longopt, False)
                        
            def finalize_options(self):
                pass
            
            def run(self):
                self.task_obj()
            
            @classmethod
            def _handle_dependencies(cls):
                for need in cls.task_obj.needs:
                    cmdclass = dist.cmdclass[need]
                    cls.user_options.extend(cmdclass.user_options)
            
        cmd.__name__ = self.displayname
        self._command_class = cmd
        return cmd
    
    @property
    def options(self):
        if hasattr(self.func, "options"):
            return self.func.options
        return []
    
    @property
    def name(self):
        return self.func.__name__
    
    @property
    def doc(self):
        try:
            return self.func.__doc__
        except AttributeError:
            return ""
    
    @property
    def consume_args(self):
        return getattr(self.func, "consume_args", False)
    
    @property
    def description(self):
        doc = self.doc
        if doc:
            period = doc.find(".")
            if period > -1:
                doc = doc[0:period]
        else:
            doc = ""
        return doc
    
    def __call__(self, *args, **kw):
        # make sure the dependencies are called
        for need in self.needs:
            call_task(need)
        info("---> %s", self.displayname)
        return self.func(*args, **kw)
    
    def __hash__(self):
        return hash(self.func)
    
    def __eq__(self, other):
        return self.func == other.func
    
    @property
    def longname(self):
        if hasattr(self, "_longname"):
            return self._longname
        return "%s.%s" % (self.func.__module__, self.name)
    
    @property
    def needs(self):
        return getattr(self.func, "needs", [])
    
    @property
    def user_defined(self):
        return self.longname.startswith("paver.defaults")
    
    def valid(self, options):
        """Determine if this task is allowable given the 
        current build environment."""
        if hasattr(self.func, "required_keys"):
            for key in self.func.required_keys:
                parts = key.split(".")
                current = options
                valid = True
                for part in parts:
                    if part not in current:
                        valid = False
                        break
                    current = current[part]
                if not valid:
                    return False
        return True
    
def error(message, *args):
    """Displays an error message to the user."""
    log.error(message, *args)

def info(message, *args):
    """Displays a message to the user. If the quiet option is specified, the
    message will not be displayed."""
    log.info(message, *args)

def debug(message, *args):
    """Displays a message to the user, but only if the verbose flag is
    set."""
    log.debug(message, *args)

def sh(command, capture=False, ignore_error=False):
    """Runs an external command. If capture is True, the output of the
    command will be captured and returned as a string.  If the command 
    has a non-zero return code raise a BuildFailure. You can pass
    ignore_error=True to allow non-zero return codes to be allowed to
    pass silently, silently into the night.
    
    If the dry_run option is True, the command will not
    actually be run."""
    def runpipe():
        p = subprocess.Popen(command, shell=True, 
                stdout=subprocess.PIPE)
        
        p.wait()
        if p.returncode and not ignore_error:
            raise BuildFailure(p.returncode)

        return p.stdout.read()

    if capture:
        return dry(command, runpipe)
    else:
        returncode = dry(command, subprocess.call, command, shell=True)
        if returncode and not ignore_error:
            raise BuildFailure(returncode)

def dry(message, func, *args, **kw):
    """Wraps a function that performs a destructive operation, so that
    nothing will happen when a dry run is requested.
    
    Runs func with the given arguments and keyword arguments. If this
    is a dry run, print the message rather than running the function."""
    info(message)
    if options['dry_run']:
        return
    return func(*args, **kw)

class PavementError(Exception):
    """Exception that represents a problem in the pavement.py file
    rather than the process of running a build."""
    pass

class BuildFailure(Exception):
    """Represents a problem with some part of the build's execution."""
    pass

from paver.path import path
