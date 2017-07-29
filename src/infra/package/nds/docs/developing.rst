==========
Developing
==========

This page contains the following sections.

.. toctree::
   :maxdepth: 2

   developing
   building

Here's how to set up a development environment using this package.

Check out the source:

1.) svn co $GTSVN/apps/dicts/nds/
2.) switch to gtsvn/apps/dicts/nds/src/infra/package/nds/ ... 
3.) create a virtual environment, and source its activation file

.. code-block::

    $ virtualenv env

4.) Activate the virtual environment.

.. code-block::
    $ . env/bin/activate

5.) Then run the following setup.py command, which will install package
dependencies, compile a dev-only environment (giving access to `neahtta`
and fab commands:

.. code-block:: 

    $ python setup.py develop

Note, whenever you work on the project, repeat steps 4-5.

To test that this works:

.. code-block::

    $ which neahtta

Next, if you're just getting started on developing, you will need to
follow the installation setup in `installation.rst` and set up
project(s) within NDS.

Building a release
------------------

If you need to build a python package for install on a remote system,
follow the following steps:

1.) Bump the version number
2.) Build the package
3.) Copy or transfer the compiled zip file in `dist/blahblah.zip` to the
remote system.


TODO: including npm and bower dependencies-- probably want to
pre-compile and uglify things, and remove that as a part of
application.py
