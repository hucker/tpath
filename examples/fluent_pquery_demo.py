#!/usr/bin/env python3
"""
Demo script showing the new fluent PQuery API.
"""

import tempfile
import os
from pathlib import Path
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tpath.pquery import PQuery, pquery

def create_demo_structure():
    """Create a demo directory structure for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create multiple source directories
    src_dir = temp_dir / "src"
    test_dir = temp_dir / "test"
    docs_dir = temp_dir / "docs"
    logs_dir = temp_dir / "logs"
    config_dir = temp_dir / "config"
    
    for dir_path in [src_dir, test_dir, docs_dir, logs_dir, config_dir]:
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
    
    # Create config files
    (config_dir / "app.conf").write_text("debug=true")
    (config_dir / "db.conf").write_text("host=localhost")
    
    return temp_dir, src_dir, test_dir, docs_dir, logs_dir, config_dir

def demo_default_constructor():
    """Demonstrate PQuery() default constructor."""
    print("=== PQuery() Default Constructor ===")
    
    # Create some files in a temp directory and cd there
    temp_dir = Path(tempfile.mkdtemp())
    (temp_dir / "file1.txt").write_text("content1")
    (temp_dir / "file2.py").write_text("content2")
    (temp_dir / "file3.log").write_text("content3")
    
    original_cwd = os.getcwd()
    try:
        os.chdir(str(temp_dir))
        
        # Default constructor searches current directory
        print("1. PQuery() searches current directory by default:")
        files = PQuery().where(lambda p: True).files()
        for file in files:
            print(f"  - {file.name}")
        
    finally:
        os.chdir(original_cwd)
    
    return temp_dir

def demo_fluent_from_methods():
    """Demonstrate fluent from_() and from_path() methods."""
    print("\n=== Fluent from_() and from_path() Methods ===")
    
    temp_dir, src_dir, test_dir, docs_dir, logs_dir, config_dir = create_demo_structure()
    
    # Single from_()
    print("1. Single from_() method:")
    py_files = PQuery().from_(src_dir).where(lambda p: p.suffix == ".py").files()
    for file in py_files:
        print(f"  - {file.relative_to(temp_dir)}")
    
    # Chaining from_() and from_path()
    print("\n2. Chaining from_() and from_path():")
    code_files = (PQuery()
                  .from_(src_dir)
                  .from_path(test_dir)
                  .where(lambda p: p.suffix == ".py")
                  .files())
    
    for file in code_files:
        print(f"  - {file.relative_to(temp_dir)}")
    
    # Multiple directories
    print("\n3. Multiple directories with from_path():")
    config_files = (PQuery()
                   .from_(config_dir)
                   .from_path(src_dir)  # Also has config.json
                   .where(lambda p: "config" in p.name.lower() or p.suffix in [".conf", ".json"])
                   .files())
    
    for file in config_files:
        print(f"  - {file.relative_to(temp_dir)}")
    
    return temp_dir

def demo_recursive_method():
    """Demonstrate the recursive() method."""
    print("\n=== Recursive() Method ===")
    
    temp_dir, src_dir, test_dir, docs_dir, logs_dir, config_dir = create_demo_structure()
    
    # Recursive search (default)
    print("1. Recursive search (default):")
    all_py = (PQuery()
              .from_(src_dir)
              .recursive(True)  # This is actually the default
              .where(lambda p: p.suffix == ".py")
              .files())
    
    for file in all_py:
        print(f"  - {file.relative_to(temp_dir)}")
    
    # Non-recursive search
    print("\n2. Non-recursive search:")
    top_level_py = (PQuery()
                   .from_(src_dir)
                   .recursive(False)
                   .where(lambda p: p.suffix == ".py")
                   .files())
    
    for file in top_level_py:
        print(f"  - {file.relative_to(temp_dir)}")
    
    return temp_dir

def demo_complex_fluent_queries():
    """Demonstrate complex fluent API queries."""
    print("\n=== Complex Fluent Queries ===")
    
    temp_dir, src_dir, test_dir, docs_dir, logs_dir, config_dir = create_demo_structure()
    
    # Complex query with multiple conditions
    print("1. Large files OR Python files from multiple directories:")
    large_or_py = (PQuery()
                   .from_(src_dir)
                   .from_path(logs_dir)
                   .from_path(docs_dir)
                   .recursive(True)
                   .where(lambda p: p.size.bytes > 500 or p.suffix == ".py")
                   .files())
    
    for file in large_or_py:
        size_mb = file.size.bytes / 1024
        print(f"  - {file.relative_to(temp_dir)} ({size_mb:.1f} KB)")
    
    # Using select() to extract data
    print("\n2. File information tuples using select():")
    file_info = (PQuery()
                .from_(logs_dir)
                .where(lambda p: p.suffix == ".log")
                .select(lambda p: (p.name, p.size.bytes, "large" if p.size.bytes > 100 else "small")))
    
    for name, size, category in file_info:
        print(f"  - {name}: {size} bytes ({category})")
    
    # Method chaining in different orders
    print("\n3. Method chaining works in any order:")
    
    # Order 1: recursive -> from -> where
    files1 = (PQuery()
              .recursive(False)
              .from_(src_dir)
              .from_path(config_dir)
              .where(lambda p: True)
              .count())
    
    # Order 2: from -> recursive -> where
    files2 = (PQuery()
              .from_(src_dir)
              .from_path(config_dir)
              .recursive(False)
              .where(lambda p: True)
              .count())
    
    print(f"  Both queries found {files1} and {files2} files (should be equal)")
    
    return temp_dir

def demo_convenience_methods():
    """Demonstrate convenience methods with fluent API."""
    print("\n=== Convenience Methods ===")
    
    temp_dir, src_dir, test_dir, docs_dir, logs_dir, config_dir = create_demo_structure()
    
    # Using different result methods
    query = (PQuery()
             .from_(src_dir)
             .from_path(test_dir)
             .where(lambda p: p.suffix == ".py"))
    
    print("1. Different result methods on same query:")
    
    # files() - get list of files
    files = query.files()
    print(f"  files(): {len(files)} files")
    
    # first() - get first match
    first = query.first()
    print(f"  first(): {first.name if first else 'None'}")
    
    # exists() - check if any match
    exists = query.exists()
    print(f"  exists(): {exists}")
    
    # count() - count matches
    count = query.count()
    print(f"  count(): {count}")
    
    # select() - extract properties
    names = query.select(lambda p: p.name)
    print(f"  select(names): {names}")
    
    # Iteration
    print("  iteration:")
    for file in query:
        print(f"    - {file.name}")

def demo_backwards_compatibility():
    """Demonstrate that old pquery() function still works."""
    print("\n=== Backwards Compatibility ===")
    
    temp_dir, src_dir, test_dir, docs_dir, logs_dir, config_dir = create_demo_structure()
    
    # Old style still works
    print("1. Old pquery() convenience function:")
    old_style = pquery(from_=src_dir).where(lambda p: p.suffix == ".py").files()
    
    # New fluent style
    print("2. New fluent PQuery() style:")
    new_style = PQuery().from_(src_dir).where(lambda p: p.suffix == ".py").files()
    
    print(f"  Old style found: {len(old_style)} files")
    print(f"  New style found: {len(new_style)} files")
    print(f"  Results are equivalent: {len(old_style) == len(new_style)}")

if __name__ == "__main__":
    print("🔍 New Fluent PQuery API Demo")
    print("=" * 60)
    
    demo_default_constructor()
    demo_fluent_from_methods()
    demo_recursive_method()
    demo_complex_fluent_queries()
    demo_convenience_methods()
    demo_backwards_compatibility()
    
    print("\n✨ New Fluent API Features:")
    print("  PQuery()                           # Default to current directory")
    print("  PQuery().from_(path)               # Set starting path")
    print("  PQuery().from_path(path)           # Add additional path")
    print("  PQuery().recursive(True/False)     # Set recursive behavior")
    print("  PQuery().where(lambda p: ...)      # Add filter condition")
    print("    .files()                         # Get list of files")
    print("    .select(lambda p: ...)           # Extract properties")
    print("    .first()                         # Get first match")
    print("    .exists()                        # Check if any exist")
    print("    .count()                         # Count matches")
    print("    # or iterate directly")
    print("\n🔗 Method chaining works in any order (except where() should be last)")
    print("✅ Full backwards compatibility with old pquery() function")