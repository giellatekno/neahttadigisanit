import os
import tempfile
import unittest

import simplejson

import neahtta


class YamlTests(object):

    yaml_file = ''

    @property
    def parsed_yaml(self):
        import yaml
        if hasattr(self, '_parsed_yaml'):
            return self._parsed_yaml
        with open(self.yaml_file, 'r') as F:
            _p = yaml.load(F.read().decode('utf-8'))
        self._parsed_yaml = _p
        return self._parsed_yaml

    @property
    def wordforms_that_shouldnt_fail(self):
        def parse_item(i):
            return ((i[0], i[1]), i[2])

        return map(parse_item, self.parsed_yaml.get('LookupTests'))

    @property
    def paradigm_generation_tests(self):
        if hasattr(self, '_paradigm_generation_tests'):
            return self._paradigm_generation_tests

        _tests = []

        def read_test_item(i):
            _fst = i.get('lexicon')[0]
            _snd = i.get('lexicon')[1]
            _thrd = i.get('search')
            _frth = i.get('fail_message')

            for t, vs in i.get('test').iteritems():
                if t == 'form_doesnt_contain':
                    test_func = form_doesnt_contain
                if t == 'form_contains':
                    test_func = form_contains
                _fth = test_func(set(vs))

                return (_fst, _snd, _thrd, _frth)
            else:
                return ()

        self._paradigm_generation_tests = map(
            read_test_item, self.parsed_yaml.get('ParadigmGeneration'))

        return self._paradigm_generation_tests


def form_contains(_test_set):
    """ A function that wraps a set, and then tests that the paradigm
    generation output partially intersects. """

    def test_contains(paradigm):
        """
        [
            ["roa\u0111\u0111i", ["N", "Sg", "Gen"], ["roa\u0111i"]],
            ["roa\u0111\u0111i", ["N", "Sg", "Ill"], ["roa\u0111\u0111\u00e1i"]],
            ["roa\u0111\u0111i", ["N", "Pl", "Ill"], ["ro\u0111iide"]]
        ]
        """
        forms = set(
            second_list[0]
            for first_list in paradigm
            for second_list in first_list
        )
        if not bool(forms & _test_set):
            print 78, 'failed', u' '.join(forms), u' '.join(_test_set)
        return bool(forms & _test_set)

    return test_contains


def form_doesnt_contain(_test_set):
    """ A function that wraps a set, and then tests that the paradigm
    generation output partially intersects. """

    def test_doesnt_contain(paradigm):
        """
        paradigm = [
            ["roa\u0111\u0111i", ["N", "Sg", "Gen"], ["roa\u0111i"]],
            ["roa\u0111\u0111i", ["N", "Sg", "Ill"], ["roa\u0111\u0111\u00e1i"]],
            ["roa\u0111\u0111i", ["N", "Pl", "Ill"], ["ro\u0111iide"]]
        ]
        """
        forms = set(
            second_list[0]
            for first_list in paradigm
            for second_list in first_list
        )
        if _test_set & forms:
            print 101, 'failed', u' '.join(forms), u' '.join(_test_set)
        return len(_test_set & forms) == 0

    return test_doesnt_contain


class WordLookupTests(unittest.TestCase):
    def setUp(self):
        _app = neahtta.app
        # Turn on debug to disable SMTP logging
        _app.debug = True
        _app.logger.removeHandler(_app.logger.smtp_handler)

        # Disable caching
        _app.caching_enabled = False
        self.app = _app.test_client()
        self.current_app = _app

        if self.current_app.config.fcgi_script_path:
            self.url_base = self.current_app.config.fcgi_script_path
        else:
            self.url_base = ''


class BasicTests(WordLookupTests):
    def test_api_null_lookup(self):
        """ Test that a null lookup to the api doesn't return a 500
        """
        url = self.url_base + "/lookup/sme/nob/?callback=jQuery3094203984029384&lookup=&lemmatize=true"

        rv = self.app.get(url)
        self.assertEqual(rv.status_code, 200)

    def test_api_lookup(self):
        """ Test that a null lookup to the api doesn't return a 500
        """
        url = self.url_base + "/lookup/sme/nob/?callback=jQuery3094203984029384&lookup=mannat&lemmatize=true"

        rv = self.app.get(url)
        self.assertEqual(rv.status_code, 200)

    def test_all_words_for_no_404s(self):
        for lang_pair, form in self.wordforms_that_shouldnt_fail[1::]:
            print "testing: %s / %s" % (repr(lang_pair), repr(form))
            base = '/%s/%s/' % lang_pair
            rv = self.app.post(
                base, data={
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
            base = self.url_base + u'/lookup/%s/%s/?' % (_from, _to)
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
            base = self.url_base + u'/lookup/%s/%s/?' % (_from, _to)
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


class ParadigmGenerationTests(WordLookupTests):
    def test_all_words_for_no_404s(self):
        for (source, target, lemma, error_msg,
             test_func) in self.paradigm_generation_tests:
            base = self.url_base + '/paradigm/%s/%s/%s/' % (
                source,
                target,
                lemma,
            )
            print "testing: %s " % base
            rv = self.app.get(base)
            result = simplejson.loads(rv.data)

            if result['input']['lemma'] == lemma:
                print 'paradigm'
                test_result = test_func(result['paradigms'])
                self.assertTrue(test_result)

            # self.assertEqual(rv.status_code, 200)
