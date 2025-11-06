#!/usr/bin/env python3
"""
Demo of the enhanced PQuery constructor with lazy initialization.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from tpath.pquery import PQuery


def create_test_structure():
    """Create a test directory structure."""
    temp_dir = Path(tempfile.mkdtemp())

    # Create files and directories
    (temp_dir / "app.py").write_text("print('app')" * 50)  # 550 chars
    (temp_dir / "test.py").write_text("# test")
    (temp_dir / "README.md").write_text("# Documentation")
    (temp_dir / "config.json").write_text('{"key": "value"}')

    # Create subdirectory
    subdir = temp_dir / "subdir"
    subdir.mkdir()
    (subdir / "nested.py").write_text("# nested python")
    (subdir / "data.txt").write_text("some data")

    return temp_dir


def demo_enhanced_constructor():
    """Demonstrate the enhanced PQuery constructor with parameters."""
    print("🚀 Enhanced PQuery Constructor Demo")
    print("=" * 50)

    temp_dir = create_test_structure()

    print("\n1. Default constructor (lazy initialization):")
    print("   PQuery() -> defaults applied when query runs")
    query = PQuery()
    print(
        f"   Before execution: start_paths={query.start_paths}, query_func={query._query_func}"
    )

    # Change to temp directory for demo
    original_cwd = os.getcwd()
    try:
        os.chdir(str(temp_dir))
        files = query.files()
        print(f"   After execution: found {len(files)} files in current directory")
        print(f"   Files: {[f.name for f in files]}")
    finally:
        os.chdir(original_cwd)

    print("\n2. Constructor with from_ parameter:")
    print("   PQuery(from_='/path') -> sets starting directory")
    query = PQuery(from_=temp_dir)
    files = query.files()
    print(f"   Found {len(files)} files: {[f.name for f in files]}")

    print("\n3. Constructor with recursive parameter:")
    print("   PQuery(from_='/path', recursive=False) -> non-recursive search")
    query = PQuery(from_=temp_dir, recursive=False)
    files = query.files()
    print(f"   Non-recursive: {len(files)} files (top-level only)")
    print(f"   Files: {[f.name for f in files]}")

    query = PQuery(from_=temp_dir, recursive=True)
    files = query.files()
    print(f"   Recursive: {len(files)} files (including subdirs)")
    print(f"   Files: {[f.name for f in files]}")

    print("\n4. Constructor with where parameter:")
    print("   PQuery(where=lambda p: p.suffix == '.py') -> custom filter")
    query = PQuery(from_=temp_dir, where=lambda p: p.suffix == ".py")
    files = query.files()
    print(f"   Python files only: {[f.name for f in files]}")

    print("\n5. All parameters together:")
    print("   PQuery(from_, recursive=False, where=lambda p: p.size.bytes > 100)")
    query = PQuery(from_=temp_dir, recursive=False, where=lambda p: p.size.bytes > 100)
    files = query.files()
    print(f"   Large files (>100 bytes), non-recursive: {[f.name for f in files]}")

    print("\n6. Fluent methods override constructor:")
    print("   Constructor sets Python filter, but fluent .where() overrides it")
    query = PQuery(from_=temp_dir, where=lambda p: p.suffix == ".py").where(
        lambda p: p.suffix == ".md"
    )  # Override to markdown
    files = query.files()
    print(f"   Markdown files (overrode Python filter): {[f.name for f in files]}")

    print("\n7. Default where function behavior:")
    print("   PQuery() defaults to lambda p: p.is_file() (excludes directories)")

    # Create a directory to show it gets filtered out
    test_dir = temp_dir / "test_subdir"
    test_dir.mkdir()

    query = PQuery(from_=temp_dir, recursive=False)
    all_items = query.files()
    print(f"   Default filter excludes directories: {len(all_items)} items")
    print(f"   All files: {[f.name for f in all_items]}")

    # Show what would happen if we included directories
    query_with_dirs = PQuery(
        from_=temp_dir, recursive=False, where=lambda p: True
    )  # Include everything
    all_items_with_dirs = query_with_dirs.files()
    print(f"   With directories included: {len(all_items_with_dirs)} items")

    return temp_dir


def demo_lazy_vs_eager():
    """Demonstrate lazy vs eager initialization concepts."""
    print("\n🔄 Lazy vs Eager Initialization")
    print("=" * 40)

    temp_dir = create_test_structure()

    print("\n1. Lazy initialization (current approach):")
    print("   Constructor stores parameters, applies them when query runs")

    query = PQuery(from_=temp_dir, recursive=False)
    print(f"   After constructor: start_paths={len(query.start_paths)} (empty)")
    print(f"   After constructor: is_recursive={query.is_recursive} (default)")

    query.files()
    print(f"   After execution: start_paths={len(query.start_paths)} (populated)")
    print(f"   After execution: is_recursive={query.is_recursive} (from constructor)")

    print("\n2. Benefits of lazy initialization:")
    print("   ✅ Constructor parameters can be overridden by fluent methods")
    print("   ✅ Defaults are applied consistently when needed")
    print("   ✅ Flexible method chaining order")
    print("   ✅ Consistent behavior whether using constructor or fluent API")

    # Demonstrate override capability
    query_override = (
        PQuery(from_=temp_dir, recursive=False)
        .recursive(True)  # Override constructor parameter
        .where(lambda p: p.suffix == ".py")
    )

    files_override = query_override.files()
    print(
        "\n   Example: Constructor set recursive=False, fluent .recursive(True) overrode it"
    )
    print(f"   Result: Found {len(files_override)} Python files recursively")


if __name__ == "__main__":
    temp_dir = demo_enhanced_constructor()
    demo_lazy_vs_eager()

    print("\n✨ Key Features:")
    print("  • PQuery() - Default constructor with sensible defaults")
    print("  • PQuery(from_=path) - Set starting directory")
    print("  • PQuery(recursive=True/False) - Control recursion")
    print("  • PQuery(where=lambda p: ...) - Set initial filter")
    print("  • Lazy initialization - defaults applied when query runs")
    print("  • Fluent override - methods can override constructor parameters")
    print("  • Default where function - lambda p: p.is_file() (files only)")

    print(f"\n🗂️  Test files created in: {temp_dir}")
    print("    Feel free to explore the directory structure!")
