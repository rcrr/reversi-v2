# test/reversi/lm/test_hlp_optimize.py
The dedicated hlp_optimize suite — a NO-DB suite (handcrafted checkpoint fixtures + a SimpleNamespace ctx mock) that
pins the binary round-trip, the error paths, the golden hashes and the two gate functions — the level where the worker's
decision logic lives. 4 classes / 20 tests.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestHlpOptimizeIO` (setUp builds the deterministic fixture — w [0.1, 0.2, 0.3] f32, one (s, y) pair, rho [1.5] — in a `TemporaryDirectory` under `CUSTOM_TMP_BASE`, defensive tearDown) | 9 | `test_store_and_load_cycle`: the scalars + the arrays WITH the dtype pins (w/sl/yl float32, rho plain float). `test_empty_history_roundtrip`: the len_mem=0 path. `test_history_length_mismatch_raises`: asymmetric sl/yl/rho raise ValueError and NO file is created. `test_wrong_description_raises` / `test_wrong_version_raises`: the 2 header `RuntimeError` gates, message-pinned — the handcrafted writers pass `compressed=True` to the manual `binio.BinaryWriter` (the LZ4 guard passes, the header gate is still reached). `test_checksum_mismatch_raises`: corrupts the SIDEcar file (a content-byte flip would trip the LZ4 frame guard first) → the "Checkpoint checksum mismatch" RuntimeError. `test_file_golden_hash`: the deterministic bytes pin to the golden below. `test_store_compressed_by_default`: the first 4 file bytes are the LZ4 frame magic. `test_sidecar_produced_and_matches`: the `.SHA3-256` sidecar exists and verifies |
| `TestHlpOptimizeHelpers` | 3 | `hlp_optimize_info_dict` projects to EXACTLY the 5 context keys (extras dropped) + `KeyError` on a missing key + the weights-hash golden below (= the independent `sha3_256(w.tobytes())`) |
| `TestHlpOptimizeCacheConsistency` (the mock ctx: dm "123abc", zed "456xyz", ridge 0.01) | 4 | valid → True; the 3 gate mismatches (`..._design_matrix_checksum`, `..._zed_checksum`; `test_inconsistent_ridge`) → False |
| `TestHlpOptimizeStatusConverged` | 4 | g_norm below the tolerance → True; above → False; the f32 round-trip (the stored np.float32 values do not trip the comparison); `test_judged_against_new_tolerance` (a looser CURRENT tolerance accepts a checkpoint that was not converged under the old one — the tolerance is a judgement criterion, not part of the objective) |

## Goldens pinned

- The checkpoint file golden: `2a2f96dfcd6224bb799ecba92011cafafa36564ac770865cfc6d04e1e978633f` (deterministic bytes —
  fixed header, fixed field order, no timestamps; the LZ4-compressed frame; a format change breaks this).
- The weights hash golden: `78a7baac51aedf442b3de09a583af1a0704c8aece3b156aaf630780b2d7dc060` (w = [0.1, 0.2, 0.3]
  f32).

## Conventions

- DB-free BY CONSTRUCTION: the whole suite runs under `SKIP_REGAB_DB=1` without skipping anything.
- The mock ctx records its log events but the tests assert only on the return values; the 3-WARN diagnostics per failed
  gate are asserted by NO test or probe (a known gap, no pin).
- `test_store_and_load_cycle` uses approximate assertions for f/g_norm/ridge/min_grad (`assertAlmostEqual`) while the
  arrays are pinned exactly (`assert_array_equal`) — the f32 metadata is round-trip stable; the approximate style is
  harmless.

## Integration

- This file owns the checkpoint IO + the helper branches — the suite-level mirror of the worker's end-to-end path is
  `test_checksum_mismatch_raises`.
- The per-function pin that would catch a signature change to any of the 6 hlp_optimize names; the worker test only
  exercises the end-to-end paths.
