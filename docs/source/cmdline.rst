.. _cmdline:

Paver Command Line
==================

Paver does sophisticated command line parsing globally and for each task::

  paver [-q] [-n] [-v] [-f pavement] [-h] [option.name=key] [taskname] [taskoptions] [taskname...]

The command line options are:

-q
  quiet... don't display much info (info and debug messages are not shown)

-n
  dry run... don't actually run destructive commands

-v
  verbose... display debug level output

-h
  display the command line options and list of available tasks. Note
  that -h can be provided for any task to display the command line options
  and detailed help for that task.

-f <pavement>
  use a different file than "pavement.py"


If you run paver without a task, it will only run the "auto" task, if there
is one. Otherwise, Paver will do nothing.

``paver help`` is the equivalent of ``paver -h``, and ``paver help taskname``
is the equivalent of ``paver taskname -h``.

You can set build options via the command line by providing optionname=value.
The option names can be in dotted notation, so ``foo.bar.baz=something`` will
set options['foo']['bar']['baz'] = 'something' in the options. If you need
to enter a value with multiple words, put quotes around the part with the space.

`Important and useful`: Options are set at the point in which they appear in
the command line. That means that you can set an option before one task
and then set it to another value for the next task.
