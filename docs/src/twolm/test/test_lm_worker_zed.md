# twolm/test/test_lm_worker_zed.py
The worker integration test of the ZED level: the isolated
factory math + the rlm_01.json end-to-end golden (the y / z
literals — the single source of truth after the step-3 class c
deletions of the former probe D2-D4 tier) + the `_down` clearing
pin (D-092 T5). 2 classes / 3 tests — 1 DB-free factory test + 2
DB-gated worker tests.
> State: D-092 · 17a5f95 · 2026-09-01 · suite 3/0/0 (2 DB-gated)

## Coverage

| class | what it pins |
|---|---|
| `TestZedFunFactory` (1 test, no DB) | the factory math: alpha 0.02, `[-64, 0, 6, +64]` int8 → `[0.02, 0.5, 0.545, 0.98]` float32 (allclose 1e-6/1e-7) + the round-trip `z2y(y2z(y)) == float32(y)` |
| `TestLMWorkerZed` (2 tests, DB-gated) | shared setUp: the `SKIP_REGAB_DB` gate FIRST (L82-86, the D-092 T1 fix — the header's live-DB claim is now true) → stdout patch → the D-085 idiom (L92-96, T4: `TemporaryDirectory` under `CUSTOM_TMP_BASE` created FIRST, `tmp_dir = Path(self._tmp.name)` — `Path` load-bearing, the dead `shutil` import gone, the `WORKSPACE_ROOT`-anchored `rlm_01.json`) → a fresh `LogisticModel` → the move to DESIGN_MTR + the step-6 pin; defensive `getattr` tearDown. `test_compute_zed`: the pre-state (y2z/z None); `logit_clipping == 0.03` pinned; `expected_y = [10, 36, −22, 18, −16, 14, −22, 20, 0, 2]` int8; `move_to_step('ZED')` + the step-7 pin; the published attrs non-None; `z` is an ndarray, dtype float32, shape (10,); `expected_z` (10,) float32 literal via `assert_array_equal`. `test_down_clears_zed_attributes` (D-092 T5): move to ZED, then `move_to_step(6)`: pins step 6 + worker name "DESIGN_MTR" + ALL 4 ctx attrs None |

## Goldens pinned

- The rlm_01 (10,) y int8 + (10,) z float32 literals — clipping
  0.03, the same (10,) training set as the DESIGN_MTR golden (the
  pipeline grows, the positions don't).
- The step pins: 6 (DESIGN_MTR) in setUp + 7 (ZED) in
  `test_compute_zed` — the 8-level pipeline ordering locked.

## Conventions

- The 2 worker tests are DB-gated (D-092 T1) because the setUp's
  move to DESIGN_MTR runs the positions chain (the live regab DB)
  on a fresh base dir — the same gate class as
  test_wrk_design_matrix (D-090 T1); since D-130 the gate
  is the db_long_gate (SKIP_REGAB_DB + LONG). The factory test is
  NOT gated (no DB) — 3/0/2 under the gate.
- The D-085 idiom applied in D-092 T4 (the CWD `mkdtemp` + CWD
  json + dead `shutil` + non-defensive tearDown are gone).

## Integration

- No cache round-trip test exists (and none can): ZED has no
  cache file (the first non-cache level) — the end-to-end
  coverage is the single compute + the `_down` pin.
- The rlm_01.json fixture is reused (the same (10,) training set
  as the DESIGN_MTR golden); the independent re-derivation of the
  golden (the float32-exact recompute, the float64 reference, the
  hash identity) is probe-side (D5-D7, D10).
