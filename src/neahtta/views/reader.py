# -*- encoding: utf-8 -*-
from datetime import timedelta
from functools import update_wrapper

from bookmarklet_code import generate_bookmarklet_code
from flask import (Response, abort, current_app, json, make_response,
                   render_template, request, session)
from flask.ext.babel import gettext as _
from flask.ext.babel import lazy_gettext
from i18n.utils import iso_filter
from morphology.utils import tagfilter
from utils.json import fmtForCallback
from utils.logger import logSimpleLookups

from . import blueprint


def json_response(data, pretty=False):
    """Turn data into json.

    Args:
        data (dict): dict to jsonify
        pretty (bool): if True, make json slightly more human friendly

    Returns:
        flask.Response
    """
    if pretty:
        data = json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        data = json.dumps(data)

    return Response(response=data, status=200, mimetype="application/json")


def crossdomain(origin=None,
                methods=None,
                headers=None,
                max_age=21600,
                attach_to_all=True,
                automatic_options=True):
    """ Cross-domain decorator from Flask documentation with some
    modifications. This provides an OPTIONS response containing
    permitted headers and content types.
    """

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

    current_app.limiter.check()

    if (from_language, to_language) not in current_app.config.dictionaries and \
       (from_language, to_language) not in current_app.config.variant_dictionaries:
        abort(404)

    success = False

    if request.method == 'GET':
        # URL parameters
        lookup_key = user_input = request.args.get('lookup', False)
        has_callback = request.args.get('callback', False)
        pretty = request.args.get('pretty', False)

        multiword = request.args.get('multiword', False)

    elif request.method == 'POST':
        input_json = simplejson.loads(request.data)

        lookup_key = user_input = input_json.get('lookup', False)
        has_callback = request.args.get('callback', False) or input_json.get(
            'callback', False)
        pretty = input_json.get('pretty', False)

        multiword = input_json.get('multiword', False)
    elif request.method == 'OPTIONS':
        return json_response({})

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

    response_data = {'result': [], 'tags': [], 'tag_msg': "", 'success': False}

    if lookup_key is False or not lookup_key.strip():
        return json_response(response_data)

    mlex = current_app.morpholexicon

    multi_lookups = []
    multi_tags = []

    for lookup in lookups:
        morpholexicon_lookup = mlex.lookup(
            lookup,
            source_lang=from_language,
            target_lang=to_language,
            split_compounds=True
            # , non_compound_only=True
            # , no_derivations=True
        )

        def filterPOSAndTag(analysis):
            filtered_pos = tagfilter(analysis.pos, from_language, to_language)
            joined = ' '.join(analysis.tag)
            return (analysis.lemma, joined)

        #Implementation of Der/ and Cmp/ resulted in nested array
        # (both here and in morpholex)
        #This is a quick fix, but TODO: maybe rethink the structure of new code?
        analyses = morpholexicon_lookup.analyses
        tags = map(filterPOSAndTag, analyses)

        if multiword:
            _u_in = lookup
        else:
            _u_in = user_input

        ui_lang = iso_filter(session.get('locale', to_language))
        result = SimpleJSON(
            morpholexicon_lookup.entries
            ##result = SimpleJSON( entr
            ,
            target_lang=to_language,
            source_lang=from_language,
            ui_lang=ui_lang,
            user_input=_u_in)
        result = result.sorted_by_pos()

        if len(result) > 0:
            success = True

        result_with_input = [{'input': lookup, 'lookups': result}]

        logSimpleLookups(lookup, result_with_input, from_language, to_language)

        multi_lookups.extend(result)
        multi_tags.extend(tags)

    results_with_input = [{'input': lookup_key, 'lookups': multi_lookups}]

    data = json.dumps({
        'result': results_with_input,
        'tags': tags,
        'tag_msg': _(" is a possible form of ... "),
        'success': success
    })

    if pretty:
        data = json.dumps(
            json.loads(data), sort_keys=True, indent=4, separators=(',', ': '))

    if has_callback:
        data = '%s(%s)' % (has_callback, data)

    return Response(response=data, status=200, mimetype="application/json")


def ie8_instrux():
    return render_template('reader_ie8_notice.html')


def ie8_instrux_json():
    # Force template into json response
    has_callback = request.args.get('callback', False)
    r = render_template('reader_ie8_notice.html')

    formatted = fmtForCallback(json.dumps(r), has_callback)
    return Response(
        response=formatted, status=200, mimetype="application/json")


def reader_test_page():
    """ This is also tied to a context processer making this item
    visible in the navigational menu if the template is found. """

    return render_template('reader_tests.template')


def reader_update():

    reader_settings = current_app.config.reader_settings

    bkmklt = generate_bookmarklet_code(reader_settings, request.host)

    # Force template into json response
    has_callback = request.args.get('callback', False)
    return render_template('reader_update.html', bookmarklet=bkmklt)


def reader_update_json():

    # TODO: api_host and media_host from settings
    reader_settings = current_app.config.reader_settings

    bkmklt = generate_bookmarklet_code(reader_settings, request.host)

    # Force template into json response
    has_callback = request.args.get('callback', False)
    r = render_template('reader_update.html', bookmarklet=bkmklt)

    formatted = fmtForCallback(json.dumps(r), has_callback)

    return Response(
        response=formatted, status=200, mimetype="application/json")


def fetch_messages(locale):
    from i18n.polib import pofile

    try:
        _pofile = pofile('translations/%s/LC_MESSAGES/messages.po' % locale)
    except:
        _pofile = False

    if _pofile:
        jsentries = filter(
            lambda x: any(['.js' in a[0] for a in x.occurrences]),
            list(_pofile))

        jsentries_dict = dict(
            [(e.msgid, e.msgstr or False) for e in jsentries])

    else:
        jsentries_dict = dict()
    override_symbol = current_app.config.reader_settings.get(
        'reader_symbol', False)
    if override_symbol:
        jsentries_dict[u'Á'] = override_symbol

    return jsentries_dict


def bookmarklet_configs():
    """ Compile a JSON response containing dictionary pairs,
    and internationalization strings.
    """

    from flask.ext.babel import get_locale

    NAMES = current_app.config.NAMES
    LOCALISATION_NAMES_BY_LANGUAGE = current_app.config.LOCALISATION_NAMES_BY_LANGUAGE

    has_callback = request.args.get('callback', False)
    sess_lang = request.args.get('language', get_locale())

    translated_messages = fetch_messages(sess_lang)
    print translated_messages

    dictionaries = []

    prepared = []

    pair_groups = current_app.config.pair_definitions_grouped_source_locale()

    new_group = False
    for grouper, group in pair_groups.iteritems():
        for (_from, _to), pair_options in group:
            prepared.append((_from, _to))

            reader_dict_opts = current_app.config.reader_options.get(_from, {})

            if grouper != new_group:
                group = {
                    'iso':
                    grouper,
                    'locale_name':
                    unicode(NAMES.get(grouper)),
                    'self_name':
                    unicode(LOCALISATION_NAMES_BY_LANGUAGE.get(grouper))
                }
            else:
                group = False

            new_group = grouper

            dictionaries.append({
                'from': {
                    'iso': _from,
                    'name': unicode(NAMES.get(_from))
                },
                'to': {
                    'iso': _to,
                    'name': unicode(NAMES.get(_to))
                },
                'uri': "/lookup/%s/%s/" % (_from, _to),
                'settings': reader_dict_opts,
                'group': group
            })

            _has_variant = current_app.config.pair_definitions.get((_from, _to), {}) \
                                             .get('input_variants', False)

            if _has_variant:
                for variant in _has_variant:
                    v_from = variant.get('short_name')
                    variant_dict_opts = current_app.config.reader_options.get(
                        v_from, {})
                    if not (v_from, _to) in prepared:
                        dictionaries.append({
                            'from': {
                                'iso':
                                v_from,
                                'name':
                                "%s (%s)" % (unicode(NAMES.get(_from, _from)),
                                             _(variant.get('description', '')))
                            },
                            'to': {
                                'iso': _to,
                                'name': "%s" % unicode(NAMES.get(_to))
                            },
                            'uri':
                            "/lookup/%s/%s/" % (v_from, _to),
                            'settings':
                            variant_dict_opts
                        })
                        prepared.append((v_from, _to))

    data = {
        'dictionaries': dictionaries,
        'localization': translated_messages,
        'default_language_pair': current_app.config.default_language_pair
    }

    formatted = fmtForCallback(json.dumps(data), has_callback)

    return Response(
        response=formatted, status=200, mimetype="application/json")


def bookmarklet():

    reader_settings = current_app.config.reader_settings

    bkmklt = generate_bookmarklet_code(reader_settings, request.host)

    return render_template(
        'reader.html',
        bookmarklet=bkmklt,
        language_pairs=current_app.config.pair_definitions)
