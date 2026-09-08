# reversi/test/paths.py
Test-path helpers: the single home of the workspace-root-anchored paths
the unit tests use. `WORKSPACE_ROOT` is derived ONCE here, keyed on the
workspace marker (`pyproject.toml`) instead of a `parents[N]` level
count — the D-085 unification (Roberto's choice "A" of the design
discussion), which replaced each D-065 test file's own
`Path(__file__).resolve().parents[3]` derivation.
> State: D-085 · aef6188 · 2026-08-31 · suite 3/0/0 (via
  test_paths, no DB)

## API

| name | contract |
|---|---|
| `WORKSPACE_ROOT` (L51) | The workspace root: the first ancestor of this file's directory containing `pyproject.toml` (the marker-based derivation; `RuntimeError` if not found, L43) |
| `CUSTOM_TMP_BASE` (L56) | `WORKSPACE_ROOT / "build" / "tmp"` — the shared test-artifact base of the D-065 house rule (unit tests write files ONLY under `<workspace-root>/build/tmp`) |

`__all__` (L31) = [WORKSPACE_ROOT, CUSTOM_TMP_BASE]. The derivation
helper `_workspace_root()` (L34) is private. No public functions,
hence no `@validate_call` decorators (house convention: public
functions/factories only).

## Architecture

56 lines.

- L34-43 `_workspace_root()`: walks up from this file's own directory
  (L37-39) until the marker is found (L41); raises `RuntimeError`
  (L43) otherwise.
- L47-51 the marker comment + the `WORKSPACE_ROOT` module-level
  derivation; L53-56 `CUSTOM_TMP_BASE`.

The test files import the constants instead of recomputing them:
`test_cache_manager.py`, `test_logistic_model.py` (CUSTOM_TMP_BASE);
`test_lm_worker_config/positions/features/indexes.py` (both — the
JSON fixture is anchored to the same root:
`str(WORKSPACE_ROOT / "src" / "reversi" / "test" / "data" /
"rlm_00.json")`); `test_regab.py` (both — the one remaining
CWD-relative `mkdtemp(dir='./build/tmp')` re-anchored +
`load_dotenv(WORKSPACE_ROOT / ".env")`).

## Verified invariants

Pinned by the `test_paths` suite (3/0/0, see test_paths.md):

- `WORKSPACE_ROOT` is absolute and holds `pyproject.toml`
  (`test_workspace_root_holds_the_marker`).
- `WORKSPACE_ROOT / "src" / "twolm" / "test" / "paths.py"` exists —
  the root is the ancestor of the test package, pinning the
  `src/twolm/test/` layout (`test_workspace_root_is_ancestor_of_this_file`).
- `CUSTOM_TMP_BASE == WORKSPACE_ROOT / "build" / "tmp"`, absolute
  (`test_custom_tmp_base_is_under_the_root`).

## Open issues

None.

## Conventions

- The marker is `pyproject.toml` (present at the root since D-011).
  `.git` and `.env` would work too but are weaker (VCS metadata /
  local file).
- `build/` is gitignored; `build/tmp` is created by the tests'
  `setUpClass` (`mkdir(parents=True, exist_ok=True)`).
- The module is `paths.py` (not `test_paths.py`) so `unittest
  discover -p 'test_*.py'` never loads it as a test module; it has a
  dedicated test module, `test_paths.py`.
- Per-test semantics unchanged (D-065): the base dir is shared,
  created once per test class; each test gets its own fresh
  `tempfile.TemporaryDirectory(dir=CUSTOM_TMP_BASE)` sub-directory,
  removed in its (defensive) tearDown.

## Integration

- Every D-065 test file that writes artifacts or reads fixtures
  imports from this module — the single point of the path
  derivation (a rename surfaces in exactly one place).
