.. users guide for mupub application script

.. include:: subs.txt

==================
MUPUB User's Guide
==================


Overview
--------

The **mupub** application is implemented as a python support library
containing a command line script. The various commands provided by
this script are described here.

.. note:: This is a preliminary document as many required features
          have not yet been implemented. One important feature,
          :ref:`auto-pieceid`, cannot be fully completed until this
          design has been reviewed.


Installation
------------

This application is still in development and is distributed using a
|wheel| file to make installation a little easier. To install from a
wheel distribution locally.

.. code-block:: bash

  $ python3 -m pip install mupub-0.2.4-py2.py3-none-any.whl --user

The application requires python3. The ``--user`` switch in the above
command will direct pip to install the application and library without
requiring permissions. Installing in this fashion will install all the
required packages. If all the required packages are installed on the
target machine, installations can be accomplished from a simple
distribution package,

.. code-block:: bash

   $ python3 -m setup install mupub-0.2.4.tar.gz --user


General usage
-------------

The mupub application is a collection of commands that mirror the
functionality provided by existing scripts and java code. Because it
is written in a single language, it is hoped that the resulting tool
is more cohesive. As an introduction to the capabilities, it is useful
to look at the help provided by the command-line tool and then outline
the individual commands in more detail.

.. code-block:: text

    $ mupub --help
    usage: mupub [-h] [-v] {init,tag,check,clean,build}

    This is a command-line utility for managing the publication of
    Mutopia Project contributions. All unctionality is provided by
    commands within this utility:

        init  - Initialize workspace. Creates $HOME/.mupub
        check - Reviews the contributed piece for validity.
        tag   - Modifies the header with MutopiaProject fields.
        build - Builds a complete set of output files for publication.
        clean - Clears all build products.

    positional arguments:
      {init,tag,check,clean,build}

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit

    Use mupub <command> --help for specific command help

More detail is provided on these commands in the following sections:

  - :ref:`init-command`
  - :ref:`check-command`
  - :ref:`build-command`
  - :ref:`tag-command`
  - :ref:`clean-command`

.. _init-command:

Initialize Command
~~~~~~~~~~~~~~~~~~
Before using the tool, it is necessary to build a basic configuration.
Running the ``init`` command will initialize a configuration file and
initialize a small database.

  - The configuration file is written in |YAML| and the user can
    edit it after initializing.

  - A small database is created and populated using a command that
    requests information from the configured website.

  - The default logging is a rotating file configuration. The
    definition can be expanded to include console output as well.

**Regarding the database:** SQLite3 is provided within the python
standard library so no additional packages are necessary. The primary
purpose is for validation of these items,

  - Composers
  - Instruments
  - Licenses
  - Styles

These tables are managed on the admin page of the website and it is
not necessary to manually modify this small local database other than
to re-run the ``init`` command with,

.. code-block:: bash

   $ mupub init --sync-only

This will perform only the database synchronization without prompting
for database changes.


.. _check-command:

Check Command
~~~~~~~~~~~~~
This command verifies that a contribution has a valid header. During a
build the `publisher` changes their directory to the target piece
within the MutopiaProject folder hierarchy (see :doc:`archive-naming`)
to execute **mupub** commands. Typically, you would run this command
to verify the contribution is ready to build.

  - Resolve the |LilyPond| source file.
  - Read the header elements.
  - Check that all required header elements are valid.
  - Install the appropriate |lilypond| compiler if necessary.

The goal of the check command is to insure a :ref:`build-command` will
succeed. The command line options are available with,

.. code-block:: text

   $ mupub check --help
    usage: mupub check [-h] [--header-file HEADER_FILE] [infile]

    positional arguments:
      infile                lilypond input file (try to work it out if not given)

    optional arguments:
      -h, --help            show this help message and exit
      --header-file HEADER_FILE
                            lilypond file that contains the header

The ``infile`` positional argument is optional so it is possible to
simply run ``$ mupub check`` on simple cases and the application
will attempt to work out the build using the naming convention. For
more complicated submissions it may be necessary to specify the one or
more ``infiles``. The ``--header-file`` option may be used on very
large submissions where headers are defined in a separate include file.


.. _tag-command:

Tag Command
~~~~~~~~~~~

This command updates the MutopiaProject elements in the header file to
reflect the current copyright graphics and publication date. If it is
a new submission, the integer identifier is passed so that the footer
is updated with the publication date. Just as in :ref:`check <check-command>`
and :ref:`build <build-command>`, the ``--header-file`` option may be used to
locate the header and, if not given, default to the naming convention.
There should only be a single location in a submission where the
header file is defined.

.. note:: This command is ripe for automation. Currently, if the
          identifier is not passed on the command line it is simply
          set to zero. The future is to infer new identifier indices
          from the existing archive.

.. code-block:: text

    $ mupub tag --help
    usage: mupub build [-h] [--header-file HEADER_FILE] [--id ID]

    optional arguments:
      -h, --help            show this help message and exit
      --header-file HEADER_FILE
                            lilypond file that contains the header
      --id ID               Integer portion of the Mutopia identifier



.. _build-command:

Build Command
~~~~~~~~~~~~~

Once the submission has been :ref:`checked <check-command>`, a build
can be done to generate all the assets necessary for publication (see
:ref:`req-pub` for requirements). The command structure is similar to
the :ref:`check-command`,

.. code-block:: text

    $ mupub build --help
    usage: mupub build [-h] [--header-file HEADER_FILE] [--collect-only]
                       [infile [infile ...]]

    positional arguments:
      infile                lilypond input file (try to work it out if not given)

    optional arguments:
      -h, --help            show this help message and exit
      --header-file HEADER_FILE
                            lilypond file that contains the header
      --collect-only        collect built files into publishable assets

A build is sensitive to the complexity of the submission. On large
submissions it may be necessary to *collect* several part files and
provide them as a compressed or zip'ed file. On extremely complex
submissions, it may be necessary to manually build additional files
and then use the ``--collect-only`` option to gather files into
compressed collections.

.. note:: Very complex builds have not been adequately tested.

Use the :ref:`tag-command` before doing a final build for publication.


.. _clean-command:

Clean Command
~~~~~~~~~~~~~

It is likely that you will encounter issues during the build and you
may need to iterate the build process. Doing a build-edit-build cycle
is typically not a problem but for an official build it is a good idea
to start with a clean slate. All this command does is erase any build
files. The command allows a dry-run to allow you to run the command to
see what it would do without actually doing it,

.. code-block:: text

    $ mupub clean --help
    usage: mupub build [-h] [--verbose] [--dry-run]

    optional arguments:
      -h, --help  show this help message and exit
      --verbose   Louder.
      --dry-run   Show what would be done but don't do it.
