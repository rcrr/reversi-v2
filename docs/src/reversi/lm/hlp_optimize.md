# reversi/lm/hlp_optimize.py
The OPTIMIZE domain module of the LM pipeline. Unlike every other rlm_* level, the "cache" of this level is NOT a data
class behind a store/load/is_cache_consistent trio: it is a plain **checkpoint dictionary** serialized with binio (the
design comment). Six public names: the binary round-trip pair, the two gates the worker consults, the lbfgs-info
projection and the duck-typed weight hash. The 11th active level (CREATED sentinel → CONFIG → FEATURES → SU_ANALYSIS →
POSITIONS → INDEXES → ANOVA → WMAPS → DESIGN_MTR → ZED → GRADIENT → OPTIMIZE).

## API

| name | contract |
|---|---|
| `save_optimization_checkpoint(filepath, ..., compressed=True)` | `@validate_call` — the binary write (header "RGLM Optimization Checkpoint" v1 + checksums + scalars + metadata + the history triples); LZ4 whole-file frame by default |
| `load_optimization_checkpoint(filepath, compressed=True)` | `@validate_call` — the mirror read (LZ4 guard + decompress by default); returns the 15-key checkpoint dict |
| `is_optimization_cache_consistent(ctx, checkpoint)` | the 3-gate check (NO `@validate_call` — see Conventions) |
| `is_optimization_status_converged(ctx, checkpoint)` | the g_norm-vs-tolerance judgement (NO `@validate_call` — the note) |
| `optimization_info_dict(lbfgs_info)` | `@validate_call` — projects the lbfgs 9-key info to the 5 context keys; `KeyError` on a missing key |
| `weights_compute_sha3_256_hash(w)` | `@validate_call`, `NDArray[np.float32]` gate — plain `sha3_256(w.tobytes())` (no data class at this level) |

## Architecture

- `save_optimization_checkpoint`: header + the two upstream checksum strings (design-matrix, zed) + ridge/min_grad as
  f32 + max_iters/m/converged/reason/iters + f/g_norm as f32 + the `len(sl)` length prefix + w + one (s, y, rho) triple
  per history entry (zip). Fail-fast `ValueError` on asymmetric history lengths, before the writer opens. The writer
  runs with `compressed=True` by default — the LZ4 whole-file frame; the sidecar is written by the binio writer
  (cache_manager re-writes it idempotently in the pipeline flow).
- `load_optimization_checkpoint`: the LZ4 guard + decompress (default) → the header gates (description + version, 2
  `RuntimeError`) → the R3 SHA3-256 sidecar verify BEFORE any payload is trusted → the 15-key dict.
- `is_optimization_cache_consistent` (the no-validation note — the hlp_indexes class): THREE gates: the design-matrix
  checksum, the zed checksum, `math.isclose(ridge, cp_ridge, rel_tol=1e-5, abs_tol=1e-8)` (the ridge is part of the
  objective — a change invalidates the checkpoint exactly like a zed change). Each failed gate emits its own 3×WARN
  diagnostic block (keep+document).
- `optimization_info_dict`: the 5 context keys (converged/reason/iters/f/g_norm), extras dropped.
- `is_optimization_status_converged` (the note): compare the stored g_norm with the CURRENT `min_grad[0]` tolerance — a
  judgement criterion, NOT part of the objective: a looser tolerance accepts a not-converged checkpoint, a stricter one
  forces further iterations.
- `weights_compute_sha3_256_hash`: the duck-typed data-checksum hook.

## Verified invariants

Pinned by the 83-check `probes/verify_optimize.py` + `test_hlp_optimize.py` (20 tests, no DB) + `test_wrk_optimize.py`
(3 DB-gated tests).

- Module source shape (probe A1-A20): 271 lines, the 6-name `__all__`, the design comment, the M6 check, the 3 gates,
  the R3 verify, the 2 no-validation notes.
- Worker source shape (probe B1-B17): the 190-line file, the decorator + pydantic/binio imports, the 16 lbfgs kwargs,
  the warm-start consumption, the try/except, the `_down` scope.
- The live-DB decision paths (probe H4-H8 + H6b, rlm_02): completed (2nd instance: "already completed", zero lbfgs
  calls, byte-identical weights); resume (crafted INCOMPLETE checkpoint → "Resuming optimization from iteration 5", warm
  start consumed); zed-inconsistent (clipping 0.01→0.02 → "Starting from scratch"); ridge-only-inconsistent
  (ridge 0.01→0.02, UNCHANGED zed checksum → scratch, as a clipping change); use_cache=False (no load, the checkpoint is
  still saved); corrupted (the load raises, the worker deletes file + sidecar, re-optimizes, re-saves).
- The determinism + round-trip facts: the deterministic compressed file (the LZ4 frame) hashes to
  `2a2f96dfcd6224bb799ecba92011cafafa36564ac770865cfc6d04e1e978633f`; the sidecar verifies; the dtypes survive (w/sl/ yl
  float32, rho float64, f32 metadata back through np.float32).
- The f32-stored ridge/min_grad never trip the isclose gates (f32 error ~6e-8 ≪ rel_tol 1e-5): no false inconsistency on
  a round-tripped checkpoint.
- The GRADIENT float32 contract is consumed losslessly: lbfgs `x0.copy()` keeps float32 end-to-end and the
  `NDArray[np.float32]` hash gate can never reject a live weight vector.

## Open issues

None.

## Conventions

- The checkpoint file name is config-driven (`optimization.checkpoint_file`), NOT rlmwf_-prefixed: a user-addressable
  checkpoint.
- No atomic write: no temp-file + rename — the delete+scratch recovery covers the crash-mid-save case.
- The 3-WARN diagnostic pattern in the consistency function is a documented deviation from the silent rlm_* shape.
- The checkpoint is deterministic for a given input (fixed header, fixed field order, no timestamps) — the golden-hash
  pins depend on it; the LZ4 frame keeps the determinism (same input → same frame, the python-lz4 defaults, no
  timestamps).

## Integration

- The worker (wrk_optimize.py) calls all six functions; the checkpoint is written on EVERY run (intermediate via the
  lbfgs `save_fn` when `save_every_n > 0`, final unconditionally) and read only when
  `checkpoint_path.exists() and ctx.use_cache`; it carries the design-matrix + zed checksums of the run that wrote it,
  so any upstream change or a ridge change invalidates it (the three gates).
- The `iters` field of the final checkpoint is the count of iterations performed; the lbfgs `info` dict carries the 9
  keys the worker consumes (w/converged/reason/iters/f/g_norm/sl/yl/rho).
