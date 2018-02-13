### Morpho-Lexical interface
###

# TODO: do not display analyzed lexical entries for words with mini-paradigms,
# e.g., lemma_ref contents should be stripped.

# Will need to operate on the output of lookup(), and this is language
# specific, so decorator registry thing is probably good here.

from flask import current_app


from lexicon.lexicon import hash_node

from itertools import groupby
from operator import itemgetter

class MorphoLexiconOverrides(object):

    def override_results(self, function):
        """ This runs the morpholex lookup, and passes the output
        through the a set of functions to process the output.
        """
        def decorate(wordform, **input_kwargs):
            _from = input_kwargs.get('source_lang')
            raw_return = input_kwargs.get('return_raw_data', False)

            entries_and_tags = function(wordform, **input_kwargs)
            if raw_return:
                entries_and_tags, stdout, stderr, entr_right = entries_and_tags
            else:
                entries_and_tags, entr_right = entries_and_tags

            for f in self.override_functions[_from]:
                new_res = f(entries_and_tags)
                if new_res is not None:
                    entries_and_tags = new_res
                else:
                    continue

            if raw_return:
                return MorphoLexiconResult(entries_and_tags), stdout, stderr, MorphoLexiconResult(entr_right)
            else:
                return MorphoLexiconResult(entries_and_tags), MorphoLexiconResult(entr_right)

        return decorate

    def post_morpho_lexicon_override(self, *language_isos):
        """ Use this function to register functions as part of this
        override """
        def wrapper(override_function):
            for language_iso in language_isos:
                self.override_functions[language_iso]\
                    .append(override_function)
                print '%s morpholex overrides: registered - %s' % \
                        ( language_iso
                        , override_function.__name__
                        )
        return wrapper

    def __init__(self):
        from collections import defaultdict
        self.override_functions = defaultdict(list)

morpholex_overrides = MorphoLexiconOverrides()

from operator import itemgetter

class MorphoLexiconResult(list):
    """ A subcalss of the List object meant to make sorting through
    results more readable.
    """

    @property
    def analyses(self):
        """ Return a list of Lemma objects for each entry result
        """
        # return [lem for e, lems in self
        #             for lem in lems
        #             if lem is not None]
        return sum(map(itemgetter(1), self), [])

    @property
    def entries(self):
        """ Return a list of entry objects for each entry result
        """
        # return [e for e, analyses in self]
        return map(itemgetter(0), self)

class MorphoLexicon(object):
    morphology_kwarg_names = [
        'split_compounds',
        'non_compound_only',
        'no_derivations',
        'return_raw_data',
    ]

    lexicon_kwarg_names = [
        'source_lang',
        'target_lang',
        'lemma',
        'pos',
        'pos_type',
        'entry_hash',
    ]

    def lookup(self, wordform, **kwargs):
        """ Performs a lookup with morphology and lexicon working
        together. Numerous keyword arguments/parameters are available
        here.

            morpholexicon.lookup(wordform, keyword_arg_1=asdf,
                                 keyword_arg_2=bbq)

        Required keyword arguments:
          - `source_lang` - the 3-character ISO for the source language
          - `target_lang` - the 3-character ISO for the target language

        Optional lexicon keyword arguments:
          - `lemma` - A lemma, if a lemma is known
          - `pos` - Part of speech filter
          - `pos_type` - POS type filter
          - `entry_hash` - an entry hash to return a specific entry

        Optional morphology keyword arguments:
          - `split_compounds` - Split compounds in the morphology, and
            return lemmas for each part of the compound.

          - `non_compound_only` - Filter out compounds by removing
          analyses with the compound tag (this is set in the Morphology
          configuration for the language analyser:

              configs/sanit.config.yaml:
                  Morphology
                    sme:
                      options:
                        compoundBoundary: "here."

          - `no_derivations` - Filter out derivations by removing

            analyses with the derivation tag. This is also specified in
            the configuration for `derivationMarker`

          - `return_raw_data` - Include the raw stdout/stderr data from
          the analyzer.

        """

        source_lang = kwargs.get('source_lang')
        target_lang = kwargs.get('target_lang')

        morph_kwargs = {}
        lex_kwargs = {}
        lemma_attrs = {}

        if 'lemma_attrs' in kwargs:
            lemma_attrs = kwargs.pop('lemma_attrs')

        if 'entry_hash' in lemma_attrs:
            entry_hash_filter = lemma_attrs.pop('entry_hash')
        else:
            entry_hash_filter = False

        for k, v in kwargs.iteritems():
            if k in self.morphology_kwarg_names:
                morph_kwargs[k] = v

        for k, v in kwargs.iteritems():
            if k in self.lexicon_kwarg_names:
                lex_kwargs[k] = v

        # TODO: if analyses dropping componuds results in lexicalized
        # form that does not exist in lexicon, then fall back to
        # compounds?

        # TODO: to hide more_info link properly, we still need to know
        # what information has been stripped away in morph_kwargs and
        # lex_kwargs, so a count of discarded results for at least one
        # of these would be good.  -- alternative is to run the lookup
        # twice, which might take too much time if someone's hitting
        # detail frequently.

        analyzer = self.analyzers.get(source_lang)
        try:
            analyses = analyzer.lemmatize(wordform, **morph_kwargs)
        except AttributeError:
            analyses = []
            analyses_right = []


        return_raw_data = morph_kwargs.get('return_raw_data', False)
        raw_output = ''
        raw_errors = ''


        if return_raw_data and analyses:
            analyses, raw_output, raw_errors, analyses_right = analyses
        else:
            analyses, analyses_right = analyses
        # if analyses:
        #     lookup_lemmas = [l.lemma for l in analyses]
        # else:
        #     analyses = []

        entries_and_tags = []
        entries_and_tags_right = []

        if analyses:
            #for analysis in list(set(analyses)):
            for analysis in list(analyses):
                if isinstance(analysis, list):
                    if analysis[0].lemma:
                        lex_kwargs = {
                            'lemma': analysis[0].lemma,
                            'pos': analysis[0].pos,
                            'pos_type': False,
                            'user_input': wordform,
                        }
                    else:
                        continue
                    #    lex_kwargs = {
                    #        'lemma': False,
                    #        'pos': False,
                    #        'pos_type': False,
                    #        'user_input': wordform,
                    #    }
                else:
                    if analysis:
                        lex_kwargs = {
                            'lemma': analysis.lemma,
                            'pos': analysis.pos,
                            'pos_type': False,
                            'user_input': wordform,
                        }
                    else:
                        continue


                xml_result = self.lexicon.lookup( source_lang
                                                , target_lang
                                                , **lex_kwargs
                                                )

                if xml_result:
                    for e in xml_result:
                        entries_and_tags.append((e, analysis))
                else:
                    entries_and_tags.append((None, analysis))

        if analyses_right:
            #for analysis in list(set(analyses)):
            for analysis_r in list(analyses_right):
                if isinstance(analysis_r, list):
                    if analysis_r[0].lemma:
                        lex_kwargs_right = {
                            'lemma': analysis_r[0].lemma,
                            'pos': analysis_r[0].pos,
                            'pos_type': False,
                            'user_input': wordform,
                        }
                    else:
                        continue
                else:
                    if analysis_r:
                        lex_kwargs_right = {
                            'lemma': analysis_r.lemma,
                            'pos': analysis_r.pos,
                            'pos_type': False,
                            'user_input': wordform,
                        }
                    else:
                        continue


                xml_result_right = self.lexicon.lookup( source_lang
                                                , target_lang
                                                , **lex_kwargs_right
                                                )

                if xml_result_right:
                    for e in xml_result_right:
                        entries_and_tags_right.append((e, analysis_r))
                else:
                    entries_and_tags_right.append((None, analysis_r))

        no_analysis_xml = self.lexicon.lookup( source_lang
                                             , target_lang
                                             , wordform
                                             , lemma_attrs=lemma_attrs
                                             , user_input=wordform
                                             )


        if no_analysis_xml:
            for e in no_analysis_xml:
                entries_and_tags.append((e, None))
                entries_and_tags_right.append((e, None))


        if entry_hash_filter:
            def filt((x, _)):
                if x is not None:
                    return hash_node(x) == entry_hash_filter
                return True
            entries_and_tags = filter(filt, entries_and_tags)
            entries_and_tags_right = filter(filt, entries_and_tags_right)

        # group by entry

        results = []
        results_right = []
        _by_entry = itemgetter(0)
        _by_entry_r = itemgetter(0)
        #Entries were previously sorted alphabetically
        #sorted_grouped_entries = groupby(
        #    sorted(entries_and_tags, key=_by_entry),
        #    _by_entry)

        def collect_same_lemma(array):
            #Collect same lemma in original order
            global array_sorted
            array_sorted = []
            k = 0
            l = []
            l0 = []
            none_not_added = True
            while k < len(array):
                for i in range(0, len(array)):
                    if (array[i][1] != None) & (array[k][1] != None):
                        if array[i][0] == array[k][0]:
                            if array[i] not in l:
                                array_sorted.append(array[i])
                                l.append(array[i])
                                l0.append(array[i][0])
                    else:
                        if (none_not_added) & (array[i][0] not in l0):
                            array_sorted.append(array[i])
                            none_not_added = False
                k += 1
            j = 0
            #In case there is the same entry twice (with and without analyses), remove the one without analyses
            while j < len(array_sorted):
                for i in range(0, len(array_sorted)):
                    if (array_sorted[i][0] == array_sorted[j][0]):
                        if (array_sorted[i][1] is not None) & (array_sorted[j][1] is None):
                            del array_sorted[j]
                            break
                        else:
                            if (array_sorted[j][1] is not None) & (array_sorted[i][1] is None):
                                del array_sorted[i]
                                break
                j += 1
            return array_sorted


        entries_and_tags_sorted = collect_same_lemma(entries_and_tags)
        sorted_grouped_entries = groupby(entries_and_tags_sorted, _by_entry)

        for grouper, grouped in sorted_grouped_entries:
            analyses = [an for _, an in grouped if an is not None]
            results.append((grouper, analyses))
        entries_and_tags = results


        entries_and_tags_sorted_r = collect_same_lemma(entries_and_tags_right)
        sorted_grouped_entries_r = groupby(entries_and_tags_sorted_r, _by_entry_r)

        for grouper, grouped in sorted_grouped_entries_r:
            analyses_r = [an for _, an in grouped if an is not None]
            results_right.append((grouper, analyses_r))
        entries_and_tags_right = results_right


        # TODO: may need to do the same for derivation?
        # NOTE: test with things that will never return results just to
        # make sure recursion doesn't get carried away.
        _ret = None
        if (len(entries_and_tags) == 0) and ('non_compound_only' in kwargs):
            if kwargs['non_compound_only']:
                new_kwargs = kwargs.copy()
                new_kwargs.pop('non_compound_only')
                _ret = self.lookup(wordform, **new_kwargs)
            else:
                _ret = []
        elif (len(entries_and_tags) == 0) and not analyses:
            _ret = MorphoLexiconResult([])
        else:
            _ret = MorphoLexiconResult(entries_and_tags)


        ret_right = None
        if (len(entries_and_tags_right) == 0) and ('non_compound_only' in kwargs):
            if kwargs['non_compound_only']:
                new_kwargs = kwargs.copy()
                new_kwargs.pop('non_compound_only')
                ret_right = self.lookup(wordform, **new_kwargs)
            else:
                ret_right = []
        elif (len(entries_and_tags_right) == 0) and not analyses_right:
            ret_right = MorphoLexiconResult([])
        else:
            ret_right = MorphoLexiconResult(entries_and_tags_right)


        if return_raw_data:
            return _ret, raw_output, raw_errors, ret_right
        else:
            return _ret, ret_right

    def __init__(self, config):
        self.analyzers = config.morphologies
        self.lexicon = config.lexicon

        self.lookup = morpholex_overrides.override_results(
            self.lookup
        )


    def variant_lookup(self, search_type, wordform, **kwargs):
        """ Performs a lookup with morphology and lexicon working
        together. Numerous keyword arguments/parameters are available
        here.

            morpholexicon.lookup(wordform, keyword_arg_1=asdf,
                                 keyword_arg_2=bbq)

        Required keyword arguments:
          - `source_lang` - the 3-character ISO for the source language
          - `target_lang` - the 3-character ISO for the target language

        Optional lexicon keyword arguments:
          - `lemma` - A lemma, if a lemma is known
          - `pos` - Part of speech filter
          - `pos_type` - POS type filter
          - `entry_hash` - an entry hash to return a specific entry

        Optional morphology keyword arguments:
          - `split_compounds` - Split compounds in the morphology, and
            return lemmas for each part of the compound.

          - `non_compound_only` - Filter out compounds by removing
          analyses with the compound tag (this is set in the Morphology
          configuration for the language analyser:

              configs/sanit.config.yaml:
                  Morphology
                    sme:
                      options:
                        compoundBoundary: "here."

          - `no_derivations` - Filter out derivations by removing

            analyses with the derivation tag. This is also specified in
            the configuration for `derivationMarker`

          - `return_raw_data` - Include the raw stdout/stderr data from
          the analyzer.

        """

        source_lang = kwargs.get('source_lang')
        target_lang = kwargs.get('target_lang')

        morph_kwargs = {}
        lex_kwargs = {}
        lemma_attrs = {}

        if 'lemma_attrs' in kwargs:
            lemma_attrs = kwargs.pop('lemma_attrs')

        if 'entry_hash' in lemma_attrs:
            entry_hash_filter = lemma_attrs.pop('entry_hash')
        else:
            entry_hash_filter = False

        for k, v in kwargs.iteritems():
            if k in self.morphology_kwarg_names:
                morph_kwargs[k] = v

        for k, v in kwargs.iteritems():
            if k in self.lexicon_kwarg_names:
                lex_kwargs[k] = v

        # TODO: if analyses dropping componuds results in lexicalized
        # form that does not exist in lexicon, then fall back to
        # compounds?

        # TODO: to hide more_info link properly, we still need to know
        # what information has been stripped away in morph_kwargs and
        # lex_kwargs, so a count of discarded results for at least one
        # of these would be good.  -- alternative is to run the lookup
        # twice, which might take too much time if someone's hitting
        # detail frequently.

        analyzer = self.analyzers.get(source_lang)
        try:
            analyses = analyzer.lemmatize(wordform, **morph_kwargs)
        except AttributeError:
            analyses = []
            analyses_right = []

        return_raw_data = morph_kwargs.get('return_raw_data', False)
        raw_output = ''
        raw_errors = ''

        if return_raw_data and analyses:
            analyses, raw_output, raw_errors, analyses_right = analyses
        else:
            analyses_right = analyses

        # if analyses:
        #     lookup_lemmas = [l.lemma for l in analyses]
        # else:
        #     analyses = []

        entries_and_tags = []
        entries_and_tags_right = []

        if analyses:
            for analysis in list(analyses):
                if isinstance(analysis, list):
                    if analysis[0].lemma:
                        lex_kwargs = {
                            'lemma': analysis[0].lemma,
                            'pos': analysis[0].pos,
                            'pos_type': False,
                            'user_input': wordform,
                        }
                    else:
                        continue
                else:
                    if analysis:
                        lex_kwargs = {
                            'lemma': analysis.lemma,
                            'pos': analysis.pos,
                            'pos_type': False,
                            'user_input': wordform,
                        }
                    else:
                        continue


                xml_result = self.lexicon.variant_lookup( source_lang
                                                        , target_lang
                                                        , search_type
                                                        , **lex_kwargs
                                                        )
                if xml_result:
                    for e in xml_result:
                        entries_and_tags.append((e, analysis))
                else:
                    entries_and_tags.append((None, analysis))

        if analyses_right:
            #for analysis in list(set(analyses)):
            for analysis_r in list(analyses_right):
                if isinstance(analysis_r, list):
                    if analysis_r[0].lemma:
                        lex_kwargs_right = {
                            'lemma': analysis_r[0].lemma,
                            'pos': analysis_r[0].pos,
                            'pos_type': False,
                            'user_input': wordform,
                        }
                    else:
                        continue
                else:
                    if analysis_r:
                        lex_kwargs_right = {
                            'lemma': analysis_r.lemma,
                            'pos': analysis_r.pos,
                            'pos_type': False,
                            'user_input': wordform,
                        }
                    else:
                        continue


                xml_result_right = self.lexicon.lookup( source_lang
                                                , target_lang
                                                , **lex_kwargs_right
                                                )

                if xml_result_right:
                    for e in xml_result_right:
                        entries_and_tags_right.append((e, analysis_r))
                else:
                    entries_and_tags_right.append((None, analysis_r))


        no_analysis_xml = self.lexicon.variant_lookup( source_lang
                                                     , target_lang
                                                     , search_type
                                                     , wordform
                                                     , lemma_attrs=lemma_attrs
                                                     , user_input=wordform
                                                     )

        if no_analysis_xml:
            for e in no_analysis_xml:
                entries_and_tags.append((e, None))
                entries_and_tags_right.append((e, None))

        if entry_hash_filter:
            def filt((x, _)):
                if x is not None:
                    return hash_node(x) == entry_hash_filter
                return True
            entries_and_tags = filter(filt, entries_and_tags)

        # group by entry

        results = []
        results_right = []
        _by_entry = itemgetter(0)
        _by_entry_r = itemgetter(0)
        #Entries were previously sorted alphabetically
        #sorted_grouped_entries = groupby(
        #    sorted(entries_and_tags, key=_by_entry),
        #    _by_entry)

        def collect_same_lemma(array):
            #Collect same lemma in original order
            global array_sorted
            array_sorted = []
            k = 0
            l = []
            l0 = []
            none_not_added = True
            while k < len(array):
                for i in range(0, len(array)):
                    if (array[i][1] != None) & (array[k][1] != None):
                        if array[i][0] == array[k][0]:
                            if array[i] not in l:
                                array_sorted.append(array[i])
                                l.append(array[i])
                                l0.append(array[i][0])
                    else:
                        if (none_not_added) & (array[i][0] not in l0):
                            array_sorted.append(array[i])
                            none_not_added = False
                k += 1
            j = 0
            #In case there is the same entry twice (with and without analyses), remove the one without analyses
            while j < len(array_sorted):
                for i in range(0, len(array_sorted)):
                    if (array_sorted[i][0] == array_sorted[j][0]):
                        if (array_sorted[i][1] is not None) & (array_sorted[j][1] is None):
                            del array_sorted[j]
                            break
                        else:
                            if (array_sorted[j][1] is not None) & (array_sorted[i][1] is None):
                                del array_sorted[i]
                                break
                j += 1
            return array_sorted


        entries_and_tags_sorted = collect_same_lemma(entries_and_tags)
        sorted_grouped_entries = groupby(entries_and_tags_sorted, _by_entry)

        for grouper, grouped in sorted_grouped_entries:
            analyses = [an for _, an in grouped if an is not None]
            results.append((grouper, analyses))
        entries_and_tags = results


        entries_and_tags_sorted_r = collect_same_lemma(entries_and_tags_right)
        sorted_grouped_entries_r = groupby(entries_and_tags_sorted_r, _by_entry_r)

        for grouper, grouped in sorted_grouped_entries_r:
            analyses_r = [an for _, an in grouped if an is not None]
            results_right.append((grouper, analyses_r))
        entries_and_tags_right = results_right


        # TODO: may need to do the same for derivation?
        # NOTE: test with things that will never return results just to
        # make sure recursion doesn't get carried away.
        _ret = None
        if (len(entries_and_tags) == 0) and ('non_compound_only' in kwargs):
            if kwargs['non_compound_only']:
                new_kwargs = kwargs.copy()
                new_kwargs.pop('non_compound_only')
                _ret = self.lookup(wordform, **new_kwargs)
            else:
                _ret = []
        elif (len(entries_and_tags) == 0) and not analyses:
            _ret = MorphoLexiconResult([])
        else:
            _ret = MorphoLexiconResult(entries_and_tags)

        ret_right = None
        if (len(entries_and_tags_right) == 0) and ('non_compound_only' in kwargs):
            if kwargs['non_compound_only']:
                new_kwargs = kwargs.copy()
                new_kwargs.pop('non_compound_only')
                ret_right = self.lookup(wordform, **new_kwargs)
            else:
                ret_right = []
        elif (len(entries_and_tags_right) == 0) and not analyses_right:
            ret_right = MorphoLexiconResult([])
        else:
            ret_right = MorphoLexiconResult(entries_and_tags_right)


        if return_raw_data:
            return _ret, raw_output, raw_errors, ret_right
        else:
            return _ret, ret_right
