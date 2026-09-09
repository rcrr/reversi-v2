# reversi/test/test_wrk_config.py
The test module of the CONFIG worker (Roberto's file, brought in
with the D-076 pipeline enablement; the D-078 T1-T4 campaign
re-anchored it; D-142 removed the cache class and added the
fingerprint + no-cache pins). 3 classes / 13 tests / no PERF gates.
> State: D-142 · 181cb57 · 2026-09-09 · suite 13/0/0

## Coverage

| class | what it pins |
|---|---|
| `TestLMWorkerConfig` (6) | the moves: up (step 1, name `CONFIG`, `ctx.cfg` set, `use_cache` True), down (back to step 0 `CREATED` + the `cfg`/`use_cache`/`config_checksum` reset — D-142), the with-cache round-trip CONFIG → CREATED → CONFIG, the `properties` bag round-trip from the fixture, the fingerprint (`ctx.config_checksum` == sha3_256 of `model_dump_json(indent=4)`, D-142), and the no-cache state (NO `rlmwf_*` file in the base dir after an up — the ad-hoc cache flow is gone, D-142) |
| `TestLMWorkerConfigValidation` (4) | one constraint per test over a schema-complete payload: invalid json5 → `ValueError` (json5 0.15.0 raises a plain ValueError — this version exposes no JSON5Exception), ec 99 → ValidationError, invalid status list → ValidationError, invalid hex mask → ValidationError |
| `TestLMWorkerConfigBaseDir` (3) | the three `_validate_base_dir` gates with the precise OS types (D-078 R3): the a-file → `NotADirectoryError` (raised in the FACADE `__init__`, not the worker), the not-writable (chmod 0o444, chmod-back in tearDown) → `PermissionError`, the missing → `FileNotFoundError` (the D1 test: the fixture loaded with json5, `base_dir` pointed at a non-existent dir, re-dumped to a temp json, passed WITHOUT an override) |

## Goldens pinned

- The fingerprint: `ctx.config_checksum` == `hashlib.sha3_256(
  ctx.cfg.model_dump_json(indent=4).encode()).hexdigest()` — the
  normalized dump (the effective config, the base_dir override
  included) is the single source of truth for the SAVE config
  record and the analytics report line (D-142).
- The no-cache state: the base dir holds NO `rlmwf_*` file after
  `move_to_step('CONFIG')` (the config record is a SAVE artifact,
  D-142).
- The invalid-case payloads (one constraint each over the
  schema-complete payload — `ec=10`, `status ["CMS"]`, the
  `FFFFFFFFFFFFFFFF` mobility, the `00000000000000FF` pattern):
  `ec=99`, `status=["INVALID"]`, `mask="ZZZZZZZZZZZZZZZZ"`.
- The gate messages: "not a directory", "not writable",
  "doesn't exist" (assertIn on the exception text, lower-case
  where noted).
- The properties-bag values from `rlm_00.json`: `number == 7`,
  `string == 'A string'`, `is_on is False`, missing key →
  `None` (the D-080 `LMBaseConfig.properties` extension bag,
  exercised end-to-end through the worker).
- The `ValueError` type for the invalid-json5 case — pins the
  json5 0.15.0 behaviour (upgrading json5 must re-check this
  golden).

## Conventions

- The D-065 idiom on all 3 classes: the shared `CUSTOM_TMP_BASE`
  (from `reversi.test.paths`) + `setUpClass` mkdir +
  `TemporaryDirectory(dir=...)` created FIRST in setUp +
  defensive tearDown.
- The json_config paths are `WORKSPACE_ROOT`-anchored (D-085),
  never CWD-relative.

## Integration

- Exercises `wrk_config.py` through the real StateMachine
  (the CONFIG level of the LM pipeline) with the
  `rlm_00.json` fixture.
