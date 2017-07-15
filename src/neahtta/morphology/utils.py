from morphology import Tag
from flask import current_app

__all__ = [
    'tagfilter',
    'tagfilter_conf',
]

def tagfilter_conf(filters, s, *args, **kwargs):
    """ A helper function for filters to extract app.config from the
    function for import in other modules.

    Given a set of tag filters, this function replaces each piece of a
    tag and returns it for rendering.

    This also handles replacements of multiple tags.

    Following tests check whether or not various tag substitutions work.

        >>> filt = {'Sg+Px1Sg': 'Possessive: 1s'}
        >>> tagsep = '+'
        >>> tagfilter_conf(filt, "N+AN+Sg+Px1Sg", tagsep='+')
        'N+AN+Possessive: 1s'

        >>> filt = {'Sg+Px1Sg': 'Possessive: 1s', 'N': 'Noun', 'AN': 'Animate'}
        >>> tagfilter_conf(filt, "N+AN+Sg+Px1Sg", tagsep='+').replace('+', ' ')
        'Noun Animate Possessive: 1s'

        >>> filt = {'N+AN+Sg+Px1Sg': 'Animate Noun Possessive: 1s', 'N': 'Noun', 'AN': 'Animate'}
        >>> tagfilter_conf(filt, "N+AN+Sg+Px1Sg", tagsep='+').replace('+', ' ')
        'Animate Noun Possessive: 1s'

    """

    tagsep = kwargs.get('tagsep')

    if not s:
        return s

    filtered = []

    # Unfortunate type conversions
    if isinstance(s, list):
        parts = s
    elif isinstance(s, Tag):
        string = s.tag_string
        parts = list(s)
        s = string
    else:
        if tagsep:
            parts = s.split(tagsep)
        else:
            parts = s.split(' ')
            tagsep = ' '

    # Find out if the tagset has any tags that count for
    # multi-replacement
    multi_replacements = []
    for k, v in filters.iteritems():
        if '+' in k:
            multi_replacements.append((k, v))

    # Sort the replacements from longest set of tags to shortest
    multi_replacements = sorted(
        multi_replacements,
        key=lambda (x, y): x.count('+'),
        reverse=True)

    # return matches and their indexes in the original list
    def subfinder(mylist, pattern):
        matches = []
        for i in range(len(mylist)):
            # if this element is a match, and a sublist matching the
            # length is a match ... 
            if mylist[i] == pattern[0] and mylist[i:i+len(pattern)] == pattern:
                matches.append((pattern, (i, i+len(pattern))))
        return matches

    longest_matches = []

    # then with the substring replacements, maybe just make replacement
    # first, and then run the rest of the parts through as normal

    for mr, tg in multi_replacements:
        _mr = mr.split('+')
        matches = subfinder(parts, _mr)
        if matches:
            for m in matches:
                longest_matches.append((m, tg))

    if len(longest_matches) > 0:
        longest_matches = sorted(longest_matches, key=lambda (x, _): len(x),
                                 reverse=True)
        longest_match = longest_matches[0]
    else:
        longest_match = False

    completely_replaced = False

    if longest_match:

        ((source, indexes), replacement) = longest_match
        (a, b) = indexes

        if len(longest_match) == len(parts):
            filtered = [replacement]
            completely_replaced = True
        else:
            # iterate list to make replacement on sublist:
            # replace once, and then continue.

            subreplacement = False
            replc = []
            for i in range(len(parts)):
                item = parts[i]
                if (a <= i <= b) and not subreplacement:
                    replc.append(replacement)
                    subreplacement = True
                if (a <= i <= b) and subreplacement:
                    continue
                else:
                    replc.append(item)
            parts = replc

    if not completely_replaced:
        for part in parts:
            # try part, and if it doesn't work, then try part.lower()
            _f_part = filters.get( part
                                 , filters.get( part.lower()
                                              , part
                                              )
                                 )
            filtered.append(_f_part)

    return tagsep.join([a for a in filtered if a.strip()])

def tagfilter(s, lang_iso, targ_lang, generation=False, tagset=False, tagsep=' '):
    if tagset:
        filters = current_app.config.tag_filters.get((lang_iso, targ_lang, tagset), False)
    elif generation:
        filters = current_app.config.tag_filters.get((lang_iso, targ_lang, 'generation'), False)
    else:
        filters = current_app.config.tag_filters.get((lang_iso, targ_lang), False)

    if filters:
        return tagfilter_conf(filters, s, tagsep=tagsep)
    else:
        if isinstance(s, Tag):
            return s.sep.join(s)
        if isinstance(s, list):
            return ' '.join(s)
        return s
