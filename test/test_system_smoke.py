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
            last_week = file_path.mtime.cal.win_days(
                -7, 0
            )  # Last 7 days through today
            last_month = file_path.mtime.cal.win_months(
                -1, 0
            )  # Last month through this month

            assert isinstance(last_week, bool)
            assert isinstance(last_month, bool)

        # Test 10: Stat property access and ctime fix validation
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
        print("   - Validated 10 major feature categories")

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
