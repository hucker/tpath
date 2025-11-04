#!/usr/bin/env python3
"""
Demo script showing the new intuitive calendar API with negative time offsets.
"""

from pathlib import Path

from src.tpath import TPath

def main():
    # Create some demo files to work with
    demo_dir = Path("demo_files")
    demo_dir.mkdir(exist_ok=True)
    
    # Create a test file
    test_file = demo_dir / "test.txt"
    test_file.write_text("Hello, world!")
    
    # Convert to TPath for enhanced functionality
    tfile = TPath(test_file)
    
    print("New Intuitive Calendar API Demo")
    print("=" * 40)
    print(f"File: {tfile}")
    print(f"Modified: {tfile.mtime.datetime}")
    print()
    
    print("Calendar Window Examples:")
    print("(Negative = past, 0 = now, positive = future)")
    print()
    
    # Examples of the new intuitive API
    examples = [
        ("Last 7 days through today", "win_days(-7, 0)"),
        ("Last 30 days through today", "win_days(-30, 0)"),
        ("Last week (7 days ago to 1 day ago)", "win_days(-7, -1)"),
        ("Last 2 hours through now", "win_hours(-2, 0)"),
        ("Last 6 months through today", "win_months(-6, 0)"),
        ("Last quarter through today", "win_quarters(-1, 0)"),
    ]
    
    for description, method_call in examples:
        # Use eval to dynamically call the method on our cal object
        result = eval(f"tfile.mtime.cal.{method_call}")
        # The cal methods return True/False for whether the file is in the window
        status = "✓ YES" if result else "✗ NO"
        print(f"📅 {description:.<40} {status}")
        print(f"   Code: file.mtime.cal.{method_call}")
        print()
    
    print("✨ The API now uses mathematical conventions:")
    print("   • Negative numbers = past")
    print("   • Zero = now/today") 
    print("   • Positive numbers = future")
    print("   • win_* methods clearly indicate window checking")
    print("   • start/end parameter names are intuitive")
    
    # Cleanup
    test_file.unlink()
    demo_dir.rmdir()

if __name__ == "__main__":
    main()