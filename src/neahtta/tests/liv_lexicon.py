# -*- encoding: utf-8 -*-

# um
# vȱlda+V+Ind+Prs+Sg3

from __future__ import absolute_import
import os
import tempfile
import unittest

import neahtta

from .lexicon import (BasicTests, ParadigmGenerationTests,
                      WordLookupAPIDefinitionTests, WordLookupAPITests,
                      WordLookupDetailTests, WordLookupTests, form_contains,
                      form_doesnt_contain)

paradigm_generation_tests = [
    # source, target, lemma, error_msg, paradigm_test

    ###  - V:
    ('liv', 'fin', u'vȱlda', u" vȱlda  not generating",
     form_doesnt_contain(set([u"um"]))),
]


class ParadigmGenerationTests(ParadigmGenerationTests):
    paradigm_generation_tests = paradigm_generation_tests
