==============================================
 Paver - Easy Scripting for Software Projects
==============================================

.. image:: https://github.com/paver/paver/blob/master/docs/source/_static/paver_banner.jpg?raw=true
    :height: 126
    :width: 240

:Web: https://pythonhosted.org/Paver/
:Download: https://pypi.python.org/pypi/Paver/
:Source: https://github.com/paver/paver/
:Keywords: build, scripting, make alternative, svn, git, path.py, documentation,
  automation, tasks, virtualenv, integration

--

.. _paver-synopsis:

Paver is a Python-based software project scripting tool along the lines of
Make or Rake. It is not designed to handle the dependency tracking requirements
of, for example, a C program. It is designed to help out with all of your other
repetitive tasks (run documentation generators, moving files about, downloading
things), all with the convenience of Python’s syntax and massive library of code.


Documentation
=============

Current build status:

.. image:: https://travis-ci.org/paver/paver.svg?branch=master
    :target: https://travis-ci.org/paver/paver

`Documentation`_  is hosted on PyPI (docs for development version are on `GitHub <https://github.com/paver/paver/tree/master/docs/>`_).

.. _`Documentation`: https://pythonhosted.org/Paver/

.. _paver-installation:

Installation
============

You can install Paver either via the Python Package Index (PyPI)
or from source.

To install a PyPI release using `pip`::

    $ pip install -U Paver

… or alternatively from source (github `master`)::

    $ pip install -e git+https://github.com/paver/paver.git#egg=Paver

To install using `easy_install`::

    $ easy_install -U Paver

.. _paver-installation:

Testing
============

Reference test suite can be run using Docker::

	sudo docker run -it paver/paver

When developing locally, build it first::

    sudo docker build -t  paver/paver . && sudo docker run -it paver/paver

When trying to debug inside the dev environment, run::

    sudo docker run -it paver/paver /bin/bash

Alternatively, on your computer without any virtualization to catch environment-specific bugs::

	$ virtualenv paver-venv
	$ source paver-venv/bin/activate
	(paver-venv) $ pip install -r test-requirements.txt
	(paver-venv) $ python setup.py test


.. _getting-help:

Getting Help
============

.. _mailing-list:

Mailing list
------------

For any discussion about usage or development of Paver, you are welcomed to join
the `paver mailing list`_ .

.. _`paver mailing list`: https://groups.google.com/group/paver/

IRC
---

Come chat with us on IRC. The `#paver`_ channel is located at the `Freenode`_
network.

.. _`#paver`: irc://irc.freenode.net/paver
.. _`Freenode`: https://freenode.net

.. _bug-tracker:

Bug tracker
===========

If you have any suggestions, bug reports or annoyances please report them
to GitHub `issue tracker`_.

.. _`issue tracker`: https://github.com/paver/paver/issues/


