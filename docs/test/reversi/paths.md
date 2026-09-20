# test/reversi/paths.py
Test-path helpers: the single home of the workspace-root-anchored paths the unit tests use. `WORKSPACE_ROOT` is derived
ONCE here, keyed on the workspace marker (`pyproject.toml`) instead of a `parents[N]` level count.

## API

| name | contract |
|---|---|
| `WORKSPACE_ROOT` | The workspace root: the first ancestor of this file's directory containing `pyproject.toml` (the marker-based derivation; `RuntimeError` if not found) |
| `CUSTOM_TMP_BASE` | `WORKSPACE_ROOT / "build" / "tmp"` — the shared test-artifact base of the house rule (unit tests write files ONLY under `<workspace-root>/build/tmp`) |

`__all__` = [WORKSPACE_ROOT, CUSTOM_TMP_BASE]. The derivation helper `_workspace_root()` is private. No public
functions, hence no `@validate_call` decorators (house convention: public functions/factories only).

## Architecture

56 lines.

- `_workspace_root()`: walks up from this file's own directory until the marker is found; raises `RuntimeError`
  otherwise.
- the marker comment + the `WORKSPACE_ROOT` module-level derivation; `CUSTOM_TMP_BASE`.

The test files import the constants instead of recomputing them: `test_cache_manager.py`, `test_logistic_model.py` (both
constants); `test_wrk_config/positions/features/indexes.py` (both — the JSON fixture is anchored to the same root:
`str(WORKSPACE_ROOT / "src" / "reversi" / "test" / "data" / "rlm_00.json")`); `test_regab.py`
(`mkdtemp(dir=CUSTOM_TMP_BASE)` + `load_dotenv(WORKSPACE_ROOT / ".env")`).

## Verified invariants

Pinned by the `test_paths` suite (3/0/0, see test_paths.md):

- `WORKSPACE_ROOT` is absolute and holds `pyproject.toml` (`test_workspace_root_holds_the_marker`).
- `WORKSPACE_ROOT / "src" / "reversi" / "test" / "paths.py"` exists — the root is the ancestor of the test package,
  pinning the `test/reversi/` layout (`test_workspace_root_is_ancestor_of_this_file`).
- `CUSTOM_TMP_BASE == WORKSPACE_ROOT / "build" / "tmp"`, absolute (`test_custom_tmp_base_is_under_the_root`).

## Open issues

None.

## Conventions

- The marker is `pyproject.toml`. `.git` and `.env` would work too but are weaker (VCS metadata / local file).
- `build/` is gitignored; `build/tmp` is created by the tests' `setUpClass` (`mkdir(parents=True, exist_ok=True)`).
- The module is `paths.py` (not `test_paths.py`) so `unittest discover -p 'test_*.py'` never loads it as a test module;
  it has a dedicated test module, `test_paths.py`.
- Per-test semantics: the base dir is shared, created once per test class; each test gets its own fresh
  `tempfile.TemporaryDirectory(dir=CUSTOM_TMP_BASE)` sub-directory, removed in its (defensive) tearDown.

## Integration

- Most test files that write artifacts or read fixtures import from this module — the single point of the path
  derivation (a rename surfaces in exactly one place). Exceptions: `test_state_machine.py` carries its own `parents[3]`
  derivation, and the binio usage tests use a bare `mkdtemp`.
