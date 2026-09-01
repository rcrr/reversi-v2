# twolm/lm_worker_optimize.py

Analysis date: 2026-09-01 — analysis session 26 (D-096, bring-in
analysis); fix campaign D-096 approved by Roberto in the same session
and applied in the same session (R2 "mettiamo try/catch", R4 _down
clears w_checksum + opt_info, T8/T9b/T10 + T1-T7 test items, M1/M2/
M4/M5). Brought in by Roberto (commit 1ebdd8b — the 10th active level
of the pipeline). Probe (scratch/verify_optimize.py, 92 checks, tiers
A–H, re-pinned post-campaign): 0 mismatches.

The OPTIMIZE worker — the pipeline's optimizer level. `_up` implements
a 4-step recipe: (1) consult the existing checkpoint (if any) through
the two rlm_optimize gates, deciding between completed-load,
warm-resume and scratch; (2) build the two lbfgs wrappers (`logger_fn`
→ `ctx.log_event`, `save_fn` → intermediate INCOMPLETE checkpoints);
(3) run `lbfgs` (opt_lbfgs) with the GRADIENT-level `ctx.fg` closure
(float32 contract, D-094 R1); (4) update the context (`w`,
`opt_info`, `w_checksum`) and save the final checkpoint. The
checkpoint is written on EVERY run (final save unconditional;
intermediate only when `save_every_n > 0`) and read only when
`checkpoint_path.exists() and ctx.use_cache` (the D-071 R1 pattern: a
cache-disabled run still warms the checkpoint).

## Suite status (session 26, post D-096)

- `test_lm_worker_optimize`: 3/0/0 live (1 class; all 3 tests
  DB-gated since D-096 T1 — the setUp moves through GRADIENT on a
  fresh base dir, so a live DB is required): the loss-decrease run,
  the max-iters → completed → checkpoint-reload run (byte-identical
  weights, no lbfgs in run 2), and the new T7 `_down` test (R4: fg +
  w_checksum + opt_info cleared, ctx.w kept).
- `test_rlm_optimize`: 19/0/0 (no DB — see test_rlm_optimize.md).
- Full discover: 598 tests, 71 skipped under `SKIP_REGAB_DB=1`, GREEN;
  ungated (live DB): 598 run, 17 skipped, GREEN. The full `-W error`
  discover is clean.

## State per Roberto

Pipeline-in-progress, 10 active levels (CREATED sentinel → CONFIG →
POSITIONS → FEATURES → INDEXES → WMAPS → DESIGN_MTR → ZED → GRADIENT
→ OPTIMIZE — the worker list in logistic_model.py; the 5 remaining
factory imports are commented: generate, vld_positions, validate,
analytics, save). The next line-by-line step is
`lm_worker_generate`. OPTIMIZE fix campaign (D-096) CLOSED: R1
(ridge gate moved into `is_optimization_cache_consistent` — a ridge
change now behaves exactly like a zed-checksum change; the "restart a
caldo" from warm weights parked as idea I-014 — "un'ottimizzazione
che svilupperei solo in seguito, se capiamo che ha un valore
pratico"), R2 (try/except around the checkpoint load — a corrupted
checkpoint is deleted and the run starts from scratch instead of
killing the worker), R3 (load verifies the SHA3-256 sidecar — "Sta li
per questo motivo!"), R4 (_down also clears w_checksum + opt_info;
ctx.w kept — it is the re-optimized WMAPS vector), T8/T9b/T10
(Aauthor typo, dead `Path` import, factory `@validate_call`), M1
(min_grad_count unused), M2 (unreachable else removed), M4
(cecksum ×2), M5 (intermediate save iters=k+1), plus the test batch
T1-T7 (gate, D-085 idiom, dead if-False, dead imports, stray
comment, the vacuous `assertNotIn` replaced with the real lbfgs
marker, the new `_down` test).

## Architecture (190 lines, post D-096)

- imports (L28-41): TYPE_CHECKING, pydantic (T10), binio (R2),
  Worker/Relevance, lbfgs, the 6 rlm_optimize names; `RLMContext`
  under TYPE_CHECKING (L43-44). T8 fixed the "Aauthor" header typo
  (L7); T9 removed the dead `Path` import.
- `__all__` L48; triple blanks L45-47 (house worker style, kept).
- `_up` (L52-176):
  - L53-62: config + `checkpoint_path = base_dir /
    optimization.checkpoint_file` (config-named, not rlmwf_-prefixed);
    `w_init = ctx.w`; `min_grad_value, _ = opt_cfg.min_grad` (M1).
  - L64-75: step 1 — the checkpoint gate `checkpoint_path.exists()
    and ctx.use_cache` (note: `ctx.use_cache`, the context field the
    CONFIG worker populated — NOT `cfg.use_cache`), with R2's
    try/except: a load raising `RuntimeError` (the 2 header gates,
    the R3 checksum mismatch), `binio.BinaryFormatError` (truncated /
    corrupted framing, malformed sidecar) or `OSError` (missing
    file/sidecar) → WARN + `unlink(missing_ok=True)` of the content
    and the sidecar → scratch.
  - L77-102: the 3-way decision: `is_optimization_cache_consistent`
    (the 3 gates incl. the R1 ridge gate) → mismatch: WARN "Starting
    from scratch"; `is_optimization_status_converged or iters >=
    max_iters` → completed: load cp['w'] + `w_checksum` +
    `opt_info`, `return` (skip lbfgs); `iters < max_iters` →
    warm-resume: `w_init`/`initial_sl`/`initial_yl`/`initial_rho` /
    `initial_iter` from the checkpoint. M2: the old trailing else was
    unreachable (iters is an int) — removed, comment kept (L100-102).
  - L104-129: step 2 — `logger_fn` (INFO) + `save_fn` (7 params,
    matches the lbfgs hint; writes an INCOMPLETE/non-converged
    checkpoint; M5: `iters=k + 1` — completed-count semantics, as the
    final save).
  - L131-149: step 3 — the `lbfgs` call: `fg=ctx.fg`, `x0=w_init`,
    the 5 config scalars, both wrappers, the 4 warm-start kwargs.
  - L151-176: step 4 — `ctx.w = w_opt`, `ctx.opt_info =
    optimization_info_dict(info)`, `ctx.w_checksum =
    weights_compute_sha3_256_hash(w_opt)`, the final
    `save_optimization_checkpoint` (the `info` dict carries the 9
    keys: w/converged/reason/iters/f/g_norm/sl/yl/rho).
- `_down` (L178-185): clears `ctx.fg` and — R4 (D-096) — `ctx.w_checksum`
  + `ctx.opt_info`. `ctx.w` is deliberately KEPT (comment L181-183):
  it is the re-optimized WMAPS weight vector; the WMAPS cache restores
  the zero-initialized value when that level recomputes.
- `lm_worker_optimize` factory (L187-190): T10 added the
  `@validate_call` decorator (all 9 worker factories now share the
  pattern).

## Verified facts (probe tiers B, H)

- The factory's decorator + the 16 lbfgs kwargs + the warm-start
  consumption are pinned statically (B4, B13) and behaviorally (H5:
  a crafted INCOMPLETE checkpoint resumes with its sl/yl/rho and the
  0-based start index).
- All 6 decision paths verified live (H4-H8): completed (no lbfgs in
  run 2, byte-identical weights), resume (warm start consumed),
  zed-inconsistent → scratch, ridge-only-inconsistent → scratch (R1,
  H6b), use_cache=False → no load + checkpoint still saved (H7),
  corrupted checkpoint → delete + scratch + valid re-save (H8).
- The float32 contract flows through: `ctx.w` is float32 after
  50 lbfgs iterations; `weights_compute_sha3_256_hash` (gated
  `NDArray[np.float32]`) never rejects.
- The base dir after a full run holds exactly the 12 expected files
  (the 5 rlmwf_ cache pairs 01/02/04/05/06 + the checkpoint pair);
  no rlmwf_03*/07*/08* file (H1).

## Minor notes

- The "Atomically" claim that used to sit in rlm_optimize's save
  comment was dropped (M9): the checkpoint write is in-place; the R2
  delete+scratch recovery is what makes a crash-mid-save recoverable.
- The intermediate checkpoints' `iters` now count completed
  iterations (M5), so a resume starts exactly where the interrupted
  run stopped.
- `_up` reads `ctx.use_cache` (context field) — a test that wants to
  gate the checkpoint load off must set `context.use_cache` after the
  CONFIG level has run (probe H7).

## Integration notes

- Consumes `ctx.fg` (the GRADIENT-level closure, D-093/D-094) and the
  WMAPS-level `ctx.w` (zero-initialized at WMAPS compute time).
- Produces the model artifact of the pipeline: the optimized `ctx.w`
  + `ctx.w_checksum` + `ctx.opt_info` — the inputs of the future
  GENERATE/VALIDATE/ANALYTICS/SAVE levels.
- The checkpoint is the only level cache that is a plain dict (not a
  data class) and that is NOT managed by cache_manager (no rlmwf_
  prefix, config-named file, no delete-on-inconsistency — the
  worker's own 3-way decision replaces it; the R2 try/except is the
  corruption recovery that cache_manager's load_fn has for the other
  levels).

## Appendix — line reference

190 lines, as of D-096 (169 at the bring-in; D-096: +1 pydantic
import +1 binio import, +1 decorator, +9 R2 lines, +2 R4 lines, the
M2/M5 comments, in-place typo fixes, ws sweep).

- L28-44: imports + TYPE_CHECKING
- L45-47: triple blanks (house worker style)
- L48: `__all__`
- L52-176: `_up` (config L53-62; checkpoint gate L64-75 with R2
  try/except; 3-way decision L77-102; wrappers L104-129 with M5
  L119-121; lbfgs L131-149; final update+save L151-176)
- L178-185: `_down` (R4: fg + w_checksum + opt_info)
- L187-190: `lm_worker_optimize` factory (T10 decorator)
