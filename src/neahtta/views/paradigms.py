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
from . import blueprint
import inspect

from morphology.utils import tagfilter
from flask import ( request
                  , current_app
                  , json
                  , session
                  , Response
                  , render_template
                  , abort
                  , redirect
                  , g
                  )

from .search import DictionaryView, SearcherMixin
from .reader import json_response
from utils.encoding import decodeOrFail

from i18n.utils import get_locale

__all__ = [
    'ParadigmLanguagePairSearchView',
]


def lineno():
    """Return the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno


def json_response_pretty(data, *args, **kwargs):
    data = json.dumps( data
                     , sort_keys=True
                     , indent=4
                     , separators=(',', ': ')
                     )

    return Response( response=data
                   , status=200
                   , mimetype="application/json"
                   )


class ParadigmLanguagePairSearchView(DictionaryView, SearcherMixin):

    from lexicon import DetailedFormat as formatter

    def options(self, _from, _to, lemma):
        _filters = current_app.config.tag_filters.get((g._from, g._to), False)
        _tagsets = current_app.config.morphologies.get(g._from).tagsets.sets

        tagsets_serializer_ready = {}

        for key, ts in _tagsets.iteritems():
            tagsets_serializer_ready[key] = ts.members

        return json_response({
            'tagsets': tagsets_serializer_ready,
            'filters': _filters
        })

    @staticmethod
    def get_tagsets():
        _tagsets = current_app.config.morphologies.get(g._from).tagsets.sets

        return {
            key: [m.val for m in ts.members]
            for key, ts in _tagsets.iteritems()
        }

    def get_paradigms(self, _from, lemma):
        def filter_tag(f):
            print(lineno(), f.tag)
            filtered_tag = tagfilter(f.tag, g._from, g._to).split(' ')
            print(lineno(), f.input, filtered_tag, [f.form], f.tag.tag_string)
            return (f.input, filtered_tag, [f.form], f.tag.tag_string)

        # Generation constraints
        # Sjekk om ordklasse er satt
        pos_filter = request.args.get('pos', False)

        # Sjekk om e_node er satt
        e_node = request.args.get('e_node', False)

        # Sjekk om paradigmene er mellomlagret
        cache_key = '+'.join([a for a in [
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

        return [map(filter_tag, paradigm) for paradigm in paradigms]


    def get(self, _from, _to, lemma):
        # TODO: submit and process on separate thread, optional poll
        # argument to not submit and just check for result

        # Sjekk om generatoren eksisterer
        self.check_pair_exists_or_abort(_from, _to)

        # Sørg for at dette er unicode
        self.lemma_match = user_input = lemma = decodeOrFail(lemma)

        # Sjekk om pretty er blant argumentene
        pretty = request.args.get('pretty', False)

        if pretty:
            resp_fx = json_response_pretty
        else:
            resp_fx = json_response

        return resp_fx({
            'paradigms': self.get_paradigms(_from, lemma),
            'tagsets': self.get_tagsets(),
            'input': {
                'lemma': lemma,
                'pos': request.args.get('pos', False),
            }
        })

    def search_to_paradigm(self, lookup_value, **search_kwargs):

        errors = []

        search_result_obj = self.do_search_to_obj(lookup_value, generate=True, **search_kwargs)

        paradigms = []

        for entry, tag, paradigm, layouts in search_result_obj.entries_and_tags_and_paradigms:
            paradigms.append(paradigm)

        return paradigms

    def entry_filterer(self, entries, **kwargs):
        """ Runs on formatted result from DetailedFormat thing

            TODO: will need to reconstruct this for new style views
            because the formatters are going away
        """

        # Post-analysis filter arguments
        pos_filter = request.args.get('pos', False)
        e_node = request.args.get('e_node', False)
        lemma_match = self.lemma_match

        def _byPOS(r):
            if r.get('input')[1].upper() == pos_filter.upper():
                return True
            else:
                return False

        def _byLemma(r):
            if r.get('input')[0] == lemma_match:
                return True
            else:
                return False

        def _byNodeHash(r):
            node = r.get('entry_hash')
            if node == e_node:
                return True
            else:
                return False

        def default_result(r):
            return r

        entry_filters = [default_result]

        if lemma_match:
            entry_filters.append(_byLemma)

        if e_node:
            entry_filters.append(_byNodeHash)

        if pos_filter:
            entry_filters.append(_byPOS)

        def filter_entries_for_view(entries):
            _entries = []
            for f in entry_filters:
                _entries = filter(f, entries)
            return _entries

        return filter_entries_for_view(entries)
