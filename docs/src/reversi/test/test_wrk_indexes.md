# reversi/test/test_wrk_indexes.py
The suite of the INDEXES worker (Roberto's file, brought in with
the a323e0f line-by-line enablement; the D-084 T1-T3 + M1
campaign + the D-085 re-anchoring). 1 class / 2 tests / no PERF
— both DB-gated.
> State: D-157 · 2026-09-11 · suite 2/0/0 (2 DB-gated)

## Coverage

| class | what it pins |
|---|---|
| `TestLMWorkerIndexes` (2, `SKIP_REGAB_DB` gated) | `test_compute_and_populate_cache` — move to INDEXES (step 4 pinned): the FLAT `rlmwf_04_INDEXES.dat` + `rlmwf_04_INDEXES.dat.SHA3-256` exist on disk (the D-078 machine-level naming pinned end-to-end), the logs contain "Executing heavy computation", `ctx.hlp_indexes` non-None. `test_read_cache_on_new_instance` — the first instance warms the cache; a SECOND instance on the same cache dir (move to FEATURES, the StringIO cleared, then to INDEXES): the logs contain "Cache successfully loaded and validated" and do NOT contain "Executing heavy computation" (cache hit, nothing recomputed); `ctx.hlp_indexes` non-None |

The shared setUp: the db_long_gate FIRST (the SKIP_REGAB_DB +
LONG gates, D-130; the move to INDEXES runs POSITIONS —
a DB hit on a fresh base dir, the D-157 order) + stdout
patched to a StringIO + the D-065
`TemporaryDirectory` idiom (the shared `CUSTOM_TMP_BASE` from
`reversi.test.paths`, `setUpClass` mkdir, the temp dir created FIRST
so a mid-setup failure still leaves a cleanable dir) + a
`LogisticModel` on the `rlm_00.json` fixture (anchored to
`WORKSPACE_ROOT`, `base_dir_override` = the tmp dir) +
`move_to_step('FEATURES')` (step 2 pinned, D-157; the comment
is ACCURATE — "INDEXES depends on the feature_set loaded
there" — the test_wrk_features M1 comment, removed at D-157,
pointed at POSITIONS) + a defensive tearDown (getattr guards).

## Goldens pinned

- The flat cache file names: `rlmwf_04_INDEXES.dat` +
  `rlmwf_04_INDEXES.dat.SHA3-256`.
- The witness log lines: "Executing heavy computation" (compute
  run) and "Cache successfully loaded and validated" (cache hit)
  — with the NEGATIVE pin "Executing heavy computation" absent on
  the second run.
- The step numbering: 0 / `CREATED`, 3 / `FEATURES` (setUp),
  4 / `INDEXES` (the compute test) — pinned in three places.

## Conventions

- The D-065 idiom + the D-085 `WORKSPACE_ROOT`/`CUSTOM_TMP_BASE`
  anchoring (shared `reversi.test.paths`) — the CWD-relative
  `mkdtemp` and the per-file `__file__` derivation are gone.
- The `SKIP_REGAB_DB` gate at the top of setUp (the test_regab
  pattern).
- The header run note documents the live-DB requirement and the
  gate (the established pattern).

## Integration

- The end-to-end cache round-trip pin, one level deeper than
  test_wrk_positions (the same shape).
- What the tests do NOT pin (probe-only): the on-disk content /
  data-checksum identity (probe C3-C5), the exact
  feature-set-hash / rds-checksum metadata, the `_down` clearing
  (C7), the `rlmwf_03_FEATURES*` absence (C2).
