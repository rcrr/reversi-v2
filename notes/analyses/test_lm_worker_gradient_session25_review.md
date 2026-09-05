<!-- ARCHIVED — D-106 step 15 (the docs/ rewrite, 2026-09-04): the
     complete session-25 test-doc (D-093/D-094) moved out of
     docs/src/twolm/test/test_lm_worker_gradient.md per
     docs_rules.md §1/§4/§6. This is a frozen historical record:
     it is never updated. NOTE: the file is UNCHANGED since
     34442b2 (2026-09-01) — 1 class / 2 tests / 142 lines is
     still correct (no step-3 conversion touched it; the D1-D4 +
     D11 pipeline-state pins deleted from the probe are now owned
     by this file — setUp the step-7 pre-state,
     test_generate_gradient the fg-None pre-state + step 8 +
     callable + shapes, test_down_clears_gradient the step pins
     again). The "573 tests / 68 skipped" full-discover figure
     predates steps 3-10. The D-094 T5/T6/T7/T8 campaign
     narrative is frozen history. -->

# twolm/test/test_lm_worker_gradient.py

Analysis date: 2026-09-01 — analysis session 25 (D-093); fix
campaign D-094 approved by Roberto and applied in the same session.
Brought in by Roberto (commit a0adc6e). Probe (scratch/
verify_gradient.py, 61 checks, tiers A–G, re-pinned in D-094 to the
post-campaign state): 0 mismatches.

## Suite status (session 25, post D-094)

- `test_lm_worker_gradient`: 2/0/0 live (1 class / 2 tests; both
  DB-gated since D-094 T5 — the setUp moves through ZED on a fresh
  base dir, so a live DB is required; 2/0/2 under the gate).
- `test_rlm_gradient` (the domain module, D-094 M1): 8/0/0.
- Full discover: 573 tests, 68 skipped under `SKIP_REGAB_DB=1`,
  GREEN; ungated (live DB): 573 run, 17 skipped (PERF only),
  GREEN.

## State per Roberto

GRADIENT fix campaign (D-094) CLOSED: T5 (the SKIP_REGAB_DB gate —
the header L38-39 claim was false at bring-in: under the gate the
test RAN on the live DB; now 2/0/2 gated), T6 (the D-085 idiom),
T7 (the _down test), T8 (4 ws lines) applied. The file now follows
the exact worker-test house pattern (gate FIRST in setUp,
TemporaryDirectory under CUSTOM_TMP_BASE created first,
WORKSPACE_ROOT-anchored json, defensive tearDown).

## Architecture (142 lines, post D-094)

- 1 class: `TestLMWorkerGradient` (L61) — "Tests the GRADIENT
  worker integration and exact values using rlm_02.json."
- setUp (L64-87): the T5 gate (L65-69, `# T5 (D-093):` comment —
  the worker test needs the live regab DB, the setUp moves through
  ZED on a fresh base dir); the stdout patcher (L72-73); the T6
  idiom (L75-79: `TemporaryDirectory` under `CUSTOM_TMP_BASE`
  created FIRST, `self.tmp_dir = Path(self._tmp.name)`, the
  `WORKSPACE_ROOT`-anchored rlm_02.json path); the model (L81-83,
  `Verbosity.LOW`); `move_to_step('ZED')` + step 7 pin (L86-87).
- tearDown (L89-92): defensive (both `getattr` guards — the D-085
  idiom).
- `test_generate_gradient` (L95-126): pre-state pins (fg None,
  X (199952, 8), len(w) 2981); `move_to_step('GRADIENT')` + step 8
  pin; fg not-None + callable; the goldens at w = 0: f
  0.02049378 (rtol 1e-6 / atol 1e-7), g[0] 3.558e-4, g[1] −2.395e-4,
  g[2980] 1.101e-3 (rtol 1e-4 / atol 1e-7) — all re-derived by the
  probe D6/D7 tier.
- `test_down_clears_gradient` (L128-138, NEW in D-094 T7): move to
  GRADIENT (step 8, fg not-None), then `move_to_step(7)` — pins
  step 7 + `current_worker_name == 'ZED'` + `ctx.fg is None`
  (live-verified by the probe D11).

## Verified facts

- All 4 goldens match the independent float64 re-derivation on the
  live rlm_02 dataset (the probe D6/D7: f 0.020493777 float32,
  g re-derived via np.add.at + hand-rolled sigmoid).
- The (199952, 8) / 2981 shape pins match the live pipeline state
  (probe D4): 199952 positions, 8 pattern instances (DIAG3 + EDGE,
  no intercept, no mobilities — probe D12), 2981 w entries.
- The _down clearing is live-verified (probe D11 + the T7 test).

## Minor notes

- The goldens are the BRING-IN values (unchanged by D-094): the R1
  float32 cast of g changes the values by < 1 float32 ulp (≈1e-10
  absolute at these magnitudes) — inside the pinned tolerances.
- The "How to run" header (L30-42) already documented the
  SKIP_REGAB_DB gate at bring-in (L38-39) — the claim was false
  then (T5), true since D-094.

## Appendix — line reference

142 lines, as of D-094 (118 at the D-093 bring-in; D-094: the
setUp T5 gate + T6 idiom, the T7 _down test, 4 ws lines emptied
in place).

- L44-57: imports (os L45 [T5], tempfile L46, paths L57 [T6],
  shutil gone [T6])
- L61: `TestLMWorkerGradient`
- L64-87: setUp (gate L65-69 [T5], patcher L72-73, idiom L75-79
  [T6], model L81-83, ZED L86-87)
- L89-92: defensive tearDown [T6]
- L95-126: `test_generate_gradient` (pre-state L98-102, GRADIENT
  L106-107, goldens L116-126)
- L128-138: `test_down_clears_gradient` [T7]
