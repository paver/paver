import sys
import optparse
import types
import inspect

environment = None

class PavementError(Exception):
    """Exception that represents a problem in the pavement.py file
    rather than the process of running a build."""
    pass

class BuildFailure(Exception):
    """Represents a problem with some part of the build's execution."""
    pass


class Environment(object):
    def __init__(self, pavement):
        self.pavement = pavement
    
    def log(self, message, *args):
        print message % args
        
    def get_task(self, taskname):
        task = getattr(self.pavement, taskname, None)
        if not task:
            task = _import_task(taskname)
        return task
        
    def _call_task(self, task_name, needs, func):
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
        self.name = "%s.%s" % (func.__module__, func.__name__)
        try:
            self.__doc__ = func.__doc__
        except AttributeError:
            pass
        
    def __call__(self, *args, **kw):
        retval = environment._call_task(self.name, self.needs, self.func)
        self.called = True
        return retval
    
    def __repr__(self):
        return "Task: " + self.__name__

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

def _parse_command_line(args):
    parser = optparse.OptionParser()
    parser.disable_interspersed_args()
    
    options, args = parser.parse_args(args)
    if not args:
        return None, []
        
    taskname = args.pop(0)
    task = environment.get_task(taskname)
    if not task:
        raise BuildFailure("Unknown task: %s" % taskname)
    return task, args

@task
def help():
    task_list = environment.get_tasks()
    for task in task_list:
        print task.name

def main(args=None):
    global environment
    if args is None:
        if len(sys.argv) > 1:
            args = sys.argv[1:]
        else:
            args = []
    mod = __import__("pavement")
    environment = Environment(mod)
    while True:
        task, args = _parse_command_line(args)
        if task is None:
            break
        task()
    