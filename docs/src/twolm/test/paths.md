# `src/twolm/test/paths.py`

Test-path helpers: the single home of the workspace-root-anchored paths the
unit tests use. Introduced by D-085 (session 23, 2026-08-31).

## Purpose

Before D-085, each D-065 test file recomputed the workspace root from its own
location (`Path(__file__).resolve().parents[3]`) and anchored `build/tmp` to
it, while the JSON fixture paths and the `.env` file were anchored to the
CWD — two conventions living in the same `setUp`. D-085 (Roberto's choice,
solution "A" of the design discussion) moved the derivation to this module:

- **`WORKSPACE_ROOT`** — the workspace root, derived ONCE here, keyed on the
  workspace marker (`pyproject.toml`) instead of a level count. The walk-up
  starts from this file's own directory and returns the first ancestor that
  contains `pyproject.toml`; it raises `RuntimeError` if the marker is not
  found. Being marker-based (not `parents[N]`-based), the derivation survives
  file moves.
- **`CUSTOM_TMP_BASE`** — `WORKSPACE_ROOT / "build" / "tmp"`, the shared
  test-artifact base of the D-065 house rule (unit tests write files ONLY
  under `<workspace-root>/build/tmp` and clean them up afterwards).

The test files import the constants instead of recomputing them:

- `test_cache_manager.py`, `test_logistic_model.py`: `CUSTOM_TMP_BASE`.
- `test_lm_worker_config/positions/features/indexes.py`: `CUSTOM_TMP_BASE,
  WORKSPACE_ROOT` (the JSON fixture is now anchored to the same root:
  `str(WORKSPACE_ROOT / "src" / "twolm" / "test" / "data" / "rlm_00.json")` —
  the D-085 unification Roberto asked for).
- `test_regab.py`: `CUSTOM_TMP_BASE` (the one remaining CWD-relative
  `mkdtemp(dir='./build/tmp')` re-anchored) and `WORKSPACE_ROOT`
  (`load_dotenv(WORKSPACE_ROOT / ".env")` — the `.env` is now loaded from the
  explicit root path instead of the search starting from the calling file).

## API

`__all__ = ['WORKSPACE_ROOT', 'CUSTOM_TMP_BASE']`. The derivation helper
`_workspace_root()` is private. No public functions, hence no
`@validate_call` decorators (house convention: public functions/factories
only).

## Verified invariants (test_paths, 3/0/0)

- `WORKSPACE_ROOT` is absolute and holds `pyproject.toml`.
- `WORKSPACE_ROOT / "src" / "twolm" / "test" / "paths.py"` exists (the root is
  the ancestor of the test package — pins the `src/twolm/test/` layout).
- `CUSTOM_TMP_BASE == WORKSPACE_ROOT / "build" / "tmp"`, absolute.

## Conventions

- The marker is `pyproject.toml` (present at the root since D-011). `.git`
  and `.env` would work too but are weaker (VCS metadata / local file).
- `build/` is gitignored; `build/tmp` is created by the tests' `setUpClass`
  as before (`mkdir(parents=True, exist_ok=True)`).
- The module name is `paths.py` (not `test_paths.py`) so `unittest discover
  -p 'test_*.py'` never loads it as a test module; it has a dedicated test
  module, `test_paths.py`.
- Per-test semantics unchanged (D-065): the base dir is shared and created
  once per test class; each test gets its own fresh
  `tempfile.TemporaryDirectory(dir=CUSTOM_TMP_BASE)` sub-directory and removes
  it in its (defensive) tearDown — per-test isolation, per-test cleanup.
