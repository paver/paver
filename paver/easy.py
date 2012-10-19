import subprocess
import sys

from paver import tasks
#needed for paver.easy.* import
from paver.options import Bunch

def dry(message, func, *args, **kw):
    """Wraps a function that performs a destructive operation, so that
    nothing will happen when a dry run is requested.

    Runs func with the given arguments and keyword arguments. If this
    is a dry run, print the message rather than running the function."""
    if message is not None:
        info(message)
    if tasks.environment.dry_run:
        return
    return func(*args, **kw)

def error(message, *args):
    """Displays an error message to the user."""
    tasks.environment.error(message, *args)

def info(message, *args):
    """Displays a message to the user. If the quiet option is specified, the
    message will not be displayed."""
    tasks.environment.info(message, *args)

def debug(message, *args):
    """Displays a message to the user, but only if the verbose flag is
    set."""
    tasks.environment.debug(message, *args)

def sh(command, capture=False, ignore_error=False, cwd=None):
    """Runs an external command. If capture is True, the output of the
    command will be captured and returned as a string.  If the command 
    has a non-zero return code raise a BuildFailure. You can pass
    ignore_error=True to allow non-zero return codes to be allowed to
    pass silently, silently into the night.  If you pass cwd='some/path'
    paver will chdir to 'some/path' before exectuting the command.
    
    If the dry_run option is True, the command will not
    actually be run."""
    def runpipe():
        kwargs = { 'shell': True, 'cwd': cwd}
        if capture:
            kwargs['stderr'] = subprocess.STDOUT
            kwargs['stdout'] = subprocess.PIPE
        p = subprocess.Popen(command, **kwargs)
        p_stdout = p.communicate()[0]
        if p_stdout is not None:
            p_stdout = p_stdout.decode(sys.getdefaultencoding())
        if p.returncode and not ignore_error:
            if capture and p_stdout is not None:
                error(p_stdout)
            raise BuildFailure("Subprocess return code: %d" % p.returncode)

        if capture:
            return p_stdout

    return dry(command, runpipe)


class _SimpleProxy(object):
    __initialized = False
    def __init__(self, rootobj, name):
        self.__rootobj = rootobj
        self.__name = name
        self.__initialized = True
    
    def __get_object(self):
        return getattr(self.__rootobj, self.__name)
        
    def __getattr__(self, attr):
        return getattr(self.__get_object(), attr)
    
    def __setattr__(self, attr, value):
        if self.__initialized:
            setattr(self.__get_object(), attr, value)
        else:
            super(_SimpleProxy, self).__setattr__(attr, value)
            
    def __call__(self, *args, **kw):
        return self.__get_object()(*args, **kw)
    
    def __str__(self):
        return str(self.__get_object())
    
    def __repr__(self):
        return repr(self.__get_object())

environment = _SimpleProxy(tasks, "environment")
options = _SimpleProxy(environment, "options")
call_task = _SimpleProxy(environment, "call_task")

call_pavement = tasks.call_pavement
task = tasks.task
needs = tasks.needs
might_call = tasks.might_call
cmdopts = tasks.cmdopts
consume_args = tasks.consume_args
consume_nargs = tasks.consume_nargs
no_auto = tasks.no_auto
no_help = tasks.no_help
BuildFailure = tasks.BuildFailure
PavementError = tasks.PavementError

# these are down here to avoid circular dependencies. Ideally, nothing would
# be using paver.easy other than pavements.
from paver.path import path

import paver.misctasks
