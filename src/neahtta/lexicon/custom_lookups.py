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
        self.lemma = etree.XPath('.//e[lg/l/text() = $lemma]')

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

    def lookupLemma(self, lemma):
        return self.XPath( self.lemma
                         , lemma=lemma
                         )


