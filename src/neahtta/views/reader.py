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

@blueprint.route('/lookup/<from_language>/<to_language>/',
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

    if (from_language, to_language) not in current_app.config.dictionaries:
        abort(404)

    success = False

    # URL parameters
    lookup_key = user_input = request.args.get('lookup', False)
    has_callback            = request.args.get('callback', False)
    pretty                  = request.args.get('pretty', False)

    # Sometimes due to probably weird client-side behavior, the lookup
    # key is set but set to nothing, as such we need to return a
    # response when this happens, but the response is nothing.
    if lookup_key is False or not lookup_key.strip():

        data = json.dumps({ 'result': []
                          , 'tags': []
                          , 'tag_msg': ""
                          , 'success': False
                          })

        return Response( response=data
                       , status=200
                       , mimetype="application/json"
                       )

    def filterPOS(r):
        def fixTag(t):
            t_pos = t.get('pos', False)
            if not t_pos:
                return t
            t['pos'] = tagfilter(t_pos, from_language, to_language)
            return t
        return fixTag(r)

    mlex = current_app.morpholexicon

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
            joined = ' '.join(analysis.tag)
            return (analysis.lemma, joined)
        tags = map(filterPOSAndTag, analyses)
    else:
        tags = []

    ui_lang = iso_filter(session.get('locale', to_language))
    result = SimpleJSON( xml_nodes
                       , target_lang=to_language
                       , source_lang=from_language
                       , ui_lang=ui_lang
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

### @blueprint.route('/read/debug/', methods=['GET'])
### def bookmarklet_debug():
###     from bookmarklet_code import bookmarklet_escaped
###     bkmklt = bookmarklet_escaped.replace( 'sanit.oahpa.no'
###                                         , 'localhost%3A5000'
###                                         )\
###                                 .replace( 'bookmarklet.min.js'
###                                         , 'bookmarklet.js'
###                                         )
###     return render_template('reader.html', bookmarklet=bkmklt)

### @blueprint.route('/read/example/', methods=['GET'])
### def bookmarklet_example_page():
###     from bookmarklet_code import bookmarklet_escaped
###     bkmklt = bookmarklet_escaped.replace( 'sanit.oahpa.no'
###                                         , 'localhost%3A5000'
###                                         )\
###                                 .replace( 'bookmarklet.min.js'
###                                         , 'bookmarklet.js'
###                                         )
###     hostname = request.host
###     return render_template( 'reader_example.html'
###                           , bookmarklet_local=bkmklt
###                           , bookmarklet=bookmarklet_escaped
###                           , hostname=hostname
###                           )

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

    dictionaries = [
        { 'from': {'iso': _from, 'name': unicode(NAMES.get(_from))}
        , 'to':   {'iso': _to,   'name': unicode(NAMES.get(_to))}
        , 'uri': "/lookup/%s/%s/" % (_from, _to)
        }
        for _from, _to in current_app.config.dictionaries.keys()
    ]

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
