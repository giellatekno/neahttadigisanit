""" Morphology module.
"""

from __future__ import absolute_import
from .morphology import (Tagsets, Tagset, Tag, HFST, PyHFST, XFST, OBT, Morphology,
                        generation_overrides)

__all__ = [
    'XFST', 'HFST', 'PyHFST', 'OBT', 'Morphology', 'generation_overrides', 'Tag',
    'Tagsets', 'Tagset'
]
