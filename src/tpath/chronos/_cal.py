"""
Calendar-based time window filtering for Chronos package.

Provides calendar window filtering functionality that works with any object 
having datetime and base_time properties (Time or Chronos objects).
"""

import datetime as dt
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    pass


class TimeObj(Protocol):
    """Protocol for objects that can be used with Cal (Time or Chronos objects)."""
    
    @property
    def datetime(self) -> dt.datetime:
        """Get datetime object."""
        ...
    
    @property
    def base_time(self) -> dt.datetime:
        """Get base time for calculations."""
        ...


def normalize_weekday(day_spec: str) -> int:
    """Normalize various day-of-week specifications to Python weekday numbers.

    Args:
        day_spec: Day specification as a string

    Returns:
        int: Python weekday number (0=Monday, 1=Tuesday, ..., 6=Sunday)

    Accepts:
        - Full names: 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'
        - 3-letter abbrev: 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'
        - 2-letter abbrev: 'mo', 'tu', 'we', 'th', 'fr', 'sa', 'su'
        - Pandas style: 'w-mon', 'w-tue', etc.
        - All case insensitive

    Examples:
        normalize_weekday('monday') -> 0
        normalize_weekday('MON') -> 0
        normalize_weekday('w-sun') -> 6
        normalize_weekday('thu') -> 3
    """
    day_spec = str(day_spec).lower().strip()

    # Remove pandas-style prefix
    if day_spec.startswith("w-"):
        day_spec = day_spec[2:]

    # Full day names
    day_names = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }

    # 3-letter abbreviations
    day_abbrev3 = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}

    # 2-letter abbreviations
    day_abbrev2 = {"mo": 0, "tu": 1, "we": 2, "th": 3, "fr": 4, "sa": 5, "su": 6}

    # Check all mappings
    for mapping in [day_names, day_abbrev3, day_abbrev2]:
        if day_spec in mapping:
            return mapping[day_spec]

    # Generate helpful error message
    valid_examples = [
        "Full: 'monday', 'sunday'",
        "3-letter: 'mon', 'sun', 'tue', 'wed', 'thu', 'fri', 'sat'",
        "2-letter: 'mo', 'su', 'tu', 'we', 'th', 'fr', 'sa'",
        "Pandas: 'w-mon', 'w-sun'",
    ]
    raise ValueError(
        f"Invalid day specification: '{day_spec}'. Valid formats:\n"
        + "\n".join(f"  • {ex}" for ex in valid_examples)
    )


class Cal:
    """Calendar window filtering functionality for Time/Chronos objects."""

    def __init__(self, time_obj: TimeObj) -> None:
        """Initialize with a Time or Chronos object to provide calendar filtering methods."""
        self.time_obj: TimeObj = time_obj

    @property
    def dt_val(self) -> dt.datetime:
        """Get datetime from the time object."""
        return self.time_obj.datetime

    @property
    def base_time(self) -> dt.datetime:
        """Get base_time from the time object."""
        return self.time_obj.base_time

    def win_minutes(self, start: int = 0, end: int | None = None) -> bool:
        """True if timestamp falls within the minute window(s) from start to end.

        Args:
            start: Minutes from now to start range (negative = past, 0 = current minute, positive = future)
            end: Minutes from now to end range (defaults to start for single minute)

        Examples:
            chronos.cal.win_minutes(0)          # This minute (now)
            chronos.cal.win_minutes(-5)         # 5 minutes ago only
            chronos.cal.win_minutes(-10, -5)    # From 10 minutes ago through 5 minutes ago
            chronos.cal.win_minutes(-30, 0)     # Last 30 minutes through now
        """
        if end is None:
            end = start

        # Ensure proper order (start <= end, since we want chronological order)
        if start > end:
            start, end = end, start

        target_time = self.dt_val

        # Calculate the time window boundaries
        start_time = self.base_time + dt.timedelta(minutes=start)
        start_minute = start_time.replace(second=0, microsecond=0)

        end_time = self.base_time + dt.timedelta(minutes=end)
        end_minute = end_time.replace(second=0, microsecond=0) + dt.timedelta(minutes=1)

        return start_minute <= target_time < end_minute

    def win_hours(self, start: int = 0, end: int | None = None) -> bool:
        """True if timestamp falls within the hour window(s) from start to end.

        Args:
            start: Hours from now to start range (negative = past, 0 = current hour, positive = future)
            end: Hours from now to end range (defaults to start for single hour)

        Examples:
            chronos.cal.win_hours(0)          # This hour (now)
            chronos.cal.win_hours(-2)         # 2 hours ago only
            chronos.cal.win_hours(-6, -1)     # From 6 hours ago through 1 hour ago
            chronos.cal.win_hours(-24, 0)     # Last 24 hours through now
        """
        if end is None:
            end = start

        if start > end:
            start, end = end, start

        target_time = self.dt_val

        # Calculate the time window boundaries
        start_time = self.base_time + dt.timedelta(hours=start)
        start_hour = start_time.replace(minute=0, second=0, microsecond=0)

        end_time = self.base_time + dt.timedelta(hours=end)
        end_hour = end_time.replace(minute=0, second=0, microsecond=0) + dt.timedelta(
            hours=1
        )

        return start_hour <= target_time < end_hour

    def win_days(self, start: int = 0, end: int | None = None) -> bool:
        """True if timestamp falls within the day window(s) from start to end.

        Args:
            start: Days from now to start range (negative = past, 0 = today, positive = future)
            end: Days from now to end range (defaults to start for single day)

        Examples:
            chronos.cal.win_days(0)          # Today only
            chronos.cal.win_days(-1)         # Yesterday only
            chronos.cal.win_days(-7, -1)     # From 7 days ago through yesterday
            chronos.cal.win_days(-30, 0)     # Last 30 days through today
        """
        if end is None:
            end = start

        if start > end:
            start, end = end, start

        target_date = self.dt_val.date()

        # Calculate the date range boundaries
        start_date = (self.base_time + dt.timedelta(days=start)).date()
        end_date = (self.base_time + dt.timedelta(days=end)).date()

        return start_date <= target_date <= end_date

    def win_months(self, start: int = 0, end: int | None = None) -> bool:
        """True if timestamp falls within the month window(s) from start to end.

        Args:
            start: Months from now to start range (negative = past, 0 = this month, positive = future)
            end: Months from now to end range (defaults to start for single month)

        Examples:
            chronos.cal.win_months(0)          # This month
            chronos.cal.win_months(-1)         # Last month only
            chronos.cal.win_months(-6, -1)     # From 6 months ago through last month
            chronos.cal.win_months(-12, 0)     # Last 12 months through this month
        """
        if end is None:
            end = start

        if start > end:
            start, end = end, start

        target_time = self.dt_val
        base_year = self.base_time.year
        base_month = self.base_time.month

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
        file_month_index = target_time.year * 12 + target_time.month
        start_month_index = start_year * 12 + start_month
        end_month_index = end_year * 12 + end_month

        return start_month_index <= file_month_index <= end_month_index

    def win_quarters(self, start: int = 0, end: int | None = None) -> bool:
        """True if timestamp falls within the quarter window(s) from start to end.

        Args:
            start: Quarters from now to start range (negative = past, 0 = this quarter, positive = future)
            end: Quarters from now to end range (defaults to start for single quarter)

        Examples:
            chronos.cal.win_quarters(0)          # This quarter (Q1: Jan-Mar, Q2: Apr-Jun, Q3: Jul-Sep, Q4: Oct-Dec)
            chronos.cal.win_quarters(-1)         # Last quarter
            chronos.cal.win_quarters(-4, -1)     # From 4 quarters ago through last quarter
            chronos.cal.win_quarters(-8, 0)      # Last 8 quarters through this quarter
        """
        if end is None:
            end = start

        if start > end:
            start, end = end, start

        target_time = self.dt_val
        base_time = self.base_time

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

        # Get target's quarter
        target_quarter = ((target_time.month - 1) // 3) + 1
        target_year = target_time.year

        # Check if target falls within the quarter range
        # Convert quarters to a comparable format (year * 4 + quarter)
        target_quarter_index = target_year * 4 + target_quarter
        start_quarter_index = start_year * 4 + start_quarter
        end_quarter_index = end_year * 4 + end_quarter

        return start_quarter_index <= target_quarter_index <= end_quarter_index

    def win_years(self, start: int = 0, end: int | None = None) -> bool:
        """True if timestamp falls within the year window(s) from start to end.

        Args:
            start: Years from now to start range (negative = past, 0 = this year, positive = future)
            end: Years from now to end range (defaults to start for single year)

        Examples:
            chronos.cal.win_years(0)          # This year
            chronos.cal.win_years(-1)         # Last year only
            chronos.cal.win_years(-5, -1)     # From 5 years ago through last year
            chronos.cal.win_years(-10, 0)     # Last 10 years through this year
        """
        if end is None:
            end = start

        if start > end:
            start, end = end, start

        target_year = self.dt_val.year
        base_year = self.base_time.year

        # Calculate year range boundaries
        start_year = base_year + start
        end_year = base_year + end

        return start_year <= target_year <= end_year

    def win_weeks(
        self, start: int = 0, end: int | None = None, week_start: str = "monday"
    ) -> bool:
        """True if timestamp falls within the week window(s) from start to end.

        Args:
            start: Weeks from now to start range (negative = past, 0 = current week, positive = future)
            end: Weeks from now to end range (defaults to start for single week)
            week_start: Week start day (default: 'monday' for ISO weeks)
                - 'monday'/'mon'/'mo' (ISO 8601 default)
                - 'sunday'/'sun'/'su' (US convention)
                - Supports full names, abbreviations, pandas style ('w-mon')
                - Case insensitive

        Examples:
            chronos.cal.win_weeks(0)                     # This week (Monday start)
            chronos.cal.win_weeks(-1, week_start='sun')  # Last week (Sunday start)
            chronos.cal.win_weeks(-4, 0)                 # Last 4 weeks through this week
            chronos.cal.win_weeks(-2, -1, 'sunday')      # 2-1 weeks ago (Sunday weeks)
        """
        if end is None:
            end = start

        if start > end:
            start, end = end, start

        # Normalize the week start day
        week_start_day = normalize_weekday(week_start)

        target_date = self.dt_val.date()
        base_date = self.base_time.date()

        # Calculate the start of the current week based on week_start_day
        days_since_week_start = (base_date.weekday() - week_start_day) % 7
        current_week_start = base_date - dt.timedelta(days=days_since_week_start)

        # Calculate week boundaries
        start_week_start = current_week_start + dt.timedelta(weeks=start)
        end_week_start = current_week_start + dt.timedelta(weeks=end)
        end_week_end = end_week_start + dt.timedelta(
            days=6
        )  # End of week (6 days after start)

        return start_week_start <= target_date <= end_week_end


__all__ = ["Cal"]