# -*- encoding: utf-8 -*-
""" Various rules for displaying ``sme`` entries properly, and
connecting FST to Lexicon.
"""

# NOTE: if copying this for a new language, remember to make sure that
# it's being imported in __init__.py

# * paradigm documentation here:
#   https://giellalt.github.io/dicts/dictionarywork.html

from logging import getLogger

from neahtta.nds_lexicon import autocomplete_filters as autocomplete_filters
from neahtta.nds_lexicon import lexicon_overrides as lexicon
from neahtta.morpholex import morpholex_overrides as morpholex
from neahtta.morphology import generation_overrides as morphology

morph_log = getLogger("morphology")

# This is called before any lookup is done, regardless of whether it
# came from analysis or not.


@autocomplete_filters.autocomplete_filter_for_lang(("nob", "sme"))
def remove_orig_entry(entries):
    return [e for e in entries if "orig_entry" not in e.attrib]


@morphology.pregenerated_form_selector(*["sme", "SoMe"])
def pregenerate_sme(form, tags, node, **kwargs):
    """**pregenerated form selector**: mini_paradigm / lemma_ref

    If mini_paradigm and lemma_ref exist for this node, then grab
    analyses and tags from the node, instead of from the FST.
    """
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


_str_norm = "string(normalize-space(%s))"

SME_NOB_DICTS = [
    ("sme", "nob"),
    ("SoMe", "nob"),
]

NOB_SME = [
    ("nob", "sme"),
]


@lexicon.entry_source_formatter(*["sme", "SoMe"])
def format_source_sme(ui_lang, e, target_lang):
    """**Entry source formatter**

    Format the source for a variety of parameters. Here:

     * Include @pos and @class attributes
     * if there is a lemma_ref, then we provide the link to that
       entry too (e.g., munnje)
    # TODO: new-style templates
    """
    from flask import current_app
    from neahtta.morphology.utils import tagfilter_conf

    paren_args = []

    lemma = e.xpath("string(normalize-space(lg/l/text()))")
    klass = e.xpath("string(normalize-space(lg/l/@class))")
    pos = e.xpath("string(normalize-space(lg/l/@pos))")

    lemma_ref = e.xpath("string(normalize-space(lg/lemma_ref/text()))")

    if lemma_ref:
        link_target = f"/detail/sme/{target_lang}/{lemma_ref}.html"
        lemma_ref_link = f'<a href="{link_target}"/>{lemma_ref}</a>'
        lemma_ref_link = f'<span class="see_also"> &rarr; {lemma_ref_link}'
        lemma_ref_link += "</span>"
    else:
        lemma_ref_link = ""

    if pos:
        filters = current_app.config.tag_filters.get(("sme", ui_lang))
        if filters:
            paren_args.append(tagfilter_conf(filters, pos))
        else:
            paren_args.append(pos)

    if klass:
        paren_args.append(klass.lower())

    if paren_args:
        thing = f"{lemma} ({', '.join(paren_args)})"
        return thing + lemma_ref_link
    else:
        return lemma


@lexicon.entry_source_formatter("nob")
def format_source_nob(ui_lang, e, target_lang):
    """**Entry source formatter**

    Format the source for a variety of parameters. Here:

     * Include @pos and @class attributes
     * if there is a lemma_ref, then we provide the link to that
       entry too (e.g., munnje)
    """
    from flask import current_app

    lemma = e.xpath("string(normalize-space(lg/l/text()))")
    pos = e.xpath("string(normalize-space(lg/l/@pos))")
    til_ref = e.xpath("string(normalize-space(lg/l/@til_ref))")
    orig_entry = e.xpath("string(normalize-space(lg/l/@orig_entry))")

    lemma_ref = e.xpath("string(normalize-space(lg/lemma_ref/text()))")

    tag_filter = current_app.config.tag_filters.get(("sme", "nob"))
    if til_ref and orig_entry:
        link_return = f"/nob/sme/ref/?l_til_ref={orig_entry}"
        link = f'<a href="{link_return}">{orig_entry}</a>'
        lemma_ref_link = f'<span class="see_also"> &rarr; {link}</span>'
        transl_pos = f"({tag_filter.get(pos)})"
        return f"{lemma} {transl_pos} {lemma_ref_link}"


@lexicon.entry_target_formatter(("sme", "nob"), ("SoMe", "nob"))
def format_target_sme(ui_lang, e, tg):
    """**Entry target translation formatter**

    Display @reg (region) attribute in translations, but only for ``N
    Prop``.
    """
    typ = e.xpath("string(normalize-space(lg/l/@type))")
    pos = e.xpath("string(normalize-space(lg/l/@pos))")

    if pos == "N" and typ == "Prop":
        reg = tg.xpath("string(normalize-space(t/@reg))")
        if reg:
            t_lemma = tg.xpath("string(normalize-space(t/text()))")
            return f"{t_lemma} ({reg})"


@lexicon.entry_target_formatter(("nob", "sme"))
def format_fra_ref_links(ui_lang, e, tg):
    """**Entry target translation formatter**

    Display @reg (region) attribute in translations, but only for ``N
    Prop``.
    """
    _str_norm = "string(normalize-space(%s))"

    fra_ref = tg.xpath("string(normalize-space(re/@fra_ref))")
    fra_text = tg.xpath("string(normalize-space(re/text()))")

    if fra_ref is not None:
        if len(fra_ref) > 0:
            href = f"/nob/sme/ref/?l_til_ref={fra_ref}"
            return f'<a href="{href}">{fra_text}</a> &rarr;'

    typ = e.xpath("string(normalize-space(lg/l/@type))")
    pos = e.xpath("string(normalize-space(lg/l/@pos))")

    if pos == "N" and typ == "Prop":
        reg = tg.xpath("string(normalize-space(t/@reg))")
        if reg:
            t_lemma = tg.xpath("string(normalize-space(t/text()))")
            return f"{t_lemma} ({reg})"


def match_homonymy_entries(entries_and_tags):
    """**Post morpho-lexicon override**

    This is performed after lookup has occurred, in order to filter out
    entries and analyses, when these depend on eachother.

    Here: we only want to return entries where the analysis type tag
    matches the entry type attribute.
    """
    filtered_results = []
    is_analysis = False

    for entry, analyses in entries_and_tags:
        analyses_to_append = []
        if entry is not None:
            entry_type = entry.find("lg/l").attrib.get("type", False)
            entry_analysis = entry.find("lg/analysis")
            if entry_analysis is not None:
                is_analysis = True
            tag_type = [x for x in [a.tag["type"] for a in analyses]]
            if entry_type:
                if len(tag_type) > 0:
                    if entry_type in tag_type or is_analysis:
                        filtered_results.append((entry, analyses))
                else:
                    if entry_type in tag_type:
                        filtered_results.append((entry, analyses))
                    else:
                        if entry_analysis is not None:
                            filtered_results.append((entry, analyses))
            else:
                part_in_tag_type = False
                if len(tag_type) > 0:
                    i = 0
                    for analysis in analyses:
                        for part in analysis.tag.parts:
                            if part in tag_type:
                                part_in_tag_type = True
                        if not part_in_tag_type:
                            analyses_to_append.append(analysis)
                        if not entry_type and tag_type[i] is None:
                            analyses_to_append.append(analyses[i])
                        i += 1
                    filtered_results.append((entry, analyses_to_append))
                else:
                    filtered_results.append((entry, []))
        else:
            print("no entry")
            filtered_results.append((entry, analyses))

    # Check in filtered_results if there are entries with same lemma but one
    # has static paradigm (and matches the search). If yes, display only
    # entry with static paradigm. (Maybe too many arrays, should make it
    # more elegant!)
    entries_lemmaID_pos = []
    lemma_pos_array = []
    for entry, analyses in filtered_results:
        is_analysis = False
        if entry is not None:
            has_lemma_ref = entry.find("lg/lemma_ref")
            entry_analysis = entry.find("lg/analysis")
            entry_type = entry.find("lg/l").attrib.get("type", False)
            if entry_analysis is not None:
                is_analysis = True
        else:
            has_lemma_ref = None
        lemmaID = False
        pos = False
        lemma_pos_pair = []
        if has_lemma_ref is not None:
            entry_lemmaID = entry.find("lg/lemma_ref").attrib.get("lemmaID", False)
            lemmaID = entry_lemmaID.split("_")[0]
            pos = entry_lemmaID.split("_")[1].upper()
        for item in analyses:
            if [str(item.lemma), str(item.pos)] not in lemma_pos_pair:
                lemma_pos_pair.append([str(item.lemma), str(item.pos)])
        if len(lemma_pos_pair) == 1:
            lemma_pos_pair = lemma_pos_pair[0]
        entries_lemmaID_pos.append([entry, lemma_pos_pair, [lemmaID, pos]])
        lemma_pos_array.append([lemma_pos_pair, [lemmaID, pos]])

    for var in lemma_pos_array:
        if var in lemma_pos_array and [[], var[0]] in lemma_pos_array:
            entries_lemmaID_pos.pop(lemma_pos_array.index(var))
            filtered_results.pop(lemma_pos_array.index(var))

    return filtered_results


morpholex.post_morpho_lexicon_override("sme")(match_homonymy_entries)
