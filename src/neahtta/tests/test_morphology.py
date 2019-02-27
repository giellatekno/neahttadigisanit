# -*- encoding: utf-8 -*-
"""Test classes from morphology/morphology.py"""
from __future__ import absolute_import
import unittest
import os
import sys

HERE = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from parameterized import parameterized

from neahtta import app
from morphology.morphology import HFST, Lemma, Morphology, Tagsets

class TestHFST(unittest.TestCase):
    """Test the HFST class."""

    def setUp(self):
        """Set up common variables."""
        self.hfst = HFST(
            'hfst-lookup',
            '/usr/share/giella/sme/analyser-dict-gt-desc.hfstol',
            ifst_file='/usr/share/giella/sme/generator-dict-gt-norm.hfstol',
            options={
                'derivationMarker': '+Der',
                'tagsep': '+',
                'inverse_tagsep': '+',
                'compoundBoundary': '+Cmp#'
            })
        self.app_context = app.app_context()

    def test_tagprocessor(self):
        """Test the tagprocessor."""
        self.assertEqual(
            self.hfst.tag_processor('guolit\tguolli+N+Sg+Nom\t0,000000'),
            ('guolit', 'guolli+N+Sg+Nom'))

    def test_clean(self):
        """Test the cleaner."""
        got = '''guollái\tguolli+N+Sg+Ill\t0,000000
guollái\tguolli+N+Sg+Ill\t0,000000
guollái\tguolli+N+Sg+Ill\t0,000000
guollái\tguollái+A+Sg+Nom\t0,000000'''
        wanted = [('guollái', [
            'guolli+N+Sg+Ill', 'guolli+N+Sg+Ill', 'guolli+N+Sg+Ill',
            'guollái+A+Sg+Nom'
        ])]

        self.assertEqual(self.hfst.clean(got), wanted)

    def test_lookup(self):
        """Test the analyser."""
        with self.app_context:
            got = self.hfst.lookup([u'guollái', u'viežži'])
            wanted = [(u'guollái', [u'guolli+N+Sg+Ill', u'guollái+A+Sg+Nom']),
                      (u'viežži', [
                          u'viežžat+V+TV+Der/NomAg+N+Sg+Acc',
                          u'viežžat+V+TV+Der/NomAg+N+Sg+Gen',
                          u'viežžat+V+TV+Der/NomAg+N+Sg+Nom',
                          u'viežžat+V+TV+Imprt+Du2', u'viežžat+V+TV+PrsPrc'
                      ])]

            self.maxDiff = None
            self.assertEqual(got, wanted)

    def test_inverse_lookup_by_string(self):
        """Test the generator that works on strings."""
        with self.app_context:
            got = self.hfst.inverselookup_by_string('guolli+N+Pl+Nom')
            wanted = [('guolli+N+Pl+Nom', ['guolit'])]

            self.assertEqual(got, wanted)


if __name__ == '__main__':
    unittest.main()
