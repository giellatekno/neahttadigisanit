""" A view for generating paradigms for a JSON api.

Usage:
    HTTP GET /PROJNAME/from_lang/to_lang/lemma/?params

    PROJNAME - itwewina, kidwinan, etc
    from_lang - source language to generate paradigm in
    to_lang - language translations to display (if any)
    lemma - word lemma

    @params - a few things to constrain what paradigms are returned
      pos - part of speech, case sensitive, V, Pron, etc.
      e_node - the node ID for the entry to use as the canonical lemma.
      (you may not need this, however you'll see this value pop up in
      the HTML interface in URL parameters)

History:
 * originally developed as part of asynchronous paradigms, for when we
   had really slow FSTs in crk.
 * New interest in using this type of thing as a service for other north
   american languages, combined with the reader lookup stuff.
 * rehabilitated into use after lots of new functionality added: new
   paradigm system needed, added pretty print option for json output

"""
from __future__ import print_function

import inspect

from flask import (Response, abort, current_app, g, json, redirect,
                   render_template, request, session)
from i18n.utils import get_locale
from morphology.utils import tagfilter
from utils.encoding import decodeOrFail

from . import blueprint
from .reader import json_response
from .search import DictionaryView, SearcherMixin

__all__ = [
    'ParadigmLanguagePairSearchView',
]


def lineno():
    """Return the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno


class ParadigmLanguagePairSearchView(DictionaryView, SearcherMixin):

    from lexicon import DetailedFormat as formatter

    @staticmethod
    def clean_lemma(lemma):
        print(lineno(), lemma.tag)
        filtered_tag = tagfilter(lemma.tag, g._from, g._to).split(' ')
        print(lineno(), lemma.input, filtered_tag, [lemma.form], lemma.tag.tag_string)
        return (lemma.input, filtered_tag, [lemma.form], lemma.tag.tag_string)

    def get_paradigms(self, _from, lemma):

        # Generation constraints
        # Sjekk om ordklasse er satt
        pos_filter = request.args.get('pos', False)

        # Sjekk om e_node er satt
        e_node = request.args.get('e_node', False)

        # Sjekk om paradigmene er mellomlagret
        cache_key = '+'.join(
            [a for a in [
                _from,
                lemma,
                pos_filter,
                e_node,
            ] if a])

        paradigms = current_app.cache.get(cache_key.encode('utf-8'))

        # Bestem search_kwargs
        search_kwargs = {
            'split_compounds': True,
            'non_compounds_only': True,
            'no_derivations': False,
        }

        # Lag paradigmer om de ikke er mellomlagret
        if paradigms is None:
            paradigms = \
                self.search_to_paradigm(lemma,
                                        detailed=True,
                                        **search_kwargs)

        return [map(self.clean_lemma, paradigm) for paradigm in paradigms]

    def get(self, _from, _to, lemma):
        # TODO: submit and process on separate thread, optional poll
        # argument to not submit and just check for result

        # Sjekk om generatoren eksisterer
        self.check_pair_exists_or_abort(_from, _to)

        # Sørg for at dette er unicode
        self.lemma_match = user_input = lemma = decodeOrFail(lemma)

        return json_response(
            {
                'paradigms': self.get_paradigms(_from, lemma),
                'tagsets': self.tagsets_serializer_ready(_from),
                'input': {
                    'lemma': lemma,
                    'pos': request.args.get('pos', False)
                }
            },
            pretty=request.args.get('pretty', False)
        )

    def search_to_paradigm(self, lookup_value, **search_kwargs):
        search_result_obj = self.do_search_to_obj(
            lookup_value, generate=True, **search_kwargs)

        print(lineno(), search_result_obj)
        return [
            paradigm for _, _, paradigm, _ in search_result_obj.
            entries_and_tags_and_paradigms
        ]
