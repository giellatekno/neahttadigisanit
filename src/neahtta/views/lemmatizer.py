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





def json_response_pretty(data):
    """Make the json more human friendly.

    Args:
        data (dict): the data to process

    Returns:
        flask.Response
    """
    data = json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

    return Response(response=data, status=200, mimetype="application/json")


class LemmatizerView(DictionaryView, SearcherMixin):
    """A view to produce a json formatted lemma."""
    from lexicon import DetailedFormat as formatter

    @staticmethod
    def get(_from, wordform):
        """Produce a json formatted cleaned lemma of the given wordform.

        Args:
            _from (str): the language the wordform is expected to be
            wordform (str): a string given to the lemmatizer

        Returns:
            flask.Response
        """
        # Check for cache entry here
        errors = []

        tag_language = request.args.get('tag_language', 'eng')
        pretty = request.args.get('pretty', 'eng')

        if _from in current_app.morpholexicon.analyzers:
            morph = current_app.morpholexicon.analyzers[_from]
        else:
            errors.append("Morphology for <%s> does not exist" % _from)

        wordform = decodeOrFail(wordform)

        from morphology.utils import tagfilter

        def filter_tag(lemma):
            """Return a lemma where the tags are filtered.

            Args:
                lemma (morphology.Lemma): the lemma that should be filtered.
            """
            filtered_tag = tagfilter(lemma.tag, _from, tag_language).split(' ')
            return (lemma.lemma, filtered_tag, [lemma.form], lemma.tag.tag_string)

        lemmas = morph.lemmatize(wordform)

        cleaned_lemmas = map(filter_tag, lemmas)

        _tagsets = current_app.config.morphologies.get(_from).tagsets.sets

        tagsets_serializer_ready = {}

        for key, tagset in _tagsets.iteritems():
            tagsets_serializer_ready[key] = [m.val for m in tagset.members]

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
