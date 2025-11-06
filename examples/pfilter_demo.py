#!/usr/bin/env python3
"""
Demo script showing enhanced pfilter functionality with multiple paths and glob/rglob.
"""

import tempfile
from pathlib import Path

from tpath.pquery._pquery import pcount, pfilter, pfind


def create_demo_structure():
    """Create a demo directory structure for testing."""
    temp_dir = Path(tempfile.mkdtemp())

    # Create multiple source directories
    src_dir = temp_dir / "src"
    test_dir = temp_dir / "test"
    docs_dir = temp_dir / "docs"

    for dir_path in [src_dir, test_dir, docs_dir]:
        dir_path.mkdir(parents=True)

    # Create files in src/
    (src_dir / "main.py").write_text("print('main')")
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

    return temp_dir, src_dir, test_dir, docs_dir


def demo_multiple_paths():
    """Demonstrate pfilter with multiple starting paths."""
    print("=== Multiple Paths Demo ===")

    temp_dir, src_dir, test_dir, docs_dir = create_demo_structure()

    # Search across multiple directories for Python files
    python_files = pfind(
        from_=[src_dir, test_dir],  # Multiple paths
        query=lambda p: p.suffix == ".py",
    )

    print(f"Python files across src/ and test/: {len(python_files)}")
    for file in python_files:
        print(f"  - {file.relative_to(temp_dir)}")

    # Count files by type across all directories
    total_py = pcount([src_dir, test_dir, docs_dir], lambda p: p.suffix == ".py")
    total_md = pcount([src_dir, test_dir, docs_dir], lambda p: p.suffix == ".md")

    print(f"\nTotal .py files: {total_py}")
    print(f"Total .md files: {total_md}")

    return temp_dir


def demo_glob_vs_rglob(temp_dir):
    """Demonstrate glob vs rglob behavior."""
    print("\n=== Glob vs RGlob Demo ===")

    src_dir = temp_dir / "src"

    # Recursive search (default) - finds all Python files including nested
    recursive_py = list(
        pfilter(
            from_=src_dir,
            query=lambda p: p.suffix == ".py",
            recursive=True,  # Uses rglob - searches subdirectories
        )
    )

    # Non-recursive search - only finds top-level Python files
    non_recursive_py = list(
        pfilter(
            from_=src_dir,
            query=lambda p: p.suffix == ".py",
            recursive=False,  # Uses glob - current directory only
        )
    )

    print(f"Recursive search in src/: {len(recursive_py)} files")
    for file in recursive_py:
        print(f"  - {file.relative_to(temp_dir)}")

    print(f"\nNon-recursive search in src/: {len(non_recursive_py)} files")
    for file in non_recursive_py:
        print(f"  - {file.relative_to(temp_dir)}")


def demo_complex_queries(temp_dir):
    """Demonstrate complex lambda queries."""
    print("\n=== Complex Queries Demo ===")

    # Find small Python files OR any test files
    complex_results = list(
        pfilter(
            from_=[temp_dir / "src", temp_dir / "test"],
            query=lambda p: (p.suffix == ".py" and p.size.bytes < 50)
            or "test" in p.name,
        )
    )

    print(f"Small Python files OR test files: {len(complex_results)}")
    for file in complex_results:
        print(f"  - {file.relative_to(temp_dir)} ({file.size.bytes} bytes)")


if __name__ == "__main__":
    print("🔍 Enhanced pfilter Demo")
    print("=" * 50)

    temp_dir = demo_multiple_paths()
    demo_glob_vs_rglob(temp_dir)
    demo_complex_queries(temp_dir)

    print(f"\n📁 Demo files created in: {temp_dir}")
    print("✨ Demo complete!")
