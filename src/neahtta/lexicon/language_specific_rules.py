"""

A set of lexicon-related language specific rules, provided by
`lexicon.LexiconOverrides`. There is probably a better location
for this documentation, but for now ...

Example source formatting function:

    @lexicon_overrides.entry_source_formatter('sme')
    def format_source_sme(ui_lang, entry_node):
        # do some processing on the entry node ...
        if successful:
            return some_formatted_string
        return None

Example target string formatting function:

    @lexicon_overrides.entry_target_formatter('sme')
    def format_target_sme(ui_lang, entry_node, tg_node):
        # do some processing on the entry and tg node ...
        if successful:
            return some_formatted_string
        return None

"""

from lexicon import lexicon_overrides

@lexicon_overrides.entry_source_formatter('sma')
def format_source_sma(ui_lang, e):
    from neahtta import tagfilter_conf
    from neahtta import app

    paren_args = []

    _str_norm = 'string(normalize-space(%s))'
    _lemma = e.xpath(_str_norm % 'lg/l/text()')
    _class = e.xpath(_str_norm % 'lg/l/@class')
    _pos = e.xpath(_str_norm % 'lg/l/@pos')

    if _pos:
        print _pos
        filters = app.config.tag_filters.get(('sma', 'nob'))
        print filters

        paren_args.append(tagfilter_conf(filters, _pos))
        print paren_args

    if _class:
        paren_args.append(_class.lower())

    if len(paren_args) > 0:
        return '%s (%s)' % (_lemma, ', '.join(paren_args))
    else:
        return _lemma

    return None

