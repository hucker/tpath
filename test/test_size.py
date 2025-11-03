"""
Test file for Size functionality (_size.py).
"""

import os
import sys

# Add the src directory to the path so we can import tpath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tpath import TPath, Size


def test_size_properties():
    """Test Size class properties and conversions."""
    print("Testing Size properties...")
    
    # Create a test file with known content
    test_file = TPath("test_size_file.txt")
    content = "Hello, World! This is a test file for size testing."
    test_file.write_text(content)
    
    try:
        size = test_file.size
        assert isinstance(size, Size)
        
        # Test basic size properties
        assert isinstance(size.bytes, int)
        assert size.bytes > 0
        assert size.bytes == len(content.encode('utf-8'))
        
        # Test decimal units (KB, MB, GB, TB)
        assert isinstance(size.kb, float)
        assert isinstance(size.mb, float)
        assert isinstance(size.gb, float)
        assert isinstance(size.tb, float)
        
        # Test binary units (KiB, MiB, GiB, TiB)
        assert isinstance(size.kib, float)
        assert isinstance(size.mib, float)
        assert isinstance(size.gib, float)
        assert isinstance(size.tib, float)
        
        # Test conversions are correct
        assert abs(size.kb - size.bytes / 1000) < 1e-10
        assert abs(size.mb - size.bytes / (1000 * 1000)) < 1e-10
        assert abs(size.kib - size.bytes / 1024) < 1e-10
        assert abs(size.mib - size.bytes / (1024 * 1024)) < 1e-10
        
        print(f"File size: {size.bytes} bytes")
        print(f"File size: {size.kb:.6f} KB")
        print(f"File size: {size.mb:.9f} MB")
        print(f"File size: {size.kib:.6f} KiB")
        print(f"File size: {size.mib:.9f} MiB")
        
        print("✅ Size properties tests passed")
        
    finally:
        # Clean up
        if test_file.exists():
            test_file.unlink()


def test_size_string_parsing():
    """Test Size.fromstr() method for parsing size strings."""
    print("Testing Size string parsing...")
    
    test_cases = [
        ("100", 100),
        ("1KB", 1000),
        ("1KiB", 1024),
        ("2.5MB", 2_500_000),
        ("1.5GiB", int(1.5 * 1024 * 1024 * 1024)),
        ("0.5TB", 500_000_000_000),
        ("2TiB", 2 * 1024 * 1024 * 1024 * 1024),
    ]
    
    for size_str, expected_bytes in test_cases:
        try:
            result = Size.fromstr(size_str)
            assert result == expected_bytes, f"Expected {expected_bytes}, got {result} for {size_str}"
            print(f"{size_str:>8} -> {result:>15} bytes ✅")
        except ValueError as e:
            print(f"{size_str:>8} -> Error: {e} ❌")
            raise
    
    print("✅ Size string parsing tests passed")


def test_size_string_parsing_errors():
    """Test Size.fromstr() error handling."""
    print("Testing Size string parsing error handling...")
    
    invalid_cases = [
        "invalid",
        "123XB",
        "",
        "1.2.3MB",
        "-100MB",
    ]
    
    for invalid_str in invalid_cases:
        try:
            Size.fromstr(invalid_str)
            print(f"❌ Expected error for '{invalid_str}' but got success")
            assert False, f"Should have raised ValueError for '{invalid_str}'"
        except ValueError:
            print(f"✅ Correctly rejected: '{invalid_str}'")
    
    print("✅ Size error handling tests passed")


def test_size_edge_cases():
    """Test Size class with edge cases."""
    print("Testing Size edge cases...")
    
    # Test zero size file
    zero_file = TPath("zero_size_test.txt")
    zero_file.write_text("")  # Empty file
    
    try:
        zero_size = zero_file.size
        assert zero_size.bytes == 0
        assert zero_size.kb == 0
        assert zero_size.mb == 0
        
        print(f"Zero size: {zero_size.bytes} bytes")
        
    finally:
        if zero_file.exists():
            zero_file.unlink()
    
    # Test large size calculation
    large_content = "x" * 1000000  # 1MB of content
    large_file = TPath("large_size_test.txt")
    large_file.write_text(large_content)
    
    try:
        large_size = large_file.size
        assert large_size.bytes == 1000000
        assert abs(large_size.mb - 1.0) < 0.001  # Close to 1MB
        
        print(f"Large size: {large_size.mb:.3f} MB")
        
    finally:
        if large_file.exists():
            large_file.unlink()
    
    print("✅ Size edge cases tests passed")


def test_size_comparison():
    """Test Size comparison functionality."""
    print("Testing Size comparisons...")
    
    # Create files of different sizes
    small_file = TPath("test_small.txt")
    large_file = TPath("test_large.txt")
    
    small_file.write_text("small")
    large_file.write_text("This is a much larger file with more content")
    
    try:
        small_size = small_file.size
        large_size = large_file.size
        
        # Test that larger file has larger size
        assert large_size.bytes > small_size.bytes
        
        # Test comparison with fromstr
        min_size_bytes = Size.fromstr("10")  # 10 bytes (smaller than our test files)
        assert large_size.bytes > min_size_bytes
        
        print(f"Small file: {small_size.bytes} bytes")
        print(f"Large file: {large_size.bytes} bytes")
        print(f"Minimum size: {min_size_bytes} bytes")
        
        print("✅ Size comparison tests passed")
        
    finally:
        # Clean up
        for file in [small_file, large_file]:
            if file.exists():
                file.unlink()


if __name__ == "__main__":
    test_size_properties()
    test_size_string_parsing()
    test_size_string_parsing_errors()
    test_size_edge_cases()
    test_size_comparison()
    print("\n✅ All size tests completed!")