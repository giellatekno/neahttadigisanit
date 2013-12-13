# -*- encoding: utf-8 -*-

import os
import neahtta
import unittest
import tempfile

from .lexicon import ( BasicTests
                     , WordLookupTests
                     , WordLookupDetailTests
                     , WordLookupAPITests
                     , WordLookupAPIDefinitionTests
                     )

wordforms_that_shouldnt_fail = [
    ( ('sma', 'nob'), 'mijjieh'),
    ( ('sma', 'nob'), 'mijjese'),

    ( ('nob', 'sma'), 'drikke'),
    ( ('nob', 'sma'), 'forbi'),
    ( ('nob', 'sma'), 'stige'),

    # test that nob->sma placenames work with nynorsk
    ( ('nob', 'sma'), 'Noreg'),
    ( ('nob', 'sma'), 'Norge'),
    ( ('nob', 'sma'), 'skilnad'),

    # placenames returned
    ( ('sma', 'nob'), 'Röörovse'),

    # misc inflections
    ( ('sma', 'nob'), 'jovkedh'),
    ( ('sma', 'nob'), 'jovkem'),


]


definition_exists_tests = [
    #  lang    pair    search    definition lemmas
    #                            

    # test hid works: guvlieh is unambiguously høre, govloeh is
    # unambiguously hørest
    ( ('sma', 'nob'), u'guvlieh', u'høre'),
    ( ('sma', 'nob'), u'govloeh', u'høres'),
]

# TODO: testcase for null lookup-- is returning 500 but should not be,
# but also need to make sure this fix sticks around.

#   /lookup/sme/nob/?callback=jQuery3094203984029384&lookup=&lemmatize=true

# TODO: use api lookups to determine that rule overrides are formatting
# things correctly


class BasicTests(BasicTests):

    def test_single_word(self):
        """ Test that the basic idea of testing will work.
            If there's a problem here, this is a problem. ;)
        """
        lang_pair, form = wordforms_that_shouldnt_fail[0]

        base = '/%s/%s/' % lang_pair
        rv = self.app.post(base, data={
            'lookup': form,
        })

        assert 'mijjieh' in rv.data
        assert u'vi' in rv.data.decode('utf-8')
        self.assertEqual(rv.status_code, 200)


class WordLookupAPIDefinitionTests(WordLookupAPIDefinitionTests):
	definition_exists_tests = definition_exists_tests

class WordLookupDetailTests(WordLookupDetailTests):
	wordforms_that_shouldnt_fail = wordforms_that_shouldnt_fail

class WordLookupAPITests(WordLookupAPITests):
	wordforms_that_shouldnt_fail = wordforms_that_shouldnt_fail
