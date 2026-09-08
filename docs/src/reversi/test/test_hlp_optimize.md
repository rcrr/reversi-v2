# reversi/test/test_hlp_optimize.py
The dedicated hlp_optimize suite — the house pattern (D-094 M1
for gradient, D-090 T6 for design_matrix, D-092 T3 for zed): a
NO-DB suite (handcrafted checkpoint fixtures + a SimpleNamespace
ctx mock) that pins the binary round-trip, the error paths, the
golden hashes and the two gate functions — the level where the
worker's decision logic lives. 4 classes / 19 tests. D-096 M10
expanded it from the bring-in 4 tests (Roberto: "M: falli tutti")
and T14/T15 fixed the header claim + the misleading names.
> State: D-096 · b1b8934 · 2026-09-01 · suite 19/0/0

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestHlpOptimizeIO` (setUp builds the deterministic fixture — w [0.1, 0.2, 0.3] f32, one (s, y) pair, rho [1.5] — in a `TemporaryDirectory` under `CUSTOM_TMP_BASE`, defensive tearDown) | 8 | `test_store_and_load_cycle`: the scalars + the arrays WITH the dtype pins (w/sl/yl float32, rho plain float). `test_empty_history_roundtrip`: the len_mem=0 path. `test_history_length_mismatch_raises`: M6 — asymmetric sl/yl/rho raise ValueError and NO file is created. `test_wrong_description_raises` / `test_wrong_version_raises`: the 2 header `RuntimeError` gates, message-pinned. `test_checksum_mismatch_raises`: R3 — flip the last content byte (sidecar untouched) → the "Checkpoint checksum mismatch" RuntimeError. `test_file_golden_hash`: the deterministic bytes pin to the golden below. `test_sidecar_produced_and_matches`: the `.SHA3-256` sidecar exists and verifies |
| `TestHlpOptimizeHelpers` | 3 | `optimization_info_dict` projects to EXACTLY the 5 context keys (extras dropped) + `KeyError` on a missing key + the weights-hash golden below (= the independent `sha3_256(w.tobytes())`) |
| `TestHlpOptimizeCacheConsistency` (the mock ctx: dm "123abc", zed "456xyz", ridge 0.01) | 4 | valid → True; the 3 gate mismatches (T15-renamed `..._design_matrix_checksum`, `..._zed_checksum`; `test_inconsistent_ridge` — the R1 gate) → False |
| `TestHlpOptimizeStatusConverged` | 4 | g_norm below the tolerance → True; above → False; the f32 round-trip (the stored np.float32 values do not trip the comparison); `test_judged_against_new_tolerance` (M3 semantics: a looser CURRENT tolerance accepts a checkpoint that was not converged under the old one — the tolerance is a judgement criterion, not part of the objective) |

## Goldens pinned

- The checkpoint file golden:
  `6e01ff8614e8732484b7af59b01615989357ce1af2419864621965af221b
  d280` (deterministic bytes — fixed header, fixed field order,
  no timestamps; a format change breaks this + the probe G3 at
  once).
- The weights hash golden:
  `78a7baac51aedf442b3de09a583af1a0704c8aece3b156aaf630780b2d7d
  c060` (w = [0.1, 0.2, 0.3] f32).

## Conventions

- DB-free BY CONSTRUCTION: the whole suite runs under
  `SKIP_REGAB_DB=1` without skipping anything (T14 fixed the
  header's false "a live regab DB is required" claim).
- The mock ctx records its log events but the tests assert only
  on the return values — the log-pattern pins (the 3-WARN
  diagnostics per failed gate) live in the probe, keeping the
  suite focused.
- `test_store_and_load_cycle` keeps Roberto's original
  approximate assertions for f/g_norm/ridge/min_grad
  (`assertAlmostEqual`) while the arrays are pinned exactly
  (`assert_array_equal`) — the f32 metadata is round-trip
  stable; the approximate style is the original author's choice
  and harmless.

## Integration

- After the step-3 class c deletions, this file owns the
  checkpoint IO + the helper branches the probe used to pin
  (former F1-F10 + G1/G2 + G4 + G5) — the suite-level mirror of
  the worker's R2 path (probe H8) is
  `test_checksum_mismatch_raises`.
- The per-function pin that would catch a signature change to
  any of the 6 hlp_optimize names; the worker test only
  exercises the end-to-end paths.
