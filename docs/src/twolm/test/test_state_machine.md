# test_state_machine.md — analysis

Date: 2026-08-29. One test file: `test_state_machine.py` (19 tests, 3
classes), added with the module (commit 66ab84b). **Analysis session 19;
R1 + T1 applied (D-057); R2 applied with 3 new `TestLogEntry` tests
(D-058, side effect: T11 resolved); R3 sentinel pinned with 1 new
`TestStateMachine` test (D-059); R4 failure semantics pinned with 1
new test (D-060, closes T6); T2–T5, T7–T10 OPEN, fix campaign
pending Roberto's approval (together with the R5 ruling on the
module).**

Suite: **20/0/0 GREEN, no PERF gates** (13 → 15 with T1, → 18 with
the R2 tests, → 19 with the R3 sentinel pin, → 20 with the R4 retry
pin). Fast (~0.18s).

## How to run

```
$ python -m unittest twolm.test.test_state_machine
```

## Coverage by area

### `TestStateMachine` (15 tests: original 13 + 1 D-059 + 1 D-060)

| Test | What it pins |
|---|---|
| `test_initialization` | `current_step == 0`, `current_worker_name == "CREATED"`, 3 workers, exactly 1 log (the init DEBUG event). |
| `test_move_up_single_step` | 0→1: only `up[1]` called (with the context object); `down[1]` not; history len 1, direction `up`. |
| `test_move_up_multiple_steps` | 0→2: `up[1]` + `up[2]` called once each; no down; history len 2. |
| `test_move_down_single_step` | 2→1: only `down[2]` called (mocks reset first); history len 3, last direction `down`. |
| `test_move_down_to_zero` | 2→0: `down[2]` + `down[1]` once each (`down[0]` never); history len 4. |
| `test_move_to_same_step` | 0→0: no callable executed, empty history. |
| `test_worker_zero_is_sentinel_never_executed` (D-059) | up 0→2 then down 2→0: `up[0]`/`down[0]` are never invoked — pins the worker-0 sentinel semantics against a future off-by-one "fix". |
| `test_retry_after_failure_skips_failed_step` (D-060) | failure at step 1 (side_effect), retry of the same target runs only `up[2]` (failed `up[1]` skipped), then down to 0 runs `down[2]`+`down[1]` and up to 2 re-executes `up[1]` — pins the documented failure/retry/recovery semantics (T6). |
| `test_move_to_step_by_string` | `"positions"` (lowercase) → step 2, both ups executed. |
| `test_move_to_step_by_invalid_string` | Unknown name → ValueError, message contains "not found in the pipeline". |
| `test_move_to_step_out_of_bounds_high` | Index 3 (== len) → IndexError. |
| `test_move_to_step_out_of_bounds_negative` | Index −1 → IndexError. |
| `test_move_to_step_invalid_type` | `3.14` → TypeError. |
| `test_worker_exception_propagation_and_logging` | `up[1]` raising RuntimeError: re-raised; `current_step == 1` (the failed step); exactly 1 ERROR log with the right step/worker/message; history records the failed attempt (len 1). |
| `test_history_export_csv` | 2 moves (0→2, 2→0) → CSV with 4 rows; row 0 = CONFIG/up; row 3 = CONFIG/down. File cleaned up in `finally`. |

### `TestLogEntry` (3 tests, added D-058)

- `test_init_log_is_typed_record`: `logs[0]` is a `StateMachine.LogEntry`
  with the 5 field values pinned (aware-UTC `time`, step 0,
  "CREATED", `Relevance.DEBUG`, the init message).
- `test_log_entry_is_immutable`: assigning a field raises
  `FrozenInstanceError` (frozen dataclass).
- `test_asdict_form_for_dump`: `dataclasses.asdict(entry)` yields
  exactly the 5 keys `time/step/worker_name/relevance/message`
  (the file/DB dump shape for the intended final pipeline worker).
- **Coverage**: the R2 typed-record contract, incl. the three
  intended log-consumer uses (inspection, REPL, dump).

### `TestVerbosityGating` (2 tests, added D-057)

- `test_gating_matrix`: all 6 verbosity levels × 5 relevance levels
  (30 cells) — asserts on captured stdout that `log_event` prints
  iff `relevance >= verbosity` (NONE silent, VERY_LOW ERROR-only),
  and that `logs` accumulates every event even when not printed.
- `test_enum_values`: pins the D-057 split — VERY_LOW = 4, NONE = 5
  (and 0–3 unchanged).
- **Coverage**: the whole verbosity/print gate (T1), including the
  pre-fix behaviour that used to be unpinned.

**Verified**: every expectation above was re-derived independently
(ground-truth probes, docs/src/twolm/state_machine.md V1–V17) — zero
mismatches. The tests correctly pin the load-bearing semantics,
including the up/down asymmetry (target's `up` runs, target's `down`
does not), the failure semantics, and the same-step no-op.

## Test defects (T1–T11)

All OPEN; priorities proposed after the R1–R5 rulings.

### T1 — No Verbosity coverage at all (P0 with R1) — FIXED (D-057)
`Verbosity` was never exercised: the gate table (V1) — including
"NONE still prints ERROR" — was unpinned. Fixed together with R1:
`TestVerbosityGating` now pins the full 6×5 gating matrix (post
D-057: VERY_LOW ERROR-only, NONE silent) plus the enum values.

### T2 — No context-injection coverage (P0)
The injected `context.log_event` binding, `get_cache_file_path_for_next_level`
(level/name/`{level:02}` format), `get_cache_file_full_path_for_next_level`
(base_dir join; the absolute-prefix-drops-base_dir case), the
`cfg`-missing `AttributeError`, and the empty-workers `Path()` /
"UNDEFINED" / `move_to_last` no-op path are all untested (V9, V17).

### T3 — stdout is patched but never asserted (P1)
`setUp` patches `sys.stdout` globally, yet no test inspects the
captured output: `log_event`'s live print format (V12),
`show_event_log` and `show_history_of_moves` (V13) have no golden at
all. The patch is currently just noise-suppression.

### T4 — `move_to_last` untested (P1)
No test exercises `move_to_last` — happy path, empty-workers no-op, or
the duplicate-name misdirection (V8c, R5).

### T5 — CSV test is thin + writes to CWD (P2)
Only row count and 4 cell values are checked: no header-row assertion,
no ISO-8601/`+00:00` format check, no `duration_sec` value check; the
file is written to the current working directory instead of a tempdir
(cleanup is `finally`-based).

### T6 — Retry-after-failure quirk unpinned (P1 with R4) — FIXED (D-060)
A retry of the same target after a failure executes only steps above
the failed one (V6b). R4 resolved as "keep + document" (D-060): the
failure semantics are in the `move_to_step` docstring, and
`test_retry_after_failure_skips_failed_step` now pins both the
retry-skip and the down-then-up recovery.

### T7 — `bool` / `np.int64` edge unpinned (P2)
`move_to_step(True)` is silently accepted as step 1; `np.int64(1)`
raises TypeError (V7). Pin both (or the strict guard, per M3).

### T8 — `current_worker_name` untested (P2)
Property never asserted directly, including the "UNDEFINED" empty case
(V9f).

### T9 — `StepMove` content untested (P2)
History entries are asserted only on length/direction/worker_name:
aware-UTC `start`/`finish`, the `duration == finish - start` identity,
and the `finally`-append on failure are unpinned at the field level
(V14; the failure-append half is only len-asserted).

### T10 — Duplicate-name behaviour unpinned (P2)
First-match-wins on duplicate worker names (V8b) is undocumented and
unpinned; combined with T4 it hides R5.

### T11 — Dead import (P2) — RESOLVED (side effect of D-058)
`from datetime import datetime` was never used; the new
`TestLogEntry.test_init_log_is_typed_record` uses it
(`assertIsInstance(entry.time, datetime)`), so the import is now
load-bearing. (Now at L49 after the two D-057/D-058 import adds.)

## Completeness verdict

**Core move mechanics: solid.** The 13 tests cover the public move
API well (int/string targets, both directions, multi-step, same-step
no-op, bounds/type/name errors, exception propagation + logging, CSV
row semantics), and every expectation matches independently derived
behaviour.

**Three whole areas are untested**: (1) the logging/verbosity layer
(5×5 gate, live print format, show_* output); (2) the context
injection layer (the module's main integration surface with domain
workers); (3) the edge semantics (move_to_last, retry-after-failure,
bool/duplicate names, StepMove field content).

## Proposed priorities

- **P0** (with the R rulings): T1 — done (D-057); T2 (injection
  coverage), R2/R5 code fixes if approved.
- **P1**: T3 (print/display goldens), T4 (move_to_last); T6 — done
  (D-060); R4 — resolved (D-060).
- **P2**: T5, T7, T8, T9, T10 (T11 resolved with D-058) + the
  M-sweep (dead imports, cosmetics, doc notes, repr).
