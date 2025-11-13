# TPath - Enhanced pathlib with Age, Size, and Calendar Utilities

TPath is a `p`athlib.Pat`h subclass that provides first-class age, size, and calendar windowing functions for file operations. It allows you to work with files using natural, expressive syntax focused on **properties rather than calculations**.

## Philosophy: Property-Based File Operations

**The core goal of `TPath` is to create a file object system that is property-based rather than providing a single entry point of timestamp from which the end user must perform all calculations.**

Instead of giving you raw timestamps and forcing you to do mental math, TPath provides direct properties for the things you actually need in real-world file operations, resulting in **readable, maintainable code**.

### The Problem with Raw Timestamps

Traditional file libraries give you timestamps and leave you to figure out the rest:

```python
from pathlib import Path
from datetime import datetime, timedelta
import os

path = Path("logfile.txt")
stat = path.stat()
mtime = stat.st_mtime

# Complex calculations required for common operations
age_seconds = datetime.now().timestamp() - mtime
age_days = age_seconds / 86400  # Remember: 60*60*24 = 86400
size_mb = stat.st_size / 1048576  # Remember: 1024*1024 = 1048576

# Calendar window checking requires even more complex logic
today = datetime.now().date()
file_date = datetime.fromtimestamp(mtime).date()
last_week = today - timedelta(days=7)
is_from_last_week = last_week <= file_date <= today

if age_days > 7 and size_mb > 100 and is_from_last_week:
    print(f"Large file from last week: {age_days:.1f} days, {size_mb:.1f} MB")
```

### `TPath` Solution: Properties for Everything You Need

```python
from tpath import TPath

# Direct, readable properties - no calculations needed
path = TPath("logfile.txt")

if path.age.days > 7 and path.size.mb > 100 and path.mtime.cal.in_days(-7, 0):
    print(f"Large file from last week: {path.age.days:.1f} days, {path.size.mb:.1f} MB")
```

**No mental overhead. No error-prone calculations. Just readable code that expresses intent clearly.**

## Installation

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

# File querying with PQuery
from tpath import PQuery
large_files = PQuery().where(lambda p: p.size.mb > 10).files()
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

# Calendar window properties
print(f"Modified today: {path.mtime.cal.in_days(0)}")
print(f"Modified this week: {path.mtime.cal.in_days(-7, 0)}")
```

### Shell-Style Pattern Matching

Standalone `matches()` function for shell-style pattern matching:

```python
from tpath import matches

# Basic pattern matching
print(f"Is Python file: {matches('script.py', '*.py')}")
print(f"Is log file: {matches('app.log', '*.log', '*.LOG', case_sensitive=False)}")

# Multiple patterns and wildcards
matches("backup_2024.zip", "backup_202[3-4]*")       # True
matches("report.pdf", "*.pdf", "*.docx", "*.txt")    # True
```

### Pattern Examples

```python
# File extensions
matches("document.pdf", "*.pdf")                      # Standard extension
matches("script.py", "*.py", "*.js", "*.ts")          # Multiple extensions

# Wildcards
matches("backup_2024_12_25.zip", "backup_*")          # Prefix matching
matches("temp_file_123.txt", "*_temp_*", "*temp*")    # Contains pattern
matches("file.backup.old", "*.*.old")                 # Multiple dots

# Character classes  
matches("data2024.csv", "data[0-9][0-9][0-9][0-9]*") # Year pattern
matches("fileA.txt", "file[A-Z].*")                   # Letter range
matches("config_prod.ini", "*[!dev]*")                # Exclude pattern

# Real-world patterns
matches("error.log.2024-01", "*.log.*")               # Rotated logs
matches("Thumbs.db", "[Tt]humbs.db")                  # Case variants
matches("~document.tmp", "~*", "*.tmp", ".*")         # Temporary patterns
```

### Supported Pattern Syntax

| Pattern  | Description                   | Example         | Matches                    |
| -------- | ----------------------------- | --------------- | -------------------------- |
| `*`      | Any sequence of characters    | `*.log`         | `app.log`, `error.log.old` |
| `?`      | Any single character          | `file?.txt`     | `file1.txt`, `fileA.txt`   |
| `[seq]`  | Any character in sequence     | `data[0-9].csv` | `data1.csv`, `data9.csv`   |
| `[!seq]` | Any character NOT in sequence | `*[!0-9].txt`   | `fileA.txt`, `file_.txt`   |
| `[a-z]`  | Character range               | `[A-Z]*.py`     | `Main.py`, `Test.py`       |

### Performance Notes

- `matches()` is optimized for single file checking
- For bulk operations, combine with PQuery's lazy evaluation
- Pattern compilation is cached internally for repeated use
- Use `full_path=False` (default) when possible for better performance

## Advanced Features

### Calendar Window Filtering

**TPath provides intuitive calendar window filtering to check if files fall within specific time ranges.** This is perfect for finding files from "last week", "this month", "last quarter", etc. These capabilities all derive from the [`frist` package](https://github.com/hucker/frist).

### Key Features

- **Intuitive API**: Negative numbers = past, 0 = now, positive = future
- **Window checking**: `in_*` methods clearly indicate boundary checking (not duration measurement)
- **Mathematical conventions**: Follows standard mathematical notation for time offsets
- **Multiple time units**: Minutes, hours, days, months, quarters, years

### Basic Calendar Windows

```python
from tpath import TPath

path = TPath("document.txt")

# Single time point checks
path.mtime.cal.in_days(0)        # Modified today
path.mtime.cal.in_months(0)      # Modified this month  
path.mtime.cal.in_years(0)       # Modified this year

# Past time windows
path.mtime.cal.in_days(-1)       # Modified yesterday
path.mtime.cal.in_hours(-6)      # Modified 6 hours ago
path.mtime.cal.in_minutes(-30)   # Modified 30 minutes ago
```

### Range-Based Window Filtering

The real power comes from range-based filtering using `start` and `end` parameters:

```python
# Last 7 days through today
path.mtime.cal.in_days(-7, 0)

# Last 30 days through today  
path.mtime.cal.in_days(-30, 0)

# From 2 weeks ago through 1 week ago (excluding this week)
path.mtime.cal.in_days(-14, -7)

# Last 6 months through this month
path.mtime.cal.in_months(-6, 0)

# Last quarter only (excluding current quarter)
path.mtime.cal.in_quarters(-1, -1)

# Last 2 years through this year
path.mtime.cal.in_years(-2, 0)
```

### Real-World Examples

```python
from tpath import TPath
from pathlib import Path

# Find all Python files modified in the last week
project_dir = Path("my_project")
recent_python_files = [
    TPath(f) for f in project_dir.rglob("*.py") 
    if TPath(f).mtime.cal.in_days(-7, 0)
]

# Archive old log files (older than 30 days)
log_dir = Path("/var/log")
old_logs = [
    TPath(f) for f in log_dir.glob("*.log")
    if not TPath(f).mtime.cal.in_days(-30, 0)  # NOT in last 30 days
]

# Find large files created this quarter
large_recent_files = [
    TPath(f) for f in Path("/data").rglob("*")
    if TPath(f).size.mb > 100 and TPath(f).ctime.cal.in_quarters(0)
]

# Backup files from last month only
backup_candidates = [
    TPath(f) for f in Path("/important").rglob("*")
    if TPath(f).mtime.cal.in_months(-1, -1)  # Last month only
]
```

### Working with Different Time Types

TPath provides calendar filtering for all timestamp types:

```python
path = TPath("important_file.txt")

# Creation time windows
path.ctime.cal.in_days(-7, 0)     # Created in last 7 days
path.create.cal.in_months(0)      # Created this month (alias)

# Modification time windows  
path.mtime.cal.in_hours(-6, 0)    # Modified in last 6 hours
path.modify.cal.in_days(-1)       # Modified yesterday (alias)

# Access time windows
path.atime.cal.in_minutes(-30, 0) # Accessed in last 30 minutes
path.access.cal.in_weeks(-2, 0)   # Accessed in last 2 weeks (alias)
```

### Precision vs. Convenience

**Important distinction**: Calendar windows check **boundaries**, not precise durations.

```python
# This checks if file was modified between "7 days ago at current time" and "now"
# The actual span varies from ~6-7 days depending on when you run it
path.mtime.cal.in_days(-7, 0)

# For precise duration checking, use age properties instead:
path.age.days < 7  # Exactly less than 7 * 24 hours
```

Calendar windows are perfect for **"last week", "this month", "last quarter"** type queries where you want natural calendar boundaries, not precise 168-hour periods.

### Config File Integration

**Perfect for reading configuration values!** All property types support parsing from strings:

```python
from tpath import TPath
from tpath._size import Size
from tpath._age import Age
from tpath._time import Time

# Parse size strings (great for config files)
max_size = Size.parse("100MB")        # → 100,000,000 bytes
cache_limit = Size.parse("1.5GiB")    # → 1,610,612,736 bytes
temp_limit = Size.parse("500MB")      # → 500,000,000 bytes

# Parse age/time duration strings
cache_expire = Age.parse("24h")        # → 86,400 seconds
cleanup_after = Age.parse("7d")        # → 604,800 seconds  
session_timeout = Age.parse("30m")     # → 1,800 seconds

# Parse datetime strings
backup_date = Time.parse("2023-12-25")           # → datetime object
log_time = Time.parse("2023-12-25 14:30:00")     # → datetime object
timestamp = Time.parse("1640995200")             # → Unix timestamp to datetime

# Real-world config file usage
config = {
    "cache": {"max_size": "1GB", "expire_after": "24h"},
    "backup": {"date": "2023-01-01", "max_size": "10GiB"}
}

# Parse and use config values
max_cache = Size.parse(config["cache"]["max_size"])
expire_time = Age.parse(config["cache"]["expire_after"])
backup_time = Time.parse(config["backup"]["date"])

# Use with actual files
if path.size.bytes > max_cache:
    print("File too large for cache!")
if path.age.seconds > expire_time:
    print("File expired!")
```

## Key Features & Benefits

- **Property-based design**: Direct access to common file properties without calculations
- **Full pathlib compatibility**: Drop-in replacement for pathlib.Path
- **Natural syntax**: `path.age.days` instead of complex timestamp math
- **Shell-style pattern matching**: Standalone `matches()` function with fnmatch wildcards
- **Calendar window filtering**: Intuitive `in_*` methods for time range checking
- **Comprehensive time units**: seconds, minutes, hours, days, weeks, months, quarters, years
- **Multiple size units**: bytes, KB/KiB, MB/MiB, GB/GiB, TB/TiB, PB/PiB
- **Config file integration**: Parse strings with Size.parse(), Age.parse(), Time.parse()
- **Different time types**: Handle ctime, mtime, atime separately with user-friendly aliases
- **Performance optimized**: Cached stat calls to avoid repeated filesystem operations
- **Mathematical conventions**: Negative = past, 0 = now, positive = future

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
