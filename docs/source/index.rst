===========================================
Paver: Easy Scripting for Software Projects
===========================================

.. image:: _static/paver_banner.jpg

Paver is a Python-based build/distribution/deployment scripting tool along the
lines of Make or Rake. What makes Paver unique is its integration with 
commonly used Python libraries. Common tasks that were easy before remain 
easy. More importantly, dealing with *your* applications specific needs and 
requirements is now much easier.

* Build files are :ref:`just Python <justpython>`
* :ref:`One file with one syntax <onefile>`, pavement.py, knows how to manage
  your project
* :ref:`File operations <pathmodule>` are unbelievably easy, thanks to the 
  built-in version of Jason Orendorff's path.py.
* Need to do something that takes 5 lines of code? 
  :ref:`It'll only take 5 lines of code. <fivelines>`.
* Completely encompasses :ref:`distutils and setuptools  <setuptools>` so 
  that you can customize behavior as you need to.
* Wraps :ref:`Sphinx <doctools>` for generating documentation, and adds utilities
  that make it easier to incorporate fully tested sample code.
* Wraps :ref:`Subversion <svn>` for working with code that is checked out.
* Wraps :ref:`virtualenv <virtualenv>` to allow you to trivially create a
  bootstrap script that gets a virtual environment up and running. This is
  a great way to install packages into a contained environment.
* Can use all of these other libraries, but :ref:`requires none of them <nodeps>`
* Easily transition from setup.py without making your users learn about or
  even install Paver! (See the :ref:`Getting Started Guide <gettingstarted>` 
  for an example).

See how it works! Check out the :ref:`Getting Started Guide <gettingstarted>`.

Paver was created by `Kevin Dangoor <blueskyonmars.com>`_ of `SitePen <sitepen.com>`_.

Status
------

Paver is currently alpha release software. There is one major feature (zc.buildout
integration) planned for 1.0. At this point, it is unlikely that there will
be significant changes to the pavement syntax, but there are no guarantees.
If there are breaking changes, they will almost certainly be minor.

See the :ref:`changelog <changelog>` for more information about recent improvements.

Installation
------------

The easiest way to get Paver is if you have setuptools_ installed.

``easy_install Paver``

Without setuptools, it's still pretty easy. Download the Paver .tgz file from 
`Paver's Cheeseshop page`_, untar it and run:

``python setup.py install``

.. _Paver's Cheeseshop page: http://pypi.python.org/pypi/Paver/
.. _setuptools: http://peak.telecommunity.com/DevCenter/EasyInstall

Help and Development
--------------------

You can get help from the `mailing list`_.

If you'd like to help out with Paver, you can check the code out from Googlecode:

``svn checkout http://paver.googlecode.com/svn/trunk/ paver-read-only``

You can also take a look at `Paver's project page on Googlecode <http://code.google.com/p/paver/>`_.

.. _mailing list: http://groups.google.com/group/paver

License
-------

Paver is licensed under a BSD license. See the LICENSE.txt file in the 
distribution.

Contents
--------

.. toctree::
   :maxdepth: 2
   
   foreword
   features
   getting_started
   pavement
   paverstdlib
   cmdline
   articles
   changelog
   todo
   credits

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

