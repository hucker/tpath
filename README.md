# TPath - Enhanced pathlib with Age and Size Utilities

TPath is a pathlib extension that provides first-class age and size functions for file operations using a lambda-based approach (instead of operator overloading like pathql). It allows you to get file ages and sizes in natural, expressive syntax.

## Features

- **Age Operations**: Get file age in various units (seconds, minutes, hours, days, weeks, months, years)
- **Size Operations**: Get file size in multiple formats (bytes, KB, MB, GB, KiB, MiB, GiB, etc.)
- **Multiple Time Types**: Work with creation time (ctime), modification time (mtime), and access time (atime)
- **Custom Base Time**: Calculate ages relative to any date/time
- **String Parsing**: Parse size strings like "1.5GB", "2KiB", etc.
- **Full pathlib Compatibility**: All standard pathlib.Path functionality is preserved

## Installation

```bash
# Clone or download the repository
# Add src directory to your Python path or install as a package
```

## Quick Start

```python
from tpath import TPath

# Create a TPath object (works like pathlib.Path)
path = TPath("myfile.txt")

# Age operations (lambda-based)
print(path.age.days)          # Age in days since creation
print(path.age.hours)         # Age in hours since creation
print(path.atime.age.minutes) # Minutes since last access
print(path.mtime.age.weeks)   # Weeks since last modification

# Size operations
print(path.size.bytes)        # Size in bytes
print(path.size.kb)           # Size in kilobytes (1000 bytes)
print(path.size.kib)          # Size in kibibytes (1024 bytes)
print(path.size.gb)           # Size in gigabytes
print(path.size.gib)          # Size in gibibytes

# Parse size strings
bytes_val = TPath.size.fromstr("1.5GB")  # Returns 1500000000
```

## Detailed Usage

### Age Operations

```python
from tpath import TPath

path = TPath("example.txt")

# Default age (based on creation time)
age_seconds = path.age.seconds
age_minutes = path.age.minutes
age_hours = path.age.hours
age_days = path.age.days
age_weeks = path.age.weeks
age_months = path.age.months
age_years = path.age.years

# Different time types
creation_age = path.ctime.age.days      # Age since creation
modification_age = path.mtime.age.days  # Age since last modification
access_age = path.atime.age.days        # Age since last access

# Get raw timestamps and datetime objects
timestamp = path.mtime.timestamp
dt = path.mtime.datetime
```

### Size Operations

```python
from tpath import TPath, SizeProperty

path = TPath("largefile.bin")

# Decimal units (base 1000)
size_kb = path.size.kb    # Kilobytes
size_mb = path.size.mb    # Megabytes  
size_gb = path.size.gb    # Gigabytes
size_tb = path.size.tb    # Terabytes

# Binary units (base 1024)
size_kib = path.size.kib  # Kibibytes
size_mib = path.size.mib  # Mebibytes
size_gib = path.size.gib  # Gibibytes
size_tib = path.size.tib  # Tebibytes

# Parse size strings (like pathql)
bytes_1kb = SizeProperty.fromstr("1KB")      # 1000 bytes
bytes_1kib = SizeProperty.fromstr("1KiB")    # 1024 bytes
bytes_2_5mb = SizeProperty.fromstr("2.5MB")  # 2500000 bytes
bytes_1_5gib = SizeProperty.fromstr("1.5GiB") # 1610612736 bytes
```

### Custom Base Time

```python
from datetime import datetime, timedelta
from tpath import TPath

path = TPath("oldfile.txt")

# Age relative to yesterday
yesterday = datetime.now() - timedelta(days=1)
path_yesterday = path.with_base_time(yesterday)
print(path_yesterday.age.days)  # Days older than yesterday

# Age relative to a specific date
specific_date = datetime(2024, 1, 1)
path_2024 = path.with_base_time(specific_date)
print(path_2024.age.years)  # Years since 2024
```

### Practical Examples

```python
from tpath import TPath

# Find old files
def find_old_files(directory, days_old=30):
    """Find files older than specified days."""
    dir_path = TPath(directory)
    old_files = []
    for file_path in dir_path.iterdir():
        if file_path.is_file() and file_path.age.days > days_old:
            old_files.append(file_path)
    return old_files

# Find large files
def find_large_files(directory, size_gb=1.0):
    """Find files larger than specified GB."""
    dir_path = TPath(directory)
    large_files = []
    for file_path in dir_path.iterdir():
        if file_path.is_file() and file_path.size.gb > size_gb:
            large_files.append(file_path)
    return large_files

# Clean up old temporary files
def cleanup_temp_files(temp_dir, hours_old=24):
    """Remove temporary files older than specified hours."""
    temp_path = TPath(temp_dir)
    for file_path in temp_path.glob("*.tmp"):
        if file_path.age.hours > hours_old:
            file_path.unlink()
            print(f"Deleted old temp file: {file_path}")
```

## API Reference

### TPath Class

Main class that extends `pathlib.Path` with age and size functionality.

```python
TPath(path, base_time=None)
```

**Parameters:**
- `path`: String or Path object representing the file/directory path
- `base_time`: Optional datetime object to use as base for age calculations (defaults to now)

**Properties:**
- `age`: AgeProperty for creation time age
- `ctime`: TimeProperty for creation time
- `mtime`: TimeProperty for modification time  
- `atime`: TimeProperty for access time
- `size`: SizeProperty for size operations

**Methods:**
- `with_base_time(base_time)`: Create new TPath with different base time

### AgeProperty Class

Provides age calculations in various time units.

**Properties:**
- `seconds`: Age in seconds
- `minutes`: Age in minutes
- `hours`: Age in hours
- `days`: Age in days
- `weeks`: Age in weeks
- `months`: Age in months (approximate)
- `years`: Age in years (approximate)

### SizeProperty Class

Provides size information in various units.

**Properties:**
- `bytes`: Size in bytes
- `kb`, `mb`, `gb`, `tb`: Size in decimal units (base 1000)
- `kib`, `mib`, `gib`, `tib`: Size in binary units (base 1024)

**Static Methods:**
- `fromstr(size_string)`: Parse size string and return bytes

### TimeProperty Class

Handles different file time types with age calculation.

**Properties:**
- `age`: AgeProperty for this time type
- `timestamp`: Raw timestamp value
- `datetime`: datetime object for this time

## Supported Size String Formats

The `fromstr` method supports these formats:

- Plain numbers: `"100"` (bytes)
- Decimal units: `"1KB"`, `"2.5MB"`, `"0.5GB"`, `"1TB"`
- Binary units: `"1KiB"`, `"2.5MiB"`, `"0.5GiB"`, `"1TiB"`

## Comparison with pathql

TPath provides similar functionality to pathql but uses lambdas instead of operator overloading:

```python
# pathql style (operator overloading)
old_files = path.age > days(30)
large_files = path.size > gb(1)

# TPath style (lambda-based)
old_files = path.age.days > 30
large_files = path.size.gb > 1
```

The lambda-based approach provides:
- More explicit and readable syntax
- Better IDE support and autocomplete
- Clearer method chaining
- No operator overloading conflicts

## License

[Your License Here]

## Contributing

[Contributing guidelines here]