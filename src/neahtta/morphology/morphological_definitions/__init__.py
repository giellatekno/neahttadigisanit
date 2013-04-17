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

    from morphology import generation_overrides as rewrites

"""


from sme import *
from sma import *
