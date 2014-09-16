from flask import ( request
                  , Response
                  , json
                  , session
                  , render_template
                  , current_app
                  , abort
                  )

from . import blueprint

from utils.json import fmtForCallback
from utils.logger import logSimpleLookups
from i18n.utils import iso_filter

from morphology.utils import tagfilter
from flaskext.babel import gettext as _

from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper


def json_response(data, *args, **kwargs):
    return Response( response=json.dumps(data)
                   , status=200
                   , mimetype="application/json"
                   )


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    """ Cross-domain decorator from Flask documentation with some
    modifications. This provides an OPTIONS response containing
    permitted headers and content types.
    """
    from   logging                        import getLogger
    debug_log = getLogger("debug_log")

    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers
            debug_log.info(request.method)
            debug_log.info(repr(origin))

            debug_log.info("headers: " + repr(headers))

            debug_log.info("request.headers:")
            for k, v in request.headers:
                debug_log.info("    %s\t%s" % (k, v))

            debug_log.info("h:")
            for k, v in h:
                debug_log.info("    %s\t%s" % (k, v))
            debug_log.info(" -- ")

            # origin is '*' here
            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            # NB: Content-Type wasn't set, so I'm doing it here, but
            # also it needs to be in the Access-Control-Allow-Headers.
            h['Content-Type'] = 'application/json'
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

@blueprint.route('/lookup/<from_language>/<to_language>/',
           methods=['OPTIONS', 'GET', 'POST'], endpoint="lookup")
@crossdomain(origin='*', headers=['Content-Type'])
def lookupWord(from_language, to_language):
    """
    .. http:post:: /lookup/(string:from_language)/(string:to_language)

       Looks up a query in the lexicon. Lookups are lemmatized first,
       but the non-lemmatized input is also checked in the lexicon.

       The lookup string may contain multiple lookups as well, separated
       by `|`, but this needs to be signaled by an additional parameter,
       `multiword`.

       :param from_language: the source language of the lookup
       :param to_language:   the target language to display translations
       :form lookup: the search word.
       :form multiword: (optional) enable multiple lookups, separated by
           `|` in the lookup string.

       :throws Http404: In the event that the language pair does not exist.
       :returns:
           JSON data is returned with the help of the formatter
           :py:class:`lexicon.formatters.SimpleJSON`
    """
    import simplejson

    from lexicon import SimpleJSON

    if (from_language, to_language) not in current_app.config.dictionaries and \
       (from_language, to_language) not in current_app.config.variant_dictionaries:
        abort(404)

    success = False

    if request.method == 'GET':
        # URL parameters
        lookup_key = user_input = request.args.get('lookup', False)
        has_callback            = request.args.get('callback', False)
        pretty                  = request.args.get('pretty', False)

        multiword   = request.args.get('multiword', False)

    elif request.method == 'POST':
        input_json = simplejson.loads(request.data)

        lookup_key = user_input = input_json.get('lookup', False)
        has_callback            = request.args.get('callback', False) or input_json.get('callback', False)
        pretty                  = input_json.get('pretty', False)

        multiword   = input_json.get('multiword', False)

    if multiword:
        if isinstance(lookup_key, str) or isinstance(lookup_key, unicode):
            lookups = lookup_key.split('|')
        else:
            lookups = lookup_key
            lookup_key = '|'.join(lookup_key)
    else:
        lookups = [lookup_key]

    # Sometimes due to probably weird client-side behavior, the lookup
    # key is set but set to nothing, as such we need to return a
    # response when this happens, but the response is nothing.

    response_data = {
        'result'  : [],
        'tags'    : [],
        'tag_msg' : "",
        'success' : False
    }

    if lookup_key is False or not lookup_key.strip():
        return json_response(response_data)

    mlex = current_app.morpholexicon

    multi_lookups = []
    multi_tags = []

    for lookup in lookups:
        morpholexicon_lookup = mlex.lookup( lookup
                                      , source_lang=from_language
                                      , target_lang=to_language
                                      , split_compounds=True
                                      # , non_compound_only=True
                                      # , no_derivations=True
                                      )

        def filterPOSAndTag(analysis):
            filtered_pos = tagfilter(analysis.pos, from_language, to_language)
            joined = ' '.join(analysis.tag)
            return (analysis.lemma, joined)

        analyses = morpholexicon_lookup.analyses

        tags = map(
            filterPOSAndTag,
            analyses
        )

        if multiword:
            _u_in = lookup
        else:
            _u_in = user_input

        ui_lang = iso_filter(session.get('locale', to_language))
        result = SimpleJSON( morpholexicon_lookup.entries
                           , target_lang=to_language
                           , source_lang=from_language
                           , ui_lang=ui_lang
                           , user_input=_u_in
                           )

        result = result.sorted_by_pos()

        if len(result) > 0:
            success = True

        result_with_input = [{'input': lookup, 'lookups': result}]

        logSimpleLookups( lookup
                        , result_with_input
                        , from_language
                        , to_language
                        )

        multi_lookups.extend(result)
        multi_tags.extend(tags)

    results_with_input = [{'input': lookup_key, 'lookups': multi_lookups}]

    data = json.dumps({ 'result': results_with_input
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

@blueprint.route('/read/ie8_instructions/', methods=['GET'])
def ie8_instrux():
    return render_template('reader_ie8_notice.html')

@blueprint.route('/read/ie8_instructions/json/', methods=['GET'])
def ie8_instrux_json():
    # Force template into json response
    has_callback = request.args.get('callback', False)
    r = render_template('reader_ie8_notice.html')

    formatted = fmtForCallback(json.dumps(r), has_callback)
    return Response( response=formatted
                   , status=200
                   , mimetype="application/json"
                   )

@blueprint.route('/read/update/', methods=['GET'])
def reader_update():
    from bookmarklet_code import bookmarklet_escaped
    from urllib import quote_plus
    bkmklt = bookmarklet_escaped.replace( 'sanit.oahpa.no'
                                        , quote_plus(request.host)
                                        )
    # Force template into json response
    has_callback = request.args.get('callback', False)
    return render_template('reader_update.html', bookmarklet=bkmklt)

@blueprint.route('/read/update/json/', methods=['GET'])
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

def fetch_messages(locale):
    from i18n.polib import pofile

    try:
        _pofile = pofile('translations/%s/LC_MESSAGES/messages.po' % locale)
    except:
        return {}

    jsentries = filter( lambda x: any(['.js' in a[0] for a in x.occurrences])
                      , list(_pofile)
                      )

    return dict( [(e.msgid, e.msgstr or False) for e in jsentries] )


@blueprint.route('/read/config/', methods=['GET'])
def bookmarklet_configs():
    """ Compile a JSON response containing dictionary pairs,
    and internationalization strings.
    """
    from flaskext.babel import get_locale
    from configs.language_names import NAMES

    has_callback = request.args.get('callback', False)
    sess_lang = request.args.get('language', get_locale())

    translated_messages = fetch_messages(sess_lang)

    dictionaries = []

    prepared = []

    for (_from, _to), pair_options in current_app.config.dictionaries.iteritems():
        prepared.append((_from, _to))

        reader_dict_opts = current_app.config.reader_options.get(_from, {})

        dictionaries.append(
            { 'from': {'iso': _from, 'name': unicode(NAMES.get(_from))}
            , 'to':   {'iso': _to,   'name': unicode(NAMES.get(_to))}
            , 'uri': "/lookup/%s/%s/" % (_from, _to)
            , 'settings': reader_dict_opts
            }
        )


        _has_variant = current_app.config.pair_definitions.get((_from, _to), {}) \
                                         .get('input_variants', False)

        if _has_variant:
            for variant in _has_variant:
                v_from = variant.get('short_name')
                variant_dict_opts = current_app.config.reader_options.get(v_from, {})
                if not (v_from, _to) in prepared:
                    dictionaries.append(
                        { 'from': {'iso': v_from, 'name': unicode(NAMES.get(v_from))}
                        , 'to':   {'iso': _to,    'name': unicode(NAMES.get(_to))}
                        , 'uri': "/lookup/%s/%s/" % (_from, _to)
                        , 'settings': variant_dict_opts
                        }
                    )
                    prepared.append((v_from, _to))

    data = { 'dictionaries': dictionaries
           , 'localization': translated_messages
           }

    formatted = fmtForCallback(json.dumps(data), has_callback)

    return Response( response=formatted
                   , status=200
                   , mimetype="application/json"
                   )

@blueprint.route('/read/', methods=['GET'])
def bookmarklet():
    from bookmarklet_code import bookmarklet_escaped
    from urllib import quote_plus
    bkmklt = bookmarklet_escaped
    bkmklt = bookmarklet_escaped.replace( 'sanit.oahpa.no'
                                        , quote_plus(request.host)
                                        )

    return render_template( 'reader.html'
                          , bookmarklet=bkmklt
                          , language_pairs=current_app.config.pair_definitions
                          )
