"""
TPath - A pathlib extension with time-based age and size utilities using lambdas.

Provides first-class age and size functions for file operations.
"""

import re
import time
from datetime import datetime
from pathlib import Path
from typing import Union, Optional


class SizeProperty:
    """Property class for handling file size operations with various units."""
    
    def __init__(self, path: Path):
        self.path = path
        
    @property
    def bytes(self) -> int:
        """Get file size in bytes."""
        return self.path.stat().st_size if self.path.exists() else 0
    
    @property
    def kb(self) -> float:
        """Get file size in kilobytes (1000 bytes)."""
        return self.bytes / 1000
    
    @property
    def mb(self) -> float:
        """Get file size in megabytes (1000^2 bytes)."""
        return self.bytes / 1000**2
    
    @property
    def gb(self) -> float:
        """Get file size in gigabytes (1000^3 bytes)."""
        return self.bytes / 1000**3
    
    @property
    def tb(self) -> float:
        """Get file size in terabytes (1000^4 bytes)."""
        return self.bytes / 1000**4
    
    @property
    def kib(self) -> float:
        """Get file size in kibibytes (1024 bytes)."""
        return self.bytes / 1024
    
    @property
    def mib(self) -> float:
        """Get file size in mebibytes (1024^2 bytes)."""
        return self.bytes / 1024**2
    
    @property
    def gib(self) -> float:
        """Get file size in gibibytes (1024^3 bytes)."""
        return self.bytes / 1024**3
    
    @property
    def tib(self) -> float:
        """Get file size in tebibytes (1024^4 bytes)."""
        return self.bytes / 1024**4
    
    @staticmethod
    def fromstr(size_str: str) -> int:
        """
        Parse a size string and return the size in bytes.
        
        Examples:
            "100" -> 100 bytes
            "1KB" -> 1000 bytes
            "1KiB" -> 1024 bytes
            "2.5MB" -> 2500000 bytes
            "1.5GiB" -> 1610612736 bytes
        """
        size_str = size_str.strip().upper()
        
        # Handle plain numbers (bytes)
        if size_str.isdigit():
            return int(size_str)
        
        # Regular expression to parse size with unit
        match = re.match(r'^(\d+(?:\.\d+)?)\s*([KMGT]I?B?)$', size_str)
        if not match:
            raise ValueError(f"Invalid size format: {size_str}")
        
        value = float(match.group(1))
        unit = match.group(2)
        
        # Define multipliers
        binary_units = {
            'B': 1,
            'KB': 1000,
            'MB': 1000**2,
            'GB': 1000**3,
            'TB': 1000**4,
            'KIB': 1024,
            'MIB': 1024**2,
            'GIB': 1024**3,
            'TIB': 1024**4,
        }
        
        if unit not in binary_units:
            raise ValueError(f"Unknown unit: {unit}")
        
        return int(value * binary_units[unit])


class AgeProperty:
    """Property class for handling file age operations."""
    
    def __init__(self, path: Path, timestamp: float, base_time: datetime):
        self.path = path
        self.timestamp = timestamp
        self.base_time = base_time
        
    @property
    def seconds(self) -> float:
        """Get age in seconds."""
        if not self.path.exists():
            return 0
        file_time = datetime.fromtimestamp(self.timestamp)
        return (self.base_time - file_time).total_seconds()
    
    @property
    def minutes(self) -> float:
        """Get age in minutes."""
        return self.seconds / 60
    
    @property
    def hours(self) -> float:
        """Get age in hours."""
        return self.seconds / 3600
    
    @property
    def days(self) -> float:
        """Get age in days."""
        return self.seconds / 86400
    
    @property
    def weeks(self) -> float:
        """Get age in weeks."""
        return self.days / 7
    
    @property
    def months(self) -> float:
        """Get age in months (approximate - 30.44 days)."""
        return self.days / 30.44
    
    @property
    def years(self) -> float:
        """Get age in years (approximate - 365.25 days)."""
        return self.days / 365.25


class TimeProperty:
    """Property class for handling different time types (ctime, mtime, atime) with age calculation."""
    
    def __init__(self, path: Path, time_type: str, base_time: datetime):
        self.path = path
        self.time_type = time_type
        self.base_time = base_time
        
    @property
    def age(self) -> AgeProperty:
        """Get age property for this time type."""
        if not self.path.exists():
            return AgeProperty(self.path, time.time(), self.base_time)
        
        stat = self.path.stat()
        if self.time_type == 'ctime':
            timestamp = stat.st_ctime
        elif self.time_type == 'mtime':
            timestamp = stat.st_mtime
        elif self.time_type == 'atime':
            timestamp = stat.st_atime
        else:
            timestamp = stat.st_ctime  # default to creation time
            
        return AgeProperty(self.path, timestamp, self.base_time)
    
    @property
    def timestamp(self) -> float:
        """Get the raw timestamp for this time type."""
        if not self.path.exists():
            return 0
        
        stat = self.path.stat()
        if self.time_type == 'ctime':
            return stat.st_ctime
        elif self.time_type == 'mtime':
            return stat.st_mtime
        elif self.time_type == 'atime':
            return stat.st_atime
        else:
            return stat.st_ctime
    
    @property
    def datetime(self):
        """Get the datetime object for this time type."""
        return datetime.fromtimestamp(self.timestamp)


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
        >>> TPath.size.fromstr("1.5GB")  # Parse size string
    """
    
    _base_time: datetime
    
    def __new__(cls, *args, **kwargs):
        # Extract our custom arguments
        base_time = kwargs.pop('base_time', None)
        
        # Create the path instance
        if args:
            self = super().__new__(cls, *args, **kwargs)
        else:
            self = super().__new__(cls, **kwargs)
        
        # Set our custom attributes
        object.__setattr__(self, '_base_time', base_time or datetime.now())
        
        return self
    
    @property
    def age(self) -> AgeProperty:
        """Get age property based on creation time."""
        return TimeProperty(self, 'ctime', self._base_time).age
    
    @property
    def ctime(self) -> TimeProperty:
        """Get creation time property."""
        return TimeProperty(self, 'ctime', self._base_time)
    
    @property
    def mtime(self) -> TimeProperty:
        """Get modification time property."""
        return TimeProperty(self, 'mtime', self._base_time)
    
    @property
    def atime(self) -> TimeProperty:
        """Get access time property."""
        return TimeProperty(self, 'atime', self._base_time)
    
    @property
    def size(self) -> SizeProperty:
        """Get size property."""
        return SizeProperty(self)
    
    def with_base_time(self, base_time: datetime) -> 'TPath':
        """Create a new TPath with a different base time for age calculations."""
        new_path = TPath(str(self))
        object.__setattr__(new_path, '_base_time', base_time)
        return new_path


# Convenience functions
def tpath(path: Union[str, Path], base_time: Optional[datetime] = None) -> TPath:
    """Create a TPath object."""
    new_path = TPath(path)
    if base_time:
        object.__setattr__(new_path, '_base_time', base_time)
    return new_path


# For backward compatibility and ease of import
__all__ = ['TPath', 'tpath', 'SizeProperty', 'AgeProperty', 'TimeProperty']
