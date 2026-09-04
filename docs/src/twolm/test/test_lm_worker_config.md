# twolm/test/test_lm_worker_config.py
The test module of the CONFIG worker (Roberto's file, brought in
with the D-076 pipeline enablement; the D-078 T1-T4 campaign
re-anchored it, and step 3 of D-106 moved probe check D1 into it).
4 classes / 15 tests / no PERF gates.
> State: D-106 · 73a72d3 · 2026-09-04 · suite 15/0/0

## Coverage

| class | what it pins |
|---|---|
| `TestLMWorkerConfig` (4) | the moves: up (step 1, name `CONFIG`, `ctx.cfg` set, `use_cache` True), down (back to step 0 `CREATED` + the `cfg`/`use_cache` reset), the with-cache round-trip CONFIG → CREATED → CONFIG, and the `properties` bag round-trip from the fixture |
| `TestLMWorkerConfigValidation` (4) | one constraint per test over a schema-complete payload: invalid json5 → `ValueError` (json5 0.15.0 raises a plain ValueError — this version exposes no JSON5Exception), ec 99 → ValidationError, invalid status list → ValidationError, invalid hex mask → ValidationError |
| `TestLMWorkerConfigBaseDir` (3) | the three `_validate_base_dir` gates with the precise OS types (D-078 R3): the a-file → `NotADirectoryError` (raised in the FACADE `__init__`, not the worker), the not-writable (chmod 0o444, chmod-back in tearDown) → `PermissionError`, the missing → `FileNotFoundError` (the D1 test: the fixture loaded with json5, `base_dir` pointed at a non-existent dir, re-dumped to a temp json, passed WITHOUT an override) |
| `TestLMWorkerConfigCacheLogic` (4) | first-run files at the FLAT `rlmwf_01_CONFIG.dat` + `.SHA3-256` (the D-076/D-078 naming), the skip-identical second run, the update-on-change, the corruption → RuntimeError "not matching" |

## Goldens pinned

- The sidecar format: `checksum_file.read_text().strip()` ==
  `hashlib.sha3_256(cache_file.read_bytes()).hexdigest()` — bare
  hex, no binio basename column (protects the D-076/D-078 naming
  + the ad-hoc cache flow; the C7 probe asymmetry is the other
  side — a binio-format sidecar FAILS the worker's verify).
- The flat path: `base_dir/rlmwf_01_CONFIG.dat` (no `rlmwf_`
  subdirectory) — the filename-prefix concatenation semantics.
- The invalid-case payloads (one constraint each over the
  schema-complete payload — `ec=10`, `status ["CMS"]`, the
  `FFFFFFFFFFFFFFFF` mobility, the `00000000000000FF` pattern):
  `ec=99`, `status=["INVALID"]`, `mask="ZZZZZZZZZZZZZZZZ"`.
- The skip-identical second run pins BOTH the mtime equality and
  the checksum content equality (the no-rewrite behaviour).
- The gate messages: "not a directory", "not writable",
  "doesn't exist" (assertIn on the exception text, lower-case
  where noted).
- The properties-bag values from `rlm_00.json`: `number == 7`,
  `string == 'A string'`, `is_on is False`, missing key →
  `None` (the D-080 `RLMBaseConfig.properties` extension bag,
  exercised end-to-end through the worker).
- The `ValueError` type for the invalid-json5 case — pins the
  json5 0.15.0 behaviour (upgrading json5 must re-check this
  golden).

## Conventions

- The D-065 idiom on all 4 classes: the shared `CUSTOM_TMP_BASE`
  (from `twolm.test.paths`) + `setUpClass` mkdir +
  `TemporaryDirectory(dir=...)` created FIRST in setUp +
  defensive tearDown.
- The json_config paths are `WORKSPACE_ROOT`-anchored (D-085),
  never CWD-relative.

## Integration

- Exercises `lm_worker_config.py` through the real StateMachine
  (the CONFIG level of the RLM pipeline) with the
  `rlm_00.json` fixture.
