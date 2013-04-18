### Morpho-Lexical interface
###

# TODO: do not display analyzed lexical entries for words with mini-paradigms,
# e.g., lemma_ref contents should be stripped.

# Will need to operate on the output of lookup(), and this is language
# specific, so decorator registry thing is probably good here.

class MorphoLexiconOverrides(object):

    def override_results(self, function):
        """ This runs the morpholex lookup, and passes the output
        through the a set of functions to process the output.
        """
        def decorate(wordform, **input_kwargs):
            _from = input_kwargs.get('source_lang')

            xml_result, fst_result = function(wordform, **input_kwargs)

            for f in self.override_functions[_from]:
                new_res = f(xml_result, fst_result)
                if new_res is not None:
                    xml_result, fst_result = new_res
                else:
                    continue

            return xml_result, fst_result

        return decorate

    def post_morpho_lexicon_override(self, function):
        """ Registry function """
        def wrapper(override_function):
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

class MorphoLexicon(object):
    morphology_kwarg_names = [
        'split_compounds',
        'non_compound_only',
        'no_derivations',
    ]

    lexicon_kwarg_names = [
        'source_lang',
        'target_lang',
        'lemma',
        'pos',
        'pos_type',
    ]

    def lookup(self, wordform, **kwargs):
        source_lang = kwargs.get('source_lang')
        target_lang = kwargs.get('target_lang')

        morph_kwargs = {}

        for k, v in kwargs.iteritems():
            if k in self.morphology_kwarg_names:
                morph_kwargs[k] = v

        # TODO: if analyses dropping componuds results in lexicalized
        # form that does not exist in lexicon, then fall back to
        # compounds?
        analyzer = self.analyzers.get(source_lang)
        try:
            analyses = analyzer.lemmatize(wordform, **morph_kwargs)
        except AttributeError:
            analyses = []

        if analyses:
            lookup_lemmas = [l.lemma for l in analyses]
        else:
            analyses = []

        xml_results = []
        for analysis in list(set(analyses)):
            lex_kwargs = {
                'lemma': analysis.lemma,
                'pos': analysis.pos,
                'pos_type': False,
            }
            xml_result = self.lexicon.lookup( source_lang
                                            , target_lang
                                            , **lex_kwargs
                                            )
            if xml_result:
                xml_results.extend(xml_result)

        no_analysis_xml = self.lexicon.lookup( source_lang
                                             , target_lang
                                             , wordform
                                             )

        if no_analysis_xml:
            xml_results.extend(no_analysis_xml)

        # TODO: may need to do the same for derivation?
        # NOTE: test with things that will never return results just to
        # make sure recursion doesn't get carried away.
        if (len(xml_results) == 0) and ('non_compound_only' in kwargs):
            if kwargs['non_compound_only']:
                new_kwargs = kwargs.copy()
                new_kwargs.pop('non_compound_only')
                return self.lookup(wordform, **new_kwargs)
            else:
                return [], []
        elif (len(xml_results) == 0) and not analyses:
            return [], []
        else:
            return list(set(xml_results)), analyses

    def __init__(self, config):
        self.analyzers = config.morphologies
        self.lexicon = config.lexicon

        self.lookup = morpholex_overrides.override_results(
            self.lookup
        )
