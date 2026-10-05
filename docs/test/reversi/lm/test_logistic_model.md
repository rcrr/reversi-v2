# test/reversi/lm/test_logistic_model.py
The logistic-model unit suite — 2 classes / 31 tests, no PERF gates, ~1.1 s, no DB.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestLogisticModel` | 27 | the context init (LMContext, `config_file_path` round-trip, `base_dir_override` None, `cfg` None); the SM sentinel start (`current_step == 0`, "CREATED"); the init `ValidationError` on a non-str config path; the injected cache closure requiring `cfg` (AttributeError before CONFIG); the `move_to_step` delegation (int → step 1 / CONFIG; str 'POSITIONS' → step 4, crossing the dummy CONFIG + FEATURES + SU_ANALYSIS); the invalid config path + base_dir override `FileNotFoundError`s; the facade pass-through pins (`test_facade_delegates_to_state_machine` — per-method `patch.object(self.model.sm, ...)` + `assert_called_once_with`); the views + verbosity round-trip; the injected cache helpers ARE the machine closures (would have caught R1); the pre-injection no-op lambda fallback; the injected helper computing the worker path (dummy `cfg`, `addCleanup` restore); the CREATED sentinel workers raise; the config/base_dir helper edge branches (bad type, missing path, a directory / a file); the CSV export pass-through (header-only artifact, under `build/tmp`); the `run()` driver — the explicit target (CONFIG first, then the levels up to it, the machine history pinned), the config `target_level` honored, the `"last"` resolution (the field default / the case / a blank value / an absent field / no cfg → `move_to_last`), the argument-over-field precedence, the RESUME (a deeper target does not re-run the levels done, the same target is a no-op), a backward target running the down() steps, the unknown-name ValueError and the wrong-type TypeError, the base `BaseModel.run` generic default (a 2-worker pipeline + the `None` hook), the base last/blank-string resolution (the bare `BaseModel` over "last" / "LAST" / a blank / "" → `move_to_last`), and the `build_model` script entry (the facade built on the config + `move_to_last`, the `LogisticModel` patched in the module namespace) |
| `TestRunFacadeOnARealConfig` | 3 | `run()` on the REAL pipeline (no factory mocks, the rlm_00 fixture with `target_level` set by a config copy under `build/tmp`): the field drives the stop (FEATURES, step 2, `su_analysis_tables` still None), the explicit argument beats the field (SU_ANALYSIS, step 3, the corpus tables published), and the resume (a second `run()` is a no-op, the published tables are the SAME object, the machine history is the 3 up moves) |

## Goldens pinned

- The pass-through `assert_called_once_with` contracts (per-method).
- The closure identity pins (injected helpers == the machine closures; pre-injection == the no-op lambda default).
- The exception types/messages at the facade boundary: the init ValidationError, the helper FileNotFoundErrors, the
  sentinel raises, the `run()` unknown-name ValueError (`Worker 'NOPE' not found in the pipeline.`) and the wrong-type
  TypeError (the gate's message).
- The cache-path computation for the dummy `cfg` (the worker-path pin).
- The `run()` machine history: the sequence of (step, worker, direction) triples for a target move and for the resume.
- The real-config resolutions: `target_level` "FEATURES" → step 2; the argument "SU_ANALYSIS" → step 3 with the tables
  published; the same-target second call leaving the tables object identical.

## Conventions

- The `build/tmp` artifact rule: CSV export artifacts land under `build/tmp`.
- The 2 probe-derived tests pin the full guard contract.
- The testbed (the setUp contract): `setUpClass` — `CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)`, imported from
  the shared `test.reversi.paths` module.
- `sys.stdout` patched to a StringIO (keeps the SM display out of the test log); the dummy `dummy_config.json` (`{}`) in
  a `tempfile.TemporaryDirectory(dir=CUSTOM_TMP_BASE)` created FIRST in setUp (mid-setup failures still leave a
  cleanable `temp_dir`).
- `patch('reversi.lm.logistic_model.wrk_config', ...)` + the same for `wrk_positions`, `wrk_features`, `wrk_su_analysis`
  and `wrk_anova`: the five factories are replaced in the MODULE namespace, so the worker-list entries pick up the
  dummy workers; the `build_model` test patches `LogisticModel` the same way.
- One shared `LogisticModel` built in setUp (the tests are non-mutating; the one mutating test restores via
  `addCleanup`); `tearDown` is defensive against mid-setup failures.
- `TestRunFacadeOnARealConfig` runs the REAL workers (no factory patches) and stops at FEATURES / SU_ANALYSIS — the
  levels that need no database; its config copies follow the D-255 idiom (a copy in the temp dir, so the embedded config
  provenance stays coherent) and the artifacts land in the test's temp dir.

## Integration

- Module under test: `logistic_model.md` (the first concrete domain facade — LogisticModel + the LMContext dataclass) on
  `base_model.md` (the BaseModel facade base, which owns `run()` + the `_configured_target_level` hook).
- `test_state_machine.md` covers the SM core; this suite covers the facade boundary + the LMContext shape + the
  injection layer + the target-driven stop.
