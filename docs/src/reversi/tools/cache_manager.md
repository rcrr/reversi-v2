# reversi/tools/cache_manager.py
A small, domain-agnostic caching utility: one public function orchestrates a 4-step validation pipeline for "load cached
result or recompute" around injected business-logic callbacks — the load-or-compute engine behind every rlmwf cache
file, and the domain module importing `reversi.tools.state_machine` (`Relevance`) + `reversi.tools.binio` (the sidecar
API, no cycle). House `@validate_call` gate: `cache_path` coerced `str` → `Path`.

## API

| name | contract |
|---|---|
| `cache_manager_load_or_compute(...)` | The only public API. 4-step pipeline (below). Returns `(cache_hit: bool, data: T, data_checksum: str \| None)` |
| `_verify_checksum(path)` | Step 2: thin wrapper over binio's `verify_sha3_256_sidecar`; maps `FileNotFoundError` / `BinaryFormatError` / `UnicodeDecodeError` → `False` (a bad sidecar invalidates, never crashes) |
| `_delete_cache_files(path)` | Unlinks data + sidecar, both `missing_ok=True` (idempotent) |
| `_compute_and_store(...)` | The shared "compute" tail: DEBUG log, `compute_fn()`, data checksum, `store_fn(data, path)`, binio `write_sha3_256_sidecar`, DEBUG logs (the compute-path process lines at DEBUG — the LOG wave; the outcome lines of `cache_manager_load_or_compute` stay INFO/WARN/ERROR); returns `(False, data, data_checksum)` |
| `_compute_sha3_256_hash(data)` | Duck typing: if the data object has a callable `compute_sha3_256_hash` attribute, call it and return the result, else `None` |
| `SHA3_256_CHECKSUM_SUFFIX` · `ComputeFunc / LoadFunc / StoreFunc / ValidateFunc / LoggerFunc` | `".SHA3-256"` sidecar suffix constant; the 5 callback type aliases |

## Architecture

- The helpers: `_verify_checksum` (the binio call + the exception mapping); `_delete_cache_files` (both unlinks with
  `missing_ok=True`); `_compute_sha3_256_hash` (the getattr duck-typing, the callable gate, the None case);
  `_compute_and_store` (the shared compute tail: the DEBUG log, compute, the data checksum, store, the sidecar, return).
- `cache_manager_load_or_compute` (the validate_call gate + the pipeline): Step 0 → Step 1 → Step 2 (the checksum
  gate) → Step 3 (the try wraps load + checksum + validate; the False branch) → success.

Pipeline (steps 0-3, per the docstring):

1. **Step 0 — allowed?** `is_allowed` false → compute tail, which **also stores** — INTENTIONAL: a cache-disabled run
   still transcribes the result (it warms the cache; pinned in docstring + test).
2. **Step 1 — present?** missing → compute tail.
3. **Step 2 — consistent?** sidecar missing/mismatching → WARN "Checksum validation failed ... (sidecar missing or
   mismatched)", delete both, compute tail.
4. **Step 3 — valid?** `load_fn` + the duck-typed data checksum + `validate_fn` in ONE try/except (a raising validator
   is indistinguishable from — and behaves as — a load failure) → ERROR "Failed to load or validate cache file ...",
   delete both, compute tail; `validate_fn` False (no exception) → WARN "Application data validation failed ...",
   same tail.
5. **Success** → INFO, `(True, loaded_data, loaded_data_checksum)`. All failure paths converge on `_compute_and_store` —
   the caller always gets fresh, stored, checksummed data.

The two checksums (do not confuse): the FILE checksum (the sidecar — binio's `sha3_256sum` format; legacy bare-hex still
verifies via binio's first-token parser) and the DATA checksum (the 3rd element — the object's content hash via the
duck-typed `compute_sha3_256_hash()`, `None` when absent).

## Verified invariants

Pinned by the 6-check `probes/verify_cache_manager.py` + the 22-test suite (no DB). The probe keeps V2 ×3 (sidecar
naming), V9c (step-3b WARN), V10b (success identity — the SAME object `load_fn` returned), V16 (`logger_fn` receives
`(Relevance, str)`).

- The 4 steps + success (TestCacheManagerPipeline, 13): step 0 forces computation AND still writes data + valid sidecar
  (the warm-cache intent); step 1 (missing) computes + stores; step 2 (mismatch + missing-sidecar) deletes both, the
  the step-2 WARN, recomputes + re-stores with a verifying sidecar; step 3a (`load_fn` raises) → ERROR with the
  exception text;
  step 3b (`validate_fn` False or RAISING) same; success → `(True, data)`, load once, compute/store not called.
- The checksum helpers (TestChecksumHelpers, 8): a binio-written sidecar verifies through the wrapper, the legacy
  bare-hex one still verifies (compat), missing / mismatched / malformed (`BinaryFormatError`) / undecodable
  (`UnicodeDecodeError`) all map to `False` never raising, delete removes both files idempotently, the sidecar content
  is exactly binio's `sha3_256sum` line.
- The duck-typed data checksum (6): `compute_sha3_256_hash()` → its digest is the 3rd element on BOTH the compute and
  the load path; missing method → `None`; non-callable attribute → `None`; RAISING on the load path → caught by the
  step-3 try/except, delete + recompute, ERROR carries the text.
- The `@validate_call` gate (TestValidateCallCoercion): a `str` `cache_path` is coerced to `Path` and works (the inner
  store_fn observes a Path; the flow then dies in the sidecar write with FileNotFoundError).

## Open issues

None.

## Conventions

- `logger_fn` takes `(Relevance, str)` — the natural binding is the `log_event` method `StateMachine.__init__` injects
  into the shared `Context`.
- The binio import trade-off: importing reversi.tools.binio buys the exact-binio sidecar naming + content, cross-process
  sidecars verifying, legacy bare-hex keeping valid (zero cache invalidation).
- No PERF gates: 22 tests in ~0.05 s.

## Integration

- Every rlmwf cache level (SU_ANALYSIS, POSITIONS, INDEXES, WMAPS, DESIGN_MTR, GENERATE, VLD_POSITIONS) runs this
  pipeline with its own callbacks — the worker docs pin the level-specific goldens; this module is the engine.
- The step-2 checksum call is the single entry into binio's `verify_sha3_256_sidecar` (the sidecar format of the whole
  cache system — binio.md); the `data_checksum` 3rd element is published on the ctx by the worker (`ctx.rds_checksum`,
  `ctx.hlp_indexes_checksum`, …) and reaches the downstream comparisons through that stored metadata, not through the
  `validate_fn`.
