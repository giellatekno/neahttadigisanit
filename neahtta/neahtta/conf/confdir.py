"""
This module is for organizing language-specific differences between
morphology and lexicon, and is currently used mostly for managing
systematic changes in generation paradigms based on the lexicon.

Overrides are grouped by language for convenience, but could really be
in any order, so long as they are imported into __init__.py here, and
thus able to be imported by the main module. You'll see whether
they're registered when starting the web service.

New files should be imported here, and should also begin generally by
importing the following module to produce replacement functions.

    from morphology import generation_overrides

"""

import imp
import os
import sys


def _getlangs(app):
    configs_path = app.config.language_specific_rules_path

    def _popname(n):
        name, _, suffix = n.partition(".")
        return name

    filenames = [
        f
        for f in os.listdir(configs_path)
        if f.endswith(".py") and not f.startswith((".", "__"))
    ]

    return list(map(_popname, filenames))


def _import(app, m):
    path = os.path.join(app.config.language_specific_rules_path, m + ".py")
    module_name = "conf." + m

    return imp.load_source(module_name, path)


def load_overrides(app):
    """Search for .py files containing various overrides that we want
    to load.
    """
    config_languages = set(app.config.languages.keys())
    languages_in_dir = set(_getlangs(app))

    languages_to_override = list(config_languages & languages_in_dir)

    if not languages_to_override:
        print(
            "* No overrides. If this is not what you want, check\n"
            "  that the language in question is defined in the present config\n"
            "  file, and that the language ISO matches the ISOs in \n"
            "  configs/language_specific_configs/\n"
            " \n",
            f"   Languages in config file: {', '.join(config_languages)}\n",
            f"   Overrides available for: {', '.join(languages_in_dir)}\n",
            file=sys.stderr,
        )

    language_overrides = []
    for m in languages_to_override:
        language_overrides.append(_import(app, m))
    return language_overrides
