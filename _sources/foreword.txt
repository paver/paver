********************
Foreword: Why Paver?
********************

    Paver occupies a sweet spot in the python toolset, the design is sound,
    it's easier than mud to work with at a basic level, and it has a nice grade
    of descent into more advanced things.

    -- David Eyk


I didn't want to make a new build tool. Honestly. The main reason that I created Paver
is...

The Declarative/Imperative Divide
---------------------------------

When you solve the same problem repeatedly, patterns emerge and you're able to easily
see ways to reduce how much effort is involved in solving that problem. Often
times, you'll end up with a `declarative solution`_. Python's standard distutils
is a declarative solution. In your call to the ``setup()`` function, you declare
some metadata about your project and provide a list of the parts and you end
up with a nice command line interface. That command line interface knows how to
make redistributable tarballs (and eggs if you have setuptools), install the
package, build C extensions and more.

zc.buildout does a similar thing for deployments. Declare the parts of your system
and specify a recipe for each part (each recipe with its own collection of options)
and you can build up a consistent system with one command.

These tools sound great, don't they? They are great. As long as you don't need
to customize the capabilities they provide. For example, it's not uncommon that
you'll need to move some file here, create some directory there, etc. Then what?

In an `imperative system`_, you'd just add the few lines of code you need.

For distutils and zc.builout and other similar tools, the answer usually involves
extra boilerplate surrounding the code in question and then installing that code somewhere. You basically have to create declarative syntax for something that is a one-off rather than a larger, well-understood problem. And, for distutils and zc.buildout, you have to use two entirely different mechanisms.

.. _`declarative solution`: http://en.wikipedia.org/wiki/Declarative_programming
.. _`imperative system`: http://en.wikipedia.org/wiki/Imperative_programming

Consistency for Project Related Tasks
-------------------------------------

And that's the next thing that bothered me with the state of Python tools. It 
would be nice to have a consistent interface in command line and configuration 
for the tools that I use to work with my projects. Every tool I bring in to 
the project adds new command line interfaces, more config files (and some of
those config files duplicate project metadata!).

That's Why Paver Is Here
------------------------

Paver is set up to provide declarative handling of common tasks with as easy
an escape hatch to imperative programming as possible (just add a function
with a decorator in the same file). Your project-related configuration
options are all together and all accessible to different parts of your
build and deployment setup. And the language used for everything is Python,
so you're not left guessing how to do a ``for`` loop.

Of course, rebuilding the great infrastructure provided by tools like distutils
makes no sense. So, Paver just uses distutils and other tools directly.

Paver also goes beyond just providing an extension mechanism for distutils.
It adds a bunch of useful capabilities for things like working with files
and directories, elegantly handling sample code for your documentation and 
building bootstrap scripts to allow your software to easily be installed
in an isolated virtualenv.

I'm already using Paver for SitePen's Support service user interface
project and I use Paver to manage Paver itself! It's been working out
great for me, and it's set up in such a way that whatever kind of scripting
your project needs it should be pretty simple with Paver.

Making the Switch is Easy
-------------------------

Finally, I've put some time into making sure that moving a project from
distutils to Paver is easy for everyone involved (people making the
projects and people using the projects). Check out the
:ref:`Getting Started Guide <gettingstarted>` to see an example of how
a project moves from distutils to Paver (even maintaining the
``python setup.py install`` command that everyone's used to!)

Thanks for reading!

Kevin Dangoor
May 2008
