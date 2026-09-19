# reversi/base_model.py
`BaseModel` is a thin **facade base class** for pipeline domains: it encapsulates the generic delegation to
`reversi.tools.state_machine.StateMachine` so concrete domain facades (LogisticModel today, DeepNetworkModel in the
planned future) do not repeat the boilerplate. It owns NO pipeline state of its own: the `StateMachine` is the only
stateful object, and the facade is a pure pass-through layer plus ONE orchestrating entry — `run()`, the target-driven
driver (the generic half of the pipeline stop; the domain supplies its configured target through the
`_configured_target_level` hook). `self.context` is the SAME object as `self.sm.context` (identity verified — both point
at the shared LMContext).

## API

| name | contract |
|---|---|
| `BaseModel.__init__(workers, context, verbosity=STANDARD)` | Stores `self.context` and builds `self.sm = StateMachine(workers, context, verbosity)`; gated by `@validate_call`; no other own validation |
| `current_step` (property) | → `self.sm.current_step` |
| `current_worker_name` (property) | → `self.sm.current_worker_name` |
| `verbosity` (property, get + set) | → `self.sm.verbosity` both ways |
| `move_to_step` | Pass-through to `self.sm.move_to_step` (gated by the SM's @validate_call) |
| `move_to_last`, `show_event_log`, `show_history_of_moves`, `export_history_of_moves_as_csv` | Pass-throughs |
| `run(target_level=None)` | The target-driven driver: `move_to_step(1)` when the machine is still at the sentinel (the domain config must be loaded), then the target = the explicit argument, else `_configured_target_level()`, else the last step; `"last"` (any case) and a blank value → `move_to_last()`, anything else → `move_to_step(target)`. The machine's contracts apply unchanged (the target IS executed, the ValueError / TypeError gate, the down() of a backward move) |
| `_configured_target_level()` | The domain hook: `None` in the base (the whole pipeline); a concrete facade overrides it to read its own config |

`__all__` = [BaseModel].

## Architecture

126 lines.

- the module header comment; imports (pathlib, typing.List, pydantic, state_machine).
- `class BaseModel` (docstring the DeepNetworkModel forward-reference, kept by design).
- The pass-through surface: every delegation method is a one-line pass-through (source-verified); type errors on
  `move_to_step`/`move_to_last` surface from the SM's @validate_call gate, not from the facade. The `__init__` boundary
  itself is facade-gated, so the class is gated at BOTH its own entry and the inner SM boundary.
- `run()` is the ONLY method with logic of its own: it resolves the stop and hands the move to the machine, which keeps
  every execution contract (the up/down steps, the failure semantics, the history). The CONFIG-first move is what makes
  the domain hook resolvable at all: the config is read from the context AFTER the first level ran. A second call with a
  deeper target is a RESUME — the levels already done are not re-run, so the published context artifacts survive and the
  on-disk caches stay hot; the motivating case is a pipeline whose long level (the SU_ANALYSIS corpus) is worth running
  before deciding whether to go further.

## Verified invariants

Pinned by the `probes/verify_logistic_model.py` (21 checks — the base_model + logistic_model family probe) + the
`test_logistic_model` suite (29 tests) through the LogisticModel subclass.

- V1: `model.context is model.sm.context` — one shared context object, no copy: the facade hands the SAME object to the
  StateMachine in `__init__` (source-verified); the suite pins the context's own shape
  (`test_logistic_model::test_context_initialization`).
- V2: `model.sm` is a StateMachine; `verbosity` defaults to STANDARD; the setter delegates (set on the facade → visible
  on the SM) — `test_facade_views_and_verbosity_round_trip`.
- V3: at construction `current_step == 0`, `current_worker_name == "CREATED"` (the SM starts at the sentinel) —
  `test_state_machine_initialization`.
- V4: the 5 delegation methods (`move_to_step`, `move_to_last`, `show_event_log`, `show_history_of_moves`,
  `export_history_of_moves_as_csv`) are one-line pass-throughs —
  `test_logistic_model::test_facade_delegates_to_state_machine` (per-method `patch.object(self.model.sm, ...)` +
  `assert_called_once_with`); the properties are covered by `test_facade_views_and_verbosity_round_trip`.
- V5: `run()` is generic and inherited — the base hook returns None (the last step), a bare `BaseModel` over a 2-worker
  pipeline drives it, and the LogisticModel override reads the config —
  `test_logistic_model::test_run_base_default_is_the_last_step`.

## Open issues

None.

## Conventions

- `@validate_call` on `__init__` is the house convention for constructors/factories (pydantic, arbitrary_types_allowed):
  wrong-typed constructor args raise a pydantic `ValidationError` at the facade boundary; the SM gate runs behind it
  (belt-and-braces).
- A domain facade adds behaviour by OVERRIDING a hook, not by re-implementing the generic driver: `run()` stays here,
  `_configured_target_level()` is the single override point.

## Integration

- `LogisticModel` (logistic_model.md) is the concrete domain facade on this base; the sibling modules wrk_config /
  wrk_positions / hlp_config_schemas are the pipeline levels.
- `state_machine.md` is the delegated-to core; the facade adds no behaviour of its own beyond the delegation + the own
  `@validate_call` gate + the `run()` stop resolution.
