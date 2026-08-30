# twolm/lm_worker_config.py

Analysis date: 2026-07-22 — analysis session 21 (D-077); fix
campaign D-078 applied 2026-08-30 (session 21).

The CONFIG worker of the RLM pipeline. It loads the RLM JSON5 config
file, validates it into a pydantic model, stores a checksummed copy in
the per-worker cache slot, and exposes the resulting model (and the
`use_cache` flag) on the context for the workers that follow. D-076
enabled it in the pipeline (the first non-SENTINEL level) and fixed
its cache naming; D-078 applied Roberto's calls on the analysis
(R2 machine-level prefix fix, R3 precise exception types, M1-M5,
T1-T4; R1 deferred to the full-pipeline review, I-011).

## Suite status (session 21, post D-078)

- `test_lm_worker_config`: 14/0/0 (Roberto's file; D-076 fixed 2 path
  typos + completed the validation payload; D-078 applied the T1-T4
  campaign)
- Full discover: 496 tests, 52 skipped under `SKIP_REGAB_DB=1`, GREEN

## State per Roberto

Pipeline-in-progress: CONFIG is the second active level (SENTINEL →
CONFIG). D-078 ruling on the cache flow (R1): **leave it as-is** —
the cache_manager-style load-or-compute does not fit a JSON file, the
CONFIG step may not need a cache at all, and the whole question is
revisited **when the full pipeline is complete** (the
"storicizzazione" idea — a historical copy of the config that
generated a model — is recorded at I-011).

## Architecture

- `lm_worker_config() -> Worker` (L150-153): factory returning
  `Worker("CONFIG", _up, _down)`; D-078 M4: now
  `@validate_call(config=ConfigDict(arbitrary_types_allowed=True))`.
- `_up` (L51-63): log → `_load` → `_validate` → INFO
  name/description/base_dir → `ctx.use_cache = cfg.use_cache` →
  `ctx.cfg = cfg` → `_store_to_file` → "stored to cache file." log
  (D-078 M2: now AFTER the store).
- `_down` (L65-68): "Clearing configuration..." (ERROR) →
  `ctx.cfg = None`, `ctx.use_cache = None`.
- `_load` (L70-80): `json5.load` (UTF-8), DEBUG log of the config
  path (D-078 M1: was the file object repr), optional
  `ctx.base_dir_override` applied to the raw dict before
  `ReversiLogisticModelConfig(**raw)`.
- `_validate` (L82-83): only calls `_validate_base_dir`.
- `_validate_base_dir` (L85-98): three gates, D-078 R3 precise OS
  types: `FileNotFoundError` ("doesn't exist"), `NotADirectoryError`
  ("is not a directory"), `PermissionError` ("is not writable");
  each logged at ERROR before the raise; messages unchanged.
- `_store_to_file` (L100-147): the cache write/verify logic (below).

## Cache flow (verified, D-078 state)

`_store_to_file` is a self-contained load-or-store implementation
(kept ad-hoc per the D-078 R1 ruling):

- `cache_file_path = ctx.get_cache_file_full_path_for_current_level()`
  — the injected machine closure, which does the naming:
  `Path(f"{cache_files_prefix}{level:02}_{name}.dat")` (filename-
  prefix concatenation, D-078 — the machine-level R2 fix), under
  `cfg.base_dir`. The physical file is flat:
  `base_dir/rlmwf_01_CONFIG.dat` (probe B7-B9).
- Sidecar `<dat>.SHA3-256` containing the bare hex digest (no binio
  basename column) of `cfg.model_dump_json(indent=4)` (B10-B12).
- First run: dat missing → write both. Repeat run: dat present →
  sidecar must exist ("is missing" → RuntimeError), on-disk digest
  recomputed in 8192-byte chunks and compared to the stored one
  ("not matching" → RuntimeError), then current-vs-stored: identical
  → no-op (C1-C2), different → rewrite (C4).
- `ctx.use_cache` is never consulted by this function (E5): caching
  is unconditional.

## Issues — disposed (D-078)

- **R1 — RESOLVED AS DEFERRED.** The ad-hoc cache flow (hashlib +
  manual 8192-chunk verify + bare-hex sidecar) stays. The
  cache_manager/binio standard (D-072) is revisited only when the
  full pipeline is complete. Verified asymmetry on record (probe):
  binio's verifier CAN read the worker's bare-hex sidecar (first
  token), the worker's full-content compare CANNOT read a binio-
  format sidecar (C7). Corruption RAISES here (pinned) vs
  cache_manager's delete + recompute. `use_cache` is copied to the
  context (B6) but never consumed in this module. Roberto's
  "storicizzazione" idea → I-011.
- **R2 — RESOLVED AT MACHINE LEVEL.** The prefix semantics clash
  (SM closure pathlib join vs the schema's "Filename prefix") lived
  in the ONE shared injected closure, so it would have recurred in
  every cache-consuming worker — fixed once in
  `state_machine._get_cache_file_path` (D-078: verbatim
  filename-prefix concatenation; replaces the D-069 M8 join). This
  worker's D-076 per-worker concatenation was replaced by a direct
  use of the injected full-path closure (uniform with
  lm_worker_positions). The latent `rlmwf_/02_POSITIONS.dat`
  subdirectory + no-mkdir trap for lm_worker_positions is thereby
  gone before that worker is enabled.
- **R3 — FIXED.** `_validate_base_dir` now raises the precise OS
  types (FileNotFoundError / NotADirectoryError / PermissionError)
  as in the logistic_model helpers; messages unchanged; the
  not-writable test updated to `PermissionError`.

## Minor notes — disposed (D-078)

- M1 (was L71): FIXED — the DEBUG log prints
  `ctx.config_file_path`, not the file object repr.
- M2 (was L60): FIXED — "stored to cache file." logged after
  `_store_to_file`.
- M3 (was L91/L96): FIXED — trailing whitespace removed.
- M4 (was L151): FIXED — `@validate_call` on the public factory
  (house convention D-068 M11).
- M5 (L32): CLOSED AS KEEP — `import hashlib` stays, per the R1
  ruling (the ad-hoc flow is kept).

## Test notes (test_lm_worker_config.py, D-078)

- T1 FIXED: the D-065 idiom on all 4 classes (`CUSTOM_TMP_BASE =
  Path(__file__).resolve().parents[3] / "build" / "tmp"` +
  setUpClass mkdir + `tempfile.TemporaryDirectory(dir=...)` FIRST in
  setUp + defensive tearDown); the dead `shutil` import removed; a
  stray per-test `tempfile.mkdtemp(dir='./build/tmp')` inside
  `test_base_dir_is_a_file_raises_error` removed — it leaked a tmp
  dir on every run (found via build/tmp leftovers).
- T2 FIXED: the bare-`Exception` pin replaced with `ValueError` —
  note: json5 0.15.0 raises a plain `ValueError` on a syntax error;
  this version of the module has NO `JSON5Exception` attribute, so
  the originally proposed `json5.JSON5Exception` pin was not usable.
- T3 FIXED: the `_down` reset pinned in `test_move_down`
  (`context.cfg is None` / `context.use_cache is None`).
- T4 FIXED: the bare-hex sidecar format pinned in
  `test_cache_files_created_on_first_run` (content ==
  `sha3_256(.dat bytes).hexdigest()`, no basename column).
- T5/T6 report-only, unchanged (header grammar; mtime coarseness in
  the skip-identical test — the content assertion already pins it).

## Integration notes

- D-074 R1: `ctx.cfg` must be set before any injected
  `get_cache_file_*_for_current_level` closure is called — the
  closures read `getattr(self.context, 'cfg')` and raise
  `AttributeError` without it (E4a/E4b). The pipeline ordering
  (CONFIG before the cache-consuming workers) is load-bearing.
- D-076: the SM gate split means pydantic ValidationErrors raised
  here (invalid config data) propagate as domain errors to the
  orchestrator instead of being mis-converted to the gate's
  `TypeError` (E1; D-060). (The base_dir gates now raise the
  precise OS types, D-078 R3 — also domain errors, propagated.)
- `use_cache` is copied from the config onto the context (B6) but
  never consumed in this module — it is the intended switch for the
  later cache-consuming workers (R1 / I-011 scope).
- `rlm_config_schemas.py` is the config domain: field-by-field
  analysis deferred to its own round (Roberto's order: positions +
  schemas after this one).

## Appendix — line reference

153 lines, as of the D-078 commit.

- L28-41: imports (json5 L31, hashlib L32, pydantic L37)
- L47: `__all__`
- L51-63: `_up` (M2 store-then-log)
- L65-68: `_down`
- L70-80: `_load` (M1 path log)
- L82-83: `_validate`
- L85-98: `_validate_base_dir` (R3 precise OS types)
- L100-147: `_store_to_file` (full-path closure L108)
- L150-153: `lm_worker_config()` (M4 `@validate_call`)
