# -*- encoding: utf-8 -*-

import os
import neahtta
import unittest
import tempfile

from .lexicon import ( form_contains
                     , form_doesnt_contain
                     , WordLookupAPITests
                     # NB: only comment these in as needed, otherwise
                      # they fail
                     # , BasicTests
                     # , WordLookupTests
                     # , WordLookupDetailTests
                     # , WordLookupAPIDefinitionTests
                     # , ParadigmGenerationTests
                     # , form_contains
                     )

## These tests are for making sure that NDS infrastructure can take user input 
## and propery resolve an analysis and lexical entries.
wordforms_that_shouldnt_fail = [
    ( ('crk', 'eng'), u'nipihk'),

    # syllabics

    ( ('crkS', 'eng'), u'ᓂᐚᐸᐦᑌᐣ'),
    ( ('crkS', 'eng'), u'ᐚᐸᐦᑕᒼ'),

    # ᐱᐳᐣ

]


paradigm_generation_tests = [
    # source, target, lemma, error_msg, paradigm_test

    # possible tests are defined as follows:
    # `form_contains` - resulting form is a member of the provided set
    # `form_doesnt_contain` - resulting form is a member of the provided set

###  - http://localhost:5000/detail/sme/nob/iige.json
###  - localhost:5000/detail/sme/nob/manne.json

    ('crk', 'eng', u'nipihk',
            "Not generating from mini_paradigm",
            form_contains(set([u'munnje', u'mus', u'munin']))),

###  - A: 
###     - http://localhost:5000/detail/sme/nob/ruoksat.json
###     - test that context is found as well as paradigm
###     - test that +Use/NGminip forms are not generated
    ('sme', 'nob', u'heittot',
            "Dialectical forms present",
            form_doesnt_contain(set([u"heittohat", u"heittohut", u"heittohit"]))),

###  - A + context="bivttas":  heittot
###     - http://localhost:5000/detail/sme/nob/heittot.html

    ('sme', 'nob', u'heittot',
            "Context missing",
            form_contains(set([u"heittogis (bivttas)"]))),

###  - A + context="báddi":  guhkki
###     - http://localhost:5000/detail/sme/nob/guhkki.html

    ('sme', 'nob', u'guhkki',
            "Context missing",
            form_contains(set([u"guhkes (báddi)"]))),

###  - Num + context="gápmagat":  guokte
###     - http://localhost:5000/detail/sme/nob/guokte.html

    ('sme', 'nob', u'guokte',
            "Context missing",
            form_contains(set([u"guovttit (gápmagat)"]))),

###  - N + illpl="no": eahketroađđi, sihkarvuohta, skuvlaáigi

    ('sme', 'nob', u'eahketroađđi',
            "Illative plural present",
            form_doesnt_contain(set([u'eahketrođiide']))),

###  - N Prop Sg: Norga, Ruoŧŧa
###     - http://localhost:5000/detail/sme/nob/Ruoŧŧa.html
    ('sme', 'nob', u'Ruoŧŧa',
            "Forms not generated",
            form_contains(set([u'Ruoŧa bokte', u'Ruŧŧii', u'Ruoŧas']))),

###  - N Prop Pl: Iččát
###     - <l pos="N" type="Prop" nr="Pl">Iččát</l>

    ('sme', 'nob', u'Iččát',
            "Forms not generated",
            form_contains(set([u'Iččáid bokte', u'Iččáide', u'Iččáin']))),

    ('sme', 'nob', u'mannat',
            "Forms not generated",
            form_contains(set([u'manan']))),

    ('sme', 'nob', u'deaivvadit',
            "Overgenerating forms",
            form_doesnt_contain(set([u'deaivvadan']))),


    ('sme', 'nob', u'girji',
            "Overgenerating forms. Possible tag filtration issue.",
            form_doesnt_contain(set([u'girjje']))),

###  - N 
###    - <l pos="N" type="G3">sámeášši</l>

    ('sme', 'nob', u'sámeášši',
            "Forms not generated",
            form_contains(set([u'sámeášši', u'sámeáššái', u'sámeáššiiguin']))),


    #     u'Ráisa', 
    #     u'dálkkádagat', 
    #     u'deaivvadit' - check that Pl3 deaivvadedje and deaivvadit are
    #     generated

###  - V: boahtit
###     - check context, and paradigm: 
###     - http://localhost:5000/detail/sme/nob/boahtit.json

# TODO: this test

###  - V + context="dat", v + context="sii"
###     - check context, and that paradigm is not generated for 1st person
###     - http://localhost:5000/detail/sme/nob/ciellat.html
###     - http://localhost:5000/detail/sme/nob/deaivvadit.html

# TODO: this test

###  - N

# TODO: find most common kinds of nouns

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

### 
### class ParadigmGenerationTests(ParadigmGenerationTests):
###     paradigm_generation_tests = paradigm_generation_tests
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


