# -*- encoding: utf-8 -*-

import os
import neahtta
import unittest
import tempfile

from .lexicon import (BasicTests, WordLookupTests, WordLookupDetailTests,
                      WordLookupAPITests, WordLookupAPIDefinitionTests,
                      ParadigmGenerationTests, form_contains,
                      form_doesnt_contain)

paradigm_generation_tests = [
    # source, target, lemma, error_msg, paradigm_test

    ###  - V:
    ('fin', 'sme', u'mennä', "Fin verbs not generating",
     form_doesnt_contain(set([u"menen"]))),

    ###  - N + context="bivttas":  heittot
    ###     - http://localhost:5000/detail/sme/nob/heittot.html
    ('fin', 'sme', u'kirja', "Fin nouns not generating",
     form_contains(set([u"kirjaa"]))),
]


class ParadigmGenerationTests(ParadigmGenerationTests):
    paradigm_generation_tests = paradigm_generation_tests


class ParadigmSelectionTest(WordLookupTests):
    """ These are really only for testing specifics in the paradigm
    directory structure the code, and don't need to be run as generation
    as a whole is tested above.
    """

    def test_misc_paradigms(self):
        from paradigms import ParadigmConfig

        lookups = self.current_app.morpholexicon.lookup(
            'mennä', source_lang='fin', target_lang='sme')

        pc = self.current_app.morpholexicon.paradigms
        # print self.current_app
        pc = ParadigmConfig(app=None, debug=True)
        for node, analyses in lookups:
            print "Testing: ", node, analyses
            # for a in analyses:
            #     print " - " + repr(a.tag.matching_tagsets())
            print pc.get_paradigm('fin', node, analyses, debug=True)
            print '--'
