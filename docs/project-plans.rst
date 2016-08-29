.. mupub application requirements and project plan
.. include:: subs.txt

===================
Mupub Project Plans
===================

This document contains both the requirements for the project as well
as a project plan. Contributing developers will want to start here.


.. _req-project:

Project Requirements
--------------------

The application being developed is a drop-in replacement for an
existing publishing application. This implies a history and a known
amount of usability that must be considered during development.

.. _req-glossary:

Glossary
````````
The following definitions may be useful for
following this document.

.. glossary::

   web site
     In the context of this document, *web site* refers to |mutopia|.

   data server
     The physical store for assets.

   submission
     One or more files that comprise a single piece by a composer. This
     may be a single score in an opus or an entire opus. Large or complex
     submissions may contain multiple files.

   publication
     The transition of a submission to finished assets on the data
     server. A submission is deemed published when its assets can be
     found via the *web site.*

   publisher
     The person assigned to initiate and monitor the *publication* process.

   primary user
     The *publisher*


.. _req-phys:

Physical folder naming
``````````````````````

:PHYS-NAMING: Verify the submitted files follow the appropriate naming
              conve ntion. See also :doc:`archive-naming`.


.. _req-hdr:

Header Verification
```````````````````
Ability to parse the |lilypond| header section of a submission into
key / value pairs and verify that minimum keys exist to continue
publication.

:HDR-COMPDATE: Date of composition is valid according to our
               |mutopia| copyright rules.

:HDR-COMPOSER: Composer key is a valid unique reference to an existing
               composer.

These keys are unique with a format defined as, ::

   <capitalized last name> + <first initial> [ + <initial> ...]

For example, **BachJS**, **BachCPE**, **AguadoD**

:HDR-SOURCE: The source must refer to a valid publishing entity.

:HDR-DATE: The date of the source publication which will be used to
           verify compliance with open source rules.


.. _req-pub:

Publication
```````````
The translation of a submission to assets available on the data server
is known as publication.

:PUB-DEF: The application shall create all assets required for
          publication.

This includes the following,

  - PDF files in US-Letter and A4 format
  - MIDI file(s)
  - ZIP'd PostScript files in US-Letter and A4 format
  - Preview PNG image
  - A single RDF file that fully represents the submission
  - A log of the change history for this submission

:PUB-AUTO: This tool will make every effort to complete all tasks with
           minimal intervention from the user.

Any effort to comply with the definition of automation (see
:ref:`req-glossary`) is acceptable here. It is futile to list every
item that contributes to minimal user interaction so consider this a
minimal set.

  - With the exception of manual review of the published assets, the
    publishing process shall run with minimal interaction with the
    user.

  - The application shall have the ability to deliver new assets, or
    update existing assets, on the data server.

  - It is recommended that publication processes will interact
    tightly with the web site so that assets are available on the
    site as soon as the publishing process completes.

  - In the event of a new submission, the application shall be able
    to generate a unique numeric identifier for the submission.

  - The application shall manage |lilypond| versions so that each
    piece is built against the appropriate compiler.


.. _req-devo-plan:

Project Development Plan
------------------------
This section defines the core development structure of the project.
Implicit in the structure defined here is desire to maintain as modern
a development posture as possible to ease future modifications and
attract skilled contributors.

.. _req-impl-devo:

Implementation and development
``````````````````````````````

:DEVO-LANG: Python3 shall be the language for development and
            implementation.

:DEVO-LIB: Additional packages and libraries may be used as deemed
           necessary by the developers as long as they are available
           in the standard python package index (``pypi``) and can be
           installed and managed with the ``pip`` installer.

:DEVO-VIRT: A virtual environment will be used to manage consistent
            library usage among developers. This is typical of modern
            application development with python.

See also :doc:`developer`

.. _req-test:

Testing and coverage
````````````````````
Unit testing will be an integral part of project development.


:TEST-UNIT: The builtin unit test framework -- ``python -m unittest``
            -- will be used to implement an integrated unit testing
            environment. This is a minimal requirement, developers
            have the option of introducing new test frameworks or
            harnessing as long as the result is a net improvement in
            accuracy or ease of use.

:TEST-COVER: The project will achieve a minimum of 90% code coverage
             at the time of release and it will be a goal to maintain
             this coverage while striving for 100%.

:TEST-BRANCH: Branch analysis will be enabled for all coverage
              reports.


.. _req-doc:

Project Documentation
`````````````````````
:DOC-TOOL: All documentation will be written using |sphinx| and ReST.

:DOC-CODE: Doc strings within python code will be formatted so that
           sphinx tools (autodoc) can be used to create a reasonable
           developer manual.

The following tools are optional but are necessary if you need to
modify existing graphics within documents.

  - ``dia`` for UML diagrams

  - ``inkscape`` for various raster images and icons
