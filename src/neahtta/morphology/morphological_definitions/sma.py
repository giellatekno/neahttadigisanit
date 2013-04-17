# -*- encoding: utf-8 -*-
""" sma-specific overrides, and pregenerated paradigm selection.
"""

# NOTE: if copying this for a new language, remember to make sure that
# it's being imported in __init__.py

from morphology import generation_overrides as rewrites

LEX_TO_FST = {
    'a': 'A',
    'adv': 'Adv',
    'n': 'N',
    # TODO: npl filter
    'npl': 'N',
    'num': 'Num',
    'prop': 'Prop',
    'v': 'V',
}

@rewrites.pregenerated_form_selector('sma')
def pregenerate_sma(form, tags, node):
    _has_mini_paradigm = node.xpath('.//mini_paradigm[1]')

    _has_lemma_ref     = node.xpath('.//lemma_ref')
    if len(_has_lemma_ref) > 0:
        return form, [], node, []
    if len(_has_mini_paradigm) == 0:
        return form, tags, node
    else:
        mp = _has_mini_paradigm[0]

    def analysis_node(node):
        """ Node ->
            ("lemma", ["Pron", "Sg", "Tag"], ["wordform", "wordform"])
        """
        tag = node.xpath('.//@ms')
        if len(tag) > 0:
            tag = tag[0].split('_')
        else:
            tag = []

        wfs = node.xpath('.//wordform/text()')

        return (form, tag, wfs)

    analyses = map(analysis_node, mp.xpath('.//analysis'))

    return form, tags, node, analyses

@rewrites.tag_filter_for_iso('sma')
def lexicon_pos_to_fst_sma(form, tags, node=None):

    new_tags = []
    for t in tags:
        _t = []
        for p in t:
            _t.append(LEX_TO_FST.get(p, p))
        new_tags.append(_t)

    return form, new_tags, node

@rewrites.tag_filter_for_iso('sma')
def include_hid_in_gen(form, tags, node):
    new_tags = tags[:]

    if len(node) > 0:
        hid = node.xpath('.//l/@hid')
        if hid:
            hid = hid[0]
            new_tags = []
            for tag in tags:
                ntag = [hid] + tag
                new_tags.append(ntag)

    return form, new_tags, node

@rewrites.tag_filter_for_iso('sma')
def proper_nouns(form, tags, node):
    if len(node) > 0:
        pos = node.xpath('.//l/@pos')
        _type = node.xpath('.//l/@type')

        if ("prop" in pos) or ("prop" in _type):
            tags = [
                'N+Prop+Sg+Gen'.split('+'),
                'N+Prop+Sg+Ill'.split('+'),
                'N+Prop+Sg+Ine'.split('+'),
            ]

    return form, tags, node


@rewrites.tag_filter_for_iso('sma')
def sma_common_noun_pluralia_tanta(form, tags, node):
    if len(node) > 0:
        num = node.xpath('.//l/@num')
        nr  = node.xpath('.//l/@nr')
        numera = False
        if len(num) > 0:
            numera = num[0].lower()
        if len(nr) > 0:
            numera = nr[0].lower()
        if numera == "pl":
            tags = [
                '+'.join(tag).replace('Sg', 'Pl').split('+')
                for tag in tags
            ]

    return form, tags, node
