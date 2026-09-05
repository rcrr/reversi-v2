<!-- ARCHIVED — D-106 step 27 (the docs/ rewrite, 2026-09-04): the PATHS + TEST_PATHS pair (paths.md + this doc) moved out of docs/src/twolm/test/ into the snapshot schema per docs_rules.md §1/§4. This is a frozen historical record: it is never updated. Stale-in-current-context notes: none — the 3-test content is unchanged since D-085. -->

# `src/twolm/test/test_paths.py`

Unit tests for the `twolm.test.paths` workspace-root constants (D-085,
session 23, 2026-08-31). Suite: 3/0/0 GREEN, no DB, no gate, no artifacts
(pure path assertions).

## How to run

Run from the workspace root (the directory containing `.venv` and `src`):

```
source .venv/bin/activate
time python3 -m unittest twolm.test.test_paths
```

## Content (1 class / 3 tests)

`TestPaths`:

- `test_workspace_root_holds_the_marker` — `WORKSPACE_ROOT` is absolute and
  holds the `pyproject.toml` marker (the marker-based derivation, D-085:
  not a `parents[N]` level count).
- `test_workspace_root_is_ancestor_of_this_file` —
  `WORKSPACE_ROOT / "src" / "twolm" / "test" / "paths.py"` exists: pins that
  the root is the ancestor of the test package (the `src/twolm/test/` layout).
- `test_custom_tmp_base_is_under_the_root` — `CUSTOM_TMP_BASE` is exactly
  `<root>/build/tmp` and absolute.

## Notes

- The module under test is imported as `from twolm.test import paths` and the
  constants are read as attributes (`paths.WORKSPACE_ROOT`, ...) — the tests
  pin the module-level constants without importing the names, so a future
  rename surfaces in exactly one place.
- No DB involvement, hence no `SKIP_REGAB_DB` gate and no `build/tmp`
  artifacts: these tests only assert on the computed paths.
