"""
Calendar-based time window filtering for TPath.

Provides calendar window filtering functionality as a separate component
that works with Time objects through composition.
"""

from datetime import timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._time import Time


class Calendar:
    """Calendar window filtering functionality for Time objects."""

    def __init__(self, time_obj: "Time"):
        """Initialize with a Time object to provide calendar filtering methods."""
        self.time = time_obj

    def in_minutes(self, ago: int, through: int | None = None) -> bool:
        """True if file timestamp falls within the minute window(s) going back from now.
        
        Args:
            ago: Minutes ago from now (positive values for past, 0 for current minute)
            through: Optional end of range in minutes ago (defaults to ago for single minute)
            
        Examples:
            file.mtime.calendar.in_minutes(0)        # This minute (now)
            file.mtime.calendar.in_minutes(5)        # 5 minutes ago only
            file.mtime.calendar.in_minutes(10, 5)    # From 10 minutes ago through 5 minutes ago
            file.mtime.calendar.in_minutes(30, 0)    # Last 30 minutes including now
        """
        if through is None:
            through = ago
        
        # Ensure proper order (ago >= through, since ago is further back)
        if ago < through:
            ago, through = through, ago
        
        file_time = self.time.datetime
        
        # Check each minute in the range (ago is further back, through is closer to now)
        for minutes_back in range(through, ago + 1):
            target_time = self.time.base_time - timedelta(minutes=minutes_back)
            minute_start = target_time.replace(second=0, microsecond=0)
            minute_end = minute_start + timedelta(minutes=1)
            
            if minute_start <= file_time < minute_end:
                return True
        
        return False

    def in_hours(self, ago: int, through: int | None = None) -> bool:
        """True if file timestamp falls within the hour window(s) going back from now.
        
        Args:
            ago: Hours ago from now (positive values for past, 0 for current hour)
            through: Optional end of range in hours ago (defaults to ago for single hour)
            
        Examples:
            file.mtime.calendar.in_hours(0)        # This hour (now)
            file.mtime.calendar.in_hours(2)        # 2 hours ago only
            file.mtime.calendar.in_hours(6, 1)     # From 6 hours ago through 1 hour ago
            file.mtime.calendar.in_hours(24, 0)    # Last 24 hours including now
        """
        if through is None:
            through = ago
        
        if ago < through:
            ago, through = through, ago
        
        file_time = self.time.datetime
        
        for hours_back in range(through, ago + 1):
            target_time = self.time.base_time - timedelta(hours=hours_back)
            hour_start = target_time.replace(minute=0, second=0, microsecond=0)
            hour_end = hour_start + timedelta(hours=1)
            
            if hour_start <= file_time < hour_end:
                return True
        
        return False

    def in_days(self, ago: int, through: int | None = None) -> bool:
        """True if file timestamp falls within the day window(s) going back from now.
        
        Args:
            ago: Days ago from now (positive values for past, 0 for today)
            through: Optional end of range in days ago (defaults to ago for single day)
            
        Examples:
            file.mtime.calendar.in_days(0)        # Today
            file.mtime.calendar.in_days(1)        # Yesterday (1 day ago)
            file.mtime.calendar.in_days(7, 1)     # From 7 days ago through yesterday
            file.mtime.calendar.in_days(30, 0)    # Last 30 days including today
        """
        if through is None:
            through = ago
        
        if ago < through:
            ago, through = through, ago
        
        file_date = self.time.datetime.date()
        
        for days_back in range(through, ago + 1):
            target_date = (self.time.base_time - timedelta(days=days_back)).date()
            if file_date == target_date:
                return True
        
        return False

    def in_months(self, ago: int, through: int | None = None) -> bool:
        """True if file timestamp falls within the month window(s) going back from now.
        
        Args:
            ago: Months ago from now (positive values for past, 0 for this month)
            through: Optional end of range in months ago (defaults to ago for single month)
            
        Examples:
            file.mtime.calendar.in_months(0)        # This month
            file.mtime.calendar.in_months(1)        # Last month (1 month ago)
            file.mtime.calendar.in_months(6, 1)     # From 6 months ago through last month
            file.mtime.calendar.in_months(12, 0)    # Last 12 months including this month
        """
        if through is None:
            through = ago
        
        if ago < through:
            ago, through = through, ago
        
        file_time = self.time.datetime
        base_year = self.time.base_time.year
        base_month = self.time.base_time.month
        
        for months_back in range(through, ago + 1):
            # Calculate target year and month (going backwards)
            target_month = base_month - months_back
            target_year = base_year
            
            # Handle year boundary crossings
            while target_month <= 0:
                target_month += 12
                target_year -= 1
            
            if (file_time.year == target_year and 
                file_time.month == target_month):
                return True
        
        return False

    def in_quarters(self, ago: int, through: int | None = None) -> bool:
        """True if file timestamp falls within the quarter window(s) going back from now.
        
        Args:
            ago: Quarters ago from now (positive values for past, 0 for this quarter)
            through: Optional end of range in quarters ago (defaults to ago for single quarter)
            
        Examples:
            file.mtime.calendar.in_quarters(0)        # This quarter (Q1: Jan-Mar, Q2: Apr-Jun, Q3: Jul-Sep, Q4: Oct-Dec)
            file.mtime.calendar.in_quarters(1)        # Last quarter
            file.mtime.calendar.in_quarters(4, 1)     # From 4 quarters ago through last quarter
            file.mtime.calendar.in_quarters(8, 0)     # Last 8 quarters including this quarter
        """
        if through is None:
            through = ago
        
        if ago < through:
            ago, through = through, ago
        
        file_time = self.time.datetime
        base_time = self.time.base_time
        
        # Get current quarter (1-4)
        current_quarter = ((base_time.month - 1) // 3) + 1
        current_year = base_time.year
        
        for quarters_back in range(through, ago + 1):
            # Calculate target quarter and year
            target_quarter = current_quarter - quarters_back
            target_year = current_year
            
            # Handle year boundary crossings
            while target_quarter <= 0:
                target_quarter += 4
                target_year -= 1
            
            # Convert quarter to month range
            quarter_start_month = (target_quarter - 1) * 3 + 1
            quarter_end_month = quarter_start_month + 2
            
            # Check if file falls within this quarter
            if (file_time.year == target_year and 
                quarter_start_month <= file_time.month <= quarter_end_month):
                return True
        
        return False

    def in_years(self, ago: int, through: int | None = None) -> bool:
        """True if file timestamp falls within the year window(s) going back from now.
        
        Args:
            ago: Years ago from now (positive values for past, 0 for this year)
            through: Optional end of range in years ago (defaults to ago for single year)
            
        Examples:
            file.mtime.calendar.in_years(0)        # This year
            file.mtime.calendar.in_years(1)        # Last year (1 year ago)
            file.mtime.calendar.in_years(5, 1)     # From 5 years ago through last year
            file.mtime.calendar.in_years(10, 0)    # Last 10 years including this year
        """
        if through is None:
            through = ago
        
        if ago < through:
            ago, through = through, ago
        
        file_year = self.time.datetime.year
        base_year = self.time.base_time.year
        
        for years_back in range(through, ago + 1):
            target_year = base_year - years_back
            if file_year == target_year:
                return True
        
        return False


__all__ = ["Calendar"]