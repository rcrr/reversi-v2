# twolm/test/test_lm_worker_generate.py

Added 2026-09-02 — session 27, D-098 T5 (Roberto: "T5: ok" +
"Aggiungi anche il file test_lm_worker_generate.py con i dovuti
tests sul worker"). At the bring-in (e31c061) there was NO worker
test at all — Roberto confirmed. House worker-test shape (same as
test_lm_worker_indexes / test_lm_worker_optimize et al.): a
live-DB suite that moves the machine through the full 10-level
chain on a fresh base dir and then exercises the GENERATE level.
3 tests, all DB-gated. Probe (scratch/verify_generate.py, tier
E): 0 mismatches.

## Suite status (session 27, post D-098)

- `test_lm_worker_generate`: 3/0/0 live (1 class; all 3 tests
  DB-gated — the setUp moves through OPTIMIZE, which runs the
  positions chain + the lbfgs optimization on a fresh base dir).
  3/0/3 under `SKIP_REGAB_DB=1`. Full discover: 615 tests, 74
  skipped under the gate, GREEN.

## State per Roberto

NEW in D-098 T5 (the file did not exist at the bring-in).
Written directly to the house pattern: the SKIP_REGAB_DB gate
FIRST in setUp (with the why-comment), the D-085 idiom
(TemporaryDirectory FIRST under CUSTOM_TMP_BASE, the
WORKSPACE_ROOT-anchored rlm_02.json), the house run-instruction
header, the defensive tearDown.

## Architecture (185 lines)

- imports (L44-59): unittest, os, tempfile, hashlib, numpy +
  nptest, StringIO/patch, Path, binio (the sidecar verify),
  Verbosity, LogisticModel, CUSTOM_TMP_BASE + WORKSPACE_ROOT.
- `TestLMWorkerGenerate` (L62-181):
  - setUpClass (L66-67): CUSTOM_TMP_BASE mkdir.
  - setUp (L69-98): the gate FIRST; the stdout patcher; the D-085
    idiom; rlm_02.json (the 199952-position dataset — the one the
    probe E tier re-derives); `LogisticModel` at Verbosity.HIGH;
    `move_to_step('OPTIMIZE')` + the step-9 + name pins (the
    setUp consumes the full chain incl. the lbfgs run, so the
    GENERATE inputs — `ctx.w` + `ctx.w_checksum` — are real).
  - tearDown (L100-104): defensive (the getattr pattern).
  - `test_compute_and_populate_cache` (L106-136): the pre-state
    pins (`w_dense is None`, `dense_w_checksum is None`);
    `move_to_step('GENERATE')` + the step-10 + name pins; the
    flat files `rlmwf_10_GENERATE.dat` + `.SHA3-256` exist and the
    sidecar verifies (`binio.verify_sha3_256_sidecar`); the log
    says "Executing heavy computation"; the rlm_02 golden: shape
    (6588,) — 1 (intercept) + 6561 (EDGE) + 27 (DIAG3) — float32,
    `dense_w_checksum` == `ec9d65453bb112bf277c79f96a86edfa9468bb01f42a2763cd82d69c5b2b15b4`
    (the probe E7 golden) AND the duck-typed identity
    sha3_256(w_dense.tobytes()) == dense_w_checksum.
  - `test_read_cache_on_new_instance` (L138-169): the 2nd
    instance on the SAME base dir moves through OPTIMIZE (all
    cache hits, the checkpoint reload — no lbfgs) and then to
    GENERATE: the log must say "Cache successfully loaded and
    validated" and must NOT say "Executing heavy computation";
    `w_dense` array-equal, `dense_w_checksum` equal.
  - `test_down_clears_generate_attributes` (L171-181): after
    GENERATE (both fields not-None), `move_to_step(9)` back to
    OPTIMIZE must leave `w_dense is None` +
    `dense_w_checksum is None` (the `_down` scope pinned).

## Verified facts

- All 3 live paths were re-derived by the probe E tier (E1 the
  pipeline reaches GENERATE, E2-E7 the golden, E8 the files, E9
  the second-instance cache hit, E11 the `_down` clearing) — the
  test pins the same facts in unittest form.
- The hash golden `ec9d6545…` matches across: the probe, the
  worker test, and `ctx.dense_w_checksum` (the duck-typed data
  checksum returned by cache_manager_load_or_compute).

## Minor notes

- The setUp's OPTIMIZE move is what makes the suite DB-bound AND
  the slow one (the lbfgs run, ~10 s per test) — the same cost
  test_lm_worker_optimize already carries; the GENERATE level
  itself is cheap (the vectorized expansion).
- The 2nd instance re-running through OPTIMIZE exercises the
  checkpoint-reload path for free (the "Iterations" + no "L-BFGS -
  [" behaviour of test_lm_worker_optimize's run 2).

## Appendix — line reference

185 lines.

- L28-42: header (how-to-run block — the DB-gated claim is TRUE:
  the gate is in setUp)
- L44-59: imports
- L62-181: `TestLMWorkerGenerate` (setUp L69-98 with the gate
  L72-76 + the idiom L81-88; tearDown L100-104;
  test_compute_and_populate_cache L106-136;
  test_read_cache_on_new_instance L138-169;
  test_down_clears_generate_attributes L171-181)
- L184-185: `__main__`
