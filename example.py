"""
Example usage of TPath - A pathlib extension with age and size utilities.

This example demonstrates how to use TPath's lambda-based approach for
file age and size operations.
"""

from datetime import datetime, timedelta

from tpath import Size, TPath


def main():
    print("=== TPath Example Usage ===\n")

    # Create a TPath object (works just like pathlib.Path)
    file_path = TPath("example_file.txt")

    # Create a sample file
    file_path.write_text(
        "This is an example file for demonstrating TPath functionality.\n" * 10
    )

    print("1. Basic Path Operations:")
    print(f"   File path: {file_path}")
    print(f"   File exists: {file_path.exists()}")
    print(f"   Is file: {file_path.is_file()}")
    print(f"   Parent directory: {file_path.parent}")

    print("\n2. Size Operations (Lambda-based):")
    print(f"   Size in bytes: {file_path.size.bytes}")
    print(f"   Size in KB: {file_path.size.kb:.2f}")
    print(f"   Size in KiB: {file_path.size.kib:.2f}")
    print(f"   Size in MB: {file_path.size.mb:.6f}")
    print(f"   Size in MiB: {file_path.size.mib:.6f}")

    print("\n3. Age Operations (Lambda-based, default to creation time):")
    print(f"   Age in seconds: {file_path.age.seconds:.2f}")
    print(f"   Age in minutes: {file_path.age.minutes:.6f}")
    print(f"   Age in hours: {file_path.age.hours:.8f}")
    print(f"   Age in days: {file_path.age.days:.10f}")

    print("\n4. Different Time Types:")
    print(f"   Creation time age (days): {file_path.ctime.age.days:.10f}")
    print(f"   Modification time age (days): {file_path.mtime.age.days:.10f}")
    print(f"   Access time age (days): {file_path.atime.age.days:.10f}")

    print("\n5. Custom Base Time (age relative to other dates):")
    # Age relative to yesterday
    yesterday = datetime.now() - timedelta(days=1)
    path_with_base = file_path.with_base_time(yesterday)
    print(f"   Age relative to yesterday: {path_with_base.age.days:.2f} days")

    # Age relative to a week ago
    week_ago = datetime.now() - timedelta(weeks=1)
    path_week_base = file_path.with_base_time(week_ago)
    print(f"   Age relative to a week ago: {path_week_base.age.weeks:.2f} weeks")

    print("\n6. Size String Parsing (like pathql):")
    size_examples = ["1KB", "2.5MB", "1.5GiB", "0.1TB"]
    for size_str in size_examples:
        bytes_value = Size.parse(size_str)
        print(f"   '{size_str}' = {bytes_value:,} bytes")

    print("\n7. Practical Examples:")

    # Find files older than 1 hour
    current_dir = TPath(".")
    print("   Files in current directory older than 1 hour:")
    for path in current_dir.iterdir():
        if path.is_file() and path.age.hours > 1:
            print(f"     - {path.name}: {path.age.hours:.2f} hours old")

    # Find large files (> 1KB)
    print("   Files larger than 1KB:")
    for path in current_dir.iterdir():
        if path.is_file() and path.size.bytes > 1000:
            print(f"     - {path.name}: {path.size.kb:.2f} KB")

    print("\n8. Lambda-like Usage Examples:")

    # You can chain operations naturally
    if file_path.exists():
        print(f"   File age in days: {file_path.age.days}")
        print(f"   File size in MB: {file_path.size.mb}")
        print(f"   Last modified (hours ago): {file_path.mtime.age.hours}")
        print(f"   Last accessed (minutes ago): {file_path.atime.age.minutes}")

    # Clean up
    file_path.unlink()
    print("\n   Cleanup: File deleted successfully")

    print("\n=== Example Complete ===")


if __name__ == "__main__":
    main()
