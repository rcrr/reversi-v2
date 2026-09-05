<!-- ARCHIVED — D-106 step 16 (the docs/ rewrite, 2026-09-04): the
     complete session-26 test-doc (D-096) moved out of
     docs/src/twolm/test/test_rlm_optimize.md per
     docs_rules.md §1/§4/§6. This is a frozen historical record:
     it is never updated. NOTE: the file is UNCHANGED since
     b1b8934 (2026-09-01) — 4 classes / 19 tests / 340 lines is
     still correct. The step-3 class c deletions of the probe's
     F1-F10 (checkpoint IO) + G1/G2 + G4 + G5 (the helper
     branches) landed in THIS file's coverage (the M10 expansion
     already owned them). The "598 tests / 71 skipped"
     full-discover figure predates steps 3-10. The D-096 M10 +
     T14/T15 campaign narrative is frozen history. -->

# twolm/test/test_rlm_optimize.py

Analysis date: 2026-09-01 — analysis session 26 (D-096, bring-in
analysis); the M10 expansion + T14/T15 applied in the D-096 campaign
(Roberto: "M: falli tutti" — the dedicated-suite expansion, the
header fix, the D-085 idiom, the misleading test renames). Brought in
by Roberto (commit 1ebdd8b). Probe (scratch/verify_optimize.py, tiers
C/F/G, re-pinned post-campaign): 0 mismatches.

The dedicated rlm_optimize suite — the house pattern (D-094 M1 for
gradient, D-090 T6 for design_matrix, D-092 T3 for zed): a NO-DB
suite (handcrafted checkpoint fixtures + a SimpleNamespace ctx mock)
that pins the binary round-trip, the error paths, the golden hashes
and the two gate functions — the level where the worker's decision
logic lives.

## Suite status (session 26, post D-096)

- `test_rlm_optimize`: 19/0/0 (4 classes; no DB, no gate — the header
  says so, T14). Full discover: 598 tests, 71 skipped under
  `SKIP_REGAB_DB=1`, GREEN.

## State per Roberto

As brought in: 4 tests in 2 classes (the IO round-trip + 3
consistency tests) — green on first run, but with the bring-in gaps:
the header claimed "a live regab DB is required" although the file
uses no DB (T14); the two consistency tests were named
`test_inconsistent_iters` / `test_inconsistent_m` although they test
the checksum gates (T15); the CWD-relative mkdtemp setUp (no D-085
idiom); and the coverage gaps M10 flagged: no error-path pins, no
empty-history round-trip, no dtype pins, no golden file hash, and
`optimization_info_dict` / `weights_compute_sha3_256_hash` /
`is_optimization_status_converged` untested. D-096 (M10, "falli
tutti"): expanded to 19 tests in 4 classes, all green.

## Architecture (340 lines, post D-096)

- `_mock_ctx(ridge, min_grad, dm, zed)` (L63-78): the SimpleNamespace
  mock — `log_event` (recording), the two checksum fields, and the
  nested `cfg.stat_model.ridge_regularization` +
  `cfg.optimization.min_grad` the two gate functions read (the R1
  ridge gate made the cfg nesting necessary in the mocks).
- `TestRLMOptimizeIO` (L81-238): setUp builds the deterministic
  fixture (w [0.1, 0.2, 0.3] f32, one (s, y) pair, rho [1.5]) in a
  `TemporaryDirectory` under `CUSTOM_TMP_BASE` (D-085 idiom,
  defensive tearDown). 8 tests:
  - `test_store_and_load_cycle`: the scalars + the arrays WITH the
    dtype pins (w/sl/yl float32, rho plain float).
  - `test_empty_history_roundtrip`: the len_mem=0 path.
  - `test_history_length_mismatch_raises`: M6 — asymmetric sl/yl/rho
    raise ValueError and NO file is created (the check runs before
    the writer opens).
  - `test_wrong_description_raises` / `test_wrong_version_raises`:
    the 2 header `RuntimeError` gates, message-pinned.
  - `test_checksum_mismatch_raises`: R3 — flip the last content byte
    (sidecar untouched) → load raises the "Checkpoint checksum
    mismatch" RuntimeError.
  - `test_file_golden_hash`: the deterministic bytes pin to
    `6e01ff8614e8732484b7af59b01615989357ce1af2419864621965af221bd280`.
  - `test_sidecar_produced_and_matches`: the `.SHA3-256` sidecar
    exists and verifies.
- `TestRLMOptimizeHelpers` (L240-261): 3 tests — `info_dict`
  projects to exactly the 5 context keys (extras dropped), KeyError
  on a missing key, and the weights-hash golden
  `78a7baac51aedf442b3de09a583af1a0704c8aece3b156aaf630780b2d7dc060`
  (= the independent `sha3_256(w.tobytes())`).
- `TestRLMOptimizeCacheConsistency` (L264-305): 4 tests on the
  fixture ctx (dm "123abc", zed "456xyz", ridge 0.01): valid → True;
  the 3 gate mismatches (T15 renamed: `..._design_matrix_checksum`,
  `..._zed_checksum`; new `test_inconsistent_ridge` — R1) → False.
- `TestRLMOptimizeStatusConverged` (L308-336): 4 tests — g_norm below
  the tolerance → True; above → False; the f32 round-trip (the
  stored np.float32 values do not trip the comparison); and
  `test_judged_against_new_tolerance` (M3 semantics: a looser current
  tolerance accepts a checkpoint that was not converged under the
  old one — the tolerance is a judgement criterion, not part of the
  objective).

## Verified facts (probe tiers C, F, G)

- The file golden hash and the sidecar content are byte-stable across
  runs (F5/F6) — the checkpoint format is deterministic for a given
  input (fixed header, fixed field order, no timestamps).
- All 4 consistency branches (incl. the R1 ridge gate) and the 3-WARN
  diagnostic pattern per failed gate (G4); all 4 status branches
  (G5).
- The M6 fail-fast leaves no file behind (F10) — the same shape as
  the D-095 empty-suffix guard.

## Minor notes

- The header's "-1-" line now reads "(no live regab DB required —
  pure checkpoint IO and cache-validation tests, as in
  test_rlm_gradient)" (T14) — the old "a live regab DB is required"
  was simply wrong for this file (no gate was ever needed).
- The mock ctx records its log events (`_events`) but the tests only
  assert on the return values — the log-pattern pins live in the
  probe (G4), keeping the suite focused.
- `test_store_and_load_cycle` keeps Roberto's original approximate
  assertions for f/g_norm/ridge/min_grad (assertAlmostEqual) while
  the arrays are pinned exactly (assert_array_equal) — the f32
  metadata is round-trip stable, the approximate style is just the
  original author's choice and harmless.

## Integration notes

- No DB anywhere: the whole suite runs under `SKIP_REGAB_DB=1`
  without skipping anything (the 19 tests are all live in the gated
  598-test discover).
- The golden hashes are the same ones the probe pins (F5/G3) — a
  format change to `save_optimization_checkpoint` breaks BOTH at
  once.
- The R3 `test_checksum_mismatch_raises` is the suite-level mirror of
  the worker's R2 path (probe H8): the worker deletes the corrupted
  file + sidecar and starts from scratch.

## Appendix — line reference

340 lines, as of D-096 (157 at the bring-in; D-096: header fix T14,
D-085 idiom, T15 renames, +15 tests for the M10 expansion, ws sweep).

- L28-42: header (how-to-run block, the no-DB line)
- L44-60: imports (hashlib, tempfile, unittest, Path,
  SimpleNamespace, numpy, binio, the 6 rlm_optimize names,
  CUSTOM_TMP_BASE)
- L63-78: `_mock_ctx`
- L81-238: `TestRLMOptimizeIO` (setUp L84-114, tearDown L116-118;
  8 tests L120-237)
- L240-261: `TestRLMOptimizeHelpers`
- L264-305: `TestRLMOptimizeCacheConsistency`
- L308-336: `TestRLMOptimizeStatusConverged`
- L339-340: `__main__`
