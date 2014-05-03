#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Morphological tools
"""

class Tagset(object):
    def __init__(self, name, members):
        self.name = name
        self.members = members

    def __str__(self):
        return '<Tagset: "%s">' % self.name

class Tagsets(object):
    def __init__(self, set_definitions):
        self.sets = {}
        self.set_definitions = set_definitions
        self.createTagSets()

    def createTagSets(self):
        for name, tags in self.set_definitions.iteritems():
            tagset = Tagset(name, tags)
            self.set(name, tagset)

    def get(self, name):
        return self.sets.get(name, False)

    def __getitem__(self, key):
        return self.get(key)

    def set(self, name, tagset):
        self.sets[name] = tagset

class Tag(object):
    """ A model for tags. Can be used as an iterator, as well.

    >>> for part in Tag('N+G3+Sg+Ill', '+'):
    >>>     print part

    Also, indexing is the same as Tag.getTagByTagset()

    >>> _type = Tagset('type', ['G3', 'NomAg'])
    >>> _case = Tagset('case', ['Nom', 'Ill', 'Loc'])
    >>> _ng3illsg = Tag('N+G3+Sg+Ill', '+')
    >>> _ng3illsg[_type]
    'G3'
    >>> _ng3illsg[_case]
    'Ill'

    TODO: maybe also contains for tag parts and tagsets

    TODO: begin integrating Tag and Tagsets into morphology code below,
    will help when generalizing the lexicon-morphology 'type' and 'pos'
    stuff. E.g., in `sme`, we look up words by 'pos' and 'type' when it
    exists, but in other languages this will be different. As such, we
    will need `Tag`, and `Tagset` and `Tagsets` to mitigate this.

    Also, will need some sort of lexicon lookup definition in configs,
    to describe how to bring these items together.
    """
    def __init__(self, string, sep, tagsets={}):
        self.tag_string = string
        self.sep = sep
        self.parts = self.tag_string.split(sep)
        if isinstance(tagsets, Tagsets):
            self.sets = tagsets.sets
        elif isinstance(tagsets, dict):
            self.sets = tagsets
        else:
            self.sets = tagsets

    def __contains__(self, b):
        if isinstance(b, str) or isinstance(b, unicode):
            return self.sets.get(b, False)
        return False

    def __getitem__(self, b):
        """ Overloading the xor operator to produce the tag piece that
        belongs to a given tagset. """
        _input = b
        if isinstance(b, int):
            return self.parts[b]
        if isinstance(b, str) or isinstance(b, unicode):
            b = self.sets.get(b, False)
            if not b:
                _s = ', '.join(self.sets.keys())
                raise IndexError("Invalid tagset <%s>. Choose one of: %s" % (_input, _s))
        elif isinstance(b, Tagset):
            pass
        return self.getTagByTagset(b)

    def __iter__(self):
        for x in self.parts:
            yield x

    def __str__(self):
        return '<Tag: %s>' % self.sep.join(self.parts)

    def __repr__(self):
        return '<Tag: %s>' % self.sep.join(self.parts)

    def matching_tagsets(self):
        ms = {}
        for key in self.sets.keys():
            if self[key]:
                ms[key] = self[key]
        return ms

    def getTagByTagset(self, tagset):
        for p in self.parts:
            if p in tagset.members:
                return p

    def splitByTagset(self, tagset):
        """
        >>> tagset = Tagset('compound', ['Cmp#'])
        >>> tag = Tag('N+Cmp#+N+Sg+Nom')
        >>> tag.splitByTagset(tagset)
        [<Tag: N>, <Tag: N+Sg+Nom>]
        """
        raise NotImplementedError

class Lemma(object):
    """ Lemma class that is bound to the morphology
    """
    def __key(self):
        return ( self.lemma
               , self.pos
               , self.tool.formatTag(self.tag_raw)
               )

    def __eq__(x, y):
        return x.__key() == y.__key()

    def __hash__(self):
        return hash(self.__key())

    def __unicode__(self):
        return self.lemma

    def __repr__(self):
        _lem, _pos, _tag = self.__key()
        _lem = unicode(_lem).encode('utf-8')
        _pos = unicode(_pos).encode('utf-8')
        _tag = unicode(_tag).encode('utf-8')
        cls = self.__class__.__name__
        return '<%s: %s, %s, %s>' % (cls, _lem, _pos, _tag)

    def __init__(self, lemma, pos='',
                 tag=[''], fulltag=[''], _input=False, tool=False, tagsets={}):
        self.tagsets = tagsets
        self.tool = tool
        self.lemma = lemma
        self.pos = pos
        self.tag_raw = tag
        self.tag = self.tool.tagStringToTag( fulltag
                                           , tagsets=tagsets
                                           )
        if 'pos' in self.tag:
            self.pos = self.tag['pos']
        else:
            self.pos = self.tag.parts[0]
        self.input = _input
        self.form = _input

class GeneratedForm(Lemma):
    """ Helper class for generated forms, adds attribute `self.form`,
    alters repr format. """

    def __key(self):
        return ( self.lemma
               , self.pos
               , self.tool.formatTag(self.tag_raw)
               )

    def __repr__(self):
        _lem, _pos, _tag = self.__key()
        _lem = unicode(_lem).encode('utf-8')
        _pos = unicode(_pos).encode('utf-8')
        _tag = unicode(_tag).encode('utf-8')
        f = unicode(self.form).encode('utf-8')
        cls = self.__class__.__name__
        return '<%s: %s, %s, %s, %s>' % (cls, f, _lem, _pos, _tag)

    def __init__(self, *args, **kwargs
                 ):

        super(GeneratedForm, self).__init__(*args, **kwargs)
        self.form = self.input

def word_generation_context(generated_result, *generation_input_args, **generation_kwargs):
    """ **Post-generation filter***

    Include context for verbs in the text displayed in paradigm
    generation. The rule in this case is rather complex, and looks at
    the tag used in generation.

    Possible contexts:
      * (mun) dieđán
    """
    language = generation_kwargs.get('language')

    from jinja2 import Template
    from flask import current_app

    context_for_tags = current_app.config.paradigm_contexts.get(language, {})

    node  = generation_input_args[2]

    if len(node) == 0:
        return generated_result

    context = node.xpath('.//l/@context')

    if len(context) > 0:
        context = context[0]
    else:
        context = None

    def apply_context(form):
        lemma, tag, forms = form
        tag = '+'.join(tag)

        context_formatter = context_for_tags.get(
            (context, tag), False
        )
        if context_formatter:
            formatted = []
            if forms:
                for f in forms:
                    _kwargs = {'word_form': f, 'context': context}
                    if isinstance(context_formatter, Template):
                        f = context_formatter.render(**_kwargs)
                    else:
                        f = context_formatter % _kwargs
                    formatted.append(f)
            formatted_forms = formatted
        else:
            formatted_forms = forms

        tag = tag.split('+')

        return (lemma, tag, formatted_forms)

    return map(apply_context, generated_result)


class GenerationOverrides(object):
    """ Class for collecting functions marked with decorators that
    provide special handling of tags. One class instantiated in
    morphology module: `generation_overrides`.

    >>> @generation_overrides.tag_filter_for_iso('sme')
    >>> def someFunction(form, tags, xml_node):
    >>>     ... some processing on tags, may be conditional, etc.
    >>>     return form, tags, xml_node

    Each time morphology.generation is run, the args will be passed
    through all of these functions in the order that they were
    registered, allowing for language-specific conditional rules for
    filtering.

    There is also a post-generation tag rewrite decorator registry function
    """

    ##
    ### Here are the functions that apply all the rules
    ##

    def restrict_tagsets(self, lang_code, function):
        """ This runs through each function in the tagset restriction
        registry, and applies it to the input arguments of the decorated
        function.
        """
        def decorate(*args, **kwargs):
            newargs = args
            newkwargs = kwargs
            for f in self.registry[lang_code]:
                newargs = f(*newargs, **newkwargs)
            return function(*newargs, **newkwargs)
        return decorate

    def process_generation_output(self, lang_code, function):
        """ This runs the generator function, and applies all of the
        function contexts to the output. Or in other words, this
        decorator works on the output of the decorated function, but
        also captures the input arguments, making them available to each
        function in the registry.
        """
        def decorate(*input_args, **input_kwargs):
            generated_forms = function(*input_args, **input_kwargs)
            for f in self.postgeneration_processors[lang_code]:
                generated_forms = f(generated_forms, *input_args, **input_kwargs)
            for f in self.postgeneration_processors['all']:
                input_kwargs['language'] = lang_code
                if f not in self.postgeneration_processors[lang_code]:
                    generated_forms = f(generated_forms, *input_args, **input_kwargs)
            return generated_forms
        return decorate

    def process_analysis_output(self, lang_code, function):
        """ This runs the analysis function, and applies all of the
        function contexts to the output. Or in other words, this
        decorator works on the output of the decorated function, but
        also captures the input arguments, making them available to each
        function in the registry.
        """
        def decorate(*input_args, **input_kwargs):
            generated_forms = function(*input_args, **input_kwargs)
            for f in self.postanalyzers[lang_code]:
                generated_forms = f( generated_forms
                                   , *input_args
                                   , **input_kwargs
                                   )
            return generated_forms
        return decorate

    def apply_pregenerated_forms(self, lang_code, function):
        def decorate(*args, **kwargs):
            newargs = args
            newkwargs = kwargs
            f = self.pregenerators.get(lang_code, False)
            if f:
                newargs = f(*newargs, **newkwargs)
            return function(*newargs, **newkwargs)
        return decorate

    ##
    ### Here are the decorators
    ##

    def post_analysis_processor_for_iso(self, *language_isos):
        """ For language specific processing after analysis is completed,
        for example, stripping tags before presentation to users.
        """
        def wrapper(postanalysis_function):
            for language_iso in language_isos:
                self.postanalyzers[language_iso].append(postanalysis_function)
                self.postanalyzers_doc[language_iso].append((postanalysis_function.__name__,
                                                             postanalysis_function.__doc__))
                print '%s overrides: registered post-analysis processor - %s' % \
                      ( language_iso
                      , postanalysis_function.__name__
                      )
        return wrapper

    def pregenerated_form_selector(self, *language_isos):
        """ The function that this decorates is used to select and
        construct a pregenerated paradigm for a given word and XML node.

        Only one may be defined.
        """
        def wrapper(pregenerated_selector_function):
            for language_iso in language_isos:
                self.pregenerators[language_iso] = pregenerated_selector_function
                self.pregenerators_doc[language_iso] = [(pregenerated_selector_function.__name__,
                                                         pregenerated_selector_function.__doc__)]
                print '%s overrides: registered static paradigm selector - %s' % \
                      ( language_iso
                      , pregenerated_selector_function.__name__
                      )
        return wrapper

    def tag_filter_for_iso(self, *language_isos):
        """ Register a function for a language ISO
        """
        def wrapper(restrictor_function):
            for language_iso in language_isos:
                self.registry[language_iso].append(restrictor_function)
                self.tag_filter_doc[language_iso].append(
                    ( restrictor_function.__name__
                    , restrictor_function.__doc__
                    )
                )
                print '%s overrides: registered pregeneration tag filterer - %s' %\
                      ( language_iso
                      , restrictor_function.__name__
                      )
        return wrapper

    def postgeneration_filter_for_iso(self, *language_isos):
        """ Register a function for a language ISO
        """
        def wrapper(restrictor_function):
            for language_iso in language_isos:
                self.postgeneration_processors[language_iso]\
                    .append(restrictor_function)
                self.postgeneration_processors_doc[language_iso]\
                    .append((restrictor_function.__name__,
                             restrictor_function.__doc__))
                print '%s overrides: registered entry context formatter - %s' %\
                      ( language_iso
                      , restrictor_function.__name__
                      )
        return wrapper

    def __init__(self):
        from collections import defaultdict

        self.registry      = defaultdict(list)
        self.tag_filter_doc  = defaultdict(list)
        self.pregenerators = defaultdict(list)
        self.pregenerators_doc = defaultdict(list)
        self.postanalyzers = defaultdict(list)
        self.postanalyzers_doc = defaultdict(list)

        self.postgeneration_processors = defaultdict(list)
        self.postgeneration_processors['all'] = [
            word_generation_context
        ]

        self.postgeneration_processors_doc = defaultdict(list)

generation_overrides = GenerationOverrides()

class XFST(object):

    def splitTagByCompound(self, analysis):
        _cmp = self.options.get('compoundBoundary', False)
        if _cmp:
            return analysis.split(_cmp)
        else:
            return [analysis]

    def clean(self, _output):
        """
            Clean XFST lookup text into

            [('keenaa', ['keen+V+1Sg+Ind+Pres', 'keen+V+3SgM+Ind+Pres']),
             ('keentaa', ['keen+V+2Sg+Ind+Pres', 'keen+V+3SgF+Ind+Pres'])]

        """

        analysis_chunks = [a for a in _output.split('\n\n') if a.strip()]

        cleaned = []
        for chunk in analysis_chunks:
            lemmas = []
            analyses = []

            for part in chunk.split('\n'):
                lemma, _, analysis = part.partition('\t')
                lemmas.append(lemma)
                analyses.append(analysis)

            lemma = list(set(lemmas))[0]

            append_ = (lemma, analyses)

            cleaned.append(append_)

        return cleaned

    # TODO: need to cache eeeeeeeeeeeeverything.
    def _exec(self, _input, cmd, timeout=5):
        """ Execute a process, but kill it after 5 seconds. Generally
        we expect small things here, not big things.
        """
        import subprocess
        from threading import Timer

        try:
            _input = _input.encode('utf-8')
        except:
            pass

        lookup_proc = subprocess.Popen(cmd.split(' '),
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)

        def kill_proc(proc=lookup_proc):
            try:
                proc.kill()
                raise Exception("Process for %s took too long." % cmd)
            except OSError:
                pass
            return

        if not timeout:
            t = Timer(5, kill_proc)
            t.start()

        output, err = lookup_proc.communicate(_input)

        if output:
            try:
                output = output.decode('utf-8')
            except:
                pass

        if err:
            try:
                err = err.decode('utf-8')
            except:
                pass

        return (output, err)

    def __init__(self, lookup_tool, fst_file, ifst_file=False, options={}):
        self.cmd = "%s -flags mbTT %s" % (lookup_tool, fst_file)
        self.options = options

        if ifst_file:
            self.icmd = "%s -flags mbTT %s" % (lookup_tool, ifst_file)
        else:
            self.icmd = False

    # def __rshift__(left, right):
    #     right.tool = left
    #     left.logger = right.logger
    #     return right

    def applyMorph(self, morph):
        morph.tool = self
        self.logger = morph.logger
        return morph

    def lookup(self, lookups_list):
        lookup_string = '\n'.join(lookups_list)
        output, err = self._exec(lookup_string, cmd=self.cmd)
        if len(output) == 0 and len(err) > 0:
            name = self.__class__.__name__
            msg = """%s: %s""" % (name, err)
            self.logger.error(msg.strip())
        return self.clean(output)

    def inverselookup_by_string(self, lookup_string):
        import sys
        if not self.icmd:
            print >> sys.stderr, " * Inverse lookups not available."
            return False

        output, err = self._exec(lookup_string, cmd=self.icmd)
        return self.clean(output)

    def inverselookup(self, lemma, tags):
        import sys
        if not self.icmd:
            print >> sys.stderr, " * Inverse lookups not available."
            return False

        lookups_list = []
        for tag in tags:
            lookups_list.append(self.formatTag([lemma] + tag, inverse=True))
        lookup_string = '\n'.join(lookups_list)
        output, err = self._exec(lookup_string, cmd=self.icmd)
        return self.clean(output)

    def tagUnknown(self, analysis):
        if '+?' in analysis:
            return True
        else:
            return False

    def tagStringToTag(self, parts, tagsets={}, inverse=False):
        if inverse:
            delim = self.options.get('inverse_tagsep',
                self.options.get('tagsep', '+'))
        else:
            delim = self.options.get('tagsep', '+')
        tag = delim.join(parts)
        return Tag(tag, delim, tagsets=tagsets)

    def formatTag(self, parts, inverse=False):
        if inverse:
            delim = self.options.get('inverse_tagsep',
                self.options.get('tagsep', '+'))
        else:
            delim = self.options.get('tagsep', '+')
        return delim.join(parts)

    def splitAnalysis(self, analysis, inverse=False):
        """ u'lemma+Tag+Tag+Tag' -> [u'lemma', u'Tag', u'Tag', u'Tag'] """
        if inverse:
            delim = self.options.get('inverse_tagsep',
                self.options.get('tagsep', '+'))
        else:
            delim = self.options.get('tagsep', '+')

        return analysis.split(delim)

class OBT(XFST):
    """ TODO: this is almost like CG, so separate out those things if
    necessary.
    """

    def clean(self, _output):
        """ Clean CG lookup text into

            [('keenaa', ['keen+V+1Sg+Ind+Pres', 'keen+V+3SgM+Ind+Pres']),
             ('keentaa', ['keen+V+2Sg+Ind+Pres', 'keen+V+3SgF+Ind+Pres'])]

        """

        analysis_chunks = []

        chunk = []
        for line in _output.splitlines():

            if line.startswith('"<'):
                if len(chunk) > 0:
                    analysis_chunks.append(chunk)
                chunk = [line]
                continue
            elif line.startswith("\t\""):
                chunk.append(line.strip())
        else:
            analysis_chunks.append(chunk)

        cleaned = []
        for chunk in analysis_chunks:
            form, analyses = chunk[0], chunk[1::]

            lemmas = []
            tags = []
            for part in analyses:
                tagparts = part.split(' ')
                lemma = tagparts[0]
                lemma = lemma.replace('"', '')
                lemmas.append(lemma)
                tags.append(' '.join([lemma] + tagparts[1::]))

            lemma = list(set(lemmas))[0]

            form = form[2:len(form) - 2]
            append_ = (form, tags)

            cleaned.append(append_)

        return cleaned

    def splitAnalysis(self, analysis):
        return analysis.split(' ')

    def __init__(self, lookup_tool, options={}):
        self.cmd = lookup_tool
        self.options = options

class Morphology(object):

    def generate_to_objs(self, *args, **kwargs):
        def make_lemma(r):
            lems = []

            lemma, tag, forms = r
            _pos      = tag[0]
            _analysis = tag
            _fulltag  = tag
            for f in forms:
                lem = GeneratedForm(lemma, _pos, _analysis, fulltag=_fulltag,
                         _input=f, tool=self.tool,
                         tagsets=self.tagsets)
                lems.append(lem)
            return lems

        generated = sum(map(make_lemma, self.generate(*args, **kwargs)), [])
        return generated

    def generate(self, lemma, tagsets, node=None, pregenerated=None):
        """ Run the lookup command, parse output into
            [(lemma, ['Verb', 'Inf'], ['form1', 'form2'])]

            If pregenerated, we pass the forms in using the same
            structure as the analyzed output. The purpose here is that
            pregenerated forms in lexicon may differ from language to
            language, and we want to allow processing for that to occur
            elsewhere.

            TODO: cache pregenerated forms, return them.

        """
        if len(node) > 0:
            key = self.generate_cache_key(lemma, tagsets, node)
        else:
            key = self.generate_cache_key(lemma, tagsets)

        _is_cached = self.cache.get(key)
        if _is_cached:
            return _is_cached

        if pregenerated:
            _is_cached = self.cache.set(key, pregenerated)
            return pregenerated

        res = self.tool.inverselookup(lemma, tagsets)
        reformatted = []
        for tag, forms in res:
            unknown = False
            for f in forms:
                # TODO: how does OBT handle unknown?
                if '+?' in f:
                    unknown = True
                    msg = self.tool.__class__.__name__ + ': ' + \
                         tag + '\t' + '|'.join(forms)
                    self.tool.logger.error(msg)

            if not unknown:
                parts = self.tool.splitAnalysis(tag, inverse=True)
                lemma = parts[0]
                tag = parts[1::]
                reformatted.append((lemma, tag, forms))
            else:
                parts = self.tool.splitAnalysis(tag, inverse=True)
                lemma = parts[0]
                tag = parts[1::]
                forms = False
                reformatted.append((lemma, tag, forms))

        _is_cached = self.cache.set(key, reformatted)
        return reformatted

    # TODO: option, or separate function to also return discarded to
    # find out what's been removed to hide more_info link 
    def lemmatize(self, form, split_compounds=False,
                  non_compound_only=False, no_derivations=False):
        """ For a wordform, return a list of lemmas
        """
        def remove_compound_analyses(_a):
            _cmp = self.tool.options.get('compoundBoundary', False)
            if not _cmp:
                return True
            if _cmp in _a:
                return False
            else:
                return True

        def remove_derivations(_a):
            _der = self.tool.options.get('derivationMarker', False)
            if not _der:
                return True
            if _der in _a:
                return False
            else:
                return True

        def maybe_filter(function, iterable):
            result = filter(function, iterable)
            if len(result) > 0:
                return result
            else:
                return iterable

        lookups = self.tool.lookup([form])

        # Check for unknown

        unknown = False
        for k, v in lookups:
            for a in v:
                if '?' in a:
                    unknown = True

        if unknown:
            return False

        lemmas = set()

        for _form, analyses in lookups:

            if non_compound_only:
                analyses = maybe_filter(remove_compound_analyses, analyses)

            if no_derivations:
                analyses = maybe_filter(remove_derivations, analyses)

            if split_compounds:
                analyses = sum( map(self.tool.splitTagByCompound, analyses)
                              , []
                              )

            for analysis in analyses:
                _an_parts = self.tool.splitAnalysis(analysis)
                # If a word doesn't have a PoS in an analysis, we try to
                # handle it as best as possible.
                if len(_an_parts) == 1:
                    _lem = _an_parts[0]
                    lem = Lemma(lemma=_lem, _input=_lem, tool=self.tool, tagsets=self.tagsets)
                else:
                    _lem      = _an_parts[0]
                    _pos      = _an_parts[1]
                    _analysis = _an_parts[1::]
                    _fulltag  = _an_parts[1::]
                    lem = Lemma( _lem, _pos, _analysis
                               , fulltag=_fulltag, _input=form
                               , tool=self.tool, tagsets=self.tagsets
                               )
                lemmas.add(lem)

        return list(lemmas)

    def de_pickle_lemma(self, lem, tag):
        _tag = self.tool.splitAnalysis(tag)
        lem = Lemma( lem, '', _tag, fulltag=_tag
                   , tool=self.tool, tagsets=self.tagsets
                   )
        return lem

    def generate_cache_key(self, lemma, generation_tags, node=False):
        """ key is something like generation-LANG-nodehash-TAG|TAG|TAG
        """
        import hashlib
        _cache_tags = '|'.join(['+'.join(a) for a in generation_tags])

        _cache_key = hashlib.md5()
        _cache_key.update('generation-%s-' % self.langcode)
        _cache_key.update(lemma.encode('utf-8'))
        if len(node) > 0:
            node_hash = node.__hash__()
            _cache_key.update(str(node_hash))
        _cache_key.update(_cache_tags.encode('utf-8'))
        return _cache_key.hexdigest()

    def __init__(self, languagecode, tagsets={}, cache=False):
        self.langcode = languagecode

        self.generate = generation_overrides.apply_pregenerated_forms(
            languagecode, self.generate
        )
        self.generate = generation_overrides.restrict_tagsets(
            languagecode, self.generate
        )
        self.generate = generation_overrides.process_generation_output(
            languagecode, self.generate
        )

        self.lemmatize = generation_overrides.process_analysis_output(
            languagecode, self.lemmatize
        )

        if cache:
            self.cache = cache
        else:
            self.cache = False

        import logging
        logfile = logging.FileHandler('morph_log.txt')
        self.logger = logging.getLogger('morphology')
        self.logger.setLevel(logging.ERROR)
        self.logger.addHandler(logfile)

        self.tagsets = Tagsets(tagsets)
