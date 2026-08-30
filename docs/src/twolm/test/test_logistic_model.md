# test_logistic_model.md — analysis

Date: 2026-08-30. One test file: `test_logistic_model.py` (156 lines,
1 class, 7 test methods — 5 active + 2 muted with a `_` prefix per
Roberto), added with the module (6bb45fb). **Analysis session 21;
the source modules' fix batch 1 is applied (D-074) — the TEST batch
(T1-T6) is still pending Roberto's calls. Test file untouched.**

Suite: **5/0/0 GREEN, no PERF gates.** Fast (~0.009s).

## How to run

```
$ python -m unittest twolm.test.test_logistic_model
```

## Testbed design (setUp, L58-89)

- `sys.stdout` patched to a StringIO (keeps the SM display output
  out of the test log).
- A dummy `dummy_config.json` (`{}`) in `tempfile.mkdtemp()` — the
  system temp dir, NOT build/tmp (T2).
- `patch('twolm.logistic_model.lm_worker_config', return_value=
  Worker("CONFIG", ...))` + the same for `lm_worker_positions`:
  the factories are replaced in the MODULE namespace, so when the
  worker-list entries are uncommented the construction picks up the
  dummy workers. The patches are currently INERT (the list entries
  are commented — see T3).
- `LogisticModel(config_file_path=..., verbosity=STANDARD)` built
  once in setUp and shared by all tests (the tests are
  non-mutating: they only read facade state or construct fresh
  models).

## Coverage by area

### `TestLogisticModel` (5 active tests)

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
- `test_facade_methods_exist`: see T1 — the name overpromises.
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

Status: all OPEN (fix campaign pending Roberto's calls). T3 is
intentional (pipeline development), T6 report-only.

### T1 — `test_facade_methods_exist` overpromises and underpins (P1)
The name and docstring ("Verify that facade methods correctly point
to the state machine") promise a delegation check; the body only
CALLS two of the seven facade methods (`show_event_log`,
`show_history_of_moves`) inside a `try/except` that converts any
exception to `self.fail` — a smoke test in disguise, and the
try/except+fail is an anti-pattern (letting the exception propagate
fails the test just as clearly, with a better traceback). Uncovered:
`move_to_step`, `move_to_last`, the `verbosity` property (get + set),
`export_history_of_moves_as_csv`. Proposed fix: patch the SM's
methods on `self.model.sm` (or assert on `model.sm` state) and pin
the actual delegation per method — e.g. `assertAnyCall`-style checks
that each facade call lands on the SM with the same arguments, plus
the verbosity round-trip and the current_step/current_worker_name
views.

### T2 — Artifacts in the SYSTEM temp dir (P1, D-065 house rule)
`tempfile.mkdtemp()` (L65) with no `dir=` creates the dummy config
under the system temp (e.g. /tmp), not under
`workspace_root/build/tmp` — the same deviation Roberto fixed in
test_cache_manager (T6, D-072). Additionally, if setUp raises
between `mkdtemp()` and the end of setUp, `tearDown` is never run
and the dir leaks. Proposed fix: `tempfile.mkdtemp(dir=Path(
__file__).resolve().parents[3] / "build" / "tmp")` (the
test_cache_manager idiom) + wrap the setUp body so a mid-setup
failure still removes the created dir.

### T3 — Two muted tests (intentional — pipeline development)
`_test_move_to_step_delegates_to_state_machine` and
`_test_move_to_step_by_string` are muted by Roberto's design; they
come back when the corresponding worker entries are uncommented
("Restore the tests when the POSITION STEP is added", L114/L123).
Note: their factory patches are currently inert (nothing calls
`lm_worker_config()`/`lm_worker_positions()` in the source). Report-
only: do not touch until the pipeline grows.

### T4 — Integration corners untested (P2, breadth)
Nothing pins: (a) the INJECTED callables — `log_event` default is a
no-op lambda pre-injection / a bound SM method post-injection, and
the two cache-helper names (a pin would have caught R1 — the D-069
name divergence — immediately); (b) the sentinel callables
(`_created_up`/`_created_down` raise RuntimeError on direct call —
the D-059 "explicit sentinel" the state_machine resolution
anticipated); (c) the helper edge branches (int → TypeError,
directory-as-config → FileNotFoundError "not a file", file-as-
base_dir → NotADirectoryError); (d) the `export_history_of_moves_
as_csv` pass-through (with a build/tmp artifact).

### T5 — Dead import (P2)
`Relevance` (L51) is imported but never used in the test file.

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
  what hides any display-layer regression: `test_facade_methods_
  exist` (T1) could capture the StringIO and assert the table
  output — the state_machine display goldens (D-063) show the idiom.
- **The factory-patch design is forward-looking**: it will keep
  working verbatim as each worker entry is uncommented, because the
  patch targets the names in `twolm.logistic_model`'s own namespace.

## Completeness verdict

**Facade basics pinned, integration corners open (post analysis,
session 21)**: context + SM initialization, both exception paths of
the path validators, and the sentinel start are covered; the two
muted tests already pin the delegation semantics of `move_to_step`
(int + name) and will activate with the pipeline. Open: the
delegation pin itself (T1), the D-065 artifact base (T2), the
injected-callables + sentinel + edge branches (T4), the dead import
(T5), header grammar report-only (T6).

**Verdict**: 5/0/0 GREEN. Fix campaign pending Roberto's calls.

## Appendix: class map (2026-08-30, file 156 lines)

| Line | Class / item | Notes |
|---|---|---|
| 43-51 | imports | L47 MagicMock/patch · L48 StringIO · L50-51 twolm (Relevance dead — T5) |
| 55 | `TestLogisticModel` | 7 methods (5 active + 2 muted) |
| 58 | `setUp` | stdout patch, dummy config (system temp — T2), factory patches (inert — T3), shared model |
| 91 | `tearDown` | stop patchers, remove config + rmdir |
| 102 | `test_context_initialization` | active |
| 109 | `test_state_machine_initialization` | active |
| 114 | `_test_move_to_step_delegates_to_state_machine` | MUTED (T3) |
| 123 | `_test_move_to_step_by_string` | MUTED (T3) |
| 132 | `test_invalid_config_path` | active |
| 137 | `test_base_dir_override_validation` | active |
| 145 | `test_facade_methods_exist` | active — overpromises (T1) |
| 155 | `unittest.main` guard | — |
