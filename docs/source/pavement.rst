.. _pavement:

pavement.py in depth
====================

Paver is meant to be a hybrid declarative/imperative system for getting stuff done.
You declare things via the options in pavement.py. And, in fact, many projects
can get away with nothing but options in pavement.py. Consider, for example,
an early version of Paver's own pavement file::
  
  from paver.easy import *
  import paver.doctools

  options(
      setup=dict(
      name='paver',
      version="0.3",
      description='Python build tool',
      author='Kevin Dangoor',
      author_email='dangoor+paver@gmail.com',
      #url='',
      packages=['paver'],
      package_data=setuputils.find_package_data("paver", package="paver",
                                              only_in_packages=False),
      install_requires=[],
      test_suite='nose.collector',
      zip_safe=False,
      entry_points="""
      [console_scripts]
      paver = paver.command:main
      """,
      ),
    
      sphinx=Bunch(
          builddir="build",
          sourcedir="source"
      )
    
  )

  @task
  @needs('paver.doctools.html')
  def html():
      """Build Paver's documentation and install it into paver/docs"""
      builtdocs = path("docs") / options.sphinx.builddir / "html"
      destdir = path("paver") / "docs"
      destdir.rmtree()
      builtdocs.move(destdir)


This file has both declarative and imperative aspects. The options define 
enough information for distutils, setuptools and Sphinx to do their
respective jobs. This would function just fine without requiring you
to define any tasks.

However, for Paver's 'paverdoc' built-in task to work, we need
Sphinx's generated HTML to end up inside of Paver's package tree.
So, we override the html task to move the generated files.

Defining Tasks
--------------

Tasks are just simple functions. You designate a function as being a
task by using the @task decorator.

You can also specify that a task depends on another task running
first with the @needs decorator. A given task will run only once regardless 
of how many times it's specified in @needs or whether the task shows 
up on the command line.

Manually Calling Tasks
----------------------

Sometimes, you need to do something `before` running another task, so
the @needs decorator doesn't quite do the job.

Of course, tasks are just Python functions. So, you can just call the
other task like a function! 

How Task Names Work
---------------------

Tasks have both a long name and a short name. The short name is just
the name of the function. The long name is the fully qualified Python
name for the function object.

For example, the Sphinx support includes a task function called "html".
That task's long name is "paver.sphinx.html".

If you ```import paver.sphinx``` in your pavement.py, you'll be able 
to use either name to refer to that task.

Tasks that you define in your pavement are always available by their
short names. Tasks defined elsewhere are available by their short names
unless there is a conflict where two tasks are trying to use the same
short name.

Tasks are always available unambiguously via their long names.
  
