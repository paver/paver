from paver import git, runtime
from paver.tests.mock import Mock, patch

@patch(git, "sh")
def test_simple_clone(sh):
    git.clone("git://foo/foo.git", "bar")
    assert sh.called
    assert sh.call_args[0][0] == "git clone git://foo/foo.git bar"

