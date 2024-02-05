from flask import Response, current_app, json, request

from neahtta.utils.json import fmtForCallback

__all__ = ["autocomplete"]


def autocomplete(from_language, to_language):
    has_callback = request.args.get("callback", False)

    try:
        lookup_key = request.args["lookup"]
    except KeyError:
        return fmtForCallback(
            json.dumps(" * autocomplete requires lookup query param"), has_callback
        )

    autocomplete_tries = current_app.config.lexicon.autocomplete_tries
    try:
        autocompleter = autocomplete_tries[from_language, to_language]
    except KeyError:
        return fmtForCallback(
            json.dumps(" * No autocomplete for this language pair."), has_callback
        )

    autos = autocompleter.autocomplete(lookup_key)
    if not autos:
        autos = autocompleter.autocomplete(lookup_key.strip())

    # Only lemmatize if nothing returned from autocompleter?
    return Response(
        response=fmtForCallback(json.dumps(autos), has_callback),
        status=200,
        mimetype="application/json",
    )
