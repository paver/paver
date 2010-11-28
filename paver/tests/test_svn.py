from paver import svn
from paver.tests.mock import Mock, patch

@patch(svn, "sh")
def test_simple_checkout(sh):
    svn.checkout("http://foo", "bar")
    assert sh.called
    assert sh.call_args[0][0] == "svn co http://foo bar"

@patch(svn, "sh")
def test_checkout_with_revision(sh):
    svn.checkout("http://foober", "baz", revision="1212")
    assert sh.called
    assert sh.call_args[0][0] == "svn co -r 1212 http://foober baz", sh.call_args[0][0]

@patch(svn, "sh")
def test_simple_update(sh):
    svn.update("bar")
    assert sh.called
    assert sh.call_args[0][0] == "svn up bar"
    sh.reset()
    svn.update()
    assert sh.called
    assert sh.call_args[0][0] == "svn up "

@patch(svn, "sh")
def test_update_with_revision(sh):
    svn.update(revision="1234")
    assert sh.called
    assert sh.call_args[0][0] == "svn up -r 1234 "

@patch(svn, "sh")
def test_simple_export(sh):
    svn.export("http://foo", "bar")
    assert sh.called
    assert sh.call_args[0][0] == "svn export http://foo bar"

@patch(svn, "sh")
def test_export_with_revision(sh):
    svn.export("http://foo", "bar", revision="1234")
    assert sh.called
    assert sh.call_args[0][0] == "svn export -r 1234 http://foo bar"

@patch(svn, "sh")
def test_svn_info(sh):
    sh.return_value="""Path: dojotoolkit/dojo
URL: http://svn.dojotoolkit.org/src/dojo/trunk
Repository Root: http://svn.dojotoolkit.org/src
Repository UUID: 560b804f-0ae3-0310-86f3-f6aa0a117693
Revision: 13301
Node Kind: directory
Schedule: normal
Last Changed Author: jaredj
Last Changed Rev: 13299
Last Changed Date: 2008-04-10 11:44:52 -0400 (Thu, 10 Apr 2008)
"""
    output = svn.info()
    assert sh.called
    assert output.path == "dojotoolkit/dojo"
    assert output.url == "http://svn.dojotoolkit.org/src/dojo/trunk"
    assert output.last_changed_date == "2008-04-10 11:44:52 -0400 (Thu, 10 Apr 2008)"
    
