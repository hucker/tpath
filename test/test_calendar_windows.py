from pathlib import Path

from tpath import TPath


def test_calendar_basics(tmp_path: Path) -> None:
    """Test basic calendar functionality works."""
    test_file = TPath(tmp_path / "testfile.txt")
    test_file.write_text("Testing")

    # File should be modified today
    assert test_file.mtime.cal.in_days(0)
    assert test_file.mtime.cal.in_months(0)
    assert test_file.mtime.cal.in_quarters(0)
    assert test_file.mtime.cal.in_years(0)
    assert test_file.mtime.cal.in_weeks(0)  # This week

    # File should not be modified in the past
    assert not test_file.mtime.cal.in_days(-1)  # Yesterday
    assert not test_file.mtime.cal.in_months(-1)  # Last month
    assert not test_file.mtime.cal.in_weeks(-1)  # Last week


def test_method_existence(tmp_path: Path) -> None:
    """Test that all methods exist."""
    test_file = TPath(tmp_path / "testfile.txt")
    test_file.write_text("Testing")

    # Check methods exist on cal property
    assert hasattr(test_file.mtime.cal, "in_days")
    assert hasattr(test_file.mtime.cal, "in_months")
    assert hasattr(test_file.mtime.cal, "in_quarters")
    assert hasattr(test_file.mtime.cal, "in_years")
    assert hasattr(test_file.mtime.cal, "in_hours")
    assert hasattr(test_file.mtime.cal, "in_minutes")
    assert hasattr(test_file.mtime.cal, "in_weeks")


def test_aliases(tmp_path: Path) -> None:
    """Test that aliases work."""
    test_file = TPath(tmp_path / "testfile.txt")
    test_file.write_text("Testing")

    # Check aliases exist on cal property
    assert hasattr(test_file.create.cal, "in_days")
    assert hasattr(test_file.modify.cal, "in_days")
    assert hasattr(test_file.access.cal, "in_days")


def test_range_functionality(tmp_path: Path) -> None:
    """Test range functionality with 'through' parameter."""
    test_file = TPath(tmp_path / "testfile.txt")
    test_file.write_text("Testing")

    # Test ranges that include current time
    assert test_file.mtime.cal.in_days(-7, 0)  # Last 7 days through today
    assert test_file.mtime.cal.in_months(-6, 0)  # Last 6 months through this month
    assert test_file.mtime.cal.in_years(-2, 0)  # Last 2 years through this year
    assert test_file.mtime.cal.in_weeks(-4, 0)  # Last 4 weeks through this week


def test_return_types(tmp_path: Path) -> None:
    """Test that methods return proper boolean values."""
    test_file = TPath(tmp_path / "testfile.txt")
    test_file.write_text("Testing")

    # All methods should return booleans
    assert isinstance(test_file.mtime.cal.in_days(0), bool)
    assert isinstance(test_file.mtime.cal.in_months(0), bool)
    assert isinstance(test_file.mtime.cal.in_quarters(0), bool)
    assert isinstance(test_file.mtime.cal.in_years(0), bool)
    assert isinstance(test_file.mtime.cal.in_hours(0), bool)
    assert isinstance(test_file.mtime.cal.in_minutes(0), bool)
    assert isinstance(test_file.mtime.cal.in_weeks(0), bool)

    # Range methods should also return booleans
    assert isinstance(test_file.mtime.cal.in_days(-7, 0), bool)
    assert isinstance(test_file.mtime.cal.in_months(-6, -1), bool)
    assert isinstance(test_file.mtime.cal.in_weeks(-2, 0), bool)
