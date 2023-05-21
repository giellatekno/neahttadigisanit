# -*- encoding: utf-8 -*-
""" Various rules for displaying ``smn`` entries properly, and
connecting FST to Lexicon.
"""

# NOTE: if copying this for a new language, remember to make sure that
# it's being imported in __init__.py

# * paradigm documentation here:
#   https://giellalt.github.io/dicts/dictionarywork.html

from logging import getLogger

from nds_lexicon import autocomplete_filters as autocomplete_filters
from morphology import generation_overrides as morphology

morph_log = getLogger('morphology')

@morphology.pregenerated_form_selector(*['smn', 'smnM'])
def pregenerate_smn(form, tags, node, **kwargs):
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

    analyses = list(map(analysis_node, mp.xpath('.//analysis')))

    return form, tags, node, analyses
