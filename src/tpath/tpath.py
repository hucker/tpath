"""
TPath - A pathlib extension with time-based age and size utilities using lambdas.

This module provides backward compatibility by re-exporting all classes.
New code should import directly from the tpath package.

Deprecated: Import from tpath package instead:
    from tpath import TPath, SizeProperty, AgeProperty, TimeProperty
"""

# Re-export everything for backward compatibility
from .core import TPath, tpath
from .age import AgeProperty
from .size import SizeProperty
from .time_property import TimeProperty

# For backward compatibility and ease of import
__all__ = ['TPath', 'tpath', 'SizeProperty', 'AgeProperty', 'TimeProperty']
