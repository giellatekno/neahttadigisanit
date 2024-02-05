# -*- encoding: utf-8 -*-
"""
mrj-specific overrides.

"""

from neahtta.configs.language_specific_rules.common import (
    match_homonymy_entries,
    remove_blank,
)
from neahtta.morpholex import morpholex_overrides as morpholex

morpholex.post_morpho_lexicon_override("mrj")(match_homonymy_entries)
