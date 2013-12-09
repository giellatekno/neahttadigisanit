# -*- encoding: utf-8 -*-
"""
sma-specific overrides, and pregenerated paradigm selection.

A set of lexicon-related language specific rules, provided by
`lexicon.LexiconOverrides`. There is probably a better location
for this documentation, but for now ...

Example source formatting function:

    @lexicon.entry_source_formatter('sme')
    def format_source_sme(ui_lang, entry_node):
        # do some processing on the entry node ...
        if successful:
            return some_formatted_string
        return None

Example target string formatting function:

    @lexicon.entry_target_formatter('sme', 'nob')
    def format_target_sme(ui_lang, entry_node, tg_node):
        # do some processing on the entry and tg node ...
        if successful:
            return some_formatted_string
        return None

"""

# NOTE: if copying this for a new language, remember to make sure that
# it's being imported in __init__.py

from morphology import generation_overrides as morphology
from lexicon import lexicon_overrides as lexicon
from flask import current_app

@lexicon.entry_source_formatter('sma')
def format_source_sma(ui_lang, e, target_lang):
    from morphology.utils import tagfilter_conf

    paren_args = []

    _str_norm = 'string(normalize-space(%s))'
    _lemma = e.xpath(_str_norm % 'lg/l/text()')
    _class = e.xpath(_str_norm % 'lg/l/@class')
    _pos = e.xpath(_str_norm % 'lg/l/@pos')

    _lemma_ref = e.xpath(_str_norm % 'lg/lemma_ref/text()')
    if _lemma_ref:
        _link_targ = u'/detail/%s/%s/%s.html' % ('sma', target_lang, _lemma_ref)
        _lemma_ref_link = u'<a href="%s"/>%s</a>' % (_link_targ, _lemma_ref)
        _lemma_ref_link = u'<span class="see_also"> → '  + _lemma_ref_link
        _lemma_ref_link += u'</span>'

    else:
        _lemma_ref_link = ''

    if _pos:
        filters = current_app.config.tag_filters.get(('sma', 'nob'))
        paren_args.append(tagfilter_conf(filters, _pos))

    if _class:
        paren_args.append(_class)

    if len(paren_args) > 0:
        entry_string = '%s (%s)' % (_lemma, ', '.join(paren_args))
        return entry_string + _lemma_ref_link
    else:
        return _lemma

    return None


LEX_TO_FST = {
    'a': 'A',
    'adv': 'Adv',
    'n': 'N',
    'npl': 'N',
    'num': 'Num',
    'prop': 'Prop',
    'v': 'V',
}

@morphology.pregenerated_form_selector('sma')
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

@morphology.tag_filter_for_iso('sma')
def lexicon_pos_to_fst_sma(form, tags, node=None):

    new_tags = []
    for t in tags:
        _t = []
        for p in t:
            _t.append(LEX_TO_FST.get(p, p))
        new_tags.append(_t)

    return form, new_tags, node

@morphology.tag_filter_for_iso('sma')
def add_homonymy_tag(form, tags, node):
    """ **Tag filter: homonym tags**

    If the entry selected has @hid, we need to insert this in order to
    generate the forms properly
    
        govledh+Hom1+V+TV+Ind+Prs+Sg3 

    """
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

@morphology.tag_filter_for_iso('sma')
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


@morphology.tag_filter_for_iso('sma')
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



from common import remove_blank

morphology.postgeneration_filter_for_iso(
    'sma',
)(remove_blank)

