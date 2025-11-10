"""Clean tests for PQuery.map_parallel (safe copy).

This file is a replacement test harness used while the original
``test_map_parallel.py`` is being repaired. It contains the same
semantics but is written conservatively to satisfy CODESTYLE.md.
"""

from __future__ import annotations

import pathlib
import time

import pytest

from tpath.pquery._pquery import pquery


def _make_files(tmp_path: pathlib.Path, count: int) -> list[str]:
    """Create `count` files under ``tmp_path`` and return their paths."""
    paths: list[str] = []
    for i in range(count):
        p = tmp_path / f"file_{i}.txt"
        p.write_text(f"{i}\n")
        paths.append(str(p))
    return paths


@pytest.mark.parametrize("workers", [1, 2])
def test_basic(tmp_path: pathlib.Path, workers: int) -> None:
    """All files are processed and MapResult fields are present."""
    _make_files(tmp_path, 4)

    results = list(
        pquery(from_=str(tmp_path)).map_parallel(lambda p: p.name, workers=workers)
    )

    assert len(results) == 4, "expected 4 results"
    names = {r.data for r in results}
    assert names == {f"file_{i}.txt" for i in range(4)}, "unexpected result names"


def test_single_worker_series_timing(tmp_path: pathlib.Path) -> None:
    """With one worker, sleeps run in series and take longer."""
    _make_files(tmp_path, 4)

    def work(p: pathlib.Path) -> str:
        time.sleep(0.18)
        return p.name

    start = time.perf_counter()
    results = list(pquery(from_=str(tmp_path)).map_parallel(work, workers=1))
    series_time = time.perf_counter() - start

    assert len(results) == 4, "expected 4 results"
    assert series_time >= 4 * 0.15, "expected series timing"


def test_multi_worker_speedup(tmp_path: pathlib.Path) -> None:
    """Confirm multi-worker execution is faster than serial."""
    _make_files(tmp_path, 4)

    def work(p: pathlib.Path) -> str:
        time.sleep(0.18)
        return p.name

    start = time.perf_counter()
    list(pquery(from_=str(tmp_path)).map_parallel(work, workers=1))
    series_time = time.perf_counter() - start

    start = time.perf_counter()
    list(pquery(from_=str(tmp_path)).map_parallel(work, workers=4))
    parallel_time = time.perf_counter() - start

    assert parallel_time > 0, "parallel_time should be positive"
    assert series_time / parallel_time >= 1.5, "expected measurable speedup"


@pytest.mark.parametrize("policy", ["continue", "collect"])
def test_exception_policy_continue_collect(tmp_path: pathlib.Path, policy: str) -> None:
    """When one file raises, policy records failure and continues."""
    _make_files(tmp_path, 6)

    def work(p: pathlib.Path) -> str:
        if p.name.endswith("file_2.txt"):
            raise ValueError("boom")
        return p.name

    results = list(
        pquery(from_=str(tmp_path)).map_parallel(work, workers=2, exception_policy=policy)
    )

    failures = [r for r in results if not r.success]
    successes = [r for r in results if r.success]

    assert len(failures) == 1, "expected exactly one failure"
    assert isinstance(failures[0].exception, ValueError), "expected ValueError"
    assert len(successes) == 5, "expected 5 successes"


def test_exception_policy_exit(tmp_path: pathlib.Path) -> None:
    """Using 'exit' should stop soon after a failure; some successes expected."""
    _make_files(tmp_path, 12)

    def work(p: pathlib.Path) -> str:
        if p.name.endswith("file_5.txt"):
            raise RuntimeError("stopnow")
        time.sleep(0.02)
        return p.name

    results = list(
        pquery(from_=str(tmp_path)).map_parallel(work, workers=3, exception_policy="exit")
    )

    failures = [r for r in results if not r.success]
    successes = [r for r in results if r.success]

    assert len(failures) >= 1, "expected at least one failure"
    assert any(isinstance(r.exception, RuntimeError) for r in failures), "expected RuntimeError in failures"
    assert len(successes) >= 1, "expected some successes before exit"
    assert len(results) < 12, "expected fewer than total files due to exit"
