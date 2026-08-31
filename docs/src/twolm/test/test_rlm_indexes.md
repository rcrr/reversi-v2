# twolm/test/test_rlm_indexes.py

Analysis date: 2026-08-31 — analysis session 23 (D-083).

Roberto's file, brought in with the INDEXES enablement (a323e0f,
the line-by-line pipeline step 5). 5 classes / 13 tests / no
PERF. Green on first run (all file I/O mocked — `twolm.rlm_
indexes.binio` patched, no temp dirs, no DB). Awaiting
Roberto's call: T1-T5 + M1-M2.

## Suite status (session 23, D-083)

- `test_rlm_indexes`: 13/0/0 (no DB, no gates)
- Full discover: 515 tests, 56 skipped under `SKIP_REGAB_DB=1`
  (17 PERF + 35 regab + 2 positions + 2 features), GREEN; ungated
  (live DB): 515 run, 17 skipped (PERF only), GREEN.

## Coverage

- Shared dummy (L57): `DUMMY_INDEXES = np.zeros((2, 2),
  dtype=np.uint32)` across the whole file.
- `TestReversiLogisticModelIndexes` (3 tests):
  - `test_init_success` (L63-77): the 3 attributes + `isinstance
    np.ndarray` + the uint32 dtype + `assertIs(obj.indexes,
    DUMMY_INDEXES)` (the by-reference storage pinned — the only
    test in the file that pins that contract).
  - `test_init_fails_with_invalid_hash_type` (L79-88): a
    non-str `feature_set_hash` (12345) is rejected — but via the
    BROAD `assertRaises(Exception)` (T3), not the pydantic
    `ValidationError`.
  - `test_init_fails_with_invalid_indexes_type` (L90-96):
    intended to pin the `indexes: IndexArray` rejection (a list
    of lists) — but the call OMITS the required `rds_checksum`
    (T4): the ValidationError raised is for the missing argument,
    so the docstring's claim is NOT actually pinned.
- `TestRlmIndexesStoreToFile` (2 tests, binio mocked):
  - `test_store_to_file_success` (L103-133): `BinaryWriter`
    instantiated with `Path(filename)` + the exact 4-call
    sequence pinned (`write_header(desc, 1)`, `write_string` ×2,
    `write_array`) — both `assert_has_calls(any_order=False)` and
    the full `method_calls ==` comparison.
  - `test_store_to_file_accepts_path_object` (L136-147): a
    `pathlib.Path` filename passes through to `BinaryWriter`
    unchanged.
- `TestRlmIndexesLoadFromFile` (5 tests, binio mocked):
  - `test_load_from_file_success_with_checksum` (L154-173): the
    default `checksum=True` calls `verify_sha3_256_sidecar`
    exactly once + the round-trip fields (feature_set_hash, the
    uint32 dtype, `assertIs` on the array). NOTE: both
    `read_string` mocks return the same "stored_hash", so
    `rds_checksum` is never asserted (M3).
  - `test_load_from_file_success_without_checksum` (L176-187):
    `checksum=False` → `assert_not_called` on the sidecar verify.
  - `test_load_from_file_checksum_mismatch` (L190-197): the
    RuntimeError + "checksum file signature doesn't match".
  - `test_load_from_file_invalid_description` (L200-211): the
    RuntimeError + "not a proper".
  - `test_load_from_file_invalid_version` (L214-225): the
    RuntimeError + "version is not consistent".
- `TestRlmIndexesCompute` (1 test, NO mock — the L233 comment
  "Non mockiamo il modulo" says so, T5: English per AGENTS.md
  rule 4): a MagicMock ctx; pins `compute_indexes` called once
  with the ctx positions ("dummy_positions" — a string, the mock
  absorbs it), the resulting `feature_set_hash`, and
  `assertIs` on the returned array.
- `TestRlmIndexesIsCacheConsistent` (2 tests):
  - `test_is_cache_consistent_returns_true` (L255-268): both
    fields "identical_hash" → True.
  - `test_is_cache_consistent_returns_false` (L270-283): ONLY
    the feature_set_hash differs ("live_hash" vs
    "outdated_cached_hash", rds identical) → False. The
    rds-only-differs branch is UNTESTED (M2 — probe B11 covers
    it).

The suite is a solid per-function pin of the store/load contract
(exact call sequence, all 3 RuntimeError messages, both
checksum flags) + the compute/is_cache_consistent logic. The
coverage gaps are the two `is_cache_consistent` branches (M2)
and the `rds_checksum` value on the load path (M3) — both
covered by the D-083 probe.

## Defects — OPEN (awaiting Roberto's call)

- T1 (F3): the DEAD import `from twolm.pattern import
  IndexArray` (L52) — zero code-level uses (the only other
  textual occurrence is the docstring at L91; verified with an
  AST walk).
- T2 (F4): header grammar — "How to use the unit tests
  rlm_indexes module." (the established pattern).
- T3 (F7): the 2 BROAD `assertRaises(Exception)` (L83, L92) —
  the house style pins the precise pydantic `ValidationError`
  (the test_lm_worker_config T2 / test_mobility T2 pattern).
- T4 (F7): `test_init_fails_with_invalid_indexes_type` OMITS the
  required `rds_checksum` — the test passes, but on the missing-
  argument ValidationError, not on the `indexes` type its
  docstring claims. Fix: add `rds_checksum=` so the invalid
  `indexes=[[1, 2], [3, 4]]` is the thing under test.
- T5 (F5): the Italian comment at L233 ("Non mockiamo il
  modulo...") — English notes in the workspace (AGENTS.md rule
  4).
- M1 (F9): 19 non-comment trailing-whitespace lines. Scope as in
  D-078 M3: the license-header `# ` lines stay.
- M2 (F8, P2 breadth candidate): the rds-only-differs branch of
  `is_cache_consistent` is untested — a 3rd test mirroring
  `test_is_cache_consistent_returns_false` with the roles
  swapped (rds "outdated", feature_set_hash "identical_hash")
  would pin both fields independently.

## Verdict

A good per-function suite (the store/load contract fully pinned,
the error paths complete); the gaps are small (M2/M3 — both
probe-covered) plus the T1-T5 hygiene. T4 is the only genuine
logic gap in the assertions (a test that passes for the wrong
reason).
