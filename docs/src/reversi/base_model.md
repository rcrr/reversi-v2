# reversi/base_model.py
`BaseModel` is a thin **facade base class** for pipeline domains: it
encapsulates the generic delegation to `reversi.tools.state_machine.StateMachine`
so concrete domain facades (LogisticModel today, DeepNetworkModel in the
planned future) do not repeat the boilerplate. It owns NO pipeline state
of its own: the `StateMachine` is the only stateful object, and the
facade is a pure pass-through layer. `self.context` is the SAME object
as `self.sm.context` (identity verified — both point at the shared
RLMContext).
> State: D-075 · afd8f76 · 2026-08-30 · suite 17/0/0 (via
  test_logistic_model through the LogisticModel subclass, no dedicated
  suite)

## API

| name | contract |
|---|---|
| `BaseModel.__init__(workers, context, verbosity=STANDARD)` (L50) | Stores `self.context` and builds `self.sm = StateMachine(workers, context, verbosity)`; gated by `@validate_call` (L49, D-074/R1 — decided once with logistic_model R3, applied to both facades); no other own validation |
| `current_step` (property, L59) | → `self.sm.current_step` |
| `current_worker_name` (property, L63) | → `self.sm.current_worker_name` |
| `verbosity` (property, get L67 + set L70) | → `self.sm.verbosity` both ways |
| `move_to_step` (L74) | Pass-through to `self.sm.move_to_step` (gated by the SM's @validate_call, D-069 M11) |
| `move_to_last` (L78), `show_event_log` (L82), `show_history_of_moves` (L85), `export_history_of_moves_as_csv` (L88) | Pass-throughs |

`__all__` (L39) = [BaseModel] (M1, D-075 — before that this was the only
twolm module without one).

## Architecture

89 lines (post D-075).

- L28 the module header comment; L31-36 imports (pathlib, typing.List,
  pydantic — the D-074/R1 add —, state_machine).
- `class BaseModel` L42 (docstring L43-47 — the DeepNetworkModel
  forward-reference, M2 informational, kept by design).
- The pass-through surface: every method is a one-line delegation
  (source-verified); type errors on `move_to_step`/`move_to_last`
  surface from the SM's @validate_call gate, not from the facade.
  Post D-074/R1 the `__init__` boundary itself is facade-gated, so the
  class is gated at BOTH its own entry and the inner SM boundary.

## Verified invariants

Pinned by the `probes/verify_logistic_model.py` (21 checks — the
base_model + logistic_model family probe) + the `test_logistic_model`
suite (17 tests) through the LogisticModel subclass. The pre-step-3
30-check figure froze in the archive.

- V1: `model.context is model.sm.context` — one shared context object,
  no copy (the suite's `test_context_initialization` + probe).
- V2: `model.sm` is a StateMachine; `verbosity` defaults to STANDARD;
  the setter delegates (set on the facade → visible on the SM) —
  `test_facade_views_and_verbosity_round_trip`.
- V3: at construction `current_step == 0`,
  `current_worker_name == "CREATED"` (the SM starts at the sentinel) —
  `test_state_machine_initialization`.
- V4: all 7 pass-through methods are one-line delegations —
  `test_facade_delegates_to_state_machine` (per-method
  `patch.object(self.model.sm, ...)` + `assert_called_once_with`).

## Open issues

None.

## Conventions

- `@validate_call` on `__init__` is the house convention for
  constructors/factories (pydantic, arbitrary_types_allowed) — the
  approved behaviour change: wrong-typed constructor args now raise a
  pydantic `ValidationError` at the facade boundary instead of at the
  inner SM gate; the SM gate still runs behind it (belt-and-braces).

## Integration

- `LogisticModel` (logistic_model.md) is the first concrete domain
  facade on this base; the sibling modules
  wrk_config / lm_worker_positions / rlm_config_schemas were
  deliberately NOT analyzed in the session-21 analysis (Roberto: "Lo
  faremo in seguito") — they were brought in afterwards as the
  pipeline levels.
- `state_machine.md` is the delegated-to core; the facade adds no
  behaviour of its own beyond the delegation + the own `@validate_call`
  gate.
