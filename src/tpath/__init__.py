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
    >>> Size.fromstr("1.5GB")
"""

# Import all public classes and functions
from .core import TPath, tpath
from .age import Age
from .size import Size
from .time_property import Time

__version__ = "0.1.0"
__author__ = "Your Name"

# Public API - users can import any of these directly
__all__ = [
    'TPath',           # Main TPath class
    'tpath',           # Convenience function
    'Age',             # Age calculation class
    'Size',            # Size calculation class
    'Time',            # Time property class
]