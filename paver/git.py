"""Convenience functions for working with git.

This module does not include any tasks, only functions.

At this point, these functions do not use any kind of library. They require
the git binary on the path."""

from paver.easy import sh, Bunch, path

def clone(url, dest_folder):
    sh("git clone %(url)s %(path)s" % dict(url=url, path=dest_folder) )
