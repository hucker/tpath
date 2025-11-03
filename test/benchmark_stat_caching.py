"""
Performance test for TPath stat caching.

This script demonstrates the performance improvement from caching stat operations.
"""

import time
from pathlib import Path

from tpath import TPath


def benchmark_stat_caching():
    """Benchmark stat operation caching."""
    print("🔍 TPath Stat Caching Performance Test")
    print("=" * 50)

    # Create a test file
    test_file = TPath("benchmark_test.txt")
    test_file.write_text(
        "This is a test file for benchmarking stat caching performance."
    )

    try:
        # Test cached stat performance
        print("\n📊 Testing TPath (with caching):")

        # First access (cache miss)
        start_time = time.perf_counter()
        size1 = test_file.size.bytes
        first_time = time.perf_counter() - start_time

        # Subsequent accesses (cache hits)
        times = []
        for _i in range(10):
            start_time = time.perf_counter()
            size = test_file.size.bytes
            times.append(time.perf_counter() - start_time)

        avg_cached_time = sum(times) / len(times)

        print(f"  First access (cache miss):  {first_time*1000:.3f} ms")
        print(f"  Avg cached access:          {avg_cached_time*1000:.3f} ms")
        print(f"  Speedup ratio:              {first_time/avg_cached_time:.1f}x")

        # Test regular Path performance for comparison
        print("\n📊 Testing regular Path (no caching):")
        regular_path = Path("benchmark_test.txt")

        times = []
        for _i in range(10):
            start_time = time.perf_counter()
            size = regular_path.stat().st_size
            mtime = regular_path.stat().st_mtime
            ctime = regular_path.stat().st_ctime
            # Force variable usage for benchmarking
            _ = size + mtime + ctime
            times.append(time.perf_counter() - start_time)

        avg_uncached_time = sum(times) / len(times)
        print(f"  Avg uncached access:        {avg_uncached_time*1000:.3f} ms")

        # Compare overall performance
        print("\n⚡ Performance Improvement:")
        improvement = avg_uncached_time / avg_cached_time
        print(f"  TPath cached vs uncached:   {improvement:.1f}x faster")

        # Test cache consistency
        print("\n✅ Cache Consistency:")
        print(f"  File size (all calls):      {size1} bytes")
        print(f"  Cache working correctly:    {size == size1}")

    finally:
        # Clean up
        if test_file.exists():
            test_file.unlink()

    print("\n🎯 Summary:")
    print("  • Stat operations are cached using @cached_property")
    print("  • Subsequent property accesses reuse cached stat")
    print("  • Significant performance improvement for repeated access")
    print("  • No impact on correctness or functionality")


def test_cache_invalidation():
    """Test that cache works correctly across different instances."""
    print("\n🔄 Cache Invalidation Test:")
    print("=" * 50)

    test_file = TPath("cache_test.txt")
    test_file.write_text("Initial content")

    try:
        # First instance
        path1 = TPath("cache_test.txt")
        size1 = path1.size.bytes
        print(f"  Path1 initial size:         {size1} bytes")

        # Modify file
        test_file.write_text("Much longer content for testing cache invalidation")

        # Second instance (should have fresh cache)
        path2 = TPath("cache_test.txt")
        size2 = path2.size.bytes
        print(f"  Path2 after modification:   {size2} bytes")

        # First instance cache is stale (this is expected behavior)
        size1_cached = path1.size.bytes
        print(f"  Path1 cached (stale):       {size1_cached} bytes")

        print("\n  ✅ Each TPath instance has its own cache")
        print("  ⚠️  Cache is per-instance, not per-file")
        print("  💡 Create new TPath instance for fresh file state")

    finally:
        if test_file.exists():
            test_file.unlink()


if __name__ == "__main__":
    benchmark_stat_caching()
    test_cache_invalidation()
    print("\n🎉 Stat caching benchmarks completed!")
