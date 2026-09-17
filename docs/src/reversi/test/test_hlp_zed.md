# reversi/test/test_hlp_zed.py
The dedicated data-object suite of the hlp_zed module. 3 classes / 10
tests / no DB, no gate — the file is fully offline: the module has no
file I/O and no LMContext beyond the two attributes `hlp_zed_compute`
reads, so no `tempfile`, no `reversi.test.paths`, no `import os`.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestZedFunFactory` (no DB) | 4 | `test_y2z_golden`: alpha 0.02, `[-64, 0, 6, 64]` int8 → `[0.02, 0.5, 0.545, 0.98]` float32 (allclose 1e-6/1e-7) + the dtype pin. `test_z2y_inverse`: the inverse mapping back. `test_round_trip`: alpha 0.03, `[-64, −22, 0, 18, 63, 64]` — `z2y(y2z(y)) == float32(y)`. `test_endpoints_for_two_clipplings`: for α ∈ {0.02, 0.03}: `y2z(−64) = c`, `y2z(0) = 0.5`, `y2z(+64) = 1 − c` (the affine range contract, 6 places) |
| `TestHlpZedCompute` (a `SimpleNamespace` mock ctx, no DB) | 2 | `test_compute_golden`: clipping 0.03, values `[10, 36, −22, 20]` → z (4,) float32 EXACT (assert_array_equal) against the hand-derived literal `[0.5734375, 0.764375, 0.3384375, 0.646875]` (= `0.5 + y·(1−2·0.03)/128` — the same float32 literals the rlm_01 pipeline golden pins; the mock values are a SUBSET of the live y, so they match the pipeline output bit-for-bit); the result is a `LMZed` with callable closures + shape/dtype pins. `test_compute_hash`: `compute_sha3_256_hash() == hashlib.sha3_256(z.tobytes()).hexdigest()` (the identity, independent of the value) |
| `TestLMZed` | 4 | `test_init_stores_by_reference` (the 3 attrs are the SAME objects — no copy); `test_init_rejects_invalid_z` (`z="not_an_array"` → the precise pydantic `ValidationError`); `test_init_rejects_non_callable` (`y2z="not_callable"` → `ValidationError`); `test_hash_golden`: the rlm_01 live golden z (10,) float32 literal → the pinned sha3_256 `3d49fd5d56ced2f7bb70e5c24c8100b3318a7e66e7c990de53ed2f16f365d9b2` (the golden-hash pin class — as the WMAPS `12c3344e…` and DESIGN_MTR `da86a916…` pins) |

## Goldens pinned

- The factory literal `[0.02, 0.5, 0.545, 0.98]` (alpha 0.02).
- The (4,) exact compute golden `[0.5734375, 0.764375, 0.3384375,
  0.646875]`.
- The rlm_01 (10,) z hash golden `3d49fd5d56ced2f7bb70e5c24c8100b
  3318a7e66e7c990de53ed2f16f365d9b2` — the hash covers z ONLY
  (the closures are a pure function of logit_clipping, not part
  of the checksum).

## Conventions

- DB-free BY CONSTRUCTION (the module has no file I/O) — hence no
  SKIP_REGAB_DB gate and no `reversi.test.paths` import.
- Mirrors the test_hlp_wmaps / test_hlp_design_matrix house
  pattern: the isolated factory math, the handcrafted-mock
  compute pins, the init validation, the hash golden.

## Integration

- Independent of the pipeline: the per-function pin that would
  catch a signature change to `hlp_zed` (the worker test only
  exercises the end-to-end path).
- The LIVE golden (the rlm_01 (10,) y/z) lives in
  test_wrk_zed.py (`TestLMWorkerZed`) — the single source
  of truth; this file's mock values reuse the rlm_01
  fixture values as a subset.
