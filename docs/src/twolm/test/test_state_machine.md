# test_state_machine.md — analysis

Date: 2026-08-29. One test file: `test_state_machine.py` (32 tests, 5
classes), added with the module (commit 66ab84b). **Analysis session 19;
R1 + T1 applied (D-057); R2 applied with 3 new `TestLogEntry` tests
(D-058, side effect: T11 resolved); R3 sentinel pinned with 1 new
`TestStateMachine` test (D-059); R4 failure semantics pinned with 1
new test (D-060, closes T6); R5 resolved (D-061) with 2 new
duplicate-name tests, which also close T10 (duplicates unreachable);
T2 resolved with 7 new `TestContextInjection` tests (D-062);
T3 resolved with 3 new `TestDisplayGoldens` tests (D-063);
T4, T5, T7–T9 remain OPEN.**

Suite: **32/0/0 GREEN, no PERF gates** (13 → 15 with T1, → 18 with
the R2 tests, → 19 with the R3 sentinel pin, → 20 with the R4 retry
pin, → 22 with the D-061 duplicate-name tests, → 29 with the D-062
context-injection tests, → 32 with the D-063 display goldens).
Fast (~0.09s).

## How to run

```
$ python -m unittest twolm.test.test_state_machine
```

## Coverage by area

### `TestStateMachine` (17 tests: original 13 + 1 D-059 + 1 D-060 + 2 D-061)

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
| `test_duplicate_worker_names_raise` (D-061) | Two workers both named `"A"` → `ValueError` at construction, message contains "Duplicate worker name". |
| `test_duplicate_worker_names_case_insensitive` (D-061) | Workers `"CONFIG"` + `"config"` → same `ValueError`: the uniqueness check is case-insensitive, matching the case-insensitive name resolution. |

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

### `TestContextInjection` (7 tests, added D-062)

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

### `TestDisplayGoldens` (3 tests, added D-063)

The module's `datetime` is patched with a frozen clock advancing
1ms per `now()` call, so every golden is exact and wall-clock
independent.

- `test_log_event_live_print_format`: the live line
  `[ts] [step:02][name:15] [rel:verb] message` — full golden for the
  init DEBUG line + the two CONFIG INFO lines; pins the numeric
  IntEnum rendering (`[1:0]`, `[2:0]`, M6) and the padding.
- `test_show_event_log_golden`: end-to-end buffer — the move's live
  lines, then the table: banner, 54-dash separator, header, one row
  per log entry (`step:04`, `name:15`, numeric relevance).
- `test_show_history_of_moves_golden`: end-to-end buffer — the
  move's live lines, then the table: header, 80-dash rule, one row
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

Status: T1 (D-057), T2 (D-062), T3 (D-063), T6 (D-060), T10 (D-061),
T11 (D-058) resolved; T4, T5, T7–T9 OPEN. Priorities proposed after
the R1–R5 rulings.

### T1 — No Verbosity coverage at all (P0 with R1) — FIXED (D-057)
`Verbosity` was never exercised: the gate table (V1) — including
"NONE still prints ERROR" — was unpinned. Fixed together with R1:
`TestVerbosityGating` now pins the full 6×5 gating matrix (post
D-057: VERY_LOW ERROR-only, NONE silent) plus the enum values.

### T2 — No context-injection coverage (P0) — FIXED (D-062)
The injected `context.log_event` binding, `get_cache_file_path_for_next_level`
(level/name/`{level:02}` format), `get_cache_file_full_path_for_next_level`
(base_dir join; the absolute-prefix-drops-base_dir case), the
`cfg`-missing `AttributeError`, and the empty-workers `Path()` /
"UNDEFINED" / `move_to_last` no-op path are now all pinned by the 7
`TestContextInjection` tests (incl. the V17 shared-context re-bind).
Side finding during the work: the prefix is f-string-concatenated, so
a prefix without a trailing separator silently glues the level name
onto it (any `Path` prefix, since `str(Path)` drops the trailing
slash) — recorded in M8 (module doc), no code action.

### T3 — stdout is patched but never asserted (P1) — FIXED (D-063)
`setUp` patches `sys.stdout` globally, yet no test inspects the
captured output: `log_event`'s live print format (V12),
`show_event_log` and `show_history_of_moves` (V13) had no golden at
all. Now `TestDisplayGoldens` pins all three paths with exact
end-to-end goldens under a frozen clock (1ms per `now()` call); the
stdout patch is now load-bearing, not noise suppression.

### T4 — `move_to_last` untested (P1)
No test exercises `move_to_last` — happy path and empty-workers no-op
remain untested. The duplicate-name misdirection (V8c, R5) is no longer
reachable: D-061 rejects duplicates at construction, so the happy
path is the only live behaviour worth pinning.

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

**One whole area is still untested**: the edge semantics
(move_to_last happy path, bool/np.int64, StepMove field content —
T4/T7/T9), plus the thin CSV test (T5). The verbosity gate (D-057),
the display layer goldens (D-063), retry-after-failure (D-060),
duplicate names (D-061), and the context injection layer — the
module's main integration surface with domain workers — are all
pinned (D-062).

## Proposed priorities

- **P0** (with the R rulings): T1 — done (D-057); T2 — done (D-062);
  R2 — resolved (D-058); R5 — resolved (D-061).
- **P1**: T3 — done (D-063); T4 (move_to_last); T6 — done (D-060);
  R4 — resolved (D-060).
- **P2**: T5, T7, T8, T9 (T11 resolved with D-058; T10 resolved with
  D-061) + the M-sweep (dead imports, cosmetics, doc notes, repr;
  M12 closed with D-061).
