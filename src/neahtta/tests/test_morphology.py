# -*- encoding: utf-8 -*-
"""Test classes from morphology/morphology.py"""
from __future__ import absolute_import
import unittest
import os
import sys

HERE = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from lxml import etree
from parameterized import parameterized

from neahtta import app
from morphology.morphology import HFST, Lemma, Morphology, Tagsets


def fst_tool():
    return app.config.morphologies['sme'].tool


class TestHFST(unittest.TestCase):
    """Test the HFST class."""

    def test_tagprocessor(self):
        """Test the tagprocessor."""
        self.assertEqual(
            fst_tool().tag_processor('guolit\tguolli+N+Sg+Nom\t0,000000'),
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

        self.assertEqual(fst_tool().clean(got), wanted)

    def test_lookup(self):
        """Test the analyser."""
        with app.app_context():
            got = fst_tool().lookup(
                [u'guollái', u'viežži'])
            wanted = [(u'guollái', [u'guolli+N+Sg+Ill', u'guollái+A+Sg+Nom']),
                      (u'viežži',
                       [u'viežžat+V+TV+PrsPrc', u'viežžat+V+TV+Imprt+Du2',
                        u'viežžat+V+TV+Der/NomAg+N+Sg+Gen',
                        u'viežžat+V+TV+Der/NomAg+N+Sg+Acc',
                        u'viežžat+V+TV+Der/NomAg+N+Sg+Nom'])]

            self.maxDiff = None
            self.assertEqual(got, wanted)

    def test_inverse_lookup_by_string(self):
        """Test the generator that works on strings."""
        with app.app_context():
            got = fst_tool().inverselookup_by_string('guolli+N+Pl+Nom')
            wanted = [('guolli+N+Pl+Nom', ['guolit'])]

            self.assertEqual(got, wanted)

    def test_split_analysis(self):
        """Test the analysis line splitter."""
        got = fst_tool().splitAnalysis('guolli+N+Sg+Loc')
        wanted = ['guolli', 'N', 'Sg', 'Loc']

        self.assertEqual(got, wanted)

    def test_format_tags(self):
        """Test the tag formatter."""
        got = fst_tool().formatTag(fst_tool().splitAnalysis('guolli+N+Sg+Loc'))
        wanted = 'guolli+N+Sg+Loc'

        self.assertEqual(got, wanted)

    @parameterized.expand([
        ('lemma part of tags', 'guolli',
         ['guolli+N+Sg+Loc', 'guolli+N+Pl+Nom'],
         [('guolli+N+Sg+Loc', ['guolis']), ('guolli+N+Pl+Nom', ['guolit'])]),
        ('lemma not part of tags', 'guolli',
         ['N+Sg+Loc', 'N+Pl+Nom'],
         [('guolli+N+Sg+Loc', ['guolis']), ('guolli+N+Pl+Nom', ['guolit'])])
    ])
    def test_inverse_lookup(self, name, lemma, tags, wanted):
        """Test the generator that works on lists of strings."""
        with app.app_context():
            self.maxDiff = None
            self.assertEqual(
                fst_tool().inverselookup(lemma, tags), wanted, msg=name)


class TestMorphology(unittest.TestCase):
    """Test the Morphology class."""

    default_sme_tagsets = {
        'second_persons': ['Sg2', 'Du2', 'Pl2'],
        'supinum': ['Sup'],
        'number': ['Sg', 'Pl'],
        'pos': [
            'A', 'Adp', 'Adv', 'CC', 'CS', 'Interj', 'N', 'Num', 'Pcle',
            'Po', 'Pr', 'Pron', 'V'
        ],
        'possessive': ['PxSg2'],
        'third_persons': ['Sg3', 'Du3', 'Pl3'],
        'tense': ['Prs', 'Prt'],
        'nouns_null_number': ['Ess'],
        'vmax': ['v1', 'v2', 'v3', 'v4', 'v5'],
        'negation': ['ConNeg'],
        'nonfinite_paradigm': ['ConNeg', 'PrfPrc', 'Neg'],
        'semantics': [
            'Sem/Act', 'Sem/Ani', 'Sem/AniProd', 'Sem/Body',
            'Sem/Body-abstr', 'Sem/Build', 'Sem/Build-part', 'Sem/Clth',
            'Sem/Clth-jewl', 'Sem/Clth-part', 'Sem/Ctain',
            'Sem/Ctain-abstr', 'Sem/Ctain-clth', 'Sem/Curr', 'Sem/Edu',
            'Sem/Event', 'Sem/Feat-phys', 'Sem/Feat-psych', 'Sem/Featg',
            'Sem/Fem', 'Sem/Food', 'Sem/Furn', 'Sem/Group', 'Sem/Hum',
            'Sem/Lang', 'Sem/Mal', 'Sem/Mat', 'Sem/Measr', 'Sem/Money',
            'Sem/Obj', 'Sem/Obj-clo', 'Sem/Obj-el', 'Sem/Org', 'Sem/Partg',
            'Sem/Perc-emo', 'Sem/Plant', 'Sem/Plc', 'Sem/Plc-elevate',
            'Sem/Plc-line', 'Sem/Plc-water', 'Sem/Route', 'Sem/Semcon',
            'Sem/Stateg', 'Sem/Substnc', 'Sem/Sur', 'Sem/Time', 'Sem/Tool',
            'Sem/Tool-catch', 'Sem/Txt', 'Sem/Veh', 'Sem/Wpn', 'Sem/Wthr'
        ],
        'case': ['Nom', 'Acc', 'Gen', 'Ill', 'Loc', 'Ess', 'Com'],
        'negative': ['Neg'],
        'noun_type': ['Coll'],
        'single_tense_display': ['Sup'],
        'first_persons': ['Sg1', 'Du1', 'Pl1'],
        'pron_type':
            ['Dem', 'Indef', 'Interr', 'Pers', 'Recipr', 'Refl', 'Rel'],
        'type': [
            'NomAg', 'G3', 'G7', 'Aktor', 'res.', 'Prop', 'Coll', 'Dem',
            'Indef', 'Interr', 'Pers', 'Recipr', 'Refl', 'Rel'
        ]
    }

    def make_lemmatize_answer(self, wordform, tags):
        """Make a list with the same format that Morpology.morph_lemmatize does.

        Args:
            wordform: the wordform that morph_lemmatize is fed
            tags: a list of tags that morph_lemmatize produces

        Returns:
            list of morphology.Lemma
        """
        return [
            Lemma(
                tag=tag.split('+'),
                _input=wordform,
                tool=fst_tool(),
                tagsets=Tagsets(self.default_sme_tagsets)) for tag in tags
        ]

    def test_generate(self):
        """Test the generator."""
        tagsets = '''guolli+N+Sg+Nom
guolli+N+Sg+Acc
guolli+N+Sg+Gen
guolli+N+Sg+Ill
guolli+N+Sg+Loc
guolli+N+Sg+Com
guolli+N+Ess
guolli+N+Pl+Nom
guolli+N+Pl+Acc
guolli+N+Pl+Gen
guolli+N+Pl+Ill
guolli+N+Pl+Loc
guolli+N+Pl+Com'''

        args = ('guolli', tagsets, etree.Element('e'))
        kwargs = {'no_preprocess_paradigm': True}

        with app.app_context():
            got = app.config.morphologies['sme'].generate(*args, **kwargs)
            wanted = [([u'guolli', u'N', u'Sg', u'Nom'], [u'guolli']),
                      ([u'guolli', u'N', u'Sg', u'Acc'], [u'guoli']),
                      ([u'guolli', u'N', u'Sg', u'Gen'], [u'guole', u'guoli']),
                      ([u'guolli', u'N', u'Sg', u'Ill'], [u'guollái']),
                      ([u'guolli', u'N', u'Sg', u'Loc'], [u'guolis']),
                      ([u'guolli', u'N', u'Sg', u'Com'], [u'guliin']),
                      ([u'guolli', u'N', u'Ess'], [u'guollin']),
                      ([u'guolli', u'N', u'Pl', u'Nom'], [u'guolit']),
                      ([u'guolli', u'N', u'Pl', u'Acc'], [u'guliid']),
                      ([u'guolli', u'N', u'Pl', u'Gen'], [u'guliid']),
                      ([u'guolli', u'N', u'Pl', u'Ill'], [u'guliide']),
                      ([u'guolli', u'N', u'Pl', u'Loc'], [u'guliin']),
                      ([u'guolli', u'N', u'Pl', u'Com'], [u'guliiguin'])]

            self.assertEqual(got, wanted)

    @parameterized.expand([
        (
                'north sami defaults', 'guollebiebman',
                {
                    'split_compounds': True,
                    'non_compound_only': False,
                    'no_derivations': False
                },
                [
                    'guollebiebman+N+Sg+Nom',
                    'guolli+N+Cmp/SgNom', 'biebman+N+Sg+Nom',
                    'biebman+N+Sg+Gen+Allegro', 'biebmat+V+TV',
                    'Der/NomAct+N+Sg+Nom',
                    'Der/NomAct+N+Sg+Gen', 'guollebiebman+N+Sg+Gen+Allegro'
                ]
        ),
        (
                'non compound True', 'guollebiebman',
                {
                    'split_compounds': True,
                    'non_compound_only': False,
                    'no_derivations': True
                },
                [
                    'guollebiebman+N+Sg+Nom', 'guolli+N+Cmp/SgNom',
                    'biebman+N+Sg+Nom', 'biebman+N+Sg+Gen+Allegro',
                    'guollebiebman+N+Sg+Gen+Allegro'
                ]
        ),
        (
                'remove_compound', 'guollebiebman',
                {
                    'split_compounds': True,
                    'non_compound_only': True,
                    'no_derivations': False
                },
                ['guollebiebman+N+Sg+Nom', 'guollebiebman+N+Sg+Gen+Allegro']
        ),
        (
                'split on compound false', 'guollebiebman',
                {
                    'split_compounds': False,
                    'non_compound_only': False,
                    'no_derivations': False
                },
                [
                    'guollebiebman+N+Sg+Nom',
                    'guolli+N+Cmp/SgNom+Cmp#biebman+N+Sg+Nom',
                    'guolli+N+Cmp/SgNom+Cmp#biebman+N+Sg+Gen+Allegro',
                    'guolli+N+Cmp/SgNom+Cmp#biebmat+V+TV',
                    'Der/NomAct+N+Sg+Nom', 'Der/NomAct+N+Sg+Gen',
                    'guollebiebman+N+Sg+Gen+Allegro'
                ]
        ),
        (
                'unknown input', 'asdf',
                {
                    'split_compounds': False,
                    'non_compound_only': False,
                    'no_derivations': False
                },
                ['asdf']
        )
    ])
    def test_lemmatize(self, name, wordform, kwargs, tags):
        """Test the lemmatizer with different arguments."""
        with app.app_context():
            got = app.config.morphologies['sme'].morph_lemmatize(wordform,
                                                                 **kwargs)
            wanted = self.make_lemmatize_answer(wordform, tags)
            self.assertListEqual(got, wanted, msg=name)

    @parameterized.expand([('no unknown', [('a', ['b', 'c'])], False),
                           ('has unknown', [('a', ['b', '?'])], True)])
    def test_has_unknown(self, name, lookups, wanted):
        self.assertEqual(
            app.config.morphologies['sme'].has_unknown(lookups), wanted, msg=name)


if __name__ == '__main__':
    unittest.main()
