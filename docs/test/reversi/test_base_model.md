# test/reversi/test_base_model.py

The `BaseModel` facade unit suite — 1 class / 9 tests, no DB, < 0.2 s. The facade is the generic delegation layer
shared by the concrete pipeline facades (the `LogisticModel` first among them): a 3-worker mock machine pins the
contract without touching the domain.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestBaseModelFacade` | 9 | construction (the machine is built, the context is shared, step 0); the `current_step` / `current_worker_name` / `verbosity` delegation (get + set); `move_to_step` / `move_to_last`; `run()` — the named target, the "last" string, the default (the base `_configured_target_level` is None → the whole pipeline), and the RESUME semantics (a deeper target does not re-run the levels already done); the `_configured_target_level` base default |

## Goldens pinned

None. (The pins are the delegation and stop-target contracts; no hash or value goldens.)

## Conventions

- the 3 mock workers are `MagicMock` up/down callables named `A` / `B` / `C` (the test_state_machine idiom), so a
  stop-target test reads as a worker name, not an index.
- stdout is patched for the whole class (the machine logs at the STANDARD verbosity by default).

## Integration

Mirrors `src/reversi/base_model.py` (the `BaseModel` facade). A concrete facade that forgets to delegate (or
re-implements the run/resume logic) surfaces here first, at < 0.2 s cost; the domain-level behaviour of
`LogisticModel` itself stays in `test_logistic_model` and the end-to-end chain.
