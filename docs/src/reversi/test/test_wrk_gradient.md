# reversi/test/test_wrk_gradient.py
The worker integration test of the GRADIENT level: the rlm_02
end-to-end golden (the 4 values at w=0 — the single source of
truth after the step-3 class c deletions of the former probe
D1-D4 / D11 pipeline-state tier) + the `_down` clearing pin
(D-094 T7). 1 class / 2 tests, both DB-gated (the setUp moves
through ZED on a fresh base dir, so a live DB is required —
`test_wrk_gradient` 2/0/2 under the gate).
> State: D-094 · 34442b2 · 2026-09-01 · suite 2/0/0 (2 DB-gated)

## Coverage

| class | what it pins |
|---|---|
| `TestLMWorkerGradient` (2 tests, DB-gated) | shared setUp: the `SKIP_REGAB_DB` gate FIRST (L65-69, the D-094 T5 fix — the header's live-DB claim is now true) → the stdout patcher → the D-085 idiom (T6: `TemporaryDirectory` under `CUSTOM_TMP_BASE` created FIRST, `tmp_dir = Path(...)`, the `WORKSPACE_ROOT`-anchored `rlm_02.json`) → a fresh `LogisticModel` (LOW) → the move to ZED + the step-7 pin; defensive `getattr` tearDown. `test_generate_gradient`: the pre-state (fg None, X (199952, 8), len(w) 2981); `move_to_step('GRADIENT')` + the step-8 pin; fg not-None + callable; the goldens at w = 0: f 0.02049378 (rtol 1e-6 / atol 1e-7), g[0] 3.558e-4, g[1] −2.395e-4, g[2980] 1.101e-3 (rtol 1e-4 / atol 1e-7). `test_down_clears_gradient` (D-094 T7): move to GRADIENT (step 8, fg not-None), then `move_to_step(7)` — pins step 7 + `current_worker_name == 'ZED'` + `ctx.fg is None` |

## Goldens pinned

- The 4 live values at w=0 on the rlm_02 dataset (199952
  positions, 8 pattern instances — DIAG3 + EDGE, no intercept,
  no mobilities; 2981 w entries) — all re-derived by the probe
  D6/D7 tier (the independent float64 reference).
- The step pins: 7 (ZED) in setUp + 8 (GRADIENT) in
  `test_generate_gradient` + 7/ZED again in the _down test — the
  9-level pipeline ordering locked.

## Conventions

- Both tests are DB-gated (D-094 T5): the setUp's move to ZED
  runs the positions chain (the live regab DB) on a fresh base
  dir — the same gate class as the other worker tests (the
  db_long_gate: SKIP_REGAB_DB + LONG, D-130).
- The goldens are the BRING-IN values (unchanged by D-094): the
  R1 float32 cast of g changes the values by < 1 float32 ulp
  (≈1e-10 absolute at these magnitudes) — inside the pinned
  tolerances.
- The "How to run" header documented the gate at bring-in
  (L38-39) — the claim was false then (T5), true since D-094.

## Integration

- No cache round-trip test exists (and none can): GRADIENT has
  no cache file (the second non-cache level) — the end-to-end
  coverage is the single compute + the `_down` pin.
- The rlm_02.json fixture (the full 199952-position training set
  — the largest fixture in the pipeline; the zero-weights
  handcrafted-mock goldens live in test_hlp_gradient.py instead).
- The independent re-derivation of the goldens (float32-exact
  f, the np.add.at + hand-rolled-sigmoid g) is probe-side
  (D6/D7) + unit-side (`test_hlp_gradient`'s `_reference`).
