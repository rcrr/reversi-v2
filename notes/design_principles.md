# design_principles.md — active design principles

The workspace design policy, cross-cutting: it binds any new code in the pipeline, not one module.

The register of every DESIGN PRINCIPLE in force right now.

Lifecycle (same commit as the decision it records):
- RECORD — every decision (including "leave as-is for now") goes to notes/decisions.md with date and rationale.
- PROMOTE — a decision that establishes an enduring design principle adds its numbered line here, in the same commit.
- RETIRE — a design principle no longer in force is removed here, retirement logged in decisions.md with a new D-number.

Governance: a design principle is added, amended or retired only on explicit user approval. The DP-numbers are global,
ordered from the smallest to the largest, and NEVER reused (an amendment keeps its number; a retirement leaves the gap);
the order is by value: DP-510 < DP-511 < DP-511.1 < DP-511.3 < DP-511.17 < DP-512 < DP-600 < DP-999. A design principle
is a bold title line (`**DP-NNN — the topic**`), a blank line, and a 1–3 line description (longer only when it must be)
— or, when the design principle fits, one bold line; two blank lines between one design principle and the next. Lines
are ~120 chars. When a new design principle is best placed in a specific order a notation (`**DP-NNN.N — the topic**`)
can be used.

**DP-010 — Dual scalar/array API**

Public functions, operating on vectorizable input, like `Bitboard`, `Position`, or `Index`, accept a scalar or array and
return the input kind. Not a style choice — it follows the numpy design, which the solution's performance is built on.


**DP-020 — Pydantic validation**

`@validate_call` on public functions, when the function has no specific performance problem and has no convoluted
backstory (the standing case: the state-machine Context, whose validation gate is deliberately separate from the move
execution). The validation is applied consistently.


**DP-030 — Numba njit compilation**

When performance is the goal and the benefit is proven, hot loops run as `njit(cache=True)` kernels — the best
performance is the objective. The kernel is always embedded in a normal Python function, scalar or vectorized. The
kernel doesn't leak into the API, unless it is consumed by a larger kernel in a different module to avoid code
duplication.
