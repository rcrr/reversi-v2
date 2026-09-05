<!-- ARCHIVED — D-106 step 13 (the docs/ rewrite, 2026-09-04): the
     complete session-23 analysis (D-089) + the D-090
     fix-campaign narrative moved out of
     docs/src/twolm/rlm_design_matrix.md per docs_rules.md
     §1/§4. This is a frozen historical record: it is never
     updated. Stale-in-current-context notes: (1) the "55 checks"
     figure — the current probes/verify_design_matrix.py (the
     4091e72 move) has 53 check calls: A1-A15 (module source),
     B1-B9 (worker source), C1-C14 (the worker-test source),
     D5-D8 + D10 (live-DB golden re-derivation survivors), F1 +
     F4 + F5 (cross-fixture facts), G1-G7 (the dedicated unit
     test source). The D-106 step-3 class c deletions: D0 + the
     test-source extraction machinery, D1-D4 (step 6 / shape /
     dtype / X == literal), D9 (flat-file existence) —
     test_lm_worker_design_matrix.py is now the single source of
     truth; F2/F3 moved to the hub verify_logistic_model.py
     V3c/V3d. The probe's "Run from ... scratch/
     verify_design_matrix.py" line is pre-move (cosmetic); (2) the
     "550 tests / 64 skipped" full-discover figure predates
     steps 3-10 (current: 664/87 gated); (3) the D-089 warning-fix
     + D-090 T4/R1/T5 + V1-V5 narrative is frozen history. -->

# twolm/rlm_design_matrix.py

Analysis date: 2026-08-31 — analysis session 23 (D-089); fix
campaign D-090 approved by Roberto ("Procedi su tutti i T, e R1")
and applied in the same session. Brought in by Roberto (the
UNCOMMITTED 2026-08-31 bring-in — the 7th active level of the
pipeline — the import + worker-list entry in logistic_model.py were
his; RLMContext already carried the `design_matrix` +
`design_matrix_checksum` blackboard fields from first import).
Probe (scratch/verify_design_matrix.py, 55 checks, tiers A–G,
re-pinned in D-090 to the post-campaign state): 0 mismatches.

The DESIGN_MTR domain module of the RLM pipeline: the
`ReversiLogisticModelDesignMatrix` data object (the (N,I) uint32
matrix X — the w-index of each (position, feature-instance) cell —
+ the `wmaps_obj_checksum` metadata) + the 4 public functions
(store / load / compute / is_cache_consistent) + the duck-typed
`compute_sha3_256_hash` — the data object of the 7th active level
(CREATED sentinel → CONFIG → POSITIONS → FEATURES → INDEXES →
WMAPS → DESIGN_MTR) and the FOURTH cache_manager consumer in the
pipeline (after POSITIONS D-079, INDEXES D-083, WMAPS D-085-era
wiring).

## Suite status (session 23, post D-090)

- `test_rlm_design_matrix`: 12/0/0 (4 classes; no DB, no gate —
  the handcrafted-mock compute pins (incl. the guard's ValueError),
  the consistency compare, the store/load cycle, the golden hash +
  sidecar/error-path pins, the init validation) — NEW in D-090 T6.
- `test_lm_worker_design_matrix`: 3/0/0 (2 classes; the end-to-end
  cache round-trip pin + the rlm_01 golden-content pin — the setUp
  moves through WMAPS on a fresh base dir, so a live DB is
  required; DB-gated since D-090 T1).
- Full discover: 550 tests, 64 skipped under `SKIP_REGAB_DB=1`
  (17 PERF + 35 regab + 2 positions + 2 features + 2 indexes + 3
  wmaps + 3 design_matrix), GREEN; ungated (live DB): 550 run, 17
  skipped (PERF only), GREEN. The full `-W error` discover is clean
  (the NumPy 2.5 warning fix below).

## State per Roberto

Pipeline-in-progress, 7 active levels, enabled by Roberto's
2026-08-31 bring-in (uncommented the `lm_worker_design_matrix`
import + worker-list entry, added the two modules + the test).
The next line-by-line step is `lm_worker_zed` (the next commented
entry). DESIGN_MTR fix campaign (D-090) CLOSED: rlm_design_matrix
T4/R1/T5 fixed; lm_worker_design_matrix T2/T3/T5 fixed; the worker
test T1/T5/T7 fixed; the dedicated `test_rlm_design_matrix.py`
added (T6).

## Architecture (133 lines, post D-090)

- `ReversiLogisticModelDesignMatrix` (L53-65): plain class.
  `__init__` (L55-58, `@validate_call
  (config=ConfigDict(arbitrary_types_allowed=True))`) with 2
  fields — `wmaps_obj_checksum: str`, `X: np.ndarray` (N,I) uint32
  (N = training positions, I = total feature instances) — assigned
  by reference (no copy). `compute_sha3_256_hash` (L60-65,
  `@validate_call`): `sha3_256` over `X.tobytes()` ONLY (the single
  data array — the duck-typed data-checksum hook cache_manager
  invokes, the 3rd return element, the D-071 T2 pattern).
- `rlm_design_matrix_store_to_file` (L68-78, `@validate_call`):
  `filename: str | Path` → Path; `binio.BinaryWriter` —
  `write_header(description, version=1)` (description =
  `"ReversiLogisticModelDesignMatrix binary data file"`) →
  `write_string(wmaps_obj_checksum)` → `write_array(X)`. The
  docstring is the plain "Saves the Design Matrix instance to a
  binary file." (no sidecar overpromise — the pipeline-flow
  sidecar is written by cache_manager, the D-072 machine).
- `rlm_design_matrix_load_from_file` (L81-104, `@validate_call`):
  `checksum: bool = True` — when True,
  `binio.verify_sha3_256_sidecar(filename)` first; mismatch →
  RuntimeError "The checksum file signature doesn't match with
  current file." (the D-072 binio sidecar API). Then the header
  gate: wrong description → RuntimeError "The file is not a proper
  {expected_description}."; wrong version → RuntimeError "File
  version mismatch: found {version}, expected {expected_version}".
  Then read_string + read_array → a fresh
  `ReversiLogisticModelDesignMatrix`.
- `rlm_design_matrix_compute` (L107-124): NO `@validate_call` —
  the source documents why (L107: "Here validation is not
  possible, it brings in a convoluted issue with circular imports"
  — the rlm_indexes L166 note class; D-090 T4). Body: `pindexes =
  ctx.rlm_indexes.indexes`; `col_offsets = np.repeat(
  ctx.iwmap_feature_offset[:-1], n_instances_per_feature)`;
  `pindexes_with_offsets = pindexes + col_offsets`; the SINGLE
  guard (L116-117): `np.any(ctx.iwmap[pindexes_with_offsets] ==
  -1)` → ValueError "It should never happen, pindexes is referring
  an invalid value." (the redundant 2nd guard merged away, D-090
  R1); `X = np.empty(pindexes.shape, dtype=np.uint32)`; the
  explicit-cast fix (L119-122, D-089): `np.take(ctx.iwmap.astype
  (np.uint32), pindexes_with_offsets, out=X)` — the `astype` is
  required because `ctx.iwmap` is int64 (the −1 unseen-config
  sentinel) while X is uint32: the implicit output kind-cast is
  deprecated in NumPy 2.5 (future: a hard error). Returns
  `ReversiLogisticModelDesignMatrix(wmaps_obj_checksum=ctx.
  wmaps_obj_checksum, X=X)`.
- `rlm_design_matrix_is_cache_consistent` (L130-133): NO
  `@validate_call` (same constraint, no comment — as in
  rlm_indexes / rlm_wmaps); the 1-field metadata compare —
  `dm.wmaps_obj_checksum == ctx.wmaps_obj_checksum` (pure; no DB
  params in the module). This is the cache_manager `validate_fn`
  (business validity, step 3 — a mismatch deletes + recomputes,
  the D-071 R2 pattern). Note: unlike WMAPS (2 fields) and INDEXES
  (3 fields), DESIGN_MTR carries no independent model params — the
  design matrix is a pure function of the WMAPS outputs + the
  pindexes, so the wmaps checksum alone covers it.

## Verified facts (D-089/D-090 probe — 55 checks, 0 mismatches)

- V1 (A-tier): structure — 133 lines; `__all__` = the 5 public
  names; exactly 4 `@validate_call` decorators (init,
  compute_sha3_256_hash, store, load — NOT compute /
  is_cache_consistent; the L107 no-validation note added in D-090
  T4); the store write order; the load checksum default + sidecar
  verify + the 3 RuntimeError messages; the 1-field
  is_cache_consistent compare; 0 non-comment trailing-whitespace
  lines (D-090 T5); the explicit-cast fix pinned (L119-122); the
  single guard pinned (L116-117).
- V2 (B-tier): the worker file — 80 lines; `__all__ =
  ['lm_worker_design_matrix']`; the factory WITH `@validate_call`
  + the pydantic import (D-090 T2); the full 7-kwargs
  cache_manager wiring with the `load_fn = lambda path:
  rlm_design_matrix_load_from_file(path, checksum=False)` shape
  (D-090 T3); `_down` clears BOTH `ctx.design_matrix` and
  `ctx.design_matrix_checksum` (the house shape — no gap this
  time); 0 whitespace-only lines (D-090 T5).
- V3 (D0-D10, live DB, rlm_01): the golden content re-derived
  independently — the pipeline run on rlm_01.json (cut_off 2;
  F=4, n_instances [1,1,4,1] (DIAG3 = 4 instances, CORE = 1),
  n_configurations [1,65,27,81], K=174) compared against the
  pinned (10,7) uint32 literal extracted from the test source
  (the single source of truth): X == pipeline output == the
  independent recompute `X = iwmap[pindexes + col_offsets]`; every
  value a valid w index (< W=21); the intercept column all 0; each
  feature's instance columns stay within its iwmap region; the
  flat cache files + the data checksum are correct.
- V4 (live DB, cross-run): a second instance on the same base_dir:
  "Cache successfully loaded and validated", no "Forcing
  computation"; the flat `rlmwf_06_DESIGN_MTR.dat` + `.SHA3-256`
  (the D-078 machine-level naming).
- V5 (G-tier): the dedicated test file — 258 lines; 4 classes / 12
  tests; no DB claim in the header (the file is DB-free); the
  D-085 idiom applied; the golden hash
  `da86a916e03c76befa6f5df70e6221b0f9a355173e356ea63fef89ea9719757b`
  pinned; the 3 RuntimeError pins + the ValidationError pin + the
  guard ValueError pin; 0 whitespace-only lines.

## Issues — RESOLVED (D-089/D-090)

- **The NumPy 2.5 DeprecationWarning (RESOLVED, D-089):** "Implicit
  casting of output to a different kind is deprecated. In a future
  version, this will result in an error." — the implicit int64
  (iwmap) → uint32 (X) output cast in `np.take(..., out=X)`. Value-
  correct today (verified identical), FATAL under `-W error` (the
  take aborts, X keeps the `np.empty` garbage), a hard error in
  future NumPy. Fix: the explicit source cast `ctx.iwmap.astype
  (np.uint32)` (a K×4-byte temp — small; the `out=` path and the
  guards preserved). Verified: Roberto's exact `-W error` command
  OK; the full `-W error` discover clean.
- **R1 — the two compute guards were redundant (RESOLVED, D-090,
  merged):** L115 `any(iwmap[pindexes_with_offsets] == -1)` and
  L118 `pindexes.size != count_nonzero(iwmap[pindexes_with_offsets]
  >= 0)` check the SAME invariant (iwmap values are −1 or ≥ 0, so
  "any −1" ⟺ "not all ≥ 0"). The redundant 2nd guard removed; the
  single −1 guard (the precise ValueError message) kept. The guard
  remains as a defensive re-check of the WMAPS R1 contract
  (pindexes dense, unsigned — the only way a referenced iwmap slot
  is −1 is a data bug, hence "It should never happen").

## Minor notes — RESOLVED (D-090)

- **T4 FIXED**: the no-validation note added above
  `rlm_design_matrix_compute` (L107) — the exact rlm_indexes L166
  wording (as in rlm_wmaps L181).
- **R1 FIXED**: the redundant 2nd guard removed (see Issues).
- **T5 FIXED**: the 3 non-comment trailing-whitespace lines
  stripped (L110, L120, L125 pre-campaign); scope as in D-078 M3:
  the license-header `# ` lines stay.

## Integration notes

- Pipeline ordering: `ctx.rlm_indexes` (INDEXES), `ctx.iwmap` +
  `ctx.iwmap_feature_offset` + `ctx.wmaps_obj_checksum` (WMAPS)
  must all be set before `rlm_design_matrix_compute` runs — the SM
  half-open interval semantics guarantee every up-move to step 6
  passes through all of them.
- The worker (lm_worker_design_matrix) consumes the injected
  full-path closure (`get_cache_file_full_path_for_current_level`),
  so the flat `rlmwf_06_DESIGN_MTR.dat` naming comes from the D-078
  machine-level prefix concatenation — no per-worker naming code.
- `is_allowed = ctx.use_cache` — the CONFIG worker's switch is
  consumed (as in POSITIONS/INDEXES/WMAPS): with `use_cache=False`
  the level always recomputes but still warms the cache file (the
  D-071 R1 pattern).
- The two checksums are distinct (as in WMAPS/INDEXES):
  `design_matrix_checksum` = the DATA checksum (sha3_256 over
  `X.tobytes()` — the duck-typed `compute_sha3_256_hash`, returned
  by cache_manager as the 3rd element); the `.SHA3-256` sidecar =
  the FILE checksum (binio `sha3_256sum` format over the
  serialized `.dat`). `is_cache_consistent` compares the metadata
  (`wmaps_obj_checksum`) only — pure compare, no recompute.
- X's dtype contract is uint32 (pinned 3× in the worker test +
  twice in the dedicated test): the w-index range is far below
  uint32 max; the uint32 choice matches the pindexes/offset dtypes
  (no upcast in `pindexes + col_offsets`).

## Appendix — line reference

133 lines, as of D-090 (135 at D-089, post the 2-line explicit-cast
fix; D-090: +1 note line, −2 redundant-guard lines, 3 ws lines
emptied in place).

- L29-38: imports (hashlib L31, pydantic L36, binio L38)
- L40-41: `RLMContext` under TYPE_CHECKING
- L45-49: `__all__` (the 5 public names)
- L53-65: `ReversiLogisticModelDesignMatrix` (`__init__` L55-58,
  `compute_sha3_256_hash` L60-65)
- L68-78: `rlm_design_matrix_store_to_file`
- L81-104: `rlm_design_matrix_load_from_file` (L84-86 checksum
  gate, L93-96 header gate)
- L107-124: `rlm_design_matrix_compute` (L107 no-validation note
  [T4]; the single guard L116-117 [R1]; the explicit-cast fix
  L119-122 [D-089])
- L130-133: `rlm_design_matrix_is_cache_consistent`
