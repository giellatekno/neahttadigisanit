# -*- encoding: utf-8 -*-

import os
import neahtta
import unittest
import tempfile

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


# TODO: testcase for null lookup-- is returning 500 but should not be,
# but also need to make sure this fix sticks around.

#   /lookup/sme/nob/?callback=jQuery3094203984029384&lookup=&lemmatize=true

# TODO: use api lookups to determine that rule overrides are formatting
# things correctly


class WordLookupTests(unittest.TestCase):

    def setUp(self):
        _app = neahtta.app
        # Turn on debug to disable SMTP logging
        _app.debug = True
        _app.logger.removeHandler(_app.logger.smtp_handler)

        # Disable caching
        _app.caching_enabled = False
        self.app = _app.test_client()

    def test_api_null_lookup(self):
        """ Test that a null lookup to the api doesn't return a 500
        """
        url = "/lookup/sma/nob/?callback=jQuery3094203984029384&lookup=&lemmatize=true"

        rv = self.app.get(url)
        self.assertEqual(rv.status_code, 200)

    def test_api_lookup(self):
        """ Test that a null lookup to the api doesn't return a 500
        """
        url = "/lookup/sma/nob/?callback=jQuery3094203984029384&lookup=mannat&lemmatize=true"

        rv = self.app.get(url)
        self.assertEqual(rv.status_code, 200)

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

    def test_all_words_for_no_404s(self):
        for lang_pair, form in wordforms_that_shouldnt_fail[1::]:
            print "testing: %s / %s" % (repr(lang_pair), repr(form))
            base = '/%s/%s/' % lang_pair
            rv = self.app.post(base, data={
                'lookup': form,
            })

            self.assertEqual(rv.status_code, 200)

