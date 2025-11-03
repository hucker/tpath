"""
Size property implementation for TPath.

Handles file size operations with various units.
"""

import re
from pathlib import Path


class Size:
    """Property class for handling file size operations with various units."""
    
    def __init__(self, path: Path):
        self.path = path
        
    @property
    def bytes(self) -> int:
        """Get file size in bytes."""
        # Use cached stat if available (TPath instance), otherwise use regular stat
        if hasattr(self.path, '_cached_stat'):
            cached_stat = self.path._cached_stat
            return cached_stat.st_size if cached_stat else 0
        else:
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
    def pb(self) -> float:
        """Get file size in petabytes (1000^5 bytes)."""
        return self.bytes / 1000**5
    
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
    
    @property
    def pib(self) -> float:
        """Get file size in pebibytes (1024^5 bytes)."""
        return self.bytes / 1024**5
    
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
        match = re.match(r'^(\d+(?:\.\d+)?)\s*([KMGTP]I?B?)$', size_str)
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
            'PB': 1000**5,
            'KIB': 1024,
            'MIB': 1024**2,
            'GIB': 1024**3,
            'TIB': 1024**4,
            'PIB': 1024**5,
        }
        
        if unit not in binary_units:
            raise ValueError(f"Unknown unit: {unit}")
        
        return int(value * binary_units[unit])


__all__ = ['Size']
