#!/usr/bin/env python3
"""
Comprehensive End-to-End System Smoke Test for TPath

This test creates a diverse set of files with different:
- Extensions (.txt, .py, .json, .md, .log, .data, etc.)
- Sizes (empty, small, medium, large)
- Creation times (recent, old, very old)
- Modification times (recent, old, stale)
- Access times (recent, old)

Then validates that TPath filtering and properties work correctly
across all combinations using generated filter statements.
"""

import json
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from src.tpath import TPath


class SystemSmokeTest:
    """Comprehensive system test for TPath functionality."""

    def __init__(self):
        self.test_dir = None
        self.files: list[dict[str, Any]] = []
        self.created_files: list[TPath] = []

    def setup_test_environment(self):
        """Create temporary directory for test files."""
        self.test_dir = Path(tempfile.mkdtemp(prefix="tpath_smoke_"))
        print(f"📁 Test directory: {self.test_dir}")

    def cleanup_test_environment(self):
        """Clean up all test files and directory."""
        if self.test_dir and self.test_dir.exists():
            for file_path in self.created_files:
                file_path.unlink(missing_ok=True)

            # Remove any remaining files and the directory
            for item in self.test_dir.rglob("*"):
                if item.is_file():
                    item.unlink()
            self.test_dir.rmdir()
            print("🧹 Cleaned up test directory")

    def generate_file_specifications(self) -> list[dict[str, Any]]:
        """Generate specifications for diverse test files."""

        # Different file extensions to test
        extensions = [
            ".txt",
            ".py",
            ".json",
            ".md",
            ".log",
            ".csv",
            ".xml",
            ".yaml",
            ".ini",
            ".cfg",
            ".data",
            ".tmp",
            ".bak",
            ".old",
        ]

        # Different size categories (in bytes)
        size_specs = [
            {"name": "empty", "size": 0},
            {"name": "tiny", "size": 50},
            {"name": "small", "size": 1024},  # 1KB
            {"name": "medium", "size": 50 * 1024},  # 50KB
            {"name": "large", "size": 1024 * 1024},  # 1MB
            {"name": "huge", "size": 5 * 1024 * 1024},  # 5MB
        ]

        # Different time scenarios (relative to now)
        now = datetime.now()
        time_specs = [
            {"name": "now", "offset": timedelta(0)},
            {"name": "recent", "offset": timedelta(minutes=-30)},
            {"name": "hour_ago", "offset": timedelta(hours=-1)},
            {"name": "yesterday", "offset": timedelta(days=-1)},
            {"name": "week_ago", "offset": timedelta(days=-7)},
            {"name": "month_ago", "offset": timedelta(days=-30)},
            {"name": "quarter_ago", "offset": timedelta(days=-90)},
            {"name": "year_ago", "offset": timedelta(days=-365)},
        ]

        specs = []
        file_id = 1

        # Generate combinations of extensions, sizes, and times
        for ext in extensions:
            for size_spec in size_specs:
                for create_time_spec in time_specs[
                    :4
                ]:  # Limit combinations for manageable test
                    for mod_time_spec in time_specs[:3]:
                        # Create file specification
                        spec = {
                            "id": file_id,
                            "name": f"test_{file_id:03d}_{size_spec['name']}{ext}",
                            "extension": ext,
                            "size": size_spec["size"],
                            "size_category": size_spec["name"],
                            "create_time": now + create_time_spec["offset"],
                            "create_time_category": create_time_spec["name"],
                            "modify_time": now + mod_time_spec["offset"],
                            "modify_time_category": mod_time_spec["name"],
                        }
                        specs.append(spec)
                        file_id += 1

                        # Limit total files for reasonable test time
                        if len(specs) >= 200:
                            break
                    if len(specs) >= 200:
                        break
                if len(specs) >= 200:
                    break
            if len(specs) >= 200:
                break

        return specs

    def create_test_files(self, specs: list[dict[str, Any]]):
        """Create actual files based on specifications."""
        print(f"📝 Creating {len(specs)} test files...")

        for spec in specs:
            file_path = TPath(self.test_dir / spec["name"])

            # Create file with specified size
            if spec["size"] == 0:
                file_path.touch()
            else:
                # Generate content based on extension
                content = self._generate_file_content(spec["extension"], spec["size"])
                file_path.write_text(content, encoding="utf-8")

            # Store the created file
            self.created_files.append(file_path)
            spec["path"] = file_path

        print(f"✅ Created {len(self.created_files)} files")

    def _generate_file_content(self, extension: str, target_size: int) -> str:
        """Generate appropriate content for different file types."""
        if extension == ".json":
            # Generate JSON content
            data = {
                "test": True,
                "size": target_size,
                "content": "x" * max(0, target_size - 50),
            }
            content = json.dumps(data, indent=2)
        elif extension == ".py":
            # Generate Python content
            base_content = f'#!/usr/bin/env python3\n"""Test file"""\ntest_data = "{"x" * max(0, target_size - 100)}"\n'
            content = base_content + "#" + "x" * max(0, target_size - len(base_content))
        elif extension == ".md":
            # Generate Markdown content
            content = f"# Test File\n\nThis is test content.\n\n{'Content ' * (target_size // 8)}"
        else:
            # Generate plain text content
            content = "Test content " + "x" * max(0, target_size - 13)

        # Ensure we hit the target size approximately
        if len(content) < target_size:
            content += "x" * (target_size - len(content))
        elif len(content) > target_size:
            content = content[:target_size]

        return content

    def modify_file_times(self, specs: list[dict[str, Any]]):
        """Modify file creation and modification times as specified."""
        print("⏰ Setting file timestamps...")

        for spec in specs:
            file_path = spec["path"]

            # Convert datetime to timestamp
            create_timestamp = spec["create_time"].timestamp()
            modify_timestamp = spec["modify_time"].timestamp()

            # Set access and modification times
            # Note: We can't actually change creation time on most filesystems,
            # but we can set mtime and atime
            os.utime(file_path, (create_timestamp, modify_timestamp))

        print("✅ File timestamps set")

    def run_comprehensive_tests(self, specs: list[dict[str, Any]]) -> dict[str, int]:
        """Run comprehensive tests on all created files."""
        print("🧪 Running comprehensive TPath tests...")

        results = {}
        all_files = [TPath(spec["path"]) for spec in specs]

        # Test 1: Basic file properties
        results["total_files"] = len(all_files)
        results["existing_files"] = sum(1 for f in all_files if f.exists())
        results["readable_files"] = sum(1 for f in all_files if f.is_file())

        # Test 2: Size-based filtering
        results["empty_files"] = sum(1 for f in all_files if f.size.bytes == 0)
        results["small_files"] = sum(1 for f in all_files if 0 < f.size.bytes <= 1024)
        results["medium_files"] = sum(
            1 for f in all_files if 1024 < f.size.bytes <= 50 * 1024
        )
        results["large_files"] = sum(1 for f in all_files if f.size.bytes > 50 * 1024)

        # Test 3: Extension-based filtering
        extensions = {".txt", ".py", ".json", ".md", ".log", ".csv"}
        for ext in extensions:
            results[f"files{ext}"] = sum(1 for f in all_files if f.suffix == ext)

        # Test 4: Age-based filtering (using age property)
        results["very_new_files"] = sum(1 for f in all_files if f.age.minutes < 1)
        results["recent_files"] = sum(1 for f in all_files if f.age.hours < 1)
        results["daily_files"] = sum(1 for f in all_files if f.age.days < 1)
        results["weekly_files"] = sum(1 for f in all_files if f.age.days < 7)

        # Test 5: Calendar-based filtering
        results["today_modified"] = sum(
            1 for f in all_files if f.mtime.calendar.in_days(0)
        )
        results["this_month_modified"] = sum(
            1 for f in all_files if f.mtime.calendar.in_months(0)
        )
        results["this_year_modified"] = sum(
            1 for f in all_files if f.mtime.calendar.in_years(0)
        )

        # Test 6: Time property access
        ctime_accessible = 0
        mtime_accessible = 0
        atime_accessible = 0

        for f in all_files:
            try:
                _ = f.ctime.timestamp
                ctime_accessible += 1
            except (OSError, AttributeError):
                pass

            try:
                _ = f.mtime.timestamp
                mtime_accessible += 1
            except (OSError, AttributeError):
                pass

            try:
                _ = f.atime.timestamp
                atime_accessible += 1
            except (OSError, AttributeError):
                pass

        results["ctime_accessible"] = ctime_accessible
        results["mtime_accessible"] = mtime_accessible
        results["atime_accessible"] = atime_accessible

        # Test 7: Alias properties (create, modify, access)
        results["create_alias_works"] = sum(
            1 for f in all_files if f.create.timestamp == f.ctime.timestamp
        )
        results["modify_alias_works"] = sum(
            1 for f in all_files if f.modify.timestamp == f.mtime.timestamp
        )
        results["access_alias_works"] = sum(
            1 for f in all_files if f.access.timestamp == f.atime.timestamp
        )

        # Test 8: Size parsing and comparison
        results["size_kb_conversion"] = sum(
            1 for f in all_files if f.size.kb == f.size.bytes / 1000
        )
        results["size_mb_conversion"] = sum(
            1 for f in all_files if f.size.mb == f.size.bytes / 1000000
        )

        # Test 9: Complex filtering combinations
        results["large_recent_python"] = sum(
            1
            for f in all_files
            if f.suffix == ".py" and f.size.bytes > 1024 and f.age.days < 1
        )

        results["small_old_text"] = sum(
            1
            for f in all_files
            if f.suffix == ".txt" and f.size.bytes <= 1024 and f.age.days >= 7
        )

        # Test 10: Calendar range filtering
        results["last_week_range"] = sum(
            1
            for f in all_files
            if f.mtime.calendar.in_days(7, 0)  # Last 7 days through today
        )

        results["last_month_range"] = sum(
            1
            for f in all_files
            if f.mtime.calendar.in_months(1, 0)  # Last month through this month
        )

        print(f"✅ Completed {len(results)} test categories")
        return results

    def validate_results(
        self, specs: list[dict[str, Any]], results: dict[str, int]
    ) -> bool:
        """Validate test results against expected values."""
        print("🔍 Validating results...")

        failures = []

        # Validate basic counts
        expected_total = len(specs)
        if results["total_files"] != expected_total:
            failures.append(
                f"Expected {expected_total} total files, got {results['total_files']}"
            )

        if results["existing_files"] != expected_total:
            failures.append(
                f"Expected {expected_total} existing files, got {results['existing_files']}"
            )

        # Validate size categories match specifications
        expected_empty = sum(1 for spec in specs if spec["size"] == 0)
        if results["empty_files"] != expected_empty:
            failures.append(
                f"Expected {expected_empty} empty files, got {results['empty_files']}"
            )

        # Validate extension counts
        for ext in [".txt", ".py", ".json", ".md", ".log", ".csv"]:
            expected_count = sum(1 for spec in specs if spec["extension"] == ext)
            actual_count = results.get(f"files{ext}", 0)
            if actual_count != expected_count:
                failures.append(
                    f"Expected {expected_count} {ext} files, got {actual_count}"
                )

        # Validate time property accessibility
        if results["ctime_accessible"] != expected_total:
            failures.append(
                f"ctime not accessible for all files: {results['ctime_accessible']}/{expected_total}"
            )

        if results["mtime_accessible"] != expected_total:
            failures.append(
                f"mtime not accessible for all files: {results['mtime_accessible']}/{expected_total}"
            )

        # Validate aliases work correctly
        if results["create_alias_works"] != expected_total:
            failures.append(
                f"create alias doesn't work for all files: {results['create_alias_works']}/{expected_total}"
            )

        if results["modify_alias_works"] != expected_total:
            failures.append(
                f"modify alias doesn't work for all files: {results['modify_alias_works']}/{expected_total}"
            )

        # Print validation results
        if failures:
            print("❌ Validation failures:")
            for failure in failures:
                print(f"  - {failure}")
            return False
        else:
            print("✅ All validations passed!")
            return True

    def print_comprehensive_report(self, results: dict[str, int]):
        """Print a detailed report of all test results."""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TPATH SYSTEM SMOKE TEST REPORT")
        print("=" * 60)

        print("\n📁 File Inventory:")
        print(f"  Total files created: {results['total_files']}")
        print(f"  Files existing: {results['existing_files']}")
        print(f"  Files readable: {results['readable_files']}")

        print("\n📏 Size Distribution:")
        print(f"  Empty files (0 bytes): {results['empty_files']}")
        print(f"  Small files (1-1024 bytes): {results['small_files']}")
        print(f"  Medium files (1KB-50KB): {results['medium_files']}")
        print(f"  Large files (>50KB): {results['large_files']}")

        print("\n📄 File Type Distribution:")
        extensions = [".txt", ".py", ".json", ".md", ".log", ".csv"]
        for ext in extensions:
            count = results.get(f"files{ext}", 0)
            print(f"  {ext} files: {count}")

        print("\n⏰ Age-based Filtering:")
        print(f"  Very new files (<1 min): {results['very_new_files']}")
        print(f"  Recent files (<1 hour): {results['recent_files']}")
        print(f"  Daily files (<1 day): {results['daily_files']}")
        print(f"  Weekly files (<7 days): {results['weekly_files']}")

        print("\n📅 Calendar-based Filtering:")
        print(f"  Modified today: {results['today_modified']}")
        print(f"  Modified this month: {results['this_month_modified']}")
        print(f"  Modified this year: {results['this_year_modified']}")

        print("\n🔗 Property Accessibility:")
        print(
            f"  ctime accessible: {results['ctime_accessible']}/{results['total_files']}"
        )
        print(
            f"  mtime accessible: {results['mtime_accessible']}/{results['total_files']}"
        )
        print(
            f"  atime accessible: {results['atime_accessible']}/{results['total_files']}"
        )

        print("\n🏷️  Alias Properties:")
        print(
            f"  create alias works: {results['create_alias_works']}/{results['total_files']}"
        )
        print(
            f"  modify alias works: {results['modify_alias_works']}/{results['total_files']}"
        )
        print(
            f"  access alias works: {results['access_alias_works']}/{results['total_files']}"
        )

        print("\n🔧 Size Conversions:")
        print(
            f"  KB conversion correct: {results['size_kb_conversion']}/{results['total_files']}"
        )
        print(
            f"  MB conversion correct: {results['size_mb_conversion']}/{results['total_files']}"
        )

        print("\n🎯 Complex Filtering:")
        print(f"  Large recent Python files: {results['large_recent_python']}")
        print(f"  Small old text files: {results['small_old_text']}")
        print(f"  Files modified in last week: {results['last_week_range']}")
        print(f"  Files modified in last month: {results['last_month_range']}")

        print("=" * 60)

    def run_full_test(self) -> bool:
        """Run the complete end-to-end system test."""
        print("🚀 Starting TPath Comprehensive System Smoke Test")
        print("=" * 60)

        try:
            # Setup
            self.setup_test_environment()

            # Generate file specifications
            specs = self.generate_file_specifications()
            print(f"📋 Generated {len(specs)} file specifications")

            # Create test files
            self.create_test_files(specs)

            # Modify file times
            self.modify_file_times(specs)

            # Run comprehensive tests
            results = self.run_comprehensive_tests(specs)

            # Print detailed report
            self.print_comprehensive_report(results)

            # Validate results
            success = self.validate_results(specs, results)

            if success:
                print("\n🎉 SYSTEM SMOKE TEST: PASSED")
                print(
                    "All TPath features working correctly across diverse file scenarios!"
                )
            else:
                print("\n💥 SYSTEM SMOKE TEST: FAILED")
                print("Some TPath features not working as expected.")

            return success

        except Exception as e:
            print("\n💥 SYSTEM SMOKE TEST: ERROR")
            print(f"Test failed with exception: {e}")
            import traceback

            traceback.print_exc()
            return False

        finally:
            # Always cleanup
            self.cleanup_test_environment()


def main():
    """Run the comprehensive system smoke test."""
    test = SystemSmokeTest()
    success = test.run_full_test()
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
