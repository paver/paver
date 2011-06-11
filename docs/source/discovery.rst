.. _discovery:

Task discovery (paver.discovery)
==================================

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


Discovery in standard library
-------------------------------

Setuptools
~~~~~~~~~~~~~

Discovery of distutils/setuptools commands is tightly integrated into Paver.
See separate :ref:`setuptools <setuptools>` chapter.

Unlike other discoveries, setuptools commands are not namespaced.

Django
~~~~~~~~~~~~~

To use Django commands, you must tell paver where your project settings are::

    options(
        discovery = Bunch(
            django = Bunch(
                settings_path = "%s"
            )
        )
    )

and explicitly add them::


    from paver.discovery import discover_django

    discover_django(options)

Now you can use all django commands, namespaced by ``django.`` prefix, i.e.::

    paver django.validate --traceback

