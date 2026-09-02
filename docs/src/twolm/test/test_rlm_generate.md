# twolm/test/test_rlm_generate.py

Analysis date: 2026-09-02 — analysis session 27 (D-097); the T4
expansion + T6/T7/M5 batch applied in the D-098 campaign (Roberto:
"T4: ok" — the suite was proposed for expansion, siblings run
10-19 tests vs the bring-in's 1). Brought in by Roberto (commit
e31c061). Probe (scratch/verify_generate.py, tiers C/D, re-pinned
post-campaign): 0 mismatches.

The GENERATE domain suite: mock-context compute goldens (no DB, no
gate) + the cache-consistency branches + the binary IO round-trip
and the 3 header gates + the init validation. 4 classes / 14 tests
post D-098 T4 (the bring-in had 1 class / 1 test — the compute
happy path only).

## Suite status (session 27, post D-098)

- `test_rlm_generate`: 14/0/0 (no DB, no gate). Full discover:
  615 tests, 74 skipped under `SKIP_REGAB_DB=1`, GREEN; ungated:
  615 run, 17 skipped (PERF only), GREEN. `-W error` discover
  clean.

## State per Roberto

As brought in: 1 class / 1 test (the 3-feature mock compute
golden) — green on first run, with the house bring-in gaps:
T6 (the Italian comment "AGGIUNTO ref mock" L45 — AGENTS.md rule
4), T7 (13 trailing-ws lines), M5 (the dead mock field
`ctx.z`), and the thinness itself (T4: no IO round-trip, no
sidecar/description/version gates, no consistency branches, no
init validation, no error branches). D-098 (all approved): the
file rewritten with the house run-instruction header, the mock
cleaned (English comment, no `ctx.z`, no ws), and the 3 new
classes.

## Architecture (312 lines, post D-098)

- imports (L43-61): unittest, tempfile, numpy + nptest, Path,
  SimpleNamespace, pydantic ValidationError, binio, Relevance, the
  5 rlm_generate public names, CUSTOM_TMP_BASE.
- `TestRLMGenerateCompute` (L64-193): the 3-feature mock context
  (L67-125: Intercept / Pattern (identity principal ref) /
  Mobility — iwmap offsets [0,1,4,9], w_ranges, the 4-row wmap,
  w = [0.5, −0.2, 1.0, 3.0], w_checksum "abc654", a no-op
  logger).
  - `test_compute_w_dense` (L127-150): the bring-in golden, kept
    verbatim in semantics: (9,) float32, INT 0.5, PAT
    [−0.2, −0.2, −0.2] (config 1 seen; configs 0/2 unseen →
    weighted mean (−0.2·10)/10 = −0.2), MOB [1, 1, 2, 3, 3]
    (clamp + linear interpolation over the 2 seen configs).
  - `test_unknown_category_raises` (L152-169, NEW): category 9 →
    `RuntimeError` with the exact message "The feature category
    is unknown: 9" (the D-098 M3 wording).
  - `test_mobility_without_seen_configs_warns_and_zeroes`
    (L171-193, NEW): an empty-wmap mobility feature → zeros (4,)
    + exactly one WARN event (Relevance.WARN, "no seen
    configurations").
- `TestRLMGenerateCacheConsistency` (L196-209, NEW): the
  w_checksum equality gate — True on match, False on a stale
  "stale" checksum.
- `TestRLMGenerateIO` (L212-293, NEW): the D-085 idiom
  (TemporaryDirectory FIRST under CUSTOM_TMP_BASE, defensive
  tearDown); the object: w_checksum "io_test_checksum" + w_dense
  [0.5, −0.2, 1.0, 3.0] float32.
  - `test_store_and_load_cycle` (L236-245): checksum=False
    round-trip (checksum + dtype + values).
  - `test_compute_sha3_256_hash_golden` (L247-251): the duck-typed
    hash pinned to `460c993da80d5ff6fd5581660d71be905c482eadc5520718b56051f6545cd07a`.
  - `test_load_with_valid_sidecar` (L253-259): store +
    `binio.write_sha3_256_sidecar` + checksum=True load.
  - `test_load_with_mismatched_sidecar` (L261-273): the mid-file
    byte flip → `RuntimeError: Checksum mismatch.` (message
    pinned — the R3 gate runs before any payload parse).
  - `test_load_rejects_wrong_description` (L275-283): a
    hand-written header "A description that is not the dense-
    weights one" v1 → `RuntimeError: Wrong file format: ...`
    (message pinned).
  - `test_load_rejects_version_mismatch` (L285-293, NEW with the
    D-098 T1 gate): the proper description with version 2 →
    `RuntimeError: File version mismatch: found 2, expected 1`
    (message pinned).
- `TestRLMGenerateInit` (L296-309, NEW): `__init__` validation —
  the valid object; list w_dense → ValidationError (the NDArray
  gate); non-str w_checksum → ValidationError.

## Verified facts

- The mock golden was independently re-derived by hand (and by the
  probe D11) before the campaign: all values above match a
  from-scratch computation of the three branches.
- The live pipeline re-derivation (probe E tier, rlm_02: K = 6588,
  the per-feature weighted means, orbit invariance, seen-config
  exactness, the full vector equality) is the domain-module
  coverage; this file covers the branches the live data cannot
  reach (unknown category, empty mobility, the 3 header gates,
  the init validation).

## Minor notes

- The empty-array `wmap` in the two error-branch tests is
  `np.zeros((0, 3), dtype=np.int64)` — the (0,3) shape keeps the
  column indexing `wmap[:, 0] == fid` well-defined.
- The mid-file corruption (L264-269) is offset-computed
  (`size // 2`), not a fixed offset like the wmaps suite: the
  dense file is small, a fixed 100 could fall past EOF.
- No `test_lm_worker_generate` existed at the bring-in (Roberto
  confirmed) — the worker round-trip + `_down` pin live in the
  new test_lm_worker_generate.py (D-098 T5).
