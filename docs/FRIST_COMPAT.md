Frist compatibility notes

Scope

- This note records the `frist` API and semantics relevant to `tpath` compatibility (checked against `hucker/frist` main branch and PyPI release).

Checked sources

- GitHub: `src/frist/_cal_policy.py` (main branch)
- PyPI: `https://pypi.org/project/frist/` (current latest: 0.15.0)

Latest published version

- PyPI latest: `frist==0.15.0` (released recently)

Calendar semantics

- `frist` uses half-open calendar intervals everywhere: start is inclusive, end is exclusive.
  - Example: `Cal(...).day.in_(-7, 1)` covers the 7 days before the reference **and** the reference day (use `end=1` to include ref day).
  - This affects `minute.in_`, `hour.in_`, `day.in_`, `week.in_`, `month.in_`, `qtr.in_`, `year.in_`, and policy-aware `Biz.work_day` helpers.

`BizPolicy` constructor (exact signature)

- From `src/frist/_cal_policy.py` (main branch / v0.15.0):

dataclass BizPolicy

- `fiscal_year_start_month: int = 1`
- `workdays: list[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])`
- `start_of_business: datetime.time = datetime.time(9, 0)`
- `end_of_business: datetime.time = datetime.time(17, 0)`
- `holidays: set[str] = field(default_factory=set)`

Important parameter notes

- Use the exact field names above when constructing a `BizPolicy` instance.
- Example: `BizPolicy(fiscal_year_start_month=4, workdays=[0,1,2,3,4], holidays={"2026-01-01"})`
- `workdays` must be a `list[int]` (Monday=0 .. Sunday=6). Passing a `set` will raise a runtime TypeError in the current implementation.
- `holidays` must be a `set[str]` of ISO date strings (`YYYY-MM-DD`).
- `fiscal_year_start_month` must be an `int` 1..12.

Why this matters for `tpath`

- Some examples in docs/readme (and earlier commits) use alternate names like `fy_start_month`, `fy_start_month`, `work_hours`, or pass `workdays` as a `set`. Those examples may not match the actual dataclass signature in `0.15.0`.
- Tests in `tpath` that previously assumed inclusive end bounds (inclusive semantics) need to be updated to match the half-open intervals used by `frist`.

Recommended actions for `tpath`

- Pin `frist` in `pyproject.toml` to the tested version to avoid API surprises. Example:

  [tool.poetry.dependencies]
  frist = "==0.15.0"

  or for `pip` requirements:
  frist==0.15.0

  Then regenerate your lockfile (`uv lock` or the lock tool you use) and verify CI.

- Update any `BizPolicy(...)` calls to use the exact field names shown above and pass `workdays` as a `list`.
- Audit tests that check calendar ranges and adjust to half-open intervals (i.e., when wanting to include the reference day use `end=1`).

Quick examples

- Create a policy:

  ```py
  from frist import BizPolicy
  policy = BizPolicy(
      fiscal_year_start_month=4,
      workdays=[0,1,2,3,4],
      start_of_business=datetime.time(9,0),
      end_of_business=datetime.time(17,0),
      holidays={"2026-01-01"},
  )
  ```

- Calendar window including the reference day:

  ```py
  from frist import Cal
  c = Cal(target_dt=my_dt, ref_dt=ref_dt)
  # include ref date in day-range check
  c.in_days(-7, 1)
  ```

Notes & caveats

- The `frist` README or examples may contain a small number of mismatching example names; rely on the source (`src/frist/_cal_policy.py`) for the definitive API in the published version.
- If you find code that uses `workdays` as a `set` or constructor kwargs like `fy_start_month`, update them to match the code above or pin to a version that supports alternate names (if any existed historically).

If you want, I can:

- Update `pyproject.toml` in this repo to pin `frist==0.15.0` and regenerate the lockfile.
- Search the `tpath` codebase for `BizPolicy(`, `fy_start_month`, `fy_start`, or `workdays=` occurrences and update usages/examples.

(Generated on 2025-11-22)
