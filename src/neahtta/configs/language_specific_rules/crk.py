from morphology import generation_overrides as morphology
from lexicon import lexicon_overrides

from lexicon import search_types, CustomLookupType
from lexicon.lexicon import PARSED_TREES
from lxml import etree

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


# TODO: document how this custom class is constructed.
# @search_types.add_custom_lookup_type('substring_match')
class SubstringLookups(CustomLookupType):
    """
    NB: for the moment this is eng-crk specific.

    # TODO: document this
    # TODO: sort matches

    """

    def __init__(self, filename=False, tree=False):
        super(SubstringLookups, self).__init__(filename=filename, tree=tree)

        self.xpath_evaluator = etree.XPathDocumentEvaluator(self.tree)

        # Initialize XPath queries
        self.lemma = etree.XPath('.//e[contains(mg/tg/key/text(), $lemma)]')

    def lookupLemma(self, lemma):

        keys = ' and '.join([
            '(mg/tg/key/text() = "%s")' % l
            for l in lemma.split(',')
        ])

        key_expr = './/e[%s]' % keys

        xp = etree.XPath(key_expr)

        nodes = self.XPath( xp, lemma=lemma)
        return self.modifyNodes(nodes, lemma=lemma)

search_types.add_custom_lookup_type('substring_match')(SubstringLookups)

# NB: this search type has not been registered, just copying here so it
# will not get lost.
# 
# search_types.add_custom_lookup_type('keyword')(SubstringLookups)
class KeywordLookups(CustomLookupType):
    """
    NB: for the moment this is eng-crk specific.

    1. search by //e/mg/tg/t/text() instead of //e/lg/l/text()
    2. after the search, we duplicate and re-test the matched <e />
       nodes to remove any <mg /> that do not apply to the query.
    3. Duplicated nodes are returned to the rest of the query, and no
       one knows the difference

    TODO: how to provide an entry hash for these? Linkability to search
      results would be great.

    TODO: think about how to generalize this. Since this is code beyond
    a sort of 'base functionality', it may need to stand somewhere other
    than in `lexicon.lexicon`. Providing an easy API for extending
    search types would be great, because down the line there will be
    more search types.

    """

    def __init__(self, filename=False, tree=False):
        if not tree:
            if filename not in PARSED_TREES:
                print "parsing %s" % filename
                try:
                    self.tree = etree.parse(filename)
                    PARSED_TREES[filename] = self.tree
                except Exception, e:
                    print
                    print " *** ** ** ** ** ** * ***"
                    print " *** ERROR parsing %s" % filename
                    print " *** ** ** ** ** ** * ***"
                    print
                    print " Check the compilation process... "
                    print " Is the file empty?"
                    print " Saxon errors?"
                    print
                    sys.exit(2)
            else:
                self.tree = PARSED_TREES[filename]
        else:
            self.tree = tree

        self.xpath_evaluator = etree.XPathDocumentEvaluator(self.tree)

        # Initialize XPath queries
        self.lemma = etree.XPath('.//e[mg/tg/key/text() = $lemma]')

    def cleanEntry(self, e):
        ts = e.findall('mg/tg/t')
        ts_text = [t.text for t in ts]
        ts_pos = [t.get('pos') for t in ts]

        l = e.find('lg/l')
        right_text = [l.text]

        return {'left': ts_text, 'pos': ts_pos, 'right': right_text}

    def modifyNodes(self, nodes, lemma):
        """ Modify the nodes in some way, but by duplicating them first.

        Here we select the children of the <e /> and run a test on them,
        if they succeed, then don't pop the node. Then return the
        trimmed elements.

        This is probably the best option for compatibility with the rest
        of NDS, but need to have a way of generalizing this, because at
        the moment, this is lexicon-specific.
        """
        import copy

        def duplicate_node(node):
            # previously: etree.XML(etree.tostring(node))
            return copy.deepcopy(node) 

        def test_node(node):
            tg_node_expr = " and ".join([
                '(key/text() = "%s")' % l_part
                for l_part in lemma.split(',')
            ])
            _xp = 'tg[%s]' % tg_node_expr
            return len(node.xpath(_xp)) == 0

        def process_node(node):
            mgs = node.findall('mg')
            c = len(node.findall('mg'))
            # Remove nodes not passing the test, these shall diminish
            # and go into the west, and remain <mg />.
            for mg in mgs:
                if test_node(mg):
                    c -= 1
                    node.remove(mg)
            # If trimming <mg /> results in no actual translations, we
            # don't display the node.
            if c == 0:
                return None
            else:
                return node

        new_nodes = []
        for node in map(duplicate_node, nodes):
            new_nodes.append(process_node(node))

        return [n for n in new_nodes if n != None]

    def lookupLemma(self, lemma):

        keys = ' and '.join([
            '(mg/tg/key/text() = "%s")' % l
            for l in lemma.split(',')
        ])

        key_expr = './/e[%s]' % keys

        xp = etree.XPath(key_expr)

        nodes = self.XPath( xp, lemma=lemma)
        return self.modifyNodes(nodes, lemma=lemma)




@morphology.postgeneration_filter_for_iso('crk', 'crkMacr')
def force_hyphen(generated_forms, *input_args, **input_kwargs):
    """ For any +Cnj forms that are generated, filter out those
    without ê- """

    def matches_hyphen(f):
        return u'ê-' in f or u'ē-' in f

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

