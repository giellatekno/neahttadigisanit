# -*- encoding: utf-8 -*-

import os
import neahtta
import unittest
import tempfile

from .lexicon import ( ParadigmGenerationTests
                     , form_contains
                     , form_doesnt_contain
                     )

paradigm_generation_tests = [

###  - V:
    ('myv', 'fin', u'тукшномс',
            "forms not generated",
            form_contains(set([u'тукшнось']))),

]


class ParadigmGenerationTests(ParadigmGenerationTests):
	paradigm_generation_tests = paradigm_generation_tests
