# -*- encoding: utf-8 -*-
"""
mrj-specific overrides.

"""

from morpholex import morpholex_overrides as morpholex

from configs.language_specific_rules.common import remove_blank, match_homonymy_entries

morpholex.post_morpho_lexicon_override(
    'mrj'
)(match_homonymy_entries)
