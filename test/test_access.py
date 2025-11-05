"""
Test file for TPath access properties.
"""

import os
import platform
import tempfile

from tpath import TPath


def test_basic_access_properties():
    """Test basic access properties (readable, writable, executable)."""
    print("Testing basic access properties...")

    # Create a test file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp:
        tmp.write("Test content")
        test_file_path = tmp.name

    try:
        test_file = TPath(test_file_path)

        # Test basic properties exist and return booleans
        assert isinstance(test_file.readable, bool)
        assert isinstance(test_file.writable, bool)
        assert isinstance(test_file.executable, bool)

        # On a normal file we just created, it should be readable and writable
        assert test_file.readable is True
        assert test_file.writable is True

        # On Windows, executable should always be True
        if platform.system() == "Windows":
            assert test_file.executable is True

        print("✅ Basic access properties tests passed")

    finally:
        # Clean up
        os.unlink(test_file_path)


def test_derived_access_properties():
    """Test derived access properties (read_only, write_only, read_write)."""
    print("Testing derived access properties...")

    # Create a test file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp:
        tmp.write("Test content")
        test_file_path = tmp.name

    try:
        test_file = TPath(test_file_path)

        # Test derived properties exist and return booleans
        assert isinstance(test_file.read_only, bool)
        assert isinstance(test_file.write_only, bool)
        assert isinstance(test_file.read_write, bool)

        # Our test file should be read-write (not read-only or write-only)
        assert test_file.read_write is True
        assert test_file.read_only is False
        assert test_file.write_only is False

        print("✅ Derived access properties tests passed")

    finally:
        # Clean up
        os.unlink(test_file_path)


def test_access_mode_method():
    """Test the access_mode method."""
    print("Testing access_mode method...")

    # Create a test file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp:
        tmp.write("Test content")
        test_file_path = tmp.name

    try:
        test_file = TPath(test_file_path)

        # Test basic modes
        assert test_file.access_mode("R") is True
        assert test_file.access_mode("W") is True
        assert test_file.access_mode("RW") is True
        assert test_file.access_mode("RO") is False  # Not read-only
        assert test_file.access_mode("WO") is False  # Not write-only

        # Test case insensitive
        assert test_file.access_mode("r") is True
        assert test_file.access_mode("rw") is True

        # Test executable depends on platform
        exec_result = test_file.access_mode("X")
        assert isinstance(exec_result, bool)

        # On Windows, should be executable
        if platform.system() == "Windows":
            assert exec_result is True

        # Test invalid mode raises ValueError
        try:
            test_file.access_mode("INVALID")
            raise AssertionError("Should have raised ValueError")
        except ValueError:
            pass  # Expected

        print("✅ Access mode method tests passed")

    finally:
        # Clean up
        os.unlink(test_file_path)


def test_nonexistent_file_access():
    """Test access properties on nonexistent files."""
    print("Testing access properties on nonexistent files...")

    # Create a path to a file that doesn't exist
    nonexistent = TPath("nonexistent_file_for_access_testing.txt")

    # Make sure it doesn't exist
    if nonexistent.exists():
        nonexistent.unlink()

    # Access properties should all return False for nonexistent files
    assert nonexistent.readable is False
    assert nonexistent.writable is False
    assert nonexistent.executable is False
    assert nonexistent.read_only is False
    assert nonexistent.write_only is False
    assert nonexistent.read_write is False

    print("✅ Nonexistent file access tests passed")


def test_access_stat_caching():
    """Test that access properties work with stat caching."""
    print("Testing access stat caching...")

    # Create a test file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp:
        tmp.write("Test content")
        test_file_path = tmp.name

    try:
        test_file = TPath(test_file_path)

        # Access multiple properties - should work with cached stat
        readable1 = test_file.readable
        writable1 = test_file.writable
        readable2 = test_file.readable
        writable2 = test_file.writable

        # Should be consistent due to using os.access() directly
        assert readable1 == readable2
        assert writable1 == writable2

        print("✅ Access stat caching tests passed")

    finally:
        # Clean up
        os.unlink(test_file_path)


def test_property_access():
    """Test that all access properties are accessible."""
    print("Testing property access...")

    # Create a test file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp:
        tmp.write("Test content")
        test_file_path = tmp.name

    try:
        test_file = TPath(test_file_path)

        # Test that all properties exist
        assert hasattr(test_file, "readable")
        assert hasattr(test_file, "writable")
        assert hasattr(test_file, "executable")
        assert hasattr(test_file, "read_only")
        assert hasattr(test_file, "write_only")
        assert hasattr(test_file, "read_write")
        assert hasattr(test_file, "owner_readable")
        assert hasattr(test_file, "owner_writable")
        assert hasattr(test_file, "owner_executable")

        # Test that access_mode is callable
        assert callable(test_file.access_mode)

        print("✅ Access property access tests passed")

    finally:
        # Clean up
        os.unlink(test_file_path)


if __name__ == "__main__":
    test_basic_access_properties()
    test_derived_access_properties()
    test_access_mode_method()
    test_nonexistent_file_access()
    test_access_stat_caching()
    test_property_access()
    print("\n🎉 All access property tests passed!")
