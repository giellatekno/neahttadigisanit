# -*- encoding: utf-8 -*-

# gatáa.ang ñasa'áa

from __future__ import absolute_import
import os
import tempfile
import unittest

from .lexicon import (WordLookupAPIDefinitionTests, WordLookupAPITests,
                      WordLookupDetailTests)

# These should not produce a 404.

wordforms_that_shouldnt_fail = [
    (('hdn', 'eng'), u'gántl'),
]

# These forms should have a matching definition, i.e., <väli> must be a
# possible definition of <ло>

# With these tests, there is not as big of a need to be extensive, as
# much as making sure that there are tests for a larger variety of types
# of words, to make sure that the FST lines up with the lexicon.

# NB: make sure word strings are unicode, marked with u.

definition_exists_tests = [
    #  lang    pair    search    definition lemmas
    #

    # test that spaces and periods work
    (('hdn', 'eng'), u"gatáa.ang ñasa'áa", "for S to eat"),
    (('hdn', 'eng'), u"kíl is", "for S to tell C to stay in location"),
    (('hdn', 'eng'), u"skyáahl'uuj",
     u'for S to be lucky [said of a man or of hunting/fishing tools (but not a gun)]'
     ),
    (('hdn', 'eng'), u"skyáahläsaa.ang",
     u'for S to be lucky [said of a man or of hunting/fishing tools (but not a gun)]'
     ),
]

# paradigm_generation_tests = [
#     # source, target, lemma, error_msg, paradigm_test
#
# ###  - V:
#     ('kpv', 'fin', u'мунны',
#             "kpv verbs not generating",
#             form_contains(set([u"муна"]))),
#
# ###  - N + context="bivttas":  heittot
# ###     - http://localhost:5000/detail/sme/nob/heittot.html
#
#     ('kpv', 'fin', u'морс',
#             "kpv nouns not generating",
#             form_contains(set([u"морслӧн"]))),
#
# ]


class WordLookupAPIDefinitionTests(WordLookupAPIDefinitionTests):
    definition_exists_tests = definition_exists_tests


class WordLookupDetailTests(WordLookupDetailTests):
    wordforms_that_shouldnt_fail = wordforms_that_shouldnt_fail


class WordLookupAPITests(WordLookupAPITests):
    wordforms_that_shouldnt_fail = wordforms_that_shouldnt_fail


# class ParadigmGenerationTests(ParadigmGenerationTests):
#     paradigm_generation_tests = paradigm_generation_tests
