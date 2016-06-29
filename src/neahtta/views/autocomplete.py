from flask import request, Response, json
from utils.json import fmtForCallback

from . import blueprint
from flask import current_app

__all__ = ["autocomplete"]

def autocomplete(from_language, to_language):

    autocomplete_tries = current_app.config.lexicon.autocomplete_tries
    # URL parameters
    lookup_key   = request.args.get('lookup', False)
    lemmatize    = request.args.get('lemmatize', False)
    has_callback = request.args.get('callback', False)

    autocompleter = autocomplete_tries.get((from_language, to_language), False)

    if not autocompleter:
        return fmtForCallback(
                json.dumps(" * No autocomplete for this language pair."),
                has_callback)

    autos = autocompleter.autocomplete(lookup_key)

    # Only lemmatize if nothing returned from autocompleter?
    return Response(response=fmtForCallback(json.dumps(autos), has_callback),
                    status=200,
                    mimetype="application/json")
