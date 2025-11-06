"""
Tests for pquery lambda-based filtering functionality.
"""

from tpath.pquery._filter import pquery, pfilter, pfind, pfirst, pexists, pcount


def test_pfilter_basic_functionality(tmp_path):
    """Test basic pfilter functionality with lambda expressions."""
    # Create test files
    (tmp_path / "small.txt").write_text("small")
    (tmp_path / "large.txt").write_text("x" * 1000)
    (tmp_path / "test.py").write_text("print('hello')")

    # Test basic filtering
    small_files = list(pfilter(tmp_path, lambda p: p.size.bytes < 100))
    assert len(small_files) == 2  # small.txt and test.py

    py_files = list(pfilter(tmp_path, lambda p: p.suffix == ".py"))
    assert len(py_files) == 1
    assert py_files[0].name == "test.py"


def test_pfilter_complex_queries(tmp_path):
    """Test complex lambda expressions with AND/OR logic."""
    # Create diverse test files
    (tmp_path / "small.txt").write_text("tiny")
    (tmp_path / "large.txt").write_text("x" * 1000)
    (tmp_path / "medium.py").write_text("print('medium')")
    (tmp_path / "huge.log").write_text("y" * 5000)

    # Test OR logic
    text_or_large = list(
        pfilter(tmp_path, query=lambda p: p.suffix == ".txt" or p.size.bytes > 2000)
    )
    assert len(text_or_large) == 3  # both .txt files + huge.log

    # Test AND logic
    readable_py = list(
        pfilter(tmp_path, query=lambda p: p.suffix == ".py" and p.readable)
    )
    assert len(readable_py) == 1
    assert readable_py[0].name == "medium.py"


def test_pfilter_convenience_functions(tmp_path):
    """Test convenience functions pfind, pfirst, pexists, pcount."""
    # Create test files
    (tmp_path / "file1.txt").write_text("content1")
    (tmp_path / "file2.py").write_text("content2")
    (tmp_path / "file3.log").write_text("content3")

    # Test pfind (returns list)
    all_files = pfind(tmp_path, lambda p: True)
    assert len(all_files) == 3
    assert isinstance(all_files, list)

    # Test pfirst (returns first match or None)
    first_txt = pfirst(tmp_path, lambda p: p.suffix == ".txt")
    assert first_txt is not None
    assert first_txt.suffix == ".txt"

    no_match = pfirst(tmp_path, lambda p: p.suffix == ".xyz")
    assert no_match is None

    # Test pexists (returns bool)
    assert pexists(tmp_path, lambda p: p.suffix == ".py") is True
    assert pexists(tmp_path, lambda p: p.suffix == ".xyz") is False

    # Test pcount (returns int)
    assert pcount(tmp_path, lambda p: True) == 3
    assert pcount(tmp_path, lambda p: p.suffix == ".txt") == 1
    assert pcount(tmp_path, lambda p: p.suffix == ".xyz") == 0


def test_pfilter_recursive_vs_non_recursive(tmp_path):
    """Test recursive vs non-recursive directory traversal."""
    # Create nested directory structure
    (tmp_path / "root.txt").write_text("root")
    sub_dir = tmp_path / "subdir"
    sub_dir.mkdir()
    (sub_dir / "nested.txt").write_text("nested")

    # Test recursive (default)
    recursive_files = list(pfilter(tmp_path, lambda p: p.suffix == ".txt"))
    assert len(recursive_files) == 2

    # Test non-recursive
    non_recursive_files = list(
        pfilter(tmp_path, lambda p: p.suffix == ".txt", recursive=False)
    )
    assert len(non_recursive_files) == 1
    assert non_recursive_files[0].name == "root.txt"


def test_pfilter_with_tpath_properties(tmp_path):
    """Test pfilter using various TPath properties."""
    # Create files with different properties
    (tmp_path / "readable.txt").write_text("content")
    (tmp_path / "empty.txt").write_text("")

    # Test using size properties
    non_empty = list(pfilter(tmp_path, lambda p: p.size.bytes > 0))
    assert len(non_empty) == 1

    # Test using access properties
    readable_files = list(pfilter(tmp_path, lambda p: p.readable))
    assert len(readable_files) == 2  # Both files should be readable

    # Test using age properties (files should be very recent)
    recent_files = list(pfilter(tmp_path, lambda p: p.age.seconds < 60))
    assert len(recent_files) == 2


def test_pfilter_multiple_paths(tmp_path):
    """Test pfilter with multiple starting paths."""
    # Create multiple directories with files
    dir1 = tmp_path / "dir1"
    dir2 = tmp_path / "dir2"
    dir1.mkdir()
    dir2.mkdir()

    (dir1 / "file1.txt").write_text("content1")
    (dir1 / "file2.py").write_text("content2")
    (dir2 / "file3.txt").write_text("content3")
    (dir2 / "file4.log").write_text("content4")

    # Test with list of string paths
    txt_files = list(pfilter([str(dir1), str(dir2)], lambda p: p.suffix == ".txt"))
    assert len(txt_files) == 2

    # Test with list of Path objects
    all_files = list(pfilter([dir1, dir2], lambda p: True))
    assert len(all_files) == 4

    # Test with convenience functions and multiple paths
    py_count = pcount([dir1, dir2], lambda p: p.suffix == ".py")
    assert py_count == 1

    first_log = pfirst([dir1, dir2], lambda p: p.suffix == ".log")
    assert first_log is not None
    assert first_log.suffix == ".log"

    has_txt = pexists([dir1, dir2], lambda p: p.suffix == ".txt")
    assert has_txt is True


def test_pfilter_glob_vs_rglob(tmp_path):
    """Test that recursive flag properly uses glob vs rglob methods."""
    # Create nested structure
    (tmp_path / "root.txt").write_text("root")

    sub1 = tmp_path / "sub1"
    sub1.mkdir()
    (sub1 / "sub1.txt").write_text("sub1")

    sub2 = sub1 / "sub2"
    sub2.mkdir()
    (sub2 / "deep.txt").write_text("deep")

    # Recursive should find all files (uses rglob)
    recursive_files = list(pfilter(tmp_path, lambda p: p.suffix == ".txt", recursive=True))
    assert len(recursive_files) == 3  # root.txt, sub1.txt, deep.txt

    # Non-recursive should only find top-level files (uses glob)
    non_recursive_files = list(pfilter(tmp_path, lambda p: p.suffix == ".txt", recursive=False))
    assert len(non_recursive_files) == 1  # only root.txt
    assert non_recursive_files[0].name == "root.txt"

    # Test intermediate directory non-recursive
    sub1_files = list(pfilter(sub1, lambda p: p.suffix == ".txt", recursive=False))
    assert len(sub1_files) == 1  # only sub1.txt
    assert sub1_files[0].name == "sub1.txt"


def test_pquery_basic_functionality(tmp_path):
    """Test basic pquery functionality with fluent API."""
    # Create test files
    (tmp_path / "small.txt").write_text("small")
    (tmp_path / "large.txt").write_text("x" * 1000)
    (tmp_path / "test.py").write_text("print('hello')")

    # Test basic querying with files()
    small_files = pquery(from_=tmp_path).where(lambda p: p.size.bytes < 100).files()
    assert len(small_files) == 2  # small.txt and test.py

    py_files = pquery(from_=tmp_path).where(lambda p: p.suffix == ".py").files()
    assert len(py_files) == 1
    assert py_files[0].name == "test.py"


def test_pquery_select_functionality(tmp_path):
    """Test pquery select() method for extracting properties."""
    # Create test files
    (tmp_path / "file1.txt").write_text("content1")
    (tmp_path / "file2.py").write_text("content2")
    (tmp_path / "file3.log").write_text("content3")

    # Test selecting file names
    names = pquery(from_=tmp_path).where(lambda p: True).select(lambda p: p.name)
    assert len(names) == 3
    assert "file1.txt" in names
    assert "file2.py" in names
    assert "file3.log" in names

    # Test selecting file sizes
    sizes = pquery(from_=tmp_path).where(lambda p: p.suffix == ".txt").select(lambda p: p.size.bytes)
    assert len(sizes) == 1
    assert sizes[0] == 8  # "content1"

    # Test selecting suffixes
    suffixes = pquery(from_=tmp_path).where(lambda p: True).select(lambda p: p.suffix)
    assert set(suffixes) == {".txt", ".py", ".log"}


def test_pquery_convenience_methods(tmp_path):
    """Test pquery convenience methods: first(), exists(), count()."""
    # Create test files
    (tmp_path / "file1.txt").write_text("content1")
    (tmp_path / "file2.py").write_text("content2")
    (tmp_path / "file3.log").write_text("content3")

    # Test first()
    first_txt = pquery(from_=tmp_path).where(lambda p: p.suffix == ".txt").first()
    assert first_txt is not None
    assert first_txt.suffix == ".txt"

    no_match = pquery(from_=tmp_path).where(lambda p: p.suffix == ".xyz").first()
    assert no_match is None

    # Test exists()
    assert pquery(from_=tmp_path).where(lambda p: p.suffix == ".py").exists() is True
    assert pquery(from_=tmp_path).where(lambda p: p.suffix == ".xyz").exists() is False

    # Test count()
    assert pquery(from_=tmp_path).where(lambda p: True).count() == 3
    assert pquery(from_=tmp_path).where(lambda p: p.suffix == ".txt").count() == 1
    assert pquery(from_=tmp_path).where(lambda p: p.suffix == ".xyz").count() == 0


def test_pquery_multiple_paths(tmp_path):
    """Test pquery with multiple starting paths."""
    # Create multiple directories with files
    dir1 = tmp_path / "dir1"
    dir2 = tmp_path / "dir2"
    dir1.mkdir()
    dir2.mkdir()

    (dir1 / "file1.txt").write_text("content1")
    (dir1 / "file2.py").write_text("content2")
    (dir2 / "file3.txt").write_text("content3")
    (dir2 / "file4.log").write_text("content4")

    # Test with list of paths
    txt_files = pquery(from_=[dir1, dir2]).where(lambda p: p.suffix == ".txt").files()
    assert len(txt_files) == 2

    # Test select with multiple paths
    names = pquery(from_=[dir1, dir2]).where(lambda p: True).select(lambda p: p.name)
    assert len(names) == 4

    # Test count with multiple paths
    py_count = pquery(from_=[dir1, dir2]).where(lambda p: p.suffix == ".py").count()
    assert py_count == 1


def test_pquery_iteration(tmp_path):
    """Test that pquery objects are iterable."""
    # Create test files
    (tmp_path / "file1.txt").write_text("content1")
    (tmp_path / "file2.py").write_text("content2")

    # Test iteration
    query = pquery(from_=tmp_path).where(lambda p: True)
    files_list = list(query)
    assert len(files_list) == 2

    # Test that iteration works multiple times
    files_list2 = list(query)
    assert len(files_list2) == 2
    assert files_list[0].name == files_list2[0].name