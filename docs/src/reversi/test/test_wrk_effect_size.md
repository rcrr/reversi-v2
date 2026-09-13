# reversi/test/test_wrk_effect_size.py
The NO-DB suite of the EFFECT_SIZE worker (the I-017, D-187):
the factory (the worker name), the enable no-op (the D-175
opt-in), the ANOVA (the eta²/omega² per sub-variable), the
graceful degradation (the adherence skipped when the corpus is
absent), the adherence (the fixed trio, the computed path), the
report, and the down (the D-060 no-op). 1 class / 7 tests / no
database (the mock ctx, the synthetic indexes + the game
values).
> State: D-187 (T17) · 2026-09-13 · suite 7/0/0

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestWrkEffectSize` | 7 | `test_factory` (the worker factory: the EFFECT_SIZE name); `test_enable_no_op` (the D-175 opt-in: the enable false -> the no-op, the "disabled" log); `test_anova` (the eta²/omega² per sub-variable: the log has one ANOVA line per sub-variable (the instance count)); `test_adherence_graceful_degradation` (the tables None (the FEATURE_ANALYSIS disabled) -> the adherence SKIPPED (the log note), the ANOVA runs); `test_adherence_computed` (the tables set (the ideal = the synthetic distribution) -> the adherence is computed, the log has the Adherence lines, the top-N); `test_report_written` (the TXT report, the dir_name under base_dir); `test_down_no_op` (the D-060 no-op: the down is a no-op, the log note) |

## Goldens pinned

- The synthetic raw codes: the rlm_00 fixture's feature set (the
  LMC / the ALMC / the DLMC + the ELLE / the EDGE), the 100
  positions, the random raw codes (the 0..n_conf range) + the
  random game values (the standard normal).
- The ANOVA: one line per sub-variable (the instance count) —
  the eta²/omega² are computed (the T13 kernel).
- The graceful degradation: the tables None -> the adherence
  SKIPPED (the log note), the ANOVA runs (it does not need the
  corpus).
- The adherence: the tables set -> the adherence is computed
  (the log has the Adherence lines, the top-N, the T14 kernel).
- The D-060 no-op: the down is a no-op (the worker publishes
  nothing on the ctx).

## Conventions

- The house test header (the "How to run" block).
- The NO-DB mock-ctx suite: the `_MockCtx` (the cfg, the
  feature_set, the hlp_indexes (the synthetic raw codes), the
  game_values, the feature_analysis_tables, the log buffer) over
  the rlm_00 fixture's feature set (the `load_campaign`). The
  synthetic raw codes (the `np.random.default_rng`) keep the
  suite fast + deterministic (no LONG tier).
- The `tempfile.TemporaryDirectory` per test (the report lands
  in a tmp dir, the tearDown cleans up).

## Integration

- Consumed by `run_utests.sh` (section 4 — the pipeline, at the
  step 6 worker position: between the INDEXES worker and the
  WMAPS data module).
- The worker (wrk_effect_size) is registered at step 6 by the
  T18 wiring (the 18 levels, NO cache slot).
