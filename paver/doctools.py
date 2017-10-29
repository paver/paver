"""Tasks and utility functions and classes for working with project
documentation."""

import re

from paver.easy import *

try:
    import sphinx
    import sphinx.apidoc
    has_sphinx = True
except ImportError:
    has_sphinx = False

try:
    import cogapp
    has_cog = True
except ImportError:
    has_cog = False

def _get_paths():
    """look up the options that determine where all of the files are."""
    opts = options
    docroot = path(opts.get('docroot', 'docs'))
    if not docroot.exists():
        raise BuildFailure("Sphinx documentation root (%s) does not exist."
                           % docroot)
    builddir = docroot / opts.get("builddir", ".build")
    builddir.mkdir_p()
    srcdir = docroot / opts.get("sourcedir", "")
    if not srcdir.exists():
        raise BuildFailure("Sphinx source file dir (%s) does not exist" 
                            % srcdir)
    apidir = None
    if opts.get("apidir", "api"):
        apidir = srcdir / opts.get("apidir", "api")
        apidir.mkdir_p()
    htmldir = builddir / "html"
    htmldir.mkdir_p()
    doctrees = builddir / "doctrees"
    doctrees.mkdir_p()
    return Bunch(locals())

@task
def html():
    """Build HTML documentation using Sphinx. This uses the following
    options in a "sphinx" section of the options.

    docroot
      the root under which Sphinx will be working. Default: docs
    builddir
      directory under the docroot where the resulting files are put.
      default: .build
    sourcedir
      directory under the docroot for the source files
      default: (empty string)
    apidir
      directory under the sourcedir for the auto-generated API docs (empty = don't create them)
      default: api
    """
    if not has_sphinx:
        raise BuildFailure('install sphinx to build html docs')
    options.order('sphinx', add_rest=True)
    paths = _get_paths()

    # First, auto-gen additional sources
    if paths.apidir:
        sphinxopts = ['', '-f', '-o', paths.apidir] + options.setup.packages
        dry("sphinx-apidoc %s" % (" ".join(sphinxopts),), sphinx.apidoc.main, sphinxopts)

    # Then generate HTML tree
    sphinxopts = ['', '-b', 'html', '-d', paths.doctrees, 
        paths.srcdir, paths.htmldir]
    dry("sphinx-build %s" % (" ".join(sphinxopts),), sphinx.main, sphinxopts)

@task
def doc_clean():
    """Clean (delete) the built docs. Specifically, this deletes the
    build directory under the docroot. See the html task for the
    options list."""
    options.order('sphinx', add_rest=True)
    paths = _get_paths()
    paths.builddir.rmtree_p()
    paths.builddir.mkdir_p()
    if paths.apidir and paths.apidir != paths.srcdir:
        paths.apidir.rmtree_p()
        paths.apidir.mkdir_p()

_sectionmarker = re.compile(r'\[\[\[section\s+(.+)\]\]\]')
_endmarker = re.compile(r'\[\[\[endsection\s*.*\]\]\]')

class SectionedFile(object):
    """Loads a file into memory and keeps track of all of the
    sections found in the file. Sections are started with a
    line that looks like this::
    
      [[[section SECTIONNAME]]]
    
    Anything else can appear on the line outside of the brackets
    (so if you're in a source code file, you can put the section marker
    in a comment). The entire lines containing the section markers are
    not included when you request the text from the file.
    
    An end of section marker looks like this::
    
      [[[endsection]]]
      
    Sections can be nested. If you do nest sections, you will use
    dotted notation to refer to the inner sections. For example,
    a "dessert" section within an "order" section would be referred
    to as "order.dessert".
    
    The SectionedFile provides dictionary-style access to the
    sections. If you have a SectionedFile named 'sf',
    sf[sectionname] will give you back a string of that section
    of the file, including any inner sections. There won't
    be any section markers in that string.
    
    You can get the text of the whole file via the ``all`` property
    (for example, ``sf.all``).
    
    Section names must be unique across the file, but inner section
    names are kept track of by the full dotted name. So you can
    have a "dessert" section that is contained within two different
    outer sections.
    
    Ending a section without starting one or ending the file without
    ending a section will yield BuildFailures.
    """
    
    def __init__(self, filename=None, from_string=None):
        """Initialize this SectionedFile object from a file or string.
        If ``from_string`` is provided, that is the text that will
        be used and a filename is optional. If a filename is provided
        it will be used in error messages.
        """
        self.filename = filename
        self.contents = []
        self.sections = {}
        if from_string is not None:
            from six import StringIO
            self._read_file(StringIO(from_string))
        else:
            with open(filename) as f:
                self._read_file(f)
        
    def _read_file(self, f):
        """Do the work of reading the file."""
        contents = self.contents
        sections = self.sections
        real_lineno = 1
        output_lineno = 0
        
        stack = []
        line = f.readline()
        while line:
            m = _sectionmarker.search(line)
            if m:
                section = m.group(1)
                debug("Section %s found at %s (%s)", section, real_lineno, 
                      output_lineno)
                stack.append(section)
                sectionname = ".".join(stack)
                if sectionname in sections:
                    raise BuildFailure("""section '%s' redefined
(in file '%s', first section at line %s, second at line %s)""" %
                                        (sectionname, self.filename,
                                         sections[sectionname][0],
                                         real_lineno))
                sections[".".join(stack)] = [real_lineno, output_lineno]
            elif _endmarker.search(line):
                sectionname = ".".join(stack)
                try:
                    section = stack.pop()
                except IndexError:
                    raise BuildFailure("""End section marker with no starting marker
(in file '%s', at line %s)""" % (self.filename, real_lineno))
                debug("Section %s end at %s (%s)", section, real_lineno, 
                      output_lineno)
                sections[sectionname].append(output_lineno)
            else:
                contents.append(line)
                output_lineno += 1
            line = f.readline()
            real_lineno += 1
        if stack:
            section = ".".join(stack)
            raise BuildFailure("""No end marker for section '%s'
(in file '%s', starts at line %s)""" % (section, self.filename, 
                                        sections[section][0]))
    
    def __getitem__(self, key):
        """Look up a section, and return the text of the section."""
        try:
            pos = self.sections[key]
        except KeyError:
            raise BuildFailure("No section '%s' in file '%s'" %
                               (key, self.filename))
        return "".join(self.contents[pos[1]:pos[2]])
    
    def __len__(self):
        """Number of sections available in the file."""
        return len(self.sections)
    
    def keys(self):
        return self.sections.keys()
    
    @property
    def all(self):
        """Property to get access to the whole file."""
        return "".join(self.contents)

_default_include_marker = dict(
    py="# "
)

class Includer(object):
    """Looks up SectionedFiles relative to the basedir.
    
    When called with a filename and an optional section, the Includer
    will:
    
    1. look up that file relative to the basedir in a cache
    2. load it as a SectionedFile if it's not in the cache
    3. return the whole file if section is None
    4. return just the section desired if a section is requested
    
    If a cog object is provided at initialization, the text will be
    output (via cog's out) rather than returned as
    a string.
    
    You can pass in include_markers which is a dictionary that maps
    file extensions to the single line comment character for that
    file type. If there is an include marker available, then
    output like:
    
    # section 'sectionname' from 'file.py'
    
    There are some default include markers. If you don't pass
    in anything, no include markers will be displayed. If you
    pass in an empty dictionary, the default ones will
    be displayed.
    """
    def __init__(self, basedir, cog=None, include_markers=None):
        self.include_markers = {}
        if include_markers is not None:
            self.include_markers.update(_default_include_marker)
        if include_markers:
            self.include_markers.update(include_markers)
        self.basedir = path(basedir)
        self.cog = cog
        self.files = {}
    
    def __call__(self, fn, section=None):
        f = self.files.get(fn)
        if f is None:
            f = SectionedFile(self.basedir / fn)
            self.files[fn] = f
        ext = path(fn).ext.replace(".", "")
        marker = self.include_markers.get(ext)
        if section is None:
            if marker:
                value = marker + "file '" + fn + "'\n" + f.all
            else:
                value = f.all
        else:
            if marker:
                value = marker + "section '" + section + "' in file '" + fn \
                      + "'\n" + f[section]
            else:
                value = f[section]
        if self.cog:
            self.cog.cogmodule.out(value)
        else:
            return value

def _cogsh(cog):
    """The sh command used within cog. Runs the command (unless it's a dry run)
    and inserts the output into the cog output if insert_output is True."""
    def shfunc(command, insert_output=True):
        output = sh(command, capture=insert_output)
        if insert_output:
            cog.cogmodule.out(output)
    return shfunc

def _runcog(options, uncog=False):
    """Common function for the cog and runcog tasks."""
    if not has_cog:
        raise BuildFailure('install Cog to build html docs')

    options.order('cog', 'sphinx', add_rest=True)
    c = cogapp.Cog()
    if uncog:
        c.options.bNoGenerate = True
    c.options.bReplace = True
    c.options.bDeleteCode = options.get("delete_code", False)
    includedir = options.get('includedir', None)
    if includedir:
        include = Includer(includedir, cog=c, 
                           include_markers=options.get("include_markers"))
        # load cog's namespace with our convenience functions.
        c.options.defines['include'] = include
        c.options.defines['sh'] = _cogsh(c)
    
    c.options.defines.update(options.get("defines", {}))

    c.sBeginSpec = options.get('beginspec', '[[[cog')
    c.sEndSpec = options.get('endspec', ']]]')
    c.sEndOutput = options.get('endoutput', '[[[end]]]')
    
    basedir = options.get('basedir', None)
    if basedir is None:
        basedir = path(options.get('docroot', "docs")) / options.get('sourcedir', "")
    basedir = path(basedir)
        
    pattern = options.get("pattern", "*.rst")
    if pattern:
        files = basedir.walkfiles(pattern)
    else:
        files = basedir.walkfiles()
    for f in files:
        dry("cog %s" % f, c.processOneFile, f)
    

@task
def cog(options):
    """Runs the cog code generator against the files matching your 
    specification. By default, cog will run against any .rst files
    in your Sphinx document root. Full documentation for Cog is
    here:
    
    https://nedbatchelder.com/code/cog/
    
    In a nutshell, you put blocks in your file that look like
    this:
    
    [[[cog cog.outl("Hi there!")
    ]]]
    [[[end]]]
    
    Cog will replace the space between ]]] and [[[end]]] with
    the generated output. In this case, Hi there!
    
    Here are the options available for the cog task. These are
    looked up in the 'cog' options section by default. The
    'sphinx' option set is also searched.
    
    basedir
        directory to look in for files to cog. If not set,
        'docroot' is looked up.
    pattern
        file glob to look for under basedir. By default, ``*.rst``
    includedir
        If you have external files to include in your
        documentation, setting includedir to the root
        of those files will put a paver.doctools.Includer 
        in your Cog namespace as 'include'. This lets you
        easily include files and sections of files. Here's
        an example usage::

            [[[cog include('filename_under_includedir.py', 'mysection')]]]
            [[[end]]]
    defines
        Dictionary of objects added to your Cog namespace.
        (can supersede 'include' and 'sh' defined by includedir.)
    beginspec
        String used at the beginning of the code generation block.
        Default: [[[cog
    endspec
        String used at the end of the code generation block.
        Default; ]]]
    endoutput
        String used at the end of the generated output
        Default: [[[end]]]
    delete_code
        Remove the generator code. Note that this will mean that the
        files that get changed cannot be changed again since the code
        will be gone. Default: False
    include_markers
        Dictionary mapping file extensions to the single line
        comment marker for that file. There are some defaults.
        For example, 'py' maps to '# '. If there is a known
        include marker for a given file, then a comment
        will be displayed along the lines of:
        
        # section 'SECTIONNAME' in file 'foo.py'
        
        If this option is not set, these lines will not
        be displayed at all. If this option is set to an
        empty dictionary, the default include markers
        will be displayed. You can also pass in your own
        extension -> include marker settings.
    """
    _runcog(options)
    
@task
def uncog(options):
    """Remove the Cog generated code from files. Often, you will want to
    do this before committing code under source control, because you
    don't generally want generated code in your version control system.
    
    This takes the same options as the cog task. Look there for
    more information.
    """
    _runcog(options, True)
