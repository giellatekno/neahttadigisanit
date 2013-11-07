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

    ( ('SoMe', 'nob'), 'duddet'),
    ( ('SoMe', 'nob'), 'etter'),
    ( ('fin', 'sme'), 'huitaista'),
    ( ('fin', 'sme'), 'hänen kanssa'),
    ( ('fin', 'sme'), 'hänen kanssaan'),
    ( ('fin', 'sme'), 'kanssa'),
    ( ('fin', 'sme'), 'oppia'),
    ( ('fin', 'sme'), 'talo'),
    ( ('fin', 'sme'), 'vetää'),
    ( ('fin', 'sme'), 'yhdessä'),
    ( ('fin', 'sme'), 'ääni'),
    ( ('nob', 'sma'), 'mishandle'),
    ( ('nob', 'sme'), 'amanu'),
    ( ('nob', 'sme'), 'best'),
    ( ('nob', 'sme'), 'dag'),
    ( ('nob', 'sme'), 'deksel'),
    ( ('nob', 'sme'), 'deltaker'),
    ( ('nob', 'sme'), 'der'),
    ( ('nob', 'sme'), 'etter'),
    ( ('nob', 'sme'), 'fin'),
    ( ('nob', 'sme'), 'finne'),
    ( ('nob', 'sme'), 'fjæra'),
    ( ('nob', 'sme'), 'fjæreområde'),
    ( ('nob', 'sme'), 'gang'),
    ( ('nob', 'sme'), 'gå'),
    ( ('nob', 'sme'), 'ha'),
    ( ('nob', 'sme'), 'har'),
    ( ('nob', 'sme'), 'hvor'),
    ( ('nob', 'sme'), 'i dag'),
    ( ('nob', 'sme'), 'jente'),
    ( ('nob', 'sme'), 'lage'),
    ( ('nob', 'sme'), 'land'),
    ( ('nob', 'sme'), 'leamaw'),
    ( ('nob', 'sme'), 'lege'),
    ( ('nob', 'sme'), 'men'),
    ( ('nob', 'sme'), 'måned'),
    ( ('nob', 'sme'), 'måneder'),
    ( ('nob', 'sme'), 'ovdal'),
    ( ('nob', 'sme'), 'skatt'),
    ( ('nob', 'sme'), 'skatter'),
    ( ('nob', 'sme'), 'slå'),
    ( ('nob', 'sme'), 'som'),
    ( ('nob', 'sme'), 'søster'),
    ( ('nob', 'sme'), 'tekst'),
    ( ('nob', 'sme'), 'tilbe'),
    ( ('nob', 'sme'), 'tvinge'),
    ( ('nob', 'sme'), 'verden'),
    ( ('nob', 'sme'), 'våkne'),
    ( ('sma', 'nob'), 'daaresjidh'),
    ( ('sma', 'nob'), 'daaresjimmie'),
    ( ('sme', 'fin'), 'ahte'),
    ( ('sme', 'fin'), 'almmiguovlu'),
    ( ('sme', 'fin'), 'bealljái'),
    ( ('sme', 'fin'), 'beasat'),
    ( ('sme', 'fin'), 'beassat'),
    ( ('sme', 'fin'), 'biegga'),
    ( ('sme', 'fin'), 'boagusta'),
    ( ('sme', 'fin'), 'boagustit'),
    ( ('sme', 'fin'), 'boahtin'),
    ( ('sme', 'fin'), 'botnje'),
    ( ('sme', 'fin'), 'buot'),
    ( ('sme', 'fin'), 'báhcit'),
    ( ('sme', 'fin'), 'coggat'),
    ( ('sme', 'fin'), 'dadjá'),
    ( ('sme', 'fin'), 'dalle'),
    ( ('sme', 'fin'), 'de'),
    ( ('sme', 'fin'), 'dohpo'),
    ( ('sme', 'fin'), 'doppe'),
    ( ('sme', 'fin'), 'dovdat'),
    ( ('sme', 'fin'), 'dušše'),
    ( ('sme', 'fin'), 'dállu'),
    ( ('sme', 'fin'), 'dáppehan'),
    ( ('sme', 'fin'), 'eamidin'),
    ( ('sme', 'fin'), 'fadda'),
    ( ('sme', 'fin'), 'fas'),
    ( ('sme', 'fin'), 'fáippastit'),
    ( ('sme', 'fin'), 'gal'),
    ( ('sme', 'fin'), 'garra'),
    ( ('sme', 'fin'), 'geahčadit'),
    ( ('sme', 'fin'), 'giige'),
    ( ('sme', 'fin'), 'gitta'),
    ( ('sme', 'fin'), 'guovttos'),
    ( ('sme', 'fin'), 'gutna'),
    ( ('sme', 'fin'), 'gávdno'),
    ( ('sme', 'fin'), 'háv'),
    ( ('sme', 'fin'), 'hávdádit'),
    ( ('sme', 'fin'), 'jienas'),
    ( ('sme', 'fin'), 'jietnadan'),
    ( ('sme', 'fin'), 'juo'),
    ( ('sme', 'fin'), 'juohke'),
    ( ('sme', 'fin'), 'juoidá'),
    ( ('sme', 'fin'), 'juos'),
    ( ('sme', 'fin'), 'kanssa'),
    ( ('sme', 'fin'), 'lahkonit'),
    ( ('sme', 'fin'), 'leamaš'),
    ( ('sme', 'fin'), 'liegga'),
    ( ('sme', 'fin'), 'liikká'),
    ( ('sme', 'fin'), 'mearkugohte'),
    ( ('sme', 'fin'), 'miessi'),
    ( ('sme', 'fin'), 'misiin'),
    ( ('sme', 'fin'), 'mojohallat'),
    ( ('sme', 'fin'), 'mot'),
    ( ('sme', 'fin'), 'muhto'),
    ( ('sme', 'fin'), 'muhtumis'),
    ( ('sme', 'fin'), 'máhta'),
    ( ('sme', 'fin'), 'máhttit'),
    ( ('sme', 'fin'), 'naba'),
    ( ('sme', 'fin'), 'nebe'),
    ( ('sme', 'fin'), 'njammat'),
    ( ('sme', 'fin'), 'nu'),
    ( ('sme', 'fin'), 'nuppis'),
    ( ('sme', 'fin'), 'oaidná'),
    ( ('sme', 'fin'), 'olbmot'),
    ( ('sme', 'fin'), 'olgeš'),
    ( ('sme', 'fin'), 'olu'),
    ( ('sme', 'fin'), 'orui'),
    ( ('sme', 'fin'), 'ovddabealde'),
    ( ('sme', 'fin'), 'ovddal'),
    ( ('sme', 'fin'), 'roava'),
    ( ('sme', 'fin'), 'ruovgat'),
    ( ('sme', 'fin'), 'ráfálaš'),
    ( ('sme', 'fin'), 'ráigánit'),
    ( ('sme', 'fin'), 'sevii'),
    ( ('sme', 'fin'), 'vadjat'),
    ( ('sme', 'fin'), 'veahás'),
    ( ('sme', 'fin'), 'veaháš'),
    ( ('sme', 'fin'), 'viegahallat'),
    ( ('sme', 'fin'), 'vuollegis'),
    ( ('sme', 'fin'), 'vuollái'),
    ( ('sme', 'fin'), 'vuot'),
    ( ('sme', 'fin'), 'váldi'),
    ( ('sme', 'fin'), 'váldobargu'),
    ( ('sme', 'fin'), 'álddagas'),
    ( ('sme', 'fin'), 'álddu'),
    ( ('sme', 'fin'), 'áldu'),
    ( ('sme', 'fin'), 'čohka'),
    ( ('sme', 'fin'), 'čuhppe'),
    ( ('sme', 'fin'), 'čuččodit'),
    ( ('sme', 'fin'), 'čábbát'),
    ( ('sme', 'nob'), 'Eanet'),
    ( ('sme', 'nob'), 'beaivi'),
    ( ('sme', 'nob'), 'bágget'),
    ( ('sme', 'nob'), 'deltaker'),
    ( ('sme', 'nob'), 'dohkalaš'),
    ( ('sme', 'nob'), 'dohkkalaš'),
    ( ('sme', 'nob'), 'dohkket'),
    ( ('sme', 'nob'), 'dohkkálaš'),
    ( ('sme', 'nob'), 'dohkálaš'),
    ( ('sme', 'nob'), 'duddjot'),
    ( ('sme', 'nob'), 'duogábealde'),
    ( ('sme', 'nob'), 'duogáš'),
    ( ('sme', 'nob'), 'dáhpáhuvvat'),
    ( ('sme', 'nob'), 'feaskkir'),
    ( ('sme', 'nob'), 'geardi'),
    ( ('sme', 'nob'), 'heivemin'),
    ( ('sme', 'nob'), 'heivvemin'),
    ( ('sme', 'nob'), 'jente'),
    ( ('sme', 'nob'), 'leamaš'),
    ( ('sme', 'nob'), 'logaldalli'),
    ( ('sme', 'nob'), 'maŋŋel'),
    ( ('sme', 'nob'), 'mánnu'),
    ( ('sme', 'nob'), 'olggoš'),
    ( ('sme', 'nob'), 'olla'),
    ( ('sme', 'nob'), 'ollašuhttit'),
    ( ('sme', 'nob'), 'ollu'),
    ( ('sme', 'nob'), 'ovdal'),
    ( ('sme', 'nob'), 'seakka'),
    ( ('sme', 'nob'), 'skuohppu'),
    ( ('sme', 'nob'), 'ullu'),
    ( ('sme', 'nob'), 'vahku'),
    ( ('sme', 'nob'), 'vuortnuhit'),
    ( ('sme', 'nob'), 'čáppat'),

( ('sme', 'nob'), 'niidii'),
( ('sme', 'nob'), 'goarrrut'),
( ('sme', 'nob'), 'goarrut'),
( ('sme', 'nob'), 'čuohppat'),
( ('sme', 'nob'), 'coggat'),
( ('sme', 'nob'), 'bidjat'),
( ('sme', 'fin'), 'missä'),
( ('fin', 'sme'), 'missä'),
( ('sme', 'nob'), 'valdit'),
( ('sme', 'nob'), 'váldit'),
( ('sme', 'nob'), 'gárvodit'),
( ('sme', 'nob'), 'nuollat'),
( ('sme', 'nob'), 'hupmat'),
( ('sme', 'nob'), 'Áđđestaddi'),
( ('sme', 'nob'), 'hálla'),
( ('sme', 'nob'), 'hállat'),
( ('sme', 'fin'), 'diibmu'),
( ('sme', 'nob'), 'liibmet'),
( ('nob', 'sme'), 'sy'),

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
