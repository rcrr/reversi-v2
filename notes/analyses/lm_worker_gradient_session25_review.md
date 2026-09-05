<!-- ARCHIVED — D-106 step 15 (the docs/ rewrite, 2026-09-04): the
     complete session-25 analysis (D-093) + the D-094
     fix-campaign narrative moved out of
     docs/src/twolm/lm_worker_gradient.md per
     docs_rules.md §1/§4. This is a frozen historical record: it
     is never updated. Stale-in-current-context notes: (1) the
     probe tier B is now part of the 54-call
     probes/verify_gradient.py (the 4091e72 move + the D-106
     step-3 class c deletions — D1-D4 + D11 to the worker test,
     E2/E3 to the hub); (2) the "573 tests / 68 skipped"
     full-discover figure predates steps 3-10 (current: 664/87
     gated); (3) the D-094 T2/T4/M4 campaign narrative is frozen
     history. -->

# twolm/lm_worker_gradient.py

Analysis date: 2026-09-01 — analysis session 25 (D-093); fix
campaign D-094 approved by Roberto and applied in the same session.
Brought in by Roberto (commit a0adc6e — the 9th active level of the
pipeline). Probe (scratch/verify_gradient.py, 61 checks, tiers
A–G, re-pinned in D-094 to the post-campaign state): 0 mismatches.

The GRADIENT worker of the RLM pipeline: builds the loss/gradient
closure in `_up` (`ctx.fg = rlm_gradient_compute(ctx)`) and clears
it in `_down`. The SECOND non-cache level (after ZED): the comment
at L48 documents the on-the-fly choice — "GRADIENT building is a
closure generation, very fast. No cache needed." No cache_manager
wiring, no rlmwf_07* / rlmwf_08* file ever (the next cache level
takes rlmwf_08).

## Suite status (session 25, post D-094)

- `test_lm_worker_gradient`: 2/0/0 live (1 class; both tests
  DB-gated since D-094 T5 — the setUp moves through ZED on a fresh
  base dir, so a live DB is required).
- `test_rlm_gradient` (the domain module, D-094 M1): 8/0/0.
- Full discover: 573 tests, 68 skipped under `SKIP_REGAB_DB=1`,
  GREEN; ungated (live DB): 573 run, 17 skipped (PERF only),
  GREEN. The full `-W error` discover is clean.

## State per Roberto

Pipeline-in-progress, 9 active levels. GRADIENT fix campaign
(D-094) CLOSED: T2 (the factory `@validate_call` + the pydantic
import) + T4 (3 ws lines) applied; M4 (the triple blank lines L39-
41 / L43-45) left as-is — the canonical pattern of all 8 worker
files (house style).

## Architecture (62 lines, post D-094)

- `_up` (L46-52): logs "Building gradient and loss function
  (fg)..." (L47), the by-design comment (L48: "GRADIENT building
  is a closure generation, very fast. No cache needed."),
  `ctx.fg = rlm_gradient_compute(ctx)` (L50), logs "Gradient
  function generated." (L52).
- `_down` (L54-56): logs "Clearing gradient function..." (L55),
  `ctx.fg = None` (L56).
- `lm_worker_gradient()` (L60-62, `@validate_call
  (config=ConfigDict(arbitrary_types_allowed=True))` since D-094
  T2 — like all 7 other worker factories): returns
  `Worker("GRADIENT", _up, _down)`.

## Verified facts

- The worker list is the 9 active entries (probe E2): CREATED
  sentinel + CONFIG + POSITIONS + FEATURES + INDEXES + WMAPS +
  DESIGN_MTR + ZED + GRADIENT.
- Live: at ZED `ctx.fg` is None; after `move_to_step('GRADIENT')`
  (step 8) `ctx.fg` is callable (probe D1/D2/D3); after
  `move_to_step(7)` back to ZED, `ctx.fg` is None again (probe
  D11, the worker test test_down_clears_gradient since D-094 T7).
- No `rlmwf_07*` / `rlmwf_08*` file ever materializes in the base
  dir (probe D10) — the cache files stop at rlmwf_06_DESIGN_MTR.
- The `fg` blackboard field was pre-declared in RLMContext
  (logistic_model.py L135) at first import.

## Minor notes

- M3 (informational, by design): the second non-cache level — the
  next cache level (OPTIMIZE) takes rlmwf_08.
- M4 (left as-is): the triple blank lines (L39-41 before `__all__`,
  L43-45 before `_up`) are the canonical pattern of all 8 worker
  files.

## Appendix — line reference

62 lines, as of D-094 (59 at the D-093 bring-in; D-094: +1 pydantic
import line +1 decorator line [T2], 3 ws lines emptied in place
[T4]).

- L28-35: imports (pydantic L32 [T2], state_machine L34,
  rlm_gradient L35)
- L37-38: `RLMContext` under TYPE_CHECKING
- L39-41 + L43-45: the house-style triple blanks [M4]
- L42: `__all__`
- L46-52: `_up` (comment L48, compute L50)
- L54-56: `_down`
- L59-62: the factory (L59 decorator [T2], docstring L61)
