# test_logistic_model.md — analysis

Date: 2026-08-30. One test file: `test_logistic_model.py` (post
D-076, 1 class, 15 test methods — 14 active + 1 muted with a `_`
prefix per Roberto: D-076 restored `test_move_to_step_delegates_to_
state_machine`, the CONFIG level it targets now exists;
`_test_move_to_step_by_string` stays muted until POSITIONS), added
with the module (6bb45fb). **Analysis
session 21; the source modules' fix batch 1 (D-074) and the TEST
batch (D-075: T1/T2/T4/T5 fixed, T3 intentional report-only, T6
report-only) are applied.**

Suite: **14/0/0 GREEN, no PERF gates.** Fast (~0.05s).

## How to run

```
$ python -m unittest twolm.test.test_logistic_model
```

## Testbed design (setUp, L74-110)

- `setUpClass` (L70): `CUSTOM_TMP_BASE.mkdir(parents=True,
  exist_ok=True)` — the module-level `CUSTOM_TMP_BASE` (L62) is
  `Path(__file__).resolve().parents[3] / "build" / "tmp"` (the D-065
  idiom, T2/D-075, as in test_cache_manager).
- `sys.stdout` patched to a StringIO (keeps the SM display output
  out of the test log).
- A dummy `dummy_config.json` (`{}`) in
  `tempfile.TemporaryDirectory(dir=CUSTOM_TMP_BASE)` — under
  `<workspace-root>/build/tmp`, NOT the system temp (T2 FIXED).
  Created FIRST in setUp, so a mid-setup failure still leaves a
  `temp_dir` that tearDown (or the GC of the unentered
  TemporaryDirectory) cleans.
- `patch('twolm.logistic_model.lm_worker_config', return_value=
  Worker("CONFIG", ...))` + the same for `lm_worker_positions`:
  the factories are replaced in the MODULE namespace, so when the
  worker-list entries are uncommented the construction picks up the
  dummy workers. The patches are currently INERT (the list entries
  are commented — see T3).
- `LogisticModel(config_file_path=..., verbosity=STANDARD)` built
  once in setUp and shared by all tests (the tests are
  non-mutating: they only read facade state or construct fresh
  models; the one test that mutates the shared context —
  `test_injected_cache_helper_computes_the_worker_path`, which sets
  a dummy `cfg` — restores it via `addCleanup`).
- `tearDown` (L112): defensive against mid-setup failures — stops
  only the patchers that exist, then `temp_dir.cleanup()`.

## Coverage by area

### `TestLogisticModel` (13 active tests)

- `test_context_initialization`: `model.context` is an RLMContext;
  `config_file_path` round-trips (str compare); `base_dir_override`
  None; `cfg` None (V: context starts empty).
- `test_state_machine_initialization`: `current_step == 0`,
  `current_worker_name == "CREATED"` (the sentinel start).
- `test_invalid_config_path`: a non-existent config file →
  FileNotFoundError (the `_check_config_file_path` existence branch;
  also exercises the `str` input type).
- `test_base_dir_override_validation`: a non-existent override dir
  → FileNotFoundError (the existence branch).
- **T1 (D-075)** — `test_facade_methods_exist` (the overpromising
  try/except smoke test) REPLACED by:
  - `test_facade_delegates_to_state_machine`: per-method
    `patch.object(self.model.sm, ...)` pins — `show_event_log`,
    `show_history_of_moves`, `move_to_step` (int AND str name),
    `move_to_last`, `export_history_of_moves_as_csv` each land on
    the SM with the same arguments (`assert_called_once_with`).
  - `test_facade_views_and_verbosity_round_trip`: the read-only
    views (`current_step`, `current_worker_name`, `verbosity`)
    mirror `model.sm`, and the `verbosity` property round-trips
    (set HIGH → visible on the SM → restored to STANDARD).
- **T4 (D-075)** — the integration corners:
  - `test_injected_cache_helpers_are_the_machine_closures`: post-
    construction the context's `*_for_current_level` attributes are
    the SM-injected closures (`__name__` = `_get_cache_file_path` /
    `_get_cache_file_full_path`), `log_event` the bound SM method —
    a regression to the pre-D-074 names would have left the no-op
    lambda defaults (this pin would have caught R1).
  - `test_pre_injection_fallback_is_no_op_lambda`: a bare
    (un-injected) `RLMContext` keeps the lambda no-op defaults —
    the cache helpers return None, `log_event()` does nothing.
  - `test_injected_cache_helper_computes_the_worker_path`: with a
    dummy `cfg` (SimpleNamespace), the injected closures compute
    `cache/00_CREATED.dat` and `base/cache/00_CREATED.dat` (the
    pathlib join of D-069 M8 through the facade context).
  - `test_created_sentinel_workers_raise`: direct calls to
    `_created_up`/`_created_down` raise the pinned RuntimeErrors
    ("Executing/Cleaning created step should never happen." — the
    D-059 explicit sentinel).
  - `test_config_path_helper_edge_branches`: int → TypeError,
    missing → FileNotFoundError ("No such file: 'ghost.json'"),
    directory → IsADirectoryError (the M3/D-074 type).
  - `test_base_dir_helper_edge_branches`: int → TypeError, a file
    → NotADirectoryError.
  - `test_export_history_of_moves_as_csv_pass_through`: the CSV
    export writes a real header-only file (empty history) under the
    build/tmp artifact dir (D-065); header pinned to
    `step,worker_name,direction,start_utc,finish_utc,duration_sec`.
- **Muted (2, Roberto's plan — "una riga alla volta")**:
  - `_test_move_to_step_delegates_to_state_machine`: after
    `move_to_step(1)`, step 1, `config_up_mock` called ONCE with the
    context, `config_down_mock` not called.
  - `_test_move_to_step_by_string`: `move_to_step("POSITIONS")` →
    step 2, both up-mocks called once with the context (name-based
    move through 2 levels).
  - Precondition today (verified by probe): with only CREATED in
    the list, `move_to_step(1)` → IndexError (out of bounds) and
    `move_to_step("POSITIONS")` → ValueError (unknown worker) — the
    tests are correctly muted.

## Test defects (T1-T6)

Status: T1/T2/T4/T5 FIXED (D-075); T3 intentional (pipeline
development), T6 report-only — both unchanged by design.

### T1 — `test_facade_methods_exist` overpromises and underpins (P1) — FIXED (D-075)
The name and docstring ("Verify that facade methods correctly point
to the state machine") promised a delegation check; the body only
CALLED two of the seven facade methods (`show_event_log`,
`show_history_of_moves`) inside a `try/except` that converted any
exception to `self.fail` — a smoke test in disguise, and the
try/except+fail is an anti-pattern (letting the exception propagate
fails the test just as clearly, with a better traceback). Uncovered:
`move_to_step`, `move_to_last`, the `verbosity` property (get + set),
`export_history_of_moves_as_csv`. **Applied (D-075):** the method is
replaced by `test_facade_delegates_to_state_machine` (per-method
`patch.object(self.model.sm, ...)` + `assert_called_once_with` pins
for all five pass-throughs, `move_to_step` pinned with BOTH an int
and a name string) and `test_facade_views_and_verbosity_round_trip`
(the three read-only views mirror the SM; the verbosity property
round-trips and is restored).

### T2 — Artifacts in the SYSTEM temp dir (P1, D-065 house rule) — FIXED (D-075)
`tempfile.mkdtemp()` with no `dir=` created the dummy config under
the system temp (e.g. /tmp), not under `workspace_root/build/tmp`
— the same deviation Roberto fixed in test_cache_manager (T6,
D-072). Additionally, if setUp raised between `mkdtemp()` and the
end of setUp, `tearDown` was never run and the dir leaked. **Applied
(D-075):** the test_cache_manager idiom — module-level
`CUSTOM_TMP_BASE = Path(__file__).resolve().parents[3] / "build" /
"tmp"` (L62) + `setUpClass` mkdir (L70) +
`tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))` created
FIRST in setUp (a mid-setup failure still leaves a `temp_dir` that
tearDown or the GC cleans) + defensive tearDown (stops only the
patchers that exist, then `temp_dir.cleanup()`).

### T3 — Two muted tests (intentional — pipeline development)
`_test_move_to_step_delegates_to_state_machine` and
`_test_move_to_step_by_string` are muted by Roberto's design; they
come back when the corresponding worker entries are uncommented
("Restore the tests when the POSITION STEP is added", L114/L123).
Note: their factory patches are currently inert (nothing calls
`lm_worker_config()`/`lm_worker_positions()` in the source). Report-
only: do not touch until the pipeline grows.

### T4 — Integration corners untested (P2, breadth) — FIXED (D-075)
Nothing pinned: (a) the INJECTED callables — `log_event` default is
a no-op lambda pre-injection / a bound SM method post-injection,
and the two cache-helper names (a pin would have caught R1 — the
D-069 name divergence — immediately); (b) the sentinel callables
(`_created_up`/`_created_down` raise RuntimeError on direct call —
the D-059 "explicit sentinel" the state_machine resolution
anticipated); (c) the helper edge branches (int → TypeError,
directory-as-config → IsADirectoryError "not a file" post M3/D-074,
file-as-base_dir → NotADirectoryError); (d) the
`export_history_of_moves_as_csv` pass-through (with a build/tmp
artifact). **Applied (D-075):** 7 new tests — (a) the injected
closures' `__name__`s + `log_event` identity, the bare-context
no-op-lambda fallback, and the path computation through a dummy
`cfg` (`cache/00_CREATED.dat`, `base/cache/00_CREATED.dat`); (b)
both sentinels' pinned RuntimeError messages; (c) both helpers'
edge branches; (d) the CSV pass-through (header-only file, header
pinned, artifact under the build/tmp temp dir).

### T5 — Dead import (P2) — FIXED (D-075)
`Relevance` was imported but never used in the test file. **Applied
(D-075):** removed from the import (the top-level import now also
pulls the private helpers `_check_config_file_path`,
`_check_base_dir_override`, `_created_up`, `_created_down` for the
T4 corner pins).

### T6 — Header grammar (cosmetic, report-only)
L30: "How to use the unit tests logistic_model module." — the same
pattern as the test_board/test_feature/test_cache_manager header
nits; left as-is per the report-only pattern unless Roberto wants a
sweep.

## Observations

- **No PERF gates**: 5 tests in 0.009s; the shared-in-setUp model is
  cheap (1-worker machine) and safe because no test mutates
  `self.model`.
- **The stdout patch is load-bearing** for clean output but is also
  what hides any display-layer regression: a test could capture the
  StringIO and assert the table output — the state_machine display
  goldens (D-063) own that idiom and are not duplicated here.
- **The factory-patch design is forward-looking**: it will keep
  working verbatim as each worker entry is uncommented, because the
  patch targets the names in `twolm.logistic_model`'s own namespace.

## Completeness verdict

**Facade basics + integration corners pinned (post D-075)**:
context + SM initialization, both exception paths of the path
validators (plus the edge branches, T4), the sentinel start AND the
sentinel callables themselves (T4), the full delegation contract
per method (T1), the injected callables' identity + fallback +
path computation (T4 — would have caught R1), the CSV pass-through
(T4), and the D-065 artifact base (T2). The two muted tests already
pin the delegation semantics of `move_to_step` (int + name) and
will activate with the pipeline (T3, intentional). Remaining:
header grammar report-only (T6).

**Verdict**: 13/0/0 GREEN. Test campaign CLOSED (T1/T2/T4/T5
fixed, T3 intentional, T6 report-only); D-075.

## Appendix: class map (2026-08-30, file 294 lines, post D-075)

| Line | Class / item | Notes |
|---|---|---|
| 43-56 | imports | L48 SimpleNamespace (T4 dummy cfg) · L50 MagicMock/patch · L52-55 twolm (incl. the 4 private helpers for T4; Relevance removed — T5) |
| 62 | `CUSTOM_TMP_BASE` | build/tmp, D-065 idiom (T2) |
| 66 | `TestLogisticModel` | 15 methods (13 active + 2 muted) |
| 70 | `setUpClass` | mkdir CUSTOM_TMP_BASE (T2) |
| 74 | `setUp` | TemporaryDirectory FIRST (T2), stdout patch, dummy config under build/tmp, factory patches (inert — T3), shared model |
| 112 | `tearDown` | defensive patcher stops + temp_dir.cleanup() (T2) |
| 124 | `test_context_initialization` | active |
| 131 | `test_state_machine_initialization` | active |
| 137 | `_test_move_to_step_delegates_to_state_machine` | MUTED (T3) |
| 146 | `_test_move_to_step_by_string` | MUTED (T3) |
| 154 | `test_invalid_config_path` | active |
| 159 | `test_base_dir_override_validation` | active |
| 167 | `test_facade_delegates_to_state_machine` | active — T1 pin (replaces test_facade_methods_exist) |
| 191 | `test_facade_views_and_verbosity_round_trip` | active — T1 pin |
| 205 | `test_injected_cache_helpers_are_the_machine_closures` | active — T4 (would have caught R1) |
| 219 | `test_pre_injection_fallback_is_no_op_lambda` | active — T4 |
| 228 | `test_injected_cache_helper_computes_the_worker_path` | active — T4 (dummy cfg, addCleanup restore) |
| 242 | `test_created_sentinel_workers_raise` | active — T4 (D-059 sentinel) |
| 252 | `test_config_path_helper_edge_branches` | active — T4 |
| 267 | `test_base_dir_helper_edge_branches` | active — T4 |
| 278 | `test_export_history_of_moves_as_csv_pass_through` | active — T4 (header-only, build/tmp) |
| 293 | `unittest.main` guard | — |
