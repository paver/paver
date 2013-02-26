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
from paver.path import path, pushd
from paver.shell import sh

import paver.misctasks
