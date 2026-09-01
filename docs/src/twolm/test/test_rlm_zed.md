# twolm/test/test_rlm_zed.py

Analysis date: 2026-08-31 — created in session 24 (D-092 T3), the
dedicated data-object suite of the 8th pipeline level (ZED)
closing the coverage gap flagged in D-091 (the domain module
arrived with only the worker test — the D-090 T6 class gap, as at
the DESIGN_MTR bring-in). NEW file, house idioms from day one
(no DB claim in the header, no temp files needed — the module has
no file I/O).

## Suite status (session 24)

- `test_rlm_zed`: 10/0/0 (3 classes; no DB, no gate — the file is
  fully offline: the factory math, the handcrafted-mock compute,
  the data-object init validation).
- Full discover: 563 tests, 66 skipped under `SKIP_REGAB_DB=1`
  (the gate list is unchanged by this file — no gate exists here),
  GREEN; ungated: 563 run, 17 skipped (PERF only), GREEN; the full
  `-W error` discover clean.

## State per Roberto

Created by Nia in the D-092 fix campaign (Roberto: "T1-T8: OK"),
mirroring the test_rlm_wmaps / test_rlm_design_matrix house
pattern: the isolated factory math, the handcrafted-mock compute
pins, the init validation, the hash golden.

## Architecture (157 lines)

- Imports (L44-55): `unittest`, `hashlib`,
  `SimpleNamespace` (L44-46, the mock-context builder); numpy +
  numpy.testing (L48-49); `ValidationError` from pydantic (L51);
  the 3 domain names from `twolm.rlm_zed` (L53-55). No DB, no
  `twolm.test.paths`, no `tempfile` (no file I/O in the module).
- `TestZedFunFactory` (L59-88, 4 tests, no DB):
  - `test_y2z_golden` (L62): alpha 0.02, `[-64, 0, 6, 64]` int8 →
    `[0.02, 0.5, 0.545, 0.98]` float32 (allclose 1e-6/1e-7) + the
    float32 dtype pin.
  - `test_z2y_inverse` (L70): the inverse mapping back to
    `[-64, 0, 6, 64]` float32.
  - `test_round_trip` (L76): alpha 0.03, `[-64, −22, 0, 18, 63,
    64]` — `z2y(y2z(y)) == float32(y)` (allclose).
  - `test_endpoints_for_two_clipplings` (L82): for α ∈ {0.02,
    0.03}: `y2z(−64) = c`, `y2z(0) = 0.5`, `y2z(+64) = 1 − c`
    (the affine range contract, 6 places).
- `TestRLMZedCompute` (L90-117, 2 tests, no DB): the
  `_mock_ctx` helper (L93-96) builds the SimpleNamespace chain
  `cfg.stat_model.logit_clipping` + `game_values` (int8).
  - `test_compute_golden` (L98): clipping 0.03, values
    `[10, 36, −22, 20]` → z (4,) float32 EXACT (assert_array_equal)
    against the hand-derived literal `[0.5734375, 0.764375,
    0.3384375, 0.646875]` (= `0.5 + y·(1−2·0.03)/128`, the same
    float32 literals the rlm_01 pipeline golden pins, L106-107);
    the result is a `ReversiLogisticModelZed` with callable
    closures + the shape/dtype pins.
  - `test_compute_hash` (L112): `compute_sha3_256_hash() ==
    hashlib.sha3_256(z.tobytes()).hexdigest()` (the identity,
    independent of the value).
- `TestReversiLogisticModelZed` (L119-153, 4 tests, no DB):
  - `test_init_stores_by_reference` (L125): the 3 attrs are the
    SAME objects (no copy).
  - `test_init_rejects_invalid_z` (L133): `z="not_an_array"` →
    `ValidationError` (the NDArray annotation is enforced by
    `@validate_call` + `arbitrary_types_allowed`, L136).
  - `test_init_rejects_non_callable` (L138):
    `y2z="not_callable"` → `ValidationError` (L141-142).
  - `test_hash_golden` (L144): the rlm_01 live golden z (10,)
    float32 literal (L147-149) → the pinned sha3_256
    `3d49fd5d56ced2f7bb70e5c24c8100b3318a7e66e7c990de53ed2f16f365d9b2`
    (L153) — the golden-hash pin class (as the WMAPS
    `12c3344e...` and DESIGN_MTR `da86a916...` pins).

## Verified facts (D-092 probe, G tier — 0 mismatches)

- V1: structure — 157 lines; 3 classes (L59/90/119); 10 tests;
  no DB / no gate / no paths / no `import os` (G2); the factory
  goldens + round-trip + 2-clippling endpoints (G4); the mock
  compute exact golden + identity (G5); the 2 ValidationError
  pins + by-reference (G6); the hash golden (G7); the no-DB
  header claim (G8); 0 trailing-ws lines (G9); the 3-name import
  (G10).
- V2: behavior — 10/0/0 GREEN (no DB), in the full discover both
  gated and ungated; the `-W error` discover clean.

## Integration notes

- The file is DB-free BY CONSTRUCTION (the module has no file I/O
  and no RLMContext beyond the two attributes `rlm_zed_compute`
  reads) — hence no SKIP_REGAB_DB gate and no
  `twolm.test.paths` import (the D-065 artifact rule has nothing
  to apply to).
- The (4,) compute golden and the (10,) hash golden reuse the
  rlm_01 fixture values — the single source of truth remains the
  worker test's pinned literals (re-derived independently by the
  probe D tier); the mock values are a SUBSET of the live y
  ([10, 36, −22, 20] ⊂ the live (10,)) so the float32 literals
  match the pipeline output bit-for-bit.
- The hash golden covers z ONLY (M1 in the rlm_zed doc): the
  closures are a pure function of logit_clipping and not part of
  the checksum.

## Appendix — line reference

157 lines, as of D-092 (new file).

- L28-42: the run-note header (L38-39 the no-DB claim)
- L44-55: imports (hashlib L45, SimpleNamespace L46, pydantic
  L51, the 3 domain names L53-55)
- L59-88: `TestZedFunFactory` (4 tests: L62, L70, L76, L82)
- L90-117: `TestRLMZedCompute` (`_mock_ctx` L93-96; 2 tests: L98,
  L112)
- L119-153: `TestReversiLogisticModelZed` (`_closures` L122; 4
  tests: L125, L133, L138, L144)
- L156-157: the `__main__` guard
