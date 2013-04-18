# -*- encoding: utf-8 -*-
# NOTE: if copying this for a new language, remember to make sure that
# it's being imported in __init__.py

# * paradigm documentation here:
#   http://giellatekno.uit.no/doc/dicts/dictionarywork.html

from logging import getLogger

from morphology import generation_overrides as morphology
from lexicon import lexicon_overrides as lexicon
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
}

morph_log = getLogger('morphology')

# This is called before any lookup is done, regardless of whether it
# came from analysis or not.

# NOTE: some mwe will mess things up here a bit, in that pos is
# passed in with part of the mwe. Thus, if there is no POS, do
# nothing.
@lexicon.pre_lookup_tag_rewrite_for_iso('sme')
def pos_to_fst(*args, **kwargs):
    if 'lemma' in kwargs and 'pos' in kwargs:
        _k = kwargs['pos'].replace('.', '').replace('+', '')
        new_pos = LEX_TO_FST.get(_k, False)
        if new_pos:
            kwargs['pos'] = new_pos
        else:
            morph_log.error("Missing LEX_TO_FST pair for %s" % _k.encode('utf-8'))
            morph_log.error("in morphology.morphological_definitions.sme")
    return args, kwargs

@lexicon.pre_lookup_tag_rewrite_for_iso('SoMe')
def some_pos_to_fst(*args, **kwargs):
    if 'lemma' in kwargs and 'pos' in kwargs:
        _k = kwargs['pos'].replace('.', '').replace('+', '')
        new_pos = LEX_TO_FST.get(_k, False)
        if new_pos:
            kwargs['pos'] = new_pos
        else:
            morph_log.error("Missing LEX_TO_FST pair for %s" % _k.encode('utf-8'))
            morph_log.error("in morphology.morphological_definitions.sme")
    return args, kwargs

# TODO: may no longer need to remove elements from tags now that those
# that are presented to users come directly from the pretty presentation
# analyzer, however other languages may need this, so here is a model.
# @morphology.post_analysis_processor_for_iso('sme')
# def test_f(generated_forms, *input_args, **input_kwargs):
#     exclusions = [
#         'Ani', 'Body', 'Build', 'Clth', 'Edu', 'Event', 'Fem',
#         'Food', 'Group', 'Hum', 'Mal', 'Measr', 'Obj', 'Org',
#         'Plant', 'Plc', 'Route', 'Sur', 'Time', 'Txt', 'Veh', 'Wpn',
#         'Wthr', 'Allegro', 'v1', 'v2', 'v3', 'v4',
#     ]
#     return generated_forms

# TODO: simplify this decorator process. really only need
# pregenerate_sme(node) -> returning analyses
@morphology.pregenerated_form_selector('sme')
def pregenerate_sme(form, tags, node):
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


@morphology.tag_filter_for_iso('sme')
def lexicon_pos_to_fst(form, tags, node=None):

    new_tags = []
    for t in tags:
        _t = []
        for p in t:
            _t.append(LEX_TO_FST.get(p, p))
        new_tags.append(_t)

    return form, new_tags, node

@morphology.tag_filter_for_iso('sme')
def impersonal_verbs(form, tags, node=None):
    if len(node) > 0:
        context = node.xpath('.//l/@context')

        if ("upers" in context) or ("dat" in context):
            new_tags = [
                'V+Ind+Prs+Sg3'.split('+'),
                'V+Ind+Prt+Sg3'.split('+'),
                'V+Ind+Prs+ConNeg'.split('+'),
            ]

            return form, new_tags, node

    return form, tags, node

@morphology.tag_filter_for_iso('sme')
def reciprocal_verbs(form, tags, node=None):
    if len(node) > 0:
        context = node.xpath('.//l/@context')

        if ("sii" in context):
            new_tags = [
                'V+Ind+Prs+Pl3'.split('+'),
                'V+Ind+Prt+Pl3'.split('+'),
                'V+Ind+Prs+ConNeg'.split('+'),
            ]

            return form, new_tags, node

    return form, tags, node

@morphology.tag_filter_for_iso('sme')
def common_noun_pluralia_tanta(form, tags, node):
    """ Pluralia tanta common noun

    `ruossalassánit` with <l nr="Pl" /> requires only plural
    paradigm.
    """
    if len(node) > 0:
        nr = node.xpath('.//l/@nr')
        if ("pl" in nr) or ("Pl" in nr):
            tags = [
                'N+Pl+Nom'.split('+'),
                'N+Pl+Ill'.split('+'),
                'N+Pl+Loc'.split('+'),
            ]

    return form, tags, node

@morphology.tag_filter_for_iso('sme')
def proper_noun_pluralia_tanta(form, tags, node):
    """ Pluralia tanta

    `Gállábártnit` with <l nr="Pl" /> requires only plural
    paradigm.

    Note, there is a singularia tanta, but this may require a separate
    rule, as it mostly concerns pronouns.
    """
    if len(node) > 0:
        _type = node.xpath('.//l/@type')
        nr = node.xpath('.//l/@nr')
        if (("pl" in nr) or ("Pl" in nr)) and ("Prop" in _type):
            tags = [
                'N+Prop+Pl+Gen'.split('+'),
                'N+Prop+Pl+Ill'.split('+'),
                'N+Prop+Pl+Loc'.split('+'),
            ]

    return form, tags, node

@morphology.tag_filter_for_iso('sme')
def compound_numerals(form, tags, node):
    if len(node) > 0:
        if 'num' in node.xpath('.//l/@pos'):
            tags = [
                'Num+Sg+Gen'.split('+'),
                'Num+Sg+Ill'.split('+'),
                'Num+Sg+Loc'.split('+'),
            ]
    return form, tags, node

context_for_tags = {
    ("mun", "V+Ind+Prs+Sg1"):       "(odne mun) %(word_form)s",
    ("mun", "V+Ind+Prt+Sg1"):       "(ikte mun) %(word_form)s",
    ("mun", "V+Ind+Prs+ConNeg"):    "(in) %(word_form)s",

    # EX: ciellat
    ("dat", "V+Ind+Prs+Sg3"):       "(odne dat) %(word_form)s",
    ("dat", "V+Ind+Prt+Sg3"):       "(ikte dat) %(word_form)s",
    ("dat", "V+Ind+Prs+ConNeg"):    "(ii) %(word_form)s",

    # EX: deaivvadit
    # TODO: requires a tag filter above to include Pl3 in paradigm
    ("sii", "V+Ind+Prs+Pl3"):       "(odne sii) %(word_form)s",
    ("sii", "V+Ind+Prt+Pl3"):       "(ikte sii) %(word_form)s",
    ("sii", "V+Ind+Prs+ConNeg"):    "(eai) %(word_form)s",

    # EX: bieggat
    ("upers", "V+Ind+Prs+Sg1"):       "(odne) %(word_form)s",
    ("upers", "V+Ind+Prt+Sg1"):       "(ikte) %(word_form)s",
    ("upers", "V+Ind+Prs+ConNeg"):    "(ii) %(word_form)s",

}

@morphology.postgeneration_filter_for_iso('sme')
def verb_context(generated_result, *generation_input_args):
    # lemma = generation_input_args[0]
    # tags  = generation_input_args[1]
    node  = generation_input_args[2]

    if len(node) == 0:
        return generated_result

    context = node.xpath('.//l/@context')

    if len(context) > 0:
        context = context[0]
    else:
        return generated_result

    def apply_context(form):
        lemma, tag, forms = form
        tag = '+'.join(tag)

        context_formatter = context_for_tags.get((context, tag), False)
        if context_formatter:
            formatted = []
            for f in forms:
                f = context_formatter % {'word_form': f}
                formatted.append(f)
            formatted_forms = formatted
        else:
            formatted_forms = forms

        tag = tag.split('+')

        return (lemma, tag, formatted_forms)

    return map(apply_context, generated_result)

# TODO: post-generated tag morphology for sme, because FST must have
# +These+Kinds+Of+Tags
# @morphology.postgeneration_filter_for_iso('sme')


@morpholex.post_morpho_lexicon_override('sme')
def remove_analyses_for_lemma_ref(xml, fst):
    if xml is None or fst is None:
        return None

    _str_norm = 'string(normalize-space(%s))'

    # TODO: group xml nodes by lemma

    # if there is an entry that is an analysis and the set contains
    # another entry with its matching lemma, then discard the entries
    # that are the lemma, and discard the analyses, and display only the
    # one lemma_ref entry.

    from collections import defaultdict
    nodes_by_lemma = defaultdict(list)

    for e in xml:
        lemma = e.xpath(_str_norm % 'lg/l/text()')
        lemma_ref_lemma = e.xpath(_str_norm % 'lg/lemma_ref/text()')

        if lemma_ref_lemma:
            nodes_by_lemma[lemma_ref_lemma].append(
                (e, True)
            )
        elif lemma:
            nodes_by_lemma[lemma].append(
                (e, False)
            )

    def node_lg_l_matches_str(n, s):
        lg_l = n.xpath(
            _str_norm % 'lg/l/text()'
        )
        return lg_l == s


    return_nodes = []
    for lemma, nodes in nodes_by_lemma.iteritems():
        # get the lemma_ref node
        lemma_ref_node = filter( lambda (n, is_lemma_ref): is_lemma_ref
                               , nodes
                               )
        if len(lemma_ref_node) == 0:
            return_nodes.append([node for node, _ in nodes])
            continue
        # if it exists... 
        if len(lemma_ref_node) > 0:
            _l_node, _is_l_ref = lemma_ref_node[0]
            lemma_ref_lemma = _l_node.xpath(
                _str_norm % 'lg/lemma_ref/text()'
            )

            # Match nodes by lg_l vs. lemma_ref_string
            _match = lambda (m_n, _): \
                node_lg_l_matches_str(m_n, lemma_ref_lemma)
            lemmas_matching = filter( _match, nodes )
            # If there is a lemma for the lemma_ref string ...
            if len(lemmas_matching) > 0:
                # include the lemma_ref node in output
                return_nodes.append(_l_node)

                def analysis_lemma_is_not(analysis):
                    return lemma_ref_lemma != analysis.lemma

                # wipe out analyses in fst for a lemma if there is a lemma_ref
                fst = filter( analysis_lemma_is_not
                            , fst
                            )

    if len(return_nodes) == 0:
        return_nodes = xml

    if isinstance(return_nodes, list) and isinstance(return_nodes[0], list):
        return_nodes = sum(return_nodes, [])

    return return_nodes, fst

# TODO: same for SoMe

# TODO: general thing to not display analyses for specific parts of
# speech, must be registered after above fx because we still want
# analyses to filter out lemmas and lemma_refs

# TODO: display paradigm even for lemma_ref entries?
