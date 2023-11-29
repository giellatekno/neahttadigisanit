# This code works if you copy paste it into the browser's console,
# however in order for it to work as a bookmarklet, it must be URL
# encoded.

# import os
from urllib.parse import quote, quote_plus

bmark = "javascript:(function()%7B(function()%7Bvar%20e%3D%22OMGNDS_API_HOSTBBQ%22%2Ct%3D%22OMGNDS_MEDIA_HOSTBBQ%22%2Cn%3D%220.0.4%22%2Ca%3D%22file%3A%22%3D%3D%3Dwindow.location.protocol%3F%22http%3A%22%3A%22%22%2Co%3Ddocument.createElement(%22link%22)%3Bo.href%3Da%2Bt%2B%22%2Fstatic%2Fcss%2Fjquery.neahttadigisanit.css%22%2Co.rel%3D%22stylesheet%22%3Bvar%20d%3Ddocument.createElement(%22script%22)%3Bif(d.type%3D%22text%2Fjavascript%22%2Cd.src%3Da%2Bt%2B%22%2Fstatic%2Fjs%2Fbookmarklet.min.js%22%2Cwindow.NDS_API_HOST%3De%2Cwindow.NDS_BOOKMARK_VERSION%3Dn%2C%22skuvla.info%22%3D%3Dwindow.location.hostname%26%26window.frames.length%3E0)%7Bvar%20i%3Bi%3Dwindow.frames%5B1%5D%2Ci.window.NDS_API_HOST%3Dwindow.NDS_API_HOST%2Ci.document.getElementsByTagName(%22head%22)%5B0%5D.appendChild(o)%2Ci.document.getElementsByTagName(%22body%22)%5B0%5D.appendChild(d)%7Delse%20document.getElementsByTagName(%22head%22)%5B0%5D.appendChild(o)%2Cdocument.getElementsByTagName(%22body%22)%5B0%5D.appendChild(d)%7D)()%3B%7D)()"


# def cwd(x):
#     return os.path.join(os.path.dirname(__file__), x)


# def bookmarklet_quote(x):
#     return quote(x, safe="()")


# TODO
# fails on server:
# FileNotFoundError: [Errno 2] No such file or directory:
# '/home/neahtta/git-neahtta-test/neahtta/venv/lib/python3.9/site-packages/static/js/bookmark.min.js'
# when the package is installed (using pip install .), site-packages/ is
# filled with each individual file and folder from the src/ directory.
# but "static" is not included. if I can get it to be included, maybe it'll
# work.

# anders: just pasted inline, this isn't supposed to change, right?
# with open(cwd("src/static/js/bookmark.min.js")) as f:
#    bmark = f.read().replace("\n", "")

# anders: it seems to be already replaced? is this correct? Is this wrapping
# another layer of encoding or something?
bookmarklet_escaped = quote(bmark, safe="()")  # bookmarklet_quote(bmark)

prod_host = "sanit.oahpa.no"


def generate_bookmarklet_code(reader_settings, request_host):
    api_host = reader_settings.get("api_host", request_host)
    media_host = reader_settings.get("media_host", request_host)

    bmarklet = bmark
    bmarklet = bmarklet.replace(
        "OMGNDS_API_HOSTBBQ", "//" + quote_plus(api_host)
    ).replace("OMGNDS_MEDIA_HOSTBBQ", "//" + quote_plus(media_host))

    return bmarklet
