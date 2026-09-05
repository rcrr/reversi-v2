<!-- ARCHIVED — D-106 step 14 (the docs/ rewrite, 2026-09-04): the
     complete session-24 analysis (D-091) + the D-092
     fix-campaign narrative moved out of
     docs/src/twolm/lm_worker_zed.md per docs_rules.md §1/§4. This
     is a frozen historical record: it is never updated. Stale-in-
     current-context notes: (1) the probe tier B is now part of the
     51-call probes/verify_zed.py (the 4091e72 move + the D-106
     step-3 class c deletions); (2) the "563 tests / 66 skipped"
     full-discover figure predates steps 3-10 (current: 664/87
     gated); (3) the D-091/D-092 T2/T8 campaign narrative is
     frozen history. -->

# twolm/lm_worker_zed.py

Analysis date: 2026-08-31 — analysis session 24 (D-091); fix
campaign D-092 approved by Roberto ("T1-T8: OK") and applied in the
same session. Brought in by Roberto (commit 439c966 — the 8th
active level of the pipeline).

The ZED worker of the RLM pipeline: the FIRST non-cache worker in
the pipeline — no `cache_manager` wiring at all (no load-or-compute
cycle, no `is_allowed` switch, no rlmwf_07* file). The level is
recomputed on every up-move: the computation is pure vectorized
affine math over `ctx.game_values`, so the on-the-fly choice is
documented in `_up` (L49). The machine contract is unchanged: `_up`
publishes the 4 context attributes, `_down` clears ALL FOUR.

## Suite status (session 24, post D-092)

- `test_lm_worker_zed`: 3/0/0 live (2 classes — 1 DB-free
  `TestZedFunFactory` math test + 2 DB-gated `TestLMWorkerZed`
  worker tests, the gate added in D-092 T1: under
  `SKIP_REGAB_DB=1` the 2 worker tests skip, the factory test runs
  — 3/0/2 gated). The setUp moves through DESIGN_MTR on a fresh
  base dir, so the 2 worker tests need the live DB.
- Full discover: 563 tests, 66 skipped under `SKIP_REGAB_DB=1`,
  GREEN; ungated (live DB): 563 run, 17 skipped, GREEN. The full
  `-W error` discover is clean.

## State per Roberto

Pipeline-in-progress, 8 active levels, enabled by Roberto's
2026-08-31 bring-in (commit 439c966). The next line-by-line step is
`lm_worker_gradient` (the next commented entry). ZED fix campaign
(D-092) CLOSED: T2 (factory `@validate_call` + pydantic import) +
T8 (3 ws lines) fixed here; the worker test T1/T4/T5/T8 fixed; the
domain module T6/T7/T8 fixed; the dedicated `test_rlm_zed.py`
added (T3).

## Architecture (73 lines, post D-092)

- Imports (L28-38): `Worker, Relevance` from state_machine (L34),
  `rlm_zed_compute` from rlm_zed (L35), `validate_call,
  ConfigDict` from pydantic (L32 — added in D-092 T2),
  `RLMContext` under TYPE_CHECKING (L37-38). NO
  `twolm.cache_manager` import (by design).
- `_up` (L46-59): `log_event(INFO, "Computing Zed array (Z) and
  transformations...")`; the by-design comment (L49: "ZED
  computation is very fast (vectorized math), so we compute it on
  the fly without disk caching."); `zed_obj = rlm_zed_compute
  (ctx)` (L50); `zed_checksum = zed_obj.compute_sha3_256_hash()`
  (L51); publishes `ctx.y2z / ctx.z2y / ctx.z / ctx.zed_checksum`
  (L53-56); logs the shape (L58) and the checksum (L59).
- `_down` (L62-67): `log_event(INFO, "Clearing Zed attributes...")`
  then clears ALL FOUR attributes to None (L64-67) — the house
  shape; no gap at bring-in (pinned live by probe D12 and by
  test_down_clears_zed_attributes, D-092 T5).
- `lm_worker_zed()` (L70-73): the factory — `@validate_call
  (config=ConfigDict(arbitrary_types_allowed=True))` since D-092
  T2 (the house convention of the other 6 workers) — returns
  `Worker("ZED", _up, _down)` (L73).

## Verified facts (D-091/D-092 probe — 60 checks, 0 mismatches)

- V1 (B-tier): structure — 73 lines; `__all__ =
  ['lm_worker_zed']` (L42); the factory WITH `@validate_call` +
  the pydantic import (D-092 T2); NO cache_manager import (the
  L49 by-design comment pinned); `_up` sets the 4 ctx attributes
  (L53-56); `_down` clears all four (L64-67); `Worker("ZED", ...)`
  (L73); 0 non-comment trailing-whitespace lines (D-092 T8).
- V2 (D-tier, live DB, rlm_01): the full pipeline through ZED —
  the pre-state (all 4 ctx attrs None), step 7 + worker name
  "ZED", the golden y/z content (see the rlm_zed doc V3), the
  checksum identity, the endpoints + round-trip of the published
  closures, EXACTLY the 5 flat files + 5 sidecars in the base dir
  (no rlmwf_07*), and the `_down` clearing (back at step 6, all 4
  attrs None again).

## Minor notes

- **M2 (informational, D-091):** the flat-file numbering skips 07
  (FEATURES skipped 03): the next cache level (GRADIENT) takes
  rlmwf_08.
- The no-cache design is the first deviation from the uniform
  7-kwargs `cache_manager` wiring of the 4 cache-consuming levels
  (POSITIONS, INDEXES, WMAPS, DESIGN_MTR) — intentional and
  documented (the L49 comment); the 4 ctx attributes are still
  cleared on down (the machine contract holds, probe D12).

## Integration notes

- Pipeline ordering: `ctx.game_values` (POSITIONS) + `ctx.cfg.
  stat_model.logit_clipping` (CONFIG) must be set — the SM
  half-open interval semantics guarantee every up-move to step 7
  passes through both. The worker's setUp test moves through
  DESIGN_MTR (step 6) first, so the full 8-level chain is exercised
  end-to-end on the live DB.
- Downstream: GRADIENT (the next commented level) will consume
  `ctx.z` + `ctx.y2z` + `ctx.z2y` + `ctx.zed_checksum`.
- No `use_cache` interaction: with `ctx.use_cache=False` (the
  CONFIG switch) the other levels still warm their cache files;
  ZED has nothing to warm — the behavior is identical either way.

## Appendix — line reference

73 lines, as of D-092 (70 at D-091 bring-in; D-092: +1 pydantic
import +1 blank line [T2], +1 decorator line [T2], 3 ws lines
emptied in place [T8]).

- L28-38: imports (pydantic L32 [T2], state_machine L34, rlm_zed
  L35, TYPE_CHECKING L37-38)
- L42: `__all__`
- L46-59: `_up` (L49 by-design comment, L50 compute, L51 checksum,
  L53-56 the 4 ctx publishes, L58-59 the 2 logs)
- L62-67: `_down` (L64-67 the 4 None clears)
- L70-73: `lm_worker_zed` (L70 decorator [T2], L73 the Worker)
