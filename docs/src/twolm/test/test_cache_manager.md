# test_cache_manager.md — analysis

Date: 2026-08-30. One test file: `test_cache_manager.py` (13 tests,
2 classes + 1 base), added with the module (commit a0cd31f).
**Analysis session 20 — no test changes yet; T1-T8 documented,
priorities proposed, campaign pending Roberto's approvals.**

Suite: **13/0/0 GREEN, no PERF gates.** Fast (~0.025s).

## How to run

```
$ python -m unittest twolm.test.test_cache_manager
```

## Coverage by area

### `TestChecksumHelpers` (7 tests)

- `test_compute_checksum_returns_valid_sha3_256`: 64-char lowercase
  hex — pins the format shape (V1a/V1b), not the value.
- `test_compute_checksum_is_deterministic`: two calls equal (V1).
- `test_save_and_verify_checksum_success`: `_save_checksum` +
  `_verify_checksum` round-trip True (V3b).
- `test_verify_checksum_fails_if_sidecar_missing`: False without
  sidecar (V3a).
- `test_verify_checksum_fails_if_sidecar_corrupted`: False with a
  `"0" * 64` sidecar (V3d).
- `test_delete_cache_files_removes_both`: data + sidecar gone after
  deletion (V4).
- `test_delete_cache_files_does_not_raise_if_missing`: double delete
  no-raise (V4 idempotency).
- **Coverage**: the 4 low-level helpers, happy + fail paths. What is
  NOT pinned: the sidecar content format (T3), the data-file content
  after a re-store (T7).

### `TestCacheManagerPipeline` (6 tests)

- `test_step0_not_allowed_forces_computation`: `is_allowed=False`
  with a pre-existing cache file → compute once, store once with
  `(DUMMY_DATA, cache_path)`, load not called, `cache_hit=False`;
  INFO "Cache not allowed by configuration. Forcing computation."
  pinned (V5a/V5c). What is NOT pinned: that the cache file is
  re-written anyway (T4, depends on R1), and that the 3rd return
  element is `None` (T1).
- `test_step1_missing_file_forces_computation`: no file → compute +
  store, load not called, `cache_hit=False` (V6).
- `test_step2_checksum_mismatch_forces_recomputation`: data +
  wrong sidecar → compute + store, load not called, WARN "Checksum
  mismatch for '<path>'. Deleting cache and recomputing." pinned (V7).
  Only the MISMATCH variant: the missing-sidecar variant is never
  exercised at pipeline level (T5).
- `test_step3a_load_exception_forces_recomputation`: valid checksum,
  `load_fn` raises IOError → compute + store, ERROR "Failed to load
  cache file '<path>': Disk read error. Recomputing." pinned (V8).
- `test_step3b_validation_fails_forces_recomputation`: valid checksum
  + load, `validate_fn` False → compute + store, validate called once
  with the loaded data (V9).
- `test_success_path_returns_cached_data`: valid checksum + load +
  validate → `cache_hit=True`, the loaded payload returned, load
  called once with the path, validate once with the payload, compute
  + store NOT called, INFO "Cache successfully loaded and validated
  from '<path>'." pinned (V10).
- **Coverage**: all 4 pipeline steps + the success path, with the
  cache_hit flag and the key log messages. What is NOT covered at
  all: the duck-typed data-checksum feature (T2, P0) and the 3rd
  return element (T1).

## Test defects (T1-T8)

Status: all OPEN — campaign pending Roberto's approvals.

### T1 — The 3rd return element (data checksum) is never asserted (P1)
Every pipeline test unpacks `checksum` and never checks it. The
documented contract (`str | None`, the data object's own checksum)
is unpinned: it is `None` for the plain `DUMMY_DATA` dict on every
path, and that is exactly what should be asserted.

### T2 — The duck-typed `compute_sha3_256_hash` path is untested (P0)
The module's headline feature (docstring L141-143) is invisible to
the suite: no test data object has a `compute_sha3_256_hash`
method. Unpinned: the value flows to the 3rd return element on BOTH
the compute and the load paths (V11); a non-callable attribute or a
missing one yields `None` (V12); a raising method on the LOAD path
is caught by the step-3 try/except → recompute (V13). This is the
only load-bearing branch of the module with zero coverage.

### T3 — Sidecar content format not pinned (P2)
Only the round-trip through `_verify_checksum` is tested; the actual
on-disk format (bare 64-hex, no trailing newline, V15) is never
asserted. Pin it so the format cannot drift (and so the R3 decision
has a pin to rewrite).

### T4 — Step 0 "still writes the cache" not pinned (P1, after R1)
`test_step0` asserts the call pattern but not the on-disk effect:
the data file + sidecar are created even with `is_allowed=False`
(V5b). Whichever way R1 is ruled, this behaviour must be pinned
(rewritten if the ruling is "compute only").

### T5 — Step 2 missing-sidecar variant untested at pipeline level (P2)
The step-2 branch fires on BOTH mismatch and missing sidecar; the
suite covers only the mismatch. Add the missing-sidecar case (same
WARN message, V7/V15c adjacency).

### T6 — Artifacts under CWD-relative `./build/tmp` (P1, house rule)
`CUSTOM_TMP_BASE = Path("./build/tmp")` (L75) is relative to the
CWD, not the workspace root. The D-065 house rule (test artifacts
ONLY under `workspace_root/build/tmp`) is applied in
test_state_machine.py via `Path(__file__).resolve().parents[3] /
"build" / "tmp"`. Running the suite from any other CWD would create
`build/tmp` wherever it is invoked (and would NOT find the existing
tree). Fix: derive the root from `__file__` like the other suite.

### T7 — No on-disk assertion after recompute (P2)
The three "forces recomputation" tests check the return value and
the calls, but never the file: that the recompute actually replaced
the corrupt/stale bytes and left a VALID sidecar (V7b/V8b/V9b) is
unpinned. A store_fn that writes nothing would pass today.

### T8 — Header grammar (cosmetic, report-only)
L30: "How to use the unit tests cache_manager module." — same
pattern as the test_board/test_feature header nits; the
'Activate the environment.' line itself is fine. Report-only unless
Roberto wants it swept in the campaign.

## Observations

- **No PERF gates**: 13 tests in 0.025s; `tempfile.TemporaryDirectory`
  under build/tmp with `tearDown` cleanup is the right idiom here.
- **`DUMMY_DATA` is shared module state** (a dict literal reused by
  every mock): safe today because no test mutates it, but a per-test
  `copy.deepcopy` would be cheaper insurance if T2 adds data classes.
- **`_fake_store` writes `str(data)` to disk**: the pipeline tests
  never actually load what they stored (load is mocked to return
  `DUMMY_DATA`); the step-3 tests write "valid data" by hand +
  `_save_checksum`, so load-vs-store round-trip consistency is NOT
  exercised end-to-end. Acceptable for a utility whose load/store are
  injected by the domain — but worth one note: an end-to-end
  (store then load the same object) test would pin T7 at the same
  time.
- **`Relevance` import is load-bearing** (the `assert_any_call`
  pins).

## Completeness verdict

**Pipeline coverage is good** (all 4 steps + success, flags and log
messages pinned; the delete-and-recompute invariant is consistently
asserted through the call pattern). **The gap is the data-checksum
feature** — the module's distinctive addition over a plain
load-or-compute (T2, P0) — plus the unpinned 3rd return element (T1)
and the D-065 artifact-path deviation (T6).

**Verdict**: 13/0/0 GREEN as-is. Proposed campaign: P0 = T2 (4-5
tests: with-method compute path, with-method load path, no-method →
None, non-callable attr, raising method on load); P1 = T1 + T4 (after
the R1 ruling) + T6; P2 = T3 + T5 + T7 (+ optional end-to-end store→
load) + T8 if Roberto wants it. Source-side items (R1-R4, M1-M3)
are separate Roberto's-call items in the module doc.

## Appendix: class map (2026-08-30, at analysis)

| Line | Class / item | Tests |
|---|---|---|
| 72 | `DUMMY_DATA` | — |
| 75 | `CUSTOM_TMP_BASE` (CWD-relative — T6) | — |
| 78 | `BaseCacheTestCase` | — |
| 95 | `TestChecksumHelpers` | 7 |
| 154 | `TestCacheManagerPipeline` | 6 |
| 344 | `unittest.main` guard | — |
