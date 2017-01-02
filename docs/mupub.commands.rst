.. include:: subs.txt

mupub.commands package
======================

The mupub script is implemented as a set of commands. These commands
are registered in setup.py and dispatched to routines within this
package. Each top-level command is implemented in its own module.

Help is provided by way of :py:mod:`argparse` and the available
commands are described when help is requested at the top-level, ::

  $ mupub --help
  usage: mupub [-h] [-v] {check,clean,init,build,tag}

  This is a command-line utility for managing the publication of
  Mutopia Project contributions. All unctionality is provided by
  commands within this utility:

      init  - Initialize workspace. Creates $HOME/.mupub
      check - Reviews the contributed piece for validity.
      tag   - Modifies the header with MutopiaProject fields.
      build - Builds a complete set of output files for publication.
      clean - Clears all build products.

  positional arguments:
    {check,clean,init,build,tag}

  optional arguments:
    -h, --help            show this help message and exit
    -v, --version         show program's version number and exit

  Use mupub <command> --help for specific command help


mupub.commands.build module
---------------------------

.. automodule:: mupub.commands.build
    :members:
    :undoc-members:
    :show-inheritance:

mupub.commands.check module
---------------------------

.. automodule:: mupub.commands.check
    :members:
    :undoc-members:
    :show-inheritance:

mupub.commands.clean module
---------------------------

.. automodule:: mupub.commands.clean
    :members:
    :undoc-members:
    :show-inheritance:

mupub.commands.init module
--------------------------

.. automodule:: mupub.commands.init
    :members:
    :undoc-members:
    :show-inheritance:

mupub.commands.tag module
-------------------------

.. automodule:: mupub.commands.tag
    :members:
    :undoc-members:
    :show-inheritance:
