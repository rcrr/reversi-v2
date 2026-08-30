# regab.py — analysis

Date: 2026-08-29. Module added by Roberto (2 files: regab.py + test_regab.py).
**Fix batch T1-T7 applied (D-052): suite 33 → 37/0/0 GREEN.**

Suite: **37 tests, GREEN 37/0/0** (5 classes; 35 require live PostgreSQL + `.env`, 2 are fully mocked).
`SKIP_REGAB_DB=1` skips all DB-dependent tests (35 skipped, 2 run — T6).

## Architecture

`regab` (REversi GAme Base) is the database-access and serialization layer.
It queries a PostgreSQL database for game positions (`regab_prng_gp` table),
wraps results in a `RegabDataSet`, and can serialize/deserialize datasets to
binary files via the `binio` module.

### Components

| Component | Role |
|---|---|
| `GameValue = np.int8` | Type alias for game values (-64 to +64). |
| `GameValueArray` | Pydantic-validated `NDArray[np.int8]`. |
| `RegabDBConnection(dbname, user, host, port, password, activate_conn)` | Wraps `psycopg2` connection; sets `search_path` to `reversi`. |
| `regab_gp_as_df(rc, bid, status, ec, *, limit, where, fields)` | Queries `regab_prng_gp` table, returns `pd.DataFrame`. |
| `RegabDataSet(rc, bid, status, ec, df_mogv)` | Holds a dataset: connection params + 3-column DataFrame (mover int64, opponent int64, game_value int8). |
| `regab_extract_data_set_from_db(rc, bid, status, ec)` | Extracts a `RegabDataSet` from the database. |
| `regab_store_data_set_to_file(rds, filename)` | Serializes to a `binio` framed binary file. No sidecar is written here — in the pipeline flow cache_manager writes it (D-080 cross-ref fix, with the docstring). |
| `regab_load_data_set_from_file(filename, checksum)` | Deserializes from a `binio` file; verifies checksum by default. |

### On-disk format (via binio)

```
[header: "RegabDataSet binary data file", version=1]
[dbname: string]
[user: string]
[host: string]
[port: string]
[num_bid: u32]
[bid[0]..bid[n-1]: u32]
[num_status: u32]
[status[0]..status[n-1]: string]
[ec: u32]
[mover: int64 array]
[opponent: int64 array]
[game_value: int8 array]
```

### Validation pipeline

- **`regab_gp_as_df`**: double-decorated — `@_validate_with_db_context` (sets `ContextVar`) then `@validate_call` (Pydantic). Pydantic validators access the DB connection via `ContextVar` to validate `fields` against actual column names.
- **`BidArgument`**: `BeforeValidator(_ensure_list)` converts single int→[int]; `Field(ge=0)` per element.
- **`StatusArgument`**: `BeforeValidator(_ensure_list)` for str→[str]; `Field(min_length=3, max_length=3)` per element.
- **`EcArgument`**: `Field(ge=0, le=60)`.
- **`WhereArgument`** (T7): `AfterValidator(_validate_where_clause)` blocks SQL comments, statement terminators, and dangerous keywords to prevent SQL injection via the `where` clause.
- **`FieldsArgument`**: `AfterValidator(_validate_db_fields)` — DB-backed column check.
- **`DfMogvArgument`**: `AfterValidator(_ensure_column_count_and_type)` — 3 columns, types int64/int64/int8.

## Verified facts (V1–V5)

| # | Fact | Method |
|---|---|---|
| V1 | `compute_sha3_256_hash` golden matches independent recomputation | `hashlib.sha3_256` over column `tobytes()` in insertion order → `b507cd34...` |
| V2 | `generate_positions_and_game_values` uses `.view(Bitboard)` to reinterpret int64→uint64 | bit-width match, no data loss |
| V3 | `_ensure_column_count_and_type` dtype comparison (`'int64'` string) works with pandas | `df.dtypes.iloc[i] == 'int64'` → True |
| V4 | `status_str` construction safe: Pydantic enforces len=3 on status strings | no quotes or special chars possible |
| V5 | `ContextVar` pattern correct: `_validate_with_db_context` sets before `@validate_call`, resets in `finally` | concurrent-safe |

## Defects

All seven disposed in the fix batch (D-052, 2026-08-29).

### T1 — Header typo `Aauthor` (D-052, FIXED)
`# Aauthor Roberto Corradini` → `# Author Roberto Corradini`. Same as binio T3.

### T2 — Dead typing imports: `Callable`, `Type`, `Self` (D-052, FIXED)
Removed from the `typing` import line; `Tuple` is used (return type of `generate_positions_and_game_values`) and kept.

### T3 — Dependencies missing from `pyproject.toml` (D-052, FIXED)
`psycopg2`, `pandas`, `python-dotenv` added to the project dependencies.

### T4 — `_validate_db_fields` hits DB even when `fields=None` (D-052, FIXED)
The `SELECT ... LIMIT 0` query for `colnames` is now deferred: it only runs when `fields_input` is actually a string or list (i.e. `colnames` is needed). The common `fields=None` default returns `base_colnames` without touching the database.

### T5 — Dead imports in test_regab.py (D-052, FIXED)
Removed: `numpy.typing as npt`, `time`, `io`, `itertools`, `mock_open`, `Callable`, `TypeAlias`, `List`.

### T6 — No DB-unavailable skip mechanism (D-052, FIXED)
`BaseTestCase.setUp` now checks `SKIP_REGAB_DB=1` and calls `skipTest()`. With the env var set: 35 skipped, 2 run (the fully-mocked `TestRegabDataSetFileLoadExceptions`). Without it: 37/0/0 GREEN as before.

### T7 — SQL injection via `where` parameter (D-052, FIXED)
New `WhereArgument` with `_validate_where_clause` `AfterValidator`: blocks SQL comments (`--`, `/* */`), statement terminators (`;`), and dangerous keywords (SELECT, INSERT, UPDATE, DELETE, DROP, UNION, ALTER, CREATE, EXEC, EXECUTE, TRUNCATE). The `where` parameter of `regab_gp_as_df` is typed `WhereArgument`; docstring documents the forbidden patterns and a valid example. 4 new tests: comment, SELECT, semicolon, valid expression.

## Observations (not defects)

- **`_validate_db_fields` DB dependency**: the validator requires a live DB connection even for purely structural validation (e.g., testing that `fields=['seq', 'seq']` raises a duplicate error). This makes offline unit testing difficult — tests must mock or have a DB. (The test suite uses a real DB.)
- **`compute_sha3_256_hash` column order**: iterates `for col in df`, which uses DataFrame insertion order (always mover→opponent→game_value). Deterministic but implicit.
- **`regab_store_data_set_to_file` uses `Path(filename)`**: confirms `from pathlib import Path` is used (not dead).
- **No `self._closed` guard on `RegabDBConnection.close()`**: calling `close()` twice may raise if `conn` is already closed — but the `if self.conn:` guard at L156 prevents most double-close errors.

## Suite status

```
$ python -m unittest twolm.test.test_regab
.....................................
--------------------------------------------------------------
Ran 37 tests in 0.9s
OK

$ SKIP_REGAB_DB=1 python -m unittest twolm.test.test_regab
Ran 37 tests ... OK (skipped=35)
```

35 of 37 tests require a live PostgreSQL database and `.env` file;
2 (`TestRegabDataSetFileLoadExceptions`) are fully mocked.
`SKIP_REGAB_DB=1` skips the DB-dependent tests (T6). No PERF gates.

## Appendix: line-number reference (2026-08-29, post T1-T7)

- `GameValue`: L63
- `_validate_game_value_array`: L65
- `GameValueArray`: L72
- `RegabDBConnection`: L76
- `RegabDBConnection.__init__`: L106
- `RegabDBConnection.activate_conn`: L147
- `RegabDBConnection.close`: L153
- `rc_context`: L167
- `_validate_db_fields`: L170
- `_validate_with_db_context`: L196
- `_ensure_list`: L227
- `BidArgument`: L233
- `StatusArgument`: L236
- `EcArgument`: L242
- `_WHERE_FORBIDDEN`: L249
- `_validate_where_clause`: L255
- `WhereArgument`: L264
- `FieldsArgument`: L267
- `regab_gp_as_df`: L271
- `_ensure_column_count_and_type`: L357
- `DfMogvArgument`: L368
- `RegabDataSet`: L370
- `RegabDataSet.__init__`: L388
- `RegabDataSet.generate_positions_and_game_values`: L417
- `RegabDataSet.compute_sha3_256_hash`: L425
- `regab_extract_data_set_from_db`: L438
- `regab_load_data_set_from_file`: L470
- `regab_store_data_set_to_file`: L548