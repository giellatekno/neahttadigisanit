# -*- encoding: utf-8 -*-

from __future__ import absolute_import
import os
import tempfile
import unittest

import neahtta

from .lexicon import (ParadigmGenerationTests, form_contains,
                      form_doesnt_contain)

paradigm_generation_tests = [

    ###  - V:
    ('myv', 'fin', u'тукшномс', "forms not generated",
     form_contains(set([u'тукшнось']))),
]


class ParadigmGenerationTests(ParadigmGenerationTests):
    paradigm_generation_tests = paradigm_generation_tests
