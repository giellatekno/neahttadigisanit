import os
import neahtta
import unittest
import tempfile
import simplejson

class WordLookupTests(unittest.TestCase):

    def setUp(self):
        _app = neahtta.app
        # Turn on debug to disable SMTP logging
        _app.debug = True
        _app.logger.removeHandler(_app.logger.smtp_handler)

        # Disable caching
        _app.caching_enabled = False
        self.app = _app.test_client()

class BasicTests(WordLookupTests):
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

    def test_all_words_for_no_404s(self):
        for lang_pair, form in self.wordforms_that_shouldnt_fail[1::]:
            print "testing: %s / %s" % (repr(lang_pair), repr(form))
            base = '/%s/%s/' % lang_pair
            rv = self.app.post(base, data={
                'lookup': form,
            })

            self.assertEqual(rv.status_code, 200)

class WordLookupDetailTests(WordLookupTests):

    def test_all_words_for_no_404s(self):
        for lang_pair, form in self.wordforms_that_shouldnt_fail[1::]:
            _from, _to = lang_pair
            base = '/detail/%s/%s/%s.html' % (_from, _to, form)
            print "testing: %s " % base
            rv = self.app.get(base)

            self.assertEqual(rv.status_code, 200)

class WordLookupAPITests(WordLookupTests):

    def test_all_words_for_no_404s(self):
        from urllib import urlencode
        for lang_pair, form in self.wordforms_that_shouldnt_fail[1::]:
            _from, _to = lang_pair
            base = u'/lookup/%s/%s/?' % (_from, _to)
            url = base + urlencode({'lookup': form.encode('utf-8')})
            print "testing: %s " % url
            rv = self.app.get(url)
            print "  got: %d bytes" % len(rv.data)

            self.assertEqual(rv.status_code, 200)

class WordLookupAPIDefinitionTests(WordLookupTests):

    def test_words_for_definitions(self):
        from urllib import urlencode
        for lang_pair, form, expected_def in self.definition_exists_tests:
            _from, _to = lang_pair
            base = u'/lookup/%s/%s/?' % (_from, _to)
            url = base + urlencode({'lookup': form.encode('utf-8')})
            print "testing: <%s> for <%s>" % (form, expected_def)
            rv = self.app.get(url)
            result = simplejson.loads(rv.data)

            definitions = []
            for r in result.get('result'):
                for l in r.get('lookups'):
                    results = True
                    definitions.extend(l.get('right'))

            found = False
            if len(definitions) > 0:
                if expected_def in map(unicode, definitions):
                    print '  FOUND'
                else:
                    print '  NOT FOUND: ' + repr(definitions)
                self.assertIn(expected_def, map(unicode, definitions))
            else:
                if len(expected_def) == 0 or expected_def is None:
                    if len(definitions) == 0:
                        print '  NO DEFINITIONS -- EXPECTED NONE'
                    else:
                        print '  HAS DEFINITIONS -- EXPECTED NONE'
                    self.assertIs(len(definitions), 0)
                else:
                    print '  NO DEFINITIONS -- EXPECTED <%s>' % expected_def
                    raise AssertionError("No definitions.")


            # if expected_def in l.get('right'):
            #     print expected_def
            #     print l.get('right')
            #     found_match = True
            print '--'


