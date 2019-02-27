""" A view for generating paradigms for a JSON api.

Usage:
    HTTP GET /PROJNAME/from_lang/wordform/?params

    PROJNAME - itwewina, kidwinan, etc
    from_lang - source language to generate paradigm in
    wordform - wordform

    @params - a few things to constrain what paradigms are returned
      pretty - True: returns indented output
      tag_language - crk/eng/otw/etc, change lanaguage of user-friendly tags

History:
 * created after lots of new functionality added: new lemmatizer json
 service needed

"""

from flask import (Response, current_app, json,
                   request)
from utils.encoding import decodeOrFail

from .reader import json_response
from .search import DictionaryView, SearcherMixin

__all__ = [
    'LemmatizerView',
]





def json_response_pretty(data, *args, **kwargs):
    data = json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

    return Response(response=data, status=200, mimetype="application/json")


class LemmatizerView(DictionaryView, SearcherMixin):

    from lexicon import DetailedFormat as formatter

    def options(self, _from, _to, lemma):
        # TODO: return morphologies
        _filters = current_app.config.tag_filters.get((_from, _to), False)
        _tagsets = current_app.config.morphologies.get(_from).tagsets.sets

        tagsets_serializer_ready = {}

        for key, ts in _tagsets.iteritems():
            tagsets_serializer_ready[key] = ts.members

        return json_response({
            'tagsets': tagsets_serializer_ready,
            'filters': _filters
        })

    def get(self, _from, wordform):

        # Check for cache entry here
        errors = []

        tag_language = request.args.get('tag_language', 'eng')
        pretty = request.args.get('pretty', 'eng')

        if _from in current_app.morpholexicon.analyzers:
            morph = current_app.morpholexicon.analyzers[_from]
        else:
            errors.append("Morphology for <%s> does not exist" % _from)

        user_input = wordform = decodeOrFail(wordform)

        has_analyses = False
        cache_key = '+'.join([a for a in [
            _from,
            wordform,
        ] if a])

        from morphology.utils import tagfilter

        ui_locale = get_locale()

        def filter_tag(f):
            filtered_tag = tagfilter(f.tag, _from, tag_language).split(' ')
            return (f.lemma, filtered_tag, [f.form], f.tag.tag_string)

        lemmas = morph.lemmatize(wordform)

        cleaned_lemmas = map(filter_tag, lemmas)

        _tagsets = current_app.config.morphologies.get(_from).tagsets.sets

        tagsets_serializer_ready = {}

        for key, ts in _tagsets.iteritems():
            tagsets_serializer_ready[key] = [m.val for m in ts.members]

        if pretty:
            resp_fx = json_response_pretty
        else:
            resp_fx = json_response

        return resp_fx({
            'cleaned_lemmas': cleaned_lemmas,
            'tagsets': tagsets_serializer_ready,
            'input': {
                'wordform': wordform,
            }
        })
