# reversi/lm/wrk_gradient.py
The GRADIENT worker of the LM pipeline — the 10th active level (step 10): builds the loss/gradient closure in `_up`
(reading the `high_performance_fg` flag + the `hi_perf_blocks` block count from `ctx.cfg.optimization` and passing
both to `hlp_gradient_compute`) and clears it in `_down`. The SECOND non-cache level (after ZED): the comment
documents the on-the-fly choice — "GRADIENT building is a closure generation, very fast. No cache needed." No
cache_manager wiring, no rlmwf_09* / rlmwf_10* file ever.

## API

| name | contract |
|---|---|
| `wrk_gradient()` | the factory — `@validate_call(config=ConfigDict(arbitrary_types_allowed=True))` (like all the other worker factories) returning `Worker("GRADIENT", _up, _down)` |

## Architecture

- Imports: `Worker, Relevance` from state_machine; `hlp_gradient_compute` from hlp_gradient; `validate_call, ConfigDict`
  from pydantic; `LMContext` under TYPE_CHECKING. NO `reversi.tools.cache_manager` import (by design — pinned by probe
  B).
- `_up`: INFO "Building gradient and loss function (fg)..." → the by-design comment ("GRADIENT building is a closure
  generation, very fast. No cache needed.") → `high_performance = ctx.cfg.optimization.high_performance_fg` →
  `hi_perf_blocks = ctx.cfg.optimization.hi_perf_blocks` →
  `ctx.fg = hlp_gradient_compute(ctx, high_performance=high_performance, hi_perf_blocks=hi_perf_blocks)` → INFO
  "Gradient function generated (high_performance: {True|False})." (the log line names the built variant).
- `_down`: INFO "Clearing gradient function..." → `ctx.fg = None`.
- The house-style triple blank lines (before `__all__` and before `_up`) — the canonical pattern of the worker files.

## Verified invariants

Pinned by the `probes/verify_gradient.py` B + C + D + E + G tiers + the 4-test suite (2 classes: the DB-gated pair +
`TestGradientFlagWiring`).

- Source shape (probe B1-B9): `__all__ = ['wrk_gradient']`, the factory WITH `@validate_call` + the
  pydantic import, NO cache_manager import (the by-design comment pinned), `_up` reads the `high_performance_fg` flag
  + `hi_perf_blocks`, sets `ctx.fg` (passing both) and logs the variant, `_down` clears it, `Worker("GRADIENT", ...)`.
- The worker-test source shape (probe C1-C11): the 2 classes / 4 tests (the 2 DB-gated rlm_02 tests +
  the no-DB TestGradientFlagWiring pair), the gate, the idiom, the step pins, the 4 goldens, the _down test, the wiring
  test (C11: the worker + the Context-subclass mock + the marker pin), 0 non-comment ws lines.
- The full pipeline through GRADIENT (live DB, probe D0 + D5-D10 + D12, rlm_02 — 199952 positions): the pipeline
  bootstrap (the move to GRADIENT runs the whole chain); alpha + clipping; f(w=0) + g(w=0) re-derived (the independent
  float64 reference, the float32 R1 pin); f+g at w ≠ 0 (the ridge); the closure stateless (2 calls); NO rlmwf_09*/10*
  file in the base dir (the cache files stop at rlmwf_08_DESIGN_MTR); the feature set (8 instances: DIAG3 + EDGE, no
  intercept, no mobilities).
- The cross-file facts (probe E1/E4-E8): LMContext's `fg` field pre-declared; scipy in pyproject.toml + in the venv; the
  `ridge_regularization` field; the rlm_02 config.
- The dedicated suite (probe G1-G9): 3 classes / 15 tests, no DB wiring, the goldens pinned (the
  TestHighPerformanceFg class: the equivalence, the f32 contract, the determinism, the markers).
- The live goldens (DB-gated): `test_generate_gradient` (the 4 pinned values at w=0, rlm_02 → the classic path) +
  `test_down_clears_gradient` (the step-9 / "ZED" / fg-None pin) — `test_wrk_gradient.py`.

## Open issues

None.

## Conventions

- The no-cache design is a deviation from the uniform 7-kwargs `cache_manager` wiring — intentional and documented (the
  comment); `ctx.fg` is still cleared on down (the machine contract holds).
- No `use_cache` interaction: with `ctx.use_cache=False` the other levels still warm their cache files; GRADIENT has
  nothing to warm — the behavior is identical either way.

## Integration

- The 10th LM level; the domain module (hlp_gradient.py) carries the closure math, this worker the machine glue.
- Consumes `ctx.design_matrix` (DESIGN_MTR), `ctx.z` (ZED), `ctx.w` (WMAPS) + `ctx.cfg.stat_model.ridge_regularization`
  + `ctx.cfg.optimization.high_performance_fg` / `hi_perf_blocks` (all CONFIG) — the SM half-open interval semantics
  guarantee all are set. The worker-test setUp moves through ZED (step 9)
  first, so the full 10-level chain is exercised end-to-end on the live DB.
- Publishes `ctx.fg` (the loss/gradient closure) for the OPTIMIZE level onward.
