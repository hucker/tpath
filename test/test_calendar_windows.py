import tempfile

from tpath import TPath


def test_calendar_basics():
    """Test basic calendar functionality works."""
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        test_file = TPath(temp_file.name)
        temp_file.close()

        try:
            test_file.write_text("Testing")

            # File should be modified today
            assert test_file.mtime.cal.win_days(0)
            assert test_file.mtime.cal.win_months(0)
            assert test_file.mtime.cal.win_quarters(0)
            assert test_file.mtime.cal.win_years(0)

            # File should not be modified in the past
            assert not test_file.mtime.cal.win_days(-1)  # Yesterday
            assert not test_file.mtime.cal.win_months(-1)  # Last month

        finally:
            test_file.unlink(missing_ok=True)


def test_method_existence():
    """Test that all methods exist."""
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        test_file = TPath(temp_file.name)
        temp_file.close()

        try:
            test_file.write_text("Testing")

            # Check methods exist on cal property
            assert hasattr(test_file.mtime.cal, 'win_days')
            assert hasattr(test_file.mtime.cal, 'win_months')
            assert hasattr(test_file.mtime.cal, 'win_quarters')
            assert hasattr(test_file.mtime.cal, 'win_years')
            assert hasattr(test_file.mtime.cal, 'win_hours')
            assert hasattr(test_file.mtime.cal, 'win_minutes')

        finally:
            test_file.unlink(missing_ok=True)


def test_aliases():
    """Test that aliases work."""
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        test_file = TPath(temp_file.name)
        temp_file.close()

        try:
            test_file.write_text("Testing")

            # Check aliases exist on cal property
            assert hasattr(test_file.create.cal, 'win_days')
            assert hasattr(test_file.modify.cal, 'win_days')
            assert hasattr(test_file.access.cal, 'win_days')

        finally:
            test_file.unlink(missing_ok=True)


def test_range_functionality():
    """Test range functionality with 'through' parameter."""
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        test_file = TPath(temp_file.name)
        temp_file.close()

        try:
            test_file.write_text("Testing")

            # Test ranges that include current time
            assert test_file.mtime.cal.win_days(-7, 0)    # Last 7 days through today
            assert test_file.mtime.cal.win_months(-6, 0)  # Last 6 months through this month
            assert test_file.mtime.cal.win_years(-2, 0)   # Last 2 years through this year

            # Test parameter order normalization - these should be equivalent
            result1 = test_file.mtime.cal.win_days(-7, 0)
            result2 = test_file.mtime.cal.win_days(0, -7)
            assert result1 == result2, "Range parameter order should be normalized"

        finally:
            test_file.unlink(missing_ok=True)


def test_return_types():
    """Test that methods return proper boolean values."""
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        test_file = TPath(temp_file.name)
        temp_file.close()

        try:
            test_file.write_text("Testing")

            # All methods should return booleans
            assert isinstance(test_file.mtime.cal.win_days(0), bool)
            assert isinstance(test_file.mtime.cal.win_months(0), bool)
            assert isinstance(test_file.mtime.cal.win_quarters(0), bool)
            assert isinstance(test_file.mtime.cal.win_years(0), bool)
            assert isinstance(test_file.mtime.cal.win_hours(0), bool)
            assert isinstance(test_file.mtime.cal.win_minutes(0), bool)

            # Range methods should also return booleans
            assert isinstance(test_file.mtime.cal.win_days(-7, 0), bool)
            assert isinstance(test_file.mtime.cal.win_months(-6, -1), bool)

        finally:
            test_file.unlink(missing_ok=True)
