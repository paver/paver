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

Tasks can specify that they accept command line arguments, via three
other decorators. The ``@consume_args`` decorator tells Paver that *all*
command line arguments following this task's name should be passed to the
task. If you'd like specifying a number of consumed arguments, let use
``@consume_nargs``. This later is similar by default to the previous,
but alos accept as an ``int`` argument the number of command line arguments
the decorated task will consume.
You can either look up the arguments in ``options.args``, or just
specify args as a parameter to your function. For example, Paver's "help"
task is declared like this::

    @task
    @consume_args
    def help(args, help_function):
        pass

    @task
    @consume_nargs(3)
    def mytask(args):
        pass

The "args" parameter is just an attribute on tasks.environment (as is
help_function), so it is passed in using the same rules described in the
previous section.

.. versionadded:: 1.1.0
    ``@consume_nargs`` decorator superseeds ``@consume_args``,
    and optionally accepts an ``int`` as argument: the number of command line
    argument the decorated task will consume.

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

For fine-tuning, you may add ``optparse.Option`` instances::

    @tasks.task
    @tasks.cmdopts([
        make_option("-f", "--foo", help="foo")
    ])
    def foo_instead_of_spam_and_eggs(options):
        pass


You may share ``@cmdopts`` between tasks. To do that and to avoid confusion,
You have to add share_with argument::

    @task
    @cmdopts([
        ('username=', 'u', 'Username to use when logging in to the servers')
    ])
    def deploy_to_linux(options):
        pass


    @task
    @needs(['deploy_to_linux'])
    @cmdopts([
        ('username=', 'u', 'Username to use when logging in to the servers')
    ], share_with=['deploy_to_linux'])
    def deploy(options):
        pass


For sharing, following must be fullfilled:

* Both long and short option names must be same
* ``share_with`` argument must be specified on top-level task

Otherwise, ``PavementError`` is raised.

Hiding tasks
---------------

Some tasks may only exist as a shared dependency between other tasks and may not
make sense to be called directly.

There is no way to provide that, however you can hide them from ``paver help``
to reduce noise. Just decorate function with ``@no_help`` decorator::

    @task
    @no_help
    def hidden_dependency():
        pass

Of course, this should not be used usually. If task is not to be called at all,
why not just make them a g'old function?

More complex dependencies
--------------------------

``@needs`` might not cover all your needs. For example, depending on argument
or environment, you might decide to call an appropriate task in the middle of
another one.

There are two key options for fixing that:

#. ``@might_call`` decorator, which indicates that task might invoke ``call_task`` on one or more of the specified tasks. This allows you to provide command line options to task that might be called (it is inserted in dependency chain)::

    @task
    @cmdopts([
        ('username=', 'u', 'Whom to greet')
    ], share_with=['deploy_to_linux'])
    def say_hello(options):
        if not hasattr(options, "username"):
            print 'SPAM'
        else:
            print 'Hello, my dear user %s' % options.username


    @task
    @might_call('say_hello')
    def greet_user(options):
        setup_environment()

        call_task('say_hello')

        do_cleanup()

#. Providing options and arguments to another tasks directly.
   Options are provided with final assigned value::

    @task
    @cmdopts([
        ('long-username=', 'u', 'Whom to greet')
    ], share_with=['deploy_to_linux'])
    def say_hello(options):
        if not hasattr(options, "username"):
            print 'SPAM'
        else:
            print 'Hello, my dear user %s' % options.long_username


    @task
    def greet_user(options):
        call_task('say_hello', options={
            'long_username' : 'Kitty'
        })

Console arguments (args) should be passed as in console::

    @task
    @consume_args
    def say_hello(args):
        print 'Hello to ALL the users: %s' % ', '.join(args)


    @task
    def greet_user(options):
        call_task('say_hello', args = [
            'Arthur Pewtey',
            'The Reverend Arthur Belling',
        ])
