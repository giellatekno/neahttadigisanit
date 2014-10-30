from . import blueprint

from search import ( IndexSearchPage
                   , LanguagePairSearchView
                   , DetailedLanguagePairSearchView
                   , ParadigmLanguagePairSearchView
                   , ReferredLanguagePairSearchView
                   )

blueprint.add_url_rule( '/'
                      , view_func=IndexSearchPage.as_view('index_search_page')
                      , endpoint="canonical-root"
                      )

blueprint.add_url_rule( '/<_from>/<_to>/'
                      , view_func=LanguagePairSearchView.as_view('language_pair_search')
                      )

blueprint.add_url_rule( '/<_from>/<_to>/ref/'
                      , view_func=ReferredLanguagePairSearchView.as_view('referred_language_pair_search')
                      )

blueprint.add_url_rule( '/detail/<_from>/<_to>/<wordform>.<format>'
                      , view_func=DetailedLanguagePairSearchView.as_view('detailed_language_pair_search')
                      )

blueprint.add_url_rule( '/paradigm/<_from>/<_to>/<lemma>'
                      , view_func=ParadigmLanguagePairSearchView.as_view('paradigm_generator')
                      )
