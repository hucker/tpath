"""
Test file for TPath functionality.
"""

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from tpath import Size, TPath


def test_tpath_file_operations(tmp_path: Path) -> None:
    """
    Test basic TPath file operations.

    Args:
        tmp_path (Path): pytest temporary directory fixture.

    Verifies file creation, property access, and size/age calculations for TPath objects.
    """
    # Arrange
    test_content: str = "Hello, World! This is a test file for TPath."
    test_file: Path = tmp_path / "test_file.txt"
    test_file.write_text(test_content)

    # Act
    tpath_file: TPath = TPath(test_file)
    expected_size: int = len(test_content.encode())
    actual_size: int = tpath_file.size.bytes

    # Assert
    assert tpath_file.exists()
    assert tpath_file.is_file()
    assert not tpath_file.is_dir()
    assert actual_size == expected_size
    assert tpath_file.size.kb == expected_size / 1000
    assert tpath_file.size.kib == expected_size / 1024
    assert tpath_file.age.seconds >= 0
    assert tpath_file.age.minutes >= 0
    assert tpath_file.age.hours >= 0
    assert tpath_file.age.days >= 0
    assert hasattr(tpath_file.ctime, "age")
    assert hasattr(tpath_file.mtime, "age")
    assert hasattr(tpath_file.atime, "age")


def test_tpath_with_base_time(tmp_path: Path) -> None:
    """
    Test TPath with custom base time.

    Args:
        tmp_path (Path): pytest temporary directory fixture.

    Verifies that age calculations are correct when using a custom base time.
    """
    # Arrange
    test_file: Path = tmp_path / "test_file.txt"
    test_file.write_text("test content")
    tpath_file: TPath = TPath(test_file)
    yesterday: datetime = datetime.now() - timedelta(days=1)

    # Act
    old_path: TPath = tpath_file.with_base_time(yesterday)
    actual_days: float = old_path.age.days

    # Assert
    assert actual_days < 0
    assert abs(actual_days) >= 0.9  # Should be close to 1 day


@pytest.mark.parametrize(
    "size_str,expected_bytes",
    [
        ("100", 100),
        ("1KB", 1000),
        ("1KiB", 1024),
        ("2.5MB", 2500000),
        ("1.5GiB", 1610612736),  # 1.5 * 1024^3
        ("0.5TB", 500000000000),  # 0.5 * 1000^4
    ],
)
def test_size_parsing_valid(size_str: str, expected_bytes: int) -> None:
    """
    Test size string parsing with valid inputs.

    Args:
        size_str (str): Size string to parse.
        expected_bytes (int): Expected byte value.
    """
    # Act
    actual_bytes: int = Size.parse(size_str)
    # Assert
    assert actual_bytes == expected_bytes


@pytest.mark.parametrize(
    "invalid_size",
    [
        "invalid",
        "1.5.5MB",
        "5XYZ",
        "",
        "MB",
    ],
)
def test_size_parsing_invalid(invalid_size: str) -> None:
    """
    Test size string parsing with invalid inputs.

    Args:
        invalid_size (str): Invalid size string to parse.
    """
    # Act & Assert
    with pytest.raises(ValueError):
        Size.parse(invalid_size)


def test_pathlib_compatibility():
    """
    Test that TPath maintains pathlib.Path compatibility.

    Asserts that TPath and Path share core attributes and behaviors.
    """
    # Arrange
    tpath_obj: TPath = TPath(".")
    regular_path: Path = Path(".")

    # Assert
    assert tpath_obj.is_dir() == regular_path.is_dir()
    assert tpath_obj.absolute() == regular_path.absolute()
    assert tpath_obj.parent == regular_path.parent
    assert tpath_obj.name == regular_path.name
    assert isinstance(tpath_obj, Path)


def test_tpath_extended_properties():
    """
    Test that TPath has extended properties not in regular Path.

    Asserts that TPath exposes additional file metadata properties.
    """
    # Arrange
    tpath_obj: TPath = TPath(".")
    regular_path: Path = Path(".")

    # Assert
    assert hasattr(tpath_obj, "size")
    assert hasattr(tpath_obj, "age")
    assert hasattr(tpath_obj, "ctime")
    assert hasattr(tpath_obj, "mtime")
    assert hasattr(tpath_obj, "atime")
    assert not hasattr(regular_path, "size")
    assert not hasattr(regular_path, "age")
