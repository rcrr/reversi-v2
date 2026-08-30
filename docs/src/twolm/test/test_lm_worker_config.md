# twolm/test/test_lm_worker_config.py

Analysis date: 2026-07-22 — analysis session 21.

Roberto's new test file (session 21), brought in with the D-076 pipeline
enablement. 4 classes / 14 tests / no PERF:

- `TestLMWorkerConfig` — move_up (config loads, ctx.cfg set, use_cache True),
  move_down (step/name), with_cache (repeated up is a no-op), property checks
  (name / description / base_dir round-trips).
- `TestLMWorkerConfigBaseDir` — a-file base_dir → NotADirectoryError at
  construction; not-writable (chmod 0o444 + tearDown chmod-back) → RuntimeError
  "not writable".
- `TestLMWorkerConfigValidation` — invalid json5, ec out of range (99),
  invalid status list, invalid hex mask — each a pydantic ValidationError.
  The payload is schema-complete (D-076 fix: output / stat_model /
  optimization.checkpoint_file / validation_data_set added) so each test pins
  the ONE constraint under test.
- `TestLMWorkerConfigCacheLogic` — first-run files at the FLAT
  `rlmwf_01_CONFIG.dat` + `.SHA3-256` (the D-076 naming), update-on-change,
  skip-identical second run, corruption → RuntimeError "not matching".

## D-076 fixes (applied, with Roberto's knowledge)

- `py/twolm/test/data/rlm_00.json` → `src/twolm/test/data/rlm_00.json` x2
  (the original-repo layout prefix).
- Validation payload completed as above.

## Open items (D-077, awaiting ruling)

- T1: `tempfile.mkdtemp(dir='./build/tmp')` is CWD-relative and creates no base
  dir — replace with the D-065 `__file__`-anchored idiom (CUSTOM_TMP_BASE =
  `Path(__file__).resolve().parents[3] / "build" / "tmp"` + setUpClass mkdir +
  defensive tearDown, as in test_cache_manager).
- T2: `test_invalid_json_syntax` pins bare `Exception` — pin
  `json5.JSON5Exception`.
- T3: the `_down` reset is unpinned — `test_move_down` never asserts
  `context.cfg is None` / `context.use_cache is None`.
- T4: the bare-hex sidecar format is unpinned (probe B10-B12) — add a pin, or
  replace it if R1 changes the format.
- T5/T6 (report-only): header grammar; mtime comparison in the
  skip-identical test (coarser than the content assertion already present).

Suite: 14/0/0 GREEN (session 21, D-076 commit 6ac9d74).
