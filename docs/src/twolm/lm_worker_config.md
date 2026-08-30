# twolm/lm_worker_config.py

Analysis date: 2026-07-22 — analysis session 21.

The CONFIG worker of the RLM pipeline. It loads the RLM JSON5 config file, validates it
into a pydantic model, stores a checksummed copy in the per-worker cache slot, and
exposes the resulting model (and the `use_cache` flag) on the context for the workers
that follow. D-076 enabled it in the pipeline (the first non-SENTINEL level) and fixed
its cache naming.

## Suite status (session 21)

- `test_lm_worker_config`: 14/0/0 (Roberto's new file; two path typos `py/` → `src/`
  and a schema-complete validation payload fixed in the D-076 commit, with his
  knowledge)
- Full discover: 496 tests, 52 skipped under `SKIP_REGAB_DB=1`, GREEN

## State per Roberto

Pipeline-in-progress: CONFIG is the second active level (SENTINEL → CONFIG). The next
worker (POSITIONS) is analyzed in a dedicated round, together with `rlm_config_schemas`.

## Architecture

- `lm_worker_config() -> Worker` (L151-153): factory returning
  `Worker("CONFIG", _up, _down)`.
- `_up` (L49-61): log → `_load` → `_validate` → INFO name/description/base_dir →
  `ctx.use_cache = cfg.use_cache` → `ctx.cfg = cfg` → "stored to cache file." log →
  `_store_to_file`.
- `_down` (L63-66): "Clearing configuration..." (ERROR) → `ctx.cfg = None`,
  `ctx.use_cache = None`.
- `_load` (L68-78): `json5.load` (UTF-8), DEBUG log of the file object, optional
  `ctx.base_dir_override` applied to the raw dict before
  `ReversiLogisticModelConfig(**raw)`.
- `_validate` (L80-81): only calls `_validate_base_dir`.
- `_validate_base_dir` (L83-96): three RuntimeError gates (exists / is_dir / writable).
- `_store_to_file` (L98-141): the cache write/verify logic (see below).

## Cache flow (verified)

`_store_to_file` is a self-contained load-or-store implementation:

- `cache_file_path = cfg.base_dir / f"{cfg.cache_files_prefix}{level_name}"` where
  `level_name` is the `.name` of the injected closure result — the D-076 fix. The
  schema documents `cache_files_prefix` as a *filename* prefix, so the physical file is
  flat: `base_dir/rlmwf_01_CONFIG.dat` (probe B7-B9).
- Sidecar `<dat>.SHA3-256` containing the bare hex digest (no binio basename column) of
  `cfg.model_dump_json(indent=4)` (B10-B12).
- First run: dat missing → write both. Repeat run: dat present → sidecar must exist
  ("is missing"), on-disk digest recomputed in 8192-byte chunks and compared to the
  stored one ("not matching" → RuntimeError), then current-vs-stored: identical → no-op
  (C1-C2), different → rewrite (C4).
- `ctx.use_cache` is never consulted by this function (E5): caching is unconditional.

## Issues (awaiting ruling)

### R1 — Cache-flow consistency: ad-hoc reimplementation vs. the D-072 standard

The CONFIG worker does not use `cache_manager_load_or_compute` / the binio sidecar API
that D-072 standardized for the rest of the cache flow. Consequences, probe-verified:

- Asymmetry: binio's `verify_sha3_256_sidecar` CAN read the worker's bare-hex sidecar
  (it parses the first token; B13), but the worker's full-content `.strip()` comparison
  CANNOT read a binio-format sidecar (`"<hex>  <basename>\n"` → spurious "not
  matching"; C7). Two cache writers in one codebase, two incompatible sidecar formats.
- Corruption semantics differ from the house standard: cache_manager deletes a
  failing cache and recomputes (D-071 R2); the worker RAISES (its
  `test_cache_corruption_raises_runtime_error` pins the crash). Adopting the cache
  manager would change that test's semantics (WARN + recompute instead of error).
- `use_cache` (present in the config and copied to the context, E probe) is never
  consulted: the worker always writes the cache files.

Options: (a) adopt `cache_manager_load_or_compute` + binio sidecars and gate on
`use_cache` (changes the corruption-test semantics); (b) keep the ad-hoc
implementation and document the divergence (bare-hex format, unconditional caching);
(c) keep the ad-hoc implementation but at least write the sidecar in binio format and
parse it binio-style (keeps the raise semantics, removes the asymmetry).

### R2 — Prefix semantics: closure join vs. filename prefix (cross-ref, deferred)

The SM-injected closure does `Path(prefix) / f"{level:02}_{worker}.dat"` (D-069 M8),
which makes `rlmwf_` a directory component; the worker now concatenates instead.
Latent in the next worker: `lm_worker_positions.py` L58-59 passes the injected
`ctx.get_cache_file_full_path_for_current_level()` directly into
`cache_manager_load_or_compute` — that is the `rlmwf_/02_POSITIONS.dat` subdirectory
form, and `cache_manager` performs no `mkdir` anywhere → the same `FileNotFoundError`
on first write. Resolution belongs to the lm_worker_positions round (per-worker
concatenation mirroring the worker, or a shared helper).

### R3 — Exception types in `_validate_base_dir`

All three gates raise `RuntimeError` (with distinct, logged messages). The
`logistic_model.py` helpers use the precise OS types (`FileNotFoundError` /
`NotADirectoryError` / `PermissionError`). Options: (a) map to the precise types;
(b) keep `RuntimeError` as the worker-level "validation failed" type.

## Minor notes (awaiting ruling)

- M1 (L71): the DEBUG log prints the file object `f` (repr `<_io.TextIOWrapper ...>`),
  not `ctx.config_file_path`.
- M2 (L60): "stored to cache file." is logged BEFORE `_store_to_file` actually runs.
- M3 (L91, L96): trailing whitespace after the two `raise RuntimeError(...)` lines.
- M4 (L151): the public factory `lm_worker_config()` has no `@validate_call` (house
  convention D-068 M11: gate every public function). `Worker.__init__` is already
  gated, so the practical delta is zero — convention only.
- M5 (L32): `import hashlib` is redundant only if R1(a)/(c) is adopted (the binio API
  replaces the local hashing).

## Test notes (test_lm_worker_config.py, awaiting ruling)

- T1: `tempfile.mkdtemp(dir='./build/tmp')` is CWD-relative and does not create the
  base — breaks outside a CWD that has `build/tmp`, and diverges from the D-065 house
  idiom. Fix: `Path(__file__).resolve().parents[3] / "build" / "tmp"` + setUpClass
  mkdir + defensive tearDown (the test_cache_manager pattern).
- T2: `test_invalid_json_syntax` pins `Exception` — too broad to catch a regression to
  a different failure type. Pin `json5.JSON5Exception`.
- T3: the `_down` reset is unpinned: `test_move_down` asserts step/name but not
  `context.cfg is None` / `context.use_cache is None` (the C3 probe behaviour).
- T4: the bare-hex sidecar format is unpinned (probe B10-B12). A pin is worth adding —
  or replacing, if R1 changes the format.
- T5 (report-only): header grammar "How to use the unit tests lm_worker_config
  module." follows the pattern of the other test files; T6 (report-only):
  `test_cache_skipped_on_identical_second_run` compares mtime, which is coarser than
  content equality (already asserted).

## Integration notes

- D-074 R1: `ctx.cfg` must be set before any injected `get_cache_file_*_for_current_level`
  closure is called — the closures read `getattr(self.context, 'cfg')` and raise
  `AttributeError` without it (E4a/E4b). The pipeline ordering (CONFIG before the
  cache-consuming workers) is load-bearing.
- D-076: the SM gate split means pydantic ValidationErrors raised here (invalid
  config data, base_dir problems) propagate as domain errors to the orchestrator
  instead of being mis-converted to the gate's `TypeError` (E1; D-060).
- `use_cache` is copied from the config onto the context (B6) but never consumed in
  this module — it is the intended switch for the later cache-consuming workers
  (R1 scope).
- `rlm_config_schemas.py` is the config domain: field-by-field analysis deferred to
  its own round (Roberto's order: positions + schemas after this one).

## Appendix — line reference

153 lines, as of the D-076 commit.

- L28-41: imports (json5 L31, hashlib L32)
- L45: `__all__`
- L49-61: `_up`
- L63-66: `_down`
- L68-78: `_load`
- L80-81: `_validate`
- L83-96: `_validate_base_dir` (trailing whitespace L91, L96)
- L98-141: `_store_to_file` (naming fix L102-110)
- L151-153: `lm_worker_config()`
