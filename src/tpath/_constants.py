"""
Constants used throughout the TPath package.
"""

# Time conversion constants
SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 3600
SECONDS_PER_DAY = 86400
SECONDS_PER_WEEK = 604800  # 7 * 24 * 60 * 60

# Advanced time constants for age calculations
DAYS_PER_MONTH = 30.44  # Average days per month
DAYS_PER_YEAR = 365.25  # Average days per year (accounting for leap years)
SECONDS_PER_MONTH = int(DAYS_PER_MONTH * SECONDS_PER_DAY)  # 2630016
SECONDS_PER_YEAR = int(DAYS_PER_YEAR * SECONDS_PER_DAY)  # 31557600

# Size conversion constants (binary - 1024-based)
BYTES_PER_KIB = 1024
BYTES_PER_MIB = 1024 * 1024
BYTES_PER_GIB = 1024 * 1024 * 1024
BYTES_PER_TIB = 1024 * 1024 * 1024 * 1024
BYTES_PER_PIB = 1024 * 1024 * 1024 * 1024 * 1024

# Size conversion constants (decimal - 1000-based)
BYTES_PER_KB = 1000
BYTES_PER_MB = 1000 * 1000
BYTES_PER_GB = 1000 * 1000 * 1000
BYTES_PER_TB = 1000 * 1000 * 1000 * 1000
BYTES_PER_PB = 1000 * 1000 * 1000 * 1000 * 1000

# Default fallback timestamp (1 day after Unix epoch to avoid timezone issues)
DEFAULT_FALLBACK_TIMESTAMP = SECONDS_PER_DAY

# Calendar constants
DAYS_PER_WEEK = 7
MONTHS_PER_YEAR = 12

# Weekday mappings for calendar functions
WEEKDAY_NAMES = {
    0: "monday", 1: "tuesday", 2: "wednesday", 3: "thursday",
    4: "friday", 5: "saturday", 6: "sunday"
}

WEEKDAY_ABBREVIATIONS = {
    "mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6,
    "mo": 0, "tu": 1, "we": 2, "th": 3, "fr": 4, "sa": 5, "su": 6
}

# Access mode specifications
ACCESS_MODE_READ = "R"
ACCESS_MODE_WRITE = "W"
ACCESS_MODE_EXECUTE = "X"
ACCESS_MODE_READ_ONLY = "RO"
ACCESS_MODE_WRITE_ONLY = "WO"
ACCESS_MODE_READ_WRITE = "RW"
ACCESS_MODE_ALL = "RWX"

__all__ = [
    "SECONDS_PER_MINUTE", "SECONDS_PER_HOUR", "SECONDS_PER_DAY", "SECONDS_PER_WEEK",
    "DAYS_PER_MONTH", "DAYS_PER_YEAR", "SECONDS_PER_MONTH", "SECONDS_PER_YEAR",
    "BYTES_PER_KIB", "BYTES_PER_MIB", "BYTES_PER_GIB", "BYTES_PER_TIB", "BYTES_PER_PIB",
    "BYTES_PER_KB", "BYTES_PER_MB", "BYTES_PER_GB", "BYTES_PER_TB", "BYTES_PER_PB",
    "DEFAULT_FALLBACK_TIMESTAMP", "DAYS_PER_WEEK", "MONTHS_PER_YEAR",
    "WEEKDAY_NAMES", "WEEKDAY_ABBREVIATIONS",
    "ACCESS_MODE_READ", "ACCESS_MODE_WRITE", "ACCESS_MODE_EXECUTE",
    "ACCESS_MODE_READ_ONLY", "ACCESS_MODE_WRITE_ONLY", "ACCESS_MODE_READ_WRITE", "ACCESS_MODE_ALL"
]
