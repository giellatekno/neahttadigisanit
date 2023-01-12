""" Morphology module.
"""

from .morphology import (Tagsets, Tagset, Tag, HFST, PyHFST, XFST, OBT, Morphology,
                        generation_overrides)

__all__ = [
    'XFST', 'HFST', 'PyHFST', 'OBT', 'Morphology', 'generation_overrides', 'Tag',
    'Tagsets', 'Tagset'
]
