"""Convenience functions for working with bzr.

This module does not include any tasks, only functions."""

from paver.options import Bunch
from bzrlib.builtins import cmd_branch, cmd_checkout, cmd_update, cmd_pull, cmd_version_info
from StringIO import StringIO

__all__ = ["checkout", "update", "branch", "pull", "info"]

def do_bzr_cmd(cmd_class, output=True, **kwarg):
    if output:
        import bzrlib.ui
        from bzrlib.ui.text import TextUIFactory
        bzrlib.ui.ui_factory = TextUIFactory()
    cmd = cmd_class()
    if output:
        cmd._setup_outf()
    else:
        cmd.outf = StringIO()
    cmd.run(**kwarg)

    return cmd.outf

def checkout(url, dest, revision=None):
    """Checkout from the URL to the destination."""
    do_bzr_cmd(cmd_checkout, branch_location=url, to_location=dest, revision=revision)

def update(path='.'):
    """Update the given path."""
    do_bzr_cmd(cmd_update, dir=path)

def branch(url, dest, revision=None):
    """Branch from the given URL to the destination."""
    do_bzr_cmd(cmd_branch, from_location=url, to_location=dest, revision=revision)

def pull(url, revision=None):
    """Pull from the given URL at the optional revision."""
    do_bzr_cmd(cmd_pull, location=url, revision=revision)

def info(location=None):
    """Retrieve the info at location."""
    data = Bunch()
    sio = do_bzr_cmd(cmd_version_info, False, location=location)
    sio.seek(0)

    for line in sio.readlines():
        if not ":" in line:
            continue
        key, value = line.split(":", 1)
        key = key.lower().replace(" ", "_").replace("-", "_")
        data[key] = value.strip()
    return data
