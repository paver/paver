"""Convenience functions for working with mercurial

This module does not include any tasks, only functions.

At this point, these functions do not use any kind of library.  They require
the hg binary on the PATH."""

from paver.easy import sh


def clone(url, dest_folder, rev=None):
    """Clone a mercurial repository.

    Parameters:
        url (string): The path to clone the repository from.  Could be local
            or remote.
        dest_folder (string): The local folder where the repository will be
            cloned.
        rev=None (string or None): If specified, the revision to clone to.
            If omitted or `None`, all changes will be cloned.

    Returns:
        None"""
    rev_string = ''
    if rev:
        rev_string = ' -r %s' % rev

    sh('hg clone{rev} {url} {dest}'.format(
        rev=rev_string, url=url, dest=dest_folder))


def pull(repo_path, rev=None, url=None):
    """Pull changes into a mercurial repository.

    Parameters:
        repo_path (string): The local path to a mercurial repository.
        rev=None (string or None): If specified, the revision to pull to.
            If omitted or `None`, all changes will be pulled.
        url=None (string or None): If specified, the repository to pull from.
            If omitted or `None`, the default location of the repository will
            be used.

    Returns:
        None"""
    rev_string = ''
    if rev:
        rev_string = ' -r %s' % rev

    url_string = ''
    if url:
        url_string = ' ' + url

    sh('hg pull{rev} -R {repo}{url}'.format(rev=rev_string,
                                            repo=repo_path,
                                            url=url_string))


def latest_tag(repo_path, relative_to='tip'):
    """Get the latest tag from a mercurial repository.

    Parameters:
        repo_path (string): The local path to a mercurial repository.
        relative_to='tip' (string): If provided, the revision to use as
            a reference. Defaults to 'tip'.

    Returns:
        The string name of the latest tag."""

    stdout = sh('hg log --template "{{latesttag}}" -r {rev} -R {repo}'.format(
        rev=relative_to, repo=repo_path), capture=True)

    return stdout.strip()


def update(repo_path, rev='tip', clean=False):
    """Update a mercurial repository to a revision.

    Parameters:
        repo_path (string): The local path to a mercurial repository.
        rev='tip' (string): If provided, the revision to update to.  If
            omitted, 'tip' will be used.
        clean=False (bool): If `True`, the update will discard uncommitted
            changes.

    Returns:
        None"""
    clean_string = ''
    if clean:
        clean_string = ' --clean'

    sh('hg update -r {rev} -R {repo}{clean}'.format(
        rev=rev, repo=repo_path, clean=clean_string))


def branches(repo_path, closed=False):
    """List branches for the target repository.

    Parameters:
        repo_path (string): The local path to a mercurial repository.
        closed=False (bool): Whether to include closed branches in the
            branch list.

    Returns:
        A python tuple.  The first item of the tuple is the current branch.
        The second item of the tuple is a list of the branches"""
    current_branch = sh('hg branch -R {repo}'.format(repo=repo_path),
                        capture=True).strip()

    closed_string = ''
    if closed:
        closed_string = ' --closed'

    stdout_string = sh('hg branches -R {repo}{closed}'.format(
        repo=repo_path, closed=closed_string), capture=True)

    # Branch list comes out in the format:
    # <branchname>        <revnum>:<sha1>
    branches = [line.split()[0] for line in stdout_string.split('\n')
                if len(line) > 0]

    return current_branch, branches
