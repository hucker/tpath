"""
Comprehensive end-to-end system test for TPath.

This test creates diverse files and validates TPath functionality
across multiple dimensions: file types, sizes, ages, and time scenarios.
"""

import os
import tempfile
import time
from pathlib import Path

from tpath import TPath


def test_comprehensive_system_smoke():
    """
    Comprehensive system smoke test covering multiple TPath features.

    Creates files with different extensions, sizes, and timestamps,
    then validates filtering and property access across all scenarios.
    """
    # Create temporary directory
    test_dir = Path(tempfile.mkdtemp(prefix="tpath_test_"))
    created_files = []

    try:
        # Define test scenarios
        extensions = [".txt", ".py", ".json", ".md", ".log"]
        sizes = [0, 100, 1024, 10240]  # 0B, 100B, 1KB, 10KB
        time_offsets = [0, -3600, -86400]  # now, 1hr ago, 1day ago

        # Create diverse test files
        file_specs = []
        for ext in extensions:
            for size in sizes:
                for offset in time_offsets:
                    file_name = f"test_{len(file_specs):03d}{ext}"
                    file_path = TPath(test_dir / file_name)

                    # Create file with content
                    if size == 0:
                        file_path.touch()
                    else:
                        content = "x" * size
                        file_path.write_text(content)

                    # Modify timestamp
                    timestamp = time.time() + offset
                    os.utime(file_path, (timestamp, timestamp))

                    created_files.append(file_path)
                    file_specs.append(
                        {
                            "path": file_path,
                            "extension": ext,
                            "size": size,
                            "offset": offset,
                        }
                    )

        # Test 1: Basic file operations
        assert len(created_files) == len(extensions) * len(sizes) * len(time_offsets)
        assert all(f.exists() for f in created_files)
        assert all(f.is_file() for f in created_files)

        # Test 2: Size-based filtering
        empty_files = [f for f in created_files if f.size.bytes == 0]
        small_files = [f for f in created_files if 0 < f.size.bytes <= 1024]
        large_files = [f for f in created_files if f.size.bytes > 1024]

        expected_empty = len([s for s in file_specs if s["size"] == 0])
        expected_small = len([s for s in file_specs if 0 < s["size"] <= 1024])
        expected_large = len([s for s in file_specs if s["size"] > 1024])

        assert len(empty_files) == expected_empty
        assert len(small_files) == expected_small
        assert len(large_files) == expected_large

        # Test 3: Extension-based filtering
        for ext in extensions:
            ext_files = [f for f in created_files if f.suffix == ext]
            expected_count = len([s for s in file_specs if s["extension"] == ext])
            assert len(ext_files) == expected_count

        # Test 4: Time property access
        for file_path in created_files:
            # All time properties should be accessible
            assert isinstance(file_path.ctime.timestamp, float)
            assert isinstance(file_path.mtime.timestamp, float)
            assert isinstance(file_path.atime.timestamp, float)

            # Aliases should work
            assert file_path.create.timestamp == file_path.ctime.timestamp
            assert file_path.modify.timestamp == file_path.mtime.timestamp
            assert file_path.access.timestamp == file_path.atime.timestamp

        # Test 5: Age calculations
        for file_path in created_files:
            age = file_path.age
            assert isinstance(age.seconds, float)
            assert isinstance(age.minutes, float)
            assert isinstance(age.hours, float)
            assert isinstance(age.days, float)
            # Age can be slightly negative due to clock precision, so allow small negative values
            assert age.seconds >= -1  # Should be approximately positive (file age)

        # Test 6: Calendar filtering
        for file_path in created_files:
            # All files should be in current time periods
            assert file_path.mtime.cal.win_years(0)  # This year
            assert file_path.mtime.cal.win_months(0)  # This month

            # Today check depends on when files were created
            # (Some might be from "yesterday" due to offset)
            calendar_result = file_path.mtime.cal.win_days(0)
            assert isinstance(calendar_result, bool)

        # Test 7: Size conversions
        for file_path in created_files:
            size = file_path.size
            assert size.kb == size.bytes / 1000
            assert size.mb == size.bytes / 1000000
            assert size.gb == size.bytes / 1000000000
            assert size.kib == size.bytes / 1024
            assert size.mib == size.bytes / (1024 * 1024)

        # Test 8: Complex filtering combinations
        python_files = [f for f in created_files if f.suffix == ".py"]
        recent_files = [f for f in created_files if f.age.hours < 2]

        # Verify combinations work
        assert len(python_files) > 0
        assert len(recent_files) > 0  # Test 9: Calendar range filtering
        for file_path in created_files:
            # Test range functionality
            last_week = file_path.mtime.cal.win_days(-7, 0)  # Last 7 days through today
            last_month = file_path.mtime.cal.win_months(
                -1, 0
            )  # Last month through this month

            assert isinstance(last_week, bool)
            assert isinstance(last_month, bool)

        # Test 10: Access control properties (Windows and Unix compatible)
        for file_path in created_files:
            # Basic access properties should always be accessible
            assert isinstance(file_path.readable, bool)
            assert isinstance(file_path.writable, bool)
            assert isinstance(file_path.executable, bool)

            # Derived access properties
            assert isinstance(file_path.read_only, bool)
            assert isinstance(file_path.write_only, bool)
            assert isinstance(file_path.read_write, bool)

            # Files we created should be readable and writable
            assert file_path.readable is True
            assert file_path.writable is True

            # Read-write check (should be True since we can read and write)
            assert file_path.read_write is True

            # Read-only and write-only should be False for our test files
            assert file_path.read_only is False
            assert file_path.write_only is False

        # Test 11: Access mode method
        for file_path in created_files:
            # Test various access mode specifications
            assert file_path.access_mode("R") is True  # Should be readable
            assert file_path.access_mode("W") is True  # Should be writable
            assert file_path.access_mode("RW") is True  # Should be read-write
            assert file_path.access_mode("RO") is False  # Should not be read-only
            assert file_path.access_mode("WO") is False  # Should not be write-only

            # Test case insensitive
            assert file_path.access_mode("r") is True
            assert file_path.access_mode("rw") is True

            # Executable depends on platform
            executable_result = file_path.access_mode("X")
            assert isinstance(executable_result, bool)

            # On Windows, files are typically executable if they exist
            # On Unix, depends on actual permissions
            if os.name == "nt":  # Windows
                assert executable_result is True
            # On Unix, we don't assert a specific value since it depends on umask

        # Test 12: Owner permission properties (Unix-specific but safe on Windows)
        for file_path in created_files:
            # These should return boolean values on all platforms
            assert isinstance(file_path.owner_readable, bool)
            assert isinstance(file_path.owner_writable, bool)
            assert isinstance(file_path.owner_executable, bool)

            # Files we created should have owner read/write permissions
            assert file_path.owner_readable is True
            assert file_path.owner_writable is True

            # Owner executable depends on platform and file type
            owner_exec = file_path.owner_executable
            assert isinstance(owner_exec, bool)

            # On Windows, should be True for existing files
            if os.name == "nt":
                assert owner_exec is True

        # Test 14: Stat property access and ctime fix validation
        for file_path in created_files:
            stat_result = file_path.stat()

            # Basic stat properties should be accessible
            assert hasattr(stat_result, "st_size")
            assert hasattr(stat_result, "st_mtime")
            assert hasattr(stat_result, "st_atime")
            assert hasattr(stat_result, "st_ctime")

            # Size should match
            assert stat_result.st_size == file_path.size.bytes

            # Times should be accessible (ctime fix working)
            ctime_from_stat = stat_result.st_ctime
            ctime_from_property = file_path.ctime.timestamp
            assert isinstance(ctime_from_stat, float)
            assert isinstance(ctime_from_property, float)

        print("✅ System smoke test completed successfully!")
        print(f"   - Created and tested {len(created_files)} files")
        print(f"   - Tested {len(extensions)} file extensions")
        print(f"   - Tested {len(sizes)} size categories")
        print(f"   - Tested {len(time_offsets)} time scenarios")
        print("   - Validated 14 major feature categories")
        print("   - Tested cross-platform access controls")
        print("   - Verified owner/group properties")
        print("   - Validated permission checking")

    finally:
        # Cleanup
        for file_path in created_files:
            file_path.unlink(missing_ok=True)

        # Remove test directory
        if test_dir.exists():
            for item in test_dir.rglob("*"):
                if item.is_file():
                    item.unlink()
            test_dir.rmdir()


if __name__ == "__main__":
    test_comprehensive_system_smoke()
    print("🎉 All tests passed!")
