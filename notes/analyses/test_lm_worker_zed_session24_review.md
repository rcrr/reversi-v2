<!-- ARCHIVED — D-106 step 14 (the docs/ rewrite, 2026-09-04): the
     complete session-24 test-doc (D-091/D-092) moved out of
     docs/src/twolm/test/test_lm_worker_zed.md per
     docs_rules.md §1/§4/§6. This is a frozen historical record: it
     is never updated. NOTE: the file is UNCHANGED since 17a5f95
     (2026-09-01) — 2 classes / 3 tests / 164 lines is still
     correct (no step-3 conversion touched it; the D2-D4 + D12
     golden pins deleted from the probe are now owned by this
     file). The "563 tests / 66 skipped" full-discover figure
     predates steps 3-10. The D-092 T1/T4/T5/T8 campaign narrative
     is frozen history. -->

# twolm/test/test_lm_worker_zed.py

Analysis date: 2026-08-31 — analysis session 24 (D-091); fix
campaign D-092 approved by Roberto ("T1-T8: OK") and applied in the
same session. Brought in by Roberto (commit 439c966).

The worker integration test of the 8th pipeline level (ZED): the
isolated factory math + the rlm_01.json end-to-end golden (the y /
z literals, re-derived independently by the probe D tier) + the
_down clearing pin (D-092 T5).

## Suite status (session 24, post D-092)

- `test_lm_worker_zed`: 3/0/0 live — `TestZedFunFactory` (1 test,
  no DB) + `TestLMWorkerZed` (2 tests, both DB-gated since D-092
  T1 — the setUp moves through DESIGN_MTR on a fresh base dir, so a
  live DB is required): 3/0/2 under `SKIP_REGAB_DB=1` (the 2 worker
  tests skip, the factory test runs — the header claim now true).
- Full discover: 563 tests, 66 skipped under the gate, GREEN;
  ungated: 563 run, 17 skipped (PERF only), GREEN; the full
  `-W error` discover clean; build/tmp clean.

## State per Roberto

Part of the 2026-08-31 ZED bring-in (commit 439c966). ZED fix
campaign (D-092) CLOSED: T1 (the SKIP_REGAB_DB gate in the worker
setUp — the header L38-39 claim was FALSE pre-fix: under the gate
the 2 tests RAN on the live DB), T4 (the D-085 idiom:
TemporaryDirectory under CUSTOM_TMP_BASE created FIRST +
WORKSPACE_ROOT-anchored json + the defensive tearDown + the dead
`shutil` import gone, `Path` now load-bearing via
`Path(self._tmp.name)`), T5 (the `test_down_clears_zed_attributes`
added), T8 (7 ws lines) fixed.

## Architecture (164 lines, post D-092)

- Imports (L44-58): `unittest` + `os` (L44-45, the gate, D-092
  T1) + `tempfile` (L46); numpy + numpy.testing (L48-49);
  patch/StringIO/Path (L51-53); the twolm block — `Verbosity`,
  `LogisticModel`, `zed_fun_factory` (L55-57) +
  `WORKSPACE_ROOT, CUSTOM_TMP_BASE` from `twolm.test.paths`
  (L58, D-092 T4). No `shutil` (dead since the idiom).
- `TestZedFunFactory` (L62-76, 1 test, no DB): `test_zed_fun_factory`
  (L65) — alpha 0.02, `[-64, 0, 6, +64]` int8 →
  `[0.02, 0.5, 0.545, 0.98]` float32 (allclose 1e-6/1e-7) + the
  round-trip `z2y(y2z(y)) == float32(y)`.
- `TestLMWorkerZed` (L78-160, 2 tests, DB-gated): setUp (L81-104) —
  the gate FIRST (L82-86, D-092 T1), the stdout patcher (L88-90),
  the D-085 idiom (L92-96, D-092 T4: TemporaryDirectory created
  FIRST under CUSTOM_TMP_BASE, `tmp_dir = Path(self._tmp.name)`,
  the WORKSPACE_ROOT-anchored `rlm_01.json`), the LogisticModel on
  a fresh base dir (L98-100), the move to DESIGN_MTR + the step-6
  pin (L103-104). Defensive tearDown (L106-110).
  - `test_compute_zed` (L112-147): the pre-state (y2z/z None,
    L113-114); `logit_clipping == 0.03` pinned (L116-118);
    `expected_y = [10, 36, −22, 18, −16, 14, −22, 20, 0, 2]`
    int8 (L120-124); move to ZED + the step-7 pin (L126-127); the
    published attrs non-None (L129-130); `z` is an ndarray (L132);
    dtype float32 + shape (10,) (L133-134); `expected_z` (10,)
    float32 literal (L136-145); `assert_array_equal` (L147).
  - `test_down_clears_zed_attributes` (L149-160, D-092 T5): move to
    ZED (L151-152) then `move_to_step(6)` (L154); pins step 6 +
    worker name "DESIGN_MTR" (L155-156) + all 4 ctx attrs None
    (L157-160).

## Verified facts (D-091/D-092 probe — 60 checks, 0 mismatches)

- V1 (C-tier): structure — 164 lines; the 2 classes (L62/L78); the
  3 tests; the gate (L85) + the header claim (L38-39, now true);
  the D-085 idiom (L94-96); no dead imports (no `shutil`; `Path`
  load-bearing, 1 use); the step pins (L103-104, L126-127); the
  goldens (L116, L120, L136-145); the _down test (L149-160); 0
  non-comment trailing-whitespace lines (D-092 T8).
- V2 (D-tier, live DB, rlm_01): the golden content re-derived
  independently (see the rlm_zed doc V3) — the test's y/z literals
  are the single source of truth for the pipeline output (clipping
  0.03; z == the literal == the float32-exact recompute).

## Integration notes

- The 2 worker tests are DB-gated (D-092 T1) because the setUp's
  move to DESIGN_MTR runs the positions chain (the live regab DB)
  on a fresh base dir — the same gate class as
  test_lm_worker_design_matrix (D-090 T1). The factory test is NOT
  gated (no DB).
- No cache round-trip test exists (and none can): ZED has no cache
  file (the first non-cache level) — the end-to-end coverage is the
  single compute + the _down pin.
- The rlm_01.json fixture is reused (the same (10,) training set as
  the DESIGN_MTR golden — the pipeline grows, the positions don't).

## Appendix — line reference

164 lines, as of D-092 (138 at D-091 bring-in; D-092: +1 `import
os`, +1 paths import, the setUp reworked (+10: gate + idiom +
comments), the defensive tearDown (+2), the _down test (+13), 5 ws
lines emptied in place [T8]).

- L44-58: imports (os L45 [T1], paths L58 [T4])
- L62-76: `TestZedFunFactory` (1 test)
- L78-160: `TestLMWorkerZed` (setUp L81-104 — gate L82-86 [T1],
  idiom L92-96 [T4]; tearDown L106-110 [T4]; test_compute_zed
  L112-147; test_down_clears_zed_attributes L149-160 [T5])
- L163-164: the `__main__` guard
