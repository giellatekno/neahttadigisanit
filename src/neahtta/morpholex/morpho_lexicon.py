### Morpho-Lexical interface
###

# TODO: do not display analyzed lexical entries for words with mini-paradigms,
# e.g., lemma_ref contents should be stripped.

# Will need to operate on the output of lookup(), and this is language
# specific, so decorator registry thing is probably good here.

from collections import defaultdict, OrderedDict
from itertools import groupby
from operator import itemgetter
from six import iteritems

from nds_lexicon.lexicon import hash_node


class MorphoLexiconOverrides(object):
    def __init__(self):
        self.override_functions = defaultdict(list)

    def override_results(self, function):
        """ This runs the morpholex lookup, and passes the output
        through the a set of functions to process the output.
        """

        def decorate(wordform, **input_kwargs):
            _from = input_kwargs.get('source_lang')
            raw_return = input_kwargs.get('return_raw_data', False)

            entries_and_tags = function(wordform, **input_kwargs)
            if raw_return:
                entries_and_tags, stdout, stderr = entries_and_tags
            else:
                entries_and_tags = entries_and_tags

            for override_function in self.override_functions[_from]:
                new_res = override_function(entries_and_tags)
                if new_res is not None:
                    entries_and_tags = new_res
                else:
                    continue

            if raw_return:
                return MorphoLexiconResult(entries_and_tags), stdout, stderr
            else:
                return MorphoLexiconResult(entries_and_tags)

        return decorate

    def post_morpho_lexicon_override(self, *language_isos):
        """ Use this function to register functions as part of this
        override """

        def wrapper(override_function):
            for language_iso in language_isos:
                self.override_functions[language_iso] \
                    .append(override_function)
                print('%s morpholex overrides: registered - %s' % \
                      (language_iso
                       , override_function.__name__
                       ))

        return wrapper


morpholex_overrides = MorphoLexiconOverrides()


class MorphoLexiconResult(list):
    """ A subclass of the List object meant to make sorting through
    results more readable.
    """

    @property
    def analyses(self):
        """ Return a list of Lemma objects for each entry result
        """
        return sum(list(map(itemgetter(1), self)), [])

    @property
    def entries(self):
        """ Return a list of entry objects for each entry result
        """
        return list(map(itemgetter(0), self))


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

    def __init__(self, config):
        self.analyzers = config.morphologies
        self.lexicon = config.lexicon

        self.lookup = morpholex_overrides.override_results(self.lookup)

    @staticmethod
    def make_lex_kwargs(wordform, analysis):
        if isinstance(analysis, list):
            if analysis[0].lemma:
                return {
                           'lemma': analysis[0].lemma,
                           'pos': analysis[0].pos,
                           'pos_type': False,
                           'user_input': wordform,
                       }, analysis
        else:
            if analysis:
                return {
                           'lemma': analysis.lemma,
                           'pos': analysis.pos,
                           'pos_type': False,
                           'user_input': wordform,
                       }, analysis

    @staticmethod
    def add_to_dict(entries_and_tags, entry, analysis):
        if not entries_and_tags.get(entry):
            entries_and_tags[entry] = list()
        if analysis not in entries_and_tags[entry]:
            entries_and_tags[entry].append(analysis)

    def make_xml_result(self, source_lang, target_lang, lex_kwargs, analysis,
                        entries_and_tags):
        xml_result = self.lexicon.lookup(source_lang, target_lang,
                                         **lex_kwargs)
        if xml_result:
            for entry in xml_result:
                self.add_to_dict(entries_and_tags, entry, analysis)
        else:
            self.add_to_dict(entries_and_tags, None, analysis)

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
        lemma_attrs = kwargs.pop('lemma_attrs', {})
        entry_hash_filter = lemma_attrs.pop('entry_hash', False)
        morph_kwargs = {
            key: value
            for key, value in iteritems(kwargs)
            if key in self.morphology_kwarg_names
        }

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

        return_raw_data = morph_kwargs.get('return_raw_data', False)
        raw_output = ''
        raw_errors = ''

        if return_raw_data and analyses:
            analyses, raw_output, raw_errors = analyses
        else:
            analyses = analyses

        # Lookup capitalized variant as well
        # Cannot use title() because it thinks all non-alphabet characters are word boundaries,
        # including hyphens, apostrophes and combining macrons
        if wordform and not wordform[0].isupper(): 
            try:
                uppercase_analyses = analyzer.lemmatize(wordform[0].upper() + wordform[1:], **morph_kwargs)
            except AttributeError:
                uppercase_analyses = []

            if analyses:
                if return_raw_data and uppercase_analyses:
                    if uppercase_analyses[0]:
                        analyses.extend(uppercase_analyses[0])
                    raw_output += uppercase_analyses[1]
                    raw_errors += uppercase_analyses[2]
                elif uppercase_analyses:
                    analyses.extend(uppercase_analyses)
            else:
                if return_raw_data and uppercase_analyses:
                    analyses, raw_output, raw_errors = uppercase_analyses
                else:
                    analyses = uppercase_analyses

        entries_and_tags = OrderedDict()
        if analyses:
            all_lex_kwargs = (self.make_lex_kwargs(wordform, analysis) for
                              analysis in list(analyses))
            for lexc_kwargs, analysis in all_lex_kwargs:
                self.make_xml_result(source_lang, target_lang, lexc_kwargs,
                                     analysis, entries_and_tags)

        no_analysis_xml = self.lexicon.lookup(
            source_lang,
            target_lang,
            wordform,
            lemma_attrs=lemma_attrs,
            user_input=wordform)

        if no_analysis_xml:
            for entry in no_analysis_xml:
                if not entries_and_tags.get(entry):
                    entries_and_tags[entry] = []

        if entry_hash_filter:
            for node in entries_and_tags.copy().keys(): # Copy as we cannot modify a dict during iteration
                if node is None or hash_node(node) != entry_hash_filter:
                    del entries_and_tags[node]

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
            _ret = MorphoLexiconResult(
                [(key, value) for key, value in iteritems(entries_and_tags)])

        if return_raw_data:
            return _ret, raw_output, raw_errors
        else:
            return _ret

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
        lemma_attrs = kwargs.pop('lemma_attrs', {})
        entry_hash_filter = lemma_attrs.pop('entry_hash', False)
        morph_kwargs = {
            key: value
            for key, value in iteritems(kwargs)
            if key in self.morphology_kwarg_names
        }

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

        return_raw_data = morph_kwargs.get('return_raw_data', False)
        raw_output = ''
        raw_errors = ''

        if return_raw_data and analyses:
            analyses, raw_output, raw_errors, analyses_right = analyses
        else:
            analyses, analyses_right = analyses

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

                xml_result = self.lexicon.variant_lookup(
                    source_lang, target_lang, search_type, **lex_kwargs)
                if xml_result:
                    for entry in xml_result:
                        entries_and_tags.append((entry, analysis))
                else:
                    entries_and_tags.append((None, analysis))

        if analyses_right:
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

                xml_result_right = self.lexicon.lookup(
                    source_lang, target_lang, **lex_kwargs_right)

                if xml_result_right:
                    for entry in xml_result_right:
                        entries_and_tags_right.append((entry, analysis_r))
                else:
                    entries_and_tags_right.append((None, analysis_r))

        no_analysis_xml = self.lexicon.variant_lookup(
            source_lang,
            target_lang,
            search_type,
            wordform,
            lemma_attrs=lemma_attrs,
            user_input=wordform)

        if no_analysis_xml:
            for entry in no_analysis_xml:
                entries_and_tags.append((entry, None))
                entries_and_tags_right.append((entry, None))

        if entry_hash_filter:

            def filt(tuple_to_unpack):
                (x, _) = tuple_to_unpack
                if x is not None:
                    return hash_node(x) == entry_hash_filter
                return True

            entries_and_tags = list(filter(filt, entries_and_tags))

        # group by entry

        results = []
        results_right = []
        _by_entry = itemgetter(0)
        _by_entry_r = itemgetter(0)

        def collect_same_lemma(array):
            # Collect same lemma in original order
            global array_sorted
            array_sorted = []
            index = 0
            lemmas = []
            lemmas0 = []
            none_not_added = True
            while index < len(array):
                for index2 in range(0, len(array)):
                    if (array[index2][1] != None) & (array[index][1] != None):
                        if array[index2][0] == array[index][0]:
                            if array[index2] not in lemmas:
                                array_sorted.append(array[index2])
                                lemmas.append(array[index2])
                                lemmas0.append(array[index2][0])
                    else:
                        if (none_not_added) & (
                                array[index2][0] not in lemmas0):
                            array_sorted.append(array[index2])
                            none_not_added = False
                index += 1
            index3 = 0
            # In case there is the same entry twice (with and without analyses), remove the one without analyses
            while index3 < len(array_sorted):
                for index2 in range(0, len(array_sorted)):
                    if (array_sorted[index2][0] == array_sorted[index3][0]):
                        if (array_sorted[index2][1] is
                            not None) & (array_sorted[index3][1] is None):
                            del array_sorted[index3]
                            break
                        else:
                            if (array_sorted[index3][1] is not None) & (
                                    array_sorted[index2][1] is None):
                                del array_sorted[index2]
                                break
                index3 += 1
            return array_sorted

        entries_and_tags_sorted = collect_same_lemma(entries_and_tags)
        sorted_grouped_entries = groupby(entries_and_tags_sorted, _by_entry)

        for grouper, grouped in sorted_grouped_entries:
            analyses = [an for _, an in grouped if an is not None]
            results.append((grouper, analyses))
        entries_and_tags = results

        entries_and_tags_sorted_r = collect_same_lemma(entries_and_tags_right)
        sorted_grouped_entries_r = groupby(entries_and_tags_sorted_r,
                                           _by_entry_r)

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

        if (len(entries_and_tags_right) == 0) and (
                'non_compound_only' in kwargs):
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
