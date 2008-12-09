from paver.easy import *

from paver import doctools, tasks, options

def test_sections_from_file():
    simpletext = """# [[[section foo]]]
#Foo!
# [[[endsection]]]
"""
    f = doctools.SectionedFile(from_string=simpletext)
    assert len(f) == 1, "Sections found: %s" % f
    assert f['foo'] == "#Foo!\n", "Foo section contained: '%s'" % f['foo']

def display(msg, *args):
    print msg % args

doctools.debug = display

def test_nested_sections():
    myfile = """
[[[section bar]]]
    Hi there.
    [[[section baz]]]
    Yo.
    [[[endsection]]]
[[[endsection]]]
"""
    f = doctools.SectionedFile(from_string=myfile)
    assert len(f) == 2
    assert f['bar'] == """    Hi there.
    Yo.
""", "Bar was: '%s'" % (f['bar'])
    assert f['bar.baz'] == """    Yo.
"""

def test_section_doesnt_end():
    myfile = """
[[[section bar]]]
Yo.
"""
    try:
        f = doctools.SectionedFile(from_string=myfile)
        assert False, "Expected a BuildFailure"
    except BuildFailure, e:
        assert str(e) == """No end marker for section 'bar'
(in file 'None', starts at line 2)""", "error was: %s" % (str(e))

def test_section_already_defined():
    myfile = """
[[[section foo]]]
First one.
[[[endsection]]]

[[[section foo]]]
Second one.
[[[endsection]]]
"""
    try:
        f = doctools.SectionedFile(from_string=myfile)
        assert False, "Expected a BuildFailure"
    except BuildFailure, e:
        assert str(e) == """section 'foo' redefined
(in file 'None', first section at line 2, second at line 6)""", \
        "error was: %s" % (str(e))
        

def test_endmarker_without_start():
    myfile = """
[[[section foo]]]
This is a good section.
[[[endsection]]]

[[[endsection]]]
"""
    try:
        f = doctools.SectionedFile(from_string=myfile)
        assert False, "Expected a BuildFailure"
    except BuildFailure, e:
        assert str(e) == """End section marker with no starting marker
(in file 'None', at line 6)""", \
        "error was: %s" % (str(e))

def test_whole_file():
    myfile = """
[[[section bar]]]
    Hi there.
    [[[section baz]]]
    Yo.
    [[[endsection]]]
[[[endsection]]]
"""
    f = doctools.SectionedFile(from_string=myfile)
    assert f.all == """
    Hi there.
    Yo.
""", "All was: %s" % (f.all)
    
def test_bad_section():
    f = doctools.SectionedFile(from_string="")
    try:
        f['foo']
        assert False, "Should have a BuildFailure"
    except BuildFailure, e:
        assert str(e) == "No section 'foo' in file 'None'", \
               "Error: '%s'" % (str(e))
    
def test_include_lookup():
    basedir = path(__file__).dirname() / "data"
    include = doctools.Includer(basedir, include_markers={})
    everything = include("t1.py")
    assert everything == """# file 't1.py'
print "Hi!"

print "More"
""", "Everything was: '%s'" % (everything)
    first = include("t1.py", "first")
    assert first == """# section 'first' in file 't1.py'
print "Hi!"
""", "First was '%s'" % (first)
    second = include("t2.py", "second.inner")
    assert second == """# section 'second.inner' in file 't2.py'
print sys.path
""", "Second was '%s'" % (second)
    
def test_cogging():
    env = tasks.Environment(doctools)
    tasks.environment = env
    opt = env.options
    opt.cog = options.Bunch()
    basedir = path(__file__).dirname()
    opt.cog.basedir = basedir
    opt.cog.pattern = "*.rst"
    opt.cog.includedir = basedir / "data"
    env.options = opt
    doctools.cog()
    textfile = basedir / "data/textfile.rst"
    data = open(textfile).read()
    print data
    assert "print sys.path" in data
    doctools.uncog()
    data = open(textfile).read()
    assert "print sys.path" not in data
    
def test_cogging_with_markers_removed():
    env = tasks.Environment(doctools)
    tasks.environment = env
    opt = env.options
    opt.cog = Bunch()
    basedir = path(__file__).dirname()
    opt.cog.basedir = basedir
    opt.cog.pattern = "*.rst"
    opt.cog.includedir = basedir / "data"
    opt.cog.delete_code = True
    env.options = opt
    textfile = basedir / "data/textfile.rst"
    original_data = open(textfile).read()
    try:
        doctools.cog()
        data = open(textfile).read()
        print data
        assert "[[[cog" not in data
    finally:
        open(textfile, "w").write(original_data)
    