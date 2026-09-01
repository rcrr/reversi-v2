# twolm/rlm_optimize.py

Analysis date: 2026-09-01 — analysis session 26 (D-096, bring-in
analysis); fix campaign D-096 approved by Roberto in the same session
(R1: keep the clipping-equivalent behavior, hot-restart parked as
idea I-014; R2: "mettiamo try/catch"; R3: "verifichiamo la checksum.
Sta li per questo motivo!"; R4: _down also clears w_checksum +
opt_info; T1–T15: "falli tutti"; M: "falli tutti") and applied in the
same session. Brought in by Roberto (commit 1ebdd8b — the 10th active
level of the pipeline — the import + worker-list entry in
logistic_model.py were his; RLMContext already carried the `w`, `fg`,
`w_checksum` and `opt_info` blackboard fields). Probe
(scratch/verify_optimize.py, 92 checks, tiers A–H, re-pinned in D-096
to the post-campaign state): 0 mismatches.

The OPTIMIZE domain module of the RLM pipeline — unlike every other
rlm_* level, the "cache" of this level is NOT a data class behind a
store/load/is_cache_consistent trio: it is a plain **checkpoint
dictionary** serialized with binio (the L56-57 design comment). Six
public names: `save_optimization_checkpoint` +
`load_optimization_checkpoint` (the binary round-trip),
`is_optimization_cache_consistent` + `is_optimization_status_converged`
(the two gates the worker consults), `optimization_info_dict` (the
lbfgs-info → context projection) and `weights_compute_sha3_256_hash`
(the duck-typed hash of the weight vector). The 10th active level
(CREATED sentinel → CONFIG → POSITIONS → FEATURES → INDEXES → WMAPS →
DESIGN_MTR → ZED → GRADIENT → OPTIMIZE); the next cache level takes
rlmwf_08 (the checkpoint file is config-named, not rlmwf_-prefixed).

## Suite status (session 26, post D-096)

- `test_rlm_optimize`: 19/0/0 (4 classes; no DB, no gate — the M10
  expansion of D-096: the IO round-trip + dtypes, the empty-history
  round-trip, the M6 length-mismatch fail-fast, the 2 header
  RuntimeError gates, the R3 corrupted-content gate, the file golden
  hash, the sidecar, the 3 helper tests, the 4 consistency branches
  (incl. the R1 ridge gate), the 4 status branches).
- `test_lm_worker_optimize`: 3/0/0 live (1 class; all 3 tests
  DB-gated since D-096 T1 — the setUp moves through GRADIENT on a
  fresh base dir, so a live DB is required).
- Full discover: 598 tests, 71 skipped under `SKIP_REGAB_DB=1` (17
  PERF + 35 regab + 2 positions + 2 features + 2 indexes + 3 wmaps +
  3 design_matrix + 2 zed + 2 gradient + 3 optimize), GREEN; ungated
  (live DB): 598 run, 17 skipped (PERF only), GREEN. The full
  `-W error` discover is clean.

## State per Roberto

Pipeline-in-progress, 10 active levels, enabled by Roberto's
2026-09-01 bring-in (commit 1ebdd8b: the two modules + the two tests,
uncommented the `lm_worker_optimize` import + worker-list entry).
The next line-by-line step is `lm_worker_generate` (the next
commented entry). OPTIMIZE fix campaign (D-096) CLOSED: R1 (the ridge
gate moved INTO is_optimization_cache_consistent — a ridge change now
behaves exactly like a zed-checksum change: "Starting from scratch";
the "restart a caldo" from warm weights is parked as I-014, "un
ottimizzazione che svilupperei solo in seguito, se capiamo che ha un
valore pratico"), R2 (try/except around the checkpoint load — a
corrupted checkpoint is deleted + the run starts from scratch instead
of killing the worker), R3 (load verifies the SHA3-256 sidecar — "Sta
li per questo motivo!"), R4 (_down clears w_checksum + opt_info in
addition to fg; ctx.w is kept — it is the re-optimized WMAPS vector),
T1–T15 all applied, M1–M10 all applied.

## Architecture (267 lines, post D-096)

- `save_optimization_checkpoint` (L59-107, `@validate_call`): the
  binary write — header "RGLM Optimization Checkpoint" v1, the two
  upstream checksum strings, ridge + min_grad as f32, max_iters/m/
  converged/reason/iters metadata, f + g_norm as f32, the single
  `len(sl)` length prefix, the w array, then one (s, y, rho) triple
  per history entry (zip). M6 (D-096): fail-fast `ValueError` when
  the three history lists differ in length (L77-82) — the file format
  cannot represent asymmetric lengths; previously the write would have
  emitted `len(sl)` triples worth of framing against `min(len)`
  written entries. M9 (D-096): the old "Atomically serialize" comment
  dropped (there is no temp-file + rename; the R2 delete+scratch
  recovery covers the crash-mid-save case).
- `load_optimization_checkpoint` (L110-170, `@validate_call`): the
  mirror read. R3 (D-096): after the header gates (description +
  version, 2 `RuntimeError`), the SHA3-256 sidecar is verified
  (L126) and a mismatch raises `RuntimeError` BEFORE any payload is
  trusted — the sidecar "sta lì per questo motivo". Returns the
  17-key checkpoint dictionary.
- `is_optimization_cache_consistent(ctx, cp)` (L174-211, no
  `@validate_call` — the L173 note, the rlm_indexes L166 class:
  `RLMContext` is a TYPE_CHECKING import, decorating would force the
  circular import). THREE gates (D-096 R1 added the third): the
  design-matrix checksum, the zed checksum, and — new —
  `math.isclose(ridge_regularization, cp ridge, rel_tol=1e-5,
  abs_tol=1e-8)`. Rationale (in the docstring): the ridge coefficient
  is part of the objective, so a change invalidates the checkpoint
  exactly like a zed change does. Each failed gate emits its own
  3×WARN diagnostic block (the per-parameter detail the worker's
  generic "Checkpoint config mismatch" WARN cannot carry — the other
  rlm_* is_cache_consistent functions compare pure data and are
  silent; here the function also inspects the live cfg, so the
  diagnostics stay in the function, M7 resolved as keep+document).
- `optimization_info_dict(lbfgs_info)` (L214-227, `@validate_call`):
  projects the lbfgs info dict to the 5 context keys
  (converged/reason/iters/f/g_norm); `KeyError` on a missing key.
- `is_optimization_status_converged(ctx, cp)` (L231-259, no
  `@validate_call` — the L230 note). D-096 slimmed it down: the ridge
  gate moved to the consistency gate (R1) and the dead
  `mg_is_consistent` isclose + its TRACE log were removed (M3). What
  remains: compare the stored g_norm with the CURRENT
  `min_grad[0]` tolerance. The tolerance is a judgement criterion,
  not part of the objective (docstring L232-243): a looser tolerance
  accepts a not-converged checkpoint, a stricter one forces further
  iterations — this is the "ricalcola la convergenza se hai ancora
  iterazioni a budget" behavior Roberto asked for.
- `weights_compute_sha3_256_hash(w)` (L262-267, `@validate_call`,
  `NDArray[np.float32]` gate): plain `sha3_256(w.tobytes())` — the
  duck-typed hash (no data class at this level).

## Verified facts (probe scratch/verify_optimize.py, 92 checks, 0
mismatches)

- The deterministic checkpoint bytes (the test fixture values) hash to
  `6e01ff86…1bd280`; the `.SHA3-256` sidecar is produced in the binio
  `sha3_256sum` format and matches.
- Round-trip preserves the dtypes: w/sl/yl float32, rho float64, f32
  metadata back through np.float32.
- The 4 checkpoint decision paths verified live on the pipeline
  (tiers H4–H8): completed (2nd instance: "already completed", zero
  lbfgs calls, byte-identical weights), resume (crafted INCOMPLETE
  checkpoint → "Resuming optimization from iteration 5" + the warm
  start sl/yl/rho consumed), zed-inconsistent (clipping 0.01→0.02 →
  "Starting from scratch"), ridge-only-inconsistent (R1: ridge 0.01→
  0.02 with an UNCHANGED zed checksum → "Starting from scratch", the
  same behavior as a clipping change), use_cache=False (no load, the
  checkpoint is still saved — the D-071 R1 pattern), corrupted
  checkpoint (R2+R3: the load raises, the worker deletes the file +
  sidecar, re-optimizes and re-saves a valid checkpoint).
- The f32-stored ridge/min_grad values never trip the isclose gates
  (f32 relative error ~6e-8 ≪ rel_tol 1e-5/1e-3): no false
  inconsistency on a round-tripped checkpoint.
- The float32 contract of the GRADIENT level (D-094 R1) is consumed
  losslessly: lbfgs `x0.copy()` keeps float32 end-to-end (ctx.w is
  float32 after 50 iterations) and the `NDArray[np.float32]` gate of
  `weights_compute_sha3_256_hash` can never reject a live weight
  vector.

## Minor notes

- M1: `min_grad_count` was unpacked but unused in the worker (now
  `min_grad_value, _ = opt_cfg.min_grad`).
- M2: the trailing "state is unrecognized" else was unreachable (iters
  is an int: `iters >= max` or `iters < max` always holds) — removed,
  the comment documents why.
- M4: "cecksum" → "checksum" (×2 in the worker).
- M5: intermediate checkpoints now store `iters=k+1` (completed-count
  semantics, as the final save) — a resume starts exactly where the
  interrupted run stopped (no redundant iteration).
- M7: the consistency/status functions log (WARN/TRACE) — deviation
  from the silent rlm_* shape, resolved as keep+document (the
  per-parameter diagnostics).
- M8: the checkpoint file name is config-driven
  (`optimization.checkpoint_file`), not rlmwf_-prefixed — intentional
  (a user-addressable checkpoint; the next cache level still takes
  rlmwf_08, verified in probe H1).
- The worker's `_up` reads `ctx.use_cache` (the context field the
  CONFIG worker populated from cfg) — not `cfg.use_cache`.

## Integration notes

- The worker (lm_worker_optimize.md) calls all six functions; the
  checkpoint is written on EVERY run (intermediate via lbfgs
  `save_fn` when `save_every_n > 0`, final unconditionally) and read
  only when `checkpoint_path.exists() and ctx.use_cache`.
- The checkpoint carries the design_matrix + zed checksums of the run
  that wrote it: any upstream change (positions, feature set,
  frequency clipping, logit clipping) or a ridge change invalidates
  it (the three gates).
- The `iters` field of the final checkpoint is the count of
  iterations performed; the lbfgs `info` dict carries the 9 keys the
  worker consumes (w/converged/reason/iters/f/g_norm/sl/yl/rho).

## Appendix — line reference

267 lines, as of D-096 (245 at the bring-in; D-096: +1 M6 check
block, +3 ridge gate lines, +4 R3 verify lines, −24 status-slimming
lines, +2 notes lines, ws sweep, in-place fixes).

- L2: header (T13 fixed: was "rglm.py", the original repo name)
- L28: `from __future__ import annotations`
- L30-43: imports (math, hashlib, numpy, npt, Path, typing — T9
  removed the dead `Tuple`; pydantic L37; binio + Relevance L39-40;
  TYPE_CHECKING L42-43)
- L47-52: `__all__` (the 6 public names)
- L56-57: the checkpoint-dict design comment
- L59-107: `save_optimization_checkpoint` (docstring L76; M6 check
  L77-82; writer L83; header L84; checksums L85-86; f32 pair L87-88;
  i32s + reason L89-93; f/g_norm L94-95; len + w L97-98; M9 comment
  L100-103; triple loop L104-107)
- L110-170: `load_optimization_checkpoint` (docstring L112-117;
  header gates L119-124; R3 verify L126-128; checksums L131-134;
  metadata L137-143; memory L146-153; return L154-170)
- L173: no-validation note [T11]
- L174-211: `is_optimization_cache_consistent` (3-gate docstring
  L175-189; dm gate L191-195; zed gate L197-201; ridge gate L203-208;
  INFO + return L210-211)
- L214-227: `optimization_info_dict`
- L230: no-validation note [T11]
- L231-259: `is_optimization_status_converged` (docstring L232-243;
  min_grad read L244-246; cp echoes L248-252; comparison L254-259)
- L262-267: `weights_compute_sha3_256_hash`
