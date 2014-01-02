from . import blueprint
from flask import current_app

import sys

import simplejson

from logging import getLogger

from utils.logger import *
from utils.data import *
from i18n.utils import iso_filter
from utils.encoding import *

from flask import ( request
                  , session
                  , Response
                  , render_template
                  , abort
                  , redirect
                  )

def to_xml_string(n):
    """ Return a string from an lxml node within an entry result.
    """
    from lxml import etree
    if 'entries' in n:
        if 'node' in n.get('entries'):
            node = n['entries']['node']
            _str = etree.tostring(node, pretty_print=True, encoding="utf-8")
            return _str.decode('utf-8')
    return ''

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
    from operator import itemgetter

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

    if cached_result is None:

        # Use the original language pair if the user has selected a
        # variant

        if (from_language, to_language) not in current_app.config.dictionaries and \
           (from_language, to_language)     in current_app.config.variant_dictionaries:
            var = current_app.config.variant_dictionaries.get((from_language, to_language))
            (from_language, to_language) = var.get('orig_pair')

        # Generation paradigms, and generation options
        lang_paradigms = current_app.config.paradigms.get(from_language)
        if not lang_paradigms:
            unsupportedLang(', no paradigm defined.')

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
                        _generated = morph.generate_string(paradigm_from_file, node)
                    else:
                        # try with pos, fallback to upper
                        paradigm = lang_paradigms.get(
                            pos, lang_paradigms.get(pos.upper(), False)
                        )

                        if paradigm:
                            _pos_type = [pos]
                            if _type:
                                _pos_type.append(_type)
                            form_tags = [_pos_type + _t.split('+') for _t in paradigm]

                            _generated = morph.generate(lemma, form_tags, node)
                        else:
                            _generated = False

                    r['paradigm'] = _generated
                    _formatted_with_paradigms.append(r)
                formatted_results.extend(_formatted_with_paradigms)
            else:
                analyses_without_lex.extend(morph_analyses)

        analyses = [(l.lemma, l.pos, l.tag) for l in analyses]

        detailed_result = sorted( pickleable_result(formatted_results)
                                , key=lambda x: x.get('lemma')
                                )

        current_app.cache.set(entry_cache_key, detailed_result)
    else:
        detailed_result = cached_result

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

    if format == 'json':
        result = simplejson.dumps({
            "success": True,
            "result": detailed_result
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

        return render_template( 'word_detail.html'
                              , language_pairs=current_app.config.pair_definitions
                              , result=detailed_result
                              , user_input=user_input
                              , _from=from_language
                              , _to=to_language
                              , more_detail_link=want_more_detail
                              , zip=zipNoTruncate
                              , has_analyses=has_analyses
                              )

@blueprint.route('/more/', methods=['GET'])
def more_dictionaries():
    return render_template('more_dictionaries.html')

# For direct links, form submission.
@blueprint.route('/<_from>/<_to>/', methods=['GET', 'POST'])
def indexWithLangs(_from, _to):
    from lexicon import FrontPageFormat
    from operator import itemgetter

    # mobile test for most common browsers
    mobile = False
    if request.user_agent.platform in ['iphone', 'android']:
        mobile = True

    iphone = False
    if request.user_agent.platform == 'iphone':
        iphone = True

    analyses_without_lex = []
    mlex = current_app.morpholexicon

    user_input = lookup_val = request.form.get('lookup', False)

    if (_from, _to) not in current_app.config.dictionaries and \
       (_from, _to) not in current_app.config.variant_dictionaries:
        abort(404)

    swap_from, swap_to = (_to, _from)

    successful_entry_exists = False
    errors = []

    results = False
    analyses = False

    if request.method == 'POST' and lookup_val:

        mlex = current_app.morpholexicon

        entries_and_tags = mlex.lookup( lookup_val
                                      , source_lang=_from
                                      , target_lang=_to
                                      , split_compounds=True
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

        logIndexLookups(user_input, results, _from, _to)

        show_info = False
    else:
        user_input = ''
        show_info = True

    if len(errors) == 0:
        errors = False

    # Variables to control presentation based on variants present
    current_pair = current_app.config.pair_definitions.get((_from, _to), {})
    reverse_pair = current_app.config.pair_definitions.get((_to, _from), {})

    current_pair_variants = current_pair.get('input_variants', False)
    has_variant = bool(current_pair_variants)
    has_mobile_variant = False

    if has_variant:
        _mobile_variants = filter( lambda x: x.get('type', '') == 'mobile'
                                 , current_pair_variants
                                 )
        if len(_mobile_variants) > 0:
            has_mobile_variant = _mobile_variants[0]


    variant_dictionaries = current_app.config.variant_dictionaries
    is_variant, orig_pair = False, ()

    if variant_dictionaries:
        variant    = variant_dictionaries.get((_from, _to), False)
        is_variant = bool(variant)
        if is_variant:
            orig_pair = variant.get('orig_pair')

    # Now we check if the reverse has variants for swapping
    # If there is a reverse pair with variants, get the mobile one as a
    # preference for swapping if the user is a mobile user, otherwise
    # just the default.

    reverse_has_variant = False
    if is_variant:
        _reverse_is_variant = current_app.config.variant_dictionaries.get( orig_pair
                                                                         , False
                                                                         )
    else:
        _reverse_is_variant = current_app.config.variant_dictionaries.get( (_to, _from)
                                                                         , False
                                                                         )

    _reverse_variants = reverse_pair.get('input_variants', False)

    if _reverse_variants:
        _mobile_variants = filter( lambda x: x.get('type', '') == 'mobile'
                                 , _reverse_variants
                                 )
        _standard_variants = filter( lambda x: x.get('type', '') == 'standard'
                                   , _reverse_variants
                                   )
        if mobile and len(_mobile_variants) > 0:
            _preferred_swap = _mobile_variants[0]
            _short_name = _preferred_swap.get('short_name')
            swap_from = _short_name
    else:
        if is_variant:
            swap_to, swap_from = orig_pair

    # TODO: include form analysis of user input #formanalysis
    return render_template( 'index.html'
                          , language_pairs=current_app.config.pair_definitions
                          , variant_dictionaries=variant_dictionaries
                          , is_variant=is_variant
                          , orig_pair=orig_pair
                          , has_variant=has_variant
                          , has_mobile_variant=has_mobile_variant
                          , _from=_from
                          , _to=_to
                          , swap_from=swap_from
                          , swap_to=swap_to
                          , user_input=lookup_val
                          , word_searches=results
                          , analyses=analyses
                          , analyses_without_lex=analyses_without_lex
                          , errors=errors
                          , show_info=show_info
                          , zip=zipNoTruncate
                          , successful_entry_exists=successful_entry_exists
                          , mobile=mobile
                          , iphone=iphone
                          )

accepted_lemma_args = {
    'l_til_ref': 'til_ref',
}

# For direct links, form submission.
@blueprint.route('/<_from>/<_to>/ref/', methods=['GET'])
def indexWithLangsToReference(_from, _to):
    from lexicon import FrontPageFormat
    from operator import itemgetter

    # mobile test for most common browsers
    mobile = False
    if request.user_agent.platform in ['iphone', 'android']:
        mobile = True

    iphone = False
    if request.user_agent.platform == 'iphone':
        iphone = True

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

    # TODO: include form analysis of user input #formanalysis
    return render_template( 'index.html'
                          , language_pairs=current_app.config.pair_definitions
                          , _from=_from
                          , _to=_to
                          , swap_from=_to
                          , swap_to=_from
                          , user_input=lookup_val
                          , word_searches=results
                          , analyses=analyses
                          , analyses_without_lex=analyses_without_lex
                          , errors=errors
                          , show_info=show_info
                          , zip=zipNoTruncate
                          , successful_entry_exists=successful_entry_exists
                          , mobile=mobile
                          , iphone=iphone
                          )

@blueprint.route('/about/', methods=['GET'])
def about():
    from jinja2 import TemplateNotFound
    try:
        return render_template('about.%s.html' % current_app.config.short_name)
    except TemplateNotFound:
        print >> sys.stderr, (
            ' * OBS! about.%s.html not found, '
            'falling back to about.sanit.html.' % current_app.config.short_name
        )
        return render_template('about.sanit.html')

def gen_doc(from_language, docs_list):
    _docs = []
    for lx, fxs in docs_list.iteritems():
        if lx != from_language:
            continue

        keys = ('name', 'doc')
        functions = [(fx, unicode(d.decode('utf-8')).strip()) for fx, d in fxs]

        functions = [dict(zip(keys, d)) for d in functions]

        # TODO: find decorated function doc
        doc = {
            'name': lx,
            'main_doc': "TODO", #  mod.__doc__,
            'functions': functions
        }

        _docs.append(doc)
    return _docs

@blueprint.route('/config_doc/<from_language>/', methods=['GET'])
def config_doc(from_language):
    """ Quick overview of language-specific details.
    """
    excludes = [
        '__builtins__',
        '__doc__',
        '__file__',
        '__package__',
    ]

    override_mods = current_app.config.overrides

    from morphology import generation_overrides
    from lexicon import lexicon_overrides
    from morpholex import morpholex_overrides

    generation_docs = gen_doc(from_language, generation_overrides.tag_filter_doc)
    pregen_doc = gen_doc(from_language, generation_overrides.pregenerators_doc)
    postanalysis_doc = gen_doc(from_language, generation_overrides.postanalyzers_doc)
    postgen_doc = gen_doc(from_language, generation_overrides.postgeneration_processors_doc)

    # TODO: lexicon overrides
    # TODO: morpholexicon overrides

    # TODO: filter paradigms, tag_filters

    paradigms = current_app.config.paradigms.get(from_language, {})
    tag_transforms = current_app.config.tag_filters
    languages = []

    return render_template( 'config_doc.html'

                          , generation_docs=generation_docs
                          , pregen_doc=pregen_doc
                          , postanalysis_doc=postanalysis_doc
                          , postgen_doc=postgen_doc

                          , paradigms=paradigms
                          , tag_transforms=tag_transforms
                          , languages=languages
                          , lang_name=from_language
                          )


@blueprint.route('/plugins/', methods=['GET'])
def plugins():
    return render_template('plugins.html')


@blueprint.route('/', methods=['GET'], endpoint="canonical-root")
def index():

    default_from, default_to = current_app.config.default_language_pair
    mobile_redir = current_app.config.mobile_redirect_pair

    iphone = False
    if request.user_agent.platform == 'iphone':
        iphone = True

    mobile = False
    if mobile_redir:
        target_url = '/%s/%s/' % tuple(mobile_redir)
        if request.user_agent.platform in ['iphone', 'android']:
            mobile = True
            # Only redirect if the user isn't coming back to the home page
            # from somewhere within the app.
            if request.referrer and request.host:
                if not request.host in request.referrer:
                    return redirect(target_url)
            else:
                return redirect(target_url)

    return render_template( 'index.html'
                          , language_pairs=current_app.config.pair_definitions
                          , _from=default_from
                          , _to=default_to
                          , swap_from=default_to
                          , swap_to=default_from
                          , show_info=True
                          , mobile=mobile
                          , iphone=iphone
                          )
