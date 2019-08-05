# -*- encoding: utf-8 -*-
""" Various rules for displaying ``sme`` entries properly, and
connecting FST to Lexicon.
"""

# NOTE: if copying this for a new language, remember to make sure that
# it's being imported in __init__.py

# * paradigm documentation here:
#   https://giellalt.uit.no/dicts/dictionarywork.html

from logging import getLogger

from lexicon import autocomplete_filters as autocomplete_filters
from lexicon import lexicon_overrides as lexicon
from morpholex import morpholex_overrides as morpholex
from morphology import generation_overrides as morphology

morph_log = getLogger('morphology')

# This is called before any lookup is done, regardless of whether it
# came from analysis or not.


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

    _has_lemma_ref = node.xpath('.//lemma_ref')
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


_str_norm = 'string(normalize-space(%s))'

SME_NOB_DICTS = [
    ('sme', 'nob'),
    ('SoMe', 'nob'),
]

NOB_SME = [
    ('nob', 'sme'),
]


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
        _link_targ = u'/detail/%s/%s/%s.html' % ('sme', target_lang,
                                                 _lemma_ref)
        _lemma_ref_link = u'<a href="%s"/>%s</a>' % (_link_targ, _lemma_ref)
        _lemma_ref_link = u'<span class="see_also"> &rarr; ' + _lemma_ref_link
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
        _lemma_ref_link = u'<span class="see_also"> &rarr; ' + _link
        _lemma_ref_link += u'</span>'
        _transl_pos = "(%s)" % tag_filter.get(_pos)
        _new_str = [_lemma, _transl_pos, _lemma_ref_link]
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
            return "<a href='/nob/sme/ref/?l_til_ref=%s'>%s</a> &rarr;" % (
                _fra_ref, _fra_text)

    _type = e.xpath(_str_norm % 'lg/l/@type')
    _pos = e.xpath(_str_norm % 'lg/l/@pos')

    if _pos == 'N' and _type == 'Prop':
        _t_lemma = tg.xpath(_str_norm % 't/text()')
        _reg = tg.xpath(_str_norm % 't/@reg')
        if _reg:
            return "%s (%s)" % (_t_lemma, _reg)

    return None


def match_homonymy_entries(entries_and_tags):
    """ **Post morpho-lexicon override**

    This is performed after lookup has occurred, in order to filter out
    entries and analyses, when these depend on eachother.

    Here: we only want to return entries where the analysis type tag
    matches the entry type attribute.
    """
    filtered_results = []

    for entry, analyses in entries_and_tags:
        if entry is not None:
            entry_type = entry.find('lg/l').attrib.get('type', False)
            entry_analysis = entry.find('lg/analysis')
            tag_type = [
                x for x in [a.tag['type'] for a in analyses]
                if x is not None
            ]
            if entry_type:
                if len(tag_type) > 0:
                    if entry_type in tag_type:
                        filtered_results.append((entry, analyses))
                else:
                    if entry_type in tag_type:
                        filtered_results.append((entry, analyses))
                    else:
                        if entry_analysis is not None:
                            filtered_results.append((entry, analyses))
            else:
                part_in_tag_type = False
                if len(tag_type)>0:
                    for part in analyses[0].tag.parts:
                        if part in tag_type:
                            part_in_tag_type = True
                    if not part_in_tag_type:
                        filtered_results.append((entry, analyses))
                else:
                    filtered_results.append((entry, analyses))
        else:
            filtered_results.append((entry, analyses))

    return filtered_results


morpholex.post_morpho_lexicon_override('sme')(match_homonymy_entries)
