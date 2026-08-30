# twolm/test/test_lm_worker_config.py

Analysis date: 2026-07-22 — analysis session 21.

Roberto's new test file (session 21), brought in with the D-076
pipeline enablement. 4 classes / 14 tests / no PERF:

- `TestLMWorkerConfig` — move_up (config loads, ctx.cfg set,
  use_cache True), move_down (step/name + the D-078 T3 reset pins),
  with_cache (repeated up is a no-op), property checks (name /
  description / base_dir round-trips).
- `TestLMWorkerConfigBaseDir` — a-file base_dir → NotADirectoryError
  at construction (the facade's `__init__` check, not the worker);
  not-writable (chmod 0o444 + chmod-back in tearDown) →
  PermissionError "not writable" (D-078 R3: was RuntimeError).
- `TestLMWorkerConfigValidation` — invalid json5 (D-078 T2:
  `ValueError` — json5 0.15.0 raises a plain ValueError, this
  version has no JSON5Exception), ec out of range (99), invalid
  status list, invalid hex mask — each a pydantic ValidationError.
  The payload is schema-complete (D-076 fix: output / stat_model /
  optimization.checkpoint_file / validation_data_set added) so each
  test pins the ONE constraint under test.
- `TestLMWorkerConfigCacheLogic` — first-run files at the FLAT
  `rlmwf_01_CONFIG.dat` + `.SHA3-256` (the D-076/D-078 naming; the
  D-078 T4 pin: bare-hex sidecar == sha3_256 of the .dat),
  update-on-change, skip-identical second run, corruption →
  RuntimeError "not matching".

## D-076 fixes (applied, with Roberto's knowledge)

- `py/twolm/test/data/rlm_00.json` → `src/twolm/test/data/rlm_00.json`
  x2 (the original-repo layout prefix).
- Validation payload completed as above.

## D-078 fix campaign (Roberto: "T1-T6: OK")

- T1 FIXED — the D-065 idiom on all 4 classes: module-level
  `CUSTOM_TMP_BASE = Path(__file__).resolve().parents[3] / "build" /
  "tmp"` + `setUpClass` mkdir + `tempfile.TemporaryDirectory(dir=...)`
  created FIRST in setUp (a mid-setup failure still leaves a
  cleanable temp dir) + defensive tearDown (stops only the patchers
  / cleanups that exist). The dead `shutil` import removed. A stray
  per-test `tempfile.mkdtemp(dir='./build/tmp')` inside
  `test_base_dir_is_a_file_raises_error` (Roberto's original line)
  removed — it leaked a tmp dir on every run; caught via build/tmp
  leftovers after the campaign run.
- T2 FIXED — `test_invalid_json_syntax` pinned `ValueError` instead
  of bare `Exception` (the actual json5 0.15.0 exception for a
  syntax error; this version of the module exposes no
  `JSON5Exception` attribute — the D-077 proposal was adjusted).
- T3 FIXED — `test_move_down` now pins the `_down` reset:
  `context.cfg is None` and `context.use_cache is None`.
- T4 FIXED — `test_cache_files_created_on_first_run` now pins the
  sidecar format: `checksum_file.read_text().strip()` ==
  `hashlib.sha3_256(cache_file.read_bytes()).hexdigest()` (bare hex,
  no binio basename column).
- T5/T6 unchanged (report-only: header grammar; mtime coarseness —
  the content assertion already pins the no-rewrite behaviour).
- R3 side effect: `test_base_dir_is_not_writable_raises_error` now
  expects `PermissionError` (was `RuntimeError`), message pin kept.

Suite: 14/0/0 GREEN (D-076 commit 6ac9d74; D-078 commit d6a850e).
