"""
Minimal test to understand the issue
"""

import tempfile
from pathlib import Path
from tpath import TPath

# Test basic construction
print("Testing basic TPath construction...")

# Try string construction first
tpath_str = TPath(".")
print(f"TPath('.') -> name='{tpath_str.name}', str='{tpath_str}'")

# Test with full path string
with tempfile.TemporaryDirectory() as temp_dir:
    full_path = f"{temp_dir}/test.txt"
    Path(full_path).write_text("test")
    
    print(f"\nTesting with full path: {full_path}")
    tpath_full = TPath(full_path)
    print(f"TPath(full_path) -> name='{tpath_full.name}', str='{tpath_full}'")
    
    # Test Path object
    path_obj = Path(full_path)
    print(f"\nPath object: {path_obj}")
    print(f"Args passed to TPath: {(str(path_obj),)}")
    
    tpath_from_path = TPath(path_obj)
    print(f"TPath(Path(...)) -> name='{tpath_from_path.name}', str='{tpath_from_path}'")