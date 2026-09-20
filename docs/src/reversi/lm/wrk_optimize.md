# reversi/lm/wrk_optimize.py
The OPTIMIZE worker — the pipeline's optimizer level. `_up` implements a 4-step recipe: (1) consult the existing
checkpoint (if any) through the two hlp_optimize gates, deciding between completed-load, warm-resume and scratch; (2)
build the two lbfgs wrappers (`logger_fn` → `ctx.log_event`, `save_fn` → intermediate INCOMPLETE checkpoints); (3) run
`lbfgs` (opt_lbfgs) with the GRADIENT-level `ctx.fg` closure (float32 contract); (4) update the context (`w`,
`opt_info`, `w_checksum`) and save the final checkpoint. The checkpoint is written on EVERY run (final save
unconditional; intermediate only when `save_every_n > 0`) and read only when
`checkpoint_path.exists() and ctx.use_cache` (a cache-disabled run still warms the checkpoint).

## API

| name | contract |
|---|---|
| `wrk_optimize()` | the factory — `@validate_call(config=ConfigDict(arbitrary_types_allowed=True))` (all 18 worker factories share the pattern) returning `Worker("OPTIMIZE", _up, _down)` |

## Architecture

- `_up`:
  - config + `checkpoint_path = base_dir / optimization. checkpoint_file` (config-named, not rlmwf_-prefixed);
    `w_init = ctx.w`; `min_grad_value, _ = opt_cfg.min_grad` (the count is unused).
  - step 1: the checkpoint gate `checkpoint_path.exists() and ctx.use_cache` (the context field the CONFIG worker
    populated — NOT `cfg.use_cache`), with the try/except: a load raising `RuntimeError` (the 2 header gates, the
    checksum mismatch), `binio.BinaryFormatError` (corrupted framing, malformed sidecar) or `OSError` (missing
    file/sidecar) → WARN + `unlink(missing_ok=True)` of content + sidecar → scratch. Then the 3-way decision: the 3-gate
    consistency check (incl. the ridge gate) → mismatch: WARN "Starting from scratch"; converged or `iters >= max_iters`
    → completed: load cp['w'] + `w_checksum` + `opt_info`, `return` (skip lbfgs); `iters < max_iters` → warm-resume:
    w_init + the initial sl/yl/rho/iter from the checkpoint (the old trailing else was unreachable — iters is an int).
  - step 2: `logger_fn` (INFO) + `save_fn` (7 params, matches the lbfgs hint; writes an INCOMPLETE/non-converged
    checkpoint; `iters=k+1` — completed-count semantics, as the final save).
  - step 3: the `lbfgs` call: `fg=ctx.fg`, `x0=w_init`, the 8 config scalars, both wrappers, the 4 warm-start kwargs.
  - step 4: `ctx.w = w_opt`, `ctx.opt_info = optimization_info_dict(info)`,
    `ctx.w_checksum = weights_compute_sha3_256_hash(w_opt)`, the final `save_optimization_checkpoint` (the `info` dict
    carries the 9 keys: w/converged/reason/iters/f/g_norm/sl/yl/rho).
- `_down`: clears `ctx.fg` and `ctx.w_checksum` + `ctx.opt_info`. `ctx.w` is deliberately KEPT: it is the re-optimized
  WMAPS weight vector; the WMAPS cache restores the zero-initialized value when that level recomputes.

## Verified invariants

Pinned by the `probes/verify_optimize.py` B + D + H tiers + the 3-test suite.

- Source shape (probe B1-B17): the 190-line file, the factory decorator + the pydantic/binio imports, the 16 lbfgs
  kwargs + the warm-start consumption (B13), the try/except, the `_down` scope, the header typo fix, the dead `Path`
  import gone.
- The worker-test source shape (probe D1-D11): the 175-line file, the gate, the idiom, the 3 step pins (GRADIENT=10,
  OPTIMIZE=11), the marker, the pins.
- The 6 live decision paths (probe H4-H8 + H6b): completed (no lbfgs in run 2, byte-identical weights), resume (warm
  start consumed), zed-inconsistent → scratch, ridge-only-inconsistent → scratch, use_cache=False → no load + checkpoint
  still saved (H7), corrupted checkpoint → delete + scratch + valid re-save (H8).
- The float32 contract flows through: `ctx.w` is float32 after 50 lbfgs iterations; `weights_compute_sha3_256_hash`
  (gated `NDArray[np.float32]`) never rejects.
- The base dir after a full run holds the 4 rlmwf_ cache pairs (04/05/07/08) + the checkpoint pair; no
  rlmwf_01*/02*/09*/10*/11* file (H1).

## Open issues

None.

## Conventions

- The checkpoint is the only level cache that is a plain dict (not a data class) and is NOT managed by cache_manager (no
  rlmwf_ prefix, config-named file, no delete-on-inconsistency — the worker's own 3-way decision replaces it; the
  try/except is the corruption recovery that cache_manager's load_fn has for the other levels).
- `_up` reads `ctx.use_cache` (context field) — a test that wants to gate the checkpoint load off must set
  `context.use_cache` after the CONFIG level has run (probe H7).
- The intermediate checkpoints' `iters` count completed iterations, so a resume starts exactly where the interrupted run
  stopped (no redundant iteration).

## Integration

- The 11th LM level; consumes `ctx.fg` (the GRADIENT-level closure) and the WMAPS-level `ctx.w` (zero-initialized at
  WMAPS compute time) + the `optimization` config block.
- Produces the model artifact of the pipeline: the optimized `ctx.w` + `ctx.w_checksum` + `ctx.opt_info` — the inputs of
  the GENERATE/VALIDATE/ANALYTICS/SAVE levels.
- The worker-test setUp moves through GRADIENT (step 10) first, so the full 11-level chain is exercised end-to-end on
  the live DB before OPTIMIZE.
