# base_model.py — analysis

Date: 2026-08-30. Module added by Roberto (6bb45fb, 6-file batch with
logistic_model + 3 sibling domain modules + test_logistic_model).
**Analysis session 21; fix campaign pending Roberto's calls.**
Sibling modules lm_worker_config / lm_worker_positions /
rlm_config_schemas are deliberately NOT analyzed in this session
(Roberto: "Lo faremo in seguito").

Suite: no dedicated suite (covered by test_logistic_model through
the LogisticModel subclass, 5/0/0 GREEN).

## Architecture

`BaseModel` is a thin **facade base class** for pipeline domains: it
encapsulates the generic delegation to `twolm.state_machine.
StateMachine` so concrete domain facades (LogisticModel today,
DeepNetworkModel in the planned future) do not repeat the boilerplate.
It owns NO pipeline state of its own: the `StateMachine` is the only
stateful object, and the facade is a pure pass-through layer.
`self.context` is the SAME object as `self.sm.context` (identity
verified, V1 — both point at the shared RLMContext).

### Components

| Component | Role |
|---|---|
| `BaseModel.__init__(workers, context, verbosity=STANDARD)` | Stores `self.context` and builds `self.sm = StateMachine(workers, context, verbosity)`. No own validation (see R1). |
| `current_step` (property) | → `self.sm.current_step`. |
| `current_worker_name` (property) | → `self.sm.current_worker_name`. |
| `verbosity` (property, get + set) | → `self.sm.verbosity` both ways (D-068-style delegation). |
| `move_to_step(target_step)` | Pass-through to `self.sm.move_to_step` (gated by the SM's @validate_call, D-069 M11). |
| `move_to_last()` | Pass-through. |
| `show_event_log()` | Pass-through. |
| `show_history_of_moves()` | Pass-through. |
| `export_history_of_moves_as_csv(filename)` | Pass-through. |

## Verified facts (V1-V5)

Independently re-derived (scratch/verify_logistic_model.py, 30-check
probe covering base_model + logistic_model together), zero
mismatches.

| # | Fact | Method |
|---|---|---|
| V1 | `model.context is model.sm.context` (one shared context object, no copy) | Identity probe |
| V2 | `model.sm` is a StateMachine; `verbosity` defaults to STANDARD; the setter delegates (set on the facade → visible on the SM) | Probe |
| V3 | At construction `current_step == 0`, `current_worker_name == "CREATED"` (the SM starts at the sentinel) | Probe |
| V4 | All 7 pass-through methods are one-line delegations (source-verified); type errors on `move_to_step`/`move_to_last` surface from the SM's @validate_call gate, not from the facade | Source + probe (state_machine docs) |
| V5 | base_model.py has NO `__all__` — the only twolm module without one (all other 13 define it) | grep |

## Issues (R1)

### R1 — No `@validate_call` on `__init__` — OPEN, awaiting Roberto's call
House convention (NOTES.md "Conventions in the code"): `@validate_call`
(pydantic, arbitrary_types_allowed) on all public functions.
`BaseModel.__init__` (and `LogisticModel.__init__`, see
logistic_model.md R3) carry no gate: `workers: List[Worker]` /
`context: Context` are only enforced at the inner
`StateMachine.__init__` boundary (which IS gated, D-069 M11), so a
wrong-typed argument still fails fast — but as a pydantic
ValidationError from the SM, and the facade's own annotations are
not validated at the facade boundary. Options: (a) add
`@validate_call(config=ConfigDict(arbitrary_types_allowed=True))` to
`BaseModel.__init__` (and `LogisticModel.__init__` — decision made
once, applied to both); (b) leave as-is (the thin layer defers to the
SM gate; the domain constructors do their own manual path checks).

## Minor notes (M1-M2)

- **M1** — Missing `__all__ = ['BaseModel']` (V5): every other twolm
  module defines `__all__` (D-068 M1 pattern).
- **M2** — The docstring forward-references `DeepNetworkModel` (a
  not-yet-ported module). Informational; keep — it documents the
  intended reuse of the facade.

## Appendix: line-number reference (2026-08-30, file 84 lines)

- `# twolm/base_model.py` header comment: L28
- imports: L31 (pathlib) · L32 (typing.List) · L34 (state_machine)
- `class BaseModel`: L38 (docstring: L39-43)
- `__init__`: L45 (body: L46-51)
- `current_step` property: L53-55
- `current_worker_name` property: L57-59
- `verbosity` property: L61-63 (getter) · L65-67 (setter)
- `move_to_step`: L69-71
- `move_to_last`: L73-75
- `show_event_log`: L77-78
- `show_history_of_moves`: L80-81
- `export_history_of_moves_as_csv`: L83-84
- (no `__all__` — M1)
