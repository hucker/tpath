"""
Debug TPath constructor
"""

import tempfile
from pathlib import Path
from tpath import TPath

with tempfile.TemporaryDirectory() as temp_dir:
    # Create a regular Path object
    path_obj = Path(temp_dir) / "test.txt"
    path_obj.write_text("test content")
    
    print("Path object:")
    print(f"  path_obj = {path_obj}")
    print(f"  path_obj.name = {path_obj.name}")
    print(f"  str(path_obj) = {str(path_obj)}")
    
    # Create TPath from the Path object
    tpath = TPath(path_obj)
    
    print("\nTPath object:")
    print(f"  tpath = {tpath}")
    print(f"  type(tpath) = {type(tpath)}")
    print(f"  tpath.name = {tpath.name}")
    print(f"  str(tpath) = {str(tpath)}")
    print(f"  tpath.exists() = {tpath.exists()}")
    
    # Also test regular string construction
    tpath2 = TPath(str(path_obj))
    print(f"\nTPath from string:")
    print(f"  tpath2 = {tpath2}")
    print(f"  tpath2.name = {tpath2.name}")
    print(f"  tpath2.exists() = {tpath2.exists()}")