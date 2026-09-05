<!-- ARCHIVED — D-106 step 12 (the docs/ rewrite, 2026-09-04): the
     complete session-23 test-doc (D-086/D-087) moved out of
     docs/src/twolm/test/test_lm_worker_wmaps.md per
     docs_rules.md §1/§4/§6. This is a frozen historical record:
     it is never updated. NOTE: the file is UNCHANGED since D-087
     (ded27eb, 2026-08-31) — 2 classes / 3 tests / 315 lines is
     still correct (no step-3 conversion touched it; the E0-E9
     golden-content re-derivation that was probe-tier is now
     owned by TestLMWorkerWmapsExactValues). The "535 tests /
     61 skipped" full-discover figure predates steps 3-10. The
     T1 + T9 campaign narrative is frozen history. -->

# twolm/test/test_lm_worker_wmaps.py

Analysis date: 2026-08-31 — analysis session 23 (D-086); fix
campaign D-087 approved by Roberto ("Procedi su tutto") and applied
in the same session.

Roberto's file, brought in with the WMAPS enablement (73b4342, the
line-by-line pipeline step 6). 2 classes / 3 tests / no PERF /
ALL DB-DEPENDENT (the setUp moves through INDEXES, which runs
POSITIONS on a fresh base dir). Green on first run. The D-085
paths idiom was applied per Roberto's instruction in D-086,
before the analysis campaign (both classes: the CWD mkdtemp →
TemporaryDirectory under the shared CUSTOM_TMP_BASE, the 2 CWD
json_config lines → WORKSPACE_ROOT-anchored, defensive tearDowns,
the dead shutil import removed). T1 + T9 all resolved in D-087.

## Suite status (session 23, post D-087)

- `test_lm_worker_wmaps`: 3/0/0 (live DB; 3/0/3 under
  `SKIP_REGAB_DB=1` since D-087 T1)
- Full discover: 535 tests, 61 skipped under `SKIP_REGAB_DB=1`
  (17 PERF + 35 regab + 2 positions + 2 features + 2 indexes + 3
  wmaps), GREEN; ungated (live DB): 535 run, 17 skipped (PERF
  only), GREEN.

## Coverage

- `TestLMWorkerWmaps` (2 tests, L61-159; stdout patched to a
  StringIO, the house worker-test pattern; base dir under
  CUSTOM_TMP_BASE, rlm_00.json from WORKSPACE_ROOT):
  - `test_compute_and_populate_cache` (L104-127): first run —
    `move_to_step("WMAPS")` (step 5); the base dir holds the flat
    `rlmwf_05_WMAPS.dat` + `.SHA3-256` (the D-078 naming pinned);
    "Forcing computation" in the logs (the cache_manager
    first-run string); all 6 ctx arrays non-None + `len(ctx.w) >
    0`; `verbosity=Verbosity.HIGH` (the house pattern as in the
    other worker tests).
  - `test_read_cache_on_new_instance` (L129-159): the second
    instance on the SAME base dir moves to "INDEXES" first
    (the 5-worker list is exercised: CONFIG → POSITIONS →
    FEATURES → INDEXES), then the WMAPS level HITS the cache:
    "Cache successfully loaded and validated" in the logs,
    "Forcing computation" NOT in the logs (no recompute), the
    wmaps data IDENTICAL to the first run.
- `TestLMWorkerWmapsExactValues` (1 test, L163-314; rlm_01.json
  from WORKSPACE_ROOT, cut_off=2):
  - `test_compute_wmaps_exact_values` (L201-314): the GOLDEN
    CONTENT pin — before WMAPS: all 6 ctx arrays are None (the
    half-open interval guarantee); after:
    `expected_fwr` (4,3) = [[−1,0,0],[1,1,4],[5,5,15],[16,16,20]]
    int64 (per-feature [fallback, w_min, w_max]);
    `expected_iwmap_feature_offset` = [0,1,66,93,174] uint32
    (F+1 cumulative); `expected_iwmap` (174,) int64 (mostly −1 —
    the unseen configurations); `expected_wmap` (21,3);
    `expected_wf` (10,3) all freq 1 (f1: 6,11,15; f2: 3,5,10,11,
    20,23; f3: 40); `w` = 21 float32 zeros. Every literal was
    independently re-derived by the D-086 probe (tier E0-E9,
    pipeline run vs the literals extracted from the test source —
    the single source of truth, 0 mismatches).

The suite is the end-to-end cache round-trip pin (both directions,
the D-078 file names) + the golden content pin (all 6 arrays), as
in the other worker test files.

## Defects — RESOLVED (D-087)

- **T1 FIXED (F2)**: the missing `SKIP_REGAB_DB` gate — both
  setUps now start with the gate (the D-080 T2 / D-084 T2 class;
  `import os` added L45). The header had been claiming the gate
  ("SKIP_REGAB_DB=1 skips the DB-gated tests") that did not exist
  in the code — the 3 tests would have ERRORED (not skipped) in a
  no-DB environment. Now the claim is true: 3/0/3 under the gate.
- **T9 FIXED (F9)**: the 20 non-comment trailing-whitespace lines
  stripped; scope as in D-078 M3: the license-header `# ` lines
  stay.

## Verdict

A complete worker-level pin post D-087 (the round-trip in both
directions + the full golden content); the gate now matches the
header (as in the other worker test files); the D-085 idiom keeps
all temp material under the shared CUSTOM_TMP_BASE.
