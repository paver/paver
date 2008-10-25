.. _pavement:

pavement.py in depth
====================

Paver is meant to be a hybrid declarative/imperative system for getting stuff done.
You declare things via the options in pavement.py. And, in fact, many projects
can get away with nothing but options in pavement.py. Consider, for example,
Paver's own pavement file::
  
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
task by using the @task decorator. Interesting tidbit: unlike
many decorators you find in Python, Paver's decorators do not actually
replace the function with a new object. They just put marker data on the
function object and also keep track of things in a companion
paver.runtime.Task object.

You can also specify that a task depends on another task running
first with the @needs decorator. As long as the options don't change,
a given task will run only once regardless of how many times it's
specified in @needs or whether the task shows up on the command line.

Manually Calling Tasks
----------------------

Sometimes, you need to do something `before` running another task, so
the @needs decorator doesn't quite do the job.

Of course, tasks are just Python functions. So, you can just call the
other task! However, this is not ideal, because Python functions
don't do things like keeping track of their dependencies or whether
they've been called already.

paver.runtime provides a call_task function. It's very simple to use:

.. autofunction:: paver.runtime.call_task

How Task Names Work
---------------------

Tasks have both a long name and a short name. The short name is just
the name of the function. The long name is the fully qualified Python
name for the function object.

For example, the Sphinx support includes a task function called "html".
That task's long name is "paver.sphinx.html".

If you ```import paver.sphinx``` in your pavement.py, you'll be able 
to use either name to refer to that task.

The `last` task that is defined with a given short name is the one that
gets the name. Generally, this will be `your` pavement.py file. So,
in the example at the front of this chapter, the html task in
pavement.py is the one that the "html" short name refers to.

Tasks are always available unambiguously via their long names.
  

The Magic
---------

When you run Paver it looks for 'pavement.py' in the current directory. 
pavement.py is standard Python, with two small bits of magic:

1. Everything in paver.defaults is available as if you had done 
   ``from paver.defaults import *``. In fact, if you're using an IDE that does
   code completion you might want to manually add that statement to the
   top of your file.
2. When your pavement is being processed, options() is a function that updates
   runtime.options. When processing is done, options is replaced by runtime.options
   for convenience.

It is purposefully not a lot of magic, and the implementation of that "magic" isn't
magical at all. Your pavement file is actually executed in the namespace of
paver.defaults. After that, paver.defaults.options = runtime.options, and then
the tasks are run.