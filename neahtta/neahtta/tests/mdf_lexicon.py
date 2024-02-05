# -*- encoding: utf-8 -*-

import os
import tempfile
import unittest

import neahtta

from .lexicon import ParadigmGenerationTests, form_contains, form_doesnt_contain

paradigm_generation_tests = [
    ###  - V:
    ("mdf", "fin", "инжи", "forms not generated", form_contains(set(["инжи"]))),
    (
        "mdf",
        "fin",
        "тушендомс",
        "forms not generated",
        form_contains(set(["тушендомс"])),
    ),
]


class ParadigmGenerationTests(ParadigmGenerationTests):
    paradigm_generation_tests = paradigm_generation_tests
