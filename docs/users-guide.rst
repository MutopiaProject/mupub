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
      --version             show program's version number and exit
      --verbose             louder

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
      --dry-run   Show what would be done but don't do it.


Examples
--------

Installation
~~~~~~~~~~~~

.. code-block:: text

  glenl@lola:Concerto_No3$ python3 -m pip install ~/work/mupub/dist/mupub-0.3.0-py2.py3-none-any.whl --user
  Processing /home/glenl/work/mupub/dist/mupub-0.3.0-py2.py3-none-any.whl
  Requirement already satisfied: clint>=0.5.1 in /home/glenl/.local/lib/python3.5/site-packages (from mupub==0.3.0)
  Requirement already satisfied: pypng>=0.0.18 in /home/glenl/.local/lib/python3.5/site-packages (from mupub==0.3.0)
  Requirement already satisfied: setuptools>=0.7.0 in /usr/lib/python3/dist-packages (from mupub==0.3.0)
  Requirement already satisfied: ruamel.yaml>=0.12.18 in /home/glenl/.local/lib/python3.5/site-packages (from mupub==0.3.0)
  Requirement already satisfied: requests>=2.11.1 in /home/glenl/.local/lib/python3.5/site-packages (from mupub==0.3.0)
  Requirement already satisfied: args in /home/glenl/.local/lib/python3.5/site-packages (from clint>=0.5.1->mupub==0.3.0)
  Installing collected packages: mupub
  Successfully installed mupub-0.3.0
  glenl@lola:Concerto_No3$ which mupub
  /home/glenl/.local/bin/mupub
  glenl@lola:Concerto_No3$ mupub --version
  mupub version 0.3.0


Build
~~~~~

This is a recent update to |LilyPond| 2.19.46 and output shows the
compiler resolves to 2.19.51 as expected. Also, because this naming is
correct and it is a single piece, it is possible to accomplish a build
with a simple build directives (no other parameters). I've truncated
long lines from ``Interpreting music...`` for brevity.

.. code-block:: text

  glenl@lola:Concerto_No3$ pwd
  /home/glenl/work/mu/ftp/BeethovenLv/O37/Concerto_No3
  glenl@lola:Concerto_No3$ mupub check
  LilyPond compiler will be /home/glenl/.mupub/lycache/2.19.51-1/bin/lilypond
  glenl@lola:Concerto_No3$ mupub build
  Building score, page size = a4
  GNU LilyPond 2.19.51
  Processing `Concerto_No3-lys/Concerto_No3.ly'
  Parsing...
  Interpreting music...[8][16] ...
  Preprocessing graphical objects...
  Interpreting music...
  MIDI output to `Concerto_No3.midi'...
  Finding the ideal number of pages...
  Fitting music on 102 or 103 pages...
  Drawing systems...
  Layout output to `/tmp/lilypond-LMtloT'...
  Copying to `Concerto_No3.ps'...
  Converting to `Concerto_No3.pdf'...
  Deleting `/tmp/lilypond-LMtloT'...
  Success: compilation successfully completed
  Building score, page size = letter
  GNU LilyPond 2.19.51
  Processing `Concerto_No3-lys/Concerto_No3.ly'
  Parsing...
  Interpreting music...[8][16] ...
  Preprocessing graphical objects...
  Interpreting music...
  MIDI output to `Concerto_No3.midi'...
  Finding the ideal number of pages...
  Fitting music on 102 or 103 pages...
  Drawing systems...
  Layout output to `/tmp/lilypond-iEntMb'...
  Copying to `Concerto_No3.ps'...
  Converting to `Concerto_No3.pdf'...
  Deleting `/tmp/lilypond-iEntMb'...
  Success: compilation successfully completed
  Building preview and midi
  GNU LilyPond 2.19.51
  Processing `Concerto_No3-lys/Concerto_No3.ly'
  Parsing...
  Interpreting music...[8][16] ...
  Preprocessing graphical objects...
  Interpreting music...
  MIDI output to `Concerto_No3.midi'...
  Finding the ideal number of pages...
  Fitting music on 102 or 103 pages...
  Drawing systems...
  Layout output to `Concerto_No3.preview.svg'...
  Success: compilation successfully completed
  Creating RDF file
  glenl@lola:Concerto_No3$ ls -1
  Concerto_No3-a4.pdf
  Concerto_No3-a4.ps.gz
  Concerto_No3-let.pdf
  Concerto_No3-let.ps.gz
  Concerto_No3-lys
  Concerto_No3-lys.zip
  Concerto_No3.mid
  Concerto_No3-preview.svg
  Concerto_No3.rdf

Generated RDF
~~~~~~~~~~~~~

.. code-block:: xml

  <?xml version='1.0' encoding='UTF-8'?>
  <rdf:RDF xmlns:mp="http://www.mutopiaproject.org/piece-data/0.1/"
           xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about=".">
      <mp:title>Piano Concerto No. 3 in C Minor (1st Movement: Allegro con brio)</mp:title>
      <mp:composer>BeethovenLv</mp:composer>
      <mp:opus>Op. 37</mp:opus>
      <mp:lyricist />
      <mp:for>Piano and Orchestra</mp:for>
      <mp:date>19th Century</mp:date>
      <mp:style>Classical</mp:style>
      <mp:metre />
      <mp:arranger />
      <mp:source>Breitkopf and Hartel (1862-1865)</mp:source>
      <mp:licence>Public Domain</mp:licence>
      <mp:lyFile>Concerto_No3-lys.zip</mp:lyFile>
      <mp:midFile>Concerto_No3.mid</mp:midFile>
      <mp:psFileA4>Concerto_No3-a4.ps.gz</mp:psFileA4>
      <mp:pdfFileA4>Concerto_No3-a4.pdf</mp:pdfFileA4>
      <mp:psFileLet>Concerto_No3-let.ps.gz</mp:psFileLet>
      <mp:pdfFileLet>Concerto_No3-let.pdf</mp:pdfFileLet>
      <mp:pngFile>Concerto_No3-preview.svg</mp:pngFile>
      <mp:pngHeight>0</mp:pngHeight>
      <mp:pngWidth>0</mp:pngWidth>
      <mp:id>Mutopia-2016/12/29-899</mp:id>
      <mp:maintainer>Stelios Samelis</mp:maintainer>
      <mp:maintainerEmail />
      <mp:maintainerWeb />
      <mp:moreInfo />
      <mp:lilypondVersion>2.19.46</mp:lilypondVersion>
    </rdf:Description>
  </rdf:RDF>


Listing of zipped source files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

  glenl@lola:Concerto_No3$ unzip -l Concerto_No3-lys.zip
  Archive:  Concerto_No3-lys.zip
    Length      Date    Time    Name
  ---------  ---------- -----   ----
      15502  2017-01-02 13:06   Concerto_No3-lys/pianotwo.ly
       7664  2017-01-02 13:06   Concerto_No3-lys/clarinetti.ly
       8863  2017-01-02 13:06   Concerto_No3-lys/oboi.ly
       9788  2017-01-02 13:06   Concerto_No3-lys/violinotwo.ly
       8487  2017-01-02 13:06   Concerto_No3-lys/flauti.ly
       9942  2017-01-02 13:06   Concerto_No3-lys/violinoone.ly
       5966  2017-01-02 13:06   Concerto_No3-lys/cornies.ly
       2683  2017-01-02 13:06   Concerto_No3-lys/Concerto_No3.ly
       7094  2017-01-02 13:06   Concerto_No3-lys/bassi.ly
       9671  2017-01-02 13:06   Concerto_No3-lys/fagotti.ly
       2610  2017-01-02 13:06   Concerto_No3-lys/timpani.ly
       7692  2017-01-02 13:06   Concerto_No3-lys/viola.ly
      18924  2017-01-02 13:06   Concerto_No3-lys/pianoone.ly
       3710  2017-01-02 13:06   Concerto_No3-lys/trombe.ly
  ---------                     -------
     118596                     14 files
  glenl@lola:Concerto_No3$
