# TPath - Enhanced pathlib with Age, Size, and Calendar Utilities

TPath is a pathlib extension that provides first-class age, size, and calendar membership functions for file operations. It allows you to work with files using natural, expressive syntax focused on **properties rather than calculations**.

## Philosophy: Property-Based File Operations

**The core goal of TPath is to create a file object system that is property-based rather than providing a single entry point of timestamp from which the end user must perform all calculations.**

Instead of giving you raw timestamps and forcing you to do mental math, TPath provides direct properties for the things you actually need in real-world file operations, resulting in **readable, maintainable code**. In order to accomplish a reduction in cognitive load the Path object was overloaded to have a reference time (almost always set to `datetime.now()`) that allows file ages to be directly measured, support for caching the os.stat_result value and support for accurate "creation time" using the birthtime values.  These details are handled behind the scenes and enable property based ages and membership, minimal calls to `os.stat/path.stat` and nearly zero calculations for all file properties.  This has the added benefit that file iteration operating over `TPath` objects has require only a single parrameter, the path, in order to obtain ALL information related to the file of interest.

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

**Complex queries become trivial with PQuery's fluent interface:**

```python
from tpath import PQuery, matches

# Multi-directory, multi-pattern, calendar-membership query in 6 readable lines
# in_months(-3, 0) = calendar month boundaries (Aug 1st - Oct 31st if today is Oct 15th)
# Calendar membership ≠ duration math: 90 days ≠ 3 months, avg_days*months ≠ real months
# TPath makes "this quarter", "this month", "last 3 months" queries natural and correct!
backup_candidates = list(
    PQuery()
    .from_("/home/user/docs", "/home/user/projects")
    .where(lambda p: matches(p, "*.doc*", "*.pdf", "*.xls*") and
                     p.size.mb >= 1.0 and
                     p.mtime.cal.in_months(-3, 0))
    .select(lambda p: (p, p.size.mb, p.age.days))
)

print(f"Found {len(backup_candidates)} backup candidates")
```

**No mental overhead. No error-prone calculations. Just readable code that expresses intent clearly.**

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

# File querying with PQuery
from tpath import PQuery

# Stream processing (memory efficient)
for file in PQuery().where(lambda p: p.size.mb > 10).files():
    process_large_file(file)

# Materialize when you need a list
large_files = list(PQuery().where(lambda p: p.size.mb > 10).files())
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
from tpath import matches, PQuery

# Use with PQuery for file filtering
python_files = (PQuery()
    .from_("./src")
    .where(lambda p: matches(p, "*.py"))
    .files()
)

# Multiple patterns with case-insensitive matching
log_files = (PQuery()
    .from_("./logs")
    .where(lambda p: matches(p, "*.log", "*.LOG", case_sensitive=False))
    .files()
)

# Complex pattern matching with wildcards
backup_files = (PQuery()
    .from_("./backups")
    .where(lambda p: matches(p, "backup_202[3-4]*", "*important*"))
    .files()
)
```

## PQuery - Powerful File Querying

**PQuery provides a fluent, chainable API for filtering files based on age, size, and other properties.** It's designed for complex file filtering operations with readable, expressive syntax.

> **Note**: PQuery is NOT SQL and is not meant to replicate all SQL features. It provides a paradigm with SQL-like characteristics for file operations, enabling semantically similar operations like filtering, sorting, and result transformation in a familiar pattern.

While the code mimics SQL, it does so only to provide a set of tools that allows you to think abstractly about filtering files using a tool set that many programmers are familiar with. There is no query optimizer beyond being careful with calling stat.

### Basic Usage

```python
from tpath import PQuery

# Simple queries - starts from current directory by default
q = PQuery()

# Find files by extension (streaming)
for file in q.where(lambda p: p.suffix == '.py').files():
    process_python_file(file)

# Get list when needed
python_files = list(q.where(lambda p: p.suffix == '.py').files())

# Find files by size
large_files = list(q.where(lambda p: p.size.mb > 10).files())

# Find files by calendar window
recent_files = list(q.where(lambda p: p.mtime.cal.in_days(-7, 0)).files())

# Complex combined criteria
old_large_logs = list(q
    .where(lambda p: p.suffix == '.log' and p.size.mb > 50 and p.age.days > 30)
    .files())
```

### Deep File System Traversal

> **PQuery uses a stack-based directory walker, not recursion.** This means it can traverse extremely deep file systems without any risk of Python stack overflow. The traversal is fully iterative, so you can safely query directories with thousands of nested levels.

### Type Safety Best Practices

For optimal type checking and IDE support, consider using typed functions instead of inline lambdas:

```python
from tpath import PQuery, TPath

# Instead of inline lambdas (limited type inference)
large_files = PQuery().where(lambda p: p.size.mb > 10).files()

# Use typed functions for better type checking
def is_large_file(path: TPath) -> bool:
    """Check if file is larger than 10MB."""
    return path.size.mb > 10

def get_file_info(path: TPath) -> dict[str, str | float]:
    """Extract file metadata for reporting."""
    return {
        'name': path.name,
        'size_mb': path.size.mb,
        'age_days': path.age.days
    }

# Better type safety and IDE support
large_files = PQuery().where(is_large_file).files()
file_info = PQuery().where(is_large_file).select(get_file_info)  # Returns list[Any]
```

> **Important:** When using `where`, you must pass the function itself (e.g., `where(is_large_file)`), not the result of calling the function (e.g., `where(is_large_file())`). Passing the result of a function call will cause a type error and is a common mistake caught by the type checker.

### Method Chaining/Fluent Interface

Properties can be set in the boject initialzation by filling in the appropriate keyword args.  A fluent interface
is also available that can be more readable.

```python
# Build complex queries step by step
cleanup_files = (PQuery()
    .from_("/var/log")              # Set starting directory
    .recursive(True)                # Include subdirectories
    .where(lambda p: p.suffix in ['.log', '.tmp'] and p.age.days > 30)
    .files()
)

# Search multiple directories at once
all_logs = (PQuery()
    .from_("/var/log", "/opt/app/logs", "/home/user/logs")  # Multiple paths
    .where(lambda p: p.suffix == '.log')
    .files()
)

# Remove duplicate files from results (useful with overlapping search paths)
unique_logs = (PQuery()
    .from_(log_dirs, backup_dirs, "/var/log")  # Multiple sources may overlap
    .where(lambda p: p.suffix == '.log')
    .distinct()                                # Remove duplicate files from results
)

# Execute and process results
total_size = sum(f.size.bytes for f in cleanup_files)
print(f"Found {len(cleanup_files)} files totaling {total_size // 1024**2} MB")
```

### Result Transformation with select()

Transform results into more useful formats:

```python
# Get file names and sizes as tuples
file_info = (PQuery()
    .from_("./logs")
    .where(lambda p: p.suffix == '.log')
    .select(lambda p: (p.name, p.size.mb))
)
# Returns: [('app.log', 2.3), ('error.log', 0.8), ...]

# Create custom dictionaries
file_metadata = (PQuery()
    .from_("./documents")
    .where(lambda p: p.suffix in ['.pdf', '.docx'])
    .select(lambda p: {
        'name': p.name,
        'size_mb': p.size.mb,
        'age_days': p.mtime.age.days
    })
)
# Returns: [{'name': 'report.pdf', 'size_mb': 2.1, 'age_days': 5}, ...]
```

### Utility Methods

```python
# Check if any files match (without loading all results)
has_large_files = (PQuery()
    .from_("./data")
    .where(lambda p: p.size.gb > 1)
    .exists()
)

# Count matching files
num_python_files = (PQuery()
    .from_("./src")
    .where(lambda p: p.suffix == '.py')
    .count()
)

# Get first match
latest_log = (PQuery()
    .from_("./logs")
    .where(lambda p: p.suffix == '.log')
    .first()  # Returns TPath or None
)
```

### Sorting and Top-K Selection

```python
# Get top 10 largest files (efficient for top-k)
largest_files = (PQuery()
    .from_("./data")
    .take(10, key=lambda p: p.size.bytes)
)

# Sort all files by modification time
all_by_time = (PQuery()
    .from_("./logs")
    .order_by(key=lambda p: p.mtime.timestamp, ascending=False)
)

# Performance tip: use take() for top-N, order_by() for complete ordering
```

### Pagination for Large Datasets

```python
# Process files in batches to manage memory
for page in PQuery().from_("./massive/dataset").paginate(100):
    process_batch(page)
    print(f"Processed {len(page)} files")

# Web API pagination
query = PQuery().from_("./documents").where(lambda p: p.suffix == '.pdf')
pages = list(query.paginate(20))  # Get all pages
first_page = pages[0] if pages else []

# Manual page iteration
paginator = query.paginate(50)
page1 = next(paginator, [])  # First 50 files
page2 = next(paginator, [])  # Next 50 files
page3 = next(paginator, [])  # Next 50 files

# Efficient batch processing with progress
total_processed = 0
for page_num, page in enumerate(query.paginate(200)):
    total_processed += len(page)
    print(f"Page {page_num + 1}: processed {total_processed} files")
    
    # Process each file in the page
    for file in page:
        backup_file(file)
```

### Streaming vs. Materialization

**PQuery uses streaming by default for memory efficiency:**

```python
# Streaming (memory efficient) - processes one file at a time
for file in PQuery().from_("./large/dataset").files():
    process_file(file)  # Starts immediately, uses O(1) memory
    if should_stop():
        break  # Can exit early

# Materialization (when you need a list)
all_files = list(PQuery().from_("./data").files())  # O(n) memory
count = len(all_files)      # Can get length
first = all_files[0]        # Can index
for file in all_files:      # Can iterate multiple times
    process_file(file)

# Transform results with select (also streaming)
for name in PQuery().from_("./logs").select(lambda p: p.name):
    print(name)  # Streams file names

# Materialize selected results when needed
file_names = list(PQuery().from_("./logs").select(lambda p: p.name))
```

**When to use each approach:**

- **Streaming**: Large datasets, one-time processing, memory constrained
- **Lists**: Need length/indexing, multiple iterations, small datasets

### Performance and Efficiency

PQuery uses lazy evaluation - filters are only applied when you call execution methods:

```python
# Build the query (no filesystem operations yet)
q = PQuery().from_("/large/directory").where(lambda p: p.size.gb > 5)

# Only now does it scan the filesystem
large_files = q.files()  # Execute the query

# Reuse queries efficiently
more_files = q.where(lambda p: p.suffix == '.mp4').files()
```

#### Efficiency Guide for Large Datasets

Different operations have vastly different performance characteristics:

```python
# ⚡ MOST EFFICIENT - Early termination operations  
query.take(10)                    # O(10) - stops after 10 files
query.first()                     # O(1) - stops after first match  
query.exists()                    # O(1) - stops after first match
query.distinct().take(10)         # O(k≤n) - stops after 10 unique files

# ⚡ STREAMING - Memory efficient processing
for file in query.files():        # O(1) memory - processes one file at a time
    process_file(file)

# ⚡ PAGINATION - Batch processing with controlled memory
for page in query.paginate(100):  # O(100) memory - processes 100 files at a time
    process_batch(page)

# 📈 EFFICIENT - Heap-based top-N selection  
query.take(10, key=lambda p: p.size.bytes)           # O(n + 10 log n) - top 10 largest
query.take(10, key=lambda p: p.size.bytes, reverse=False)  # O(n + 10 log n) - top 10 smallest
query.take(5, key=lambda p: p.mtime.timestamp)       # O(n + 5 log n) - 5 newest files

# 🐌 EXPENSIVE - Must materialize full results
list(query.files())               # O(n) memory - loads all files into list
query.count()                     # O(n) - must count all matches
query.order_by()                      # O(n log n) - full sort required

# 💡 Performance Tips:
# - Use streaming: for file in query.files() for memory efficiency
# - Use pagination: for page in query.paginate(100) for batch processing
# - Use list() only when you need random access or length
# - Use distinct().take(n) for unique results with early stopping
# - Use take(n, key=...) instead of list(query.order_by().take(n)) when possible  
# - Chain filters early: .where().distinct().take() is optimal order
# - Use exists() instead of len(list(query.files())) > 0 to check for matches
```

## Pattern Matching with `matches()`

**TPath provides a standalone `matches()` function for shell-style pattern matching.** This function works with any path type and integrates seamlessly with PQuery for powerful file filtering.

### Basic Pattern Matching

```python
from tpath import matches, TPath
from pathlib import Path

# Basic usage - works with strings, Path, or TPath objects
matches("app.log", "*.log")              # True
matches("readme.txt", "*.log")           # False
matches(Path("data.csv"), "*.csv")       # True  
matches(TPath("script.py"), "*.py")      # True

# Multiple patterns (OR logic) - returns True if ANY pattern matches
matches("report.pdf", "*.pdf", "*.docx", "*.txt")     # True
matches("config.ini", "*.json", "*.yaml", "*.toml")   # False

# Wildcards and character classes
matches("backup_2024.zip", "backup_202[3-4]*")       # True
matches("data_file_v1.txt", "data_*_v?.txt")          # True
matches("config.local.ini", "*config*")               # True
```

### Case Sensitivity Control

```python
# Case-sensitive matching (default)
matches("IMAGE.JPG", "*.jpg")                         # False
matches("IMAGE.JPG", "*.JPG")                         # True

# Case-insensitive matching  
matches("IMAGE.JPG", "*.jpg", case_sensitive=False)   # True
matches("README.TXT", "*readme*", case_sensitive=False) # True
```

### Full Path vs Filename Matching

```python
# Default: match against filename only
test_path = "/home/user/projects/app/src/main.py"
matches(test_path, "*.py")                             # True
matches(test_path, "*app*")                           # False (filename is "main.py")

# Full path matching
matches(test_path, "*app*", full_path=True)           # True
matches(test_path, "*/src/*", full_path=True)         # True
matches(test_path, "*projects*", full_path=True)      # True
```

### Integration with PQuery

Use `matches()` with PQuery's `.where()` method for powerful file filtering:

```python
from tpath import PQuery, matches

# Find log files using pattern matching
log_files = (PQuery()
    .from_("./logs")
    .where(lambda p: matches(p, "*.log", "*.LOG", case_sensitive=False))
    .files()
)

# Find configuration files across project
config_files = (PQuery()
    .from_("./")
    .recursive(True)
    .where(lambda p: matches(p, "*.conf", "*.ini", "*config*", "*.yaml", "*.json"))
    .files()
)

# Complex filtering: large Python files with test patterns
test_files = (PQuery()
    .from_("./")
    .recursive(True)
    .where(lambda p: matches(p, "*test*", "*_test.py", "test_*.py") and p.size.kb > 10)
    .files()
)

# Clean up temporary files by pattern
temp_files = (PQuery()
    .from_("./")
    .recursive(True)
    .where(lambda p: matches(p, "*.tmp", "*.temp", ".*", "~*", full_path=True) and 
                     p.age.days > 7)
    .files()
)

# Backup candidates - important file types from recent activity
backup_files = (PQuery()
    .from_("/home/user/documents")
    .recursive(True)
    .where(lambda p: matches(p, "*.doc*", "*.pdf", "*.xls*", "*.ppt*") and
                     p.size.mb > 1 and
                     p.mtime.cal.in_months(-3, 0))  # Modified in last 3 months
    .files()
)
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

| Pattern | Description | Example | Matches |
|---------|-------------|---------|---------|
| `*` | Zero or more characters | `*.log` | `app.log`, `error.log.old`, `.log` |
| `?` | Any single character | `file?.txt` | `file1.txt`, `fileA.txt` |
| `[seq]` | Any character in sequence | `data[0-9].csv` | `data1.csv`, `data9.csv` |
| `[!seq]` | Any character NOT in sequence | `*[!0-9].txt` | `fileA.txt`, `file_.txt` |
| `[a-z]` | Character range | `[A-Z]*.py` | `Main.py`, `Test.py` |

### Performance Notes

- `matches()` is optimized for single file checking
- For bulk operations, combine with PQuery's lazy evaluation
- Pattern compilation is cached internally for repeated use
- Use `full_path=False` (default) when possible for better performance

## Advanced Features

### Calendar Window Filtering

**TPath provides intuitive calendar window filtering to check if files fall within specific time ranges.** This is perfect for finding files from "last week", "this month", "last quarter", etc.

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
- **Property Based Dates by [Chronos](https://github.com/hucker/chronos)**

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

## Logging Support


PQuery supports flexible logging for query operations and statistics. You can attach a standard Python logger to track progress, errors, and matched files during queries.

**How to enable logging:**
- Pass a `logging.Logger` instance to the `PQuery` constructor or use the class method `PQuery.set_logger()` to set a logger for all queries.
- Log messages include query start, progress (every N files), errors, and completion.

**Example: Setting a class-level logger**
```python
import logging
from src.tpath.pquery import PQuery

logger = logging.getLogger("pquery_global")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
logger.addHandler(handler)

PQuery.set_logger(logger)  # Set class-level logger for all queries

query = PQuery(from_="/logs")
for file in query.files():
    process(file)
```

You can also pass a logger to an individual query if you want per-instance logging.

See tests in `test/pquery/test_logger.py` for more usage patterns.

## License

MIT License - see LICENSE file for details.
