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
    ('mdf', 'fin', u'инжи',
            "forms not generated",
            form_contains(set([u'инжи']))),

    ('mdf', 'fin', u'тушендомс',
            "forms not generated",
            form_contains(set([u'тушендомс']))),
]


class ParadigmGenerationTests(ParadigmGenerationTests):
	paradigm_generation_tests = paradigm_generation_tests

