import sys
import optparse
import types
import inspect
import itertools

environment = None

class PavementError(Exception):
    """Exception that represents a problem in the pavement.py file
    rather than the process of running a build."""
    pass

class BuildFailure(Exception):
    """Represents a problem with some part of the build's execution."""
    pass


class Environment(object):
    _all_tasks = None
    
    def __init__(self, pavement=None):
        self.pavement = pavement
        self.task_finders = []
        try:
            # for the time being, at least, tasks.py can be used on its
            # own!
            from paver import options
            self.options = options.Namespace()
        except ImportError:
            pass
    
    def log(self, message, *args):
        print message % args
        
    def debug(self, message, *args):
        print message % args
    
    def error(self, message, *args):
        print message % args
        
    def get_task(self, taskname):
        task = getattr(self.pavement, taskname, None)
        
        # delegate to task finders next
        if not task:
            for finder in self.task_finders:
                task = finder(taskname)
                if task:
                    break

        # try to look up by full name
        if not task:
            task = _import_task(taskname)
            
        # if there's nothing by full name, look up by
        # short name
        if not task:
            all_tasks = self.get_tasks()
            matches = [t for t in all_tasks
                        if t.shortname == taskname]
            if len(matches) > 1:
                matched_names = [t.name for t in matches]
                raise BuildFailure("Ambiguous task name %s (%s)" %
                                    (taskname, matched_names))
            elif matches:
                task = matches[0]
        return task
        
    def call_task(self, task_name, needs, func):
        funcargs = inspect.getargspec(func)[0]
        kw = dict()
        for arg in funcargs:
            if arg == 'env':
                kw['env'] = self
            else:
                try:
                    kw[arg] = getattr(self, arg)
                except AttributeError:
                    raise PavementError("Task %s requires an argument (%s) that is "
                        "not present in the environment" % (task_name, arg))
        
        self.log("---> " + task_name)
        for req in needs:
            task = self.get_task(req)
            if not task:
                raise PavementError("Requirement %s for task %s not found" %
                    (req, task_name))
            if not isinstance(task, Task):
                raise PavementError("Requirement %s for task %s is not a Task"
                    % (req, task_name))
            if not task.called:
                task()
        return func(**kw)
    
    def get_tasks(self):
        if self._all_tasks:
            return self._all_tasks
        result = set()
        modules = set()
        def scan_module(module):
            modules.add(module)
            for name in dir(module):
                item = getattr(module, name, None)
                if isinstance(item, Task):
                    result.add(item)
                if isinstance(item, types.ModuleType) and item not in modules:
                    scan_module(item)
        scan_module(self.pavement)
        self._all_tasks = result
        return result
    
def _import_task(taskname):
    """Looks up a dotted task name and imports the module as necessary
    to get at the task."""
    parts = taskname.split('.')
    if len(parts) < 2:
        return None
    func_name = parts[-1]
    full_mod_name = ".".join(parts[:-1])
    mod_name = parts[-2]
    try:
        module = __import__(full_mod_name, fromlist=[mod_name])
    except ImportError:
        return None
    return getattr(module, func_name)

class Task(object):
    called = False
    def __init__(self, func):
        self.func = func
        self.needs = []
        self.__name__ = func.__name__
        self.shortname = func.__name__
        self.name = "%s.%s" % (func.__module__, func.__name__)
        self.option_names = set()
        self.user_options = []
        try:
            self.__doc__ = func.__doc__
        except AttributeError:
            pass
        
    def __call__(self, *args, **kw):
        retval = environment.call_task(self.name, self.needs, self.func)
        self.called = True
        return retval
    
    def __repr__(self):
        return "Task: " + self.__name__
    
    @property    
    def parser(self):
        options = self.user_options
        parser = optparse.OptionParser()
        parser.disable_interspersed_args()
        
        needs_tasks = [environment.get_task(task) for task in self.needs]
        for task in itertools.chain([self], needs_tasks):
            for option in task.user_options:
                try:
                    longname = option[0]
                    if longname.endswith('='):
                        action = "store"
                        longname = longname[:-1]
                    else:
                        action = "store_true"
            
                    environment.debug("Task %s: adding option %s (%s)" %
                                     (self.name, longname, option[1]))
                    try:
                        if option[1] is None:
                            parser.add_option("--" + longname, action=action, 
                                              dest=longname)
                        else:
                            parser.add_option("-" + option[1], 
                                              "--" + longname, action=action, 
                                              dest=longname)
                    except optparse.OptionConflictError:
                        raise PavementError("""In setting command options for %r, 
option %s for %r is already in use
by another task in the dependency chain.""" % (self, option, task))
                    self.option_names.add((task.shortname, longname))
                except IndexError:
                    raise PavementError("Invalid option format provided for %r: %s"
                                        % (self, option))
        return parser
        
    def parse_args(self, args):
        import paver.options
        environment.debug("Task %s: Parsing args %s" % (self.name, args))
        optholder = environment.options.setdefault(self.shortname, 
                                                   paver.options.Bunch())
        options, args = self.parser.parse_args(args)
        for task_name, option_name in self.option_names:
            try:
                optholder = environment.options[task_name]
            except KeyError:
                optholder = paver.options.Bunch()
                environment.options[task_name] = optholder
            optholder[option_name] = getattr(options, option_name)
        return args

def task(func):
    """Specifies that this function is a task.
    
    Note that this decorator does not actually replace the function object.
    It just keeps track of the task and sets an is_task flag on the
    function object."""
    if isinstance(func, Task):
        return func
    task = Task(func)
    return task

def needs(*args):
    """Specifies tasks upon which this task depends.

    req can be a string or a list of strings with the names
    of the tasks. You can call this decorator multiple times
    and the various requirements are added on. You can also
    call with the requirements as a list of arguments.

    The requirements are called in the order presented in the
    list."""
    def entangle(func):
        req = args
        func = task(func)
        needs_list = func.needs
        if len(req) == 1:
            req = req[0]
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
        func = task(func)
        func.user_options = options
        return func
    return entangle

def _preparse(args):
    task = None
    while args:
        arg = args.pop(0)
        if '=' in arg:
            key, value = arg.split("=")
            try:
                environment.options.setdotted(key, value)
            except AttributeError:
                raise BuildFailure("""This appears to be a standalone Paver
tasks.py, so the build environment does not support options. The command
line (%s) attempts to set an option.""" % (args))
        elif arg.startswith('-'):
            args.insert(0, arg)
            break
        else:
            task = environment.get_task(arg)
            if task is None:
                raise BuildFailure("Unknown task: %s" % arg)
            break
    return task, args

def _parse_command_line(args):
    task, args = _preparse(args)
    
    if not task:
        # this is where global options should be dealt with
        parser = optparse.OptionParser()
        parser.disable_interspersed_args()
        options, args = parser.parse_args(args)
        if not args:
            return None, []
        
        taskname = args.pop(0)
        task = environment.get_task(taskname)
        
    if not task:
        raise BuildFailure("Unknown task: %s" % taskname)
    args = task.parse_args(args)
    return task, args

@task
def help():
    task_list = environment.get_tasks()
    for task in task_list:
        print task.name

def _process_commands(args):
    while True:
        task, args = _parse_command_line(args)
        if task is None:
            break
        task()

def main(args=None):
    global environment
    if args is None:
        if len(sys.argv) > 1:
            args = sys.argv[1:]
        else:
            args = []
    environment = Environment()
    mod = __import__("pavement")
    environment.pavement = mod
    _process_commands(args)
