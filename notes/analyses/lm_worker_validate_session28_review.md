<!-- ARCHIVED — D-106 step 18 (the docs/ rewrite, 2026-09-04): the
     complete session-28 analysis (D-101) + the D-102
     fix-campaign narrative moved out of
     docs/src/twolm/lm_worker_validate.md per docs_rules.md
     §1/§4. This is a frozen historical record: it is never
     updated. Stale-in-current-context notes: (1) the "28 checks"
     figure — see the sibling rlm_validate_session28_review.md
     header for the 18 surviving check calls + the step-3
     deletion/conversion list; (2) the "622 tests / 80 skipped"
     full-discover figure predates steps 3-17 (current: 664/87
     gated); (3) the D-101/D-102 campaign narrative (T1 the
     factory gate, T2 the dead numpy import, T4 the 3 ws lines,
     M1 the RMSE/MAE zero guard) is frozen history. -->

# twolm/lm_worker_validate.py

Analysis date: 2026-09-02 — analysis session 28 (D-101, the
VALIDATE bring-in, Roberto's commit 536eadc); fix campaign D-102
approved by Roberto ("R1: OK, T1: OK, T2: OK, T3, T4: OK, T5: OK,
M1-M3: OK. Procedi") and applied in the same session. Brought in by
Roberto (536eadc — the 13th active level of the pipeline, the first
bring-in with a dedicated data module `rlm_validate.py` besides the
worker).

The VALIDATE worker of the RLM pipeline: the THIRD non-cache worker
(after FEATURES, ZED, GRADIENT) — no `cache_manager` wiring at all
(no load-or-compute cycle, no `is_allowed` switch, no rlmwf_12*
file). The level is recomputed on every up-move: it is a pure
forward pass over the validation positions with the optimized
`ctx.w_dense`, so the rlmwf_12 slot stays unused (confirmed live —
probe C5). The machine contract is unchanged: `_up` publishes the
ONE context attribute `ctx.vld_metrics` (the 7-key metrics dict),
`_down` clears it.

## Suite status (session 28, post D-102)

- `test_lm_worker_validate`: 3/0/0 live (1 class, all 3 tests
  DB-gated — the setUp moves through VLD_POSITIONS on a fresh base
  dir, so the live regab DB is required; under `SKIP_REGAB_DB=1` the
  3 tests skip — 3/0/3 gated).
- Full discover: 622 tests, 80 skipped under `SKIP_REGAB_DB=1`,
  GREEN (2.6 s); ungated (live DB): 622 run, 17 skipped, GREEN
  (30.6 s). The full `-W error` discover is clean.

## State per Roberto

Pipeline-in-progress, 13 active levels, enabled by Roberto's
2026-09-02 bring-in (536eadc). The next line-by-line step is
`lm_worker_analytics` (the next commented entry, L53). VALIDATE fix
campaign (D-102) CLOSED: R1 (the unimported `Any` in the data
module, rlm_validate), T1 (factory `@validate_call` + pydantic
import), T2 (the dead `numpy` import removed here + the dead regab
imports removed in rlm_validate), T4 (3 ws lines), M1 (the
RMSE/MAE zero guard) fixed here; T3/T4 in rlm_validate; T5 the
dedicated test file added.

## Architecture (75 lines, post D-102)

- Imports (L28-38): `Worker, Relevance` from state_machine (L34),
  `validate_model` from rlm_validate (L35), `validate_call,
  ConfigDict` from pydantic (L30 — added in D-102 T1, the dead
  `numpy as np` import replaced — T2), `RLMContext` under
  TYPE_CHECKING (L37-38). NO `twolm.cache_manager` import (by
  design).
- `_up` (L46-62): `log_event(INFO, "Starting model validation...")`
  (L47); `metrics = validate_model(ctx)` (L49, rlm_validate);
  publishes `ctx.vld_metrics = metrics` (L50); 7 INFO log lines
  (L52-60): the completion line ("Validation completed. Loss
  (MSE/2): ...", 8-e format), MSE/MAE (4-e format), MAE(y)/RMSE(y)
  (2-f format), and the RMSE/MAE ratio (2-f format) — the last one
  ZERO-GUARDED since D-102 M1: a perfect Y-space fit
  (`vld_mae_y == 0`) logs the "n/a (vld_mae_y is 0 — perfect
  Y-space fit)" line (L60) instead of dividing by zero.
- `_down` (L65-69): `log_event(INFO, "Clearing validation
  attributes...")` then clears the ONE attribute to None (L67) —
  the scope is complete: `_up` sets exactly `vld_metrics` (pinned by
  probe A9 and test_down_clears_vld_metrics).
- `lm_worker_validate()` (L72-75): the factory — `@validate_call
  (config=ConfigDict(arbitrary_types_allowed=True))` since D-102
  T1 (all 11 sibling worker factories share the pattern) — returns
  `Worker("VALIDATE", _up, _down)` (L75).

## Verified facts (D-101/D-102 probe — 28 checks, 0 mismatches)

scratch/verify_validate.py, tiers A (structure, 13 checks), B
(pipeline state, 4), C (live golden re-derivation, 7, gated on
SKIP_REGAB_DB), D (unit math, no DB, 3). Pre-campaign the probe
reported exactly the 8 worklist mismatches (A2-A8); post D-102 all
28 pass.

- V1 (A-tier): structure — 75 lines; `__all__ =
  ['lm_worker_validate']` (L42); the factory WITH `@validate_call`
  + the pydantic import (D-102 T1); NO numpy import (T2);
  `validate_model` the single public data name; NO cache_manager
  import (A11); `_up` sets the 1 ctx attribute (L50); `_down`
  clears it (L67); `Worker("VALIDATE", ...)` (L75); 0 non-comment
  trailing-whitespace lines (D-102 T4).
- V2 (C-tier, live DB, rlm_02): the full pipeline through VALIDATE
  (step 12, no crash — no cache-path trap this time, unlike
  D-097/D-099) with the 7-metric goldens: `vld_loss
  0.00700794393196702`, `vld_mse_z 0.01401588786393404`,
  `vld_mae_z 0.09311295300722122`, `vld_mae_y
  12.161691665649414`, `vld_mse_y 239.10484313964844`,
  `vld_rmse_y 15.46301555633545`, `vld_samples 200` (bid [8]
  validation vs the bid [6,7] training model); the 7 INFO log lines
  (incl. "RMSE/MAE: 1.27" — the docstring normal-distribution
  indicator is 1.253); the validation loss ≈ the training final
  loss (7.1250e-03 — no overfitting signal); NO rlmwf_12* file in
  the base dir (C5); second instance: identical metrics (deterministic
  recompute) + no DB re-extraction + exactly 6 "Cache successfully
  loaded and validated" hits (the 6 cache_manager levels; CONFIG and
  the OPTIMIZE checkpoint have their own load flows) (C6); the
  `_down` clearing (C7).
- V3 (D-tier, no DB): the full metric math on a hand-computed
  2-position case (loss 0.0625, mse_z 0.125, mae_z 0.25, mae_y
  32.0, mse_y 2048.0, rmse_y sqrt(2048), samples 2) re-derived
  independently; every metric a PYTHON float (the float() casts) +
  `vld_samples` an int; the M1 zero-guard demo: a perfect Y-space
  fit (mae_y == 0) logs the n/a line and does NOT raise
  (D-102 M1; pre-campaign the same case raised ZeroDivisionError).

## Minor notes

- **M1 (FIXED, D-102)** — the RMSE/MAE ratio (worker L57-60)
  divided by `vld_mae_y` WITHOUT a zero guard: a perfect Y-space fit
  (all predictions exactly on target) raised ZeroDivisionError in
  the `_up` log line — demonstrated live pre-campaign (probe D3).
  Now guarded: the n/a line is logged instead.
- **M2 (FIXED, D-102, rlm_validate)** — `vld_P` unpacked from
  `vld_indexes.shape` but never used → underscore-unpacked
  (`vld_M, _ = vld_indexes.shape`, the D-096 M1 pattern).
- **M3 (FIXED, D-102, rlm_validate)** — the returned dict omitted
  `vld_mse_y` although `mse_y` was computed (L142) — it only fed
  `rmse_y`. Roberto's call: the key belongs in the dict; it is now
  the 6th metric (7 keys total).
- **Report-only (no number):** the dense-mapping idiom in
  rlm_validate (`np.repeat(ctx.iwmap_feature_offset[:-1],
  n_instances_per_feature)` + `vld_indexes + col_offsets` +
  `np.sum(ctx.w_dense[dense_indices], axis=1)`) differs from
  rlm_generate's per-feature start/end loop — both valid, left as
  is.
- The no-cache design is the third deviation from the uniform
  7-kwargs `cache_manager` wiring — intentional and confirmed by
  Roberto (the bring-in analysis D-101 asked whether it was by
  design; the rlmwf_12 slot stays unused, the flat-file numbering
  will skip 12 like it skipped 03/07/08).

## Integration notes

- Pipeline ordering: VALIDATE is the 13th level; its inputs come
  from VLD_POSITIONS (`ctx.vld_positions`, `ctx.vld_game_values`),
  FEATURES (`ctx.feature_set`), WMAPS (`ctx.iwmap_feature_offset`),
  GENERATE (`ctx.w_dense`), ZED (`ctx.y2z` / `ctx.z2y`) — the SM
  half-open interval semantics guarantee every up-move to step 12
  passes through all five. The test setUp moves through
  VLD_POSITIONS (step 11) first, so the full 13-level chain is
  exercised end-to-end on the live DB.
- The `sigmoid` is REUSED from rlm_gradient (defined + exported
  there) — no local copy (probe A10).
- `Worker.up` is `@validate_call`-gated with `context: Context`
  (state_machine L87-90): a bare SimpleNamespace is rejected — the
  D3 probe builds a real RLMContext.
- No `use_cache` interaction: with `ctx.use_cache=False` (the
  CONFIG switch) the other levels still warm their cache files;
  VALIDATE has nothing to warm — the behavior is identical either
  way.
- Downstream: ANALYTICS (the next commented level) will consume
  `ctx.vld_metrics` (the `ctx.analytics_report` blackboard field is
  already pre-declared, L155).

## Appendix — line reference

75 lines, as of D-102 (71 at the 536eadc bring-in; D-102: +1
pydantic import line [T1, replacing the numpy line — T2], +1
decorator line [T1], +2 guard lines [M1], 3 ws lines emptied in
place [T4]).

- L28-38: imports (pydantic L30 [T1], state_machine L34,
  rlm_validate L35, TYPE_CHECKING L37-38)
- L42: `__all__`
- L46-62: `_up` (L47 start log, L49 the validate_model call, L50
  the ctx publish, L52-60 the 7 metric log lines — L57-60 the
  M1-guarded RMSE/MAE line)
- L65-69: `_down` (L67 the single None clear)
- L72-75: `lm_worker_validate` (L72 decorator [T1], L75 the Worker)
