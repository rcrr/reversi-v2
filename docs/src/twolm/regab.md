# regab.py — analysis

Date: 2026-08-29. Module added by Roberto (2 files: regab.py + test_regab.py).

Suite: **33 tests, GREEN 33/0/0** (5 classes, all require live PostgreSQL + `.env`).

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
| `regab_store_data_set_to_file(rds, filename)` | Serializes to a `binio` framed binary file with SHA3-256 sidecar. |
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

### T1 — Header typo `Aauthor` (L7)
`# Aauthor Roberto Corradini` → `# Author Roberto Corradini`. Same as binio T3.

**Severity**: Cosmetic.

### T2 — Dead typing imports: `Callable`, `Type`, `Self` (L43)
`from typing import TypeAlias, Callable, Union, List, Annotated, Tuple, Type, Self, Any` — `Callable`, `Type`, and `Self` are never used in the code body. `Tuple` is used (L388 return type).

**Severity**: Cosmetic — unused imports.

### T3 — Dependencies missing from `pyproject.toml`
`psycopg2`, `pandas`, `python-dotenv` are imported at module level but not listed in `pyproject.toml`. These are hard dependencies: without them, `import twolm.regab` fails.

**Severity**: Hard import failure.

### T4 — `_validate_db_fields` hits DB even when `fields=None`
The validator always runs `SELECT * FROM regab_prng_gp LIMIT 0` (L174-176) to get `colnames`, but when `fields_input` is None/empty (the common default), `colnames` is never used — `base_colnames` is returned directly. The DB query is unnecessary work.

**Severity**: Minor — performance observation, not a correctness bug.

### T7 — SQL injection via `where` parameter
The `where` parameter in `regab_gp_as_df` (L306-307) is concatenated directly into the SQL string with no validation:
```python
q = q + ' AND {:s}'.format(where)
```
All other parameters (`bid`, `status`, `ec`, `limit`) are Pydantic-validated. `fields` goes through `_validate_db_fields`. `where` is a bare `str | None` with no validator.

**Severity**: Medium — the function is not publicly exposed (internal pipeline), but bare string concatenation into SQL is a best-practice violation.

## Observations (not defects)

- **`_validate_db_fields` DB dependency**: the validator requires a live DB connection even for purely structural validation (e.g., testing that `fields=['seq', 'seq']` raises a duplicate error). This makes offline unit testing difficult — tests must mock or have a DB. (The test suite uses a real DB.)
- **`compute_sha3_256_hash` column order**: iterates `for col in df`, which uses DataFrame insertion order (always mover→opponent→game_value). Deterministic but implicit.
- **`regab_store_data_set_to_file` uses `Path(filename)`**: confirms `from pathlib import Path` is used (not dead).
- **No `self._closed` guard on `RegabDBConnection.close()`**: calling `close()` twice may raise if `conn` is already closed — but the `if self.conn:` guard at L156 prevents most double-close errors.

## Suite status

```
$ python -m unittest twolm.test.test_regab
.................................
--------------------------------------------------------------
Ran 33 tests in 0.811s
OK
```

All 33 tests require a live PostgreSQL database and `.env` file. No PERF gates, no skip-if-DB-unavailable mechanism.

## Appendix: line-number reference (2026-08-29)

- `GameValue`: L62
- `_validate_game_value_array`: L64
- `GameValueArray`: L71
- `RegabDBConnection`: L75
- `RegabDBConnection.__init__`: L105
- `RegabDBConnection.activate_conn`: L146
- `RegabDBConnection.close`: L152
- `rc_context`: L166
- `_validate_db_fields`: L169
- `_validate_with_db_context`: L194
- `_ensure_list`: L225
- `BidArgument`: L231
- `StatusArgument`: L234
- `EcArgument`: L240
- `FieldsArgument`: L243
- `regab_gp_as_df`: L247
- `_ensure_column_count_and_type`: L328
- `DfMogvArgument`: L339
- `RegabDataSet`: L341
- `RegabDataSet.generate_positions_and_game_values`: L388
- `RegabDataSet.compute_sha3_256_hash`: L396
- `regab_extract_data_set_from_db`: L409
- `regab_load_data_set_from_file`: L441
- `regab_store_data_set_to_file`: L519