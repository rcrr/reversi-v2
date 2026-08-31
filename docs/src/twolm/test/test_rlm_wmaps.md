# twolm/test/test_rlm_wmaps.py

Analysis date: 2026-08-31 — analysis session 23 (D-086); fix
campaign D-087 approved by Roberto ("Procedi su tutto") and applied
in the same session.

Roberto's file, brought in with the WMAPS enablement (73b4342, the
line-by-line pipeline step 6). 4 classes / 13 tests / no PERF / no
DB / no gate. Green on first run (the compute tests use a
handcrafted 4×3 mock pindexes; the IO tests use a real temp dir
under the shared CUSTOM_TMP_BASE — the D-085 idiom, applied per
Roberto's instruction in D-086 before the analysis campaign).
T2/T3/T4 + T9 + T10 all resolved in D-087 (the original 6 tests
untouched, +5 IO pins + the 2 init tests = 13).

## Suite status (session 23, post D-087)

- `test_rlm_wmaps`: 13/0/0 (no DB, no gates)
- Full discover: 535 tests, 61 skipped under `SKIP_REGAB_DB=1`
  (17 PERF + 35 regab + 2 positions + 2 features + 2 indexes + 3
  wmaps), GREEN; ungated (live DB): 535 run, 17 skipped (PERF
  only), GREEN.

## Coverage

- `TestRLMWmapsCompute` (2 tests, no mocks — a handcrafted
  SimpleNamespace ctx over a 4×3 uint32 pindexes, 2 features:
  F0 n_instances=1 n_configurations=3, F1 n_instances=2
  n_configurations=2):
  - `test_compute_with_fallback` (L100-142, cut_off=2): the full
    output pin — w len 4, iwmap [1,0,0,2,3] semantics (per-feature
    offsets), wmap 4 rows, wf 2 rows; the below-cutoff
    configurations fold into the single fallback weight per
    feature (config_id −1), the above-cutoff ones get their own
    weights; the per-feature w ranges in feature_w_ranges.
  - `test_compute_without_fallback` (L144-160, cut_off=0): the
    no-fallback branch — w len 5, wf shape (0,3), fwr[0,0] = −1.
    (R2 observation carried from D-086: cut_off=0 is unreachable
    via the real config — `frequency_cut_off` is PositiveInt —
    the branch is mock-only; knowing it is correct is the point.)
- `TestRLMWmapsCacheConsistency` (3 tests, L162-201): the
  2-field metadata compare with a SimpleNamespace ctx
  (cut_off=5) — True when both rlm_indexes_checksum and cut_off
  match; False when only the hash differs; False when only the
  cut_off differs. Both single-field branches pinned.
- `TestRLMWmapsIO` (6 tests since D-087 T10, L203-296; real temp
  dir under CUSTOM_TMP_BASE, the D-085 idiom):
  - `test_store_and_load_cycle` (L233-253): store → load with
    `checksum=False` both sides — all 8 fields round-trip
    (rlm_indexes_checksum, cut_off=42, the 6 arrays, float32
    dtype preserved).
  - `test_compute_sha3_256_hash_golden` (L255-259, D-087 T10):
    the duck-typed `compute_sha3_256_hash()` on the known IO
    object = `12c3344ec23c798d7b35eb6eae01034b29ee5c539bfb2018c
    a2eabc73c861dfa` (golden content, the D-081 philosophy).
  - `test_load_with_valid_sidecar` (L261-267, D-087 T10): the
    `checksum=True` path accepts a matching sidecar (store →
    `binio.write_sha3_256_sidecar` → load `checksum=True`
    round-trips).
  - `test_load_with_mismatched_sidecar` (L269-280, D-087 T10):
    a byte-flip in the .dat against its sidecar → RuntimeError
    "checksum file signature doesn't match" (the sidecar
    verify, step 1 of the load).
  - `test_load_rejects_wrong_description` (L282-288, D-087 T10):
    a `binio.BinaryWriter` file with a wrong header description →
    RuntimeError "not a proper ...".
  - `test_load_rejects_version_mismatch` (L290-296, D-087 T10):
    a header with version 2 → RuntimeError "version mismatch".
- `TestRLMWmapsInit` (2 tests, D-087 T10, L299-321):
  - `test_init_accepts_valid_arrays` (L316-317): the sanity
    constructor.
  - `test_init_fails_with_invalid_cut_off_type` (L319-321): a
    string `cut_off` is rejected via the precise pydantic
    `ValidationError` (the D-084 T3 pattern).

The suite is now a complete per-function pin: the compute
semantics (both branches), the consistency (both single-field
branches), the full store/load contract (cycle + golden hash +
the 3 load error paths + both checksum flags), the init
validation. The former D-086 coverage gaps are closed (T10).

## Defects — RESOLVED (D-087)

- **T2 FIXED (F3)**: header grammar — "-1- Run the tests." (the
  file has NO live DB and no DB-gated tests; the previous header
  claimed "a live regab DB is required; SKIP_REGAB_DB=1 skips the
  DB-gated tests" — wrong, as in the D-084 T3 class).
- **T3 FIXED (F5)**: the leftover generation comment ("#
  twolm/test/test_rlm_wmaps.py (sostituisci la classe
  TestRLMWmapsCacheConsistency)") removed — the D-084 T5
  Italian-leftover class.
- **T4 FIXED (F4)**: the dead imports removed — `from io import
  StringIO` AND `from unittest.mock import patch` (zero
  code-level uses in the file; verified by grep/AST).
- **T9 FIXED (F9)**: the 21 non-comment trailing-whitespace lines
  stripped; scope as in D-078 M3: the license-header `# ` lines
  stay.
- **T10 FIXED (F8)**: the coverage batch — 5 new IO tests (the
  golden hash, the valid/mismatched sidecar, the wrong
  description, the version mismatch) + the TestRLMWmapsInit class
  (2 tests).

## Verdict

A complete per-function suite post D-087 (the store/load contract
fully pinned with the 3 RuntimeError messages and both checksum
flags, the compute branches, the consistency branches, the golden
hash, the init validation); the hygiene is clean. The D-085
paths idiom (shared CUSTOM_TMP_BASE + defensive tearDown) is
the only external dependency the file has beyond the module
under test.
