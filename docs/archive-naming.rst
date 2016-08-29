.. document to clarify naming conventions

.. include:: subs.txt

================
 Archive Naming
================
This document describes how existing and new entries should be named
for the purpose of consistency.


Introduction
------------

This document is concerned with the structure of the archive so some
definitions are in order,

.. _archive-glossary:

web server
    Where the |mutopia| web pages are served.

archive
    The hiearchy of file folders that hold the published assets of the
    Mutopia Project. The *archive* has a consistent structure to allow
    cataloging tools like our *web server* to locate pieces for the user.
    All submissions into the archive must be consistent with the
    structure.

data server
    A network entity that physically stores pieces in the archive.This
    *data server* could be located on the same host as the *web server*
    or a separate cloud server.


The archive file structure
--------------------------

It is probably easiest to explain the basic structure and then go
through some examples, ::

  ftp
  ├── COMPOSER
  │   └── SIMPLE-PIECE-NAME
  │       └── SIMPLE-PIECE.ly
  │   ├── COMPLEX-PIECE
  │   │   └── COMPLEX-PIECE-lys
  │   │       ├── PART-1.ly
  │   │       ├── PART-2.ly
  │   ├── OPUS
  │   │   ├── SIMPLE-PIECE-NAME
  │   │   │   └── SIMPLE-PIECE.ly
  │   │   ├── COMPLEX-PIECE-NAME
  │   │   │   └── COMPLEX-PIECE-NAME-lys
  │   │   │       ├── PIECE-PART-1.ly
  │   │   │       ├── PIECE-PART-2.ly


There are examples of simple pieces at the top of our archive, ::

  ftp
  ├── AbtF
  │   └── swallows
  │       └── swallows.ly
  ├── AdamA
  │   ├── giselle
  │       └── giselle.ly
  ├── AlbenizIMF
  │   └── O71
  │       └── Rumores_de_la-caleta
  │           └── Rumores_de_la-caleta.ly

An example of a complex piece is this Bach Air in BWV1068, ::

  ├── BachJS
  │   ├── BWV1068
  │   │   ├── air-tromb
  │   │   │   └── air-tromb.ly
  │   │   ├── bach-air
  │   │   │   └── bach-air-lys
  │   │   │       ├── bach-air-continuo.ly
  │   │   │       ├── bach-air-notes.ly
  │   │   │       ├── bach-air-score.ly
  │   │   │       ├── bach-air-viola.ly
  │   │   │       ├── bach-air-violin1.ly
  │   │   │       └── bach-air-violin2.ly
  │   │   └── bach_air_bmv_1068
  │   │       └── bach_air_bmv_1068.ly


.. _naming-glossary:

ftp
    The top of the hierarchy is a folder called ``ftp``. The naming
    is traditional and does not imply that the access must be the
    file transfer protocol.

COMPOSER
    The name of the composer. This is a specially formatted name that
    describes a single composer. It has the format of, ::

      <capitalized-lastname><uppercase-initial>[+<uppercase initial>...]

    These are formatted in this fashion to keep the file hierarchy
    simple and to allow software mechanisms to lookup extended
    information using this name. The characters are ASCII (not UTF-8)
    and contain no punctuation. Some examples are **BachJS**,
    **BachCPS**, and **KuffnerJ**.

SIMPLE-PIECE-NAME
    A name for the submitted piece, formatted without spaces but may
    contain underscores or hyphens. The name must be unique for this
    composer. The built assets, including |lilypond| files, will be
    found here.

COMPLEX-PIECE-NAME
    A container for a more complex piece. Like SIMPLE-PIECE-NAME, the
    built assets will be found here, but the |lilypond| files will be
    found in a folder of the same name with the ``-lys`` suffix. When
    built, the |lilypond| files will be collected into a zip file.

OPUS
    This is an extra level in the hierarchy to allow pieces to be more
    closely associated with their containing opus. There may be
    SIMPLE- or COMPLEX- PIECE-NAME folders under an OPUS.


An attempt at a naming grammar
``````````````````````````````
The location of the |lilypond| files is determinant and the grammar
for building the name of the containing folder might look something
like this,

.. productionlist::
   piece-folder : `composer` "/" name-folder "/" piece-sub-folder
   name-folder : `name` | opus-folder
   opus-folder : `opus` "/" `name`
   piece-sub-folder : simple | complex
   simple: `name`
   complex: `name` "/" `name` "-lys"
