# -*- encoding: utf-8 -*-

import os
import neahtta
import unittest
import tempfile

wordforms_that_shouldnt_fail = [
    ( ('sme', 'nob'), 'sihke'),
    ( ('sme', 'nob'), 'mannat'),
    ( ('sme', 'nob'), 'manai'),
    ( ('sme', 'nob'), u'Gállábártnit'),

    ( ('nob', 'sme'), 'drikke'),
    ( ('nob', 'sme'), 'forbi'),
    ( ('nob', 'sme'), 'stige'),

    # This one contains a blank definition node, but translations.
    ( ('nob', 'sme'), 'sette'),

    # Copied some words from a previous test log. May need to go through
    # these and do things about results instead of just testing that
    # 404s and 500s aren't returned

    # Test that SoMe paths work
    ( ('SoMe', 'nob'), 'geahcci'),
    ( ('SoMe', 'nob'), 'leazzaba'),
    ( ('SoMe', 'nob'), 'leažžaba'),
    ( ('SoMe', 'nob'), 'munnuide'),

    # Test that finn paths work: TODO: -- ensure analysis returned?
    ( ('fin', 'sme'), 'menijä'),
    ( ('fin', 'sme'), 'menijää'),
    ( ('fin', 'sme'), 'menisi'),
    ( ('fin', 'sme'), 'mennä'),

    # test that nob->sme placenames work
    ( ('nob', 'sme'), 'Austerrike'),
    ( ('nob', 'sme'), 'Noreg'),
    ( ('nob', 'sme'), 'austerrikisk'),
    ( ('nob', 'sme'), 'skilnad'),
    ( ('nob', 'sme'), 'Østerrike'),
    ( ('nob', 'sme'), 'Aust-Noreg'),

    # sme->fin 
    ( ('sme', 'fin'), 'leažžaba'),

    # placenames returned
    ( ('sme', 'nob'), 'Gálbbejávrrit'),
    ( ('sme', 'nob'), 'Gállábártnit'),

    # misc inflections
    ( ('sme', 'nob'), 'diehtit'),
    ( ('sme', 'nob'), 'girjaide'),
    ( ('sme', 'nob'), 'girji'),
    ( ('sme', 'nob'), 'girjiide'),
    ( ('sme', 'nob'), 'girjjaid'),
    ( ('sme', 'nob'), 'girjjaide'),
    ( ('sme', 'nob'), 'girjjiide'),
    ( ('sme', 'nob'), 'guovdageaidnulaš'),
    ( ('sme', 'nob'), 'leaččan'),
    ( ('sme', 'nob'), 'leažžaba'),
    ( ('sme', 'nob'), 'manai'),
    ( ('sme', 'nob'), 'manan'),
    ( ('sme', 'nob'), 'mannat'),
    ( ('sme', 'nob'), 'moai'),
    ( ('sme', 'nob'), 'muinna'),
    ( ('sme', 'nob'), 'mun'),
    ( ('sme', 'nob'), 'munnje'),
    ( ('sme', 'nob'), 'munnos'),
    ( ('sme', 'nob'), 'munnuide'),
    ( ('sme', 'nob'), 'mánnageahčči'),
    ( ('sme', 'nob'), 'mánná'),
    ( ('sme', 'nob'), 'neahkameahttun'),
    ( ('sme', 'nob'), 'sihke'),
    ( ('sme', 'nob'), 'sihkestan'),
    ( ('sme', 'nob'), 'sihkestit'),

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
        url = "/lookup/sme/nob/?callback=jQuery3094203984029384&lookup=&lemmatize=true"

        rv = self.app.get(url)
        self.assertEqual(rv.status_code, 200)

    def test_api_lookup(self):
        """ Test that a null lookup to the api doesn't return a 500
        """
        url = "/lookup/sme/nob/?callback=jQuery3094203984029384&lookup=mannat&lemmatize=true"

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

        assert 'sihke' in rv.data
        assert u'både' in rv.data.decode('utf-8')
        self.assertEqual(rv.status_code, 200)

    def test_all_words_for_no_404s(self):
        for lang_pair, form in wordforms_that_shouldnt_fail[1::]:
            print "testing: %s / %s" % (repr(lang_pair), repr(form))
            base = '/%s/%s/' % lang_pair
            rv = self.app.post(base, data={
                'lookup': form,
            })

            self.assertEqual(rv.status_code, 200)

    # def test_all_words_for_no_404s_detail_view(self):
    #     for lang_pair, form in wordforms_that_shouldnt_fail[1::]:
    #         _from, _to = lang_pair
    #         base = '/detail/%s/%s/%s.html' % (_from, _to, form)
    #         print "testing: %s " % base
    #         rv = self.app.get(base)

    #         self.assertEqual(rv.status_code, 200)
