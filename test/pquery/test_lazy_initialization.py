"""
Test lazy initialization of PQuery constructor parameters.
"""

import tempfile
import pytest
from pathlib import Path

from tpath.pquery import PQuery


def test_default_constructor_lazy_initialization():
    """Test that PQuery() applies defaults only when query is executed."""
    query = PQuery()
    
    # Initially, working state should be empty
    assert query.start_paths == []
    assert query._query_func is None
    
    # Create temp files to test with
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        (temp_path / "test.txt").write_text("content")
        
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(str(temp_path))
            
            # When we execute the query, defaults should be applied
            files = query.files()
            
            # Now working state should be populated
            assert len(query.start_paths) == 1
            assert str(query.start_paths[0]) == "."
            assert query.is_recursive is True
            assert query._query_func is not None
            assert len(files) == 1
            assert files[0].name == "test.txt"
            
        finally:
            os.chdir(original_cwd)


def test_constructor_with_from_parameter():
    """Test PQuery constructor with from_ parameter."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        (temp_path / "test.py").write_text("print('hello')")
        
        query = PQuery(from_=temp_dir)
        
        # Initially, working state should be empty
        assert query.start_paths == []
        assert query._query_func is None
        
        # Execute query to apply defaults
        files = query.files()
        
        # Should use the provided from_ path
        assert len(query.start_paths) == 1
        assert query.start_paths[0] == temp_path
        assert query.is_recursive is True  # Default
        assert len(files) == 1
        assert files[0].name == "test.py"


def test_constructor_with_recursive_parameter():
    """Test PQuery constructor with recursive parameter."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        (temp_path / "test.txt").write_text("content")
        
        # Create subdirectory with file
        subdir = temp_path / "subdir"
        subdir.mkdir()
        (subdir / "nested.txt").write_text("nested")
        
        # Non-recursive query
        query = PQuery(from_=temp_dir, recursive=False)
        files = query.files()
        
        assert query.is_recursive is False
        assert len(files) == 1  # Only top-level file
        assert files[0].name == "test.txt"
        
        # Recursive query
        query2 = PQuery(from_=temp_dir, recursive=True)
        files2 = query2.files()
        
        assert query2.is_recursive is True
        assert len(files2) == 2  # Both files
        file_names = {f.name for f in files2}
        assert file_names == {"test.txt", "nested.txt"}


def test_constructor_with_where_parameter():
    """Test PQuery constructor with where parameter."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        (temp_path / "test.py").write_text("python file")
        (temp_path / "test.txt").write_text("text file")
        
        # Custom where function
        query = PQuery(from_=temp_dir, where=lambda p: p.suffix == ".py")
        files = query.files()
        
        assert len(files) == 1
        assert files[0].name == "test.py"


def test_constructor_all_parameters():
    """Test PQuery constructor with all parameters."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        (temp_path / "large.txt").write_text("x" * 1000)
        (temp_path / "small.txt").write_text("small")
        
        query = PQuery(
            from_=temp_dir,
            recursive=False,
            where=lambda p: p.size.bytes > 500
        )
        files = query.files()
        
        assert len(files) == 1
        assert files[0].name == "large.txt"


def test_fluent_methods_override_constructor():
    """Test that fluent methods can override constructor parameters."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        (temp_path / "test.py").write_text("python")
        (temp_path / "test.txt").write_text("text")
        
        # Constructor sets where, but fluent method overrides it
        query = PQuery(
            from_=temp_dir,
            where=lambda p: p.suffix == ".py"  # Would match only .py
        ).where(lambda p: p.suffix == ".txt")  # Override to match only .txt
        
        files = query.files()
        
        assert len(files) == 1
        assert files[0].name == "test.txt"


def test_lazy_initialization_with_chaining():
    """Test that lazy initialization works with method chaining."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        (temp_path / "test.txt").write_text("content")
        
        # Chain methods before executing
        query = (PQuery(from_=temp_dir)
                .recursive(False)
                .where(lambda p: p.suffix == ".txt"))
        
        # Before execution, working state should still be empty
        assert query.start_paths == []
        
        # Execute and verify
        files = query.files()
        assert len(files) == 1
        assert files[0].name == "test.txt"
        
        # After execution, working state should be populated
        assert len(query.start_paths) == 1


def test_default_where_filters_files_only():
    """Test that default where function filters out directories."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        (temp_path / "file.txt").write_text("content")
        (temp_path / "subdir").mkdir()
        
        query = PQuery(from_=temp_dir)
        files = query.files()
        
        # Should only return the file, not the directory
        assert len(files) == 1
        assert files[0].name == "file.txt"
        assert files[0].is_file()