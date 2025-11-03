# TPath Package Structure

The TPath package has been refactored into separate modules for better maintainability and organization. This document explains the new structure and import patterns.

## Package Structure

```
src/tpath/
├── __init__.py          # Main package interface
├── core.py              # TPath main class and tpath() function
├── age.py               # AgeProperty class
├── size.py              # SizeProperty class
├── time_property.py     # TimeProperty class
└── tpath.py            # Backward compatibility (re-exports)
```

## Import Patterns

### Recommended: Package-level imports

Users should import directly from the main package without needing to know the internal structure:

```python
# Recommended approach - clean and simple
from tpath import TPath, SizeProperty, tpath

# Create paths and use functionality
path = TPath("myfile.txt")
size_bytes = SizeProperty.fromstr("1.5GB")
convenience_path = tpath("otherfile.txt")
```

### Advanced: Module-specific imports

For advanced users who want specific modules:

```python
# Import from specific modules
from tpath.core import TPath, tpath
from tpath.size import SizeProperty
from tpath.age import AgeProperty
from tpath.time_property import TimeProperty
```

### Backward compatibility

Existing code using the old import structure will continue to work:

```python
# Still works (backward compatibility)
from tpath.tpath import TPath, SizeProperty
```

## Benefits of the New Structure

### 1. **Separation of Concerns**
- Each class has its own file
- Related functionality is grouped together
- Easier to understand and maintain

### 2. **Better IDE Support**
- Cleaner autocompletion
- Better navigation between related classes
- Clearer module boundaries

### 3. **Maintainability**
- Easier to modify individual components
- Reduced risk of merge conflicts
- Clear module responsibilities

### 4. **Testing**
- Can test individual modules in isolation
- Cleaner test organization
- Better test coverage analysis

### 5. **Package Interface**
- Users don't need to know internal structure
- Clean public API via `__init__.py`
- Easy to reorganize internally without breaking user code

## Module Responsibilities

### `core.py`
- Main `TPath` class
- Core pathlib extension functionality
- `tpath()` convenience function

### `size.py` 
- `SizeProperty` class
- Size calculations and unit conversions
- Size string parsing (`fromstr` method)

### `age.py`
- `AgeProperty` class
- Age calculations in various time units
- Time difference computations

### `time_property.py`
- `TimeProperty` class
- Handles different time types (ctime, mtime, atime)
- Bridges between time types and age calculations

### `__init__.py`
- Public package interface
- Exposes all user-facing classes and functions
- Package metadata and documentation

### `tpath.py` (Backward Compatibility)
- Re-exports all classes for backward compatibility
- Marked as deprecated in documentation
- Will be maintained for existing code

## Migration Guide

### For New Projects
Use the clean package-level imports:

```python
from tpath import TPath, SizeProperty
```

### For Existing Projects
No changes needed - all existing imports continue to work.

### Future Considerations
The `tpath.py` module may be deprecated in future major versions, but will be maintained for backward compatibility in the current major version.

## Example Usage

```python
# Clean imports
from tpath import TPath, SizeProperty

# Use as before
path = TPath("example.txt")
print(f"Size: {path.size.mb:.2f} MB")
print(f"Age: {path.age.hours:.2f} hours")

# Size parsing
bytes_val = SizeProperty.fromstr("2.5GB")
print(f"Parsed size: {bytes_val:,} bytes")
```

The refactored structure maintains all existing functionality while providing a cleaner, more maintainable codebase.