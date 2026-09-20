# reversi/test/test_wrk_generate.py
The GENERATE worker integration suite, in the house worker-test shape (as in test_wrk_indexes / test_wrk_optimize et
al.): a live-DB suite that moves the machine through the full 12-level chain on a fresh base dir and then exercises the
GENERATE level. 1 class / 3 tests, all DB-gated.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestLMWorkerGenerate` (setUp: the SKIP_REGAB_DB gate FIRST with the why-comment — the setUp moves through OPTIMIZE on a fresh base dir, so a live DB is required; the stdout patcher; TemporaryDirectory FIRST under CUSTOM_TMP_BASE, the WORKSPACE_ROOT-anchored rlm_02.json; `LogisticModel` at Verbosity.HIGH; `move_to_step('OPTIMIZE')` + the step-11 + name pins; defensive tearDown) | 3 | `test_compute_and_populate_cache`: the pre-state pins (`w_dense is None`, `dense_w_checksum is None`); `move_to_step('GENERATE')` + the step-12 + name pins; the flat files `rlmwf_12_GENERATE.dat` + `.SHA3-256` exist and the sidecar verifies (`binio.verify_sha3_256_sidecar`); the log says "Executing heavy computation"; the rlm_02 golden — shape (6588,) (= 1 intercept + 6561 EDGE + 27 DIAG3), float32, `dense_w_checksum` == the golden below AND the duck-typed identity sha3_256(w_dense.tobytes()) == dense_w_checksum. `test_read_cache_on_new_instance`: the 2nd instance on the SAME base dir moves through OPTIMIZE (all cache hits, the checkpoint reload — no lbfgs) and then to GENERATE: the log says "Cache successfully loaded and validated" and NOT "Executing heavy computation"; `w_dense` array-equal, `dense_w_checksum` equal. `test_down_clears_generate_attributes`: after GENERATE (both fields not-None), `move_to_step(11)` back to OPTIMIZE leaves `w_dense is None` + `dense_w_checksum is None` (the `_down` scope) |

## Goldens pinned

- The dense hash golden `ec9d65453bb112bf277c79f96a86edfa9468bb01f42a2763cd82d69c5b2b15b4` (the probe E7 golden) —
  matches across the probe, this test, and `ctx.dense_w_checksum`.
- The shape golden (6588,) = 1 (intercept) + 6561 (EDGE) + 27 (DIAG3), float32.

## Conventions

- The setUp's OPTIMIZE move is what makes the suite DB-bound AND slow (the lbfgs run, ~10 s per test) — the same cost
  test_wrk_optimize already carries; the GENERATE level itself is cheap (the vectorized expansion).
- The 2nd instance re-running through OPTIMIZE exercises the checkpoint-reload path for free (the no-"L-BFGS - ["
  behavior of test_wrk_optimize's run 2).
- Follows the house pattern: the db_long_gate first in setUp (the SKIP_REGAB_DB + LONG tier, with the why-comment), the
  house run-instruction header (the DB-gated claim TRUE — the gate is in setUp), defensive tearDown.

## Integration

- This file owns the probe's E1 (bootstrap to GENERATE), E3 (shape/dtype), E8 (the flat files + sidecar), E9 (the
  second-instance cache hit), E10 (the version gate on the real file — via the hlp_generate load path) + E11 (the
  `_down` scope).
- The E2/E4/E5/E7 live re-derivation (K, orbit invariance, the full vector, the hash) remains in the probe — the test
  pins the same facts in unittest form.
