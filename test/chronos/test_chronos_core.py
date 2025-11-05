"""
Test file for standalone Chronos functionality.

Tests the Chronos class as a standalone dt.datetime utility without file dependencies.
"""

import datetime as dt

import pytest

from tpath.chronos import Chronos


def test_chronos_creation():
    """Test basic Chronos object creation."""
    target_time = dt.datetime(2024, 1, 1, 12, 0, 0)
    reference_time = dt.datetime(2024, 1, 2, 12, 0, 0)

    # Test with explicit reference time
    chronos = Chronos(target_time, reference_time)
    assert chronos.target_time == target_time
    assert chronos.reference_time == reference_time

    # Test with default reference time (now)
    chronos_now = Chronos(target_time)
    assert chronos_now.target_time == target_time
    assert chronos_now.reference_time is not None


def test_chronos_properties():
    """Test Chronos object properties."""
    target_time = dt.datetime(2024, 1, 1, 12, 0, 0)
    reference_time = dt.datetime(2024, 1, 2, 12, 0, 0)

    chronos = Chronos(target_time, reference_time)

    # Test basic properties
    assert chronos.date_time == target_time
    assert chronos.base_time == reference_time
    assert chronos.timestamp == target_time.timestamp()

    # Test convenience properties
    assert chronos.seconds_ago == 86400.0  # 24 hours
    assert chronos.minutes_ago == 1440.0  # 24 * 60 minutes
    assert chronos.hours_ago == 24.0  # 24 hours
    assert chronos.days_ago == 1.0  # 1 day


def test_chronos_age_property():
    """Test that Chronos age property works correctly."""
    target_time = dt.datetime(2024, 1, 1, 12, 0, 0)
    reference_time = dt.datetime(2024, 1, 2, 12, 0, 0)

    chronos = Chronos(target_time, reference_time)
    age = chronos.age

    # Test that age calculations work
    assert age.seconds == 86400.0
    assert age.minutes == 1440.0
    assert age.hours == 24.0
    assert age.days == 1.0
    assert age.weeks == pytest.approx(1.0 / 7.0)


def test_chronos_calendar_property():
    """Test that Chronos calendar property works correctly."""
    target_time = dt.datetime(2024, 1, 1, 12, 0, 0)
    reference_time = dt.datetime(2024, 1, 1, 18, 0, 0)  # Same day, 6 hours later

    chronos = Chronos(target_time, reference_time)
    cal = chronos.cal

    # Test calendar window functionality
    assert cal.win_days(0)  # Same day
    assert cal.win_hours(-6, 0)  # Within 6 hours
    assert not cal.win_days(-1)  # Not yesterday


def test_chronos_with_reference_time():
    """Test creating new Chronos with different reference time."""
    target_time = dt.datetime(2024, 1, 1, 12, 0, 0)
    original_ref = dt.datetime(2024, 1, 2, 12, 0, 0)
    new_ref = dt.datetime(2024, 1, 3, 12, 0, 0)

    chronos1 = Chronos(target_time, original_ref)
    chronos2 = chronos1.with_reference_time(new_ref)

    # Original should be unchanged
    assert chronos1.reference_time == original_ref
    assert chronos1.days_ago == 1.0

    # New one should have different reference
    assert chronos2.reference_time == new_ref
    assert chronos2.target_time == target_time  # Same target
    assert chronos2.days_ago == 2.0  # Different calculation


def test_chronos_string_representations():
    """Test string representations of Chronos objects."""
    target_time = dt.datetime(2024, 1, 1, 12, 30, 45)
    reference_time = dt.datetime(2024, 1, 2, 12, 0, 0)

    chronos = Chronos(target_time, reference_time)

    # Test __repr__
    repr_str = repr(chronos)
    assert "Chronos" in repr_str
    assert "2024-01-01T12:30:45" in repr_str
    assert "2024-01-02T12:00:00" in repr_str

    # Test __str__
    str_str = str(chronos)
    assert "Chronos for 2024-01-01 12:30:45" in str_str


def test_chronos_parse_static_method():
    """Test Chronos.parse static method."""
    # Test Unix timestamp
    chronos1 = Chronos.parse("1704110400")  # 2024-01-01 12:00:00 UTC
    assert chronos1.target_time.year == 2024
    assert chronos1.target_time.month == 1
    assert chronos1.target_time.day == 1

    # Test ISO format
    chronos2 = Chronos.parse("2024-01-01T12:30:00")
    assert chronos2.target_time.hour == 12
    assert chronos2.target_time.minute == 30

    # Test simple date
    chronos3 = Chronos.parse("2024-12-25")
    assert chronos3.target_time.month == 12
    assert chronos3.target_time.day == 25

    # Test with custom reference time
    ref_time = dt.datetime(2024, 6, 1)
    chronos4 = Chronos.parse("2024-01-01", ref_time)
    assert chronos4.reference_time == ref_time


def test_chronos_parse_errors():
    """Test Chronos.parse error handling."""
    with pytest.raises(ValueError, match="Unable to parse time string"):
        Chronos.parse("invalid-date-format")

    with pytest.raises(ValueError, match="Unable to parse time string"):
        Chronos.parse("not-a-date-at-all")


if __name__ == "__main__":
    pytest.main([__file__])
