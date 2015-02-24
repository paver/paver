.. _gettingstarted:

==========================
Getting Started with Paver
==========================

Often, the easiest way to get going with a new tool is to see an example
in action, so that's how we'll get started with Paver. In the Paver
distribution, there are samples under docs/samples. The Getting
Started samples are in the "started" directory under there.

The Old Way
===========

Our first sample is called "The Old Way" (and it's in the 
docs/samples/started/oldway directory). It's a fairly typical project
with one Python package and some docs, and we want to be able to
distribute it.

Python's distutils_ makes it easy indeed to create a distributable
package. We create a setup.py file that looks like this::

  #<== include('started/oldway/setup.py')==>
  #<==end==>
  
With that simple setup script, you can run::

  python setup.py sdist

to build a source distribution::

  # <== 
  # sh('cd docs/samples/started/oldway; python setup.py sdist',
  #    insert_output=False)
  # sh('ls -l docs/samples/started/oldway/dist')
  # ==>
  # <==end==>

Then your users can run the familiar::

  python setup.py install

to install the package, or use setuptools' even easier::

  easy_install "TheOldWay"

for packages that are up on the Python Package Index.

.. _distutils: http://docs.python.org/dist/dist.html

The Old Way's Docs
------------------

The Old Way project is at least a bit modern in that it uses Sphinx_ for documentation. When you use sphinx-quickstart to get going with your
docs, Sphinx will give you a Makefile that you can run to generate
your HTML docs. So, generating the HTML docs is easy::

  make html

Except, in this project (as in Paver itself), we want to include the
HTML files in a docs directory in the package for presenting help to
the users. We end up creating a shell script to do this::

  # <== include("started/oldway/builddocs.sh")==>
  # <==end==>

Of course, creating a script like this means that we have to actually
remember to run it. We could change this script to "buildsdist.sh"
and add a ``python setup.py sdist`` to the end of the file. But,
wouldn't it be nicer if we could just use ``python setup.py sdist``
directly?

You can `create new distutils commands`_, but do you really want to
drop stuff like that in the distutils/command package in your
Python library directory? And how would you call the sdist command
anyway? setuptools_ helps, but it still requires setting up a module
and entry point for this collection of commands.

.. _create new distutils commands: http://docs.python.org/dist/node84.html
.. _setuptools: http://peak.telecommunity.com/DevCenter/setuptools
.. _Sphinx: http://sphinx.pocoo.org


Work with me here
-----------------

I just `know` there are some people reading this and thinking
"man, what a contrived example!". Building, packaging, distributing
and deploying of projects is quite custom for every project.
Part of the point of Paver is to make it easy to handle whatever
weird requirements arise in your project. This example may seem
contrived, but it should give you an idea of how easy Paver
makes it to get your tasks done.

The New Way
===========

Let's bring in Paver now to clean up our scripting a bit. Converting
a project to use Paver is really, really simple. Recall the setup
function from our Old Way setup.py::

  # <== include("started/oldway/setup.py", "setup")==>
  # <==end==>

Getting Started with Paver
--------------------------

setup.py is a standard Python script. It's just called setup.py
as a convention. Paver works a bit more like Make or Rake.
To use Paver, you run ``paver <taskname>`` and the paver
command will look for a pavement.py file in the current directory.
pavement.py is a standard Python module. A typical pavement will 
import from paver.easy to get a bunch of convenience functions
and objects and then import other modules that include useful
tasks::

    # <== include('started/newway/pavement.py', 'imports')==>
    # <==end==>

Converting from setup.py to pavement.py is easy. Paver provides
a special ``options`` object that holds all of your build options.
``options`` is just a dictionary that allows attribute-style
access and has some special searching abilities. The options
for distutils operations are stored in a ``setup`` section of the
options. And, as a convenience, Paver provides a setup function
that sets the values in that options section (and goes a step
further, by making all of the distutils/setuptools commands 
available as Paver tasks). Here's what the conversion looks like::

  # <== include('started/newway/pavement.py', 'setup')==>
  # <==end==>

Paver is compatible with distutils
----------------------------------

Choosing to use Paver does not mean giving up on distutils or
setuptools. Paver lets you continue to use distutils and setuptools
commands. When you import a module that has Paver tasks in it,
those tasks automatically become available for running. If you
want access to distutils and setuptools commands as well, you can either
use the ``paver.setuputils.setup`` function as described
above, or call ``paver.setuputils.install_distutils_tasks()``.

We can see this in action by looking at ``paver help``::

  # <== sh('cd docs/samples/started/newway; paver help')==>
  # <==end==>

That command is listing all of the available tasks, and you can see
near the top there are tasks from distutils.command. All of the
standard distutils commands are available.

There's one more thing we need to do before our Python package
is properly redistributable: tell distutils about our special files.
We can do that with a simple MANIFEST.in::

    # <== include('started/newway/MANIFEST.in')==>
    # <==end==>

With that, we can run ``paver sdist`` and end up with the
equivalent output file::

  # <== 
  # sh('cd docs/samples/started/newway; paver sdist',
  #    insert_output=False)
  # sh('ls -l docs/samples/started/newway/dist')
  # ==>
  # <==end==>

It also means that users of The New Way can also run ``paver install``
to install the package on their system. Neat.

But people are used to setup.py!
--------------------------------

``python setup.py install`` has been around a long time. And while
you could certainly put a README file in your package telling
people to run ``paver install``, we all know that no one actually
reads docs. (Hey, thanks for taking the time to read this!)

No worries, though. You can run ``paver generate_setup`` to get a
setup.py file that you can ship in your tarball. Then your users
can run ``python setup.py install`` just like they're used to,
and Paver will take over.

But people don't have Paver yet!
--------------------------------

There are millions of Python installations that don't have Paver yet,
but have Python and distutils. How can they run a Paver-based install?

Easy, you just run ``paver minilib`` and you will get a file called
paver-minilib.zip. That file has enough of Paver to allow someone
to install most projects. The Paver-generated setup.py knows to look
for that file and use it if it sees it.

Worried about bloating your package? The paver-minilib is not large::

  # <==
  # sh('cd docs/samples/started/newway ; paver minilib',
  #    insert_output=False)
  # sh('ls -l docs/samples/started/newway/paver-minilib.zip')
  # ==>
  # <==end==>

Paver itself is bootstrapped with a generated setup file and a
paver-minilib.

Hey! Didn't you just create more work for me?
---------------------------------------------

You might have noticed that we now have three commands to run in
order to get a proper distribution for The New Way. Well, you can
actually run them all at once: ``paver generate_setup minilib sdist``.
That's not terrible, but it's also not great. You don't want to
end up with a broken distribution just because you forgot one of
the tasks.

By design, one of the easiest things to do in Paver is to extend
the behavior of an existing "task", and that includes distutils
commands. All we need to do is create a new sdist task in our
pavement.py::

  # <== include('started/newway/pavement.py', 'sdist')==>
  # <==end==>

The @task decorator just tells Paver that this is a task and not just
a function. The @needs decorator specifies other tasks that should
run before this one. You can also use the `call_task(taskname)`
function within your task if you wish. The function name determines
the name of the task. The docstring is what shows up in Paver's
help output.

With that task in our pavement.py, ``paver sdist`` is all it takes
to build a source distribution after generating a setup file
and minilib.

.. note:: If you are depending on distutils task (via @needs), you have to call ``setup()`` before task is defined.
   Under the hood, ``setup`` call installs distutils/setupsools task and make them available, so do not make it conditional.

Tackling the Docs
-----------------

Until the tools themselves provide tasks and functions that make
creating pavements easier, Paver's Standard Library will include
a collection of modules that help out for commonly used tools. 
Sphinx is one package for which Paver has built-in support.

To use Paver's Sphinx support, you need to have Sphinx installed
and, in your pavement.py, ``import paver.doctools``. Just performing
the import will make the doctools-related tasks available.
``paver help html`` will tell us how to use the html command::

  # <== sh('paver help paver.doctools.html')==>
  # <==end==>

According to that, we'll need to set the builddir setting, since we're
using a builddir called "_build". Let's add this to our pavement.py::

  # <== include('started/newway/pavement.py', 'sphinx')==>
  # <==end==>

And with that, ``paver html`` is now equivalent to ``make html`` using
the Makefile that Sphinx gave us.

Getting rid of our docs shell script
------------------------------------

You may remember that shell script we had for moving our generated
docs to the right place::

  # <== include('started/oldway/builddocs.sh')==>
  # <==end==>

Ideally, we'd want this to happen whenever we generate the docs.
We've already seen how to override tasks, so let's try that out
here::

  # <== include('started/newway/pavement.py', 'html')==>
  # <==end==>

There are a handful of interesting things in here. The equivalent of
'make html' is the @needs('paver.doctools.html'), since that's
the task we're overriding.

Inside our task, we're using "path". This is a customized
version of Jason Orendorff's path module. All kinds of file
and directory operations become super-simple using this module.

We start by deleting our destination directory, since we'll be copying
new generated files into that spot. Next, we look at the built
docs directory that we'll be moving::

  # <== include('started/newway/pavement.py', 'html.builtdocs')==>
  # <==end==>

One cool thing about path objects is that you can use the natural
and comfortable '/' operator to build up your paths.

The next thing we see here is the accessing of options. The
options object is available to your tasks. It's basically a dictionary
that offers attribute-style access and can search for variables
(which is why you can type options.builddir instead of
the longer options.sphinx.builddir). That property of options is
also convenient for being able to share properties between sections.

And with that, we eliminate the shell script as a separate file.

Fixing another wart in The Old Way
----------------------------------

In the documentation for The Old Way, we actually included the
function body directly in the docs. But, we had to cut and paste
it there. Sphinx does offer a way to include an external file
in your documentation. Paver includes a better way.

There are a couple of parts to the documentation problem:

1. It's good to have your code in separate files from your docs
   so that the code can be complete, runnable and, above all,
   testable programs so that you can be sure that everything works.
2. You want your writing and the samples included with your writing
   to stand up as reasonable, coherent documents. Python's doctest
   style does not always lend itself to coherent documents.
3. It's nice to have the code sample that you're writing about
   included inline with the documents as you're writing them.
   It's easier to write when you can easily see what you're
   writing about.

#1 and #3 sound mutually exclusive, but they're not. Paver has a
two part strategy to solve this problem. Let's look at part of the index.rst
document file to see the first part::

  # <== include("started/newway/docs/index.rst", "mainpart")==>
  # <==end==>

In The New Way's index.rst, you can see the same mechanism being used that
is used in this Getting Started guide. Paver includes Ned Batchelder's
Cog_ package. Cog lets you drop snippets of Python into a file and have
those snippets generate stuff that goes into the file. Unlike a template
language, Cog is designed so that you can leave the markers in and
regenerate as often as you need to. With a template language, you have
the template and the finalized output, but not a file that has both.

So, as I'm writing this Getting Started document, I can glance up and see
the index.rst contents right inline. You'll notice The # [[ [cog part in there
is calling an include() function. This is the second part offered by
Paver. Paver lets you specify an "includedir" for use with Cog.
This lets you include files relative to that directory. And, critically,
it also lets you mark off sections of those files so that you can
easily include just the part you want. In the example above, we're picking
up the 'code' section of the newway/thecode.py file. Let's take a look
at that file::

  # <== sh("cat docs/samples/started/newway/newway/thecode.py") ==>
  # <==end==>

Paver has a Cog-like syntax for defining named sections. So, you just
use the ``include`` function with the relative filename and the section
you want, and it will be included. Sections can even be nested (and
you refer to nested sections using familiar dotted notation).

.. _Cog: http://nedbatchelder.com/code/cog/

Bonus Deployment Example
------------------------

pavements are just standard Python. The syntax for looping and things
like that are just what you're used to. The options are standard Python
so they can contain lists and other objects. Need to deploy to
multiple hosts? Just put the hosts in the options and loop over them.

Let's say we want to deploy The New Way project's HTML files to a
couple of servers. This is similar to what I do for Paver itself, though
I only have one server. First, we'll set up some variables to use for
our deploy task::

  # <== include('started/newway/pavement.py', 'deployoptions')==>
  # <==end==>

As you can see, we can put whatever kinds of objects we wish into
the options. Now for the deploy task itself::

  # <== include("started/newway/pavement.py", "deploy")==>
  # <==end==>

You'll notice the new "cmdopts" decorator. Let's say that you have
sensitive information like a password that you don't want to include
in your pavement. You can easily make it a command line option for that
task using cmdopts. options.deploy.username will be set to whatever
the user enters on the command line.

It's also worth noting that when looking up options, Paver gives
priority to options in a section with the same name as the task. So,
options.username will prefer options.deploy.username even if there
is a username in another section.

Our deploy task uses a simple for loop to run an rsync command
for each host. Let's do a dry run providing a username to see
what the commands will be::

  # <== sh("cd docs/samples/started/newway; paver -n deploy -u kevin")==>
  # <==end==>

Where to go from here
---------------------

The first thing to do is to just get started using Paver. As you've seen
above, it's easy to get Paver into your workflow, even with existing
projects.

Use the ``paver help`` command.

If you really want more detail now, you'll want to read more about 
:ref:`pavement files <pavement>` and the 
:ref:`Paver Standard Library <stdlib>`.
