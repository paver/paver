.. _todo:

Paver todos
===========

* when calling distutils commands, if options.setup changes, copy the options
  to the Distribution object
* be able to pass an options dictionary to call_task and have that be the lead
  namespace. Additionally, there should be a decorator for tasks that sets
  the default order for that task, but this will be overridden by the
  call_task value.
* incorporate cog for file inclusion.

* Capture BuildFailures better
* lazily evaluated config parameters
* Wrap errors that come up in path.py with BuildFailures
* Wrap errors in sh() calls in BuildFailures
* '-f' command line flag to select a different pavement
* zc.buildout support (or similar functionality)
* Use Paramiko to handle deployment tasks
* More docs
