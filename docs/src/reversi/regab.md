# reversi/regab.py
`regab` (REversi GAme Base) is the database-access and serialization
layer of the pipeline: it queries a PostgreSQL database for game
positions (the `regab_prng_gp` table), wraps the results in a
`RegabDataSet`, and serializes/deserializes datasets to binary files
via the `binio` module. It is the data source of the POSITIONS and
VLD levels.
> State: D-139 · 9ba523b · 2026-09-08 · suite 37/0/0 (35 live-DB tests;
  SKIP_REGAB_DB=1 → 35 skipped / 2 run, 0.9 s)

## API

| name | contract |
|---|---|
| `GameValue = np.int8` (L63) / `GameValueArray` (L72) | The game-value types (-64 to +64); `GameValueArray` is the pydantic-validated `NDArray[np.int8]` |
| `RegabDBConnection(dbname, user, host, port, password, activate_conn=True)` (L76) | Wraps a `psycopg2` connection; `__init__` (L106), `activate_conn` (L147), `close` (L153 — the `if self.conn` guard prevents most double-close); sets `search_path` to `reversi` |
| `regab_gp_as_df(rc, bid, status, ec, *, limit, where, fields)` (L271) | Queries `regab_prng_gp`, returns a `pd.DataFrame`; the double-decorated entry point (below); `where` is `WhereArgument`-guarded (T7) |
| `RegabDataSet(rc, bid, status, ec, df_mogv)` (L370) | A dataset: connection params + a 3-column DataFrame (mover int64, opponent int64, game_value int8); `__init__` (L388); `generate_positions_and_game_values` (L417 — reinterprets the int64 columns as `Bitboard` via `.view`, no data loss); `compute_sha3_256_hash` (L425 — over the column `tobytes()` in insertion order mover→opponent→game_value, implicit but deterministic) |
| `regab_extract_data_set_from_db(rc, bid, status, ec)` (L438) | Extracts a `RegabDataSet` from the database |
| `regab_store_data_set_to_file(rds, filename, compressed=True)` (L553) | Serializes to a `binio` framed binary file; LZ4 whole-file frame by default (D-139, as in model_weights); the SHA3-256 sidecar is written by the binio writer (the checksum service is on by default), and in the pipeline flow `cache_manager` re-writes the same sidecar (idempotent) |
| `regab_load_data_set_from_file(filename, checksum=True, compressed=True)` (L470) | Deserializes; verifies the `binio` sidecar checksum by default |

The on-disk format (binio-framed): header `"RegabDataSet binary
data file"` / version 1, then dbname, user, host, port (strings),
num_bid + bid[] (u32), num_status + status[] (strings), ec (u32),
mover (int64), opponent (int64), game_value (int8).

## Architecture

615 lines (post D-080 + D-139).

- Types (L63-72): `GameValue` + the `GameValueArray`
  BeforeValidator.
- Connection (L76-165): `RegabDBConnection` — the psycopg2 wrapper
  with the `reversi` search path.
- The ContextVar bridge (L167-225): `rc_context` (L167);
  `_validate_db_fields` (L170) does the DB-backed column check
  (deferred — the `SELECT ... LIMIT 0` colnames query runs only when
  `fields_input` is actually a string or list, the T4 fix);
  `_validate_with_db_context` (L196) sets the ContextVar before
  `@validate_call` and resets it in `finally`; `_ensure_list` (L227).
- Argument validators (L233-267): `BidArgument` (int→[int], `ge=0`),
  `StatusArgument` (str→[str], 3 chars each), `EcArgument`
  (`ge=0, le=60`), `_WHERE_FORBIDDEN` (L249) +
  `_validate_where_clause` (L255) + `WhereArgument` (L264 — the T7
  SQL-injection guard: blocks comments `--`/`/* */`, the `;`
  terminator, and the dangerous keywords SELECT/INSERT/UPDATE/
  DELETE/DROP/UNION/ALTER/CREATE/EXEC/EXECUTE/TRUNCATE),
  `FieldsArgument` (L267).
- `regab_gp_as_df` (L271-355): double-decorated —
  `@_validate_with_db_context` FIRST (sets the ContextVar) then
  `@validate_call` (pydantic), so the DB-backed validators can read
  the connection from the ContextVar; builds the parametrized query
  (status strings are safe — pydantic enforces len=3, no quotes
  possible).
- The DataFrame guard (L357-368): `_ensure_column_count_and_type`
  (3 columns, dtypes compared as the strings `'int64'`/`'int8'`) +
  `DfMogvArgument`.
- `RegabDataSet` (L370-435) + the three module-level functions
  (L438-614).

## Verified invariants

No dedicated probe — the invariants are pinned by the
`test_regab` suite (see test_regab.md) and by the live-DB run of the
module suite.

- V1: `compute_sha3_256_hash` matches an independent
  `hashlib.sha3_256` recomputation over the column `tobytes()` —
  pinned by `TestRegabDataSet.test_compute_sha3_256_hash` with the
  golden `b507cd34abfd13ea5c636f97e983bec2c5d8f4308b90e379a553cc9093681670`.
- V2: `generate_positions_and_game_values` uses `.view(Bitboard)`
  (int64→uint64 reinterpret, bit-width match, no data loss) —
  pinned by `TestRegabDataSet.test_generate_positions_and_game_values`.
- V3: the dtype guard compares the STRING `'int64'` (pandas
  dtypes) — pinned by `test_invalid_df_mogv_column_types` (float64
  game_value → TypeError).
- V4: `status_str` construction is safe — pydantic enforces len=3 on
  the status strings, so no quotes/special chars can reach the
  query (the T4/T7-era hardening).
- V5: the ContextVar pattern is correct — set before `@validate_call`,
  reset in `finally` (concurrent-safe by construction; no test can
  exercise the concurrency, the pattern is verified by inspection +
  the double-decorator order in `regab_gp_as_df`).

## Open issues

None.

## Conventions

- `SKIP_REGAB_DB=1` skips the 35 DB-dependent tests (the T6 gate in
  `BaseTestCase.setUp`); the 2 fully-mocked
  `TestRegabDataSetFileLoadExceptions` tests always run.
- The test data relies on `.env` in the workspace root (D-085:
  `load_dotenv(WORKSPACE_ROOT / ".env")`): the suite is NOT
  self-contained; `test_extract_data_from_db` reads its optional
  `TEST_RDATA_TEST_EXTRACTION_*` params there.
- `_validate_db_fields` needs a live DB even for purely structural
  checks (a standalone mock-based test would isolate it — not done;
  the suite uses the real DB).
- `compute_sha3_256_hash` iterates `for col in df` — the insertion
  order (mover→opponent→game_value), deterministic but implicit.
- Only the default (LZ4-compressed) `binio` store path is tested.

## Integration

- The POSITIONS level: `wrk_positions` builds the 5-arg
  `RegabDBConnection` from `ctx.cfg.regab_data_set.regab_db_connection`
  (port + password take effect since the D-080 R1 fix), extracts via
  `regab_extract_data_set_from_db`, and wires
  `regab_load_data_set_from_file(path, checksum=False)` /
  `regab_store_data_set_to_file` as the `cache_manager` data
  functions — the sidecar is written by the binio writer
  (`cache_manager` re-writes it idempotently in the pipeline
  flow).
- The VLD level: `wrk_vld_positions` uses the same load/store
  pair for the validation dataset.
- `binio.md` is the serialization backend; `cache_manager.md` the
  idempotent sidecar re-writer in the pipeline flow.
