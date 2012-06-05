"""Helper functions and data structures used by pavements."""

import warnings

warnings.warn("Import from paver.easy instead of paver.runtime",
              DeprecationWarning, 2)

from paver.easy import *

__all__ = ["Bunch", "task", "Task", "needs", "dry", "error",
           "info", "debug", "call_task", "require_keys", "sh", "options",
           "BuildFailure", "PavementError", "path", 'cmdopts', "consume_args"]


def call_task(task_name, options=None):
    """DEPRECATED. Just call the task instead.
    
    Calls the desired task, including any tasks upon which that task
    depends. options is an optional dictionary that will be added
    to the option lookup search order.
    
    You can always call a task directly by calling the function directly.
    But, if you do so the dependencies aren't called. call_task ensures
    that these are called.
    
    Note that call_task will only call the task `once` during a given
    build as long as the options remain the same. If the options are
    changed, the task will be called again."""
    warnings.warn("Just call the function instead of using call_task",
                  DeprecationWarning, 2)
    task = environment.get_task(task_name)
    task()

def require_keys(keys):
    """GONE. There is no equivalent in Paver 1.0. Calling this
    will raise an exception.
    
    A set of dotted-notation keys that must be present in the
    options for this task to be relevant.
    
    """
    raise PavementError("require_keys is no longer available.")


class PaverImportError(ImportError):
    pass
