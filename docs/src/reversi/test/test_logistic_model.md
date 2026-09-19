# reversi/test/test_logistic_model.py
The logistic-model unit suite — 1 class / 17 tests, no PERF gates, ~0.15 s, no DB. 311 lines.

## Coverage

| class (line) | tests | what it pins |
|---|---|---|
| `TestLogisticModel` (L62) | 17 | the context init (LMContext, `config_file_path` round-trip, `base_dir_override` None, `cfg` None); the SM sentinel start (`current_step == 0`, "CREATED"); the init `ValidationError` on a non-str config path; the injected cache closure requiring `cfg` (AttributeError before CONFIG); the `move_to_step` delegation (int → step 1 / CONFIG; str 'POSITIONS' → step 3, crossing the dummy CONFIG + FEATURES); the invalid config path + base_dir override `FileNotFoundError`s; the facade pass-through pins (`test_facade_delegates_to_state_machine` — per-method `patch.object(self.model.sm, ...)` + `assert_called_once_with`); the views + verbosity round-trip; the injected cache helpers ARE the machine closures (would have caught R1); the pre-injection no-op lambda fallback; the injected helper computing the worker path (dummy `cfg`, `addCleanup` restore); the CREATED sentinel workers raise; the config/base_dir helper edge branches (str-vs-Path, trailing-slash); the CSV export pass-through (header-only artifact, under `build/tmp`) |

## Testbed design (setUp, L68-104)

- `setUpClass` (L64): `CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)` — imported from the shared
  `reversi.test.paths` module.
- `sys.stdout` patched to a StringIO (keeps the SM display out of the test log); the dummy `dummy_config.json` (`{}`) in
  a `tempfile.TemporaryDirectory(dir=CUSTOM_TMP_BASE)` created FIRST in setUp (mid-setup failures still leave a
  cleanable `temp_dir`).
- `patch('reversi.lm.logistic_model.wrk_config', ...)` + the same for `wrk_positions`: the factories are replaced in the
  MODULE namespace, so the uncommented worker-list entries pick up the dummy workers.
- One shared `LogisticModel` built in setUp (the tests are non-mutating; the one mutating test restores via `addCleanup`);
  `tearDown` (L112) is defensive against mid-setup failures.

## Goldens pinned

- The pass-through `assert_called_once_with` contracts (per-method).
- The closure identity pins (injected helpers == the machine closures; pre-injection == the no-op lambda default).
- The exception types/messages at the facade boundary: the init ValidationError, the helper FileNotFoundErrors, the
  sentinel raises.
- The cache-path computation for the dummy `cfg` (the worker-path pin).

## Conventions

- The `build/tmp` artifact rule: CSV export artifacts land under `build/tmp`.
- The 2 probe-derived tests pin the full guard contract.

## Integration

- Module under test: `logistic_model.md` (the first concrete domain facade — LogisticModel + the LMContext dataclass) on
  `base_model.md` (the BaseModel facade base).
- `test_state_machine.md` covers the SM core; this suite covers the facade boundary + the LMContext shape + the
  injection layer.
