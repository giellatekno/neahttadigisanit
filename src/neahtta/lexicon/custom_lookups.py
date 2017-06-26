from .lexicon import XMLDict
from lxml import etree

class CustomLookupType(XMLDict):
    """ This is the custom lookup type class from which all custom
    lookup types should be subclassed.
    """

    def __init__(self, *args, **kwargs):
        """ Initialize the trees in the parent class and then provide
        some overrides. """

        super(CustomLookupType, self).__init__(*args, **kwargs)

        self.xpath_evaluator = etree.XPathDocumentEvaluator(self.tree)
        # Initialize XPath queries
        self.lemma = etree.XPath('.//e[mg/tg/key/text() = $lemma]')

    def cleanEntry(self, e):
        """ This function provides some basic parsing of each `<e />`
        node, returning a dictionary:

            Ex.) {'left': 'kissa', 'pos': 'N', 'right': 'cat'}

        """
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


