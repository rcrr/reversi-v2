# twolm/lm_worker_config.py
The CONFIG worker of the RLM pipeline — the second level, the first
non-sentinel. It loads the RLM JSON5 config file, validates it into
the rlm_config_schemas domain model, stores a checksummed copy in
the per-worker cache slot, and publishes the model (and the
`use_cache` flag) on the context for the workers that follow.
> State: D-078 · d6a850e · 2026-08-30 · suite 15/0/0

## API

| name | contract |
|---|---|
| `lm_worker_config()` | the only `__all__` name; `@validate_call` factory returning `Worker("CONFIG", _up, _down)` |
| `_up` / `_down` | the worker callables (module-level privates, 6 with `_load`, `_validate`, `_validate_base_dir`, `_store_to_file`) |

## Architecture

- `_up`: log → `_load` → `_validate` → INFO (name/description/
  base_dir) → `ctx.use_cache = cfg.use_cache` → `ctx.cfg = cfg` →
  `_store_to_file` → the "stored to cache file." log (AFTER the
  store).
- `_down`: the ERROR "Clearing configuration..." →
  `ctx.cfg = None`, `ctx.use_cache = None`.
- `_load`: `json5.load` (UTF-8) of `ctx.config_file_path` with the
  DEBUG log of the path; an optional `ctx.base_dir_override` is
  applied to the raw dict before `ReversiLogisticModelConfig(**raw)`.
- `_validate` → `_validate_base_dir`: three gates with the precise
  OS exception types, each logged at ERROR before the raise —
  `FileNotFoundError` (doesn't exist), `NotADirectoryError`
  (is not a directory), `PermissionError` (is not writable).
- `_store_to_file`: a self-contained load-or-store (kept ad-hoc,
  the D-078 R1 ruling — see Open issues). The path comes from the
  injected machine closure (the naming authority, D-078): the
  physical file is FLAT, `base_dir/rlmwf_01_CONFIG.dat`. First run
  writes the `.dat` (`cfg.model_dump_json(indent=4)`) + the
  `.SHA3-256` sidecar (bare hex digest of the `.dat`). Repeat run:
  the sidecar must exist (else RuntimeError "is missing"); the
  on-disk digest is recomputed in 8192-byte chunks and compared
  (else "not matching"); identical → no-op, different → rewrite.
  It never consults `ctx.use_cache` — caching is unconditional.

## Verified invariants

Pinned by `probes/verify_lm_worker_config.py` (25 checks) +
`test_lm_worker_config.py` (15 tests, 4 classes).

- Source shape: the `__all__` name, the factory name "CONFIG", the
  module callables, the 6 privates — probe section A.
- The loaded state: `ctx.cfg` a ReversiLogisticModelConfig, name
  round-trip, `use_cache` True from the config — probe B3/B4/B6.
- The cache files: the flat `base_dir/rlmwf_01_CONFIG.dat` + the
  `.SHA3-256` sidecar, no `rlmwf_` subdirectory, the `.dat`
  content == `model_dump_json(indent=4)`, the sidecar == bare hex
  `sha3_256` of the dump, NOT binio format, and binio can still
  READ the bare-hex sidecar — probe B7-B13.
- The repeat-run behaviour: the identical second run leaves mtime
  and content untouched, the `_down` reset, the changed-config
  rewrite — probe C1-C4.
- The failure behaviour: the corrupted `.dat` → RuntimeError
  "not matching", the missing sidecar → "is missing", the
  binio-format sidecar makes the worker verify FAIL (the
  asymmetry) — probe C5-C7.
- The integration: the bare (un-injected) context keeps the no-op
  closure lambda, `use_cache` is absent from the `_store_to_file`
  source, `rlm_00.json` is NOT plain JSON (json5 load-bearing),
  the down log line — probe E4a/E5/E6/E7.
- The moves: up (config loaded, `ctx.cfg` set), down (the reset
  pins), the with-cache no-op, the property round-trips —
  `TestLMWorkerConfig`.
- The validation: invalid json5 → `ValueError` (json5 0.15.0
  raises a plain ValueError), ec out of range / invalid status /
  invalid hex mask → pydantic ValidationError, one constraint per
  test (the payload is schema-complete) —
  `TestLMWorkerConfigValidation`.
- The base_dir gates: the a-file → `NotADirectoryError`, the
  not-writable → `PermissionError` "not writable", the missing →
  `FileNotFoundError` — `TestLMWorkerConfigBaseDir`.
- The cache logic: first-run files at the flat names with the
  bare-hex sidecar, the skip-identical second run, the
  update-on-change, the corruption RuntimeError —
  `TestLMWorkerConfigCacheLogic`.

## Open issues

- **R1 (revisit due, D-078 ruling)** — the ad-hoc cache flow
  (hashlib + the manual 8192-chunk verify + the bare-hex sidecar)
  stays: the cache_manager-style load-or-compute does not fit a
  JSON file, and the CONFIG step may not need a cache at all.
  Revisited when the full pipeline is complete (now met, 15/15);
  the "storicizzazione" idea (a historical copy of the config
  that generated a model) is recorded at I-011.

## Conventions

- The injected machine closures are the naming authority
  (D-078) — the worker does no path arithmetic of its own.
- `json5` is a declared dependency (added for this worker,
  D-076) — the config fixture `rlm_00.json` is JSON5 with
  comments.
- The test artifacts follow the D-065 idiom (`build/tmp`,
  `CUSTOM_TMP_BASE` from `reversi.test.paths`).
- `@validate_call` on the public factory (house convention
  D-069, applied D-078 M4).

## Integration

- The CONFIG level of the RLM pipeline: the facade
  (`logistic_model.py`) instantiates `Worker` and the machine;
  this module provides the level's `_up`/`_down`.
- Consumes `rlm_config_schemas` (the domain) and
  `state_machine.Worker`; publishes `ctx.cfg` / `ctx.use_cache`
  that every later cache-consuming worker reads.
- Test fixture: `src/reversi/test/data/rlm_00.json` (JSON5).
