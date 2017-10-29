"""
Wrapper around path.py to add dry run support and other paver integration.
"""
import functools
import os
from contextlib import contextmanager
import sys

if sys.version_info[0] == 3:
    from paver.deps.path3 import path as _orig_path
else:
    from paver.deps.path2 import path as _orig_path

from paver import tasks

__all__ = ['path', 'pushd']


@contextmanager
def pushd(dir):
    '''A context manager for stepping into a directory and automatically coming
    back to the previous one. The original directory is returned.
    Usage is like this::

        from paver.easy import *

        @task
        def my_task():
            with pushd('new/directory') as old_dir:
                ...do stuff...
    '''
    old_dir = os.getcwd()
    tasks.environment.info('cd %s' % dir)
    os.chdir(dir)
    try:
        yield old_dir
        tasks.environment.info('cd %s' % old_dir)
    finally:
        os.chdir(old_dir)

class path(_orig_path):
    def chdir(self):
        # compatability with the ancient path.py that had a .chdir() method
        self.__enter__()

# This is used to prevent implementation details of dry'd functions from
# printing redundant information.
# In particular, foo_p methods usually call the foo method internally and
# we don't want to print that information twice.
# We can say that the former implies the latter and call it a day.
_silence_nested_calls = False

def _make_wrapper(name, func):
    from paver.easy import dry

    @functools.wraps(func)
    def wrapper(*args, **kwds):
        global _silence_nested_calls
        msg = None
        if not _silence_nested_calls:
            msg = name + ' ' + ' '.join(map(repr, args))
        try:
            _silence_nested_calls = True
            return dry(msg, func, *args, **kwds)
        finally:
            _silence_nested_calls = False
    return wrapper

_METHOD_BLACKLIST = [
    'rename', 'renames', 'mkdir', 'mkdir_p', 'makedirs', 'makedirs_p',
    'rmdir', 'rmdir_p', 'removedirs', 'removedirs_p', 'touch',
    'remove', 'remove_p', 'unlink', 'unlink_p', 'link', 'symlink',
    'copyfile', 'copymode', 'copystat', 'copy', 'copy2', 'copytree',
    'move', 'rmtree', 'rmtree_p',
    # added atop of original dry run support
    'chown', 'chmod', 'utime', 'write_bytes', 'write_lines', 'write_text'
]


for name in _METHOD_BLACKLIST:
    if not hasattr(_orig_path, name):
        continue
    wrapper = _make_wrapper(name, getattr(_orig_path, name))
    setattr(path, name, wrapper)
