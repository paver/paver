"""Convenience functions for working with git.

This module does not include any tasks, only functions.

At this point, these functions do not use any kind of library. They require
the git binary on the path."""

from paver.easy import sh, Bunch, path

def clone(url, dest_folder):
    sh("git clone %(url)s %(path)s" % dict(url=url, path=dest_folder) )

def pull(destination, remote="origin", branch="master"):
    """Perform a git pull. Destination must be absolute path"""
    sh("cd %(destination)s; git pull %(remote)s %(branch)s" % dict(
        destination=destination, remote=remote, branch=branch) )
