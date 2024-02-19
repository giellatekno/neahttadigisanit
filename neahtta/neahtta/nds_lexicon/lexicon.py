from lxml import etree
import sys
from hashlib import blake2b

from .lookups import SearchTypes

""" Our project-wide search_types repository. """
search_types = SearchTypes({})

DEFAULT_XPATHS = {
    "pos": "lg/l/@pos",
}


def hash_node(node):
    # anders: used in a template, where it is concatenated with a string, so
    # it cannot be an int (which is what we get from hash()), it must be string
    # return str(hash(etree.tostring(node)))

    # anders: I was running into issues where the "e_node" argument never
    # matched, and I had an idea that this may have been because in somewhat
    # newer python versions, strings are randomly salted when given to
    # hash() - because otherwise there would be a potential DoS attack
    # available against many python programs who did not protect against this
    # by default. Basically, if an application was using dictionaries with
    # string keys, an attacker could find a particular string that would
    # create keys with the same hash, and hence make the upper-case N^2
    # run time of hashmap insertion happen a lot - thereby purposefully
    # slowing a python application down to basically a halt.

    # references:
    # "oCERT-2011-003 multiple implementations denial-of-service via
    # hash algorithm collision":
    # http://ocert.org/advisories/ocert-2011-003.html
    # https://docs.python.org/3/reference/datamodel.html#object.__hash__
    # -- which states that: python enabled this by default in 3.3.
    # -> which means that for us, when running python 2.7, the implementation
    # above (or, rather, "return unicode(hash(etree.tostring(node)))" - would
    # work just fine for this purpose, but ever since the switch to python 3,
    # we have had this bug.)

    # In practice, you can see this if you do run (on the command line)
    # $ python -c "print(hash('a'))"
    # Notice how you get a different output each time, even though the string
    # never changes. This is the unpredictable randomized salting in action.

    # Long story short, I am now trying to switch this way that we hash <e>
    # nodes to a method that will be "stable" - i.e. produce the same
    # hash every single time we hash it.
    s = etree.tostring(node)

    # small digest size, for a shorter string in urls
    h = blake2b(s, digest_size=10)
    return h.hexdigest()


class LexiconOverrides:
    """Class for collecting functions marked with decorators that
    provide special handling of tags. One class instantiated in
    morphology module: `generation_overrides`.

    Current practice is to store these in language-specific modules within
    :py:module:`configs.language_specific_rules`...
    """

    ##
    ### Here are the functions that apply all the rules
    ##

    def format_source(self, lang_iso, ui_lang, e, target_lang, default_str):
        """Find the function decorated by
            @overrides.entry_source_formatter(iso)
        and run the function on an XML node.
        """
        if lang_iso in self.source_formatters:
            return (
                self.source_formatters.get(lang_iso)(ui_lang, e, target_lang)
                or default_str
            )
        return default_str

    def format_target(self, src_iso, targ_iso, ui_lang, e, tg, default_str):
        """Find the function decorated by
            @overrides.entry_source_formatter(iso)
        and run the function on an XML node.
        """
        if (src_iso, targ_iso) in self.target_formatters:
            return (
                self.target_formatters.get((src_iso, targ_iso))(ui_lang, e, tg)
                or default_str
            )
        return default_str

    def process_prelookups(self, lexicon_language_pairs, function):
        """This runs the generator function, and applies all of the
        function contexts to the output. Or in other words, this
        decorator works on the output of the decorated function, but
        also captures the input arguments, making them available to each
        function in the registry.
        """

        def decorate(*args, **kwargs):
            # anders: unused
            # lang_pair = lexicon_language_pairs.get(args)
            _from = args[0]
            newargs = args
            newkwargs = kwargs
            for f in self.prelookup_processors[_from]:
                newargs, newkwargs = f(*newargs, **newkwargs)
            return function(*newargs, **newkwargs)

        return decorate

    def process_postlookups(self, lexicon_language_pairs, function):
        """Lexicon lookups are passed through all of these functions"""

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
        """Register a function for a language ISO.

        Functions decorated by this registry decorator should take one
        argument, an entry node, and return either a string or None. If
        None is returned, then a default value will be returned instead.

        The default value is passed to the function format_source, which
        selects the registered function and executes it.
        """

        def wrapper(formatter_function):
            for language_iso in language_isos:
                if language_iso in self.source_formatters:
                    print(
                        f" * OBS! Source formatter already registered for {language_iso}."
                    )
                    print(
                        f"   ignoring redefinition on <{formatter_function.__name__}>."
                    )
                else:
                    self.source_formatters[language_iso] = formatter_function
                    print(
                        f"{language_iso} formatter: entry formatter for source - {formatter_function.__name__}"
                    )

        return wrapper

    def entry_target_formatter(self, *iso_pairs):
        """Register a function for a language ISO"""

        def wrapper(formatter_function):
            for src_iso, targ_iso in iso_pairs:
                if (src_iso, targ_iso) in self.target_formatters:
                    print(
                        f" * OBS! Target formatter already registered for {repr((src_iso, targ_iso))}."
                    )
                    print(
                        f"   ignoring redefinition on <{formatter_function.__name__}>."
                    )
                else:
                    self.target_formatters[(src_iso, targ_iso)] = formatter_function
                    print(
                        f"{src_iso} - {targ_iso} formatter: entry formatter for target - {formatter_function.__name__}"
                    )

        return wrapper

    def pre_lookup_tag_rewrite_for_iso(self, *language_isos):
        """Register a function for a language ISO to adjust tags used in
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
                self.prelookup_processors[language_iso].append(restrictor_function)
                print(
                    f"{language_iso} overrides: lexicon pre-lookup arg rewriter - {restrictor_function.__name__}"
                )

        return wrapper

    def postlookup_filters_for_lexicon(self, *lexica):
        """Register a function for a language ISO to adjust tags used
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
                self.postlookup_filters[lexicon].append(restrictor_function)
                print(
                    f"{lexicon} overrides: lexicon lookup filter - {restrictor_function.__name__}"
                )

        return wrapper

    def external_search(self, *lexica):
        """Register a function for a language ISO to adjust tags used
        in FSTs for use in lexicon lookups. The decorator function takes
        a tuple for every function that the decorator should be applied
        to

        >>> @lexicon_overrides.lookup_filters_for_lexicon(('sme', 'nob'))
        >>> def someFunction(nodelist):
        >>>     ... some processing on tags, may be conditional, etc.
        >>>     return nodelist
        """

        def wrapper(search_function):
            for shortcut_name, source, target in lexica:
                self.external_search_redirect[
                    (shortcut_name, source, target)
                ] = search_function
                print(
                    f"{source}->{target} overrides: lexicon lookup filter - {shortcut_name}"
                )

        return wrapper

    def __init__(self):
        from collections import defaultdict

        self.prelookup_processors = defaultdict(list)
        self.target_formatters = defaultdict(bool)
        self.source_formatters = defaultdict(bool)
        self.postlookup_filters = defaultdict(list)
        self.external_search_redirect = defaultdict(bool)


lexicon_overrides = LexiconOverrides()

PARSED_TREES = {}

regexpNS = "http://exslt.org/regular-expressions"


# @search_types.add_custom_lookup_type('regular')
class XMLDict:
    """XML dictionary class. Initiate with a file path or an already parsed
    tree, exposes methods for searching in XML.

    Entries should be formatted by creating an EntryNodeIterator object,
    which will clean them on iteration.
    """

    PARSED_TREES = PARSED_TREES

    def __init__(self, filename=False, tree=False, options=None):
        options = {} if options is None else options
        xpaths = DEFAULT_XPATHS.copy()
        xpaths.update(**options)

        if tree:
            self.tree = tree
        else:
            try:
                self.tree = PARSED_TREES[filename]
            except KeyError:
                print(f"parsing {filename}")
                try:
                    self.tree = etree.parse(filename)
                except Exception as e:
                    # checking Exception specifically here, because it's
                    # not really clear from the lxml docs exactly which
                    # exception gets raised for the different type of errors.
                    # FileNotFoundError is not raised at all, for example.
                    print(f"Fail: Could not parse {filename}", file=sys.stderr)
                    print(e, file=sys.stderr)
                    print(type(e), file=sys.stderr)
                    sys.exit(2)
                else:
                    PARSED_TREES[filename] = self.tree

        self.xpath_evaluator = etree.XPathDocumentEvaluator(self.tree)

        # Initialize XPath queries
        _re_pos_match = f"""re:match({xpaths['pos']}, $pos, "i")"""

        self.lemmaStartsWith = etree.XPath(
            f".//e[starts-with({xpaths['pos']}, $lemma)]"
        )

        self.lemma = etree.XPath(".//e[lg/l/text() = $lemma]")

        self.lemmaPOS = etree.XPath(
            ".//e[lg/l/text() = $lemma and " + _re_pos_match + "]",
            namespaces={"re": regexpNS},
        )

        self.lemmaPOSAndType = etree.XPath(
            " and ".join(
                [".//e[lg/l/text() = $lemma", _re_pos_match, "lg/l/@type = $_type]"]
            ),
            namespaces={"re": regexpNS},
        )

    def XPath(self, xpathobj, *args, **kwargs):
        return xpathobj(self.tree, *args, **kwargs)

    def lookupLemmaStartsWith(self, lemma):
        return self.XPath(self.lemmaStartsWith, lemma=lemma)

    def lookupLemma(self, lemma):
        return self.XPath(self.lemma, lemma=lemma)

    def lookupLemmaPOS(self, lemma, pos):
        # Can't insert variables in EXSLT expressions within a compiled
        # xpath statement, so doing this.
        pos = f"^{pos}$"
        return self.XPath(self.lemmaPOS, lemma=lemma, pos=pos)

    def lookupLemmaPOSAndType(self, lemma, pos, _type):
        pos = f"^{pos}$"
        return self.XPath(self.lemmaPOSAndType, lemma=lemma, pos=pos, _type=_type)

    def iterate_entries(self, start=0, end=20, words=False):
        if words:
            _xp = etree.XPath(".//e/lg/l/text()")
            ws = _xp(self.tree)

            if end:
                ws = ws[start:end]

            return ws
        else:
            if end:
                _xp = etree.XPath(f".//e[position() >= {start} and position() < {end}]")
            else:
                _xp = etree.XPath(".//e")

        return _xp(self.tree)

    def iterate_letter_pages(self, page_size=20):
        # 1.) make list of tuples containing the first letter and the
        # iteration number, and then the page count

        # 2.) filter out only instances where the first letter is
        # different from the second

        _xp = etree.XPath(".//e/lg/l/text()")
        ws = _xp(self.tree)

        counts = []
        page = 0
        last_letter = ws[0][0]

        for i, w in enumerate(ws):
            current_letter = w[0].lower()
            if i % page_size == 0 and i > 0:
                page += 1
            if last_letter != current_letter:
                counts.append((current_letter, page))
            last_letter = current_letter

        return counts

    def iterate_entries_count(self):
        _xp = etree.XPath(".//e")
        es = len(_xp(self.tree))

        return len(es)

    def lookupOtherLemmaAttr(self, **attrs):
        attr_conditions = []
        for k, v in attrs.items():
            attr_conditions.append(f"lg/l/@{k} = '{v}'")
        attr_conditions = " and ".join(attr_conditions)

        _xpath_expr = f".//e[{attr_conditions}]"
        _xp = etree.XPath(_xpath_expr, namespaces={"re": regexpNS})
        return _xp(self.tree)


class AutocompleteFilters:
    def autocomplete_filter_for_lang(self, language_iso):
        def wrapper(filter_function):
            self._filters[language_iso].append(filter_function)
            print(
                f"{language_iso} filter: autocomplete entry filter for language - {filter_function.__name__}"
            )

        return wrapper

    def __init__(self, *args, **kwargs):
        from collections import defaultdict

        self._filters = defaultdict(list)


autocomplete_filters = AutocompleteFilters()


def autocompleteKey(word):
    """Propernouns should be placed after all other words.
    To do this, the Unicode character U+FFFD � REPLACEMENT CHARACTER
    is added to the start of propernouns when sorting, as this is
    the last character in the Default Unicode Collation Element Table.
    """
    if word and word[0].isupper():
        return "\uFFFD" + word
    else:
        return word


class AutocompleteTrie(XMLDict):
    def __init__(self, *args, **kwargs):
        if "language_pair" in kwargs:
            self.language_pair = kwargs.pop("language_pair")

        super().__init__(*args, **kwargs)

        from .trie import Trie

        print("Building autocomplete trie...")
        filename = kwargs["filename"]

        parsed_key = f"auto-{filename}"
        if parsed_key not in PARSED_TREES:
            self.trie = Trie()
            self.trie.update(self.allLemmas)
            PARSED_TREES[parsed_key] = self.trie
        else:
            self.trie = PARSED_TREES[parsed_key]

    @property
    def allLemmas(self):
        """Returns iterator for all lemmas."""
        entries = self.tree.findall("e/lg/l")
        filters = autocomplete_filters._filters.get(self.language_pair, [])
        for f in filters:
            entries = f(entries)
        lemma_strings = (e.text for e in entries if e.text)
        return lemma_strings

    def autocomplete(self, query):
        from unicodedata import combining

        if not self.trie:
            return []

        if not hasattr(self.trie, "autocomplete"):
            # anders: only if explicitly turned off autocompletions?
            return []

        qlen = len(query)
        result = []
        for candidate in self.trie.autocomplete(query):
            if len(candidate) == qlen:
                # candidate is query exactly, so there is no "next" character
                # to check - it is always a candidate we want to show
                result.append(candidate)
                continue

            if len(candidate) > qlen:
                # candidate has longer length than query, so check if the
                # character immediately following the common start of
                # candidate and query is a combining character. if it is, we
                # do not want to show that as a valid candidate.
                # For example, if the query is "мо", a candidate can be
                # "мо<COMBINING MACRON>[...]", which really means that
                # the candidate is actually "мо̄[...]" (the COMBINING MACRON
                # makes the "о" an "о̄", which are two different characters).
                # so we ignore that candidate completely.
                if combining(candidate[qlen]):
                    pass
                else:
                    result.append(candidate)

            assert None, "candidate is never shorter than query"

        return sorted(result, key=autocompleteKey)


class ReverseLookups(XMLDict):
    """
    1. don't use entries with reverse="no" at entry level
    2. search by e/mg/tg/t/text() instead of /e/lg/l/text()
    """

    def cleanEntry(self, e):
        ts = e.findall("mg/tg/t")
        ts_text = [t.text for t in ts]
        ts_pos = [t.get("pos") for t in ts]

        L = e.find("lg/l")
        right_text = [L.text]

        return {"left": ts_text, "pos": ts_pos, "right": right_text}

    def lookupLemmaStartsWith(self, lemma):
        _xpath = f'.//e[mg/tg/t/starts-with(text(), "{lemma}")]'
        return self.XPath(_xpath)

    def lookupLemma(self, lemma):
        _xpath = [f'.//e[mg/tg/t/text() = "{lemma}"', "not(@reverse)]"]
        _xpath = " and ".join(_xpath)
        nodes = self.XPath(_xpath)
        return self.modifyNodes(nodes)

    def lookupLemmaPOS(self, lemma, pos):
        _xpath = " and ".join(
            [
                f'.//e[mg/tg/t/text() = "{lemma}"',
                "not(@reverse)",
                f'mg/tg/t/@pos = "{pos.lower()}"]',
            ]
        )
        return self.XPath(_xpath)


class Lexicon:
    def __init__(self, settings):
        """Create a lexicon based on the configuration.

        Each XML file will be loaded individually, and the file handle
        will be cached, so if multiple dictionaries (for example, one
        lexicon may have multiple input variants), these will not be
        loaded into memory separately.
        """

        # Initialize variant lookup types
        lookup_types = {
            "regular": XMLDict,
            "test_data": XMLDict,
        }

        lookup_types.update(search_types.search_types)

        language_pairs = {}
        for langpair, path in settings.dictionaries.items():
            options = settings.dictionary_options.get(langpair, {})

            # anders: the paths have changed
            d = XMLDict(filename=f"neahtta/{path}", options=options)
            language_pairs[langpair] = d

        alternate_dicts = {}
        for langpair, opts in settings.variant_dictionaries.items():
            # anders: paths have changed
            filename = "neahtta/" + opts.get("path")
            options = settings.dictionary_options.get(langpair, {})
            d = XMLDict(filename=filename, options=options)
            alternate_dicts[langpair] = d

        # run through variant searches for overrides
        variant_searches = {}

        for k, variants in settings.search_variants.items():
            pair_variants = {}
            for var in variants:
                variant_type = var.get("type", "regular")
                cls = lookup_types.get(variant_type)
                variant_search = cls(filename=var.get("path"))
                pair_variants[variant_type] = variant_search
            variant_searches[k] = pair_variants

        self.variant_searches = variant_searches
        langs_and_alternates = {}
        langs_and_alternates.update(language_pairs)
        langs_and_alternates.update(alternate_dicts)

        self.lookup = lexicon_overrides.process_postlookups(
            langs_and_alternates,
            lexicon_overrides.process_prelookups(langs_and_alternates, self.lookup),
        )

        self.variant_lookup = lexicon_overrides.process_postlookups(
            variant_searches,
            lexicon_overrides.process_prelookups(variant_searches, self.variant_lookup),
        )

        self.language_pairs = langs_and_alternates

        autocomplete_tries = {}
        for k, v in language_pairs.items():
            if settings.pair_definitions.get(k).get("autocomplete"):
                has_root = language_pairs.get(k)
                if has_root:
                    fname = settings.dictionaries.get(k)
                    autocomplete_tries[k] = AutocompleteTrie(
                        tree=has_root.tree, filename=fname, language_pair=k
                    )

        self.autocomplete_tries = autocomplete_tries

    def get_lookup_type(self, user_input, lexicon, lemma, pos, pos_type, lem_args):
        """Determine what type of lookup to perform based on the
        available arguments, and return that lookup function.
        """

        args = (bool(lemma), bool(pos), bool(pos_type), bool(lem_args))

        funcs = {
            (True, False, False, False): lexicon.lookupLemma,
            (True, True, False, False): lexicon.lookupLemmaPOS,
            (True, True, True, False): lexicon.lookupLemmaPOSAndType,
            (False, False, False, True): lexicon.lookupOtherLemmaAttr,
        }

        try:
            f = funcs[args]
        except KeyError as e:
            msg = (
                f"Unknown lookup type for <{user_input}> ({lemma=}, {pos=}, "
                f"{pos_type=}, {lem_args=})"
            )
            raise Exception(msg) from e

        largs = [lemma]

        if pos:
            largs.append(pos)
        if pos_type:
            largs.append(pos_type)

        return f, largs

    def browse(self, _from, _to, page=0, count=20, _format=None):
        try:
            _dict = self.language_pairs[(_from, _to)]
        except KeyError:
            raise Exception(f"Undefined language pair {_from} {_to}")

        start = count * page
        end = count * (page + 1)

        result = _dict.iterate_entries(start, end)

        if not result:
            return False

        if _format:
            result = list(_format(result))

        return result

    def list_words(self, _from, _to, start=0, end=40, _format=None):
        _dict = self.language_pairs.get((_from, _to), False)

        if not _dict:
            raise Exception(f"Undefined language pair {_from} {_to}")

        result = _dict.iterate_entries(start, end, words=True)

        if len(result) == 0:
            return False

        if _format:
            result = list(_format(result))

        return result

    def get_letter_positions(self, _from, _to):
        _dict = self.language_pairs.get((_from, _to), False)

        if not _dict:
            raise Exception(f"Undefined language pair {_from} {_to}")

        result = _dict.iterate_letter_pages()

        if len(result) == 0:
            return False

        return result

    def lookup(
        self,
        _from,
        _to,
        lemma,
        pos=False,
        pos_type=False,
        _format=False,
        lemma_attrs=False,
        user_input=False,
    ) -> list:
        """Perform a lexicon lookup. Depending on the keyword
        arguments, several types of lookups may be performed.

          * lemma lookup -
            `lexicon.lookup(source_lang, target_lang, lemma)`

          * lemma lookup + POS -
            `lexicon.lookup(source_lang, target_lang, lemma, pos=POS)`

             This lookup uses the lemma, and the `@pos` attribute on the <l /> node.

          * lemma lookup + POS + Type -
             `lexicon.lookup(source_lang, target_lang, lemma, pos=POS)`

             This lookup uses the lemma, the `@pos` attribute on the <l /> node,
             and the `@type` attribute.

          * lemma lookup + other attributes
            `lexicon.lookup(source_lang, target_lang, lemma, lemma_attrs={'attr_1': asdf, 'attr_2': asdf}`

            A dictionary of arguments may be supplied, matching attributes on the <l /> node.
        """
        try:
            dictionary = self.language_pairs[(_from, _to)]
        except KeyError as e:
            raise Exception(f"Undefined language pair {_from} {_to}") from e

        lookup_func, largs = self.get_lookup_type(
            user_input,
            dictionary,
            lemma,
            pos,
            pos_type,
            lemma_attrs,
        )

        if lemma_attrs:
            result = lookup_func(**lemma_attrs)
        else:
            result = lookup_func(*largs)

        if _format:
            result = list(_format(result))

        assert isinstance(result, list)
        return result

    def variant_lookup(
        self,
        _from,
        _to,
        search_type,
        lemma,
        pos=False,
        pos_type=False,
        _format=False,
        lemma_attrs=False,
        user_input=False,
    ):
        """Perform a lexicon lookup. Depending on the keyword
        arguments, several types of lookups may be performed.

          * term lookup -
            `lexicon.lookup(source_lang, target_lang, type, term)`

          TODO: these

          * lemma lookup + POS -
            `lexicon.lookup(source_lang, target_lang, lemma, pos=POS)`

             This lookup uses the lemma, and the `@pos` attribute on the <l /> node.

          * lemma lookup + POS + Type -
             `lexicon.lookup(source_lang, target_lang, lemma, pos=POS)`

             This lookup uses the lemma, the `@pos` attribute on the <l /> node,
             and the `@type` attribute.

          * lemma lookup + other attributes
            `lexicon.lookup(source_lang, target_lang, lemma, lemma_attrs={'attr_1': asdf, 'attr_2': asdf}`

            A dictionary of arguments may be supplied, matching attributes on the <l /> node.
        """

        _dict = self.variant_searches.get((_from, _to), {}).get(search_type, False)

        if not _dict:
            raise Exception(f"Undefined language pair {_from} {_to}")

        _lookup_func, largs = self.get_lookup_type(
            _dict, lemma, pos, pos_type, lemma_attrs
        )

        if not _lookup_func:
            raise Exception(
                f"Unknown lookup type for <{user_input}> (lemma: {lemma}, pos: {pos}, pos_type: {pos_type}, lemma_attrs: {repr(lemma_attrs)})"
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

        _look = partial(self.lookup, _from=_from, _to=_to, *args, **kwargs)

        results = zip(lookups, list(map(lambda x: _look(lemma=x), lookups)))
        success = any(res for _, res in results)

        return results, success
