# reversi/lm/wrk_zed.py
The ZED worker of the LM pipeline — the 8th active level and the
FIRST non-cache worker in the pipeline: no `cache_manager` wiring
at all (no load-or-compute cycle, no `is_allowed` switch, no
rlmwf_07* file). The level is recomputed on every up-move: the
computation is pure vectorized affine math over `ctx.game_values`,
so the on-the-fly choice is documented in `_up` (L49). The
machine contract is unchanged: `_up` publishes the 4 context
attributes, `_down` clears ALL FOUR.
> State: D-092 · 17a5f95 · 2026-09-01 · suite 3/0/0 (2 DB-gated)

## API

| name | contract |
|---|---|
| `wrk_zed()` | the factory — `@validate_call(config=ConfigDict(arbitrary_types_allowed=True))` (the D-092 T2 house-convention fix) returning `Worker("ZED", _up, _down)` |

## Architecture

- Imports: `Worker, Relevance` from state_machine; `hlp_zed_compute`
  from hlp_zed; `validate_call, ConfigDict` from pydantic (added
  in D-092 T2); `LMContext` under TYPE_CHECKING. NO
  `reversi.tools.cache_manager` import (by design — pinned by probe B).
- `_up`: INFO "Computing Zed array (Z) and transformations..." →
  the by-design comment (L49: "ZED computation is very fast
  (vectorized math), so we compute it on the fly without disk
  caching.") → `zed_obj = hlp_zed_compute(ctx)` →
  `zed_checksum = zed_obj.compute_sha3_256_hash()` → publishes
  `ctx.y2z / ctx.z2y / ctx.z / ctx.zed_checksum` → the 2 INFO
  lines (the shape + the checksum).
- `_down`: INFO "Clearing Zed attributes..." → ALL FOUR
  attributes to None (the house shape; no gap at bring-in —
  pinned by `test_down_clears_zed_attributes`, D-092 T5 — the
  probe D12 live check moved to that test at step 3).

## Verified invariants

Pinned by the `probes/verify_zed.py` B + C + D + F + G tiers +
the 3-test suite.

- Source shape (probe B1-B8): the 73-line file, `__all__ =
  ['wrk_zed']`, the factory WITH `@validate_call` + the
  pydantic import (T2), NO cache_manager import (the L49
  by-design comment pinned), `_up` sets the 4 ctx attributes,
  `_down` clears all four, `Worker("ZED", ...)` (L73), 0
  non-comment trailing-whitespace lines (T8).
- The worker-test source shape (probe C1-C10): the 164-line
  file, the 2 classes, the 3 tests, the gate + the now-true
  header claim (T1), the D-085 idiom (T4), no dead imports
  (`Path` load-bearing), the step pins, the goldens, the _down
  test (T5), 0 non-comment ws lines (T8).
- The full pipeline through ZED (live DB, probe D1/D5-D11,
  rlm_01): the pre-state (all 4 ctx attrs None), step 7 + worker
  name "ZED", the golden y/z content (the hlp_zed doc), the
  checksum identity, the endpoints + round-trip of the published
  closures, EXACTLY the 5 flat files + 5 sidecars in the base
  dir (no rlmwf_07*).
- The dedicated suite (probe F4/F5 + G1-G10): the 157-line file,
  3 classes / 10 tests, no DB wiring, the goldens pinned, the
  hash golden `3d49fd5d...`, the 4 D-007 mirror docs exist.
- The end-to-end golden (DB-gated): `test_compute_zed` (the
  (10,) y int8 + z float32 literals, the step-7 pin, the
  pre-state pins) + `test_down_clears_zed_attributes` —
  `test_wrk_zed.py` (3 tests, 2 DB-gated since D-092 T1).

## Open issues

None.

## Conventions

- The no-cache design is the first deviation from the uniform
  7-kwargs `cache_manager` wiring of the 4 cache-consuming levels
  (POSITIONS, INDEXES, WMAPS, DESIGN_MTR) — intentional and
  documented (the L49 comment); the 4 ctx attributes are still
  cleared on down (the machine contract holds).
- No `use_cache` interaction: with `ctx.use_cache=False` (the
  CONFIG switch) the other levels still warm their cache files;
  ZED has nothing to warm — the behavior is identical either
  way.

## Integration

- The 8th LM level; the domain module (hlp_zed.py) carries the
  data object + the math, this worker the machine glue.
- Consumes `ctx.game_values` (POSITIONS) + `ctx.cfg.stat_model.
  logit_clipping` (CONFIG) — the SM half-open interval semantics
  guarantee both are set. The worker-test setUp moves through
  DESIGN_MTR (step 6) first, so the full 8-level chain is
  exercised end-to-end on the live DB.
- Publishes `ctx.z / ctx.y2z / ctx.z2y / ctx.zed_checksum` for
  the GRADIENT level onward.
