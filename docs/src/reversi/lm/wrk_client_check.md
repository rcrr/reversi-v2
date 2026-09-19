# reversi/lm/wrk_client_check.py
The CLIENT_CHECK worker — the 17th step of the LM pipeline (after SAVE; PLOT follows at 18). a non-cache worker: no
`cache_manager` wiring, no cache file (the level is recomputed on every up-move). The acceptance test of the saved model
file: it re-reads the SAVE artifact from disk, builds the client's vectorized Evaluation Function on the FILE weights,
and recomputes the validation residuals in Y space — they must coincide with the validation series VALIDATE published on
the context (`ctx.vld_rn`, I-018) within `ctx.cfg.client_check_tol` (default 1e-8, the config field). Y space, because Y
values are comparable across models (different logit_clipping); Z values are distorted per model. The two sides are
expected bit-identical (the same f32 pipeline over the bit-exact file round-trip): the tolerance guards against pipeline
drift and file corruption, not against rounding noise. On a breach the worker logs ERROR and raises RuntimeError. No
context attribute is published; `_down` is a no-op (log only).

## API

| name | contract |
|---|---|
| `wrk_client_check()` | the factory — `@validate_call(config=ConfigDict(arbitrary_types_allowed=True))` returning `Worker("CLIENT_CHECK", _up, _down)` |

## Architecture

- `_up`: INFO "Starting client check..." → re-read `base_dir / cfg.output` with the v2 reader (which re-verifies the
  embedded config checksum) → the client's array EF on the FILE weights + the f64-view residual (`rn_file`) → the
  reference `rn_ref = ctx.vld_rn` (the VALIDATE series, I-018) → `diff = |rn_file − rn_ref|`, `max_diff`, `first_bad`,
  `tol = ctx.cfg.client_check_tol` → the breach branch: the ERROR line + `RuntimeError` (the message carries the max
  difference, the first bad position, the tolerance and the divergence diagnosis) → the pass line: "Client check passed:
  {n} validation residuals, max difference {max_diff:.3e} (tolerance {tol:.1e})."
- `_down`: INFO "Clearing client check attributes..." — nothing is cleared (the worker re-reads the file on every
  up-move, as SAVE).
- Imports: numpy, pydantic, `Worker` / `Relevance`, `make_evaluation_function_array` (the client factory: the check IS
  the client running on the saved file), `model_weights_read_file` (the v2 reader), `LMContext` under TYPE_CHECKING. NO
  `reversi.tools.cache_manager` import and NO `sigmoid` import (I-018: the worker no longer re-derives the forward
  pass).

## Verified invariants

Pinned by the 6-test `test_wrk_client_check` suite (no DB) + the full-chain suite (DB-gated).

- The bit-identity golden: on a synthetic rlm_04-mirror context (the test_client layout, 2000 seeded collision-free
  positions), the file round-trip + the client's array EF reproduce the published validation series BIT-EXACTLY — the
  pass line pins "max difference 0.000e+00 (tolerance 1.0e-08)" (`test_up_passes_on_unmodified_file`). The DB-gated
  A2030 chain pins the same line at full scale (20000 validation residuals); the A2050 VLONG chain exercises the
  199932-residual form.
- The failure path: a FILE written from a diverged in-memory state (its residuals no longer match the published series,
  max difference ~0.2) → the RuntimeError with the full diagnosis message + exactly one ERROR log line
  (`test_up_diverged_weights_raise`); the missing-file case propagates the read's `FileNotFoundError`
  (`test_up_missing_file_raises`).
- The tolerance is the cfg field (the JSON config value, not a module constant): the same divergence is ADMITTED by a
  wide tolerance (1.0) and REJECTED by a tight one (1e-4) (`test_tolerance_is_read_from_config`).
- The factory name (`test_factory_returns_named_worker`) + the no-op `_down` log (`test_down_is_a_noop_log`).
- The pipeline shape (18 levels, the PLOT last) — `probes/verify_logistic_model.py` V3c.

## Open issues

None.

## Conventions

- The reference is the PUBLISHED series (`ctx.vld_rn`, I-018): the validation forward pass runs ONCE, in VALIDATE, the
  level that owns it. Do not reintroduce a local re-derivation — the single source is the point.
- The comparison runs in the rounded-lossless f64 view on BOTH sides: the quantities compared are the exact residuals,
  and the f32 rounding of the metrics' own `rn_y` (f32 minus int8) never enters the tolerance arithmetic.
- A deviation from the uniform `cache_manager` wiring — the rlmwf_17 slot stays unused.
- The worker is stateless by design: it publishes no context attribute (the ANALYTICS level, upstream, has already
  written its reports; the check result lives in the event log).

## Integration

- Pipeline ordering: CLIENT_CHECK is the 17th step; its inputs come from SAVE (the file at `base_dir / cfg.output`),
  VLD_POSITIONS (`ctx.vld_positions`, `ctx.vld_game_values`), CONFIG (`ctx.cfg.client_check_tol`) and VALIDATE
  (`ctx.vld_rn`, the published series — I-018).
- Consumes the client: `make_evaluation_function_array` (client.md) — the in-pipeline consumer that proves the
  out-of-pipeline artifact (the saved file + the client) reproduces the pipeline's own validation. The scalar EF stays
  the test_client.py pin (the 1100× speed ratio makes the array EF the level's tool).
- Downstream: PLOT (step 18) — the matplotlib diagnostics, consuming nothing from the check (its result lives in the
  event log); the gate-first ordering is the point: the figures are drawn for a VERIFIED model file. A breach leaves
  `current_step` at 17 and the machine never reaches PLOT.
