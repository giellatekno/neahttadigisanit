import datetime


def get_time():
    return datetime.datetime.now().replace(microsecond=0).isoformat()


def get_ip(request):
    if request.environ.get("HTTP_X_FORWARDED_FOR") is None:
        return request.remote_addr or ''
    else:    
        return request.environ["HTTP_X_FORWARDED_FOR"]


def logIndexLookups(user_input, results, from_language, to_language):
    from logging import getLogger
    from flask import request

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
                l_right = ', '.join(
                    [_l.get('tx') for _l in lookup.get('right')])
                tx_set.add(l_right)
                result_lemmas.add(lookup.get('left'))

    result_lemmas = ', '.join(list(result_lemmas))
    meanings = '; '.join(list(tx_set))

    user_ip = ''

    if request:
        user_ip = get_ip(request)

    user_log = getLogger("user_log")
    user_log.info('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' %
                  (user_input, str(success), result_lemmas, meanings,
                   from_language, to_language, get_time(), user_ip))


def logSimpleLookups(user_input, results, from_language, to_language):
    from logging import getLogger
    from flask import request

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

    user_ip = ''
    if request:
        user_ip = get_ip(request)

    user_log = getLogger("user_log")
    user_log.info('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' %
                  (user_input, str(success), result_lemmas, meanings,
                   from_language, to_language, get_time(), user_ip))
