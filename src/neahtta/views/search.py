# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from logging import getLogger
import sys

from flask import (abort, current_app, g, redirect, render_template,
                   request, session, url_for)
from flask_babel import gettext as _
from flask.views import MethodView
import json
try:
    from urllib import urlopen
except ImportError: # py3
    from urllib.request import urlopen
try:
    from urllib import quote
except ImportError: # py3
    from urllib.parse import quote

from urllib.error import HTTPError

from i18n.utils import get_locale
from nds_lexicon import FrontPageFormat
from utils.encoding import decode_or_fail
from utils.logger import logIndexLookups
from six import iteritems

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


class AppViewSettingsMixin(object):
    def __init__(self, *args, **kwargs):

        # Apply some default values for the present application

        self.default_from, self.default_to = current_app.config.default_language_pair
        self.default_pair_settings = current_app.config.pair_definitions[(
            self.default_from, self.default_to)]
        super(AppViewSettingsMixin, self).__init__(*args, **kwargs)


class DictionaryView(MethodView):

    entry_filterer = lambda self, x: x

    validate_request = lambda self, x: True

    @staticmethod
    def tagsets_serializer_ready(lang):
        """Make the tagsets ready for serialization."""
        _tagsets = current_app.config.morphologies.get(lang).tagsets.sets

        return {
            key: [m.val for m in tagset.members]
            for key, tagset in iteritems(_tagsets)
        }

    def post_search_context_modification(self, search_result, context):
        """ Perform any additional alterations to the context generated
        from the search before it is rendered.  """
        return context

    def get_shared_context(self, _from, _to, *args, **kwargs):
        """ Return some things that are in all templates. Additional
        kwargs passed here will end up in the context passsed to
        templates. """

        current_pair_settings, orig_pair_opts = current_app.config.resolve_original_pair(
            _from, _to)

        o_pair = orig_pair_opts.get('orig_pair')
        if orig_pair_opts.get('orig_pair') != ():
            orig_from, orig_to = o_pair
        else:
            orig_from, orig_to = _from, _to

        current_search_variant = False

        if 'search_variant_type' in kwargs:
            variant_type = kwargs['search_variant_type']
            variants = [
                variant for variant in current_pair_settings.get('search_variants')
                if variant.get('type') == variant_type
            ]
            if variants:
                current_search_variant = variants[0]

        shared_context = {
            'display_swap':
            self.get_reverse_pair(_from, _to),
            'current_pair_settings':
            current_pair_settings,
            'current_variant_options':
            orig_pair_opts.get('variant_options'),
            'current_search_variant':
            current_search_variant,
            'current_locale':
            get_locale(),
            '_from':
            _from,
            '_to':
            _to,
            'orig_from':
            orig_from,
            'orig_to':
            orig_to,
            'last_searches':
            session.get('last_searches-' + current_app.config.short_name, []),
        }

        shared_context.update(**kwargs)

        # Render some additional templates
        search_info = current_app.lexicon_templates.render_individual_template(
            _from, 'search_info.template', **shared_context)
        search_form = current_app.lexicon_templates.render_individual_template(
            _from, 'index_search_form.template', **shared_context)
        shared_context['search_info_template'] = search_info
        shared_context['index_search_form'] = search_form

        shared_context.update(**orig_pair_opts)
        return shared_context

    def get_lemma_lookup_args(self):
        lemma_lookup_args = {}
        for key, value in iteritems(request.args):
            if key in self.accepted_lemma_args:
                lemma_lookup_args[self.accepted_lemma_args.get(key)] = value
        return lemma_lookup_args

    @staticmethod
    def check_pair_exists_or_abort(_from, _to):

        if (_from, _to) not in current_app.config.dictionaries and \
           (_from, _to) not in current_app.config.variant_dictionaries:
            abort(404)

        return False

    @staticmethod
    def force_locale(_from, _to):

        from flask_babel import refresh

        _, orig_pair_opts = current_app.config.resolve_original_pair(
            _from, _to)

        opts = orig_pair_opts.get('variant_options')

        current_locale = get_locale()

        if opts and ('force_locale' in opts):
            layout_forces = opts.get('force_locale', {})

            if current_locale in layout_forces:
                session['force_locale'] = session['locale'] = layout_forces[
                    current_locale]
                # Refresh the localization infos, and send the user back whence they
                # came.
                refresh()
            else:
                try:
                    del session['force_locale']
                except:
                    pass

        return False

    @staticmethod
    def get_reverse_pair(_from, _to):
        """ If the reverse pair for (_from, _to) exists, return the
        pair's settings, otherwise False. """

        # TODO: move this to config object.

        _, orig_pair_opts = current_app.config.resolve_original_pair(
            _from, _to)
        _r_from, _r_to = orig_pair_opts.get('swap_from'), orig_pair_opts.get(
            'swap_to')
        reverse_exists = current_app.config.dictionaries.get((_r_from, _r_to),
                                                             False)

        return reverse_exists


class IndexSearchPage(DictionaryView, AppViewSettingsMixin):
    """ A simple view to handle potential mobile redirects to a default
    language pair specified only for mobile.
    """

    template_name = 'index.html'

    @staticmethod
    def maybe_do_mobile_redirect():
        """ If this is a mobile platform, redirect; otherwise return
        None/do no action.
        """

        mobile_redirect_pair = current_app.config.mobile_redirect_pair

        if mobile_redirect_pair:
            from_lang, to_lang = tuple(mobile_redirect_pair)
            target_url = url_for(
                'views.canonical_root_search_pair', _from=from_lang, _to=to_lang)
            if request.user_agent.platform in ['iphone', 'android']:
                # Only redirect if the user isn't coming back to the home page
                # from somewhere within the app.
                if request.referrer and request.host:
                    if not request.host in request.referrer:
                        return redirect(target_url)
                else:
                    return redirect(target_url)

        return False

    def dispatch_request(self):

        redir = self.maybe_do_mobile_redirect()
        if redir:
            return redir

        reverse_exists = \
            current_app.config.dictionaries.get(
                (self.default_to, self.default_from), False)

        current_pair_settings, orig_pair_opts = current_app.config.resolve_original_pair(
            self.default_from, self.default_to)
        template_context = self.get_shared_context(self.default_from,
                                                   self.default_to)

        o_pair = orig_pair_opts.get('orig_pair')
        if orig_pair_opts.get('orig_pair') != ():
            orig_from, orig_to = o_pair
        else:
            orig_from, orig_to = self.default_from, self.default_to

        template_context.update({
            'display_swap':
            reverse_exists,
            'swap_from':
            self.default_to,
            'swap_to':
            self.default_from,
            'show_info':
            True,
            'current_pair_settings':
            current_pair_settings,
            'current_variant_options':
            orig_pair_opts.get('variant_options'),
            'current_locale':
            get_locale(),
            '_from':
            self.default_from,
            '_to':
            self.default_to,
            'orig_from':
            orig_from,
            'orig_to':
            orig_to,
        })

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

    def entry_sorter_key(self, req):
        return req.get('left')

    @property
    def formatted_results_sorted(self):
        """ Formatted results sorted by entry_sorter_key
        """
        return sorted(self.formatted_results, key=self.entry_sorter_key)

    @property
    def formatted_results_pickleable(self):
        # TODO: implement
        def pickleable_result(results):
            """ Pop the various keys that need to be removed.
            """
            pickleable = []
            for result in [result.copy() for result in results]:
                result.pop('node')
                analyses = []
                for ana in result.get('analyses', []):
                    # TODO: tag formatter
                    analyses.append((ana.lemma, ana.tag.tag_string))
                result['analyses'] = analyses
                pickleable.append(result)
            return pickleable

        pickle_result = pickleable_result(self.formatted_results_sorted)

        return pickle_result

    def generate_paradigm(self, node, morph_analyses):
        _str_norm = 'string(normalize-space(%s))'

        morph = current_app.config.morphologies.get(g._from, False)
        mlex = current_app.morpholexicon

        lemma_elt = node.xpath('./lg/l')[0]
        lemma = lemma_elt.xpath(_str_norm % './text()')

        paradigm_from_file, paradigm_template = mlex.paradigms.get_paradigm(
            g._from, node, morph_analyses, return_template=True)
        if paradigm_from_file:
            extra_log_info = {
                'template_path': paradigm_template,
            }

            generated, stdout, _ = morph.generate_to_objs(
                lemma,
                paradigm_from_file,
                node,
                extra_log_info=extra_log_info,
                return_raw_data=True,
                no_preprocess_paradigm=True)
        else:
            # For pregenerated things
            generated, stdout, _ = morph.generate_to_objs(
                lemma, [], node, return_raw_data=True)
        self.debug_text += '\n\n' + stdout + '\n\n'

        return generated

    @property
    def formatted_results(self):
        if hasattr(self, '_formatted_results'):
            return self._formatted_results

        self._formatted_results = []

        fmtkwargs = {
            'target_lang': self._to,
            'source_lang': self._from,
            'ui_lang': g.ui_lang,
            'user_input': self.user_input
        }

        # Formatting of this stuff should be moved somewhere more
        # reasonable.
        for result, morph_analyses in self.entries_and_tags:
            if result is not None:

                _formatted = self.formatter(
                    [result],
                    additional_template_kwargs={'analyses': morph_analyses},
                    **fmtkwargs)

                if self.entry_filterer:
                    _formatted = self.entry_filterer(_formatted)

                self._formatted_results.extend(_formatted)

        return self._formatted_results

    @property
    def entries(self):
        if hasattr(self, '_entries'):
            return self._entries

        self._entries = [a for a, _ in self.entries_and_tags]
        return self._entries

    def sort_entries_and_tags_and_paradigm(
            self, unsorted_entries_and_tags_and_paradigms):
        has_custom_sort = template_rendering_overrides.sort_entry_list_display.get(
            (g._from, g._to), False)

        if has_custom_sort:
            return has_custom_sort(self,
                                   unsorted_entries_and_tags_and_paradigms)

        entries_and_tags = unsorted_entries_and_tags_and_paradigms
        return entries_and_tags

    @property
    def entries_and_tags_and_paradigms(self):
        if hasattr(self, '_entries_and_tags_and_paradigms'):
            return self._entries_and_tags_and_paradigms

        self._entries_and_tags_and_paradigms = []

        # Formatting of this stuff should be moved somewhere more
        # reasonable.
        for result, morph_analyses in self.entries_and_tags:

            if result is not None:

                paradigm = False
                has_layout = False

                if self.generate:
                    paradigm = self.generate_paradigm(result, morph_analyses)
                else:
                    paradigm = []

                if current_app.config.paradigm_layouts and paradigm:
                    mlex = current_app.morpholexicon
                    layouts = \
                        mlex.paradigms.get_paradigm_layout(g._from, result,
                                                           morph_analyses,
                                                           return_template=True,
                                                           multiple=True)

                    if layouts:
                        has_layout = [
                            l.for_paradigm(paradigm).fill_generation()
                            for (l, _) in layouts if l
                        ]
                        if not has_layout:
                            has_layout = False

                self._entries_and_tags_and_paradigms.append(
                    (result, morph_analyses, paradigm, has_layout))

        # TODO: custom alphabetical order.
        # TODO: sorting_problem
        return self.sort_entries_and_tags_and_paradigm(
            self._entries_and_tags_and_paradigms)

    @property
    def analyses_without_lex(self):
        if hasattr(self, '_analyses_without_lex'):
            return self._analyses_without_lex

        self._analyses_without_lex = []
        for result, morph_analyses in self.entries_and_tags:
            if result is None:
                self._analyses_without_lex.extend(morph_analyses)

        return self._analyses_without_lex

    def __init__(self,
                 _from,
                 _to,
                 user_input,
                 entries_and_tags,
                 formatter,
                 generate,
                 sorter=None,
                 filterer=None,
                 debug_text=False,
                 other_counts={}):
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

        if sorter is not None:
            self.entry_sorter_key = sorter

        if filterer is not None:
            self.entry_filterer = filterer

        self.analyses = [(lem.input, lem.lemma, list(lem.tag))
                         for lem in entries_and_tags.analyses]

        if self.formatted_results:
            self.successful_entry_exists = True


class SearcherMixin(object):
    """ This mixin provides common methods for performing the search,
    and returning view-ready results.
    """
    entr_r = []

    def do_search_to_obj(self, lookup_value, **kwargs):
        """ Run the search, and provide a result object.
        """
        mlex = current_app.morpholexicon

        search_kwargs = {
            'split_compounds': kwargs.get('split_compounds', True),
            'non_compounds_only': kwargs.get('non_compounds_only', False),
            'no_derivations': kwargs.get('no_derivations', False),
            'return_raw_data': True,
            'lemma_attrs': kwargs.get('lemma_attrs', {}),
        }

        variant_type = kwargs.get('variant_type', False)
        if variant_type:
            morpholex_result = mlex.variant_lookup(
                variant_type,
                lookup_value,
                source_lang=g._from,
                target_lang=g._to,
                **search_kwargs)
        else:
            morpholex_result = mlex.lookup(
                lookup_value,
                source_lang=g._from,
                target_lang=g._to,
                **search_kwargs)

        entries_and_tags, raw_output, raw_error = morpholex_result
        fst_text = raw_error + '\n--\n' + raw_output

        generate = kwargs.get('generate', False)
        search_result_obj = SearchResult(
            g._from,
            g._to,
            lookup_value,
            entries_and_tags,
            self.formatter,
            generate=generate,
            filterer=self.entry_filterer,
            debug_text=fst_text,
            other_counts={},
        )

        return search_result_obj

    def search_to_detailed_context(self, lookup_value, **search_kwargs):
        # TODO: There's a big mess contained here, and part of it
        # relates to lexicon formatters. Slowly working on unravelling
        # it.

        # TODO: this can probably be generalized to be part of the last
        # function.

        errors = False

        search_result_obj = self.do_search_to_obj(
            lookup_value, generate=True, **search_kwargs)

        template_results = [{
            'input':
            search_result_obj.search_term,
            'lookups':
            search_result_obj.formatted_results_sorted
            # 'analyses': search_result_obj.analyses
        }]

        logIndexLookups(
            search_result_obj.search_term,
            template_results,
            g._from,
            g._to,
        )

        show_info = False

        #Here analyses_right related to the same variable in morphology.py
        search_context = {
            'result': search_result_obj.formatted_results_sorted,

            # These variables can be turned into something more general
            'successful_entry_exists':
            search_result_obj.successful_entry_exists,
            'word_searches': template_results,
            'analyses': search_result_obj.analyses,
            'analyses_right': search_result_obj.analyses,
            'analyses_without_lex': search_result_obj.analyses_without_lex,
            'user_input': search_result_obj.search_term,
            'current_locale': get_locale(),
            'errors': errors,  # is this actually getting set?
            'show_info': show_info,
            'language_pairs_other_results': search_result_obj.other_results,
            'debug_text': search_result_obj.debug_text
        }

        return search_context

    # TODO: NST removal
    def search_to_context(self,
                          lookup_value,
                          detailed=False,
                          **default_context_kwargs):
        """ This needs a big redo.

            Note however: new-style templates require similar input
            across Detail/main page view, so can really refactor and
            chop stuff down.

            TODO: inclusion of context_processors ?

            TODO: And the big mess is:
              * do_search_to_obj
              * search_context - simplify
        """

        current_pair, _ = current_app.config.resolve_original_pair(
            g._from, g._to)
        async_paradigm = current_pair.get('asynchronous_paradigms', False)
        lemma_attrs = default_context_kwargs.get('lemma_attrs', {})
        generate = detailed and not async_paradigm

        if 'variant_type' in default_context_kwargs:
            variant_type = default_context_kwargs.get('variant_type')
            search_result_obj = self.do_search_to_obj(
                lookup_value,
                generate=generate,
                lemma_attrs=lemma_attrs,
                variant_type=variant_type)
        else:
            search_result_obj = self.do_search_to_obj(
                lookup_value, generate=generate, lemma_attrs=lemma_attrs)

        if detailed:
            template = 'detail_entry.template'
        else:
            template = 'entry.template'

        _rendered_entry_templates = []

        template_results = [{
            'input':
            search_result_obj.search_term,
            'lookups':
            search_result_obj.formatted_results_sorted
        }]

        logIndexLookups(search_result_obj.search_term, template_results,
                        g._from, g._to)

        show_info = False

        # TODO: sorting_problem

        k = 0
        res_par = []
        if_none = False
        if_next_der = False
        tags = ('Der', 'VAbess', 'VGen', 'Ger', 'Comp', 'Superl')
        #If in the results there is a 'None' entry followed by der tag/s those are removed
        #and are not shown in the results (e.g. "bagoheapmi")
        for item in search_result_obj.entries_and_tags:
            if item[1]:
                if if_none and item[1][0].lemma.startswith(tags):
                    if_next_der = True
                if item[0] != None and not item[1][0].lemma.startswith(tags):
                    if_next_der = False
                if item[0] != None and not if_next_der:
                    res_par.append(item)
                    if_none = False
                else:
                    if_none = True
            else:
                res_par.append(item)

        def korp_query(lemma):
            current_pair_settings, orig_pair_opts = current_app.config.resolve_original_pair(g._from, g._to)
            o_pair = orig_pair_opts.get('orig_pair')
            if orig_pair_opts.get('orig_pair') != ():
                orig_from, orig_to = o_pair
            else:
                orig_from, orig_to = g._from, g._to

            korp_opts = current_pair_settings.get('korp_options')
            start_query = korp_opts.get('start_query')
            corpora = korp_opts.get('corpora')
            k_query = ''

            if (korp_opts.get('lemma_search_path') and lemma and start_query and corpora):
                k_query = start_query + corpora + '&cqp=%5Blemma+%3D+%22' + quote(lemma) + '%22%5D&start=0&end=99'
            return k_query

        korp_hits = 0
        for _, analyses, paradigm, has_layout in search_result_obj.entries_and_tags_and_paradigms:
            if k < len(res_par):
                if res_par[k][0] is not None:
                    if not analyses:
                        analyses = 'az'

                    if res_par[k][1]:
                        url_json = korp_query(res_par[k][1][0].lemma)
                        if sys.version[0] == 2:
                            url_json = url_json.encode('utf8')
                        if url_json:
                            try:
                                response = urlopen(url_json)
                            except HTTPError:
                                korp_hits = 0
                            else:
                                data = json.loads(response.read())
                                if data.get("hits", None) is not None:
                                    korp_hits = data["hits"]

                    tplkwargs = {
                        'lexicon_entry':
                        res_par[k][0],
                        'analyses':
                        analyses,
                        'analyses_right':
                        res_par[k][1],
                        'korp_hits':
                        korp_hits,
                        'paradigm':
                        paradigm,
                        'layout':
                        has_layout,
                        'user_input':
                        search_result_obj.search_term,
                        'word_searches':
                        template_results,
                        'errors':
                        False,
                        'show_info':
                        show_info,
                        'successful_entry_exists':
                        search_result_obj.successful_entry_exists
                    }

                    tplkwargs.update(**default_context_kwargs)

                    # Process all the context processors
                    current_app.update_template_context(tplkwargs)

                    _rendered_entry_templates.append(
                        current_app.lexicon_templates.render_template(
                            g._from, template, **tplkwargs))
                k += 1

        all_analyses = sum(
            [analyses for _, analyses in search_result_obj.entries_and_tags],
            [])

        if all_analyses:
            lemma = all_analyses[0].lemma
            url_json = korp_query(lemma)
            if sys.version[0] == 2 :
                url_json = url_json.encode('utf8')
            if url_json:
                try:
                    response = urlopen(url_json)
                except HTTPError:
                    korp_hits = 0
                else:
                    data = json.loads(response.read())
                    if data.get("hits", None) is not None:
                        korp_hits = data["hits"]
            
        else:
            korp_hits = ''

        indiv_template_kwargs = {
            'analyses': all_analyses,
            'analyses_right': all_analyses,
            'korp_hits': korp_hits,
        }
        indiv_template_kwargs.update(**default_context_kwargs)

        # Process all the context processors
        current_app.update_template_context(indiv_template_kwargs)

        all_analysis_template = \
            current_app.lexicon_templates.render_individual_template(
                g._from, 'analyses.template', **indiv_template_kwargs)

        header_template = \
            current_app.lexicon_templates.render_individual_template(
                g._from, 'includes.template', **indiv_template_kwargs)


        if search_result_obj.analyses_without_lex:
            leftover_tpl_kwargs = {
                'analyses': search_result_obj.analyses_without_lex,
                'analyses_right': search_result_obj.analyses_without_lex,
                'korp_hits': korp_hits,
            }
            leftover_tpl_kwargs.update(**default_context_kwargs)
            # Process all the context processors
            current_app.update_template_context(leftover_tpl_kwargs)

            leftover_analyses_template = \
                current_app.lexicon_templates.render_individual_template(
                    g._from, 'analyses.template', **leftover_tpl_kwargs)
        else:
            leftover_analyses_template = False

        find_problem = \
            current_app.lexicon_templates.render_individual_template(
                g._from, 'find_problem.template', **indiv_template_kwargs)

        search_context = {

            # This is the new style stuff.
            'entry_templates':
            _rendered_entry_templates,
            'entry_template_header_includes':
            header_template,
            'leftover_analyses_template':
            leftover_analyses_template,
            'all_analysis_template':
            all_analysis_template,
            'find_problem':
            find_problem,

            # These variables can be turned into something more general
            'successful_entry_exists':
            search_result_obj.successful_entry_exists,
            'word_searches':
            template_results,
            'analyses':
            search_result_obj.analyses,
            'analyses_right':
            search_result_obj.analyses,
            'analyses_without_lex':
            search_result_obj.analyses_without_lex,
            'user_input':
            search_result_obj.search_term,
            'last_searches':
            session.get('last_searches-' + current_app.config.short_name, []),
            'errors':
            False,  # where should we expect errors?
            'language_pairs_other_results':
            search_result_obj.other_results,
            'debug_text':
            search_result_obj.debug_text
        }

        search_context.update(**default_context_kwargs)

        return self.post_search_context_modification(search_result_obj,
                                                     search_context)


class LanguagePairSearchView(DictionaryView, SearcherMixin):
    """ This view returns either the search form, or processes the
    search request.

    This will be as much view logic as possible, search functionality
    will go elsewhere.

    TODO: confirm logging of each lookup, and generalize logging for all
    views, maybe to a pre-response hook so logging is completely out of
    view code?

    """

    methods = ['GET', 'POST']

    template_name = 'index.html'

    formatter = FrontPageFormat

    @staticmethod
    def log_in_session(user_input):

        uri = u'%s://%s%s?lookup=%s' % (request.scheme, request.host,
                                        request.path, user_input)

        last_search_key = 'last_searches-' + current_app.config.short_name
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
            'successful_entry_exists': False,
            'word_searches': False,
            'analyses': False,
            'analyses_right': False,
            'analyses_without_lex': False,
            'user_input': False,
            'errors': False,  # is this actually getting set?

            # Show the default info under search box
            'show_info': True,
        }

        if 'lookup' in request.args:
            user_input = request.args.get('lookup')

            if current_app.config.strip_spaces and user_input:
                user_input = user_input.strip()
            # This performs lots of the work...
            search_result_context = self.search_to_context(
                user_input, **self.get_shared_context(_from, _to))

            self.log_in_session(user_input)

            # missing current_pair_settings
            return render_template(self.template_name, **search_result_context)
        else:
            default_context.update(**self.get_shared_context(_from, _to))
            return render_template(self.template_name, **default_context)

    def post(self, _from, _to):

        self.check_pair_exists_or_abort(_from, _to)
        self.force_locale(_from, _to)

        user_input = request.form.get('lookup', False)

        if current_app.config.strip_spaces and user_input:
            user_input = user_input.strip()

        if user_input in ['teksti-tv', 'tekst tv', 'teaksta tv']:
            session['text_tv'] = True

        if not user_input:
            user_input = ''

        self.log_in_session(user_input)

        # This performs lots of the work...
        search_result_context = self.search_to_context(
            user_input, **self.get_shared_context(_from, _to))

        # missing current_pair_settings
        return render_template(self.template_name, **search_result_context)


class ReferredLanguagePairSearchView(LanguagePairSearchView):
    """ This overrides some functionality in order to provide the
        /lang/lang/ref/ functionality.
    """

    accepted_lemma_args = {
        'l_til_ref': 'til_ref',
        'e_node': 'entry_hash',
    }

    # TODO: NST removal
    def get(self, _from, _to):

        self.check_pair_exists_or_abort(_from, _to)

        user_input = request.form.get('lookup', False)

        if current_app.config.strip_spaces and user_input:
            user_input = user_input.strip()

        if not user_input:
            user_input = ''
            # TODO: return an error.

        lookup_context = self.get_shared_context(_from, _to)
        lookup_context['lemma_attrs'] = self.get_lemma_lookup_args()

        # This performs lots of the work...
        search_result_context = self.search_to_context(user_input,
                                                       **lookup_context)

        # missing current_pair_settings
        return render_template(self.template_name, **search_result_context)


class DetailedLanguagePairSearchView(DictionaryView, SearcherMixin):
    """ The major difference between this view and the main index search
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
    from nds_lexicon import DetailedFormat as formatter

    accepted_lemma_args = {
        'e_node': 'entry_hash',
    }

    methods = ['GET']

    @property
    def template_name(self):
        if request.args.get('embedded', False):
            return 'word_detail_embedded.html'
        return 'word_detail.html'

    def entry_filterer(self, entries):
        """ Runs on formatted result from DetailedFormat thing.

            Determine the ways that entries will be filtered, and run
            them in sequence.
        """

        # Post-analysis filter arguments, defined in query parameters
        pos_filter = request.args.get('pos_filter', False)
        lemma_match = request.args.get('lemma_match', False)
        e_node = request.args.get('e_node', False)

        def by_pos(req):
            return req.get('input')[1].upper() == pos_filter.upper()

        def by_lemma(req):
            return req.get('input')[0] == self.user_input

        def by_node_hash(req):
            node = req.get('entry_hash')
            return node == e_node

        def default_result(req):
            return req

        entry_filters = [default_result]

        if e_node:
            entry_filters.append(by_node_hash)

        if pos_filter:
            entry_filters.append(by_pos)

        if lemma_match:
            entry_filters.append(by_lemma)

        def filter_entries_for_view(entries):
            _entries = []
            for entry_filter in entry_filters:
                _entries = list(filter(entry_filter, entries))
            return _entries

        return filter_entries_for_view(entries)

    def validate_request(self):
        """Is the format correct?"""

        if format not in ['json', 'html']:
            return _("Invalid format. Only json and html allowed.")

    @staticmethod
    def request_cache_key():
        return u'%s?%s?%s' % (request.path, request.query_string, g.ui_lang)

    # TODO: this
    def get_cache_entry(self):
        pass

    def get(self, _from, _to, wordform, format):

        # Check for cache entry here

        self.check_pair_exists_or_abort(_from, _to)

        self.validate_request()

        user_input = wordform = decode_or_fail(wordform)

        if current_app.config.strip_spaces and user_input:
            user_input = user_input.strip()

        self.user_input = user_input

        # Analyzer arguments
        no_compounds = request.args.get('no_compounds', False)

        # Determine whether to display the more detail link
        lemma_match = request.args.get('lemma_match', False)
        e_node = request.args.get('e_node', False)

        want_more_detail = no_compounds or lemma_match or e_node

        # Set up morphology arguments
        if no_compounds:
            _split = True
            _non_c = True
            _non_d = False
        else:
            _split = True
            _non_c = False
            _non_d = False

        search_kwargs = {
            'split_compounds': _split,
            'non_compounds_only': _non_c,
            'no_derivations': _non_d,
        }

        search_kwargs['lemma_attrs'] = self.get_lemma_lookup_args()

        has_analyses = False

        search_result_context = self.search_to_context(user_input,
                                                       detailed=True,
                                                       **search_kwargs)

        has_analyses = search_result_context.get('successful_entry_exists')

        # TODO: cache search result here
        search_result_context['has_analyses'] = has_analyses
        search_result_context['more_detail_link'] = want_more_detail

        return render_template(self.template_name, **search_result_context)
