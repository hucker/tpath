"""
Chronos - Comprehensive datetime utility package.

A standalone datetime package for age calculations, calendar windows, and datetime parsing.
Designed to be reusable beyond file operations.

Main exports:
    Chronos: Main datetime utility class
    Age: Duration calculations with multiple time units
    Cal: Calendar window filtering functionality
"""

from ._chronos import Chronos
from ._age import Age
from ._cal import Cal

__version__ = "1.0.0"
__author__ = "TPath Project"

__all__ = ["Chronos", "Age", "Cal"]