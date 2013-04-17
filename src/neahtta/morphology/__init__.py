""" Morphology module.
"""

from morphology import ( Tagsets
                       , Tag
                       , XFST
                       , OBT
                       , Morphology
                       , generation_overrides
                       )

# Import to register the functions
import morphological_definitions

__all__ = [ 'XFST'
          , 'OBT'
          , 'Morphology'
          , 'morphological_definitions'
          , 'generation_overrides'
          ]
