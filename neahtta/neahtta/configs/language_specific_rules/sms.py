# -*- encoding: utf-8 -*-
""" Various rules for displaying ``sms`` entries properly, and
connecting FST to Lexicon.
"""

from neahtta.morphology import generation_overrides as morphology


@morphology.pregenerated_form_selector(*["sms", "smsM"])
def pregenerate_sms(form, tags, node, **kwargs):
    """**pregenerated form selector**: mini_paradigm / lemma_ref

    If mini_paradigm and lemma_ref exist for this node, then grab
    analyses and tags from the node, instead of from the FST.
    """
    _has_mini_paradigm = node.xpath(".//mini_paradigm[1]")

    _has_lemma_ref = node.xpath(".//lemma_ref")
    _pos = node.xpath(".//l/@pos")

    # Return tags but no forms in order to trigger further analysis attempts

    if len(_has_lemma_ref) > 0:
        return form, [], node, []
    if len(_has_mini_paradigm) == 0:
        return form, tags, node
    else:
        mp = _has_mini_paradigm[0]

    exclude_nds = mp.attrib.get("exclude", "") == "NDS"
    if exclude_nds:
        return form, tags, node, []

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
