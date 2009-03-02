import sys
import os
import optparse
import types
import inspect
import itertools
import traceback

VERSION = "1.0a2"

class PavementError(Exception):
    """Exception that represents a problem in the pavement.py file
    rather than the process of running a build."""
    pass

class BuildFailure(Exception):
    """Represents a problem with some part of the build's execution."""
    pass


class Environment(object):
    _task_in_progress = None
    _task_output = None
    _all_tasks = None
    _dry_run = False
    verbose = False
    interactive = False
    quiet = False
    _file = "pavement.py"
    
    def __init__(self, pavement=None):
        self.pavement = pavement
        self.task_finders = []
        try:
            # for the time being, at least, tasks.py can be used on its
            # own!
            from paver import options
            self.options = options.Namespace()
            self.options.dry_run = False
            self.options.pavement_file = self.pavement_file
        except ImportError:
            pass
    
    def info(self, message, *args):
        self._log(2, message, args)
        
    def debug(self, message, *args):
        self._log(1, message, args)
    
    def error(self, message, *args):
        self._log(3, message, args)
    
    def _log(self, level, message, args):
        output = message % args
        if self._task_output is not None:
            self._task_output.append(output)
        if level > 2 or (level > 1 and not self.quiet) or \
            self.verbose:
            self._print(output)
    
    def _print(self, output):
        print output
    
    def _exit(self, code):
        sys.exit(1)

    def _set_dry_run(self, dr):
        self._dry_run = dr
        try:
            self.options.dry_run = dr
        except AttributeError:
            pass
    
    def _get_dry_run(self):
        return self._dry_run
        
    dry_run = property(_get_dry_run, _set_dry_run)
        
    def _set_pavement_file(self, pavement_file):
        self._file = pavement_file
        try:
            self.options.pavement_file = pavement_file
        except AttributeError:
            pass

    def _get_pavement_file(self):
        return self._file

    pavement_file = property(_get_pavement_file, _set_pavement_file)
    
    file = property(fset=_set_pavement_file)

    def get_task(self, taskname):
        task = getattr(self.pavement, taskname, None)
        
        # delegate to task finders next
        if not task:
            for finder in self.task_finders:
                task = finder.get_task(taskname)
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
        
        if not self._task_in_progress:
            self._task_in_progress = task_name
            self._task_output = []
            running_top_level = True
        else:
            running_top_level = False
        def do_task():
            self.info("---> " + task_name)
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
        if running_top_level:
            try:
                return do_task()
            except Exception, e:
                self._print("""

Captured Task Output:
---------------------
""")
                self._print("\n".join(self._task_output))
                if isinstance(e, BuildFailure):
                    self._print("\nBuild failed running %s: %s" % 
                                (self._task_in_progress, e))
                else:
                    self._print(traceback.format_exc())
            self._task_in_progress = None
            self._task_output = None
            self._exit(1)
        else:
            return do_task()
    
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
        for finder in self.task_finders:
            result.update(finder.get_tasks())
        self._all_tasks = result
        return result
    
environment_stack = []
environment = Environment()

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
    return getattr(module, func_name, None)

class Task(object):
    called = False
    consume_args = False
    __doc__ = ""
    
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
        
        needs_tasks = [(environment.get_task(task), task) for task in self.needs]
        for task, task_name in itertools.chain([(self, self.name)], needs_tasks):
            if not task:
                raise PavementError("Task %s needed by %s does not exist"
                    % (task_name, self))
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
                                              dest=longname.replace('-', '_'),
                                              help=option[2])
                        else:
                            parser.add_option("-" + option[1], 
                                              "--" + longname, action=action, 
                                              dest=longname.replace('-', '_'),
                                              help=option[2])
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
            option_name = option_name.replace('-', '_')
            try:
                optholder = environment.options[task_name]
            except KeyError:
                optholder = paver.options.Bunch()
                environment.options[task_name] = optholder
            value = getattr(options, option_name)
            if value is not None:
                optholder[option_name] = getattr(options, option_name)
        return args
        
    @property
    def description(self):
        doc = self.__doc__
        if doc:
            period = doc.find(".")
            if period > -1:
                doc = doc[0:period]
        else:
            doc = ""
        return doc


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

def consume_args(func):
    """Any command line arguments that appear after this task on the
    command line will be placed in options.args."""
    func = task(func)
    func.consume_args = True
    return func

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

def _parse_global_options(args):
    # this is where global options should be dealt with
    parser = optparse.OptionParser(usage="""Usage: %prog [global options] taskname [task options] [taskname [taskoptions]]""")
    
    parser.add_option('-n', '--dry-run', action='store_true',
                    help="don't actually do anything")
    parser.add_option('-v', "--verbose", action="store_true",
                    help="display all logging output")
    parser.add_option('-q', '--quiet', action="store_true",
                    help="display only errors")
    parser.add_option("-i", "--interactive", action="store_true",
                    help="enable prompting")
    parser.add_option("-f", "--file", metavar="FILE",
                    help="read tasks from FILE [%default]")
    parser.add_option("--version", action="store_true",
                    help="display Paver version number")
    parser.set_defaults(file=environment.pavement_file)

    parser.disable_interspersed_args()
    options, args = parser.parse_args(args)
    if options.version:
        print "Paver %s" % VERSION
    for key, value in vars(options).items():
        setattr(environment, key, value)
        
    return args

def _parse_command_line(args):
    task, args = _preparse(args)
    
    if not task:
        args = _parse_global_options(args)
        if not args:
            return None, []
        
        taskname = args.pop(0)
        task = environment.get_task(taskname)
        
    if not task:
        raise BuildFailure("Unknown task: %s" % taskname)
        
    args = task.parse_args(args)
    if task.consume_args:
        try:
            environment.options.args = args
        except AttributeError:
            pass
        environment.args = args
        args = []

    return task, args

def _cmp_task_names(a, b):
    a = a.name
    b = b.name
    a_in_pavement = a.startswith("pavement.")
    b_in_pavement = b.startswith("pavement.")
    if a_in_pavement and not b_in_pavement:
        return 1
    if b_in_pavement and not a_in_pavement:
        return -1
    return cmp(a, b)
    
def _group_by_module(items):
    groups = []
    current_group_name = None
    current_group = None
    maxlen = 5
    for item in items:
        name = item.name
        dotpos = name.rfind(".")
        group_name = name[:dotpos]
        maxlen = max(len(item.shortname), maxlen)
        if current_group_name != group_name:
            current_group = []
            current_group_name = group_name
            groups.append([group_name, current_group])
        current_group.append(item)
    return maxlen, groups

@task
@consume_args
def help(args):
    """This help display."""
    if args:
        task_name = args[0]
        task = environment.get_task(task_name)
        if not task:
            print "Task not found: %s" % (task_name)
            return
        
        print "\n%s" % task_name
        print "-" * (len(task_name))
        print
        print task.__doc__
        return
        
    task_list = environment.get_tasks()
    task_list = sorted(task_list, cmp=_cmp_task_names)
    maxlen, task_list = _group_by_module(task_list)
    fmt = "  %-" + str(maxlen) + "s - %s"
    for group_name, group in task_list:
        print "\nTasks from %s:" % (group_name)
        for task in group:
            print(fmt % (task.shortname, task.description))

def _process_commands(args):
    while True:
        task, args = _parse_command_line(args)
        if task is None:
            break
        task()

def call_pavement(new_pavement, args):
    if isinstance(args, basestring):
        args = args.split()
    global environment
    environment_stack.append(environment)
    environment = Environment()
    environment.pavement_file = new_pavement
    _launch_pavement(args)
    environment = environment_stack.pop()

def _launch_pavement(args):
    mod = types.ModuleType("pavement")
    try:
        execfile(environment.pavement_file, mod.__dict__)
        environment.pavement = mod
        _process_commands(args)
    except PavementError, e:
        print "\n\n*** Problem with pavement:\n%s\n%s\n\n" % (
                    os.path.abspath(environment.pavement_file), e)

def main(args=None):
    global environment
    if args is None:
        if len(sys.argv) > 1:
            args = sys.argv[1:]
        else:
            args = []
    environment = Environment()

    # need to parse args to recover pavement-file to read before executing
    args = _parse_global_options(args)
    _launch_pavement(args)
    
