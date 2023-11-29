# -*- encoding: utf-8 -*-

# um
# vȱlda+V+Ind+Prs+Sg3

import os
import tempfile
import unittest

import neahtta

from .lexicon import (
    BasicTests,
    ParadigmGenerationTests,
    WordLookupAPIDefinitionTests,
    WordLookupAPITests,
    WordLookupDetailTests,
    WordLookupTests,
    form_contains,
    form_doesnt_contain,
)

paradigm_generation_tests = [
    # source, target, lemma, error_msg, paradigm_test
    ###  - V:
    ("liv", "fin", "vȱlda", " vȱlda  not generating", form_doesnt_contain(set(["um"]))),
]


class ParadigmGenerationTests(ParadigmGenerationTests):
    paradigm_generation_tests = paradigm_generation_tests
