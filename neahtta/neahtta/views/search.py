from logging import getLogger
from functools import cached_property

from flask import (
    abort,
    current_app,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask.views import MethodView

from neahtta.i18n.utils import get_locale
from neahtta.nds_lexicon import FrontPageFormat
from neahtta.utils.logger import logIndexLookups
from neahtta.utils.flatten import list_flat

from .custom_rendering import template_rendering_overrides

user_log = getLogger("user_log")

######### TODO: this is a big todo, but, slowly refactor everything into mixins
######### and class-based views. So far the view functions here are really
######### complex as a result of being hacked together, but they need to be
######### chopped down into testable and easily comprehensible parts.

#### Next goals once this is done: simplify
#### view->search->formatting->template mess. new style templates should
#### allow for throwing a lot out.

#### * the ->formatting-> part will be solved with the new template system, which
####   will remove the need for this step.

#### * take a look at the SearchResult object and new templates, and
####   simplify the amount of context that is needed to be passed into
####   templates. SearchResult object should actually be enough.


class AppViewSettingsMixin:
    def __init__(self, *args, **kwargs):
        self.default_from, self.default_to = current_app.config.default_language_pair
        self.default_pair_settings = current_app.config.pair_definitions[
            (self.default_from, self.default_to)
        ]
        super().__init__(*args, **kwargs)


class DictionaryView(MethodView):
    def entry_filterer(self, x):
        return x

    def validate_request(self, x):
        return True

    @staticmethod
    def tagsets_serializer_ready(lang):
        """Make the tagsets ready for serialization."""
        _tagsets = current_app.config.morphologies.get(lang).tagsets.sets

        return {
            key: [m.val for m in tagset.members] for key, tagset in _tagsets.items()
        }

    def post_search_context_modification(self, search_result, context):
        """Perform any additional alterations to the context generated
        from the search before it is rendered."""
        return context

    def get_shared_context(self, _from, _to, *args, **kwargs):
        """Return some things that are in all templates. Additional
        kwargs passed here will end up in the context passsed to
        templates."""

        (
            current_pair_settings,
            orig_pair_opts,
        ) = current_app.config.resolve_original_pair(_from, _to)

        o_pair = orig_pair_opts.get("orig_pair")
        if orig_pair_opts.get("orig_pair") != ():
            orig_from, orig_to = o_pair
        else:
            orig_from, orig_to = _from, _to

        current_search_variant = False

        if "search_variant_type" in kwargs:
            variant_type = kwargs["search_variant_type"]
            variants = [
                variant
                for variant in current_pair_settings.get("search_variants")
                if variant.get("type") == variant_type
            ]
            if variants:
                current_search_variant = variants[0]

        shared_context = {
            "display_swap": self.get_reverse_pair(_from, _to),
            "current_pair_settings": current_pair_settings,
            "current_variant_options": orig_pair_opts.get("variant_options"),
            "current_search_variant": current_search_variant,
            "current_locale": get_locale(),
            "_from": _from,
            "_to": _to,
            "orig_from": orig_from,
            "orig_to": orig_to,
            "last_searches": session.get(
                "last_searches-" + current_app.config.short_name, []
            ),
        }

        shared_context.update(**kwargs)

        # Render some additional templates
        search_info = current_app.lexicon_templates.render_individual_template(
            _from, "search_info.template", **shared_context
        )
        search_form = current_app.lexicon_templates.render_individual_template(
            _from, "index_search_form.template", **shared_context
        )
        shared_context["search_info_template"] = search_info
        shared_context["index_search_form"] = search_form

        shared_context.update(**orig_pair_opts)
        return shared_context

    def get_lemma_lookup_args(self):
        lemma_lookup_args = {}
        for key, value in request.args.items():
            if key in self.accepted_lemma_args:
                lemma_lookup_args[self.accepted_lemma_args.get(key)] = value
        return lemma_lookup_args

    @staticmethod
    def check_pair_exists_or_abort(_from, _to):
        pair = (_from, _to)
        dictionaries = current_app.config.dictionaries
        variant_dictionaries = current_app.config.variant_dictionaries
        if (pair not in dictionaries) and (pair not in variant_dictionaries):
            abort(404)

    @staticmethod
    def force_locale(_from, _to):
        from flask_babel import refresh

        _, orig_pair_opts = current_app.config.resolve_original_pair(_from, _to)

        opts = orig_pair_opts.get("variant_options")

        current_locale = get_locale()

        if opts and ("force_locale" in opts):
            layout_forces = opts.get("force_locale", {})

            if current_locale in layout_forces:
                session["force_locale"] = session["locale"] = layout_forces[
                    current_locale
                ]
                # Refresh the localization infos, and send the user back
                # whence they came.
                refresh()
            else:
                try:
                    del session["force_locale"]
                except KeyError:
                    pass

        return False

    @staticmethod
    def get_reverse_pair(_from, _to):
        """If the reverse pair for (_from, _to) exists, return the
        pair's settings, otherwise False."""

        # TODO: move this to config object.

        _, orig_pair_opts = current_app.config.resolve_original_pair(_from, _to)
        _r_from, _r_to = orig_pair_opts.get("swap_from"), orig_pair_opts.get("swap_to")
        reverse_exists = current_app.config.dictionaries.get((_r_from, _r_to), False)

        return reverse_exists


class IndexSearchPage(DictionaryView, AppViewSettingsMixin):
    """A simple view to handle potential mobile redirects to a default
    language pair specified only for mobile.
    """

    template_name = "index.html"

    @staticmethod
    def maybe_do_mobile_redirect():
        """If this is a mobile platform, redirect; otherwise return
        None/do no action.
        """

        mobile_redirect_pair = current_app.config.mobile_redirect_pair

        if mobile_redirect_pair:
            from_lang, to_lang = tuple(mobile_redirect_pair)
            target_url = url_for(
                "views.canonical_root_search_pair", _from=from_lang, _to=to_lang
            )
            if request.user_agent.platform in ["iphone", "android"]:
                # Only redirect if the user isn't coming back to the home page
                # from somewhere within the app.
                if request.referrer and request.host:
                    if request.host not in request.referrer:
                        return redirect(target_url)
                else:
                    return redirect(target_url)

        return False

    def dispatch_request(self):
        redir = self.maybe_do_mobile_redirect()
        if redir:
            return redir

        reverse_exists = current_app.config.dictionaries.get(
            (self.default_to, self.default_from), False
        )

        (
            current_pair_settings,
            orig_pair_opts,
        ) = current_app.config.resolve_original_pair(self.default_from, self.default_to)
        template_context = self.get_shared_context(self.default_from, self.default_to)

        o_pair = orig_pair_opts.get("orig_pair")
        if orig_pair_opts.get("orig_pair") != ():
            orig_from, orig_to = o_pair
        else:
            orig_from, orig_to = self.default_from, self.default_to

        template_context.update(
            {
                "display_swap": reverse_exists,
                "swap_from": self.default_to,
                "swap_to": self.default_from,
                "show_info": True,
                "current_pair_settings": current_pair_settings,
                "current_variant_options": orig_pair_opts.get("variant_options"),
                "current_locale": get_locale(),
                "_from": self.default_from,
                "_to": self.default_to,
                "orig_from": orig_from,
                "orig_to": orig_to,
            }
        )

        return render_template(self.template_name, **template_context)


def entry_sorter_key(d):
    return d["lemma"]


class SearchResult:
    """This object is the lexicon lookup search result. It mostly
    provides readability conveniences.

        self.entries_and_tags
        self.analyses
        self.analyses_without_lex
        self.formatted_results
        self.successful_entry_exists
    """

    def __init__(
        self,
        _from,
        _to,
        user_input,
        entries_and_tags,
        formatter,
        generate,
        sorter=entry_sorter_key,
        filterer=None,
        debug_text=False,
        other_counts={},
    ):
        self.user_input = user_input
        self.search_term = user_input
        self.entries_and_tags = entries_and_tags
        # When to display unknowns
        self.successful_entry_exists = False
        self._from = _from
        self._to = _to
        self.formatter = formatter
        self.generate = generate
        self.debug_text = debug_text
        self.other_results = other_counts
        self.entry_sorter_key = sorter

        if filterer is not None:
            self.entry_filterer = filterer

        self.analyses = [
            (lem.input, lem.lemma, list(lem.tag)) for lem in entries_and_tags.analyses
        ]

        if self.formatted_results:
            self.successful_entry_exists = True

    @property
    def formatted_results_sorted(self):
        """Formatted results sorted by entry_sorter_key"""
        return self.formatted_results
        return sorted(self.formatted_results, key=self.entry_sorter_key)

    def generate_paradigm(self, node, morph_analyses):
        from neahtta.morpholex import MorphoLexicon

        try:
            morph = current_app.config.morphologies[g._from]
        except KeyError:
            # the config is checked when starting up, so this should never
            # happen
            print(f"no morphology found for language {g._from}")
            return []

        mlex: MorphoLexicon = current_app.morpholexicon

        lemma_elt = node.xpath("./lg/l")[0]
        lemma = lemma_elt.xpath("string(normalize-space(./text()))")

        # anders: for gåetie, there were more analyses, and the first one was
        # correct, but then it included many Lemmas which were for the
        # Capitalized version of the word, Gåetie (which is a different word,
        # and a proper noun). This somehow caused the the other ones to be
        # "mixed" into this one, and lead to finding no paradigms
        # hence why this hack is here (hopefully not too long)
        if morph_analyses:
            morph_analyses = [morph_analyses[0]]

        paradigm_from_file, paradigm_template = mlex.paradigms.get_paradigm(
            g._from, node, morph_analyses, return_template=True
        )
        if paradigm_from_file:
            extra_log_info = {
                "template_path": paradigm_template,
            }

            generated, stdout, _ = morph.generate_to_objs(
                lemma,
                paradigm_from_file,
                node,
                extra_log_info=extra_log_info,
                no_preprocess_paradigm=True,
            )
        else:
            # For pregenerated things
            generated, stdout, _ = morph.generate_to_objs(lemma, [], node)
        self.debug_text += "\n\n" + stdout + "\n\n"

        return generated

    @cached_property
    def formatted_results(self):
        results = []

        fmtkwargs = {
            "target_lang": self._to,
            "source_lang": self._from,
            "ui_lang": g.ui_lang,
            "user_input": self.user_input,
        }

        # Formatting of this stuff should be moved somewhere more reasonable
        for result, morph_analyses in self.entries_and_tags:
            if result is not None:
                _formatted = self.formatter(
                    [result],
                    additional_template_kwargs={"analyses": morph_analyses},
                    **fmtkwargs,
                )

                if self.entry_filterer:
                    _formatted = self.entry_filterer(_formatted)

                results.extend(_formatted)

        return results

    @cached_property
    def entries(self):
        return [entry for entry, _tags in self.entries_and_tags]

    def sort_entries_and_tags_and_paradigm(
        self, unsorted_entries_and_tags_and_paradigms
    ):
        try:
            key = (g._from, g._to)
            sorter = template_rendering_overrides.sort_entry_list_display[key]
        except KeyError:
            return unsorted_entries_and_tags_and_paradigms
        else:
            return sorter(self, unsorted_entries_and_tags_and_paradigms)

    @cached_property
    def entries_and_tags_and_paradigms(self):
        etp = []

        # Formatting of this stuff should be moved somewhere more reasonable
        for result, morph_analyses in self.entries_and_tags:
            if result is None:
                continue
            has_layout = False

            if self.generate:
                paradigm = self.generate_paradigm(result, morph_analyses)

                if current_app.config.paradigm_layouts and paradigm:
                    layouts = current_app.morpholexicon.paradigms.get_paradigm_layout(
                        g._from,
                        result,
                        morph_analyses,
                        return_template=True,
                        multiple=True,
                    )

                    if layouts:
                        has_layout = [
                            L.for_paradigm(paradigm).fill_generation()
                            for (L, _) in layouts
                            if L
                        ]
                        if not has_layout:
                            has_layout = False
            else:
                paradigm = []

            etp.append((result, morph_analyses, paradigm, has_layout))

        return self.sort_entries_and_tags_and_paradigm(etp)

    @cached_property
    def analyses_without_lex(self):
        results = []
        for entry, analyses in self.entries_and_tags:
            if entry is None:
                results.extend(analyses)
        return results


class SearcherMixin:
    """This mixin provides common methods for performing the search,
    and returning view-ready results."""

    entr_r = []

    def do_search_to_obj(self, lookup_value, **kwargs) -> SearchResult:
        search_kwargs = {
            "split_compounds": kwargs.get("split_compounds", True),
            "non_compounds_only": kwargs.get("non_compounds_only", False),
            "no_derivations": kwargs.get("no_derivations", False),
            "lemma_attrs": kwargs.get("lemma_attrs", {}),
        }

        mlex = current_app.morpholexicon
        variant_type = kwargs.get("variant_type", False)
        if variant_type:
            entries_and_tags, stdout, stderr = mlex.variant_lookup(
                variant_type,
                lookup_value,
                source_lang=g._from,
                target_lang=g._to,
                **search_kwargs,
            )
        else:
            entries_and_tags, stdout, stderr = mlex.lookup(
                lookup_value, source_lang=g._from, target_lang=g._to, **search_kwargs
            )

        return SearchResult(
            g._from,
            g._to,
            lookup_value,
            entries_and_tags,
            self.formatter,
            generate=kwargs.get("generate"),
            filterer=self.entry_filterer,
            debug_text=f"{stdout}\n--\n{stderr}",
            other_counts={},
        )

    # anders: unused
    def search_to_detailed_context(self, lookup_value, **search_kwargs):
        assert False, "unused function"

    # def search_to_detailed_context(self, lookup_value, **search_kwargs):
    #     # TODO: There's a big mess contained here, and part of it
    #     # relates to lexicon formatters. Slowly working on unravelling
    #     # it.

    #     # TODO: this can probably be generalized to be part of the last
    #     # function.

    #     errors = False

    #     search_result_obj = self.do_search_to_obj(
    #         lookup_value, generate=True, **search_kwargs
    #     )

    #     template_results = [
    #         {
    #             "input": search_result_obj.search_term,
    #             "lookups": search_result_obj.formatted_results_sorted,
    #             # 'analyses': search_result_obj.analyses
    #         }
    #     ]

    #     logIndexLookups(
    #         search_result_obj.search_term,
    #         template_results,
    #         g._from,
    #         g._to,
    #     )

    #     show_info = False

    #     # Here analyses_right related to the same variable in morphology.py
    #     search_context = {
    #         "result": search_result_obj.formatted_results_sorted,
    #         # These variables can be turned into something more general
    #         "successful_entry_exists": search_result_obj.successful_entry_exists,
    #         "word_searches": template_results,
    #         "analyses": search_result_obj.analyses,
    #         "analyses_right": search_result_obj.analyses,
    #         "analyses_without_lex": search_result_obj.analyses_without_lex,
    #         "user_input": search_result_obj.search_term,
    #         "current_locale": get_locale(),
    #         "errors": errors,  # is this actually getting set?
    #         "show_info": show_info,
    #         "language_pairs_other_results": search_result_obj.other_results,
    #         "debug_text": search_result_obj.debug_text,
    #     }

    #    return search_context

    def search_to_context(self, lookup_value, detailed=False, **default_context_kwargs):
        """Note: new-style templates require similar input
        across Detail/main page view, so can really refactor and
        chop stuff down."""
        current_pair, _ = current_app.config.resolve_original_pair(g._from, g._to)
        async_paradigm = current_pair.get("asynchronous_paradigms", False)
        lemma_attrs = default_context_kwargs.get("lemma_attrs", {})
        generate = detailed and not async_paradigm

        if "variant_type" in default_context_kwargs:
            variant_type = default_context_kwargs.get("variant_type")
            search_result: SearchResult = self.do_search_to_obj(
                lookup_value,
                generate=generate,
                lemma_attrs=lemma_attrs,
                variant_type=variant_type,
            )
        else:
            search_result: SearchResult = self.do_search_to_obj(
                lookup_value, generate=generate, lemma_attrs=lemma_attrs
            )

        template = "detail_entry.template" if detailed else "entry.template"

        _rendered_entry_templates = []

        template_results = [
            {
                "input": search_result.search_term,
                "lookups": search_result.formatted_results_sorted,
            }
        ]

        logIndexLookups(search_result.search_term, template_results, g._from, g._to)

        show_info = False

        k = 0
        res_par = []
        if_none = False
        if_next_der = False
        tags = ("Der", "VAbess", "VGen", "Ger", "Comp", "Superl")

        fmtkwargs = {
            "target_lang": g._to,
            "source_lang": g._from,
            "ui_lang": g.ui_lang,
            "user_input": lookup_value,
        }

        # anders: update: This causes words that are not lexicalized to
        # disappear, because it filters based on a lemma match from the
        # dictionary! Therefore, temporarily disabled

        # anders: hack to get lemma_match respected.
        # this is the same code as in formatted_results(), which _does_ do
        # entry filtering based on lemma_match. So we run the same filter
        # here, and update `entries_and_tags` accordingly (discarding the
        # actual "results" from the filtering)

        # entries_and_tags = []
        # for item in search_result.entries_and_tags:
        #     # same code as formatted_results()
        #     if item[0] is not None:
        #         _formatted = self.formatter(
        #             [item[0]],
        #             additional_template_kwargs={"analyses": item[1]},
        #             **fmtkwargs,
        #         )
        #         if self.entry_filterer:
        #             _filtered = self.entry_filterer(_formatted)
        #             if _filtered:
        #                 entries_and_tags.append(item)

        # If in the results there is a 'None' entry followed by der tag/s those are removed
        # and are not shown in the results (e.g. "bagoheapmi")
        for item in search_result.entries_and_tags:
            dict_entry, analyses = item
            if analyses:
                if if_none and analyses[0].lemma.startswith(tags):
                    if_next_der = True
                if dict_entry is not None and not analyses[0].lemma.startswith(tags):
                    if_next_der = False
                if dict_entry is not None and not if_next_der:
                    res_par.append(item)
                    if_none = False
                else:
                    if_none = True
            else:
                res_par.append(item)

        etp = search_result.entries_and_tags_and_paradigms
        for _dict_entry, analyses, paradigm, has_layout in etp:
            # anders:
            # this "picks" res_par[k] instead of going in the order of `etp` !
            # which in turn gets its order directly from entries_and_tags,
            # which is the order that we get from the analyser
            if k < len(res_par):
                if res_par[k][0] is not None:
                    if not analyses:
                        analyses = "az"

                    tplkwargs = {
                        "lexicon_entry": res_par[k][0],
                        "analyses": analyses,
                        "analyses_right": res_par[k][1],
                        "korp_hits": 1,  # we assume it exists
                        "paradigm": paradigm,
                        "layout": has_layout,
                        "user_input": search_result.search_term,
                        "word_searches": template_results,
                        "errors": False,
                        "show_info": show_info,
                        "successful_entry_exists": search_result.successful_entry_exists,
                    }

                    tplkwargs.update(**default_context_kwargs)

                    # Process all the context processors
                    current_app.update_template_context(tplkwargs)

                    _rendered_entry_templates.append(
                        current_app.lexicon_templates.render_template(
                            g._from, template, **tplkwargs
                        )
                    )
                k += 1

        all_analyses = list_flat(
            analyses for _, analyses in search_result.entries_and_tags
        )

        indiv_template_kwargs = {
            "analyses": all_analyses,
            "analyses_right": all_analyses,
            "korp_hits": 1,
        }
        indiv_template_kwargs.update(**default_context_kwargs)

        # Process all the context processors
        current_app.update_template_context(indiv_template_kwargs)

        all_analysis_template = (
            current_app.lexicon_templates.render_individual_template(
                g._from, "analyses.template", **indiv_template_kwargs
            )
        )

        header_template = current_app.lexicon_templates.render_individual_template(
            g._from, "includes.template", **indiv_template_kwargs
        )

        if search_result.analyses_without_lex:
            leftover_tpl_kwargs = {
                "analyses": search_result.analyses_without_lex,
                "analyses_right": search_result.analyses_without_lex,
                "korp_hits": 1,
            }
            leftover_tpl_kwargs.update(**default_context_kwargs)
            # Process all the context processors
            current_app.update_template_context(leftover_tpl_kwargs)

            leftover_analyses_template = (
                current_app.lexicon_templates.render_individual_template(
                    g._from, "analyses.template", **leftover_tpl_kwargs
                )
            )
        else:
            leftover_analyses_template = False

        find_problem = current_app.lexicon_templates.render_individual_template(
            g._from, "find_problem.template", **indiv_template_kwargs
        )

        search_context = {
            # This is the new style stuff.
            "entry_templates": _rendered_entry_templates,
            "entry_template_header_includes": header_template,
            "leftover_analyses_template": leftover_analyses_template,
            "all_analysis_template": all_analysis_template,
            "find_problem": find_problem,
            # These variables can be turned into something more general
            "successful_entry_exists": search_result.successful_entry_exists,
            "word_searches": template_results,
            "analyses": search_result.analyses,
            "analyses_right": search_result.analyses,
            "analyses_without_lex": search_result.analyses_without_lex,
            "user_input": search_result.search_term,
            "last_searches": session.get(
                "last_searches-" + current_app.config.short_name, []
            ),
            "errors": False,  # where should we expect errors?
            "language_pairs_other_results": search_result.other_results,
            "debug_text": search_result.debug_text,
        }

        search_context.update(**default_context_kwargs)

        return self.post_search_context_modification(search_result, search_context)


class LanguagePairSearchView(DictionaryView, SearcherMixin):
    """Handles the /<from>/<to>/[?lookup=<lookup>] route."""

    methods = ["GET", "POST"]
    template_name = "index.html"
    formatter = FrontPageFormat

    @staticmethod
    def log_in_session(user_input):
        uri = "%s://%s%s?lookup=%s" % (
            request.scheme,
            request.host,
            request.path,
            user_input,
        )

        last_search_key = "last_searches-" + current_app.config.short_name
        if last_search_key in session:
            if (uri, user_input) not in session[last_search_key]:
                session[last_search_key].insert(0, (uri, user_input))
                if len(session[last_search_key]) > 3:
                    session[last_search_key] = session[last_search_key][0:3]
        else:
            session[last_search_key] = [(uri, user_input)]

    def get(self, _from, _to):
        self.check_pair_exists_or_abort(_from, _to)
        self.force_locale(_from, _to)

        # If the view is for an input variant, we need the original
        # pair:

        default_context = {
            # These variables are produced from a search.
            "successful_entry_exists": False,
            "word_searches": False,
            "analyses": False,
            "analyses_right": False,
            "analyses_without_lex": False,
            "user_input": False,
            "errors": False,  # is this actually getting set?
            # Show the default info under search box
            "show_info": True,
        }

        try:
            user_input = request.args["lookup"]
        except KeyError:
            default_context.update(**self.get_shared_context(_from, _to))
            return render_template(self.template_name, **default_context)

        user_input = user_input.strip()

        # This performs lots of the work...
        search_result_context = self.search_to_context(
            user_input, **self.get_shared_context(_from, _to)
        )

        self.log_in_session(user_input)

        # missing current_pair_settings
        return render_template(self.template_name, **search_result_context)

    def post(self, _from, _to):
        self.check_pair_exists_or_abort(_from, _to)
        self.force_locale(_from, _to)

        user_input = request.form.get("lookup", "")
        user_input = user_input.strip()

        if user_input in ["teksti-tv", "tekst tv", "teaksta tv"]:
            session["text_tv"] = True

        self.log_in_session(user_input)

        # This performs lots of the work...
        search_result_context = self.search_to_context(
            user_input, **self.get_shared_context(_from, _to)
        )

        # missing current_pair_settings
        return render_template(self.template_name, **search_result_context)


class ReferredLanguagePairSearchView(LanguagePairSearchView):
    """This overrides some functionality in order to provide the
    /lang/lang/ref/ functionality.
    """

    accepted_lemma_args = {
        "l_til_ref": "til_ref",
        "e_node": "entry_hash",
    }

    # TODO: NST removal
    def get(self, _from, _to):
        self.check_pair_exists_or_abort(_from, _to)

        user_input = request.form.get("lookup", "")
        user_input = user_input.strip()

        lookup_context = self.get_shared_context(_from, _to)
        lookup_context["lemma_attrs"] = self.get_lemma_lookup_args()

        # This performs lots of the work...
        search_result_context = self.search_to_context(user_input, **lookup_context)

        # missing current_pair_settings
        return render_template(self.template_name, **search_result_context)


class DetailedLanguagePairSearchView(DictionaryView, SearcherMixin):
    """The major difference between this view and the main index search
    is that this view also accepts some parameters for filtering
    entries, because it corresponds to links followed from the main page
    search results.

    .. http:get::
              /detail/(string:from)/(string:to)/(string:wordform).(string:fmt)

        Look up up a query in the lexicon (including lemmatizing input,
        and the lexicon against the input sans lemmatization), returning
        translation information, word analyses, and sample paradigms for
        words and tags which support it.

        :samp:`/detail/sme/nob/orrut.html`
        :samp:`/detail/sme/nob/orrut.json`

        Here are the basic parameters required for a result.

        :param from: the source language
        :param to: the target language
        :param wordform:
            the wordform to be analyzed. If in doubt, encode and escape
            the string into UTF-8, and URL encode it. Some browser do
            this automatically and present the URL in a user-readable
            format, but mostly, the app does not seem to care.
        :param format:
            the data format to return the result in. `json` and `html`
            are currently accepted.

        Then there are the optional parameters...

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

    from neahtta.nds_lexicon import DetailedFormat as formatter

    accepted_lemma_args = {
        "e_node": "entry_hash",
    }

    methods = ["GET"]

    @property
    def template_name(self):
        if "embedded" in request.args:
            return "word_detail_embedded.html"
        return "word_detail.html"

    def entry_filterer(self, entries):
        """Runs on formatted result from DetailedFormat."""
        # anders: entries is a neahtta.nds_lexicon.DetailedFormat,
        # which inherits from EntryNodeIterator, which is an iterator
        # that calls self.clean() on every element of self.nodes.
        # DetailedFormat.clean() returns a dictionary, so in this function,
        # entries is essentially an iterator over dictionaries.
        # see line 507 in nds_lexicon/formatters.py

        # Post-analysis filter arguments, defined in query parameters
        pos_filter = request.args.get("pos_filter")
        lemma_match = request.args.get("lemma_match")
        e_node = request.args.get("e_node")

        entries = iter(entries)
        if e_node:
            entries = filter(lambda d: d["entry_hash"] == e_node, entries)
        if pos_filter:
            pos_up = pos_filter.upper()
            entries = filter(lambda d: d["pos"].upper() == pos_up, entries)
        if lemma_match:
            entries = filter(lambda d: d["lemma"] == self.user_input, entries)

        return list(entries)

    def get(self, _from, _to, wordform, format):
        self.check_pair_exists_or_abort(_from, _to)
        self.user_input = wordform.strip()
        no_compounds = request.args.get("no_compounds", False)
        lemma_match = request.args.get("lemma_match", False)
        e_node = request.args.get("e_node", False)

        search_kwargs = {
            "split_compounds": True,
            "non_compounds_only": no_compounds,
            "no_derivations": False,
        }

        search_kwargs["lemma_attrs"] = self.get_lemma_lookup_args()

        search_result_context = self.search_to_context(
            self.user_input, detailed=True, **search_kwargs
        )

        has_analyses = search_result_context.get("successful_entry_exists", False)
        want_more_detail = no_compounds or lemma_match or e_node

        search_result_context["has_analyses"] = has_analyses
        search_result_context["more_detail_link"] = want_more_detail

        return render_template(self.template_name, **search_result_context)
