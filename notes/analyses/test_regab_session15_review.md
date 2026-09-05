<!-- ARCHIVED — D-106 step 26 (the docs/ rewrite, 2026-09-04): the REGAB family (regab.md + this doc) moved out of docs/src/twolm/test/ into the snapshot schema per docs_rules.md §1/§4. This is a frozen historical record: it is never updated. Stale-in-current-context notes: (1) the T5/T6 "Defects" section is the D-052 fix-campaign narrative — applied and closed. (2) the "31 DB-dependent tests" figure in the BaseTestCase note is a typo frozen here: it is 35 (37 − the 2 fully-mocked). (3) the class map is still the current one (the D-085 +1 import shift is already reflected). -->

# test_regab.md — analysis

Date: 2026-08-29. One test file: `test_regab.py` (37 tests, 5 classes).
**T5 + T6 + T7 applied (D-052): suite 33 → 37/0/0 GREEN.**
D-085 (session 23): the `.env` load and the checksum test's
`mkdtemp` re-anchored to the shared twolm.test.paths module
(`WORKSPACE_ROOT` / `CUSTOM_TMP_BASE`).

Suite: **37/0/0 GREEN, no PERF gates.** 35 tests require a live PostgreSQL
database and `.env` file; 2 (`TestRegabDataSetFileLoadExceptions`) are fully
mocked. `SKIP_REGAB_DB=1` skips the DB-dependent tests (35 skipped, 2 run).

## How to run

```
$ source .venv/bin/activate
$ ssh -N -f -L 5432:localhost:5432 username@database_host   # port forward
$ python -m unittest twolm.test.test_regab
# or, without a database:
$ SKIP_REGAB_DB=1 python -m unittest twolm.test.test_regab
```

Requires `.env` in workspace root with:
```
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
DB_HOST=...
DB_PORT=5432
# Optional for TestRegabDataSet.test_extract_data_from_db:
TEST_RDATA_TEST_EXTRACTION_ARG_BID=...
TEST_RDATA_TEST_EXTRACTION_ARG_STATUS=...
TEST_RDATA_TEST_EXTRACTION_ARG_EC=...
TEST_RDATA_TEST_EXTRACTION_EXPECTED_COUNT=...
```

## Coverage by area

### `BaseTestCase` (abstract, extended by 4 classes)
- `setUp`: checks `SKIP_REGAB_DB` (T6) and skips when set; loads `.env` via `load_dotenv(WORKSPACE_ROOT / ".env")` (D-085: explicit workspace-root path, not the caller-relative search), creates `RegabDBConnection`, asserts connection is open.
- `tearDown`: closes connection, asserts it's closed.
- **Every test inherits** DB setup/teardown, so all 31 DB-dependent tests in the four subclasses exercise the real database.

### `TestRegabDB` (2 tests)
- `test_connection_status`: connection is not None and `closed == 0`.
- `test_schema_search_path`: `SHOW search_path` includes `reversi`.
- **Coverage**: basic DB connection validation.

### `TestRegabGPAsDF` (16 tests)
- `test_valid_query_construction`: full query with bid=[7,8], status=['CMS','CMR'], ec=10, limit=5, where="game_value > 0", fields=[...]. Asserts DataFrame non-empty.
- `test_valid_query_construction_all_defaults`: minimal query with defaults (no limit/where/fields).
- `test_invalid_bid`: negative bid → `ValidationError`.
- `test_invalid_status`: status 'AAAA' (len=4) → `ValueError`.
- `test_invalid_ec`: ec=61 → `ValidationError`.
- `test_invalid_limit`: limit=-1 → `ValueError`.
- `test_invalid_where`: where=123 (not a string) → `ValidationError`.
- `test_invalid_where_sql_comment_dash` (T7): where containing `--` → `ValueError`.
- `test_invalid_where_sql_select` (T7): where containing `SELECT` → `ValueError`.
- `test_invalid_where_semicolon` (T7): where containing `;` → `ValueError`.
- `test_valid_where_expression` (T7): valid where expression accepted, non-empty DataFrame.
- `test_invalid_fields_wrong_string`: fields='invalid_field' → `ValueError`.
- `test_invalid_fields_duplicated_entries`: fields=['seq','seq'] → `ValueError`.
- `test_invalid_fields_wrong_list`: fields=['seq','not_valid_col_name'] → `ValueError`.
- `test_invalid_fields_wrong_element_in_the_list`: fields=['seq','game_value',3] → `ValueError`.
- `test_all_fields`: fields='*' → DataFrame columns match all table columns.
- **Coverage**: excellent — valid query, all defaults, 4 SQL-injection guards, 5 invalid-fields paths.

### `TestRegabDataSet` (13 tests)
- `test_valid_initialization`: round-trip all fields.
- `test_invalid_bid_type`: bid='not_a_list' → `ValidationError`.
- `test_invalid_bid_value`: bid=[-1,2] → `ValueError`.
- `test_invalid_status_type`: status='not_a_list' → `ValidationError`.
- `test_invalid_status_length`: status=['CMS','CM'] (len=2) → `ValueError`.
- `test_invalid_ec_type`: ec='not_an_int' → `ValidationError`.
- `test_invalid_ec_value`: ec=61 → `ValueError`.
- `test_invalid_df_mogv_type`: df_mogv='not_a_dataframe' → `ValidationError`.
- `test_invalid_df_mogv_columns`: 2 columns → `ValueError`.
- `test_invalid_df_mogv_column_types`: game_value as float64 → `TypeError`.
- `test_extract_data_from_db`: `regab_extract_data_set_from_db` with params from `.env` → non-empty 3-column DataFrame.
- `test_generate_positions_and_game_values`: creates dataset, calls `generate_positions_and_game_values` → verifies both outputs.
- `test_compute_sha3_256_hash`: computes hash → asserts against golden `b507cd34abfd13ea5c636f97e983bec2c5d8f4308b90e379a553cc9093681670`.
- **Coverage**: excellent — all validation paths + DB extraction + generation + hash golden.

### `TestRegabDataSetChecksum` (4 tests)
- Uses `setUp` (creates temp dir under the shared `CUSTOM_TMP_BASE` — D-085: was the CWD-relative `./build/tmp` — builds a `RegabDataSet`) + `tearDown` (removes temp dir).
- `test_store_and_load`: store→load round-trip, all fields match.
- `test_load_without_checksum`: store then load with `checksum=False` — still matches.
- `test_load_missing_checksum_file`: store then remove `.SHA3-256` sidecar → `FileNotFoundError`.
- `test_load_mismatched_checksum`: store then append extra bytes → `RuntimeError`.
- **Coverage**: good — covers both checksum paths and two error paths.

### `TestRegabDataSetFileLoadExceptions` (2 tests)
- Uses `unittest.mock.patch` on `binio.BinaryReader` and `binio.verify_sha3_256_sidecar`.
- `test_load_invalid_file_description`: wrong description header → `RuntimeError`.
- `test_load_invalid_file_version`: wrong version header → `RuntimeError`.
- **Coverage**: mocks allow testing header validation without a DB.

## Defects (test file only)

### T5 — Dead imports (D-052, FIXED)
Removed: `numpy.typing as npt`, `time`, `io`, `itertools`, `mock_open`, and the unused `Callable`, `TypeAlias`, `List` typing imports. `patch` and `MagicMock` are used in `TestRegabDataSetFileLoadExceptions`.

### T6 — No DB-unavailable skip mechanism (D-052, FIXED)
`BaseTestCase.setUp` now checks `SKIP_REGAB_DB=1` and calls `skipTest()`. With the env var set: 35 skipped, 2 run. Without it: 37/0/0 GREEN.

## Observations (test file only)

- **Test data relies on `.env`**: `BaseTestCase` reads credentials from `.env` via `load_dotenv(WORKSPACE_ROOT / ".env")` (D-085: anchored to the workspace root, not the CWD / caller). The `.env` file is not committed (and should not be). This means tests are not self-contained — they require environment setup.
- **`test_extract_data_from_db` params in `.env`**: `TEST_RDATA_TEST_EXTRACTION_ARG_BID` etc. are optional — if not set, the test raises `ValueError` in `setUp`, not in the test itself.
- **No unit tests for `_validate_db_fields` standalone**: the validator is tested only through `regab_gp_as_df`. A standalone unit test (mocking the DB cursor) would isolate the validation logic.
- **No test for `regab_store_data_set_to_file` with `compressed=True`**: only the default (uncompressed) binio path is tested.

## Completeness verdict

**The suite is thorough within its DB-required constraint**: all public API paths have tests, validation errors are covered (including the SQL-injection guards), the hash golden is pinned, and the binary file round-trip works end-to-end.

**Verdict**: 37/0/0 GREEN. T5, T6, T7 all fixed (D-052). The `SKIP_REGAB_DB` gate makes CI and DB-less local runs possible.

## Appendix: class map (as of D-085; the D-085 import shifted all lines by +1)

| Line | Class | Tests | Requires DB |
|---|---|---|---|
| 88 | `BaseTestCase` | 0 (base) | yes |
| 126 | `TestRegabDB` | 2 | yes |
| 146 | `TestRegabGPAsDF` | 16 | yes |
| 280 | `TestRegabDataSet` | 13 | yes (1 optional `.env`-driven) |
| 553 | `TestRegabDataSetChecksum` | 4 | yes (inherits BaseTestCase) |
| 648 | `TestRegabDataSetFileLoadExceptions` | 2 | no (fully mocked) |