from paver.easy import *

from paver.release import setup_meta

import paver.doctools
import paver.virtual
import paver.misctasks
from paver.setuputils import setup


options = environment.options

setup(**setup_meta)

options(
    minilib=Bunch(
        extra_files=['doctools', 'virtual'],
        versioned_name=False,
    ),
    sphinx=Bunch(
        builddir="build",
        sourcedir="source"
    ),
    virtualenv=Bunch(
        packages_to_install=["nose", "Sphinx>=0.6b1", "docutils", "virtualenv"],
        install_paver=False,
        script_name='bootstrap.py',
        paver_command_line=None,
        dest_dir="virtualenv"
    ),
    cog=Bunch(
        includedir="docs/samples",
        beginspec="<==",
        endspec="==>",
        endoutput="<==end==>"
    ),
    deploy=Bunch(
        deploydir="blueskyonmars.com/projects/paver"
    )
)

# not only does paver bootstrap itself, but it should work even with just 
# distutils
if paver.setuputils.has_setuptools:
    old_sdist = "setuptools.command.sdist"
    options.setup.update(dict(
        install_requires=[],
        test_suite='nose.collector',
        zip_safe=False,
        entry_points="""
[console_scripts]
paver = paver.tasks:main
"""
    ))
else:
    old_sdist = "distutils.command.sdist"
    options.setup.scripts = ['distutils_scripts/paver']

options.setup.package_data=paver.setuputils.find_package_data("paver", package="paver",
                                                only_in_packages=False)

if paver.doctools.has_sphinx:
    @task
    @needs('cog', 'paver.doctools.html')
    def html():
        """Build Paver's documentation and install it into paver/docs"""
        builtdocs = path("docs") / options.sphinx.builddir / "html"
        destdir = path("paver") / "docs"
        destdir.rmtree()
        builtdocs.move(destdir)
    
    @task
    @needs('html', "minilib", "generate_setup", old_sdist)
    def sdist():
        """Builds the documentation and the tarball."""
        pass

if paver.virtual.has_virtualenv:
    @task
    def bootstrap():
        """Build a virtualenv bootstrap for developing paver."""
        # we have to pull some private api shenanigans that normal people don't
        # because we're bootstrapping paver itself.
        paver.virtual._create_bootstrap(options.script_name,
                              options.packages_to_install,
                              options.paver_command_line,
                              options.install_paver,
                              more_text="""    subprocess.call([join("""
                              """bin_dir, 'python'), '-c', """
                              """'import sys; sys.path.append("."); """
                              """import paver.command; paver.command.main()', """
                              """'develop'])""")
    
@task
def clean():
    """Cleans up this paver directory. Removes the virtualenv traces and
    the build directory."""
    path("build").rmtree()
    path("bin").rmtree()
    path("lib").rmtree()
    path(".Python").remove()
    
@task
@needs("uncog")
@consume_args
def commit(args):
    """Removes the generated code from the docs and then commits to bzr."""
    sh("git commit " + ' '.join(args))

@task
@cmdopts([
    ("branch=", "b", "Branch from which to publish"),
    ("docs-branch=", "d", "Docs branch to commit/push to"),
    ("git-repo=", "g", "Github repository to use"),
    ("deploy-key=", "k", "Deploy key to use"),
])
def publish_docs(options):
    """Publish current docs/site do paver.github.com"""

    # we are going to mess around with files, so do it in temporary place
    import os
    from subprocess import check_call, CalledProcessError
    from tempfile import mkdtemp, mkstemp

    current_repo = path(os.curdir).abspath()
    branch = getattr(options, 'branch', 'master')
    docs_branch = getattr(options, 'docs_branch', 'gh-pages')
    repo = getattr(options, 'git_repo', 'git@github.com:paver/paver.git')

    try:
        safe_clone = path(mkdtemp(prefix='paver-clone-'))
        docs_repo = path(mkdtemp(prefix='paver-docs-'))
        fd, git = mkstemp(prefix='tmp-git-ssh-')

        # TODO: I strongly believe there have to be better way to provide custom
        # identity file for git, but cannot find one...so, workaround
        f = os.fdopen(fd, 'w')
        f.writelines(["#!/bin/sh", os.linesep, "ssh%s $*" % (" -i "+options.deploy_key if getattr(options, "deploy_key", None) else "")])
        f.close()

        os.chmod(git, 0777)

        safe_clone.chdir()

        sh('git init')

        check_call(['git', 'remote', 'add', '-t', branch, '-f', 'origin', 'file://'+str(current_repo)], env={"GIT_SSH" : git})

        check_call(['git', 'checkout', branch], env={"GIT_SSH" : git})

        check_call(['python', os.path.join(str(current_repo), "distutils_scripts", "paver"), 'html'], env={
            'PYTHONPATH' : os.path.join(str(current_repo))
        })


        docs_repo.chdir()

        sh('git init')

        check_call(['git', 'remote', 'add', '-t', docs_branch, '-f', 'origin', repo], env={"GIT_SSH" : git})
        check_call(['git', 'checkout', docs_branch], env={"GIT_SSH" : git})

        check_call(['rsync', '-av', os.path.join(str(safe_clone), 'paver', 'docs')+'/', str(docs_repo)])

        sh('git add *')

        #TODO: '...from revision abc'
        try:
            check_call(['git', 'commit', '-a', '-m', "Commit auto-generated documentation"])
        except CalledProcessError:
            # usually 'working directory clean'
            pass
        else:
            check_call(['git', 'push', 'origin', '%s:%s' % (docs_branch, docs_branch)], env={"GIT_SSH" : git})


    finally:
        safe_clone.rmtree()
        docs_repo.rmtree()
        os.remove(git)
