# test/reversi/lm/test_wrk_config.py
The test module of the CONFIG worker. 3 classes / 13 tests / no PERF gates.

## Coverage

| class | what it pins |
|---|---|
| `TestLMWorkerConfig` (6) | the moves: up (step 1, name `CONFIG`, `ctx.cfg` set), down (back to step 0 `CREATED` + the `cfg`/`use_cache`/`config_checksum` reset), the with-cache round-trip CONFIG → CREATED → CONFIG, the `properties` bag round-trip from the fixture, the fingerprint (`ctx.config_checksum` == sha3_256 of `model_dump_json(indent=4)`), and the no-cache state (NO `rlmwf_*` file in the base dir after an up) |
| `TestLMWorkerConfigValidation` (4) | one constraint per test over a schema-complete payload: invalid json5 → `ValueError` (json5 0.15.0 raises a plain ValueError — this version exposes no JSON5Exception), ec 99 → ValidationError, invalid status list → ValidationError, invalid hex mask → ValidationError |
| `TestLMWorkerConfigBaseDir` (3) | the three `_validate_base_dir` gates with the precise OS types: the a-file → `NotADirectoryError` (raised in the FACADE `__init__`, not the worker), the not-writable (chmod 0o444, chmod-back in tearDown) → `PermissionError`, the missing → `FileNotFoundError` (the D1 test: the fixture loaded with json5, `base_dir` pointed at a non-existent dir, re-dumped to a temp json, passed WITHOUT an override) |

## Goldens pinned

- The fingerprint: `ctx.config_checksum` == `hashlib.sha3_256( ctx.cfg.model_dump_json(indent=4).encode()).hexdigest()`
  — the normalized dump (the effective config, the base_dir override included) is the single source of truth for the
  EMBEDDED model-file config provenance and the analytics report line.
- The no-cache state: the base dir holds NO `rlmwf_*` file after `move_to_step('CONFIG')` (the configuration provenance
  is EMBEDDED in the model file at SAVE).
- The invalid-case payloads (one constraint each over the schema-complete payload — `ec=10`, `status ["CMS"]`, the
  `FFFFFFFFFFFFFFFF` mobility, the `00000000000000FF` pattern): `ec=99`, `status=["INVALID"]`,
  `mask="ZZZZZZZZZZZZZZZZ"`.
- The gate messages: "not a directory", "not writable", "doesn't exist" (assertIn on the exception text, lower-case
  where noted).
- The properties-bag values from `rlm_00.json`: `number == 7`, `string == 'A string'`, `is_on is False`, missing key →
  `None` (the `LMBaseConfig.properties` extension bag, exercised end-to-end through the worker).
- The `ValueError` type for the invalid-json5 case — pins the json5 0.15.0 behaviour (upgrading json5 must re-check this
  golden).

## Conventions

- The idiom on all 3 classes: the shared `CUSTOM_TMP_BASE` (from `test.reversi.paths`) + `setUpClass` mkdir +
  `TemporaryDirectory(dir=...)` created FIRST in setUp + defensive tearDown.
- The `TestLMWorkerConfig` json_config path is `WORKSPACE_ROOT`-anchored; the `TestLMWorkerConfigBaseDir` cases pass
  CWD-relative paths on purpose (the resolver resolves them against the CWD).

## Integration

- Exercises `wrk_config.py` through the real StateMachine (the CONFIG level of the LM pipeline) with the `rlm_00.json`
  fixture.
