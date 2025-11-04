"""
TPath - A pathlib extension with time-based age and size utilities.

This package provides enhanced pathlib functionality with lambda-based
age and size operations. Users can import directly from tpath without
needing to know the internal package structure.

Examples:
    >>> from tpath import TPath, Size
    >>> path = TPath("myfile.txt")
    >>> path.age.days
    >>> path.size.gb
    >>> Size.parse("1.5GB")
"""

import importlib
from pathlib import Path

__version__ = "0.1.0"
__author__ = "Chuck Bass"

# Core exports - always available
from ._age import Age
from ._core import TPath
from ._size import Size
from ._time import Time, TimeType

# Base __all__ with core exports
__all__ = [
    "TPath",
    "Age",
    "Size",
    "Time",
    "TimeType",
]


def _discover_and_import_modules():
    """
    Automatically discover and import all modules in the package.
    This ensures new .py files are automatically included if they have __all__.
    """
    package_dir = Path(__file__).parent
    additional_exports = []

    # Get list of existing core modules to avoid re-importing
    core_modules = {"_age", "_core", "_size", "_time"}

    for py_file in package_dir.glob("_*.py"):
        if py_file.name == "__init__.py":
            continue

        module_name = py_file.stem

        # Skip if it's a core module (already imported above)
        if module_name in core_modules:
            continue

        try:
            # Import the module
            module = importlib.import_module(f".{module_name}", package=__name__)

            # If the module has __all__, expose those exports
            if hasattr(module, "__all__"):
                module_all = module.__all__
                if isinstance(module_all, list | tuple):
                    for export_name in module_all:
                        if isinstance(export_name, str) and hasattr(
                            module, export_name
                        ):
                            # Add to global namespace
                            globals()[export_name] = getattr(module, export_name)
                            additional_exports.append(export_name)

        except ImportError as e:
            # Don't fail the whole package, just warn
            print(f"Warning: Could not import module {module_name}: {e}")

    return additional_exports


# Auto-discover and import additional modules
_additional_exports = _discover_and_import_modules()

# Create final __all__ list - need to create new list to avoid linting issues
__all__ = sorted(list(__all__) + _additional_exports)
