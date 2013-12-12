# -*- encoding: utf-8 -*-

import os
import unittest
import tempfile

from .lexicon import ( WordLookupDetailTests
                     , WordLookupAPITests
                     , WordLookupAPIDefinitionTests
                     )

# These should not produce a 404.

wordforms_that_shouldnt_fail = [
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

    # мортъясыԍ       морт+N+Pl+Ela
    # мортлаԋ 
    #       морсъяслысь         морс

    # testing that molotsov orthography works and returns lookups 
    ( ('kpvS', 'fin'), u'морсјаслыԍ', u'mehu'),
    ( ('kpvS', 'fin'), u'морсъяслысь', u'mehu'),
    ( ('kpvS', 'fin'), u'мортлаԋ', u'ihminen'),
    ( ('kpvS', 'fin'), u'бюҗет', u'budjetti'),

]

class WordLookupAPIDefinitionTests(WordLookupAPIDefinitionTests):
	definition_exists_tests = definition_exists_tests

class WordLookupDetailTests(WordLookupDetailTests):
	wordforms_that_shouldnt_fail = wordforms_that_shouldnt_fail

class WordLookupAPITests(WordLookupAPITests):
	wordforms_that_shouldnt_fail = wordforms_that_shouldnt_fail
