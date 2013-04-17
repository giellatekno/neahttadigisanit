# This code works if you copy paste it into the browser's console,
# however in order for it to work as a bookmarklet, it must be URL
# encoded.

from urllib import quote

with open('static/js/bookmark.min.js', 'r') as F:
    bmark = F.read().replace('\n', '')

bookmarklet_quote = lambda x: quote(x, safe="()")
bookmarklet_escaped = bookmarklet_quote(bmark)

prod_host = "sanit.oahpa.no"
demo_host = "localhost%3A5000"
