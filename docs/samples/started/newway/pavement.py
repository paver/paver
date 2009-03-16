# [[[section imports]]]
from paver.easy import *
import paver.doctools
from paver.setuputils import setup
# [[[endsection]]]

# [[[section setup]]]
setup(
    name="TheNewWay",
    packages=['newway'],
    version="1.0",
    url="http://www.blueskyonmars.com/",
    author="Kevin Dangoor",
    author_email="dangoor@gmail.com"
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

# [[[section minilib]]]
options(
    minilib = Bunch(
        extra_files=["doctools"]
    )
)
# [[[endsection]]]

# [[[section sdist]]]
@task
@needs('generate_setup', 'minilib', 'setuptools.command.sdist')
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""
    pass
# [[[endsection]]]

# [[[section html]]]
@task
@needs('paver.doctools.html')
def html(options):
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
def deploy(options):
    """Deploy the HTML to the server."""
    for host in options.hosts:
        sh("rsync -avz -e ssh %s/ %s@%s:%s/" % (options.htmldir,
            options.username, host, options.hostpath))
# [[[endsection]]]

# the pass that follows is to work around a weird bug. It looks like
# you can't compile a Python module that ends in a comment.
pass
