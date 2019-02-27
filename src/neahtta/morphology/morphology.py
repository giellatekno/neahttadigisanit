#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Morphological tools
"""
import imp
import os
import re
from itertools import groupby
from operator import itemgetter

from cache import cache

# TODO: get from global path
configs_path = os.path.join(os.path.dirname(__file__), '../')


class TagPart(object):
    """ This is a part of a tag, which should behave mostly like a string:

        >>> v = TagPart('V')
        >>> v == 'V'
        True
        >>> repr(v)
        'V'
        >>> str(v)
        'V'
        >>> unicode(v)
        u'V'

    Except when some additional attributes are defined to allow for
    regular expression matching

        >>> v = TagPart({'match': '^PV', 'regex': True})
        >>> v == 'bbq'
        False
        >>> v == 'PV/e'
        True

    If the tagset fails to compile:

        >>> v = TagPart({'match': '(asdf', 'regex': True})
        >>> v == 'bbq'
        False
        >>> v == 'PV/e'
        True

    """

    def __init__(self, _t):
        self._t = _t
        self.regex = False
        if type(_t) == dict:
            self.val = _t.get('match')
            self.regex = _t.get('regex', False)
        else:
            self.val = _t
        if self.regex:
            try:
                self._re = re.compile(self.val)
            except Exception, e:
                print self._t
                raise e

    def __unicode__(self):
        return self.val

    def __repr__(self):
        return self.val

    def __eq__(self, other):
        if self.regex:
            m = self._re.match(other)
            return m is not None
        else:
            return self.val == other


class Tagset(object):
    def __init__(self, name, members):
        self.name = name
        self.members = map(TagPart, members)

    def __str__(self):
        return '<Tagset: "%s">' % self.name

    def __contains__(self, item):
        return item in self.members


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

    def all_tags(self):
        _all = list(
            set(sum([v.members for k, v in self.sets.iteritems()], [])))
        return _all


class Tag(object):
    """ A model for tags. Can be used as an iterator, as well.

    #>> for part in Tag('N+G3+Sg+Ill', '+'):
    #>>     print part

    Also, indexing is the same as Tag.getTagByTagset()

    >>> _type = Tagset('type', ['G3', 'NomAg'])
    >>> _case = Tagset('case', ['Nom', 'Ill', 'Loc'])
    >>> _ng3illsg = Tag('N+G3+Sg+Ill', '+')
    >>> _ng3illsg[_type]
    'G3'
    >>> _ng3illsg[_case]
    'Ill'
    >>> _pv = Tagset('preverb', ['1', '2', {'match': '^PV', 'regex': True}])
    >>> pv_tag = Tag('PV/e+V+Sg', '+')
    >>> 'PV/e' in _pv
    True
    >>> pv_tag[_pv]
    'PV/e'
    >>> pv_tag = Tag('PV/omgbbq+V+Sg', '+')
    >>> 'PV/omgbbq' in _pv
    True
    >>> pv_tag[_pv] != 'PV/e'
    True

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
                raise IndexError(
                    "Invalid tagset <%s>. Choose one of: %s" % (_input, _s))
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
        #>> tagset = Tagset('compound', ['Cmp#'])
        [Cmp#]
        #>> tag = Tag('N+Cmp#+N+Sg+Nom')
        #>> tag.splitByTagset(tagset)
        [<Tag: N>, <Tag: N+Sg+Nom>]
        """
        raise NotImplementedError


class Lemma(object):
    """ Lemma class that is bound to the morphology
    """

    def __key(self):
        return (self.lemma, self.pos, self.tool.formatTag(self.tag_raw))

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

    def prepare_tag(self, tag, tagsets):
        """ Clean up the tag, lemma, and POS, make adjustments depending
        on whether the langauge has tags before the lemma.

        NB: if there's a problem here, make sure any possible tags
        before the lemma are defined as some member of any tagset.
        """
        all_tags = tagsets.all_tags()
        self.tag = self.tool.tagStringToTag(tag, tagsets=tagsets)

        # Best guess is the first item, otherwise...
        lemma = tag[0]
        # Best guess is the first item, otherwise...
        #self.lemma = tag[0]
        #del tag[0]
        if lemma in all_tags:
            # Separate out items that are not values in a tagset, these
            # are probably the lemma.
            not_tags = [t for t in tag if t not in all_tags]
            if len(not_tags) > 0:
                self.lemma = not_tags[0]
            else:
                self.lemma = tag[0]
        else:
            self.lemma = lemma

        self.pos = self.tag['pos']
        self.tag_raw = tag

    def __init__(self, tag=[''], _input=False, tool=False, tagsets={}):
        self.tagsets = tagsets
        self.tool = tool

        self.prepare_tag(tag, tagsets)

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
        return (self.lemma, self.pos, self.tool.formatTag(self.tag_raw))

    def __repr__(self):
        _lem, _pos, _tag = self.__key()
        _lem = unicode(_lem).encode('utf-8')
        _pos = unicode(_pos).encode('utf-8')
        _tag = unicode(_tag).encode('utf-8')
        f = unicode(self.form).encode('utf-8')
        cls = self.__class__.__name__
        return '<%s: %s, %s, %s, %s>' % (cls, f, _lem, _pos, _tag)

    def __init__(self, *args, **kwargs):

        super(GeneratedForm, self).__init__(*args, **kwargs)
        self.form = self.input


def word_generation_context(generated_result, *generation_input_args,
                            **generation_kwargs):
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

    node = generation_input_args[2]

    if len(node) == 0:
        return generated_result

    context = node.xpath('.//l/@context')

    if len(context) > 0:
        context = context[0]
    else:
        context = None

    def apply_context(form):
        #        tag, forms = form

        # trigger different tuple lengths and adjust the entities
        #([u'viessat', u'V', u'Ind', u'Prt', u'Pl1'], [u'viesaimet'])
        # ==>  (u'viessat', [u'V', u'Ind', u'Prt', u'Pl1'], [u'viesaimet'])

        # fix for the bug 2406
        if len(form) == 2:
            tmp_tag, tmp_forms = form
            tmp_lemma = tmp_tag[0]
            tmp_tag = tmp_tag[1:len(tmp_tag)]
            form = (tmp_lemma, tmp_tag, tmp_forms)

        lemma, tag, forms = form

        tag = '+'.join(tag)

        # Get the context, but also fall back to the None option.
        context_formatter = context_for_tags.get(
            (context, tag),
            context_for_tags.get((None, tag), False),
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

        return (tag, formatted_forms)

    return map(apply_context, generated_result)


class GenerationOverrides(object):
    """ Class for collecting functions marked with decorators that
    provide special handling of tags. One class instantiated in
    morphology module: `generation_overrides`.

    #>> @generation_overrides.tag_filter_for_iso('sme')
    #>> def someFunction(form, tags, xml_node):
    #>>     ... some processing on tags, may be conditional, etc.
    #>>     return form, tags, xml_node

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
            raw = input_kwargs.get('return_raw_data', False)
            if raw:
                generated_forms, stdout, stderr = function(
                    *input_args, **input_kwargs)
            else:
                generated_forms = function(*input_args, **input_kwargs)
            for f in self.postgeneration_processors[lang_code]:
                generated_forms = f(generated_forms, *input_args,
                                    **input_kwargs)
            for f in self.postgeneration_processors['all']:
                input_kwargs['language'] = lang_code
                if f not in self.postgeneration_processors[lang_code]:
                    generated_forms = f(generated_forms, *input_args,
                                        **input_kwargs)
            if raw:
                return generated_forms, stdout, stderr
            else:
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
                generated_forms = f(generated_forms, *input_args,
                                    **input_kwargs)
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
                self.postanalyzers_doc[language_iso].append(
                    (postanalysis_function.__name__,
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
                self.pregenerators[
                    language_iso] = pregenerated_selector_function
                self.pregenerators_doc[language_iso] = [
                    (pregenerated_selector_function.__name__,
                     pregenerated_selector_function.__doc__)
                ]
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
                    (restrictor_function.__name__,
                     restrictor_function.__doc__))
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

        self.registry = defaultdict(list)
        self.tag_filter_doc = defaultdict(list)
        self.pregenerators = defaultdict(list)
        self.pregenerators_doc = defaultdict(list)
        self.postanalyzers = defaultdict(list)
        self.postanalyzers_doc = defaultdict(list)

        self.postgeneration_processors = defaultdict(list)
        self.postgeneration_processors['all'] = [word_generation_context]

        self.postgeneration_processors_doc = defaultdict(list)


generation_overrides = GenerationOverrides()


class XFST(object):
    def splitTagByCompound(self, analysis):
        _cmp = self.options.get('compoundBoundary', False)
        if _cmp:
            #analysis_split = analysis.split(_cmp)
            #if 'Cmp' in analysis:
            #    last_analysis = analysis_split[len(analysis_split)-1]
            #    analysis_split[len(analysis_split)-1] = last_analysis+'+DCmp'
            return analysis.split(_cmp)
            #return analysis_split
        else:
            return [analysis]

    def splitTagByString(self, analysis, tag_input):
        def splitTag(item, tag_string):
            if tag_string in item:
                res = []
                while tag_string in item:
                    fa = re.findall(tag_string, item)
                    if len(fa) == 1:
                        res.append(item[0:item.find("+" + tag_string)])
                        res.append(
                            item[item.find("+" + tag_string) + 1:len(item)])
                        break
                    else:
                        result = item[0:item.find("+" + tag_string)]
                        result2 = item[item.find("+" + tag_string) +
                                       1:len(item)]
                        res.append(result)
                        item = result2
                myres_array.append(res)
            else:
                myres_array.append(item)
            return

        global myres_array
        myres_array = []
        if isinstance(analysis, list):
            for var in analysis:
                splitTag(var, tag_input)
        else:
            splitTag(analysis, tag_input)

        fin_res = []
        for item in myres_array:
            if isinstance(item, list):
                for var in item:
                    fin_res.append(var)
            else:
                fin_res.append(item)
        return fin_res

    def tag_processor(self, analysis_line):
        """ This is a default tag processor which just returns the
        wordform separated from the tag for a given line of analysis.

        You can write a function to replace this for an individual
        morphology by adding it to a file somewhere in the PYTHONPATH,
        and then setting the Morphology option `tagProcessor` to this path.

        Ex.)

            Morphology:
              crk:
                options:
                  tagProcessor: "configs/language_specific_rules/file.py:function_name"

        Note the colon. It may also be a good idea to write some tests
        in the docstring for that function. If these are present they
        will be quickly tested on launch of the service, and failures
        will prevent launch.

        A tag processor must accept a string as input, and return a
        tuple of the wordform and processed tag. You may do this to for
        example, re-order tags, or relabel them, but whateve the output
        is, it must be a string.

        Ex.)

            'wordform\tlemma+Tag+Tag+Tag'

            ->

            ('wordform', 'lemma+Tag+Tag+Tag')

        """

        wordform, lemma_tags = analysis_line.split('\t')[:2]

        return (wordform, lemma_tags)

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
                (lemma, analysis) = self.tag_processor(part)
                lemmas.append(lemma)
                analyses.append(analysis)

            lemma = list(set(lemmas))[0]

            append_ = (lemma, analyses)
            cleaned.append(append_)

        return cleaned

    @cache.memoize(60 * 5)
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

        try:
            lookup_proc = subprocess.Popen(
                cmd.split(' '),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        except OSError:
            raise Exception(
                "Error executing lookup command for this request, confirm that lookup utilities and analyzer files are present."
            )
        except Exception, e:
            raise Exception("Unhandled exception <%s> in lookup request" % e)

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

    def load_tag_processor(self):
        import sys

        # import doctest

        print >> sys.stdout, "Loading the tag processor."

        _path = self.options.get('tagProcessor')
        module_path, _, from_list = _path.partition(':')

        try:
            mod = imp.load_source('.', os.path.join(configs_path, module_path))
        except:
            sys.exit("Unable to import <%s>" % module_path)

        try:
            func = mod.__getattribute__(from_list)
        except:
            sys.exit(
                "Unable to load <%s> from <%s>" % (from_list, module_path))

        self.tag_processor = func

    def __init__(self, lookup_tool, fst_file, ifst_file=False, options={}):
        self.cmd = "%s -flags mbTT %s" % (lookup_tool, fst_file)
        self.options = options

        if ifst_file:
            self.icmd = "%s -flags mbTT %s" % (lookup_tool, ifst_file)
        else:
            self.icmd = False

        if 'tagProcessor' in self.options:
            self.load_tag_processor()

    def applyMorph(self, morph):
        morph.tool = self
        self.logger = morph.logger
        return morph

    def lookup(self, lookups_list, raw=False):
        lookup_string = '\n'.join(lookups_list)
        output, err = self._exec(lookup_string, cmd=self.cmd)
        if len(output) == 0 and len(err) > 0:
            name = self.__class__.__name__
            msg = """%s - %s: %s""" % (self.langcode, name, err)
            self.logger.error(msg.strip())
        if raw:
            return self.clean(output), output, err
        return self.clean(output)

    def inverselookup_by_string(self, lookup_string, raw=False):
        import sys
        if not self.icmd:
            print >> sys.stderr, " * Inverse lookups not available."
            return False

        output, err = self._exec(lookup_string, cmd=self.icmd)
        if raw:
            return self.clean(output), output, err

        return self.clean(output)

    def inverselookup(self,
                      lemma,
                      tags,
                      raw=False,
                      no_preprocess_paradigm=False):

        # Some templates (namely those where there are tags before
        # the lemma), will cause problems. Thus if the lemma is
        # already in the tag, we consider this to be a completed tag
        # string for generation. Otherwise, prefix the lemma then
        # send to generation.
        #
        if not no_preprocess_paradigm:
            lookups_list = []
            for tag in tags:
                if lemma in tag:
                    combine = self.splitAnalysis(tag, inverse=True)
                else:
                    combine = [lemma] + self.splitAnalysis(tag, inverse=True)
                lookups_list.append(self.formatTag(combine))
            lookup_string = '\n'.join(lookups_list)
        else:
            lookup_string = tags + '\n'
        return self.inverselookup_by_string(lookup_string, raw=raw)

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


class HFST(XFST):
    def __init__(self, lookup_tool, fst_file, ifst_file=False, options={}):
        self.cmd = "%s %s" % (lookup_tool, fst_file)
        self.options = options

        if ifst_file:
            self.icmd = "%s %s" % (lookup_tool, ifst_file)
        else:
            self.icmd = False

        if 'tagProcessor' in self.options:
            self.load_tag_processor()


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
        # TODO: occasionally lemma is not lemma, but first part of a
        # tag, need to fix with the tagsets
        def make_lemma(r):
            lems = []

            tag, forms = r
            if isinstance(forms, list):
                for f in forms:
                    lem = GeneratedForm(
                        tag, _input=f, tool=self.tool, tagsets=self.tagsets)
                    lems.append(lem)
            else:
                lems = []
            return lems

        generate_out, stdin, stderr = self.generate(*args, **kwargs)
        generated = sum(map(make_lemma, generate_out), [])

        return_raw_data = kwargs.get('return_raw_data', False)
        if return_raw_data:
            return generated, stdin, stderr
        else:
            return generated

    def generate(self, lemma, tagsets, node=None, pregenerated=None, **kwargs):
        """ Run the lookup command, parse output into
            [(lemma, ['Verb', 'Inf'], ['form1', 'form2'])]

            If pregenerated, we pass the forms in using the same
            structure as the analyzed output. The purpose here is that
            pregenerated forms in lexicon may differ from language to
            language, and we want to allow processing for that to occur
            elsewhere.

            TODO: cache pregenerated forms, return them.

        """

        return_raw_data = kwargs.get('return_raw_data', False)
        no_preprocess_paradigm = kwargs.get('no_preprocess_paradigm', False)

        # tagsets as passed in include the lemma and do not require
        # preprocessing to add it in
        # if no_preprocess_paradigm:

        if len(node) > 0:
            key = self.generate_cache_key(lemma, tagsets, node)
        else:
            key = self.generate_cache_key(lemma, tagsets)

        stdout_key = key + 'stdout'
        stderr_key = key + 'stderr'

        _is_cached = self.cache.get(key)

        if _is_cached:
            if return_raw_data:
                cache_stdout = self.cache.get(stdout_key)
                cache_stderr = self.cache.get(stdout_key)
                if cache_stdout is None: cache_stdout = 'no cache data'
                if cache_stderr is None: cache_stderr = 'no cache data'
                return _is_cached, 'stdout cached: ' + cache_stdout, 'stderr cached: ' + cache_stderr
            else:
                return _is_cached

        # TODO: cache
        if pregenerated:
            _is_cached = self.cache.set(key, pregenerated)
            if return_raw_data:
                return pregenerated, 'pregenerated', ''
            else:
                return pregenerated

        if return_raw_data:
            res, raw_output, raw_errors = self.tool.inverselookup(
                lemma,
                tagsets,
                raw=True,
                no_preprocess_paradigm=no_preprocess_paradigm)
        else:
            res = self.tool.inverselookup(
                lemma, tagsets, no_preprocess_paradigm=no_preprocess_paradigm)
            raw_output = ''
            raw_errors = ''

        reformatted = []
        tag = False
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
                reformatted.append((self.tool.splitAnalysis(tag, inverse=True),
                                    forms))
            else:
                parts = self.tool.splitAnalysis(tag, inverse=True)
                forms = False
                reformatted.append((parts, forms))

        # Log generation error:
        if len(reformatted) == 0:

            logg_args = [
                'GENERATE',
                self.langcode,
                tag or '',
            ]

            if len(tagsets) > 0:
                _tagsets = ','.join(['+'.join(t) for t in tagsets])
            else:
                _tagsets = ''
            logg_args.append(_tagsets)

            if 'extra_log_info' in kwargs:
                _extra_log_info = kwargs.pop('extra_log_info')
                extra_log_info = ', '.join([
                    "%s: %s" % (k, v)
                    for (k, v) in _extra_log_info.iteritems()
                ])
                extra_log_info = extra_log_info.encode('utf-8')
                logg_args.append(extra_log_info)

            logg = "\t".join([a for a in logg_args if a])
            self.logger.error(logg.strip())

        _is_cached = self.cache.set(key, reformatted)
        _is_cached_out = self.cache.set(stdout_key, raw_output)
        _is_cached_ert = self.cache.set(stderr_key, raw_errors)

        if return_raw_data:
            return reformatted, raw_output, raw_errors
        else:
            return reformatted

    # TODO: option, or separate function to also return discarded to
    # find out what's been removed to hide more_info link
    def lemmatize(self,
                  form,
                  split_compounds=False,
                  non_compound_only=False,
                  no_derivations=False,
                  return_raw_data=False):
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

        #If the user input is lexicalized then put it as the first element in analyses
        def check_if_lexicalized(array):
            found = False
            for i in range(0, len(array)):
                if form in array[i]:
                    array.insert(0, array[i])
                    del array[i + 1]
                    found = True
                    break
            if found:
                return array
            else:
                #If the user input is not in the base form, the for above doesn't find the analyses
                #so find the longest analyses and put it/them in the first/s element/s
                #in analyses if it is not one of the single parts
                mystr = []
                indmax = []
                for i in range(0, len(array)):
                    mystr.append(len(array[i][0:array[i].find("+")]))
                indmax = [i for i, j in enumerate(mystr) if j == max(mystr)]
                if (max(mystr) < len(form)):
                    k = 0
                    for i in range(0, len(indmax)):
                        array.insert(k, array.pop(indmax[i]))
                        k += 1
                return array

        if return_raw_data:
            lookups, raw_output, raw_errors = self.tool.lookup([form],
                                                               raw=True)
        else:
            lookups = self.tool.lookup([form])

        # Check for unknown

        unknown = False
        for k, v in lookups:
            for a in v:
                if '?' in a:
                    unknown = True

        if unknown:
            if return_raw_data:
                return False, raw_output, raw_errors
            else:
                return False

        #lemmas = set()
        #Use list() instead of set() to keep original order
        lemmas = list()
        ##lemmas_r = list()

        for _form, analyses in lookups:

            if non_compound_only:
                analyses = maybe_filter(remove_compound_analyses, analyses)

            if no_derivations:
                analyses = maybe_filter(remove_derivations, analyses)

            #Introduce the variable 'analyses_right' because in some cases when Der/ tags
            # we want to show only specific analyses and not all
            ##analyses_right = analyses
            analyses_der = analyses
            #In case of multiple analyses with different types of Der we need to keep them all
            #so in each case we append the results
            #(probably no need for all these variables, so maybe TODO: clean)
            ##analyses_right_fin = []
            analyses_der_fin = []

            analyses = check_if_lexicalized(analyses)
            cnt = []
            for item in analyses:
                cnt.append(item.count('Der'))
            cnt_orth = []
            for item in analyses:
                cnt_orth.append(item.count('Err/Orth'))
            import heapq
            if (min(cnt_orth) == 0
                    and max(cnt_orth) == 1) or (min(cnt_orth) == 0
                                                and max(cnt_orth) == 0):
                if len(cnt) > 1 and min(cnt) == 0 and heapq.nsmallest(
                        2, cnt)[-1] != 0:
                    analyses = [
                        analyses[cnt.index(min(cnt))], analyses[cnt.index(
                            heapq.nsmallest(2, cnt)[-1])]
                    ]
                else:
                    if min(cnt) != 0:
                        analyses = [analyses[cnt.index(min(cnt))]]
            else:
                if (min(cnt_orth) == 1 and max(cnt_orth) == 1):
                    analyses = analyses
            if split_compounds:
                analyses = sum(map(self.tool.splitTagByCompound, analyses), [])
            tags = ('Der', 'VAbess', 'VGen', 'Ger', 'Comp', 'Superl')
            an_split = []
            for item in analyses:
                an_split.append(item.split('+'))
            k = 0
            for item in an_split:
                index = []
                if_tags = False
                for i in range(0, len(item)):
                    if item[i].startswith(tags):
                        index.append(i)
                        if_tags = True
                s = '+'
                b = []
                if not if_tags:
                    b.append(analyses[k])
                else:
                    for i in range(len(index)):
                        if i == 0:
                            b.append(s.join(item[0:index[i]]))
                        else:
                            b.append(s.join(item[index[i - 1]:index[i]]))
                        if i == len(index) - 1:
                            b.append(s.join(item[index[i]:len(item)]))
                k += 1
                analyses_der_fin.append(b)

            def fix_nested_array(nested_array):
                not_nested_array = []
                if len(nested_array) != 0:
                    if isinstance(nested_array[0], list):
                        for item in nested_array:
                            if len(item) > 1:
                                for var in item:
                                    not_nested_array.append(var)
                            else:
                                not_nested_array.append(item[0])
                else:
                    not_nested_array = analyses
                return not_nested_array

            #Fix in case analyses_der_fin and analyses_right_fin are nested arrays
            array_not_nested = fix_nested_array(analyses_der_fin)

            def remove_duplicates(array_var):
                newlist = []
                for item in array_var:
                    if item not in newlist:
                        newlist.append(item)
                return newlist

            #Remove duplicates due to append if entry with analyses or not (in collect_same_lemma in morpho_lexicon.py)
            analyses_der_fin = remove_duplicates(array_not_nested)
            ##analyses_right_fin = analyses_der_fin

            for analysis in analyses_der_fin:
                # TODO: here's where to begin solving finding a lemma
                # from:
                # PV/maci+PV/pwana+nipâw+V+AI+Ind+Prs+1Sg
                _an_parts = self.tool.splitAnalysis(analysis)

                # If a word doesn't have a PoS in an analysis, we try to
                # handle it as best as possible.
                if len(_an_parts) == 1:
                    _lem = _an_parts[0]
                    lem = Lemma(
                        _an_parts,
                        _input=_lem,
                        tool=self.tool,
                        tagsets=self.tagsets)
                else:
                    lem = Lemma(
                        _an_parts,
                        _input=form,
                        tool=self.tool,
                        tagsets=self.tagsets)
                #lemmas.add(lem)
                lemmas.append(lem)
            ##
            '''for analysis_r in analyses_right_fin:
                # TODO: here's where to begin solving finding a lemma
                # from:
                # PV/maci+PV/pwana+nipâw+V+AI+Ind+Prs+1Sg
                _an_parts = self.tool.splitAnalysis(analysis_r)

                # If a word doesn't have a PoS in an analysis, we try to
                # handle it as best as possible.
                if len(_an_parts) == 1:
                    _lem = _an_parts[0]
                    lem = Lemma(_an_parts, _input=_lem, tool=self.tool, tagsets=self.tagsets)
                else:
                    lem = Lemma( _an_parts
                               , _input=form
                               , tool=self.tool, tagsets=self.tagsets
                               )
                #lemmas.add(lem)
                lemmas_r.append(lem)'''##

        if return_raw_data:
            ##return list(lemmas), raw_output, raw_errors, list(lemmas_r)
            return list(lemmas), raw_output, raw_errors
        else:
            ##return list(lemmas), list(lemmas_r)
            return list(lemmas)

    def de_pickle_lemma(self, lem, tag):
        _tag = self.tool.splitAnalysis(tag)
        lem = Lemma(
            lem, '', _tag, fulltag=_tag, tool=self.tool, tagsets=self.tagsets)
        return lem

    def generate_cache_key(self, lemma, generation_tags, node=False):
        """ key is something like generation-LANG-nodehash-TAG|TAG|TAG
        """
        import hashlib
        if type(generation_tags) == list:
            _cache_tags = '|'.join(['+'.join(a) for a in generation_tags])
        else:
            _cache_tags = generation_tags

        _cache_key = hashlib.md5()
        _cache_key.update('generation-%s-' % self.langcode)
        _cache_key.update(lemma.encode('utf-8'))
        if node is not None:
            if len(node) > 0:
                node_hash = node.__hash__()
                _cache_key.update(str(node_hash))
        _cache_key.update(_cache_tags.encode('utf-8'))
        return _cache_key.hexdigest()

    def __init__(self, languagecode, tagsets={}, cache=False):
        self.langcode = languagecode

        self.generate = generation_overrides.apply_pregenerated_forms(
            languagecode, self.generate)
        self.generate = generation_overrides.restrict_tagsets(
            languagecode, self.generate)
        self.generate = generation_overrides.process_generation_output(
            languagecode, self.generate)

        self.lemmatize = generation_overrides.process_analysis_output(
            languagecode, self.lemmatize)

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
