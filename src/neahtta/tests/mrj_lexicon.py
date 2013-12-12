# -*- encoding: utf-8 -*-

import os
import unittest
import tempfile

# These should not produce a 404.

wordforms_that_shouldnt_fail = [
    ( ('mrj', 'fin'), u'ловка'),
    ( ('mrj', 'fin'), u'ломбы'),
    ( ('mrj', 'fin'), u'ло'),
]


# These forms should have a matching definition, i.e., <väli> must be a
# possible definition of <ло>

definition_exists_tests = [
    #  lang    pair    search    definition lemmas
    #                            
    ( ('mrj', 'fin'), u'ло', u'väli'),
    ( ('mrj', 'fin'), u'ло', u'kalastaa'),

    # ( ('mrj', 'fin'), u'ловка',  ''),

    # ( ('mrj', 'fin'), u'ломбы',  ''),

]

from .lexicon import ( WordLookupDetailTests
                     , WordLookupAPITests
                     , WordLookupAPIDefinitionTests
                     )

class WordLookupAPIDefinitionTests(WordLookupAPIDefinitionTests):
	definition_exists_tests = definition_exists_tests

class WordLookupDetailTests(WordLookupDetailTests):
	wordforms_that_shouldnt_fail = wordforms_that_shouldnt_fail

class WordLookupAPITests(WordLookupAPITests):
	wordforms_that_shouldnt_fail = wordforms_that_shouldnt_fail
