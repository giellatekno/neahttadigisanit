from morphology import Tag
from flask import current_app

__all__ = [
    'tagfilter',
    'tagfilter_conf',
]

def tagfilter_conf(filters, s):
    """ A helper function for filters to extract app.config from the
    function for import in other modules.

    Given a set of tag filters, this function replaces each piece of a
    tag and returns it for rendering.
    """

    if not s:
        return s

    filtered = []

    if isinstance(s, list):
        parts = s
    elif isinstance(s, Tag):
        parts = list(s)
    else:
        # TODO: use morphology splitter
        parts = s.split(' ')

    for part in parts:
        # try part, and if it doesn't work, then try part.lower()
        _f_part = filters.get( part
                             , filters.get( part.lower()
                                          , part
                                          )
                             )
        filtered.append(_f_part)

    return ' '.join([a for a in filtered if a.strip()])

def tagfilter(s, lang_iso, targ_lang, generation=False):
    if generation:
        filters = current_app.config.tag_filters.get((lang_iso, targ_lang, 'generation'), False)
    else:
        filters = current_app.config.tag_filters.get((lang_iso, targ_lang), False)

    # morph = current_app.config.morphologies.get(lang_iso, False)
    # if morph:
    #     splitter = morph.tool.splitAnalysis(s)
    # else:
    #     splitter = lambda x: x.split('+')

    if filters:
        return tagfilter_conf(filters, s)
    else:
        if isinstance(s, Tag):
            return s.sep.join(s)
        if isinstance(s, list):
            return ' '.join(s)
        return s
