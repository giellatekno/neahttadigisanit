from . import blueprint

from .paradigms import ParadigmLanguagePairSearchView
from .search import (DetailedLanguagePairSearchView, IndexSearchPage,
                    LanguagePairSearchView, ReferredLanguagePairSearchView)
from .variant_search import LanguagePairSearchVariantView

from .autocomplete import autocomplete
from .locale import set_locale
from .main import (about, about_sources, config_doc, config_docs, escape_tv,
                   externalFormSearch, more_dictionaries,
                   session_clear)
from .reader import (bookmarklet, bookmarklet_configs, ie8_instrux, lookupWord,
                     reader_test_page, reader_update, reader_update_json)

try:
    from .lemmatizer import LemmatizerView
except:
    pass

blueprint.add_url_rule(
    '/',
    view_func=IndexSearchPage.as_view('index_search_page'),
    endpoint="canonical-root")

blueprint.add_url_rule(
    '/<_from>/<_to>/',
    view_func=LanguagePairSearchView.as_view('language_pair_search'),
    endpoint="canonical_root_search_pair")

blueprint.add_url_rule(
    '/<_from>/<_to>/ref/',
    view_func=ReferredLanguagePairSearchView.as_view(
        'referred_language_pair_search'),
    endpoint="search_pair_referred_search")

blueprint.add_url_rule(
    '/v/<_from>/<_to>/<variant_type>/',
    view_func=LanguagePairSearchVariantView.as_view(
        'language_pair_variant_search'),
    endpoint="language_pair_variant_search")

blueprint.add_url_rule(
    '/detail/<_from>/<_to>/<wordform>.<format>',
    view_func=DetailedLanguagePairSearchView.as_view(
        'detailed_language_pair_search'),
    endpoint="detailed_language_pair_search")

blueprint.add_url_rule(
    '/paradigm/<_from>/<_to>/<lemma>/',
    view_func=ParadigmLanguagePairSearchView.as_view('paradigm_generator'),
    endpoint="paradigm_language_pair")

if LemmatizerView:
    blueprint.add_url_rule(
        '/lemmas/<_from>/<wordform>/',
        view_func=LemmatizerView.as_view('lemmatizer'),
        endpoint="lemmatizer")

# TODO: commenting out until this feature comes back, prevent anything
# from breaking in other projects if this is unmaintained.
# blueprint.add_url_rule( '/list/keywords/<_from>/<_to>/'
#                       , view_func=search_keyword_list
#                       , methods=['GET']
#                       , endpoint="search_keyword_list"
#                       )


blueprint.add_url_rule(
    '/lookup/<from_language>/<to_language>/',
    view_func=lookupWord,
    methods=['OPTIONS', 'GET', 'POST'],
    endpoint="lookup")

blueprint.add_url_rule(
    '/read/ie8_instructions/', methods=['GET'], view_func=ie8_instrux)

blueprint.add_url_rule(
    '/read/test/', methods=['GET'], view_func=reader_test_page)

blueprint.add_url_rule(
    '/read/update/', methods=['GET'], view_func=reader_update)

blueprint.add_url_rule(
    '/read/update/json/', methods=['GET'], view_func=reader_update_json)

blueprint.add_url_rule(
    '/read/config/', methods=['GET'], view_func=bookmarklet_configs)

blueprint.add_url_rule(
    '/read/', methods=['GET'], endpoint='reader_info', view_func=bookmarklet)


blueprint.add_url_rule(
    '/session/clear/<sess_key>/',
    view_func=session_clear,
    methods=['GET'],
    endpoint="clear_session_key")

blueprint.add_url_rule(
    '/more/',
    methods=['GET'],
    view_func=more_dictionaries,
    endpoint="more_dictionaries")

blueprint.add_url_rule(
    '/extern/<_from>/<_to>/<_search_type>/',
    methods=['POST'],
    view_func=externalFormSearch,
    endpoint='external_form_search')

blueprint.add_url_rule(
    '/about/', methods=['GET'], endpoint='about', view_func=about)

blueprint.add_url_rule(
    '/about/sources/',
    methods=['GET'],
    endpoint='about_sources',
    view_func=about_sources)

blueprint.add_url_rule(
    '/escape/text-tv/',
    methods=['GET'],
    view_func=escape_tv,
    endpoint='escape_tv')

blueprint.add_url_rule(
    '/config_doc/',
    methods=['GET'],
    view_func=config_docs,
    endpoint="config_docs")

blueprint.add_url_rule(
    '/config_doc/<from_language>/',
    methods=['GET'],
    view_func=config_doc,
    endpoint="config_doc")


blueprint.add_url_rule(
    '/locale/<iso>/',
    methods=['GET'],
    view_func=set_locale,
    endpoint='set_locale')


blueprint.add_url_rule(
    '/autocomplete/<from_language>/<to_language>/',
    methods=['GET'],
    view_func=autocomplete,
    endpoint="autocomplete")

browse = False
try:
    from .browse import *
    browse = True
except ImportError:
    pass

if browse:
    blueprint.add_url_rule(
        '/browse/<_from>/<_to>/',
        view_func=BrowseView.as_view('word_browser'),
        endpoint='browse_pair')
