.. _changelog:

Paver Changelog
===============

1.0a1 (unreleased)
----------------
* COMPATIBILITY BREAK: paver.misctasks is no longer imported by default, even when using paver.easy
* DEPRECATIONS: paver.runtime and paver.defaults have been deprecated. Watch the
  warnings for info on how to change to the new paver.easy module.
* COMPATIBILITY WARNING: By default, the sh() function will now raise a 
  BuildFailure exception if the return code of the process is non-zero.
  Passing ignore_error=True will switch back to the previous behavior.
  Thanks to Marc Sibson.
* Regardless of logging level, output for a task is captured. If there is a BuildFailure,
  then that captured output is displayed.
* The new paver.tasks module encapsulates everything needed for running tasks
  in a file. The distutils ties have been reduced.
* @needs now accepts a list of requirements in the form @needs('task1', 'task2')
  (passing in a list still works as well)
* Bundles (temporarily) PoachEggs and adds tasks for paver.virtual to support
  using PoachEggs to manage your eggs.
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
