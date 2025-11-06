#!/usr/bin/env python3
"""
Demo script showing the new pquery API - pathql-inspired file querying.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from tpath.pquery import pquery


def create_demo_structure():
    """Create a demo directory structure for testing."""
    temp_dir = Path(tempfile.mkdtemp())

    # Create multiple source directories
    src_dir = temp_dir / "src"
    test_dir = temp_dir / "test"
    docs_dir = temp_dir / "docs"
    logs_dir = temp_dir / "logs"

    for dir_path in [src_dir, test_dir, docs_dir, logs_dir]:
        dir_path.mkdir(parents=True)

    # Create files in src/
    (src_dir / "main.py").write_text("print('main')" * 100)  # larger file
    (src_dir / "utils.py").write_text("# utilities")
    (src_dir / "config.json").write_text('{"version": "1.0"}')

    # Create nested structure in src/
    models_dir = src_dir / "models"
    models_dir.mkdir()
    (models_dir / "user.py").write_text("class User: pass")
    (models_dir / "data.py").write_text("class Data: pass")

    # Create files in test/
    (test_dir / "test_main.py").write_text("def test_main(): pass")
    (test_dir / "test_utils.py").write_text("def test_utils(): pass")

    # Create files in docs/
    (docs_dir / "README.md").write_text("# Documentation")
    (docs_dir / "API.md").write_text("# API Reference")

    # Create log files
    (logs_dir / "app.log").write_text("INFO: Application started")
    (logs_dir / "error.log").write_text("ERROR: Something went wrong")
    (logs_dir / "debug.log").write_text("DEBUG: " + "x" * 1000)  # large log

    return temp_dir, src_dir, test_dir, docs_dir, logs_dir


def demo_pquery_basics():
    """Demonstrate basic pquery functionality."""
    print("=== PQuery Basics ===")

    temp_dir, src_dir, test_dir, docs_dir, logs_dir = create_demo_structure()

    # Basic file listing
    print("1. All Python files:")
    py_files = pquery(from_=src_dir).where(lambda p: p.suffix == ".py").files()
    for file in py_files:
        print(f"  - {file.relative_to(temp_dir)}")

    # Using select to extract properties
    print("\n2. File sizes of Python files:")
    py_sizes = (
        pquery(from_=src_dir)
        .where(lambda p: p.suffix == ".py")
        .select(lambda p: (p.name, p.size.bytes))
    )
    for name, size in py_sizes:
        print(f"  - {name}: {size} bytes")

    # Multiple directories
    print("\n3. All files across multiple directories:")
    all_files = pquery(from_=[src_dir, test_dir]).where(lambda p: True).files()
    print(f"  Found {len(all_files)} files total")

    return temp_dir


def demo_pquery_advanced():
    """Demonstrate advanced pquery features."""
    print("\n=== Advanced PQuery Features ===")

    temp_dir, src_dir, test_dir, docs_dir, logs_dir = create_demo_structure()

    # Complex filtering with AND/OR
    print("1. Large files OR Python files:")
    large_or_py = (
        pquery(from_=temp_dir)
        .where(lambda p: p.size.bytes > 500 or p.suffix == ".py")
        .files()
    )

    for file in large_or_py:
        print(f"  - {file.relative_to(temp_dir)} ({file.size.bytes} bytes)")

    # Using convenience methods
    print("\n2. Convenience methods:")

    # First match
    first_log = pquery(from_=logs_dir).where(lambda p: p.suffix == ".log").first()
    print(f"  First log file: {first_log.name if first_log else 'None'}")

    # Check existence
    has_errors = pquery(from_=logs_dir).where(lambda p: "error" in p.name).exists()
    print(f"  Has error logs: {has_errors}")

    # Count files
    md_count = pquery(from_=temp_dir).where(lambda p: p.suffix == ".md").count()
    print(f"  Markdown files: {md_count}")

    return temp_dir


def demo_pquery_select():
    """Demonstrate pquery select functionality for data extraction."""
    print("\n=== PQuery Select Examples ===")

    temp_dir, src_dir, test_dir, docs_dir, logs_dir = create_demo_structure()

    # Extract just file names
    print("1. File names only:")
    names = pquery(from_=src_dir).where(lambda p: True).select(lambda p: p.name)
    print(f"  {', '.join(names)}")

    # Extract file extensions
    print("\n2. Unique file extensions:")
    extensions = pquery(from_=temp_dir).where(lambda p: True).select(lambda p: p.suffix)
    unique_exts = {ext for ext in extensions if ext}  # filter out empty
    print(f"  {', '.join(sorted(unique_exts))}")

    # Extract complex data
    print("\n3. File info tuples:")
    file_info = (
        pquery(from_=logs_dir)
        .where(lambda p: p.suffix == ".log")
        .select(lambda p: (p.name, p.size.bytes, p.readable))
    )

    for name, size, readable in file_info:
        print(f"  - {name}: {size} bytes, readable: {readable}")

    # Create summary data
    print("\n4. File size summary:")
    sizes_by_ext = {}

    all_files = (
        pquery(from_=temp_dir)
        .where(lambda p: True)
        .select(lambda p: (p.suffix, p.size.bytes))
    )

    for ext, size in all_files:
        if ext not in sizes_by_ext:
            sizes_by_ext[ext] = []
        sizes_by_ext[ext].append(size)

    for ext, sizes in sizes_by_ext.items():
        ext_name = ext if ext else "(no extension)"
        total_size = sum(sizes)
        avg_size = total_size / len(sizes)
        print(f"  {ext_name}: {len(sizes)} files, avg {avg_size:.1f} bytes")


def demo_iteration():
    """Demonstrate that pquery objects are iterable."""
    print("\n=== PQuery Iteration ===")

    temp_dir, src_dir, test_dir, docs_dir, logs_dir = create_demo_structure()

    # Direct iteration
    print("Iterating over Python files:")
    query = pquery(from_=src_dir).where(lambda p: p.suffix == ".py")

    for file in query:
        print(f"  - Processing {file.name}")

    # Can iterate multiple times
    print("\nIterating again (query is reusable):")
    file_count = sum(1 for _ in query)
    print(f"  Found {file_count} Python files")


if __name__ == "__main__":
    print("🔍 PQuery API Demo")
    print("=" * 50)

    temp_dir = demo_pquery_basics()
    demo_pquery_advanced()
    demo_pquery_select()
    demo_iteration()

    print(f"\n📁 Demo files created in: {temp_dir}")
    print("✨ PQuery demo complete!")

    print("\n📚 API Summary:")
    print("  pquery(from_=path).where(lambda p: condition)")
    print("    .files()    # Get list of matching files")
    print("    .select()   # Extract properties from files")
    print("    .first()    # Get first match or None")
    print("    .exists()   # Check if any matches exist")
    print("    .count()    # Count matching files")
    print("    # or iterate directly over the query")
