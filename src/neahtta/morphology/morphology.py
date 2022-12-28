#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Morphological tools
"""
from __future__ import absolute_import
from __future__ import print_function
import heapq
import imp
import os
import re
from xmlrpc.client import TRANSPORT_ERROR
from six import iteritems
from termcolor import colored

from cache import cache

try:
    unicode
except NameError:
    unicode = str

try:
    import hfst
except ModuleNotFoundError as e:
    HAVE_PYHFST = False
else:
    HAVE_PYHFST = True

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
            except Exception as e:
                print(self._t)
                raise e

    def __unicode__(self):
        return self.val

    def __repr__(self):
        return self.val

    def __hash__(self):
        return hash(self._t)

    def __eq__(self, other):
        if self.regex:
            m = self._re.match(other)
            return m is not None
        else:
            return self.val == other


class Tagset(object):
    def __init__(self, name, members):
        self.name = name
        self.members = list(map(TagPart, members))

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
        for name, tags in iteritems(self.set_definitions):
            tagset = Tagset(name, tags)
            self.set(name, tagset)

    def get(self, name):
        return self.sets.get(name, False)

    def __getitem__(self, key):
        return self.get(key)

    def set(self, name, tagset):
        self.sets[name] = tagset

    def all_tags(self):
        list_of_lists = [list(v.members) for k, v in iteritems(self.sets)]
        flattened_list = list(item for sublist in list_of_lists for item in sublist)
        _all = list(set(flattened_list))
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
        actio = False
        if "Actio+" in tag:
            lemma = tag
            self.lemma = lemma
            actio = True
            self.pos = ""
            self.tag_raw = [tag]
        else:
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

        if not actio:
            try:
                self.pos = self.tag['pos']
            except:
                self.tag.encode('utf-8')
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
        # Letting pos be None is problematic when sorting or grouping by pos
        if self.pos is None:
            if tagsets['verb_derivations'] and self.lemma in tagsets['verb_derivations']:
                # e.g. VAbess does not have a marked pos
                self.pos = 'V'
            else:
                self.pos = "Unknown"
                error_msg = "No part of speech found for lemma \"{}\". Make sure it is listed in the appropriate tagset file".format(self.lemma)
                print(colored(error_msg,"yellow"), flush=True)
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

    return list(map(apply_context, generated_result))


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
                print('%s overrides: registered post-analysis processor - %s' % \
                      ( language_iso
                      , postanalysis_function.__name__
                      ))

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
                print('%s overrides: registered static paradigm selector - %s' % \
                      ( language_iso
                      , pregenerated_selector_function.__name__
                      ))

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
                print('%s overrides: registered pregeneration tag filterer - %s' %\
                      ( language_iso
                      , restrictor_function.__name__
                      ))

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
                print('%s overrides: registered entry context formatter - %s' %\
                      ( language_iso
                      , restrictor_function.__name__
                      ))

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
        is_cmp = False
        if _cmp:
            # in order to obtain a better display for compounds a "dummy" tag is needed for the last part of the analysis
            # Check if "Cmp" tag and if yes, split analysis and add u'\u24D2'(= ⓒ ) to last part
            # If the last part of the analysis contains "Der" tag, split it and add u'\u24D3'(= ⓓ ) to the first part and
            # u'\u24DB' (= ⓛ ) to the last part
            # Ex_1: miessemánnofeasta
            #   analysis_1 u'miessem\xe1nnu+N+Cmp/SgNom+Cmp#feasta+N+Sg+Nom'
            #   becomes: u'miessem\xe1nnu+N+Cmp/SgNom', u'feasta+N+Sg+Nom+\u24d2'
            # Ex_2: musihkkaalmmuheapmi
            #   analysis_1 = u'musihkka+N+Cmp/SgNom+Cmp#almmuheapmi+N+Sg+Nom'
            #   becomes = u'musihkka+N+Cmp/SgNom', u'almmuheapmi+N+Sg+Nom+\u24d2'
            #   analysis_2 = u'musihkka+N+Cmp/SgNom+Cmp#almmuhit+V+TV+Der/NomAct+N+Sg+Nom'
            #   becomes = u'musihkka+N+Cmp/SgNom', u'almmuhit+V+TV+\u24d3+Der/NomAct+N+Sg+Nom+\u24db'
            if 'Cmp' in analysis:
                is_cmp = True
            if isinstance(_cmp, list):
                for item in _cmp:
                    if item in analysis:
                        analysis = analysis.split(item)
                        if is_cmp:
                            last_analysis = analysis[len(analysis)-1]
                            analysis[len(analysis)-1] = last_analysis + '+' + u'\u24D2'
                            if 'Der' in last_analysis:
                                ind_der = last_analysis.find('Der')
                                analysis[len(analysis)-1] = last_analysis[0:ind_der] + u'\u24D3' + '+' + last_analysis[ind_der:] + '+' + u'\u24DB'
                if isinstance(analysis, list):
                    return analysis
                else:
                    return [analysis]
            else:
                analysis = analysis.split(_cmp)
                if is_cmp:
                    last_analysis = analysis[len(analysis)-1]
                    analysis[len(analysis)-1] = last_analysis + '+' + u'\u24D2'
                    if 'Der' in last_analysis:
                        ind_der = last_analysis.find('Der')
                        analysis[len(analysis)-1] = last_analysis[0:ind_der] + u'\u24D3' + '+' + last_analysis[ind_der:] + '+' + u'\u24DB'
                return analysis
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

        weight = []
        try:
            wordform, lemma_tags, weight = analysis_line.split('\t')[:3]
        except:
            wordform, lemma_tags = analysis_line.split('\t')[:2]

        if '?' in analysis_line:
            lemma_tags += '\t+?'

        if weight:
            return (wordform, lemma_tags, weight)
        else:
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
            weights = []
            updated_lemmas = []

            for part in chunk.split('\n'):
                try:
                    (lemma, analysis, weight) = self.tag_processor(part)
                except:
                    (lemma, analysis) = self.tag_processor(part)
                lemmas.append(lemma)
                analyses.append(analysis)
                try:
                    weights.append(weight)
                except:
                    print("not using weights")

            lemma = list(set(lemmas))[0]

            append_ = (lemma, analyses, weights)
            cleaned.append(append_)

        return cleaned

    @cache.memoize(60 * 5)
    def _exec(self, _input, cmd, timeout=5):
        """ Execute a process, but kill it after 5 seconds. Generally
        we expect small things here, not big things.
        """
        import subprocess
        from threading import Timer

        print(f"_exec(), {cmd=}", flush=True)

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
        except Exception as e:
            raise Exception("Unhandled exception <%s> in lookup request" % e)

        def kill_proc(proc=lookup_proc):
            try:
                proc.kill()
                raise Exception("Process for %s took too long." % cmd)
            except OSError:
                pass

        if not timeout:
            t = Timer(5, kill_proc)
            t.start()

        output, err = lookup_proc.communicate(_input)

        if output is not None:
            try:
                output = output.decode('utf-8')
            except:
                pass

        if err is not None:
            try:
                err = err.decode('utf-8')
            except:
                pass

        return (output, err)

    def load_tag_processor(self):
        import sys

        # import doctest

        print("Loading the tag processor.", file=sys.stdout)

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
        print("lookup()", flush=True)
        lookup_string = '\n'.join(lookups_list)

        print(f"{lookup_string=}", flush=True)
        output, err = self._exec(lookup_string, cmd=self.cmd)
        print(f"{output=}", flush=True)
        print(f"{err=}", flush=True)
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
            print(" * Inverse lookups not available.", file=sys.stderr)
            return False

        output, err = self._exec(lookup_string, cmd=self.icmd)
        if raw:
            return self.clean(output), output, err

        return self.clean(output)

    def inverselookup(self, lemma, tags, raw=False,
                      no_preprocess_paradigm=False):
        """Do an inverse lookup."""
        if not no_preprocess_paradigm:
            lookup_string = self.get_inputstring(lemma, tags)
        else:
            lookup_string = tags

        return self.inverselookup_by_string(lookup_string, raw=raw)

    def get_inputstring(self, lemma, tags):
        """Make inputstring for inverselookup_by_string.

        Some templates (namely those where there are tags before the lemma),
        will cause problems. Thus if the lemma is  already in the tag, we
        consider this to be a completed tag string for generation. Otherwise,
        prefix the lemma then send to generation.
        """
        lookups_list = []
        for tag in tags:
            if lemma in tag:
                combine = self.splitAnalysis(tag, inverse=True)
            else:
                combine = [lemma] + self.splitAnalysis(tag, inverse=True)
            lookups_list.append(self.formatTag(combine))

        return '\n'.join(lookups_list)


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
        if "Actio+" in parts:
            tag = parts
            return Tag(tag, delim, tagsets=tagsets)
        else:
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
        print(f"HFST.__init__({lookup_tool=}, {fst_file=})", flush=True)
        self.cmd = "%s %s" % (lookup_tool, fst_file)
        self.options = options

        if ifst_file:
            self.icmd = "%s %s" % (lookup_tool, ifst_file)
        else:
            self.icmd = False

        if 'tagProcessor' in self.options:
            self.load_tag_processor()


class PyHFST(XFST):
    def __new__(cls, *args, **kwargs):
        if not HAVE_PYHFST:
            from textwrap import dedent
            msg = dedent(f"""
                warning: pyhfst morphology tool requires python hfst package,
                (pip install hfst)
                  (just note when you do: it takes a while to compile, and you may
                   need some libraries and such...)
                falling back to HFST
            """)
            print(msg, flush=True)
            return HFST(*args, **kwargs)

    def __init__(self, lookup_tool, fst_file, ifst_file=None, options={}):
        self.options = options
        print("ABOUT TO USE PYHFST!", flush=True)


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
        generated = sum(list(map(make_lemma, generate_out)), [])

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

        idxs = []
        for tag, forms, weights in res:
            indexes = []
            indexes = [i for i, x in enumerate(weights) if x == min(weights)]
            idxs.append(indexes)
        updated_res = []
        for i in range(0, len(idxs)):
            #if not using weights idxs is an array of empty arrays
            forms = []
            new_res = []
            for idx in idxs[i]:
                forms.append(res[i][1][idx])
                new_res = (res[i][0], forms)
            if new_res:
                updated_res.append(new_res)
            else:
                updated_res.append([res[i][0], res[i][1]])

        for tag, forms in updated_res:
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
                    for (k, v) in iteritems(_extra_log_info)
                ])
                extra_log_info = extra_log_info
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

    # start: morph_lemmatizer internal functions
    def remove_compound_analyses(self, analyses, non_compound_only):
        cmp = self.tool.options.get('compoundBoundary', False)
        if non_compound_only and cmp:
            return [analysis for analysis in analyses if cmp not in analysis]

        return analyses

    def remove_derivations(self, analyses, no_derivations):
        der = self.tool.options.get('derivationMarker', False)
        if no_derivations and der:
            return [analysis for analysis in analyses if der not in analysis]

        return analyses

    @staticmethod
    def maybe_filter(function, iterable):
        return list(filter(function, iterable))

    # If the user input is lexicalized then put it as the first element in analyses
    @staticmethod
    def check_if_lexicalized(form, array):
        for index in range(0, len(array)):
            if form == array[index].split("+")[0]:
                array.insert(0, array[index])
                del array[index + 1]
                return array
        else:
            # If the user input is not in the base form, the for above doesn't find the analyses
            # so find the longest analyses and put it/them in the first/s element/s
            # in analyses if it is not one of the single parts
            mystr = [
                len(array[index][0:array[index].find("+")])
                for index in range(0, len(array))
            ]
            indmax = [index for index, j in enumerate(mystr) if j == max(mystr)]
            if (max(mystr) <= len(form)):
                index2 = 0
                for index in range(0, len(indmax)):
                    array.insert(index2, array.pop(indmax[index]))
                    index2 += 1
            return array

    @staticmethod
    def fix_nested_array(nested_array, analyses):
        if not nested_array:
            return analyses

        if isinstance(nested_array[0], list):
            return [var for item in nested_array for var in item]

        return []

    @staticmethod
    def remove_duplicates(array_var):
        newlist = []
        for item in array_var:
            if item not in newlist:
                newlist.append(item)
        return newlist

    # end: morph_lemmatizer internal functions

    def morph_lemmatize(self,
                  form,
                  split_compounds=False,
                  non_compound_only=False,
                  no_derivations=False,
                  return_raw_data=False):
        """ For a wordform, return a list of lemmas
        """

        lookups, raw_output, raw_errors = self.tool.lookup([form], raw=True)

        if self.has_unknown(lookups):
            if return_raw_data:
                return False, raw_output, raw_errors
            else:
                return False

        lemmas = [lemma
                  for lemma in self.lookups_to_lemma(form, lookups,
                                                     no_derivations,
                                                     non_compound_only,
                                                     split_compounds)]

        if return_raw_data:
            return list(lemmas), raw_output, raw_errors
        else:
            return list(lemmas)

    def lookups_to_lemma(self, form, lookups, no_derivations,
                         non_compound_only, split_compounds):
        for _, analyses, _ in lookups:
            analyses = self.remove_compound_analyses(analyses,
                                               non_compound_only)
            analyses = self.remove_derivations(analyses, no_derivations)

            analyses = self.check_if_lexicalized(form, analyses)
            analyses = self.rearrange_on_count(analyses)
            analyses = self.split_on_compounds(analyses, split_compounds)

            analyses_der_fin = self.make_analyses_der_fin(analyses)

            for analysis in analyses_der_fin:
                yield self.analysis_to_lemma(analysis, form)

    def analysis_to_lemma(self, analysis, wordform):
        analysis_parts = self.tool.splitAnalysis(analysis)
        lemma = ""
        if len(analysis_parts) == 1:
            if "Actio" in analysis_parts[0]:
                analysis_parts = ["Actio+"+analysis_parts[0].split("Actio")[1]]
                lemma = analysis_parts
        else:
            lemma = analysis_parts[0] if len(analysis_parts) == 1 else wordform
        return Lemma(
            analysis_parts, _input=lemma, tool=self.tool, tagsets=self.tagsets)

    def make_analyses_der_fin(self, analyses):
        analyses_der_fin = []
        tags = ('Der', 'VAbess', 'VGen', 'Ger', 'Comp', 'Superl', 'Actio')
        for analysis in analyses:
            if "Actio" in analysis:
                analysis = analysis.split("Actio")[0]+"Actio"+analysis.split("Actio+")[1]
            analysis_parts = analysis.split('+')
            index = [index1 for index1, part in enumerate(analysis_parts[1:], start=1)
                     if part.startswith(tags)]
            s = '+'
            b = []
            if index:
                b.append(s.join(analysis_parts[:index[0]]))
                for previous, current in zip(index, index[1:]):
                    b.append(s.join(analysis_parts[previous:current]))
                b.append(s.join(analysis_parts[index[-1]:len(analysis_parts)]))
            else:
                b.append(analysis)

            analyses_der_fin.extend(b)

        # Remove duplicates due to append if entry with analyses or not (in collect_same_lemma in morpho_lexicon.py)
        return  self.remove_duplicates(analyses_der_fin)

    def split_on_compounds(self, analyses, split_compounds):
        if split_compounds:
            analyses = sum(list(map(self.tool.splitTagByCompound, analyses)), [])
        return analyses

    @staticmethod
    def rearrange_on_count(analyses):
        errorth_count = [analysis.count('Err/Orth') for analysis in analyses]

        if (min(errorth_count) == 0
            and max(errorth_count) == 1) or (min(errorth_count) == 0
                                        and max(errorth_count) == 0):
            der_count = [analysis.count('Der') for analysis in analyses]
            if len(der_count) > 1 and min(der_count) == 0 and heapq.nsmallest(
                    2, der_count)[-1] != 0:
                analyses = [
                    analyses[der_count.index(min(der_count))], analyses[der_count.index(
                        heapq.nsmallest(2, der_count)[-1])]
                ]
            else:
                if (min(errorth_count) == 0
                    and max(errorth_count) == 0 and not max(der_count) > 1):
                    analyses = analyses
                elif min(der_count) != 0:
                    analyses = [analyses[der_count.index(min(der_count))]]
                elif (min(errorth_count) == 0
                    and max(errorth_count) > 0):
                    idx = [i for i, x in enumerate(errorth_count) if x == 0]
                    analyses = [analyses[item] for item in idx]
        else:
            if (min(errorth_count) == 1 and max(errorth_count) == 1):
                analyses = analyses
        return analyses

    def has_unknown(self, lookups):
        return not all(['?' not in analysis for _, analyses,_ in lookups
                       for analysis in analyses])

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
        genstr = 'generation-%s-' % self.langcode
        _cache_key.update(genstr.encode('utf-8'))
        _cache_key.update(lemma.encode('utf-8'))
        if node is not None:
            node_hash = node.__hash__()
            _cache_key.update(str(node_hash).encode('utf-8'))
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
            languagecode, self.morph_lemmatize)

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
