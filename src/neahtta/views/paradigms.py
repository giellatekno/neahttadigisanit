from . import blueprint

__all__ = [
    'ParadigmLanguagePairSearchView',
]

from flask import ( request
                  , current_app
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


class ParadigmLanguagePairSearchView(DictionaryView, SearcherMixin):

    from lexicon import DetailedFormat as formatter

    def options(self, _from, _to, lemma):
        _tagsets = current_app.config.morphologies.get(g._from).tagsets.sets

        tagsets_serializer_ready = {}

        # TODO: user-friendly converted tagsets might result in
        # comparison errors, so analyses need to be userfriendly and
        # normal
        for key, ts in _tagsets.iteritems():
            tagsets_serializer_ready[key] = ts.members

        return json_response({
            'tagsets': tagsets_serializer_ready,
        })

    def get(self, _from, _to, lemma):

        # Check for cache entry here

        self.check_pair_exists_or_abort(_from, _to)

        user_input = lemma = decodeOrFail(lemma)

        # Generation constraints
        pos_filter = request.args.get('pos', False)
        e_node = request.args.get('e_node', False)
        # This is the same
        self.lemma_match = user_input

        _split = True
        _non_c = True
        _non_d = False

        search_kwargs = {
            'split_compounds': _split,
            'non_compounds_only': _non_c,
            'no_derivations': _non_d,
        }

        has_analyses = False
        cache_key = '+'.join([a for a in [
            _from,
            lemma,
            pos_filter,
            e_node,
        ] if a])

        paradigms = current_app.cache.get(cache_key.encode('utf-8'))

        if paradigms is None:
            paradigms = \
                self.search_to_paradigm(user_input,
                                        detailed=True,
                                        **search_kwargs)

            current_app.cache.set(cache_key.encode('utf-8'), paradigms, timeout=None)

        from morphology.utils import tagfilter

        ui_locale = get_locale()

        def filter_tag((_input, tag, forms)):
            filtered_tag = tagfilter(tag, g._from, g._to).split(' ')
            return (_input, filtered_tag, forms, tag)

        paradigms = [map(filter_tag, _p) for _p in paradigms]

        # TODO: cache search result here
        # current_app.cache.set(entry_cache_key,
        # search_result_context.detailed_entry_pickleable)

        # search_result_context.update(**self.get_shared_context(_from, _to))

        _tagsets = current_app.config.morphologies.get(g._from).tagsets.sets

        tagsets_serializer_ready = {}

        # TODO: user-friendly converted tagsets might result in
        # comparison errors, so analyses need to be userfriendly and
        # normal
        for key, ts in _tagsets.iteritems():
            tagsets_serializer_ready[key] = ts.members

        return json_response({
            'paradigms': paradigms,
            'tagsets': tagsets_serializer_ready,
            'input': {
                'lemma': lemma,
                'pos': pos_filter,
            }
        })


    def search_to_paradigm(self, lookup_value, **search_kwargs):

        errors = []

        search_result_obj = self.do_search_to_obj(lookup_value, generate=True, **search_kwargs)

        paradigms = []

        for a in search_result_obj.formatted_results:
            paradigms.append(a.get('paradigm'))

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
