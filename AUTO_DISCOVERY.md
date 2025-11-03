# Auto-Discovery System for TPath

## Overview

The TPath package now includes an automatic module discovery system that will automatically include any new `.py` files you add to the package. This means you don't need to manually update the `__init__.py` file every time you add a new module.

## How It Works

The auto-discovery system in `src/tpath/__init__.py`:

1. **Scans for new modules**: Automatically finds all `_*.py` files in the package directory
2. **Imports modules**: Dynamically imports any new modules that aren't part of the core set
3. **Exports public APIs**: If a module has an `__all__` list, those exports are automatically added to the package's public API
4. **Updates __all__**: The main `__all__` list is automatically updated with discovered exports

## Adding New Modules

To add a new module that will be automatically discovered:

1. **Create a new file** in `src/tpath/` with a name starting with underscore (e.g., `_mymodule.py`)

2. **Define your classes/functions** in the file

3. **Add an `__all__` list** to specify what should be exported:
   ```python
   # _mymodule.py
   class MyClass:
       pass
   
   def my_function():
       pass
   
   # This tells the auto-discovery what to export
   __all__ = ['MyClass', 'my_function']
   ```

4. **Import and use**: The module will be automatically imported and available:
   ```python
   from tpath import MyClass, my_function
   ```

## Core Modules

These modules are always imported explicitly (not auto-discovered):
- `_core.py` - TPath, tpath
- `_age.py` - Age
- `_size.py` - Size  
- `_time.py` - Time

## Benefits

- **No manual updates**: Just add your file with `__all__` and it's automatically available
- **Clean imports**: Users can import new functionality directly from `tpath`
- **Backwards compatible**: Existing code continues to work unchanged
- **Package consistency**: All modules follow the same import pattern

## Example

```python
# Before: Manual import updates needed
# After: Just create _utilities.py with:

class FileHelper:
    def clean_name(self, name: str) -> str:
        return name.strip().replace(" ", "_")

__all__ = ['FileHelper']

# Now automatically available as:
from tpath import FileHelper
```

## Build System Integration

The `pyproject.toml` is configured to automatically include all Python files in the package during builds, so new modules are automatically included in distributions.