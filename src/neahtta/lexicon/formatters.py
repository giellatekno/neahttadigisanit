from lexicon import lexicon_overrides
from morphology.utils import tagfilter
from utils.data import flatten
from flask import current_app

from .lexicon import hash_node


class FormattingError(Exception):
    pass


class EntryNodeIterator(object):
    """ A class for iterating through the result of an LXML XPath query,
    while cleaning the nodes into a more usable format.

    .clean() is where most of the magic happens, so if new formats are
    needed, just override this.

    """

    def l_node(self, entry):
        l = entry.find('lg/l')
        try:
            lemma = l.text
        except:
            lemma = ''
        pos = l.get('pos')
        context = l.get('context')
        type = l.get('type')
        hid = l.get('hid')
        if context == None:
            context = False
        if type == None:
            type = False
        if hid == None:
            hid = False

        return lemma, pos, context, type, hid

    def tg_nodes(self, entry):
        """ Select <tg /> nodes. If an entry has <tg /> nodes marked
        with xml:lang attributes, then return only the entries matching
        the target_lang, otherwise, if there are no xml:lang attributes
        on any of the <tg /> nodes, then return all entries unfiltered.
        """
        # how to detect multi-format? problem is that behavior between
        # pair format may be disrupted by disallowing fallback?
        target_lang = self.query_kwargs.get('target_lang', False)

        if not target_lang:
            multi = False
        else:
            multi = len(entry.xpath("mg/tg/@xml:lang")) > 0 and True or False

        if multi:
            ts = entry.xpath("mg/tg[@xml:lang='%s']/t" % target_lang)
            tgs = entry.xpath("mg/tg[@xml:lang='%s']" % target_lang)
        else:
            ts = entry.findall('mg/tg/t')
            tgs = entry.findall('mg/tg')

        return tgs, ts

    def examples(self, tg):
        _ex = []

        possible_errors = False
        for xg in tg.findall('xg'):
            _x = xg.find('x')
            _xt = xg.find('xt')

            if _x is not None and hasattr(_x, 'text'):
                _x_tx = _x.text
            else:
                _x_tx = ''
                possible_errors = True

            if _xt is not None and hasattr(_xt, 'text'):
                _xt_tx = _xt.text
            else:
                _xt_tx = ''
                possible_errors = True

            _ex.append((_x_tx, _xt_tx))

        if possible_errors:
            from lxml import etree
            error_xml = etree.tostring(tg, pretty_print=True, encoding="utf-8")
            current_app.logger.error(
                "Potential XML formatting problem on <xg /> node\n\n%s" %
                error_xml.strip())

        if len(_ex) == 0:
            return False
        else:
            return _ex

    def find_translation_text(self, tg):
        """ This parses a <tg /> node and returns text, annotations, xml:lang.

        Annotations means here: tg/re, tg/te, or tg/tf. If there is no
        <t /> node, we try to fall back to using one of these,
        otherwise, pick the <t /> node and use the annotations as
        definition.
        """

        tCtn = tg.find('tCtn')

        if tCtn is not None:
            return self.find_translation_text(tCtn)

        def orFalse(l):
            if len(l) > 0:
                return l[0]
            else:
                return False

        text = False
        re = tg.find('re')
        te = tg.find('te')
        tf = tg.find('tf')

        te_text = ''
        re_text = ''
        tf_text = ''

        if te is not None: te_text = te.text
        if re is not None: re_text = re.text
        if tf is not None: tf_text = tf.text

        tx = tg.findall('t')

        link = True

        if not tx:
            if te_text:
                text, te_text = [te_text], ''
            elif re_text:
                text, re_text = [re_text], ''
            elif tf_text:
                text, tf_text = [tf_text], ''
        else:
            text = [_tx.text for _tx in tx if _tx.text is not None]

        for item in tx:
            if item.text is None:
                item.text = 'word_not _yet_translated'

        lang = tg.xpath('@xml:lang')

        annotations = []
        for a in [te_text, re_text, tf_text]:
            if a is not None:
                if a.strip():
                    annotations.append(a)

        return text, annotations, lang

    def __init__(self, nodes, *query_args, **query_kwargs):
        if not nodes or len(nodes) == 0:
            self.nodes = []
        else:
            self.nodes = [a for a in nodes if a is not None]
        self.query_args = query_args
        self.query_kwargs = query_kwargs
        self.additional_template_kwargs = {}

        if 'additional_template_kwargs' in query_kwargs:
            self.additional_template_kwargs = query_kwargs.get(
                'additional_template_kwargs')
            query_kwargs.pop('additional_template_kwargs')

    def __iter__(self):
        from lxml import etree
        for node in self.nodes:
            try:
                yield self.clean(node)
            except Exception, e:
                import traceback
                import sys
                exc_type, exc_value, exc_traceback = sys.exc_info()
                tb_str = traceback.format_exception(exc_type, exc_value,
                                                    exc_traceback)
                if node is not None:
                    error_xml = etree.tostring(
                        node, pretty_print=True, encoding="utf-8")
                else:
                    error_xml = 'No entry for lookup'
                msg_args = (error_xml.strip(), ''.join(tb_str),
                            repr(self.query_args), repr(self.query_kwargs))
                current_app.logger.error(
                    "Potential XML formatting problem somewhere in... \n\n%s\n\n%s\n\n%s\n\n%s"
                    % msg_args)
                continue


class SimpleJSON(EntryNodeIterator):
    """ A simple JSON-ready format for /lookups/
    """

    def sorted_by_pos(self):
        _from = self.query_kwargs.get('source_lang')
        _to = self.query_kwargs.get('target_lang')

        def filterPOS(r):
            def fixTag(t):
                t_pos = t.get('pos', False)
                if not t_pos:
                    return t
                t['pos'] = tagfilter(t_pos, _from, _to)
                return t

            return fixTag(r)

        return map(filterPOS, list(self))

    def clean(self, e):
        lemma, lemma_pos, lemma_context, _, lemma_hid = self.l_node(e)
        tgs, ts = self.tg_nodes(e)

        # TODO: format source in JSON view
        target_formatteds = []
        right_langs = []
        translations = []
        for tg in tgs:
            default_text, default_annotations, default_lang = self.find_translation_text(
                tg)
            tf_text = lexicon_overrides.format_target(
                self.query_kwargs.get('source_lang'),
                self.query_kwargs.get('target_lang'),
                self.query_kwargs.get('ui_lang'), e, tg, False)
            if tf_text:
                default_lang.append(default_lang)
                target_formatteds.append(tf_text)
            else:
                translations.append((default_text, default_annotations,
                                     default_lang))

        if len(target_formatteds) > 0:
            right_text = target_formatteds
        else:
            right_text = flatten([a for a, b, c in translations])
            right_langs = flatten([c for a, b, c in translations])

        return {
            'left': lemma,
            'context': lemma_context,
            'pos': lemma_pos,
            'right': right_text,
            'lang': right_langs,
            'hid': lemma_hid,
            'input': self.query_kwargs.get('user_input', '')
        }


class FrontPageFormat(EntryNodeIterator):
    def clean_tg_node(self, e, tg):
        from functools import partial

        ui_lang = self.query_kwargs.get('ui_lang')

        # TODO: detect if there are texts vs. annotations only,
        # still need to run those through

        texts, annotations, lang = self.find_translation_text(tg)

        link = True

        if texts:
            if not isinstance(texts, list):
                texts = [texts]
        elif annotations:
            if not isinstance(annotations, list):
                annotations = [annotations]
        else:
            from lxml import etree
            error_xml = etree.tostring(e, pretty_print=True, encoding="utf-8")
            current_app.logger.error(
                "Potential XML formatting problem while processing <tg /> nodes.\n\n" + \
                repr(self.query_kwargs) + "\n\n" + \
                repr(self.query_args) + "\n\n" + \
                error_xml.strip()
            )

            texts = []

        # e node, tg node, default text for when formatter doesn't
        # exist for current iso

        # Apply to each translation text separately
        target_formatter = partial(lexicon_overrides.format_target,
                                   self.query_kwargs.get('source_lang'),
                                   self.query_kwargs.get('target_lang'),
                                   ui_lang, e, tg)

        def add_link(_p):

            if '<a ' in _p or '</a>' in _p:
                return _p

            src_lang = self.query_kwargs.get('source_lang')

            _from_l = self.query_kwargs.get('target_lang')
            _to_l = src_lang

            # Does the reversed pair exist as a variant? If so we need
            # to get the original pair and re-reverse it
            if (_to_l, _from_l) in current_app.config.variant_dictionaries:
                _var = current_app.config.variant_dictionaries.get((_to_l,
                                                                    _from_l))
                (_to_l, _from_l) = _var.get('orig_pair')

            if (_from_l, _to_l) not in current_app.config.dictionaries and \
               (_from_l, _to_l)     in current_app.config.variant_dictionaries:
                var = current_app.config.variant_dictionaries.get((_from_l,
                                                                   _to_l))
                (_from_l, _to_l) = var.get('orig_pair')

            pair = (_from_l, _to_l)

            if pair not in current_app.config.dictionaries:
                return _p

            _url = [
                'detail',
                self.query_kwargs.get('target_lang'), src_lang,
                '%s.html?no_compounds=true&lemma_match=true' % _p
            ]
            _url = '/' + '/'.join(_url)
            link = "<a href='%s'>%s</a>" % (_url, _p)
            return link

        # problem: no <t /> nodes available here for til_/fra_ref words

        target_formatted = []
        if len(texts) > 0:
            # TODO: does this not actually pass texts ?
            target_formatted = map(target_formatter, texts)
        elif len(annotations) > 0:
            # target_formatter expects some default text to be passed in
            # the event that no formatting is able to be made
            target_formatted = map(target_formatter, annotations)

        # If there were changes, then we want to give absolute control
        # on this string to the formatter.
        target_reformatted = []
        if set(target_formatted) != set(texts):
            target_reformatted = True

        target_formatted_unlinked = target_formatted
        target_formatted = map(add_link, target_formatted)

        right_node = {
            'tx': ', '.join(texts),
            're': annotations,
            'target_reformatted': target_reformatted,
            'target_formatted_unlinked': target_formatted_unlinked,
            'examples': self.examples(tg),
            'target_formatted': ', '.join(target_formatted)
        }

        return right_node, lang

    def clean(self, e):
        lemma, lemma_pos, lemma_context, lemma_type, lemma_hid = self.l_node(e)
        tgs, ts = self.tg_nodes(e)

        ui_lang = self.query_kwargs.get('ui_lang')

        _right = map(lambda tg: self.clean_tg_node(e, tg), tgs)

        right_langs = [lang for _, lang in _right]
        right_nodes = [fmt_node for fmt_node, _ in _right]

        # # Make our own hash, 'cause lxml won't
        # entry_hash = [ unicode(lemma)
        #              , unicode(lemma_context)
        #              , unicode(lemma_pos)
        #              , ','.join(sorted([t['tx'] for t in right_nodes]))
        #              ]
        # entry_hash = str('-'.join(entry_hash).__hash__())

        entry_hash = hash_node(e)

        # node, and default format for if a formatter doesn't exist for
        # iso

        source_lang = self.query_kwargs.get('source_lang')
        target_lang = self.query_kwargs.get('target_lang')
        lemma_attrs = self.query_kwargs.get('lemma_attrs', False)

        if lemma and lemma_pos:
            default_format = "%s (%s)" % (
                lemma, tagfilter(lemma_pos, source_lang, target_lang))
        elif lemma and not lemma_pos:
            default_format = lemma
        elif lemma_attrs:
            default_format = ''

        def add_link(_p):
            """ If there's a link already, then don't add one,
            otherwise...
            """

            if '<a ' in _p or '</a>' in _p:
                return _p

            # TODO: will need a more lasting solution...
            src_lang = self.query_kwargs.get('source_lang')
            if src_lang == 'SoMe':
                src_lang = 'sme'

            _url = [
                'detail', src_lang,
                self.query_kwargs.get('target_lang'),
                '%s.html?e_node=%s' % (lemma, entry_hash)
            ]
            _url = '/' + '/'.join(_url)
            link = "<a href='%s'>%s</a>" % (_url, _p)
            return link

        source_formatted_unlinked = lexicon_overrides.format_source(
            source_lang, ui_lang, e, target_lang, default_format)

        source_formatted = add_link(source_formatted_unlinked)

        formatted_dict = {
            'left': lemma,
            'source_formatted': source_formatted,
            'source_unlinked': source_formatted_unlinked,
            'context': lemma_context,
            'pos': lemma_pos,
            'right': right_nodes,
            'lang': right_langs,
            'hid': lemma_hid,
            'entry_hash': entry_hash
        }

        formatted_dict.update(self.additional_template_kwargs)
        return formatted_dict


# TODO: adding hverandre functionality requires some additional
# attributes to be available, but this formatter class is annoying,
# and a good argument for how this should all just be handled by xslt or
# some template thing instead.


class DetailedFormat(FrontPageFormat):
    def clean(self, e):
        lemma, lemma_pos, lemma_context, lemma_type, lemma_hid = self.l_node(e)
        tgs, ts = self.tg_nodes(e)

        ui_lang = self.query_kwargs.get('ui_lang')

        _right = map(lambda tg: self.clean_tg_node(e, tg), tgs)

        right_langs = [lang for _, lang in _right]
        right_nodes = [fmt_node for fmt_node, _ in _right]

        entry_hash = hash_node(e)

        # node, and default format for if a formatter doesn't exist for
        # iso

        source_lang = self.query_kwargs.get('source_lang')
        target_lang = self.query_kwargs.get('target_lang')
        lemma_attrs = self.query_kwargs.get('lemma_attrs', False)

        if lemma and lemma_pos:
            default_format = "%s (%s)" % (
                lemma, tagfilter(lemma_pos, source_lang, target_lang))
        elif lemma and not lemma_pos:
            default_format = lemma
        elif lemma_attrs:
            default_format = ''

        def add_link(_p):
            """ If there's a link already, then don't add one,
            otherwise...
            """
            return _p

        source_formatted_unlinked = lexicon_overrides.format_source(
            source_lang, ui_lang, e, target_lang, default_format)

        source_formatted = add_link(source_formatted_unlinked)

        formatted_dict = {
            'left': lemma,
            'source_formatted': source_formatted,
            'source_unlinked': source_formatted_unlinked,
            'context': lemma_context,
            'pos': lemma_pos,
            'right': right_nodes,
            'lang': right_langs,
            'hid': lemma_hid,
            'entry_hash': entry_hash,
            'input': (lemma, lemma_pos, '', lemma_type),
            'node': e
        }

        formatted_dict.update(self.additional_template_kwargs)
        return formatted_dict
