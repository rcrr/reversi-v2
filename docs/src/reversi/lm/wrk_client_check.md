# reversi/lm/wrk_client_check.py
The CLIENT_CHECK worker — the 16th active level of the LM pipeline (step 15, after SAVE; PLOT follows as the 17th). The
7th non-cache worker — no `cache_manager` wiring, no rlmwf_17* file (a pure verification step, recomputed on every
up-move). The acceptance test of the saved model file: it re-reads the SAVE artifact from disk, builds the client's
vectorized Evaluation Function on the FILE weights, and recomputes the validation residuals in Y space — they must
coincide with the in-memory VALIDATE forward pass's residuals within `ctx.cfg.client_check_tol` (default 1e-8, the
config field). Y space, because Y values are comparable across models (different logit_clipping); Z values are distorted
per model. The two sides are expected bit-identical (the same f32 pipeline over the bit-exact file round-trip): the
tolerance guards against pipeline drift and file corruption, not against rounding noise. On a breach the worker logs
ERROR and raises RuntimeError. No context attribute is published; `_down` is a no-op (log only).

## API

| name | contract |
|---|---|
| `wrk_client_check()` | the factory — `@validate_call(config=ConfigDict(arbitrary_types_allowed=True))` returning `Worker("CLIENT_CHECK", _up, _down)` |
| `_validation_residuals_y(ctx) -> (N,) f64` | private — the reference validation residuals: the exact `hlp_validate.validate_model` forward pass on the IN-MEMORY context state (the A1a ruling), returned as the rounded-lossless f64 view (the f32 predictions + the int8 game values both upcast exactly, so no f32 rounding noise enters the comparison) |

## Architecture

- Imports (L28-42): numpy (L30), pydantic (L32), `Worker, Relevance` (L36), `make_evaluation_function_array` (L37 — the
  client factory: the check IS the client running on the saved file), `sigmoid` (L38 — the hlp_gradient scipy-expit, the
  SAME function hlp_validate uses), `model_weights_read_file` (L39 — the v2 reader, which re-verifies the embedded
  config checksum), `LMContext` under TYPE_CHECKING (L41-42). NO `reversi.tools.cache_manager` import (by design).
- `_validation_residuals_y` (L50-69): the A1a reference — the `hlp_validate` forward pass reproduced on the in-memory
  state: `compute_indexes` (L62) → the per-instance `col_offsets` (L63-64, the same
  `np.repeat(offsets[:-1], n_instances)` as hlp_validate L116) → `dense_indices = vld_indexes + col_offsets` (L65) →
  `np.sum(w_dense[dense_indices], axis=1)` (L66) → `sigmoid` (L67) → `ctx.z2y` (L68) → the f64-view residual (L69).
- `_up` (L72-115): INFO "Starting client check..." (L73) → re-read `base_dir / cfg.output` (L78-79) → the client's array
  EF on the FILE weights + the f64-view residual (L84-87) → the reference residual (L92) → `diff = |rn_file − rn_ref|`,
  `max_diff`, `first_bad`, `tol = ctx.cfg.client_check_tol` (L94-97) → the breach branch (L99-110): the ERROR line +
  `RuntimeError` (the message carries the max difference, the first bad position, the tolerance, and the "the model
  file, the client, or the validation forward pass has diverged" diagnosis) → the pass line (L112-115): "Client check
  passed: {n} validation residuals, max difference {max_diff:.3e} (tolerance {tol:.1e}).".
- `_down` (L118-121): INFO "Clearing client check attributes..." — nothing cleared (stateless: the file is re-read on
  every up-move, as SAVE).
- `wrk_client_check()` (L124-126): the factory, `@validate_call`-decorated (the uniform worker-factory idiom).

## Verified invariants

Pinned by the 6-test `test_wrk_client_check` suite (no DB) + the full-chain suite (DB-gated).

- The bit-identity golden: on a synthetic rlm_04-mirror context (the test_client.py layout, 2000 seeded collision-free
  positions), the file round-trip + the client's array EF reproduce the validation residuals BIT-EXACTLY — the pass line
  pins "max difference 0.000e+00 (tolerance 1.0e-08)" (`test_up_passes_on_unmodified_file`). The DB-gated A2030 chain
  pins the same line at full scale (20000 validation residuals, test_lm_worker_full_chain); the A2050 VLONG chain
  exercises the 199932-residual form.
- The failure path: diverged in-memory weights (the file and the ctx no longer agree, max difference ~0.2) → the
  RuntimeError with the full diagnosis message + exactly one ERROR log line (`test_up_diverged_weights_raise`); the
  missing-file case propagates the read's `FileNotFoundError` (`test_up_missing_file_raises`).
- The tolerance is the cfg field (the JSON config value, not a module constant): the same divergence is ADMITTED by a
  wide tolerance (1.0) and REJECTED by a tight one (1e-4) (`test_tolerance_is_read_from_config`).
- The factory name (`test_factory_returns_named_worker`) + the no-op `_down` log (`test_down_is_a_noop_log`).
- The pipeline shape (17 active levels, the PLOT last) — `probes/verify_logistic_model.py` V3c.

## Open issues

None.

## Conventions

- The A1a ruling: the reference residuals are RECOMPUTED here from the in-memory ctx state (VALIDATE itself is untouched
  — the closure stands). The formula is a copy of hlp_validate's forward pass: if that formula ever changes, this copy
  must follow (the divergence would be caught by the check itself — it would fail the pipeline).
- The comparison runs in the rounded-lossless f64 view on BOTH sides: the quantities compared are the exact residuals,
  and the f32 rounding of hlp_validate's own `rn_y` (f32 minus int8) never enters the tolerance arithmetic.
- The 7th deviation from the uniform 7-kwargs `cache_manager` wiring — the rlmwf_17 slot stays unused, like
  03/07/08/09/12/13/15.
- The worker is stateless by design: it publishes no context attribute (the ANALYTICS level, upstream at 14, has already
  written its reports; the check result lives in the event log).

## Integration

- Pipeline ordering: CLIENT_CHECK is the 17th step; its inputs come from SAVE (the file at `base_dir / cfg.output`),
  VLD_POSITIONS (`ctx.vld_positions`, `ctx.vld_game_values`), FEATURES (`ctx.feature_set`), WMAPS
  (`ctx.iwmap_feature_offset`), GENERATE (`ctx.w_dense`), ZED (`ctx.z2y`) and CONFIG (`ctx.cfg.client_check_tol`) — the
  SM half-open interval semantics guarantee every up-move to step 15 passes through all of them.
- Consumes the client: `make_evaluation_function_array` (client.md) — the in-pipeline consumer that proves the
  out-of-pipeline artifact (the saved file + the client) reproduces the pipeline's own validation. The scalar EF stays
  the test_client.py pin (the 1100× speed ratio makes the array EF the level's tool).
- Downstream: PLOT (the 17th level) — the matplotlib diagnostics, consuming nothing from the check (its result lives in
  the event log); the gate-first ordering is the point: the figures are drawn for a VERIFIED model file. A breach leaves
  `current_step` at 15 and the machine never reaches PLOT.
