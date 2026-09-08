# twolm/lm_worker_optimize.py
The OPTIMIZE worker — the pipeline's optimizer level. `_up`
implements a 4-step recipe: (1) consult the existing checkpoint
(if any) through the two hlp_optimize gates, deciding between
completed-load, warm-resume and scratch; (2) build the two lbfgs
wrappers (`logger_fn` → `ctx.log_event`, `save_fn` →
intermediate INCOMPLETE checkpoints); (3) run `lbfgs` (opt_lbfgs)
with the GRADIENT-level `ctx.fg` closure (float32 contract, D-094
R1); (4) update the context (`w`, `opt_info`, `w_checksum`) and
save the final checkpoint. The checkpoint is written on EVERY run
(final save unconditional; intermediate only when
`save_every_n > 0`) and read only when
`checkpoint_path.exists() and ctx.use_cache` (the D-071 R1
pattern: a cache-disabled run still warms the checkpoint).
> State: D-096 · b1b8934 · 2026-09-01 · suite 3/0/0 (3 DB-gated)

## API

| name | contract |
|---|---|
| `lm_worker_optimize()` | the factory — `@validate_call(config=ConfigDict(arbitrary_types_allowed=True))` (D-096 T10, all 9 worker factories now share the pattern) returning `Worker("OPTIMIZE", _up, _down)` |

## Architecture

- `_up` (L52-176):
  - config + `checkpoint_path = base_dir / optimization.
    checkpoint_file` (config-named, not rlmwf_-prefixed);
    `w_init = ctx.w`; `min_grad_value, _ = opt_cfg.min_grad`
    (M1: the count is unused).
  - step 1 (L64-102): the checkpoint gate
    `checkpoint_path.exists() and ctx.use_cache` (the context
    field the CONFIG worker populated — NOT `cfg.use_cache`),
    with R2's try/except: a load raising `RuntimeError` (the 2
    header gates, the R3 checksum mismatch),
    `binio.BinaryFormatError` (corrupted framing, malformed
    sidecar) or `OSError` (missing file/sidecar) → WARN +
    `unlink(missing_ok=True)` of content + sidecar → scratch.
    Then the 3-way decision: the 3-gate consistency check (incl.
    the R1 ridge gate) → mismatch: WARN "Starting from scratch";
    converged or `iters >= max_iters` → completed: load cp['w']
    + `w_checksum` + `opt_info`, `return` (skip lbfgs);
    `iters < max_iters` → warm-resume: w_init + the initial
    sl/yl/rho/iter from the checkpoint (M2: the old trailing
    else was unreachable — iters is an int).
  - step 2 (L104-129): `logger_fn` (INFO) + `save_fn` (7 params,
    matches the lbfgs hint; writes an INCOMPLETE/non-converged
    checkpoint; M5: `iters=k+1` — completed-count semantics, as
    the final save).
  - step 3 (L131-149): the `lbfgs` call: `fg=ctx.fg`,
    `x0=w_init`, the 5 config scalars, both wrappers, the 4
    warm-start kwargs.
  - step 4 (L151-176): `ctx.w = w_opt`, `ctx.opt_info =
    optimization_info_dict(info)`, `ctx.w_checksum =
    weights_compute_sha3_256_hash(w_opt)`, the final
    `save_optimization_checkpoint` (the `info` dict carries the
    9 keys: w/converged/reason/iters/f/g_norm/sl/yl/rho).
- `_down` (L178-185): clears `ctx.fg` and — R4 (D-096) —
  `ctx.w_checksum` + `ctx.opt_info`. `ctx.w` is deliberately
  KEPT (comment L181-183): it is the re-optimized WMAPS weight
  vector; the WMAPS cache restores the zero-initialized value
  when that level recomputes.

## Verified invariants

Pinned by the `probes/verify_optimize.py` B + D + H tiers + the
3-test suite.

- Source shape (probe B1-B17): the 190-line file, the factory
  decorator + the pydantic/binio imports, the 16 lbfgs kwargs +
  the warm-start consumption (B4, B13), the R2 try/except, the
  R4 `_down` scope, the T8 header typo fix, the dead `Path`
  import gone.
- The worker-test source shape (probe D1-D11): the 174-line
  file, the gate (T1), the D-085 idiom (T2), the 3 step pins
  (GRADIENT=8, OPTIMIZE=9), the T6 marker, the T7 pins.
- The 6 live decision paths (probe H4-H8 + H6b): completed (no
  lbfgs in run 2, byte-identical weights), resume (warm start
  consumed), zed-inconsistent → scratch, ridge-only-inconsistent
  → scratch (R1, H6b), use_cache=False → no load + checkpoint
  still saved (H7), corrupted checkpoint → delete + scratch +
  valid re-save (H8).
- The float32 contract flows through: `ctx.w` is float32 after
  50 lbfgs iterations; `weights_compute_sha3_256_hash` (gated
  `NDArray[np.float32]`) never rejects.
- The base dir after a full run holds exactly the 12 expected
  files (the 5 rlmwf_ cache pairs 01/02/04/05/06 + the
  checkpoint pair); no rlmwf_03*/07*/08* file (H1).

## Open issues

None.

## Conventions

- The checkpoint is the only level cache that is a plain dict
  (not a data class) and is NOT managed by cache_manager (no
  rlmwf_ prefix, config-named file, no delete-on-inconsistency —
  the worker's own 3-way decision replaces it; the R2
  try/except is the corruption recovery that cache_manager's
  load_fn has for the other levels).
- `_up` reads `ctx.use_cache` (context field) — a test that
  wants to gate the checkpoint load off must set
  `context.use_cache` after the CONFIG level has run (probe H7).
- The intermediate checkpoints' `iters` count completed
  iterations (M5), so a resume starts exactly where the
  interrupted run stopped (no redundant iteration).

## Integration

- The 10th RLM level; consumes `ctx.fg` (the GRADIENT-level
  closure, D-093/D-094) and the WMAPS-level `ctx.w` (zero-
  initialized at WMAPS compute time) + the `optimization` config
  block.
- Produces the model artifact of the pipeline: the optimized
  `ctx.w` + `ctx.w_checksum` + `ctx.opt_info` — the inputs of
  the GENERATE/VALIDATE/ANALYTICS/SAVE levels.
- The worker-test setUp moves through GRADIENT (step 8) first,
  so the full 9-level chain is exercised end-to-end on the live
  DB before OPTIMIZE.
