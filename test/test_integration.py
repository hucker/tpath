"""
Integration tests for TPath functionality.
Tests the complete functionality working together.
"""

import datetime as dt

from tpath import Size, TPath


def test_integration_basic_workflow():
    """Test a complete basic workflow with TPath."""
    print("Testing basic integration workflow...")

    # Create a test file
    test_file = TPath("integration_test.txt")
    content = "This is an integration test file for TPath functionality."
    test_file.write_text(content)

    try:
        # Test all main functionality together
        assert test_file.exists()
        assert test_file.is_file()

        # Test size functionality
        size = test_file.size
        assert size.bytes == len(content.encode("utf-8"))
        assert size.kb == size.bytes / 1000
        assert size.kib == size.bytes / 1024

        # Test age functionality
        age = test_file.age
        # Allow for very small negative values due to clock precision
        assert age.seconds >= -0.01  # Relaxed to handle clock precision issues
        assert age.minutes >= -0.01 / 60
        assert age.days >= -0.01 / 86400

        # Test time properties
        ctime = test_file.ctime
        mtime = test_file.mtime
        atime = test_file.atime

        # Allow for small negative values due to clock precision
        assert ctime.age.seconds >= -0.01
        assert mtime.age.seconds >= -0.01
        assert atime.age.seconds >= -0.01

        print(f"✅ File: {test_file}")
        print(f"✅ Size: {size.bytes} bytes ({size.kb:.3f} KB)")
        print(f"✅ Age: {age.seconds:.3f} seconds")
        print(f"✅ Created: {ctime.datetime}")

        print("✅ Basic integration workflow tests passed")

    finally:
        # Clean up
        if test_file.exists():
            test_file.unlink()


def test_integration_file_operations():
    """Test integration with file operations."""
    print("Testing file operations integration...")

    # Test with different file types and operations
    test_files = []

    try:
        # Create multiple test files
        for i in range(3):
            file_path = TPath(f"test_file_{i}.txt")
            content = f"Test file number {i} " * (i + 1) * 10
            file_path.write_text(content)
            test_files.append(file_path)

        # Test finding files by size
        large_files = [f for f in test_files if f.size.bytes > 100]

        assert len(large_files) >= 2  # Files 1 and 2 should be larger

        # Test finding files by age (all should be very young)
        recent_files = [f for f in test_files if f.age.minutes < 1]

        assert len(recent_files) == len(test_files)  # All should be recent

        # Test size comparison using parse
        min_size = Size.parse("50B")
        medium_files = [f for f in test_files if f.size.bytes > min_size]

        assert len(medium_files) >= 1

        print(f"✅ Created {len(test_files)} test files")
        print(f"✅ Found {len(large_files)} large files")
        print(f"✅ Found {len(recent_files)} recent files")
        print(f"✅ Found {len(medium_files)} medium+ files")

        print("✅ File operations integration tests passed")

    finally:
        # Clean up
        for file_path in test_files:
            if file_path.exists():
                file_path.unlink()


def test_integration_pathlib_compatibility():
    """Test integration with pathlib operations."""
    print("Testing pathlib compatibility integration...")

    # Create a test directory structure
    test_dir = TPath("test_integration_dir")
    test_dir.mkdir(exist_ok=True)

    try:
        # Create files in directory
        file1 = test_dir / "file1.txt"
        file2 = test_dir / "file2.log"

        file1.write_text("Content of file 1")
        file2.write_text("Content of file 2 with more text")

        # Test directory operations with TPath extensions
        assert test_dir.is_dir()

        # Test iterating and using TPath features
        files_info = []
        for file_path in test_dir.iterdir():
            if file_path.is_file():
                tpath_file = TPath(file_path)
                files_info.append(
                    {
                        "name": tpath_file.name,
                        "size": tpath_file.size.bytes,
                        "age": tpath_file.age.seconds,
                        "suffix": tpath_file.suffix,
                    }
                )

        assert len(files_info) == 2

        # Test glob patterns with TPath
        txt_files = list(test_dir.glob("*.txt"))
        assert len(txt_files) == 1
        assert TPath(txt_files[0]).suffix == ".txt"

        print(f"✅ Directory: {test_dir}")
        print(f"✅ Files found: {len(files_info)}")
        for info in files_info:
            print(f"   {info['name']}: {info['size']} bytes, {info['age']:.3f}s old")
        print(f"✅ TXT files: {len(txt_files)}")

        print("✅ Pathlib compatibility integration tests passed")

    finally:
        # Clean up
        if test_dir.exists():
            for file_path in test_dir.iterdir():
                if file_path.is_file():
                    file_path.unlink()
            test_dir.rmdir()


def test_integration_custom_base_time():
    """Test integration with custom base time scenarios."""
    print("Testing custom base time integration...")

    # Test scenario: file management with custom reference time
    reference_time = dt.datetime.now() - dt.timedelta(hours=12)

    test_file = TPath("base_time_test.txt").with_base_time(reference_time)
    test_file.write_text("Testing custom base time scenarios")

    try:
        # File should appear "old" relative to 12 hours ago
        age = test_file.age
        assert age.hours < 0  # Negative because file is newer than base

        # Test different time properties with custom base
        ctime_hours = test_file.ctime.age.hours
        mtime_hours = test_file.mtime.age.hours

        assert ctime_hours < 0
        assert mtime_hours < 0

        # Test that size still works normally
        size = test_file.size
        assert size.bytes > 0

    finally:
        # Clean up
        if test_file.exists():
            test_file.unlink()
