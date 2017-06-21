from morphology import generation_overrides as morphology
from lexicon import lexicon_overrides

# @lexicon_overrides.postlookup_filters_for_lexicon(('eng', 'crk'))
# def sort_by_rank(lex, nodelist, *args, **kwargs):
# 
#     _str_norm = 'string(normalize-space(%s))'
# 
#     def get_rank(n):
#         try:
#             rank = int( n.xpath(_str_norm % './/rank/@rank') )
#         except:
#             rank = False
#         if rank:
#             return rank
#         else:
#             return n.xpath(_str_norm % './/l/text()')
# 
#     return sorted(nodelist, key=get_rank)

@morphology.postgeneration_filter_for_iso('crk', 'crkMacr')
def force_hyphen(generated_forms, *input_args, **input_kwargs):
    """ For any +Cnj forms that are generated, filter out those
    without ê- """

    def matches_hyphen(f):
        return u'ê-' in f

    def form_fx((tag, forms)):
        if forms:
            _hyph = [f for f in forms if '-' in f]
            if len(_hyph) > 0:
                unhyphs = [h.replace('-', '') for h in _hyph]
                # throw out all forms that have a hyphenated equivalent
                _filt = lambda x: x not in unhyphs and '%' not in x
                fs = filter(_filt, forms)
                return (tag, fs)

        return (tag, forms)

    return map(form_fx, generated_forms)

@morphology.tag_filter_for_iso('crk', 'crkMacr')
def adjust_tags_for_gen(lemma, tags, node=None, **kwargs):
    """ **tag filter**: Lexicon -> FST changes.

    Change POS to be compatible with FST for when they are not.
    """

    if 'template_tag' not in kwargs:
        return lemma, tags, node

    from flask import current_app, g
    import re
    # get tagset for pre-lemma stuff

    morph = current_app.config.morphologies.get(g._from, False)

    tagsets = morph.tagsets.sets

    prelemmas = tagsets.get('prelemma_tags')
    # TODO: where is the lemma

    # print g._from
    # print lemma
    # print list(prelemmas.members)

    cleaned_tags = []
    for t in tags:
        # print t

        cleaned_tag = []

        for pl in prelemmas.members:
            before = []
            rest = []

            pl = unicode(pl)

            try:
                _pl = re.compile(pl)
            except Exception, e:
                _pl = False

            for part in t:
                if _pl:
                    if _pl.match(part) or pl == part:
                        before.append(part)
                        continue
                else:
                    if pl == part:
                        before.append(part)
                        continue
                rest.append(part)

        cleaned_tag.extend(before)
        cleaned_tag.append(lemma)
        cleaned_tag.extend(rest)

        # print cleaned_tag

        cleaned_tags.append(cleaned_tag)


    if len(cleaned_tags) == 0 and len(tags) > 0:
        tags = cleaned_tags

    # print cleaned_tags

    return lemma, cleaned_tags, node

