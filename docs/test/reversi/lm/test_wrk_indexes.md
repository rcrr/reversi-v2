# test/reversi/lm/test_wrk_indexes.py
The suite of the INDEXES worker. 1 class / 2 tests / no PERF — both DB-gated.

## Coverage

| class | what it pins |
|---|---|
| `TestLMWorkerIndexes` (2, `SKIP_REGAB_DB` gated) | `test_compute_and_populate_cache` — move to INDEXES (step 5 pinned): the FLAT `rlmwf_05_INDEXES.dat` + `rlmwf_05_INDEXES.dat.SHA3-256` exist on disk (the machine-level naming is pinned end-to-end), the logs contain "Executing heavy computation", `ctx.hlp_indexes` non-None. `test_read_cache_on_new_instance` — the first instance warms the cache; a SECOND instance on the same cache dir (move to FEATURES, the StringIO cleared, then to INDEXES): the logs contain "Cache successfully loaded and validated" and do NOT contain "Executing heavy computation" (cache hit, nothing recomputed); `ctx.hlp_indexes` non-None |

The shared setUp: the db_long_gate FIRST (the SKIP_REGAB_DB + LONG gates; the move to INDEXES runs POSITIONS — a DB hit
on a fresh base dir) + stdout patched to a StringIO + the `TemporaryDirectory` idiom (the shared `CUSTOM_TMP_BASE` from
`test.reversi.paths`, `setUpClass` mkdir, the temp dir created FIRST so a mid-setup failure still leaves a cleanable
dir) + a `LogisticModel` on the `rlm_00.json` fixture (anchored to `WORKSPACE_ROOT`, `base_dir_override` = the tmp dir)
+ `move_to_step('FEATURES')` (step 2 pinned; the comment is ACCURATE — "INDEXES depends on the feature_set loaded
there") + a defensive tearDown (getattr guards).

## Goldens pinned

- The flat cache file names: `rlmwf_05_INDEXES.dat` + `rlmwf_05_INDEXES.dat.SHA3-256`.
- The witness log lines: "Executing heavy computation" (compute run) and "Cache successfully loaded and validated"
  (cache hit) — with the NEGATIVE pin "Executing heavy computation" absent on the second run.
- The step numbering: 0 / `CREATED`, 2 / `FEATURES` (setUp), 5 / `INDEXES` (the compute test) — pinned in three places.

## Conventions

- The `TemporaryDirectory` idiom + the `WORKSPACE_ROOT`/`CUSTOM_TMP_BASE` anchoring (shared `test.reversi.paths`) — the
  artifacts go under the shared `CUSTOM_TMP_BASE` (the house idiom).
- The `SKIP_REGAB_DB` gate at the top of setUp (the test_regab pattern).
- The header run note documents the live-DB requirement and the gate (the established pattern).

## Integration

- The end-to-end cache round-trip pin, one level deeper than test_wrk_positions (the same shape).
- What the tests do NOT pin (probe-only): the on-disk content / data-checksum identity (probe C3-C5), the exact
  feature-set-hash / rds-checksum metadata, the `_down` clearing (C7), the `rlmwf_02_FEATURES*` absence (C2).
