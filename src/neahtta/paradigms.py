# -*- encoding: utf-8 -*-
"""
Testing ideas:

This should not return +Oops

    morphology:
      pos: N
      possessive: PxSg2
      number: Pl
    lexicon:
      XPATH:
        sem_type: ".//l/@sem_type"
        nr: ".//l/@nr"
    --
    {{ lemma }}+N+Oops

Programmer documentation:

Overall explanation: when the ParadigmConfig object is instantiated, the
directory is processed, and all .paradigm files for the active languages
in the `app` are read. When they are read, the YAML half is parsed into
a class containing a list of functions that will be used to later test
word lookup results. If the test passes, then the second half, a jinja2
template, will be returned. Things that are matched in the YAML are able
to be used directly in the template. For a bigger description, see the
corresponding README.

Each part of the YAML half of a paradigm file is represented by one of
the following classes: TagRule, TagSetRule, LexRule, LexiconRuleSet. Of
all of these, LexiconRuleSet is more of the outlier, since XPATH
contexts must be processed first, before LexRule instances are created.
Otherwise, this should make it possible to more easily extend, if more
comparison types are needed (beyond X == Y and X is in list Y).

TODO: allow user-defined global XPATH context.
"""

import os, sys
import yaml
from lxml import etree
from paradigm_layouts import parse_table

__all__ = ['ParadigmConfig']

class TagRule(object):
    """ Compares a whole tag, either checking that it is contained in a
        list of tags, or equals a tag.
    """

    def __init__(self, tag):

        if isinstance(tag, str):
            tag = unicode(tag)

        self.tag = tag

        if isinstance(tag, str) or isinstance(tag, unicode):
            self.cmp = lambda x, y: (x == y, x)
        elif isinstance(tag, list):
            self.cmp = lambda x, y: (x in y, x)

    def compare(self, node, analyses):
        """ Compare takes analyses and node, and returns a boolean.
            Evaluation is such that `any` match in the analysis set is
            taken as the match for the overall value, i.e., some tag
            must match this rule for it to be True.

            Returns tuple (Truth, [Context]), where Truth is boolean,
            context is the successful matched context in tuple form,
            (key, matched_value).
        """

        evals = [ self.cmp(lemma.tag.tag_string, self.tag)
                     for lemma in analyses
                ]

        # Include what was matched.
        truth = any([t for t, c in evals])
        context = [('tag', c) for t, c in evals if t]

        return truth, context

class LexRule(object):

    def __init__(self, lex_key, lex_value):
        self.key = lex_key
        if isinstance(lex_value, str):
            tag = unicode(lex_value)
        self.value = lex_value

        if isinstance(lex_value, str) or isinstance(lex_value, unicode):
            self.cmp = lambda x, y: (x == y, x)
        elif isinstance(lex_value, list):
            self.cmp = lambda x, y: (x in y, x)

    def compare(self, node, analyses, xpath_context={}):
        """ Compare takes analyses and node, and returns a boolean.
            Evaluation is such that `any` match in the analysis set is
            taken as the match for the overall value, i.e., some tag
            must match this rule for it to be True.

            Returns tuple (Truth, [Context]), where Truth is boolean,
            context is the successful matched context in tuple form,
            (key, matched_value).
        """

        if xpath_context.get(self.key):
            truth, val = self.cmp(xpath_context[self.key], self.value)
        else:
            truth = False
            val = ''

        context = (self.key, val)

        return truth, context

# TODO: read from user defined file elsewhere
DEFAULT_RULES = {
    'lemma': ".//l/text()",
}

class LexiconRuleSet(object):
    """ This evaluates a context against lexicon nodes.
    """

    def __init__(self, lex_rules={}):
        self.comps = []
        self.lex_rules = lex_rules
        self.xpath = lex_rules.get('XPATH', {})
        self.xpath.update(DEFAULT_RULES)
        self.xpath_contexts = {}

        _str_norm = 'string(normalize-space(%s))'
        for k, v in self.xpath.iteritems():
            self.xpath_contexts[k] = etree.XPath(_str_norm % v)

        for k, v in lex_rules.iteritems():

            if k == 'XPATH':
                continue

            self.comps.append(LexRule(k, v))

    def extract_context(self, node):

        extracted_context = {}

        if node is not None:
            for k, v in self.xpath_contexts.iteritems():
                _v = v(node)
                if not _v:
                    _v = False
                extracted_context[k] = _v

        return extracted_context

    def compare(self, node, analyses):
        # Evaluation depends on XPATH stuff, so that needs to be run
        # first on the node, with additional potential rules

        # prepare xpath context
        # run comps with xpath_context
        if node is not None:
            xpath_context = self.extract_context(node)

            self._evals = [comp.compare(node, analyses, xpath_context) for comp in self.comps]

            truth = all([t for t, c in self._evals])
            contexts = [c for t, c in self._evals if t] + list(xpath_context.iteritems())

            return truth, contexts
        return (False, [])

class NullRule(object):
    def compare(self, node, analyses):
        return (False, [])


class TagSetRule(object):
    """ This rule compares a tagset, and looks to see if there are any
    matching results in the possible analyses.
    """

    def __init__(self, tagset, value):
        self.tagset = tagset
        if isinstance(value, unicode):
            value = unicode(value)
        self.tagset_value = value

        # in cmp functions
        # x = whatever value the tagset turns up (ex. 'Inf'), y = the
        # expected set of values that are defined in YAML
        if isinstance(value, str) or isinstance(value, unicode):
            self.cmp = lambda x, y: (x == y, x)
        elif isinstance(value, list):
            self.cmp = lambda x, y: (x in y, x)
        elif isinstance(value, bool):
            def _cmp(x, y):
                # when tag contains a value from this tagset, x is true,
                # otherwise x is None
                if x is None:
                    return (False, x)
                else:
                    return (True, x)
                return (False, x)
            self.cmp = _cmp

    def compare(self, node, analyses):

        evals = [ self.cmp(lemma.tag[self.tagset], self.tagset_value)
                     for lemma in analyses
                ]

        truth = any([t for t, c in evals])
        context = [(self.tagset, c) for t, c in evals if t]

        return truth, context

class ParadigmRuleSet(object):
    """ This is a rule set, which is defined by the first half of a
    paradigm file. It provides a way of turning the rule definition into
    an instance that can evaluate lexicon nodes and analyses. """

    # def __repr__(self):
    #     print self.rule_def
    #     return super(ParadigmRuleSet, self).__repr__()

    def __init__(self, rule_def, debug=False):
        """ .. py:function:: __init__(self, rule_def)

        Parses a python dict of the rule definition, and returns
        a function that returns True or False. Function takes analysis
        output, and xml nodes.

        :param dict rule_def: Parsed YAML rule definition
        """

        self.debug = debug

        self.rule_def = rule_def

        lex = rule_def.get('lexicon', False)
        morph = rule_def.get('morphology', )
        self.name = rule_def.get('name', 'NO NAME')

        # List of functions, for which all() must return True or False
        self.comps = []

        if not lex and not morph:
            print >> sys.stderr, "Missing morphology or lexicon rule context in <%s>" % self.name
            self.comps = [NullRule()]
            lex = {}
            morph = {}

        # Here are the special morphology things. All the rest of the keys
        # are tagsets
        if 'tag' in morph:
            self.comps.append(TagRule(morph.get('tag')))
            morph.pop('tag')

        if morph:
            for k, v in morph.iteritems():
                self.comps.append(TagSetRule(k, v))

        if lex:
            lex_rule = LexiconRuleSet(lex)
        else:
            lex_rule = LexiconRuleSet()
        self.comps.append(lex_rule)

    def evaluate(self, node, analyses, debug=False):
        """ Run all the comparators, and collect the context.
            Returns a tuple (Truth, Context); Context is a dict
        """

        if self.debug:
            print >> sys.stderr, analysis

        self._evals = [ comp.compare(node, analyses)
                        for comp in self.comps
                      ]

        truth = all([t for t, c in self._evals])
        contexts = [c for t, c in self._evals if t]

        context = dict(sum(contexts, []))
        if self.debug and truth:
            print >> sys.stderr, "Found matching paradigm in %s." % self.name

        return truth, context

class ParadigmConfig(object):
    """ A class for providing directory-based paradigm definitions.
    This class reads and parses the configs for the sets of languages
    available, and provides a general method for resolving the proper
    paradigm from dictionary entry nodes and morphological analyses. """

    def __init__(self, app=None, debug=False):
        self.debug = debug
        self._app = app
        self.read_paradigm_directory()

    def check_updates(self, language):
        updates = []
        for ind, paradigm_rule in enumerate(self.paradigm_layout_rules.get(language, [])):
            if os.path.getmtime(paradigm_rule.get('path')) != paradigm_rule.get('updated'):
                updates.append(ind)

        if len(updates) > 0:
            self.read_paradigm_directory()

    def get_paradigm_layout(self, language, node, analyses, debug=False, return_template=False, multiple=False):
        """ .. py:function:: get_paradigm(language, node, analyses)

        Render a paradigm layout if one exists for language.

        :param str language: The 3-character ISO for the language.
        :param lxml node: The lxml element for the <e /> node selected from a lookup
        :param list analyses: A list containing Lemma objects from a lookup.

        :return Table: the table object that can be used to fill in with generations

            table = paradigm_config.get_paradigm_layout(lang, node, analyses)
            filled_table = t.fill_generation(generated_paradigms)

        """
        from operator import itemgetter

        # Need to order possible matches by most extensive match, then
        # return that one.

        possible_matches = []

        self.check_updates(language)

        for paradigm_rule in self.paradigm_layout_rules.get(language, []):
            condition = paradigm_rule.get('condition')
            layout = paradigm_rule.get('template')
            _, _, path = paradigm_rule.get('path').partition('language_specific_rules')

            try:
                truth, context = condition.evaluate(node, analyses, debug=debug)
                if debug:
                    print >> sys.stderr, truth
                    print >> sys.stderr, context
            except Exception, e:
                print e
                print 'Exception in compiling rule or evaluating.'
                print '  ' + paradigm_rule.get('path')
                print '  node:'
                print node
                print '  analyses:'
                print analyses
                raise e

            # We have a match, so count how extensive it was.
            if truth:
                possible_matches.append(
                    (len(context.keys()), context, layout, path)
                )

        # Sort by count, and pick the first
        possible_matches = sorted(possible_matches, key=itemgetter(0), reverse=True)
        if debug:
            print >> sys.stderr, " - Possible matches: %d" % len(possible_matches)

        def paradigm_ordering((_c, _context, _layout, _path)):
            """ Sort by type if it exists, otherwise sort by
            alphabetical order of filename """
            _type = _layout.options.get('layout', {}).get('type', False)
            if _type:
                return _type
            else:
                return _path

        # def paradigm_ordering_cmp(a, b):
        #     print a
        #     print b
        #     if a in ['basic', 'simple']:
        #         return 0
        #     if b in ['basic', 'simple']:
        #         return 0
        #     return a > b

        if len(possible_matches) > 0:
            if multiple:
                _matches = []
                for _count, _context, _layout, _path in sorted(possible_matches, key=paradigm_ordering):
                    if return_template:
                        _matches.append((_layout, _path))
                    else:
                        _matches.append(_layout)
                # TODO: sort so that 'basic' and 'standard' etc are
                # first, then alphabetic order.
                return _matches
            else:
                count, context, layout, path = possible_matches[0]
                if debug:
                    print >> sys.stderr, context
                    print >> sys.stderr, path
                if return_template:
                    return layout, path
                else:
                    return layout

        if multiple:
            return False

        if return_template:
            return False, False
        else:
            return False

    def get_paradigm(self, language, node, analyses, debug=False, return_template=False):
        """ .. py:function:: get_paradigm(language, node, analyses)

        Render a paradigm if one exists for language.

        :param str language: The 3-character ISO for the language.
        :param lxml node: The lxml element for the <e /> node selected from a lookup
        :param list analyses: A list containing Lemma objects from a lookup.

        :return unicode: Plaintext string containing the paradigm to be generated, including
        any context provided.

        """
        from operator import itemgetter

        # Need to order possible matches by most extensive match, then
        # return that one.

        # TODO: there's also the chance that multiple analyses have
        # their own matches too, not just multiple rules.

        possible_matches = []

        for paradigm_rule in self.paradigm_rules.get(language, []):
            condition = paradigm_rule.get('condition')
            template = paradigm_rule.get('template')
            _, _, path = paradigm_rule.get('path').partition('language_specific_rules')

            try:
                truth, context = condition.evaluate(node, analyses)
            except Exception, e:
                print e
                print 'Exception in compiling rule or evaluating.'
                print '  ' + paradigm_rule.get('path')
                print '  node:'
                print node
                print '  analyses:'
                print analyses
                raise e

            # We have a match, so count how extensive it was.
            if truth:
                possible_matches.append(
                    (len(context.keys()), context, template, path)
                )

        # Sort by count, and pick the first
        possible_matches = sorted(possible_matches, key=itemgetter(0), reverse=True)
        if self.debug:
            print >> sys.stderr, " - Possible matches: %d" % len(possible_matches)

        if len(possible_matches) > 0:
            count, context, template, path = possible_matches[0]
            if debug:
                print >> sys.stderr, context

            template_context = {}
            template_context.update(context)
            template_context['lexicon'] = node
            template_context['analyses'] = analyses

            rendered = template.render(**template_context)
            if return_template:
                return rendered, path
            else:
                return rendered

        if return_template:
            return False, False
        else:
            return False

    def read_paradigm_directory(self):
        """ .. py:method:: read_paradigm_directory()

        Read through the paradigm directory, and read .paradigm files

        In running contexts, this expects a Flask app instance to be
        passed. For testing purposes, None may be passed.

        """
        from collections import defaultdict
        print >> sys.stderr, "* Reading paradigm directory."

        # Use a plain jinja environment if none exists.
        if self._app is None:
            from jinja2 import Environment
            jinja_env = Environment()
            available_langs = False
        else:
            jinja_env = self._app.jinja_env
            available_langs = self._app.config.languages

        self.jinja_env = jinja_env

        if hasattr(self, '_paradigm_directory'):
            return self._paradigm_directory

        # Path relative to working directory
        # TODO: need to grab from other configs?
        _path = os.path.join( os.getcwd()
                            , 'configs/language_specific_rules/paradigms/'
                            )

        # We only want the ones that exist for this instance.
        lang_directories = [ p for p in os.listdir(_path) ]

        if available_langs:
            lang_directories = [ p for p in lang_directories
                                 if p in available_langs ]

        _lang_files = {}
        _lang_layout_files = {}

        # get all the .paradigm files that belong to a language
        for lang in lang_directories:
            _lang_path = os.path.join( _path
                                     , lang
                                     )
            _lang_paradigm_files = []
            _lang_paradigm_layout_files = []

            for _p, dirs, files in os.walk(_lang_path):
                for f in files:
                    if f.endswith('.paradigm'):
                        _lang_paradigm_files.append(
                            os.path.join(_p, f)
                        )

                    if self._app.config.paradigm_layouts:
                        if f.endswith('.layout'):
                            _lang_paradigm_layout_files.append(
                                os.path.join(_p, f)
                            )

            _lang_files[lang] = _lang_paradigm_files
            _lang_layout_files[lang] = _lang_paradigm_layout_files

        _lang_paradigms = defaultdict(list)
        _lang_paradigm_layouts = defaultdict(list)

        _file_successes = []

        for lang, files in _lang_files.iteritems():
            for f in files:
                paradigm_rule = self.read_paradigm_file(jinja_env, f)

                if paradigm_rule:
                    _lang_paradigms[lang].append(paradigm_rule)
                    _file_successes.append(' - %s: %s' % (lang, paradigm_rule.get('name')))

        self.paradigm_rules = _lang_paradigms

        for lang, files in _lang_layout_files.iteritems():
            for f in files:
                paradigm_rule = self.read_paradigm_layout_file(jinja_env, f, lang)

                if paradigm_rule:
                    _lang_paradigm_layouts[lang].append(paradigm_rule)
                    _file_successes.append(' - LAYOUT %s: %s' % (lang, paradigm_rule.get('name')))
                else:
                    _file_successes.append(' ERROR: - LAYOUT %s: %s' % (lang, f))

        self.paradigm_layout_rules = _lang_paradigm_layouts

        print >> sys.stderr, '\n'.join(_file_successes)

        return None

    def read_paradigm_file(self, jinja_env, path):
        with open(path, 'r') as F:
            _raw = F.read().decode('utf-8')
        return self.parse_paradigm_string(jinja_env, _raw, path)

    def read_paradigm_layout_file(self, jinja_env, path, lang):
        with open(path, 'r') as F:
            _raw = F.read().decode('utf-8')
        return self.parse_paradigm_layout_string(_raw, path, lang)

    def parse_paradigm_layout_string(self, p_string, path, lang):
        condition_yaml, __, paradigm_string_txt = p_string.partition('--')

        parsed_condition = False
        if condition_yaml and paradigm_string_txt:
            try:
                condition_yaml = yaml.load(condition_yaml)
            except Exception, e:
                print >> sys.stderr, "\n** Problem reading paradigm rule condition at: "
                print >> sys.stderr, e
                print >> sys.stderr, " in:"
                _, lx, path = path.partition('language_specific_rules')
                print >> sys.stderr, "    " + lx + path
                print >> sys.stderr, "\n** Could not start service."
                sys.exit()

            name = condition_yaml.get('name')
            desc = condition_yaml.get('desc', '')

            # Check for 'paradigm', which is a reference to an existing
            # paradigm defition; if one exists, copy the `lexicon` and
            # `morphology` keys
            if 'paradigm' in condition_yaml:
                # morphology, lexicon keys only
                paradigm_rule = condition_yaml.get('paradigm')
                matching_p = [p for p in self.paradigm_rules[lang] if p['basename'] == paradigm_rule]
                if len(matching_p) == 0:
                    print >> sys.stderr, "\n** References a paradigm file (%s) that does not exist" % paradigm_rule
                    print >> sys.stderr, " in:"
                    _, lx, path = path.partition('language_specific_rules')
                    print >> sys.stderr, "    " + lx + path
                    sys.exit()

                # Copy from the parsed condition's rule definiton so
                # that we can create a new ParadigmRuleSet
                rule_def = matching_p[0].get('condition').rule_def

                if rule_def.get('lexicon', False):
                    condition_yaml['lexicon'] = rule_def.get('lexicon')
                if rule_def.get('morphology', False):
                    condition_yaml['morphology'] = rule_def.get('morphology')

            parsed_template, errors = parse_table(paradigm_string_txt.strip(), yaml_definition=condition_yaml, path=path)

            if not parsed_template:
                print errors
                return False

            parsed_condition = { 'condition': ParadigmRuleSet(condition_yaml, debug=self.debug)
                               , 'template': parsed_template
                               , 'name': name
                               , 'description': desc
                               , 'path': path
                               , 'updated': os.path.getmtime(path)
                               }

        return parsed_condition

    def parse_paradigm_string(self, jinja_env, p_string, path):
        condition_yaml, __, paradigm_string_txt = p_string.partition('--')

        parsed_condition = False
        if condition_yaml and paradigm_string_txt:
            try:
                condition_yaml = yaml.load(condition_yaml)
            except Exception, e:
                print >> sys.stderr, "\n** Problem reading paradigm rule condition at: "
                print >> sys.stderr, e
                print >> sys.stderr, " in:"
                _, lx, path = path.partition('language_specific_rules')
                print >> sys.stderr, "    " + lx + path
                print >> sys.stderr, "\n** Could not start service."
                sys.exit()

            name = condition_yaml.get('name')
            desc = condition_yaml.get('desc', '')
            parsed_template = jinja_env.from_string(paradigm_string_txt.strip())
            parsed_condition = { 'condition': ParadigmRuleSet(condition_yaml, debug=self.debug)
                               , 'template': parsed_template
                               , 'name': name
                               , 'description': desc
                               , 'path': path
                               , 'basename': os.path.basename(path)
                               , 'updated': os.path.getmtime(path)
                               }

        return parsed_condition

if __name__ == "__main__":
    from neahtta import app

    pc = ParadigmConfig(app)

    lookups = app.morpholexicon.lookup('mannat', source_lang='sme', target_lang='nob') \
            + app.morpholexicon.lookup(u'Ráisa', source_lang='sme', target_lang='nob')

    for node, analyses in lookups:
        print node, analyses
        print pc.get_paradigm('sme', node, analyses)

