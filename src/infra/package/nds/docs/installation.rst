.. highlight:: shell

============
Installation
============

If you are looking for documentation on how to set up an environment for
developing specifically, see `developing.rst`

Follow the inital installation, then set up an environment.

Stable release
--------------

To install Neahttadigisánit, run this command in your terminal:

TODO: nds isn't available yet in pypi, so there are a few options ... 

.. code-block:: console


From sources
------------

The sources for Neahttadigisánit can be downloaded from the `svn repo`_.

You can checkout the public repository:

.. code-block:: console

    $ svn checkout https://gtsvn.uit.no/langtech/trunk/apps/dicts/nds

Note if you're doing the above step, you probably want to read
Giellatekno's documentation on language infrastructure, because there
are probably way more things you're interested in.

Or download the `tarball`_:

    TODO: haven't built an official release yet.

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install


Environment setup
-----------------

TODO: explain what directory paths we're in when all these commands are
run, no matter how the user has installed the package, we can assume
they're in a virtualenvironment with the nds package installed.

Presently since we're halfway to having a module: 

make sure `dicts` is available in the working path, feel free to just
link it from svn, or check out that dir from svn.

.. code::

  ln -s $GTSVN/apps/dicts/nds/src/neahtta/dicts .


Then do the same for language specific rules, OR if you know what you're
doing (or documentation exists), you can create a new directory for
checkin somewhere else, make sure it's available here and the config
file refers to it. Otherwise:

.. code::

  ln -s $GTSVN/apps/dicts/nds/src/neahtta/configs/language_specific_rules .

Then you should be able to run the following command to test that
everything works and further troubleshoot: 

.. code::

    neahtta config.yml serve

Generating a secret key
-----------------------

.. code::

    neahtta generate_secret > secret_key.do.not.check.in


Installing node dependencies
----------------------------

If you see the following error message:

.. code::

    Couldn't find uglify js: `npm install uglify-js`

.. code::

    npm install


Installing custom locales
-------------------------

NDS projects usually contain minority languages that are not supported
by babel, the localization packge used in the project. If you have
locale files for these, you can install them, otherwise you can use a
`neahtta` command to automatically create files (it simply copies the
English one). For NDS this is sufficient for now.

.. code::

    $ neahtta <path_to_config> generate_locales


TODO: configure static dir paths?

