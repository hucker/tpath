"""
Test file for standalone Cal (calendar) functionality.

Tests the Cal class as a standalone utility for calendar window calculations.
"""

import datetime as dt

import pytest

from tpath.chronos import Cal, Chronos


def test_cal_with_chronos():
    """Test Cal functionality using Chronos objects."""
    # Create a Chronos object for January 1, 2024 at noon
    target_time = dt.datetime(2024, 1, 1, 12, 0, 0)
    reference_time = dt.datetime(2024, 1, 1, 18, 0, 0)  # Same day, 6 hours later

    chronos = Chronos(target_time, reference_time)
    cal = chronos.cal

    # Test that we can access calendar functionality
    assert isinstance(cal, Cal)
    assert cal.dt_val == target_time
    assert cal.base_time == reference_time


def test_cal_win_minutes():
    """Test calendar minute window functionality."""
    target_time = dt.datetime(2024, 1, 1, 12, 30, 0)
    reference_time = dt.datetime(2024, 1, 1, 12, 35, 0)  # 5 minutes later

    chronos = Chronos(target_time, reference_time)
    cal = chronos.cal

    # Should be within current minute range
    assert cal.win_minutes(-5, 0)  # Last 5 minutes through now
    assert not cal.win_minutes(1, 5)  # Future minutes
    assert cal.win_minutes(-10, 0)  # Broader range including target


def test_cal_win_hours():
    """Test calendar hour window functionality."""
    target_time = dt.datetime(2024, 1, 1, 10, 30, 0)
    reference_time = dt.datetime(2024, 1, 1, 12, 30, 0)  # 2 hours later

    chronos = Chronos(target_time, reference_time)
    cal = chronos.cal

    # Should be within hour ranges
    assert cal.win_hours(-2, 0)  # Last 2 hours through now
    assert not cal.win_hours(-1, 0)  # Just last hour (too narrow)
    assert cal.win_hours(-3, 0)  # Broader range


def test_cal_win_days():
    """Test calendar day window functionality."""
    target_time = dt.datetime(2024, 1, 1, 12, 0, 0)
    reference_time = dt.datetime(2024, 1, 2, 12, 0, 0)  # Next day

    chronos = Chronos(target_time, reference_time)
    cal = chronos.cal

    # Test day windows
    assert cal.win_days(-1, 0)  # Yesterday through today
    assert cal.win_days(-1)  # Just yesterday
    assert not cal.win_days(0)  # Just today (target was yesterday)
    assert not cal.win_days(-2, -2)  # Two days ago only


def test_cal_win_weeks():
    """Test calendar week window functionality."""
    # Monday Jan 1, 2024
    target_time = dt.datetime(2024, 1, 1, 12, 0, 0)  # Monday
    reference_time = dt.datetime(2024, 1, 8, 12, 0, 0)  # Next Monday

    chronos = Chronos(target_time, reference_time)
    cal = chronos.cal

    # Test week windows
    assert cal.win_weeks(-1, 0)  # Last week through this week
    assert cal.win_weeks(-1)  # Just last week
    assert not cal.win_weeks(0)  # Just this week


def test_cal_win_weeks_custom_start():
    """Test calendar week functionality with custom week start."""
    # Sunday Jan 7, 2024
    target_time = dt.datetime(2024, 1, 7, 12, 0, 0)  # Sunday
    reference_time = dt.datetime(2024, 1, 14, 12, 0, 0)  # Next Sunday

    chronos = Chronos(target_time, reference_time)
    cal = chronos.cal

    # Test with Sunday week start
    assert cal.win_weeks(-1, week_start="sunday")
    assert cal.win_weeks(-1, week_start="sun")
    assert cal.win_weeks(-1, week_start="su")


def test_cal_win_months():
    """Test calendar month window functionality."""
    target_time = dt.datetime(2024, 1, 15, 12, 0, 0)  # January 15
    reference_time = dt.datetime(2024, 2, 15, 12, 0, 0)  # February 15

    chronos = Chronos(target_time, reference_time)
    cal = chronos.cal

    # Test month windows
    assert cal.win_months(-1, 0)  # Last month through this month
    assert cal.win_months(-1)  # Just last month
    assert not cal.win_months(0)  # Just this month


def test_cal_win_quarters():
    """Test calendar quarter window functionality."""
    target_time = dt.datetime(2024, 1, 15, 12, 0, 0)  # Q1 2024
    reference_time = dt.datetime(2024, 4, 15, 12, 0, 0)  # Q2 2024

    chronos = Chronos(target_time, reference_time)
    cal = chronos.cal

    # Test quarter windows
    assert cal.win_quarters(-1, 0)  # Last quarter through this quarter
    assert cal.win_quarters(-1)  # Just last quarter (Q1)
    assert not cal.win_quarters(0)  # Just this quarter (Q2)


def test_cal_win_years():
    """Test calendar year window functionality."""
    target_time = dt.datetime(2023, 6, 15, 12, 0, 0)  # 2023
    reference_time = dt.datetime(2024, 6, 15, 12, 0, 0)  # 2024

    chronos = Chronos(target_time, reference_time)
    cal = chronos.cal

    # Test year windows
    assert cal.win_years(-1, 0)  # Last year through this year
    assert cal.win_years(-1)  # Just last year
    assert not cal.win_years(0)  # Just this year


def test_cal_range_ordering():
    """Test that Cal handles range parameters in any order."""
    target_time = dt.datetime(2024, 1, 3, 12, 0, 0)
    reference_time = dt.datetime(2024, 1, 5, 12, 0, 0)

    chronos = Chronos(target_time, reference_time)
    cal = chronos.cal

    # These should be equivalent (automatically ordered)
    assert cal.win_days(-5, -1) == cal.win_days(-1, -5)
    assert cal.win_days(-3, 0) == cal.win_days(0, -3)


def test_cal_single_vs_range():
    """Test single time unit vs range specifications."""
    target_time = dt.datetime(2024, 1, 1, 12, 0, 0)
    reference_time = dt.datetime(2024, 1, 2, 12, 0, 0)

    chronos = Chronos(target_time, reference_time)
    cal = chronos.cal

    # Single day (yesterday only)
    assert cal.win_days(-1)  # Just yesterday

    # Range (yesterday through today)
    assert cal.win_days(-1, 0)  # Yesterday through today


def test_weekday_normalization():
    """Test the normalize_weekday function indirectly through Cal."""
    from tpath.chronos._cal import normalize_weekday

    # Test full names
    assert normalize_weekday("monday") == 0
    assert normalize_weekday("sunday") == 6

    # Test 3-letter abbreviations
    assert normalize_weekday("mon") == 0
    assert normalize_weekday("sun") == 6

    # Test 2-letter abbreviations
    assert normalize_weekday("mo") == 0
    assert normalize_weekday("su") == 6

    # Test case insensitivity
    assert normalize_weekday("MONDAY") == 0
    assert normalize_weekday("Sun") == 6

    # Test pandas style
    assert normalize_weekday("w-mon") == 0
    assert normalize_weekday("w-sun") == 6


def test_weekday_normalization_errors():
    """Test error handling in weekday normalization."""
    from tpath.chronos._cal import normalize_weekday

    with pytest.raises(ValueError, match="Invalid day specification"):
        normalize_weekday("invalid")

    with pytest.raises(ValueError, match="Invalid day specification"):
        normalize_weekday("xyz")


if __name__ == "__main__":
    pytest.main([__file__])
