import subprocess
import sys

from paver import tasks
from paver.options import Bunch

def dry(message, func, *args, **kw):
    """Wraps a function that performs a destructive operation, so that
    nothing will happen when a dry run is requested.

    Runs func with the given arguments and keyword arguments. If this
    is a dry run, print the message rather than running the function."""
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
            raise BuildFailure("Subprocess return code: %s" % returncode)

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
cmdopts = tasks.cmdopts
consume_args = tasks.consume_args
no_auto = tasks.no_auto
BuildFailure = tasks.BuildFailure
PavementError = tasks.PavementError

# these are down here to avoid circular dependencies. Ideally, nothing would
# be using paver.easy other than pavements.
if sys.version_info > (2,5):
    from paver.path25 import path, pushd
else:
    from paver.path import path

import paver.misctasks
