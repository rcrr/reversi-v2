# reversi/test/test_state_machine.py
The state-machine unit suite — 5 classes / 49 tests, no PERF gates,
~0.3 s, no DB. The E2/E3 probe checks from `verify_wrk_config.py`
are pinned as full-message `assertEqual` in two existing tests.

## Coverage

| class (line) | tests | what it pins |
|---|---|---|
| `TestStateMachine` (L62) | 33 | the init state (`current_step == 0`, `current_worker_name == "CREATED"`, 3 workers, exactly 1 init DEBUG log); the up/down mechanics (single/multi-step, down-to-zero, same-step no-op, the up/down asymmetry — the target's `up` runs, the target's `down` does not); the worker-0 sentinel never executed; the failure/retry/recovery semantics (the failed step is skipped on retry, then re-executed); `move_to_last` (3 pins: happy path, from intermediate, single-worker no-op); int/string targets (the E2/E3 full messages — "Worker 'NON_EXISTENT_WORKER' not found in the pipeline.", the IndexError/TypeError bounds); the bool/np.int64 edge (both rejected); the constructor `ValidationError`s; `current_worker_name` live view + "UNDEFINED"; the StepMove field content (aware-UTC start/finish, `duration == finish - start` exactly, the failed-step-still-recorded pin); the exception propagation + exactly-1-ERROR log; the CSV export (exact header fields, ISO-8601 `+00:00` parsed back, `duration_sec` identity, artifact under `build/tmp`); duplicate worker names (reject + case-insensitive); the explicit `_run_step` direction dispatch; the `__repr__` goldens on Worker/StateMachine; the CSV parent-dir creation; the cache prefix VERBATIM concatenation (`cache01_CONFIG.dat`) |
| `TestLogEntry` (L532) | 3 | the R2 typed-record contract: the 5 field values of `logs[0]` (aware-UTC time, step 0, "CREATED", `Relevance.DEBUG`, the init message), the frozen-dataclass immutability (`FrozenInstanceError`), the `dataclasses.asdict` 5-key dump shape |
| `TestVerbosityGating` (L577) | 2 | the full 6×5 gating matrix on captured stdout (prints iff `relevance >= verbosity` — NONE silent, VERY_LOW ERROR-only; `logs` accumulates even when not printed) + the enum values (VERY_LOW = 4, NONE = 5) |
| `TestContextInjection` (L629) | 8 | the injected `log_event` is the machine's bound method (`__self__ is sm`) and appends to THIS machine's logs; the cache-file path `{prefix}{level:02}_{name}.dat` tracks `current_step` at call time; the base_dir join + the absolute-prefix-drops-base_dir case; the `cfg`-missing `AttributeError` naming `cfg`; the empty-workers degenerate paths (`Path()`, "UNDEFINED", the `move_to_last` guarded no-op); the V17 shared-context re-bind to the LAST machine built |
| `TestDisplayGoldens` (L761) | 3 | under a frozen clock (1ms per `now()`): the live line `[ts UTC] [step:02][name:15] [rel.name:verb.name] message` full golden (the enum-NAME rendering + explicit `UTC` marker); the `show_event_log` buffer (banner, 66-underscore separator, the `TIMESTAMP (UTC) \| STEP \| WORKER \| RELEVANCE \| MESSAGE` header); the `show_history_of_moves` buffer (the right-aligned `Dur (s)` header, 80-dash rule, the 0.003000 duration pin) |

## Goldens pinned

- The 3 display goldens (exact end-to-end buffers, wall-clock
  independent — the frozen clock).
- The Worker/StateMachine `__repr__` strings.
- The CSV header field names + the ISO-8601 `+00:00` round-trip.
- The E2/E3 FULL exception messages (the probe contract, now test-pinned).
- The cache-path shapes (`00_CREATED` → `02_POSITIONS` → `01_CONFIG`,
  `base/cache/01_CONFIG.dat`, the verbatim `cache01_CONFIG.dat`).
- The gating-matrix cells (30) + the enum values.

## Conventions

- The `setUp` global stdout patch is LOAD-BEARING: the captured
  stdout is asserted — not noise suppression.
- Test artifacts are written ONLY under `workspace_root/build/tmp`
  (the house rule, now via the shared `reversi.test.paths`
  `CUSTOM_TMP_BASE`) and removed in `finally` — a failing test leaves
  no garbage.
- The re-pinned guard contract (E2/E3) lives in the suite — the probe
  no longer carries those checks.

## Integration

- Module under test: `state_machine.md` (the generic pipeline
  state-machine core). The context-injection layer (this suite's
  `TestContextInjection`) is the module's main integration surface
  with the domain workers — the `LMContext` injection is
  load-bearing.
- The E2/E3 full-message conversions came from
  `probes/verify_wrk_config.py` (E2/E3 → the two
  `TestStateMachine` full-message pins).
