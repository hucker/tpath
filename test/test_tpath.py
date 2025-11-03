"""
Test file for TPath functionality.
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add the src directory to the path so we can import tpath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tpath.tpath import TPath, Size


def test_basic_functionality():
    """Test basic TPath functionality."""
    print("Testing TPath basic functionality...")
    
    # Create a test file
    test_file = TPath("test_file.txt")
    test_file.write_text("Hello, World! This is a test file for TPath.")
    
    print(f"File created: {test_file}")
    print(f"File exists: {test_file.exists()}")
    print(f"File size in bytes: {test_file.size.bytes}")
    print(f"File size in KB: {test_file.size.kb:.2f}")
    print(f"File size in MB: {test_file.size.mb:.6f}")
    print(f"File size in KiB: {test_file.size.kib:.2f}")
    
    # Test age functionality
    print(f"\nAge functionality:")
    print(f"Age in seconds: {test_file.age.seconds:.2f}")
    print(f"Age in minutes: {test_file.age.minutes:.6f}")
    print(f"Age in hours: {test_file.age.hours:.8f}")
    print(f"Age in days: {test_file.age.days:.10f}")
    
    # Test different time types
    print(f"\nDifferent time types:")
    print(f"Creation time age (days): {test_file.ctime.age.days:.10f}")
    print(f"Modification time age (days): {test_file.mtime.age.days:.10f}")
    print(f"Access time age (days): {test_file.atime.age.days:.10f}")
    
    # Test with custom base time
    yesterday = datetime.now() - timedelta(days=1)
    old_path = test_file.with_base_time(yesterday)
    print(f"\nWith base time set to yesterday:")
    print(f"Age in days: {old_path.age.days:.2f}")
    
    # Clean up
    test_file.unlink()
    print(f"\nTest file deleted: {not test_file.exists()}")


def test_size_parsing():
    """Test size string parsing functionality."""
    print("\nTesting size string parsing...")
    
    test_cases = [
        "100",
        "1KB",
        "1KiB", 
        "2.5MB",
        "1.5GiB",
        "0.5TB"
    ]
    
    for size_str in test_cases:
        try:
            bytes_value = Size.fromstr(size_str)
            print(f"{size_str:>8} -> {bytes_value:>12} bytes")
        except ValueError as e:
            print(f"{size_str:>8} -> Error: {e}")


def test_pathlib_compatibility():
    """Test that TPath maintains pathlib.Path compatibility."""
    print("\nTesting pathlib compatibility...")
    
    # Create a TPath
    tpath_obj = TPath(".")
    regular_path = Path(".")
    
    print(f"TPath absolute: {tpath_obj.absolute()}")
    print(f"Path absolute:  {regular_path.absolute()}")
    print(f"TPath is_dir(): {tpath_obj.is_dir()}")
    print(f"Path is_dir():  {regular_path.is_dir()}")
    
    # Test that we can still use all Path methods
    print(f"TPath parent: {tpath_obj.parent}")
    print(f"TPath name: {tpath_obj.name}")
    print(f"TPath suffix: {tpath_obj.suffix}")


if __name__ == "__main__":
    test_basic_functionality()
    test_size_parsing()
    test_pathlib_compatibility()
    print("\nAll tests completed!")