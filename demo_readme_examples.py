#!/usr/bin/env python3
"""
Demo script showcasing the calendar windowing functionality described in the README.
This demonstrates the property-based design philosophy of TPath.
"""

from pathlib import Path
from tpath import TPath
import tempfile
import time
import os
from datetime import datetime, timedelta

def main():
    print("TPath Calendar Window Filtering Demo")
    print("=" * 50)
    print("Demonstrating property-based file operations vs. raw timestamp calculations")
    print()
    
    # Create temporary directory with test files
    test_dir = Path(tempfile.mkdtemp(prefix="tpath_demo_"))
    print(f"Creating demo files in: {test_dir}")
    
    try:
        # Create files with different timestamps
        files_to_create = [
            ("today.txt", 0),          # Now
            ("yesterday.txt", -86400), # 1 day ago
            ("last_week.txt", -604800), # 7 days ago
            ("last_month.py", -2592000), # 30 days ago
            ("old_log.log", -7776000),  # 90 days ago
        ]
        
        created_files = []
        for filename, offset in files_to_create:
            file_path = TPath(test_dir / filename)
            file_path.write_text(f"Demo content created {abs(offset//86400)} days ago")
            
            # Set the timestamp
            timestamp = time.time() + offset
            os.utime(file_path, (timestamp, timestamp))
            created_files.append(file_path)
        
        print(f"Created {len(created_files)} files with different timestamps")
        print()
        
        # Demonstrate the philosophy: Property-based vs. Raw calculations
        print("🔍 TPath Philosophy Demo: Property-Based vs. Raw Timestamps")
        print("-" * 60)
        
        example_file = created_files[2]  # last_week.txt
        print(f"Example file: {example_file.name}")
        print(f"Modified: {example_file.mtime.datetime}")
        print()
        
        # The OLD way (complex calculations)
        print("❌ OLD WAY - Complex timestamp calculations:")
        print("```python")
        print("from pathlib import Path")
        print("from datetime import datetime, timedelta")
        print("import os")
        print()
        print("path = Path('last_week.txt')")
        print("stat = path.stat()")
        print("mtime = stat.st_mtime")
        print("age_seconds = datetime.now().timestamp() - mtime")
        print("age_days = age_seconds / 86400  # Remember: 60*60*24 = 86400")
        print("today = datetime.now().date()")
        print("file_date = datetime.fromtimestamp(mtime).date()")
        print("last_week = today - timedelta(days=7)")
        print("is_from_last_week = last_week <= file_date <= today")
        print("```")
        print()
        
        # The NEW way (property-based)
        print("✅ TPATH WAY - Direct, readable properties:")
        print("```python")
        print("from tpath import TPath")
        print()
        print("path = TPath('last_week.txt')")
        print("age_days = path.age.days")
        print("is_from_last_week = path.mtime.cal.win_days(-7, 0)")
        print("```")
        print()
        
        # Show actual values
        print("📊 Actual Results:")
        print(f"   Age in days: {example_file.age.days:.1f}")
        print(f"   From last week: {example_file.mtime.cal.win_days(-7, 0)}")
        print(f"   Modified today: {example_file.mtime.cal.win_days(0)}")
        print()
        
        # Calendar Window Examples
        print("📅 Calendar Window Filtering Examples")
        print("-" * 40)
        
        for file_path in created_files:
            print(f"\n📄 {file_path.name}")
            print(f"   Modified: {file_path.mtime.datetime.strftime('%Y-%m-%d %H:%M')}")
            print(f"   Age: {file_path.age.days:.1f} days")
            
            # Test various windows
            tests = [
                ("Today", "win_days(0)"),
                ("This week", "win_days(-7, 0)"),
                ("This month", "win_months(0)"),
                ("Last 30 days", "win_days(-30, 0)"),
                ("Last quarter", "win_months(-3, 0)"),
            ]
            
            for desc, method in tests:
                result = eval(f"file_path.mtime.cal.{method}")
                status = "✓" if result else "✗"
                print(f"   {status} {desc}: {method}")
        
        print()
        
        # Real-world filtering examples
        print("🎯 Real-World Filtering Examples")
        print("-" * 35)
        
        # Find files from last week
        last_week_files = [f for f in created_files if f.mtime.cal.win_days(-7, 0)]
        print(f"Files from last 7 days: {len(last_week_files)}")
        for f in last_week_files:
            print(f"  • {f.name}")
        
        # Find old files (older than 30 days)
        old_files = [f for f in created_files if not f.mtime.cal.win_days(-30, 0)]
        print(f"\nFiles older than 30 days: {len(old_files)}")
        for f in old_files:
            print(f"  • {f.name} ({f.age.days:.0f} days old)")
        
        # Find Python files
        python_files = [f for f in created_files if f.suffix == '.py']
        print(f"\nPython files: {len(python_files)}")
        for f in python_files:
            in_last_month = f.mtime.cal.win_days(-30, 0)
            status = "recent" if in_last_month else "old"
            print(f"  • {f.name} ({status})")
        
        print()
        print("✨ Key Benefits of TPath's Property-Based Design:")
        print("   • No mental math or timestamp calculations")
        print("   • Self-documenting code (win_days(-7, 0) = 'last 7 days')")
        print("   • Less error-prone (no magic numbers like 86400)")
        print("   • More readable and maintainable")
        print("   • Direct properties for common operations")
        
    finally:
        # Cleanup
        for file_path in created_files:
            file_path.unlink(missing_ok=True)
        test_dir.rmdir()
        print(f"\nCleaned up demo files from: {test_dir}")

if __name__ == "__main__":
    main()