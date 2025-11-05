"""
Test file for Time functionality (_time.py).
"""

import datetime as dt

from tpath import Age, PathTime, TPath


def test_time_properties():
    """Test PathTime class properties."""
    print("Testing PathTime properties...")

    # Create a test file
    test_file = TPath("test_time_file.txt")
    test_file.write_text("Testing time functionality")

    try:
        # Test ctime property
        ctime = test_file.ctime
        assert isinstance(ctime, PathTime)

        # Test mtime property
        mtime = test_file.mtime
        assert isinstance(mtime, PathTime)

        # Test atime property
        atime = test_file.atime
        assert isinstance(atime, PathTime)

        # Test that time properties have age
        assert isinstance(ctime.age, Age)
        assert isinstance(mtime.age, Age)
        assert isinstance(atime.age, Age)

        print(f"Creation time age: {ctime.age.days:.10f} days")
        print(f"Modification time age: {mtime.age.days:.10f} days")
        print(f"Access time age: {atime.age.days:.10f} days")

        print("✅ Time properties tests passed")

    finally:
        # Clean up
        if test_file.exists():
            test_file.unlink()


def test_time_timestamp_access():
    """Test Time timestamp property."""
    print("Testing Time timestamp access...")

    # Create a test file
    test_file = TPath("test_timestamp_file.txt")
    test_file.write_text("Testing timestamp access")

    try:
        # Test timestamp properties exist and return numbers
        ctime = test_file.ctime
        mtime = test_file.mtime
        atime = test_file.atime

        assert isinstance(ctime.timestamp, float)
        assert isinstance(mtime.timestamp, float)
        assert isinstance(atime.timestamp, float)

        # Timestamps should be reasonable (recent)
        now = dt.datetime.now().timestamp()
        assert abs(ctime.timestamp - now) < 60  # Within 1 minute
        assert abs(mtime.timestamp - now) < 60
        assert abs(atime.timestamp - now) < 60

        print(f"Creation timestamp: {ctime.timestamp}")
        print(f"Modification timestamp: {mtime.timestamp}")
        print(f"Access timestamp: {atime.timestamp}")

        print("✅ Timestamp access tests passed")

    finally:
        # Clean up
        if test_file.exists():
            test_file.unlink()


def test_time_datetime_access():
    """Test Time datetime property."""

    # Create a test file
    test_file = TPath("test_datetime_file.txt")
    test_file.write_text("Testing datetime access")

    try:
        # Test datetime properties exist and return datetime objects
        ctime = test_file.ctime
        mtime = test_file.mtime
        atime = test_file.atime

        assert isinstance(ctime.datetime, dt.datetime)
        assert isinstance(mtime.datetime, dt.datetime)
        assert isinstance(atime.datetime, dt.datetime)

        # Datetime should be recent
        now = dt.datetime.now()
        time_diff = abs((ctime.datetime - now).total_seconds())
        assert time_diff < 60  # Within 1 minute

    finally:
        # Clean up
        if test_file.exists():
            test_file.unlink()


def test_time_with_custom_base():
    """Test Time with custom base time."""

    # Create a test file with custom base time
    yesterday = dt.datetime.now() - dt.timedelta(days=1)
    test_file = TPath("test_base_time_file.txt").with_base_time(yesterday)
    test_file.write_text("Testing custom base time")

    try:
        # Test that age is calculated relative to custom base time
        age = test_file.ctime.age
        assert isinstance(age, Age)

        # File should appear "older" (negative age) since base time is in past
        assert age.days < 0

        print(f"Age with yesterday base: {age.days:.2f} days")

        # Test with different time types
        mtime_age = test_file.mtime.age
        atime_age = test_file.atime.age

        assert mtime_age.days < 0
        assert atime_age.days < 0

    finally:
        # Clean up
        if test_file.exists():
            test_file.unlink()


def test_time_nonexistent_file():
    """Test Time behavior with nonexistent files."""
    print("Testing Time with nonexistent files...")

    # Create path to nonexistent file
    nonexistent = TPath("nonexistent_file.txt")

    # Ensure file doesn't exist
    if nonexistent.exists():
        nonexistent.unlink()

    # Test that Time properties handle nonexistent files gracefully
    ctime = nonexistent.ctime
    mtime = nonexistent.mtime
    atime = nonexistent.atime

    assert isinstance(ctime, PathTime)
    assert isinstance(mtime, PathTime)
    assert isinstance(atime, PathTime)

    # Test that age is accessible (should return current time age)
    assert isinstance(ctime.age, Age)
    assert isinstance(mtime.age, Age)
    assert isinstance(atime.age, Age)

    # Test timestamp returns 0 for nonexistent files
    assert ctime.timestamp == 0
    assert mtime.timestamp == 0
    assert atime.timestamp == 0
