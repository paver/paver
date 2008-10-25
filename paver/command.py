"""Paver's command-line driver"""

import os
import sys
import optparse

from paver import defaults
from paver import runtime
from paver import setuputils

def load_build(source):
    """Load's the pavement into paver.defaults"""
    module = compile(source, "pavement.py", "exec")
    exec module in defaults.__dict__

def finalize_env(options):
    """prune out tasks that are not relevant"""
    for name, task in runtime.TASKS.items():
        if not task.valid(options):
            del runtime.TASKS[name]

def _check_file():
    """Verify that a pavement exists"""
    if not os.path.exists("pavement.py"):
        print "WARNING: No pavement.py file here!"
        return False
    return True
    
def _read_pavement():
    """Read the pavement"""
    return open("pavement.py").read().strip()

def main():
    """The main function called by the command."""
    has_pavement = _check_file()
    
    if has_pavement:
        load_build(_read_pavement())
    args = sys.argv
    
    if len(args) == 1:
        args.append("help")
    
    finalize_env(runtime.options)
    
    setupargs = runtime.options.get('setup', dict())
    setupargs['distclass'] = setuputils.Distribution
    setuputils.setup(**setupargs)
