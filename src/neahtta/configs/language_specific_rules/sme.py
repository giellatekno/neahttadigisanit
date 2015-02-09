# -*- encoding: utf-8 -*-
""" Various rules for displaying ``sme`` entries properly, and
connecting FST to Lexicon.
"""

# NOTE: if copying this for a new language, remember to make sure that
# it's being imported in __init__.py

# * paradigm documentation here:
#   http://giellatekno.uit.no/doc/dicts/dictionarywork.html

from logging import getLogger

from morphology import generation_overrides as morphology
from lexicon import lexicon_overrides as lexicon
from lexicon import autocomplete_filters as autocomplete_filters
from morpholex import morpholex_overrides as morpholex

LEX_TO_FST = {
    'a': 'A',
    'adj': 'A',
    'adp': 'Adp',
    'adv': 'Adv',
    'aktor': 'NomAg',
    'egen': 'Prop',
    'interj': 'Interj',
    'konj': 'CC',
    'n': 'N',
    'npl': 'N',
    'num': 'Num',
    'part': 'Pcle',
    'postp': 'Po',
    'prep': 'Pr',
    'pron': 'Pron',
    'prop': 'Prop',
    'subj': 'CS',
    'subst': 'N',
    'v': 'V',
    'verb': 'V',
    '': '',
}

morph_log = getLogger('morphology')

# This is called before any lookup is done, regardless of whether it
# came from analysis or not.

# TODO: til_ref / fra_ref
#  * need to allow <lg> <l /> </lg> (blank)
#  * need to render <mg /> with fra_ref, with links which generate a
#  query to til_ref 
#  * maybe include these in get parameters or something. 

# NOTE: some mwe will mess things up here a bit, in that pos is
# passed in with part of the mwe. Thus, if there is no POS, do
# nothing.
@lexicon.pre_lookup_tag_rewrite_for_iso(*['sme', 'SoMe'])
def pos_to_fst(*args, **kwargs):
    """ For synchronizing PoS between lexicon and FST. Should be less
    necessary now.

    TODO: generalize to a setting in .yaml or somewhere.
    """
    if 'lemma' in kwargs and 'pos' in kwargs:
        _k = kwargs.get('pos', '')
        if _k is not None:
            _k = _k.replace('.', '').replace('+', '')
            new_pos = LEX_TO_FST.get(_k, False)
        else:
            _k = False
            new_pos = False
        if new_pos:
            kwargs['pos'] = new_pos
        else:
            if _k:
                morph_log.error("sme.py: Missing LEX_TO_FST pair for %s" % _k.encode('utf-8'))
                morph_log.error("sme.py: in morphology.morphological_definitions.sme")
    return args, kwargs

@autocomplete_filters.autocomplete_filter_for_lang(('nob', 'sme'))
def remove_orig_entry(entries):
    _entries = [e for e in entries if 'orig_entry' not in e.attrib]
    return _entries

@morphology.pregenerated_form_selector(*['sme', 'SoMe'])
def pregenerate_sme(form, tags, node, **kwargs):
    """ **pregenerated form selector**: mini_paradigm / lemma_ref

    If mini_paradigm and lemma_ref exist for this node, then grab
    analyses and tags from the node, instead of from the FST.
    """
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


@morphology.tag_filter_for_iso(*['sme', 'SoMe'])
def lexicon_pos_to_fst(form, tags, node=None, **kwargs):
    """ **tag filter**: Lexicon -> FST changes.

    Change POS to be compatible with FST for when they are not.
    """

    new_tags = []
    for t in tags:
        _t = []
        for p in t:
            _t.append(LEX_TO_FST.get(p, p))
        new_tags.append(_t)

    return form, new_tags, node


_str_norm = 'string(normalize-space(%s))'

# commented out; Bug 1719

### NB: if commenting back in, argument structure for decorator function is changed.
### @morpholex.post_morpho_lexicon_override(*['sme', 'SoMe'])
### def remove_analyses_for_analyzed_forms_with_lemma_ref(xml, fst):
###     """ **Post morpho-lexicon override**
### 
###     If there is an entry that is an analysis and the set of XML entries
###     resulting from the lookup contains another entry with its matching
###     lemma, then discard the analyses.
###     """
### 
###     if xml is None or fst is None:
###         return None
### 
###     from collections import defaultdict
###     nodes_by_lemma = defaultdict(list)
### 
###     for e in xml:
###         lemma = e.xpath(_str_norm % 'lg/l/text()')
###         lemma_ref_lemma = e.xpath(_str_norm % 'lg/lemma_ref/text()')
### 
###         if lemma_ref_lemma:
###             nodes_by_lemma[lemma_ref_lemma].append(
###                 (e, True)
###             )
###         elif lemma:
###             nodes_by_lemma[lemma].append(
###                 (e, False)
###             )
### 
###     def lg_l_matches_str(n, s):
###         return n.xpath(_str_norm % 'lg/l/text()') == s
### 
###     for lemma, nodes in nodes_by_lemma.iteritems():
###         # get the lemma_ref node
###         lemma_ref_node = filter( lambda (n, is_lemma_ref): is_lemma_ref
###                                , nodes
###                                )
### 
###         if len(lemma_ref_node) > 0:
###             _l_node, _is_l_ref = lemma_ref_node[0]
###             lemma_ref_lemma = _l_node.xpath(
###                 _str_norm % 'lg/lemma_ref/text()'
###             )
### 
###             # Match nodes by lg_l vs. lemma_ref_string
###             _match = lambda (m_n, _): \
###                 lg_l_matches_str(m_n, lemma_ref_lemma)
###             lemmas_matching = filter( _match, nodes )
###             # If there is a lemma for the lemma_ref string ...
###             if len(lemmas_matching) > 0:
###                 def analysis_lemma_is_not(analysis):
###                     return lemma_ref_lemma != analysis.lemma
### 
###                 # wipe out analyses in fst for a lemma if there is a lemma_ref
###                 fst = filter( analysis_lemma_is_not
###                             , fst
###                             )
### 
###     return xml, fst

# commented out; bug 1719

### NB: if commenting back in, argument structure for decorator function is changed.
### @morpholex.post_morpho_lexicon_override(*['sme', 'SoMe'])
### def remove_analyses_for_specific_closed_classes(xml, fst):
###     """ **Post morpho-lexicon override**
### 
###     Remove analyses from list when the XML entry contains a specific PoS
###     type.
### 
###     This has to be done in two steps:
###      * check for xml entries containing the types
###      * filter out the matching lemma from those entries, *or*, remove
###        analyses that have a member of the hideanalysis tagset
### 
###     NB: this must be registered after ``remove_analyses_for_analyzed_forms_with_lemma_ref``,
###     because that function depends on analyses still existing to some of
###     these types.
###     """
### 
###     if xml is None or fst is None:
###         return None
### 
###     restrict_xml_type = [ 'Pers'
###                         , 'Dem'
###                         , 'Rel'
###                         , 'Refl'
###                         , 'Recipr'
###                         , 'Neg'
###                         ]
### 
###     restrict_lemmas = [ 'leat'
###                       ]
### 
###     for e in xml:
###         _pos_type = e.xpath(_str_norm % 'lg/l/@type')
###         _lemma = e.xpath(_str_norm % 'lg/l/text()')
### 
###         if _pos_type in restrict_xml_type:
###             restrict_lemmas.append(_lemma)
### 
###     def lemma_not_in_list(lemma):
###         _lemma = lemma.lemma not in restrict_lemmas
###         return _lemma
### 
###     def hideanalysis_tagset(lemma):
###         _hide = lemma.tag['hideanalysis']
###         _hide_analysis = True
###         if _hide:
###             if len(_hide) > 0:
###                 _hide_analysis = False
### 
###         return _hide_analysis
### 
###     fst = filter( hideanalysis_tagset
###                 , filter( lemma_not_in_list
###                         , fst
###                         )
###                 )
### 
###     return xml, fst

SME_NOB_DICTS = [
    ('sme', 'nob'),
    ('SoMe', 'nob'),
]

NOB_SME = [
    ('nob', 'sme'),
]

# NB: this filter is what would be needed, but now we're going to trust
# the lexicon is pre-prepared instead.
# @lexicon.postlookup_filters_for_lexicon(*SME_NOB_DICTS)
# def usage_vd_only_for_entry(lexicon, nodelist, lookup_kwargs):
#     def filter_node(n):
#         usages = n.get('usage', '').split(',')
#         return 'vd' in usages or 'nds' in usages
#     if nodelist:
#         return filter(filter_node, nodelist)
#     else:
#         return nodelist

# @lexicon.postlookup_filters_for_lexicon(*NOB_SME)
# def clean_tgs_with_no_usage_vd(lexicon, nodelist, lookup_kwargs):
#     """ A little node manipulation to remove <t /> nodes without
#     usage=vd.
# 
#     Basically: go through all <mg />/<tg />, iterate <t />, and if it is
#     not usage=vd, remove it; then if this results in the <tg /> having
#     no entries, clear.
#     """
#     def clean_tgs(n):
#         for tg in n.xpath('./mg/tg'):
#             _ts = tg.xpath('./t')
#             for t in _ts:
#                 if not t.get('usage', '') == 'vd':
#                     tg.remove(t)
#             _ts = tg.xpath('./t')
#             if len(_ts) == 0:
#                 tg.clear()
#         return n
#     if nodelist:
#         return map(clean_tgs, nodelist)
#     return nodelist

@lexicon.entry_source_formatter(*['sme', 'SoMe'])
def format_source_sme(ui_lang, e, target_lang):
    """ **Entry source formatter**

    Format the source for a variety of parameters. Here:

     * Include @pos and @class attributes
     * if there is a lemma_ref, then we provide the link to that
       entry too (e.g., munnje)
    # TODO: new-style templates
    """
    from morphology.utils import tagfilter_conf
    from flask import current_app

    paren_args = []

    _str_norm = 'string(normalize-space(%s))'
    _lemma = e.xpath(_str_norm % 'lg/l/text()')
    _class = e.xpath(_str_norm % 'lg/l/@class')
    _pos = e.xpath(_str_norm % 'lg/l/@pos')

    _lemma_ref = e.xpath(_str_norm % 'lg/lemma_ref/text()')

    _til_ref = e.xpath(_str_norm % 'lg/l/@til_ref')

    if _lemma_ref:
        _link_targ = u'/detail/%s/%s/%s.html' % ('sme', target_lang, _lemma_ref)
        _lemma_ref_link = u'<a href="%s"/>%s</a>' % (_link_targ, _lemma_ref)
        _lemma_ref_link = u'<span class="see_also"> &rarr; '  + _lemma_ref_link
        _lemma_ref_link += u'</span>'
    else:
        _lemma_ref_link = ''

    if _pos:
        filters = current_app.config.tag_filters.get(('sme', ui_lang))
        if filters:
            paren_args.append(tagfilter_conf(filters, _pos))
        else:
            paren_args.append(_pos)

    if _class:
        paren_args.append(_class.lower())

    if len(paren_args) > 0:
        thing = '%s (%s)' % (_lemma, ', '.join(paren_args))
        return thing + _lemma_ref_link
    else:
        return _lemma

    return None

@lexicon.entry_source_formatter('nob')
def format_source_nob(ui_lang, e, target_lang):
    """ **Entry source formatter**

    Format the source for a variety of parameters. Here:

     * Include @pos and @class attributes
     * if there is a lemma_ref, then we provide the link to that
       entry too (e.g., munnje)
    # TODO: new-style templates
    """
    from morphology.utils import tagfilter_conf
    from flask import current_app

    paren_args = []

    _str_norm = 'string(normalize-space(%s))'
    _lemma = e.xpath(_str_norm % 'lg/l/text()')
    _class = e.xpath(_str_norm % 'lg/l/@class')
    _pos = e.xpath(_str_norm % 'lg/l/@pos')

    _lemma_ref = e.xpath(_str_norm % 'lg/lemma_ref/text()')

    _til_ref = e.xpath(_str_norm % 'lg/l/@til_ref')
    _orig_entry = e.xpath(_str_norm % 'lg/l/@orig_entry')

    tag_filter = current_app.config.tag_filters.get(('sme', 'nob'))
    if _til_ref and _orig_entry:
        _link_return = "/nob/sme/ref/?l_til_ref=%s" % _orig_entry
        _link = "<a href='%s'>%s</a>" % (_link_return, _orig_entry)
        _lemma_ref_link = u'<span class="see_also"> &rarr; '  + _link
        _lemma_ref_link += u'</span>'
        _transl_pos = "(%s)" % tag_filter.get(_pos)
        _new_str = [ _lemma
                   , _transl_pos
                   , _lemma_ref_link
                   ]
        _new_str = ' '.join(_new_str)
        return _new_str

    return None

@lexicon.entry_target_formatter(('sme', 'nob'), ('SoMe', 'nob'))
def format_target_sme(ui_lang, e, tg):
    """**Entry target translation formatter**

    Display @reg (region) attribute in translations, but only for ``N
    Prop``.

    # TODO: new-style templates
    """
    _str_norm = 'string(normalize-space(%s))'

    _type = e.xpath(_str_norm % 'lg/l/@type')
    _pos = e.xpath(_str_norm % 'lg/l/@pos')

    if _pos == 'N' and _type == 'Prop':
        _t_lemma = tg.xpath(_str_norm % 't/text()')
        _reg = tg.xpath(_str_norm % 't/@reg')
        if _reg:
            return "%s (%s)" % (_t_lemma, _reg)

    return None

@lexicon.entry_target_formatter(('nob', 'sme'))
def format_fra_ref_links(ui_lang, e, tg):
    """**Entry target translation formatter**

    Display @reg (region) attribute in translations, but only for ``N
    Prop``.
    """
    # print 'format_fra_ref_links'
    _str_norm = 'string(normalize-space(%s))'

    _fra_ref = tg.xpath(_str_norm % 're/@fra_ref')
    _fra_text = tg.xpath(_str_norm % 're/text()')

    # print ''
    # print _fra_text
    # print _fra_ref

    if _fra_ref is not None:
        if len(_fra_ref) > 0:
            return "<a href='/nob/sme/ref/?l_til_ref=%s'>%s</a> &rarr;" % (_fra_ref, _fra_text)

    _type = e.xpath(_str_norm % 'lg/l/@type')
    _pos = e.xpath(_str_norm % 'lg/l/@pos')

    if _pos == 'N' and _type == 'Prop':
        _t_lemma = tg.xpath(_str_norm % 't/text()')
        _reg = tg.xpath(_str_norm % 't/@reg')
        if _reg:
            return "%s (%s)" % (_t_lemma, _reg)

    return None

from common import remove_blank

# Remove blank analyses
morphology.postgeneration_filter_for_iso(
    'sme',
    'SoMe'
)(remove_blank)
