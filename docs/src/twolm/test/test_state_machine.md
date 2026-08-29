# test_state_machine.md — analysis

Date: 2026-08-29. One test file: `test_state_machine.py` (49 tests, 5
classes), added with the module (commit 66ab84b). **Analysis session 19;
R1 + T1 applied (D-057); R2 applied with 3 new `TestLogEntry` tests
(D-058, side effect: T11 resolved); R3 sentinel pinned with 1 new
`TestStateMachine` test (D-059); R4 failure semantics pinned with 1
new test (D-060, closes T6); R5 resolved (D-061) with 2 new
duplicate-name tests, which also close T10 (duplicates unreachable);
T2 resolved with 7 new `TestContextInjection` tests (D-062);
T3 resolved with 3 new `TestDisplayGoldens` tests (D-063);
T4 resolved with 3 new `move_to_last` tests (D-064);
T5 resolved by rewriting `test_history_export_csv` (D-065 — the
suite count is unchanged, it is a rewrite, not an addition)
together with the new house rule: test artifacts are written only
under `workspace_root/build/tmp` and removed afterwards;
T7 resolved with 2 new bool/np.int64 pin tests (D-066);
T8 + T9 resolved together with 5 new tests (D-067:
current_worker_name + StepMove field content); M-sweep: M1 + M4 +
M7 + M10 applied with 4 new `TestStateMachine` tests (D-068:
explicit direction dispatch, `__repr__` on Worker/StateMachine,
CSV export creates missing parent dirs); M-sweep: M3 + M5 + M8 +
M11 applied (D-069: bool rejected, cache helpers renamed
`*_for_current_level`, pathlib join of the cache prefix,
@validate_call on the public surface — 3 new tests, the bool test
rewritten to rejection); M-sweep closed with M6 + M9 (D-070: M6
print cleanup — enum names + explicit UTC marker on the live line,
`TIMESTAMP (UTC)` header / 2-digit step / `RELEVANCE` name column /
66-underscore rule in `show_event_log`, right-aligned `Dur (s)`
header in `show_history_of_moves` — the 3 display goldens
rewritten in place, suite count unchanged; M9 left as-is, the
injection is load-bearing — the future redesign is parked at
I-010). **All T items resolved; M-sweep COMPLETE (M1-M12 all
disposed; M2, M12 done).**

Suite: **49/0/0 GREEN, no PERF gates** (13 → 15 with T1, → 18 with
the R2 tests, → 19 with the R3 sentinel pin, → 20 with the R4 retry
pin, → 22 with the D-061 duplicate-name tests, → 29 with the D-062
context-injection tests, → 32 with the D-063 display goldens, → 35
with the D-064 move_to_last pins, → 37 with the D-066
bool/np.int64 pins, → 42 with the D-067 current_worker_name +
StepMove pins, → 46 with the D-068 M-sweep pins (M4 dispatch, M7
repr, M10 CSV parent dirs), → 49 with the D-069 M-sweep pins (M3
bool rejection, M11 constructor ValidationErrors, M8 Path prefix
join). Fast (~0.23s).

## How to run

```
$ python -m unittest twolm.test.test_state_machine
```

## Coverage by area

### `TestStateMachine` (34 tests: original 13 + 1 D-059 + 1 D-060 + 2 D-061 + 3 D-064 + 2 D-066 + 5 D-067 + 4 D-068 + 3 D-069)

| Test | What it pins |
|---|---|
| `test_initialization` | `current_step == 0`, `current_worker_name == "CREATED"`, 3 workers, exactly 1 log (the init DEBUG event). |
| `test_move_up_single_step` | 0→1: only `up[1]` called (with the context object); `down[1]` not; history len 1, direction `up`. |
| `test_move_up_multiple_steps` | 0→2: `up[1]` + `up[2]` called once each; no down; history len 2. |
| `test_move_down_single_step` | 2→1: only `down[2]` called (mocks reset first); history len 3, last direction `down`. |
| `test_move_down_to_zero` | 2→0: `down[2]` + `down[1]` once each (`down[0]` never); history len 4. |
| `test_move_to_same_step` | 0→0: no callable executed, empty history. |
| `test_move_to_last_happy_path` (D-064) | `move_to_last()` from step 0: name-based dispatch to the last worker (unambiguous since D-061) — `up[1]` + `up[2]` executed, `current_step` 2, history len 2. |
| `test_move_to_last_from_intermediate_position` (D-064) | From step 1: only the remaining `up[2]` executes (already-executed `up[1]` not re-run), `current_step` 2, history len 2. |
| `test_move_to_last_single_worker_noop` (D-064) | Single-worker machine: the only worker is the step-0 sentinel — `move_to_last()` is a no-op (no callable invoked, state untouched). |
| `test_worker_zero_is_sentinel_never_executed` (D-059) | up 0→2 then down 2→0: `up[0]`/`down[0]` are never invoked — pins the worker-0 sentinel semantics against a future off-by-one "fix". |
| `test_retry_after_failure_skips_failed_step` (D-060) | failure at step 1 (side_effect), retry of the same target runs only `up[2]` (failed `up[1]` skipped), then down to 0 runs `down[2]`+`down[1]` and up to 2 re-executes `up[1]` — pins the documented failure/retry/recovery semantics (T6). |
| `test_move_to_step_by_string` | `"positions"` (lowercase) → step 2, both ups executed. |
| `test_move_to_step_by_invalid_string` | Unknown name → ValueError, message contains "not found in the pipeline". |
| `test_move_to_step_out_of_bounds_high` | Index 3 (== len) → IndexError. |
| `test_move_to_step_out_of_bounds_negative` | Index −1 → IndexError. |
| `test_move_to_step_invalid_type` | `3.14` → TypeError. |
| `test_bool_rejected_as_int_step` (D-069) | `move_to_step(True)` and `move_to_step(False)` → TypeError (same message as the np.int64 case); machine untouched (step 0, no history, init log only) — bool is explicitly NOT a valid step (M3, D-069). Rewritten from `test_bool_accepted_as_int_step` (D-066). |
| `test_numpy_int64_rejected` (D-066) | `move_to_step(np.int64(1))` → TypeError ("integer index or a string worker name") — np.int64 is not a Python int subclass (V7); still TypeError through the D-069 strict gate + wrapper. |
| `test_constructor_rejects_non_worker_entry` (D-069) | `StateMachine([42], Context())` → pydantic `ValidationError` (@validate_call on `__init__`, M11) instead of a raw AttributeError. |
| `test_constructor_rejects_non_context` (D-069) | Non-Context object → `ValidationError`; a `Context` subclass (RLMContext) still passes. |
| `test_current_worker_name_tracks_current_step` (D-067) | The property is a live view of (workers, current_step): CREATED → CONFIG → POSITIONS → CREATED across the moves. |
| `test_current_worker_name_empty_workers_undefined` (D-067) | No workers → "UNDEFINED" (V9f). |
| `test_step_move_fields_up` (D-067) | StepMove field content for both up entries: step/worker_name/direction, aware-UTC start/finish (`utcoffset() == 0`), `finish >= start`, and `duration == finish - start` exactly. |
| `test_step_move_fields_down` (D-067) | Down-move entries: the target is excluded — the last entries are (2, POSITIONS, down) then (1, CONFIG, down), duration identity on both. |
| `test_step_move_recorded_on_failure` (D-067) | A failed step is still recorded (the timer's finally): field-level pin (step 1, CONFIG, up, aware-UTC finish, duration identity) — not just a len assert. |
| `test_worker_exception_propagation_and_logging` | `up[1]` raising RuntimeError: re-raised; `current_step == 1` (the failed step); exactly 1 ERROR log with the right step/worker/message; history records the failed attempt (len 1). |
| `test_history_export_csv` (rewritten D-065) | 2 moves (0→2, 2→0) → CSV with 4 rows; exact header field names (`step,worker_name,direction,start_utc,finish_utc,duration_sec`); row 0 = step 1 CONFIG/up; row 3 = step 1 CONFIG/down; every row: ISO-8601 `+00:00` aware-UTC timestamps (parsed back, `tzinfo` non-None) and `duration_sec == finish - start`. Artifact under `workspace_root/build/tmp`, removed in `finally`. |
| `test_duplicate_worker_names_raise` (D-061) | Two workers both named `"A"` → `ValueError` at construction, message contains "Duplicate worker name". |
| `test_duplicate_worker_names_case_insensitive` (D-061) | Workers `"CONFIG"` + `"config"` → same `ValueError`: the uniqueness check is case-insensitive, matching the case-insensitive name resolution. |
| `test_run_step_rejects_unknown_direction` (D-068) | `_run_step`'s direction dispatch is explicit: `"sideways"` → `ValueError` (the bad value in the message) and neither `up` nor `down` callable runs (M4). |
| `test_worker_repr` (D-068) | `repr(workers[1]) == "Worker('CONFIG')"` (M7). |
| `test_state_machine_repr_tracks_state` (D-068) | `repr(sm)` is the compact state summary `workers=3, current_step=0, verbosity=STANDARD`, tracks `current_step` after a move, and reflects a custom verbosity by name (`NONE`); context/logs/history are not in it (M7). |
| `test_csv_export_creates_missing_parent_dirs` (D-068) | A nested filename under `build/tmp` (parents absent) is created by the export; header + 1 row verified; artifact and its dirs removed in `finally` (M10; D-065 house rule). |
| `test_path_cache_prefix_joins_without_gluing` (D-069) | A `Path("cache")` prefix (no trailing slash) is joined with pathlib — `cache/01_CONFIG.dat` and `base/cache/01_CONFIG.dat`, no silent gluing (M8). |

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

### `TestContextInjection` (8 tests: 7 added D-062 + 1 D-069)

- `test_injected_log_event_is_live_machine_binding`:
  `context.log_event.__self__ is sm` and a call through the injected
  binding appends a `LogEntry` (step/worker/relevance/message pinned)
  to this machine's logs.
- `test_cache_file_path_tracks_current_step`:
  `{prefix}{level:02}_{name}.dat` with `level = current_step` at call
  time — `00_CREATED` → `02_POSITIONS` → `01_CONFIG` across moves.
- `test_cache_file_full_path_joins_base_dir`: relative prefix under
  `cfg.base_dir` → `base/cache/01_CONFIG.dat`.
- `test_absolute_cache_prefix_drops_base_dir`: absolute prefix
  (`/abs/cache/`) drops `base_dir` (pathlib `/`, V9) — full path is
  the bare path.
- `test_missing_cfg_raises_attribute_error`: without a populated `cfg`
  both helpers raise `AttributeError` naming `cfg` (bare getattr, no
  default).
- `test_empty_workers_degenerate_paths`: empty pipeline → `Path()`
  cache path, `"UNDEFINED"` worker name, `move_to_last` guarded
  no-op (no exception, state untouched).
- `test_shared_context_rebinds_to_last_machine`: a context shared by
  two machines re-binds to the **last** one built (helper output and
  `log_event` target flip to machine 2 — V17, the injection is a
  side effect).
- **Coverage**: the whole context-injection layer (T2) — the module's
  main integration surface with domain workers.

### `TestDisplayGoldens` (3 tests, added D-063; goldens rewritten
in place D-070/M6 to the cleaned format)

The module's `datetime` is patched with a frozen clock advancing
1ms per `now()` call, so every golden is exact and wall-clock
independent.

- `test_log_event_live_print_format`: the live line
  `[ts UTC] [step:02][name:15] [rel.name:verb.name] message` — full
  golden for the init DEBUG line + the two CONFIG INFO lines; pins
  the enum-NAME rendering (`[DEBUG:HIGH]`) + the explicit `UTC`
  marker (M6, D-070) and the padding.
- `test_show_event_log_golden`: end-to-end buffer — the move's live
  lines, then the table: banner, 66-underscore separator, header
  `TIMESTAMP (UTC) | STEP | WORKER | RELEVANCE | MESSAGE` (2-digit
  step, relevance name), one row per log entry (M6, D-070).
- `test_show_history_of_moves_golden`: end-to-end buffer — the
  move's live lines, then the table: header (the `Dur (s)` header
  right-aligned over its values, M6, D-070), 80-dash rule, one row
  per executed step; microsecond start stamps and `duration =
  finish - start` pinned at 0.003000 by the frozen clock.
- **Coverage**: the whole display layer (T3) — `setUp`'s global
  stdout patch is no longer noise suppression: captured stdout is
  asserted.

**Verified**: every expectation above was re-derived independently
(ground-truth probes, docs/src/twolm/state_machine.md V1–V17) — zero
mismatches. The tests correctly pin the load-bearing semantics,
including the up/down asymmetry (target's `up` runs, target's `down`
does not), the failure semantics, and the same-step no-op.

## Test defects (T1–T11)

Status: all T items resolved — T1 (D-057), T2 (D-062), T3 (D-063),
T4 (D-064), T5 (D-065), T6 (D-060), T7 (D-066), T8 + T9 (D-067),
T10 (D-061), T11 (D-058). Priorities proposed after the R1–R5
rulings.

### T1 — No Verbosity coverage at all (P0 with R1) — FIXED (D-057)
`Verbosity` was never exercised: the gate table (V1) — including
"NONE still prints ERROR" — was unpinned. Fixed together with R1:
`TestVerbosityGating` now pins the full 6×5 gating matrix (post
D-057: VERY_LOW ERROR-only, NONE silent) plus the enum values.

### T2 — No context-injection coverage (P0) — FIXED (D-062)
The injected `context.log_event` binding, `get_cache_file_path_for_current_level`
(level/name/`{level:02}` format), `get_cache_file_full_path_for_current_level`
(base_dir join; the absolute-prefix-drops-base_dir case), the
`cfg`-missing `AttributeError`, and the empty-workers `Path()` /
"UNDEFINED" / `move_to_last` no-op path are now all pinned by the 7
`TestContextInjection` tests (incl. the V17 shared-context re-bind).
Side finding during the work: the prefix was f-string-concatenated,
so a prefix without a trailing separator silently glued the level
name onto it (any `Path` prefix, since `str(Path)` drops the
trailing slash) — recorded in M8 (module doc); FIXED in D-069 with
the pathlib join + `test_path_cache_prefix_joins_without_gluing`
(8th test).

### T3 — stdout is patched but never asserted (P1) — FIXED (D-063)
`setUp` patches `sys.stdout` globally, yet no test inspects the
captured output: `log_event`'s live print format (V12),
`show_event_log` and `show_history_of_moves` (V13) had no golden at
all. Now `TestDisplayGoldens` pins all three paths with exact
end-to-end goldens under a frozen clock (1ms per `now()` call); the
stdout patch is now load-bearing, not noise suppression.

### T4 — `move_to_last` untested (P1) — FIXED (D-064)
No test exercised `move_to_last`. Now 3 new `TestStateMachine`
tests pin the live behaviour: happy path from step 0 (name-based
dispatch to the last worker — unambiguous since D-061), from an
intermediate position (only the remaining step executes), and the
single-worker no-op (the only worker is the step-0 sentinel, D-059
+ D-061). The empty-workers no-op was already pinned with D-062
(`test_empty_workers_degenerate_paths`); the duplicate-name
misdirection (V8c, R5) is unreachable (D-061).

### T5 — CSV test is thin + writes to CWD (P2) — FIXED (D-065)
`test_history_export_csv` now asserts the exact header field names,
the ISO-8601 `+00:00` aware-UTC format (parsed back with
`datetime.fromisoformat`, `tzinfo` non-None) and the
`duration_sec == finish - start` identity for every row, in addition
to the original row count + cell assertions. The artifact is written
under `workspace_root/build/tmp` (house rule, D-065: test files are
written ONLY there and removed afterwards — a `finally` unlink, so a
failing test leaves no garbage either) instead of the current
working directory.

### T6 — Retry-after-failure quirk unpinned (P1 with R4) — FIXED (D-060)
A retry of the same target after a failure executes only steps above
the failed one (V6b). R4 resolved as "keep + document" (D-060): the
failure semantics are in the `move_to_step` docstring, and
`test_retry_after_failure_skips_failed_step` now pins both the
retry-skip and the down-then-up recovery.

### T7 — `bool` / `np.int64` edge unpinned (P2) — FIXED (D-066)
`move_to_step(True)` is silently accepted as step 1; `np.int64(1)`
raises TypeError (V7). Now both are pinned (test-only):
`test_bool_accepted_as_int_step` (True → step 1, False → step 0
no-op) and `test_numpy_int64_rejected` (TypeError with the exact
message fragment). The optional strictness guard for bool (M3)
remains Roberto's call in the M-sweep — the pins document the
current behaviour either way.

### T8 — `current_worker_name` untested (P2) — FIXED (D-067)
Property never asserted directly, including the "UNDEFINED" empty
case (V9f). Now pinned: it is a live view of (workers, current_step)
across up and down moves, and returns "UNDEFINED" on an empty
pipeline.

### T9 — `StepMove` content untested (P2) — FIXED (D-067)
History entries are now asserted at field level (V14): up and down
entries carry aware-UTC `start`/`finish` (`utcoffset() == 0`),
`finish >= start`, and the exact `duration == finish - start`
identity; the down-move sequence confirms the excluded target; and
a failed step is still recorded by the timer's `finally` — pinned
with field content, not just a len assert.

### T10 — Duplicate-name behaviour unpinned (P2) — RESOLVED (D-061)
Moot by construction: D-061 rejects duplicate names in `__init__`
(case-insensitive `ValueError`), so first-match-wins (V8b) is
unreachable. The new behaviour is pinned by the two D-061 tests
(reject + case-insensitive).

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

**The whole module is now pinned**: the move mechanics (including
`move_to_last`, D-064), the verbosity gate (D-057), the display
layer goldens (D-063), retry-after-failure (D-060), duplicate names
(D-061), the context injection layer — the module's main
integration surface with domain workers (D-062), the CSV export
contract (D-065), the bool/np.int64 index edge (D-066), and
`current_worker_name` + the `StepMove` field content (D-067), and
the M-sweep pins (D-068: explicit `_run_step` direction dispatch,
`__repr__` on Worker/StateMachine, CSV parent-dir creation; D-069:
bool rejection, renamed cache helpers, pathlib prefix join,
@validate_call on the public surface).
Nothing remains in the T list; the M-sweep is down to M6 (cosmetic
print drift) and M9 (injection side effect) — both awaiting
Roberto's call.

## Proposed priorities

- **P0** (with the R rulings): T1 — done (D-057); T2 — done (D-062);
  R2 — resolved (D-058); R5 — resolved (D-061).
- **P1**: T3 — done (D-063); T4 — done (D-064); T6 — done (D-060);
  R4 — resolved (D-060).
- **P2**: all done — T5 (D-065), T7 (D-066), T8 + T9 (D-067), T11
  (D-058 side effect), T10 (D-061) — + M-sweep: M1, M4, M7, M10
  done (D-068); M3, M5, M8, M11 done (D-069); M12 closed with
  D-061; remaining: M6 (cosmetic print), M9 (injection side
  effect) — both Roberto's calls.
