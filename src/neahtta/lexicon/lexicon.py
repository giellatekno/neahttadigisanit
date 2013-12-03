from lxml import etree

##
##  Lexicon
##
##

class LexiconOverrides(object):
    """ Class for collecting functions marked with decorators that
    provide special handling of tags. One class instantiated in
    morphology module: `generation_overrides`.

    Current practice is to store these in language-specific modules within
    :py:module:`configs.language_specific_rules`...
    """

    ##
    ### Here are the functions that apply all the rules
    ##

    def format_source(self, lang_iso, ui_lang, e, target_lang, default_str):
        """ Find the function decorated by
                @overrides.entry_source_formatter(iso)
            and run the function on an XML node.
        """
        if lang_iso in self.source_formatters:
            return self.source_formatters.get(lang_iso)(ui_lang, e, target_lang) \
                or default_str
        return default_str

    def format_target(self, src_iso, targ_iso, ui_lang, e, tg, default_str):
        """ Find the function decorated by
                @overrides.entry_source_formatter(iso)
            and run the function on an XML node.
        """
        if (src_iso, targ_iso) in self.target_formatters:
            return self.target_formatters.get((src_iso, targ_iso))(ui_lang, e, tg) \
                or default_str
        return default_str

    def process_prelookups(self, lexicon_language_pairs, function):
        """ This runs the generator function, and applies all of the
        function contexts to the output. Or in other words, this
        decorator works on the output of the decorated function, but
        also captures the input arguments, making them available to each
        function in the registry.
        """
        def decorate(*args, **kwargs):
            lang_pair = lexicon_language_pairs.get(args)
            _from = args[0]
            newargs = args
            newkwargs = kwargs
            for f in self.prelookup_processors[_from]:
                newargs, newkwargs = f(*newargs, **newkwargs)
            return function(*newargs, **newkwargs)
        return decorate

    def process_postlookups(self, lexicon_language_pairs, function):
        """ Lexicon lookups are passed through all of these functions
        """
        def decorate(*lang_pair_args, **kwargs):
            lang_pair = lexicon_language_pairs.get(lang_pair_args)
            result_nodes = function(*lang_pair_args, **kwargs)
            for f in self.postlookup_filters[lang_pair_args]:
                result_nodes = f(lang_pair, result_nodes, kwargs)
            return result_nodes
        return decorate

    ##
    ### Here are the decorators
    ##

    def entry_source_formatter(self, *language_isos):
        """ Register a function for a language ISO.

        Functions decorated by this registry decorator should take one
        argument, an entry node, and return either a string or None. If
        None is returned, then a default value will be returned instead.

        The default value is passed to the function format_source, which
        selects the registered function and executes it.

        """
        def wrapper(formatter_function):
            for language_iso in language_isos:
                if language_iso in self.source_formatters:
                    print ' * OBS! Source formatter already registered for %s.' % \
                        language_iso
                    print '   ignoring redefinition on <%s>.' % \
                        restrictor_function.__name__
                else:
                    self.source_formatters[language_iso] = formatter_function
                    print '%s formatter: entry formatter for source - %s' %\
                          ( language_iso
                          , formatter_function.__name__
                          )
        return wrapper

    def entry_target_formatter(self, *iso_pairs):
        """ Register a function for a language ISO
        """
        def wrapper(formatter_function):
            for (src_iso, targ_iso) in iso_pairs:
                if (src_iso, targ_iso) in self.target_formatters:
                    print ' * OBS! Target formatter already registered for %s.' % \
                        repr((src_iso, targ_iso))
                    print '   ignoring redefinition on <%s>.' % \
                        formatter_function.__name__
                else:
                    self.target_formatters[(src_iso, targ_iso)] = formatter_function
                    print '%s formatter: entry formatter for target - %s' %\
                          ( '%s - %s' % (src_iso, targ_iso)
                          , formatter_function.__name__
                          )
        return wrapper

    def pre_lookup_tag_rewrite_for_iso(self, *language_isos):
        """ Register a function for a language ISO to adjust tags used in
        FSTs for use in lexicon lookups.

        >>> @lexicon_overrides.pre_lookup_tag_rewrite_for_iso('sme')
        >>> def someFunction(*args, **kwargs):
        >>>     ... some processing on tags, may be conditional, etc.
        >>>     return args, kwargs

        A typical example usage would be:

        >>> @lexicon.pre_lookup_tag_rewrite_for_iso('sme')
        >>> def pos_to_fst(*args, **kwargs):
        >>>     if 'lemma' in kwargs and 'pos' in kwargs:
        >>>         _k = kwargs['pos'].replace('.', '').replace('+', '')
        >>>         new_pos = LEX_TO_FST.get(_k, False)
        >>>         if new_pos:
        >>>             kwargs['pos'] = new_pos
        >>>     return args, kwargs

        Thus replacing the FST output containing 'egen' as a POS to
        'Prop' so that it may be found in a lexical entry containing
        a 'Prop' attribute.
        """
        def wrapper(restrictor_function):
            for language_iso in language_isos:
                self.prelookup_processors[language_iso]\
                    .append(restrictor_function)
                print '%s overrides: lexicon pre-lookup arg rewriter - %s' %\
                      ( language_iso
                      , restrictor_function.__name__
                      )
        return wrapper

    def postlookup_filters_for_lexicon(self, *lexica):
        """ Register a function for a language ISO to adjust tags used
        in FSTs for use in lexicon lookups. The decorator function takes
        a tuple for every function that the decorator should be applied
        to

        >>> @lexicon_overrides.lookup_filters_for_lexicon(('sme', 'nob'))
        >>> def someFunction(nodelist):
        >>>     ... some processing on tags, may be conditional, etc.
        >>>     return nodelist

        """
        def wrapper(restrictor_function):
            for lexicon in lexica:
                self.postlookup_filters[lexicon]\
                    .append(restrictor_function)
                print '%s overrides: lexicon lookup filter - %s' %\
                      ( lexicon
                      , restrictor_function.__name__
                      )
        return wrapper

    def __init__(self):
        from collections import defaultdict

        self.prelookup_processors = defaultdict(list)
        self.target_formatters = defaultdict(bool)
        self.source_formatters = defaultdict(bool)
        self.postlookup_filters = defaultdict(list)

lexicon_overrides = LexiconOverrides()


PARSED_TREES = {}

regexpNS = "http://exslt.org/regular-expressions"

class XMLDict(object):
    """ XML dictionary class. Initiate with a file path or an already parsed
    tree, exposes methods for searching in XML.

    Entries should be formatted by creating an EntryNodeIterator object,
    which will clean them on iteration.

    """
    def __init__(self, filename=False, tree=False):
        if not tree:
            if filename not in PARSED_TREES:
                print "parsing %s" % filename
                self.tree = etree.parse(filename)
                PARSED_TREES[filename] = self.tree
            else:
                self.tree = PARSED_TREES[filename]
        else:
            self.tree = tree
        self.xpath_evaluator = etree.XPathDocumentEvaluator(self.tree)

        # Initialize XPath queries

        self.lemmaStartsWith = etree.XPath(
            './/e[starts-with(lg/l/text(), $lemma)]'
        )

        self.lemma = etree.XPath('.//e[lg/l/text() = $lemma]')

        self.lemmaPOS = etree.XPath(
            './/e[lg/l/text() = $lemma and re:match(lg/l/@pos, $pos, "i")]',
            namespaces={'re': regexpNS})

        self.lemmaPOSAndType = etree.XPath(
            ' and '.join([ './/e[lg/l/text() = $lemma'
                         , 're:match(lg/l/@pos, $pos, "i")'
                         , 'lg/l/@type = $_type]'
                         ])
            , namespaces={'re': regexpNS}
        )

    def XPath(self, xpathobj, *args, **kwargs):
        return xpathobj(self.tree, *args, **kwargs)

    def lookupLemmaStartsWith(self, lemma):
        return self.XPath( self.lemmaStartsWith
                         , lemma=lemma
                         )

    def lookupLemma(self, lemma):
        return self.XPath( self.lemma
                         , lemma=lemma
                         )

    def lookupLemmaPOS(self, lemma, pos):
        # Can't insert variables in EXSLT expressions within a compiled
        # xpath statement, so doing this.
        pos = "^%s$" % pos
        return self.XPath( self.lemmaPOS
                         , lemma=lemma
                         , pos=pos
                         )

    def lookupLemmaPOSAndType(self, lemma, pos, _type):
        pos = "^%s$" % pos
        return self.XPath( self.lemmaPOSAndType
                         , lemma=lemma
                         , pos=pos
                         , _type=_type
                         )

    def lookupOtherLemmaAttr(self, **attrs):
        attr_conditions = []
        for k, v in attrs.iteritems():
            attr_conditions.append("lg/l/@%s = '%s'" % (k, v))
        attr_conditions = ' and '.join(attr_conditions)

        # .//e[lg/l/@til_ref = 'omtopersoner' and lg/l/@til_ref = 'omtopersoner']
        _xpath_expr = ".//e[%s]" % attr_conditions
        _xp = etree.XPath(_xpath_expr , namespaces={'re': regexpNS})
        return _xp(self.tree)

class AutocompleteTrie(XMLDict):

    @property
    def allLemmas(self):
        """ Returns iterator for all lemmas.
        """
        # TODO: ignore til_ref things
        return (e.text for e in self.tree.findall('e/lg/l') if e.text)

    def autocomplete(self, query):
        if self.trie:
            if hasattr(self.trie, 'autocomplete'):
                return sorted(list(self.trie.autocomplete(query)))
        return []

    def __init__(self, *args, **kwargs):
        super(AutocompleteTrie, self).__init__(*args, **kwargs)

        from trie import Trie

        print "* Preparing autocomplete trie..."
        filename = kwargs.get('filename')

        parsed_key = 'auto-' + filename
        if parsed_key not in PARSED_TREES:
            self.trie = Trie()
            try:
                self.trie.update(self.allLemmas)
            except:
                print "Trie processing error"
                print list(self.allLemmas)
                self.trie = False
            PARSED_TREES[parsed_key] = self.trie

        else:
            self.trie = PARSED_TREES[filename]


class ReverseLookups(XMLDict):
    """

    1. use only entries that have the attribute usage="vd" at entry
    level

    2. don't use entries with reverse="no" at entry level

    3. search by e/mg/tg/t/text() instead of /e/lg/l/text()

    """

    def cleanEntry(self, e):
        ts = e.findall('mg/tg/t')
        ts_text = [t.text for t in ts]
        ts_pos = [t.get('pos') for t in ts]

        l = e.find('lg/l')
        right_text = [l.text]

        return {'left': ts_text, 'pos': ts_pos, 'right': right_text}

    def lookupLemmaStartsWith(self, lemma):
        _xpath = './/e[mg/tg/t/starts-with(text(), "%s")]' % lemma
        return self.XPath(_xpath)

    def lookupLemma(self, lemma):
        _xpath = [ './/e[mg/tg/t/text() = "%s"' % lemma
                 , 'not(@reverse)]'
                 ]
        _xpath = ' and '.join(_xpath)
        return self.XPath(_xpath)

    def lookupLemmaPOS(self, lemma, pos):
        _xpath = ' and '.join(
            [ './/e[mg/tg/t/text() = "%s"' % lemma
            , 'not(@reverse)'
            , 'mg/tg/t/@pos = "%s"]' % pos.lower()
            ]
        )
        return self.XPath(_xpath)


class Lexicon(object):

    def __init__(self, settings):

        language_pairs = dict(
            [ (k, XMLDict(filename=v))
              for k, v in settings.dictionaries.iteritems() ]
        )

        self.lookup = lexicon_overrides.process_postlookups(
            language_pairs,
            lexicon_overrides.process_prelookups(
                language_pairs,
                self.lookup
            )
        )

        self.language_pairs = language_pairs

        autocomplete_tries = {}
        for k, v in language_pairs.iteritems():
            has_root = language_pairs.get(k)
            if has_root:
                fname = settings.dictionaries.get(k)
                autocomplete_tries[k] = AutocompleteTrie( tree=has_root.tree
                                                        , filename=fname
                                                        )

        self.autocomplete_tries = autocomplete_tries

    def get_lookup_type(self, lexicon, lemma, pos, pos_type, lem_args):
        args = ( bool(lemma)
               , bool(pos)
               , bool(pos_type)
               , bool(lem_args)
               )

        funcs = { (True, False, False, False): lexicon.lookupLemma
                , (True, True, False, False):  lexicon.lookupLemmaPOS
                , (True, True, True, False):   lexicon.lookupLemmaPOSAndType
                , (False, False, False, True): lexicon.lookupOtherLemmaAttr
                }

        largs = [lemma]

        if pos:
            largs.append(pos)
        if pos_type:
            largs.append(pos_type)

        return funcs.get(args, False), largs

    def lookup(self, _from, _to, lemma,
               pos=False, pos_type=False,
               _format=False, lemma_attrs=False):

        _dict = self.language_pairs.get((_from, _to), False)

        if not _dict:
            raise Exception("Undefined language pair %s %s" % (_from, _to))

        _lookup_func, largs = self.get_lookup_type(_dict, lemma, pos, pos_type, lemma_attrs)

        if not _lookup_func:
            raise Exception(
                "Unknown lookup type for lemma: %s, pos: %s, pos_type: %s" %
                ( lemma
                , pos
                , pos_type )
            )

        if lemma_attrs:
            result = _lookup_func(**lemma_attrs)
        else:
            result = _lookup_func(*largs)

        if len(result) == 0:
            return False

        if _format:
            result = list(_format(result))

        return result

    def lookups(self, _from, _to, lookups, *args, **kwargs):
        from functools import partial

        _look = partial( self.lookup
                       , _from=_from
                       , _to=_to
                       , *args
                       , **kwargs
                       )

        results = zip( lookups
                     , map(lambda x: _look(lemma=x), lookups)
                     )

        success = any([res for l, res in results])

        return results, success
