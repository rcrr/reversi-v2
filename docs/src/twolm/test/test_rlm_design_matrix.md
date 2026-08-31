# twolm/test/test_rlm_design_matrix.py

Created date: 2026-08-31 — session 23 (D-090 T6), the dedicated
data-object suite added by the DESIGN_MTR fix campaign after
Roberto's approval ("Procedi su tutti i T, e R1"). The WMAPS level
has an equivalent (test_rlm_wmaps, 13 tests); the DESIGN_MTR level
arrived with only the worker test — this file closes the coverage
gap: the compute math on a handcrafted mock, the consistency
compare, the store/load cycle + the binio error paths, the golden
hash, the init validation. No DB, no gate.

Probe (scratch/verify_design_matrix.py, tier G, 0 mismatches).

## Suite status (session 23, post D-090)

- 12/0/0 (4 classes; no DB, no gate).
- Full discover: 550 tests, 64 skipped under `SKIP_REGAB_DB=1`,
  GREEN; ungated: 550 run, 17 skipped (PERF only), GREEN.

## State per Roberto

The new file of the D-090 fix campaign (T6). The house
conventions are followed throughout: the D-085 paths idiom
(TemporaryDirectory under CUSTOM_TMP_BASE, defensive tearDown),
the golden-literal pin style, the precise-message pins.

## Architecture (258 lines)

- Imports: `unittest`, `tempfile`, numpy + numpy.testing, `Path`,
  `SimpleNamespace`, `ValidationError` (pydantic), `binio`, the 5
  public names from `twolm.rlm_design_matrix`, `CUSTOM_TMP_BASE`
  from `twolm.test.paths`.
- `TestRLMDesignMatrixCompute` (L63-128, 2 tests): a
  `SimpleNamespace` dummy ctx (no DB) — 2 features (F0: 1 instance
  / 3 configs, F1: 2 instances / 2 configs),
  `iwmap_feature_offset [0,3,5]` uint32, `iwmap [1,0,0,2,3]`
  int64, a 4×3 uint32 pindexes matrix.
  - `test_compute` (L99): the golden math pin — `X[i,j] =
    iwmap[pindexes[i,j] + col_offsets[j]]` with
    `col_offsets = [0,3,3]` (repeat the feature start offsets per
    instance) → the 4×3 uint32 matrix
    `[[1,2,2],[1,3,3],[0,2,3],[0,3,2]]` (the hand-computed
    expected values in the comment), shape + dtype + exact-array
    asserts, and the `wmaps_obj_checksum` carry-over.
  - `test_compute_rejects_invalid_pindex` (L121): the guard pin —
    set `iwmap[2] = -1` (a pindex points at an unmapped slot) →
    `ValueError`, the precise "pindexes is referring an invalid
    value" message (the single guard left by D-090 R1).
- `TestRLMDesignMatrixCacheConsistency` (L130-152, 2 tests): the
  1-field metadata compare — `test_consistent_cache` (True on
  matching `wmaps_obj_checksum`), `test_inconsistent_checksum`
  (False on a mismatch).
- `TestRLMDesignMatrixIO` (L155-235, 6 tests): the binary
  round-trip on a `TemporaryDirectory` under `CUSTOM_TMP_BASE`
  (the D-085 idiom, created FIRST, defensive tearDown).
  - `test_store_and_load_cycle` (L179): the store/load round-trip
    with the `wmaps_obj_checksum` + X array (dtype uint32 +
    exact-array) asserts.
  - `test_compute_sha3_256_hash_golden` (L195): the golden hash of
    the known IO object — `da86a916...57b` pinned as a literal.
  - `test_load_with_valid_sidecar` (L201): the `checksum=True`
    path with a matching binio sidecar (the D-072 machine).
  - `test_load_with_mismatched_sidecar` (L208): corrupt the last
    byte of the `.dat` → the precise "checksum file signature
    doesn't match" RuntimeError.
  - `test_load_rejects_wrong_description` (L221): a hand-written
    header with a wrong description → "not a proper" RuntimeError.
  - `test_load_rejects_version_mismatch` (L229): a hand-written
    header with version 2 → "version mismatch" RuntimeError.
- `TestRLMDesignMatrixInit` (L238-254, 2 tests): `__init__`
  validation — `test_init_accepts_valid_arrays` (the valid 2-field
  object), `test_init_fails_with_invalid_X_type` (a str for X →
  `ValidationError`).

## Verified facts (D-090 probe tier G — 0 mismatches)

- G1-G7: 258 lines; 4 classes / 12 tests; the header makes NO DB
  claim (the file is DB-free — no `SKIP_REGAB_DB` string); the
  D-085 idiom applied (TemporaryDirectory + defensive tearDown);
  the golden hash literal pinned; the 3 RuntimeError pins + the
  ValidationError pin + the guard ValueError pin; 0 whitespace-only
  lines.

## Integration notes

- The compute mock mirrors the WMAPS compute mock (test_rlm_wmaps)
  in style — the same 2-feature layout (1/3 and 2/2) — so the
  X values can be hand-verified against the iwmap in the comment.
- The IO golden object is a small 2×3 uint32 matrix; its
  `compute_sha3_256_hash` (sha3_256 over `X.tobytes()` only) is
  the pinned literal — a regression in the hash or in the
  serialized array breaks it.
- The sidecar/error-path tests reuse the exact binio API and the
  exact RuntimeError messages the WMAPS IO tests pin — the
  D-072/D-071 house pattern, keeping the three cache-manager
  consumer suites (POSITIONS / INDEXES / WMAPS / DESIGN_MTR)
  mutually consistent.
- The dedicated suite is the one that would catch a future
  signature change to `rlm_design_matrix_*` independent of the
  pipeline (the worker test only exercises the end-to-end path).

## Appendix — line reference

258 lines, as of D-090 (created in the D-090 campaign).

- L44-59: imports
- L63-128: `TestRLMDesignMatrixCompute` (`test_compute` L99,
  `test_compute_rejects_invalid_pindex` L121)
- L130-152: `TestRLMDesignMatrixCacheConsistency` (2 tests)
- L155-235: `TestRLMDesignMatrixIO` (6 tests; the golden hash at
  L195-199)
- L238-254: `TestRLMDesignMatrixInit` (2 tests)
