# -*- encoding: utf-8 -*-

import os
import tempfile
import unittest

from .lexicon import (
    ParadigmGenerationTests,
    WordLookupAPIDefinitionTests,
    WordLookupAPITests,
    WordLookupDetailTests,
    form_contains,
    form_doesnt_contain,
)

# These should not produce a 404.

wordforms_that_shouldnt_fail = [
    (("mrj", "fin"), "ловка"),
    (("mrj", "fin"), "ломбы"),
    (("mrj", "fin"), "ло"),
]

# These forms should have a matching definition, i.e., <väli> must be a
# possible definition of <ло>

# With these tests, there is not as big of a need to be extensive, as
# much as making sure that there are tests for a larger variety of types
# of words, to make sure that the FST lines up with the lexicon.

# NB: make sure word strings are unicode, marked with u.

definition_exists_tests = [
    #  lang    pair    search    definition lemmas
    #
    (("mrj", "fin"), "ло", "väli"),
    (("mrj", "fin"), "ло", "kalastaa"),
    (("mrj", "fin"), "ловка", "näppäryys"),
    (("mrj", "fin"), "ломбы", "tuomi"),
]

paradigm_generation_tests = [
    # source, target, lemma, error_msg, paradigm_test
    ###  - V:
    (
        "mrj",
        "fin",
        "лӓктӓш",
        "mrj verbs not generating",
        form_contains(set(["лӓктӓм", "лӓктеш"])),
    ),
    ###  - N + context="bivttas":  heittot
    ###     - http://localhost:5000/detail/sme/nob/heittot.html
    (
        "mrj",
        "fin",
        "книгӓ",
        "mrj nouns not generating",
        form_contains(set(["книгӓн", "книгӓге"])),
    ),
]


class WordLookupAPIDefinitionTests(WordLookupAPIDefinitionTests):
    definition_exists_tests = definition_exists_tests


class WordLookupDetailTests(WordLookupDetailTests):
    wordforms_that_shouldnt_fail = wordforms_that_shouldnt_fail


class WordLookupAPITests(WordLookupAPITests):
    wordforms_that_shouldnt_fail = wordforms_that_shouldnt_fail


class ParadigmGenerationTests(ParadigmGenerationTests):
    paradigm_generation_tests = paradigm_generation_tests
