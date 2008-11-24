from paver import options, tasks

def test_basic_namespace_as_dictionary():
    ns = options.Namespace(foo=1, bar=2)
    assert ns.foo == 1
    assert ns['bar'] == 2
    ns.bar = 3
    assert ns['bar'] == 3
    ns.new = 4
    assert ns.new == 4

def test_default_namespace_searching():
    ns = options.Namespace()
    ns.val = 0
    ns.foo = options.Bunch(foo=1, bar=2, baz=3, blorg=6)
    ns.bar = options.Bunch(foo=4, baz=5, bop=7, val=8)
    assert ns.val == 0, "Top namespace has priority"
    assert ns.foo == options.Bunch(foo=1, bar=2, baz=3, blorg=6)
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
    ns = options.Namespace(foo=options.Bunch(bar=1))
    ns.order('foo')
    ns.clear()
    assert len(ns) == 0
    assert len(ns._sections) == 0
    assert ns._ordering == None

def test_search_order_is_adjustable():
    ns = options.Namespace(
        bar=options.Bunch(val=1, blorg=4)
    )
    ns.baz=options.Bunch(val=2, bop=5)
    ns.foo=options.Bunch(val=3, bam=6)

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
    ns = options.Namespace()
    ns.update(foo=options.Bunch(val=2))
    assert ns._sections == ['foo'], str(ns._sections)
    ns.update([('bar', options.Bunch(val=2))])
    assert ns._sections == ['bar', 'foo'], str(ns._sections)
    ns.update(dict(baz=options.Bunch(val=3)))
    assert ns._sections == ['baz', 'bar', 'foo'], str(ns._sections)
    ns(hi='there')
    assert ns.hi == 'there'
    
def test_setdefault():
    ns = options.Namespace()
    ns.setdefault('foo', options.Bunch())
    assert ns._sections == ['foo'], ns._sections
    
def test_callables_in_bunch():
    b = options.Bunch(foo = lambda: "hi")
    assert b.foo == "hi", "foo was: %s" % b.foo
    
def test_setdotted_values():
    ns = options.Namespace()
    ns.foo = options.Bunch()
    ns.setdotted("foo.bar", "baz")
    assert ns.foo.bar == "baz"
    ns.setdotted("bligger.bar", "flilling")
    assert ns.bligger.bar == "flilling"
    ns.val = 10
    try:
        ns.setdotted("val.yo", 42)
        assert False, "Expected exception when a value is found instead of bunch"
    except options.OptionsError:
        pass
    
def test_add_dict_to_order():
    ns = options.Namespace()
    ns.foo = options.Bunch(val="yo")
    ns.bar = options.Bunch(val="there")
    assert ns.val == "there"
    ns.order('foo')
    assert ns.val == "yo"
    ns.order(dict(val="new"), add_rest=True)
    assert ns.val == "new", "Got %s" % (ns.val)
