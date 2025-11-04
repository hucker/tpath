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
    
    IMPORTANT - Stat Caching Behavior:
    ===================================
    TPath objects cache their stat() result on first access and reuse it for all subsequent
    property calculations (size, age, timestamps, etc.). This creates a consistent "snapshot"
    of the file state that enforces atomic decision-making.
    
    Benefits:
    - Consistent decisions: All properties (size, age, existence) use the same stat snapshot
    - No race conditions: File can't change between size check and age calculation
    - Performance: Multiple property accesses only call stat() once
    - Predictable behavior: Same TPath instance always returns same values

    This matches the pattern of using a single timestamp for all files in a glob operation,
    ensuring uniform timing across batch operations.
    
    LIMITATION - External Race Conditions:
    =====================================
    Stat caching provides internal consistency but CANNOT prevent external file changes
    between analysis and file operations. This is a fundamental filesystem limitation
    that requires OS-level coordination (file locking, snapshots, or atomic copies).
    
    Example Race Condition:
        file = TPath("data.txt")
        if file.size.bytes > 1000:      # Cached as large file
            # File could be truncated/deleted HERE by external process
            data = file.read_text()      # May fail or read different content!
    
    Defensive Programming Recommended:
        if file.size.bytes > 1000:
            try:
                data = file.read_text()
            except (FileNotFoundError, PermissionError) as e:
                # Handle external file changes gracefully

    Example - Atomic Analysis:
        file = TPath("data.txt")
        if file.exists() and file.size.mb > 10 and file.age.hours < 1:
            # All three conditions use the same stat snapshot - no race conditions!
            process_large_recent_file(file)
    
    For fresh data, create a new TPath instance:
        fresh_file = TPath("data.txt")  # New snapshot with current stat data

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

    # Stat Caching Implementation
    # ============================
    # This caching creates a consistent "snapshot" of file state for atomic decision-making.
    # Once stat() is called, all subsequent property accesses (size, age, timestamps) use
    # the same cached result, preventing race conditions and ensuring consistent analysis.

    @cached_property
    def _stat_cache(self):
        """Cache the stat result to avoid repeated filesystem calls."""
        try:
            return super().stat()
        except (OSError, FileNotFoundError):
            return None

    def stat(self, *, follow_symlinks: bool = True):
        """Override stat() to use cached result when possible."""
        if not follow_symlinks:
            # For symlinks with follow_symlinks=False, don't use cache
            return super().stat(follow_symlinks=False)
        
        # Use cached result for normal stat() calls
        cached_result = self._stat_cache
        if cached_result is None:
            # File doesn't exist, call parent to get proper exception
            return super().stat(follow_symlinks=follow_symlinks)
        return cached_result

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
