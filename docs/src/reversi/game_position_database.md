# reversi/game_position_database.py
The v2 port of the legacy C game_position_db module: it reads a database of game positions from a text file in the
gpdb record format and returns them as GamePosition scalars (the v2 relative view). It keeps the C record format,
the six syntax-error classes, and the three loader policy flags.

## API

The 5 `__all__` names.

| name | contract |
|---|---|
| `GpdbErrorType` | the Enum of the six syntax-error classes (the C `gpdb_syntax_err_type_t`): INCOMPLETE_ENTRY, BOARD_SIZE_IS_NOT_64, SQUARE_CHAR_IS_INVALID, PLAYER_IS_NOT_ONE_CHAR, PLAYER_CHAR_IS_INVALID, DUPLICATE_ENTRY_KEY |
| `GpdbSyntaxError` | the `ValueError` carrying `file_name`, the 0-based `line_number`, the raw `line`, the `error_type`, and the `message` (the C `gpdb_syntax_err_t`) |
| `GpdbEntry` | the frozen dataclass `(id, description, position)` — the position is a GamePosition scalar |
| `GamePositionDatabase` | the entry container keyed by id (insertion order kept): `description`, `__len__`, `__iter__`, `find(id) -> GpdbEntry \| None`, `add_or_replace(entry) -> replaced \| None` (the replaced entry keeps its position), the `positions` property (the entries stacked into a 1-D GamePositionArray) |
| `load_game_position_database(file_name, duplicates_are_errors=True, replace_duplicates=False, stop_on_error=False) -> (GamePositionDatabase, list[GpdbSyntaxError])` | the C `gpdb_dictionary_load`: the fresh db (description = the file name), the error log in line order; a missing file gives the empty db + empty log |

The record format (one line per record, the fields `;`-separated): `id;board;player;description;` — the board is
64 chars in `[bw.]` (char i = square i), the player one char in `[bw]`, the description free text. The board+player
fields are the 65-char GamePosition string of `board.py` (`game_position_from_str`). A line with no character other
than `;` (before a `#`) is a comment; anything after the fourth `;` is ignored.

## Architecture

- **The parse** (`_parse_record`, private) mirrors the C `gpdb_parse_line` line by line: the `#` cut, the
  separators-only comment classification, the four-field requirement (four `;`), and the board / player field
  checks — each failure raises the matching `GpdbSyntaxError` with the C message wording.
- **The load loop** is a plain per-line Python call of the public `game_position_from_str` on the 65-char
  board+player string: the single source of the string→GamePosition conversion stays in `board.py` (no duplicated
  parsing logic here). The databases are small (the test / POC use) — the per-record cost is irrelevant, and a
  vectorized bulk path is deliberately not built.
- **The duplicate policy** mirrors the C flag trio: with `duplicates_are_errors` (default True) a duplicate key is
  logged and the record discarded; otherwise `replace_duplicates` decides between replace (the entry keeps its
  insertion position) and keep-the-first (the record is dropped silently).

## Verified invariants

- The record parse: the comment classification, the four-field split, the trailing-garbage / inline-comment rules,
  and the five field-level error classes — `test_game_position_database::TestParseRecord`.
- The fixture load (the C `db/gpdb-test-db.txt` verbatim): 6 entries + 11 errors, the exact (line, type) error
  sequence, the entry values, and the string round trip against the file's own records —
  `test_game_position_database::TestLoadFixture`.
- The policy flags (replace / keep-first / stop-on-error) and the missing-file behaviour —
  `test_game_position_database::TestLoadPolicies`.
- The container contract (add / find / len / iteration / the replaced-entry return) —
  `test_game_position_database::TestDatabaseClass`.

## Open issues

None.

## Conventions

- The line numbering is 0-based (the C convention) — the errors carry it.
- New error classes join `GpdbErrorType` only; the messages keep the C wording.
- The module owns the FILE format; the 65-char string↔GamePosition conversion belongs to `board.py`.

## Integration

- Consumes: `board.py` (`GamePosition`, `game_position_from_str`, the player constants).
- Consumed by: the test suites and the probes that need documented position batches; the MULTI-PLY campaign
  (the mid-game anchor positions, the 8.3 pivot).
