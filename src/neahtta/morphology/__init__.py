""" Morphology module.
"""

from __future__ import absolute_import
from .morphology import (Tagsets, Tagset, Tag, HFST, XFST, OBT, Morphology,
                        generation_overrides)

__all__ = [
    'XFST', 'HFST', 'OBT', 'Morphology', 'generation_overrides', 'Tag',
    'Tagsets', 'Tagset'
]
