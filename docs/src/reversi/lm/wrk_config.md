# reversi/lm/wrk_config.py
The CONFIG worker of the LM pipeline — the second level, the first
non-sentinel. It loads the LM JSON5 config file, validates it into
the hlp_config_schemas domain model, computes the config fingerprint
(`ctx.config_checksum`, the sha3_256 of the normalized dump), and
publishes the model (and the `use_cache` flag) on the context for the
workers that follow. It writes NO cache file (D-142: the ad-hoc
cache flow is gone — the config record is a SAVE artifact, next to
the model file).
> State: D-142 · 181cb57 · 2026-09-09 · suite 13/0/0

## API

| name | contract |
|---|---|
| `wrk_config()` | the only `__all__` name; `@validate_call` factory returning `Worker("CONFIG", _up, _down)` |
| `_up` / `_down` | the worker callables (module-level privates, 5 with `_load`, `_validate`, `_validate_base_dir`) |

## Architecture

- `_up`: log → `_load` → `_validate` → INFO (name/description/
  base_dir) → `ctx.use_cache = cfg.use_cache` → `ctx.cfg = cfg` →
  the fingerprint: `ctx.config_checksum =
  hashlib.sha3_256(cfg.model_dump_json(indent=4).encode()).hexdigest()`
  (D-142: the normalized dump is the EFFECTIVE configuration of the
  run — the base_dir override included, pydantic defaults resolved —
  and this is the single source of truth for the SAVE config record
  and the analytics report line) → the INFO log of the hex.
- `_down`: the ERROR "Clearing configuration..." →
  `ctx.cfg = None`, `ctx.use_cache = None`, `ctx.config_checksum =
  None`.
- `_load`: `json5.load` (UTF-8) of `ctx.config_file_path` with the
  DEBUG log of the path; an optional `ctx.base_dir_override` is
  applied to the raw dict before `LMConfig(**raw)`.
- `_validate` → `_validate_base_dir`: three gates with the precise
  OS exception types, each logged at ERROR before the raise —
  `FileNotFoundError` (doesn't exist), `NotADirectoryError`
  (is not a directory), `PermissionError` (is not writable).

## Verified invariants

Pinned by `probes/verify_wrk_config.py` (15 checks) +
`test_wrk_config.py` (13 tests, 3 classes).

- Source shape: the `__all__` name, the factory name "CONFIG", the
  module callables, the 5 privates (the `_store_to_file` is gone,
  D-142) — probe section A.
- The loaded state: `ctx.cfg` a LMConfig, name round-trip,
  `use_cache` True from the config, `ctx.config_checksum` == the
  sha3_256 of `model_dump_json(indent=4)` (probe B3/B4/B6/B6b; the
  fingerprint is re-derived independently from the live cfg).
- The no-cache state: NO `rlmwf_*` file in the base dir after an up
  (probe B7 + `test_no_cache_file_written`), and no file-write idiom
  in the module source (probe E5).
- The repeat-run behaviour: the second up is a pure load with a
  STABLE fingerprint (probe C1), the `_down` reset (cfg, use_cache,
  config_checksum — probe C3).
- The failure behaviour: the invalid json5 → `ValueError` (json5
  0.15.0 raises a plain ValueError), the base_dir gates with the
  precise OS types (the a-file → `NotADirectoryError` raised in the
  FACADE `__init__`, the not-writable → `PermissionError`, the
  missing → `FileNotFoundError`) — `TestLMWorkerConfigBaseDir`.
- The integration: the bare (un-injected) context keeps the no-op
  closure lambda (probe E4a), `rlm_00.json` is NOT plain JSON
  (json5 load-bearing, probe E6), the down log line (probe E7).

## Conventions

- The injected machine closures are the naming authority (D-078) —
  the worker does no path arithmetic of its own. (The injected
  `get_cache_file_*` closures are simply unused by this level since
  D-142.)
- `json5` is a declared dependency (added for this worker, D-076) —
  the config fixture `rlm_00.json` is JSON5 with comments.
- `hashlib` stays imported (the fingerprint) — but the module writes
  NOTHING (probe E5 pins it).
- The test artifacts follow the D-065 idiom (`build/tmp`,
  `CUSTOM_TMP_BASE` from `reversi.test.paths`).
- `@validate_call` on the public factory (house convention D-069).

## Integration

- The CONFIG level of the LM pipeline: the facade
  (`logistic_model.py`) instantiates `Worker` and the machine;
  this module provides the level's `_up`/`_down`.
- Consumes `hlp_config_schemas` (the domain) and
  `state_machine.Worker`; publishes `ctx.cfg` / `ctx.use_cache` /
  `ctx.config_checksum` that the later workers read (the fingerprint
  is consumed by `wrk_save` — the config record — and by
  `hlp_analytics` — the report line).
- The config RECORD (the normalized dump + its checksum sidecar) is
  written by the SAVE level next to the model file (wrk_save.md) —
  D-142 moved the provenance from this level's cache slot to the
  shipped artifact.
- Test fixture: `src/reversi/test/data/rlm_00.json` (JSON5).
