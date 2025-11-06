# TPath - Enhanced pathlib with Age, Size, and Calendar Utilities

TPath is a pathlib extension that provides first-class age, size, and calendar windowing functions for file operations. It allows you to work with files using natural, expressive syntax focused on **properties rather than calculations**.

## Philosophy: Property-Based File Operations

**The core goal of TPath is to create a file object system that is property-based rather than providing a single entry point of timestamp from which the end user must perform all calculations.**

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

### TPath: Properties for Everything You Need

```python
from tpath import TPath

# Direct, readable properties - no calculations needed
path = TPath("logfile.txt")

if path.age.days > 7 and path.size.mb > 100 and path.mtime.cal.win_days(-7, 0):
    print(f"Large file from last week: {path.age.days:.1f} days, {path.size.mb:.1f} MB")
```

**No mental overhead. No error-prone calculations. Just readable code that expresses intent clearly.**

### With TPath (Direct, Readable Properties)

```python
from tpath import TPath

# Clean, readable, obvious
path = TPath("logfile.txt")

if path.age.days > 7 and path.size.mb > 100:
    print(f"Large old file: {path.age.days:.1f} days, {path.size.mb:.1f} MB")
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
from tpath import TPath

# Basic usage - works like pathlib.Path
path = TPath("my_file.txt")

# Age functionality
print(f"File is {path.age.days} days old")
print(f"File is {path.age.hours} hours old")
print(f"Modified {path.mtime.age.minutes} minutes ago")

# Size functionality  
print(f"File size: {path.size.mb} MB")
print(f"File size: {path.size.gib} GiB")

# Calendar window functionality
print(f"Modified today: {path.mtime.cal.win_days(0)}")
print(f"Modified this week: {path.mtime.cal.win_days(-7, 0)}")
print(f"Created this month: {path.ctime.cal.win_months(0)}")
```

## PQuery - Powerful File Querying

**PQuery provides a fluent, chainable API for filtering files based on age, size, and other properties.** It's designed for complex file filtering operations with readable, expressive syntax.

### Simple PQuery Examples

```python
from tpath import PQuery

# Simple queries with default starting directory (current directory)
q = PQuery()  # Starts from current directory by default

# Find all Python files
python_files = q.where(lambda p: p.suffix == '.py').files()

# Find files larger than 10MB
large_files = q.where(lambda p: p.size.mb > 10).files()

# Find files modified in the last 7 days
recent_files = q.where(lambda p: p.mtime.cal.win_days(-7, 0)).files()

# Find old, large log files
old_large_logs = (q
    .where(lambda p: p.suffix == '.log' and p.size.mb > 50 and p.age.days > 30)
    .files())
```

### Complex PQuery Examples

```python
from tpath import PQuery
from pathlib import Path

# Complex multi-criteria file cleanup query
cleanup_query = (PQuery()
    .from_("/var/log")
    .recursive(True)
    .where(lambda p: p.suffix in ['.log', '.tmp', '.cache'] and 
                     p.age.days > 30 and 
                     p.size.mb > 1 and 
                     not p.mtime.cal.win_days(-7, 0))
)

# Execute and process results
old_files = cleanup_query.files()
total_size = sum(f.size.bytes for f in old_files)
print(f"Found {len(old_files)} files totaling {total_size // 1024**2} MB")

# Project analysis query - find large source files that haven't been touched recently
project_analysis = (PQuery()
    .from_("./src")
    .recursive(True)
    .where(lambda p: p.suffix in ['.py', '.js', '.ts', '.cpp', '.h'] and
                     p.size.kb > 50 and  # Larger source files
                     p.mtime.age.days > 90 and  # Not modified in 90 days
                     p.name != '__init__.py')  # Exclude init files
)

stale_code = project_analysis.files()
for file in sorted(stale_code, key=lambda f: f.size.bytes, reverse=True):
    print(f"{file.name}: {file.size.kb:.1f} KB, {file.age.days} days old")

# Backup candidate identification
backup_candidates = (PQuery()
    .from_("/home/user/documents")
    .recursive(True)
    .where(lambda p: p.suffix in ['.doc', '.docx', '.pdf', '.xlsx'] and
                     p.size.mb > 5 and  # Important files are usually larger
                     p.ctime.cal.win_years(-1, 0) and  # Created within last year
                     p.mtime.cal.win_months(-1, 0))  # Modified within last month
)

important_files = backup_candidates.files()
print(f"Found {len(important_files)} important files for backup")
```

### PQuery Method Chaining

PQuery supports fluent method chaining for building complex queries:

```python
# Method chaining allows building complex queries step by step
query = (PQuery()
    .from_("/data")           # Set starting directory
    .recursive(True)             # Include subdirectories
    .where(lambda p: p.is_file() and p.size.gb > 1 and p.age.months > 6)  # Combined filters
)

# Execute when ready
results = query.files()
```

### Lazy Evaluation and Performance

PQuery uses lazy evaluation - filters are only applied when you call `.files()`:

```python
# Build the query (no filesystem operations yet)
q = PQuery().from_("/large/directory").where(lambda p: p.size.gb > 5)

# Only now does it scan the filesystem
large_files = q.files()  

# Reuse the same query multiple times
more_files = q.where(lambda p: p.suffix == '.mp4').files()
```

## Calendar Window Filtering

**TPath provides intuitive calendar window filtering to check if files fall within specific time ranges.** This is perfect for finding files from "last week", "this month", "last quarter", etc.

### Key Features

- **Intuitive API**: Negative numbers = past, 0 = now, positive = future
- **Window checking**: `win_*` methods clearly indicate boundary checking (not duration measurement)
- **Mathematical conventions**: Follows standard mathematical notation for time offsets
- **Multiple time units**: Minutes, hours, days, months, quarters, years

### Basic Calendar Windows

```python
from tpath import TPath

path = TPath("document.txt")

# Single time point checks
path.mtime.cal.win_days(0)        # Modified today
path.mtime.cal.win_months(0)      # Modified this month  
path.mtime.cal.win_years(0)       # Modified this year

# Past time windows
path.mtime.cal.win_days(-1)       # Modified yesterday
path.mtime.cal.win_hours(-6)      # Modified 6 hours ago
path.mtime.cal.win_minutes(-30)   # Modified 30 minutes ago
```

### Range-Based Window Filtering

The real power comes from range-based filtering using `start` and `end` parameters:

```python
# Last 7 days through today
path.mtime.cal.win_days(-7, 0)

# Last 30 days through today  
path.mtime.cal.win_days(-30, 0)

# From 2 weeks ago through 1 week ago (excluding this week)
path.mtime.cal.win_days(-14, -7)

# Last 6 months through this month
path.mtime.cal.win_months(-6, 0)

# Last quarter only (excluding current quarter)
path.mtime.cal.win_quarters(-1, -1)

# Last 2 years through this year
path.mtime.cal.win_years(-2, 0)
```

### Real-World Examples

```python
from tpath import TPath
from pathlib import Path

# Find all Python files modified in the last week
project_dir = Path("my_project")
recent_python_files = [
    TPath(f) for f in project_dir.rglob("*.py") 
    if TPath(f).mtime.cal.win_days(-7, 0)
]

# Archive old log files (older than 30 days)
log_dir = Path("/var/log")
old_logs = [
    TPath(f) for f in log_dir.glob("*.log")
    if not TPath(f).mtime.cal.win_days(-30, 0)  # NOT in last 30 days
]

# Find large files created this quarter
large_recent_files = [
    TPath(f) for f in Path("/data").rglob("*")
    if TPath(f).size.mb > 100 and TPath(f).ctime.cal.win_quarters(0)
]

# Backup files from last month only
backup_candidates = [
    TPath(f) for f in Path("/important").rglob("*")
    if TPath(f).mtime.cal.win_months(-1, -1)  # Last month only
]
```

### Working with Different Time Types

TPath provides calendar filtering for all timestamp types:

```python
path = TPath("important_file.txt")

# Creation time windows
path.ctime.cal.win_days(-7, 0)     # Created in last 7 days
path.create.cal.win_months(0)      # Created this month (alias)

# Modification time windows  
path.mtime.cal.win_hours(-6, 0)    # Modified in last 6 hours
path.modify.cal.win_days(-1)       # Modified yesterday (alias)

# Access time windows
path.atime.cal.win_minutes(-30, 0) # Accessed in last 30 minutes
path.access.cal.win_weeks(-2, 0)   # Accessed in last 2 weeks (alias)
```

### Precision vs. Convenience

**Important distinction**: Calendar windows check **boundaries**, not precise durations.

```python
# This checks if file was modified between "7 days ago at current time" and "now"
# The actual span varies from ~6-7 days depending on when you run it
path.mtime.cal.win_days(-7, 0)

# For precise duration checking, use age properties instead:
path.age.days < 7  # Exactly less than 7 * 24 hours
```

Calendar windows are perfect for **"last week", "this month", "last quarter"** type queries where you want natural calendar boundaries, not precise 168-hour periods.

## Config File Integration with parse Methods

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
- **Calendar window filtering**: Intuitive `win_*` methods for time range checking
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
