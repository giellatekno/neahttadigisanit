#!/usr/bin/env python
"""
Some general utilities
"""

__all__ = [
    'encodeOrFail',
    'decodeOrFail',
    'zipNoTruncate',
    'fmtForCallback',
    'logSimpleLookups',
    'logIndexLookups',
]

def encodeOrFail(S):
    try:
        return S.encode('utf-8')
    except:
        return S

def decodeOrFail(S):
    try:
        return S.decode('utf-8')
    except:
        return S

def zipNoTruncate(a, b):
    def tup(*bbq):
        return tuple(bbq)
    return map(tup, a, b)

def fmtForCallback(serialized_json, callback):
    if not callback:
        return serialized_json
    else:
        return "%s(%s)" % (callback, serialized_json)

def logIndexLookups(user_input, results, from_language, to_language):
    from logging import getLogger

    # This is all just for logging
    success = False
    result_lemmas = set()
    tx_set = set()

    for result in results:
        result_lookups = result.get('lookups')
        if result_lookups:
            success = True
            for lookup in result_lookups:
                l_left = lookup.get('left')
                l_right = ', '.join([_l.get('tx') for _l in lookup.get('right')])
                tx_set.add(l_right)
                result_lemmas.add(lookup.get('left'))

    result_lemmas = ', '.join(list(result_lemmas))
    meanings = '; '.join(list(tx_set))

    user_log = getLogger("user_log")
    user_log.info('%s\t%s\t%s\t%s\t%s\t%s' % (user_input,
                                            str(success),
                                            result_lemmas,
                                            meanings,
                                            from_language,
                                            to_language
                                            ))

def logSimpleLookups(user_input, results, from_language, to_language):
    from logging import getLogger

    # This is all just for logging
    success = False
    result_lemmas = set()
    tx_set = set()

    for result in results:
        result_lookups = result.get('lookups')
        if result_lookups:
            success = True
            for lookup in result_lookups:
                l_left = lookup.get('left')
                l_right = ', '.join(lookup.get('right'))
                tx_set.add(l_right)
                result_lemmas.add(lookup.get('left'))

    result_lemmas = ', '.join(list(result_lemmas))
    meanings = '; '.join(list(tx_set))

    user_log = getLogger("user_log")
    user_log.info('%s\t%s\t%s\t%s\t%s\t%s' % (user_input,
                                            str(success),
                                            result_lemmas,
                                            meanings,
                                            from_language,
                                            to_language
                                            ))

