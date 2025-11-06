"""
Path querying functionality for TPath objects.

Provides a pathql-inspired API for querying files with lambda expressions.
"""

from pathlib import Path
from typing import Callable, Iterator, Any

from .._core import TPath


class PQuery:
    """
    A path query builder that provides a fluent API for file filtering.
    
    Similar to pathql but using lambda expressions for flexible filtering.
    """
    
    def __init__(self, 
                 from_: str | Path | TPath | None = None,
                 recursive: bool | None = None, 
                 where: Callable[[TPath], bool] | None = None):
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
    
    def from_(self, path: str | Path | TPath) -> 'PQuery':
        """
        Set or add a starting directory path.
        
        Args:
            path: Starting directory path
            
        Returns:
            PQuery: Self for method chaining
            
        Example:
            PQuery().from_("/logs").where(lambda p: p.size.gb < 1)
        """
        # Apply defaults if start_paths is empty
        if not self.start_paths:
            default_path = self._init_from or '.'
            self.start_paths = [TPath(default_path)]
        
        # If this is the first call and we still have the default '.', replace it
        if len(self.start_paths) == 1 and str(self.start_paths[0]) == '.':
            self.start_paths = [TPath(path)]
        else:
            # Otherwise add to the list
            self.start_paths.append(TPath(path))
        return self
    
    def from_path(self, path: str | Path | TPath) -> 'PQuery':
        """
        Add another starting directory path.
        
        Args:
            path: Additional starting directory path
            
        Returns:
            PQuery: Self for method chaining
            
        Example:
            PQuery().from_("/logs").from_path("/var/log").where(lambda p: p.suffix == ".log")
        """
        # Apply defaults if start_paths is empty
        if not self.start_paths:
            default_path = self._init_from or '.'
            self.start_paths = [TPath(default_path)]
        
        self.start_paths.append(TPath(path))
        return self
    
    def recursive(self, recursive: bool = True) -> 'PQuery':
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
        self._init_recursive = recursive  # Ensure this takes precedence over constructor default
        return self
    
    def where(self, query: Callable[[TPath], bool]) -> 'PQuery':
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
            default_path = self._init_from or '.'
            self.start_paths = [TPath(default_path)]
        
        self.is_recursive = self._init_recursive if self._init_recursive is not None else True
        
        if self._query_func is None:
            self._query_func = self._init_where or (lambda p: p.is_file())
            
        for start_path in self.start_paths:
            if not start_path.exists():
                continue

            if not start_path.is_dir():
                # If it's a file, just test that single file
                try:
                    if self._query_func(start_path):
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
                                yield tpath
                        except (OSError, PermissionError):
                            # Skip files we can't access
                            continue
            except (OSError, PermissionError):
                # Handle cases where we can't read the directory
                continue
    
    def files(self) -> list[TPath]:
        """
        Execute the query and return matching files as a list.
        
        Returns:
            list[TPath]: List of matching file paths
            
        Example:
            recent_logs = pquery(from_="/logs").where(lambda p: p.age.hours < 24).files()
        """
        return list(self._iter_files())
    
    def select(self, selector: Callable[[TPath], Any]) -> list[Any]:
        """
        Execute the query and return selected properties from matching files.
        
        Args:
            selector: Lambda function that takes a TPath and returns any value
            
        Returns:
            list[Any]: List of selected values from matching files
            
        Example:
            file_sizes = pquery(from_="/logs").where(lambda p: p.age.hours < 24).select(lambda p: p.size.bytes)
            file_names = pquery(from_="/logs").where(lambda p: p.suffix == ".log").select(lambda p: p.name)
        """
        return [selector(path) for path in self._iter_files()]
    
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
    
    def __iter__(self) -> Iterator[TPath]:
        """Allow iteration over the query results."""
        return self._iter_files()


def pquery(from_: str | Path | TPath | list[str | Path | TPath] | None = None, recursive: bool = True) -> PQuery:
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
        query = PQuery().from_("/logs").from_path("/var/log").recursive(True).where(lambda p: p.size.gb > 1)
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
    return pquery(from_, recursive).where(query).files()


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