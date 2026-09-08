# reversi/test/test_wrk_optimize.py
The OPTIMIZE worker integration suite — the house worker-test
shape (same as test_wrk_gradient et al.): a live-DB suite
that moves the machine through the full 9-level chain on a fresh
base dir and then exercises the OPTIMIZE level. 1 class / 3
tests, all DB-gated since D-096 T1 (the db_long_gate —
SKIP_REGAB_DB + LONG, D-130 — the setUp moves through
GRADIENT on a fresh base dir — `3/0/3` under `SKIP_REGAB_DB=1`).
D-096 T1-T7 applied (gate, D-085 idiom, dead code + imports
removed, the T6 vacuous-assertion fix, the new `_down` test).
> State: D-096 · b1b8934 · 2026-09-01 · suite 3/0/0 (3 DB-gated)

## Coverage

| class | what it pins |
|---|---|
| `TestLMWorkerOptimize` (3 tests, DB-gated) | shared setUp: the `SKIP_REGAB_DB` gate FIRST (T1 — the header's live-DB claim is now true) → the stdout patcher → the D-085 idiom (T2: `TemporaryDirectory` under `CUSTOM_TMP_BASE` created FIRST, `WORKSPACE_ROOT`-anchored `rlm_02.json`) → a fresh `LogisticModel` at `Verbosity.HIGH` (deliberate: the tests assert on worker INFO logs — LOW displays WARN+ only) → `move_to_step('GRADIENT')` + the step-8 pin; defensive `getattr` tearDown. `test_optimization_runs`: records the loss at w=0, moves to OPTIMIZE (step-9 pin), asserts the loss decreased and the weights are not all zeros. `test_max_iters_treated_as_completed`: run 1 with `max_iters=10` + `log_every_n=0` (hits MAX_ITERS_REACHED); run 2 on a fresh instance in the same dir: the log must say "Checkpoint: optimization already completed." + "Iterations", and T6 pins `assertNotIn("L-BFGS - [", logs)` — the ACTUAL per-iteration lbfgs marker (the old pinned string "Starting L-BFGS optimization" was never logged by opt_lbfgs, so the old assertion was vacuous); the reloaded weights are byte-identical to run 1's. `test_down_clears_optimize` (T7): after the full run, `move_to_step(8)` (back to GRADIENT) must leave `ctx.fg is None`, `ctx.w_checksum is None`, `ctx.opt_info is None` (the R4 scope) while `ctx.w` is untouched (kept — the re-optimized WMAPS vector) |

## Goldens pinned

- The step pins: 8 (GRADIENT) in setUp + 9 (OPTIMIZE) in
  `test_optimization_runs` + 8/GRADIENT again in the _down test
  — the 10-level pipeline ordering locked.
- The T6 real lbfgs marker `"L-BFGS - ["` (the per-iteration
  log line).
- The cfg mutations (`ctx.cfg.optimization.max_iters = 10`,
  `log_every_n = 0`) work because the LMBaseConfig models are
  not frozen.

## Conventions

- All 3 tests are DB-gated (T1): the setUp's GRADIENT move runs
  POSITIONS → FEATURES → INDEXES → WMAPS → DESIGN_MTR → ZED →
  GRADIENT on a fresh base dir (all cache-miss) against the live
  regab DB.
- The header keeps the house boilerplate ("-1- Run the tests (a
  live regab DB is required; SKIP_REGAB_DB=1 skips the DB-gated
  tests, as in test_regab)") — T1 made the claim TRUE (before
  the campaign it was the classic false-claim pattern, D-091 T1 /
  D-093 T5).
- The two tests that re-enter OPTIMIZE (run 2 of the max-iters
  test, and the T7 down-move) exercise the checkpoint-reload and
  the `_down` paths on top of the same warmed base dir.

## Integration

- The suite + the probe together cover all 6 decision paths of
  the worker: this file covers the completed path + the `_down`
  scope; the probe H4-H8 + H6b covers completed / resume /
  zed-scratch / ridge-scratch / use_cache=False / corrupted.
- The rlm_02.json fixture (the full 199952-position training
  set) is reused — the same dataset as the GRADIENT worker test.
