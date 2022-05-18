# This code works if you copy paste it into the browser's console,
# however in order for it to work as a bookmarklet, it must be URL
# encoded.

from __future__ import absolute_import
import os
try:
    from urllib import quote, quote_plus
except ImportError:
    from urllib.parse import quote, quote_plus

cwd = lambda x: os.path.join(os.path.dirname(__file__), x)

with open(cwd('static/js/bookmark.min.js'), 'r') as F:
    bmark = F.read().replace('\n', '')

bookmarklet_quote = lambda x: quote(x, safe="()")
bookmarklet_escaped = bookmarklet_quote(bmark)

prod_host = "sanit.oahpa.no"


def generate_bookmarklet_code(reader_settings, request_host):
    api_host = reader_settings.get('api_host', request_host)
    media_host = reader_settings.get('media_host', request_host)

    bmarklet = bmark
    bmarklet = bmarklet.replace('OMGNDS_API_HOSTBBQ', '//' + quote_plus(api_host))\
                       .replace('OMGNDS_MEDIA_HOSTBBQ', '//' + quote_plus(media_host))

    return bmarklet
