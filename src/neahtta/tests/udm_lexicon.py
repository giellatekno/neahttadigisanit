# -*- encoding: utf-8 -*-

import os
import unittest
import tempfile

from .lexicon import (WordLookupDetailTests, WordLookupAPITests,
                      WordLookupAPIDefinitionTests, ParadigmGenerationTests,
                      form_contains, form_doesnt_contain)

# These should not produce a 404.

wordforms_that_shouldnt_fail = []

# These forms should have a matching definition, i.e., <väli> must be a
# possible definition of <ло>

# With these tests, there is not as big of a need to be extensive, as
# much as making sure that there are tests for a larger variety of types
# of words, to make sure that the FST lines up with the lexicon.

# NB: make sure word strings are unicode, marked with u.

definition_exists_tests = [
    #  lang    pair    search    definition lemmas
    #

    # ( ('udm', 'fin'), u'бюҗет', u'budjetti'),
]

paradigm_generation_tests = [
    # source, target, lemma, error_msg, paradigm_test

    ###  - V:
    # ('kpv', 'fin', u'мунны',
    #         "kpv verbs not generating",
    #         form_contains(set([u"муна"]))),

    ###  - N + context="bivttas":  heittot
    ###     - http://localhost:5000/detail/sme/nob/heittot.html

    # ('kpv', 'fin', u'морс',
    #         "kpv nouns not generating",
    #         form_contains(set([u"морслӧн"]))),
]


class WordLookupAPIDefinitionTests(WordLookupAPIDefinitionTests):
    definition_exists_tests = definition_exists_tests


class WordLookupDetailTests(WordLookupDetailTests):
    wordforms_that_shouldnt_fail = wordforms_that_shouldnt_fail


class WordLookupAPITests(WordLookupAPITests):
    wordforms_that_shouldnt_fail = wordforms_that_shouldnt_fail


class ParadigmGenerationTests(ParadigmGenerationTests):
    paradigm_generation_tests = paradigm_generation_tests
