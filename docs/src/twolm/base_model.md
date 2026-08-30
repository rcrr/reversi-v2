# base_model.py — analysis

Date: 2026-08-30. Module added by Roberto (6bb45fb, 6-file batch with
logistic_model + 3 sibling domain modules + test_logistic_model).
**Analysis session 21; fix campaign: batch 1 (D-074) R1 RESOLVED
(@validate_call on `__init__`, decided once with logistic_model R3,
applied to both facades); batch 2 (D-075) M1 FIXED (`__all__`
added, Roberto: "aggiungi"). All R/M items closed (M2 is
informational, kept by design).**
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
| `BaseModel.__init__(workers, context, verbosity=STANDARD)` | Stores `self.context` and builds `self.sm = StateMachine(workers, context, verbosity)`. Gated by `@validate_call` (D-074/R1); no other own validation. |
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
| V4 | All 7 pass-through methods are one-line delegations (source-verified); type errors on `move_to_step`/`move_to_last` surface from the SM's @validate_call gate, not from the facade. Post D-074/R1 the `__init__` boundary itself is facade-gated, so the class is now gated at BOTH its own entry and the inner SM boundary | Source + probe (state_machine docs) |
| V5 | (pre-D-075) base_model.py had NO `__all__` — the only twolm module without one (all other 13 define it); post D-075/M1 `__all__ = ['BaseModel']` (L39) | grep (pre) + re-check (post) |

## Issues (R1)

### R1 — No `@validate_call` on `__init__` — RESOLVED (D-074, session 21, with logistic_model R3)
House convention (NOTES.md "Conventions in the code"): `@validate_call`
(pydantic, arbitrary_types_allowed) on all public functions.
`BaseModel.__init__` (and `LogisticModel.__init__`, see
logistic_model.md R3) carried no gate: `workers: List[Worker]` /
`context: Context` were only enforced at the inner
`StateMachine.__init__` boundary (which IS gated, D-069 M11), so a
wrong-typed argument still failed fast — but as a pydantic
ValidationError from the SM, and the facade's own annotations were
not validated at the facade boundary. **Applied (D-074), option (a),
Roberto-approved (decided once, applied to both facades):**
`@validate_call(config=ConfigDict(arbitrary_types_allowed=True))` on
`BaseModel.__init__` AND on `LogisticModel.__init__` (pydantic is
now an import in both modules). Approved behaviour change:
wrong-typed constructor args now raise a pydantic `ValidationError`
at the facade boundary instead of at the inner SM gate; the SM gate
still runs behind it (belt-and-braces).

## Minor notes (M1-M2)

- **M1** (FIXED, D-075) — Missing `__all__ = ['BaseModel']` (V5):
  every other twolm module defines `__all__` (D-068 M1 pattern).
  Added (L39, Roberto: "aggiungi") — the module is now 89 lines.
- **M2** — The docstring forward-references `DeepNetworkModel` (a
  not-yet-ported module). Informational; keep — it documents the
  intended reuse of the facade.

## Appendix: line-number reference (2026-08-30, file 89 lines,
post D-075)

- `# twolm/base_model.py` header comment: L28
- imports: L31 (pathlib) · L32 (typing.List) · L34 (pydantic,
  D-074/R1) · L36 (state_machine)
- `__all__`: L39 (M1, D-075)
- `class BaseModel`: L42 (docstring: L43-47)
- `__init__`: L50 (body: L51-56) — `@validate_call` L49 (R1)
- `current_step` property: L59-60
- `current_worker_name` property: L63-64
- `verbosity` property: L67-68 (getter) · L70-72 (setter)
- `move_to_step`: L74-76
- `move_to_last`: L78-80
- `show_event_log`: L82-83
- `show_history_of_moves`: L85-86
- `export_history_of_moves_as_csv`: L88-89
