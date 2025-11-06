#!/usr/bin/env python3
"""
Advanced typing patterns for flexible input/narrow output APIs.

This demonstrates several techniques for handling the "wide input, narrow output" 
typing challenge that many flexible APIs face.
"""

from collections.abc import Callable, Iterator, Sequence
from pathlib import Path
from typing import Generic, Protocol, TypeAlias, TypeVar, overload

# =============================================================================
# Pattern 1: Type Aliases (What we implemented)
# =============================================================================

PathLike: TypeAlias = str | Path
PathSequence: TypeAlias = Sequence[PathLike]
PathInput: TypeAlias = PathLike | PathSequence

def process_paths_v1(paths: PathInput) -> list[Path]:
    """Simple type alias approach - good for most cases."""
    if isinstance(paths, str | Path):
        return [Path(paths)]
    return [Path(p) for p in paths]

# =============================================================================
# Pattern 2: Function Overloads (Most precise typing)
# =============================================================================

@overload
def process_paths_v2(paths: str) -> list[Path]: ...

@overload
def process_paths_v2(paths: Path) -> list[Path]: ...

@overload
def process_paths_v2(paths: Sequence[str]) -> list[Path]: ...

@overload
def process_paths_v2(paths: Sequence[Path]) -> list[Path]: ...

def process_paths_v2(paths: PathInput) -> list[Path]:
    """Overloaded function - provides perfect IDE completion."""
    if isinstance(paths, str | Path):
        return [Path(paths)]
    return [Path(p) for p in paths]

# =============================================================================
# Pattern 3: Protocol-based typing (Most flexible)
# =============================================================================

class PathConvertible(Protocol):
    """Protocol for objects that can be converted to paths."""

    def __str__(self) -> str: ...

class FlexiblePathInput(Protocol):
    """Protocol for flexible path input that covers many cases."""
    pass

# You could extend this to accept anything path-like
def process_paths_v3(paths: PathConvertible | Sequence[PathConvertible]) -> list[Path]:
    """Protocol-based approach - most flexible."""
    if hasattr(paths, '__iter__') and not isinstance(paths, str):
        return [Path(str(p)) for p in paths]  # type: ignore
    return [Path(str(paths))]

# =============================================================================
# Pattern 4: Generic Builder Pattern (What libraries like pandas use)
# =============================================================================

T = TypeVar('T')
P = TypeVar('P', bound='PathQuery')

class PathQuery(Generic[T]):
    """Generic query builder that maintains type information."""

    def __init__(self) -> None:
        self._paths: list[Path] = []

    def from_paths(self: P, *paths: PathInput) -> P:
        """Fluent API that preserves the concrete type."""
        # Handle the type conversion here
        for path_input in paths:
            if isinstance(path_input, str | Path):
                self._paths.append(Path(path_input))
            else:
                self._paths.extend(Path(p) for p in path_input)
        return self

    def where(self: P, predicate: Callable[[Path], bool]) -> P:
        """Chain operations while preserving type."""
        # Would filter self._paths here
        return self

    def execute(self) -> Iterator[Path]:
        """Execute and return the narrow output type."""
        return iter(self._paths)

# =============================================================================
# Pattern 5: Type Guards (Runtime type checking that helps static analysis)
# =============================================================================

def is_path_sequence(obj: PathInput) -> bool:
    """Type guard to help with type narrowing."""
    return hasattr(obj, '__iter__') and not isinstance(obj, str)

def process_paths_v4(paths: PathInput) -> list[Path]:
    """Using type guards for better static analysis."""
    if is_path_sequence(paths):
        # Type checker knows paths is a sequence here
        return [Path(p) for p in paths]  # type: ignore[arg-type]
    else:
        # Type checker knows paths is PathLike here
        return [Path(paths)]

# =============================================================================
# Pattern 6: Conditional Types (Advanced - requires typing_extensions)
# =============================================================================

from typing import Literal


def process_paths_v5(
    paths: PathInput,
    return_type: Literal["list"] = "list"
) -> list[Path]:
    """Could be extended to return different types based on parameter."""
    result = []
    if isinstance(paths, str | Path):
        result = [Path(paths)]
    else:
        result = [Path(p) for p in paths]

    if return_type == "list":
        return result
    # Could add other return types...

# =============================================================================
# Usage Examples showing how each pattern helps with IDE support
# =============================================================================

if __name__ == "__main__":
    # All of these provide good typing experience:

    # Type aliases (our implementation)
    result1 = process_paths_v1("/tmp")
    result2 = process_paths_v1(["/tmp", "/var"])

    # Overloads (best IDE experience)
    result3 = process_paths_v2("/tmp")        # IDE knows input is str
    result4 = process_paths_v2(["/tmp"])      # IDE knows input is Sequence[str]

    # Generic builder
    query = PathQuery().from_paths("/tmp", ["/var", "/opt"]).where(lambda p: p.exists())
    paths = list(query.execute())  # IDE knows this returns Iterator[Path]

    print(f"Processed {len(paths)} paths using advanced typing patterns")


# =============================================================================
# Key Insights for Wide Input / Narrow Output APIs:
# =============================================================================

"""
1. **Type Aliases** (what we used): Simple, readable, good for most cases
   - Pro: Easy to understand and maintain
   - Con: Less precise than overloads

2. **Function Overloads**: Most precise IDE experience  
   - Pro: Perfect autocomplete and type checking
   - Con: More verbose, need to maintain multiple signatures

3. **Protocols**: Most flexible, works with duck typing
   - Pro: Accepts any compatible type, very Pythonic
   - Con: Less precise type information

4. **Generic Builders**: Great for fluent APIs
   - Pro: Maintains type information through method chains
   - Con: More complex implementation

5. **Type Guards**: Help with runtime type narrowing
   - Pro: Bridges runtime and static typing
   - Con: Need to implement guard functions

The key insight is that you can't completely solve this with typing alone - 
you need runtime type checking and conversion. The typing system just helps
make that conversion type-safe and provides better IDE experience.

Popular libraries handle this in different ways:
- **pathlib**: Uses overloads heavily
- **pandas**: Uses generic types and type: ignore pragmas  
- **click**: Uses protocols and runtime type conversion
- **pydantic**: Uses runtime validation with type coercion

Our TypeAlias approach strikes a good balance of simplicity and usefulness.
"""
