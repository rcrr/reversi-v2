# reversi/test/test_paths.py
Unit tests for the `reversi.test.paths` workspace-root constants: 1 class / 3 tests, no DB, no gate, no artifacts (pure
path assertions).

## Coverage

| class (line) | tests | what it pins |
|---|---|---|
| `TestPaths` (L51, plain `unittest.TestCase`) | 3 | `test_workspace_root_holds_the_marker` (L54): `WORKSPACE_ROOT` is absolute and holds the `pyproject.toml` marker (the marker-based derivation, not a `parents[N]` level count); `test_workspace_root_is_ancestor_of_this_file` (L59): `WORKSPACE_ROOT / "src" / "reversi" / "test" / "paths.py"` exists — the root is the ancestor of the test package (the `src/reversi/test/` layout); `test_custom_tmp_base_is_under_the_root` (L63): `CUSTOM_TMP_BASE` is exactly `<root>/build/tmp` and absolute |

## Goldens pinned

- No float goldens: the pins are the three path identities above — the marker presence, the `src/reversi/test/paths.py`
  descendant, and the `<root>/build/tmp` equality.

## Conventions

- The module under test is imported as `from reversi.test import paths` and the constants are read as attributes
  (`paths.WORKSPACE_ROOT`, ...) — a future rename surfaces in exactly one place.
- No DB involvement, hence no `SKIP_REGAB_DB` gate and no `build/tmp` artifacts: these tests only assert on the computed
  paths.

## Integration

- Module under test: `paths.md` — the shared path-derivation module of the test suite.
