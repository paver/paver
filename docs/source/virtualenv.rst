.. _virtualenv:

Virtualenv Support
==================

Paver makes it easy to set up virtualenv environments for development and deployment.
Virtualenv gives you a place to install Python packages and keep them separate from
your main system's Python installation. Paver also includes PoachEggs which will
take a list of eggs in a requirements file and install all of those requirements
for you. When you're ready to deploy, you can "freeze" those requirements, pegging
their version numbers in a new requirements file that you can copy to your deployment
server.

The requirements file format
============================

The requirements file is what poach-eggs uses to install packages.
This document describes that format.

Each line of the requirements file indicates something to be
installed.  For example::

    MyPackage==3.0

tells poach-eggs to install the 3.0 version of MyPackage.  

You can also install a package in an "editable" form.  This puts the
source code into ``src/distname`` (making the name lower case) and
runs ``python setup.py develop`` on the package.  To indicate
editable, use ``-e``, like::

    -e http://svn.myproject.org/svn/MyProject/trunk#egg=MyProject

The ``#egg=MyProject`` part is important, because while you can
install simply given the svn location, the project name is useful in
other places.

If you need to give poach-eggs (and by association easy_install) hints
about where to find a package, you can use the ``-f``
(``--find-links``) option, like::

    -f http://someserver.org/MyPackage-3.0.tar.gz

If the package is named like ``PackageName-Version.tar.gz`` (or a zip)
then you don't need ``#egg=...``.  Note that you cannot provide
multiple ``-f`` arguments to easy_install, but you can in a
requirements file (they all get concatenated into a single ``-f`` for
easy_install).

You can also use ``-Z`` or ``--always-unzip``, which makes poach-eggs
install all packages as unzipped eggs.

paver.virtual Tasks
===================

.. automodule:: paver.virtual
    :members:

