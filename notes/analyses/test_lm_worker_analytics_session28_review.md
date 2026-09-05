<!-- ARCHIVED — D-106 step 20 (the docs/ rewrite, 2026-09-04):
     the complete D-103 T5 session-28 narrative + the D-105/M2
     re-pin moved out of
     docs/src/twolm/test/test_lm_worker_analytics.md per
     docs_rules.md §1/§4. This is a frozen historical record:
     it is never updated. Stale-in-current-context notes: (1)
     the "41 checks" probe figure — see the sibling
     rlm_analytics_session28_review.md header (C4b/C6 were
     deleted at D-106 step 3 class c because this file pins
     them); (2) the "631 tests / 87 skipped" full-discover
     figure predates steps 3-19 (current: 664/87 gated); (3)
     the D-103/D-105 campaign narrative (T5 the file added, T6
     the rlm_01 detailed_report += LMC, the D-105/M2 re-pin of
     the dense dicts + the 3-metric header lines + the two
     file-report hashes + the rlm_01 gap 27.22 → 23.87) is
     frozen history. -->

# twolm/test/test_lm_worker_analytics.py

Analysis date: 2026-09-02 — analysis session 28 (D-103, the
ANALYTICS bring-in + fix campaign). New file added by the D-103
campaign (T5, Roberto-approved: "T5: OK. Procedi!"), the dedicated
suite for the ANALYTICS level — the first suite to cover TWO
non-cache levels' downstream data (the 5th non-cache level itself +
the rlm_01 mobility-table branch of the file report). D-105 (M2,
session 29): re-pinned for the 3-metric header — the dense-metrics
pins, the new header lines (Loss row, Population line, Substitution
Delta row), the new INFO log line, the two file-report hashes, and
the rlm_01 gap 27.22 → 23.87 (the gap is now dense-vs-dense).

## How to run

Run from the workspace root (the directory containing `.venv` and
`src`):

- With the live regab DB:
  `time python3 -m unittest twolm.test.test_lm_worker_analytics`
- Gated (no DB): `SKIP_REGAB_DB=1 python3 -m unittest
  twolm.test.test_lm_worker_analytics` — all 4 tests skip
  (4/0/4).

Suite status (session 29, post D-105): 4/0/0 live (7.7 s);
full discover 631 tests, 87 skipped under `SKIP_REGAB_DB=1`,
GREEN (3.2 s); ungated 631 run, 18 skipped, GREEN (46.8 s); the
module-level `-W error` run is clean (8.0 s).

## Architecture (338 lines, post D-105)

Module-level: the GPL header (L1-27, Roberto's, as in all test
files), the run instructions (L29-41), imports (L43-55 —
`hashlib`/`re` for the masked hash, `unittest.mock.patch` +
`StringIO` for the log capture, `LogisticModel`, the D-085
`WORKSPACE_ROOT`/`CUSTOM_TMP_BASE` paths), and the
`_masked_report_hash(text)` helper (L58-65): the file report
embeds `datetime.now()` (the Creation Date line), so the golden is
the sha3_256 of the text with the date regex-masked to "DATE" —
every other byte is deterministic.

`TestLMWorkerAnalytics` (L68-241) — the rlm_02 integration class.
`setUp` (L77-100): the SKIP_REGAB_DB gate first (D-085 idiom — the
setUp moves through the whole 13-level chain to VALIDATE on a fresh
base dir, so the live regab DB is required); the stdout patcher;
`TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))` created FIRST (a
mid-setup failure still leaves a cleanable temp dir); the
`WORKSPACE_ROOT`-anchored rlm_02.json; `LogisticModel(config,
verbosity=HIGH, base_dir_override=tmp)`; `move_to_step('VALIDATE')`
→ step 12 asserted. `tearDown` (L102-106): defensive
`getattr`-guarded patcher stop + tmp cleanup.

- `test_analytics_report_goldens` (L108-184): pre-state pins
  (`analytics_report` + `train_metrics` + `train_dense_metrics`
  all None — the fields exist pre-declared on RLMContext since
  D-103 M1 / D-105 M2 but unset);
  `move_to_step('ANALYTICS')` → step 13 / worker "ANALYTICS"; the
  7-key dict pinned EXACTLY (rlm_02, bid [6,7], 199952 samples:
  train_mae_y 12.346794566613694, train_rmse_y
  15.58872172931622, train_loss 0.00712497066706419 —
  `opt_info['f']`, train_samples 199952, pop_mae_y
  21.729816221648974, pop_rmse_y 26.40637507956623, pop_loss
  0.020437248051166534) + the 4-key dense dict pinned EXACTLY
  (D-105/M2 — rlm_02 cut 1, so the dense values equal the
  compressed ones up to the f32 `w_dense` rounding:
  train_dense_mae_y 12.346794548249868, train_dense_rmse_y
  15.58872171282352, train_dense_loss 0.00712234852835536,
  train_dense_samples 199952); the console report: title line
  (the model name from the fixture), "Total Parameters (W) :
  2,981", "Dense Parameters (K) : 6,588", the 3 data rows — "Loss
  (MSE/2)    | 7.1250e-03     | 7.1223e-03     | 7.0079e-03"
  (D-105/M2), the Population line "Population (baseline)  : RMSE
  26.41  MAE 21.73  Loss 2.0437e-02", "Generalization Gap (RMSE)
  : -0.13", "Substitution Delta (RMSE)   : -0.00" (D-105/M2 —
  cut 1: f32 rounding, not substitution), NO "Creation Date", NO
  "PATTERN FEATURE" (header-only); the file report: exists at
  `base_dir/model_analytics_report.txt`, has the Creation Date +
  the empty MOBILITY section (rlm_02 has no mobility features),
  the EDGE (fid=0) + DIAG3 (fid=1) pattern headers, exactly ONE
  "(Table rows omitted" line (DIAG3 — not in the fixture's
  `detailed_report`; EDGE is), and the date-masked sha3_256 golden
  `94a4af7e5ca554e6f8b219cf5ed820e45e102489dacdc25e15d2b263158120b0`
  (D-105/M2 re-pin — the 3-metric header); the captured logs:
  "Generating model analytics report...", "Computing metrics on the
  training set...", "Computing dense-pass metrics on the training
  set..." (D-105/M2), "Analytics report saved to ", and NO
  "PATTERN FEATURE" (the tables go to the file, not the logs).
- `test_second_instance_deterministic` (L186-223): a second
  `LogisticModel` on the SAME base dir moved to ANALYTICS: exactly 6
  "Cache successfully loaded and validated" hits (the 6 cache_manager
  levels — POSITIONS, INDEXES, WMAPS, DESIGN_MTR, GENERATE,
  VLD_POSITIONS; CONFIG + the OPTIMIZE checkpoint have their own
  load flows; FEATURES/ZED/GRADIENT/VALIDATE/ANALYTICS recompute),
  no "Extracted" (no DB query), no "established successfully" (no
  DB connection); the recomputed `train_metrics` dict, the
  `train_dense_metrics` dict (D-105/M2) and the
  `analytics_report` string are IDENTICAL to the first instance
  (the no-cache determinism pin).
- `test_down_clears_analytics_attributes` (L225-241): back to
  VALIDATE (step 12) clears ALL THREE blackboard fields to None
  (D-105/M2 added `train_dense_metrics`) while the report file
  REMAINS on disk (the artifact semantics — `_down` does not
  unlink, like the OPTIMIZE checkpoint).

`TestLMWorkerAnalyticsMobility` (L244-334) — the rlm_01
mobility-table class. Same setUp idiom on rlm_01.json (the
intercept + LMC mobility + DIAG3 + CORE patterns;
`analytics.detailed_report = ["DIAG3", "LMC"]` post D-103 T6 — the
ONLY fixture that exercises the mobility table helper end-to-end).

- `test_mobility_and_pattern_tables` (L285-334): first run to
  ANALYTICS; the rlm_01 7-metric goldens (bid [7], 10 samples:
  train_mae_y 9.874833279184258e-05, train_rmse_y
  0.00013206900478667877, train_loss 4.704681197571781e-13 — the
  10-sample model converges to interpolation, train_samples 10,
  pop_mae_y 15.6, pop_rmse_y 18.39565166010707, pop_loss
  0.009125067852437496) + the 4-key dense dict pinned EXACTLY
  (D-105/M2 — rlm_01 cut 2, 5 of the 10 training positions touch
  IC configs: train_dense_mae_y 1.854193878173828,
  train_dense_rmse_y 3.3556084739848866, train_dense_loss
  0.0003036324051208794, train_dense_samples 10); the file report:
  "MOBILITY FEATURE: LMC (fid=1)", "PATTERN FEATURE: DIAG3 (fid=2)",
  "PATTERN FEATURE: CORE (fid=3)", exactly ONE omitted-rows line
  (CORE — LMC and DIAG3 are in the detailed list); the rlm_01
  date-masked sha3_256 golden
  `f6b54954a3c54d13a9a3b3e65face75a5bd709899050c0b77b236a8955cf4c8c`
  (D-105/M2 re-pin); the logs: "Optimization Status :
  CONVERGED_MIN_GRAD (16 iters)" + "Generalization Gap (RMSE) :
  23.87" (D-105/M2 — now dense-vs-dense: vld_rmse 27.22 −
  train_dense_rmse 3.36; was 27.22 as 27.22 − 0.00 compressed) +
  "Substitution Delta (RMSE)   : 3.36" (D-105/M2 — the true
  compressed-vs-dense cost: 3.36 vs the compressed 0.00).

## Conventions / notes

- D-085 idiom: the SKIP_REGAB_DB gate is FIRST in setUp (before the
  stdout patch / tmp dir), as in the other worker suites.
- Goldens are EXACT floats (no tolerance) — the pipeline is
  deterministic (the rlmwf checksum + sha3 flows pin every
  upstream artifact; the recompute is a pure float64 pass over
  pinned data, re-derived by scratch/verify_analytics.py tier C
  with 0 mismatches).
- The `detailed_report` fixture change (T6: rlm_01.json
  `["DIAG3"]` → `["DIAG3", "LMC"]`) is the only fixture edit of the
  campaign — the analytics block is consumed by the ANALYTICS level
  only, so no other golden moved (the rlm_01 file-report hash above
  is the post-T6 value).
- The 6-hit cache count mirrors the D-102 VALIDATE suite's count —
  the 5th non-cache level adds no cache file (the rlmwf_12 slot
  stays unused, the flat-file numbering skips 12 like 03/07/08).

## Appendix — line reference

338 lines, as of D-105 (304 at D-103; D-105/M2: +34 — the dense
dict blocks, the new header pins, the new log pin).

- L43-55: imports
- L58-65: `_masked_report_hash`
- L68-241: `TestLMWorkerAnalytics` (setUp L77-100, tearDown
  L102-106, goldens L108-184, second instance L186-223, _down
  L225-241)
- L244-334: `TestLMWorkerAnalyticsMobility` (setUp L254-277,
  tearDown L279-283, tables test L285-334)
- L337-338: `unittest.main()`
