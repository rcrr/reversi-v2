<!-- ARCHIVED — D-106 step 11 (the docs/ rewrite, 2026-09-04): the
     complete session-23 test-doc (D-083/D-084) + the D-085
     re-anchoring record moved out of
     docs/src/twolm/test/test_lm_worker_indexes.md per
     docs_rules.md §1/§4/§6. This is a frozen historical record:
     it is never updated. NOTE: the file is UNCHANGED since D-085
     (aef6188, 2026-08-31) — 1 class / 2 tests / 153 lines is
     still correct (no step-3 conversion touched this file); the
     "519 tests / 58 skipped" full-discover figure predates
     steps 3-10 (current: 664/87 gated). The T1-T3 + M1 campaign
     narrative and the D-085 anchoring are frozen history. -->

# twolm/test/test_lm_worker_indexes.py

Analysis date: 2026-08-31 — analysis session 23 (D-083); fix
campaign D-084 approved by Roberto ("Sì fai tutto") and applied in
the same session.

Roberto's file, brought in with the INDEXES enablement (a323e0f,
the line-by-line pipeline step 5). 1 class / 2 tests / no PERF.
Green on first run with the live DB. T1-T3 + M1 all resolved in
D-084 (the D-065 idiom, the SKIP_REGAB_DB gate, the header
grammar, the whitespace). D-085 (same session): the D-065 idiom
re-anchored to the shared twolm.test.paths module — the per-file
__file__ derivation and the CWD-relative JSON path are now both
anchored to WORKSPACE_ROOT.

## Suite status (session 23, post D-084)

- `test_lm_worker_indexes`: 2/0/0 (DB-gated since D-084 T2 — the
  setUp moves through POSITIONS on a fresh base dir, so a live DB
  is required; `SKIP_REGAB_DB=1` skips both tests, as in the
  other worker test files)
- Full discover: 519 tests, 58 skipped under `SKIP_REGAB_DB=1`
  (17 PERF + 35 regab + 2 positions + 2 features + 2 indexes),
  GREEN; ungated (live DB): 519 run, 17 skipped (PERF only), GREEN.
  (D-085: +3 — the new test_paths module; the skip breakdown is
  unchanged.)

## Coverage

- setUp (L64-92, D-084 T1/T2 idiom, D-085 re-anchored): the
  SKIP_REGAB_DB gate at the top → stdout patched to a StringIO
  (logs captured, output clean) + `TemporaryDirectory` created
  FIRST under the shared `CUSTOM_TMP_BASE` (imported from
  twolm.test.paths, L54) + a `LogisticModel` on the `rlm_00.json`
  fixture — anchored to the same `WORKSPACE_ROOT` since D-085
  (`base_dir_override` = the tmp dir) + `move_to_step('FEATURES')`
  (the comment L89 is
  ACCURATE — "INDEXES depends on the feature_set loaded there";
  in contrast to the test_lm_worker_features M1 comment, which
  pointed at POSITIONS). The pipeline preconditions are pinned
  (step 0 / `CREATED`, step 3 / `FEATURES` after the move).
  Defensive tearDown (L94-98, getattr guards).
- `test_compute_and_populate_cache` (L100-117): move to INDEXES
  (step 4 pinned) — the FLAT cache files
  `rlmwf_04_INDEXES.dat` + `rlmwf_04_INDEXES.dat.SHA3-256` exist
  on disk (the D-078 machine-level naming pinned end-to-end) and
  the logs contain "Executing heavy computation"; the context
  holds a non-None `rlm_indexes`.
- `test_read_cache_on_new_instance` (L119-150): the first
  instance moves to INDEXES (compute + store, warms the cache);
  a SECOND instance on the same cache dir moves to FEATURES, the
  StringIO is cleared, then to INDEXES: the logs contain "Cache
  successfully loaded and validated" and do NOT contain
  "Executing heavy computation" (cache hit, nothing recomputed);
  the context holds a non-None `rlm_indexes`.

The two tests pin the cache round-trip end-to-end on a real
domain data set: compute + store on the first run, load +
sidecar-verify + business-consistency on the second — the same
shape as test_lm_worker_positions, one level deeper. What the
tests do NOT pin (probe-only, D-083): the on-disk content /
data-checksum identity (probe C3-C5), the exact feature-set-
hash / rds-checksum metadata, the `_down` clearing (C7), and the
`rlmwf_03_FEATURES*` absence (C2).

## Defects — RESOLVED (D-084)

- **T1 FIXED (E2, re-anchored D-085)**: the D-065 idiom applied —
  the D-084 per-file `CUSTOM_TMP_BASE =
  Path(__file__).resolve().parents[3] / "build" / "tmp"`
  derivation is replaced by the import of the shared constants
  from `twolm.test.paths` (L54, marker-based workspace root; the
  `json_config` is anchored to the same `WORKSPACE_ROOT` since
  D-085), `setUpClass` mkdir (L61-63), `TemporaryDirectory`
  created FIRST in setUp (L76-77, so a mid-setup failure still
  leaves a cleanable temp dir), defensive tearDown with getattr
  guards (L94-98). The `shutil` import and the CWD-relative
  `mkdtemp` are gone. The same fix as test_lm_worker_positions T1
  / test_lm_worker_features T1.
- **T2 FIXED (E3)**: the `SKIP_REGAB_DB` gate at the top of setUp
  (L68-69, the test_regab wording) — a no-DB environment running
  the canonical gated command now skips both tests instead of
  erroring in setUp. The same fix as test_lm_worker_positions T2
  / test_lm_worker_features T2.
- **T3 FIXED (E4)**: header grammar — "How to run the
  lm_worker_indexes unit tests." + the run note documents the
  live-DB requirement and the gate (the established pattern, cf.
  test_lm_worker_positions T4).
- **M1 FIXED (E7)**: the 13 non-comment trailing-whitespace
  lines stripped (incl. the whitespace-only L137 at EOF pre-fix);
  scope as in D-078 M3: the license-header `# ` lines stay.

## Verdict

A good, minimal end-to-end pin of the INDEXES cache round-trip
(compute → file → file, log strings as witnesses); the
underlying behaviour is independently verified by the D-084
probe (56 checks, 0 mismatches). T1-T2 are the same robustness
fixes applied to the two earlier pipeline test files; T3 + M1
are hygiene. None changes what the two tests prove.
