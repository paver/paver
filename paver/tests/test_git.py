from paver import git, easy
from paver.tests.mock import Mock, patch

import os

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

@patch(git, "sh")
def test_simple_branch_checkout(sh):
    git.branch_checkout("my_branch", path="repo_path")
    assert sh.called
    assert sh.call_args[0][0] == "cd repo_path; git checkout my_branch"
    
@patch(git, "sh")
def test_branch_chekout_cwd(sh):
    """it should get the CWD and assume that is the repo"""
    
    git.branch_checkout("my_branch")
    assert sh.called
    assert sh.call_args[0][0] == "cd %(current_path)s; git checkout my_branch" % dict(
        current_path=os.getcwd()
    )
    
@patch(git, "sh")
def test_branch_list_correctly_parses_git_output(sh):
    output = git.branch_list(path="repo_path", __override__="""
* git_support
  master
  virtualenv_in_folder
    """)
    
    assert output == ("git_support", ["git_support", "master", "virtualenv_in_folder"])
    
@patch(git, "sh")
def test_branch_list_correctly_parses_remote_branch_output(sh):
    output = git.branch_list(path="repo_path", 
        remote_branches_only = True,
        __override__="""
    github/gh-pages
    github/git_support
    github/master""")
    
    assert output == ('',
        ["github/gh-pages", "github/git_support", "github/master"])

@patch(git, "sh")
def test_branch_track_remote(sh):
    git.branch_track_remote("origin/alpha_two", path="repo_path")
    
    assert sh.called
    assert sh.call_args[0][0] == "cd %(current_path)s; git checkout -b alpha_two --track origin/alpha_two" % dict(
        current_path="repo_path"
    )
     