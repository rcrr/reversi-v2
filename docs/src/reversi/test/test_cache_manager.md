# reversi/test/test_cache_manager.py
The cache_manager unit suite — 3 classes / 22 tests + 1 base + the `DataWithChecksum` / `DataWithBrokenChecksum`
duck-typed helpers, no DB (~0.05 s).

## Coverage

| class (line) | tests | what it pins |
|---|---|---|
| `TestChecksumHelpers` (L114, over `BaseCacheTestCase` L97 — the mkdtemp + the `CUSTOM_TMP_BASE`-anchored paths via `reversi.test.paths`) | 8 | a binio-written sidecar verifies through `_verify_checksum`, the legacy bare-hex sidecar still verifies (binio's first-token parser), missing sidecar → False (`FileNotFoundError`), mismatched well-formed digest (`"0" * 64`) → False, malformed (non-hex → `BinaryFormatError`) + undecodable (`UnicodeDecodeError`) → False never raising, `_delete_cache_files` removes both files, double delete no-raise (idempotent), the sidecar content is exactly binio's `sha3_256sum` line `<hex>  <basename>\n` |
| `TestCacheManagerPipeline` (L191) | 13 | the 4 steps + success, end to end: step 0 (`is_allowed=False` with a pre-existing file) computes + still writes data + valid sidecar (INFO pinned); step 1 (missing file) computes + stores; step 2 (wrong sidecar — and the missing-sidecar variant) deletes both, the WARN "Checksum validation failed ... (sidecar missing or mismatched)" pinned, recomputes + re-stores, new sidecar verifies; step 3a (`load_fn` raises IOError) deletes both, ERROR "Failed to load or validate cache file ... Disk read error. Recomputing." pinned; step 3b (`validate_fn` False, and the raising-validator variant) same; success returns the loaded object (identity), load called once, compute/store NOT called, INFO pinned; all failure paths: `cache_hit=False`, 3rd element `None` (`assertIsNone` on all 6 pipeline tests) |
| `TestValidateCallCoercion` (L598) | 1 | a `str` `cache_path` is coerced to `Path` by `@validate_call` and the inner store_fn observes a Path (the flow then dies in the framework's sidecar write with FileNotFoundError) |

## Goldens pinned

- No float goldens (the suite is behavioural): the pins are the exact WARN/ERROR/INFO message strings, the
  `(False, data, None)` / `(True, data, checksum)` tuple shapes, the on-disk effects (data + `sha3_256sum` sidecar after
  every (re)compute), and the exception mapping of `_verify_checksum`.
- The duck-typed data checksum pins (6 tests over `DataWithChecksum` L74 / `DataWithBrokenChecksum` L85): a data object
  with `compute_sha3_256_hash()` → its digest is the 3rd element on BOTH the compute path and the load path; missing
  method → `None`; non-callable attribute → `None` (no exception); the method RAISING on the load path → caught by the
  step-3 try/except, delete + recompute, ERROR carries the exception text.

## Conventions

- No PERF gates (~0.05 s), no DB gate (pure file I/O in `mkdtemp` dirs).
- `CUSTOM_TMP_BASE` is imported from `reversi.test.paths` (the per-file `__file__` derivation is gone).

## Integration

- Module under test: `cache_manager.md` — the load-or-compute engine behind every rlmwf cache file.
- The probe retains V2 ×3 + V9c + V10b + V16 (6 checks); the rest are covered here as named tests.
