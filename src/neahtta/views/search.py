from . import blueprint
from flask import current_app

from cache import cache

import sys

import simplejson

from logging import getLogger

from i18n.utils import iso_filter

from utils.logger import *
from utils.data import *
from utils.encoding import *

from flask import ( request
                  , session
                  , Response
                  , render_template
                  , abort
                  , redirect
                  , g
                  )

from flaskext.babel import gettext as _

from operator import itemgetter

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

from i18n.utils import get_locale

from flask.views import View, MethodView

class AppViewSettingsMixin(object):

    def __init__(self, *args, **kwargs):

        # Apply some default values for the present application

        self.default_from, self.default_to = current_app.config.default_language_pair
        self.default_pair_settings = current_app.config.pair_definitions[( self.default_from
                                                                         , self.default_to
                                                                         )]

        super(AppViewSettingsMixin, self).__init__(*args, **kwargs)

class IndexSearch(object):

    @property
    def template_name(self):
        if current_app.config.new_style_templates:
            return 'index_new_style.html'
        else:
            return 'index.html'

class IndexSearchPage(IndexSearch, View, AppViewSettingsMixin):
    """ A simple view to handle potential mobile redirects to a default
    language pair specified only for mobile.
    """

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

        current_pair_settings, orig_pair_opts = current_app.config.resolve_original_pair(self.default_from, self.default_to)
        template_context = {
            'display_swap': reverse_exists,
            'swap_from': self.default_to,
            'swap_to': self.default_from,
            'show_info': True,
            'current_pair_settings': current_pair_settings,
            'current_variant_options': orig_pair_opts.get('variant_options'),
            'current_locale': get_locale(),
            '_from': self.default_from,
            '_to': self.default_to
        }

        if current_app.config.new_style_templates:
            search_info = current_app.lexicon_templates.render_individual_template(
                self.default_from,
                'search_info.template',
                **template_context
            )
            search_form = current_app.lexicon_templates.render_individual_template(
                self.default_from,
                'index_search_form.template',
                **template_context
            )
            template_context['search_info_template'] = search_info
            template_context['index_search_form'] = search_form

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

    def entry_sorter_key(self, r):
        return r.get('left')

    @property
    def formatted_results_sorted(self):
        return sorted( self.formatted_results
                     , key=self.entry_sorter_key
                     )

    @property
    def formatted_results_pickleable(self):
        # TODO: implement
        def pickleable_result(_results):
            """ Pop the various keys that need to be removed.
            """
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

        pickle_result = pickleable_result(self.formatted_results_sorted)

        return pickle_result

    def generate_paradigm_from_formatted(self, formatted_results, morph_analyses):

        morph = current_app.config.morphologies.get(g._from, False)
        mlex = current_app.morpholexicon

        generated_and_formatted = []
        for r in formatted_results:
            lemma, pos, tag, _type = r.get('input')
            node = r.get('node')

            paradigm_from_file = mlex.paradigms.get_paradigm(
                g._from, node, morph_analyses
            )
            if paradigm_from_file:
                form_tags = [_t.split('+')[1::] for _t in paradigm_from_file.splitlines()]
                _generated = morph.generate(lemma, form_tags, node)
            else:
                # For pregenerated things
                _generated = morph.generate(lemma, [], node)

            r['paradigm'] = _generated
            generated_and_formatted.append(r)

        return generated_and_formatted

    def generate_paradigm(self, node, morph_analyses):
        _str_norm = 'string(normalize-space(%s))'

        morph = current_app.config.morphologies.get(g._from, False)
        mlex = current_app.morpholexicon

        generated_and_formatted = []

        l = node.xpath('./lg/l')[0]
        lemma = l.xpath(_str_norm % './text()')

        paradigm_from_file = mlex.paradigms.get_paradigm(
            g._from, node, morph_analyses
        )
        if paradigm_from_file:
            form_tags = [_t.split('+')[1::] for _t in paradigm_from_file.splitlines()]
            # TODO: bool not iterable
            _generated = morph.generate_to_objs(lemma, form_tags, node)
        else:
            # For pregenerated things
            _generated = morph.generate_to_objs(lemma, [], node)

        return _generated

    @property
    def formatted_results(self):
        if hasattr(self, '_formatted_results'):
            return self._formatted_results

        self._formatted_results = []

        fmtkwargs = { 'target_lang': self._to
                    , 'source_lang': self._from
                    , 'ui_lang': g.ui_lang
                    , 'user_input': self.user_input
                    }

        # Formatting of this stuff should be moved somewhere more
        # reasonable.
        for result, morph_analyses in self.entries_and_tags:
            if result is not None:

                _formatted = self.formatter(
                    [result],
                    additional_template_kwargs={'analyses': morph_analyses},
                    **fmtkwargs
                )

                if self.entry_filterer:
                    _formatted = self.entry_filterer(_formatted)

                if self.generate:
                    _formatted = self.generate_paradigm_from_formatted(_formatted, morph_analyses)

                self._formatted_results.extend(_formatted)

        return self._formatted_results

    @property
    def entries_and_tags_and_paradigms(self):
        if hasattr(self, '_entries_and_tags_and_paradigms'):
            return self._entries_and_tags_and_paradigms

        self._entries_and_tags_and_paradigms = []

        # Formatting of this stuff should be moved somewhere more
        # reasonable.
        for result, morph_analyses in self.entries_and_tags:

            if result is not None:

                # if self.entry_filterer:
                #     _formatted = self.entry_filterer(_formatted)

                paradigm = False

                if self.generate:
                    paradigm = self.generate_paradigm(result, morph_analyses)
                else:
                    paradigm = []

                self._entries_and_tags_and_paradigms.append((result,
                                                             morph_analyses,
                                                             paradigm))

        return self._entries_and_tags_and_paradigms

    @property
    def analyses_without_lex(self):
        if hasattr(self, '_analyses_without_lex'):
            return self._analyses_without_lex

        self._analyses_without_lex = []
        for result, morph_analyses in self.entries_and_tags:
            if result is None:
                self._analyses_without_lex.extend(morph_analyses)

        return self._analyses_without_lex

    def __init__(self, _from, _to, user_input, entries_and_tags, formatter, generate, sorter=None, filterer=None):
        self.user_input = user_input
        self.search_term = user_input
        self.entries_and_tags = entries_and_tags
        # When to display unknowns
        self.successful_entry_exists = False
        self._from = _from
        self._to = _to
        self.formatter = formatter
        self.generate = generate

        if sorter is not None:
            self.entry_sorter_key = sorter

        if filterer is not None:
            self.entry_filterer = filterer

        self.analyses = [ (lem.input, lem.lemma, list(lem.tag))
                          for lem in entries_and_tags.analyses
                        ]

        if len(self.formatted_results) > 0:
            self.successful_entry_exists = True

from lexicon import FrontPageFormat

class SearcherMixin(object):
    """ This mixin provides common methods for performing the search,
    and returning view-ready results.
    """

    def do_search_to_obj(self, lookup_value, **kwargs):

        successful_entry_exists = False

        mlex = current_app.morpholexicon

        search_kwargs = {
            'split_compounds': kwargs.get('split_compounds', True),
            'non_compounds_only': kwargs.get('non_compounds_only', False),
            'no_derivations': kwargs.get('no_derivations', False),
            'lemma_attrs': kwargs.get('lemma_attrs', {}),
        }

        entries_and_tags = mlex.lookup( lookup_value
                                      , source_lang=g._from
                                      , target_lang=g._to
                                      , **search_kwargs
                                      )

        generate = kwargs.get('generate', False)
        search_result_obj = SearchResult(g._from, g._to, lookup_value,
                                         entries_and_tags,
                                         self.formatter,
                                         generate=generate,
                                         filterer=self.entry_filterer)

        return search_result_obj

    def search_to_context(self, lookup_value, lemma_attrs={}):
        # TODO: There's a big mess contained here, and part of it
        # relates to lexicon formatters. Slowly working on unravelling
        # it.

        errors = []

        search_result_obj = self.do_search_to_obj(lookup_value, lemma_attrs=lemma_attrs)

        template_results = [{
            'input': search_result_obj.search_term,
            'lookups': search_result_obj.formatted_results_sorted
        }]

        logIndexLookups(search_result_obj.search_term, template_results, g._from, g._to)

        show_info = False

        if len(errors) == 0:
            errors = False

        search_context = {

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

    def search_to_detailed_context(self, lookup_value, **search_kwargs):
        # TODO: There's a big mess contained here, and part of it
        # relates to lexicon formatters. Slowly working on unravelling
        # it.

        # TODO: this can probably be generalized to be part of the last
        # function.

        errors = []

        search_result_obj = self.do_search_to_obj(lookup_value, generate=True, **search_kwargs)

        template_results = [{
            'input': search_result_obj.search_term,
            'lookups': search_result_obj.formatted_results_sorted
            # 'analyses': search_result_obj.analyses
        }]

        logIndexLookups(search_result_obj.search_term, template_results, g._from, g._to)

        show_info = False

        if len(errors) == 0:
            errors = False

        search_context = {
            'result': search_result_obj.formatted_results_sorted,

            # These variables can be turned into something more general
            'successful_entry_exists': search_result_obj.successful_entry_exists,

            'word_searches': template_results,
            'analyses': search_result_obj.analyses,
            'analyses_without_lex': search_result_obj.analyses_without_lex,
            'user_input': search_result_obj.search_term,
            'current_locale': get_locale(),

            # ?
            'errors': errors, # is this actually getting set?
            'show_info': show_info,
        }

        return search_context

    def search_to_newstyle_context(self, lookup_value, detailed=False, **default_context_kwargs):
        """ This needs a big redo.

            Note however: new-style templates require similar input
            across Detail/main page view, so can really refactor and
            chop stuff down.

            TODO: inclusion of context_processors ?

            TODO: And the big mess is:
              * do_search_to_obj
              * search_context - simplify
        """

        # TODO: ajax paradigms
        current_pair, _ = current_app.config.resolve_original_pair(g._from, g._to)
        async_paradigm = current_pair.get('asynchronous_paradigms', False)

        if detailed and not async_paradigm:
            generate = True
        else:
            generate = False

        search_result_obj = self.do_search_to_obj(lookup_value, generate=generate)

        if detailed:
            template = 'detail_entry.template'
        else:
            template = 'entry.template'

        _rendered_entry_templates = []

        template_results = [{
            'input': search_result_obj.search_term,
            'lookups': search_result_obj.formatted_results_sorted
        }]

        logIndexLookups(search_result_obj.search_term, template_results, g._from, g._to)

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

        for lz, az, paradigm in sorted(search_result_obj.entries_and_tags_and_paradigms, key=sort_entry):
            if lz is not None:

                tplkwargs = { 'lexicon_entry': lz
                            , 'analyses': az

                            , 'paradigm': paradigm
                            , 'user_input': search_result_obj.search_term
                            , 'word_searches': template_results
                            , 'errors': False
                            , 'show_info': show_info
                            , 'successful_entry_exists': search_result_obj.successful_entry_exists
                            }
                tplkwargs.update(**default_context_kwargs)

                # Process all the context processors
                current_app.update_template_context(tplkwargs)

                _rendered_entry_templates.append(
                    current_app.lexicon_templates.render_template(g._from, template, **tplkwargs)
                )

        all_az = sum([az for _, az in sorted(search_result_obj.entries_and_tags, key=sort_entry)], [])

        indiv_template_kwargs = {
            'analyses': all_az,
        }
        indiv_template_kwargs.update(**default_context_kwargs)

        # Process all the context processors
        current_app.update_template_context(indiv_template_kwargs)

        all_analysis_template = \
            current_app.lexicon_templates.render_individual_template(g._from, 'analyses.template', **indiv_template_kwargs)

        header_template = \
            current_app.lexicon_templates.render_individual_template(g._from, 'includes.template', **indiv_template_kwargs)


        if search_result_obj.analyses_without_lex:
            leftover_tpl_kwargs = {
                'analyses': search_result_obj.analyses_without_lex,
            }
            leftover_tpl_kwargs.update(**default_context_kwargs)
            # Process all the context processors
            current_app.update_template_context(leftover_tpl_kwargs)

            leftover_analyses_template = \
                current_app.lexicon_templates.render_individual_template( g._from
                                                                        , 'analyses.template'
                                                                        , **leftover_tpl_kwargs
                                                                        )
        else:
            leftover_analyses_template = False

        search_context = {

            # This is the new style stuff.
            'new_templates': _rendered_entry_templates,
            'new_template_header_includes': header_template,

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

class DictionaryView(MethodView):

    entry_filterer = lambda self, x: x

    validate_request = lambda self, x: True

    def check_pair_exists_or_abort(self, _from, _to):

        if (_from, _to) not in current_app.config.dictionaries and \
           (_from, _to) not in current_app.config.variant_dictionaries:
            abort(404)

        return False

    def get_reverse_pair(self, _from, _to):
        """ If the reverse pair for (_from, _to) exists, return the
        pair's settings, otherwise False. """

        # TODO: move this to config object.

        pair_settings, orig_pair_opts = current_app.config.resolve_original_pair(_from, _to)
        _r_from, _r_to = orig_pair_opts.get('swap_from'), orig_pair_opts.get('swap_to')
        reverse_exists = current_app.config.dictionaries.get((_r_from, _r_to), False)

        return reverse_exists

class LanguagePairSearchView(IndexSearch, DictionaryView, SearcherMixin):
    """ This view returns either the search form, or processes the
    search request.

    This will be as much view logic as possible, search functionality
    will go elsewhere.

    TODO: confirm logging of each lookup, and generalize logging for all
    views, maybe to a pre-response hook so logging is completely out of
    view code?

    """

    methods = ['GET', 'POST']

    formatter = FrontPageFormat

    def get_shared_context(self, _from, _to):
        """ Return some things that are in all templates. """

        current_pair_settings, orig_pair_opts = current_app.config.resolve_original_pair(_from, _to)
        shared_context = {
            'display_swap': self.get_reverse_pair(_from, _to),
            'current_pair_settings': current_pair_settings,
            'current_variant_options': orig_pair_opts.get('variant_options'),
            'current_locale': get_locale(),
            '_from': _from,
            '_to': _to,
        }

        if current_app.config.new_style_templates:
            search_info = current_app.lexicon_templates.render_individual_template(
                g._from,
                'search_info.template',
                **shared_context
            )
            search_form = current_app.lexicon_templates.render_individual_template(
                g._from,
                'index_search_form.template',
                **shared_context
            )
            shared_context['search_info_template'] = search_info
            shared_context['index_search_form'] = search_form
        shared_context.update(**orig_pair_opts)
        return shared_context

    def get(self, _from, _to):

        self.check_pair_exists_or_abort(_from, _to)

        # If the view is for an input variant, we need the original
        # pair:

        default_context = {

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

        self.check_pair_exists_or_abort(_from, _to)

        user_input = lookup_val = request.form.get('lookup', False)

        if user_input in ['teksti-tv', 'tekst tv', 'teaksta tv']:
            session['text_tv'] = True

        if current_app.config.new_style_templates:
            return self.handle_newstyle_post(_from, _to)

        if not user_input:
            user_input = ''
            show_info = True
            # TODO: return an error.

        # This performs lots of the work...
        search_result_context = self.search_to_context(user_input)

        search_result_context.update(**self.get_shared_context(_from, _to))

        return render_template(self.template_name, **search_result_context)

    def handle_newstyle_post(self, _from, _to):

        user_input = lookup_val = request.form.get('lookup', False)

        if not user_input:
            user_input = ''
            show_info = True
            # TODO: return an error.

        # This performs lots of the work...
        search_result_context = self.search_to_newstyle_context(user_input, **self.get_shared_context(_from, _to))

        # missing current_pair_settings
        return render_template('index_new_style.html', **search_result_context)

class ReferredLanguagePairSearchView(LanguagePairSearchView):
    """ This overrides some functionality in order to provide the
        /lang/lang/ref/ functionality.
    """

    accepted_lemma_args = {
        'l_til_ref': 'til_ref',
    }

    def get(self, _from, _to):

        self.check_pair_exists_or_abort(_from, _to)

        if current_app.config.new_style_templates:
            return self.handle_newstyle_post(_from, _to)

        user_input = lookup_val = request.form.get('lookup', False)

        if not user_input:
            user_input = ''
            show_info = True
            # TODO: return an error.

        # Get URL parameters for lookup

        lemma_lookup_args = {}
        for k, v in request.args.iteritems():
            if k in self.accepted_lemma_args:
                lemma_lookup_args[self.accepted_lemma_args.get(k)] = v

        # This performs lots of the work...
        search_result_context = self.search_to_context(user_input, lemma_attrs=lemma_lookup_args)

        search_result_context.update(**self.get_shared_context(_from, _to))

        return render_template(self.template_name, **search_result_context)

from .reader import json_response

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
    from lexicon import DetailedFormat as formatter

    methods = ['GET']
    template_name = 'word_detail.html'

    def entry_filterer(self, entries, **kwargs):
        """ Runs on formatted result from DetailedFormat thing

            TODO: will need to reconstruct this for new style views
            because the formatters are going away
        """

        # Post-analysis filter arguments
        pos_filter = request.args.get('pos_filter', False)
        lemma_match = request.args.get('lemma_match', False)
        e_node = request.args.get('e_node', False)
        wordform = request.args.get('wordform', False)

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

        return filter_entries_for_view(entries)

    def validate_request(self):
        """ Is the format correct?
        """

        if not format in ['json', 'html']:
            return _("Invalid format. Only json and html allowed.")

        self.check_pair_exists_or_abort(g._from, g._to)

    def request_cache_key(self):
        return u'%s?%s?%s' % (request.path, request.query_string, g.ui_lang)

    def get_cache_entry(self):
        # TODO: return response from cache

        # if current_app.caching_enabled:
        #     cached_result = current_app.cache.get(entry_cache_key)
        # else:
        #     cached_result = None

        # cur_morph = current_app.config.morphologies.get(from_language)

        # def depickle_result(_results):
        #     pickleable = []
        #     for j in _results:
        #         _j = j.copy()
        #         analyses = []
        #         for (lemma, tag) in _j.get('analyses', []):
        #             # TODO: tag formatter
        #             _lem = cur_morph.de_pickle_lemma(lemma, tag)
        #             analyses.append(_lem)
        #         _j['analyses'] = analyses
        #         pickleable.append(_j)
        #     return pickleable

        # json_result = cached_result
        # detailed_result = depickle_result(cached_result)
        pass

    def get(self, _from, _to, wordform, format):

        # Check for cache entry here

        self.check_pair_exists_or_abort(_from, _to)

        self.validate_request()

        user_input = wordform = decodeOrFail(wordform)

        # Analyzer arguments
        no_compounds = request.args.get('no_compounds', False)

        # Determine whether to display the more detail link
        pos_filter = request.args.get('pos_filter', False)
        lemma_match = request.args.get('lemma_match', False)
        e_node = request.args.get('e_node', False)

        if no_compounds or lemma_match or e_node:
            want_more_detail = True
        else:
            want_more_detail = False

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

        # TODO: ajax paradigms

        has_analyses = False

        if current_app.config.new_style_templates:
            search_result_context = \
                self.search_to_newstyle_context(user_input,
                                                detailed=True,
                                                **search_kwargs)
            has_analyses = search_result_context.get('successful_entry_exists')
        else:
            search_result_context = self.search_to_detailed_context(user_input, **search_kwargs)

            for result in search_result_context.get('result'):
                if result.get('analyses'):
                    if len(result.get('analyses')) > 0:
                        has_analyses = True

        # TODO: cache search result here
        # current_app.cache.set(entry_cache_key,
        # search_result_context.detailed_entry_pickleable)

        # search_result_context.update(**self.get_shared_context(_from, _to))

        search_result_context['has_analyses'] = has_analyses
        search_result_context['more_detail_link'] = want_more_detail

        if current_app.config.new_style_templates:
            template = 'word_detail_new_style.html'
        else:
            template = self.template_name

        return render_template(template, **search_result_context)

class ParadigmLanguagePairSearchView(DictionaryView, SearcherMixin):

    from lexicon import DetailedFormat as formatter

    def get(self, _from, _to, lemma):

        # Check for cache entry here

        # TODO: include e node / enry_filterer

        self.check_pair_exists_or_abort(_from, _to)
        # self.validate_request()

        user_input = lemma = decodeOrFail(lemma)

        # Generation constraints
        pos_filter = request.args.get('pos', False)
        e_node = request.args.get('e_node', False)

        _split = True
        _non_c = True
        _non_d = False

        search_kwargs = {
            'split_compounds': _split,
            'non_compounds_only': _non_c,
            'no_derivations': _non_d,
        }

        has_analyses = False
        cache_key = '+'.join([a for a in [
            lemma,
            pos_filter,
            e_node,
        ] if a])

        paradigms = current_app.cache.get(cache_key)

        if not paradigms:
            paradigms = \
                self.search_to_paradigm(user_input,
                                        detailed=True,
                                        **search_kwargs)

            current_app.cache.set(cache_key, paradigms)

        from morphology.utils import tagfilter

        ui_locale = get_locale()

        def filter_tag((_input, tag, forms)):
            filtered_tag = tagfilter(tag, g._from, g._to).split(' ')
            return (_input, filtered_tag, forms)

        paradigms = [map(filter_tag, _p) for _p in paradigms]

        # TODO: cache search result here
        # current_app.cache.set(entry_cache_key,
        # search_result_context.detailed_entry_pickleable)

        # search_result_context.update(**self.get_shared_context(_from, _to))

        return json_response({
            'paradigms': paradigms,
            'input': {
                'lemma': lemma,
                'pos': pos_filter,
            }
        })


    def search_to_paradigm(self, lookup_value, **search_kwargs):

        errors = []

        search_result_obj = self.do_search_to_obj(lookup_value, generate=True, **search_kwargs)

        paradigms = []

        for a in search_result_obj.formatted_results:
            paradigms.append(a.get('paradigm'))

        return paradigms

    def entry_filterer(self, entries, **kwargs):
        """ Runs on formatted result from DetailedFormat thing

            TODO: will need to reconstruct this for new style views
            because the formatters are going away
        """

        # Post-analysis filter arguments
        pos_filter = request.args.get('pos', False)
        e_node = request.args.get('e_node', False)

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

        def filter_entries_for_view(entries):
            _entries = []
            for f in entry_filters:
                _entries = filter(f, entries)
            return _entries

        return filter_entries_for_view(entries)
