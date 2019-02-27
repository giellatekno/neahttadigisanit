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

from flask import current_app, json, request
from morphology.utils import tagfilter
from utils.encoding import decodeOrFail

from .reader import json_response
from .search import DictionaryView, SearcherMixin

__all__ = [
    'LemmatizerView',
]


class LemmatizerView(DictionaryView, SearcherMixin):
    """A view to produce a json formatted lemma."""
    from lexicon import DetailedFormat as formatter

    @staticmethod
    def clean_lemma(lang, lemma):
        """Return a lemma where the tags are filtered.

        Args:
            lemma (morphology.Lemma): the lemma that should be filtered.
        """

        filtered_tag = tagfilter(lemma.tag, lang,
                                 request.args.get('tag_language',
                                                  'eng')).split(' ')
        return (lemma.lemma, filtered_tag, [lemma.form], lemma.tag.tag_string)

    def get(self, _from, wordform):
        """Produce a json formatted cleaned lemma of the given wordform.

        Args:
            _from (str): the language the wordform is expected to be
            wordform (str): a string given to the lemmatizer

        Returns:
            flask.Response
        """
        # Check for cache entry here
        morph = current_app.morpholexicon.analyzers[_from]
        wordform = decodeOrFail(wordform)

        return json_response(
            {
                'cleaned_lemmas': [self.clean_lemma(_from, lemma)
                                   for lemma in morph.lemmatize(wordform)],
                'tagsets': self.tagsets_serializer_ready(_from),
                'input': {
                    'wordform': wordform
                }
            },
            pretty=request.args.get('pretty', False)
        )
