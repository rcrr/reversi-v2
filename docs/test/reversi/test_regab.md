# test/reversi/test_regab.py
The regab unit suite — 8 classes / 49 tests, no PERF gates. 36 tests require a live PostgreSQL database + the workspace
`.env`; 2 (`TestRegabDataSetFileLoadExceptions`) are fully mocked; 11 (`TestRegabDedupMogv` +
`TestRegabCountPositionOverlap`) are no-DB micro tests. `SKIP_REGAB_DB=1` (or the absent LONG tier) skips the
DB-dependent tests (the db_long_gate in `BaseTestCase.setUp`). The `.env` load and the checksum test's `mkdtemp` are
anchored to the shared `test.reversi.paths` constants (`WORKSPACE_ROOT` / `CUSTOM_TMP_BASE`).

## Coverage

| class | tests | what it pins |
|---|---|---|
| `BaseTestCase` (base) | — | `setUp`: the `SKIP_REGAB_DB` gate first, then `load_dotenv(WORKSPACE_ROOT / ".env")`, then the `RegabDBConnection` + open-connection assert; `tearDown` closes and asserts closed. All 36 DB tests in the 4 subclasses exercise the real database |
| `TestRegabDB` | 3 | the connection is open (`closed == 0`); `SHOW search_path` includes `reversi`; the `activate_conn` re-open (a connection created with `activate_conn=False` is None, then established and closed) |
| `TestRegabGPAsDF` | 16 | the valid full query (bid=[7,8], status=['CMS','CMR'], ec=10, limit=5, where, fields) + all-defaults query → non-empty DataFrame; the 5 invalid-argument paths (3 `ValidationError`s: bid, ec=61, where-not-a-string; 2 `ValueError`s: status len, limit); the 4 SQL-injection guards (`--` comment, `SELECT`, `;`, + a valid expression accepted); the 4 invalid-fields paths (wrong string, duplicates, wrong list element, 3 in a str list) + `fields='*'` → all table columns |
| `TestRegabDataSet` | 13 | the valid round-trip; 7 invalid-argument paths (bid type/value, status type/length, ec type/value, df_mogv type); the 2 df_mogv column checks (2 cols, float64 game_value → TypeError); `regab_extract_data_set_from_db` with the `.env` `TEST_RDATA_TEST_EXTRACTION_*` params (optional — `ValueError` in setUp if unset); `generate_positions_and_game_values` (the `.view(Bitboard)` reinterpret); `compute_sha3_256_hash` vs the golden literal |
| `TestRegabDataSetChecksum` | 4 | the store→load round-trip (all fields match); load with `checksum=False`; a removed `.SHA3-256` sidecar → `FileNotFoundError`; an appended byte → `RuntimeError`. The temp dir is under `CUSTOM_TMP_BASE` |
| `TestRegabDataSetFileLoadExceptions` (plain `unittest.TestCase`) | 2 | `binio.BinaryReader` + `verify_sha3_256_sidecar` mocked: a wrong file description → `RuntimeError`; a wrong version → `RuntimeError`. These are the 2 tests that run without a DB |
| `TestRegabDedupMogv` (plain `unittest.TestCase`) | 5 | the no-DB micro semantics of `regab_dedup_mogv`: keep-first on a duplicated (mover, opponent) key (the kept row is the FIRST, the differing duplicate game_value is NOT a validation trigger — the pipeline does not validate the data); the no-duplicate passthrough; all-rows-identical; same-key-different-game_value keeps first (no raise); the empty frame |
| `TestRegabCountPositionOverlap` (plain `unittest.TestCase`) | 6 | the no-DB micro semantics of `regab_count_position_overlap` over `make_position` structured arrays: disjoint → 0; partial → 1; full → 2; a duplicated VLD row counts once PER record (2); a duplicated TRAIN row does NOT inflate the count (the train side is deduped first — 2, not 3); u64 top-bit keys (`0xFFFFFFFFFFFFFFFF`) match correctly |

## Goldens pinned

- The `compute_sha3_256_hash` literal `b507cd34abfd13ea5c636f97e983bec2c5d8f4308b90e379a553cc9093681670` (the golden)
  — the only hash pin in the suite.
- The `.env`-driven extraction expectation (`TEST_RDATA_TEST_EXTRACTION_EXPECTED_COUNT`) — the row-count pin of the live
  extraction.

## Conventions

- The suite is NOT self-contained: it needs the live DB + `.env` (credentials are not committed and should not be).
- No standalone unit test for `_validate_db_fields` (only through `regab_gp_as_df`) — accepted (see regab.md). The store
  path tested IS the default (LZ4-compressed).
- The injection tests pin the EXACT guard behaviour (comment, SELECT keyword, semicolon) + one accepted valid
  expression.

## Integration

- Module under test: `regab.md`. The live-DB tests are the only in-repo coverage of the PostgreSQL path (no probe for
  this module).
- `test_wrk_positions.md` / `test_wrk_vld_positions.md` cover the pipeline-level consumers (the cache_manager wiring).
