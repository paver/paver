.. _cmdline:

Paver Command Line
==================

The Paver command line interface is an extended version of the distutils
command line::

  paver [-q] [-n] [-v] [-h] [option.name=key] [task] [task...]

The command line options are:

-q
  quiet... don't display much info (info and debug messages are not shown)

-n
  dry run... don't actually run destructive commands

-v
  verbose... display debug level output

-h
  display distutils-style command line help


If you run paver without a task, it will default to the "help" task which 
lists the tasks in your pavement.py file. The help task also has the ability
to provide detailed help for a given task.

You can set build options via the command line by providing optionname=value.
The option names can be in dotted notation, so ``foo.bar.baz=something`` will
set options['foo']['bar']['baz'] = 'something' in the options. If you need
to enter a value with multiple words, put quotes around the part with the space.

`Important and useful`: Options are set at the point in which they appear in
the command line. That means that you can set an option before one task
and then set it to another value for the next task.
