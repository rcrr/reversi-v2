# test/reversi/lm/test_wrk_optimize.py
The OPTIMIZE worker integration suite — the house worker-test shape (same as test_wrk_gradient et al.): a live-DB suite
that moves the machine through the chain to OPTIMIZE (step 11) on a fresh base dir and then exercises the OPTIMIZE
level. 2 classes / 6 tests: 3 DB-gated (the live-DB `TestLMWorkerOptimize` — the db_long_gate, SKIP_REGAB_DB + LONG —
the setUp moves through GRADIENT on a fresh base dir — `3/0/3` under `SKIP_REGAB_DB=1`) + 3 UNGATED (the mock-ctx
`TestLMWorkerOptimizeMock` — a real, miniature L-BFGS over a 3×2 synthetic problem, no DB / no pipeline).

## Coverage

| class | what it pins |
|---|---|
| `TestLMWorkerOptimize` (3 tests, DB-gated) | shared setUp: the `SKIP_REGAB_DB` gate FIRST → the stdout patcher → `TemporaryDirectory` under `CUSTOM_TMP_BASE` created FIRST, `WORKSPACE_ROOT`-anchored `rlm_02.json` → a fresh `LogisticModel` at `Verbosity.HIGH` (deliberate: the tests assert on worker INFO logs — LOW displays WARN+ only) → `move_to_step('GRADIENT')` + the step-10 pin; defensive `getattr` tearDown. `test_optimization_runs`: records the loss at w=0, moves to OPTIMIZE (step-11 pin), asserts the loss decreased and the weights are not all zeros. `test_max_iters_treated_as_completed`: run 1 with `max_iters=10` + `log_every_n=0` (hits MAX_ITERS_REACHED); run 2 on a fresh instance in the same dir: the log must say "Checkpoint: optimization already completed." + "Iterations", and `assertNotIn("L-BFGS - [", logs)` — the per-iteration lbfgs marker; the reloaded weights are byte-identical to run 1's. `test_down_clears_optimize`: after the full run, `move_to_step(10)` (back to GRADIENT) must leave `ctx.fg is None`, `ctx.w_checksum is None`, `ctx.opt_info is None` while `ctx.w` is untouched (kept — the re-optimized WMAPS vector) |
| `TestLMWorkerOptimizeMock` (3 tests, UNGATED — no DB, no pipeline; the hlp_optimize `_mock_ctx` idiom, extended: a `_MockOptimizeCtx` that subclasses the base `Context` (the `Worker.up` `@validate_call` gate) carrying a SimpleNamespace cfg + the REAL `hlp_gradient_compute` closure on a tiny 3×2 design matrix — a real, if miniature, L-BFGS run) | `test_optimization_runs_small`: a real tiny L-BFGS (max_iters 100, min_grad 1e-6) — the loss drops below the w=0 value, the weights move, the published `w_checksum == sha3_256(w.tobytes())`, `opt_info` carries the 5 keys {converged, reason, iters, f, g_norm} with converged=True, and the `checkpoint_optimize.dat` file + its `.SHA3-256` sidecar exist in base_dir. `test_max_iters_treated_as_completed_small`: the checkpoint decision (the wrk_optimize disjunction) — run 1 with max_iters 10 + unreachable min_grad 1e-12 stops at MAX_ITERS_REACHED (iters 10, non-zero w); run 2 on a fresh ctx, same base dir + identical config (the consistency gates pass, the status gate is False) loads the completed checkpoint — the log says "Checkpoint: optimization already completed." + "Iterations", NOT "L-BFGS - [", and the STRONGEST form: the fg closure was never called in run 2 (a counted wrapper pins fg_calls == 0); the reloaded weights are byte-identical to run 1's + iters 10. `test_down_clears_optimize`: after `up` (fg / w_checksum / opt_info not-None), `down` clears `fg` / `w_checksum` / `opt_info` to None while `ctx.w` is kept (the re-optimized vector). |

## Goldens pinned

- The step pins: 10 (GRADIENT) in setUp + 11 (OPTIMIZE) in `test_optimization_runs` + 10/GRADIENT again in the _down
  test — the pipeline ordering locked.
- The real lbfgs marker `"L-BFGS - ["` (the per-iteration log line).
- The cfg mutations (`ctx.cfg.optimization.max_iters = 10`, `log_every_n = 0`) work because the LMBaseConfig models are
  not frozen.
- The mock-class checkpoint-reload log lines: "Checkpoint: optimization already completed." + "Iterations" (present)
  and the ABSENCE of the "L-BFGS - [" per-iteration marker — the disjunction engaged on a fresh instance (run 2), with
  the fg closure never called (a counted wrapper pins the call count to 0).

## Conventions

- All 3 tests are DB-gated: the setUp's GRADIENT move runs CONFIG → FEATURES → SU_ANALYSIS →
  POSITIONS → INDEXES → ANOVA → WMAPS → DESIGN_MTR → ZED → GRADIENT on a fresh base dir (all
  cache-miss) against the live regab DB.
- The header keeps the house boilerplate ("-1- Run the tests (a live regab DB + LONG=1 are required; SKIP_REGAB_DB=1
  skips the DB-gated tests, as in test_regab)").
- The two tests that re-enter OPTIMIZE (run 2 of the max-iters test, and the down-move) exercise the checkpoint-reload
  and the `_down` paths on top of the same warmed base dir.
- The mock class is UNGATED (NORMAL tier, no DB gate): a real, miniature L-BFGS over the 3×2 synthetic design matrix
  (3 weights, targets off the w=0 hyperplane so the run must move them) — the `_MockOptimizeCtx` subclasses the base
  `Context` because `Worker.up` is `@validate_call` on that type (a plain `SimpleNamespace` would be rejected), and the
  REAL `hlp_gradient_compute` closure is used, so the tiny run exercises the genuine optimizer, not a stub.

## Integration

- The suite + the probe together cover all 6 decision paths of the worker: this file covers the completed path + the
  `_down` scope; the probe H4-H8 + H6b covers completed / resume / zed-scratch / ridge-scratch / use_cache=False /
  corrupted.
- The rlm_02.json fixture (the full 199952-position training set) is reused — the same dataset as the GRADIENT worker
  test.
