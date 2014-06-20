## from lexicon import lexicon_overrides as lexicon
## 
## @lexicon.entry_target_formatter(('crk', 'eng'))
## def format_target_sme(ui_lang, e, tg):
##     """**Entry target translation formatter**
## 
##     Display @src (source) attribute in translations
## 
##     """
##     _str_norm = 'string(normalize-space(%s))'
## 
##     _src = e.xpath(_str_norm % '@src')
## 
##     _t_lemma = tg.xpath(_str_norm % 't/text()')
## 
##     if _src:
##         return "(%s) %s" % (src, _reg)
## 
##     return None
## 
