"""
Age property implementation for TPath.

Handles file age calculations in various time units.
"""

from datetime import datetime
from pathlib import Path


class Age:
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


__all__ = ['Age']