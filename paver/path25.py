"""Python 2.5+ path module that adds with-statement features."""
from __future__ import with_statement

import os
from contextlib import contextmanager

from paver.path import path
from paver import tasks

__all__ = ['path', 'pushd']

@contextmanager
def pushd(dir):
    '''A context manager (Python 2.5+ only) for stepping into a 
    directory and automatically coming back to the previous one. 
    The original directory is returned. Usage is like this::
    
        from __future__ import with_statement
        # the above line is only needed for Python 2.5
        
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
