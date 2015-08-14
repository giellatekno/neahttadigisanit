import os, sys

import unittest
import tempfile
import yaml
import neahtta

tests_module = os.path.join( os.getcwd()
                           , 'tests/'
                           )

project_test_file = os.path.join( tests_module
                                , 'itwewina.yaml'
                                )

import unittest
import neahtta

from flask import current_app

class YamlTests(object):

    def __init__(self, path):
        self.filename = path

        with open(self.filename, 'r') as F:
            self.yaml = yaml.load(F)

    @property
    def request_tests(self):
        cases = []
        for case_def in self.yaml.get('RequestTests'):
            # a little more processing will happen here
            uri = case_def.get('uri')
            for test in case_def.get('tests'):
                case = []
                case.append(uri)
                case.append(test)
                cases.append(case)
        return cases

    @property
    def morpholexicon_tests(self):
        cases = []
        for case_def in self.yaml.get('MorpholexicalAnalysis'):
            mlex = tuple(case_def.get('morpholexicon'))
            for test in case_def.get('tests'):
                case = []
                case.append(mlex)
                case.append(test)
                cases.append(case)
        return cases

class RequestTest(unittest.TestCase):

    def setUp(self):
        _app = neahtta.app
        _app.debug = True
        _app.logger.removeHandler(_app.logger.smtp_handler)

        _app.caching_enabled = False
        self.app = _app.test_client()
        self.current_app = _app

        self.yamltests = YamlTests(project_test_file)

    def test_requests(self):
        from cssselect import GenericTranslator, SelectorError
        from lxml.html.soupparser import fromstring

        # TODO: print useful text
        for uri, case in self.yamltests.request_tests:
            uri_formatted = uri % case.get('uri_args')
            expected = case.get('expected_values')
            value_selector = case.get('value_selector')

            # Run the mock request
            response = self.app.get(uri_formatted)

            # Parse the tree by the test definition, and compare
            tree = fromstring(response.data)
            expr = GenericTranslator().css_to_xpath(value_selector)
            selected = [a.text for a in tree.xpath(expr)]

            for e in expected:
                self.assertIn(e, selected)
            
    def test_morpholexical_analyses(self):

        skw = {
            'split_compounds': True,
            'non_compounds_only': False,
            'no_derivations': False,
            'return_raw_data': True,
        }

        with self.current_app.test_request_context('?'):

            m = self.current_app.morpholexicon
            for (source, target), case in self.yamltests.morpholexicon_tests:
                expect = case.get('expected_lemmas')
                res, raw_out, raw_err = m.lookup(case.get('input'),
                                                 source_lang=source,
                                                 target_lang=target, 
                                                 **skw)

                lemmas = [r.lemma for r in res.analyses]

                for e in expect:
                    self.assertIn(e, lemmas)

    def tearDown(self):
        pass


