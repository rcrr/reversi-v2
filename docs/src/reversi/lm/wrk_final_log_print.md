# reversi/lm/wrk_final_log_print.py
The FINAL_LOG_PRINT worker (the 19th active level (step 19), the pipeline's LAST level): it writes the FULL RUN LOG
to a file — every buffered event of every level at the maximum relevance (the machine's event log buffer, captured
independently of the display verbosity gate) in the live console line format. The level is OPTIONAL: the config
entry `log_file_name` (default None, the entry absent in every existing fixture/config) is the gate — absent entry,
the level is a no-op and the file is NOT generated. The down is a no-op — the worker publishes nothing on the ctx
(the file is a base_dir artifact, the `_down` does not unlink it).

## API
- `wrk_final_log_print() -> Worker` — the factory: the `Worker("FINAL_LOG_PRINT", _up, _down)` (the house worker
  pattern).
- `_up(ctx)`: the thin orchestrator — (1) the config gate: `cfg.log_file_name is None` makes the level a no-op (the
  "FINAL_LOG_PRINT skipped: no log_file_name." log, the file NOT generated); (2) otherwise
  `hlp_final_log_print_write_log(ctx)`.
- `_down(ctx)`: a no-op (the failure recovery is trivially satisfied — the worker publishes nothing on the ctx).
- The write logic lives in hlp_final_log_print (mirror: docs/src/reversi/lm/hlp_final_log_print.md):
  `hlp_final_log_print_write_log(ctx) -> Path`.

## Architecture
- **The log source** — the machine's event log buffer: the StateMachine fills `self.logs` (the typed `LogEntry`
  records — time, step, worker_name, relevance, message) on EVERY `log_event`, independent of the verbosity gate (the
  gate only filters the console print). The "maximum relevance" is therefore already captured — the level serializes
  what the run produced, at full fidelity.
- **The render** — `StateMachine.format_event_log()` (the generic machine's full-buffer render): it formats every
  buffered entry in the live console line format — the shared `_format_event_line` static (the single source of truth,
  the live print in `log_event` uses it too) — and joins with newlines. Injected onto the context at machine
  construction (`self.context.format_event_log = self.format_event_log`, the established injection pattern).
- **The write** — `base_dir / log_file_name` (the house report pattern — relative to base_dir), the parents created
  (`mkdir(parents=True)`), UTF-8.
- **The write asymmetry** — the file is the buffer at the moment of the write: it CARRIES the level's own
  "Starting worker FINAL_LOG_PRINT, UP step" line (the machine logs it before the worker call) but NOT the
  "FINAL_LOG_PRINT: full log written: …" confirmation nor the "Completed UP step" line (both logged after the return).
  Pinned by the e2e test + the probe B2.
- **NO cache** — a diagnostic (the file is a byproduct); no cache slot (like PLOT / ANOVA).

## Verified invariants
- Pinned by `test_wrk_final_log_print.py` (5 NO-DB tests + 1 LONG-tier e2e): the factory (the FINAL_LOG_PRINT name);
  the config-gate no-op (no file, the "skipped" log); the full-log write (the file under base_dir with the full
  buffered content); the base_dir subdir path (the parents created); the down (a no-op). The e2e (the rlm_00 full
  chain, `log_file_name` in the config from the start — the tmp fixture copy, verbosity NONE — nothing
  prints, the buffer captures everything): step 19 / FINAL_LOG_PRINT last, the write-asymmetry pins (the
  "Starting" line IN, the "Completed" + "full log written" lines OUT, the line count == the buffer at the
  write).
- Pinned by `probes/verify_final_log_print.py` (12 checks, no DB): the module structure (the factory, the skip
  branch, the hlp writer, the config field, the machine method + injection, the registration last in
  logistic_model); the behavior on a synthetic 2-worker machine (the disabled no-op, the enabled write-asymmetry
  invariant, the live-line format vs an independent re-derivation, the maximum-relevance replay).
- The pipeline shape (19 levels, FINAL_LOG_PRINT last) is pinned by `probes/verify_logistic_model.py` V3c.

## Open issues
- None.

## Conventions
- The house worker pattern: the `wrk_X() -> Worker` factory + the `_up`/`_down`; the gate in the worker, the logic in
  the hlp (the PLOT idiom, the wrk/hlp split).
- The docstring style (the house rule) in hlp_final_log_print.
- The optional gate by PRESENCE (the `log_file_name` entry), not by a boolean flag (if the entry is absent, the file
  is NOT generated).

## Integration
- The worker consumes the `ctx.cfg` (the `log_file_name` field, default None) + the
  machine-injected `format_event_log` renderer.
- The full wiring registers the worker at step 19 (after PLOT — the pipeline's last level). The `target_level` "last"
  (the config default) resolves by name — the new level is included automatically in the existing configs (the
  fixtures + the external A2030/A2050 configs carry no `log_file_name` -> the no-op path, zero golden impact).
