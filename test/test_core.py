"""
Test file for TPath core functionality (_core.py).
"""

from datetime import datetime
from pathlib import Path

from tpath import TPath


def test_tpath_creation():
    """Test TPath object creation and initialization."""
    print("Testing TPath creation...")

    # Test basic creation
    path1 = TPath("test_file.txt")
    assert isinstance(path1, TPath)
    assert str(path1) == "test_file.txt"

    # Test creation with custom base_time using with_base_time method
    custom_time = datetime(2023, 1, 1)
    path2 = TPath("test_file.txt").with_base_time(custom_time)
    assert path2._base_time == custom_time

    print("✅ TPath creation tests passed")


def test_pathlib_compatibility():
    """Test that TPath maintains pathlib.Path compatibility."""
    print("Testing pathlib compatibility...")

    # Create a TPath
    tpath_obj = TPath(".")
    regular_path = Path(".")

    # Test common Path methods work
    assert tpath_obj.is_dir() == regular_path.is_dir()
    assert str(tpath_obj.absolute()) == str(regular_path.absolute())
    assert tpath_obj.name == regular_path.name
    assert tpath_obj.suffix == regular_path.suffix

    print(f"TPath absolute: {tpath_obj.absolute()}")
    print(f"Path absolute:  {regular_path.absolute()}")
    print(f"TPath is_dir(): {tpath_obj.is_dir()}")
    print(f"Path is_dir():  {regular_path.is_dir()}")
    print(f"TPath parent: {tpath_obj.parent}")
    print(f"TPath name: {tpath_obj.name}")
    print(f"TPath suffix: {tpath_obj.suffix}")

    print("✅ Pathlib compatibility tests passed")


def test_property_access():
    """Test that TPath properties are accessible."""
    print("Testing property access...")

    # Create a test file
    test_file = TPath("test_file.txt")
    test_file.write_text("Hello, World!")

    try:
        # Test that properties are accessible (not testing exact values)
        assert hasattr(test_file, "age")
        assert hasattr(test_file, "size")
        assert hasattr(test_file, "ctime")
        assert hasattr(test_file, "mtime")
        assert hasattr(test_file, "atime")

        # Test property types
        from tpath import Age, Size, Time

        assert isinstance(test_file.age, Age)
        assert isinstance(test_file.size, Size)
        assert isinstance(test_file.ctime, Time)
        assert isinstance(test_file.mtime, Time)
        assert isinstance(test_file.atime, Time)

        print("✅ Property access tests passed")

    finally:
        # Clean up
        if test_file.exists():
            test_file.unlink()
