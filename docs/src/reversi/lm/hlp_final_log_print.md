# reversi/lm/hlp_final_log_print.py
The FINAL_LOG_PRINT hlp (the 19th level): the single-function writer. `hlp_final_log_print_write_log(ctx)`
renders the machine's full event log buffer (the maximum-relevance replay, the live-line format) and writes it to
`base_dir / log_file_name` (the parents created), returning the path. The level is optional: the `cfg.log_file_name`
entry (default None) is the gate — the guard is in the worker (`wrk_final_log_print`), this function only writes.

## API
- `hlp_final_log_print_write_log(ctx) -> Path` — undecorated (the ctx idiom): reads `ctx.cfg.base_dir` +
  `ctx.cfg.log_file_name`, `mkdir(parents=True, exist_ok=True)`, `write_text(ctx.format_event_log(Relevance.DEBUG),
  encoding="utf-8")` (the buffered log from DEBUG upward — the TRACE hot-loop detail stays out of the file),
  logs "FINAL_LOG_PRINT: log written: {path} (N lines)." at DEBUG (the post-write line — it is NOT in the file,
  see the write asymmetry below), returns the `Path`.
  - **The write asymmetry** — the file is the buffer at the moment of the write: it carries the level's own "Starting
    worker FINAL_LOG_PRINT, UP step" line (the machine logs it before the worker call) but not this confirmation nor
    the "Completed UP step" line (both logged after the return).
  - **The content** — the `format_event_log` render: the newline-joined live lines, one per buffered event, NO
    trailing newline (a `write_text` of the joined string; the file's last line has no line feed). A run at any
    verbosity produces the same content (the buffer is verbosity-independent) — a HIGH run's file is what its console
    printed; a NONE run's file is the full log of a silent run.
  - **The line shape** (one example, the init DEBUG entry):
    `[2026-09-28 12:00:00 UTC] [00][CREATED        ] [DEBUG:STANDARD] StateMachine initialized.`
    — the `[ts UTC] [step:02][worker:15] [REL:VERB] message` live format (the widths 5/8, the enum names —
    the machine's `_format_event_line` renders it).

## Architecture
- **The render source** — `ctx.format_event_log()`: the bound method the StateMachine injects at construction
  (mirror: docs/src/reversi/tools/state_machine.md). It formats every buffered `LogEntry` (all
  relevances — the buffer is filled independent of the display verbosity gate) in the live console line format, via
  the machine's shared `_format_event_line` static (the single source of truth — the live print in `log_event` uses
  the same formatter).
- **The path** — `Path(ctx.cfg.base_dir) / ctx.cfg.log_file_name` (the house report pattern — relative to base_dir,
  like the analytics report / the anova report); a dir-like name (e.g. `sub/dir/full.log`) is supported — the parents
  are created.

## Verified invariants
- No test module by design: pinned by `test_wrk_final_log_print.py` (the NO-DB mock-ctx suite: the full-log write
  on a 2-line mock render, the base_dir subdir path) + the LONG-tier e2e (the rlm_00 full chain, verbosity NONE —
  the file contains every event although nothing was printed; the write-asymmetry pins).
- Pinned by `probes/verify_final_log_print.py` (A3 the writer source pin; B2/B3 the write-asymmetry invariant + the
  live-line format vs an independent re-derivation; B4 the maximum-relevance replay — all 4 pre-logged relevances in
  the file of a VERY_LOW-verbosity machine).

## Open issues
- None.

## Conventions
- The house hlp pattern: one public function, `__all__` exported, no module docstring (the mirror is the module's
  documentation).
- The docstring is in the house style (imperative first line, the body paragraph, the untyped Args, the key-by-key
  Returns).
- Undecorated (the ctx idiom): the `validate_call` boundary applies to the non-ctx public functions — this one
  takes only the context.

## Integration
- Called by `wrk_final_log_print._up` (the 19th level, the pipeline's last level — after PLOT) when
  `cfg.log_file_name` is not None (the gate is in the worker — the None path never reaches this function: the
  "skipped" no-op log, the file NOT generated).
- The config field: `LMConfig.log_file_name: str | None` (default None, mirror: hlp_config_schemas.md) — a top-level
  JSON entry; every shipped fixture (rlm_00..rlm_04) + the external A2030/A2050 configs leave it absent (the no-op
  path, zero golden impact).
- The render depends on the StateMachine's `format_event_log` (the method + the context injection) —
  the only generic-zone change of the campaign (mirror: state_machine.md).
