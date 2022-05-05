#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
A service that provides JSON and RESTful lookups to GT-style XML lexica,
with preprocessing from morphological analysers implemented as FSTs.

This is the main file which handles initializing the app and providing
endpoint functionality.

"""
from __future__ import absolute_import
from __future__ import print_function
from application import create_app
import sys

app = create_app()
config = app.config

if __name__ == "__main__":
    app.caching_enabled = True
    if 'development' or 'dev' in sys.argv:
        app.production = False
        print("!! Running in development mode")
        sys.stdout.flush()
    else:
        app.production = True
        print("!! Running in production mode")
        sys.stdout.flush()

    app.run(debug=True, use_reloader=False)

# vim: set ts=4 sw=4 tw=72 syntax=python expandtab :
