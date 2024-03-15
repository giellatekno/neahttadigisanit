#!/usr/bin/env python
"""
A service that provides JSON and RESTful lookups to GT-style XML lexica,
with preprocessing from morphological analysers implemented as FSTs.

This is the main file which handles initializing the app and providing
endpoint functionality.
"""
import sys
from neahtta.application import create_app

# from werkzeug.middleware.profiler import ProfilerMiddleware

# tracing memory usage, only when debugging locally, because it slows
# the whole thing down to a crawl
# import tracemalloc
# tracemalloc.start()

app = create_app()
# app.wsgi_app = ProfilerMiddleware(app.wsgi_app,
#        stream=None,
#        profile_dir="profiling")
config = app.config

if __name__ == "__main__":
    app.caching_enabled = True
    if "development" in sys.argv or "dev" in sys.argv:
        app.production = False
        print("!! Running in development mode")
        sys.stdout.flush()
    else:
        app.production = True
        print("!! Running in production mode")
        sys.stdout.flush()

    app.run(debug=True, use_reloader=False)
