# twolm/test/test_rlm_wmaps.py
The unit suite of the rlm_wmaps domain module (Roberto's file,
brought in with the 73b4342 WMAPS enablement; the D-087 T2/T3/T4
+ T9 + T10 campaign). 4 classes / 13 tests / no PERF — no DB, no
gate: the compute tests use a handcrafted mock ctx, the IO tests
use a REAL temp dir under the shared `CUSTOM_TMP_BASE` (the D-085
idiom, applied per Roberto in D-086 before the campaign).
> State: D-087 · ded27eb · 2026-08-31 · suite 13/0/0

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestRLMWmapsCompute` (no mocks — a handcrafted `SimpleNamespace` ctx over a 4×3 uint32 pindexes, 2 features: F0 n_instances=1 n_configurations=3, F1 n_instances=2 n_configurations=2) | 2 | `test_compute_with_fallback` (cut_off=2): the full output pin — w len 4, iwmap `[1,0,0,2,3]` semantics (per-feature offsets), wmap 4 rows, wf 2 rows; the below-cutoff configurations fold into the single fallback weight per feature (config_id −1), the above-cutoff ones get their own weights, the per-feature ranges in feature_w_ranges. `test_compute_without_fallback` (cut_off=0): the no-fallback branch — w len 5, wf shape (0,3), fwr[0,0] = −1 (mock-only: `frequency_cut_off` is PositiveInt, so cut_off=0 is unreachable via the real config) |
| `TestRLMWmapsCacheConsistent` (a `SimpleNamespace` ctx, cut_off=5) | 3 | the 2-field metadata compare — True when both rlm_indexes_checksum and cut_off match; False when ONLY the hash differs; False when ONLY the cut_off differs (both single-field branches pinned) |
| `TestRLMWmapsIO` (real temp dir under `CUSTOM_TMP_BASE`, the D-085 idiom) | 6 | `test_store_and_load_cycle` (store → load with `checksum=False` both sides — all 8 fields round-trip, cut_off=42, the float32 dtype preserved); `test_compute_sha3_256_hash_golden` (the duck-typed hash on the known IO object — the golden below); `test_load_with_valid_sidecar` (store → `binio.write_sha3_256_sidecar` → load `checksum=True` round-trips); `test_load_with_mismatched_sidecar` (a byte-flip in the .dat → RuntimeError "checksum file signature doesn't match"); `test_load_rejects_wrong_description` (a wrong-header file → RuntimeError "not a proper ..."); `test_load_rejects_version_mismatch` (version 2 → RuntimeError "version mismatch") |
| `TestRLMWmapsInit` | 2 | `test_init_accepts_valid_arrays` (the sanity constructor); `test_init_fails_with_invalid_cut_off_type` (a string `cut_off` → the precise pydantic `ValidationError`, the D-084 T3 pattern) |

## Goldens pinned

- The `compute_sha3_256_hash` golden:
  `12c3344ec23c798d7b35eb6eae01034b29ee5c539bfb2018ca2eabc73c86
  1dfa` (the D-087 T10 addition, the D-081 golden philosophy).
- The cut_off literal 42 on the store/load cycle; the handcrafted
  4×3 pindexes fixture + the expected iwmap `[1,0,0,2,3]`.
- The 3 RuntimeError message substrings + the precise
  `ValidationError` for the init rejection.

## Conventions

- The D-085 paths idiom on the IO tests: real temp dir under the
  shared `CUSTOM_TMP_BASE` + defensive tearDown (the CWD
  `mkdtemp` is gone) — unlike test_rlm_indexes, the file I/O is
  REAL here, not mocked.
- The precise `ValidationError` pins (no broad
  `assertRaises(Exception)`).
- English-only comments (the D-087 T3 leftover-generation comment
  removed, AGENTS.md rule 4).

## Integration

- Independent of the pipeline: no model, no DB, no cache file —
  the per-function pin of the compute semantics (both branches),
  the consistency (both single-field branches), the store/load
  contract (cycle + golden + the 3 error paths), the init
  validation.
- The LIVE golden content (the rlm_01 pipeline run vs the
  literals) lives in test_lm_worker_wmaps.py
  (`TestLMWorkerWmapsExactValues`) — the single source of truth
  after the step-3 class c deletions of the former probe E tier.
