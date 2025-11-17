"""
Test file for Time functionality (_time.py).
"""

import datetime as dt
from pathlib import Path

from tpath import Age, PathTime, TPath


def test_time_properties(tmp_path: Path) -> None:
    """
    Test PathTime class properties.

    Verifies that PathTime properties exist and have correct types and age attributes.
    """

    # Arrange
    test_file: TPath = TPath(tmp_path / "test_time_file.txt")
    test_file.write_text("Testing time functionality")

    # Act
    ctime: PathTime = test_file.ctime
    mtime: PathTime = test_file.mtime
    atime: PathTime = test_file.atime

    # Assert
    assert isinstance(ctime, PathTime)
    assert isinstance(mtime, PathTime)
    assert isinstance(atime, PathTime)
    assert isinstance(ctime.age, Age)
    assert isinstance(mtime.age, Age)
    assert isinstance(atime.age, Age)


def test_time_timestamp_access(tmp_path: Path) -> None:
    """Test Time timestamp property."""

    # Arrange
    test_file: TPath = TPath(tmp_path / "test_timestamp_file.txt")
    test_file.write_text("Testing timestamp access")

    # Act
    ctime: PathTime = test_file.ctime
    mtime: PathTime = test_file.mtime
    atime: PathTime = test_file.atime
    now: float = dt.datetime.now().timestamp()

    # Assert
    assert isinstance(ctime.timestamp, float)
    assert isinstance(mtime.timestamp, float)
    assert isinstance(atime.timestamp, float)
    assert abs(ctime.timestamp - now) < 60  # Within 1 minute
    assert abs(mtime.timestamp - now) < 60
    assert abs(atime.timestamp - now) < 60


def test_time_datetime_access(tmp_path: Path) -> None:
    """Test Time datetime property."""

    # Arrange
    test_file: TPath = TPath(tmp_path / "test_datetime_file.txt")
    test_file.write_text("Testing datetime access")

    # Act
    ctime: PathTime = test_file.ctime
    mtime: PathTime = test_file.mtime
    atime: PathTime = test_file.atime
    now: dt.datetime = dt.datetime.now()
    time_diff: float = abs((ctime.target_dt - now).total_seconds())

    # Assert
    assert isinstance(ctime.target_dt, dt.datetime)
    assert isinstance(mtime.target_dt, dt.datetime)
    assert isinstance(atime.target_dt, dt.datetime)
    assert time_diff < 60  # Within 1 minute


def test_time_with_custom_base(tmp_path: Path) -> None:
    """Test Time with custom base time."""

    # Arrange
    yesterday: dt.datetime = dt.datetime.now() - dt.timedelta(days=1)
    test_file: TPath = TPath(tmp_path / "test_base_time_file.txt").with_base_time(
        yesterday
    )
    test_file.write_text("Testing custom base time")

    # Act
    age: Age = test_file.ctime.age
    mtime_age: Age = test_file.mtime.age
    atime_age: Age = test_file.atime.age

    # Assert
    assert isinstance(age, Age)
    assert age.days < 0
    assert mtime_age.days < 0
    assert atime_age.days < 0


def test_time_nonexistent_file() -> None:
    """Test Time behavior with nonexistent files."""

    # Arrange
    nonexistent: TPath = TPath("nonexistent_file.txt")
    if nonexistent.exists():
        nonexistent.unlink()

    # Act
    ctime: PathTime = nonexistent.ctime
    mtime: PathTime = nonexistent.mtime
    atime: PathTime = nonexistent.atime

    # Assert
    assert isinstance(ctime, PathTime)
    assert isinstance(mtime, PathTime)
    assert isinstance(atime, PathTime)
    assert isinstance(ctime.age, Age)
    assert isinstance(mtime.age, Age)
    assert isinstance(atime.age, Age)
    assert ctime.timestamp == 0
    assert mtime.timestamp == 0
    assert atime.timestamp == 0
