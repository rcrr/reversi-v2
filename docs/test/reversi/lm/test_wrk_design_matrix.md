# test/reversi/lm/test_wrk_design_matrix.py
The suite of the DESIGN_MTR worker — the end-to-end cache round-trip pin for the 8th active level + the rlm_01
golden-content pin (the (10,7) uint32 X literal). 2 classes / 3 tests / no PERF — ALL DB-DEPENDENT (the setUp moves
through WMAPS on a fresh base dir).

## Coverage

| class | what it pins |
|---|---|
| `TestLMWorkerDesignMatrix` (2, rlm_00.json — the 200-record fixture) | shared setUp: the `SKIP_REGAB_DB` gate FIRST → stdout patch → `TemporaryDirectory` under `CUSTOM_TMP_BASE` created FIRST → the `WORKSPACE_ROOT`-anchored json_config → a fresh `LogisticModel` (`Verbosity.HIGH`, the house) → step 0 / CREATED pins → `move_to_step('WMAPS')` + step 7 / WMAPS pins; defensive `getattr` tearDown. `test_compute_and_populate_cache`: `move_to_step('DESIGN_MTR')` + step 8 / DESIGN_MTR pins — the FLAT `rlmwf_08_DESIGN_MTR.dat` + `rlmwf_08_DESIGN_MTR.dat.SHA3-256` on disk, "Forcing computation" in the logs, `context.design_matrix` not None, the shape == the principal-indexes shape, the dtype == uint32. `test_read_cache_on_new_instance`: first instance to DESIGN_MTR (cache warm) → a second `LogisticModel` on the SAME base_dir to WMAPS → the StringIO buffer cleared → the second instance to DESIGN_MTR: "Cache successfully loaded and validated" in the logs, "Forcing computation" NOT in the logs (the negative pin — no recompute), the cached `design_matrix` not None with the same shape + the uint32 dtype |
| `TestLMWorkerDesignMatrixExactValues` (1, rlm_01.json — the 10-position golden fixture) | `test_compute_design_matrix_exact_values`: the pre-DESIGN_MTR None-ness pin (the half-open interval guarantee) → `move_to_step('DESIGN_MTR')` → the not-None pin → `X.shape == (10, 7)` + `X.dtype == np.uint32` → the pinned 10×7 literal (the single source of truth — re-derived independently by the probe: the recompute identity, the valid-w-index bound, the per-feature iwmap regions, the all-zero intercept column) via `nptest.assert_array_equal` |

## Goldens pinned

- The flat cache file names: `rlmwf_08_DESIGN_MTR.dat` + `rlmwf_08_DESIGN_MTR.dat.SHA3-256`.
- The witness log lines: "Forcing computation" (compute run) + "Cache successfully loaded and validated" (cache hit)
  with the NEGATIVE pin.
- The full rlm_01 golden: the (10,7) uint32 X literal (10 training positions, F=4 — INTERCEPT 1 / LMC 1 / DIAG3 4 / CORE
  1 instances, cut_off 2, K=174 — the design-matrix view of the same 21-weight layout the WMAPS tests pin).

## Conventions

- The `WORKSPACE_ROOT`/`CUSTOM_TMP_BASE` anchoring (both classes).
- The db_gate (the SKIP_REGAB_DB gate, the D-532 default tier) at the top of both setUps — 3/0/3 under the gate.
- The `verbosity=Verbosity.HIGH` house pattern of the worker tests.

## Integration

- The end-to-end cache round-trip pin (both directions) + the golden content pin (the full (10,7) X), as in the other
  worker test files.
- The step pins (7 = WMAPS, 8 = DESIGN_MTR) lock the 19-level pipeline ordering — a level insertion/reorder breaks both.
- The per-feature contiguity + checksum facts are probe-side.
