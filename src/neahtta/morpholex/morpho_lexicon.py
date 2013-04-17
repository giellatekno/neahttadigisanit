### Morpho-Lexical interface
###

# TODO: do not display analyzed lexical entries for words with mini-paradigms,
# e.g., lemma_ref contents should be stripped.

# Will need to operate on the output of lookup(), and this is language
# specific, so decorator registry thing is probably good here.

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


# if __name__ == "__main__":
#     from neahtta import app
# 
#     from lexicon import SimpleJSON
# 
#     tests = [
#         # 'jietnadeapmi',
#         # 'lahka',
#         # 'dahkat',
#         # 'diehtit',
#         # u'oađđit',
#         # u'spábbačiekčangilvu',
#         u'juovlaspábbačiekčangilvu',
#         u'diehtosátnegirji'
#     ]
# 
#     morph_kwargs = {
#         'source_lang': 'sme',
#         'target_lang': 'nob',
# 
#         'split_compounds': True,
#         'non_compound_only': True,
#         'no_derivations': True,
#     }
# 
#     mlex = MorphoLexicon(app.config)
#     for test in tests:
#         xml_nodes, tags = mlex.lookup(test, **morph_kwargs)
#         print xml_nodes
#         print list(SimpleJSON(xml_nodes))
#     raw_input()
# 
#     tests = [
#         'vite',
#         u'nær',
#         'gjøre',
#         'uttale',
#     ]
# 
#     morph_kwargs = {
#         'source_lang': 'nob',
#         'target_lang': 'sme',
# 
#         'split_compounds': True,
#         'non_compound_only': True,
#         'no_derivations': True,
#     }
# 
#     mlex = MorphoLexicon(app.config)
#     for test in tests:
#         xml_nodes = mlex.lookup(test, **morph_kwargs)
#         print list(SimpleJSON(xml_nodes))
#     raw_input()
# 
#     tests = [
#         u'aehtjaahka',
#         u'gööktesh',
#         u'göövtedh',
#     ]
# 
#     morph_kwargs = {
#         'source_lang': 'sma',
#         'target_lang': 'nob',
# 
#         'split_compounds': True,
#         'non_compound_only': True,
#         'no_derivations': True,
#     }
# 
#     mlex = MorphoLexicon(app.config)
#     for test in tests:
#         xml_nodes = mlex.lookup(test, **morph_kwargs)
#         pres_kwargs = {'target_lang': morph_kwargs.get('target_lang')}
#         print list(SimpleJSON(xml_nodes, **pres_kwargs))
#     raw_input()


