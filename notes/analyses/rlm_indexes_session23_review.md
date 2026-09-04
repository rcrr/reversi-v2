<!-- ARCHIVED — D-106 step 11 (the docs/ rewrite, 2026-09-04): the
     complete session-23 analysis (D-083) + the D-084 fix-campaign
     narrative moved out of docs/src/twolm/rlm_indexes.md per
     docs_rules.md §1/§4. This is a frozen historical record: it
     is never updated. Stale-in-current-context notes: (1) the
     "56 checks" probe figure predates the D-106 probes/ move +
     hub centralization (4091e72) and the step-3 class c deletions
     (4e32427: B1, B9-B11, B14, C1, C6a/C6b moved to the test
     files — see the deletion notes inside the probe); the current
     probe is 52 check calls / 48 distinct labels (A1-A11, B2-B8
     + B12-B13 — B6-B8 repeat across the corruption variants,
     C2-C5 + C6c + C7, D1-D6, E1-E7, F1-F9); (2) the "516 tests /
     58 skipped" full-discover figure predates steps 3-10 (current:
     664/87 gated); (3) the V1-V12 fact list and the R1 + M1-M6
     campaign narrative are frozen history. -->

# twolm/rlm_indexes.py

Analysis date: 2026-08-31 — analysis session 23 (D-083); fix campaign
D-084 approved by Roberto ("Sì fai tutto") and applied in the same
session. Brought in by Roberto together with lm_worker_indexes in
a323e0f (2026-08-31, the 5th active level of the pipeline — the
import + worker-list entry in logistic_model.py were the only 2 lines
the commit touched there; RLMContext already carried the
`rlm_indexes` / `rlm_indexes_checksum` blackboard fields from first
import). Probe (scratch/verify_rlm_indexes.py, 56 checks, tiers A–F,
re-pinned in D-084 to the post-campaign state): 0 mismatches.

The INDEXES domain module of the RLM pipeline: the
`ReversiLogisticModelIndexes` data object (the 2-D uint32 index
matrix + its two metadata hashes) + the 4 public functions
(store / load / compute / is_cache_consistent) + the duck-typed
`compute_sha3_256_hash` — the data object of the 5th active level
(CREATED sentinel → CONFIG → POSITIONS → FEATURES → INDEXES) and the
SECOND cache_manager consumer in the pipeline (after POSITIONS,
D-079).

## Suite status (session 23, post D-084)

- `test_rlm_indexes`: 14/0/0 (5 classes; all file I/O mocked —
  `twolm.rlm_indexes.binio` patched, no temp dirs, no DB; the
  rds-only-differs `is_cache_consistent` test added in D-084 M2).
- `test_lm_worker_indexes`: 2/0/0 (1 class / 2 tests; the end-to-end
  cache round-trip pin — the setUp moves through POSITIONS on a
  fresh base dir, so a live DB is required; DB-gated since D-084 T2).
- Full discover: 516 tests, 58 skipped under `SKIP_REGAB_DB=1`
  (17 PERF + 35 regab + 2 positions + 2 features + 2 indexes),
  GREEN; ungated (live DB): 516 run, 17 skipped (PERF only), GREEN.

## State per Roberto

Pipeline-in-progress, 5 active levels (CREATED → CONFIG →
POSITIONS → FEATURES → INDEXES), enabled line-by-line by Roberto in
a323e0f (uncommented the `lm_worker_indexes` import L44 + worker
list entry, added the two modules + the two tests). The next
line-by-line step is `lm_worker_wmaps` (the next commented entry,
L45). INDEXES fix campaign (D-084) CLOSED: R1 + M1-M4 + M6 fixed
(M5 left as-is by design, documented in the source); lm_worker
indexes M1-M3 fixed; both test files T/M fixed.

## Architecture (190 lines, post D-084)

- `ReversiLogisticModelIndexes` (L52-91): plain class, no
  dataclass / pydantic model. `__init__` (L57-75) is
  `@validate_call(config=ConfigDict(arbitrary_types_allowed=True))`
  with 3 fields — `rds_checksum: str`, `feature_set_hash: str`,
  `indexes: IndexArray` — assigned by reference (no copy, probe B1).
  `IndexArray` (pattern.py L74) =
  `Annotated[npt.NDArray[np.uint32], BeforeValidator(
  validate_index_array)]` — the pydantic gate coerces/validates the
  array. `compute_sha3_256_hash` (L77-82, `@validate_call`):
  `sha3_256(self.indexes.tobytes()).hexdigest()` — the duck-typed
  data-checksum hook cache_manager invokes (the 3rd return element,
  D-071 T2 pattern). `__repr__` (L84-91, `@validate_call` — house
  style as in pattern.py / mobility.py): one-line summary with
  rds_checksum, feature_set_hash and the indexes shape (D-084 M6).
- `rlm_indexes_store_to_file` (L94-119, `@validate_call`):
  `filename: str | Path` → Path; `binio.BinaryWriter` —
  `write_header(description, version=1)` (description =
  `"ReversiLogisticModelIndexes binary data file"`) →
  `write_string(rds_checksum)` → `write_string(feature_set_hash)` →
  `write_array(indexes)`. Write order pinned (probe A5/B3). The
  docstring (L98-104) carries the D-084 R1 correction: the file is
  stored, but NO sidecar is written by this function — in the
  pipeline flow the sidecar is written by cache_manager.
- `rlm_indexes_load_from_file` (L127-165, `@validate_call`):
  `checksum: bool = True` — when True, `binio.verify_sha3_256_sidecar
  (filename)` first; mismatch → RuntimeError "The checksum file
  signature doesn't match with current file." (D-072 binio sidecar
  API, as in regab). Then the header gate: wrong description →
  RuntimeError "The file is not a proper {expected_description}.";
  wrong version (L150, `if version != expected_version:` — D-084 M4)
  → RuntimeError "The file version is not consistent, found
  {version}, expected {expected_version}". Then
  read_string ×2 + read_array → a fresh
  `ReversiLogisticModelIndexes`.
- `rlm_indexes_compute` (L167-175): NO `@validate_call` — the
  source documents why (L166: "Here validation is not possible, it
  brings in a convoluted issue with circular imports" — the
  `ctx: RLMContext` annotation is a string under `from __future__
  import annotations`; pydantic cannot resolve it, the import sits
  under TYPE_CHECKING; D-084 M5, left as-is by design). Body:
  `rds_checksum = ctx.rds_checksum`,
  `feature_set_hash = ctx.feature_set.hash`,
  `indexes = ctx.feature_set.compute_indexes(ctx.positions)` (the
  public FeatureSet API, feature.py) → fresh object.
- `rlm_indexes_is_cache_consistent` (L178-190): NO `@validate_call`
  (same constraint, no comment); the 2-field metadata compare —
  `cached_feature_set_hash == ctx.feature_set.hash` AND
  `cached_rds_checksum == ctx.rds_checksum` (pure; no DB params in
  the module, probe A7). This is the cache_manager `validate_fn`
  (business validity, step 3/4 — a mismatch deletes + recomputes,
  D-071 R2).

## Verified facts (D-084 probe — 56 checks, 0 mismatches)

- V1 (B1): init — attribute identity; `obj.indexes is` the exact
  ndarray passed in (stored by reference, not copied).
- V2 (B2): the data checksum = `sha3_256(indexes.tobytes()).
  hexdigest()` — independently recomputed.
- V3 (B3-B5): store → the flat `.dat`; load `checksum=False`
  round-trips all 3 fields + the uint32 dtype; load `checksum=True`
  (the default) with a valid binio-format sidecar round-trips.
- V4 (B6-B8): the error paths — a corrupted file +
  `checksum=True` → RuntimeError (the sidecar-mismatch message); a
  wrong header description → RuntimeError "The file is not a
  proper ..."; a wrong version (99) → RuntimeError "The file
  version is not consistent, found 99, expected 1".
- V5 (B9-B11): `is_cache_consistent` — True when both fields match;
  False when ONLY `feature_set_hash` differs; False when ONLY
  `rds_checksum` differs (the rds-only branch now has BOTH unit-test
  coverage (D-084 M2) and probe coverage).
- V6 (B12-B13): `compute` — a real fixture FeatureSet (the
  NoNameFeatureSet from test_lm_worker_features' fixture constants,
  public API) + a fabricated 2-position array: the (2, 16) uint32
  matrix is identical to `FeatureSet.compute_indexes` called
  directly; the two checksums come from the ctx (`rds_checksum` +
  `feature_set.hash`).
- V7 (B14): init rejects a non-str `feature_set_hash` (pydantic
  ValidationError).
- V8 (C1-C5, live DB): the pipeline integration —
  `move_to_step("INDEXES")` → step 4 / "INDEXES"; the base dir holds
  ONLY the flat `rlmwf_01_CONFIG.dat` + `.SHA3-256`,
  `rlmwf_02_POSITIONS.dat` + `.SHA3-256`, `rlmwf_04_INDEXES.dat` +
  `.SHA3-256` (no `rlmwf_03_FEATURES*` — the pure-compute level
  writes nothing); `ctx.rlm_indexes` set +
  `ctx.rlm_indexes_checksum` = `sha3_256(indexes.tobytes())` (the
  DATA checksum); the on-disk sidecar is the flat
  `sha3_256sum` line over the `.dat` (the FILE checksum — different
  from the data checksum, as in POSITIONS); `indexes` shape
  (N, 16) uint32 (N = the training position count; 16 = the fixture
  n_instances sum) and identical to the independent
  `feature_set.compute_indexes` recompute.
- V9 (C6a-c, live DB): cross-run — a second instance on the same
  base_dir: "Cache successfully loaded and validated", no
  "Executing heavy computation", `rlm_indexes` IDENTICAL (checksum +
  matrix).
- V10 (C7, live DB): `_down` (down to FEATURES) clears BOTH
  `ctx.rlm_indexes` and `ctx.rlm_indexes_checksum`.
- V11 (A1-A11): structure — 190 lines; `__all__` = the 5 public
  names; exactly 5 `@validate_call` decorators (init,
  compute_sha3_256_hash, `__repr__`, store, load — NOT compute /
  is_cache_consistent; D-084 M6 added the 5th); the compute
  no-validation comment (A4); the store write order (A5); the load
  checksum default + sidecar verify + the 3 RuntimeError messages
  (A6); the 2-field is_cache_consistent compare + no DB params (A7);
  the corrected store docstring (A8, D-084 R1); "together" spelled
  correctly (A9, D-084 M2); 0 non-comment trailing-whitespace lines
  (A10, D-084 M3); the compute body (A11).
- V12 (D1-D6, worker file): 80 lines; `__all__ =
  ['lm_worker_indexes']`; the factory returns
  `Worker("INDEXES", _up, _down)` WITH `@validate_call` (D3,
  D-084 M1); the RLMContext import under TYPE_CHECKING (D4); the
  full 7-kwargs cache_manager wiring with the
  `load_fn = lambda path: rlm_indexes_load_from_file(path,
  checksum=False)` shape (D5, D-084 M3 — as in the other cache
  workers post D-080); `_down` clears both attributes + 0 non-comment
  trailing-whitespace lines (D6, D-084 M2).

## Issues — RESOLVED (D-084)

- **R1 — the store docstring overpromise (as in regab D-079 /
  D-080). FIXED.** The docstring now reads "Saves the
  ReversiLogisticModelIndexes instance to a binary file." + the
  Note: "no SHA3-256 sidecar is written by this function — in the
  pipeline flow the sidecar is written by cache_manager." (the
  regab D-080 wording). Doc-only.

## Minor notes — RESOLVED (D-084)

- **M1 FIXED**: the 5 dead imports removed (`IntEnum`, `Protocol`,
  `BeforeValidator`, `AfterValidator`, `Field`) — the import block
  is now `hashlib` / `TYPE_CHECKING` / `validate_call, ConfigDict` /
  `Path` / `binio` / `IndexArray` / the TYPE_CHECKING RLMContext.
- **M2 FIXED**: the class docstring typo "togheter" → "together".
- **M3 FIXED**: the 4 non-comment trailing-whitespace lines (L113,
  L148, L153, L179 pre-fix) stripped; scope as in D-078 M3: the
  license-header `# ` lines stay.
- **M4 FIXED**: the version gate now compares the variable —
  `if version != expected_version:` (L150).
- **M5 left as-is (by design, documented in the source L166)**: NO
  `@validate_call` on `rlm_indexes_compute` /
  `rlm_indexes_is_cache_consistent` — the RLMContext annotation
  cannot be resolved by pydantic without a real import; the import
  is deliberately under TYPE_CHECKING. The house convention
  (`@validate_call` on all public functions) already has sanctioned
  deviations (the D-069 M11 gate functions re-raise).
- **M6 FIXED (optional, applied)**: `__repr__` added to
  `ReversiLogisticModelIndexes` (L84-91, `@validate_call` — house
  style as in pattern.py / mobility.py):
  `ReversiLogisticModelIndexes(rds_checksum='...',
  feature_set_hash='...', indexes=(N, 16))`.

## Integration notes

- Pipeline ordering: `ctx.rds_checksum` (POSITIONS) and
  `ctx.feature_set` (FEATURES) must both be set before
  `rlm_indexes_compute` runs — the SM half-open interval semantics
  guarantee every up-move to step 4 passes through both levels.
- The worker (lm_worker_indexes) consumes the injected full-path
  closure (`get_cache_file_full_path_for_current_level`), so the
  flat `rlmwf_04_INDEXES.dat` naming comes from the D-078
  machine-level prefix concatenation — no per-worker naming code.
- `is_allowed = ctx.use_cache` — the CONFIG worker's switch is
  consumed (as in POSITIONS): with `use_cache=False` the level
  always recomputes but still warms the cache file (D-071 R1).
- The two checksums are distinct (V8): `rlm_indexes_checksum` =
  the DATA checksum (sha3_256 over the raw uint32 bytes — the
  duck-typed `compute_sha3_256_hash`, returned by cache_manager as
  the 3rd element); the `.SHA3-256` sidecar = the FILE checksum
  (binio `sha3_256sum` format over the serialized `.dat`).
  `is_cache_consistent` compares the metadata hashes only (pure
  compare, no recompute) — same shape as POSITIONS'
  `is_cache_consistent` (D-079).

## Appendix — line reference

190 lines, as of D-084 (180 at a323e0f arrival).

- L28-42: imports (pydantic L33 [M1: the 5 dead names removed],
  pattern IndexArray L37, TYPE_CHECKING RLMContext L39-40)
- L44-48: `__all__`
- L52-91: `ReversiLogisticModelIndexes` (docstring L54 [M2 fixed],
  `__init__` L57-75, `compute_sha3_256_hash` L77-82,
  `__repr__` L84-91 [M6 added])
- L94-119: `rlm_indexes_store_to_file` (docstring L98-104 [R1
  fixed])
- L127-165: `rlm_indexes_load_from_file` (L135-138 checksum gate,
  L142-152 header gate [M4: L150 `if version != expected_version:`])
- L166-175: `rlm_indexes_compute` (L166 no-validation comment [M5])
- L178-190: `rlm_indexes_is_cache_consistent`
