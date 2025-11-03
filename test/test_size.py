"""
Test file for Size functionality (_size.py).
"""

import os
import sys
import pytest

# Add the src directory to the path so we can import tpath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tpath import TPath, Size


def test_size_properties():
    """Test Size class properties and conversions."""
    # Arrange
    test_file = TPath("test_size_file.txt")
    content = "Hello, World! This is a test file for size testing."
    test_file.write_text(content)
    
    try:
        # Act
        size = test_file.size
        
        # Assert
        assert isinstance(size, Size), f"Expected size to be Size instance, got {type(size)}"
        
        # Test basic size properties
        assert isinstance(size.bytes, int), f"Expected size.bytes to be int, got {type(size.bytes)}"
        assert size.bytes > 0, f"Expected size.bytes to be positive, got {size.bytes}"
        assert size.bytes == len(content.encode('utf-8')), f"Expected size.bytes ({size.bytes}) to equal content length ({len(content.encode('utf-8'))})"
        
        # Test decimal units (KB, MB, GB, TB, PB)
        assert isinstance(size.kb, float), f"Expected size.kb to be float, got {type(size.kb)}"
        assert isinstance(size.mb, float), f"Expected size.mb to be float, got {type(size.mb)}"
        assert isinstance(size.gb, float), f"Expected size.gb to be float, got {type(size.gb)}"
        assert isinstance(size.tb, float), f"Expected size.tb to be float, got {type(size.tb)}"
        assert isinstance(size.pb, float), f"Expected size.pb to be float, got {type(size.pb)}"
        
        # Test binary units (KiB, MiB, GiB, TiB, PiB)
        assert isinstance(size.kib, float), f"Expected size.kib to be float, got {type(size.kib)}"
        assert isinstance(size.mib, float), f"Expected size.mib to be float, got {type(size.mib)}"
        assert isinstance(size.gib, float), f"Expected size.gib to be float, got {type(size.gib)}"
        assert isinstance(size.tib, float), f"Expected size.tib to be float, got {type(size.tib)}"
        assert isinstance(size.pib, float), f"Expected size.pib to be float, got {type(size.pib)}"
        
        # Test conversions are correct
        assert abs(size.kb - size.bytes / 1000) < 1e-10, f"KB conversion incorrect: {size.kb} vs {size.bytes / 1000}"
        assert abs(size.mb - size.bytes / (1000 * 1000)) < 1e-10, f"MB conversion incorrect: {size.mb} vs {size.bytes / (1000 * 1000)}"
        assert abs(size.kib - size.bytes / 1024) < 1e-10, f"KiB conversion incorrect: {size.kib} vs {size.bytes / 1024}"
        assert abs(size.mib - size.bytes / (1024 * 1024)) < 1e-10, f"MiB conversion incorrect: {size.mib} vs {size.bytes / (1024 * 1024)}"
        
    finally:
        # Clean up
        if test_file.exists():
            test_file.unlink()


@pytest.mark.parametrize("size_str,expected_bytes", [
    ("100", 100),
    ("1KB", 1000),
    ("1KiB", 1024),
    ("2.5MB", 2_500_000),
    ("1.5GiB", int(1.5 * 1024 * 1024 * 1024)),
    ("0.5TB", 500_000_000_000),
    ("2TiB", 2 * 1024 * 1024 * 1024 * 1024),
    ("0.001PB", 1_000_000_000_000),
    ("1PIB", 1024 * 1024 * 1024 * 1024 * 1024),
])
def test_size_string_parsing(size_str, expected_bytes):
    """Test Size.fromstr() method for parsing size strings."""
    # Arrange - parameters provided by pytest
    
    # Act
    result = Size.fromstr(size_str)
    
    # Assert
    assert result == expected_bytes, f"Expected {expected_bytes}, got {result} for {size_str}"


@pytest.mark.parametrize("invalid_str", [
    "invalid",
    "123XB",
    "",
    "1.2.3MB",
    "-100MB",
])
def test_size_string_parsing_errors(invalid_str):
    """Test Size.fromstr() error handling."""
    # Arrange - parameter provided by pytest
    
    # Act & Assert
    with pytest.raises(ValueError):
        Size.fromstr(invalid_str)


def test_size_edge_cases():
    """Test Size class with edge cases."""
    # Arrange - Test zero size file
    zero_file = TPath("zero_size_test.txt")
    zero_file.write_text("")  # Empty file
    
    try:
        # Act
        zero_size = zero_file.size
        
        # Assert
        assert zero_size.bytes == 0, f"Expected zero size file to have 0 bytes, got {zero_size.bytes}"
        assert zero_size.kb == 0, f"Expected zero size file to have 0 KB, got {zero_size.kb}"
        assert zero_size.mb == 0, f"Expected zero size file to have 0 MB, got {zero_size.mb}"
        
    finally:
        if zero_file.exists():
            zero_file.unlink()
    
    # Arrange - Test large size calculation
    large_content = "x" * 1000000  # 1MB of content
    large_file = TPath("large_size_test.txt")
    large_file.write_text(large_content)
    
    try:
        # Act
        large_size = large_file.size
        
        # Assert
        assert large_size.bytes == 1000000, f"Expected large file to have 1000000 bytes, got {large_size.bytes}"
        assert abs(large_size.mb - 1.0) < 0.001, f"Expected large file to be close to 1MB, got {large_size.mb:.3f} MB"
        
    finally:
        if large_file.exists():
            large_file.unlink()
    
    # Arrange - Test fromstr method with large values
    huge_tb_str = "5TB"
    
    # Act
    huge_size = Size.fromstr(huge_tb_str)
    
    # Assert
    assert huge_size > 4 * 1024**4, f"Expected huge size to be > 4TB in bytes, got {huge_size} bytes"


def test_size_comparison():
    """Test Size comparison functionality."""
    # Arrange - Create files of different sizes
    small_file = TPath("test_small.txt")
    large_file = TPath("test_large.txt")
    
    small_file.write_text("small")
    large_file.write_text("This is a much larger file with more content")
    
    try:
        # Act
        small_size = small_file.size
        large_size = large_file.size
        min_size_bytes = Size.fromstr("3")  # 3 bytes (smaller than our test files)
        
        # Assert
        assert large_size.bytes > small_size.bytes, f"Expected large file ({large_size.bytes} bytes) to be larger than small file ({small_size.bytes} bytes)"
        assert large_size.bytes > min_size_bytes, f"Expected large file ({large_size.bytes} bytes) to be larger than minimum size ({min_size_bytes} bytes)"
        assert small_size.bytes > min_size_bytes, f"Expected small file ({small_size.bytes} bytes) to be larger than minimum size ({min_size_bytes} bytes)"
        
    finally:
        if small_file.exists():
            small_file.unlink()
        if large_file.exists():
            large_file.unlink()


if __name__ == "__main__":
    # Note: For parametrized tests, run with pytest instead:
    # pytest test/test_size.py -v
    test_size_properties()
    test_size_edge_cases()
    test_size_comparison()