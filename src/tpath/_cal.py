"""
Calendar-based time window filtering for TPath.

Provides calendar window filtering functionality as a separate component
that works with Time objects through composition.
"""

from datetime import timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._time import Time


class Cal:
    """Calendar window filtering functionality for Time objects."""

    def __init__(self, time_obj: "Time"):
        """Initialize with a Time object to provide calendar filtering methods."""
        self.time = time_obj

    def win_minutes(self, start: int = 0, end: int | None = None) -> bool:
        """True if file timestamp falls within the minute window(s) from start to end.

        Args:
            start: Minutes from now to start range (negative = past, 0 = current minute, positive = future)
            end: Minutes from now to end range (defaults to start for single minute)

        Examples:
            file.mtime.cal.win_minutes(0)          # This minute (now)
            file.mtime.cal.win_minutes(-5)         # 5 minutes ago only
            file.mtime.cal.win_minutes(-10, -5)    # From 10 minutes ago through 5 minutes ago
            file.mtime.cal.win_minutes(-30, 0)     # Last 30 minutes through now
        """
        if end is None:
            end = start

        # Ensure proper order (start <= end, since we want chronological order)
        if start > end:
            start, end = end, start

        file_time = self.time.datetime

        # Calculate the time window boundaries
        start_time = self.time.base_time + timedelta(minutes=start)
        start_minute = start_time.replace(second=0, microsecond=0)
        
        end_time = self.time.base_time + timedelta(minutes=end)
        end_minute = end_time.replace(second=0, microsecond=0) + timedelta(minutes=1)

        return start_minute <= file_time < end_minute

    def win_hours(self, start: int = 0, end: int | None = None) -> bool:
        """True if file timestamp falls within the hour window(s) from start to end.

        Args:
            start: Hours from now to start range (negative = past, 0 = current hour, positive = future)
            end: Hours from now to end range (defaults to start for single hour)

        Examples:
            file.mtime.cal.win_hours(0)          # This hour (now)
            file.mtime.cal.win_hours(-2)         # 2 hours ago only
            file.mtime.cal.win_hours(-6, -1)     # From 6 hours ago through 1 hour ago
            file.mtime.cal.win_hours(-24, 0)     # Last 24 hours through now
        """
        if end is None:
            end = start

        if start > end:
            start, end = end, start

        file_time = self.time.datetime

        # Calculate the time window boundaries
        start_time = self.time.base_time + timedelta(hours=start)
        start_hour = start_time.replace(minute=0, second=0, microsecond=0)
        
        end_time = self.time.base_time + timedelta(hours=end)
        end_hour = end_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

        return start_hour <= file_time < end_hour

    def win_days(self, start: int = 0, end: int | None = None) -> bool:
        """True if file timestamp falls within the day window(s) from start to end.

        Args:
            start: Days from now to start range (negative = past, 0 = today, positive = future)
            end: Days from now to end range (defaults to start for single day)

        Examples:
            file.mtime.cal.win_days(0)          # Today only
            file.mtime.cal.win_days(-1)         # Yesterday only
            file.mtime.cal.win_days(-7, -1)     # From 7 days ago through yesterday
            file.mtime.cal.win_days(-30, 0)     # Last 30 days through today
        """
        if end is None:
            end = start

        if start > end:
            start, end = end, start

        file_date = self.time.datetime.date()

        # Calculate the date range boundaries
        start_date = (self.time.base_time + timedelta(days=start)).date()
        end_date = (self.time.base_time + timedelta(days=end)).date()

        return start_date <= file_date <= end_date

    def win_months(self, start: int = 0, end: int | None = None) -> bool:
        """True if file timestamp falls within the month window(s) from start to end.

        Args:
            start: Months from now to start range (negative = past, 0 = this month, positive = future)
            end: Months from now to end range (defaults to start for single month)

        Examples:
            file.mtime.cal.win_months(0)          # This month
            file.mtime.cal.win_months(-1)         # Last month only
            file.mtime.cal.win_months(-6, -1)     # From 6 months ago through last month
            file.mtime.cal.win_months(-12, 0)     # Last 12 months through this month
        """
        if end is None:
            end = start

        if start > end:
            start, end = end, start

        file_time = self.time.datetime
        base_year = self.time.base_time.year
        base_month = self.time.base_time.month

        # Calculate the start month (earliest)
        start_month = base_month + start
        start_year = base_year
        while start_month <= 0:
            start_month += 12
            start_year -= 1
        while start_month > 12:
            start_month -= 12
            start_year += 1

        # Calculate the end month (latest)
        end_month = base_month + end
        end_year = base_year
        while end_month <= 0:
            end_month += 12
            end_year -= 1
        while end_month > 12:
            end_month -= 12
            end_year += 1

        # Convert months to a comparable format (year * 12 + month)
        file_month_index = file_time.year * 12 + file_time.month
        start_month_index = start_year * 12 + start_month
        end_month_index = end_year * 12 + end_month

        return start_month_index <= file_month_index <= end_month_index

    def win_quarters(self, start: int = 0, end: int | None = None) -> bool:
        """True if file timestamp falls within the quarter window(s) from start to end.

        Args:
            start: Quarters from now to start range (negative = past, 0 = this quarter, positive = future)
            end: Quarters from now to end range (defaults to start for single quarter)

        Examples:
            file.mtime.cal.win_quarters(0)          # This quarter (Q1: Jan-Mar, Q2: Apr-Jun, Q3: Jul-Sep, Q4: Oct-Dec)
            file.mtime.cal.win_quarters(-1)         # Last quarter
            file.mtime.cal.win_quarters(-4, -1)     # From 4 quarters ago through last quarter
            file.mtime.cal.win_quarters(-8, 0)      # Last 8 quarters through this quarter
        """
        if end is None:
            end = start

        if start > end:
            start, end = end, start

        file_time = self.time.datetime
        base_time = self.time.base_time

        # Get current quarter (1-4) and year
        current_quarter = ((base_time.month - 1) // 3) + 1
        current_year = base_time.year

        # Calculate the start quarter (earliest)
        start_quarter = current_quarter + start
        start_year = current_year
        while start_quarter <= 0:
            start_quarter += 4
            start_year -= 1
        while start_quarter > 4:
            start_quarter -= 4
            start_year += 1

        # Calculate the end quarter (latest)
        end_quarter = current_quarter + end
        end_year = current_year
        while end_quarter <= 0:
            end_quarter += 4
            end_year -= 1
        while end_quarter > 4:
            end_quarter -= 4
            end_year += 1

        # Get file's quarter
        file_quarter = ((file_time.month - 1) // 3) + 1
        file_year = file_time.year

        # Check if file falls within the quarter range
        # Convert quarters to a comparable format (year * 4 + quarter)
        file_quarter_index = file_year * 4 + file_quarter
        start_quarter_index = start_year * 4 + start_quarter
        end_quarter_index = end_year * 4 + end_quarter

        return start_quarter_index <= file_quarter_index <= end_quarter_index

    def win_years(self, start: int = 0, end: int | None = None) -> bool:
        """True if file timestamp falls within the year window(s) from start to end.

        Args:
            start: Years from now to start range (negative = past, 0 = this year, positive = future)
            end: Years from now to end range (defaults to start for single year)

        Examples:
            file.mtime.cal.win_years(0)          # This year
            file.mtime.cal.win_years(-1)         # Last year only
            file.mtime.cal.win_years(-5, -1)     # From 5 years ago through last year
            file.mtime.cal.win_years(-10, 0)     # Last 10 years through this year
        """
        if end is None:
            end = start

        if start > end:
            start, end = end, start

        file_year = self.time.datetime.year
        base_year = self.time.base_time.year

        # Calculate year range boundaries
        start_year = base_year + start
        end_year = base_year + end

        return start_year <= file_year <= end_year


__all__ = ["Cal"]
