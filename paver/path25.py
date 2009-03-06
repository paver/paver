"""Python 2.5+ path module that adds with-statement features."""
from __future__ import with_statement

import os
from contextlib import contextmanager

from paver.path import path
from paver import tasks

__all__ = ['path', 'pushd']

@contextmanager
def pushd(dir):
    ''' A context manager for pushing into a dir and automatically 
    coming back to the previous one '''
    old_dir = os.getcwd()
    tasks.environment.info('cd %s' % dir)
    os.chdir(dir)
    try:
        yield old_dir
        tasks.environment.info('cd %s' % old_dir)
    finally:
        os.chdir(old_dir)
