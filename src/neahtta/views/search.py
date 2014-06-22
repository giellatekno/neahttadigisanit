from . import blueprint
from flask import current_app

import sys

import simplejson

from logging import getLogger

from utils.logger import *
from utils.data import *
from i18n.utils import iso_filter
from utils.encoding import *

from .helpers import resolve_original_pair

from flask import ( request
                  , session
                  , Response
                  , render_template
                  , abort
                  , redirect
                  )

from operator import itemgetter

user_log = getLogger("user_log")

@blueprint.route('/detail/<from_language>/<to_language>/<wordform>.<format>',
           methods=['GET'], endpoint="detail")
def wordDetail(from_language, to_language, wordform, format):
    """
    .. http:get::
              /detail/(string:from)/(string:to)/(string:wordform).(string:fmt)

        Look up up a query in the lexicon (including lemmatizing input,
        and the lexicon against the input sans lemmatization), returning
        translation information, word analyses, and sample paradigms for
        words and tags which support it.

        :samp:`/detail/sme/nob/orrut.html`
        :samp:`/detail/sme/nob/orrut.json`

        There are additional GET form parameters to control the sorting
        and display of the output.

        :param from: the source language
        :param to: the target language
        :param wordform:
            the wordform to be analyzed. If in doubt, encode and escape
            the string into UTF-8, and URL encode it. Some browser do
            this automatically and present the URL in a user-readable
            format, but mostly, the app does not seem to care.
        :param fmt:
            the data format to return the result in. `json` and `html`
            are currently accepted.

        :form pos_filter:
            Filter the analyzed forms so that only forms with a PoS
            matching `pos_filter` are displayed.
        :type pos_filter: str
        :form lemma_match:
            Filter the results so that the lemma in the input must match
            the lemma in the analyzed form.
        :type lemma_match: bool
        :form no_compounds:
            Whether or not to analyze compounds.
            True or False.
        :type no_compounds: bool
        :form e_node:
            This value is only used if the user arrives at this page via
            a link on the front pageg results, `e_node` is a unique
            identifier for the XML document.

        :throws Http404:
            In the event that the language pair or format does not exist.

        :returns:
            Data is looked up and formatted using
            :py:class:`lexicon.formatters.DetailedFormat`, and returned
            in `html` using the template `word_detail.html`

    """
    from lexicon import DetailedFormat

    import simplejson as json

    user_input = wordform
    if not format in ['json', 'html']:
        return _("Invalid format. Only json and html allowed.")

    wordform = decodeOrFail(wordform)

    # NOTE: these options are mostly for detail views that are linked to
    # from the initial page's search. Everything should work without
    # them, and with all or some of them.

    # Do we filter analyzed forms and lookups by pos?
    pos_filter = request.args.get('pos_filter', False)
    # Should we match the input lemma with the analyzed lemma?
    lemma_match = request.args.get('lemma_match', False)
    # From the front page-- match the hash of the lxml element
    e_node = request.args.get('e_node', False)

    def pickleable_result(_results):
        pickleable = []
        for j in _results:
            _j = j.copy()
            _j.pop('node')
            analyses = []
            for a in _j.get('analyses', []):
                # TODO: tag formatter
                analyses.append((a.lemma, a.tag.tag_string))
            _j['analyses'] = analyses
            pickleable.append(_j)
        return pickleable

    def _byPOS(r):
        if r.get('input')[1].upper() == pos_filter.upper():
            return True
        else:
            return False

    def _byLemma(r):
        if r.get('input')[0] == wordform:
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

    if e_node:
        entry_filters.append(_byNodeHash)

    if pos_filter:
        entry_filters.append(_byPOS)

    if lemma_match:
        entry_filters.append(_byLemma)

    def filter_entries_for_view(entries):
        _entries = []
        for f in entry_filters:
            _entries = filter(f, entries)
        return _entries

    has_analyses = False

    # Do we want to analyze compounds?
    no_compounds = request.args.get('no_compounds', False)

    ui_lang = iso_filter(session.get('locale', to_language))
    # Cache key by URL
    entry_cache_key = u'%s?%s?%s' % (request.path, request.query_string, ui_lang)

    if no_compounds or lemma_match or e_node:
        want_more_detail = True
    else:
        want_more_detail = False

    def unsupportedLang(more='.'):
        if format == 'json':
            _err = " * Detailed view not supported for this language pair"
            return json.dumps(_err + " " + more)
        elif format == 'html':
            abort(404)

    if current_app.caching_enabled:
        cached_result = current_app.cache.get(entry_cache_key)
    else:
        cached_result = None

    if cached_result is None or current_app.config.new_style_templates:

        # Use the original language pair if the user has selected a
        # variant

        if (from_language, to_language) not in current_app.config.dictionaries and \
           (from_language, to_language)     in current_app.config.variant_dictionaries:
            var = current_app.config.variant_dictionaries.get((from_language, to_language))
            (from_language, to_language) = var.get('orig_pair')

        if (from_language, to_language) not in current_app.config.dictionaries:
            return unsupportedLang()

        # Generation paradigms, and generation options
        lang_paradigms = current_app.config.paradigms.get(from_language, {})

        morph = current_app.config.morphologies.get(from_language, False)

        if no_compounds:
            _split = True
            _non_c = True
            _non_d = False
        else:
            _split = True
            _non_c = False
            _non_d = False

        mlex = current_app.morpholexicon
        entries_and_tags = mlex.lookup( wordform
                                      , source_lang=from_language
                                      , target_lang=to_language
                                      , split_compounds=_split
                                      , non_compounds_only=_non_c
                                      , no_derivations=_non_d
                                      )

        analyses = sum(map(itemgetter(1), entries_and_tags), [])

        fmtkwargs = { 'target_lang': to_language
                    , 'source_lang': from_language
                    , 'ui_lang': iso_filter(session.get('locale', to_language))
                    , 'user_input': wordform
                    }

        # [(lemma, XMLNodes)] -> [(lemma, generator(AlmostJSON))]
        formatted_results = []
        analyses_without_lex = []
        for result, morph_analyses in entries_and_tags:
            if result is not None:
                word_template_kwargs = {
                    'analyses': morph_analyses
                }

                _formatted = list(DetailedFormat(
                    [result],
                    additional_template_kwargs=word_template_kwargs,
                    **fmtkwargs
                ))

                _formatted_with_paradigms = []

                for r in filter_entries_for_view(_formatted):
                    lemma, pos, tag, _type = r.get('input')
                    node = r.get('node')

                    paradigm_from_file = mlex.paradigms.get_paradigm(
                        from_language, node, morph_analyses
                    )
                    if paradigm_from_file:
                        form_tags = [_t.split('+')[1::] for _t in paradigm_from_file.splitlines()]
                        _generated = morph.generate(lemma, form_tags, node)
                    else:
                        # For pregenerated things
                        _generated = morph.generate(lemma, [], node)

                    r['paradigm'] = _generated
                    _formatted_with_paradigms.append(r)
                formatted_results.extend(_formatted_with_paradigms)
            else:
                analyses_without_lex.extend(morph_analyses)

        analyses = [(l.lemma, l.pos, l.tag) for l in analyses]

        detailed_result = formatted_results
        pickle_result = sorted( pickleable_result(formatted_results)
                              , key=lambda x: x.get('lemma')
                              )
        json_result = pickle_result

        current_app.cache.set(entry_cache_key, pickle_result)
    else:
        # TODO: _from may be wrong in case of SoMe
        cur_morph = current_app.config.morphologies.get(from_language)
        def depickle_result(_results):
            pickleable = []
            for j in _results:
                _j = j.copy()
                analyses = []
                for (lemma, tag) in _j.get('analyses', []):
                    # TODO: tag formatter
                    _lem = cur_morph.de_pickle_lemma(lemma, tag)
                    analyses.append(_lem)
                _j['analyses'] = analyses
                pickleable.append(_j)
            return pickleable

        json_result = cached_result
        detailed_result = depickle_result(cached_result)

    # Logging
    # This ugly bit is just for compiling the use log entry
    if len(detailed_result) > 0:
        success = True
        result_lemmas = []
        tx_set = []
        for d in detailed_result:
            tx_set.append(', '.join([t.get('tx') for t in d.get('right', []) if t.get('tx', False)]))
            result_lemmas.append(d.get('input')[0])
        tx_set = '; '.join(tx_set)
    else:
        success = False
        result_lemmas = ['-']
        tx_set = '-'

    user_log.info('%s\t%s\t%s\t%s\t%s\t%s' % ( user_input
                                             , str(success)
                                             , ', '.join(result_lemmas)
                                             , tx_set
                                             , from_language
                                             , to_language
                                             )
                 )

    # Format
    if format == 'json':
        result = simplejson.dumps({
            "success": True,
            "result": json_result
        })
        return Response( response=result
                       , status=200
                       , mimetype="application/json"
                       )

    elif format == 'html':

        for result in detailed_result:
            if result.get('analyses'):
                if len(result.get('analyses')) > 0:
                    has_analyses = True

        pair_settings = current_app.config.pair_definitions[(from_language, to_language)]

        if current_app.config.new_style_templates and user_input:
            _rendered_entries = []
            analyses_without_entry = []
            def sort_entry(r):
                if r[0] is None:
                    return False
                if not r[0]:
                    return False
                try:
                    return ''.join(r[0].xpath('./lg/l/text()'))
                except:
                    return False

            _str_norm = 'string(normalize-space(%s))'
            rendered_analyses_without_entry = False
            for lz, az in sorted(entries_and_tags, key=sort_entry):
                # TODO: generate

                if lz is None:
                    analyses_without_entry.extend(az)
                    continue

                can_generate = True
                paradigm = []

                lemma = lz.xpath(_str_norm % './lg/l/text()')

                # TODO: pregenerated lexicon forms?
                paradigm_from_file = mlex.paradigms.get_paradigm(
                    from_language, lz, az
                )

                if paradigm_from_file:
                    form_tags = [_t.split('+')[1::] for _t in paradigm_from_file.splitlines()]
                    paradigm = morph.generate_to_objs(lemma, form_tags, node)

                tplkwargs = { 'lexicon_entry': lz
                            , 'analyses': az
                            , 'paradigm': paradigm

                            , '_from': from_language
                            , '_to': to_language
                            , 'user_input': user_input
                            # , 'errors': errors
                            , 'dictionaries_available': current_app.config.pair_definitions
                            , 'current_pair_settings': pair_settings
                            }

                _rendered_entries.append(
                    current_app.lexicon_templates.render_template(from_language, 'detail_entry.template', **tplkwargs)
                )

                # TODO:
                # rendered_analyses_without_entry = current_app.lexicon_templates.render_template(
                #     from_language, 
                #     'analyses.template', 
                #     analyses=analyses_without_entry,
                #     lexicon_entry=None,
                #     _from=from_language,
                #     _to=to_language,
                #     user_input=user_input,
                #     dictionaries_available=current_app.config.pair_definitions,
                #     current_pair_settings=pair_settings,
                # )


            return render_template( 'word_detail_new_style.html'
                                  , result=detailed_result
                                  , user_input=user_input
                                  , _from=from_language
                                  , _to=to_language
                                  , more_detail_link=want_more_detail
                                  , zip=zipNoTruncate
                                  , has_analyses=has_analyses
                                  , current_pair_settings=pair_settings
                                  , new_templates=_rendered_entries
                                  , analyses_without_entry=rendered_analyses_without_entry
                                  )

        return render_template( 'word_detail.html'
                              , result=detailed_result
                              , user_input=user_input
                              , _from=from_language
                              , _to=to_language
                              , more_detail_link=want_more_detail
                              , zip=zipNoTruncate
                              , has_analyses=has_analyses
                              , current_pair_settings=pair_settings
                              )

# For direct links, form submission.
### @blueprint.route('/<_from>/<_to>/', methods=['GET', 'POST'])
### def indexWithLangs(_from, _to):
###     from lexicon import FrontPageFormat
### 
###     # mobile test for most common browsers
###     mobile = False
###     if request.user_agent.platform in ['iphone', 'android']:
###         mobile = True
### 
###     iphone = False
###     if request.user_agent.platform == 'iphone':
###         iphone = True
### 
###     analyses_without_lex = []
###     mlex = current_app.morpholexicon
### 
###     user_input = lookup_val = request.form.get('lookup', False)
### 
###     if (_from, _to) not in current_app.config.dictionaries and \
###        (_from, _to) not in current_app.config.variant_dictionaries:
###         abort(404)
### 
###     swap_from, swap_to = (_to, _from)
### 
###     successful_entry_exists = False
###     errors = []
### 
###     results = False
###     analyses = False
### 
###     if request.method == 'POST' and lookup_val:
### 
###         mlex = current_app.morpholexicon
### 
###         entries_and_tags = mlex.lookup( lookup_val
###                                       , source_lang=_from
###                                       , target_lang=_to
###                                       , split_compounds=True
###                                       )
### 
###         analyses = sum(map(itemgetter(1), entries_and_tags), [])
### 
###         # Keep these around for the mobile analyses box
###         analyses = [ (lem.input, lem.lemma, list(lem.tag))
###                      for lem in analyses
###                    ]
### 
###         fmtkwargs = { 'target_lang': _to
###                     , 'source_lang': _from
###                     , 'ui_lang': iso_filter(session.get('locale', _to))
###                     , 'user_input': lookup_val
###                     }
### 
###         # [(lemma, XMLNodes)] -> [(lemma, generator(AlmostJSON))]
###         formatted_results = []
###         analyses_without_lex = []
###         for result, morph_analyses in entries_and_tags:
###             if result is not None:
###                 formatted_results.extend(FrontPageFormat(
###                     [result],
###                     additional_template_kwargs={'analyses': morph_analyses},
###                     **fmtkwargs
###                 ))
###             else:
###                 analyses_without_lex.extend(morph_analyses)
### 
###         # When to display unknowns
###         successful_entry_exists = False
###         if len(formatted_results) > 0:
###             successful_entry_exists = True
### 
###         def sort_entry(r):
###             return r.get('left')
### 
###         results = sorted( formatted_results
###                         , key=sort_entry
###                         )
### 
###         results = [ {'input': lookup_val, 'lookups': results} ]
### 
###         logIndexLookups(user_input, results, _from, _to)
### 
###         show_info = False
###     else:
###         user_input = ''
###         show_info = True
### 
###     if len(errors) == 0:
###         errors = False
### 
###     # context needs: has_mobile_variant, has_variant,
###     # variant_dictionaries, orig_pair, is_variant, pair_settings
###     pair_settings, pair_opts = resolve_original_pair(current_app.config, _from, _to)
### 
###     if current_app.config.new_style_templates and lookup_val:
###         _rendered_entries = []
###         def sort_entry(r):
###             if r[0] is None:
###                 return False
###             if len(r[0]) > 0:
###                 return False
###             try:
###                 return ''.join(r[0].xpath('./lg/l/text()'))
###             except:
###                 return False
### 
###         for lz, az in sorted(entries_and_tags, key=sort_entry):
###             if lz is not None:
###                 tplkwargs = { 'lexicon_entry': lz
###                             , 'analyses': az
### 
###                             , '_from': _from
###                             , '_to': _to
###                             , 'user_input': lookup_val
###                             , 'word_searches': results
###                             , 'errors': errors
###                             , 'show_info': show_info
###                             , 'zip': zipNoTruncate
###                             , 'dictionaries_available': current_app.config.pair_definitions
###                             , 'successful_entry_exists': successful_entry_exists
###                             , 'current_pair_settings': pair_settings
###                             }
###                 _rendered_entries.append(
###                     current_app.lexicon_templates.render_template(_from, 'entry.template', **tplkwargs)
###                 )
### 
###         all_az = sum([az for _, az in sorted(entries_and_tags, key=sort_entry)], [])
###         all_analysis_template = current_app.lexicon_templates.render_individual_template( _from
###                                                                                         , 'analyses.template'
###                                                                                         , analyses=all_az
###                                                                                         , current_pair_settings=pair_settings
###                                                                                         )
###         if analyses_without_lex:
###             leftover_analyses_template = current_app.lexicon_templates.render_individual_template( _from
###                                                                                                  , 'analyses.template'
###                                                                                                  , analyses=analyses_without_lex
###                                                                                                  , current_pair_settings=pair_settings
###                                                                                                  )
###         else:
###             leftover_analyses_template = False
### 
###         return render_template( 'index_new_style.html'
###                               , _from=_from
###                               , _to=_to
###                               , user_input=lookup_val
###                               , word_searches=results
###                               , analyses=analyses
###                               , analyses_without_lex=analyses_without_lex
###                               , leftover_analyses_template=leftover_analyses_template
###                               , all_analysis_template=all_analysis_template
###                               , errors=errors
###                               , show_info=show_info
###                               , zip=zipNoTruncate
###                               , successful_entry_exists=successful_entry_exists
###                               , current_pair_settings=pair_settings
###                               , new_templates=_rendered_entries
###                               , **pair_opts
###                               )
###     # TODO: include form analysis of user input #formanalysis
###     _r_from, _r_to = pair_opts.get('swap_from'), pair_opts.get('swap_to')
###     reverse_exists = current_app.config.dictionaries.get((_r_from, _r_to), False)
###     return render_template( 'index.html'
###                           , _from=_from
###                           , _to=_to
###                           , display_swap=reverse_exists
###                           , user_input=lookup_val
###                           , word_searches=results
###                           , analyses=analyses
###                           , analyses_without_lex=analyses_without_lex
###                           , errors=errors
###                           , show_info=show_info
###                           , zip=zipNoTruncate
###                           , successful_entry_exists=successful_entry_exists
###                           , current_pair_settings=pair_settings
###                           , **pair_opts
###                           )

accepted_lemma_args = {
    'l_til_ref': 'til_ref',
}

# For direct links, form submission.
@blueprint.route('/<_from>/<_to>/ref/', methods=['GET'])
def indexWithLangsToReference(_from, _to):
    from lexicon import FrontPageFormat

    analyses_without_lex = []
    mlex = current_app.morpholexicon

    user_input = lookup_val = request.form.get('lookup', False)

    if (_from, _to) not in current_app.config.dictionaries:
        abort(404)

    successful_entry_exists = False
    errors = []

    results = False
    analyses = False

    lemma_lookup_args = {}
    for k, v in request.args.iteritems():
        if k in accepted_lemma_args:
            lemma_lookup_args[accepted_lemma_args.get(k)] = v

    if lemma_lookup_args:

        mlex = current_app.morpholexicon

        entries_and_tags = mlex.lookup( ''
                                      , source_lang=_from
                                      , target_lang=_to
                                      , split_compounds=True
                                      , lemma_attrs=lemma_lookup_args
                                      )

        analyses = sum(map(itemgetter(1), entries_and_tags), [])

        # Keep these around for the mobile analyses box
        analyses = [ (lem.input, lem.lemma, list(lem.tag))
                     for lem in analyses
                   ]

        fmtkwargs = { 'target_lang': _to
                    , 'source_lang': _from
                    , 'ui_lang': iso_filter(session.get('locale', _to))
                    , 'user_input': lookup_val
                    }

        if lemma_lookup_args:
            fmtkwargs['lemma_attrs'] = lemma_lookup_args

        # [(lemma, XMLNodes)] -> [(lemma, generator(AlmostJSON))]
        formatted_results = []
        analyses_without_lex = []
        for result, morph_analyses in entries_and_tags:
            if result is not None:
                formatted_results.extend(FrontPageFormat(
                    [result],
                    additional_template_kwargs={'analyses': morph_analyses},
                    **fmtkwargs
                ))
            else:
                analyses_without_lex.extend(morph_analyses)

        # When to display unknowns
        successful_entry_exists = False
        if len(formatted_results) > 0:
            successful_entry_exists = True

        def sort_entry(r):
            return r.get('left')

        results = sorted( formatted_results
                        , key=sort_entry
                        )

        results = [ {'input': lookup_val, 'lookups': results} ]

        show_info = False
    else:
        user_input = ''
        show_info = True

    if len(errors) == 0:
        errors = False

    pair_settings = current_app.config.pair_definitions[(_from, _to)]
    # TODO: include form analysis of user input #formanalysis
    if current_app.config.new_style_templates:
        _rendered_entries = []
        for lexicon, analyses in entries_and_tags:
            if lexicon is not None:
                tplkwargs = { 'lexicon_entry': lexicon
                            , 'analyses': analyses

                            , '_from': _from
                            , '_to': _to
                            , 'user_input': lookup_val
                            , 'word_searches': results
                            , 'analyses': analyses
                            , 'analyses_without_lex': analyses_without_lex
                            , 'errors': errors
                            , 'successful_entry_exists': successful_entry_exists
                            , 'dictionaries_available': current_app.config.pair_definitions
                            , 'current_pair_settings': pair_settings
                            , 'entries_and_tags': entries_and_tags
                            }
                _rendered_entries.append(
                    current_app.lexicon_templates.render_template( _from
                                                                 , 'entry.template'
                                                                 , **tplkwargs
                                                                 )
                )

        all_analysis_template = current_app.lexicon_templates.render_template( _from
                                                                             , 'analyses.template'
                                                                             , analyses=analyses
                                                                             )

        reverse_exists = current_app.config.dictionaries.get((_from, _to), False)

        return render_template( 'index_new_style.html'
                              , _from=_from
                              , _to=_to
                              , swap_from=_to
                              , swap_to=_from
                              , display_swap=reverse_exists
                              , user_input=lookup_val
                              , word_searches=results
                              , analyses=analyses
                              , all_analysis_template=all_analysis_template
                              , analyses_without_lex=analyses_without_lex
                              , errors=errors
                              , show_info=show_info
                              , zip=zipNoTruncate
                              , successful_entry_exists=successful_entry_exists
                              , current_pair_settings=pair_settings
                              , entries_and_tags=entries_and_tags
                              , new_templates=_rendered_entries
                              )
    else:
        reverse_exists = current_app.config.dictionaries.get((swap_to, swap_from), False)
        return render_template( 'index.html'
                              , _from=_from
                              , _to=_to
                              , swap_from=_to
                              , swap_to=_from
                              , display_swap=reverse_exists
                              , user_input=lookup_val
                              , word_searches=results
                              , analyses=analyses
                              , analyses_without_lex=analyses_without_lex
                              , errors=errors
                              , show_info=show_info
                              , zip=zipNoTruncate
                              , successful_entry_exists=successful_entry_exists
                              , current_pair_settings=pair_settings
                              )

## @blueprint.route('/', methods=['GET'], endpoint="canonical-root")
## def index():
## 
##     default_from, default_to = current_app.config.default_language_pair
##     mobile_redir = current_app.config.mobile_redirect_pair
##     pair_settings = current_app.config.pair_definitions[(default_from, default_to)]
## 
##     iphone = False
##     if request.user_agent.platform == 'iphone':
##         iphone = True
## 
##     mobile = False
##     if mobile_redir:
##         target_url = '/%s/%s/' % tuple(mobile_redir)
##         if request.user_agent.platform in ['iphone', 'android']:
##             mobile = True
##             # Only redirect if the user isn't coming back to the home page
##             # from somewhere within the app.
##             if request.referrer and request.host:
##                 if not request.host in request.referrer:
##                     return redirect(target_url)
##             else:
##                 return redirect(target_url)
## 
##     reverse_exists = current_app.config.dictionaries.get((default_to, default_from), False)
##     return render_template( 'index.html'
##                           , current_pair_settings=pair_settings
##                           , _from=default_from
##                           , _to=default_to
##                           , display_swap=reverse_exists
##                           , swap_from=default_to
##                           , swap_to=default_from
##                           , show_info=True
##                           )


# TODO: this is a big todo, but, slowly refactor everything into mixins
# and class-based views. So far the view functions here are really
# complex as a result of being hacked together, but they need to be
# chopped down into testable and easily comprehensible parts.

from flask.views import View, MethodView

class AppViewSettingsMixin(object):

    def __init__(self, *args, **kwargs):

        # Apply some default values for the present application

        self.default_from, self.default_to = current_app.config.default_language_pair
        self.default_pair_settings = current_app.config.pair_definitions[( self.default_from
                                                                         , self.default_to
                                                                         )]

        super(AppViewSettingsMixin, self).__init__(*args, **kwargs)


class IndexSearchPage(View, AppViewSettingsMixin):
    """ A simple view to handle potential mobile redirects to a default
    language pair specified only for mobile.
    """

    template_name = 'index.html'

    def maybe_do_mobile_redirect(self):
        """ If this is a mobile platform, redirect; otherwise return
        None/do no action.
        """

        iphone = False

        if request.user_agent.platform == 'iphone':
            iphone = True

        mobile = False

        mobile_redirect_pair = current_app.config.mobile_redirect_pair

        if mobile_redirect_pair:
            target_url = '/%s/%s/' % tuple(mobile_redirect_pair)
            if request.user_agent.platform in ['iphone', 'android']:
                mobile = True
                # Only redirect if the user isn't coming back to the home page
                # from somewhere within the app.
                if request.referrer and request.host:
                    if not request.host in request.referrer:
                        return redirect(target_url)
                else:
                    return redirect(target_url)

        return False

    def dispatch_request(self):

        self.maybe_do_mobile_redirect()

        reverse_exists = \
            current_app.config.dictionaries.get( ( self.default_to
                                                 , self.default_from
                                                 )
                                               , False
                                               )

        template_context = {
            'current_pair_settings': self.default_pair_settings,
            '_from': self.default_from,
            '_to': self.default_to,
            'display_swap': reverse_exists,
            'swap_from': self.default_to,
            'swap_to': self.default_from,
            'show_info': True,
        }

        return render_template(self.template_name, **template_context)


class SearchResult(object):
    """ This object is the lexicon lookup search result. It mostly
    provides readability conveniences.

        self.entries_and_tags
        self.analyses
        self.analyses_without_lex
        self.formatted_results
        self.successful_entry_exists

    """

    def __init__(self, _from, _to, user_input, entries_and_tags, formatter):
        self.user_input = user_input
        self.search_term = user_input
        self.entries_and_tags = entries_and_tags
        # When to display unknowns
        self.successful_entry_exists = False

        analyses = sum(map(itemgetter(1), entries_and_tags), [])
        analyses = [ (lem.input, lem.lemma, list(lem.tag))
                     for lem in analyses
                   ]

        self.analyses = analyses

        analyses_without_lex = []
        formatted_results = []

        fmtkwargs = { 'target_lang': _to
                    , 'source_lang': _from
                    , 'ui_lang': iso_filter(session.get('locale', _to))
                    , 'user_input': user_input
                    }

        # Formatting of this stuff should be moved somewhere more
        # reasonable.
        for result, morph_analyses in entries_and_tags:
            if result is not None:
                formatted_results.extend(formatter(
                    [result],
                    additional_template_kwargs={'analyses': morph_analyses},
                    **fmtkwargs
                ))
            else:
                analyses_without_lex.extend(morph_analyses)

        self.formatted_results = formatted_results
        self.analyses_without_lex = analyses_without_lex

        if len(self.formatted_results) > 0:
            self.successful_entry_exists = True



from lexicon import FrontPageFormat

class SearcherMixin(object):
    """ This mixin provides common methods for performing the search, 
    and returning view-ready results.
    """

    def do_search_to_obj(self, _from, _to, lookup_value):

        successful_entry_exists = False

        mlex = current_app.morpholexicon

        entries_and_tags = mlex.lookup( lookup_value
                                      , source_lang=_from
                                      , target_lang=_to
                                      , split_compounds=True
                                      )

        search_result_obj = SearchResult(_from, _to, lookup_value,
                                         entries_and_tags,
                                         self.formatter)

        return search_result_obj

    def search_to_context(self, _from, _to, lookup_value):
        # TODO: There's a big mess contained here, and part of it
        # relates to lexicon formatters. Slowly working on unravelling
        # it.

        from .helpers import resolve_original_pair

        errors = []

        search_result_obj = self.do_search_to_obj(_from, _to, lookup_value)

        def sort_entry(r):
            return r.get('left')

        sorted_results = sorted( search_result_obj.formatted_results
                        , key=sort_entry
                        )

        template_results = [ {'input': lookup_value, 'lookups': sorted_results} ]

        logIndexLookups(lookup_value, template_results, _from, _to)

        show_info = False

        if len(errors) == 0:
            errors = False

        search_context = {
            '_from': _from,
            '_to': _to,


            # These variables can be turned into something more general
            'successful_entry_exists': search_result_obj.successful_entry_exists,

            'word_searches': template_results,
            'analyses': search_result_obj.analyses,
            'analyses_without_lex': search_result_obj.analyses_without_lex,
            'user_input': search_result_obj.search_term,

            # ?
            'errors': errors, # is this actually getting set?
            'show_info': show_info,
        }

        return search_context

    def search_to_newstyle_context(self, _from, _to, lookup_value, **default_context_kwargs):
        """ This needs a big redo.
        """

        search_result_obj = self.do_search_to_obj(_from, _to, lookup_value)

        _rendered_entry_templates = []

        def sort_entry(r):
            return r.get('left')

        # This is stuff sort of performed by the other context rendering
        # function.
        sorted_results = sorted(search_result_obj.formatted_results,
                                key=sort_entry)

        template_results = [ {'input': lookup_value, 'lookups': sorted_results} ]

        logIndexLookups(lookup_value, template_results, _from, _to)

        show_info = False

        def sort_entry(r):
            if r[0] is None:
                return False
            if len(r[0]) > 0:
                return False
            try:
                return ''.join(r[0].xpath('./lg/l/text()'))
            except:
                return False


        for lz, az in sorted(search_result_obj.entries_and_tags, key=sort_entry):
            if lz is not None:
                tplkwargs = { 'lexicon_entry': lz
                            , 'analyses': az

                            , '_from': _from
                            , '_to': _to
                            , 'user_input': lookup_value
                            , 'word_searches': template_results
                            # TODO: errors??
                            , 'errors': False
                            , 'show_info': show_info
                            # , 'zip': zipNoTruncate
                            , 'dictionaries_available': current_app.config.pair_definitions
                            , 'successful_entry_exists': search_result_obj.successful_entry_exists
                            }
                tplkwargs.update(**default_context_kwargs)
                _rendered_entry_templates.append(
                    current_app.lexicon_templates.render_template(_from, 'entry.template', **tplkwargs)
                )

        all_az = sum([az for _, az in sorted(search_result_obj.entries_and_tags, key=sort_entry)], [])

        indiv_template_kwargs = {
            'analyses': all_az,
        }
        indiv_template_kwargs.update(**default_context_kwargs)

        all_analysis_template = \
            current_app.lexicon_templates.render_individual_template(_from, 'analyses.template', **indiv_template_kwargs)

        if search_result_obj.analyses_without_lex:
            leftover_tpl_kwargs = {
                'analyses': search_result_obj.analyses_without_lex,
            }
            leftover_tpl_kwargs.update(**default_context_kwargs)
            leftover_analyses_template = \
                current_app.lexicon_templates.render_individual_template( _from
                                                                        , 'analyses.template'
                                                                        , **leftover_tpl_kwargs
                                                                        )
        else:
            leftover_analyses_template = False

        search_context = {
            '_from': _from,
            '_to': _to,

            # This is the new style stuff.
            'new_templates': _rendered_entry_templates,
            'leftover_analyses_template': leftover_analyses_template,
            'all_analysis_template': all_analysis_template,

            # These variables can be turned into something more general
            'successful_entry_exists': search_result_obj.successful_entry_exists,

            'word_searches': template_results,
            'analyses': search_result_obj.analyses,
            'analyses_without_lex': search_result_obj.analyses_without_lex,
            'user_input': search_result_obj.search_term,

            # ?
            'errors': False, # where should we expect errors?
        }

        search_context.update(**default_context_kwargs)

        return search_context

from lexicon import FrontPageFormat

class LanguagePairSearchView(MethodView, SearcherMixin):
    """ This view returns either the search form, or processes the
    search request.

    This will be as much view logic as possible, search functionality
    will go elsewhere.

    """

    methods = ['GET', 'POST']
    template_name = 'index.html'

    formatter = FrontPageFormat

    def get_shared_context(self, _from, _to):
        """ Return some things that are in all templates. """

        pair_settings, orig_pair_opts = resolve_original_pair(current_app.config, _from, _to)
        shared_context = {
            'current_pair_settings': pair_settings,
            'display_swap': self.get_reverse_pair(_from, _to),
            # TODO: 'show_info': ? set this based on sesion and whether
            # the user has seen the message once, etc.
        }
        shared_context.update(**orig_pair_opts)
        return shared_context

    def check_pair_exists_or_abort(self, _from, _to):

        if (_from, _to) not in current_app.config.dictionaries and \
           (_from, _to) not in current_app.config.variant_dictionaries:
            abort(404)

        return False

    def get_reverse_pair(self, _from, _to):
        """ If the reverse pair for (_from, _to) exists, return the
        pair's settings, otherwise False. """

        pair_settings, orig_pair_opts = resolve_original_pair(current_app.config, _from, _to)
        _r_from, _r_to = orig_pair_opts.get('swap_from'), orig_pair_opts.get('swap_to')
        reverse_exists = current_app.config.dictionaries.get((_r_from, _r_to), False)

        return reverse_exists


    def get(self, _from, _to):

        self.check_pair_exists_or_abort(_from, _to)

        # If the view is for an input variant, we need the original
        # pair:

        default_context = {
            '_from': _from,
            '_to': _to,

            # These variables are produced from a search.
            'successful_entry_exists': False,
            'word_searches': False,
            'analyses': False,
            'analyses_without_lex': False,
            'user_input': False,

            # ?
            'errors': False, # is this actually getting set?

            # Show the default info under search box
            'show_info': True,
        }

        default_context.update(**self.get_shared_context(_from, _to))

        return render_template(self.template_name, **default_context)

    def post(self, _from, _to):

        if current_app.config.new_style_templates:
            return self.handle_newstyle_post(_from, _to)

        user_input = lookup_val = request.form.get('lookup', False)

        if not user_input:
            user_input = ''
            show_info = True
            # TODO: return an error.

        # This performs lots of the work...
        search_result_context = self.search_to_context(_from, _to, user_input)

        search_result_context.update(**self.get_shared_context(_from, _to))

        return render_template(self.template_name, **search_result_context)

    def handle_newstyle_post(self, _from, _to):
        print "newstyle handle"

        user_input = lookup_val = request.form.get('lookup', False)

        if not user_input:
            user_input = ''
            show_info = True
            # TODO: return an error.

        # This performs lots of the work...
        search_result_context = self.search_to_newstyle_context(_from, _to, user_input, **self.get_shared_context(_from, _to))

        # missing current_pair_settings
        return render_template('index_new_style.html', **search_result_context)

## Class-based views routing:

blueprint.add_url_rule( '/'
                      , view_func=IndexSearchPage.as_view('index_search_page')
                      , endpoint="canonical-root"
                      )

blueprint.add_url_rule( '/<_from>/<_to>/'
                      , view_func=LanguagePairSearchView.as_view('language_pair_search')
                      )

