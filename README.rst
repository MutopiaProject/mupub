mupub - A publishing tool for the Mutopia Project

.. image:: https://readthedocs.org/projects/mutopia-rewrite/badge/?version=latest
   :target: http://mutopia-rewrite.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

Synopsis
--------
Currently the back-end publication software is a collection of shell
scripts and Java; this project aims to update this set of tools into a
more cohesive and flexible application with more opportunities for
automation.


Development setup
-----------------

This project uses typical Python3 tools. A virtual environment is
recommended to help manage the installed tools. In Ubuntu Linux, ::

  $ sudo apt-get install virtualenv

At Ubuntu 16.04 onward, a convenient set of wrapper functions and
scripts are available, ::

  $ sudo apt install virtualenvwrapper
  $ echo "source /usr/share/virtualenvwrapper/virtualenvwrapper.sh" >> ~/.bashrc

The wrapper can be organized as you like, but I prefer to manage a
single folder hierarchy like this, ::

  $ export WORKON_HOME=~/.virtualenvs
  $ mkdir $WORKON_HOME
  $ echo "export WORKON_HOME=$WORKON_HOME" >> ~/.bashrc
  $ source ~/.bashrc

To create and populate a virtual environment named ``mupub`` for this
project, ::

  $ cd <your cloned workspace>
  $ mkvirtualenv -a $PWD -r requirements.txt -p python3 mupub

To do development on the project you `activate` the environment using
the ``workon`` command and leave it using ``deactivate``, ::

  glenl@lola:mupub$ workon mupub
  (mupub) glenl@lola:mupub$
  (mupub) glenl@lola:mupub$ make test # for example
  (mupub) glenl@lola:mupub$ deactivate
  glenl@lola:mupub$

Peruse the ``Makefile`` for useful development targets. You may need
to use the `install` target to create the command-line utility to test
the application CLI.


Installing a release
--------------------
This is a command line tool that will be distributed using standard
python3 mechanisms. The distribution will be in the form of a
compressed file with the release version embedded in it. For example, ::

  (mupub) glenl@lola:mupub$ ls dist
  mupub-0.2.2.tar.gz


Installation can be accomplished with the following set of commands on
the example distribution, ::
  
  $ mkdir tmp && cd tmp
  $ zcat ../mupub-0.2.2.tar.gz | tar xvf -
  $ cd mupub-0.2.2
  $ # install library
  $ python3 -m setup install --user
  $ # install command script
  $ python3 -m pip install mupub --user
  $ cd .. && rm -rf tmp

Note the ``--user`` flag on the install and pip commands to install locally without
requiring a privileged account. You can see the results of the
installation with, ::

  $ which mupub
  /home/glenl/.local/bin/mupub
  $ mupub --version
  mupub version 0.2.2
