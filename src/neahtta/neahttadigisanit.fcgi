#!/usr/bin/env python2.7

from flup.server.fcgi import WSGIServer
from neahtta import app

if __name__ == '__main__':
    host = 'localhost'
    port = 2323
    addr = (host, port)
    app.caching_enabled = True
    WSGIServer(app, bindAddress=addr).run()

# vim: set ts=4 sw=4 tw=0 syntax=python expandtab:
