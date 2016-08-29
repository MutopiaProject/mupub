.. _publication:

Publication
===========

.. include:: subs.txt

Historical Overview
-------------------

These are the major tasks in the process of publishing a submission to
the Mutopia Project catalog:

  - Building the assets from a contribution source.

  - Synchronizing the assets with the data server (publishing).

  - Updating the website so users can access published assets.

Several submissions can be processed before updating the website. The
flow looks something like this,

.. image:: /graphics/pub-historical.svg
   :width: 66%
   :align: center

Some notes on this flow chart:

  - Merging submissions is a GIT task.

  - Assigning an ID, updating headers,and asset building are done
    using a combination of java application and shell script.

  - Updating the HTML is done via a perl script (``Update_website.pl``)
    that,

    - rebuilds the data and search caches

    - rebuilds all HTML files

  - Synchronizing is a separate operation, typically done with a tool
    like ``rsync``.

This works great because the MutopiaProject website is static HTML and
the caches are read-only. Everything is built off-line so the speed is
reasonable. Problems arise when,

  - Diacritical search is desired or you want to expand search
    functionality outside the capabilities of the cache design.

  - When you want to start tracking download counts for the purpose of
    popularity metrics.

  - The cache design causes an excessive burden on the server.


Database-driven Publication
---------------------------

The effort for a database started when I wanted a reasonable way to do
*ad hoc* queries --- I wanted to be able to mine information from our
archive for the purpose of maintenance. The first attempts at doing
this with the cache files were frustrating because I needed to write
code for each bit of information I wanted to draw out of the files. I
started looking at the RDF files, generated as part of the publication
phase, and found that if the data in the RDF file were in a database
then I could query all I wanted. Once I had the schema designed, it
was very little work to get the |django| :abbr:`ORM (Object
Relationshiop Model)` to reflect the database design.

Since we have a static web site and data access is read-only, what
exactly is the advantage of using |django| and a database? There are a
few,

  - Performance

    - Database access on a server is nicely balanced for efficient
      multiple connections to a web presentation.

    - There are tuning opportunities at the server level, as well as
      support in |django| for caching and static file serving. The
      static data (CSS, images, etc.) can be easily distributed.

    - Creates an easy path to separating catalog searching from data
      storage, which is how the |heroku| demo server works now
      with the database on |heroku| and the physical pieces on
      ``MutopiaProject.org``.

  - Convenience

    - Takes one step out of the process flow (the mass building of
      static HTML files).

    - Allows *ad hoc* queries on the database itself (without |django|) and
      an easy path to scripts that could use the |django| frameworks
      to access the data.

    - The templating system supports inheritance to reduce code
      duplication.

  - Ease of development

    - Lots of current libraries and tools to support |django| and its
      deployment. Its :abbr:`ORM (Object Relationshiop Model)` makes
      it easy to query data without writing SQL.

    - |postgres| is a well-respected high-performance database
      package that is popular on servers.

    - Python is a good base tool for all our tools and should attract
      volunteers.


It's an evolution
~~~~~~~~~~~~~~~~~

The new publication model is largely based on the existing one. With
the |django| mutopia app, the HTML pages are generated dynamically via
templates. Python and :abbr:`WSGI (Web Server Gateway Interface)` are
now driving the web site and our process flow no longer needs the
``Update HTML`` step but requires a database update after
synchronizing with the data server:

.. image:: /graphics/pub-evolved.svg
   :width: 66%
   :align: center

After the assets are built for each piece the ``AssetMap`` is updated.
This is a database table that forms a bridge between a ``Piece``
structure and its physical assets on a file storage device. If the
``Piece`` is new, a new ``AssetMap`` row is inserted with a null
relationship to the ``Piece``. If this is an edit the existing
``AssetMap`` is updated to a null ``Piece`` relationship.

At the end of this publication step, the ``Piece`` is not yet
available on the website; we need a database update:

.. image:: /graphics/pub-db-update.svg
   :width: 66%
   :align: center

This update is performed by walking through the ``AssetMap`` and
finding assets that have a null ``Piece`` reference. For each new or
changed ``Piece``, the associated RDF file (created with the asset
build) is loaded and that data is used to update an existing ``Piece`` or
insert a new ``Piece``.

Once all submissions are merged, the materialized view that manages
:abbr:`FTS (Full Text Search)` can be updated to reflect changes.
