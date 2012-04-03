.. _virtualenv:

Virtualenv Support (paver.virtual)
==================================

Paver makes it easy to set up virtualenv environments for development and deployment.
Virtualenv gives you a place to install Python packages and keep them separate from
your main system's Python installation.


Using virtualenv with tasks
============================

You may specify which virtual environment should particular task use. Do this
with ``@virtualenv`` decorator::

    from paver.easy import task
    from paver.virtual import virtualenv

    @task
    @virtualenv(dir="virtualenv")
    def t1():
        import some_module_existing_only_in_virtualenv


paver.virtual Tasks
===================

.. automodule:: paver.virtual
    :members:

