# -*- encoding: utf-8 -*-
"""Test classes from morphology/morphology.py"""

import unittest

from flask import current_app
from lxml import etree
from parameterized import parameterized

from morphology.morphology import Lemma, Tagsets
from neahtta import app

DEFAULT_SME_TAGSETS = {
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


def fst_tool():
    """Get the north sami fst tool."""
    return app.config.morphologies['sme'].tool


def make_lemmatize_answer(wordform, tags):
    """Make a list with the same format that Morpology.morph_lemmatize does.

    Args:
        wordform: the wordform that morph_lemmatize is fed
        tags: a list of tags that morph_lemmatize produces

    Returns:
        list of morphology.Lemma
    """
    if False in tags:
        return False

    return [
        Lemma(
            tag=tag.split('+'),
            _input=wordform,
            tool=fst_tool(),
            tagsets=Tagsets(DEFAULT_SME_TAGSETS)) for tag in tags
    ]


class TestHFST(unittest.TestCase):
    """Test the HFST class."""

    @parameterized.expand([
        ('known analysis', 'guolit\tguolli+N+Sg+Nom\t0,000000',
         ('guolit', 'guolli+N+Sg+Nom')),
        ('unknown analysis',
         u'geahppánit+V+Ind+Prs+Sg1\tgeahppánit+V+Ind+Prs+Sg1+?\tinf',
         (u'geahppánit+V+Ind+Prs+Sg1', u'geahppánit+V+Ind+Prs+Sg1+?\t+?'))
    ])
    def test_tagprocessor(self, name, analysis_line, result):
        """Test the tagprocessor."""
        self.assertEqual(
            fst_tool().tag_processor(analysis_line), result, msg=name)

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
            self.assertEqual(
                fst_tool().inverselookup(lemma, tags), wanted, msg=name)


class TestMorphology(unittest.TestCase):
    """Test the Morphology class."""

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
                      ([u'guolli', u'N', u'Sg', u'Gen'], [u'guoli']),
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
            [False]
        )
    ])
    def test_lemmatize(self, name, wordform, kwargs, tags):
        """Test the lemmatizer with different arguments."""
        with app.app_context():
            got = app.config.morphologies['sme'].morph_lemmatize(wordform,
                                                                 **kwargs)
            wanted = make_lemmatize_answer(wordform, tags)
            self.assertEqual(got, wanted, msg=name)

    @parameterized.expand([('no unknown', [('a', ['b', 'c'])], False),
                           ('has unknown', [('a', ['b', '?'])], True)])
    def test_has_unknown(self, name, lookups, wanted):
        """Test the morphology has unknown function."""
        self.assertEqual(
            app.config.morphologies['sme'].has_unknown(lookups), wanted,
            msg=name)

    def test_remove_compound_analyses(self):
        """Check if compounds are removed."""
        analyses_with_compounds = [
            'guollebiebman+N+Sg+Nom',
            'guolli+N+Cmp/SgNom+Cmp#biebmat+V+TV+Der/NomAct+N+Sg+Gen',
            'guolli+N+Cmp/SgNom+Cmp#biebmat+V+TV+Der/NomAct+N+Sg+Nom',
            'guolli+N+Cmp/SgNom+Cmp#biebman+N+Sg+Gen+Allegro',
            'guolli+N+Cmp/SgNom+Cmp#biebman+N+Sg+Nom'
        ]
        got = app.config.morphologies['sme'].remove_compound_analyses(
            analyses_with_compounds,
            True)
        wanted = ['guollebiebman+N+Sg+Nom']

        self.assertListEqual(got, wanted)

    def test_no_derivations(self):
        """Check if derivations are removed."""

        analyses_with_derivations = [
            'guollebiebman+N+Sg+Gen+Allegro',
            'guollebiebman+N+Sg+Nom',
            'guolli+N+Cmp/SgNom+Cmp#biebmat+V+TV+Der/NomAct+N+Sg+Gen',
            'guolli+N+Cmp/SgNom+Cmp#biebmat+V+TV+Der/NomAct+N+Sg+Nom',
            'guolli+N+Cmp/SgNom+Cmp#biebman+N+Sg+Gen+Allegro',
            'guolli+N+Cmp/SgNom+Cmp#biebman+N+Sg+Nom']
        got = app.config.morphologies['sme'].remove_derivations(
            analyses_with_derivations, True)
        wanted = ['guollebiebman+N+Sg+Gen+Allegro', 'guollebiebman+N+Sg+Nom',
                  'guolli+N+Cmp/SgNom+Cmp#biebman+N+Sg+Gen+Allegro',
                  'guolli+N+Cmp/SgNom+Cmp#biebman+N+Sg+Nom']

        self.assertListEqual(got, wanted)

    @parameterized.expand([
        (
            'wordform exists', 'guollebiebman',
            [
                'guollebiebman+N+Sg+Nom',
                'guolli+N+Cmp/SgNom+Cmp#biebmat+V+TV+Der/NomAct+N+Sg+Gen',
                'guolli+N+Cmp/SgNom+Cmp#biebmat+V+TV+Der/NomAct+N+Sg+Nom',
                'guolli+N+Cmp/SgNom+Cmp#biebman+N+Sg+Gen+Allegro',
                'guolli+N+Cmp/SgNom+Cmp#biebman+N+Sg+Nom'
            ],
            [
                'guollebiebman+N+Sg+Nom',
                'guolli+N+Cmp/SgNom+Cmp#biebmat+V+TV+Der/NomAct+N+Sg+Gen',
                'guolli+N+Cmp/SgNom+Cmp#biebmat+V+TV+Der/NomAct+N+Sg+Nom',
                'guolli+N+Cmp/SgNom+Cmp#biebman+N+Sg+Gen+Allegro',
                'guolli+N+Cmp/SgNom+Cmp#biebman+N+Sg+Nom'
            ]
        ),
        (
            'wordform does not exist', 'guollebiebmama',
            [
                'guolli+N+Cmp/SgNom+Cmp#biebman+N+Sg+Gen',
                'guolli+N+Cmp/SgNom+Cmp#biebman+N+Sg+Acc',
                'guolli+N+Cmp/SgNom+Cmp#biebmat+V+TV+Der/NomAct+N+Sg+Gen',
                'guolli+N+Cmp/SgNom+Cmp#biebmat+V+TV+Der/NomAct+N+Sg+Acc',
                'guollebiebman+N+Sg+Gen', 'guollebiebman+N+Sg+Acc'
            ],
            [
                'guollebiebman+N+Sg+Gen', 'guollebiebman+N+Sg+Acc',
                'guolli+N+Cmp/SgNom+Cmp#biebman+N+Sg+Gen',
                'guolli+N+Cmp/SgNom+Cmp#biebman+N+Sg+Acc',
                'guolli+N+Cmp/SgNom+Cmp#biebmat+V+TV+Der/NomAct+N+Sg+Gen',
                'guolli+N+Cmp/SgNom+Cmp#biebmat+V+TV+Der/NomAct+N+Sg+Acc'
            ]
        )
    ])
    def test_check_if_lexicalized(self, name, wordform, input_list, wanted):
        """Check if lexicalized form is moved to start of list."""
        got = app.config.morphologies['sme'].check_if_lexicalized(
            wordform, input_list)

        self.assertListEqual(got, wanted, msg=name)

    @parameterized.expand([('no dupes', ['a', 'b'], ['a', 'b']),
                           ('has dupes', ['a', 'a'], ['a'])])
    def test_remove_duplicates(self, name, input_list, result):
        """Test remove_duplicates."""
        self.assertListEqual(
            app.config.morphologies['sme'].remove_duplicates(input_list),
            result, msg=name)

    @parameterized.expand([
        ('nested is empty', [], ['a', 'b'], ['a', 'b']),
        ('not empty, not nested', ['c'], ['a', 'b'], []),
        ('first element not a list', ['c', ['d']], ['a', 'b'], []),
        ('all elements lists', [['d', 'e'], ['f', 'g']], ['a', 'b'],
         ['d', 'e', 'f', 'g']),
        ('first element is list', [['d', 'e'], 'f'], ['a', 'b'],
         ['d', 'e', 'f']),
    ])
    def test_fix_nested_array(self, name, nested_array, analyses, wanted):
        """Test fix_nested_array."""
        self.assertListEqual(
            app.config.morphologies['sme'].fix_nested_array(nested_array,
                                                            analyses),
            wanted,
            msg=name)

    @parameterized.expand(
        [
            (
                'split False',
                [
                    'guollebiebman+N+Sg+Nom',
                    'guolli+N+Cmp/SgNom+Cmp#biebmat+V+TV+Der/NomAct+N+Sg+Gen',
                ],
                False,
                [
                    'guollebiebman+N+Sg+Nom',
                    'guolli+N+Cmp/SgNom+Cmp#biebmat+V+TV+Der/NomAct+N+Sg+Gen',
                ]
            ),
            (
                'split True',
                [
                    'guollebiebman+N+Sg+Gen+Allegro', 'guollebiebman+N+Sg+Nom',
                    'guolli+N+Cmp/SgNom+Cmp#biebmat+V+TV+Der/NomAct+N+Sg+Gen',
                    'guolli+N+Cmp/SgNom+Cmp#biebmat+V+TV+Der/NomAct+N+Sg+Nom',
                    'guolli+N+Cmp/SgNom+Cmp#biebman+N+Sg+Gen+Allegro',
                    'guolli+N+Cmp/SgNom+Cmp#biebman+N+Sg+Nom'
                ],
                True,
                [
                    'guollebiebman+N+Sg+Gen+Allegro', 'guollebiebman+N+Sg+Nom',
                    'guolli+N+Cmp/SgNom', 'biebmat+V+TV+Der/NomAct+N+Sg+Gen',
                    'guolli+N+Cmp/SgNom', 'biebmat+V+TV+Der/NomAct+N+Sg+Nom',
                    'guolli+N+Cmp/SgNom', 'biebman+N+Sg+Gen+Allegro',
                    'guolli+N+Cmp/SgNom', 'biebman+N+Sg+Nom'
                ]
            )
        ])
    def test_split_on_compound(self, name, input_list, split_compounds,
                               wanted):
        """Test the morphology split on compound function."""
        self.assertListEqual(
            app.config.morphologies['sme'].split_on_compounds(input_list,
                                                              split_compounds),
            wanted,
            msg=name)

    @parameterized.expand([
        ('without err/orth', ['a', 'b+Der', 'c+Der'], ['a', 'b+Der']),
        ('with err/orth', ['a+Err/Orth', 'b+Der', 'c+Der'],
         ['a+Err/Orth', 'b+Der']),
        ('only der', ['a+Der', 'b+Der', 'c+Der'], ['a+Der'])
    ])
    def test_rearrange_on_count(self, name, analyses, wanted):
        """Test the morphology rearrange on count function."""
        self.assertListEqual(
            app.config.morphologies['sme'].rearrange_on_count(analyses), wanted,
            msg=name)

    @parameterized.expand([
        (
            'first',
            [
                'guollebiebman+N+Sg+Gen+Allegro', 'guollebiebman+N+Sg+Nom',
                'guolli+N+Cmp/SgNom', 'biebmat+V+TV+Der/NomAct+N+Sg+Gen',
                'guolli+N+Cmp/SgNom', 'biebmat+V+TV+Der/NomAct+N+Sg+Nom',
                'guolli+N+Cmp/SgNom', 'biebman+N+Sg+Gen+Allegro',
                'guolli+N+Cmp/SgNom', 'biebman+N+Sg+Nom'
            ],
            [
                'guollebiebman+N+Sg+Gen+Allegro',
                'guollebiebman+N+Sg+Nom',
                'guolli+N+Cmp/SgNom', 'biebmat+V+TV',
                'Der/NomAct+N+Sg+Gen',
                'Der/NomAct+N+Sg+Nom',
                'biebman+N+Sg+Gen+Allegro', 'biebman+N+Sg+Nom'
            ]
        ),
        (
            'Gerd',
            [
                u'Gerd+N+Prop+Sem/Fem+Attr', u'Gerd+N+Prop+Sem/Fem+Sg+Gen',
                u'Gerd+N+Prop+Sem/Fem+Sg+Acc', u'Gerd+N+Prop+Sem/Fem+Sg+Nom'
            ],
            [
                u'Gerd+N+Prop+Sem/Fem+Attr', u'Gerd+N+Prop+Sem/Fem+Sg+Gen',
                u'Gerd+N+Prop+Sem/Fem+Sg+Acc', u'Gerd+N+Prop+Sem/Fem+Sg+Nom'
            ]
        ),
        (
            'buoremus',
            [
                u'buorre+A+Superl+Attr', u'buorre+A+Superl+Sg+Nom'
            ],
            [
                u'buorre+A', u'Superl+Attr', u'Superl+Sg+Nom'
            ]
        ),
        (
            'vuojedettiin',
            [
                'vuodjit+V+TV+Ger'
            ],
            [
                'vuodjit+V+TV', 'Ger'
            ]
        ),
        (
            'biepmadettiin',
            [
                'biebmat+V+TV+Ger',
                'biebmat+V+TV+Der/d+V+Ger',
                'biepmadit+V+TV+Ger'
            ],
            [
                'biebmat+V+TV',
                'Ger',
                'Der/d+V',
                'biepmadit+V+TV'
            ]
        ),
        (
            'wordform',
            [
                'lemma1+A+Der+B+VAbess+C+Comp+D+Superl+E'
            ],
            [
                'lemma1+A', 'Der+B', 'VAbess+C', 'Comp+D', 'Superl+E'
            ]
        )
    ])
    def test_make_analyses_der_fin(self, name, analyses, wanted):
        """Test make_analyses_def_fin."""
        self.assertListEqual(
            app.config.morphologies['sme'].make_analyses_der_fin(analyses),
            wanted, msg=name)


def make_morpholex_result(result):
    """Make the same format as the morpholox lookup function does."""
    node, lemmas = result
    return node.find('.//l').text, node.find('.//t').text, lemmas


class TestMorphoLexicon(unittest.TestCase):
    """Test the MorphoLexicon class."""

    @parameterized.expand([
        ('sammensatt', 'guollebiebman', [
            (u'guollebiebman', u'oppdrettsvirksomhet',
             make_lemmatize_answer('guollebiebman',
                                   ['guollebiebman+N+Sg+Nom',
                                    'guollebiebman+N+Sg+Gen+Allegro'])),
            (u'guolli', u'fisk',
             make_lemmatize_answer('guolli',
                                   ['guolli+N+Cmp/SgNom'])),
            (u'biebman', u'ernæring',
             make_lemmatize_answer('biebman',
                                   ['biebman+N+Sg+Nom',
                                    'biebman+N+Sg+Gen+Allegro'])),
            (u'biebmat', u'fø',
             make_lemmatize_answer('biebmat',
                                   ['biebmat+V+TV'])),
            (u'Der/NomAct', u'verbhandlingen',
             make_lemmatize_answer('Der/NomAct',
                                   ['Der/NomAct+N+Sg+Nom',
                                    'Der/NomAct+N+Sg+Gen']))
        ]),
        ('verb', 'guoddit', [
            (u'guoddit', u'bære',
             make_lemmatize_answer('guoddit',
                                   ['guoddit+V+TV+Inf',
                                    'guoddit+V+TV+Imprt+Pl2',
                                    'guoddit+V+TV+Ind+Prs+Pl1',
                                    'guoddit+V+TV'])),
            (u'guoddi', u'bærer',
             make_lemmatize_answer('guoddi',
                                   ['guoddi+N+NomAg+Pl+Nom'])),
            ('Der/NomAg', u'den som utfører verbet',
             make_lemmatize_answer('Der/NomAg',
                                   ['Der/NomAg+N+Pl+Nom']))
        ]),
        ('pronomen', 'mii', [
            (u'mii', u'hva',
             make_lemmatize_answer('mii',
                                   ['mii+Pron+Rel+Sg+Nom',
                                    'mii+Pron+Interr+Sg+Nom',
                                    'mii+Pron+Indef+Sg+Nom'])),
            (u'mun', u'jeg',
             make_lemmatize_answer('mun',
                                   ['mun+Pron+Pers+Pl1+Nom']))
        ])
    ])
    def test_lookup(self, name, wordform, wanted):
        """Test the morpholex lookup function."""
        with app.app_context():
            kwargs = {
                'source_lang': 'sme',
                'target_lang': 'nob',
                'split_compounds': True,
                'non_compounds_only': False,
                'no_derivations': False,
            }
            result_list = current_app.morpholexicon.lookup(wordform, **kwargs)
            results = [make_morpholex_result(result)
                       for result in result_list]

            self.assertListEqual(results, wanted, msg=name)


if __name__ == '__main__':
    unittest.main()
