.. include:: subs.txt


mupub package
=============

**Mupub** is structured as a script (:py:mod:`mupub.commands`
subpackage) supported by the main :py:mod:`mupub` library package. The
internals of the script-in-package works in a supported python-ish
fashion,

 - The :py:func:`mupub.__main__` module contains the main routine for
   the script. It performs some configuration and logging tasks, then
   calls into :py:mod:`mupub.cli` module for dispatching.

 - :py:func:`mupub.cli.dispatch` sets up the argument parser, parses
   arguments, then calls into the appropriate command. This module
   defines the top-level help of the script.

 - The :py:mod:`mupub.commands` package contains the various commands
   supported by the script.


Subpackages
-----------

.. toctree::

    mupub.commands


mupub.assets module
-------------------

.. automodule:: mupub.assets
    :members:
    :undoc-members:

mupub.cli module
----------------

.. automodule:: mupub.cli
    :members:
    :undoc-members:

mupub.config module
-------------------

.. automodule:: mupub.config
    :members:
    :undoc-members:

mupub.core module
-----------------

.. automodule:: mupub.core
    :members:
    :undoc-members:

mupub.exceptions module
-----------------------

.. automodule:: mupub.exceptions
    :members:
    :undoc-members:

mupub.header module
-------------------

.. automodule:: mupub.header
    :members:
    :undoc-members:

mupub.lily module
-----------------

.. automodule:: mupub.lily
    :members:
    :undoc-members:

mupub.rdfu module
-----------------

.. automodule:: mupub.rdfu
    :members:
    :undoc-members:

mupub.tagedit module
--------------------

.. automodule:: mupub.tagedit
    :members:
    :undoc-members:

mupub.utils module
------------------

.. automodule:: mupub.utils
    :members:
    :undoc-members:

mupub.validate module
---------------------

.. automodule:: mupub.validate
    :members:
    :undoc-members:
