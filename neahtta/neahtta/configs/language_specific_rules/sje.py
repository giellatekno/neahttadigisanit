# -*- encoding: utf-8 -*-
"""
sje-specific overrides, and pregenerated paradigm selection.

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

from configs.language_specific_rules.common import match_homonymy_entries
from flask import current_app
from nds_lexicon import lexicon_overrides as lexicon
from morpholex import morpholex_overrides as morpholex
from morphology import generation_overrides as morphology


@lexicon.entry_source_formatter("sje")
def format_source_sje(ui_lang, e, target_lang):
    from morphology.utils import tagfilter_conf

    paren_args = []

    lemma = e.xpath("string(normalize-space(lg/l/text())")
    klass = e.xpath("string(normalize-space(lg/l/@class))")
    pos = e.xpath("string(normalize-space(lg/l/@pos))")

    lemma_ref = e.xpath("string(normalize-space(lg/lemma_ref/text()))")
    if lemma_ref:
        link_target = f"/detail/sje/{target_lang}/{lemma_ref}.html"
        lemma_ref_link = f'<a href="{link_target}"/>{lemma_ref}</a>'
        lemma_ref_link = f'<span class="see_also"> → {lemma_ref_link}</span>'
    else:
        lemma_ref_link = ""

    if pos:
        filters = current_app.config.tag_filters.get(("sje", "nob"))
        # paren_args.append(tagfilter_conf(filters, _pos))
        if filters:
            paren_args.append(tagfilter_conf(filters, pos))
        else:
            paren_args.append(pos)

    if klass:
        paren_args.append(klass)

    if paren_args:
        entry_string = f"{lemma} ({', '.join(paren_args)})"
        return entry_string + lemma_ref_link
    else:
        return lemma


@morphology.pregenerated_form_selector("sje")
def pregenerate_sje(form, tags, node, **kwargs):
    _has_mini_paradigm = node.xpath(".//mini_paradigm[1]")
    _has_lemma_ref = node.xpath(".//lemma_ref")

    if len(_has_lemma_ref) > 0:
        return form, [], node, []
    if len(_has_mini_paradigm) == 0:
        return form, tags, node
    else:
        mp = _has_mini_paradigm[0]

    def analysis_node(node):
        """Node ->
        ("lemma", ["Pron", "Sg", "Tag"], ["wordform", "wordform"])
        """
        tag = node.xpath(".//@ms")
        if len(tag) > 0:
            tag = tag[0].split("_")
        else:
            tag = []

        wfs = node.xpath(".//wordform/text()")

        return (form, tag, wfs)

    analyses = list(map(analysis_node, mp.xpath(".//analysis")))

    return form, tags, node, analyses


morpholex.post_morpho_lexicon_override("sje")(match_homonymy_entries)
