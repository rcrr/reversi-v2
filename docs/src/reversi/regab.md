# reversi/regab.py
`regab` (REversi GAme Base) is the database-access and serialization layer of the pipeline: it queries a PostgreSQL
database for game positions (the `regab_prng_gp` table), wraps the results in a `RegabDataSet`, and
serializes/deserializes datasets to binary files via the `binio` module. It is the data source of the POSITIONS and VLD
levels.

## API

| name | contract |
|---|---|
| `GameValue = np.int8` / `GameValueArray` | The game-value types (-64 to +64); `GameValueArray` is the pydantic-validated `NDArray[np.int8]` |
| `RegabDBConnection(dbname, user, host, port, password, activate_conn=True)` | Wraps a `psycopg2` connection; `__init__`, `activate_conn`, `close` (the `if self.conn` guard prevents most double-close); sets `search_path` to `reversi` |
| `regab_gp_as_df(rc, bid, status, ec, *, limit, where, fields)` | Queries `regab_prng_gp`, returns a `pd.DataFrame`; the double-decorated entry point (below); `where` is `WhereArgument`-guarded |
| `RegabDataSet(rc, bid, status, ec, df_mogv)` | A dataset: connection params + a 3-column DataFrame (mover int64, opponent int64, game_value int8); `__init__`; `generate_positions_and_game_values` (reinterprets the int64 columns as `Bitboard` via `.view`, no data loss); `compute_sha3_256_hash` (over the column `tobytes()` in insertion order mover→opponent→game_value, implicit but deterministic) |
| `regab_extract_data_set_from_db(rc, bid, status, ec)` | Extracts a `RegabDataSet` from the database |
| `regab_dedup_mogv(df_mogv)` | Removes duplicate (mover, opponent) rows — `drop_duplicates(subset=['mover','opponent'], keep='first')` (hash-based, O(n), order-preserving; "first" = lowest seq, the extraction is `ORDER BY seq`); returns `(deduped_df, total_rows, removed_rows)`. Pure, no logging, no data validation (the pipeline does not validate the data) |
| `regab_count_position_overlap(positions, vld_positions)` | Counts the vld records whose (mover, opponent) key is also in the training positions (the validation-independence metric) — a pandas inner-merge over the 2 key columns (the train side is `drop_duplicates`-deduped first, so a duplicated train key cannot inflate the count; a duplicated vld row counts once per record). Returns a plain int: the pipeline takes NO action on it (log only) |
| `regab_store_data_set_to_file(rds, filename, compressed=True)` | Serializes to a `binio` framed binary file; LZ4 whole-file frame by default (as in model_weights); the SHA3-256 sidecar is written by the binio writer (the checksum service is on by default), and in the pipeline flow `cache_manager` re-writes the same sidecar (idempotent) |
| `regab_load_data_set_from_file(filename, checksum=True, compressed=True)` | Deserializes; verifies the `binio` sidecar checksum by default |

The on-disk format (binio-framed): header `"RegabDataSet binary data file"` / version 1, then dbname, user, host, port
(strings), num_bid + bid[] (u32), num_status + status[] (strings), ec (u32), mover (int64), opponent (int64), game_value
(int8).

## Architecture

- Types: `GameValue` + the `GameValueArray` BeforeValidator.
- Connection: `RegabDBConnection` — the psycopg2 wrapper with the `reversi` search path.
- The ContextVar bridge: `rc_context`; `_validate_db_fields` does the DB-backed column check (deferred — the
  `SELECT ... LIMIT 0` colnames query runs only when `fields_input` is actually a string or list);
  `_validate_with_db_context` sets the ContextVar before `@validate_call` and resets it in `finally`; `_ensure_list`.
- Argument validators: `BidArgument` (int→[int], `ge=0`), `StatusArgument` (str→[str], 3 chars each), `EcArgument`
  (`ge=0, le=60`), `_WHERE_FORBIDDEN` + `_validate_where_clause` + `WhereArgument` (the SQL-injection guard: blocks
  comments `--`/`/* */`, the `;` terminator, and the dangerous keywords
  SELECT/INSERT/UPDATE/DELETE/DROP/UNION/ALTER/CREATE/EXEC/EXECUTE/TRUNCATE), `FieldsArgument`.
- `regab_gp_as_df`: double-decorated — `@_validate_with_db_context` FIRST (sets the ContextVar) then `@validate_call`
  (pydantic), so the DB-backed validators can read the connection from the ContextVar; builds the SQL by str.format()
  interpolation (a single-string `curs.execute(q)`, no parameter binding); the status validator enforces length 3 only,
  so a quote inside a 3-char status passes validation and is interpolated as-is.
- The DataFrame guard: `_ensure_column_count_and_type` (3 columns, dtypes compared as the strings `'int64'`/`'int8'`) +
  `DfMogvArgument`.
- `RegabDataSet` + the module-level functions: `regab_extract_data_set_from_db`, the two pure helpers `regab_dedup_mogv`
  + `regab_count_position_overlap`, `regab_load_data_set_from_file` and `regab_store_data_set_to_file`. The two helpers
  are @validate_call-decorated but have NO DB access — `dedup_mogv` is a `drop_duplicates` over a passed-in frame,
  `count_position_overlap` is a pandas inner-merge over the two key columns (the train side deduped first); both are
  exercised by the no-DB micro tier in `test_regab`.

## Verified invariants

No dedicated probe — the invariants are pinned by the `test_regab` suite (see test_regab.md) and by the live-DB run of
the module suite.

- V1: `compute_sha3_256_hash` matches an independent `hashlib.sha3_256` recomputation over the column `tobytes()` —
  pinned by `TestRegabDataSet.test_compute_sha3_256_hash` with the golden
  `b507cd34abfd13ea5c636f97e983bec2c5d8f4308b90e379a553cc9093681670`.
- V2: `generate_positions_and_game_values` uses `.view(Bitboard)` (int64→uint64 reinterpret, bit-width match, no data
  loss) — pinned by `TestRegabDataSet.test_generate_positions_and_game_values`.
- V3: the dtype guard compares the STRING `'int64'` (pandas dtypes) — pinned by `test_invalid_df_mogv_column_types`
  (float64 game_value → TypeError).
- V4: the interpolated values come from the validated typed arguments (bid/ec are ints, the status is a length-3 string)
  — but the StatusArgument validator enforces length ONLY (min_length=3/max_length=3), quoting is NOT enforced, and the
  single-string execute has no parameter binding, so a quote inside a 3-char status reaches the SQL as-is.

## Open issues

None.

## Conventions

- The ContextVar pattern is concurrency-safe by construction: set before `@validate_call`, reset in `finally`
  (no test can exercise the concurrency; the pattern is verified by inspection + the double-decorator order in
  `regab_gp_as_df`).
- `SKIP_REGAB_DB=1` skips the 36 DB-dependent tests (the gate in `BaseTestCase.setUp`); the 2 fully-mocked
  `TestRegabDataSetFileLoadExceptions` tests always run.
- The test data relies on `.env` in the workspace root (`load_dotenv(WORKSPACE_ROOT / ".env")`): the suite is NOT
  self-contained; `test_extract_data_from_db` reads its optional `TEST_RDATA_TEST_EXTRACTION_*` params there.
- `_validate_db_fields` needs a live DB even for purely structural checks (a standalone mock-based test would isolate it
  — not done; the suite uses the real DB).
- `compute_sha3_256_hash` iterates `for col in df` — the insertion order (mover→opponent→game_value), deterministic but
  implicit.
- Only the default (LZ4-compressed) `binio` store path is tested.

## Integration

- The POSITIONS level: `wrk_positions` builds the 5-arg `RegabDBConnection` from
  `ctx.cfg.regab_data_set.regab_db_connection` (port + password take effect), extracts via
  `regab_extract_data_set_from_db`, and wires `regab_load_data_set_from_file(path, checksum=False)` /
  `regab_store_data_set_to_file` as the `cache_manager` data functions — the sidecar is written by the binio writer
  (`cache_manager` re-writes it idempotently in the pipeline flow). The compute path is
  `wrk_positions.extract_and_prepare` (extract → `regab_dedup_mogv` per the `regab_allow_duplicate` flag → log the
  duplicate count); the cache file stores the POST-policy data set, so a flag flip changes the stored content and the
  `rds_checksum`, cascading through the downstream checksum lineage.
- The VLD level: `wrk_vld_positions` reuses the same `extract_and_prepare` (with the vld bid/status overrides) + the
  same load/store pair for the validation dataset, and after the population stats runs the validation-independence check
  (`regab_count_position_overlap` over `ctx.positions` × `ctx.vld_positions`) — LOG ONLY, no action (a threshold/quality
  parameter family is explicitly out of scope).
- `binio.md` is the serialization backend; `cache_manager.md` the idempotent sidecar re-writer in the pipeline flow.
