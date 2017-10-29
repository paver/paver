import sys
import os
import copy
import optparse
import re
import types
import inspect
import itertools
import operator
import traceback
import platform
import six

from os.path import *

from six import print_
from paver.version import VERSION

# using six.moves is complicated because we include it and it's thus not at
# the top level
if six.PY3:
    xrange = range

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
        # This conditional fixes an issue which arises if the message contains
        # formatting directives but no args are provided.
        if args:
            output = message % args
        else:
            output = message

        if self._task_output is not None:
            self._task_output.append(output)
        if level > 2 or (level > 1 and not self.quiet) or \
            self.verbose:
            self._print(output)

    def _print(self, output):
        print_(output)
        sys.stdout.flush()

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

    def call_task(self, task_name, args=None, options=None):
        task = self.get_task(task_name)
        if hasattr(task, 'paver_constraint'):
            task.paver_constraint()
        if options:
            for option in options:
                task._set_value_to_task(task_name, option, None, options[option])

        if args is not None and task.consume_args > 0:
            args = _consume_nargs(task, args)
        elif args and (task.consume_args == 0):
            raise BuildFailure("Task %s is not decorated with @consume_(n)args,"
                                "but has been called with them" % task)
        task()

    def _run_task(self, task_name, needs, func):
        try:
            getfullargspec = inspect.getfullargspec
        except AttributeError:
            (funcargs, varargs, varkw, defaults) = inspect.getargspec(func)
        else:
            (funcargs, varargs, varkw, defaults, _, _, _) = getfullargspec(func)
        kw = dict()
        for i in xrange(0, len(funcargs)):
            arg = funcargs[i]
            if arg == 'env':
                kw['env'] = self
            # Keyword arguments do now need to be in the environment
            elif (defaults is not None and
                  (i - (len(funcargs) - len(defaults))) >= 0):
                pass
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
            except Exception:
                e = sys.exc_info()[1]
                self._print("""

Captured Task Output:
---------------------
""")
                self._print("\n".join(map(str, self._task_output)))
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
                try:
                    item = getattr(module, name, None)
                except ImportError:
                    item = None
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

def _consume_nargs(task, args):
    """Set up args in environment function of number of args task consumes.
    """
    if task.consume_args > 0:
        if (args is None) or (task.consume_args != float('inf') and \
                              (len(args) < task.consume_args)):
            args_consumed = ""
            if task.consume_args == float('inf'):
                args_consumed = "all arguments"
            else:
                args_consumed = "exactly %i argument" % task.consume_args
                args_consumed += "s" if (task.consume_args > 1) else ""

            args_passed = "none" if args is None \
                                 else "got only %i" % len(args)

            raise BuildFailure("%s consumes %s, %s" %  \
                                (task.name, args_consumed, args_passed))

        _args = args if task.consume_args == float('inf') \
                     else args[:task.consume_args]
        try:
            environment.options.args = _args
        except AttributeError:
            pass
        environment.args = _args

        return [] if task.consume_args == float('inf') \
                  else args[task.consume_args:]

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
        module = __import__(full_mod_name, globals(), locals(), [mod_name])
    except ImportError:
        return None
    return getattr(module, func_name, None)

class Task(object):
    called = False
    consume_args = 0
    no_auto = False

    __doc__ = ""

    def __init__(self, func):

        super(Task, self).__init__()

        self.func = func
        self.needs = []
        self.might_call = []
        self.__name__ = func.__name__
        self.shortname = func.__name__
        self.name = "%s.%s" % (func.__module__, func.__name__)
        self.option_names = set()
        self.user_options = []
        self.negative_opt = {}
        self.share_options_with = []
        self._parser = None
        self.use_virtualenv = None
        self.virtualenv_dir = None

        try:
            self.__doc__ = func.__doc__
        except AttributeError:
            pass

    def __call__(self, *args, **kw):
        if self.use_virtualenv and self.virtualenv_dir:
            #TODO: Environment recovery?
            if platform.system() == 'Windows':
                bin_dir = 'Scripts'
            else:
                bin_dir = 'bin'
            activate_this = join(self.virtualenv_dir, bin_dir, "activate_this.py")
            with open(activate_this) as f:
                s = f.read()
            code = compile(s, activate_this, 'exec')
            exec(code, dict(__file__=activate_this))
        retval = environment._run_task(self.name, self.needs, self.func)
        self.called = True
        return retval

    def __repr__(self):
        return "Task: " + self.__name__

    def _make_option_from_tuple(self, option):
        # option is (longname, short, desc)
        longname = option[0]
        if longname and longname.endswith('='):
            action = "store"
            longname = longname[:-1]
        else:
            action = "store_true"

        destination = longname.replace('-', '_')

        opts = []

        if option[1]:
            opts.append('-' + option[1])

        if longname:
            opts.append('--' + longname)

        return optparse.make_option(*opts,
            **dict(action=action, dest=destination, help=option[2]))

    @property
    def parser(self):

        if getattr(self, '_parser', None):
            return self._parser

        self._parser = parser = optparse.OptionParser(add_help_option=False,
            usage="%%prog %s [options]" % self.name)

        parser.disable_interspersed_args()
        parser.add_option('-h', '--help', action="store_true",
                        help="display this help information")

        needs_tasks = [(environment.get_task(task), task) for task in self.needs_closure]

        # backward compatibility: tasks that inherit from Task and override constructor
        if getattr(self, "might_call", None):
            needs_tasks.extend((environment.get_task(task), task) for task in self.might_call)

        shared_tasks = {}
        parser.mirrored_options = {}
        parser.options_to_hide_from_help = []

        for task, task_name in itertools.chain([(self, self.name)], needs_tasks):
            if not task:
                raise PavementError("Task %s needed by %s does not exist"
                    % (task_name, self))

            for option in task.user_options:
                add_options = True
                try:
                    if not isinstance(option, optparse.Option):
                        option = self._make_option_from_tuple(option)

                    environment.debug("Task %s: adding option %s" %
                                     (self.name, str(option)))

                    try:
                        longname = option._long_opts[0]
                    except IndexError:
                        longname = None

                    try:
                        shortname = option._short_opts[0]
                    except IndexError:
                        shortname = None

                    # XXX: this probably needs refactored to handle commands with multiple
                    # long or short options
                    task_share_options_with = task.share_options_with or []
                    task_shares = [environment.get_task(t).name for t in task_share_options_with if environment.get_task(t)]

                    if self.share_options_with or task_shares:
                        options = (shortname, longname)

                        # either I am sharing with dependent task
                        # ...or it can share with me
                        if (
                                options in shared_tasks and (shared_tasks[options] or self.share_options_with)
                            ) \
                            or \
                            (
                                self.name in [environment.get_task(t).name for t in task_share_options_with if environment.get_task(t)]
                            ):
                            environment.debug("Task %s: NOT adding option %s," \
                                "already present; setting up mirror" %
                                             (self.name, option))

                            if option.dest not in parser.mirrored_options:
                                parser.mirrored_options[option.dest] = []
                            parser.mirrored_options[option.dest].append(task_name)
                            add_options = False

                        if options not in shared_tasks:
                            shared_tasks[options] = set()

                        if task_share_options_with:
                            shared_tasks[options] |= set(task_share_options_with)

                    if add_options:
                        try:
                            parser.add_option(option)
                        except optparse.OptionConflictError:
                            raise PavementError("""In setting command options for %r,
    option %s for %r is already in use
    by another task in the dependency chain.""" % (self, option, task))
                        # add just names; longname now contains --initial-dashes
                        self.option_names.add((task.shortname, longname[2:], option.dest))

                        if getattr(task, 'no_help', False):
                            if shortname:
                                parser.options_to_hide_from_help.append(shortname)
                            elif longname:
                                parser.options_to_hide_from_help.append(longname)
                except IndexError:
                    raise PavementError("Invalid option format provided for %r: %s"
                                        % (self, option))

        return parser

    def display_help(self, parser=None):
        if not parser:
            parser = self.parser

        for opt_str in parser.options_to_hide_from_help:
            try:
                parser.remove_option(opt_str)
            except ValueError:
                environment.error("Option %s added for hiding, but it's not in parser...?" % opt_str)

        name = self.name
        print_("\n%s" % name)
        print_("-" * len(name))
        parser.print_help()
        print_()
        print_(self.__doc__)
        print_()

    def _set_value_to_task(self, task_name, option_name, dist_option_name, value):
        import paver.options
        try:
            optholder = environment.options[task_name]
        except KeyError:
            optholder = paver.options.Bunch()
            environment.options[task_name] = optholder

        if value is not None:
            if dist_option_name in getattr(self, "negative_opt"):
                optholder[self.negative_opt[dist_option_name].replace('-', '_')] = False
            else:
                optholder[option_name] = value

    def parse_args(self, args):
        import paver.options
        environment.debug("Task %s: Parsing args %s" % (self.name, args))
        environment.options.setdefault(self.shortname, paver.options.Bunch())
        parser = self.parser
        options, args = parser.parse_args(args)

        if options.help:
            self.display_help(parser)
            sys.exit(0)

        for task_name, option_name, option_dest in self.option_names:
            if option_name != option_dest:
                dist_option_name = copy.copy(option_name)
                option_name = option_dest
            else:
                dist_option_name = option_name
            option_name = option_name.replace('-', '_')

            value = getattr(options, option_name, getattr(options, option_dest))

            self._set_value_to_task(task_name, option_name, dist_option_name, value)

            if option_name in parser.mirrored_options:
                for task_name in parser.mirrored_options[option_name]:
                    self._set_value_to_task(task_name, option_name, dist_option_name, value)

        return args

    @property
    def description(self):
        if self.__doc__:
            return re.split("\.\s+", self.__doc__, maxsplit=1)[0].strip()
        else:
            return ""

    @property
    def needs_closure(self):
        stack = [] + self.needs
        rv = []
        while stack:
            top = stack.pop()
            if top not in rv:
                rv.append(top)
                needs = []
                if environment.get_task(top):
                    deptask = environment.get_task(top)

                    if not isinstance(deptask, Task):
                        raise BuildFailure("Dependency %s is not a Task (only tasks allowed in @needs)" % deptask)

                    needs = deptask.needs

                for t in needs:
                    stack.append(t)

        return rv

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
        if isinstance(req, six.string_types):
            needs_list.append(req)
        elif isinstance(req, (list, tuple)):
            needs_list.extend(req)
        else:
            raise PavementError("'needs' decorator requires a list or string "
                                "but got %s" % req)
        return func
    return entangle

def cmdopts(options, share_with=None):
    """Sets the command line options that can be set for this task.
    This uses the same format as the distutils command line option
    parser. It's a list of tuples, each with three elements:
    long option name, short option, description.

    If the long option name ends with '=', that means that the
    option takes a value. Otherwise the option is just boolean.
    All of the options will be stored in the options dict with
    the name of the task. Each value that gets stored in that
    dict will be stored with a key that is based on the long option
    name (the only difference is that - is replaced by _).

    """
    def entangle(func):
        func = task(func)
        func.user_options = options
        func.share_options_with = share_with
        return func
    return entangle

def might_call(*args):
    """

    """
    def entangle(func):
        req = args
        func = task(func)
        might_call = func.might_call
        if len(req) == 1:
            req = req[0]
        if isinstance(req, six.string_types):
            might_call.append(req)
        elif isinstance(req, (list, tuple)):
            might_call.extend(req)
        else:
            raise PavementError("'might_call' decorator requires a list or string "
                                "but got %s" % req)
        return func
    return entangle


def consume_nargs(nb_args=None):
    """All specified command line arguments that appear after this task on the
    command line will be placed in options.args.
    By default, if :data:`nb_args` is not specified, all arguments will
    be consumed.

    :param nb_args:     number of arguments the decorated function consumes
    :type nb_args:      ``int``

    """
    def consume_args_wrapper(func):
        func = task(func)
        func.consume_args = nb_args if nb_args is not None else float('inf')
        return func

    return consume_args_wrapper

def consume_args(func):
    """Any command line arguments that appear after this task on the
    command line will be placed in options.args."""
    return consume_nargs()(func)

def no_auto(func):
    """Specify that this task does not depend on the auto task,
    and don't run the auto task just for this one."""
    func = task(func)
    func.no_auto = True
    return func

def no_help(func):
    """Do not show this task in paver help."""
    func = task(func)
    func.no_help = True
    return func

def _preparse(args):
    task = None
    taskname = None
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
            taskname = arg
            task = environment.get_task(taskname)
            if task is None:
                raise BuildFailure("Unknown task: %s" % taskname)
            break
    return task, taskname, args

def _parse_global_options(args):
    # this is where global options should be dealt with
    parser = optparse.OptionParser(usage=
        """Usage: %prog [global options] taskname [task options] """
        """[taskname [taskoptions]]""", version="Paver %s" % (VERSION),
        add_help_option=False)

    environment.help_function = parser.print_help

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
    parser.add_option('-h', "--help", action="store_true",
                    help="display this help information")
    parser.add_option("--propagate-traceback", action="store_true",
                    help="propagate traceback, do not hide it under BuildFailure"
                        "(for debugging)")
    parser.add_option('-x', '--command-packages', action="store",
                    help="list of packages that provide distutils commands")
    parser.set_defaults(file=environment.pavement_file)

    parser.disable_interspersed_args()
    options, args = parser.parse_args(args)
    if options.help:
        args.insert(0, "help")
    for key, value in vars(options).items():
        setattr(environment, key, value)

    return args

def _parse_command_line(args):
    task, taskname, args = _preparse(args)

    if not task:
        args = _parse_global_options(args)
        if not args:
            return None, []

        taskname = args.pop(0)
        task = environment.get_task(taskname)

        if not task:
            raise BuildFailure("Unknown task: %s" % taskname)

    if not isinstance(task, Task):
        raise BuildFailure("%s is not a Task" % taskname)

    if task.consume_args != float('inf'):
        args = task.parse_args(args)
    if task.consume_args > 0:
        args = _consume_nargs(task, args)

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
    # trick taken from python3porting.org
    return (a > b) - (b < a)

if six.PY3:
    import functools
    _task_names_key = functools.cmp_to_key(_cmp_task_names)

def _group_by_module(items):
    def key(item):
        dotpos = item.name.rfind('.')
        return item.name[:dotpos]

    maxlen = max(len(item.shortname) for item in items)
    groups = itertools.groupby(sorted(items, key=operator.attrgetter('name')), key=key)
    return maxlen, groups

@task
@no_auto
@consume_args
def help(args, help_function):
    """This help display."""
    if args:
        task_name = args[0]
        task = environment.get_task(task_name)
        if not task:
            print_("Task not found: %s" % (task_name))
            return

        task.display_help()
        return

    help_function()

    task_list = environment.get_tasks()
    if six.PY3:
        task_list = sorted(task_list, key=_task_names_key)
    else:
        task_list = sorted(task_list, cmp=_cmp_task_names)
    maxlen, task_list = _group_by_module(task_list)
    fmt = "  %-" + str(maxlen) + "s - %s"
    for group_name, group in task_list:
        print_("\nTasks from %s:" % (group_name))
        for task in group:
            if not getattr(task, "no_help", False):
                print_(fmt % (task.shortname, task.description))

def _process_commands(args, auto_pending=False):
    first_loop = True
    while True:
        task, args = _parse_command_line(args)
        if auto_pending:
            if task and not task.no_auto:
                environment.call_task('auto')
                auto_pending=False
        if task is None:
            if first_loop:
                task = environment.get_task('default')
                if not task:
                    break
            else:
                break
        task()
        first_loop = False

def call_pavement(new_pavement, args):
    if isinstance(args, six.string_types):
        args = args.split()
    global environment
    environment_stack.append(environment)
    environment = Environment()
    cwd = os.getcwd()
    dirname, basename = split(new_pavement)
    environment.pavement_file = basename
    try:
        if dirname:
            os.chdir(dirname)
        _launch_pavement(args)
    finally:
        os.chdir(cwd)
    environment = environment_stack.pop()

def _launch_pavement(args):
    mod = types.ModuleType("pavement")
    environment.pavement = mod

    if not exists(environment.pavement_file):
        environment.pavement_file = None
        six.exec_("from paver.easy import *\n", mod.__dict__)
        _process_commands(args)
        return

    mod.__file__ = environment.pavement_file
    try:
        pf = open(environment.pavement_file)
        try:
            source = pf.read()
        finally:
            pf.close()
        exec(compile(source, environment.pavement_file, 'exec'), mod.__dict__)
        auto_task = getattr(mod, 'auto', None)
        auto_pending = isinstance(auto_task, Task)

        from paver.misctasks import generate_setup, minilib
        resident_tasks = {
            'help': help,
            'generate_setup': generate_setup,
            'minilib': minilib,
            }
        mod.__dict__.update(resident_tasks)

        _process_commands(args, auto_pending=auto_pending)
    except PavementError:
        e = sys.exc_info()[1]
        # this is hacky, but it is needed if problem would occur within
        # argument parsing, which is actually quite common
        if getattr(environment.options, "propagate_traceback", False) \
            or '--propagate-traceback' in args:
            raise
        print_("\n\n*** Problem with pavement:\n%s\n%s\n\n" % (
                    abspath(environment.pavement_file), e))

def main(args=None):
    global environment
    if args is None:
        args = sys.argv[1:]
    environment = Environment()

    # need to parse args to recover pavement-file to read before executing
    try:
        args = _parse_global_options(args)
        _launch_pavement(args)
    except BuildFailure:
        e = sys.exc_info()[1]
        environment.error("Build failed: %s", e)
        sys.exit(1)
