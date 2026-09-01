# twolm/test/test_lm_worker_optimize.py

Analysis date: 2026-09-01 — analysis session 26 (D-096, bring-in
analysis); the T1-T7 batch applied in the D-096 campaign (Roberto:
"T1-T15: falli tutti"). Brought in by Roberto (commit 1ebdd8b). Probe
(scratch/verify_optimize.py, tier D, re-pinned post-campaign): 0
mismatches.

The OPTIMIZE worker integration suite — the house worker-test shape
(same as test_lm_worker_gradient et al.): a live-DB suite that moves
the machine through the full 9-level chain on a fresh base dir and
then exercises the OPTIMIZE level. 3 tests, all DB-gated since D-096
T1.

## Suite status (session 26, post D-096)

- `test_lm_worker_optimize`: 3/0/0 live (1 class; all 3 tests
  DB-gated since D-096 T1 — the setUp moves through GRADIENT, which
  runs the positions chain on a fresh base dir). 3/0/3 under
  `SKIP_REGAB_DB=1`. Full discover: 598 tests, 71 skipped under the
  gate, GREEN.

## State per Roberto

As brought in: 2 tests in 1 class — green on first run, with the
house bring-in gaps: no `SKIP_REGAB_DB` gate although the header
claimed one (T1 — the tests DO hit the live DB via the GRADIENT
move); the CWD-relative mkdtemp + CWD json setUp instead of the D-085
idiom (T2); a dead `if False:` block (T3); dead imports `os` (the
intended gate, never added), `skipUnless`, `Path` (T4); the stray
`#: ###` comment (T5); and a VACUOUS `assertNotIn("Starting L-BFGS
optimization", logs)` — `opt_lbfgs` never logs that string, so the
assertion passed trivially (T6). No `_down` test (T7). D-096 (all
approved): gate + idiom + cleanup + the real lbfgs marker
(`"L-BFGS - ["`) + the new `test_down_clears_optimize` pinning R4.

## Architecture (174 lines, post D-096)

- imports (L44-56): `os` (T1 — the gate now uses it), tempfile,
  unittest, StringIO/patch, Path (T2 — the idiom uses it), numpy +
  nptest, Verbosity, LogisticModel, WORKSPACE_ROOT + CUSTOM_TMP_BASE.
- `TestLMWorkerOptimize` (L59-170):
  - setUp (L62-86): T1 gate FIRST (as in test_regab — the comment
    says why the DB is needed); stdout patcher; T2 D-085 idiom
    (TemporaryDirectory FIRST under `CUSTOM_TMP_BASE`,
    `Path(self._tmp.name)`, `WORKSPACE_ROOT`-anchored rlm_02.json);
    `LogisticModel` at `Verbosity.HIGH` (the tests assert on INFO log
    lines — LOW would filter them); `move_to_step('GRADIENT')` + the
    step-8 pin.
  - tearDown (L87-91): defensive (the getattr pattern).
  - `test_optimization_runs` (L93-109): the full run — records the
    loss at w=0, moves to OPTIMIZE (step-9 pin), asserts the loss
    decreased and the weights are not all zeros. (T3 removed the dead
    `if False: self.patcher_stdout.stop()` block.)
  - `test_max_iters_treated_as_completed` (L111-151): the
    completed-checkpoint path — run 1 with `max_iters=10` +
    `log_every_n=0` (hits MAX_ITERS_REACHED); run 2 on a fresh
    instance in the same dir: the log must say "Checkpoint:
    optimization already completed." + "Iterations", and T6 pins
    `assertNotIn("L-BFGS - [", logs)` (the ACTUAL per-iteration
    lbfgs marker — the old pinned string was never logged by
    opt_lbfgs, so the old assertion was vacuous); the reloaded
    weights are byte-identical to run 1's.
  - `test_down_clears_optimize` (L154-170, NEW — T7): after the full
    run, `move_to_step(8)` (back to GRADIENT) must leave
    `ctx.fg is None`, `ctx.w_checksum is None`, `ctx.opt_info is
    None` (the R4 scope) while `ctx.w` is untouched (kept — the
    re-optimized WMAPS vector).

## Verified facts (probe tiers D, H)

- The 3 step pins (GRADIENT=8, OPTIMIZE=9) and the 3 test names are
  pinned (D7); the gate/idiom markers (D2-D4); the T6 marker
  (D8); the T7 pins (D9).
- The two live paths the tests cover (completed + full run) are
  re-verified by the probe tiers H4/H1 with the independent fg
  re-derivation.

## Minor notes

- The header keeps the house boilerplate ("-1- Run the tests (a live
  regab DB is required; SKIP_REGAB_DB=1 skips the DB-gated tests, as
  in test_regab)") — T1 made the claim TRUE (before the campaign it
  was the classic false-claim pattern, D-091 T1 / D-093 T5).
- The cfg mutations (`ctx.cfg.optimization.max_iters = 10`,
  `log_every_n = 0`) work because the RLMBaseConfig models are not
  frozen — pinned at D10.
- Verbosity.HIGH (not the LOW of the non-DB suites) is deliberate:
  the test asserts on worker INFO logs; at LOW (verbosity 3) the
  machine displays WARN+ only.

## Integration notes

- The setUp's GRADIENT move is what makes the suite DB-bound: it
  runs POSITIONS → FEATURES → INDEXES → WMAPS → DESIGN_MTR → ZED →
  GRADIENT on a fresh base dir (all cache-miss).
- The two tests that re-enter OPTIMIZE (run 2 of the max-iters test,
  and the T7 down-move) exercise the checkpoint-reload and the
  `_down` paths on top of the same warmed base dir.
- The suite + the probe together cover all 6 decision paths of the
  worker: the suite covers the completed path + the `_down` scope;
  the probe (H4-H8) covers completed / resume / zed-scratch /
  ridge-scratch / use_cache=False / corrupted.

## Appendix — line reference

174 lines, as of D-096 (149 at the bring-in; D-096: gate + idiom +
cleanup in place, +1 test, ws sweep).

- L28-42: header (how-to-run block)
- L44-56: imports
- L59-170: `TestLMWorkerOptimize` (setUp L62-86 with the T1 gate
  L63-67 + T2 idiom L73-78; tearDown L87-91; test_optimization_runs
  L93-109; test_max_iters_treated_as_completed L111-151 with the T6
  pin L147-149; test_down_clears_optimize L154-170)
- L173-174: `__main__`
