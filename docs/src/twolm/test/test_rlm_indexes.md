# twolm/test/test_rlm_indexes.py

Analysis date: 2026-08-31 — analysis session 23 (D-083); fix
campaign D-084 approved by Roberto ("Sì fai tutto") and applied in
the same session.

Roberto's file, brought in with the INDEXES enablement (a323e0f,
the line-by-line pipeline step 5). 5 classes / 14 tests / no
PERF. Green on first run (all file I/O mocked — `twolm.rlm_
indexes.binio` patched, no temp dirs, no DB). T1-T5 + M1-M2 all
resolved in D-084 (the rds-only-differs test added, 13 → 14 tests).

## Suite status (session 23, post D-084)

- `test_rlm_indexes`: 14/0/0 (no DB, no gates)
- Full discover: 516 tests, 58 skipped under `SKIP_REGAB_DB=1`
  (17 PERF + 35 regab + 2 positions + 2 features + 2 indexes),
  GREEN; ungated (live DB): 516 run, 17 skipped (PERF only), GREEN.

## Coverage

- Shared dummy (L58): `DUMMY_INDEXES = np.zeros((2, 2),
  dtype=np.uint32)` across the whole file.
- `TestReversiLogisticModelIndexes` (3 tests):
  - `test_init_success` (L64-78): the 3 attributes + `isinstance
    np.ndarray` + the uint32 dtype + `assertIs(obj.indexes,
    DUMMY_INDEXES)` (the by-reference storage pinned — the only
    test in the file that pins that contract).
  - `test_init_fails_with_invalid_hash_type` (L80-89): a
    non-str `feature_set_hash` (12345) is rejected — via the
    precise pydantic `ValidationError` since D-084 T3.
  - `test_init_fails_with_invalid_indexes_type` (L91-99): pins
    the `indexes: IndexArray` rejection (a list of lists) — the
    `rds_checksum=` added in D-084 T4 so the invalid `indexes`
    (not a missing argument) is the thing under test; `assert
    Raises(ValidationError)` since D-084 T3.
- `TestRlmIndexesStoreToFile` (2 tests, binio mocked):
  - `test_store_to_file_success` (L105-136): `BinaryWriter`
    instantiated with `Path(filename)` + the exact 4-call
    sequence pinned (`write_header(desc, 1)`, `write_string` ×2,
    `write_array`) — both `assert_has_calls(any_order=False)` and
    the full `method_calls ==` comparison.
  - `test_store_to_file_accepts_path_object` (L138-149): a
    `pathlib.Path` filename passes through to `BinaryWriter`
    unchanged.
- `TestRlmIndexesLoadFromFile` (5 tests, binio mocked):
  - `test_load_from_file_success_with_checksum` (L156-175): the
    default `checksum=True` calls `verify_sha3_256_sidecar`
    exactly once + the round-trip fields (feature_set_hash, the
    uint32 dtype, `assertIs` on the array). NOTE: both
    `read_string` mocks return the same "stored_hash", so
    `rds_checksum` is never asserted (M3, left as-is — probe
    B4 covers the rds field).
  - `test_load_from_file_success_without_checksum` (L178-189):
    `checksum=False` → `assert_not_called` on the sidecar verify.
  - `test_load_from_file_checksum_mismatch` (L192-199): the
    RuntimeError + "checksum file signature doesn't match".
  - `test_load_from_file_invalid_description` (L202-213): the
    RuntimeError + "not a proper".
  - `test_load_from_file_invalid_version` (L216-227): the
    RuntimeError + "version is not consistent".
- `TestRlmIndexesCompute` (1 test, NO mock — the L235 comment
  "The module is not mocked; only a fake 'model' object is
  created" says so, English since D-084 T5): a MagicMock ctx;
  pins `compute_indexes` called once with the ctx positions
  ("dummy_positions" — a string, the mock absorbs it), the
  resulting `feature_set_hash`, and `assertIs` on the returned
  array.
- `TestRlmIndexesIsCacheConsistent` (3 tests since D-084 M2):
  - `test_is_cache_consistent_returns_true` (L257-270): both
    fields "identical_hash" → True.
  - `test_is_cache_consistent_returns_false` (L272-285): ONLY
    the feature_set_hash differs ("live_hash" vs
    "outdated_cached_hash", rds identical) → False.
  - `test_is_cache_consistent_returns_false_rds_differs` (L287-
    299, D-084 M2): ONLY the rds_checksum differs
    ("live_hash" vs "outdated_cached_hash", feature_set_hash
    identical) → False. Both single-field branches now pinned.

The suite is a solid per-function pin of the store/load contract
(exact call sequence, all 3 RuntimeError messages, both
checksum flags) + the compute/is_cache_consistent logic. The
former coverage gaps are closed (M2 — the rds-only branch is
now a 3rd unit test; M3 — the rds value on the load path stays
probe-covered, B4).

## Defects — RESOLVED (D-084)

- **T1 FIXED (F3)**: the dead import `from twolm.pattern import
  IndexArray` removed (it had zero code-level uses — the only
  other textual occurrence was a docstring; verified with an AST
  walk in the D-083 probe).
- **T2 FIXED (F4)**: header grammar — "How to run the
  rlm_indexes unit tests." (the established pattern).
- **T3 FIXED (F7)**: the 2 broad `assertRaises(Exception)`
  replaced with the precise pydantic `ValidationError` (import
  added, L51) — the test_lm_worker_config T2 / test_mobility T2
  pattern.
- **T4 FIXED (F7)**: `test_init_fails_with_invalid_indexes_type`
  now passes `rds_checksum="valid_hash"` — the invalid
  `indexes=[[1, 2], [3, 4]]` (a list of lists, rejected by the
  `NDArray` gate: "Input should be an instance of ndarray") is
  the thing under test, as the docstring claims.
- **T5 FIXED (F5)**: the Italian comment ("Non mockiamo il
  modulo...") translated to English (AGENTS.md rule 4).
- **M1 FIXED (F9)**: the 19 non-comment trailing-whitespace lines
  stripped; scope as in D-078 M3: the license-header `# ` lines
  stay.
- **M2 FIXED (F8)**: the rds-only-differs branch of
  `is_cache_consistent` is now unit-tested (the 3rd test, roles
  swapped: rds "live_hash" vs "outdated_cached_hash",
  feature_set_hash identical) — 13 → 14 tests.

## Verdict

A good per-function suite (the store/load contract fully pinned,
the error paths complete, both `is_cache_consistent` single-field
branches now unit-tested); the hygiene is clean post D-084. The
only remaining observation (M3 — `rds_checksum` never asserted on
the load path) is probe-covered (B4) and left as-is.
