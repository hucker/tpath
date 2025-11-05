"""
Demo script showing age calculation with different time types.
"""

import time

from tpath import TPath

# Create a test file
test_file = TPath("age_demo.txt")
test_file.write_text("Initial content")

print("=== TPath Age Calculation Demo ===\n")

# Wait a moment, then modify the file
print("Waiting 2 seconds...")
time.sleep(2)
test_file.write_text("Modified content")

print(f"File: {test_file}")
print(f"File exists: {test_file.exists()}")

print("\n--- Age Calculations ---")

# Default age (uses creation time)
print(f"Default age (creation):     {test_file.age.seconds:.2f} seconds")

# Override to use modification time
print(f"Modification age:           {test_file.mtime.age.seconds:.2f} seconds")

# Override to use access time
print(f"Access age:                 {test_file.atime.age.seconds:.2f} seconds")

print("\n--- Using Aliases ---")
print(f"Creation age (alias):       {test_file.create.age.seconds:.2f} seconds")
print(f"Modification age (alias):   {test_file.modify.age.seconds:.2f} seconds")
print(f"Access age (alias):         {test_file.access.age.seconds:.2f} seconds")

print("\n--- Raw Timestamps ---")
print(f"Creation time:    {test_file.ctime.timestamp}")
print(f"Modification time: {test_file.mtime.timestamp}")
print(f"Access time:      {test_file.atime.timestamp}")

print("\n--- Age in Different Units ---")
print(f"Modification age in minutes: {test_file.mtime.age.minutes:.4f}")
print(f"Modification age in hours:   {test_file.mtime.age.hours:.6f}")

# Clean up
test_file.unlink()
print(f"\nCleaned up: {test_file}")
