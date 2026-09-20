# reversi/test/test_hlp_generate.py
The dedicated data-object suite of the hlp_generate module — 4 classes / 16 tests. No DB, no gate, no artifacts — the
SimpleNamespace mock-fixture pattern, as in test_hlp_zed / test_hlp_gradient.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestHlpGenerateCompute` (a `SimpleNamespace` mock ctx: the 3-feature set — Intercept (1 config), Pattern (3 configs, identity principal reference), Mobility (5 configs); `iwmap` offsets [0,1,4,9] with the unseen → −1 fallback slots; `wmap` 4 rows; `w = [0.5, −0.2, 1.0, 3.0]`; `w_checksum "abc654"`; a no-op logger) | 3 | `test_compute_w_dense`: the golden — (9,) float32, INT 0.5, PAT [−0.2, −0.2, −0.2] (config 1 seen; configs 0/2 unseen → the weighted mean (−0.2·10)/10 = −0.2 — the R2 semantics), MOB [1, 1, 2, 3, 3] (clamp + linear interpolation over the 2 seen configs). `test_unknown_category_raises`: category 9 → `RuntimeError` with the exact message "The feature category is unknown: 9". `test_mobility_without_seen_configs_warns_and_zeroes`: an empty-wmap mobility feature → zeros (4,) + exactly one WARN event ("no seen configurations") |
| `TestHlpGenerateCacheConsistency` (two objects sharing the same dense vector, differing only in the stored checksum) | 2 | `test_consistent_checksum`: True on a matching `w_checksum`. `test_inconsistent_checksum`: False on a stale one (the single-field gate) |
| `TestHlpGenerateIO` (TemporaryDirectory FIRST under CUSTOM_TMP_BASE, defensive tearDown; object `w_checksum "io_test_checksum"` + `w_dense [0.5, −0.2, 1.0, 3.0]` float32) | 8 | `test_store_and_load_cycle`: the checksum=False round-trip (checksum + dtype + values). `test_compute_sha3_256_hash_golden`: the duck-typed hash pinned (below). `test_load_with_valid_sidecar`: store + `binio.write_sha3_256_sidecar` + checksum=True load. `test_load_with_mismatched_sidecar`: the mid-file byte flip (offset `size // 2`) → `RuntimeError: Checksum mismatch.` (message pinned — the sidecar verify runs before any payload parse). `test_load_rejects_wrong_description`: a hand-written header with the wrong description → `RuntimeError: Wrong file format: ...` (message pinned). `test_load_rejects_version_mismatch`: the proper description with version 2 → `RuntimeError: File version mismatch: found 2, expected 1` (message pinned). The 2 additions — `test_store_compressed_by_default` (store → the first 4 file bytes are the LZ4 frame magic `b"\x04\x22\x4d\x18"` → load round-trips) + `test_load_defaults_reject_uncompressed_file` (a file written `compressed=False` → `binio.BinaryFormatError` at the compressed default); the wrong-description/wrong-version handcrafted writers pass `compressed=True` to the manual `binio.BinaryWriter` (the LZ4 guard passes, the header gate is still reached) |
| `TestHlpGenerateInit` | 3 | `test_init_accepts_valid_arrays`: the valid object. `test_init_fails_with_list_w_dense`: a list → ValidationError (the NDArray gate). `test_init_fails_with_non_str_w_checksum`: an int checksum → ValidationError |

## Goldens pinned

- The duck-typed hash golden `460c993da80d5ff6fd5581660d71be905c482eadc5520718b56051f6545cd07a` (= sha3_256 of the
  4-value float32 fixture).
- The mock compute golden (the hand re-derivation): INT 0.5; PAT weighted mean (−0.2·10)/10 = −0.2 (only config 1
  computed); MOB interp over known configs {1: 1.0, 3: 3.0} clamped → [1.0, 1.0, 2.0, 3.0, 3.0] — the same vector the
  probe D11 re-derives independently.

## Conventions

- DB-free BY CONSTRUCTION (no file I/O outside the IO class, which uses TemporaryDirectory) — hence no SKIP_REGAB_DB
  gate and no `reversi.test.paths` import beyond CUSTOM_TMP_BASE.
- The empty-array `wmap` in the error-branch tests is `np.zeros((0, 3), dtype=np.int64)` — the (0,3) shape keeps the
  column indexing `wmap[:, 0] == fid` well-defined.
- The mid-file corruption is offset-computed (`size // 2`), not a fixed offset: the dense file is small, a fixed 100
  could fall past EOF.
- Clean house style (no stale comments, no dead `ctx.z` field, no ws lines).

## Integration

- This file owns the branches the live data cannot reach: init, IO + the 3 header gates, consistency, and the compute
  error branches.
- The LIVE goldens (K = 6588, the per-feature weighted means, orbit invariance, the hash golden) live in the probe E
  tier + test_wrk_generate.py — the single source of truth.
