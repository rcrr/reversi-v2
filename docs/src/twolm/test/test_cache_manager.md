# test_cache_manager.md — analysis

Date: 2026-08-30. One test file: `test_cache_manager.py` (21 tests,
2 classes + 1 base), added with the module (commit a0cd31f).
**Analysis session 20; fix campaign batch 1 applied (D-071):
T1/T2/T3/T4/T5/T7 fixed with 8 new tests + new asserts in the 6
existing pipeline tests — suite 13 → 21. Batch 2 applied (D-072):
T6 fixed (artifact base anchored to the workspace root), helper
suite rebuilt around the binio API (2 direct-compute tests dropped —
binio's suite owns them; T3 pin restated; R3, legacy-compat,
malformed/undecodable pins added), pipeline set-ups switched to
`write_sha3_256_sidecar` — suite 21 → 21. All OPEN items closed;
T8 report-only. Module CLOSED.**

Suite: **21/0/0 GREEN, no PERF gates.** Fast (~0.15s).

## How to run

```
$ python -m unittest twolm.test.test_cache_manager
```

## Coverage by area

### `TestChecksumHelpers` (8 tests)

- `test_binio_sidecar_verifies` (R3, D-072): a sidecar written by
  binio's `write_sha3_256_sidecar` verifies True through the
  `_verify_checksum` wrapper — both modules now share one sidecar
  format and one verifier (V3).
- `test_legacy_bare_hex_sidecar_still_verifies` (D-072 compat): a
  pre-D-072 bare-hexdigest sidecar still verifies True — binio's
  first-token parser accepts it; zero cache invalidation.
- `test_verify_checksum_fails_if_sidecar_missing`: False without a
  sidecar (FileNotFoundError → False) (V3a).
- `test_verify_checksum_fails_if_sidecar_mismatched`: False with a
  well-formed but wrong digest (`"0" * 64`) (V3c).
- `test_verify_checksum_fails_if_sidecar_malformed` (D-072): False
  for a non-hex first token (BinaryFormatError) and for an
  undecodable sidecar (UnicodeDecodeError) — the wrapper maps both
  to False, never raises (V3).
- `test_delete_cache_files_removes_both`: data + sidecar gone after
  deletion (sidecar written via binio, D-072) (V4).
- `test_delete_cache_files_does_not_raise_if_missing`: double delete
  no-raise (V4 idempotency).
- `test_sidecar_content_is_binio_format` (T3, restated D-072): the
  sidecar holds exactly binio's `sha3_256sum` line
  `<hexdigest>  <basename>\n` (V15, restated).
- **Coverage**: the 2 remaining low-level helpers + the wrapper's
  exception mapping, happy + fail paths + the sidecar content
  format. Direct SHA3-256 computation is owned by the binio suite
  (the 2 old direct-compute helper tests were dropped in D-072).

### `TestCacheManagerPipeline` (13 tests)

- `test_step0_not_allowed_forces_computation`: `is_allowed=False`
  with a pre-existing cache file → compute once, store once with
  `(DUMMY_DATA, cache_path)`, load not called, `cache_hit=False`,
  3rd element `None` (T1), INFO "Cache not allowed by configuration.
  Forcing computation." pinned (V5a/V5c). D-071 (T4, R1 ruling): the
  cache file is re-written anyway — data + valid sidecar asserted on
  disk (V5b).
- `test_step1_missing_file_forces_computation`: no file → compute +
  store, load not called, `cache_hit=False`, 3rd element `None` (T1)
  (V6).
- `test_step2_checksum_mismatch_forces_recomputation`: data +
  wrong sidecar → compute + store, load not called, 3rd element
  `None` (T1), WARN "Checksum validation failed for '<path>' (sidecar
  missing or mismatched). Deleting cache and recomputing." pinned
  (V7, post D-071/M3); T7: the stale bytes are replaced and the new
  sidecar verifies.
- `test_step3a_load_exception_forces_recomputation`: valid checksum,
  `load_fn` raises IOError → compute + store, 3rd element `None`
  (T1), ERROR "Failed to load or validate cache file '<path>': Disk
  read error. Recomputing." pinned (V8, post D-071); T7: on-disk
  replacement + valid sidecar.
- `test_step3b_validation_fails_forces_recomputation`: valid checksum
  + load, `validate_fn` False → compute + store, validate called once
  with the loaded data, 3rd element `None` (T1), T7 on-disk
  (V9).
- `test_success_path_returns_cached_data`: valid checksum + load +
  validate → `cache_hit=True`, the loaded payload returned (identity),
  3rd element `None` (T1), load called once with the path, validate
  once with the payload, compute + store NOT called, INFO "Cache
  successfully loaded and validated from '<path>'." pinned (V10).
- `test_compute_path_returns_data_checksum` (T2, D-071): data WITH a
  `compute_sha3_256_hash` method → the method's digest is the 3rd
  return element on the compute path (V11a).
- `test_load_path_returns_data_checksum` (T2, D-071): valid cache,
  loaded data WITH the method → its digest is the 3rd element on the
  load path (V11b).
- `test_checksum_method_missing_returns_none` (T2 + T1, D-071):
  plain dict data (no method) → `None` on the compute path (V12).
- `test_checksum_attribute_not_callable_returns_none` (T2, D-071):
  a `compute_sha3_256_hash` attribute set to a non-callable → `None`,
  no exception, success path intact (V12).
- `test_load_path_checksum_method_raises_recomputes` (T2, D-071):
  the data checksum method RAISING on the load path is caught by the
  step-3 try/except → delete + recompute, ERROR log carries the
  exception text, 3rd element `None`, on-disk replacement (V13).
- `test_validate_exception_forces_recomputation` (R2, D-071): a
  `validate_fn` that RAISES is now caught like a load failure →
  delete + recompute, ERROR log carries the exception text, on-disk
  replacement (V16, post D-071).
- `test_step2_missing_sidecar_forces_recomputation` (T5, D-071):
  data file present but NO sidecar → the step-2 branch fires (same
  WARN message as the mismatch case), compute + store, load not
  called (V7 missing-sidecar variant).
- **Coverage**: all 4 pipeline steps + the success path, the
  cache_hit flag, the key log messages (post D-071 wordings), the
  full duck-typed data-checksum feature, the 3rd return element on
  every path, and the on-disk effects of step 0 and every
  invalidation.

## Test defects (T1-T8)

Status: T1-T5 + T7 FIXED in the D-071 campaign (Roberto's
approvals); T6 FIXED in the D-072 campaign (Roberto's OK); T3 pin
restated in D-072 with the format flip; T8 report-only. All
fixable items closed.

### T1 — The 3rd return element (data checksum) was never asserted (P1) — FIXED (D-071)
Every pipeline test unpacked `checksum` and never checked it. Now:
`assertIsNone(checksum)` ("plain dict data has no
compute_sha3_256_hash method") in all 6 existing pipeline tests, and
the real digest values are asserted in the T2 tests.

### T2 — The duck-typed `compute_sha3_256_hash` path was untested (P0) — FIXED (D-071)
The module's headline feature was invisible to the suite. Now 5 new
`TestCacheManagerPipeline` tests + 2 helper classes
(`DataWithChecksum`, `DataWithBrokenChecksum`): compute path returns
the data's own digest (V11a); load path returns it (V11b); missing
method → `None`; non-callable attribute → `None`, no exception;
raising method on the load path → caught by the step-3 try/except,
delete + recompute, ERROR log carries the exception text (V13).
Plus `test_validate_exception_forces_recomputation` pinning the
D-071/R2 behaviour for a raising validator (V16).

### T3 — Sidecar content format not pinned (P2) — FIXED (D-071), restated (D-072)
Originally `test_sidecar_content_is_bare_hexdigest`: the sidecar
holds exactly the 64-char hex digest (V15, pre-D-072 format). D-072
flipped the format: the pin is now
`test_sidecar_content_is_binio_format` — the sidecar holds exactly
binio's `sha3_256sum` line `<hexdigest>  <basename>\n` (V15,
restated).

### T4 — Step 0 "still writes the cache" not pinned (P1, after R1) — FIXED (D-071)
R1 ruled intentional by Roberto: the result is ALWAYS transcribed to
the cache file. `test_step0` now asserts the on-disk effect: data
file + sidecar exist, the sidecar verifies, and the content is the
recomputed payload (V5b).

### T5 — Step 2 missing-sidecar variant untested at pipeline level (P2) — FIXED (D-071)
New `test_step2_missing_sidecar_forces_recomputation`: data present,
no sidecar → same WARN message as the mismatch case, compute +
store, load not called (V7).

### T6 — Artifacts under CWD-relative `./build/tmp` (P1, house rule) — FIXED (D-072)
`CUSTOM_TMP_BASE = Path("./build/tmp")` was relative to the CWD, not
the workspace root; the D-065 house rule (test artifacts ONLY under
`workspace_root/build/tmp`) is applied in test_state_machine.py via
`Path(__file__).resolve().parents[3] / "build" / "tmp"`. Running the
suite from any other CWD would create `build/tmp` wherever it is
invoked (and would NOT find the existing tree). Roberto approved the
proposed fix ("T6: OK"); D-072 applied it: `CUSTOM_TMP_BASE` is now
anchored to the workspace root via `__file__`, same idiom as
test_state_machine.py. No source impact.

### T7 — No on-disk assertion after recompute (P2) — FIXED (D-071)
`test_step2`, `test_step3a`, `test_step3b` (and the two new T2/R2
recompute tests) now assert the file: the recompute replaced the
stale bytes (content == `str(DUMMY_DATA)`) and left a VALID sidecar
(`_verify_checksum` True). A store_fn that wrote nothing would no
longer pass.

### T8 — Header grammar (cosmetic, report-only) — OPEN, report-only
L30: "How to use the unit tests cache_manager module." — same
pattern as the test_board/test_feature header nits; the
'Activate the environment.' line itself is fine. Left as-is per the
report-only pattern.

## Observations

- **No PERF gates**: 21 tests in 0.15s; `tempfile.TemporaryDirectory`
  under build/tmp with `tearDown` cleanup is the right idiom here.
- **`DUMMY_DATA` is shared module state** (a dict literal reused by
  every mock): safe today because no test mutates it, but a per-test
  `copy.deepcopy` would be cheaper insurance if T2 adds data classes.
- **`_fake_store` writes `str(data)` to disk**: the pipeline tests
  never actually load what they stored (load is mocked to return
  `DUMMY_DATA`); the step-3 tests write "valid data" by hand +
  `write_sha3_256_sidecar` (D-072), so load-vs-store round-trip
  consistency is NOT
  exercised end-to-end. Acceptable for a utility whose load/store are
  injected by the domain — but worth one note: an end-to-end
  (store then load the same object) test would pin T7 at the same
  time.
- **`Relevance` import is load-bearing** (the `assert_any_call`
  pins).

## Completeness verdict

**Pipeline coverage is now complete** (post D-071): all 4 steps +
success with flags and (updated) log messages, the delete-and-
recompute invariant asserted both through the call pattern AND on
disk (T7), the full duck-typed data-checksum feature (T2), the 3rd
return element on every path (T1), the step-0 warm-cache effect
(T4/R1) and the missing-sidecar variant (T5).

**Verdict**: 21/0/0 GREEN. Campaign batch 1 (D-071) closed T1-T5 +
T7; the module's distinctive data-checksum feature is now pinned.
Campaign batch 2 (D-072) closed T6, restated the T3 pin for the
binio format, and added the R3 / legacy-compat / malformed wrapper
pins. Remaining: T8 (report-only). Module CLOSED.

## Appendix: class map (2026-08-30, post D-072; file 603 lines)

| Line | Class / item | Tests |
|---|---|---|
| 71 | `DUMMY_DATA` | — |
| 75 | `CUSTOM_TMP_BASE` (workspace-root anchored — T6 FIXED) | — |
| 78 | `DataWithChecksum` (D-071 helper) | — |
| 89 | `DataWithBrokenChecksum` (D-071 helper) | — |
| 96 | `checksum_path_for` (D-071 helper) | — |
| 101 | `BaseCacheTestCase` | — |
| 118 | `TestChecksumHelpers` | 8 |
| 126 | `test_binio_sidecar_verifies` (R3, D-072) | — |
| 133 | `test_legacy_bare_hex_sidecar_still_verifies` (D-072 compat) | — |
| 154 | `test_verify_checksum_fails_if_sidecar_malformed` (D-072) | — |
| 185 | `test_sidecar_content_is_binio_format` (T3, D-072) | — |
| 195 | `TestCacheManagerPipeline` | 13 |
| 418 | `test_compute_path_returns_data_checksum` (T2) | — |
| 441 | `test_load_path_returns_data_checksum` (T2) | — |
| 466 | `test_checksum_method_missing_returns_none` (T2/T1) | — |
| 487 | `test_checksum_attribute_not_callable_returns_none` (T2) | — |
| 512 | `test_load_path_checksum_method_raises_recomputes` (T2/V13) | — |
| 541 | `test_validate_exception_forces_recomputation` (R2) | — |
| 572 | `test_step2_missing_sidecar_forces_recomputation` (T5) | — |
| 602 | `unittest.main` guard | — |
