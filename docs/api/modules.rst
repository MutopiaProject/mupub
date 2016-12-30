mupub (a prototype)
===================

This is a prototype for the Mutopia Project build script. It is
structured as a script (:py:mod:`mupub.commands` subpackage) supported
by the main :py:mod:`mupub` library package. The internal workings of
script-in-package works in a supported python-ish fashion,

 - The :py:func:`mupub.__main__` module contains the main routine for
   the script. It performs some configuration and logging tasks, then
   calls into :py:mod:`mupub.cli` module for dispatching.

 - :py:func:`mupub.cli.dispatch` sets up the argument parser, parses
   arguments, then calls into the appropriate command. This module
   defines the top-level help of the script.

 - The :py:mod:`mupub.commands` package contains the various commands
   supported by the script.



.. toctree::
   :maxdepth: 4

   users-guide
   mupub
