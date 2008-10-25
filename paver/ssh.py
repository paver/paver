"""Functions for accessing remote hosts.

At present, these are implemented by calling ssh's command line programs.
"""

from paver.runtime import sh

def scp(source, dest):
    """Copy the source file to the destination."""
    sh("scp %s %s" % (source, dest))
    