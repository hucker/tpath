"""
Age property implementation for TPath.

Handles file age calculations in various time units.
"""

import re
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

    @staticmethod
    def parse(age_str: str) -> float:
        """
        Parse an age string and return the age in seconds.

        Examples:
            "30" -> 30 seconds
            "5m" -> 300 seconds (5 minutes)
            "2h" -> 7200 seconds (2 hours)
            "3d" -> 259200 seconds (3 days)
            "1w" -> 604800 seconds (1 week)
            "2months" -> 5260032 seconds (2 months)
            "1y" -> 31557600 seconds (1 year)
        """
        age_str = age_str.strip().lower()

        # Handle plain numbers (seconds)
        if age_str.isdigit():
            return float(age_str)

        # Regular expression to parse age with unit
        match = re.match(r"^(\d+(?:\.\d+)?)\s*([a-zA-Z]+)$", age_str)
        if not match:
            raise ValueError(f"Invalid age format: {age_str}")

        value = float(match.group(1))
        unit = match.group(2).lower()

        # Define multipliers (convert to seconds)
        unit_multipliers = {
            "s": 1,
            "sec": 1,
            "second": 1,
            "seconds": 1,
            "m": 60,
            "min": 60,
            "minute": 60,
            "minutes": 60,
            "h": 3600,
            "hr": 3600,
            "hour": 3600,
            "hours": 3600,
            "d": 86400,
            "day": 86400,
            "days": 86400,
            "w": 604800,
            "week": 604800,
            "weeks": 604800,
            "month": 2630016,  # 30.44 days
            "months": 2630016,
            "y": 31557600,  # 365.25 days
            "year": 31557600,
            "years": 31557600,
        }

        if unit not in unit_multipliers:
            raise ValueError(f"Unknown unit: {unit}")

        return value * unit_multipliers[unit]


__all__ = ["Age"]
