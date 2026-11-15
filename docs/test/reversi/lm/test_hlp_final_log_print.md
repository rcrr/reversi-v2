# test/reversi/lm/test_hlp_final_log_print.py

The `hlp_final_log_print` unit suite — 1 class / 3 tests, no DB, < 0.2 s. The run-log writer on a mock ctx:
the file lands at `base_dir / log_file_name` with the rendered event log, the parent directory is created, and
the bounded DEBUG echo is logged.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestWriteLog` | 3 | the written path and content (the renderer's text, byte-for-byte); the `mkdir(parents=True)` on a NON-EXISTENT subdirectory; the single DEBUG `log_event` echo carrying the line count |

## Goldens pinned

None. (The pins are the path, the content identity, and the echo event; no hash goldens.)

## Conventions

- the NO-DB mock-ctx idiom: a `SimpleNamespace` carrying `cfg` (base_dir + log_file_name), the
  `format_event_log` renderer, and a collecting `log_event` — the function reads exactly these.
- the scratch dir is anchored to the shared `CUSTOM_TMP_BASE` (the R-750 idiom), never the system /tmp.

## Integration

Mirrors `src/reversi/lm/hlp_final_log_print.py` (the `hlp_final_log_print_write_log` writer). The FINAL_LOG_PRINT
level in the full pipeline (its position last in the machine order, its real event buffer) stays covered by
`test_wrk_final_log_print` and the end-to-end chain; this module pins the writer itself at < 0.2 s cost.
