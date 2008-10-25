# the following line is optional, but is useful when you use a tool
# like WingIDE or if you wish to import your pavement directly into a Python
# shell.
from paver.defaults import *
import paver.doctools

# [[[section setup]]]
options(
    setup=Bunch(
        name="TheNewWay",
        packages=['newway'],
        version="1.0",
        author="Kevin Dangoor"
    )
)
# [[[endsection]]]

# [[[section sphinx]]]
options(
    sphinx=Bunch(
        builddir="_build"
    )
)
# [[[endsection]]]

# [[[section deployoptions]]]
options(
    deploy = Bunch(
        htmldir = path('newway/docs'),
        hosts = ['host1.hostymost.com', 'host2.hostymost.com'],
        hostpath = 'sites/newway'
    )
)
# [[[endsection]]]

# [[[section sdist]]]
@task
@needs(['generate_setup', 'minilib', 'setuptools.command.sdist'])
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""
    pass
# [[[endsection]]]

# [[[section html]]]
@task
@needs('paver.doctools.html')
def html():
    """Build the docs and put them into our package."""
    destdir = path('newway/docs')
    destdir.rmtree()
    # [[[section builtdocs]]]
    builtdocs = path("docs") / options.builddir / "html"
    # [[[endsection]]]
    builtdocs.move(destdir)
# [[[endsection]]]    

# [[[section deploy]]]
@task
@cmdopts([
    ('username=', 'u', 'Username to use when logging in to the servers')
])
def deploy():
    """Deploy the HTML to the server."""
    for host in options.hosts:
        sh("rsync -avz -e ssh %s/ %s@%s:%s/" % (options.htmldir,
            options.username, host, options.hostpath))
# [[[endsection]]]

# the pass that follows is to work around a weird bug. It looks like
# you can't compile a Python module that ends in a comment.
pass
