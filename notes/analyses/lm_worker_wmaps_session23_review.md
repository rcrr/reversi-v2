<!-- ARCHIVED — D-106 step 12 (the docs/ rewrite, 2026-09-04): the
     complete session-23 analysis (D-086) + the D-087
     fix-campaign narrative moved out of
     docs/src/twolm/lm_worker_wmaps.md per docs_rules.md
     §1/§4. This is a frozen historical record: it is never
     updated. Stale-in-current-context notes: (1) the probe tier B
     is now part of the 53-call probes/verify_wmaps.py (the
     4091e72 move + the D-106 step-3 class c deletions); (2) the
     "535 tests / 61 skipped" full-discover figure predates steps
     3-10; (3) the T6-T9 campaign narrative is frozen history. -->

# twolm/lm_worker_wmaps.py

Analysis date: 2026-08-31 — analysis session 23 (D-086); fix
campaign D-087 approved by Roberto ("Procedi su tutto") and applied
in the same session. Brought in by Roberto together with rlm_wmaps
in 73b4342 (2026-08-31, the 6th active level of the pipeline — the
import + worker-list entry in logistic_model.py were the only 2
lines the commit touched there). Probe (scratch/verify_wmaps.py,
tier B, re-pinned in D-087 to the post-campaign state): 0
mismatches.

The WMAPS worker of the RLM pipeline — the 6th active level
(CREATED sentinel → CONFIG → POSITIONS → FEATURES → INDEXES →
WMAPS). Like POSITIONS and INDEXES it is a CACHE-CONSUMING level:
the 4-step load-or-compute over the rlm_wmaps object (the flat
`rlmwf_05_WMAPS.dat` + binio-format sidecar + the duck-typed data
checksum), the THIRD cache_manager consumer in the pipeline after
POSITIONS (D-079) and INDEXES (D-083) — the flat cache files DO
materialize (probe V4).

## Suite status (session 23, post D-087)

- `test_lm_worker_wmaps`: 3/0/0 (2 classes — the end-to-end cache
  round-trip pin (first run DB hit through INDEXES + flat files +
  "Executing heavy computation"; second instance on the same base
  dir: "Cache successfully loaded and validated", no heavy
  computation) + the rlm_01 golden-content pin (all 6 arrays vs
  the literals). The setUp moves through INDEXES on a fresh base
  dir, so a live DB is required; DB-gated since D-087 T1, as in
  the other worker test files).
- Full discover: 535 tests, 61 skipped under `SKIP_REGAB_DB=1`
  (17 PERF + 35 regab + 2 positions + 2 features + 2 indexes + 3
  wmaps), GREEN; ungated (live DB): 535 run, 17 skipped (PERF
  only), GREEN.

## State per Roberto

Pipeline-in-progress, 6 active levels, enabled line-by-line by
Roberto in 73b4342. WMAPS worker fix campaign (D-087) CLOSED:
T6-T8 fixed. The next line-by-line step is
`lm_worker_design_matrix` (the next commented entry,
logistic_model.py L46).

## Architecture (91 lines, post D-087)

- `lm_worker_wmaps() -> Worker` (L88-91): factory returning
  `Worker("WMAPS", _up, _down)`; `@validate_call
  (config=ConfigDict(arbitrary_types_allowed=True))` since D-087
  T6 (the D-080 M1 / D-082 M1 / D-084 M1 pattern applied to the
  other five workers).
- `_up(ctx)` (L50-75): INFO "Computing weight maps (WMAPS) for the
  feature set..." → `cache_manager_load_or_compute` with the full
  7-kwargs wiring: `cache_path =
  ctx.get_cache_file_full_path_for_current_level()` (the injected
  D-078 machine-level closure — flat `rlmwf_05_WMAPS.dat`),
  `is_allowed = ctx.use_cache` (the CONFIG switch, the D-071 R1
  semantics), `load_fn = lambda path: rlm_wmaps_load_from_file
  (path, checksum=False)` (D-087 T7 — the house shape as in the
  other cache workers post D-080 M4 / D-084 M3: the `checksum=True`
  default would re-verify the sidecar cache_manager already checked
  in step 2), `store_fn = rlm_wmaps_store_to_file`,
  `validate_fn = lambda cached_wmaps: rlm_wmaps_is_cache_consistent
  (ctx, cached_wmaps)` (the 2-field metadata compare),
  `compute_fn = lambda: rlm_wmaps_compute(ctx)`,
  `logger_fn = ctx.log_event`. Then: the 6 separate context
  attributes are populated (feature_w_ranges, iwmap_feature_offset,
  iwmap, wmap, wmap_fallback, w) with the INFO
  "Model attributes ... have been set." + the INFO
  "WMAPS computed/loaded. Total weights (W): ..." → the INFO
  "Wmaps object checksum (wmaps_obj_checksum): ..." →
  `ctx.wmaps_obj_checksum = wmaps_obj_checksum` (the 7th attribute,
  the DATA checksum — the cache_manager 3rd return element).
- `_down(ctx)` (L77-86): INFO "Clearing WMAPS and W attributes..."
  → all 7 attributes to None — the 6 arrays AND
  `ctx.wmaps_obj_checksum` (D-087 T8, the house shape as in
  lm_worker_indexes._down: object + checksum).

## Verified facts (D-087 probe — 0 mismatches)

- V1 (B1-B3): 91 lines; `__all__ = ['lm_worker_wmaps']`; the
  factory WITH `@validate_call` + the pydantic import (T6).
- V2 (B4): the full 7-kwargs cache wiring with the
  `load_fn = lambda path: rlm_wmaps_load_from_file(path,
  checksum=False)` shape (T7).
- V3 (B5-B6): `_up` sets the 6 ctx arrays + `wmaps_obj_checksum`
  (the 7 attributes); `_down` clears all 7 (T8).
- V4 (live DB, cross-run): after `move_to_step("WMAPS")` — step 5,
  worker "WMAPS"; the base dir holds ONLY the flat
  `rlmwf_01_CONFIG.dat` + `.SHA3-256`, `rlmwf_02_POSITIONS.dat` +
  `.SHA3-256`, `rlmwf_04_INDEXES.dat` + `.SHA3-256`,
  `rlmwf_05_WMAPS.dat` + `.SHA3-256` (no `rlmwf_03_FEATURES*` —
  the pure-compute level writes nothing). A second instance on the
  same base_dir: "Cache successfully loaded and validated", no
  "Executing heavy computation".
- V5 (E0-E9, live DB): the golden content (see
  rlm_wmaps.md V3) — the 21-weight layout of rlm_01.json.

## Minor notes — RESOLVED (D-087)

- **T6 FIXED**: `@validate_call
  (config=ConfigDict(arbitrary_types_allowed=True))` on the public
  factory (L88) + the `from pydantic import validate_call,
  ConfigDict` import (L32) — the house convention, the same fix as
  D-080 M1 (lm_worker_positions) / D-082 M1 (lm_worker_features) /
  D-084 M1 (lm_worker_indexes).
- **T7 FIXED**: `load_fn = lambda path:
  rlm_wmaps_load_from_file(path, checksum=False)` (L56) — the
  redundant sidecar re-verification is gone (cache_manager
  verifies in step 2; the raw function would verify again in
  step 3), the same shape as the D-080 M4 / D-084 M3 fixes.
- **T8 FIXED**: `_down` now clears `ctx.wmaps_obj_checksum`
  (L85) as well — the house shape clears object + checksum.
- **T9 FIXED**: the 4 non-comment trailing-whitespace lines
  stripped; scope as in D-078 M3: the license-header `# ` lines
  stay.

## Integration notes

- Pipeline ordering: `ctx.rlm_indexes_checksum` (INDEXES) +
  `ctx.cfg.stat_model.frequency_cut_off` (CONFIG) + the pindexes
  layout (POSITIONS/FEATURES) must all be set before `compute`
  runs — the SM half-open interval semantics guarantee every
  up-move to step 5 passes through all of them.
- The worker carries NO naming code — the flat
  `rlmwf_05_WMAPS.dat` comes from the injected full-path closure
  (the D-078 machine-level fix for ALL cache-consuming workers).
- `is_allowed = ctx.use_cache`: with `use_cache=False` the level
  always recomputes but still warms the cache file (the D-071 R1
  pattern).
- `validate_fn` is the 2-field metadata compare (no DB access, no
  recompute) — a business mismatch deletes + recomputes (the
  D-071 R2 pattern).
- The worker stores 7 blackboard fields (6 arrays + the checksum),
  the only worker of the pipeline with more than one data object
  spread across separate context attributes (as in INDEXES: object
  + checksum — here 6 objects + checksum).

## Appendix — line reference

91 lines, as of D-087 (87 at 73b4342 arrival).

- L28-39: imports (pydantic L32 [T6], state_machine L34,
  rlm_wmaps L35-38, cache_manager L39, TYPE_CHECKING RLMContext
  L41-42)
- L46: `__all__`
- L50-75: `_up` (cache wiring L53-61, T7 at L56, the 6-attribute
  population L63-71, the checksum L73-74)
- L77-86: `_down` (T8 at L85)
- L88-91: `lm_worker_wmaps()` (T6: `@validate_call` at L88)
