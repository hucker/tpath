"""
Test for multiple where() detection in PQuery.
"""

import pytest
from src.tpath import PQuery


def test_multiple_where_calls_raise_error():
    """Test that multiple where() calls raise a ValueError with clear message."""
    pq = PQuery()
    
    # First where() call should work
    pq.where(lambda p: p.suffix == '.txt')
    
    # Second where() call should raise ValueError
    with pytest.raises(ValueError, match="Multiple where\\(\\) calls are not supported"):
        pq.where(lambda p: p.size.mb > 10)


def test_single_where_with_combined_logic_works():
    """Test that single where() with combined logic works correctly."""
    import tempfile
    from pathlib import Path
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test files
        (temp_path / "small.txt").write_text("x" * 10)      # 10 bytes, .txt
        (temp_path / "large.txt").write_text("x" * 1000)    # 1000 bytes, .txt
        (temp_path / "large.log").write_text("x" * 1000)    # 1000 bytes, .log
        
        # Single where with combined logic should work
        results = (PQuery()
            .from_(temp_dir)
            .where(lambda p: p.suffix == '.txt' and p.size.bytes > 500)
            .files()
        )
        
        # Should find only large.txt
        assert len(results) == 1
        assert results[0].name == "large.txt"