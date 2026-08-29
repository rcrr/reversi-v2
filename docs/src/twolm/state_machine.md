# state_machine.py — analysis

Date: 2026-08-29. Module added by Roberto (2 files: state_machine.py +
test_state_machine.py), commit 66ab84b. **Analysis session 19; R1
fixed + T1 pinned (D-057); R2 fixed (D-058: frozen `LogEntry`
dataclass); R3 resolved as sentinel (D-059: documented + pinned);
R4 resolved (D-060: failure semantics documented + pinned); R5
resolved (D-061: unique worker names enforced in `__init__`).
**All five R items closed; all T items closed; M-sweep COMPLETE:
M1, M4, M7, M10 (D-068) + M3, M5, M8, M11 (D-069) + M6, M9
(D-070) fixed — M6 print cleanup with the 3 display goldens
rewritten, M9 left as-is (Roberto: the injection is load-bearing),
future redesign parked at I-010 (M2, M12 done).**

Suite: **49 tests, GREEN 49/0/0** (5 classes, no PERF gates). Suite is
fast (~0.23s).

Full workspace: **447 tests, GREEN, 52 skipped under
`SKIP_REGAB_DB=1`** (17 PERF print-only + 35 regab DB-gated).

Dependencies: pydantic (`@validate_call`, house convention —
D-069) plus stdlib (enum, datetime, dataclasses, contextlib,
typing, pathlib, csv). pydantic ≥ 2 was already declared in
pyproject.toml for the other modules: no new dependency.

## Architecture

`state_machine` is a generic, domain-agnostic pipeline orchestrator.
A `StateMachine` drives an ordered list of `Worker` steps over a shared
`Context`, with logging, per-step timing history, and CSV export of the
history. It knows nothing about Reversi: the domain module (e.g. an
`RLMContext` + domain workers, per the `Context` docstring) is meant to
subclass/instantiate it.

### Components

| Component | Role |
|---|---|
| `Verbosity(IntEnum)` HIGH=0 … NONE=4 | Minimum-relevance gate for `log_event` printing. |
| `Relevance(IntEnum)` TRACE=0 … ERROR=4 | Relevance level of a log event. |
| `Context` | Empty base class for pipeline contexts; shared state passed between workers. |
| `Worker(name, up_callable, down_callable)` | One pipeline step; composition over the forward (`up`) and rollback (`down`) callables; `__repr__` shows the name (D-068); `__init__`/`up`/`down` are `@validate_call` (D-069). |
| `StateMachine.StepMove` (dataclass) | One executed step: step, worker_name, direction, start, finish, duration. |
| `StateMachine.LogEntry` | Frozen dataclass: typed record for one logged event (time, step, worker_name, relevance, message); `asdict()` gives the dict form for file/DB dumps (D-058). |
| `StateMachine.__init__` | Stores workers/context/verbosity; injects `log_event` + two cache-path helpers onto the context; emits the init DEBUG log; `@validate_call` (D-069): non-Worker list entries / non-Context raise `ValidationError`. |
| `StateMachine._history_timer` | Context manager appending a `StepMove` in `finally` (failure included). |
| `StateMachine._run_step` | Logs "Starting …", dispatches `up`/`down` (explicit: any other direction string raises `ValueError`, D-068), logs "Completed …"; on exception logs ERROR and re-raises. |
| `StateMachine.log_event` | Always appends to `self.logs`; prints iff `relevance >= verbosity`; `@validate_call` (D-069). |
| `show_event_log` / `show_history_of_moves` | Terminal pretty-printers of logs / history. |
| `export_history_of_moves_as_csv` | Writes the history as CSV (ISO-8601 UTC timestamps, float durations); creates missing parent dirs (D-068); `@validate_call` (D-069). |
| `move_to_step(int \| str)` | The public move API: a Python int index (case-insensitive worker name accepted too); bool is NOT valid (M3, D-069); the strict `@validate_call` gate in `_move_to_step_validated` re-raises `ValidationError` as the pinned `TypeError` (M11, D-069); walks half-open intervals; sets `current_step` **before** each step executes. |
| `move_to_last` | `move_to_step(workers[-1].name)` — name-based, see R5. |

### State model (verified — the load-bearing semantics)

`current_step` is the index of the last **executed** step, with step 0
as the initial (nothing-executed) state. For a move from `c` to `t`:

- **Up** (`t > c`): executes `up()` of workers `c+1 … t` — the target's
  `up()` **runs**.
- **Down** (`t < c`): executes `down()` of workers `c … t+1` — the
  target's `down()` does **NOT** run; `current_step` is then set to `t`
  explicitly (L313, required because the down loop's last iteration
  leaves it at `t+1`).

Consequences, all verified (V3–V6, V8):

1. **Worker 0 is unreachable — intentional sentinel** (R3, D-059):
   no public call ever invokes `workers[0].up()` or `.down()`; by
   domain design the first worker is a sentinel (the RLM pipeline's
   'CREATED' bootstrap runs outside the machine; the logistic_model
   module will make the full role explicit when ported — Roberto,
   session 19). Pinned by
   `test_worker_zero_is_sentinel_never_executed`.
2. **Failure leaves `current_step` at the failed step** `k`; a retry
   of the same target re-runs only steps `> k`, skipping `k` —
   documented and pinned (R4, D-060). Recovery: `move_to_step(k-1)`
   runs `k`'s `down()` (the domain rollback), then move up to
   re-execute `k`; handling the failure is the domain worker's
   responsibility (the machine re-raises and is domain-agnostic).
3. The down-to-target state is "target step intact, everything above it
   rolled back" — consistent with state(t) = "steps 1..t done".

### Context injection (side effect on the caller's object)

`__init__` unconditionally assigns onto the passed `Context` (L154,
L168, L176):

- `context.log_event = self.log_event` (bound method of this machine);
- `context.get_cache_file_path_for_current_level` (renamed from
  `..._for_next_level`, M5, D-069) —
  `Path(cfg.cache_files_prefix) / f"{level:02}_{name}.dat"`
  (pathlib join, M8, D-069) with `level = current_step`, i.e. the
  **currently executing** worker;
- `context.get_cache_file_full_path_for_current_level` —
  `cfg.base_dir / <that path>`.

Both cache helpers require `context.cfg` with `cache_files_prefix` and
`base_dir` (bare `getattr`, no default → raw `AttributeError` if
missing; docstring says a ConfigWorker must populate it first).

## Verified facts (V1–V17)

All verified by independent ground-truth probes against the live module
(54-check probe script, 51 direct PASS + 3 re-analysed, zero
mismatches vs. expectations once the three probe typos were corrected);
every claim below was also cross-checked against the source lines
cited.

| # | Fact | Method |
|---|---|---|
| V1 | Verbosity gate is `relevance >= verbosity` (L225); current table (post D-057): HIGH all, MODERATE DEBUG..ERROR, STANDARD INFO..ERROR, LOW WARN+ERROR, VERY_LOW ERROR-only, NONE silent — re-verified 2026-08-29 (at analysis time NONE(4) printed ERROR: the R1 defect) | 6×5 print-matrix probe on captured stdout, re-run post-fix |
| V2 | `logs` accumulates every event regardless of verbosity (gate affects print only); entries are frozen `LogEntry` dataclass instances — attribute access, immutable, `asdict()` for dumps (post D-058; at analysis time they were plain dicts and `LogEntry` a dead class: the R2 defect) | Probe + source scan |
| V3 | Worker 0's `up()`/`down()` are never invoked by `move_to_step`/`move_to_last` (up 0→2 runs up[1], up[2]; down 2→0 runs down[2], down[1]) — now documented as intentional sentinel (D-059) and pinned by a dedicated test | MagicMock call tracking |
| V4 | Down c→t runs down() of workers c..t+1 (target excluded); final `current_step == t`; the L313 reassignment is **required** (last loop iteration leaves it at t+1) | MagicMock + state inspection |
| V5 | Up c→t runs up() of workers c+1..t (target included) | MagicMock |
| V6 | Failure at step k leaves `current_step == k`; retry of the same target executes only steps > k — the failed worker is **skipped** (documented + pinned, D-060) | side_effect + reset mocks |
| V7 | `move_to_step(True)` now REJECTED — bool is not a valid step (M3, D-069 strict gate; at analysis time it was accepted as step 1); `np.int64(1)` rejected with TypeError; the public TypeError contract is unchanged (D-069 wrapper) | Edge-case probes |
| V8 | Name lookup case-insensitive; duplicate names are **rejected at construction** since D-061 (ValueError, case-insensitive check) — name-based moves, including `move_to_last`, are unambiguous (at analysis time duplicates were first-match-wins and `move_to_last` on `[A, B, A]` landed on step 0: the R5 defect) | Edge-case probes, re-run post-fix |
| V9 | Cache path at step k = `{prefix}{k:02}_{name}.dat` (active worker); full path = `base_dir / path`; relative prefix joins under `base_dir`, **absolute prefix silently drops `base_dir`** (pathlib `/`); missing `cfg` → `AttributeError`; empty workers → `Path()`, name `"UNDEFINED"`, `move_to_last` no-op | Probes with cfg stubs |
| V10 | CSV header `step,worker_name,direction,start_utc,finish_utc,duration_sec`; ISO-8601 with `+00:00`; float `duration_sec` | File round-trip |
| V11 | Failed step logs exactly [init, "Starting…", "Error in…"] — no "Completed"; error entry carries the failed step + worker | Log inspection |
| V12 | Live print: `[{ts} UTC] [{step:02}][{name:15}] [{rel.name}:{verb.name}] {msg}` — enum names + explicit UTC marker (the pre-cleanup numeric-enum / no-UTC format was re-formatted by D-070/M6) | Regex on captured line |
| V13 | `show_event_log`: "EVENT LOG" banner + `TIMESTAMP (UTC) | STEP (2-digit) | WORKER | RELEVANCE (name) | MESSAGE` (66-underscore rule); `show_history_of_moves`: `Step | Worker | Dir | Start (UTC) | Dur (s)` (microsecond start, 6-decimal duration, Dur header right-aligned) — both re-formatted by D-070/M6 | Captured output |
| V14 | `StepMove.start`/`.finish` tz-aware UTC; `duration == finish - start`; history entry appended in `finally` even on failure | Probe + existing test |
| V15 | Dead import: `Any` (state_machine.py L34 — removed by D-068); the test file's `datetime` import is now used by `TestLogEntry` (D-058, was dead at analysis time) | Source scan |
| V16 | Invalid target: IndexError (≥len or negative), ValueError (unknown name), TypeError (other types incl. float) | Edge-case probes |
| V17 | A context shared by two machines: the second `__init__` **re-binds** `log_event` + both cache helpers to itself (unconditional assignment) | `__self__` inspection |

## Defects (OPEN — awaiting Roberto's ruling)

### R1 — `Verbosity.NONE` is not silent (prints ERROR) — RESOLVED (D-057, 2026-08-29)
The label "NONE" implied zero output, but the gate is
`relevance >= verbosity` (L201), so at NONE(4) the ERROR(4) events
still printed (verified V1, and observed live during the probes:
ERROR lines emitted at NONE). Fixed per Roberto's ruling (he has
client-code visibility, the agent does not): **keep the `>=` gate and
the values 0–3 unchanged**, add `VERY_LOW = 4` (takes over the old
NONE behaviour: ERROR-only), and move `NONE` to `5` (truly silent).
HIGH..LOW behaviour is byte-identical; the only behavioural delta is
for call sites passing `Verbosity.NONE` explicitly (ERROR-only →
silent — such a site that wants errors visible should use
`VERY_LOW`; accepted given Roberto's client visibility). Pinned by
`TestVerbosityGating` (6×5 gating matrix + enum values, T1).

### R2 — `LogEntry` is dead code and the `logs` annotation lies — RESOLVED (D-058, 2026-08-29)
`class LogEntry(dict)` with class-level annotations was pure
documentation: nothing enforced keys or types, and `log_event` built
**plain dicts** — the declared `List[StateMachine.LogEntry]` (L137)
was never true (V2 at analysis time). Fixed per Roberto's ruling —
option (c), a real typed record, chosen because no client reads the
log today and the three intended consumers (inspection clients,
interactive REPL search, a final pipeline worker dumping the log to
file/DB) all benefit from it. Implemented as
`@dataclass(frozen=True)` `LogEntry` (L118-128):
- **frozen**: a log record is created once and read forever;
  mutation raises `FrozenInstanceError`;
- **attribute access** (`entry.message`): REPL-ergonomic (use #2);
  dataclass `__repr__` gives a self-documenting record in the REPL;
- **`dataclasses.asdict(entry)`**: one-liner dict form for the
  file/DB dump worker (use #3);
- `log_event` now constructs `LogEntry` directly (L217-223);
  `show_event_log` migrated to attribute access (output format
  unchanged); the `logs` annotation is now true.
Observable behaviour (prints, CSV, history) unchanged. Pinned by
`TestLogEntry` (3 tests: typed record + field values, immutability,
`asdict` 5-key form). Side effect: the test file's previously dead
`datetime` import is now used (T11/M2 resolved).

### R3 — Worker 0 can never execute (semantic) — RESOLVED as SENTINEL (D-059, 2026-08-29)
No public call invokes `workers[0].up()` or `.down()` (V3). Roberto
confirmed the sentinel reading: **by domain design the first worker
is a sentinel** — the RLM pipeline's 'CREATED' bootstrap runs outside
the machine, and the logistic_model module (to be ported next) will
make the full role explicit. No behaviour change: the state model is
self-consistent with step 0 as the "nothing executed yet" state.
Disposition: documented in the `StateMachine` class docstring (state
model + sentinel, L95-107) and the `move_to_step` docstring (up
includes target / down excludes target, L261-279), and pinned by
`test_worker_zero_is_sentinel_never_executed` (new test — up to 2 and
back to 0 never touches `up[0]`/`down[0]`).

### R4 — Post-failure retry silently skips the failed step — RESOLVED (D-060, 2026-08-29)
After a failure at step `k`, `current_step == k` (the failed step, not
`k-1` the last successful one — V6, and pinned by
`test_worker_exception_propagation_and_logging`). A subsequent
`move_to_step(t)` with `t > k` executes only steps `> k`, so the
failed worker never re-runs on a same-target retry.
Resolved per Roberto's ruling — option (a), **keep + document +
pin**, no behaviour change: the machine is domain-agnostic and
cannot know whether a failed action is re-runnable or whether
partial output is safe; the method re-raises, so it is the domain
worker's responsibility to catch and handle the exception. The
documented recovery path: `move_to_step(k-1)` (invokes `k`'s
`down()` — the domain rollback, e.g. clearing a partial cache file)
and then move up to re-execute `k`. Disposition: failure semantics
added to the `move_to_step` docstring (L261-279); pinned by
`test_retry_after_failure_skips_failed_step` (retry skips `k`;
down-then-up re-executes it, T6).

### R5 — `move_to_last` is name-based and misdirects on duplicate names
**RESOLVED (D-061)**
`move_to_last` calls `move_to_step(workers[-1].name)` (L315-321); name
resolution picks the **first** match (V8). With workers `[A, B, A]`,
`move_to_last` from step 2 landed on step 0. Roberto **rejected** the
minimal index fix: the real ambiguity sits in `move_to_step` itself
(name-based dispatch would keep picking the first match for **any**
duplicate pair), and the case did not occur in his code — so the fix
enforces the invariant instead: `__init__` now **rejects duplicate
worker names, case-insensitively** (L134-145, `ValueError`), fail-fast
before any state is touched, because name resolution is
case-insensitive. With unique names, `move_to_last`'s name-based
dispatch is unambiguous and stays unchanged. M12 closed (duplicates
impossible at construction); V8 restated. Pinned by
`test_duplicate_worker_names_raise` and
`test_duplicate_worker_names_case_insensitive` (22 tests).

## Minor notes (M1–M12)

- **M1** — Dead import `Any` (L34) — RESOLVED (D-068): removed.
- **M2** — Dead import `datetime` in test_state_machine.py —
  RESOLVED as a side effect of D-058 (now used by `TestLogEntry`).
- **M3** — `move_to_step` accepted `bool` (True→1, False→0 no-op)
  — RESOLVED (D-069, Roberto: bool is NOT a valid step): bool is
  now rejected like any other non-int/non-str type (TypeError, same
  message) by the strict gate in `_move_to_step_validated`; pinned
  by `test_bool_rejected_as_int_step` (rewritten from
  `test_bool_accepted_as_int_step`, D-066).
- **M4** — `_run_step`'s `else` branch treated any non-`'up'`
  direction string as down (L199-202) — RESOLVED (D-068): the
  dispatch is now explicit (`elif direction == 'down'`, anything
  else raises `ValueError`); no behaviour change for valid input.
  Pinned by `test_run_step_rejects_unknown_direction`.
- **M5** — Injected names `..._for_next_level` contradicted their
  own docstrings ("currently executing worker") — RESOLVED (D-069,
  Roberto's call): renamed to
  `get_cache_file_path_for_current_level` /
  `get_cache_file_full_path_for_current_level`. Known follow-up
  (Roberto): two call sites in the domain modules
  `lm_worker_config` and `logistic_model` must use the new names
  when those modules are ported.
- **M6** — Cosmetic print drift: `show_event_log` padded step to 4
  digits vs 2 in the live log line; `show_history_of_moves` header
  `Dur (s)` left-14 vs values right-15.6f; no UTC marker on the
  displayed timestamp; `[rel:verb]` printed numeric enum values,
  not names — RESOLVED (D-070, Roberto: "M6: 1, pulisci"): the
  live line now prints enum names (`[DEBUG:HIGH]`) + an explicit
  `UTC` marker; the event-log table has a `TIMESTAMP (UTC)`
  header, 2-digit step (consistent with the live line), a
  `RELEVANCE` name column and a 66-underscore rule; the history
  table's `Dur (s)` header is right-aligned over its values. The
  3 frozen-clock display goldens were rewritten to the cleaned
  format (TestDisplayGoldens).
- **M7** — No `__repr__` on `Worker`/`StateMachine` (house
  hygiene) — RESOLVED (D-068): `Worker.__repr__` →
  `Worker('NAME')`; `StateMachine.__repr__` →
  `StateMachine(workers=N, current_step=K, verbosity=LEVEL)` —
  deliberately lightweight (context, logs and history can hold
  large domain data and are excluded). Pinned by
  `test_worker_repr` + `test_state_machine_repr_tracks_state`.
  `LogEntry` has the dataclass `__repr__` (D-058).
- **M8** — Cache-helper contract — RESOLVED (D-069, hardening):
  the prefix is now joined with pathlib
  (`Path(prefix) / f"{level:02}_{name}.dat"`) instead of
  f-string-concatenated, so a prefix without a trailing separator
  (a str without '/', or ANY `Path`) can no longer silently glue
  the level name onto it (`'cache'` → `cache/01_CONFIG.dat`, not
  `cache01_CONFIG.dat`); pinned by
  `test_path_cache_prefix_joins_without_gluing`. Remaining
  contract (documented, V9): `context.cfg` must carry
  `cache_files_prefix` + `base_dir` (bare `getattr`, no default);
  an absolute `cache_files_prefix` still silently drops `base_dir`
  (pathlib `/`); empty workers → `Path()`.
- **M9** — `__init__` mutates the caller's context (injection is a
  side effect); a shared context re-binds to the **last** machine
  built on it (V17) — RESOLVED as leave-as-is (D-070, Roberto:
  the injection is fundamental, the domain workers depend on it).
  A future redesign (explicit machine reference / context-owned
  helpers) is parked in ideas.md as I-010, to be evaluated once
  all the domain modules are in the workspace and their call
  patterns are visible.
- **M10** — `export_history_of_moves_as_csv`: no parent-dir
  creation (a path with missing dirs → `FileNotFoundError`) —
  RESOLVED (D-068): `path.parent.mkdir(parents=True, exist_ok=True)`
  before the `open` (a bare filename has parent `.`, where the mkdir
  is a no-op). Pinned by
  `test_csv_export_creates_missing_parent_dirs` (artifact under
  build/tmp, D-065 house rule).
- **M11** — No `@validate_call` on any public function — RESOLVED
  (D-069, Roberto: "aggiungiamo il check @validate_call"):
  `@validate_call(config=ConfigDict(arbitrary_types_allowed=True))`
  on `Worker.__init__`/`up`/`down`, `StateMachine.__init__`
  (non-Worker entries / non-Context → `ValidationError`),
  `log_event`, `export_history_of_moves_as_csv`, and on
  `move_to_step` — as a strict gate in the private
  `_move_to_step_validated`, whose `ValidationError` is re-raised as
  the pinned public `TypeError` (contract unchanged). The module now
  imports pydantic (already a workspace dependency); pinned by
  `test_constructor_rejects_non_worker_entry` +
  `test_constructor_rejects_non_context`.
- **M12** — Duplicate worker names are allowed; name-based moves are
  first-match and silent — RESOLVED by D-061: `__init__` rejects
  duplicates (case-insensitive, `ValueError`); first-match unreachable.

## Observations (not defects)

- **Half-open interval semantics are correct as implemented**: the
  L313 reassignment is *required* for down moves (the down range
  excludes the target), and the up loop naturally ends at the target.
  The code and the L311 comment are consistent — verified, no change.
- **`np.int64` rejection is acceptable** for a plain-int pipeline API
  (other modules' scalar/array duality doesn't apply here); the
  TypeError message is clear.
- **Aware UTC datetimes** throughout (`datetime.now(timezone.utc)`),
  ISO-8601 with explicit `+00:00` in CSV — good hygiene.
- **Empty-workers degenerate state degrades gracefully**: `"UNDEFINED"`
  worker name, `Path()` cache path, `move_to_last` no-op, any
  `move_to_step` → IndexError.
- **History records failed attempts** (finally-based timer) — a
  deliberate, test-pinned choice.

## Suite status

```
$ python -m unittest twolm.test.test_state_machine
.............
--------------------------------------------------------------
Ran 13 tests in 0.026s
OK
```

## Appendix: line-number reference (2026-08-29, post M-sweep
D-068 + D-069 + D-070; all line numbers grep-verified 2026-08-29,
file 378 lines)

- `__all__`: L41
- `Verbosity`: L45 (VERY_LOW: L54, NONE: L55) · `Relevance`: L57 ·
  `Context`: L67
- `Worker.__init__`: L82 (D-069 decorator: L81) · `up`: L88 (L87) ·
  `down`: L93 (L92) · `__repr__`: L97 (D-068)
- `StateMachine` class docstring (state model + sentinel): L102-114
- `StateMachine.StepMove`: L116-123 (@dataclass L116, class L117) ·
  `StateMachine.LogEntry`: L125-135 (@dataclass(frozen=True) L125,
  class L126, fields L131-135)
- `StateMachine.__init__`: L138 (D-069 decorator: L137,
  `arbitrary_types_allowed`; verbosity param: L141; duplicate-name
  check: L142-153, D-061)
- context.log_event injection: L162
- `_get_cache_file_path`: L164 (level = current_step: L169; cfg
  prefix: L172; pathlib join: L177, D-069)
- `get_cache_file_path_for_current_level` injection: L179 (D-069
  rename)
- `_get_cache_file_full_path`: L181 (base_dir join: L184-185);
  injection: L187 (D-069 rename)
- init log: L189
- `StateMachine.__repr__`: L191-197 (D-068)
- `_history_timer` (finally append): L200-214
- `_run_step`: L215 (direction dispatch: L218-225, explicit up/down
  + ValueError, D-068; error log+raise: L227-229)
- `current_worker_name`: L232 ("UNDEFINED": L234)
- `log_event`: L238 (D-069 decorator: L237; LogEntry construction:
  L241-247; append: L248; gate `>=`: L249; print: L253-255, enum
  names + UTC marker, D-070)
- `show_event_log`: L257 (D-070 table: L258-270 — UTC header,
  2-digit step, RELEVANCE name column, 66-underscore rule)
- `show_history_of_moves`: L272 (D-070 right-aligned Dur header:
  L275-276; 80-dash rule: L277; row print: L281)
- `export_history_of_moves_as_csv`: L284 (D-069 decorator: L283;
  parent-dir mkdir: L289, D-068; fieldnames: L290)
- `move_to_step`: L304 (docstring: L305-324, incl. failure
  semantics + bool NOT valid; wrapper try: L325-326; except
  ValidationError: L327; TypeError re-raise: L331-333, D-069)
- `_move_to_step_validated`: L337 (strict D-069 decorator:
  L335-336; string→upper: L341; name lookup: L342; ValueError
  not-found: L344; IndexError: L347-348; same-step no-op: L350-351;
  up range: L353-355; down range: L356-358; pre-exec step update:
  L363; down final set: L369-370)
- `move_to_last`: L372 (name-based call: L378)
