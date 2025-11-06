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
    
    def __init__(self, from_: str | Path | TPath | list[str | Path | TPath], recursive: bool = True):
        """
        Initialize a path query.
        
        Args:
            from_: Starting directory path(s)
            recursive: Whether to search subdirectories recursively
        """
        # Normalize from_ to a list of TPath objects
        if isinstance(from_, list):
            self.start_paths = [TPath(path) for path in from_]
        else:
            self.start_paths = [TPath(from_)]
        
        self.recursive = recursive
        self._query_func: Callable[[TPath], bool] | None = None
    
    def where(self, query: Callable[[TPath], bool]) -> 'PQuery':
        """
        Add a filter condition using a lambda expression.
        
        Args:
            query: Lambda function that takes a TPath and returns bool
            
        Returns:
            PQuery: Self for method chaining
            
        Example:
            pquery(from_="/logs").where(lambda p: p.size.gb < 1)
        """
        self._query_func = query
        return self
    
    def _iter_files(self) -> Iterator[TPath]:
        """Internal method to iterate over all matching files."""
        if self._query_func is None:
            raise ValueError("No query specified. Use .where() to add a filter condition.")
            
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
                glob_method = start_path.rglob if self.recursive else start_path.glob
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


def pquery(from_: str | Path | TPath | list[str | Path | TPath], recursive: bool = True) -> PQuery:
    """
    Create a new path query.
    
    Args:
        from_: Starting directory path(s). Can be:
            - Single path (string, Path, or TPath)  
            - List of paths (strings, Paths, or TPaths)
        recursive: Whether to search subdirectories recursively
            - True: uses rglob("*") for recursive search
            - False: uses glob("*") for current directory only
    
    Returns:
        PQuery: A query builder object
        
    Examples:
        # Get all Python files
        py_files = pquery(from_="./src").where(lambda p: p.suffix == ".py").files()
        
        # Get file sizes of large files
        large_sizes = pquery(from_="/data").where(lambda p: p.size.gb > 1).select(lambda p: p.size.bytes)
        
        # Check if any recent error logs exist
        has_errors = pquery(from_="/logs").where(lambda p: "error" in p.name and p.age.hours < 1).exists()
        
        # Multiple starting paths
        all_configs = pquery(from_=["/etc", "/opt/config"]).where(lambda p: p.suffix == ".conf").files()
    """
    return PQuery(from_, recursive)


# Legacy compatibility functions (deprecated - use pquery instead)
def pfilter(
    from_: str | Path | TPath | list[str | Path | TPath],
    query: Callable[[TPath], bool],
    recursive: bool = True,
) -> Iterator[TPath]:
    """
    DEPRECATED: Use pquery().where().files() instead.
    
    Filter paths using a lambda expression.
    """
    return pquery(from_, recursive).where(query).__iter__()


def pfind(
    from_: str | Path | TPath | list[str | Path | TPath],
    query: Callable[[TPath], bool],
    recursive: bool = True,
) -> list[TPath]:
    """DEPRECATED: Use pquery().where().files() instead."""
    return pquery(from_, recursive).where(query).files()


def pfirst(
    from_: str | Path | TPath | list[str | Path | TPath],
    query: Callable[[TPath], bool],
    recursive: bool = True,
) -> TPath | None:
    """DEPRECATED: Use pquery().where().first() instead."""
    return pquery(from_, recursive).where(query).first()


def pexists(
    from_: str | Path | TPath | list[str | Path | TPath],
    query: Callable[[TPath], bool],
    recursive: bool = True,
) -> bool:
    """DEPRECATED: Use pquery().where().exists() instead."""
    return pquery(from_, recursive).where(query).exists()


def pcount(
    from_: str | Path | TPath | list[str | Path | TPath],
    query: Callable[[TPath], bool],
    recursive: bool = True,
) -> int:
    """DEPRECATED: Use pquery().where().count() instead."""
    return pquery(from_, recursive).where(query).count()


__all__ = ["pquery", "PQuery", "pfilter", "pfind", "pfirst", "pexists", "pcount"]