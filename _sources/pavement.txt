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
first with the @needs decorator. A given task will only run once
as a dependency for other tasks.

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
That task's long name is "paver.doctools.html".

If you ```import paver.doctools``` in your pavement.py, you'll be able 
to use either name to refer to that task.

Tasks that you define in your pavement are always available by their
short names. Tasks defined elsewhere are available by their short names
unless there is a conflict where two tasks are trying to use the same
short name.

Tasks are always available unambiguously via their long names.

Task Parameters
---------------

Tasks don't have to take any parameters. However, Paver allows you to work
in a fairly clean, globals-free manner(*). Generally speaking, the easiest way
to work with paver is to just do ``from paver.easy import *``, but if you
don't like having so much in your namespace, you can have any attribute
from tasks.environment sent into your function. For example::

    @task
    def my_task(options, info):
        # this task will get the options and the "info" logging function
        # sent in
        pass

(*): well, there *is* one global: tasks.environment.
  
Command Line Arguments
----------------------

Tasks can specify that they accept command line arguments, via two 
other decorators. The ``@consume_args`` decorator tells Paver that *all* 
command line arguments following this task's name should be passed to the 
task. You can either look up the arguments in ``options.args``, or just 
specify args as a parameter to your function. For example, Paver's "help" 
task is declared like this::

    @task
    @consume_args
    def help(args, help_function):
        pass
        
The "args" parameter is just an attribute on tasks.environment (as is
help_function), so it is passed in using the same rules described in the
previous section.

More generally, you're not trying to consume all of the remainder of the
command line but to just accept certain specific arguments. That's what
the cmdopts decorator is for::

    @task
    @cmdopts([
        ('username=', 'u', 'Username to use when logging in to the servers')
    ])
    def deploy(options):
        pass
        
@cmdopts takes a list of tuples, each with long option name, short option name
and help text. If there's an "=" after the long option name, that means
that the option takes a parameter. Otherwise, the option is assumed to be
boolean. The command line options set in this manner are all added to
the ``options`` under a namespace matching the name of the task. In the
case above, options.deploy.username would be set if the user ran
paver deploy -u my-user-name. Note that an equivalent command line would be
paver deploy.username=my-user-name deploy
