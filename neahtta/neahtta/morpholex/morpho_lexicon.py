"""
"Morpho-Lexical" interface. That is, "morphologial" and "lexical"
functionality "working together". This is basically the entry point to
searches, and it will call into functionality in "Morphology" for FST-related
tasks. Likewise when it comes to reading xml dictionaries, that's the
"Lexical" part.
"""

# TODO: do not display analyzed lexical entries for words with mini-paradigms,
# e.g., lemma_ref contents should be stripped.

# Will need to operate on the output of lookup(), and this is language
# specific, so decorator registry thing is probably good here.

from collections import defaultdict
from itertools import groupby
from operator import itemgetter
from typing import Optional

from neahtta.nds_lexicon.lexicon import hash_node
from neahtta.morphology.morphology import Lemma


class MorphoLexiconOverrides:
    def __init__(self):
        self.override_functions = defaultdict(list)

    def override_results(self, function):
        """This runs the morpholex lookup, and passes the output
        through the a set of functions to process the output.
        """

        def decorate(wordform, **input_kwargs):
            _from = input_kwargs.get("source_lang")

            entries_and_tags, stdout, stderr = function(wordform, **input_kwargs)

            for override_function in self.override_functions[_from]:
                new_res = override_function(entries_and_tags)
                if new_res is not None:
                    entries_and_tags = new_res
                else:
                    continue

            return MorphoLexiconResult(entries_and_tags), stdout, stderr

        return decorate

    def post_morpho_lexicon_override(self, *language_isos):
        """Use this function to register functions as part of this
        override"""

        def wrapper(override_function):
            for language_iso in language_isos:
                self.override_functions[language_iso].append(override_function)
                print(
                    "%s morpholex overrides: registered - %s"
                    % (language_iso, override_function.__name__)
                )

        return wrapper


morpholex_overrides = MorphoLexiconOverrides()


class MorphoLexiconResult(list):
    """A subclass of the List object meant to make sorting through
    results more readable."""

    @property
    def analyses(self):
        """Return a list of Lemma objects for each entry result"""
        return sum(list(map(itemgetter(1), self)), [])

    @property
    def entries(self):
        """Return a list of entry objects for each entry result"""
        return list(map(itemgetter(0), self))


class MorphoLexicon:
    morphology_kwarg_names = [
        "split_compounds",
        "non_compound_only",
        "no_derivations",
    ]

    lexicon_kwarg_names = [
        "source_lang",
        "target_lang",
        "lemma",
        "pos",
        "pos_type",
        "entry_hash",
    ]

    def __init__(self, config):
        self.analyzers = config.morphologies
        self.lexicon = config.lexicon
        self.lookup = morpholex_overrides.override_results(self.lookup)

    # Create a list where the lexc_kwargs are unique
    # all_lex_kwargs is a generator of tuples ({**lexc_kwargs}, Lemma())
    # Returns a list of 2-tuples (x, y), where
    #    x == {**lexckwargs}
    #    y == [Lemma(), Lemma(), ...]
    @staticmethod
    def make_unique_lexc_kwargs(all_lex_kwargs):
        unique_kwargs_dict = {}
        for lexc_kwargs, analysis in all_lex_kwargs:
            # ad hoc hashing
            key = (
                lexc_kwargs["lemma"]
                + lexc_kwargs["pos"]
                + str(lexc_kwargs["pos_type"])
                + lexc_kwargs["user_input"]
            )
            if key not in unique_kwargs_dict:
                unique_kwargs_dict[key] = {
                    "lexc_kwargs": lexc_kwargs,
                    "analyses": [analysis],
                }
            else:
                unique_kwargs_dict[key]["analyses"].append(analysis)
        unique_kwargs = []
        for id in unique_kwargs_dict:
            unique_kwargs.append(
                (
                    unique_kwargs_dict[id]["lexc_kwargs"],
                    unique_kwargs_dict[id]["analyses"],
                )
            )
        return unique_kwargs

    @staticmethod
    def make_lex_kwargs(wordform, analysis: Lemma):
        assert isinstance(analysis, Lemma)
        if isinstance(analysis, list):
            if analysis[0].lemma:
                d = {
                    "lemma": analysis[0].lemma,
                    "pos": analysis[0].pos,
                    "pos_type": False,
                    "user_input": wordform,
                }
                return d, analysis
        else:
            if analysis:
                d = {
                    "lemma": analysis.lemma,
                    "pos": analysis.pos,
                    "pos_type": False,
                    "user_input": wordform,
                }
                return d, analysis

    @staticmethod
    def add_to_dict(entries_and_tags, entry, analyses):
        if not entries_and_tags.get(entry):
            entries_and_tags[entry] = list()
        for analysis in analyses:
            if analysis not in entries_and_tags[entry]:
                entries_and_tags[entry].append(analysis)

    def make_xml_result(
        self, source_lang, target_lang, lex_kwargs, analyses, entries_and_tags
    ):
        xml_result = self.lexicon.lookup(source_lang, target_lang, **lex_kwargs)
        if xml_result:
            for entry in xml_result:
                self.add_to_dict(entries_and_tags, entry, analyses)
        else:
            self.add_to_dict(entries_and_tags, None, analyses)

    def _analyze(
        self,
        lang,
        wordform,
        morph_kwargs,
        also_capitalized=True,
    ):
        """Call the underlying analyzer for language `lang` on the input
        `wordform`. Additional arguments to the analyzer is in `morph_kwargs`.
        Returns a 3-tuple of (analyses, stdout, stderr), where
          analyses is ... (what?)
          stdout is a string of the "raw output" from the analysis tool
          stderr is a string of the standard error from the analysis tool
        """
        wordform = wordform.strip()
        if not wordform:
            return [], "", ""

        try:
            analyzer = self.analyzers[lang]
        except KeyError:
            # anders: this shouldn't happen, because it's checked at startup
            print(f"NO ANALYSER FOUND FOR LANGUAGE {lang}")
            return [], "", ""

        analyses, raw_output, raw_errors = analyzer.lemmatize(wordform, **morph_kwargs)

        # Lookup capitalized variant as well
        # Cannot use title() because it thinks all non-alphabet characters are
        # word boundaries (hyphens, apostrophes and combining macrons)
        if also_capitalized and not wordform[0].isupper():
            wordform = wordform[0].upper() + wordform[1:]
            uppercase_analysis = analyzer.lemmatize(wordform, **morph_kwargs)
            up_analyses, up_raw_output, up_raw_errors = uppercase_analysis

            if analyses:
                analyses.extend(up_analyses)
                raw_output += up_raw_output
                raw_errors += up_raw_errors
            else:
                analyses = up_analyses
                raw_output = up_raw_output
                raw_errors = up_raw_errors

        return analyses, raw_output, raw_errors

    def lookup(
        self,
        wordform: str,
        source_lang: str,
        target_lang: str,
        lemma: Optional[str] = None,
        pos: Optional[str] = None,
        entry_hash: Optional[int] = None,
        **kwargs,
    ):
        """Performs a lookup with morphology and lexicon working
        together.

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
        """
        lemma_attrs = kwargs.pop("lemma_attrs", {})
        entry_hash_filter = lemma_attrs.pop("entry_hash", None)
        morph_kwargs = {
            key: value
            for key, value in kwargs.items()
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

        analyses, raw_output, raw_errors = self._analyze(
            source_lang,
            wordform,
            morph_kwargs,
        )

        # Lookup of lemmas returned from fst lookup
        entries_and_tags = defaultdict(list)

        # Look up each analysed form in the dictionary, but only one lookup
        # per unique instance of (lemma, pos) from analyses
        # seen = set()
        # for analysis in analyses:
        #    assert isinstance(analysis, Lemma)
        #    key = (analysis.lemma, analysis.pos)
        #    if key not in seen:
        #        seen.add(key)
        #        entries = self.lexicon.lookup(
        #            source_lang,
        #            target_lang,
        #            lemma=analysis.lemma,
        #            pos=analysis.pos,
        #            pos_type=False,
        #            user_input=wordform,
        #        )
        #        for entry in entries:
        #            entries_and_tags[entry].append(analysis)

        # anders: I don't understand this code. The commented-out code above
        # was an attempt to do the same, but with simpler code, but it did
        # not replicate the results exactly, some details were missing.
        # ----
        if analyses:
            all_lex_kwargs = (
                self.make_lex_kwargs(wordform, analysis) for analysis in analyses
            )
            unique_lexc_kwargs = self.make_unique_lexc_kwargs(all_lex_kwargs)
            for lexc_kwargs, analyses in unique_lexc_kwargs:
                entries = self.lexicon.lookup(source_lang, target_lang, **lexc_kwargs)
                assert isinstance(entries, list), "Lexicon.lookup() returns a list"
                for entry in entries:
                    entries_and_tags[entry].extend(analyses)

                self.make_xml_result(
                    source_lang, target_lang, lexc_kwargs, analyses, entries_and_tags
                )

        plain_input_lookup_results = self.lexicon.lookup(
            source_lang,
            target_lang,
            wordform,
            lemma_attrs=lemma_attrs,
            user_input=wordform,
        )

        # manually set the entry if it doesn't exist, for the loop below
        for entry in plain_input_lookup_results:
            entries_and_tags.setdefault(entry, [])

        # prune all other entries if we're looking for one specific one
        if entry_hash_filter:
            for node in list(entries_and_tags.keys()):
                # anders: None can be in the list, but it feels like it should
                # not be able to.
                # assert node is not None, "None is not a key in entries_and_tags"
                if node is not None and (hash_node(node) != entry_hash_filter):
                    del entries_and_tags[node]

        if (not entries_and_tags) and ("non_compound_only" in kwargs):
            if kwargs["non_compound_only"]:
                new_kwargs = kwargs.copy()
                new_kwargs.pop("non_compound_only")
                _ret = self.lookup(wordform, **new_kwargs)
            else:
                _ret = []
        elif not entries_and_tags and not analyses:
            _ret = MorphoLexiconResult()
        else:
            _ret = MorphoLexiconResult(entries_and_tags.items())

        return _ret, raw_output, raw_errors

    def variant_lookup(
        self, search_type, wordform, source_lang: str, target_lang: str, **kwargs
    ):
        """Performs a lookup with morphology and lexicon working
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
        """
        lemma_attrs = kwargs.pop("lemma_attrs", {})
        entry_hash_filter = lemma_attrs.pop("entry_hash", None)
        morph_kwargs = {
            key: value
            for key, value in kwargs.items()
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

        # lookup() does this:
        # analyses, raw_output, raw_errors = self._analyze(
        #     source_lang,
        #     wordform,
        #     morph_kwargs,
        #     also_capitalized=False,
        # )
        analyzer = self.analyzers.get(source_lang)
        try:
            analyses, raw_output, raw_errors = analyzer.lemmatize(
                wordform, **morph_kwargs
            )
        except AttributeError:
            import traceback

            traceback.print_exc()
            analyses = None

        if analyses:
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
                            "lemma": analysis[0].lemma,
                            "pos": analysis[0].pos,
                            "pos_type": False,
                            "user_input": wordform,
                        }
                    else:
                        continue
                else:
                    if analysis:
                        lex_kwargs = {
                            "lemma": analysis.lemma,
                            "pos": analysis.pos,
                            "pos_type": False,
                            "user_input": wordform,
                        }
                    else:
                        continue

                xml_result = self.lexicon.variant_lookup(
                    source_lang, target_lang, search_type, **lex_kwargs
                )
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
                            "lemma": analysis_r[0].lemma,
                            "pos": analysis_r[0].pos,
                            "pos_type": False,
                            "user_input": wordform,
                        }
                    else:
                        continue
                else:
                    if analysis_r:
                        lex_kwargs_right = {
                            "lemma": analysis_r.lemma,
                            "pos": analysis_r.pos,
                            "pos_type": False,
                            "user_input": wordform,
                        }
                    else:
                        continue

                xml_result_right = self.lexicon.lookup(
                    source_lang, target_lang, **lex_kwargs_right
                )

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
            user_input=wordform,
        )

        if no_analysis_xml:
            for entry in no_analysis_xml:
                entries_and_tags.append((entry, None))
                entries_and_tags_right.append((entry, None))

        if entry_hash_filter:
            # for node in list(entries_and_tags.keys()):
            #     if node is None:
            #         continue
            #     if hash_node(node) != entry_hash_filter:
            #         del entries_and_tags[node]

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
                        if (none_not_added) & (array[index2][0] not in lemmas0):
                            array_sorted.append(array[index2])
                            none_not_added = False
                index += 1
            index3 = 0
            # In case there is the same entry twice (with and without analyses), remove the one without analyses
            while index3 < len(array_sorted):
                for index2 in range(0, len(array_sorted)):
                    if array_sorted[index2][0] == array_sorted[index3][0]:
                        if (array_sorted[index2][1] is not None) & (
                            array_sorted[index3][1] is None
                        ):
                            del array_sorted[index3]
                            break
                        else:
                            if (array_sorted[index3][1] is not None) & (
                                array_sorted[index2][1] is None
                            ):
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
        sorted_grouped_entries_r = groupby(entries_and_tags_sorted_r, _by_entry_r)

        for grouper, grouped in sorted_grouped_entries_r:
            analyses_r = [an for _, an in grouped if an is not None]
            results_right.append((grouper, analyses_r))
        entries_and_tags_right = results_right

        # TODO: may need to do the same for derivation?
        # NOTE: test with things that will never return results just to
        # make sure recursion doesn't get carried away.
        _ret = None
        if (len(entries_and_tags) == 0) and ("non_compound_only" in kwargs):
            if kwargs["non_compound_only"]:
                new_kwargs = kwargs.copy()
                new_kwargs.pop("non_compound_only")
                _ret = self.lookup(wordform, **new_kwargs)
            else:
                _ret = []
        elif (len(entries_and_tags) == 0) and not analyses:
            _ret = MorphoLexiconResult([])
        else:
            _ret = MorphoLexiconResult(entries_and_tags)

        if (len(entries_and_tags_right) == 0) and ("non_compound_only" in kwargs):
            if kwargs["non_compound_only"]:
                new_kwargs = kwargs.copy()
                new_kwargs.pop("non_compound_only")
                ret_right = self.lookup(wordform, **new_kwargs)
            else:
                ret_right = []
        elif (len(entries_and_tags_right) == 0) and not analyses_right:
            ret_right = MorphoLexiconResult([])
        else:
            ret_right = MorphoLexiconResult(entries_and_tags_right)

        return _ret, raw_output, raw_errors, ret_right
