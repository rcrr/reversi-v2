# reversi/tools/state_machine.py
A generic, domain-agnostic pipeline orchestrator: a StateMachine drives an ordered list of Worker steps over a shared
Context, with relevance-gated logging, per-step timing history and CSV export of the history. It knows nothing about
Reversi — the domain modules (e.g. the LM facade) subclass Context and feed it domain workers.

## API

| family | name | contract |
|---|---|---|
| Types | `Verbosity` | `IntEnum` HIGH=0 … NONE=5; an event prints iff `relevance >= verbosity` (NONE silent, VERY_LOW=ERROR-only) |
| Types | `Relevance` | `IntEnum` TRACE=0, DEBUG=1, INFO=2, WARN=3, ERROR=4 |
| Context | `Context` | empty base class for pipeline contexts — the shared state passed between workers |
| Worker | `Worker(name, up_callable, down_callable)` | one pipeline step; `@validate_call` on `__init__`/`up`/`down`; `__repr__` = `Worker('NAME')` |
| StateMachine | `StateMachine(workers, context, verbosity=STANDARD)` | `@validate_call` (arbitrary_types_allowed): non-Worker list entries / non-Context → ValidationError; duplicate worker names rejected case-insensitively (fail-fast); injects `log_event` + the two cache closures onto the context; emits the init DEBUG log |
| StateMachine | `StepMove` / `LogEntry` | `@dataclass` records: one executed step (step, worker_name, direction, start, finish, duration) / the frozen 5-field typed log record (`asdict()` for dumps) |
| StateMachine | `log_event(relevance, message)` | always appends a LogEntry; prints iff gated; `@validate_call` |
| StateMachine | `show_event_log()` / `show_history_of_moves()` | the terminal pretty-printers (frozen display goldens) |
| StateMachine | `export_history_of_moves_as_csv(filename)` | ISO-8601 UTC timestamps, float durations; creates missing parent dirs; `@validate_call` |
| StateMachine | `move_to_step(int \| str)` / `move_to_last()` | the public move API (the gate below); `move_to_last` = name-based dispatch to the last worker, no-op when empty |
| StateMachine | `__repr__` | deliberately lightweight: `workers=N, current_step=K, verbosity=LEVEL` (context/logs/history excluded — they can hold large domain data) |

## Architecture

- **State model (load-bearing)** — `current_step` is the index of the last executed step, step 0 the "nothing executed
  yet" state. Up c→t runs `up()` of workers c+1..t (target included); down c→t runs `down()` of workers c..t+1 (target
  excluded), then `current_step = t` is set explicitly (the down loop's last iteration leaves it at t+1).
- **Worker 0 is the intentional sentinel** — no public call ever invokes `workers[0].up()`/`.down()`; in the LM pipeline
  the level-0 CREATED is a dummy blocker (log ERROR + RuntimeError).
- **Failure semantics** — a failure at step k leaves `current_step == k`; a same-target retry re-runs only steps > k
  (the failed worker is skipped). Recovery: `move_to_step(k-1)` (runs k's `down()` — the domain rollback), then move up
  to re-execute k. The machine re-raises; handling the failure is the domain worker's responsibility.
- **The move gate is separate from execution** — `move_to_step` dispatches through the strict `@validate_call`
  `_validate_target_step` (int or case-insensitive name → index) and `_execute_move` (the up/down walk). Only the gate's
  ValidationError is converted to the pinned public TypeError — a DOMAIN worker's pydantic ValidationError raised during
  the move propagates unchanged. bool is not a valid step; np.int64 / float rejected with the same TypeError; unknown
  name ValueError; out of bounds IndexError.
- **Context injection (side effect)** — `__init__` unconditionally binds onto the passed context: `log_event` (this
  machine's bound method) + `get_cache_file_path_for_current_level` + `get_cache_file_full_path_for_current_level`. A
  context shared by two machines re-binds to the last machine built on it. The domain workers depend on this injection
  (a future redesign is parked in ideas.md).
- **Cache path** — `{cache_files_prefix}{level:02}_{worker}.dat` with `level = current_step`, i.e. the currently
  executing worker (the step is set BEFORE execution). The prefix is CONCATENATED verbatim (a bare prefix glues: `cache`
  → `cache01_CONFIG.dat`; a directory-like prefix must end with a separator). The full variant prepends `cfg.base_dir`
  (pathlib join — an absolute prefix silently drops base_dir). Both read `context.cfg` by bare `getattr` — a missing cfg
  raises AttributeError (the CONFIG worker must populate it first).
- **Logging** — every event becomes a frozen `LogEntry` (attribute access, `asdict()` for file/DB dumps); the live line
  is `[ts UTC] [step][name] [REL:VERB] msg` with enum names in fixed-width right-justified fields (`{REL:>5}:{VERB:>8}`,
  16 chars total); `show_event_log` / `show_history_of_moves` render the frozen-golden tables.

## Verified invariants

Pinned by `test_state_machine.py` (49 tests, 5 classes, no PERF gates).

- The state model: up includes the target, down excludes it, down-to-zero, the same-step no-op — `TestStateMachine` (the
  move_* tests).
- Worker 0's `up()`/`down()` are never invoked — `TestStateMachine::test_worker_zero_is_sentinel_never_executed`.
- A failure leaves `current_step` at the failed step, the retry skips it, the exception propagates with the ERROR log,
  and the StepMove is recorded in `finally` — `TestStateMachine` (the retry, worker-exception and
  step-move-recorded-on-failure tests).
- Duplicate worker names rejected at construction, case-insensitively (fail-fast ValueError) — `TestStateMachine` (the
  duplicate-name tests).
- `move_to_last` is unambiguous: happy path, from an intermediate position, single-worker no-op — `TestStateMachine`
  (the move_to_last_* tests).
- The move gate: case-insensitive name lookup, unknown name → ValueError, out of bounds → IndexError, bool / np.int64 /
  float → the pinned TypeError — `TestStateMachine` (the move_to_step_* and bool/numpy tests).
- Constructor guards: non-Worker list entry / non-Context → ValidationError — `TestStateMachine` (the constructor
  tests).
- The Verbosity gate: the 6×5 print matrix + the enum values (NONE silent, VERY_LOW ERROR-only) — `TestVerbosityGating`.
- LogEntry: a typed record with the field values, frozen (immutability), the `asdict()` 5-key dump form —
  `TestLogEntry`.
- Context injection: the bound `log_event`, the cache path tracking `current_step`, the base_dir join, the
  absolute-prefix drop, the verbatim prefix concatenation, missing cfg → AttributeError, the empty-workers degenerate
  paths, the shared-context re-bind — `TestContextInjection`.
- The display: the live print format, the event-log table and the history table (frozen-clock goldens) —
  `TestDisplayGoldens`.
- The CSV export: header, ISO-8601 `+00:00`, float durations, the missing-parent-dir creation — `TestStateMachine` (the
  history_export_csv + csv_export_creates_missing_parent_dirs tests).
- The lightweight `__repr__` (Worker name; StateMachine tracking the state) and `current_worker_name` (incl. the
  "UNDEFINED" empty-workers degenerate) and the unknown-direction rejection — `TestStateMachine` (the repr,
  current-worker-name and run_step tests).

## Open issues

None.

## Conventions

- House convention: `@validate_call` (arbitrary_types_allowed) on every public entry — including
  `Worker.__init__`/`up`/`down`.
- The move gate is SEPARATE from the move execution — never wrap a domain worker's call in the gate's try/except (domain
  ValidationErrors must propagate).
- The cache prefix is a filename prefix, concatenated verbatim — a directory-like prefix must end with a separator.
- The context injection is load-bearing — the domain workers depend on the bound helpers; any redesign goes through
  ideas.md, not ad-hoc.
- Aware UTC datetimes throughout; ISO-8601 with explicit `+00:00` in the CSV.
- The history records failed attempts (the finally-based timer) — deliberate.
- Test artifacts under `build/tmp` (house rule).

## Integration

- Consumes pydantic (`validate_call` — already a workspace dependency) + stdlib (enum, datetime, dataclasses,
  contextlib, typing, pathlib, csv).
- Consumed by: `base_model.py` (BaseModel) → `logistic_model.py` (the LM facade); the domain workers consume the
  injected `log_event` + cache helpers.
- Not a domain module: it knows nothing about Reversi.
