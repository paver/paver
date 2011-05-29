.. _discovery:

Task discovery (paver.discovery)
==================================

.. warning::
    This is just an design idea. Nothing actually implemented...yet.

Paver is an excellent point of entry to your application. To facilitate this,
there is an easy way to unify other common tools under one Paver umbrella.

Simple API is provided, so you can easily write your own discovery plugins to
integrate whatever nice tools you encountered.

TODO: Show simple discovery api and usage in pavement.py. Also, note that in
future, setuptools/distutils discovery should be implemented as discovery
plugin so we are better decoupled for non-python users.

Following tools are supported by Paver standard library:

* fabric
* django manage.py commands

Writing discovery plugins
--------------------------

* Always name your function discover_<plugin> (to avoid nameclashes in pavement)


