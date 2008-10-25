from paver import runtime
from paver.tests.mock import patch, Mock
import subprocess # for runtime.sh tests


def test_basic_namespace_as_dictionary():
    ns = runtime.Namespace(foo=1, bar=2)
    assert ns.foo == 1
    assert ns['bar'] == 2
    ns.bar = 3
    assert ns['bar'] == 3
    ns.new = 4
    assert ns.new == 4

def test_default_namespace_searching():
    ns = runtime.Namespace()
    ns.val = 0
    ns.foo = runtime.Bunch(foo=1, bar=2, baz=3, blorg=6)
    ns.bar = runtime.Bunch(foo=4, baz=5, bop=7, val=8)
    assert ns.val == 0, "Top namespace has priority"
    assert ns.foo == runtime.Bunch(foo=1, bar=2, baz=3, blorg=6)
    assert ns.foo.foo == 1
    assert ns.bar.foo == 4
    assert ns.baz == 5
    assert ns.blorg == 6
    
    try:
        ns['does not exist']
        assert False, "expected key error for missing item"
    except KeyError:
        pass
    
    del ns['val']
    
    assert ns.val == 8, "Now getting val from inner dict"
    
    del ns.bar.val
    
    try:
        a = ns['val']
        assert False, "expected exception for deleted item %s" % (ns)
    except KeyError:
        pass
    
    del ns.foo
    assert ns._sections == ['bar']

def test_clear():
    ns = runtime.Namespace(foo=runtime.Bunch(bar=1))
    ns.order('foo')
    ns.clear()
    assert len(ns) == 0
    assert len(ns._sections) == 0
    assert ns._ordering == None

def test_search_order_is_adjustable():
    ns = runtime.Namespace(
        bar=runtime.Bunch(val=1, blorg=4)
    )
    ns.baz=runtime.Bunch(val=2, bop=5)
    ns.foo=runtime.Bunch(val=3, bam=6)

    assert ns.blorg == 4
    assert ns.val == 3
    
    ns.order('baz')
    assert ns.val == 2
    assert ns.bop == 5
    try:
        ns.bam
        assert False, "expected attribute error for item not in search"
    except AttributeError:
        pass
    
    ns.order('bar', 'baz')
    assert ns.val == 1
    assert ns.blorg == 4
    assert ns.bop == 5
    
    ns.order('baz', add_rest=True)
    assert ns.val == 2
    assert ns.bam == 6

def test_update():
    ns = runtime.Namespace()
    ns.update(foo=runtime.Bunch(val=2))
    assert ns._sections == ['foo'], str(ns._sections)
    ns.update([('bar', runtime.Bunch(val=2))])
    assert ns._sections == ['bar', 'foo'], str(ns._sections)
    ns.update(dict(baz=runtime.Bunch(val=3)))
    assert ns._sections == ['baz', 'bar', 'foo'], str(ns._sections)
    ns(hi='there')
    assert ns.hi == 'there'
    
def test_setdefault():
    ns = runtime.Namespace()
    ns.setdefault('foo', runtime.Bunch())
    assert ns._sections == ['foo'], ns._sections
    
def test_callables_in_bunch():
    b = runtime.Bunch(foo = lambda: "hi")
    assert b.foo == "hi", "foo was: %s" % b.foo
    
def test_setdotted_values():
    ns = runtime.Namespace()
    ns.foo = runtime.Bunch()
    ns.setdotted("foo.bar", "baz")
    assert ns.foo.bar == "baz"
    ns.setdotted("bligger.bar", "flilling")
    assert ns.bligger.bar == "flilling"
    ns.val = 10
    try:
        ns.setdotted("val.yo", 42)
        assert False, "Expected exception when a value is found instead of bunch"
    except runtime.BuildFailure:
        pass
    
def test_add_dict_to_order():
    ns = runtime.Namespace()
    ns.foo = runtime.Bunch(val="yo")
    ns.bar = runtime.Bunch(val="there")
    assert ns.val == "there"
    ns.order('foo')
    assert ns.val == "yo"
    ns.order(dict(val="new"), add_rest=True)
    assert ns.val == "new", "Got %s" % (ns.val)

@patch(subprocess, "call")
def test_sh_raises_BuildFailure(call):
    call.return_value = 1
    try:
        runtime.sh('foo')
    except runtime.BuildFailure, e:
        assert e.args == (1, )
    else:
        assert False, 'Failed to raise BuildFailure'

    assert call.called
    assert call.call_args[0][0] == 'foo'
    assert call.call_args[1]['shell'] == True

@patch(subprocess, "Popen")
def test_sh_with_capture_raises_BuildFailure(popen):
    popen.return_value = Mock()
    popen.return_value.returncode = 1
    try:
        runtime.sh('foo', capture=True)
    except runtime.BuildFailure, e:
        assert e.args == (1, )
    else:
        assert False, 'Failed to raise BuildFailure'

    assert popen.called
    assert popen.call_args[0][0] == 'foo'
    assert popen.call_args[1]['shell'] == True
    assert popen.call_args[1]['stdout'] == subprocess.PIPE

@patch(subprocess, "call")
def test_sh_ignores_error(call):
    call.return_value = 1
    runtime.sh('foo', ignore_error=True)

    assert call.called
    assert call.call_args[0][0] == 'foo'
    assert call.call_args[1]['shell'] == True

@patch(subprocess, "Popen")
def test_sh_ignores_with_capture(popen):
    popen.return_value = Mock()
    popen.return_value.returncode = 1
    runtime.sh('foo', capture=True, ignore_error=True)

    assert popen.called
    assert popen.call_args[0][0] == 'foo'
    assert popen.call_args[1]['shell'] == True
    assert popen.call_args[1]['stdout'] == subprocess.PIPE

