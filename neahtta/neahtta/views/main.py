from logging import getLogger

from flask import (
    abort,
    current_app,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

user_log = getLogger("user_log")


def more_dictionaries():
    return render_template("more_dictionaries.html")


# For direct links, form submission.
def externalFormSearch(_from, _to, _search_type):
    """External searches require at least one thing, but for
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

    """

    from nds_lexicon import lexicon_overrides

    if (_from, _to) not in current_app.config.dictionaries and (
        _from,
        _to,
    ) not in current_app.config.variant_dictionaries:
        abort(404)

    func = lexicon_overrides.external_search_redirect.get((_search_type, _from, _to))

    if func is None:
        abort(404)

    user_input = request.form.get("lookup")
    if user_input is None:
        # anders: after using only GET for lookups to prevent
        # the dreaded 'expired document' after searching, we now
        # also have to check the query params
        user_input = request.args.get("lookup")
    pair_config, _ = current_app.config.resolve_original_pair(_from, _to)

    return func(pair_config, user_input)


def about():
    return render_template("about.template")


def about_sources():
    """This is also tied to a context processer making this item
    visible in the navigational menu if the template is found."""
    _from, _to = current_app.config.default_language_pair

    try:
        return render_template("sources.template")
    # anders: what are we catching here?
    except Exception:
        return render_template("about.template")


def gen_doc(from_language, docs_list):
    _docs = []
    for lx, fxs in docs_list.items():
        if lx != from_language:
            continue

        keys = ("name", "doc")
        functions = [(fx, d.strip()) for fx, d in fxs]

        functions = [dict(zip(keys, d)) for d in functions]

        # TODO: find decorated function doc
        doc = {
            "name": lx,
            "main_doc": "TODO",  #  mod.__doc__,
            "functions": functions,
        }

        _docs.append(doc)
    return _docs


def config_docs():
    config = current_app.config
    languages = []

    # TODO: gen doc for project level

    return render_template(
        "config_docs.html", languages=languages, config=config, app=current_app
    )


def config_doc(from_language):
    """Quick overview of language-specific details."""
    from morphology import generation_overrides

    generation_docs = gen_doc(from_language, generation_overrides.tag_filter_doc)
    pregen_doc = gen_doc(from_language, generation_overrides.pregenerators_doc)
    postanalysis_doc = gen_doc(from_language, generation_overrides.postanalyzers_doc)
    postgen_doc = gen_doc(
        from_language, generation_overrides.postgeneration_processors_doc
    )

    # TODO: lexicon overrides
    # TODO: morpholexicon overrides

    # TODO: filter paradigms, tag_filters

    paradigms = current_app.config.paradigms.get(from_language, {})
    mparadigms = current_app.morpholexicon.paradigms.paradigm_rules.get(
        from_language, []
    )

    tag_transforms = current_app.config.tag_filters
    languages = []

    return render_template(
        "config_doc.html",
        app=current_app,
        generation_docs=generation_docs,
        pregen_doc=pregen_doc,
        postanalysis_doc=postanalysis_doc,
        postgen_doc=postgen_doc,
        paradigms=paradigms,
        mparadigms=mparadigms,
        tag_transforms=tag_transforms,
        languages=languages,
        lang_name=from_language,
    )


def escape_tv():
    """Delete text_tv key in session cookie if it exists"""
    try:
        del session["text_tv"]
    except KeyError:
        pass
    return redirect(url_for("views.canonical-root"))


allowed_keys = [
    "last_searches",
]


def session_clear(sess_key):
    if sess_key in allowed_keys:
        if sess_key == "last_searches":
            sess_key += "-" + current_app.config.short_name

        try:
            del session[sess_key]
        except KeyError:
            pass
    return redirect(url_for("views.canonical-root"))
