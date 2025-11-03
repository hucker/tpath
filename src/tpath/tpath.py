"""
TPath - A pathlib extension with time-based age and size utilities using lambdas.

This module provides re-exports of all classes for convenience.
"""

# Re-export everything for convenience
from ._age import Age
from ._core import TPath, tpath
from ._size import Size
from ._time import Time

# Public API
__all__ = ["TPath", "tpath", "Size", "Age", "Time"]
