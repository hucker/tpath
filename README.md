# TPath - Enhanced pathlib with Age and Size Utilities

TPath is a pathlib extension that provides first-class age and size functions for file operations using a lambda-based approach (instead of operator overloading like pathql). It allows you to get file ages and sizes in natural, expressive syntax.

## Philosophy: Readable Code Through Common Properties

**The core principle of TPath is to provide properties for the things you actually need in real-world file operations.** Instead of forcing you to perform complex time calculations with lots of sub-calculations, TPath gives you direct access to commonly used values, resulting in **VERY readable code**.

### Before TPath (Complex Calculations)

```python
from pathlib import Path
from datetime import datetime
import os

# Complex, error-prone calculations
path = Path("logfile.txt")
stat = path.stat()
age_seconds = datetime.now().timestamp() - stat.st_mtime
age_days = age_seconds / 86400  # Remember: 60*60*24 = 86400
size_mb = stat.st_size / 1048576  # Remember: 1024*1024 = 1048576

if age_days > 7 and size_mb > 100:
    print(f"Large old file: {age_days:.1f} days, {size_mb:.1f} MB")
```

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
```

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

## Key Features

- **Lambda-based design**: No operator overloading confusion
- **Full pathlib compatibility**: Drop-in replacement for pathlib.Path
- **Natural syntax**: path.age.days instead of path.age > days(7)
- **Comprehensive time units**: seconds, minutes, hours, days, weeks, months, years
- **Multiple size units**: bytes, KB/KiB, MB/MiB, GB/GiB, TB/TiB, PB/PiB
- **Config file integration**: Parse strings with Size.parse(), Age.parse(), Time.parse()
- **Different time types**: Handle ctime, mtime, atime separately
- **Performance optimized**: Cached stat calls to avoid repeated filesystem operations

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
