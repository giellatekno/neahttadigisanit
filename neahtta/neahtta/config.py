import os
import sys
from collections import defaultdict
from functools import cmp_to_key, cached_property
from pathlib import Path

from flask import Config
import yaml

from neahtta.nds_lexicon.lexicon import DEFAULT_XPATHS

# Import configs stuff to register overrides
# from conf import *


def gettext_yaml_wrapper(loader, node):
    # anders: commented out, pretty sure this is not here because
    # of a side effect, but not entirely sure.
    # from flask_babel import lazy_gettext as _
    # forandring

    return node.value


yaml.add_constructor("!gettext", gettext_yaml_wrapper)

# This should match most language words, with few surprises, however it
# does not include the cases where a language uses a period or
# apostrophe within a word.

DEFAULT_WORD_REGEX = "[\u00C0-\u1FFF\u2C00-\uD7FF\w\-]+"
DEFAULT_WORD_REGEX_OPTS = "g"


def external_korp_url(pair_details, user_input):
    from urllib.parse import quote
    from flask import redirect
    from flask import g

    #    'korp_parallel'

    #    'bilingual_wordform_search_path'
    #    'bilingual_wordform_search_query'
    # Cip's test
    # Add this line for testing
    korp_opts = pair_details.get("korp_options")
    korp_host = pair_details.get("korp_search_host")
    link_corpus_param = pair_details.get("link_corpus_parameter")

    # TODO: original pair, if current pair is variant
    if korp_opts.get("is_korp_default_lang"):
        url_pattern = korp_opts.get("wordform_search_path_default_lang")
    else:
        url_pattern = korp_opts.get("wordform_search_path").replace(
            "TARGET_LANG_ISO", g.orig_from
        )

    if korp_opts.get("korp_parallel"):
        url_pattern = korp_opts.get("bilingual_wordform_search_path").replace(
            "TARGET_LANG_ISO", g.orig_from
        )
        if g.orig_from == "fin":
            url_pattern = url_pattern.replace("mode=parallel", "mode=parallel_fin")
        url_pattern = url_pattern.replace(
            "SEARCH_QUERY",
            quote(korp_opts.get("bilingual_wordform_search_query"), safe="#&/"),
        )

    delimiter_pattern = korp_opts.get("lemma_multiword_delimeter")

    if " " in user_input and delimiter_pattern:
        user_input = delimiter_pattern.join(user_input.split(" "))

    try:
        user_input = user_input.encode("utf-8")
    except UnicodeError as e:
        print("Error in user_input:", e)

    try:
        url_pattern = url_pattern.encode("utf-8")
    except UnicodeError as e:
        print("Error in url_pattern:", e)

    url_pattern = url_pattern.replace(b"USER_INPUT", user_input)

    try:
        url_pattern = url_pattern.decode("utf-8")
    except UnicodeError as e:
        print("Error in url_pattern:", e)

    if len(link_corpus_param) != 0:
        url_pattern = url_pattern + "&corpus=" + link_corpus_param

    redirect_url = korp_host + url_pattern

    return redirect(redirect_url)


def validate_variants(variants, lexicon):
    if not variants:
        return variants
    obligatory_keys = set(["type", "description", "short_name"])
    # anders: unused, not sure what it's for
    # optional_keys = set(["example", "onscreen_keyboard"])
    variant_count = 1
    for v in variants:
        missing_keys = obligatory_keys - set(v.keys())
        if missing_keys:
            sys.exit(
                f"Missing settings in `input_variants`: {variant_count} "
                f"for lexicon <{repr(lexicon)}>\n"
                "    " + ",".join(missing_keys)
            )
            sys.exit()
        variant_count += 1

    return variants


class Config(Config):
    """An object for exposing the settings in app.config.yaml in a nice
    objecty way, and validating some of the contents.

    NOTE: Source of confusion!
    The methods named "from_*" are intentially _NOT_ constructors!
    They are updators, and update the config from the specific source.
    They return a bool indicating updating success or not.
    This is a Flask-convention, and not something we are responsible for.
    """

    def from_yamlfile(self, filename, silent=True):
        try:
            with open(filename) as f:
                self.yaml = yaml.load(f, yaml.Loader)
        except FileNotFoundError:
            raise
            sys.exit(f"config file not found: {filename}")
        except PermissionError:
            sys.exit(f"config file not readable: {filename}")

        self.filename = filename
        self.validate()
        # anders: this does __getattribute__() on everything in dir(self)
        # I don't understand why.
        # - Maybe to prime all the cached properties? If so it wouldn't have
        #   have been named "test", so that's probably not it.
        # self.test(silent=True)
        return True

    def from_envvar(self, variable_name, silent=False):
        """Overload this method from Flask to load from yaml file, instead of
        python"""
        try:
            config_path = os.environ[variable_name]
        except KeyError:
            sys.exit(
                f"The environment variable {variable_name} is not set. "
                "Set it to the path to the configuration file, e.g. "
                "configs/sanit.config.yaml"
            )

        return self.from_yamlfile(config_path, silent=silent)

    @cached_property
    def language_configs_yaml(self):
        # anders: path change
        with open("neahtta/configs/language_names.yaml") as f:
            return yaml.load(f, yaml.Loader)

    @property
    def language_specific_rules_path(self):
        # anders: path change
        return "neahtta/configs/language_specific_rules"

    @cached_property
    def NAMES(self):
        return self.language_configs_yaml.get("isos_to_names", {})

    @cached_property
    def LOCALISATION_NAMES_BY_LANGUAGE(self):
        return self.language_configs_yaml.get("isos_to_demonym", {})

    @cached_property
    def ISO_DISPLAY_RELABELS(self):
        return self.language_configs_yaml.get("iso_display_relabels", {})

    @cached_property
    def ISO_TRANSFORMS(self):
        return self.language_configs_yaml.get("iso_transforms", {})

    @cached_property
    def default_language_pair(self):
        return self.yaml["ApplicationSettings"]["default_pair"]

    @cached_property
    def paradigm_layouts(self):
        return self.yaml["ApplicationSettings"].get("paradigm_layouts", False)

    # @property
    # def onscreen_keyboard(self):
    #     _p = self.yaml.get('ApplicationSettings', {})\
    #                   .get('onscreen_keyboard', False)
    #     return _p

    @cached_property
    def locales_available(self):
        return self.yaml["ApplicationSettings"]["locales_available"]

    @cached_property
    def hidden_locales(self):
        return self.yaml["ApplicationSettings"].get("hidden_locales", [])

    @cached_property
    def app_name(self):
        return self.yaml["ApplicationSettings"]["app_name"]

    @cached_property
    def admins(self):
        return self.yaml["ApplicationSettings"].get("admins_to_email", [])

    @property
    def geoip_logging_enabled(self):
        """Return our best guess assuming someone has followed the
        makefile otherwise allow override.
        """
        p = self.yaml["ApplicationSettings"].get("GEOIP_LOGGING_ENABLED")

        if not p:
            return []
        else:
            if Path(self.geoip_library_path).exists():
                return p
            else:
                print(
                    "Could not find GeoIP library, but geoip logging is enabled.",
                    file=sys.stderr,
                )
                print(
                    "Check that it is compiled at the following path:", file=sys.stderr
                )
                print("", file=sys.stderr)
                print("     %s" % self.geoip_library_path, file=sys.stderr)
                print("", file=sys.stderr)
                print(
                    "  ... or supply a different path with ApplicationSettings/GEOIP_LIBRARY_PATH",
                    file=sys.stderr,
                )
                print("  setting in relevant project .yaml file.", file=sys.stderr)
                print("", file=sys.stderr)
                print("See also: geo/README.md", file=sys.stderr)
                print("", file=sys.stderr)
                sys.exit()

    @property
    def geoip_path(self):
        """Return our best guess assuming someone has followed the
        makefile otherwise allow override.
        """
        default = os.path.join(os.path.dirname(__file__), "geo/data")
        _p = self.yaml["ApplicationSettings"].get("GEOIP_PATH", default)
        if _p:
            return _p
        else:
            return []

    @property
    def geoip_library_path(self):
        """Return our best guess assuming someone has followed the
        makefile otherwise allow override.
        """
        default = os.path.join(os.path.dirname(__file__), "geoip/lib/libGeoIP.so")
        _p = self.yaml.get("ApplicationSettings", {}).get("GEOIP_LIBRARY_PATH", default)
        if _p:
            return _p
        else:
            return []

    @property
    def new_style_templates(self):
        return self.yaml["ApplicationSettings"].get("new_style_templates", True)

    @cached_property
    def short_name(self):
        return self.yaml["ApplicationSettings"]["short_name"]

    @cached_property
    def default_locale(self):
        return self.yaml["ApplicationSettings"]["default_locale"]

    @cached_property
    def meta_keywords(self):
        return self.yaml["ApplicationSettings"]["meta_keywords"]

    @cached_property
    def has_project_css(self):
        path = f"static/css/{self.short_name}.css"
        try:
            with open(os.path.join(os.path.dirname(__file__), path)) as _:
                return path
        except (FileNotFoundError, PermissionError):
            return False

    @cached_property
    def meta_description(self):
        return self.yaml["ApplicationSettings"]["meta_description"]

    @cached_property
    def grouped_nav(self):
        return self.yaml["ApplicationSettings"].get("grouped_nav", False)

    @cached_property
    def new_mobile_nav(self):
        return self.yaml["ApplicationSettings"].get("new_mobile_nav", False)

    @cached_property
    def app_meta_title(self):
        return self.yaml["ApplicationSettings"]["app_meta_title"]

    @cached_property
    def fcgi_script_path(self):
        return self.yaml["ApplicationSettings"].get("fcgi_script_path", "")

    @cached_property
    def menu_flags(self):
        return self.yaml["ApplicationSettings"].get("menu_flags", True)

    @cached_property
    def render_template_errors(self):
        return self.yaml["ApplicationSettings"].get("render_template_errors", False)

    @cached_property
    def app_mobile_bookmark_name(self):
        p = self.yaml["ApplicationSettings"].get("mobile_bookmark_name", False)
        return p if p else self.app_meta_title

    @cached_property
    def polyglot_lookup(self):
        return self.yaml["ApplicationSettings"].get("polyglot_lookup", False)

    @cached_property
    def mobile_redirect_pair(self):
        return self.yaml["ApplicationSettings"]["mobile_default_pair"]

    @cached_property
    def paradigms(self):
        return self.yaml.get("Paradigms", {})

    @cached_property
    def paradigm_contexts(self):
        """This reads the `paradigms` directory and loads all of the
        paradigm files for languages active in dictionary set."""
        # anders: path change
        paradigm_path = "neahtta/configs/language_specific_rules/paradigms"
        available_langs = self.languages

        lang_directories = [
            p for p in os.listdir(paradigm_path) if p in available_langs
        ]

        paradigm_contexts = defaultdict(dict)

        _lang_files = {}
        for lang in lang_directories:
            _lang_path = os.path.join(paradigm_path, lang)
            _lang_paradigm_files = []

            for _p, dirs, files in os.walk(_lang_path):
                for f in files:
                    if f.endswith(".context"):
                        _lang_paradigm_files.append(os.path.join(_p, f))

            _lang_files[lang] = _lang_paradigm_files

        jinja_env = self.get("jinja_env")

        def reformat_context_set(filepath, _sets):
            parsed_sets = {}
            if _sets is None:
                return {}

            for s in _sets:
                entry_c = s.get("entry_context", None)
                if entry_c == "None":
                    entry_c = None

                tag_c = s.get("tag_context", None)
                if tag_c == "None":
                    tag_c = None

                template = s.get("template")

                if tag_c is None:
                    print(f"Missing tag context in <{filepath}>", file=sys.stderr)

                parsed_sets[(entry_c, tag_c)] = jinja_env.from_string(template)
            return parsed_sets

        for language, files in _lang_files.items():
            for f in files:
                tagset_path = os.path.join(_p, f)
                if os.path.exists(tagset_path):
                    try:
                        file_context_set = yaml.load(
                            open(tagset_path, "r"), yaml.Loader
                        )
                    except Exception as e:
                        print(f"YAML parsing error in <{tagset_path}>\n\n")
                        print(e)
                        sys.exit()
                    paradigm_contexts[language].update(
                        reformat_context_set(tagset_path, file_context_set)
                    )

        return paradigm_contexts

    @cached_property
    def reversable_dictionaries(self):
        def isReversable(d):
            if d.get("reversable", False):
                return d

        dicts = filter(isReversable, self.yaml["Dictionaries"])
        language_pairs = {}
        for item in dicts:
            source = item.get("source")
            target = item.get("target")
            path = item.get("path")
            language_pairs[(source, target)] = path

        return language_pairs

    @cached_property
    def languages(self):
        languages = {}
        for lang in self.yaml.get("Languages", []):
            languages[lang["iso"]] = lang.get("name", {})

        # Add variants to languages if they're missing.
        for iso in self.yaml.get("Morphology", []):
            languages.setdefault(iso, {"iso": iso})

        return languages

    @cached_property
    def minority_languages(self):
        minority_languages = {}
        for lang in self.yaml.get("Languages", []):
            if lang.get("minority_lang"):
                minority_languages[lang.get("iso")] = lang.get("name", {})
        return minority_languages

    @cached_property
    def unittests(self):
        return self.yaml.get("UnitTests", [])

    @cached_property
    def variant_dictionaries(self):
        dicts = self.yaml["Dictionaries"]
        language_pairs = {}
        for item in dicts:
            source = item.get("source")
            target = item.get("target")
            path = item.get("path")
            variants = item.get("input_variants")
            if variants:
                for v in variants:
                    path = v.get("path", item.get("path"))
                    target_variant = v.get("display_variant", False)
                    if not target_variant:
                        if v.get("short_name") != source:
                            language_pairs[(v.get("short_name"), target)] = {
                                "orig_pair": (source, target),
                                "path": path,
                            }
                    else:
                        if v.get("short_name") != target:
                            language_pairs[(source, v.get("short_name"))] = {
                                "orig_pair": (source, target),
                                "path": path,
                            }

        return language_pairs

    @cached_property
    def input_variants(self):
        dicts = self.yaml["Dictionaries"]
        language_pairs = {}
        for item in dicts:
            source = item.get("source")
            target = item.get("target")
            input_variants = item.get("input_variants", False)
            if input_variants:
                language_pairs[(source, target)] = input_variants

        return language_pairs

    @cached_property
    def search_variants(self):
        dicts = self.yaml["Dictionaries"]
        language_pairs = {}
        for item in dicts:
            source = item.get("source")
            target = item.get("target")
            input_variants = item.get("search_variants", False)
            if input_variants:
                language_pairs[(source, target)] = input_variants

        return language_pairs

    @cached_property
    def dictionaries(self):
        dicts = self.yaml["Dictionaries"]
        language_pairs = {}
        for item in dicts:
            source = item.get("source")
            target = item.get("target")
            path = item.get("path")
            language_pairs[(source, target)] = path

        return language_pairs

    @cached_property
    def dictionary_options(self):
        dicts = self.yaml["Dictionaries"]
        opts = defaultdict(dict)
        for item in dicts:
            source = item.get("source")
            target = item.get("target")
            lexicon_options = DEFAULT_XPATHS.copy()
            lexicon_options.update(**item.get("options", {}))
            opts[(source, target)] = lexicon_options

        return opts

    @cached_property
    def tag_filters(self):
        """Reads the `tagsets` directory for tagsets active in the
        dictionary set.
        """
        # anders: path change
        _path = "neahtta/configs/language_specific_rules/user_friendly_tags"
        filter_sets = {}

        def format_yaml(_yaml):
            _yaml_sets = {}
            for _set in _yaml.get("Relabel"):
                source = _set.get("source_morphology")
                target = _set.get("target_ui_language")

                _set.pop("source_morphology")
                _set.pop("target_ui_language")

                # TODO: raise error if missing 'tags'?

                # iterate through sets and set them.
                for set_name, set_tags in _set.items():
                    if (
                        source in self.languages.keys()
                        and target in self.languages.keys()
                    ):
                        if set_name == "generation_tags":
                            _yaml_sets[(source, target, "generation")] = set_tags
                        elif set_name == "tags":
                            _yaml_sets[(source, target)] = set_tags
                        else:
                            _yaml_sets[(source, target, set_name)] = set_tags
            return _yaml_sets

        for _p, dirs, files in os.walk(_path):
            for f in files:
                if f.endswith(".relabel"):
                    print(f" * Reading tagset in <{f}>")
                    relabel_path = os.path.join(_p, f)
                    try:
                        relabel_yaml = format_yaml(
                            yaml.load(open(relabel_path, "r"), yaml.Loader)
                        )
                    except Exception as e:
                        print(f" * YAML parsing error in <{relabel_path}>\n\n")
                        print(e)
                        sys.exit()
                    filter_sets.update(relabel_yaml)
                    print(
                        "   - found: "
                        + ", ".join([k[0] + " -> " + k[1] for k in relabel_yaml.keys()])
                    )

        return filter_sets

    @cached_property
    def tagset_definitions(self):
        """Reads the `tagsets` directory for tagsets active in the
        dictionary set."""

        # anders: path change
        tagset_path = "neahtta/configs/language_specific_rules/tagsets"
        sets = {}

        for _p, dirs, files in os.walk(tagset_path):
            for f in files:
                if f.endswith(".tagset"):
                    language = f.partition(".")[0]
                    tagset_path = os.path.join(_p, f)
                    try:
                        tagset_yaml = yaml.load(open(tagset_path, "r"), yaml.Loader)
                    except Exception as e:
                        print(" * YAML parsing error in <%s>\n\n" % tagset_path)
                        print(e)
                        sys.exit()
                    sets[language] = tagset_yaml

        return sets

    @cached_property
    def pair_definitions(self):
        _pair_definitions = {}
        _par_defs = {}
        for dict_def in self.yaml["Dictionaries"]:
            _from, _to = dict_def["source"], dict_def["target"]
            key = (_from, _to)
            _from_langs = self.languages[_from]
            _to_langs = self.languages[_to]
            _lang_isos = set(_from_langs.keys()) & set(_to_langs.keys())

            _missing = set(_from_langs.keys()) ^ set(_to_langs.keys())
            if _missing:
                print("Missing some name translations for", file=sys.stderr)
                print(", ".join(list(_missing)), file=sys.stderr)
                print("Check Languages in app.config.yaml", file=sys.stderr)
                sys.exit()

            _default_korp = {
                "lemma_search_path": "/?mode=TARGET_LANG_ISO#page=0&search-tab=2&search=SEARCH_QUERY",
                "lemma_search_path_default_lang": "/#page=0&search-tab=2&search=SEARCH_QUERY",
                "lemma_search_query": 'cqp|[lemma = "INPUT_LEMMA"]',
                "wordform_search_path": "/?mode=TARGET_LANG_ISO#search=word|USER_INPUT&page=0",
                "wordform_search_path_default_lang": "/#search=word|USER_INPUT&page=0",
                "bilingual_wordform_search_path": "/?mode=parallel#parallel_corpora=TARGET_LANG_ISO&page=0&search=SEARCH_QUERY",
                "bilingual_wordform_search_query": 'cqp|[(word = "USER_INPUT")]',
                "lemma_search_delimiter": "] [lemma = ",
                "is_korp_default_lang": dict_def.get("is_korp_default_lang", False),
                "korp_parallel": dict_def.get("korp_parallel", False),
                "corpora": dict_def.get("corpora", False),
                "start_query": dict_def.get("start_query", False),
            }

            _pair_options = {
                "langs": {},
                "autocomplete": dict_def.get("autocomplete", True),
                "show_korp_search": dict_def.get("show_korp_search", False),
                "korp_search_host": dict_def.get("korp_search_host", False),
                "korp_options": dict_def.get("korp_options", _default_korp),
                "asynchronous_paradigms": dict_def.get("asynchronous_paradigms", False),
                "link_corpus_parameter": dict_def.get("link_corpus_parameter", ""),
            }
            for iso in _lang_isos:
                _pair_options["langs"][iso] = (_from_langs[iso], _to_langs[iso])

            _pair_options["input_variants"] = validate_variants(
                self.input_variants.get(key, False), key
            )
            _pair_options["search_variants"] = self.search_variants.get(key, False)

            if _from == "fin":
                korp_opts = _pair_options.get("korp_options")
                korp_opts["bilingual_wordform_search_path"] = (
                    korp_opts.get("bilingual_wordform_search_path")
                    .replace("mode=parallel", "mode=parallel_fin")
                    .replace("parallel_corpora", "parallel_fin_corpora")
                )

            _par_defs[key] = _pair_options

        for k, v in self.dictionaries.items():
            _pair_definitions[k] = _par_defs[k]

        return _pair_definitions

    def pair_definitions_grouped_source_locale(self):
        from flask_babel import get_locale

        # anders: side effect?
        locale = get_locale()
        NAMES = self.NAMES

        def group_by_source_first(dict):
            """Return the source and target."""
            ((source, target), pair_options) = dict
            return (source, target)

        def minority_langs_first(dict_a, dict_b):
            """This is the cmp function, which accepts two ISO pairs
            and returns -1, 0, or 1 to sort the values depending on a few criteria:

                * are the source languages both marked as minority langs?
                * are the source languages both *not* marked as minority langs?

                 -> sort them as normal

                * is one of the source langs marked as a minority lang?

                 -> return the minority language first

            Then... Also sort by the target languages, so each grouping
            is still alphabetical."""
            ((a_source_iso, a_target_iso), pair_options) = dict_a
            ((b_source_iso, b_target_iso), pair_options) = dict_b
            a_min = a_source_iso in self.minority_languages
            b_min = b_source_iso in self.minority_languages

            def error_string(iso):
                return "The name corresponding to iso {} is missing from language_names.yaml".format(
                    iso
                )

            # TODO: Also sort reverse pairs together somehow.
            reverse_pairs = (
                (a_source_iso, a_target_iso) == (b_target_iso, b_source_iso)
            ) or ((a_target_iso, a_source_iso) == (b_source_iso, b_target_iso))

            a_source_name = NAMES.get(a_source_iso)
            if a_source_name is None:
                raise NameError(error_string(a_source_iso))
            b_source_name = NAMES.get(b_source_iso)
            if b_source_name is None:
                raise NameError(error_string(b_source_iso))

            a_target_name = NAMES.get(a_target_iso)
            if a_target_name is None:
                raise NameError(error_string(a_target_iso))
            b_target_name = NAMES.get(b_target_iso)
            if b_target_name is None:
                raise NameError(error_string(b_target_iso))

            def gt_return(a, b):
                if a > b:
                    return -2
                elif a < b:
                    return 2
                else:
                    return 0

            def gt_return_reverse(a, b):
                if a > b:
                    return 2
                elif a < b:
                    return -2
                else:
                    return 0

            if reverse_pairs:
                return 0

            if a_source_iso == b_source_iso:
                return gt_return_reverse(a_target_name, b_target_name)

            # cases of equal status
            if (a_min and b_min) or (not a_min and not b_min):
                return gt_return(a_source_name, b_source_name)

            # one is a minority lang, and one is not
            if a_min and not b_min:
                return -2
            if b_min and not a_min:
                return 2

        if not hasattr(self, "_pair_definitions_grouped_source"):
            pairs = sorted(self.pair_definitions.items(), key=group_by_source_first)
            pairs = sorted(pairs, key=cmp_to_key(minority_langs_first))

            grouped_pairs = defaultdict(list)
            for p in pairs:
                if p[0][0] in self.minority_languages:
                    grouped_pairs[p[0][0]].append(p)
                if p[0][1] in self.minority_languages:
                    grouped_pairs[p[0][1]].append(p)
                if (p[0][0] not in self.minority_languages) and (
                    p[0][1] not in self.minority_languages
                ):
                    grouped_pairs[p[0][0]].append(p)
                    grouped_pairs[p[0][1]].append(p)
            # sort by alphabetical order of language name

            def lang_name(n):
                return NAMES.get(n)

            grouped_pairs_name_order = {}
            for k in sorted(grouped_pairs.keys(), key=lang_name):
                if not k == "fin":
                    grouped_pairs_name_order[k] = grouped_pairs[k]

            self._pair_definitions_grouped_source = grouped_pairs_name_order

        return self._pair_definitions_grouped_source

    @cached_property
    def morphologies(self):
        """Read the entries in the 'Morphology' section of the config file,
        check existence of the files for 'tool' and language model files,
        and return a dict that maps language to a Morphology object. Which
        exact class depends on the 'format' field in the config. 'xfst' would
        map to a XFST object, 'hfst' a HFST object, and 'pyhfst' a PyHFST
        object."""
        _morphologies = {}

        from neahtta.morphology import XFST, Morphology, HFST, PyHFST

        formats = {
            "xfst": XFST,
            "hfst": HFST,
            "pyhfst": PyHFST,
        }

        for iso, morph_dict_item in self.yaml.get("Morphology", {}).items():
            conf_format = morph_dict_item["format"]
            tool_class = formats[conf_format]

            entry = MorphologyEntry.from_config_dict(iso, morph_dict_item)

            tool_instance = tool_class(
                lookup_tool=entry.tool,
                fst_file=entry.file,
                ifst_file=entry.ifile,
                options=entry.options,
            )

            tagsets = self.tagset_definitions.get(iso, {})
            _morphologies[iso] = tool_instance.applyMorph(
                Morphology(iso, tagsets=tagsets)
            )

        return _morphologies

    def test(self, silent=False):
        for item in dir(self):
            if not item.startswith("_") and item != "test":
                if silent:
                    self.__getattribute__(item)
                else:
                    print(item)
                    print(self.__getattribute__(item))

    def read_multiword_list(self, path):
        """Read the user-specified MWE list."""
        try:
            with open(os.path.join(os.path.dirname(__file__), path)) as f:
                lines = f.readlines()
        except Exception as e:
            print(f" * Unable to find multiword_list <{path}>")
            print(e)
            sys.exit()

        def drop_line_comment(line):
            return line.startswith("#")

        def strip_line_end_comment(line):
            line, _, _comment = line.partition("#")
            return line

        def clean_line(line):
            return line.strip()

        multiword_list = [line.strip() for line in lines if line.strip()]

        # Couldn't help myself.
        return list(
            map(
                strip_line_end_comment,
                list(filter(drop_line_comment, list(map(clean_line, multiword_list)))),
            )
        )

    @cached_property
    def reader_settings(self):
        return self.yaml.get("ReaderConfig", {}).get("Settings", {})

    @cached_property
    def reader_options(self):
        reader_options = self.yaml.get("ReaderConfig", {})

        reader_defaults = {
            "word_regex": DEFAULT_WORD_REGEX,
            "word_regex_opts": DEFAULT_WORD_REGEX_OPTS,
            "multiword_lookups": False,
        }

        for L, conf in reader_options.items():
            if L == "Settings":
                continue
            wr = conf.get("word_regex", False)
            wro = conf.get("word_regex_opts", False)
            if wr:
                reader_options[L]["word_regex"] = wr.strip()
            else:
                reader_options[L]["word_regex_opts"] = DEFAULT_WORD_REGEX
            if wro:
                reader_options[L]["word_regex_opts"] = wro.strip()
            else:
                reader_options[L]["word_regex_opts"] = DEFAULT_WORD_REGEX_OPTS
            mwe_range = conf.get("multiword_range", False)
            if mwe_range:
                _min, _, _max = mwe_range.partition(",")
                try:
                    _min = int(_min.strip().replace("-", ""))
                except ValueError:
                    _min = False

                try:
                    _max = int(_max.strip().replace("+", ""))
                except ValueError:
                    _max = False

                if _min and _max:
                    reader_options[L]["multiword_range"] = (_min, _max)
                else:
                    print(" * Multiword range must specify min _and_ max. ")
                    print("If there is no min or max, specify 0")
                    print(f"   got: {mwe_range}")
                    print("   expecting:")
                    print('    multiword_range: "-2,+2"')
                    print("  or ")
                    print('    multiword_range: "0,+2"')
                    sys.exit()

        all_isos = list(
            set(list(self.languages.keys()) + list(self.yaml.get("Morphology").keys()))
        )
        missing_isos = [a for a in all_isos if a not in reader_options.keys()]

        for L in missing_isos:
            reader_options[L] = reader_defaults

        return reader_options

    def add_optional_routes(self):
        from neahtta.nds_lexicon import lexicon_overrides as lexicon

        # add korp_routes
        korp_pairs = [
            pair
            for pair, conf in self.pair_definitions.items()
            if "show_korp_search" in conf
        ]

        searches = [tuple(["korp_wordform"] + list(p)) for p in korp_pairs]

        lexicon.external_search(*searches)(external_korp_url)

    def prepare_lexica(self):
        print("  Config.prepare_lexica(self)")
        from neahtta.nds_lexicon import Lexicon

        print("  Config.prepare_lexica(self) > self.lexicon = Lexicon(self)")
        self.lexicon = Lexicon(self)
        print("  DONE Config.prepare_lexica(self) > self.lexicon = Lexicon(self)")

        # anders: looks unused, but this reads the property, to cache it
        self.tag_filters

    def resolve_original_pair(self, _from, _to):
        """For a language pair alternate, return the original language pair
        that is the parent to the alternate.

        TODO: write tests.
        """
        from flask import request

        # mobile test for most common browsers
        mobile = False
        if request.user_agent.platform in ["iphone", "android"]:
            mobile = True

        iphone = False
        if request.user_agent.platform == "iphone":
            iphone = True

        # Variables to control presentation based on variants present
        current_pair = self.pair_definitions.get((_from, _to), {})
        reverse_pair = self.pair_definitions.get((_to, _from), {})

        swap_from, swap_to = (_to, _from)

        current_pair_variants = current_pair.get("input_variants", False)
        has_variant = bool(current_pair_variants)
        has_mobile_variant = False

        if has_variant:
            _mobile_variants = list(
                filter(lambda x: x.get("type", "") == "mobile", current_pair_variants)
            )
            if len(_mobile_variants) > 0:
                has_mobile_variant = _mobile_variants[0]

        variant_dictionaries = self.variant_dictionaries
        is_variant, orig_pair = False, ()

        if variant_dictionaries:
            variant = variant_dictionaries.get((_from, _to), False)
            is_variant = bool(variant)
            if is_variant:
                orig_pair = variant.get("orig_pair")

        # Now we check if the reverse has variants for swapping
        # If there is a reverse pair with variants, get the mobile one as a
        # preference for swapping if the user is a mobile user, otherwise
        # just the default.

        reverse_has_variant = False
        if is_variant:
            _reverse_is_variant = self.variant_dictionaries.get(orig_pair, False)
            pair_settings = self.pair_definitions[orig_pair]
        else:
            _reverse_is_variant = self.variant_dictionaries.get((_to, _from), False)
            pair_settings = self.pair_definitions.get((_from, _to), False)

        _reverse_variants = reverse_pair.get("input_variants", False)

        if _reverse_variants:
            _mobile_variants = list(
                filter(lambda x: x.get("type", "") == "mobile", _reverse_variants)
            )
            _standard_variants = list(
                filter(lambda x: x.get("type", "") == "standard", _reverse_variants)
            )
            if mobile and len(_mobile_variants) > 0:
                _preferred_swap = _mobile_variants[0]
                _short_name = _preferred_swap.get("short_name")
                swap_from = _short_name
        else:
            if is_variant:
                swap_to, swap_from = orig_pair

        # Get the description and such for the variaint in the
        # original definition

        variant_options = False
        if is_variant:
            orig_pair_variants = pair_settings.get("input_variants")
            variant_opts = list(
                filter(
                    lambda x: x.get("short_name") == _from
                    and not x.get("display_variant", False),
                    orig_pair_variants,
                )
            )
            if len(variant_opts) > 0:
                variant_options = variant_opts[0]

            d_variant_opts = list(
                filter(
                    lambda x: x.get("short_name") == _to
                    and x.get("display_variant", False),
                    orig_pair_variants,
                )
            )
            if len(d_variant_opts) > 0:
                variant_options = d_variant_opts[0]

        else:
            if pair_settings:
                orig_pair_variants = pair_settings.get("input_variants")
                if orig_pair_variants:
                    variant_opts = list(
                        filter(
                            lambda x: x.get("short_name") == _from, orig_pair_variants
                        )
                    )
                    if len(variant_opts) > 0:
                        variant_options = variant_opts[0]

        pair_opts = {
            "has_mobile_variant": has_mobile_variant,
            "has_variant": has_variant,
            "is_variant": is_variant,
            "variant_options": variant_options,
            "orig_pair": orig_pair,
            "swap_to": swap_to,
            "swap_from": swap_from,
        }
        return pair_settings, pair_opts

    def validate(self):
        """Validates the loaded Config against the schema defined in
        configs/config_schema.json.
        If validation is NOT succesful, the process exits.
        If validation IS successful, None is returned."""
        import jsonschema
        import json

        with open("neahtta/configs/config_schema.json") as f:
            schema = json.load(f)

        try:
            jsonschema.validate(instance=self.yaml, schema=schema)
        except jsonschema.exceptions.ValidationError as e:
            print(e, file=sys.stderr)
            print("", file=sys.stderr)
            sys.exit(f"Validation errors in configuration file: {self.filename}")

        # Check things that is hard/impossible to do in the schema validation,
        # namely: that files exist, and if format is hfst or xfst, that the
        # path to the tool is given, and that it exists
        for lang, obj in self.yaml.get("Morphology", {}).items():
            # this does file checks
            MorphologyEntry.from_config_dict(lang, obj)


class MorphologyEntry:
    """An object in Morphology section of a config file."""

    @classmethod
    def from_config_dict(cls, lang, obj_dict):
        from neahtta.utils.find_langmodel_file import find_langmodel_file
        from neahtta.utils.find_langmodel_file import SEARCH_PATHS

        errors = []

        inst = cls()
        inst.format = obj_dict["format"]
        inst.tool = obj_dict.get("tool")

        # checking field: tool
        if isinstance(inst.tool, list):
            errors.append(
                (
                    "tool",
                    "can no longer be a list\n)" "Use the absolute path as a string",
                )
            )
        else:
            # tool is not a list
            if inst.tool is None:
                if inst.format == "hfst" or inst.format == "xfst":
                    errors.append(
                        (
                            "tool",
                            "missing! Path to tool binary is required when "
                            "format is hfst or xfst",
                        )
                    )
            else:
                # tool is specified (not None)
                if not os.path.isabs(inst.tool):
                    errors.append(("tool", "path must be absolute"))
                else:
                    # finally search
                    if not os.path.exists(inst.tool):
                        errors.append(("tool", f"File not found: {inst.tool}"))

        # checking field: file
        inst.file = obj_dict["file"]
        if isinstance(inst.file, list):
            errors.append(
                (
                    "file",
                    "changed in 'restructuring':\n"
                    "the path can no longer be a list. "
                    "Use a relative path, as a string, to "
                    "the file as it exists under /opt/smi, "
                    "/usr/share/giella, or /usr/local/share/"
                    "giella",
                )
            )
        else:
            if found := find_langmodel_file(inst.file):
                inst.file = found
            else:
                errors.append(
                    (
                        "file",
                        "file not found in any of the "
                        "search paths. Searched in "
                        f"{SEARCH_PATHS}. Set the env var "
                        "LANGMODELS to a custom path if the "
                        "langmodel file is not located in "
                        "any of the standard locations.",
                    )
                )

        inst.ifile = obj_dict.get("inverse_file")
        if isinstance(inst.ifile, list):
            errors.append(
                (
                    "inverse_file",
                    "changed in 'restructuring':\n"
                    "the path can no longer be a list. "
                    "Use a relative path, as a string, to "
                    "the file as it exists under /opt/smi, "
                    "/usr/share/giella, or /usr/local/share/"
                    "giella",
                )
            )
        else:
            if isinstance(inst.ifile, str):
                if found := find_langmodel_file(inst.ifile):
                    inst.ifile = found
                else:
                    errors.append(
                        (
                            "inverse_file",
                            "file not found in any of the "
                            "search paths. Searched in "
                            f"{SEARCH_PATHS}. Set the env var "
                            "LANGMODELS to a custom path if the "
                            "langmodel file is not located in "
                            "any of the standard locations.",
                        )
                    )

        inst.options = obj_dict.get("options")

        if errors:
            msg = [f"Error in config: Section 'Morphology::{lang}'"]
            for i, (field, error) in enumerate(errors, start=1):
                msg.append(f"  {i}: field '{field}': {error}")
            sys.exit("\n".join(msg))

        return inst
