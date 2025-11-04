"""
Time property implementation for TPath.

Handles different time types (ctime, mtime, atime) with age calculation.
"""

import time
from datetime import datetime as dt
from pathlib import Path
from typing import Literal

from ._age import Age

TimeType = Literal["ctime", "mtime", "atime", "create", "modify", "access"]


class Time:
    """Property class for handling different time types (ctime, mtime, atime) with age calculation."""

    def __init__(self, path: Path, time_type: TimeType, base_time: dt):
        self.path = path
        # Normalize time_type aliases to standard names
        self.time_type = self._normalize_time_type(time_type)
        self.base_time = base_time

    @staticmethod
    def _normalize_time_type(time_type: TimeType) -> Literal["ctime", "mtime", "atime"]:
        """Normalize time_type aliases to standard names."""
        if time_type in ("create", "ctime"):
            return "ctime"
        elif time_type in ("modify", "mtime"):
            return "mtime"
        elif time_type in ("access", "atime"):
            return "atime"
        else:
            # This should never happen with proper typing, but provide a fallback
            return "ctime"

    def _get_stat(self):
        """Get stat result, using cache if available."""
        if hasattr(self.path, "_cached_stat"):
            return self.path._cached_stat
        else:
            return self.path.stat() if self.path.exists() else None

    @property
    def age(self) -> Age:
        """Get age property for this time type."""
        if not self.path.exists():
            return Age(self.path, time.time(), self.base_time)

        stat = self._get_stat()
        if stat is None:
            return Age(self.path, time.time(), self.base_time)

        if self.time_type == "ctime":
            timestamp = stat.st_ctime
        elif self.time_type == "mtime":
            timestamp = stat.st_mtime
        elif self.time_type == "atime":
            timestamp = stat.st_atime
        else:
            timestamp = stat.st_ctime  # default to creation time

        return Age(self.path, timestamp, self.base_time)

    @property
    def timestamp(self) -> float:
        """Get the raw timestamp for this time type."""
        if not self.path.exists():
            return 0

        stat = self._get_stat()
        if stat is None:
            return 0

        if self.time_type == "ctime":
            return stat.st_ctime
        elif self.time_type == "mtime":
            return stat.st_mtime
        elif self.time_type == "atime":
            return stat.st_atime
        else:
            return stat.st_ctime

    @property
    def datetime(self):
        """Get the datetime object for this time type."""
        return dt.fromtimestamp(self.timestamp)

    @staticmethod
    def parse(time_str: str) -> dt:
        """
        Parse a time string and return a datetime object.

        Examples:
            "2023-12-25" -> datetime object for Dec 25, 2023
            "2023-12-25 14:30" -> datetime object for Dec 25, 2023 2:30 PM
            "2023-12-25T14:30:00" -> ISO format datetime
            "1640995200" -> datetime from Unix timestamp
        """
        time_str = time_str.strip()

        # Handle Unix timestamp (all digits)
        if time_str.isdigit():
            return dt.fromtimestamp(float(time_str))

        # Try common datetime formats
        formats = [
            "%Y-%m-%d",  # 2023-12-25
            "%Y-%m-%d %H:%M",  # 2023-12-25 14:30
            "%Y-%m-%d %H:%M:%S",  # 2023-12-25 14:30:00
            "%Y-%m-%dT%H:%M:%S",  # 2023-12-25T14:30:00 (ISO)
            "%Y-%m-%dT%H:%M:%SZ",  # 2023-12-25T14:30:00Z (ISO with Z)
            "%Y/%m/%d",  # 2023/12/25
            "%Y/%m/%d %H:%M",  # 2023/12/25 14:30
            "%m/%d/%Y",  # 12/25/2023
            "%m/%d/%Y %H:%M",  # 12/25/2023 14:30
        ]

        for fmt in formats:
            try:
                return dt.strptime(time_str, fmt)
            except ValueError:
                continue

        raise ValueError(f"Unable to parse time string: {time_str}")


__all__ = ["Time", "TimeType"]
