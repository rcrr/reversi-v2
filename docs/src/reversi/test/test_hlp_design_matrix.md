# reversi/test/test_hlp_design_matrix.py
The dedicated data-object suite of the hlp_design_matrix module
(created by the D-090 fix campaign, T6 — the DESIGN_MTR level
arrived with only the worker test, this file closes the coverage
gap). 4 classes / 12 tests / no PERF — no DB, no gate: the
compute tests use a handcrafted mock ctx, the IO tests use a REAL
temp dir under the shared `CUSTOM_TMP_BASE` (the D-085 idiom,
followed from day one).
> State: D-090 · 06023cc · 2026-08-31 · suite 12/0/0

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestRLMDesignMatrixCompute` (a `SimpleNamespace` dummy ctx, no DB — 2 features: F0 1 instance / 3 configs, F1 2 instances / 2 configs; `iwmap_feature_offset [0,3,5]` uint32, `iwmap [1,0,0,2,3]` int64, a 4×3 uint32 pindexes matrix) | 2 | `test_compute`: the golden math — `X[i,j] = iwmap[pindexes[i,j] + col_offsets[j]]` with `col_offsets = [0,3,3]` (the feature start offsets repeated per instance) → the 4×3 uint32 matrix `[[1,2,2],[1,3,3],[0,2,3],[0,3,2]]` (the hand-computed values in the comment), shape + dtype + exact-array asserts, the `wmaps_obj_checksum` carry-over. `test_compute_rejects_invalid_pindex`: `iwmap[2] = -1` (a pindex points at an unmapped slot) → the precise "pindexes is referring an invalid value" ValueError (the single guard left by the D-090 R1 merge) |
| `TestRLMDesignMatrixCacheConsistency` | 2 | the 1-field metadata compare — True on matching `wmaps_obj_checksum`; False on a mismatch |
| `TestRLMDesignMatrixIO` (a `TemporaryDirectory` under `CUSTOM_TMP_BASE`, created FIRST, defensive tearDown) | 6 | `test_store_and_load_cycle` (the `wmaps_obj_checksum` + X round-trip, dtype uint32 + exact-array); `test_compute_sha3_256_hash_golden` (the golden below); `test_load_with_valid_sidecar` (the `checksum=True` path with a matching binio sidecar); `test_load_with_mismatched_sidecar` (the last byte of the `.dat` corrupted → the precise "checksum file signature doesn't match" RuntimeError); `test_load_rejects_wrong_description` (a hand-written wrong header → "not a proper" RuntimeError); `test_load_rejects_version_mismatch` (version 2 → "version mismatch" RuntimeError) |
| `TestRLMDesignMatrixInit` | 2 | `test_init_accepts_valid_arrays` (the valid 2-field object); `test_init_fails_with_invalid_X_type` (a str for X → the precise pydantic `ValidationError`) |

## Goldens pinned

- The `compute_sha3_256_hash` golden:
  `da86a916e03c76befa6f5df70e6221b0f9a355173e356ea63fef89ea971975
  7b` — sha3_256 over `X.tobytes()` of the small 2×3 uint32 IO
  object (a regression in the hash or in the serialized array
  breaks it).
- The hand-computed X matrix `[[1,2,2],[1,3,3],[0,2,3],[0,3,2]]`;
  the 3 RuntimeError message substrings + the precise
  `ValidationError` + the guard `ValueError`.

## Conventions

- The D-085 paths idiom on the IO tests (real temp dir under the
  shared `CUSTOM_TMP_BASE` + defensive tearDown) — the same
  style as test_hlp_wmaps, which it mirrors (the same 2-feature
  mock layout 1/3 + 2/2, so the X values hand-verify against the
  iwmap in the comment).
- The precise-message pins (no broad `assertRaises(Exception)`).
- The sidecar/error-path tests reuse the exact binio API and the
  exact RuntimeError messages the WMAPS IO tests pin — the four
  cache-manager consumer suites (POSITIONS / INDEXES / WMAPS /
  DESIGN_MTR) stay mutually consistent.

## Integration

- Independent of the pipeline: no model, no DB, no cache file —
  the per-function pin that would catch a future signature change
  to `hlp_design_matrix_*` (the worker test only exercises the
  end-to-end path).
- The LIVE golden (the rlm_01 (10,7) X) lives in
  test_lm_worker_design_matrix.py
  (`TestLMWorkerDesignMatrixExactValues`) — the single source of
  truth after the step-3 class c deletions of the former probe
  D0-D4/D9 tier.
