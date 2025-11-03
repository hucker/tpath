"""
Time property implementation for TPath.

Handles different time types (ctime, mtime, atime) with age calculation.
"""

import time
from datetime import datetime
from pathlib import Path

from ._age import Age


class Time:
    """Property class for handling different time types (ctime, mtime, atime) with age calculation."""
    
    def __init__(self, path: Path, time_type: str, base_time: datetime):
        self.path = path
        self.time_type = time_type
        self.base_time = base_time
        
    @property
    def age(self) -> Age:
        """Get age property for this time type."""
        if not self.path.exists():
            return Age(self.path, time.time(), self.base_time)
        
        stat = self.path.stat()
        if self.time_type == 'ctime':
            timestamp = stat.st_ctime
        elif self.time_type == 'mtime':
            timestamp = stat.st_mtime
        elif self.time_type == 'atime':
            timestamp = stat.st_atime
        else:
            timestamp = stat.st_ctime  # default to creation time
            
        return Age(self.path, timestamp, self.base_time)
    
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


__all__ = ['Time']