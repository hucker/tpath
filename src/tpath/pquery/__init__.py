"""
PQuery - Path querying functionality for TPath objects.

Provides a pathql-inspired API for querying files with lambda expressions.
"""

from ._pquery import pquery, PQuery, pfilter, pfind, pfirst, pexists, pcount

__all__ = ["pquery", "PQuery", "pfilter", "pfind", "pfirst", "pexists", "pcount"]

__version__ = "1.0.0"