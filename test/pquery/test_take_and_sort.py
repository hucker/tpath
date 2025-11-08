"""
Tests for PQuery take() and sort() methods.
"""

import os
import tempfile
import time
from collections.abc import Generator
from pathlib import Path

import pytest

from tpath import PQuery, TPath


@pytest.fixture
def test_files() -> Generator[Path, None, None]:
    """Create a temporary directory with test files of various sizes and ages."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        # Arrange
        files_info = [
            ("small.txt", 100, 1000),
            ("medium.txt", 5000, 800),
            ("large.txt", 50000, 600),
            ("huge.txt", 500000, 400),
            ("tiny.txt", 10, 200),
            ("alpha.txt", 1000, 300),
            ("beta.txt", 2000, 500),
            ("gamma.txt", 3000, 700),
        ]
        current_time = time.time()
        for name, size, age_seconds in files_info:
            file_path = temp_path / name
            with open(file_path, "w") as f:
                f.write("x" * size)
            mtime = current_time - age_seconds
            os.utime(file_path, (mtime, mtime))
        yield temp_path


class TestTakeMethod:
    """Tests for the take() method."""

    def test_take_without_key(self, test_files: Path) -> None:
        """Test take() without key just returns first n files."""
        query = PQuery().from_(paths=test_files)
        files = query.take(3)

        assert len(files) == 3
        assert all(isinstance(f, TPath) for f in files)

    def test_take_largest_files(self, test_files: Path) -> None:
        """Test take() with size key returns largest files."""
        query = PQuery().from_(paths=test_files)
        largest = query.take(3, key=lambda p: p.size.bytes)

        assert len(largest) == 3
        # Should be in order: huge.txt (500KB), large.txt (50KB), medium.txt (5KB)
        assert largest[0].name == "huge.txt"
        assert largest[1].name == "large.txt"
        assert largest[2].name == "medium.txt"

        # Verify sizes are in descending order
        sizes = [f.size.bytes for f in largest]
        assert sizes == sorted(sizes, reverse=True)

    def test_take_smallest_files(self, test_files: Path) -> None:
        """Test take() with reverse=False returns smallest files."""
        query = PQuery().from_(paths=test_files)
        smallest = query.take(3, key=lambda p: p.size.bytes, reverse=False)

        assert len(smallest) == 3
        # Should be in order: tiny.txt (10B), small.txt (100B), alpha.txt (1KB)
        assert smallest[0].name == "tiny.txt"
        assert smallest[1].name == "small.txt"
        assert smallest[2].name == "alpha.txt"

        # Verify sizes are in ascending order
        sizes = [f.size.bytes for f in smallest]
        assert sizes == sorted(sizes)

    def test_take_newest_files(self, test_files: Path) -> None:
        """Test take() with mtime key returns newest files."""
        query = PQuery().from_(paths=test_files)
        newest = query.take(3, key=lambda p: p.mtime.timestamp)

        assert len(newest) == 3
        # Should be newest first (largest timestamp)
        timestamps = [f.mtime.timestamp for f in newest]
        assert timestamps == sorted(timestamps, reverse=True)

    def test_take_oldest_files(self, test_files: Path) -> None:
        """Test take() with mtime and reverse=False returns oldest files."""
        query = PQuery().from_(paths=test_files)
        oldest = query.take(3, key=lambda p: p.mtime.timestamp, reverse=False)

        assert len(oldest) == 3
        # Should be oldest first (smallest timestamp)
        timestamps = [f.mtime.timestamp for f in oldest]
        assert timestamps == sorted(timestamps)

    def test_take_multi_column_sort(self, test_files: Path) -> None:
        """Test take() with tuple key for multi-column sorting."""
        query = PQuery().from_(paths=test_files)

        # Sort by size (descending), then by name (ascending)
        # For heapq.nlargest with tuples, we want: (size_desc, name_asc)
        # But heapq.nlargest finds the largest tuples, so we need to be careful
        files = query.take(5, key=lambda p: (p.size.bytes, p.name))

        assert len(files) == 5
        # First should be largest file by size
        assert files[0].name == "huge.txt"

        # Verify it's properly sorted by size descending (since we used nlargest)
        sizes = [f.size.bytes for f in files]
        for i in range(len(sizes) - 1):
            assert sizes[i] >= sizes[i + 1], f"Size not in descending order: {sizes}"

    def test_take_more_than_available(self, test_files: Path) -> None:
        """Test take() when requesting more files than available."""
        query = PQuery().from_(paths=test_files)
        files = query.take(100, key=lambda p: p.size.bytes)

        # Should return all available files (8 total)
        assert len(files) == 8

    def test_take_zero_files(self, test_files: Path) -> None:
        """Test take() with n=0."""
        query = PQuery().from_(paths=test_files)
        files = query.take(0, key=lambda p: p.size.bytes)

        assert len(files) == 0
        assert files == []

    def test_take_with_where_filter(self, test_files: Path) -> None:
        """Test take() combined with where() filter."""
        query = (
            PQuery().from_(paths=test_files).where(lambda p: p.size.bytes > 1000)
        )  # Files larger than 1KB

        largest = query.take(2, key=lambda p: p.size.bytes)

        assert len(largest) == 2
        assert all(f.size.bytes > 1000 for f in largest)
        # Should be huge.txt and large.txt
        assert largest[0].name == "huge.txt"
        assert largest[1].name == "large.txt"


class TestSortMethod:
    """Tests for the sort() method."""

    def test_sort_by_size_ascending(self, test_files: Path) -> None:
        """Test sort() by size in ascending order."""
        query = PQuery().from_(paths=test_files)
        files = query.sort(key=lambda p: p.size.bytes)

        assert len(files) == 8
        sizes = [f.size.bytes for f in files]
        assert sizes == sorted(sizes)

        # First should be smallest
        assert files[0].name == "tiny.txt"
        # Last should be largest
        assert files[-1].name == "huge.txt"

    def test_sort_by_size_descending(self, test_files: Path) -> None:
        """Test sort() by size in descending order."""
        query = PQuery().from_(paths=test_files)
        files = query.sort(key=lambda p: p.size.bytes, reverse=True)

        assert len(files) == 8
        sizes = [f.size.bytes for f in files]
        assert sizes == sorted(sizes, reverse=True)

        # First should be largest
        assert files[0].name == "huge.txt"
        # Last should be smallest
        assert files[-1].name == "tiny.txt"

    def test_sort_by_name(self, test_files: Path) -> None:
        """Test sort() by filename."""
        query = PQuery().from_(paths=test_files)
        files = query.sort(key=lambda p: p.name)

        assert len(files) == 8
        names = [f.name for f in files]
        assert names == sorted(names)

        # Should start with "alpha.txt"
        assert files[0].name == "alpha.txt"

    def test_sort_by_mtime(self, test_files: Path) -> None:
        """Test sort() by modification time."""
        query = PQuery().from_(paths=test_files)
        files = query.sort(key=lambda p: p.mtime.timestamp)

        assert len(files) == 8
        timestamps = [f.mtime.timestamp for f in files]
        assert timestamps == sorted(timestamps)

    def test_sort_multi_column(self, test_files: Path) -> None:
        """Test sort() with tuple key for multi-column sorting."""
        query = PQuery().from_(paths=test_files)

        # Sort by first letter of name, then by size
        files = query.sort(key=lambda p: (p.name[0], p.size.bytes))

        assert len(files) == 8

        # Verify sorting is correct
        expected_keys = [(f.name[0], f.size.bytes) for f in files]
        assert expected_keys == sorted(expected_keys)

    def test_sort_without_key(self, test_files: Path) -> None:
        """Test sort() without key sorts by default TPath ordering."""
        query = PQuery().from_(paths=test_files)
        files = query.sort()

        assert len(files) == 8
        # Should be sorted by path/name
        names = [f.name for f in files]
        assert names == sorted(names)

    def test_sort_with_where_filter(self, test_files: Path) -> None:
        """Test sort() combined with where() filter."""
        query = (
            PQuery()
            .from_(paths=test_files)
            .where(lambda p: p.name.startswith(("a", "b", "g")))
        )  # alpha, beta, gamma

        files = query.sort(key=lambda p: p.size.bytes)

        assert len(files) == 3
        assert all(f.name.startswith(("a", "b", "g")) for f in files)

        # Should be sorted by size: alpha (1KB), beta (2KB), gamma (3KB)
        assert files[0].name == "alpha.txt"
        assert files[1].name == "beta.txt"
        assert files[2].name == "gamma.txt"


class TestTakeVsSortPerformance:
    """Tests comparing take() vs sort() behavior."""

    def test_take_vs_sort_results(self, test_files: Path) -> None:
        """Test that take() and sort() give same results for top-k."""
        query = PQuery().from_(paths=test_files)

        # Get top 3 largest files using both methods
        take_result = query.take(3, key=lambda p: p.size.bytes)
        sort_result = query.sort(key=lambda p: p.size.bytes, reverse=True)[:3]

        # Should have same files in same order
        assert len(take_result) == len(sort_result)
        for take_file, sort_file in zip(take_result, sort_result, strict=True):
            assert take_file.name == sort_file.name
            assert take_file.size.bytes == sort_file.size.bytes

    def test_take_efficiency_vs_sort(self, test_files: Path) -> None:
        """Test that take() is efficient for small k vs large n."""
        query = PQuery().from_(paths=test_files)

        # Both should give same result
        take_result = query.take(2, key=lambda p: p.size.bytes)
        all_sorted = query.sort(key=lambda p: p.size.bytes, reverse=True)
        sort_result = all_sorted[:2]

        assert len(take_result) == len(sort_result) == 2
        assert take_result[0].name == sort_result[0].name
        assert take_result[1].name == sort_result[1].name


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_directory(self):
        """Test take() and sort() on empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            query = PQuery().from_(paths=temp_dir)

            assert query.take(5) == []
            assert query.sort() == []
            assert query.take(5, key=lambda p: p.size.bytes) == []
            assert query.sort(key=lambda p: p.size.bytes) == []

    def test_nonexistent_directory(self):
        """Test take() and sort() on nonexistent directory."""
        query = PQuery().from_(paths="/nonexistent/path/12345")

        assert query.take(5) == []
        assert query.sort() == []

    def test_negative_take_count(self, test_files: Path) -> None:
        """Test take() with negative count."""
        query = PQuery().from_(paths=test_files)

        # heapq.nlargest handles negative n gracefully
        files = query.take(-1, key=lambda p: p.size.bytes)
        assert files == []
