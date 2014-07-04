from . import blueprint
from flask import current_app

import sys

import simplejson

from logging import getLogger

from utils.logger import *
from utils.data import *
from utils.encoding import *

from flask import ( request
                  , Response
                  , render_template
                  , abort
                  , redirect
                  )

user_log = getLogger("user_log")

@blueprint.route('/more/', methods=['GET'])
def more_dictionaries():
    return render_template('more_dictionaries.html')

# For direct links, form submission.
@blueprint.route('/extern/<_from>/<_to>/<_search_type>/', methods=['POST'])
def externalFormSearch(_from, _to, _search_type):
    """ External searches require at least one thing, but for
    convenience, two:

    Obligatorily:

      * Some function to turn the search request into a URL, which
        returns a flask.redirect()

    This function is registered with the @lexicon.external_search
    decorator for each language pair and search shortcut:

        PAIRS = [
            ('korp_wordform', 'sme', 'nob'),
            ('korp_wordform', 'sme', fin')
        ]
        @lexicon.external_search(*PAIRS)
        def search_url(pair_details, user_input):
            from flask import redirect
            # ... do some processing ...
            return redirect(target_url)

    Optionally:

      * Redirect patterns can be stored in the dictionary config

    TODO: Templates will need a non-hardcoded means for displaying
    alternate search types. Jaska has some ideas if more examples are
    needed!

    """

    from lexicon import lexicon_overrides

    if (_from, _to) not in current_app.config.dictionaries and \
       (_from, _to) not in current_app.config.variant_dictionaries:
        abort(404)

    func = lexicon_overrides.external_search_redirect.get((_search_type, _from, _to))

    if func is None:
        abort(404)

    user_input = request.form.get('lookup')
    pair_config, _ = current_app.config.resolve_original_pair(_from, _to)

    return func(pair_config, user_input)

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

@blueprint.route('/escape/text-tv/', methods=['GET'])
def escape_tv():
    from flask import session
    del session['text_tv']
    return redirect('/')

