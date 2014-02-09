from flask import request

def to_xml_string(n):
    """ Return a string from an lxml node within an entry result.
    """
    from lxml import etree
    if 'entries' in n:
        if 'node' in n.get('entries'):
            node = n['entries']['node']
            _str = etree.tostring(node, pretty_print=True, encoding="utf-8")
            return _str.decode('utf-8')
    return ''

def resolve_original_pair(config, _from, _to):
    """ For a language pair alternate, return the original language pair
    that is the parent to the alternate.

    TODO: this was more or less copied from the index views, but now
    those other views should use this instead.
    TODO: write tests.
    """

    # mobile test for most common browsers
    mobile = False
    if request.user_agent.platform in ['iphone', 'android']:
        mobile = True

    iphone = False
    if request.user_agent.platform == 'iphone':
        iphone = True

    # Variables to control presentation based on variants present
    current_pair = config.pair_definitions.get((_from, _to), {})
    reverse_pair = config.pair_definitions.get((_to, _from), {})

    swap_from, swap_to = (_to, _from)

    current_pair_variants = current_pair.get('input_variants', False)
    has_variant = bool(current_pair_variants)
    has_mobile_variant = False

    if has_variant:
        _mobile_variants = filter( lambda x: x.get('type', '') == 'mobile'
                                 , current_pair_variants
                                 )
        if len(_mobile_variants) > 0:
            has_mobile_variant = _mobile_variants[0]


    variant_dictionaries = config.variant_dictionaries
    is_variant, orig_pair = False, ()

    if variant_dictionaries:
        variant    = variant_dictionaries.get((_from, _to), False)
        is_variant = bool(variant)
        if is_variant:
            orig_pair = variant.get('orig_pair')

    # Now we check if the reverse has variants for swapping
    # If there is a reverse pair with variants, get the mobile one as a
    # preference for swapping if the user is a mobile user, otherwise
    # just the default.

    reverse_has_variant = False
    if is_variant:
        _reverse_is_variant = config.variant_dictionaries.get( orig_pair
                                                                         , False
                                                                         )
        pair_settings = config.pair_definitions[orig_pair]
    else:
        _reverse_is_variant = config.variant_dictionaries.get( (_to, _from)
                                                                         , False
                                                                         )
        pair_settings = config.pair_definitions[(_from, _to)]

    _reverse_variants = reverse_pair.get('input_variants', False)

    if _reverse_variants:
        _mobile_variants = filter( lambda x: x.get('type', '') == 'mobile'
                                 , _reverse_variants
                                 )
        _standard_variants = filter( lambda x: x.get('type', '') == 'standard'
                                   , _reverse_variants
                                   )
        if mobile and len(_mobile_variants) > 0:
            _preferred_swap = _mobile_variants[0]
            _short_name = _preferred_swap.get('short_name')
            swap_from = _short_name
    else:
        if is_variant:
            swap_to, swap_from = orig_pair

    pair_opts = {
        'has_mobile_variant': has_mobile_variant,
        'has_variant': has_variant,
        'is_variant': is_variant,
        'orig_pair': orig_pair,
        'swap_to': swap_to,
        'swap_from': swap_from
    }
    return pair_settings, pair_opts

