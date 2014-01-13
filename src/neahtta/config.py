# -*- encoding: utf-8 -*-
import sys, os

from flask import Config

# Import configs stuff to register overrides
from configs import *

import yaml

def gettext_yaml_wrapper(loader, node):
    from flaskext.babel import lazy_gettext as _
    return node.value

# TODO: make this work, or figure out how babel wants a parser for yaml
# constructed.
yaml.add_constructor('!gettext', gettext_yaml_wrapper)

class Config(Config):
    """ An object for exposing the settings in app.config.yaml in a nice
    objecty way, and validating some of the contents.
    """

    @property
    def default_language_pair(self):
        _p = self.yaml.get('ApplicationSettings', {})\
                      .get('default_pair', False)
        if _p:
            return _p
        else:
            raise RuntimeError('Default language pair not specified in '
                               'config file %s, in ApplicationSettings.' %
                               self.filename)

    @property
    def locales_available(self):
        _p = self.yaml.get('ApplicationSettings', {})\
                      .get('locales_available', False)
        if _p:
            return _p
        else:
            raise RuntimeError('locales_available not specified in '
                               'config file %s, in ApplicationSettings.' %
                               self.filename)

    @property
    def app_name(self):
        _p = self.yaml.get('ApplicationSettings', {})\
                      .get('app_name', u"Neahttadigisánit")
        if _p:
            return _p
        else:
            raise RuntimeError('app_name not specified in '
                               'config file %s, in ApplicationSettings.' %
                               self.filename)

    @property
    def admins(self):
        _p = self.yaml.get('ApplicationSettings', {})\
                      .get('admins_to_email', False)
        if _p:
            return _p
        else:
            return []

    @property
    def short_name(self):
        _p = self.yaml.get('ApplicationSettings', {})\
                      .get('short_name', False)
        if _p:
            return _p
        else:
            raise RuntimeError('short_name not specified in '
                               'config file %s, in ApplicationSettings.' %
                               self.filename)

    @property
    def default_locale(self):
        _p = self.yaml.get('ApplicationSettings', {})\
                      .get('default_locale', False)
        if _p:
            return _p
        else:
            raise RuntimeError('default_locale not specified in '
                               'config file %s, in ApplicationSettings.' %
                               self.filename)

    @property
    def meta_keywords(self):
        _p = self.yaml.get('ApplicationSettings', {})\
                      .get('meta_keywords', False)
        if _p:
            return _p
        else:
            raise RuntimeError('meta_keywords not specified in '
                               'config file %s, in ApplicationSettings.' %
                               self.filename)

    @property
    def meta_description(self):
        _p = self.yaml.get('ApplicationSettings', {})\
                      .get('meta_description', False)
        if _p:
            return _p
        else:
            raise RuntimeError('meta_description not specified in '
                               'config file %s, in ApplicationSettings.' %
                               self.filename)

    @property
    def app_meta_title(self):
        _p = self.yaml.get('ApplicationSettings', {})\
                      .get('app_meta_title', False)
        if _p:
            return _p
        else:
            raise RuntimeError('app_meta_title not specified in '
                               'config file %s, in ApplicationSettings.' %
                               self.filename)

    @property
    def mobile_redirect_pair(self):
        _p = self.yaml.get('ApplicationSettings', {})\
                      .get('mobile_default_pair', None)
        if _p is not None:
            return _p
        else:
            raise RuntimeError('Mobile redirect pair not specified in '
                               'config file %s, in ApplicationSettings.'
                               ' If none, specify with false.' %
                               self.filename)


    @property
    def paradigms(self):
        if self._paradigms:
            return self._paradigms

        lang_paradigms = self.yaml.get('Paradigms', {})

        self._paradigms = lang_paradigms
        return self._paradigms

    @property
    def paradigm_contexts(self):
        """ This reads the `paradigms` directory and loads all of the
        paradigm files for languages active in dictionary set.
        """
        from collections import defaultdict

        if hasattr(self, '_paradigm_contexts'):
            return self._paradigm_contexts

        paradigm_path = os.path.join( os.getcwd()
                                    , 'configs/language_specific_rules/paradigms/'
                                    )

        available_langs = self.languages

        lang_directories = [ p for p in os.listdir(paradigm_path)
                             if p in available_langs ]

        self._paradigm_contexts = defaultdict(dict)

        _lang_files = {}
        for lang in lang_directories:
            _lang_path = os.path.join( paradigm_path
                                     , lang
                                     )
            _lang_paradigm_files = []

            for _p, dirs, files in os.walk(_lang_path):
                for f in files:
                    if f.endswith('.context'):
                        _lang_paradigm_files.append(
                            os.path.join(_p, f)
                        )

            _lang_files[lang] = _lang_paradigm_files

        jinja_env = self.get('jinja_env')
        def reformat_context_set(filepath, _sets):
            parsed_sets = {}
            if _sets is None:
                return {}

            for s in _sets:
                entry_c = s.get('entry_context', None)
                if entry_c == 'None':
                    entry_c = None

                tag_c = s.get('tag_context', None)
                if tag_c == 'None':
                    tag_c = None

                template = s.get('template')

                if tag_c is None:
                    print >> sys.stderr, "Missing tag context in <%s>" % filepath

                parsed_sets[(entry_c, tag_c)] = jinja_env.from_string(template)
            return parsed_sets

        for language, files in _lang_files.iteritems():
            for f in files:
                tagset_path = os.path.join(_p, f)

                try:
                    file_context_set = yaml.load(open(tagset_path, 'r').read())
                except Exception, e:
                    print " * YAML parsing error in <%s>\n\n" % tagset_path
                    print e
                    sys.exit()
                self._paradigm_contexts[language].update(
                    reformat_context_set(tagset_path, file_context_set)
                )

        return self._paradigm_contexts

    @property
    def reversable_dictionaries(self):
        if self._reversable_dictionaries:
            return self._reversable_dictionaries

        def isReversable(d):
            if d.get('reversable', False):
                return d

        dicts = filter(isReversable, self.yaml.get('Dictionaries'))
        language_pairs = {}
        for item in dicts:
            source = item.get('source')
            target = item.get('target')
            path = item.get('path')
            language_pairs[(source, target)] = path

        self._reversable_dictionaries = language_pairs
        return language_pairs

    @property
    def languages(self):
        if not self._languages:
            self._languages = {}
            for lang in self.yaml.get('Languages'):
                self._languages[lang.get('iso')] = lang.get('name', {})

        return self._languages

    @property
    def dictionaries(self):
        from collections import OrderedDict
        if self._dictionaries:
            return self._dictionaries

        dicts = self.yaml.get('Dictionaries')
        language_pairs = OrderedDict()
        for item in dicts:
            source = item.get('source')
            target = item.get('target')
            path = item.get('path')
            language_pairs[(source, target)] = path

        self._dictionaries = language_pairs
        return language_pairs

    @property
    def variant_dictionaries(self):
        from collections import OrderedDict
        if hasattr(self, '_variant_dictionaries'):
            return self._variant_dictionaries

        dicts = self.yaml.get('Dictionaries')
        language_pairs = OrderedDict()
        for item in dicts:
            source = item.get('source')
            target = item.get('target')
            path = item.get('path')
            variants = item.get('input_variants')
            if variants:
                for v in variants:
                    if v.get('short_name') != source:
                        language_pairs[(v.get('short_name'), target)] = {
                            'orig_pair': (source, target),
                            'path': path,
                        }

        self._variant_dictionaries = language_pairs
        return language_pairs

    @property
    def input_variants(self):
        from collections import OrderedDict
        if self._input_variants:
            return self._input_variants

        dicts = self.yaml.get('Dictionaries')
        language_pairs = OrderedDict()
        for item in dicts:
            source = item.get('source')
            target = item.get('target')
            input_variants = item.get('input_variants', False)
            if input_variants:
                language_pairs[(source, target)] = input_variants

        self._input_variants = language_pairs
        return language_pairs

    @property
    def tag_filters(self):
        """ Reads the `tagsets` directory for tagsets active in the
        dictionary set.
        """
        if hasattr(self, '_tag_filters'):
            return self._tag_filters

        _path = os.path.join( os.getcwd()
                            , 'configs/language_specific_rules/user_friendly_tags/'
                            )

        available_langs = self.languages

        filter_sets = {}

        def format_yaml(_yaml):
            _yaml_sets = {}
            for _set in _yaml.get('Relabel'):
                source = _set.get('source_morphology')
                target = _set.get('target_ui_language')
                tags = _set.get('tags')
                if source in self.languages.keys() and target in self.languages.keys():
                    _yaml_sets[(source, target)] = tags
            return _yaml_sets

        for _p, dirs, files in os.walk(_path):
            for f in files:
                if f.endswith('.relabel'):
                    print " * Reading tagset in <%s> " % f
                    relabel_path = os.path.join(_p, f)
                    try:
                        relabel_yaml = format_yaml(
                            yaml.load(open(relabel_path, 'r').read())
                        )
                    except Exception, e:
                        print " * YAML parsing error in <%s>\n\n" % relabel_path
                        print e
                        sys.exit()
                    filter_sets.update(relabel_yaml)
                    print "   - found: " + ', '.join(
                        [k[0] + ' -> ' + k[1] for k in relabel_yaml.keys()]
                    )

        self._tag_filters = filter_sets
        return self._tag_filters

    @property
    def tagset_definitions(self):
        """ Reads the `tagsets` directory for tagsets active in the
        dictionary set.
        """
        if self._tagset_definitions:
            return self._tagset_definitions

        tagset_path = os.path.join( os.getcwd()
                                  , 'configs/language_specific_rules/tagsets/'
                                  )

        available_langs = self.languages

        sets = {}

        for _p, dirs, files in os.walk(tagset_path):
            for f in files:
                if f.endswith('.tagset'):
                    language = f.partition('.')[0]
                    tagset_path = os.path.join(_p, f)
                    try:
                        tagset_yaml = yaml.load(open(tagset_path, 'r').read())
                    except Exception, e:
                        print " * YAML parsing error in <%s>\n\n" % tagset_path
                        print e
                        sys.exit()
                    sets[language] = tagset_yaml

        self._tagset_definitions = sets
        return sets

    @property
    def pair_definitions(self):
        from collections import OrderedDict

        if not self._pair_definitions:
            self._pair_definitions = OrderedDict()
            _par_defs = {}
            for dict_def in self.yaml.get('Dictionaries'):
                _from, _to = dict_def.get('source'), dict_def.get('target')
                key = (_from, _to)
                _from_langs = self.languages[_from]
                _to_langs = self.languages[_to]
                _lang_isos = set(_from_langs.keys()) & set(_to_langs.keys())

                _missing = set(_from_langs.keys()) ^ set(_to_langs.keys())
                if _missing:
                    print >> sys.stderr, "Missing some name translations for"
                    print >> sys.stderr, ', '.join(list(_missing))
                    print >> sys.stderr, "Check Languages in app.config.yaml"
                    sys.exit()

                _pair_options = {
                    'langs': {},
                    'show_korp_search': dict_def.get('show_korp_search', False),
                    'alternate_search_url': dict_def.get('alternate_search_url', False),
                    'lemma_search_url': dict_def.get('lemma_search_url', False),
                    'lemma_multiword_delimiter': dict_def.get('lemma_multiword_delimiter', False)
                }
                for iso in _lang_isos:
                    _pair_options['langs'][iso] = (_from_langs[iso], _to_langs[iso])

                _pair_options['input_variants'] = self.input_variants.get(key, False)

                _par_defs[key] = _pair_options

            for k, v in self.dictionaries.iteritems():
                self._pair_definitions[k] = _par_defs[k]

        return self._pair_definitions

    @property
    def morphologies(self):
        if self._morphologies:
            return self._morphologies

        self._morphologies = {}

        from morphology import XFST, OBT, Morphology
        morph_cache = self.get('cache', False)

        formats = {
            'xfst': XFST,
            'obt': OBT,
        }

        for iso, _kwargs_in in self.yaml.get('Morphology').iteritems():
            conf_format = _kwargs_in.get('format', False)
            kwargs = {}

            if not conf_format:
                print "No format specified"
                sys.exit()

            m_format = formats.get(conf_format, False)
            if not m_format:
                print "Undefined format"
                sys.exit()

            if 'tool' in _kwargs_in:
                if isinstance(_kwargs_in['tool'], list):
                    _kwt = ''.join(_kwargs_in['tool'])
                else:
                    _kwt = _kwargs_in['tool']
                kwargs['lookup_tool'] = _kwt
            else:
                print "Lookup tool missing"
                sys.exit()

            if 'file' in _kwargs_in:
                if isinstance(_kwargs_in['file'], list):
                    _kwf = ''.join(_kwargs_in['file'])
                else:
                    _kwf = _kwargs_in['file']
                kwargs['fst_file'] = _kwf

            if 'inverse_file' in _kwargs_in:
                if isinstance(_kwargs_in['inverse_file'], list):
                    _kwfi = ''.join(_kwargs_in['inverse_file'])
                else:
                    _kwfi = _kwargs_in['inverse_file']
                kwargs['ifst_file'] = _kwfi

            if 'options' in _kwargs_in:
                kwargs['options'] = _kwargs_in['options']

            tagsets = self.tagset_definitions.get(iso, {})
            self._morphologies[iso] = \
                m_format(**kwargs) >> Morphology( iso
                                                , cache=morph_cache
                                                , tagsets=tagsets
                                                )

        return self._morphologies

    def test(self, silent=False):
        for item in dir(self):
            if not item.startswith('_') and item != 'test':
                if silent:
                    self.__getattribute__(item)
                else:
                    print item
                    print self.__getattribute__(item)

    def from_envvar(self, variable_name, silent=False):
        """Loads a configuration from an environment variable pointing to
        a configuration file. This is basically just a shortcut with nicer
        error messages for this line of code::

        app.config.from_pyfile(os.environ['YOURAPPLICATION_SETTINGS'])

        :param variable_name: name of the environment variable
        :param silent: set to `True` if you want silent failure for missing
        files.
        :return: bool. `True` if able to load config, `False` otherwise.
        """
        import os
        rv = os.environ.get(variable_name)
        if not rv:
            raise RuntimeError('The environment variable %r is not set '
                               'and as such configuration could not be '
                               'loaded. Set this variable and make it '
                               'point to a configuration file' %
                               variable_name)
        return self.from_yamlfile(rv, silent=silent)

    def from_yamlfile(self, filename, silent=False):
        self._languages               = False
        self._pair_definitions        = False
        self._dictionaries            = False
        self._input_variants          = False
        self._tagset_definitions      = False
        self._reversable_dictionaries = False
        self._paradigms               = False
        self._baseforms               = False
        self._morphologies            = False

        with open(filename, 'r') as F:
            config = yaml.load(F)
        self.yaml = config
        self.filename = filename
        self.test(silent=True)
        # Prepare lexica

        return True

    def prepare_lexica(self):
        from lexicon import Lexicon
        self.lexicon = Lexicon(self)
        self.tag_filters

