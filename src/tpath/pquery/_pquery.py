"""
Path querying functionality for TPath objects.

Provides a pathql-inspired API for querying files with lambda expressions.
"""

from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

from .._core import TPath


class PQuery:
    """
    A path query builder that provides a fluent API for file filtering.

    Similar to pathql but using lambda expressions for flexible filtering.
    """

    def __init__(
        self,
        from_: str | Path | TPath | None = None,
        recursive: bool | None = None,
        where: Callable[[TPath], bool] | None = None,
    ):
        """
        Initialize a path query with optional parameters.

        Args:
            from_: Starting directory path (defaults to current directory '.' when query runs)
            recursive: Whether to search subdirectories recursively (defaults to True when query runs)
            where: Initial filter condition (defaults to files only when query runs: lambda p: p.is_file())

        Examples:
            PQuery()                                    # Uses defaults when executed
            PQuery(from_="/logs")                       # /logs dir, other defaults when executed
            PQuery(recursive=False)                     # Current dir, non-recursive, files only
            PQuery(where=lambda p: p.suffix == ".py")  # Current dir, recursive, Python files
            PQuery("/src", False, lambda p: p.size.mb > 1)  # /src, non-recursive, large files
        """
        # Store constructor parameters for lazy evaluation
        self._init_from = from_
        self._init_recursive = recursive
        self._init_where = where

        # Working state - will be populated when query runs
        self.start_paths: list[TPath] = []
        self.is_recursive: bool = True  # Default, may be overridden
        self._query_func: Callable[[TPath], bool] | None = None
        self._use_distinct: bool = False  # Whether to deduplicate results

    def from_(self, *paths: str | Path | list[str | Path]) -> "PQuery":
        """
        Set or add starting directory paths.

        Args:
            *paths: One or more starting directory paths, or lists of paths

        Returns:
            PQuery: Self for method chaining

        Examples:
            PQuery().from_("/logs").where(lambda p: p.size.gb < 1)
            PQuery().from_("/logs", "/var/log", "/opt/app/logs").where(lambda p: p.suffix == ".log")
            PQuery().from_(path_list).where(lambda p: p.suffix == ".txt")  # list of paths
            PQuery().from_("/logs", path_list, "/var/log").files()  # mixed individual and list
        """
        if not paths:
            raise ValueError("At least one path must be provided")
        
        # Flatten any lists in the arguments
        flattened_paths = []
        for path in paths:
            if isinstance(path, list):
                flattened_paths.extend(path)
            else:
                flattened_paths.append(path)
        
        if not flattened_paths:
            raise ValueError("At least one path must be provided")
            
        # Apply defaults if start_paths is empty
        if not self.start_paths:
            default_path = self._init_from or "."
            self.start_paths = [TPath(default_path)]

        # If this is the first call and we still have the default '.', replace it
        if len(self.start_paths) == 1 and str(self.start_paths[0]) == ".":
            self.start_paths = [path if isinstance(path, TPath) else TPath(path) for path in flattened_paths]
        else:
            # Otherwise add to the list
            self.start_paths.extend(path if isinstance(path, TPath) else TPath(path) for path in flattened_paths)
        return self

    def distinct(self) -> "PQuery":
        """
        Enable deduplication of results at the generator level.
        
        This method enables efficient duplicate removal by tracking seen files in a set
        during iteration. Only the first occurrence of each unique file path is yielded.
        Particularly useful when searching multiple overlapping directories or when
        symbolic links might create duplicate references.

        Returns:
            PQuery: Self for method chaining

        Examples:
            # Remove duplicates when searching multiple directories that might overlap
            unique_logs = PQuery().from_("./logs", "./backup/logs").distinct().files()
            
            # Get first 10 unique Python files (stops early when 10 found)
            first_unique = (PQuery()
                           .from_("./src", "./lib", "./vendor")
                           .where(lambda p: p.suffix == ".py")
                           .distinct()
                           .take(10))
            
            # Handle symbolic links that might create duplicates
            real_configs = (PQuery()
                           .from_("./config", "./etc/config")
                           .where(lambda p: p.suffix == ".yaml")
                           .distinct()
                           .files())
            
        Performance Notes:
            - Uses O(k) memory where k = number of unique files processed
            - Enables early termination: distinct().take(n) can stop after finding n unique items
            - More efficient than post-processing with set(results) for large datasets
            - Order of first occurrence is preserved
        """
        self._use_distinct = True
        return self

    def recursive(self, recursive: bool = True) -> "PQuery":
        """
        Set whether to search subdirectories recursively.

        Args:
            recursive: Whether to search subdirectories recursively

        Returns:
            PQuery: Self for method chaining

        Example:
            PQuery().from_("/logs").recursive(False).where(lambda p: p.suffix == ".log")
        """
        # Override both the working state and the init parameter
        self.is_recursive = recursive
        self._init_recursive = (
            recursive  # Ensure this takes precedence over constructor default
        )
        return self

    def where(self, query: Callable[[TPath], bool]) -> "PQuery":
        """
        Add a filter condition using a lambda expression.

        Args:
            query: Lambda function that takes a TPath and returns bool

        Returns:
            PQuery: Self for method chaining

        Example:
            pquery(from_="/logs").where(lambda p: p.size.gb < 1)

        Note:
            Multiple where() calls are not supported. Use logical operators within a single lambda instead:

            # WRONG: Multiple where() calls (will raise error)
            .where(lambda p: p.suffix == '.txt').where(lambda p: p.size.mb > 10)

            # CORRECT: Single where() with logical operators
            .where(lambda p: p.suffix == '.txt' and p.size.mb > 10)
        """
        # Check if where() has already been called
        if self._query_func is not None:
            raise ValueError(
                "Multiple where() calls are not supported. "
                "Combine conditions using logical operators within a single lambda instead:\n"
                "  # WRONG:\n"
                "  .where(lambda p: condition1).where(lambda p: condition2)\n"
                "  # CORRECT:\n"
                "  .where(lambda p: condition1 and condition2)"
            )

        self._query_func = query
        return self

    def _iter_files(self) -> Iterator[TPath]:
        """Internal method to iterate over all matching files."""
        # Apply defaults using null coalescing
        if not self.start_paths:
            default_path = self._init_from or "."
            self.start_paths = [TPath(default_path)]

        self.is_recursive = (
            self._init_recursive if self._init_recursive is not None else True
        )

        if self._query_func is None:
            self._query_func = self._init_where or (lambda p: p.is_file())

        # Set for tracking seen files if distinct is enabled
        seen_files: set[TPath] = set() if self._use_distinct else set()

        for start_path in self.start_paths:
            if not start_path.exists():
                continue

            if not start_path.is_dir():
                # If it's a file, just test that single file
                try:
                    if self._query_func(start_path):
                        if not self._use_distinct or start_path not in seen_files:
                            if self._use_distinct:
                                seen_files.add(start_path)
                            yield start_path
                except (OSError, PermissionError):
                    continue
                continue

            # Use glob or rglob based on recursive flag
            try:
                glob_method = start_path.rglob if self.is_recursive else start_path.glob
                for path in glob_method("*"):
                    if path.is_file():  # Only yield files, not directories
                        tpath = TPath(path)
                        try:
                            if self._query_func(tpath):
                                if not self._use_distinct or tpath not in seen_files:
                                    if self._use_distinct:
                                        seen_files.add(tpath)
                                    yield tpath
                        except (OSError, PermissionError):
                            # Skip files we can't access
                            continue
            except (OSError, PermissionError):
                # Handle cases where we can't read the directory
                continue

    def files(self) -> Iterator[TPath]:
        """
        Execute the query and return matching files as an iterator.

        Returns:
            Iterator[TPath]: Iterator of matching file paths

        Examples:
            # Stream processing (memory efficient)
            for file in pquery(from_="/logs").where(lambda p: p.age.hours < 24).files():
                process_file(file)
            
            # Materialize when needed
            all_files = list(pquery(from_=paths).distinct().files())
        """
        return self._iter_files()

    # Remove the old distinct() method - it will be on PQueryResult instead

    def select(self, selector: Callable[[TPath], Any]) -> Iterator[Any]:
        """
        Execute the query and return selected properties from matching files as an iterator.

        Args:
            selector: Lambda function that takes a TPath and returns any value

        Returns:
            Iterator[Any]: Iterator of selected values from matching files

        Examples:
            # Stream processing (memory efficient)
            for size in pquery(from_="/logs").where(lambda p: p.age.hours < 24).select(lambda p: p.size.bytes):
                process_size(size)
            
            # Materialize when needed
            file_names = list(pquery(from_="/logs").where(lambda p: p.suffix == ".log").select(lambda p: p.name))
        """
        return (selector(path) for path in self._iter_files())

    def first(self) -> TPath | None:
        """
        Return the first matching file or None if no matches.

        Returns:
            TPath | None: First matching file or None

        Example:
            latest_error = pquery(from_="./logs").where(lambda p: "error" in p.name).first()
        """
        try:
            return next(self._iter_files())
        except StopIteration:
            return None

    def exists(self) -> bool:
        """
        Check if any files match the query.

        Returns:
            bool: True if at least one matching file exists

        Example:
            has_large_files = pquery(from_="./data").where(lambda p: p.size.gb > 1).exists()
        """
        try:
            next(self._iter_files())
            return True
        except StopIteration:
            return False

    def count(self) -> int:
        """
        Count the number of matching files.

        Returns:
            int: Number of matching files

        Example:
            num_python_files = pquery(from_="./src").where(lambda p: p.suffix == ".py").count()
        """
        return sum(1 for _ in self._iter_files())

    def take(
        self, n: int, key: Callable[[TPath], Any] | None = None, reverse: bool = True
    ) -> list[TPath]:
        """
        Take the top n files, optionally ordered by a key function.

        This method is optimized for getting the "best" n files without sorting all results.
        Uses heapq.nlargest/nsmallest for O(n log k) performance when key is provided.

        Args:
            n: Number of files to return
            key: Optional function to extract comparison key from TPath
                Can return a single value or tuple for multi-column sorting
            reverse: If True (default), return largest/newest items
                    If False, return smallest/oldest items

        Returns:
            list[TPath]: Up to n files matching the criteria

        Examples:
            # Get 10 largest files (most common case)
            largest = query.take(10, key=lambda p: p.size.bytes)

            # Get 5 oldest files
            oldest = query.take(5, key=lambda p: p.mtime.timestamp, reverse=False)

            # Multi-column sort: largest files, then most recent
            best = query.take(10, key=lambda p: (p.size.bytes, p.mtime.timestamp))

            # Just any 10 files (no ordering)
            any_files = query.take(10)
        """
        import heapq

        if key is None:
            # Simple case: just take first n files
            result = []
            for i, path in enumerate(self._iter_files()):
                if i >= n:
                    break
                result.append(path)
            return result

        # Efficient top-k using heap - work directly with iterator
        if reverse:
            return heapq.nlargest(n, self._iter_files(), key=key)
        else:
            return heapq.nsmallest(n, self._iter_files(), key=key)

    def sort(
        self, key: Callable[[TPath], Any] | None = None, reverse: bool = False
    ) -> list[TPath]:
        """
        Sort all matching files by a key function.

        This method performs a full sort of all results. Use take() if you only need
        the top/bottom n files for better performance.

        Args:
            key: Function to extract comparison key from TPath
                Can return a single value or tuple for multi-column sorting
            reverse: If False (default), sort in ascending order
                    If True, sort in descending order

        Returns:
            list[TPath]: All matching files sorted by the key

        Examples:
            # Sort by file size (smallest to largest)
            by_size = query.sort(key=lambda p: p.size.bytes)

            # Sort by modification time (newest to oldest)
            by_time = query.sort(key=lambda p: p.mtime.timestamp, reverse=True)

            # Multi-column sort: by directory, then by name
            by_path = query.sort(key=lambda p: (p.parent.name, p.name))

            # Sort by name (alphabetical)
            by_name = query.sort(key=lambda p: p.name)
        """
        files = list(self._iter_files())
        if key is None:
            return sorted(files, reverse=reverse)
        return sorted(files, key=key, reverse=reverse)

    def __iter__(self) -> Iterator[TPath]:
        """Allow iteration over the query results."""
        return self._iter_files()


def pquery(
    from_: str | Path | TPath | list[str | Path | TPath] | None = None,
    recursive: bool = True,
) -> PQuery:
    """
    Create a new path query.

    Args:
        from_: Starting directory path(s). Can be:
            - Single path (string, Path, or TPath)
            - List of paths (strings, Paths, or TPaths)
            - None: defaults to current directory
        recursive: Whether to search subdirectories recursively
            - True: uses rglob("*") for recursive search
            - False: uses glob("*") for current directory only

    Returns:
        PQuery: A query builder object

    Examples:
        # Default to current directory
        py_files = pquery().where(lambda p: p.suffix == ".py").files()

        # Single path
        py_files = pquery(from_="./src").where(lambda p: p.suffix == ".py").files()

        # Multiple starting paths
        all_configs = pquery(from_=["/etc", "/opt/config"]).where(lambda p: p.suffix == ".conf").files()

        # Using the fluent API
        query = PQuery().from_("/logs").from_("/var/log").recursive(True).where(lambda p: p.size.gb > 1)
    """
    query = PQuery().recursive(recursive)

    if from_ is not None:
        if isinstance(from_, list):
            # Clear the default '.' path and add all provided paths
            query.start_paths = []
            for path in from_:
                query.start_paths.append(TPath(path))
        else:
            # Replace the default '.' path with the provided path
            query.start_paths = [TPath(from_)]

    return query


# Legacy compatibility functions (deprecated - use pquery instead)
def pfilter(
    from_: str | Path | TPath | list[str | Path | TPath],
    query: Callable[[TPath], bool],
    recursive: bool = True,
) -> Iterator[TPath]:
    """
    DEPRECATED: Use PQuery().from_().where().files() instead.

    Filter paths using a lambda expression.
    """
    return pquery(from_, recursive).where(query).__iter__()


def pfind(
    from_: str | Path | TPath | list[str | Path | TPath],
    query: Callable[[TPath], bool],
    recursive: bool = True,
) -> list[TPath]:
    """DEPRECATED: Use PQuery().from_().where().files() instead."""
    return list(pquery(from_, recursive).where(query).files())


def pfirst(
    from_: str | Path | TPath | list[str | Path | TPath],
    query: Callable[[TPath], bool],
    recursive: bool = True,
) -> TPath | None:
    """DEPRECATED: Use PQuery().from_().where().first() instead."""
    return pquery(from_, recursive).where(query).first()


def pexists(
    from_: str | Path | TPath | list[str | Path | TPath],
    query: Callable[[TPath], bool],
    recursive: bool = True,
) -> bool:
    """DEPRECATED: Use PQuery().from_().where().exists() instead."""
    return pquery(from_, recursive).where(query).exists()


def pcount(
    from_: str | Path | TPath | list[str | Path | TPath],
    query: Callable[[TPath], bool],
    recursive: bool = True,
) -> int:
    """DEPRECATED: Use PQuery().from_().where().count() instead."""
    return pquery(from_, recursive).where(query).count()


__all__ = ["pquery", "PQuery", "pfilter", "pfind", "pfirst", "pexists", "pcount"]
