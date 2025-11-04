"""
Core TPath implementation.

Main TPath class that extends pathlib.Path with age and size functionality.
"""

from datetime import datetime
from functools import cached_property
from pathlib import Path

from ._age import Age
from ._size import Size
from ._time import Time


class TPath(Path):
    """
    Extended Path class with age and size functionality using lambdas.

    Provides first-class age functions and size utilities for file operations.

    Examples:
        >>> path = TPath("myfile.txt")
        >>> path.age.days  # Age in days since creation
        >>> path.atime.age.hours  # Hours since last access
        >>> path.size.gb  # Size in gigabytes
        >>> path.size.gib  # Size in gibibytes
        >>> TPath.size.parse("1.5GB")  # Parse size string
    """

    _base_time: datetime

    def __new__(cls, *args, **kwargs):
        # Create the path instance - Path doesn't accept custom kwargs
        self = super().__new__(cls, *args, **kwargs)

        # Set our custom attributes with default value
        object.__setattr__(self, "_base_time", datetime.now())

        return self

    @cached_property
    def _cached_stat(self):
        """Cache the stat result to avoid repeated filesystem calls."""
        if not self.exists():
            return None
        return self.stat()

    @property
    def age(self) -> Age:
        """Get age property based on creation time."""
        return Time(self, "ctime", self._base_time).age

    @property
    def ctime(self) -> Time:
        """Get creation time property."""
        return Time(self, "ctime", self._base_time)

    @property
    def mtime(self) -> Time:
        """Get modification time property."""
        return Time(self, "mtime", self._base_time)

    @property
    def atime(self) -> Time:
        """Get access time property."""
        return Time(self, "atime", self._base_time)

    @property
    def create(self) -> Time:
        """Get creation time property (alias for ctime)."""
        return Time(self, "create", self._base_time)

    @property
    def modify(self) -> Time:
        """Get modification time property (alias for mtime)."""
        return Time(self, "modify", self._base_time)

    @property
    def access(self) -> Time:
        """Get access time property (alias for atime)."""
        return Time(self, "access", self._base_time)

    @property
    def size(self) -> Size:
        """Get size property."""
        return Size(self)

    def with_base_time(self, base_time: datetime) -> "TPath":
        """Create a new TPath with a different base time for age calculations."""
        new_path = TPath(str(self))
        object.__setattr__(new_path, "_base_time", base_time)
        return new_path


__all__ = ["TPath"]
