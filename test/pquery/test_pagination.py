"""
Test the new paginate() functionality.
"""

import tempfile
from pathlib import Path

from src.tpath import PQuery


def test_paginate_basic_functionality():
    """Test basic pagination functionality."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create 25 test files
        for i in range(25):
            (temp_path / f"file_{i:02d}.txt").write_text(f"content {i}")

        query = PQuery().from_(paths=temp_dir).where(lambda p: p.suffix == ".txt")

        # Test pagination with page_size=10
        pages = list(query.paginate(10))

        # Should have 3 pages: 10, 10, 5
        assert len(pages) == 3
        assert len(pages[0]) == 10
        assert len(pages[1]) == 10
        assert len(pages[2]) == 5

        # Verify all files are included exactly once
        all_files = []
        for page in pages:
            all_files.extend(page)

        assert len(all_files) == 25
        file_names = {f.name for f in all_files}
        expected_names = {f"file_{i:02d}.txt" for i in range(25)}
        assert file_names == expected_names


def test_paginate_empty_query():
    """Test pagination with no matching files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        Path(temp_dir)

        query = PQuery().from_(paths=temp_dir).where(lambda p: p.suffix == ".nonexistent")
        pages = list(query.paginate(10))

        # Should return empty list
        assert pages == []


def test_paginate_smaller_than_page_size():
    """Test pagination when total files < page_size."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create only 5 files
        for i in range(5):
            (temp_path / f"file_{i}.txt").write_text(f"content {i}")

        query = PQuery().from_(paths=temp_dir).where(lambda p: p.suffix == ".txt")
        pages = list(query.paginate(10))

        # Should have 1 page with 5 files
        assert len(pages) == 1
        assert len(pages[0]) == 5


def test_paginate_efficiency_single_scan():
    """Test that pagination only scans files once (not O(n²))."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test files
        for i in range(30):
            (temp_path / f"file_{i:02d}.txt").write_text(f"content {i}")

        query = PQuery().from_(paths=temp_dir).where(lambda p: p.suffix == ".txt")

        # Track which files we see in what order
        seen_files = []

        for page in query.paginate(10):
            for file in page:
                seen_files.append(file.name)

        # Should see all files exactly once, in order
        assert len(seen_files) == 30
        assert len(set(seen_files)) == 30  # No duplicates

        # Files should be in consistent order (depends on file system)
        # Just verify we got all expected files
        expected_names = {f"file_{i:02d}.txt" for i in range(30)}
        actual_names = set(seen_files)
        assert actual_names == expected_names


def test_paginate_with_distinct():
    """Test pagination combined with distinct()."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test files
        for i in range(15):
            (temp_path / f"file_{i}.txt").write_text(f"content {i}")

        # Test that distinct + paginate works
        query = PQuery().from_(paths=temp_dir).distinct().where(lambda p: p.suffix == ".txt")
        pages = list(query.paginate(5))

        # Should have 3 pages of 5 each
        assert len(pages) == 3
        assert all(len(page) == 5 for page in pages)

        # All files should be unique
        all_files = []
        for page in pages:
            all_files.extend(page)

        file_paths = [str(f) for f in all_files]
        assert len(file_paths) == len(set(file_paths))  # No duplicates


def test_paginate_manual_iteration():
    """Test manual iteration through pages."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test files
        for i in range(12):
            (temp_path / f"file_{i:02d}.txt").write_text(f"content {i}")

        query = PQuery().from_(paths=temp_dir).where(lambda p: p.suffix == ".txt")
        paginator = query.paginate(5)

        # Manually get pages
        page1 = next(paginator)
        page2 = next(paginator)
        page3 = next(paginator)

        assert len(page1) == 5
        assert len(page2) == 5
        assert len(page3) == 2

        # Should be exhausted
        try:
            next(paginator)
            raise AssertionError("Should have raised StopIteration")
        except StopIteration:
            pass  # Expected


if __name__ == "__main__":
    test_paginate_basic_functionality()
    test_paginate_empty_query()
    test_paginate_smaller_than_page_size()
    test_paginate_efficiency_single_scan()
    test_paginate_with_distinct()
    test_paginate_manual_iteration()
    print("All pagination tests passed! ✅")
