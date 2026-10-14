# reversi/lm/wrk_config.py
The CONFIG worker of the LM pipeline — the 1st active level (step 1), the first non-sentinel. It loads the LM JSON5
config file, validates it into the hlp_config_schemas domain model, computes the config fingerprint (`ctx.config_checksum`,
the sha3_256 of the normalized dump), and publishes the model (and the `use_cache` flag) on the context for the workers
that follow. It writes NO cache file; the configuration provenance is EMBEDDED in the v2 model file at SAVE.

## API

| name | contract |
|---|---|
| `wrk_config()` | the only `__all__` name; `@validate_call` factory returning `Worker("CONFIG", _up, _down)` |
| `_up` / `_down` | the worker callables (module-level privates, 5 with `_load`, `_validate`, `_validate_base_dir`) |

## Architecture

- `_up`: `_load` → INFO "loaded" → `_validate` → INFO "validated" → the DEBUG echo of the operational
  sections (one line each: optimization, stat_model, su_analysis, anova, regab_data_set — the
  dbname/user/host, never the password — and validation_data_set) → INFO (name/description/ base_dir) →
  `ctx.use_cache = cfg.use_cache` →
  `ctx.cfg = cfg` → the fingerprint:
  `ctx.config_checksum = hashlib.sha3_256(cfg.model_dump_json(indent=4).encode()).hexdigest()` (the normalized dump is
  the EFFECTIVE configuration of the run — the base_dir override included, pydantic defaults resolved — and this is the
  single source of truth for the EMBEDDED model-file config provenance and the analytics report line) → the INFO log of
  the hex.
- `_down`: the INFO "Clearing configuration..." → `ctx.cfg = None`, `ctx.use_cache = None`,
  `ctx.config_checksum = None`.
- `_load`: `json5.load` (UTF-8) of `ctx.config_file_path` with the DEBUG log of the path; an optional
  `ctx.base_dir_override` is applied to the raw dict before `LMConfig(**raw)`.
- `_validate` → `_validate_base_dir`: three gates with the precise OS exception types, each logged at ERROR before the
  raise — `FileNotFoundError` (doesn't exist), `NotADirectoryError` (is not a directory), `PermissionError` (is not
  writable).

## Verified invariants

Pinned by `probes/verify_wrk_config.py` (15 checks) + `test_wrk_config.py` (14 tests, 3 classes).

- Source shape: the `__all__` name, the factory name "CONFIG", the module callables, the 5 privates — probe section A.
- The loaded state: `ctx.cfg` a LMConfig, name round-trip, `use_cache` True from the config, `ctx.config_checksum` ==
  the sha3_256 of `model_dump_json(indent=4)` (probe B3/B4/B6/B6b; the fingerprint is re-derived independently from the
  live cfg).
- The no-cache state: NO `rlmwf_*` file in the base dir after an up (probe B7 + `test_no_cache_file_written`), and no
  file-write idiom in the module source (probe E5).
- The repeat-run behaviour: the second up is a pure load with a STABLE fingerprint (probe C1), the `_down` reset (cfg,
  use_cache, config_checksum — probe C3).
- The failure behaviour: the invalid json5 → `ValueError` (json5 0.15.0 raises a plain ValueError), the base_dir gates
  with the precise OS types (the a-file override → `NotADirectoryError` in the FACADE `__init__`, the a-file from
  the JSON → the worker's own gate, the not-writable → `PermissionError`, the missing → `FileNotFoundError`) —
  `TestLMWorkerConfigBaseDir`.
- The integration: the bare (un-injected) context keeps the no-op closure lambda (probe E4a), `rlm_00.json` is NOT plain
  JSON (json5 load-bearing, probe E6), the down log line (probe E7).

## Open issues

None.

## Conventions

- The injected machine closures are the naming authority — the worker does no path arithmetic of its own.
- `json5` is a declared dependency — the config fixture `rlm_00.json` is JSON5 with comments.
- `hashlib` stays imported (the fingerprint) — but the module writes NOTHING (probe E5 pins it).
- The test artifacts follow the standard idiom (`build/tmp`, `CUSTOM_TMP_BASE` from `reversi.test.paths`).
- `@validate_call` on the public factory (house convention).

## Integration

- The CONFIG level of the LM pipeline: the facade (`logistic_model.py`) instantiates `Worker` and the machine; this
  module provides the level's `_up`/`_down`.
- Consumes `hlp_config_schemas` (the domain) and `state_machine.Worker`; publishes `ctx.cfg` / `ctx.use_cache` /
  `ctx.config_checksum` that the later workers read (the fingerprint is consumed by `wrk_save` (EMBEDDED in the v2 model
  file) and by `hlp_analytics` — the report line).
- The configuration PROVENANCE (the normalized dump + the checksum) is EMBEDDED by the SAVE level in the v2 model file
  (wrk_save.md).
- Test fixture: `test/reversi/data/rlm_00.json` (JSON5).
