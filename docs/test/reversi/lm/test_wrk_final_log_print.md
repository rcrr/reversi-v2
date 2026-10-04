# test/reversi/lm/test_wrk_final_log_print.py
The FINAL_LOG_PRINT worker suite (the 19th level): the factory (the worker name), the config-gate no-op (the
absent log_file_name, the file NOT generated), the full-log write (the max-relevance replay over the machine's event
buffer), the base_dir subdir path, the down (the no-op) — and the LONG-tier end-to-end (the rlm_00 full chain, the
log_file_name entry in the config from the start — the D-322 tmp
fixture copy, the write-asymmetry pins). 2 classes / 6 tests (5 no-DB + 1 DB-gated e2e).

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestWrkFinalLogPrint` | 5 | `test_factory` (the worker factory: the FINAL_LOG_PRINT name); `test_skipped_no_file` (the absent log_file_name (the default None) -> the no-op (the "skipped" log) + the file NOT generated); `test_full_log_written` (the configured name -> the file under base_dir with the full buffered content (the mock render) + the "full log written" log); `test_subdir_path` (the dir-like name -> the parents created); `test_down_no_op` (the no-op: the log note) |
| `TestFinalLogPrintEndToEnd` | 1 | `test_full_chain_writes_the_full_log` (the LONG tier, the rlm_00 full chain, verbosity NONE — nothing prints, the buffer captures everything; the log_file_name entry in the config from the start — the D-322 tmp fixture copy (a post-CONFIG cfg mutation desyncs the config checksum fingerprinted at CONFIG: the SAVE-embedded live dump vs the fingerprint, the CLIENT_CHECK section check raises); step 19 / FINAL_LOG_PRINT last; the write-asymmetry pins: the file carries its own "Starting worker FINAL_LOG_PRINT, UP step" line but NOT the "Completed UP step" nor the "full log written" line (both post-write); the line count == the final buffer minus the two trailing post-write lines; the "Completed UP step for PLOT" present (the whole chain in the file); no FINAL_LOG_PRINT skipped line (the other levels' no-op notes — e.g. "PLOT skipped" — are expected full-log content) |

## Goldens pinned

- The mock render: the two fixed lines (the machine's renderer is a stand-in in the NO-DB suite — the render itself is
  tested in test_state_machine + the probe).
- The e2e: the rlm_00 fixture as a tmp copy WITH the log_file_name entry (the D-322 fix — the entry must be present
  BEFORE the CONFIG level; the shipped fixture stays untouched), the "full_run.log" file under the CUSTOM_TMP_BASE
  base_dir.
- The write asymmetry: the file is the buffer at the moment of the write (the "Starting" line IN — the machine logs it
  before the worker call; the two trailing lines OUT).

## Conventions

- The house test header (the "How to run" block).
- The NO-DB mock-ctx suite: the `_MockCtx` (the cfg — the real one, the facade runs CREATED -> CONFIG on the rlm_00
  fixture, the idiom — the event buffer, the format_event_log stand-in): the worker is exercised DIRECTLY
  (_up/_down), no machine involved.
- The `db_long_gate` standard gate (SKIP_REGAB_DB + LONG) + the e2e tmp under CUSTOM_TMP_BASE.
- The a/b/c rule (probe_rules §3): the factory name, the no-op log, the file existence, the subdir path and the down
  no-op live HERE — the probe (verify_final_log_print.py) does not repeat them (it owns the cross-file structure
  facts + the write-asymmetry invariant on a synthetic machine + the format cross-check).
- The step pin (19 / FINAL_LOG_PRINT) is the pipeline-shape pin of this suite — the full-chain suites carry the same
  pin.

## Integration

- Consumed by `run_utests.sh` (section 4 — the pipeline, at the 19th-level worker position: after the PLOT worker,
  before the full-chain suite).
- Exercises `wrk_final_log_print` (the 19th level) + the config field (LMConfig.log_file_name) + the
  machine-injected `format_event_log` (the generic-machine method, tested natively in
  test/reversi/tools/test_state_machine.py — the `test_format_event_log_full_replay` frozen-clock golden + the
  injection pin).
