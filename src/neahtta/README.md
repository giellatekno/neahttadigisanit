Neahttadigisánit
================

This is programmer-directed information, for development. If curious about
linguist-oriented and maintainer documentation, see
[neahttadigisanit][nds_doc].

  [nds_doc]: http://giellatekno.uit.no/doc/dicts/neahttadigisanit.html

## Overview

A service using the [Flask][1] framework to serve up dictionary entries
using XML lexica and morphological analyzer services. Returns data in
JSON, and some HTML.

 [1]: http://flask.pocoo.org/

For more information on package dependencies, see `requirements.txt`.

## Installing

Use [virtualenv][venv] to create an environment with requirements.txt, and set up a
webserver to direct requests to neahttadigisanit.fcgi. The virtualenv could
really go anywhere, but I find it useful to keep it in a local directory so
that I always know where it is.

    virtualenv .env
    . .env/bin/activate
    pip install -r requirements.txt

If more requirements become necessary, be sure to update the file and check it
in.

    pip freeze > requirements.txt

 [venv]: http://www.virtualenv.org/

### Lexical and linguistic dependencies to check

 * svn up main/words/dicts/
 * svn up main/gt/
 * svn up main/langs

#### Makefile

The Makefile in `neahtta/dicts/` can be used to generate dictionary XML files,
and also to compile and manage the installation of FSTs and other morphologies.

See `make help` for more information.

## Developing

### TODOs

See `TODOs`.

### Module-specific documentation.

For Python-module specific documentation, see the docstrings available in the
individual Python files. A short overview follows:

 * `neahtta.py` - initialization of Flask app, endpoints.
 * `config.py` and `configs/` - app configuration, yaml parsing, and yaml files
 * `configs/language_specific_rules` - directory for storing language-specific
   display, morphology and lexicon overrides.
 * `configs/language_names.py` - ISO names and 2-char -> 3-char definitions
 * `translations/` - i18n/i10n/localization details and .po files.
 * `lexicon/` - XML parsing
 * `morphology/` - FST parsing, lemmatization modules
 * `morpholex/` - Thing that ties these two together
 * `static/` - js, css, img, etc.
 * `templates/` - jinja2 templates for endpoints.
 * `dicts/` - path where XML files are typically stored

### XML format

See http://giellatekno.uit.no/doc/dicts/dictionarywork.html


<!---  
vim: set ts=4 sw=4 tw=0 syntax=markdown : -->
