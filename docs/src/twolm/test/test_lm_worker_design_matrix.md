# twolm/test/test_lm_worker_design_matrix.py

Analysis date: 2026-08-31 — analysis session 23 (D-089); fix
campaign D-090 approved by Roberto ("Procedi su tutti i T, e R1")
and applied in the same session. Brought in by Roberto in the
UNCOMMITTED 2026-08-31 bring-in. Probe (scratch/
verify_design_matrix.py, tier C, re-pinned in D-090 to the
post-campaign state): 0 mismatches.

The DESIGN_MTR worker test — the end-to-end cache round-trip pin
for the 7th active level + the rlm_01 golden-content pin (the
(10,7) uint32 X literal).

## Suite status (session 23, post D-090)

- 3/0/0 (2 classes; the setUp moves through WMAPS on a fresh base
  dir, so a live DB is required; DB-gated since D-090 T1 — 3/0/3
  under `SKIP_REGAB_DB=1`, as the header claims).
- Full discover: 550 tests, 64 skipped under the gate, GREEN;
  ungated: 550 run, 17 skipped (PERF only), GREEN.

## State per Roberto

The worker test file of the 2026-08-31 DESIGN_MTR bring-in.
DESIGN_MTR fix campaign (D-090) CLOSED: T1/T5/T7 fixed.

## Architecture (226 lines, post D-090)

- Header (L38-39): the DB claim — "a live regab DB is required;
  SKIP_REGAB_DB=1 skips the DB-gated tests, as in test_regab" —
  TRUE since D-090 T1 (the gate was missing at bring-in, the
  D-087 T1 class).
- Imports: `unittest`, `os` (T1), `tempfile`, numpy +
  numpy.testing, `patch` + `StringIO` + `Path`, `Verbosity`,
  `LogisticModel`, and — since D-090 T7 — `from twolm.test.paths
  import WORKSPACE_ROOT, CUSTOM_TMP_BASE` (the D-085 idiom; the
  `shutil` import is gone with the rmtree teardowns).
- `TestLMWorkerDesignMatrix` (2 tests, rlm_00.json — the
  266-position fixture):
  - setUp: the SKIP_REGAB_DB gate (T1, top of setUp, the D-080 T2
    / D-084 T2 / D-087 T1 shape) → stdout patch →
    TemporaryDirectory under CUSTOM_TMP_BASE created FIRST (T7,
    the D-085 idiom) → the WORKSPACE_ROOT-anchored json_config (T7)
    → a fresh `LogisticModel` (Verbosity.HIGH, the house) → step 0
    / CREATED pins → `move_to_step('WMAPS')` + step 5 / WMAPS pins.
  - tearDown: defensive `getattr` checks (T7) — the stdout
    patcher stop + the `_tmp.cleanup()`.
  - `test_compute_and_populate_cache`: `move_to_step('DESIGN_MTR')`
    + step 6 / DESIGN_MTR pins → the flat `rlmwf_06_DESIGN_MTR.dat`
    + `.SHA3-256` exist (the D-078 machine-level naming) → "Forcing
    computation" in the logs → `context.design_matrix` not None →
    the shape == the principal-indexes shape → the dtype ==
    uint32.
  - `test_read_cache_on_new_instance`: first instance to
    DESIGN_MTR (cache warm) → a second `LogisticModel` on the SAME
    base_dir to WMAPS → the StringIO buffer cleared → the second
    instance to DESIGN_MTR → "Cache successfully loaded and
    validated" in the logs → "Forcing computation" NOT in the logs
    (no recompute) → the cached `design_matrix` not None with the
    same shape + the uint32 dtype.
- `TestLMWorkerDesignMatrixExactValues` (1 test, rlm_01.json — the
  10-position golden fixture):
  - setUp: the gate (T1) → the same D-085 idiom (T7) → step 5 /
    WMAPS pin.
  - `test_compute_design_matrix_exact_values`: the pre-DESIGN_MTR
    None-ness pin → `move_to_step('DESIGN_MTR')` → the not-None
    pin → `X.shape == (10, 7)` + `X.dtype == np.uint32` → the
    pinned 10×7 literal (the single source of truth — re-derived
    independently by the probe D0-D10, 0 mismatches) via
    `nptest.assert_array_equal`.

## Verified facts (D-090 probe — 0 mismatches)

- V1 (C-tier): 226 lines; 2 classes / 3 tests; the gate in BOTH
  setUps + `import os` (T1); the D-085 idiom applied —
  TemporaryDirectory ×2 under CUSTOM_TMP_BASE, WORKSPACE_ROOT-
  anchored json ×2, the paths import (T7); no `shutil` (T7);
  all 3 `LogisticModel` constructions Verbosity.HIGH (the house);
  the D-078 cache names pinned; the step pins 5 (×2) + 6 (×2
  self.rlm + ×1 rlm2); 0 whitespace-only lines (T5).
- V2 (D-tier, live DB, rlm_01): the golden (10,7) uint32 X — the
  pinned literal == the pipeline output == the independent
  recompute `X = iwmap[pindexes + col_offsets]`; every value a
  valid w index (< W=21); the intercept column all 0; the
  per-feature columns within their iwmap regions; the flat cache
  files + the data checksum correct (see rlm_design_matrix.md V3).

## Minor notes — RESOLVED (D-090)

- **T1 FIXED**: the SKIP_REGAB_DB gate added to BOTH setUps (top
  of setUp, `if os.getenv('SKIP_REGAB_DB', '0') == '1':
  self.skipTest('SKIP_REGAB_DB=1: database tests skipped')`) +
  `import os` — the header's claim is now true (3/0/3 under the
  gate), the same fix as D-087 T1.
- **T5 FIXED**: the 21 whitespace-only lines stripped (emptied in
  place); scope as in D-078 M3: the license-header `# ` lines stay.
- **T7 FIXED**: the D-085 idiom applied to BOTH classes —
  `tempfile.mkdtemp(dir='./build/tmp')` → `tempfile.
  TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))` created FIRST,
  `self.tmp_dir = Path(self._tmp.name)`, the CWD-relative json
  configs → WORKSPACE_ROOT-anchored, the `shutil.rmtree` teardowns
  → the defensive `getattr` tearDown, the dead `shutil` import
  removed — the same idiom as D-087 T2 (test_lm_worker_wmaps) /
  D-085 (test_paths).

## Integration notes

- The golden fixture is rlm_01.json (the WMAPS fixture, reused):
  10 training positions, F=4 (INTERCEPT 1 / LMC 1 / DIAG3 4 /
  CORE 1 instances), cut_off 2, K=174 — the X literal is the
  design-matrix view of the same 21-weight layout the WMAPS tests
  pin (see rlm_wmaps.md V3).
- The step pins (5 = WMAPS, 6 = DESIGN_MTR) lock the 7-level
  pipeline ordering — a level insertion/reorder breaks both.
- The cache files are the flat `rlmwf_06_DESIGN_MTR.dat` machine-
  level naming (D-078) — no per-worker naming code.

## Appendix — line reference

226 lines, as of D-090 (202 at bring-in + the two gates + the
D-085 idiom in both setUps; 21 ws lines emptied in place; the
`shutil` import gone with the rmtree teardowns).

- L44-57: imports (`os` L45 [T1]; `twolm.test.paths` L57 [T7])
- L61-159: `TestLMWorkerDesignMatrix` (gate L65-69 [T1];
  TemporaryDirectory L77 [T7])
- L100-124: `test_compute_and_populate_cache`
- L126-159: `test_read_cache_on_new_instance`
- L161-222: `TestLMWorkerDesignMatrixExactValues` (gate L166-170
  [T1]; the golden test L195-222 with the pinned (10,7) literal at
  L209-220)
