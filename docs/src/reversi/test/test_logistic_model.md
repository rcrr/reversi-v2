# reversi/test/test_logistic_model.py
The logistic-model unit suite — 1 class / 17 tests (15 original + 2
converted from the verify_wrk_config.py D1/E4b probe checks at
D-106 step 3), no PERF gates, ~0.15 s, no DB. 311 lines; the D-075
T-campaign narrative froze in the archive.
> State: D-106 · 73a72d3 · 2026-09-04 · suite 17/0/0 (no PERF gates,
  no DB)

## Coverage

| class (line) | tests | what it pins |
|---|---|---|
| `TestLogisticModel` (L62) | 17 | the context init (RLMContext, `config_file_path` round-trip, `base_dir_override` None, `cfg` None); the SM sentinel start (`current_step == 0`, "CREATED"); the init `ValidationError` on a non-str config path (step 3: the D1 probe conversion, the D-107 guard contract); the injected cache closure requiring `cfg` (AttributeError before CONFIG — step 3, the E4b conversion); the `move_to_step` delegation (int + str name) with the CONFIG level; the invalid config path + base_dir override `FileNotFoundError`s; the facade pass-through pins (`test_facade_delegates_to_state_machine` — per-method `patch.object(self.model.sm, ...)` + `assert_called_once_with`; the T1 replacement of the overpromising smoke test); the views + verbosity round-trip; the injected cache helpers ARE the machine closures (would have caught R1); the pre-injection no-op lambda fallback; the injected helper computing the worker path (dummy `cfg`, `addCleanup` restore); the CREATED sentinel workers raise (D-059); the config/base_dir helper edge branches (str-vs-Path, trailing-slash); the CSV export pass-through (header-only artifact, under `build/tmp`) |

## Testbed design (setUp, L68-104)

- `setUpClass` (L64): `CUSTOM_TMP_BASE.mkdir(parents=True,
  exist_ok=True)` — imported from the shared `reversi.test.paths`
  module (D-065 idiom, T2/D-075, centralized at D-085).
- `sys.stdout` patched to a StringIO (keeps the SM display out of
  the test log); the dummy `dummy_config.json` (`{}`) in a
  `tempfile.TemporaryDirectory(dir=CUSTOM_TMP_BASE)` created FIRST in
  setUp (mid-setup failures still leave a cleanable `temp_dir`).
- `patch('reversi.lm.logistic_model.wrk_config', ...)` + the same
  for `wrk_positions`: the factories are replaced in the MODULE
  namespace, so the uncommented worker-list entries pick up the dummy
  workers.
- One shared `LogisticModel` built in setUp (the tests are
  non-mutating; the one mutating test restores via `addCleanup`);
  `tearDown` (L112) is defensive against mid-setup failures.

## Goldens pinned

- The pass-through `assert_called_once_with` contracts (per-method).
- The closure identity pins (injected helpers == the machine
  closures; pre-injection == the no-op lambda default).
- The exception types/messages at the facade boundary (the D-107
  guard contract: the init ValidationError, the helper
  FileNotFoundErrors, the sentinel raises).
- The cache-path computation for the dummy `cfg` (the worker-path
  pin).

## Conventions

- The D-075 T1-T6 campaign: T1 the smoke-test replacement, T2 the
  `build/tmp` artifact rule, T4 the closure/helper pins, T5/T6 the
  restored tests (D-076 + the 2026-09-02 `test_move_to_step_by_
  string` restoration per Roberto's approval — the "una riga alla
  volta" plan of D-073/D-075 T3).
- The D-106 step-3 conversions (73a72d3) added the 2 probe-derived
  tests (the full guard-contract pin).

## Integration

- Module under test: `logistic_model.md` (the first concrete domain
  facade — LogisticModel + the RLMContext dataclass) on
  `base_model.md` (the BaseModel facade base).
- `test_state_machine.md` covers the SM core; this suite covers the
  facade boundary + the RLMContext shape + the injection layer.
