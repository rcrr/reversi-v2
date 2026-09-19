# reversi/test/test_hlp_indexes.py
The unit suite of the hlp_indexes domain module. 5 classes / 14 tests / no PERF — all file I/O MOCKED
(`reversi.lm.hlp_indexes.binio` patched): no temp dirs, no DB, no gates.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestLMIndexes` | 3 | `test_init_success` (the 3 attributes, `isinstance np.ndarray` + the uint32 dtype, `assertIs(obj.indexes, DUMMY_INDEXES)` — the by-reference storage contract (pinned in 3 tests: the init, the load and the compute)); `test_init_fails_with_invalid_hash_type` (a non-str `feature_set_hash` = 12345 → the precise pydantic `ValidationError`); `test_init_fails_with_invalid_indexes_type` (a list of lists → the `IndexArray` rejection, with `rds_checksum=` present so the invalid indexes is what's under test) |
| `TestHlpIndexesStoreToFile` (binio mocked) | 2 | `test_store_to_file_success` (`BinaryWriter` instantiated with `Path(filename), compressed=True` + the exact 4-call sequence — `write_header(desc, 1)`, `write_string` ×2, `write_array` — both `assert_has_calls(any_order=False)` and the full `method_calls ==`); `test_store_to_file_accepts_path_object` (a `pathlib.Path` filename passes through unchanged, the `compressed=True` pin as well) |
| `TestHlpIndexesLoadFromFile` (binio mocked) | 5 | `test_load_from_file_success_with_checksum` (the default `checksum=True` calls `verify_sha3_256_sidecar` exactly once + the `BinaryReader` is opened with `compressed=True` + the round-trip fields — NOTE: both `read_string` mocks return the same "stored_hash", so `rds_checksum` is never asserted here; probe B4 covers the rds field); `test_load_from_file_success_without_checksum` (`checksum=False` → `assert_not_called` on the sidecar verify); `test_load_from_file_checksum_mismatch` (RuntimeError + "checksum file signature doesn't match"); `test_load_from_file_invalid_description` (RuntimeError + "not a proper"); `test_load_from_file_invalid_version` (RuntimeError + "version is not consistent") |
| `TestHlpIndexesCompute` (NO mock — a fake 'model' object) | 1 | `test_compute_success`: a MagicMock ctx; pins `compute_indexes` called once with the ctx positions ("dummy_positions" — a string, the mock absorbs it), the resulting `feature_set_hash`, and `assertIs` on the returned array |
| `TestHlpIndexesIsCacheConsistent` | 3 | `test_is_cache_consistent_returns_true` (both fields "identical_hash" → True); `test_is_cache_consistent_returns_false` (ONLY the feature_set_hash differs — "live_hash" vs "outdated_cached_hash", rds identical → False); `test_is_cache_consistent_returns_false_rds_differs` (ONLY the rds_checksum differs, roles swapped → False). Both single-field branches pinned |

## Goldens pinned

- The shared dummy: `DUMMY_INDEXES = np.zeros((2, 2), dtype=np.uint32)` across the whole file.
- The hash strings: "identical_hash" / "live_hash" / "outdated_cached_hash" / "stored_hash" / "valid_hash".
- The 3 RuntimeError message substrings (the precise pydantic `ValidationError` for the two init rejections).

## Conventions

- The full binio mock: every file I/O is patched — the suite never touches the filesystem, the temp-dir machinery is
  absent by design.
- The precise `ValidationError` pins (no broad `assertRaises(Exception)`).
- English-only comments (AGENTS.md rule 4).
- The known gap (the `rds_checksum` value never asserted on the load path — the mock returns the same string twice)
  stays probe-covered (B4) and is left as-is.

## Integration

- Independent of the pipeline: no model, no DB, no cache file — the per-function pin of the store/load contract + the
  compute / is_cache_consistent logic.
- The 52-call probe re-derives the store/load round-trip with REAL files (B3-B8) and the pipeline integration (C2-C7);
  the step-3 class c deletions (B1, B9-B11, B14, C1, C6a/C6b) all point at tests in this file or in test_wrk_indexes.py.
