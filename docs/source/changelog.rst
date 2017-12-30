.. _changelog:

Paver Changelog
===============

1.3.4 (Dec 31, 2017)
--------------------
* Minilib can now be include arbitrary packages (`#28 <https://github.com/paver/paver/issues/28>`_)
* Six is now bundled in minilib (`#193 <https://github.com/paver/paver/issues/194>`_)
* install_requires is now not overriden and six is properly declared as a dependency (`#194 <https://github.com/paver/paver/issues/193>`_)
* Regression: Installation using setup.py install with minilib will *not* install six since it will be recognised as a dependency from minilib (`#193 <https://github.com/paver/paver/issues/194>`_)


1.3.3 (Dec 29, 2017)
--------------------
* Properly exclude cache files from release

1.3.2 (Dec 28, 2017)
--------------------
* Properly specify six in release dependencies

1.3.1 (Dec 28, 2017)
--------------------
* Same as 1.3.1, but with properly bumped versions in source code
* Releases are now done from Travis CI

1.3.0 (Dec 28, 2017, tagged, but not released)
-----------------------------------------------
* ***Removed support for Python 2.6, 3.2, 3.3 and Jython 2.6*** (`#179 <https://github.com/paver/paver/issues/179>`_)
* Unvendor six (`#180 <https://github.com/paver/paver/issues/180>`_)
* https everything (`#181 <https://github.com/paver/paver/issues/181>`_)
* Mercurial convenience commands (`#159 <https://github.com/paver/paver/issues/159>`_)
* Add support for trusted hosts (`#146 <https://github.com/paver/paver/issues/146>`_)
* Minilib can now be directly executed (`#145 <https://github.com/paver/paver/issues/145>`_)
* Fix task grouping (`#158 <https://github.com/paver/paver/issues/158>`_)

1.2.4 (February 23, 2015)
-------------------------
* Make path comparison better (github `issue #78 <https://github.com/paver/paver/issues/78>`_)
* Add last_tag task
* six upgraded to 1.6.1

1.2.3 (August 10, 2014)
------------------------
* ***Removed support for Python 2.5***. 2.6 is deprecated and will be removed in next release.
* Fixed `shell.py` missing from minilib (github `issue #122 <https://github.com/paver/paver/issues/122>`_)
* Added env keyword to sh. (github `issue #132 <https://github.com/paver/paver/issues/132>`_)
* When both @cmdopts and @consume_nargs are used, the options before the
args are parsed by the task's parser and given to it (github `issue #126 <https://github.com/paver/paver/issues/126>`_)
* Support list and tuple as `sh` argument (github `issue #92 <https://github.com/paver/paver/issues/92>`_)

1.2.2 (January 12, 2014)
------------------------
* Fixed `version.py` missing from minilib (github `issue #112 <https://github.com/paver/paver/issues/112>`_)


1.2.1 (June 2, 2013)
------------------------
* Fixed most of the regressions from 1.2:
* documentation was missing from tarball (github `issue #95 <https://github.com/paver/paver/issues/95>`_)
* path.push missing in paver.easy (github `issue #97 <https://github.com/paver/paver/issues/97>`_, thanks to leonhandreke)
* broken backward compatibility with python2.5 and custom tasks (github `issue #94 <https://github.com/paver/paver/issues/94>`_)
* Variety of Python 3 problems (thanks to `Afrever <https://github.com/Arfrever>`_)
* Ignore non-system-default characters when sh()ing command with bad output

1.2 (February 24, 2013)
------------------------
* ***Python 3 support***, thanks to `@rkuppe <https://github.com/rkruppe>`_
* pypy support now tested on Travis
* ``pip`` now preferred over easy_install (github `issue #81 <https://github.com/paver/paver/issues/81>`_, thanks to pmcnr)
* ``virtual.bootstrap`` enhancements: support for ``find-links``, ``index-url``, ``system-site-packages`` and ``distribute`` options (github `issue #79 <https://github.com/paver/paver/issues/79>`_, thanks to pmcnr)
* new :func:`tasks.consume_nargs` decorator, similar to :func:`tasks.consume_args` but accepting an argument: the number of arguments that the decorated function will consume. If no argument is passed to ``consume_nargs`` decorator, all comand-line arguments will be consumed.


1.1.1 (August 25, 2012)
------------------------
* path.py fix for Jython compatibility (github `issue #70 <https://github.com/paver/paver/issues/70>`_, thanks to Arfrever)
* bundled cog updated to version 2.2 for Jython compatibility
* fixes regression for setuptools intallation (i.e. using --root parameter, github `issue #71 <https://github.com/paver/paver/issues/71>`_, thanks to Afrever for the report and yedpodtrzitko for the fix)
* basic jython compatibility tested

1.1.0 (July 30, 2012)
------------------------
* Minilib is now imported only if full paver is not available (github `issue #13 <https://github.com/paver/paver/issues/13>`_)
* Option instances may now be passed to @cmdopts (github issues `#41 <https://github.com/paver/paver/issues/41>`_ and `#42 <https://github.com/paver/paver/issues/42>`_, thanks to David Cramer)
* ``--propagate-traceback`` option for debugging ``BuildFailure``s (github issue `#43 <https://github.com/paver/paver/issues/43>`_)
* Fix misleading error message when non-task is passed to ``@needs`` (github issue `#37 <https://github.com/paver/paver/issues/37>`_)
* ``@no_help`` to provide a way to hide task from ``paver help`` (github issue `#36 <https://github.com/paver/paver/issues/36>`_)
* ``@might_call`` for more complex dependencies (see docs, not only github issue `#16 <https://github.com/paver/paver/issues/16>`_)
* bundled path.py upgraded to patched version 2.2.2 (github issue `#15 <https://github.com/paver/paver/issues/15>`_)
* correctly handle dependencies in ``install_requires`` directive for `setup.py install` command (github issue `#49 <https://github.com/paver/paver/issues/49>`_)
* fix creating virtualenv (github issue `#44 <https://github.com/paver/paver/issues/44>`_)
* fix virtualenv example in docs (github issue `#48 <https://github.com/paver/paver/issues/48>`_)
* path.rename() do not call rename twice (github issue `#47 <https://github.com/paver/paver/issues/47>`_)
* updated path.py to resolve issues with bounding os functions with CPython 2.7.3 (github issue `#59 <https://github.com/paver/paver/issues/59>`_, thanks to Pedro Romano)
* minimal version of python raised to Python 2.5 (github issue `#52 <https://github.com/paver/paver/issues/52>`_)
* always import + do not allow to overwrite basic tasks (eg. help) (github issue `#58 <https://github.com/paver/paver/issues/58>`_)
* if virtualenv is not available, PaverImportError is raised instead of generic Exception (github issue `#30 <https://github.com/paver/paver/issues/30>`_)

1.0.5 (October 21, 2011)
------------------------
* Ability to share command line options between tasks (github issue `#7 <https://github.com/paver/paver/issues/issue/7>`_)
* Flush after print (github issue `#17 <https://github.com/paver/paver/issues/issue/17>`_, thanks to Honza Kral)
* Minilib is now compatible with zipimport (github issue `#19 <https://github.com/paver/paver/issues/issue/19>`_, thanks to Piet Delport)
* Auto task is now properly not called when target task is decorated with no_auto (github issue `#4 <https://github.com/paver/paver/issues/issue/24>`_)

1.0.4 (January 16, 2011)
------------------------
* Fixed md5 deprecation warnings in the bundled cog (thanks to jszakmeister, issue #56)
* Project moved to github
* Fixed problems with negative command-line options for distutils (thanks to Nao Nakashima for bugreport, github `issue #2 <https://github.com/paver/paver/issues/2>`_)
* Japanese translation moved to `https://github.com/paver/paver-docs-jp  <http://paver.github.com/paver-docs-jp/>`_
* Tasks take cmdopts even from grandparents (thanks to aurelianito, github issue #4)
* Task description is taken from the first sentence, where the end of the sentence is dot followed by alphanumeric character (google code bug #44). Description is also stripped now.


1.0.3 (June 1, 2010)
--------------------
* Fixed deadlock problem when there's a lot of output from a subprocess (thanks to Jeremy Rossi)
* Fixed unit tests (thanks to Elias Alma)

1.0.2 (March 8, 2010)
---------------------

* FIXED A command that outputs to stderr containing formatting directives (%s) or something that looks like one would cause an error. Thanks to disturbyte for the patch.
* Tasks can take normal keyword arguments
* Returns exit code 1 if any tasks fail
* stderr is no longer swallowed up by sh() (issue #37, thanks to Marc Sibson for 
  the patch)

1.0.1 (May 4, 2009)
-------------------

This release was made possible by Adam Lowry who helped improve the code and reviewed
committed many of the patches.

* Fixed sending nonpositional arguments first with consume_args (issue #31).
* Fixed use of setuputils without defining options.setup (issue #24).
* Python 2.4 compatibility fixes (issue #28)
* sh() failures are logged to stderr.
* sh() accepts a cwd keyword argument (issue #29).
* virtualenv bootstrap generation accepts no_site_packages, unzip_setuptools,
  and destination directory arguments in options.
* Distutils config files were being ignored (issue #36) (thanks to Matthew Scott for the patch)
* The exit code was 0 whenever the first task passes, even if later tasks fail (issue #35) (thanks to Matt for the patch)
* Tasks can take normal keyword arguments (issue #33) (thanks to Chris Burroughs for the patch with test!)

1.0 (March 22, 2009)
--------------------
* If there is a task called "default", it is run if Paver is run with no
  tasks listed on the command line.
* The auto task is run, even if no tasks are specified on the command line.
* distutils' log output is now routed through Paver's logging functions, 
  which means that the output is now displayed once more (and is controlled 
  via Paver's command line arguments.)
* The paver.setuputils.setup function will automatically call 
  install_distutils_tasks. This makes it a very convenient way to upgrade 
  from distutils/setuptools to Paver.
* Nicer looking error when you run Paver with an unknown task name.
* fix the md5 deprecation warning in paver.path for real (forgot to delete the
  offending import). Also fixed an import loop when you try to import 
  paver.path.
* Improved docs for 1.0
* Paver now requires Sphinx 0.6 for the docs. In Paver's conf.py for Sphinx,
  there is an autodoc Documenter for handling Paver Tasks properly.

1.0b1 (March 13, 2009)
----------------------
* added call_task to environment and paver.easy, so it should be easy to call
  distutils tasks, for example. (Normally, with Paver 1.0, you just call Paver
  tasks like normal functions.)
* added setup() function to paver.setuputils that is a shortcut for 
  setting options in options.setup. This means that you switch from
  distutils to Paver just by renaming the file and changing the
  import.
* the -h command line argument and "help" task have been unified. You'll
  get the same output regardless of which one you use.
* the auto task is no longer called when you run the help task (issue #21).
  As part of this, a new "no_auto" decorator has been created so that any
  task can be marked as not requiring the auto behavior.
* consume_args and PavementError are now included in paver.easy (thanks to
  Marc Sibson)
* more methods in paver.path now check for existence or lack thereof
  and won't fail as a result. (mkdir and makedirs both check that the
  directory does not exist, rmdir and rmtree check to be sure that
  it does.) This is because the goal is ultimately to create or remove
  something... paver just makes sure that it either exists or doesn't.
* fix md5 deprecation warning in paver.path (issue #22)

1.0a4 (March 6, 2009)
---------------------
* call_pavement would raise an exception if the pavement being called is 
  in the current directory
* the new paver.path25 module was missing from the paver-minilib.zip

1.0a3 (March 6, 2009)
---------------------
* Added automatic running of "auto" task. If there's a task with the name "auto",
  it is run automatically. Using this mechanism, you can write code that sets up
  the options any way you wish, and without using globals at all (because the
  auto task can be given options as a parameter).
* When generating egg_info running "paver", the full path to the Paver script
  was getting included in egg-info/SOURCES.txt. This causes installation problems
  on Windows, at the very least. Paver will now instead place the pavement
  that is being run in there. This likely has the beneficial side effect of
  not requiring a MANIFEST.in file just to include the pavement.
* the options help provided via the cmdopts decorator now appears
* pavements can now refer to __file__ to get their own filename. You can also
  just declare pavement_file as an argument to your task function, if
  you wish.
* call_pavement now switches directories to the location of the pavement and
  then switches back when returning
* if you try to run a function as a task, you'll now get a more appropriate
  and descriptive BuildFailure, rather than an AttributeError
* paver can now again run tasks even when there is no pavement present.
  any task accessible via paver.easy (which now also includes misctasks)
  will work.
* added the pushd context manager (Python 2.5+). This will switch into another
  directory on the way in and then change back to the old directory on 
  the way out. Suggested by Steve Howe, with the additional suggestion from
  Juergen Hermann to return the old directory::
  
        with pushd('newdirectory') as olddirectory:
            ...do something...

1.0a2 (February 26, 2009)
-------------------------
* The bug that caused 1.0a1 to be recalled (distutils command options)
  has been fixed thanks to Greg Thornton.
* If you provide an invalid long task name, you will no longer get an 
  AttributeError. Thanks to Marc Sibson.
* If a task has an uncaught exception, the debug-level output is displayed
  *and* Paver will exit with a return code of 1. No further tasks are
  executed. Thanks to Marc Sibson.
* The version number is no longer displayed, so that you can reasonably 
  pipe the output elsewhere. A new --version option will display the version
  as before.
* Eliminate DeprecationWarnings in paver.ssh and paver.svn. Thanks to Marc
  Sibson.
* The html task will always be defined now when you import paver.doctools
  but will yield a BuildFailure if Sphinx is not installed. Hopefully this
  will lead to clearer errors for people. Thanks to Marc Sibson.
* The Getting Started Guide has been improved for 1.0. Additionally,
  the "newway" sample now has a MANIFEST.in which provides useful knowledge
  for people.

1.0a1 (January 28, 2009)
------------------------
(note: 1.0a1 was recalled because it was unable to properly handle distutils command
line options.)

* COMPATIBILITY BREAK: paver.misctasks is no longer imported by default, even when using paver.easy
* DEPRECATIONS: paver.runtime and paver.defaults have been deprecated. Watch the
  warnings for info on how to change to the new paver.easy module.
* COMPATIBILITY WARNING: By default, the sh() function will now raise a 
  BuildFailure exception if the return code of the process is non-zero.
  Passing ignore_error=True will switch back to the previous behavior.
  Thanks to Marc Sibson.
* There is a new call_pavement function (automatically imported with
  from paver.easy import \*) that can call another pavement file. The
  new pavement gets its own environment/options but runs in the same
  process.
* You can now specify an alternate file to run rather than "pavement.py" using
  the -f or --file global option. Thanks to Marc Sibson.
* Regardless of logging level, output for a task is captured. If there is a BuildFailure,
  then that captured output is displayed.
* The new paver.tasks module encapsulates everything needed for running tasks
  in a file. The distutils ties have been reduced.
* @needs now accepts a list of requirements in the form @needs('task1', 'task2')
  (passing in a list still works as well)
* Added paver.bzr (support for Bazaar-NG related operations), courtesy of
  Bryan Forbes.
* The error() function is now exported, for logging of errors (thanks to Marc Sibson)
* Added handy paver.svn.export function for exporting an svn repository revision 
  (thanks to Marc Sibson)
* The "scripts" directory has been renamed "distutils_scripts" to avoid name collision
  on Windows.

0.8.1 (June 2, 2008)
--------------------
* Fix bug in minilib on Windows (error in rmtree). Also simplifies the minilib
  implementation. Patch from Juergen Hermann.
* Fix bug in virtualenv bootstrap generation (patches from Michael Greene and
  Juergen Hermann. Michael Greene's is the one that was applied.)

0.8 (May 19, 2008)
------------------

* Installation on Windows was broken due to a / at the end of the /paver/tests
  path in MANIFEST.in
* Options can now be set on the command line using the syntax option.name=value.
  Options are set at the point in which they appear on the command line, so
  you can set one value before task1 and then another value before task2.
* Option ordering can now take an explicit dictionary or Bunch added to the
  ordering. This allows you to put in new options without changing the global
  options dictionary and more closely resembles how options would be looked
  up in a buildout.
* call_task now supports an optional "options" argument that allows you to
  pass in a dictionary or Bunch that is added to the front of the option
  search ordering.

0.7.3 (May 16, 2008)
--------------------

* Added include_markers parameter to the paver.doctools.Includer to display a nice
  comment with the name of the file and section. This can look more attractive than
  the raw cog. By default, this is turned off. Set options.cog.include_markers
  to an empty dictionary, and the default include markers will be used.
* Added options.cog.delete_code to remove the generator code when cogging.
  Default: false
* Paver 0.7.2 could not be installed by zc.buildout on the Mac due to a problem
  with the py2app command under that environment.
* cog and tests were missing from shipped distributions (bug 229324, fixed with
  a patch from Krys Wilken.)
* Added svn.checkup function that does a checkout or update. This is like an
  svn:externals that's a bit more readable and easier to control, in my opinion.

0.7.2 (May 8, 2008)
-------------------

* Fixed Python 2.4 compatibility. The paver-minilib.zip file contained 2.5 
  .pyc files. .pyc files are not compatible between major Python versions.
  The new version contains .py files.

0.7.1 (May 8, 2008)
-------------------

* 0.7 had a broken paver-minilib.zip (missing misctasks.py, which is now part of the
  standard minilib)

0.7 (May 7, 2008)
----------------------

Breaking changes:

* "targets" have become "tasks", because that name is a clearer description.
* paver.sphinxdoc has been renamed paver.doctools

New features and changes:

* runtime.OPTIONS is gone now. The old voodoo surrounding the options() function
  has been replaced with a distinctly non-magical __call__ = update in the
  Namespace class.
* distutils.core.setup is now the command line driver
* distutils/setuptools commands can be seamlessly intermingled with Tasks
* tasks can have command line settable options via the cmdopts decorator.
  Additionally, they can use the consume_args decorator to collect up
  all command line arguments that come after the task name.
* Two new tasks: cog and uncog. These run Ned Batchelder's Cog code
  generator (included in the Paver package), by default against your
  Sphinx documentation. The idea is that you can keep your code samples
  in separate files (with unit tests and all) and incorporate them
  into your documentation files. Unlike the Sphinx include directives,
  using Cog lets you work on your documentation with the code samples
  in place.
* paver.doctools.SectionedFile provides a convenient way to mark off sections
  of a file, usually for documentation purposes, so that those sections can
  be included in another documentation file.
* paver.doctools.Includer knows how to look up SectionedFiles underneath
  a directory and to cache their sections.
* options are now a "Namespace" object that will search the sections for
  values. By default, the namespace is searched starting with top-level
  items (preserving current behavior) followed by a section named the same
  as the task, followed by all of the other sections. The order can
  be changed by calling options.order.
* option values that are callable will be called and that value returned.
  This is a simple way to provide lazy evaluation of options.
* Added minilib task that creates a paver-minilib.zip file that can be
  used to distribute programs that use Paver for their builds so that
  setup.py will run even without Paver fully installed.
* Added generate_setup task that creates a setup.py file that will
  actually run Paver. This will detect paver-minilib.zip if it's
  present.
* The "help" task has been greatly improved to provide a clearer picture
  of the tasks, options and commands available.
* Add the ability to create virtualenv bootstrap scripts
* The "help" property on tasks has changed to "description"
* output is now directed through distutils.log
* Ever improving docs, including a new Getting Started guide.
* Changes to Paver's bootstrap setup so that Paver no longer uses
  distutils for its bootstrapping.


There were no versions 0.5 and 0.6.

0.4 (April 22, 2008)
--------------------

* First public release.
* Removes setuptools dependency
* More docs
* Paver can now be run even without a pavement.py file for commands like
  help and paverdocs
