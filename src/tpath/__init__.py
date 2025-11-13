"""
TPath - A pathlib extension with time-based age and size utilities.

This package provides enhanced pathlib functionality with lambda-based
age and size operations. Users can import directly from tpath without
needing to know the internal package structure.

Examples:
    >>> from tpath import TPath, Size
    >>> path = TPath("myfile.txt")
    >>> path.age.days
    >>> path.size.gb
    >>> Size.parse("1.5GB")
"""

import importlib
from pathlib import Path

__version__ = "0.1.0"
__author__ = "Chuck Bass"

# Core exports - always available
from frist import Age, Cal

from ._core import TPath
from ._size import Size
from ._time import PathTime, TimeType
from ._utils import matches

# Base __all__ with core exports
__all__ = [
    "TPath",
    "Age",
    "Cal",
    "Size",
    "PathTime",
    "TimeType",
    "matches",
]
