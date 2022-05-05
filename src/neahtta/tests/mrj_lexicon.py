# -*- encoding: utf-8 -*-

from __future__ import absolute_import
import os
import tempfile
import unittest

from .lexicon import (ParadigmGenerationTests, WordLookupAPIDefinitionTests,
                      WordLookupAPITests, WordLookupDetailTests, form_contains,
                      form_doesnt_contain)

# These should not produce a 404.

wordforms_that_shouldnt_fail = [
    (('mrj', 'fin'), u'ловка'),
    (('mrj', 'fin'), u'ломбы'),
    (('mrj', 'fin'), u'ло'),
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
    (('mrj', 'fin'), u'ло', u'väli'),
    (('mrj', 'fin'), u'ло', u'kalastaa'),
    (('mrj', 'fin'), u'ловка', u'näppäryys'),
    (('mrj', 'fin'), u'ломбы', u'tuomi'),
]

paradigm_generation_tests = [
    # source, target, lemma, error_msg, paradigm_test

    ###  - V:
    ('mrj', 'fin', u'лӓктӓш', "mrj verbs not generating",
     form_contains(set([u"лӓктӓм", u"лӓктеш"]))),

    ###  - N + context="bivttas":  heittot
    ###     - http://localhost:5000/detail/sme/nob/heittot.html
    ('mrj', 'fin', u'книгӓ', "mrj nouns not generating",
     form_contains(set([u"книгӓн", u"книгӓге"]))),
]


class WordLookupAPIDefinitionTests(WordLookupAPIDefinitionTests):
    definition_exists_tests = definition_exists_tests


class WordLookupDetailTests(WordLookupDetailTests):
    wordforms_that_shouldnt_fail = wordforms_that_shouldnt_fail


class WordLookupAPITests(WordLookupAPITests):
    wordforms_that_shouldnt_fail = wordforms_that_shouldnt_fail


class ParadigmGenerationTests(ParadigmGenerationTests):
    paradigm_generation_tests = paradigm_generation_tests
