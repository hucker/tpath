"""
TPath - A pathlib extension with time-based age and size utilities using lambdas.

This module provides backward compatibility by re-exporting all classes.
New code should import directly from the tpath package.

Deprecated: Import from tpath package instead:
    from tpath import TPath, Size, Age, Time
"""

# Re-export everything for backward compatibility
from ._core import TPath, tpath
from ._age import Age
from ._size import Size
from ._time import Time

# For backward compatibility - keep old names available
AgeProperty = Age
SizeProperty = Size
TimeProperty = Time

# For backward compatibility and ease of import
__all__ = ['TPath', 'tpath', 'Size', 'SizeProperty', 'Age', 'AgeProperty', 'Time', 'TimeProperty']
