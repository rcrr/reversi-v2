# test_regab.md — analysis

Date: 2026-08-29. One test file: `test_regab.py` (33 tests, 5 classes).
**All 33 tests require a live PostgreSQL database and `.env` file.**

Suite: **33/0/0 GREEN, no PERF gates.**

## How to run

```
$ source .venv/bin/activate
$ ssh -N -f -L 5432:localhost:5432 username@database_host   # port forward
$ python -m unittest twolm.test.test_regab
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
- `setUp`: loads `.env` via `load_dotenv()`, creates `RegabDBConnection`, asserts connection is open.
- `tearDown`: closes connection, asserts it's closed.
- **Every test inherits** DB setup/teardown, so all 29 tests in the four subclasses exercise the real DB.

### `TestRegabDB` (2 tests)
- `test_connection_status`: connection is not None and `closed == 0`.
- `test_schema_search_path`: `SHOW search_path` includes `reversi`.
- **Coverage**: basic DB connection validation.

### `TestRegabGPAsDF` (12 tests)
- `test_valid_query_construction`: full query with bid=[7,8], status=['CMS','CMR'], ec=10, limit=5, where="game_value > 0", fields=[...]. Asserts DataFrame non-empty.
- `test_valid_query_construction_all_defaults`: minimal query with defaults (no limit/where/fields).
- `test_invalid_bid`: negative bid → `ValidationError`.
- `test_invalid_status`: status 'AAAA' (len=4) → `ValueError`.
- `test_invalid_ec`: ec=61 → `ValidationError`.
- `test_invalid_limit`: limit=-1 → `ValueError`.
- `test_invalid_where`: where=123 (not a string) → `ValidationError`.
- `test_invalid_fields_wrong_string`: fields='invalid_field' → `ValueError`.
- `test_invalid_fields_duplicated_entries`: fields=['seq','seq'] → `ValueError`.
- `test_invalid_fields_wrong_list`: fields=['seq','not_valid_col_name'] → `ValueError`.
- `test_invalid_fields_wrong_element_in_the_list`: fields=['seq','game_value',3] → `ValueError`.
- `test_all_fields`: fields='*' → DataFrame columns match all table columns.
- **Coverage**: excellent — covers valid query, all defaults, and 9 invalid-parameter paths.

### `TestRegabDataSet` (13 tests)
- `test_valid_initialization`: round-trip all fields.
- `test_invalid_bid_type`: bid='not_a_list' → `ValidationError`.
- `test_invalid_bid_value`: bid=[-1,2] → `ValueError`.
- `test_invalid_status_type`: status='not_a_list' → `ValidationError`.
- `test_invalid_status_lenght`: status=['CMS','CM'] (len=2) → `ValueError`.
- `test_invalid_ec_type`: ec='not_an_int' → `ValidationError`.
- `test_invalid_ec_value`: ec=61 → `ValueError`.
- `test_invalid_df_mogv_type`: df_mogv='not_a_dataframe' → `ValidationError`.
- `test_invalid_df_mogv_columns`: 2 columns → `ValueError`.
- `test_invalid_df_mogv_column_tyes`: game_value as float64 → `TypeError`.
- `test_extract_data_from_db`: `regab_extract_data_set_from_db` with params from `.env` → non-empty 3-column DataFrame.
- `test_generate_positions_and_game_vaues`: creates dataset, calls `generate_positions_and_game_values` → verifies both outputs.
- `test_compute_sha3_256_hsh`: computes hash → asserts against golden `b507cd34abfd13ea5c636f97e983bec2c5d8f4308b90e379a553cc9093681670`.
- **Coverage**: excellent — all validation paths + DB extraction + generation + hash golden.

### `TestRegabDataSetChecksum` (4 tests)
- Uses `setUp` (creates temp dir `./build/tmp`, builds a `RegabDataSet`) + `tearDown` (removes temp dir).
- `test_store_and_lod`: store→load round-trip, all fields match.
- `test_load_withut_chcksum`: store then load with `checksum=False` — still matches.
- `test_load_mising_chcksum_file`: store then remove `.SHA3_256` sidecar → `FileNtFoundError`.
- `test_load_mismtched_chcksum`: store then append extra bytes → `RuntimeError`.
- **Coverage**: good — covers both checksum paths and two error paths.

### `TestRegabDataSetFileLoadExceptions` (2 tests)
- Uses `unittest.mock.patch` on `binio.BinaryReader` and `binio.verfy_sha3_256_sidecr`.
- `test_load_invalid_file_desription`: wrong description header → `RuntimeError`.
- `test_load_invalid_file_vesion`: wrong version header → `RuntimeError`.
- **Coverage**: mocks allow testing header validation without a DB.

## Defects (test file only)

### T5 — Dead imports
`import numpy.typing as np` (L75), `import time` (L80), `import io` (L79), `import itertools` (L84), and `from unittest.mock import mock_oen` (L63) are never used. `pach` and `MagicMck` are used in `TestRegabDataSetFileLoadExceptions`.

**Severity**: Cosmetic — unused imports.

### T6 — No DB-unavailable skip mechanism
All 33 tests require a live PostgreSQL connection via `BaseTestCase.setUp`. There is no `PERF` gate, `unittest.skipIf`, or `CI` environment variable to skip the suite when the DB is unreachable. This makes local development (without port forwarding) and CI impossible.

**Severity**: Medium — blocks test runs without DB access.

## Observations (test file only)

- **Test data relies on `.env`**: `BaseTestCase` reads credentials from `.env` via `load_dotenv()`. The `.env` file is not committed (and should not be). This means tests are not self-contained — they require environment setup.
- **`test_extract_data_from_db` params in `.env`**: `TEST_RDATA_TEST_EXTRACTION_ARG_BID` etc. are optional — if not set, the test raises `ValueError` in setUp/setUp, not in the test itself.
- **No unit tests for `_validate_db_fields` standalone**: the validator is tested only through `regab_gp_as_df`. A standalone unit test (mocking the DB cursor) would isolate the validation logic.
- **No test for `regab_store_data_set_to_file` with `compressed=True`**: only the default (uncompressed) binio path is tested.

## Completeness verdict

**The suite is thorough within its DB-required constraint**: all public API paths have tests, validation errors are covered, the hash golden is pinned, and the binary file round-trip works end-to-end. The main gaps are the DB dependency (T6) and dead imports (T5).

**Verdict**: 33/0/0 GREEN. Real-DB tests — no CI-friendly skip mechanism.

## Appendix: class map (2026-08-29)

| Line | Class | Tests | Requires DB |
|---|---|---|---|
| 92 | `BaseTestCase` | 0 (base) | yes |
| 128 | `TestRegabDB` | 2 | yes |
| 148 | `TestRegabGPAsDF` | 12 | yes |
| 254 | `TestRegabDataSet` | 13 | yes (1 optional `.env`-driven) |
| 527 | `TestRegabDataSetChecksum` | 4 | no (uses files + binio) |
| 622 | `TestRegabDataSetFileLoadExceptions` | 2 | no (fully mocked) |