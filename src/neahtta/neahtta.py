#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
A service that provides JSON and RESTful lookups to webdict xml trie
files.

This is the main file which handles initializing the app and providing
endpoint functionality. Documentation on installing and maintaining
config files is elsewhere.

"""

import sys
import logging
import urllib
from   flask                          import ( Flask
                                             , request
                                             , redirect
                                             , session
                                             , json
                                             , render_template
                                             , Markup
                                             , Response
                                             , abort
                                             )

from   werkzeug.contrib.cache         import SimpleCache
from   config                         import Config
from   utils                          import *
from   logging                        import getLogger

from   flaskext.babel                 import Babel
from   flaskext.babel                 import gettext as _


def create_app():
    """ Set up the Flask app, cache, read app configuration file, and
    other things.
    """
    from morpho_lexicon import MorphoLexicon
    # TODO: this is called twice sometimes, slowdowns have been reduced,
    # but don't know why yet. Need to check. It only happens on the
    # first POST lookup, however...

    # import inspect
    # curframe = inspect.currentframe()
    # calframe = inspect.getouterframes(curframe, 2)
    # print "caller name", calframe[1]

    cache = SimpleCache()
    app = Flask(__name__,
        static_url_path='/static',)

    app.jinja_env.line_statement_prefix = '#'
    app.jinja_env.add_extension('jinja2.ext.i18n')
    app.config['cache'] = cache
    app.cache = cache

    app.config = Config('.', defaults=app.config)
    app.config.from_envvar('NDS_CONFIG')

    app.morpholexicon = MorphoLexicon(app.config)

    try:
        with open('secret_key.do.not.check.in', 'r') as F:
            key = F.readlines()[0].strip()
        app.config['SECRET_KEY'] = key
    except IOError:
        print >> sys.stderr, """
        You need to generate a secret key, and store it in a file with the
        following name: secret_key.do.not.check.in """
        sys.exit()

    babel = Babel(app)
    babel.init_app(app)

    app.babel = babel

    return app

app = create_app()

# Configure user_log
user_log = getLogger("user_log")
useLogFile = logging.FileHandler('user_log.txt')
user_log.addHandler(useLogFile)
user_log.setLevel("INFO")

###
### Additional localization/internationalization setup, and locale helpers
###

def iso_filter(_iso):
    """ These things are sort of a temporary fix for some of the
    localization that runs off of CSS selectors, in order to include the
    3 digit ISO into the <body /> @lang attribute.
    """
    from language_names import ISO_TRANSFORMS
    return ISO_TRANSFORMS.get(_iso, _iso)

@app.babel.localeselector
def get_locale():
    """ This function defines the behavior involved in selecting a
    locale. """

    locales = app.config.locales_available

    # Does the locale exist already?
    ses_lang = session.get('locale', None)
    if ses_lang is not None:
        return ses_lang
    else:
        # Is there a default locale specified in config file?
        ses_lang = app.config.default_locale
        if not app.config.default_locale:
            # Guess the locale based on some magic that babel performs
            # on request headers.
            ses_lang = request.accept_languages.best_match(locales)
        # Append to session
        session.locale = ses_lang
        app.jinja_env.globals['session'] = session

    return ses_lang

###
### Additional template contexts
###

@app.before_request
def append_session_globals():
    """ Add two-character and three-char session locale to global
    template contexts: session_locale, session_locale_long_iso.
    """

    loc = get_locale()

    app.jinja_env.globals['session_locale'] = loc
    app.jinja_env.globals['session_locale_long_iso'] = iso_filter(loc)

@app.context_processor
def add_languages():
    return dict(internationalizations=app.config.locales_available)

@app.context_processor
def define_app_name():
    return dict(app_name=app.config.app_name)

@app.context_processor
def define_app_meta():
    return dict(app_meta_desc=app.config.meta_description)

@app.context_processor
def define_app_meta_keywords():
    return dict(app_meta_keywords=app.config.meta_keywords)


##
## Template filters
##

@app.template_filter('iso_to_language_own_name')
def iso_to_language_own_name(_iso):
    from language_names import LOCALISATION_NAMES_BY_LANGUAGE
    return LOCALISATION_NAMES_BY_LANGUAGE.get(_iso, _iso)

@app.template_filter('iso_to_i18n')
def append_language_names_i18n(s):
    from language_names import NAMES
    return NAMES.get(s, s)

@app.template_filter('to_xml_string')
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

@app.template_filter('sneak_in_link')
def sneak_in_link(s, link_src):
    """ Split a string at the first parenthesis, if the string contains
    any, and wrap the first part in a link; otherwise wrap the whole
    thing in a link.
    """

    target_word, paren, rest = s.partition('(')

    if paren:
        return '<a href="%s">%s</a> (%s' % ( link_src
                                           , target_word
                                           , rest
                                           )
    else:
        return '<a href="%s">%s</a>' % ( link_src
                                       , target_word
                                       )

def tagfilter_conf(filters, s):
    """ A helper function for filters to extract app.config from the
    function for import in other modules.
    """
    if not s:
        return s

    filtered = []
    if isinstance(s, list):
        parts = s
    else:
        parts = s.split(' ')
    for part in parts:
        # try part, and if it doesn't work, then try part.lower()
        _f_part = filters.get( part
                             , filters.get( part.lower()
                                          , part
                                          )
                             )
        filtered.append(_f_part)

    return ' '.join([a for a in filtered if a.strip()])

@app.template_filter('tagfilter')
def tagfilter(s, lang_iso, targ_lang):

    filters = app.config.tag_filters.get((lang_iso, targ_lang), False)

    if filters:
        return tagfilter_conf(filters, s)
    else:
        return s


@app.template_filter('urlencode')
def urlencode_filter(s):
    if type(s) == 'Markup':
        s = s.unescape()
    s = s.encode('utf8')
    s = urllib.quote_plus(s)
    return Markup(s)

##
##  Error templates
##
##

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e, *args, **kwargs):
    return render_template('500.html', error=e), 500

##
##  Endpoints
##
##

@app.route('/autocomplete/<from_language>/<to_language>/',
           methods=['GET'], endpoint="autocomplete")
def autocomplete(from_language, to_language):

    autocomplete_tries = app.config.lexicon.autocomplete_tries
    # URL parameters
    lookup_key   = request.args.get('lookup', False)
    lemmatize    = request.args.get('lemmatize', False)
    has_callback = request.args.get('callback', False)

    autocompleter = autocomplete_tries.get((from_language, to_language), False)

    if not autocompleter:
        return fmtForCallback(
                json.dumps(" * No autocomplete for this language pair."),
                has_callback)

    autos = autocompleter.autocomplete(lookup_key)

    # Only lemmatize if nothing returned from autocompleter?

    return Response(response=fmtForCallback(json.dumps(autos), has_callback),
                    status=200,
                    mimetype="application/json")

@app.route('/lookup/<from_language>/<to_language>/',
           methods=['GET'], endpoint="lookup")
def lookupWord(from_language, to_language):
    """
    .. http:post:: /lookup/(string:from_language)/(string:to_language)

       Looks up a query in the lexicon. Lookups are lemmatized first,
       but the non-lemmatized input is also checked in the lexicon.

       :param from_language: the source language of the lookup
       :param to_language:   the target language to display translations
       :form lookup: the search word.

       :throws Http404: In the event that the language pair does not exist.
       :returns:
           JSON data is returned with the help of the formatter
           :py:class:`lexicon.formatters.SimpleJSON`
    """
    from lexicon import SimpleJSON

    if (from_language, to_language) not in app.config.dictionaries:
        abort(404)

    success = False

    # URL parameters
    lookup_key = user_input = request.args.get('lookup', False)
    has_callback            = request.args.get('callback', False)
    pretty                  = request.args.get('pretty', False)

    if lookup_key is False:
        return json.dumps(" * lookup undefined")

    def filterPOS(r):
        def fixTag(t):
            t_pos = t.get('pos', False)
            if not t_pos:
                return t
            t['pos'] = tagfilter(t_pos, from_language, to_language)
            return t
        return fixTag(r)

    mlex = app.morpholexicon

    xml_nodes, analyses = mlex.lookup( lookup_key
                                     , source_lang=from_language
                                     , target_lang=to_language
                                     , split_compounds=True
                                     , non_compound_only=True
                                     , no_derivations=True
                                     )

    if analyses:
        def filterPOSAndTag(analysis):
            filtered_pos = tagfilter(analysis.pos, from_language, to_language)
            joined = filtered_pos + ' ' + ' '.join(analysis.tag)
            return (analysis.lemma, joined)
        tags = map(filterPOSAndTag, analyses)
    else:
        tags = []

    result = SimpleJSON( xml_nodes
                       , target_lang=to_language
                       )

    result = map(filterPOS, list(result))

    if len(result) > 0:
        success = True

    result_with_input = [{'input': lookup_key, 'lookups': result}]

    logSimpleLookups( user_input
                    , result_with_input
                    , from_language
                    , to_language
                    )

    data = json.dumps({ 'result': result_with_input
                      , 'tags': tags
                      , 'tag_msg': _(" is a possible form of ... ")
                      , 'success': success
                      })

    if pretty:
        data = json.dumps( json.loads(data)
                         , sort_keys=True
                         , indent=4
                         , separators=(',', ': ')
                         )

    if has_callback:
        data = '%s(%s)' % (has_callback, data)

    return Response( response=data
                   , status=200
                   , mimetype="application/json"
                   )

@app.route('/detail/<from_language>/<to_language>/<wordform>.<format>',
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

    # Do we want to analyze compounds?
    no_compounds = request.args.get('no_compounds', False)

    # Cache key by URL
    entry_cache_key = u'%s?%s' % (request.path, request.query_string)

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

    if app.caching_enabled:
        cached_result = app.cache.get(entry_cache_key)
    else:
        cached_result = None

    if cached_result is None:

        lang_paradigms = app.config.paradigms.get(from_language)
        if not lang_paradigms:
            unsupportedLang(', no paradigm defined.')

        morph = app.config.morphologies.get(from_language, False)

        if no_compounds:
            _split = True
            _non_c = True
            _non_d = False
        else:
            _split = True
            _non_c = False
            _non_d = False

        mlex = app.morpholexicon
        xml_nodes, analyses = mlex.lookup( wordform
                                         , source_lang=from_language
                                         , target_lang=to_language
                                         , split_compounds=_split
                                         , non_compounds_only=_non_c
                                         , no_derivations=_non_d
                                         )

        # TODO: move generation to detailed format? thus node correct
        # pos, tags, etc., are available
        res = list(DetailedFormat(xml_nodes, target_lang=to_language))

        lex_results = []
        for r in res:
            lemma = r.get('lemma')
            pos = r.get('pos')
            _type = r.get('type')
            input_info = (lemma, pos, '', _type)
            lex_results.append({
                'entries': r,
                'input': input_info,
            })

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
            node = r.get('entries').get('entry_hash')
            if node == e_node:
                return True
            else:
                return False

        if e_node:
            lex_results = filter(_byNodeHash, lex_results)
        if pos_filter:
            lex_results = filter(_byPOS, lex_results)
        if lemma_match:
            lex_results = filter(_byLemma, lex_results)

        analyses = [(l.lemma, l.pos, l.tag) for l in analyses]

        try:
            node_texts = map(to_xml_string, lex_results)
        except:
            node_texts = []

        detailed_result = {
            "input": wordform,
            "analyses": analyses,
            "lexicon": lex_results,
            "node_texts": node_texts
        }

        # Generate each paradigm.
        for _r in lex_results:
            lemma, pos, tag, _type = _r.get('input')
            try:
                node = _r.get('entries').get('node')
            except:
                node = False

            if pos is None:
                error_msg = "POS for entry is None\n"
                error_msg += "\n" + '\n'.join(node_texts)
                abort(500, error_msg)

            paradigm = lang_paradigms.get(pos, False)

            if paradigm:
                _pos_type = [pos]
                if _type:
                    _pos_type.append(_type)
                form_tags = [_pos_type + _t.split('+') for _t in paradigm]

                _generate = morph.generate(lemma, form_tags, node)
                _r['paradigms'] = _generate
            else:
                _r['paradigms'] = False

        app.cache.set(entry_cache_key, detailed_result)
    else:
        detailed_result = cached_result

    _lookup = detailed_result.get('lexicon')

    if len(_lookup) > 0:
        success = True
        result_lemmas = list(set([
            entry['input'][0] for entry in detailed_result['lexicon']
        ]))
        _meanings = []
        for lexeme in detailed_result['lexicon']:
            if lexeme['entries']:
                _entry_tx = []
                for mg in lexeme['entries']['meaningGroups']:
                    _entry_tx.append(mg['translations'])
                _meanings.append(_entry_tx)
        tx_set = '; '.join([', '.join(a) for a in _meanings])
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
        result = json.dumps({
            "success": True,
            "result": detailed_result
        })
        return result
    elif format == 'html':
        return render_template( 'word_detail.html'
                              , language_pairs=app.config.pair_definitions
                              , result=detailed_result
                              , user_input=user_input
                              , _from=from_language
                              , _to=to_language
                              , more_detail_link=want_more_detail
                              , zip=zipNoTruncate
                              )

@app.route('/read/ie8_instructions/', methods=['GET'])
def ie8_instrux():
    return render_template('reader_ie8_notice.html')

@app.route('/read/ie8_instructions/json/', methods=['GET'])
def ie8_instrux_json():
    # Force template into json response
    has_callback = request.args.get('callback', False)
    r = render_template('reader_ie8_notice.html')

    formatted = fmtForCallback(json.dumps(r), has_callback)
    return Response( response=formatted
                   , status=200
                   , mimetype="application/json"
                   )

@app.route('/read/update/', methods=['GET'])
def reader_update():
    from bookmarklet_code import bookmarklet_escaped
    from urllib import quote_plus
    bkmklt = bookmarklet_escaped.replace( 'sanit.oahpa.no'
                                        , quote_plus(request.host)
                                        )
    # Force template into json response
    has_callback = request.args.get('callback', False)
    return render_template('reader_update.html', bookmarklet=bkmklt)

@app.route('/read/update/json/', methods=['GET'])
def reader_update_json():
    from urllib import quote_plus
    from bookmarklet_code import bookmarklet_escaped
    bkmklt = bookmarklet_escaped.replace( 'sanit.oahpa.no'
                                        , quote_plus(request.host)
                                        )
    # Force template into json response
    has_callback = request.args.get('callback', False)
    r = render_template('reader_update.html', bookmarklet=bkmklt)

    formatted = fmtForCallback(json.dumps(r), has_callback)

    return Response( response=formatted
                   , status=200
                   , mimetype="application/json"
                   )

@app.route('/read/debug/', methods=['GET'])
def bookmarklet_debug():
    from bookmarklet_code import bookmarklet_escaped
    bkmklt = bookmarklet_escaped.replace( 'sanit.oahpa.no'
                                        , 'localhost%3A5000'
                                        )\
                                .replace( 'bookmarklet.min.js'
                                        , 'bookmarklet.js'
                                        )
    return render_template('reader.html', bookmarklet=bkmklt)

@app.route('/read/example/', methods=['GET'])
def bookmarklet_example_page():
    from bookmarklet_code import bookmarklet_escaped
    bkmklt = bookmarklet_escaped.replace( 'sanit.oahpa.no'
                                        , 'localhost%3A5000'
                                        )\
                                .replace( 'bookmarklet.min.js'
                                        , 'bookmarklet.js'
                                        )
    hostname = request.host
    return render_template( 'reader_example.html'
                          , bookmarklet_local=bkmklt
                          , bookmarklet=bookmarklet_escaped
                          , hostname=hostname
                          )

def fetch_messages(locale=app.config.default_locale):
    from polib import pofile

    try:
        _pofile = pofile('translations/%s/LC_MESSAGES/messages.po' % locale)
    except:
        return {}

    jsentries = filter( lambda x: any(['.js' in a[0] for a in x.occurrences])
                      , list(_pofile)
                      )

    return dict( [(e.msgid, e.msgstr or False) for e in jsentries] )


@app.route('/read/config/', methods=['GET'])
def bookmarklet_configs():
    """ Compile a JSON response containing dictionary pairs,
    and internationalization strings.
    """
    from flaskext.babel import get_locale
    from language_names import NAMES

    has_callback = request.args.get('callback', False)
    sess_lang = request.args.get('language', get_locale())

    translated_messages = fetch_messages(sess_lang)

    dictionaries = [
        { 'from': {'iso': _from, 'name': unicode(NAMES.get(_from))}
        , 'to':   {'iso': _to,   'name': unicode(NAMES.get(_to))}
        , 'uri': "/lookup/%s/%s/" % (_from, _to)
        }
        for _from, _to in app.config.dictionaries.keys()
    ]

    data = { 'dictionaries': dictionaries
           , 'localization': translated_messages
           }

    formatted = fmtForCallback(json.dumps(data), has_callback)

    return Response( response=formatted
                   , status=200
                   , mimetype="application/json"
                   )

@app.route('/more/', methods=['GET'])
def more_dictionaries():
    return render_template('more_dictionaries.html')

@app.route('/read/', methods=['GET'])
def bookmarklet():
    from bookmarklet_code import bookmarklet_escaped
    from urllib import quote_plus
    bkmklt = bookmarklet_escaped
    bkmklt = bookmarklet_escaped.replace( 'sanit.oahpa.no'
                                        , quote_plus(request.host)
                                        )

    return render_template( 'reader.html'
                          , bookmarklet=bkmklt
                          , language_pairs=app.config.pair_definitions
                          )

# For direct links, form submission.
@app.route('/<_from>/<_to>/', methods=['GET', 'POST'])
def indexWithLangs(_from, _to):
    from lexicon import FrontPageFormat

    # mobile test for most common browsers
    mobile = False
    if request.user_agent.platform in ['iphone', 'android']:
        mobile = True

    iphone = False
    if request.user_agent.platform == 'iphone':
        iphone = True

    mlex = app.morpholexicon

    user_input = lookup_val = request.form.get('lookup', False)

    if (_from, _to) not in app.config.dictionaries:
        abort(404)

    successful_entry_exists = False
    errors = []

    results = False
    analyses = False

    if request.method == 'POST' and lookup_val:

        mlex = app.morpholexicon

        xml_nodes, analyses = mlex.lookup( lookup_val
                                         , source_lang=_from
                                         , target_lang=_to
                                         , split_compounds=True
                                         )

        analyses = [(lem.input, lem.lemma, [lem.pos] + lem.tag)
                    for lem in analyses]

        fmtkwargs = { 'target_lang': _to
                    , 'source_lang': _from
                    , 'ui_lang': session.get('locale', _to)
                    }

        # [(lemma, XMLNodes)] -> [(lemma, generator(AlmostJSON))]
        formatted_results = list(FrontPageFormat(xml_nodes, **fmtkwargs))

        # When to display unknowns
        successful_entry_exists = False
        if len(formatted_results) > 0:
            successful_entry_exists = True

        results = sorted( formatted_results
                        , key=lambda (r): len(r.get('left'))
                        , reverse=True
                        )

        results = [ {'input': lookup_val, 'lookups': results} ]

        logIndexLookups(user_input, results, _from, _to)

        show_info = False
    else:
        user_input = ''
        show_info = True

    if len(errors) == 0:
        errors = False

    # TODO: include form analysis of user input #formanalysis
    return render_template( 'index.html'
                          , language_pairs=app.config.pair_definitions
                          , _from=_from
                          , _to=_to
                          , user_input=lookup_val
                          , word_searches=results
                          , analyses=analyses
                          , errors=errors
                          , show_info=show_info
                          , zip=zipNoTruncate
                          , successful_entry_exists=successful_entry_exists
                          , mobile=mobile
                          , iphone=iphone
                          )

@app.route('/about/', methods=['GET'])
def about():
    from jinja2 import TemplateNotFound
    try:
        return render_template('about.%s.html' % app.config.short_name)
    except TemplateNotFound:
        print >> sys.stderr, (
            ' * OBS! about.%s.html not found, '
            'falling back to about.sanit.html.' % app.config.short_name
        )
        return render_template('about.sanit.html')


@app.route('/plugins/', methods=['GET'])
def plugins():
    return render_template('plugins.html')

@app.route('/locale/<iso>/', methods=['GET'])
def set_locale(iso):
    from flaskext.babel import refresh

    session['locale'] = iso
    # Refresh the localization infos, and send the user back whence they
    # came.
    refresh()
    ref = request.referrer
    if ref is not None:
        return redirect(request.referrer)
    else:
        return redirect('/')

@app.route('/', methods=['GET'], endpoint="canonical-root")
def index():

    default_from, default_to = app.config.default_language_pair
    mobile_redir = app.config.mobile_redirect_pair

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
                          , language_pairs=app.config.pair_definitions
                          , _from=default_from
                          , _to=default_to
                          , show_info=True
                          , mobile=mobile
                          , iphone=iphone
                          )

if __name__ == "__main__":
    app.caching_enabled = True
    app.run(debug=True, use_reloader=False)

# vim: set ts=4 sw=4 tw=72 syntax=python expandtab :
