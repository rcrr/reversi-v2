# twolm/test/test_regab.py
The regab unit suite — 6 classes / 37 tests, no PERF gates. 35 tests
require a live PostgreSQL database + the workspace `.env`; 2
(`TestRegabDataSetFileLoadExceptions`) are fully mocked.
`SKIP_REGAB_DB=1` skips the DB-dependent tests (the T6 gate in
`BaseTestCase.setUp`, D-052). D-085 re-anchored the `.env` load and
the checksum test's `mkdtemp` to the shared `twolm.test.paths`
constants (`WORKSPACE_ROOT` / `CUSTOM_TMP_BASE`).
> State: D-085 · aef6188 · 2026-08-31 · suite 37/0/0 (35 live-DB;
  SKIP_REGAB_DB=1 → 35 skipped / 2 run, 0.9 s)

## Coverage

| class (line) | tests | what it pins |
|---|---|---|
| `BaseTestCase` (L88, base) | — | `setUp`: the `SKIP_REGAB_DB` gate FIRST (T6), then `load_dotenv(WORKSPACE_ROOT / ".env")` (D-085), then the `RegabDBConnection` + open-connection assert; `tearDown` closes and asserts closed. All 35 DB tests in the 4 subclasses exercise the real database |
| `TestRegabDB` (L126) | 2 | the connection is open (`closed == 0`); `SHOW search_path` includes `reversi` |
| `TestRegabGPAsDF` (L146) | 16 | the valid full query (bid=[7,8], status=['CMS','CMR'], ec=10, limit=5, where, fields) + all-defaults query → non-empty DataFrame; the 5 invalid-argument `ValidationError`s (bid, status len, ec=61, limit, where-not-a-string); the 4 T7 SQL-injection guards (`--` comment, `SELECT`, `;`, + a valid expression accepted); the 4 invalid-fields paths (wrong string, duplicates, wrong list element, 3 in a str list) + `fields='*'` → all table columns |
| `TestRegabDataSet` (L280) | 13 | the valid round-trip; 7 invalid-argument paths (bid type/value, status type/length, ec type/value, df_mogv type); the 3 df_mogv column checks (2 cols, float64 game_value → TypeError); `regab_extract_data_set_from_db` with the `.env` `TEST_RDATA_TEST_EXTRACTION_*` params (optional — `ValueError` in setUp if unset); `generate_positions_and_game_values` (the `.view(Bitboard)` reinterpret); `compute_sha3_256_hash` vs the golden literal |
| `TestRegabDataSetChecksum` (L553) | 4 | the store→load round-trip (all fields match); load with `checksum=False`; a removed `.SHA3-256` sidecar → `FileNotFoundError`; an appended byte → `RuntimeError`. The temp dir is under `CUSTOM_TMP_BASE` (D-085: was CWD-relative `./build/tmp`) |
| `TestRegabDataSetFileLoadExceptions` (L648, plain `unittest.TestCase`) | 2 | `binio.BinaryReader` + `verify_sha3_256_sidecar` mocked: a wrong file description → `RuntimeError`; a wrong version → `RuntimeError`. These are the 2 tests that run without a DB |

## Goldens pinned

- The `compute_sha3_256_hash` literal
  `b507cd34abfd13ea5c636f97e983bec2c5d8f4308b90e379a553cc9093681670`
  (the V1 golden) — the only hash pin in the suite.
- The `.env`-driven extraction expectation
  (`TEST_RDATA_TEST_EXTRACTION_EXPECTED_COUNT`) — the row-count pin
  of the live extraction.

## Conventions

- The suite is NOT self-contained: it needs the live DB + `.env`
  (credentials are not committed and should not be).
- No standalone unit test for `_validate_db_fields` (only through
  `regab_gp_as_df`); no test for the compressed `binio` store path
  (default uncompressed only) — both accepted (see regab.md).
- The T7 injection tests pin the EXACT guard behaviour (comment,
  SELECT keyword, semicolon) + one accepted valid expression.

## Integration

- Module under test: `regab.md`. The live-DB tests are the only
  in-repo coverage of the PostgreSQL path (no probe for this module).
- `test_lm_worker_positions.md` / `test_lm_worker_vld_positions.md`
  cover the pipeline-level consumers (the cache_manager wiring).
