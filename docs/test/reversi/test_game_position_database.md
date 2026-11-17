# test/reversi/test_game_position_database.py

The game_position_database unit suite — 4 classes / 22 tests, no DB, < 1 s. Companion of
docs/src/reversi/game_position_database.md.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestParseRecord` | 10 | the `_parse_record` contract: the comment / separators-only classification, the four-field split, the trailing-garbage and inline-comment rules, and the five field-level error classes (each raised with its `GpdbErrorType`) |
| `TestLoadFixture` | 6 | the load on the legacy fixture (the C `db/gpdb-test-db.txt` verbatim): the 6 entries + 11 errors, the exact (0-based line, error type) sequence, the loaded entry values, the opposite-players same-board pair, the string round trip against the file's own records, the `positions` property (the dtype + the insertion order) |
| `TestLoadPolicies` | 4 | the loader policy flags (replace / keep-first / stop-on-error) and the missing-file behaviour, on synthetic files under the shared `CUSTOM_TMP_BASE` (cleaned in `tearDown`) |
| `TestDatabaseClass` | 2 | the container contract: add / find / len / iteration, and the `add_or_replace` replaced-entry return (identity) |

## Goldens pinned

- The fixture load: 6 entries + 11 errors, the full (line, type) error sequence (35/40/50-53/57/61/65/66/67), the
  all-black / all-white / all-empty values, the first-loaded duplicate kept.
- The string round trip: `game_position_to_str` of every loaded entry reproduces the file's own board+player fields.

## Conventions

- The fixture is the verbatim legacy file (no local edits): it is the C `gpdb_verify` cross-validation surface.
- The synthetic policy files live under `CUSTOM_TMP_BASE` and are unlinked in `tearDown` (the house rule R-750).

## Integration

- Module under test: `game_position_database.md`; the 65-char string↔GamePosition conversion is pinned in
  `test_board.md` (the `TestGamePosition` area F) — this suite exercises the FILE layer on top of it.
