from mock import patch
from paver import hg


@patch('paver.hg.sh')
def test_simple_clone(sh):
    hg.clone("ssh://foo/foo", "bar")
    assert sh.called
    assert sh.call_args[0][0] == "hg clone ssh://foo/foo bar"


@patch('paver.hg.sh')
def test_simple_clone_to_rev(sh):
    hg.clone('ssh://foo/bar', 'baz', 'bam')
    assert sh.called
    assert sh.call_args[0][0] == 'hg clone -r bam ssh://foo/bar baz'


@patch('paver.hg.sh')
def test_pull_simple(sh):
    hg.pull('foo')
    assert sh.called
    assert sh.call_args[0][0] == 'hg pull -R foo'


@patch('paver.hg.sh')
def test_pull_rev(sh):
    hg.pull('foo', 'bar')
    assert sh.called
    assert sh.call_args[0][0] == 'hg pull -r bar -R foo'


@patch('paver.hg.sh')
def test_pull_rev_url(sh):
    hg.pull('foo', 'bar', 'baz')
    assert sh.called
    assert sh.call_args[0][0] == 'hg pull -r bar -R foo baz', sh.call_args[0][0]


def test_latest_tag():
    with patch('paver.hg.sh') as sh:
        sh.return_value = 'example'

        returned_value = hg.latest_tag('foo')
        assert returned_value == 'example', returned_value


@patch('paver.hg.sh')
def test_update_simple(sh):
    hg.update('foo')
    assert sh.called
    assert sh.call_args[0][0] == 'hg update -r tip -R foo'


@patch('paver.hg.sh')
def test_update_to_rev(sh):
    hg.update('foo', 'bar')
    assert sh.called
    assert sh.call_args[0][0] == 'hg update -r bar -R foo'


@patch('paver.hg.sh')
def test_update_to_rev_and_clean(sh):
    hg.update('foo', 'bar', True)
    assert sh.called
    assert sh.call_args[0][0] == 'hg update -r bar -R foo --clean'


@patch('paver.hg.sh')
def test_branches_with_closed(sh):
    sh.side_effect = [
        'tag1', ('branch1                123:9871230987\n'
                 'branch2                456:1957091982\n')]
    current_branch, branches = hg.branches('foo', True)

    assert sh.called
    assert sh.call_args_list[0][0][0] == 'hg branch -R foo'
    assert sh.call_args_list[1][0][0] == 'hg branches -R foo --closed'

    assert current_branch == 'tag1'
    assert branches == ['branch1', 'branch2']

