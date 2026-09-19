# reversi/test/test_wrk_gradient.py
The worker integration test of the GRADIENT level: the rlm_02 end-to-end golden (the 4 values at w=0 — the single source
of truth) + the `_down` clearing pin. 1 class / 2 tests, both DB-gated (the setUp moves through ZED on a fresh base dir,
so a live DB is required — `test_wrk_gradient` 2/0/2 under the gate).

## Coverage

| class | what it pins |
|---|---|
| `TestLMWorkerGradient` (2 tests, DB-gated) | shared setUp: the `SKIP_REGAB_DB` gate FIRST → the stdout patcher → the `TemporaryDirectory` idiom (under `CUSTOM_TMP_BASE`, created FIRST, `tmp_dir = Path(...)`, the `WORKSPACE_ROOT`-anchored `rlm_02.json`) → a fresh `LogisticModel` (LOW) → the move to ZED + the step-7 pin; defensive `getattr` tearDown. `test_generate_gradient`: the pre-state (fg None, X (199952, 8), len(w) 2981); `move_to_step('GRADIENT')` + the step-8 pin; fg not-None + callable; the goldens at w = 0: f 0.02049378 (rtol 1e-6 / atol 1e-7), g[0] 3.558e-4, g[1] −2.395e-4, g[2980] 1.101e-3 (rtol 1e-4 / atol 1e-7) — rlm_02 has NO `high_performance_fg` → the classic path. `test_down_clears_gradient`: move to GRADIENT (step 8, fg not-None), then `move_to_step(7)` — pins step 7 + `current_worker_name == 'ZED'` + `ctx.fg is None` |
| `TestGradientFlagWiring` (2 tests, NO DB) | the flag wiring of the worker on a mock context (a `Context` subclass + `SimpleNamespace` cfg + a no-op `log_event`): `test_up_flag_true_builds_hp_variant`: `high_performance_fg=True` → `wrk_gradient().up(ctx)` builds the HP closure (the `ctx.fg.high_performance is True` marker pin) + a float32-contract smoke eval. `test_up_flag_false_builds_classic_variant`: the flag False (the config default) → the classic closure (the marker False) |

## Goldens pinned

- The 4 live values at w=0 on the rlm_02 dataset (199952 positions, 8 pattern instances — DIAG3 + EDGE, no intercept, no
  mobilities; 2981 w entries) — all re-derived by the probe (the independent float64 reference).
- The step pins: 7 (ZED) in setUp + 8 (GRADIENT) in `test_generate_gradient` + 7/ZED again in the _down test — the
  10-level pipeline ordering locked.

## Conventions

- Both tests are DB-gated: the setUp's move to ZED runs the positions chain (the live regab DB) on a fresh base dir —
  the same gate class as the other worker tests (the db_long_gate: SKIP_REGAB_DB + LONG).
- The goldens are the canonical values: the R1 float32 cast of g changes the values by < 1 float32 ulp (≈1e-10 absolute
  at these magnitudes) — inside the pinned tolerances.
- The "How to run" header documents the gate.

## Integration

- No cache round-trip test exists (and none can): GRADIENT has no cache file (the second non-cache level) — the
  end-to-end coverage is the single compute + the `_down` pin.
- The rlm_02.json fixture (the full 199952-position training set — the largest fixture in the pipeline; the zero-weights
  handcrafted-mock goldens live in test_hlp_gradient.py instead).
- The independent re-derivation of the goldens (float32-exact f, the np.add.at + hand-rolled-sigmoid g) is probe-side +
  unit-side (`test_hlp_gradient`'s `_reference`).
