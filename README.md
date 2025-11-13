# TPath - Enhanced pathlib with Age, Size, and Calendar Utilities

TPath is a pathlib extension that provides first-class age, size, and calendar membership functions for file operations. It allows you to work with files using natural, expressive syntax focused on **properties rather than calculations**.

## Philosophy: Property-Based File Operations

**The core goal of TPath is to create a file object system that is property-based.**

Instead of giving you raw timestamps and forcing you to do mental math, TPath provides direct properties for the things you actually need in real-world file operations, resulting in **readable, maintainable code**. In order to accomplish a reduction in cognitive load the Path object was overloaded to have a reference time (almost always set to `datetime.now()`) that allows file ages to be directly measured providing easy access to time information for '`create`, `access` and `modify`.  These details are handled behind the scenes and enable property based ages and membership, minimal calls to `os.stat/path.stat` and nearly zero calculations for all file properties.  

### The Problem with Raw Timestamps

Traditional file libraries give you timestamps and force you into complex, error-prone calculations:

```python
from pathlib import Path
from datetime import datetime
import os

# Simple example: Find files older than 7 days
old_files = []
for path in Path("/var/log").rglob("*"):
    if path.is_file():
        stat = path.stat()
        # Manual age calculation - easy to get wrong
        age_seconds = datetime.now().timestamp() - stat.st_mtime
        age_days = age_seconds / 86400  # Remember: 60*60*24 = 86400
        size_mb = stat.st_size / 1048576  # Remember: 1024*1024 = 1048576
        
        if age_days > 7 and size_mb > 10:
            old_files.append(path)

print(f"Found {len(old_files)} old files")
```

But what about more complex queries? Traditional approaches fall apart quickly:

```python
import fnmatch
from datetime import timedelta

# Complex example: Backup candidates from multiple criteria
backup_candidates = []
for base_dir in ["/home/user/docs", "/home/user/projects"]:
    for file_path in Path(base_dir).rglob("*"):
        if not file_path.is_file():
            continue
            
        # Complex pattern matching across multiple extensions
        if not (fnmatch.fnmatch(file_path.name, "*.doc*") or 
                fnmatch.fnmatch(file_path.name, "*.pdf") or
                fnmatch.fnmatch(file_path.name, "*.xls*")):
            continue
        
        stat = file_path.stat()
        
        # Manual size filtering
        if stat.st_size < 1048576:  # Less than 1MB
            continue
            
        # Complex date arithmetic for calendar-month boundaries
        # Want files from Aug 1st through Oct 31st (if today is Oct 15th)  
        mtime = datetime.fromtimestamp(stat.st_mtime)
        now = datetime.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        three_months_ago = (current_month_start.replace(month=current_month_start.month-3) 
                           if current_month_start.month > 3 
                           else current_month_start.replace(year=current_month_start.year-1, month=current_month_start.month+9))
        if mtime < three_months_ago:
            continue
            
        # More calculations for reporting
        age_days = (datetime.now() - mtime).days
        size_mb = stat.st_size / 1048576
        backup_candidates.append((file_path, size_mb, age_days))

print(f"Found {len(backup_candidates)} backup candidates")
```

### TPath Solution: What Becomes Easy

```python
from tpath import TPath

# Simple case: One line instead of a dozen
old_files = [f for f in Path("/var/log").rglob("*") 
             if TPath(f).age.days > 7 and TPath(f).size.mb > 10]
```

No mental overhead. No error-prone calculations. Just readable code that expresses intent clearly.

## Installation

THis project is **NOT ALIVE ON PYPI YET** at this time.

### Using uv (Recommended)

```bash
# Install directly from source
uv add git+https://github.com/yourusername/tpath.git

# Or for development
git clone https://github.com/yourusername/tpath.git
cd tpath
uv sync --dev
```

### Using pip

```bash
# Install from PyPI (when published)
pip install tpath

# Or install from source
pip install git+https://github.com/yourusername/tpath.git
```

## Quick Start

```python
from tpath import TPath, matches

# Create a TPath object - works like pathlib.Path (default time reference=dt.dateime.now())
path = TPath("my_file.txt")

# Direct property access - no calculations needed
print(f"File is {path.age.days} days old")
print(f"Size: {path.size.mb} MB")
print(f"Modified this week: {path.mtime.cal.in_days(-7, 0)}")

# Pattern matching
print(f"Is Python file: {matches(path, '*.py')}")
```

## Core Features

### TPath - Enhanced Path Objects

TPath extends pathlib.Path with property-based access to file metadata:

```python
from tpath import TPath

path = TPath("my_file.txt")

# Age properties
print(f"File is {path.age.days} days old")
print(f"Modified {path.mtime.age.minutes} minutes ago")

# Size properties  
print(f"File size: {path.size.mb} MB")
print(f"File size: {path.size.gib} GiB")

# Calendar membership properties
print(f"Modified today: {path.mtime.cal.in_days(0)}")
print(f"Modified this week: {path.mtime.cal.in_days(-7, 0)}")
```

### Shell-Style Pattern Matching

Standalone `matches()` function for shell-style pattern matching:

```python
from tpath import matches

# Use with TPath for file filtering
python_files = [f for f in Path("./src").rglob("*.py") if matches(f, "*.py")]

# Multiple patterns with case-insensitive matching
log_files = [f for f in Path("./logs").rglob("*") if matches(f, "*.log", "*.LOG", case_sensitive=False)]

# Complex pattern matching with wildcards
backup_files = [f for f in Path("./backups").rglob("*") if matches(f, "backup_202[3-4]*", "*important*")]
```

## Property-Based Design with Rich Features

TPath has evolved to become almost entirely property-based, offering a rich set of features that leverage the three core time objects in a file path: `ctime` (creation time), `mtime` (modification time), and `atime` (access time). These properties are seamlessly integrated with the powerful capabilities of the [Frist](https://github.com/hucker/frist) package, enabling advanced age and period operations.

### Core Time Properties

Each TPath object provides direct access to the following time-based properties:

- **`ctime`**: Creation time of the file.
- **`mtime`**: Last modification time of the file.
- **`atime`**: Last access time of the file.

These properties are enriched with Frist's advanced functionality, allowing you to perform intuitive and expressive operations directly on file paths.

### Examples of Property-Based Operations

```python
from tpath import TPath

# Create a TPath object
path = TPath("example.txt")

# Access time-based properties
print(f"Created: {path.ctime}")
print(f"Modified: {path.mtime}")
print(f"Accessed: {path.atime}")

# Calculate age directly
print(f"File age in days: {path.age.days}")
print(f"Modified {path.mtime.age.hours} hours ago")

# Calendar-based queries
print(f"Modified this week: {path.mtime.cal.in_days(-7, 0)}")
print(f"Created this month: {path.ctime.cal.in_months(0)}")
```

### Leveraging Frist's Power

The integration with Frist brings calendar and age properties to TPath objects. You can perform advanced time and calendar-based operations with ease:

```python
# Advanced calendar operations
print(f"Modified in the last quarter: {path.mtime.cal.in_quarters(-1, 0)}")
print(f"Accessed in the last year: {path.atime.cal.in_years(-1, 0)}")

# Rich age calculations
print(f"File age in seconds: {path.age.seconds}")
print(f"File age in weeks: {path.age.weeks}")
```

### Why Property-Based Design?

By focusing on properties rather than calculations, TPath reduces cognitive load and makes your code more readable and maintainable. You no longer need to write complex logic to calculate file ages or determine calendar memberships—everything is available as a property.

### Summary

TPath, powered by Frist, provides a property-based interface that simplifies file operations while offering rich, expressive features. Whether you're working with creation, modification, or access times, TPath ensures that all the power of Frist's advanced time and calendar operations is at your fingertips.

## Powered by Frist

TPath is built on top of the powerful [Frist](https://github.com/hucker/frist) package, which provides advanced age and period operations. All of Frist's capabilities are exposed through TPath objects, enabling you to leverage its time and calendar-based functionality within your file operations.

## Development

This project uses uv for dependency management and packaging. See UV_GUIDE.md for detailed instructions.

```bash
# Install development dependencies
uv sync --dev

# Run tests  
uv run python -m pytest

# Build package
uv build

# Format code
uv run ruff format

# Lint code
uv run ruff check
```

## License

MIT License - see LICENSE file for details.
