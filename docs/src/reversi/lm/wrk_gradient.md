# reversi/lm/wrk_gradient.py
The GRADIENT worker of the LM pipeline: builds the loss/gradient
closure in `_up` (`ctx.fg = hlp_gradient_compute(ctx)`) and clears
it in `_down`. The SECOND non-cache level (after ZED): the comment
at L48 documents the on-the-fly choice — "GRADIENT building is a
closure generation, very fast. No cache needed." No cache_manager
wiring, no rlmwf_07* / rlmwf_08* file ever.
> State: D-094 · 34442b2 · 2026-09-01 · suite 2/0/0 (2 DB-gated)

## API

| name | contract |
|---|---|
| `wrk_gradient()` | the factory — `@validate_call(config=ConfigDict(arbitrary_types_allowed=True))` (D-094 T2, like all the other worker factories) returning `Worker("GRADIENT", _up, _down)` |

## Architecture

- Imports: `Worker, Relevance` from state_machine;
  `hlp_gradient_compute` from hlp_gradient; `validate_call,
  ConfigDict` from pydantic (added in D-094 T2); `LMContext`
  under TYPE_CHECKING. NO `reversi.tools.cache_manager` import (by
  design — pinned by probe B).
- `_up`: INFO "Building gradient and loss function (fg)..." →
  the by-design comment (L48: "GRADIENT building is a closure
  generation, very fast. No cache needed.") →
  `ctx.fg = hlp_gradient_compute(ctx)` → INFO "Gradient function
  generated."
- `_down`: INFO "Clearing gradient function..." → `ctx.fg =
  None`.
- The house-style triple blank lines (before `__all__` and
  before `_up`) — left as-is by Roberto (M4, the canonical
  pattern of all 8 worker files).

## Verified invariants

Pinned by the `probes/verify_gradient.py` B + C + D + E + G
tiers + the 2-test suite.

- Source shape (probe B1-B9): the 62-line file, `__all__ =
  ['wrk_gradient']`, the factory WITH `@validate_call` +
  the pydantic import (T2), NO cache_manager import (the L48
  by-design comment pinned), `_up` sets `ctx.fg`, `_down` clears
  it, `Worker("GRADIENT", ...)`.
- The worker-test source shape (probe C1-C10): the 142-line
  file, the 1 class / 2 tests, the gate (T5), the D-085 idiom
  (T6), the step pins, the 4 goldens, the _down test (T7), 0
  non-comment ws lines (T8).
- The full pipeline through GRADIENT (live DB, probe D0 +
  D5-D10 + D12, rlm_02 — 199952 positions): the pipeline
  bootstrap (the move to GRADIENT runs the whole chain); alpha +
  clipping; f(w=0) + g(w=0) re-derived (the independent float64
  reference, the float32 R1 pin); f+g at w ≠ 0 (the ridge); the
  closure stateless (2 calls); NO rlmwf_07*/08* file in the base
  dir (the cache files stop at rlmwf_06_DESIGN_MTR); the feature
  set (8 instances: DIAG3 + EDGE, no intercept, no mobilities).
- The cross-file facts (probe E1/E4-E8): LMContext's `fg`
  field pre-declared; scipy in pyproject.toml + in the venv; the
  `ridge_regularization` field; the rlm_02 config.
- The dedicated suite (probe G1-G8): the 169-line file, 2
  classes / 8 tests, no DB wiring, the goldens pinned.
- The live goldens (DB-gated): `test_generate_gradient` (the 4
  pinned values at w=0) + `test_down_clears_gradient` (the
  step-7 / "ZED" / fg-None pin) — `test_wrk_gradient.py`
  (2 tests, both DB-gated since D-094 T5).

## Open issues

None.

## Conventions

- The no-cache design is the second deviation from the uniform
  7-kwargs `cache_manager` wiring (ZED first) — intentional and
  documented (the L48 comment); `ctx.fg` is still cleared on
  down (the machine contract holds).
- No `use_cache` interaction: with `ctx.use_cache=False` the
  other levels still warm their cache files; GRADIENT has
  nothing to warm — the behavior is identical either way.

## Integration

- The 9th LM level; the domain module (hlp_gradient.py)
  carries the closure math, this worker the machine glue.
- Consumes `ctx.design_matrix` (DESIGN_MTR), `ctx.z` (ZED),
  `ctx.w` (WMAPS) + `ctx.cfg.stat_model.ridge_regularization`
  (CONFIG) — the SM half-open interval semantics guarantee all
  are set. The worker-test setUp moves through ZED (step 7)
  first, so the full 9-level chain is exercised end-to-end on
  the live DB.
- Publishes `ctx.fg` (the loss/gradient closure) for the
  OPTIMIZE level onward.
