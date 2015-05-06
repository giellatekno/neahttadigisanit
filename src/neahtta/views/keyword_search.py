
from flask import ( current_app
                  , request
                  , session
                  , Response
                  , render_template
                  , abort
                  , redirect
                  , g
                  )

from flask.ext.babel import gettext as _

from i18n.utils import get_locale

from cache import cache

from .search import LanguagePairSearchView

from lexicon import FrontPageFormat

@cache.memoize()
def fetch_keywords(_f, _t, counts=False):
    from collections import Counter

    lex = current_app.config.lexicon.language_pairs.get((_f, _t))
    tree = lex.tree
    entries = lex.tree.findall('.//e/mg/tg/key')

    _ks = [k for k in [e.text for e in entries] if k]

    keys = list(set(_ks))

    if counts:
        counts = Counter(_ks)
        return keys, counts
    else:
        return keys

class LanguagePairSearchVariantView(LanguagePairSearchView):

    # TODO: cache on search args and session lang
    methods = ['GET', 'POST']
    template_name = 'variant_search.html'
    formatter = FrontPageFormat

    def get_shared_context(self, _from, _to):
        """ Return some things that are in all templates. Include the
        variant type in the search request. """
        _sup = super(LanguagePairSearchVariantView, self)
        shared_context = _sup.get_shared_context(_from, _to,
                                                 search_form_action=request.path,
                                                 search_variant_type=self.variant_type)
        shared_context['variant_type'] = self.variant_type
        shared_context['search_form_action'] = request.path

        from operator import itemgetter

        if request.method == 'GET':
            keys, key_counts = fetch_keywords(_from, _to, counts=True)
            # shared_context['initial_keywords'] = sorted(key_counts.iteritems(), key=itemgetter(1), reverse=True)

        # TODO: send additional keywords in the current search.
        return shared_context

    def post_search_context_modification(self, search_result, context):

        # TODO: remove keywords present in search
        def get_entry_keywords():
            _str_norm = 'string(normalize-space(%s))'
            search_result.entries
            keys = []

            existing_keywords = context['user_input'].split(',')

            for e in search_result.entries:
                keys.append(e.xpath(_str_norm % './mg/tg/key/text()'))

            return [a for a in list(set(keys)) if a not in existing_keywords]

        context['available_keywords'] = get_entry_keywords()

        return context

    def get(self, variant_type, _from, _to):
        """ The only difference here between the normal type of search
        is that there's an extra argument in the URL, to select the
        variant type. This is easy to extract, and once removed and
        included elsewhere in the search everything else is the same.
        """
        self.variant_type = variant_type
        # TODO: need more from parent get to retrieve result of search_to_context
        return super(LanguagePairSearchVariantView, self).get(_from, _to)

    def post(self, variant_type, _from, _to):
        """ The only difference here between the normal type of search
        is that there's an extra argument in the URL, to select the
        variant type. This is easy to extract, and once removed and
        included elsewhere in the search everything else is the same.
        """
        self.variant_type = variant_type

        # TODO: if there are way too many results with the query, user
        # must be invited to narrow them down by adding another keyword.
        # will need to have a quick function that just counts the
        # results for a given query without sending them off to be
        # rendered, so that things go faster.

        # missing current_pair_settings
        return super(LanguagePairSearchVariantView, self).post(_from, _to)

from .reader import crossdomain

@crossdomain(origin='*', headers=['Content-Type'])
def search_keyword_list(_from, _to):
    # TODO: this is lang specific too, but probably fine for the moment.
    # TODO: cache query for teh whole duration of the service running

    import simplejson

    if (_from, _to) not in current_app.config.dictionaries and \
       (_from, _to) not in current_app.config.variant_dictionaries:
        abort(404)

    data = simplejson.dumps({ 'keywords': fetch_keywords(_from, _to) })

    return Response( response=data
                   , status=200
                   , mimetype="application/json"
                   )
