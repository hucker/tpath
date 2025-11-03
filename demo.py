"""
Comprehensive test demonstrating TPath functionality that mimics pathql behavior.
"""

from datetime import datetime, timedelta

from tpath import Size, TPath


def demo_tpath_features():
    """Demonstrate key TPath features that replace pathql functionality."""

    print("=== TPath Demo: Lambda-based pathlib Extension ===\n")

    # Create test files with different ages and sizes
    test_files = []

    # Create files of different sizes
    small_file = TPath("small.txt")
    small_file.write_text("Small file content")
    test_files.append(small_file)

    medium_file = TPath("medium.txt")
    medium_file.write_text("Medium file content " * 100)
    test_files.append(medium_file)

    large_file = TPath("large.txt")
    large_file.write_text("Large file content " * 1000)
    test_files.append(large_file)

    print("1. Created test files with different sizes:")
    for file in test_files:
        print(f"   {file.name}: {file.size.bytes} bytes ({file.size.kb:.2f} KB)")

    print("\n2. Size operations (like pathql but with lambdas):")
    print("   Instead of: path.size > kb(5)  [pathql style]")
    print("   Use:        path.size.kb > 5   [TPath lambda style]")

    large_files = [f for f in test_files if f.size.kb > 1]
    print(f"   Files larger than 1KB: {[f.name for f in large_files]}")

    print("\n3. Age operations (lambda-based):")
    print("   Instead of: path.age > hours(1)  [pathql style]")
    print("   Use:        path.age.hours > 1   [TPath lambda style]")

    for file in test_files:
        print(f"   {file.name}: {file.age.seconds:.3f} seconds old")

    print("\n4. Different time types:")
    for file in test_files:
        print(f"   {file.name}:")
        print(f"     - Created: {file.ctime.age.seconds:.3f} seconds ago")
        print(f"     - Modified: {file.mtime.age.seconds:.3f} seconds ago")
        print(f"     - Accessed: {file.atime.age.seconds:.3f} seconds ago")

    print("\n5. Size string parsing (pathql-compatible):")
    size_strings = ["1KB", "1KiB", "2.5MB", "1.5GiB"]
    for size_str in size_strings:
        bytes_val = Size.parse(size_str)
        print(f"   '{size_str}' -> {bytes_val:,} bytes")

    print("\n6. Custom base time (age relative to other dates):")
    yesterday = datetime.now() - timedelta(days=1)
    for file in test_files:
        file_yesterday = file.with_base_time(yesterday)
        print(
            f"   {file.name} age relative to yesterday: {file_yesterday.age.days:.2f} days"
        )

    print("\n7. Practical filtering examples:")

    # Filter by size (lambda style vs pathql operator overloading)
    print("   Files larger than 1KB:")
    for file in test_files:
        if file.size.kb > 1:
            print(f"     - {file.name}: {file.size.kb:.2f} KB")

    print("   Files smaller than 0.5KB:")
    for file in test_files:
        if file.size.kb < 0.5:
            print(f"     - {file.name}: {file.size.kb:.2f} KB")

    # Filter by age (very young files since we just created them)
    print("   Files younger than 1 second:")
    for file in test_files:
        if file.age.seconds < 1:
            print(f"     - {file.name}: {file.age.seconds:.3f} seconds old")

    print("\n8. Chaining operations naturally:")
    for file in test_files:
        # Natural chaining with clear semantics
        size_mb = file.size.mb
        age_mins = file.age.minutes
        mod_hours = file.mtime.age.hours

        print(f"   {file.name}:")
        print(f"     Size: {size_mb:.6f} MB")
        print(f"     Age: {age_mins:.6f} minutes")
        print(f"     Last modified: {mod_hours:.8f} hours ago")

    print("\n9. Comparison with pathql syntax:")
    print("   pathql (operator overloading):")
    print("     files_old = [f for f in paths if f.age > days(7)]")
    print("     files_big = [f for f in paths if f.size > gb(1)]")
    print("   ")
    print("   TPath (lambda-based):")
    print("     files_old = [f for f in paths if f.age.days > 7]")
    print("     files_big = [f for f in paths if f.size.gb > 1]")
    print("   ")
    print("   Benefits of lambda approach:")
    print("     ✓ More explicit and readable")
    print("     ✓ Better IDE autocomplete support")
    print("     ✓ No operator overloading conflicts")
    print("     ✓ Clear method chaining")
    print("     ✓ Type hints work better")

    # Cleanup
    print("\n10. Cleanup:")
    for file in test_files:
        if file.exists():
            file.unlink()
            print(f"    Deleted: {file.name}")

    print("\n=== Demo Complete ===")
    print("\nKey takeaway: TPath provides pathql-like functionality")
    print("but uses lambdas instead of operator overloading for")
    print("cleaner, more maintainable code with better IDE support.")


if __name__ == "__main__":
    demo_tpath_features()
