# -*- encoding: utf-8 -*-

import os
import tempfile
import unittest

import neahtta

from .lexicon import (
    WordLookupAPIDefinitionTests,  # NB: only comment these in as needed, otherwise; they fail; , BasicTests; , WordLookupTests; , WordLookupDetailTests; , ParadigmGenerationTests; , form_contains
    WordLookupAPITests,
    form_contains,
    form_doesnt_contain,
)

## These tests are for making sure that NDS infrastructure can take user input
## and propery resolve an analysis and lexical entries.
wordforms_that_shouldnt_fail = [
    (("crk", "eng"), "nipihk"),
    # syllabics
    (("crkS", "eng"), "ᓂᐚᐸᐦᑌᐣ"),
    (("crkS", "eng"), "ᐚᐸᐦᑕᒼ"),
]

# test that we can analyse and get a definition
definition_exists_tests = [
    #  lang    pair    search    definition lemmas
    #
    # spaces work
    #     ( ('crkS', 'eng'), u'ᐚᐸᐦᑕᒼ', u's/he learns by watching s.t., s/he looks on to learn s.t.'),
    #     ( ('crk', 'eng'), u'emacinipat', "s/he sleeps, s/he is asleep"),
    #     ( ('crk', 'eng'), u'e-maci-nipat', "s/he sleeps, s/he is asleep"),
    #     ( ('crkS', 'eng'), u'ᐁ ᓅᐦᑌ ᐚᐸᒼᐊᐟ', "s/he sleeps, s/he is asleep"),
    #     ( ('crkS', 'eng'), u'ᐁ ᓅᐦᑌ ᐚᐸᒼᐊᐟ', "s/he sleeps, s/he is asleep"),
    # space
    # ( ('crkS', 'eng'), u'ᐁ ᓅᐦᑌ ᐚᐸᒼᐊᐟ', "s/he sleeps, s/he is asleep"),
    # ( ('crkS', 'eng'), u'ᐁ   ᓅᐦᑌ   ᐚᐸᒪᐟ', "s/he sleeps, s/he is asleep"),
    # spaces are stripped
    (("crk", "eng"), "emacinipat ", "s/he sleeps, s/he is asleep"),
]

paradigm_generation_tests = [
    # source, target, lemma, error_msg, paradigm_test
    # possible tests are defined as follows:
    # `form_contains` - resulting form is a member of the provided set
    # `form_doesnt_contain` - resulting form is a member of the provided set
    ###  - http://localhost:5000/detail/sme/nob/iige.json
    ###  - localhost:5000/detail/sme/nob/manne.json
    # ('crk', 'eng', u'nipihk',
    #         "Not generating from mini_paradigm",
    #         form_contains(set([u'munnje', u'mus', u'munin']))),
    # form_doesnt_contain(set([u"heittohat", u"heittohut", u"heittohit"]))),
]

### class WordLookupTests(WordLookupTests):
###
###     def test_single_word(self):
###         """ Test that the basic idea of testing will work.
###             If there's a problem here, this is a problem. ;)
###         """
###         lang_pair, form = wordforms_that_shouldnt_fail[0]
###
###         base = '/%s/%s/' % lang_pair
###         rv = self.app.post(base, data={
###             'lookup': form,
###         })
###
###         assert 'nipihk' in rv.data
###         self.assertEqual(rv.status_code, 200)

### class WordLookupDetailTests(WordLookupDetailTests):
###     wordforms_that_shouldnt_fail = wordforms_that_shouldnt_fail
###


class WordLookupAPITests(WordLookupAPITests):
    wordforms_that_shouldnt_fail = wordforms_that_shouldnt_fail


# class ParadigmGenerationTests(ParadigmGenerationTests):
#     paradigm_generation_tests = paradigm_generation_tests

###
### class ParadigmSelectionTest(WordLookupTests):
###     """ These are really only for testing specifics in the paradigm
###     directory structure the code, and don't need to be run as generation
###     as a whole is tested above.
###     """
###
###     def test_misc_paradigms(self):
###         from configs.paradigms import ParadigmConfig
###
###         lookups = self.current_app.morpholexicon.lookup('mannat', source_lang='sme', target_lang='nob') \
###                 + self.current_app.morpholexicon.lookup(u'Ráisa', source_lang='sme', target_lang='nob') \
###                 + self.current_app.morpholexicon.lookup(u'dálkkádagat', source_lang='sme', target_lang='nob') \
###                 + self.current_app.morpholexicon.lookup(u'álgoálbmotášši', source_lang='sme', target_lang='nob') \
###                 + self.current_app.morpholexicon.lookup(u'Dálmmát', source_lang='sme', target_lang='nob') \
###                 + self.current_app.morpholexicon.lookup(u'Gállábártnit', source_lang='sme', target_lang='nob') \
###                 + self.current_app.morpholexicon.lookup(u'Iččát', source_lang='sme', target_lang='nob')
###
###
###         pc = self.current_app.morpholexicon.paradigms
###         # print self.current_app
###         pc = ParadigmConfig(app=None, debug=True)
###         for node, analyses in lookups:
###             print "Testing: ", node, analyses
###             # for a in analyses:
###             #     print " - " + repr(a.tag.matching_tagsets())
###             print pc.get_paradigm('sme', node, analyses, debug=True)
###             print '--'


class WordLookupAPIDefinitionTests(WordLookupAPIDefinitionTests):
    definition_exists_tests = definition_exists_tests
