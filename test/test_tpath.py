"""
Test file for TPath functionality.
"""

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from tpath import Size, TPath


def test_tpath_file_operations(tmp_path):
    """Test basic TPath file operations."""
    # Create a temporary file
    test_content = "Hello, World! This is a test file for TPath."
    test_file = tmp_path / "test_file.txt"
    test_file.write_text(test_content)

    tpath_file = TPath(test_file)

    # Test basic properties
    assert tpath_file.exists()
    assert tpath_file.is_file()
    assert not tpath_file.is_dir()

    # Test size properties
    expected_size = len(test_content.encode())
    assert tpath_file.size.bytes == expected_size
    assert tpath_file.size.kb == expected_size / 1000
    assert tpath_file.size.kib == expected_size / 1024

    # Test that age properties return positive values (file was just created)
    assert tpath_file.age.seconds >= 0
    assert tpath_file.age.minutes >= 0
    assert tpath_file.age.hours >= 0
    assert tpath_file.age.days >= 0

    # Test different time types exist and are accessible
    assert hasattr(tpath_file.ctime, "age")
    assert hasattr(tpath_file.mtime, "age")
    assert hasattr(tpath_file.atime, "age")


def test_tpath_with_base_time(tmp_path):
    """Test TPath with custom base time."""
    # Create a temporary file
    test_file = tmp_path / "test_file.txt"
    test_file.write_text("test content")

    tpath_file = TPath(test_file)

    # Test with base time set to yesterday
    yesterday = datetime.now() - timedelta(days=1)
    old_path = tpath_file.with_base_time(yesterday)

    # Age should be negative since base time is in the past
    assert old_path.age.days < 0
    assert abs(old_path.age.days) >= 0.9  # Should be close to 1 day


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
def test_size_parsing_valid(size_str, expected_bytes):
    """Test size string parsing with valid inputs."""
    result = Size.parse(size_str)
    assert result == expected_bytes


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
def test_size_parsing_invalid(invalid_size):
    """Test size string parsing with invalid inputs."""
    with pytest.raises(ValueError):
        Size.parse(invalid_size)


def test_pathlib_compatibility():
    """Test that TPath maintains pathlib.Path compatibility."""
    # Test with current directory
    tpath_obj = TPath(".")
    regular_path = Path(".")

    # Both should be directories and have same absolute path
    assert tpath_obj.is_dir() == regular_path.is_dir()
    assert tpath_obj.absolute() == regular_path.absolute()

    # Test that TPath has all the same basic Path attributes
    assert tpath_obj.parent == regular_path.parent
    assert tpath_obj.name == regular_path.name

    # Test that TPath is instance of Path
    assert isinstance(tpath_obj, Path)


def test_tpath_extended_properties():
    """Test that TPath has extended properties not in regular Path."""
    tpath_obj = TPath(".")
    regular_path = Path(".")

    # TPath should have additional properties
    assert hasattr(tpath_obj, "size")
    assert hasattr(tpath_obj, "age")
    assert hasattr(tpath_obj, "ctime")
    assert hasattr(tpath_obj, "mtime")
    assert hasattr(tpath_obj, "atime")

    # Regular Path should not have these
    assert not hasattr(regular_path, "size")
    assert not hasattr(regular_path, "age")
