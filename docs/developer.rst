=================
 Developer Notes
=================

.. include:: subs.txt


Virtual Environment
-------------------

To create an environment named ``mupub`` that will use python3 and
switch to a working folder called ``$HOME/work/mupub`` when
activated, ::

  $ mkvirtualenv -a $HOME/work/mupub --python=python3 mupub
  $ workon mupub
  (mupub) $ pip install -r requirements.txt
  ...

This implies that you must have, as a minimum to start development,
the following tools installed,

  - ``python3``, 3.5 is preferred. Note that in the ``mkvirtualenv``
    linux command above, the python3 should reference a symbolic link
    to the latest 3.* compiler on your platform.

  - ``virtualenv``, the core virtual environment tool.

  - ``virtualenvwrapper`` which, among other things, provides the
    ``mkvirtualenv`` and ``workon`` commands plus other tools for
    managing virtual environments.


For document writers
~~~~~~~~~~~~~~~~~~~~

This has been separated out to make it easy for document hosting, ::

  $ (mupub) $ pip install -r readthedocs.txt


Application structure
---------------------

The application will be developed as a package with atomic
functionality provided as a set of entry points. An entry point will
be provided for a console application that will parse arguments and
dispatch into the desired command. This can be accomplished using
``setuptools`` and is fairly common. In a ``setup.py``, ::

  setup(
     :
     :
     packages = ['mupub', 'mupub.commands'],
     entry_points = {
         'mupub.registered_commands': [
             'check = mupub.commands.check:main',
         ],
         'console_scripts': [
             'mupub = mupub.__main__:main',
         ],
     },

A stub of the ``check`` command has been created to test this. A
distribution of the package can be built with, ::

  (mupub) $ python setup.py sdist
  (mupub) $ # alternatively,
  (mupub) $ make dist

The entry points as described above will create a distribution that,
when installed, will create a command named ``mupub`` that will
parse the command line, use the first non-option argument as a command
and attempt to call into that command within the package. To add a new
command,

  - Implement the new command in ``mupub.commands``

  - Add the appropriate command to the ``mupub.registered_commands``
    list in ``setup.py``.

  - Remake the distribution
