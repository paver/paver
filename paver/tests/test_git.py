from paver import git, runtime
from paver.tests.mock import Mock, patch

@patch(git, "sh")
def test_simple_clone(sh):
    git.clone("git://foo/foo.git", "bar")
    assert sh.called
    assert sh.call_args[0][0] == "git clone git://foo/foo.git bar"

@patch(git, "sh")
def test_simple_pull(sh):
    git.pull("repo_path", "origin_remote", "master_branch")
    assert sh.called
    assert sh.call_args[0][0] == "cd repo_path; git pull origin_remote master_branch"
