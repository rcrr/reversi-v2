<!-- ARCHIVED — D-106 step 12 (the docs/ rewrite, 2026-09-04): the
     complete session-23 analysis (D-086) + the D-087/D-088
     fix-campaign narrative moved out of docs/src/twolm/rlm_wmaps.md
     per docs_rules.md §1/§4. This is a frozen historical record:
     it is never updated. Stale-in-current-context notes: (1) the
     "60 checks" figure is stale — the probe's own D-087 re-pin
     header says 64; the current probes/verify_wmaps.py (the
     4091e72 move) has 53 check calls: A1-A12 (module source),
     B1-B9 (worker source), C1-C15 (live-DB pipeline), E9 (the
     per-feature wmap row-count contiguity fact — the only E
     survivor), F1-F3 + F5 (cross-fixture facts). The D-106
     step-3 class c deletions: E0 + the test-source extraction
     machinery, E1-E6, E7/E8 (the golden-content re-derivation →
     TestLMWorkerWmapsExactValues is now the single source of
     truth), and F4/F6 moved to the hub verify_logistic_model.py
     (4091e72). The probe's "Run from ... scratch/verify_wmaps.py"
     line is pre-move; (2) the "535 tests / 61 skipped"
     full-discover figure predates steps 3-10 (current: 664/87
     gated); (3) the V1-V5 fact list + the R1/T4/T5/T9/M1
     narrative are frozen history. -->

# twolm/rlm_wmaps.py

Analysis date: 2026-08-31 — analysis session 23 (D-086); fix
campaign D-087 approved by Roberto ("Procedi su tutto") and applied
in the same session. Brought in by Roberto together with
lm_worker_wmaps in 73b4342 (2026-08-31, the 6th active level of the
pipeline — the import + worker-list entry in logistic_model.py were
the only 2 lines the commit touched there; RLMContext already
carried all 7 Wmaps blackboard fields from first import). Probe
(scratch/verify_wmaps.py, 60 checks, tiers A–F, re-pinned in D-087
to the post-campaign state): 0 mismatches.

The WMAPS domain module of the RLM pipeline: the
`ReversiLogisticModelWMaps` data object (the 6 weight-map arrays +
the two metadata scalars) + the 4 public functions (store / load /
compute / is_cache_consistent) + the duck-typed
`compute_sha3_256_hash` — the data object of the 6th active level
(CREATED sentinel → CONFIG → POSITIONS → FEATURES → INDEXES →
WMAPS) and the THIRD cache_manager consumer in the pipeline (after
POSITIONS D-079 and INDEXES D-083).

## Suite status (session 23, post D-087)

- `test_rlm_wmaps`: 13/0/0 (4 classes; no DB, no gate — the
  handcrafted-mock compute pins, the consistency compares, the
  store/load cycle, the golden hash + sidecar/error-path pins
  (D-087 T10), the init validation).
- `test_lm_worker_wmaps`: 3/0/0 (2 classes; the end-to-end cache
  round-trip pin + the rlm_01 golden-content pin — the setUp moves
  through INDEXES on a fresh base dir, so a live DB is required;
  DB-gated since D-087 T1).
- Full discover: 535 tests, 61 skipped under `SKIP_REGAB_DB=1`
  (17 PERF + 35 regab + 2 positions + 2 features + 2 indexes + 3
  wmaps), GREEN; ungated (live DB): 535 run, 17 skipped (PERF only),
  GREEN.

## State per Roberto

Pipeline-in-progress, 6 active levels, enabled line-by-line by
Roberto in 73b4342 (uncommented the `lm_worker_wmaps` import +
worker-list entry, added the two modules + the two tests + the
rlm_01.json fixture). The next line-by-line step is
`lm_worker_design_matrix` (the next commented entry, L46). WMAPS
fix campaign (D-087) CLOSED: rlm_wmaps T4/T5/T9 fixed + the R1
contract documented; lm_worker_wmaps T6-T8 fixed; both test files
T1-T4 + T9 + T10 fixed (13 → the full new-coverage suite).

## Architecture (316 lines, post D-087)

- `ReversiLogisticModelWMaps` (L49-121): plain class, no dataclass
  / pydantic model. `__init__` (L92-108, `@validate_call
  (config=ConfigDict(arbitrary_types_allowed=True))`) with 8 fields
  — `rlm_indexes_checksum: str`, `cut_off: int`, `feature_w_ranges:
  np.ndarray` (F,3) int64 [fallback, w_min, w_max] per feature,
  `iwmap_feature_offset: np.ndarray` (F+1,) uint32, `iwmap:
  np.ndarray` (K,) int64 (−1 = configuration unseen in the
  dataset), `wmap: np.ndarray` (W,3) int64 [fid, config_id_or_−1,
  freq], `wmap_fallback: np.ndarray` (F_cut,3) int64, `w:
  np.ndarray` (W,) float32 — assigned by reference (no copy).
  `compute_sha3_256_hash` (L110-120, `@validate_call`):
  `sha3_256` over the tobytes of the 6 arrays in declaration order
  (NOT the 2 scalars) — the duck-typed data-checksum hook
  cache_manager invokes (the 3rd return element, the D-071 T2
  pattern).
- `rlm_wmaps_store_to_file` (L123-140, `@validate_call`):
  `filename: str | Path` → Path; `binio.BinaryWriter` —
  `write_header(description, version=1)` (description =
  `"ReversiLogisticModelWMaps binary data file"`) →
  `write_string(rlm_indexes_checksum)` → `write_i32(cut_off)` →
  `write_array` ×6 (the 6 arrays in declaration order). The
  docstring is the plain "Saves the WMaps instance to a binary
  file." (no sidecar overpromise — the pipeline-flow sidecar is
  written by cache_manager, the D-072 machine).
- `rlm_wmaps_load_from_file` (L142-179, `@validate_call`):
  `checksum: bool = True` — when True,
  `binio.verify_sha3_256_sidecar(filename)` first; mismatch →
  RuntimeError "The checksum file signature doesn't match with
  current file." (the D-072 binio sidecar API, as in regab). Then
  the header gate: wrong description → RuntimeError "The file is
  not a proper {expected_description}."; wrong version → RuntimeError
  "File version mismatch: found {version}, expected
  {expected_version}". Then read_string + read_i32 + read_array ×6
  → a fresh `ReversiLogisticModelWMaps`.
- `rlm_wmaps_compute` (L181-309): NO `@validate_call` — the source
  documents why (L181: "Here validation is not possible, it brings
  in a convoluted issue with circular imports" — the same note as
  rlm_indexes L166; D-087 T5). The docstring carries the D-087 R1
  contract: the input pindexes matrix is DENSE by contract — every
  cell holds a valid configuration index in 0..n_configurations − 1
  (the indexes are unsigned and never −1), so the −1 'unseen
  configuration' sentinel can only appear in the OUTPUT iwmap.
  Body: `cut_off = ctx.cfg.stat_model.frequency_cut_off`; per
  feature: `cols = list(range(col_offset, col_offset + f.n_instances))`
  (the pindexes column slice), `np.unique(..., return_counts=True)`,
  `mask = stats[:,1] < cut_off` (below-cutoff configs share the
  feature's single fallback weight — config_id −1 in the wmap);
  the fallback row is written first, then the above-cutoff
  configs; `f_iwmap[stats[:,0].astype(np.int64)] = stats[:,2]`
  (L252); the wmap rows are `[fid, config_id_or_−1, freq]`;
  `w = np.zeros(next_w, dtype=np.float32)`.
- `rlm_wmaps_is_cache_consistent` (L312-316): NO `@validate_call`
  (same constraint, no comment — as in rlm_indexes); the 2-field
  metadata compare — `cached.rlm_indexes_checksum ==
  ctx.rlm_indexes_checksum` AND `cached.cut_off ==
  ctx.cfg.stat_model.frequency_cut_off` (pure; no DB params in the
  module). This is the cache_manager `validate_fn` (business
  validity, step 3 — a mismatch deletes + recomputes, the D-071
  R2 pattern).

## Verified facts (D-086/D-087 probe — 60 checks, 0 mismatches)

- V1 (A-tier): structure — 316 lines; `__all__` = the 5 public
  names; exactly 4 `@validate_call` decorators (init,
  compute_sha3_256_hash, store, load — NOT compute /
  is_cache_consistent; the L181 no-validation comment added in
  D-087 T5); the store write order; the load checksum default +
  sidecar verify + the 3 RuntimeError messages; the 2-field
  is_cache_consistent compare + no DB params; 0 non-comment
  trailing-whitespace lines (D-087 T9); the accumulate import gone
  (D-087 T4).
- V2 (B-tier): the worker file — 91 lines; `__all__ =
  ['lm_worker_wmaps']`; the factory WITH `@validate_call` (D-087
  T6); the RLMContext import under TYPE_CHECKING; the full
  7-kwargs cache_manager wiring with the
  `load_fn = lambda path: rlm_wmaps_load_from_file(path,
  checksum=False)` shape (D-087 T7); `_down` clears all 7
  attributes INCLUDING `ctx.wmaps_obj_checksum` (D-087 T8); 0
  non-comment trailing-whitespace lines.
- V3 (E0-E9, live DB): the golden content re-derived independently
  — the pipeline run on rlm_01.json (cut_off 2; F=4 INTERCEPT /
  LMC / DIAG3 / CORE; K=174) compared against the test literals
  extracted from the test source (the single source of truth):
  feature_w_ranges `[[−1,0,0],[1,1,4],[5,5,15],[16,16,20]]`
  int64; iwmap_feature_offset `[0,1,66,93,174]` uint32; iwmap
  (174,) int64 (mostly −1); wmap (21,3); wmap_fallback (10,3) all
  freq 1; w = 21 float32 zeros. The fallback wmap rows' freqs ==
  the sums of the wmap_fallback rows per feature; the per-feature
  w ranges are contiguous; NO −1 sentinel rows in the wmap
  (the fixture pindexes is dense — the R1 contract holds for
  the fixture).
- V4 (live DB, cross-run): a second instance on the same base_dir:
  "Cache successfully loaded and validated", no "Executing heavy
  computation"; the flat `rlmwf_05_WMAPS.dat` + `.SHA3-256`
  (the D-078 machine-level naming).

## Issues — RESOLVED (D-087)

- **R1 — the −1 input sentinel (the design question). RESOLVED as
  NO-GUARD, by Roberto's contract:** "non succede mai che un
  indice o un pindice (principale) sia −1. Gli indici sono degli
  uint, sono per definizione un numero compreso tra 0 e
  n_configurations − 1." The input pindexes matrix is therefore
  dense by contract, and the unguarded `f_iwmap[stats[:,0]]`
  (L252) is correct: `stats[:,0]` from `np.unique` on a dense
  matrix is always in 0..n_configurations−1. The contract is now
  documented in the `rlm_wmaps_compute` docstring (so a future
  change to the input contract is a deliberate, documented act).
  No code guard added.

## Minor notes — RESOLVED (D-087)

- **T4 FIXED**: the dead `from itertools import accumulate` import
  removed (the offsets use `np.cumsum`).
- **T5 FIXED**: the no-validation note added above
  `rlm_wmaps_compute` (L181) — the exact rlm_indexes L166 wording,
  documenting the TYPE_CHECKING circular-import constraint for
  both the compute and the is_cache_consistent functions.
- **T9 FIXED**: the 23 non-comment trailing-whitespace lines
  stripped (incl. the two code lines with trailing space:
  `above_mask = ~mask` and the `fallback_details_table = ...`
  assignment); scope as in D-078 M3: the license-header `# ` lines
  stay.
- **M1 corrected (D-088)**: the "9-space `__init__` indent"
  reported in D-087 was a misread — the body (L101-108) is
  verified to carry exactly the canonical 8-space indent
  (per-line `len(l) - len(l.lstrip(' ')) == 8` check). No code
  change; Roberto asked for the alignment (2026-08-31) and the
  verification showed it was already aligned.

## Integration notes

- Pipeline ordering: `ctx.rlm_indexes_checksum` (INDEXES) and
  `ctx.cfg.stat_model` (CONFIG) + `ctx.feature_set` (FEATURES) +
  the pindexes column layout must all be set before
  `rlm_wmaps_compute` runs — the SM half-open interval semantics
  guarantee every up-move to step 5 passes through all of them.
- The worker (lm_worker_wmaps) consumes the injected full-path
  closure (`get_cache_file_full_path_for_current_level`), so the
  flat `rlmwf_05_WMAPS.dat` naming comes from the D-078
  machine-level prefix concatenation — no per-worker naming code.
- `is_allowed = ctx.use_cache` — the CONFIG worker's switch is
  consumed (as in POSITIONS/INDEXES): with `use_cache=False` the
  level always recomputes but still warms the cache file (the
  D-071 R1 pattern).
- The two checksums are distinct (as in INDEXES):
  `wmaps_obj_checksum` = the DATA checksum (sha3_256 over the 6
  raw array tobytes — the duck-typed `compute_sha3_256_hash`,
  returned by cache_manager as the 3rd element); the `.SHA3-256`
  sidecar = the FILE checksum (binio `sha3_256sum` format over the
  serialized `.dat`). `is_cache_consistent` compares the metadata
  (rlm_indexes_checksum + cut_off) only — pure compare, no
  recompute.

## Appendix — line reference

316 lines, as of D-087 (311 at 73b4342 arrival).

- L28-37: imports (the accumulate import removed, D-087 T4;
  pydantic L35; binio L37)
- L42-47: `__all__`
- L49-121: `ReversiLogisticModelWMaps` (`__init__` L92-108,
  `compute_sha3_256_hash` L110-120)
- L123-140: `rlm_wmaps_store_to_file`
- L142-179: `rlm_wmaps_load_from_file` (L145-148 checksum gate,
  L150-157 header gate)
- L181-309: `rlm_wmaps_compute` (L181 no-validation comment
  [T5]; the R1 contract in the docstring; the pindexes column
  slice L~226; the L252 f_iwmap scatter)
- L312-316: `rlm_wmaps_is_cache_consistent`
