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

        lang_paradigms = self.yaml.get('Paradigms')

        self._paradigms = lang_paradigms
        return self._paradigms

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
    def tag_filters(self):
        if not self._tag_filters:
            tag_filters = self.yaml.get('TagTransforms')

            self._tag_filters = {}
            for k, v in tag_filters.iteritems():
                try:
                    _new_k = k.replace('(', '').replace(')', '')
                    _f, _, _t = _new_k.partition(',')
                    _f = _f.strip()
                    _t = _t.strip()
                except Exception:
                    raise RuntimeError('Error parsing language pair key'
                                       ' for %s in TagTransforms. '
                                       'Use format (sme, nob). In file'
                                       ' %s' %
                                       (k, self.filename))

                self._tag_filters[(_f, _t)] = v
        return self._tag_filters

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
    def tagset_definitions(self):
        if self._tagset_definitions:
            return self._tagset_definitions

        sets = self.yaml.get('TagSets')

        self._tagset_definitions = sets
        return sets

    @property
    def pair_definitions(self):
        from collections import OrderedDict

        if not self._pair_definitions:
            self._pair_definitions = OrderedDict()
            _par_defs = {}
            for key, path in self.dictionaries.iteritems():
                _from, _to = key
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
                    'langs': {}
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

            # TODO: tagsets
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
        self._tag_filters             = False

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

