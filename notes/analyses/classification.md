# a/b/c classification (session 30, D-106 step 1)

Classification of every check group in the 22 `scratch/verify_*.py`
probes, per `notes/probe_rules.md` §3 (a = independent invariant
KEEP; b1 = obsolete, fact evolved — re-pin, pipeline-wide facts in
the hub; b2 = obsolete, purpose served — retire to
`notes/analyses/`; c = overlap — delete, the test pins it). The
o1* one-off scripts are excluded (already decided: b2, archive).

Audit state: 2026-09-04 full run, 28 scripts, DB live, no gate
(see `build/tmp/probe-run/SUMMARY.txt`): 14 green / 13 stale /
1 to investigate. Stale groups are marked STALE; the E2/E3
investigation is resolved at the end of the
`verify_lm_worker_config.py` section (CONTRACT HOLDS — the probe
premises are stale, verified live).

Class marks: **a** keep / **a?** ambiguous-a (note says what
resolves it) / **c** delete (test named) / **c?** ambiguous-c /
**b1-hub** pipeline-wide re-pin (hub `verify_logistic_model.py`
V3c subsumes) / **b1-mod** module-local re-pin / **b2** archive.

---

## verify_t2.py (test_pattern harness — 1 "check" — audit: green)

| check group | asserts | class | rationale / covering test |
|---|---|---|---|
| T2 print-on-failure (2 paths) | the campaign's T2 fix in `test_pattern.TestPatternSetComputePrincipalIndexes.test_one_record`: on assertion failure it prints the golden + re-raises; on success it prints nothing | **b2** | Investigation one-off of a TEST-harness behavior, written for the pattern campaign (session ~7). Purpose served: the T2 fix is in and pinned by the test's own run. No invariant of the pattern module lives in it. Archive with header. |

## verify_pidx.py (pattern, first-principals — 5 checks — audit: green)

| check group | asserts | class | rationale / covering test |
|---|---|---|---|
| CORE 81-entry principal dict + 21 unique principals | pure-Python base-3 re-derivation of `compute_principal_indexes` (board.py D8 only, no pattern.py) vs the goldens | **a** | Same target, INDEPENDENT method (pure Python vs the vectorized pattern code path). `test_pattern.py::TestPatternSetComputePrincipalIndexes` pins the goldens through the code; if code+golden drifted together, only this independent enumeration catches it (the O1 lesson). |
| DIAG3 27-entry dict + 18 unique | same, symmetry_fs=[fa1h8] | **a** | as above |
| ELLE identity dict (81 = range) | same, symmetry_fs=[] (identity) | **a** | as above |

## verify_pattern_tests2.py (pattern, 29 masks — 10 checks — audit: green)

| check group | asserts | class | rationale / covering test |
|---|---|---|---|
| A. 29 masks: orbit size divides 8 + each mask is its orbit's numeric min | independent D8 orbit arithmetic (board only, no pattern.py) | **a** | Independent re-derivation of the principal rule; `test_pattern.py::TestPattern::test_init_rejects_non_minimum_orbit_masks` pins the code behavior, this pins the math it implements. |
| B. ELLE tmasks golden (8 orbit masks, D8 slot order) | orbit masks in the canonized slot order | **a** | Independent (board transformations); the test pins ELLE's tmasks through `PatternSet` code. |
| C. SMALL principal dict + uniques (pure base-3) | 2-square principal reduction, no pattern.py | **a** | as B |
| D. D8 closure on `ar` + trm permutation | group closure + permutation sanity | **a** | Independent group-theory check; no test exercises closure directly. |
| E. large-set arithmetic (13 patterns: order, attribution (i, I, r0, r1), J=49) | index attribution vs the test file's goldens, orbit sizes from first principles | **a** | Independent re-derivation of `TestPatternSet` goldens; the attribution table is cross-checked against the test literals, but the orbit sizes are recomputed, not copied. |

## verify_burnside.py (pattern, Burnside — 31 patterns × 2 formulas — audit: green)

| check group | asserts | class | rationale / covering test |
|---|---|---|---|
| Formula vs ground truth (all 31 patterns) | n_invariant = 3^B(G' orbits) and n_unique = Burnside sum, both vs (1) full 3^S enumeration (no Burnside) and (2) the production `principal_index_count` / `n_invariant_configs` | **b2** | Investigation vehicle ("Read-only Burnside study", docstring L2) that settled the D-032 formulas; purpose served — the attributes are shipped and closed. Sub-check nuance: formula↔enumeration is an independent invariant (would be **a** if kept), formula↔production attribute is **c?** (`test_pattern.py::TestPatternSymmetries::test_burnside_counts_golden` + `test_burnside_counts_invariants` pin the attribute values). Default: archive the whole script per §6; a slimmer permanent probe (formula↔enumeration only) is possible if Roberto wants the formula invariant kept alive. |

## verify_mobility.py (mobility — 6 groups — audit: STALE, crash at L156)

| check group | asserts | class | rationale / covering test |
|---|---|---|---|
| 1. popcount64 scalar + vectorized (200k random + 10 specials) | vs `int.bit_count` (independent oracle) | **a** | Borderline c: `test_mobility.py::TestMobilitySet::test_popcount64` pins 30 hand values, but the 200k-random sweep with an independent oracle is the independent part (rare-value bugs a 30-literal table cannot see). |
| 2. n_configurations brute force (6 cases incl. full overlap 0xF/0xF→9, empty→1) | subset enumeration of all (lms, alms) index values | **a** | `test_mobility.py::TestMobility::test_n_configurations_calculation` pins 1 of the 6 cases by formula; the brute force (incl. the overlap case no formula gives) is the ground truth. |
| 3. compute_indexes vs pure-Python ground truth, 200 random positions × 5 masks + dtype/shape | independent index formula `(lms&m).bc + a.bc - (alms&m).bc` from `board.legal_moves` | **a** | The test pins 2 golden positions (3 masks); the random sweep over 5 masks re-derives every cell. |
| 4. golden [53,13,66] re-derived independently | the test's golden recomputed from board + hand formula | **a** | Classic golden re-derivation: catches a tautological golden in `test_mobility.py::TestMobilitySet::test_compute_indexes`. |
| 5. hash formula + order-insensitivity + empty-set hash + empty masks shape | sha3_256 of sorted (mask, amask) pairs; `e.masks().shape == (0,2)` | **c** (hash/order/empty-hash) + **b1-mod** (the masks call) | The hash re-derivation and order-insensitivity are exactly what `test_mobility.py::TestMobilitySet::test_hash_calculation_verification` + `test_hash_equivalence_same_keys` + `test_init_empty_list` already do (the test re-derives the bytes the same way); the empty-set hash is in `test_init_empty_list`. STALE bit: `e.masks()` is no longer callable — `masks` is a property (the audit crash at L156; `test_init_empty_list` uses `ms.masks`): **b1-mod** re-pin (`e.masks` not `e.masks()`), then this group collapses into the test coverage → delete. |
| 6. underflow boundary (lms=0, alms=0xF → index 3) | independent recompute via `board.legal_moves` on the suite's underflow position | **a** | Re-derives `test_mobility.py::TestMobilitySet::test_compute_indexes_prevents_underflow`'s hand-derived literal 3 (the test computes it by board reasoning in its docstring; the probe computes it programmatically). |

## verify_logistic_model.py (logistic_model — THE HUB, 35 checks — audit: green)

| check group | asserts | class | rationale / covering test |
|---|---|---|---|
| V1a–V1g | RLMContext dataclass shape (plain base, field defaults, legacy `_for_next_level` names gone, `*_for_current_level` fields, lambda default) | **a** | Module-local structural facts; nothing in `test_logistic_model.py` pins the dataclass field table. |
| V8 | `get_type_hints(RLMContext)` succeeds (D-074 R2, no latent NameError) | **a** | Unique: no test or production code ever calls `get_type_hints` on it; this is the only pin of the latent-annotation fact. |
| V6a (valid str → Path) | helper happy path | **c?** | `test_logistic_model.py` builds models with a str path everywhere (implicit); the direct-helper happy branch is not its own test assertion. Resolves if we count implicit coverage — recommend keeping as a (direct branch pin) unless Roberto prefers lean. |
| V6b (valid Path → Path) | direct Path input | **a** | Unique: the tests pass str, never a direct `Path` to the helper. |
| V6 raises (TypeError / IsADirectoryError / FileNotFoundError) | helper bad inputs, D-074 M3 | **c** | `test_logistic_model.py::TestLogisticModel::test_config_path_helper_edge_branches` pins all three with `assertRaisesRegex` + messages. |
| V6f | `LogisticModel(123)` → pydantic ValidationError (`@validate_call` on `__init__`, D-074 R3) | **a** | No test pins the init type-coercion (grep: no ValidationError in test_logistic_model). Fail-fast guard — §4 test-conversion candidate. |
| V7a (valid dir str → Path) | helper happy path | **c?** | Every test passes `base_dir_override=<tmp dir>` (implicit). Same lean question as V6a. |
| V7b (valid dir Path → Path) | direct Path input | **a** | Unique direct call. |
| V7 raises (TypeError / NotADirectoryError) | helper bad inputs | **c** | `test_logistic_model.py::TestLogisticModel::test_base_dir_helper_edge_branches`. |
| V2a–V2d | facade: ctx identity, sm type, verbosity default + setter delegation | **c** | `test_logistic_model.py::test_context_initialization` / `test_state_machine_initialization` / `test_facade_views_and_verbosity_round_trip`. |
| V3a (step 0), V3b (CREATED) | fresh model state | **c** | Pinned at the top of every full-chain test (e.g. `test_lm_worker_indexes.py` L86, `test_lm_worker_config.py` L79). |
| V3c — **15 active levels, full worker list** | the pipeline state | **a (HUB — the canonical pin, §5.3)** | This is the one place the pipeline-wide state may live. Green at 15 (D-104, fe506c6). It subsumes every module-probe copy of the worker-list fact (see the b1-hub rows below). |
| V4a | legacy `_for_next_level` absent from the live ctx (negative fact) | **a** | The tests pin the injected helpers' presence, not the legacy names' absence. |
| V4b/c (closure `__name__`s), V4d (log_event bound method) | injected closures | **c** (V4b/c) / **a** (V4d) | `test_logistic_model.py::test_injected_cache_helpers_are_the_machine_closures` + `test_injected_cache_helper_computes_the_worker_path`; log_event's class is not tested. |
| V5 / V5b | sentinels raise RuntimeError; bare-context no-op path | **c** | `test_logistic_model.py::test_created_sentinel_workers_raise` / `test_pre_injection_fallback_is_no_op_lambda`. |
| V9 ×3 (int 1 / str POSITIONS / move_to_last → ValidationError, step stays at 1) | the gate split (D-076) + D-060 failed-step boundary, on the `{}` config | **a** | Unique: the tests use a valid config and never exercise the empty-config boundary; this pins the exact exception type and the "step stays at the failed step" fact. |
| V10 | 8 `*_checksum` fields, no `features_checksum` | **a** | Module-local field inventory (the in-memory-derivation fact); not pinned in tests. |

## verify_cache_manager.py (cache_manager — 17 V-groups — audit: STALE, ImportError)

The file is unrunnable: it imports `_compute_checksum` / `_save_checksum`,
removed in D-072 (checksum service moved to `twolm.binio`; current
exports: `_verify_checksum`, `_delete_cache_files`,
`_compute_sha3_256_hash` (data duck-typing), `cache_manager_load_or_compute`,
`SHA3_256_CHECKSUM_SUFFIX`).

| check group | asserts | class | rationale / covering test |
|---|---|---|---|
| V1a/b | `_compute_checksum` == independent hashlib sha3_256; 64-char lowercase hex | **b1-mod** | The helper no longer exists (D-072). The fact it checked now belongs to `binio.compute_sha3_256` — and `test_binio.py::test_write_and_verify` + `test_sidecar_format_is_sha3_256sum_compatible` + `test_cache_manager.py::TestChecksumHelpers::test_binio_sidecar_verifies` already pin it. Re-pin = c (delete). |
| V2 (3 sidecar-naming cases incl. extensionless + dotted) | `with_suffix` semantics of the `.SHA3-256` scheme | **a** | Independent naming derivation; `test_cache_manager.py`'s `checksum_path_for` helper assumes the scheme but no test pins the three cases (the extensionless case is unique here). |
| V3a–d | verify: missing→False, save→True, tamper→False, wrong sidecar→False | **c** | `test_cache_manager.py::TestChecksumHelpers` (missing/mismatched/malformed/verifies). (The stale `_save_checksum` import is part of the file-level b1.) |
| V15a–c | sidecar content == bare hexdigest; binio format FAILS; sha3_256sum format FAILS | **b1-mod** → re-pin = **c** | The format fact FLIPPED in D-072: binio sha3_256sum is canonical, bare hex is the legacy compatibility — the opposite of all three claims. Current fact pinned by `test_cache_manager.py::test_sidecar_content_is_binio_format` + `test_legacy_bare_hex_sidecar_still_verifies` + `test_binio_sidecar_verifies`. Delete. |
| V4 | delete removes both files + idempotent | **c** | `test_cache_manager.py::TestChecksumHelpers::test_delete_cache_files_removes_both` + `test_delete_cache_files_does_not_raise_if_missing`. |
| V5a–d (step 0: forced compute + cache warm + INFO msg + no load events) | `is_allowed=False` semantics (D-071 R1) | **c** | `test_cache_manager.py::TestLoadOrComputePipeline::test_step0_not_allowed_forces_computation` (same message, T4 file write, load-not-called). |
| V6 (step 1: missing → compute+store) | pipeline step 1 | **c** | `test_step1_missing_file_forces_computation`. |
| V7a–c (step 2: mismatch → delete + recompute + WARN) | pipeline step 2 | **c** | `test_step2_checksum_mismatch_forces_recomputation` (same WARN text, T7 content). |
| V8a–c (step 3a: load raises → recompute + ERROR text) | pipeline step 3a | **c** | `test_step3a_load_exception_forces_recomputation` (same ERROR text). |
| V9a/b (step 3b: validation fails → recompute) | pipeline step 3b | **c** | `test_step3b_validation_fails_forces_recomputation`. |
| V9c (step 3b WARN "validation failed" message) | the exact WARN | **a** | The test pins the flow + T7 but NOT the step-3b WARN message (verified: no logger assert in that test). |
| V10a/c (success + INFO message) | success path | **c** | `test_success_path_returns_cached_data` (same INFO text). |
| V10b (success returns the SAME object, `is`) | identity, not equality | **a?** | The test uses `assertEqual` (value); the probe uses `is` (identity — a copy with equal content would pass the test but fail here). Resolves if the test asserted identity; as written, the identity check is strictly stronger. |
| V11a/b (data's own checksum, compute + load path) | duck-typed `compute_sha3_256_hash` | **c** | `test_compute_path_returns_data_checksum` / `test_load_path_returns_data_checksum` (literally named V11a/V11b). |
| V12 (non-callable attr → None; dict → None) | duck-typing edge | **c** | `test_checksum_attribute_not_callable_returns_none` + `test_checksum_method_missing_returns_none`. |
| V13 (hash method raises on load → caught → recompute + ERROR) | error branch | **c** | `test_load_path_checksum_method_raises_recomputes` (same "hash boom" text). |
| V16 (logger receives (Relevance, str)) | the logger_fn contract | **a** | Unique: the tests use a MagicMock and never pin the argument types. |
| V17 (str cache_path → AttributeError, no pydantic coercion) | "no @validate_call here" guard | **a** | Unique (no test covers it); §4 fail-fast-guard test-conversion candidate. |

STEP-2 AMENDMENT (2026-09-04, the probes/ move exposed two latent
stale checks — masked in the audit by the ImportError, so the
source-only classification assumed them green): V7c (the step-2 WARN
message, in the V7a–c c-group) carried stale text ("Checksum
mismatch" vs the current "Checksum validation failed for … (sidecar
missing or mismatched) …") and is a c — test_step2_checksum_
mismatch_forces_recomputation pins the exact message + WARN —
DELETED at the move. V17's premise ("no @validate_call") is obsolete:
the function carries @validate_call now (the D-076-era gate idiom)
and pydantic lax mode coerces str → Path (verified live: the inner
store_fn sees a pathlib.PosixPath; the flow then dies
FileNotFoundError in the framework's sidecar write). RE-PINNED as the
coercion check (a — still unique, no test covers it; the §4
test-conversion candidate now converts the coercion fact).

## verify_design_matrix.py (design_matrix — 35 checks — audit: STALE, 1 mismatch)

| check group | asserts | class | rationale / covering test |
|---|---|---|---|
| A1–A8 (rlm_design_matrix.py: lines, explicit-cast fix, no raw take, `__all__`, 4 decorators, T4 note, the -1 guard, redundant guard gone) | source-text, module-local | **a** | Per §4 source-text inspections stay probes. (Line-count pins are rot-prone but house-accepted for campaign pins.) |
| B1–B9 (lm_worker_design_matrix.py: 80 lines, pydantic, 7-arg cache wiring, `_up`/`_down` shape, name, ws) | source-text, module-local | **a** | as A |
| C1–C14 (test_lm_worker_design_matrix.py: D-065 idiom, gate, goldens, step pins WMAPS=5/DESIGN_MTR=6, ws) | test-file meta | **a** | C10 pins the test's own step pins (facts ABOUT the test file — stable: DESIGN_MTR is index 6 in the 15-level list too). |
| D0–D3 (live rlm_01 to DESIGN_MTR: extraction sanity, step 6, shape (10,7), dtype) | live pipeline state | **c** | `test_lm_worker_design_matrix.py` (TestLMWorkerDesignMatrix DB tests) pins the same step/shape/dtype through the same run. |
| D4 (pipeline output == pinned literal) | golden equality | **c** | The test asserts `array_equal` against the same golden. |
| D5 (independent X = iwmap[pindexes + col_offsets] == ctx) | full independent re-derivation | **a** | THE core: recomputes the matrix from iwmap by hand; catches a code+golden tautology (O1). |
| D6/D7/D8 (values in per-feature wmap ranges; per-feature region invariants; intercept column zero) | structural invariants of X | **a** | Independent invariants, no test asserts them in this form. |
| D9 (flat cache file exists) | cache layout | **c?** | The test pins `rlmwf_06_DESIGN_MTR.dat` existence (standard pattern); resolves if the DB test asserts it. |
| D10 (checksum == sha3_256(X.tobytes()), independent recompute) | hash formula | **a** | Independent oracle (hashlib on the array, not the module method). |
| F1 (RLMContext declares the 2 fields) | module-local declaration | **a** | source, module-local |
| F2 (DESIGN_MTR import + entry uncommented) | pipeline state | **b1-hub** | Green (true) but a pipeline-wide worker-list fact — the hub V3c already subsumes it. |
| F3 (the 4 following levels commented out) | pipeline state | **b1-hub (STALE)** | The audit mismatch: all 15 levels are active (D-104). Subsumed by the hub V3c. |
| F4/F5 (rlm_01 stat_model; feature layout [1,1,4,1]/[1,65,27,81]/K=174) | fixture facts, live | **a** | Cross-fixture invariants measured on the live run. |
| G1–G7 (test_rlm_design_matrix.py: imports, idiom, 14 tests, golden hash pin, 3 RuntimeError pins, ws) | test-file meta | **a** | meta |

## verify_feature.py (feature — 22 checks — audit: green)

| check group | asserts | class | rationale / covering test |
|---|---|---|---|
| A (3 hash goldens re-implemented from scratch) | FeatureSet/MobilitySet/PatternSet hashes, pure Python, no twolm.feature | **a** | Independent re-derivation of the `test_feature.py` goldens (copied verbatim from there, then checked against a from-scratch implementation). |
| B (2 orbit-size checks) | per-pattern n_instances in mask order, sum 53 | **a** | Independent orbit computation. |
| C (3 positions × (LMC cross-check + 10-column row)) | pure-Python `compute_indexes` vs the test goldens; LMC vs `board.legal_moves` | **a** | Independent re-derivation; the LMC cross-check is a cross-module invariant. |
| D1 (factory fields) | `new_intercept` / `new_from_mobility` / `new_from_pattern` | **c** | `test_feature.py::TestFeature::test_new_intercept` / `test_new_from_mobility` / `test_new_from_pattern`. |
| D2 (direct construction → RuntimeError) | guard | **c** | `test_feature.py::TestFeature::test_init_raises_runtime_error`. |
| D3 (FeatureSet structure: hash, 53, order, category) | live structure | **c** | `test_feature.py::TestFeatureSet::test_init` pins the same goldens. |
| D4 (wrong intercept category → ValueError) | guard | **c** | `test_feature.py::TestFeatureSet::test_init_invalid_intercept_category_raises_value_error`. |
| D5 (live matrix == pure-Python matrix + dtype) | live cross-check | **a** | The test pins the golden literal; the probe's matrix is independently derived — the O1-style value. |
| D6 (edge shapes (0,10)/(3,0)/(0,0) + dtype) | empty edges | **c** | `test_feature.py::TestFeatureSetComputeIndexes::test_compute_indexes_empty_positions` / `empty_features` / `both_empty`. |
| D7 (4 wrong arg types → ValidationError) | guards | **c** | `test_feature.py::TestFeatureSetComputeIndexes::test_compute_indexes_wrong_argument_type`. |

## verify_generate.py (generate — 43 checks — audit: STALE, 2 mismatches)

| check group | asserts | class | rationale / covering test |
|---|---|---|---|
| A1–A5 (rlm_generate.py: `__all__`, notes, version gate, ws) | source-text | **a** | module-local |
| B1–B3 (lm_worker_generate.py: factory gate, D-074 naming, ws) | source-text | **a** | module-local |
| C1–C2 (test_rlm_generate.py: English comment, ws) | test-file meta | **a** | meta |
| D1/D2 (init: list rejected, non-str rejected) | init validation | **c** | `test_rlm_generate.py::TestRLMGenerateInit::test_init_fails_with_list_w_dense` / `test_init_fails_with_non_str_w_checksum`. |
| D3 (hash == independent sha3_256) | hash oracle | **a** | The test (`test_compute_sha3_256_hash_golden`) pins a golden via the module method; the probe recomputes with hashlib — catches a method+golden tautology. |
| D4 (store/load round-trip + sidecar) | IO cycle | **c** | `test_rlm_generate.py::TestRLMGenerateIO::test_store_and_load_cycle`. |
| D5 (corrupted sidecar → RuntimeError 'Checksum mismatch.') | error branch | **c** | `TestRLMGenerateIO::test_load_with_mismatched_sidecar`. |
| D6 (wrong description → 'Wrong file format') | error branch | **c** | `TestRLMGenerateIO::test_load_rejects_wrong_description`. |
| D7 (version 2 → 'File version mismatch: found 2, expected 1') | version gate (T2) | **c** | `TestRLMGenerateIO::test_load_rejects_version_mismatch`. |
| D8 (checksum=False loads without sidecar) | checksum flag | **c** | `test_store_and_load_cycle` uses `checksum=False` (L241). |
| D9/D10 (is_cache_consistent True/False) | consistency branches | **c** | `TestRLMGenerateCacheConsistency::test_consistent_checksum` / `test_inconsistent_checksum`. |
| D11 (test-mock fixture goldens re-derived by hand: [0.5, -0.2, -0.2, -0.2, 1.0, 1.0, 2.0, 3.0, 3.0]) | hand-computed weighted means | **a** | THE core: the test computes through the code; the probe re-derives the numbers by hand. |
| D12 (unknown category → RuntimeError + message) | error branch | **c** | `test_rlm_generate.py::TestRLMGenerateCompute::test_unknown_category_raises`. |
| D13 (mobility without seen configs → zeros + WARN) | edge branch | **c** | `TestRLMGenerateCompute::test_mobility_without_seen_configs_warns_and_zeroes`. |
| E1 (reaches GENERATE) | live pipeline | **c** | `test_lm_worker_generate.py::TestLMWorkerGenerate::test_compute_and_populate_cache` (step 10). |
| E2 (K = 6588 = 6561 + 27, from iwmap_feature_offset) | cross-derivation | **a** | The test pins `w_dense.shape == (6588,)`; the probe derives K from the FEATURE offset (an independently-produced quantity) and decomposes it — the equality of two separately-derived facts. |
| E3 (shape/dtype (6588,) float32) | live shape | **c** | `test_lm_worker_generate.py` L128-129. |
| E4 (orbit invariance + seen-config exactness) | invariants | **a** | Independent invariant checks, not in the test. |
| E5 (full independent re-derivation == ctx.w_dense) | the whole matrix | **a** | THE core (O1 pattern). |
| E7 (hash golden == ctx.dense_w_checksum) | absolute golden | **a** | The test does a RELATIVE recompute (hashlib vs current ctx field, L135) — both move together if the pipeline drifts; the probe's pinned literal (ec9d6545…) is absolute and catches DB/golden drift. |
| E8 (flat cache file + sidecar verify) | cache layout | **c** | `test_lm_worker_generate.py` pins both files. |
| E9 (second-instance cache hit + w_dense identity) | cross-run | **c** | `test_lm_worker_generate.py::test_read_cache_on_new_instance` (assert_array_equal). |
| E10 (version-2 gate on the real file) | gate | **c** | `test_rlm_generate.py::TestRLMGenerateIO::test_load_rejects_version_mismatch`. |
| E11 (_down clears w_dense + dense_w_checksum) | _down scope | **c** | `test_lm_worker_generate.py::test_down_clears_generate_attributes`. |
| F1 (RLMContext declares w_dense + dense_w_checksum) | module-local declaration | **a** | source |
| F2 (GENERATE uncommented; analytics + save commented) | pipeline state | **b1-hub (STALE)** | Audit mismatch: analytics + save are active (D-103/D-104). Hub V3c subsumes. |
| F3 (13 active levels / 12 factory calls) | pipeline state | **b1-hub (STALE)** | Audit mismatch: 15 levels / 14 calls now. Hub V3c subsumes. |

## verify_gradient.py (gradient — 61 checks — audit: STALE, 2 mismatches)

| check group | asserts | class | rationale / covering test |
|---|---|---|---|
| A1–A13 (rlm_gradient.py: lines, `__all__`, scipy, TYPE_CHECKING, no validate_call, defs, docstring, float32 cast, T3 note) | source-text | **a** | module-local |
| B1–B9 (lm_worker_gradient.py: 62 lines, name, factory gate, non-cache comment, `_up`/`_down`, ws) | source-text | **a** | module-local |
| C1–C10 (test_lm_worker_gradient.py: header, idiom, 2 tests, shape pins, goldens, ws) | test-file meta | **a** | meta |
| D1 (pre-state: ZED step 7, fg None) | live pre-state | **c** | `test_lm_worker_gradient.py` (C10: the test asserts step 7 before GRADIENT). |
| D2 (step 8 / GRADIENT) | live step | **c** | the test pins step 8. |
| D3 (fg callable) | worker output | **c** | `test_lm_worker_gradient.py::test_generate_gradient`. |
| D4 (X (199952,8) uint32, w (2981,) f32, z (199952,) f32) | live shapes | **c** | the test's shape pins (C9). |
| D5 (alpha = ridge/M; clipping 0.01) | config-derived | **a** | Fixture/config invariant, not asserted in the test. |
| D6 (independent float64 re-derivation of f(w=0)) | hand math | **a** | THE core (float64 oracle vs the float32 pipeline). |
| D7 (independent re-derivation of g(w=0) + dtype + golden) | hand math | **a** | THE core. |
| D8 (independent f+g (w≠0) with ridge, random w seed 42) | hand math | **a** | THE core — the ridge term at a non-zero w, re-derived by hand. |
| D9 (closure statelessness: 2 calls equal) | determinism | **a** | Not in the test. |
| D10 (no rlmwf_07*/08* files; 5 files present) | cache layout | **a** | GRADIENT/ZED write no cache — the negative layout fact is module-specific; the 5-file list is the pipeline layout through GRADIENT (stable: levels before GRADIENT are fixed). |
| D11 (live _down: step 7, ZED, fg None) | _down scope | **c** | `test_lm_worker_gradient.py::test_down_clears_gradient`. |
| D12 (feature set: no intercept, DIAG3+EDGE, 8 instances) | fixture fact | **a** | Cross-fixture fact, not in the test. |
| E1 (RLMContext fg field) | module-local | **a** | source |
| E2 (9 active workers in the list) | pipeline state | **b1-hub (STALE)** | Audit mismatch: 15 active now. Hub V3c subsumes. |
| E3 (6 commented imports) | pipeline state | **b1-hub (STALE)** | Audit mismatch: 0 commented now. Hub V3c subsumes. |
| E4/E5 (scipy in pyproject; venv 1.18.1) | workspace/venv facts | **a** | E5 is environment-sensitive (rots on a scipy upgrade) — flag for the hub or drop at re-pin time. |
| E6 (StatModelConfig ridge field, ge=0.0) | schema structure | **a** | No test file covers rlm_config_schemas. |
| E7 (rlm_02 optimization/config values) | fixture fact | **a** | |
| E8 (trailing comma in rlm_02, JSON5) | fixture fact | **a** | |
| G1–G8 (test_rlm_gradient.py: 8 tests, SimpleNamespace ctx, goldens, dtype pins, ridge formula pin, minlength pin) | test-file meta | **a** | meta |

## verify_lm_worker_config.py (lm_worker_config — 35 checks — audit: STALE, 2 mismatches — INVESTIGATED)

| check group | asserts | class | rationale / covering test |
|---|---|---|---|
| A1–A4 (`__all__`, factory name, up/down callables, 6 privates) | source-text | **a** | module-local |
| B1 (step 0 / CREATED) | fresh state | **c** | `test_lm_worker_config.py::TestLMWorkerConfig` L79. |
| B2 (move_to_step("CONFIG") → step 1 / CONFIG) | live move | **c** | `test_lm_worker_config.py::test_move_up` L90. |
| B3 (ctx.cfg is ReversiLogisticModelConfig) | live type | **c** | `test_lm_worker_config.py::test_properties` (class pins the cfg type). |
| B4 (cfg.name round-trips) | live value | **c?** | `test_properties` asserts the cfg fields; resolves if it names `cfg.name`. |
| B5 (base_dir_override wins) | live value | **c** | `TestLMWorkerConfigValidation` builds the json with `"base_dir": "will/be/overwritten"` precisely to pin the override. |
| B6 (use_cache True from config) | live value | **c** | `test_move_up_with_cache`. |
| B7/B8 (rlmwf_01_CONFIG.dat + .SHA3-256 exist) | cache files | **a** | No test pins the CONFIG-level cache files (verified: not in test_lm_worker_config). |
| B9 (no `rlmwf_` subdirectory) | naming layout (D-078) | **a** | Negative layout fact, unique. |
| B10 (.dat == model_dump_json(indent=4)) | content fact | **a** | Unique: no test pins the dump content. |
| B11 (sidecar == raw hex sha3_256 of the dump) | content + format | **a** | Unique: no test pins the sidecar content of the CONFIG file (the binio format tests use their own files). |
| B12 (sidecar NOT in binio format — 1 token) | format asymmetry | **a** | Unique cross-module fact: the CONFIG writer still emits bare hex while binio's parser accepts both. |
| B13 (binio's loader reads the bare-hex sidecar) | cross-module compatibility | **a** | Unique: the D-072 compatibility direction, live-verified. |
| C1–C7 (idempotent re-run; down reset cfg None/use_cache None; config change → new checksum; corrupted .dat → RuntimeError 'not matching'; missing sidecar → RuntimeError 'is missing'; binio-format sidecar → verify False) | live cache semantics of the CONFIG worker | **a** | None of these scenarios (corruption, missing sidecar, binio-format asymmetry, re-run idempotency) is in `test_lm_worker_config.py`. |
| D1 (missing base dir → FileNotFoundError) | guard | **a** | `test_lm_worker_config.py::TestLMWorkerConfigBaseDir` covers file→NotADirectoryError and unwritable→PermissionError, but NOT missing→FileNotFoundError. §4 test-conversion candidate. |
| D2 (file as base dir → NotADirectoryError) | guard | **c** | `test_base_dir_is_a_file_raises_error`. |
| D3 (unwritable dir → PermissionError) | guard | **c (env-dependent)** | `test_base_dir_is_not_writable_raises_error` pins it; note: both test and probe depend on the non-root assumption (as root, 0o444 is writable and neither fails). |
| E1 (domain ValidationError propagates: ec=99) | D-076 gate split | **c** | `test_lm_worker_config.py::TestLMWorkerConfigValidation::test_invalid_ec_out_of_range` (plus the status/hex-mask siblings). |
| E2 (move_to_step("POSITIONS") → ValueError "not found in the pipeline") | unknown-name guard | **b1-hub (STALE — INVESTIGATED, contract holds)** | "POSITIONS" is a VALID worker now (index 2, active since D-097) — the probe premise was written in the 4-worker era. VERIFIED LIVE (2026-09-04, empty config, no DB): `move_to_step("NOT_A_WORKER")` → `ValueError: Worker 'NOT_A_WORKER' not found in the pipeline.` (exact message, state_machine.py L357). Re-pin: any truly-unknown name. The no-exception in the audit is CORRECT behavior, not a bug — no Roberto ruling needed beyond the mechanical re-pin. |
| E3 (move_to_step(2) → IndexError "out of bounds") | out-of-bounds guard | **b1-hub (STALE — INVESTIGATED, contract holds)** | Step 2 = POSITIONS, in bounds in the 15-level list (the probe's era maxed at step 1). VERIFIED LIVE: `move_to_step(99)` → `IndexError: Target step 99 is out of bounds.` (exact message, state_machine.py L362). Re-pin: any index ≥ 15. |
| E4a (bare-context lambda no-op, returns None) | pre-injection fallback | **a** | Unique (the hub's V5b covers `_created_up`'s bare path, not the cache-path lambda). |
| E4b (injected closure w/o cfg → AttributeError) | injection order | **a** | Unique. |
| E5 (`use_cache` absent from `_store_to_file` source) | source-text | **a** | §4 source-text inspection. |
| E6 (rlm_00.json is NOT plain JSON — json5 load-bearing) | data-file fact | **a** | Unique. |
| E7 (down logs "Clearing configuration...") | log message | **a** | `test_lm_worker_config.py::test_move_down` pins the step + use_cache reset, not the message text. |

## verify_lm_worker_features.py (lm_worker_features — 25 checks — audit: STALE, 1 mismatch)

| check group | asserts | class | rationale / covering test |
|---|---|---|---|
| A1–A12 (worker source: lines, `__all__`, factory, TYPE_CHECKING, no cache_manager, @validate_call, amask log, orphan comment, ws) | source-text | **a** | module-local |
| B1a (5 active levels: CREATED, CONFIG, POSITIONS, FEATURES) | pipeline state | **b1-hub (STALE)** | The audit mismatch: 15 levels now. Hub V3c subsumes. |
| B1b (FEATURES entry + import uncommented) | pipeline state | **b1-hub** | Green (true) — pipeline-wide fact, hub V3c subsumes. |
| B2 (RLMContext declares feature_set field) | module-local | **a** | source |
| B3 (rlm_00 feature values: intercept + ALMC/LMC/DLMC + EDGE/ELLE) | fixture fact | **a** | |
| B4 (expected FeatureSet from fixture via PUBLIC API: 1 intercept + 3 mobility + 2 pattern, 16 instances) | independent construction | **a** | Independent derivation through Feature/FeatureSet/Mobility/Pattern public API (not the worker path) — the probe's stated core. |
| B5 (feature_set hash + 512 B + 16×u16, sha3_256 of tobytes, independent) | hash oracle | **a** | The test pins the same literal (453e918a…) through the code; the probe recomputes the formula (C9 cross-ref). |
| B6a (log "Processing feature set" + 5 "Processing feature:" lines) | log content | **a** | Not pinned in the test (the test's docstring mentions 2 lines; the assertions don't read logs). |
| B6b (amask log line prints the real amask — R1) | log content | **a** | The D-082 R1 fact, unique. |
| B7 (4 context attributes set with exact values) | live worker output | **a** | The test pins `feature_set is not None` (C7); the exact 4-tuple with values is the probe's. |
| B8 (rebuild from the cached .dat + identity) | cross-run determinism | **a?** | Resolves if `test_lm_worker_features.py`'s 2 gated (DB) tests include a cache round-trip (2/0/2 suggests it might); as far as the source pins show (C1-C10), the test files' content pins don't mention a second instance. |
| B9 (NO rlmwf_03_FEATURES.dat; 6-file list) | layout: FEATURES is pure compute | **a** | The negative fact is module-specific; the 6-file list (CONFIG+POSITIONS ×2 + sidecars) is the pipeline layout through POSITIONS (stable). |
| B10 (rlmwf_01_CONFIG.dat exists + sidecar verify) | layout | **a** | Cross-level layout observation (the CONFIG file's own pin lives in the config probe/test). |
| B11a (zero features → ValueError) | guard | **a** | §4 test-conversion candidate (fail-fast guard). |
| B11b (positions None → AttributeError) | guard | **a** | §4 test-conversion candidate. |
| B12 (use_cache=False → 6 files, no DB) | live integration | **a** | D-071 R1 pattern in the live pipeline (the generic mocked flow is in test_cache_manager; the live wiring is not). |
| B13 (down: feature_set + hash cleared, step 2) | _down scope | **a** | Not pinned in the test (no down test in test_lm_worker_features per C1-C10). |
| C1–C10 (test file: header, idiom, gate, 2 "Processing" docstring, 3 hash literals, order/counts pin, ws) | test-file meta | **a** | meta |

## verify_lm_worker_positions.py (lm_worker_positions — 51 checks — audit: green)

| check group | asserts | class | rationale / covering test |
|---|---|---|---|
| A1–A6 (`__all__`, factory name, @validate_call, no pathlib, ws) | source-text | **a** | module-local |
| A3 (_down resets the 4 context attributes) | _down scope | **a** | Not pinned in the test. |
| B1 (step 2 / POSITIONS) | live step | **c** | `test_lm_worker_positions.py::test_read_db_and_populate_cache` L99-100. |
| B2 (positions/game_values/rds_checksum set; 64-hex) | live attributes | **a** | The test pins file existence + logs, not the attribute values. |
| B3a/b (stats keys; count 200 / mean / std / var vs independent numpy recompute) | independent re-derivation | **a** | THE core: `training_pop_stats` recomputed with numpy from the live positions. |
| B4 (flat rlmwf_02_POSITIONS.dat + sidecar; no rlmwf_ subdir) | cache layout | **c** | `test_read_db_and_populate_cache` L103-106 pins both files. |
| B5 (sidecar == binio format `<hex>  <basename>`) | live cross-module format | **a** | The test doesn't pin the sidecar content; the format itself is pinned in test_binio/test_cache_manager (their own files). |
| B6 (rds_checksum == duck-typed recomputation) | independent checksum | **a** | Recomputes via `regab_load_data_set_from_file` + `compute_sha3_256_hash` (not the pipeline's path). |
| B7 (log "Extracted 200 positions from the database.") | log message | **c** | `test_read_db_and_populate_cache` L110-111 (assertIn "Extracted" + "positions from the database."). |
| C1 (step 2, second instance) | live step | **c** | `test_read_cache_on_new_instance` L132. |
| C2 (cache hit, no DB — log pins) | live cache | **c** | `test_read_cache_on_new_instance` L136-140 (same "Cache successfully loaded and validated" + NotIn "Extracted"/"established"). |
| C3 (data identity across runs: positions + checksum) | cross-run determinism | **a** | The test pins logs, not data identity. |
| C4 (stats identity across runs) | cross-run determinism | **a** | as C3. |
| D1a/b (use_cache=False: forced compute + cache warm) | live D-071 R1 | **c** | The same orchestration facts (message + file warm) are pinned in `test_cache_manager.py::test_step0_not_allowed_forces_computation` (mocked, same function); the live wiring is source-pinned by F4. |
| D2 (corruption → WARN + delete + recompute, live) | live end-to-end | **a** | The mocked flow is in `test_cache_manager.py::test_step2...`, but the LIVE case (real DB re-extraction, 200 positions, file restored) is a heavy end-to-end re-derivation — §4 stays-probe territory; no test covers the live corruption case. |
| D3/D3b (business inconsistency: ec 20→10 → validation failed + recompute with new params, live) | live end-to-end | **a** | Unique scenario (mutated config → new-params recompute); no test covers it. |
| D4a–g (is_cache_consistent unit: True on match; False on rds/design/wmaps/zd/ridge diffs) | unit semantics | **a** | No test covers `is_cache_consistent` for this worker (verified: not in test_lm_worker_positions.py). §4 test-conversion candidate (deterministic, cheap, single function). |
| E1–E12 (rlm_config_schemas: name required; ec ge/le 100; status enum; masks hex+even; ec int required; ec 99 passes (the D-076 domain check, not the schema); model_validator import; use_cache not in the schema; model_fields; mutable default; ValidationDataSetConfig; StatModelConfig) | schema validation, no DB | **a** | No test file exists for rlm_config_schemas (verified in the test listing). E2b/E3/E4/E5/E11/E12 are §4 test-conversion candidates (deterministic unit behavior of one module). |
| F1–F4 (5-arg RegabDBConnection call; load_fn checksum=False; regab_store docstring; is_allowed wiring) | source-text cross-ref | **a** | §4 source-text inspections |

## verify_logistic_model.py — see the dedicated section above (it IS the hub).

## verify_mobility.py — see the dedicated section above.

## verify_optimize.py (optimize — 92 checks — audit: STALE, 2 mismatches)

| check group | asserts | class | rationale / covering test |
|---|---|---|---|
| A1–A18 (rlm_optimize.py: lines, header, `__future__`, Tuple gone, `__all__`, checkpoint design comment, save/load decorators + gates, R3 sidecar verify, history M6, ws) | source-text | **a** | module-local |
| B1–B11 (lm_worker_optimize.py: lines, name, factory gate, no cache comment, `_up`/`_down`, ws) | source-text | **a** | module-local |
| C1–C16 (test_rlm_optimize.py: header, idiom, 8 classes/31 tests, mock ctx, goldens, ws) | test-file meta | **a** | meta |
| D1–D11 (test_lm_worker_optimize.py: header, idiom, gate, 3 tests, step pins GRADIENT=8/OPTIMIZE=9, lbfgs marker, R4 _down pins, cfg mutation, ws) | test-file meta | **a** | meta |
| E1 (13 active workers, VALIDATE in) | pipeline state | **b1-hub (STALE)** | Audit mismatch: 15 active now (ANALYTICS, SAVE added D-103/D-104). Hub V3c subsumes. |
| E2 (2 commented imports: analytics, save) | pipeline state | **b1-hub (STALE)** | Audit mismatch: 0 commented now. Hub V3c subsumes. |
| E3 (RLMContext pre-declared: w, fg, w_checksum, opt_info, dense_w_checksum) | module-local declaration | **a** | RLMContext field inventory (module fact, not pipeline state). |
| E4 (OptimizationConfig: min_grad Tuple + checkpoint_file Path) | schema structure | **a** | No schema test file. |
| E5 (lbfgs signature: all 16 kwargs) | cross-file source fact | **a** | |
| E6 (lbfgs info dict: the 9 keys) | cross-file source fact | **a** | |
| E7 (x0.copy() — ctx.w never mutated in place) | cross-file source fact | **a** | |
| E8 (rlm_02 optimization block values) | fixture fact | **a** | |
| F tier f1–f10 (checkpoint IO, real files: round-trip; empty history; wrong desc → RuntimeError; wrong version → RuntimeError; file hash golden 6e01ff86…; sidecar format `<hex>  <name>`; sidecar verify True; corrupted → R3 'Checkpoint checksum mismatch'; asymmetric history → M6; f32 values) | checkpoint IO | **c** | `test_rlm_optimize.py::TestRLMOptimizeIO` pins ALL of it with real files: `test_store_and_load_cycle`, `test_empty_history_roundtrip`, `test_history_length_mismatch_raises`, `test_wrong_description_raises`, `test_wrong_version_raises`, `test_checksum_mismatch_raises`, `test_file_golden_hash`, `test_sidecar_produced_and_matches`. |
| G1/G2 (info_dict filters to 5 context keys; KeyError on missing) | helper behavior | **c** | `test_rlm_optimize.py::TestRLMOptimizeHelpers::test_info_dict_filters_to_context_keys` / `test_info_dict_missing_key_raises`. |
| G3 (weights hash golden + independent recompute) | hash oracle | **a** | The test (`test_weights_hash_golden`) pins the literal; the probe recomputes sha3_256 independently — oracle value. |
| G4 (is_cache_consistent 4 branches incl. ridge) | unit branches | **c** | `TestRLMOptimizeCacheConsistency` (4 tests). |
| G5 (status_converged 4 branches) | unit branches | **c** | `TestRLMOptimizeStatusConverged` (4 tests). |
| H1 (full run: step 9 + the 12 base-dir files) | live run + cache layout | **a** | The test pins its own checkpoint file + step 9; the 12-file inventory (6 cache levels × file+sidecar through DESIGN_MTR) is a pipeline-layout observation — stable (levels before OPTIMIZE are fixed). |
| H2 (checkpoint == ctx, via independent fg) | independent cross-check | **a** | Recomputes f from the checkpoint's w with the gradient closure — not the optimizer's own bookkeeping. |
| H3 (loss decreased, independent) | invariant | **a** | |
| H4 (second instance: completed-checkpoint path, no lbfgs) | live resume | **a** | Unique scenario (the test's `test_max_iters_treated_as_completed` is a different situation). |
| H5 (crafted INCOMPLETE checkpoint → resume path) | live resume | **a** | Unique scenario (hand-crafted incomplete state). |
| H6 (changed logit_clipping → zed checksum change → scratch) | live consistency | **a** | Unique live scenario. |
| H6b (R1: ridge-only change → scratch, same zed checksum) | live consistency | **a** | The D-096 R1 pin, live — unique. |
| H7 (use_cache=False → no load, checkpoint still saved) | live D-071 R1 | **a** | Live version of the generic mocked step-0 pin. |
| H8 (R2: corrupted checkpoint → delete + scratch + re-save) | live error path | **a** | Unique live scenario (the corrupted-FILE case is in F8/test; the corrupted-CONTENT live-worker case is unique here). |

## verify_pattern_tests2.py — see the dedicated section above.

## verify_pidx.py — see the dedicated section above.

## verify_rlm_indexes.py (rlm_indexes — ~40 checks — audit: green)

| check group | asserts | class | rationale / covering test |
|---|---|---|---|
| A1–A11 (rlm_indexes.py: lines, `__all__`, 5 decorators, no-validation note, store layout (header/2 strings/3 arrays/2 u32s), load symmetry, version gate, ws) | source-text | **a** | module-local |
| B1 (init attribute identity) | behavior | **c?** | `test_rlm_indexes.py` (14 tests) pins init; identity (`is`) vs the test's equality — resolves if the test asserts identity. |
| B2 (hash == independent sha3_256 of the 3 concatenated arrays) | hash oracle | **a** | Independent recompute vs the module method. |
| B3–B5 (real store/load round-trip + sidecar) | real-file IO | **a** | `test_rlm_indexes.py` mocks ALL file I/O (binio patched — F2 pins that); the probe's unmocked real-disk round-trip is the independent path. |
| B6 (corrupted file + checksum=True → RuntimeError) | real corruption | **a** | The mocked test simulates the branch; the probe corrupts real bytes. |
| B7/B8 (wrong description/version → RuntimeError) | real gates | **a** | as B6 (real files via `binio.BinaryWriter`). |
| B9/B10/B11 (is_cache_consistent True/False branches) | unit branches | **c** | `test_rlm_indexes.py::test_is_cache_consistent...` — F8 pins BOTH single-field branches ("identical_hash" ×8, "outdated" ×2) + the match case. |
| B12/B13 (compute == FeatureSet.compute_indexes called directly, on a real FeatureSet) | independent cross-derivation | **a** | THE core: the rlm_indexes compute path vs the feature module called directly (independent). |
| B14 (init rejects non-str hash → ValidationError) | init guard | **c?** | F7 pins 2 `assertRaises(ValidationError)` in the test (one is the invalid-indexes case); resolves if the non-str feature_set_hash case is the other. |
| C1 (step 4 / INDEXES) | live step | **c** | `test_lm_worker_indexes.py::test_compute_and_populate_cache` L103. |
| C2 (6 files: CONFIG/POSITIONS/INDEXES + sidecars; NO rlmwf_03_FEATURES*) | live layout | **a** | The test pins the INDEXES files' existence; the full list + the FEATURES-negative is the probe's (stable layout through INDEXES). |
| C3 (data checksum == duck-typed recomputation) | independent checksum | **a** | |
| C4 (sidecar == flat sha3_256sum line; file checksum ≠ data checksum) | format + distinction | **a** | Independent recompute + the two-checksum distinction. |
| C5 (shape (N,16) + identity with the independent FeatureSet recompute) | independent re-derivation | **a** | THE core (O1 pattern, the same one that caught D-104 O1's tautology). |
| C6a (second-instance: "Cache successfully loaded and validated") | live cache | **c** | `test_lm_worker_indexes.py::test_read_cache_on_new_instance` L142. |
| C6b (no "Executing heavy computation" on the second run) | live cache | **c** | same test L145. |
| C6c (data identity across runs: checksum + indexes) | cross-run determinism | **a** | The test pins steps + logs, not data identity. |
| C7 (down to FEATURES: rlm_indexes + checksum cleared, step 3) | _down scope | **a** | No down test in test_lm_worker_indexes (the 2 tests are compute + cache). |
| D1–D6 (lm_worker_indexes.py: lines, `__all__`, factory gate, cache wiring, `_up`/`_down`, ws) | source-text | **a** | module-local |
| E1–E7 (test_lm_worker_indexes.py: header, D-065 idiom, gate, 2 tests, rlmwf_04 pin, ws) | test-file meta | **a** | meta |
| F1–F9 (test_rlm_indexes.py: header, mocked binio, 14 tests, 2 ValidationError pins, both consistency branches, ws) | test-file meta | **a** | meta |

## verify_save.py (save — 32 checks incl. LONG — audit: green)

| check group | asserts | class | rationale / covering test |
|---|---|---|---|
| A1–A15 (worker @validate_call, no pathlib, no ws; model_weights header/`__all__`/10 fields; rlm_client no dead import/`__all__`; test file gate/idiom/ws; fixture values) | source-text + fixture | **a** | module-local; A10–A14 are test-file meta |
| B1/B2 (read guards: wrong description → ValueError; wrong version → ValueError) | guards | **c** | `test_lm_worker_full_chain.py::TestModelWeightsReadGuards::test_wrong_description_raises` / `test_wrong_version_raises`. |
| C1 (15 levels, step 14 / SAVE) | pipeline state | **c** | `test_lm_worker_full_chain.py::TestFullChainA2030::test_full_worker_chain` L105-106 (and A2050 L304-305). (Also hub-covered worker-list fact; the test pin makes it c.) |
| C2 (vld_metrics 7 exact, rlm_04) | live goldens | **c** | the test pins the same 7 (L109-117). |
| C3 (train_metrics 7 exact) | live goldens | **c** | the test pins the same 7 (L119-126). |
| C3b (train_dense_metrics 4 exact, D-105) | live goldens | **c** | the test pins the same 4 (L128-131, re-pinned at D-105). |
| C4 (training_pop_stats 4 exact, context float64) | live goldens | **c** | the test pins the same 4 (L134-137). |
| C5 (opt_info 5 keys: converged/reason/iters + f + g_norm) | live values | **c + a** | The test pins `converged`/`reason`/`iters` (L140-142) but NOT `float(f)`/`float(g_norm)` — those two are the probe's (**a** portion). |
| C6 (file 21603 B + sha3 bcf8d918… + sidecar verify) | live file | **c** | the test pins size + hash + `verify_sha3_256_sidecar` (L153-158). |
| C7/C8/C9 (read-back: metadata; f32 tps/opt/vld; fs hash + iwmap + w_dense hash 7ecdeba6…) | read-back | **c** | the test pins the same read-back values (L160-198). |
| C10 (ef 6 training positions bit-exact) | client function | **c** | the test pins the same 6 (L229-241). |
| C11 (ef vld[42] bit-exact 11.932792663574219) | client function, vld | **c** | the test pins exactly this (L243-245, the w_dense substitution path). |
| C12 (console pins: report title + 3-metric table row + Population row + Gap 0.18 + Delta 0.01 + "Validation completed" + "Saving model weights") | console content | **a + c** | The log lines "Validation completed…"/"Saving model weights…" are pinned by the test (L203-204, **c** portion); the 3-metric TABLE rows + Population/Gap/Delta rows are NOT (the test asserts only the report title, L208-209) → **a** portion. |
| C13 (file report: masked hash d44557a8… + sections) | file report | **c** | the test pins the same hash (L223). |
| C14 (second instance: byte-identical file + 6 cache hits) | determinism | **c** | `test_second_instance_deterministic` L246-263 (6 hits pinned at L263). |
| D1–D7 (rlm_03 LONG: step 14; vld 7; train 7; dense 4; pop 4; opt 5; file 515042 B + hash; read-back subset) | rlm_03 goldens | **c** | `TestFullChainA2050::test_full_worker_chain` pins the same (L302-420; hash 57f9766b at L365, size L370, read-back L395-402). |
| D8 (rlm_03 console pins incl. the table rows + Delta -0.00) | console content | **a** | The test A2050 pins the title (L349-350) but not the table rows. |
| D9 (rlm_03 file report masked hash 57f9766b… + sections) | file report | **c** | the test pins the same hash (L365). |
| D10 (rlm_03 ef 6 training positions bit-exact) | client function | **c** | the test pins the same 6 (L423+). |

## verify_t2.py — see the dedicated section above.

## verify_validate.py (validate — ~25 checks — audit: STALE, 2 mismatches)

| check group | asserts | class | rationale / covering test |
|---|---|---|---|
| A1–A13 (worker + rlm_validate: name/`__all__`, factory gate, no dead imports, R1 `Any` import, header name, no cache_manager, 7-key dict, underscore unpack, _down scope, sigmoid reuse, test-file existence) | source-text | **a** | module-local; A8 is meta |
| B1 (VALIDATE import + entry uncommented) | pipeline state | **b1-hub** | Green (true) — hub V3c subsumes. |
| B2 (2 commented imports: analytics, save) | pipeline state | **b1-hub (STALE)** | Audit mismatch: 0 commented now. Hub V3c subsumes. |
| B3 (13 active levels / 12 calls) | pipeline state | **b1-hub (STALE)** | Audit mismatch: 15/14 now. Hub V3c subsumes. |
| B4 (RLMContext pre-declares vld_metrics + analytics_report) | module-local declaration | **a** | source |
| C1 (reaches VALIDATE step 12) | live step | **c?** | `test_lm_worker_validate.py` exists (A8 pins it; 3/0 + 2/0/2) and its DB tests run through VALIDATE — resolves if it asserts step 12. |
| C2 (vld_metrics 7 exact, rlm_02) | live goldens | **c?** | the test's DB tests pin the rlm_02 goldens (2/0/2) — resolves by reading its assertions; expected c. |
| C3 (log lines: "Starting model validation…", "Validation completed. Loss… 7.00794393e-03", "RMSE/MAE: 1.27", index/compute lines) | log content | **c?** | `test_lm_worker_full_chain.py` pins the "Validation completed" line for rlm_04 (L203); for rlm_02 the validate test may pin it. Resolves by reading `test_lm_worker_validate.py`. |
| C4 (internal consistency: mse_z == 2·loss; mae ≤ rmse (Jensen); rmse² ≈ mse; samples == len; z ∈ [0,1] band) | invariants, re-derived from ctx | **a** | Independent re-derivation in invariant form; no test asserts these relations. |
| C5 (no rlmwf_12 cache file) | layout: pure compute | **a** | Negative layout fact, module-specific. |
| C6 (second instance: identical metrics + no DB re-extraction + 6 cache hits) | cross-run determinism | **a** | Not in the validate test (2/0/2: the 2 DB tests are golden-run focused). |
| C7 (_down clears vld_metrics at step 11) | _down scope | **a?** | Resolves if `test_lm_worker_validate.py` has a down test (not evident from the source pins). |
| D1 (full metric math on the hand-computed 2-position case) | hand math | **a** | §4 test-conversion candidate (hand-computed unit math). |
| D2 (all values Python floats; samples int) | type facts | **a** | |
| D3 (zero-guarded RMSE/MAE line: perfect Y-space fit → "n/a" line, no ZeroDivisionError) | fail-fast guard (M1) | **a** | §4 test-conversion candidate (the D-102 M1 guard). |

## verify_vld_positions.py (lm_worker_vld_positions — ~24 checks — audit: STALE, 2 mismatches)

| check group | asserts | class | rationale / covering test |
|---|---|---|---|
| A1–A8 (worker: name/`__all__`, D-074 naming, factory gate, checksum=False load_fn, no dead imports, ws) | source-text | **a** | module-local |
| B1 (VLD_POSITIONS import + entry uncommented) | pipeline state | **b1-hub** | Green — hub V3c subsumes. |
| B2 (2 commented imports: analytics, save) | pipeline state | **b1-hub (STALE)** | Audit mismatch. Hub V3c subsumes. |
| B3 (13 active levels / 12 calls) | pipeline state | **b1-hub (STALE)** | Audit mismatch. Hub V3c subsumes. |
| B4 (RLMContext pre-declares vld fields + vld_metrics/analytics_report) | module-local declaration | **a** | source |
| B5 (ValidationDataSetConfig: bid/status, no ec field) | schema structure | **a** | No schema test file. |
| C1 (reaches VLD_POSITIONS) | live step | **c?** | `test_lm_worker_vld_positions.py` (A2xxx, 2/0/2) runs through VLD_POSITIONS — resolves if it asserts step 11. |
| C2 (structured (N,2) + dtype of context fields) | live shape | **c?** | expected c (the test pins the vld arrays). |
| C3a (count == len) | invariant | **a** | re-derived |
| C3b (stats == independent float64 recompute) | independent re-derivation | **a** | THE core |
| C3c (live goldens: 200 / 3.64 / 23.81 / 566.91) | live goldens | **c?** | resolves if the test pins the same stats literals. |
| C3d (rds_checksum e8087903… + int8 range [-58, 56]) | live goldens | **c?** | resolves if the test pins the checksum literal. |
| C4 (vld checksum != training checksum) | cross-fixture invariant | **a** | |
| C5 (rlmwf_11_VLD_POSITIONS.dat + sidecar verify) | cache layout | **c?** | the test pins the file (standard pattern). |
| C6 (second instance: cache hit + data identity) | cross-run | **a?** | resolves if the 2nd gated test of `test_lm_worker_vld_positions.py` is a cache round-trip with data comparison. |
| C7 (_down clears the 4 vld attributes) | _down scope | **a?** | resolves if the test has a down test. |
| D1 (factory name) | unit | **a** | |
| D2–D7 (is_cache_consistent override semantics: True on match; False on bid/status/ec-override/connection diffs; no override → False) | unit semantics | **a** | No test covers this override (verified: test_lm_worker_positions.py has no is_cache_consistent tests either). §4 test-conversion candidate. |
| D8 (load_from_db + is_cache_consistent are the REUSED lm_worker_positions functions, by `__module__`) | identity fact | **a** | Unique — pins the reuse (no re-implementation). |

## verify_wmaps.py (wmaps — 64 checks — audit: STALE, 1 mismatch)

| check group | asserts | class | rationale / covering test |
|---|---|---|---|
| A1–A13 (rlm_wmaps.py: lines, no accumulate, `__all__`, decorators, no-validation note, R1 contract docstring, store docstring, ws, above_mask line) | source-text | **a** | module-local |
| B1–B6 (lm_worker_wmaps.py: lines, name, factory gate, 7-arg cache wiring, `_up`/`_down`, ws) | source-text | **a** | module-local |
| C1–C16 (test_rlm_wmaps.py: header, idiom, D-087 T10 load-path tests, init class, goldens, ws) | test-file meta | **a** | meta |
| D1–D4 (test_lm_worker_wmaps.py: gate, idiom, goldens, ws) | test-file meta | **a** | meta |
| E1 (reaches WMAPS step 5) | live step | **c** | `test_lm_worker_wmaps.py::TestLMWorkerWmapsExactValues` (the DB test moves to WMAPS). |
| E2 (iwmap_feature_offset [1,2,4,5,6,8,9] uint32) | live goldens | **c** | `TestLMWorkerWmapsExactValues` pins the same literals. |
| E3 (iwmap 834 entries + dtype + 603 zeros / 111 ones / 120 twos) | live goldens | **c** | the test pins the same counts. |
| E4 (wmap length 7 + [0,4,4,6,7,16,32] + uint8) | live goldens | **c** | the test pins the same. |
| E5 (wmap_fallback length 8, all 0) | live goldens | **c** | the test pins the same. |
| E6 (per-feature region invariants: wmap[k] < n_instances[k]+1; 64 ≤ wmap[k] ≤ 1055) | invariants | **a** | Structural invariants, not literals; no test asserts them in this form. |
| E7 (feature-region offset identity: iwmap_feature_offset[k+1] == Σ n_instances[0..k] + 1) | cross-invariant | **a** | Independent re-derivation across two fields. |
| E8 (cross-check: independent FEATURE `compute_indexes` == iwmap values) | cross-module re-derivation | **a** | THE core (O1 pattern). |
| E9 (hash == sha3_256 of the 4 concatenated arrays, independent recompute) | hash oracle | **a** | The test pins the hash literal; the probe recomputes the formula — oracle value. |
| E10 (rlmwf_05_WMAPS.dat + sidecar verify) | cache layout | **c** | the test pins the files. |
| E11 (second-instance cache hit + no recompute + identity) | cross-run | **a?** | Resolves if `test_lm_worker_wmaps.py`'s 2 gated tests include a cache round-trip with data identity (2/0/2 suggests it might). |
| E12 (_down clears the 7 wmaps fields at step 4) | _down scope | **a?** | Resolves if the test has a down test. |
| F1/F2 (rlm_01 / rlm_00 stat_model values) | fixture facts | **a** | |
| F3 (rlm_01 use_cache True, prefix 'rlmwf_') | fixture fact | **a** | |
| F4 (WMAPS import + entry uncommented) | pipeline state | **b1-hub** | Green — hub V3c subsumes. |
| F5 (RLMContext declares the 7 Wmaps fields) | module-local declaration | **a** | source |
| F6 (the 5 later levels commented: design_matrix, zed, gradient, optimize, generate) | pipeline state | **b1-hub (STALE)** | THE audit mismatch: all 15 levels active (D-104). Hub V3c subsumes. |

## verify_zed.py (zed — 60 checks — audit: STALE, 2 mismatches)

| check group | asserts | class | rationale / covering test |
|---|---|---|---|
| A1–A12 (rlm_zed.py: lines, `__all__`, class line, decorators, hash scope, factory decorator + math pins a/b/a1/b1, no-validation note, compute body, no cache API, TYPE_CHECKING, ws) | source-text | **a** | module-local |
| A13–A15 (factory math: alpha 0.02 golden [0.02,0.5,0.545,0.98]; round-trip; endpoints) | factory behavior | **c** | `test_rlm_zed.py::TestZedFunFactory` pins the same: `test_factory_alpha_0.02_golden` (the same literal), `test_round_trip`, `test_endpoints_for_two_clipplings` (0.02 AND 0.03 — a superset of the probe's). |
| B1–B8 (lm_worker_zed.py: lines, name, factory gate, 7-arg cache wiring, `_up`/`_down`, no cache, ws) | source-text | **a** | module-local |
| C1–C10 (test_lm_worker_zed.py: header, idiom, gate, 2 tests, docstring "12066", rlm_01.json, step 7, y+z goldens, down test, ws) | test-file meta | **a** | meta |
| D1 (pre-state: zed fields None) | live pre-state | **c?** | The test's first DB test likely asserts pre-state; resolves by reading `test_lm_worker_zed.py`. |
| D2 (step 7 / ZED) | live step | **c** | the test pins step 7 (C7). |
| D3 (game_values == golden y) | live goldens | **c** | the test pins expected_y (C8). |
| D4 (z == golden z literal) | live goldens | **c** | the test pins expected_z (C8). |
| D5 (independent float32 recompute == ctx.z) | independent recompute | **a** | THE core: y2z formula re-derived by hand (the test pins the literal; the probe recomputes). |
| D6 (float64 reference matches) | precision oracle | **a** | Independent-precision check (the f32-vs-f64 gap bound). |
| D7 (zed_checksum == sha3_256(z.tobytes()), independent recompute) | hash oracle | **a** | The test pins the literal (3d49fd5d…); the probe recomputes the formula. |
| D8 (y2z/z2y callables on ctx) | wiring | **a?** | Resolves if the test asserts the closures. |
| D9 (live closure endpoints 0.03: 0.03/0.5/0.97) | live wiring | **a** | The factory endpoints at 0.03 are in the test's golden table; the LIVE closure (ctx.y2z, injected from the cfg alpha) is the integration fact — unique here. |
| D10 (live round-trip) | live wiring | **a** | as D9 (the worker-injected closure, not the factory directly). |
| D11 (no rlmwf_07_ZED*; 10-file list) | layout: ZED is pure compute | **a** | Negative layout fact, module-specific; the 10-file list is the pipeline layout through DESIGN_MTR (stable). |
| D12 (live _down: step 6, DESIGN_MTR, 4 attributes None) | _down scope | **c** | `test_lm_worker_zed.py::test_down_clears_zed_attributes` pins exactly this (C9). |
| F1 (RLMContext zed fields, lines 129–132) | module-local declaration | **a** | source |
| F2 (8 active workers, list at L213) | pipeline state | **b1-hub (STALE)** | Audit mismatch: 15 active now. Hub V3c subsumes. |
| F3 (7 commented imports: zed…save, total 7) | pipeline state | **b1-hub (STALE)** | Audit mismatch: 0 commented now. Hub V3c subsumes. |
| F4 (test_rlm_zed.py exists, 10 tests) | meta | **a** | |
| F5 (4 zed mirror docs exist) | workspace state | **a** | Meta (docs existence) — low value at re-pin; candidate to drop. |
| G1–G10 (test_rlm_zed.py: header, 3 classes/10 tests, no-DB claim, ws, imports, goldens incl. the alpha-0.02 literal + round-trip + endpoints) | test-file meta | **a** | meta |

---

# SUMMARY

| file | #a | #b1 | #b2 | #c | notes |
|---|---|---|---|---|---|
| verify_analytics.py | 14 | 3 | 0 | 6 | B1/B2/B3 pipeline state → hub (B2/B3 stale, B1 green); C4b/C6 c (test_lm_worker_analytics goldens); C2/D1-D4 = the epistemic core (independent math) |
| verify_burnside.py | 0 | 0 | 1 | 0 | investigation vehicle for D-032 — archive; sub-note: formula↔enumeration would be a standalone **a** if kept |
| verify_cache_manager.py | 4 | 2 | 0 | 11 | file-level b1: stale imports (`_compute_checksum`, `_save_checksum` — D-072); V15 format fact flipped in D-072 (re-pin = c); V9c/V10b/V16/V17 the a's |
| verify_design_matrix.py | 24 | 2 | 0 | 4 | F3 STALE → hub; D5/D10 + D6-D8 invariants the core |
| verify_feature.py | 6 | 0 | 0 | 9 | D1-D4/D6/D7 → test_feature (named per group) |
| verify_generate.py | 9 | 2 | 0 | 14 | F2/F3 STALE → hub; E5/E7/D11 the core |
| verify_gradient.py | 15 | 2 | 0 | 8 | E2/E3 STALE → hub; D6-D8 float64 re-derivations the core |
| verify_lm_worker_config.py | 20 | 2 | 0 | 5 | E2/E3 INVESTIGATED → **contract holds, premises stale** (live-verified: ValueError/IndexError with exact messages for genuinely bad targets); no bug, no ruling needed beyond re-pin (E2 → unknown name, E3 → index ≥ 15) |
| verify_lm_worker_features.py | 17 | 2 | 0 | 0 | B1a STALE → hub; B4-B13 the independent-derivation core |
| verify_lm_worker_positions.py | 20 | 0 | 0 | 7 | B1/B4/B7/C1/C2/D1 c (test_lm_worker_positions + test_cache_manager); B3/D4/E the core |
| verify_logistic_model.py | 14 | 0 | 0 | 12 | HUB: V3c = the canonical 15-level pin (§5.3); V6f/V9/V8 unique guards |
| verify_mobility.py | 4 | 1 | 0 | 3 | b1-mod: `e.masks()` → property (the crash); groups 1-4/6 the independent core |
| verify_optimize.py | 21 | 2 | 0 | 17 | E1/E2 STALE → hub; F tier all c (TestRLMOptimizeIO); H tier (H1-H8) the live-resume core |
| verify_pattern_tests2.py | 5 | 0 | 0 | 0 | all 5 groups independent (board-only re-derivation) |
| verify_pidx.py | 3 | 0 | 0 | 0 | pure-Python principal-dict re-derivations |
| verify_rlm_indexes.py | 13 | 0 | 0 | 6 | B tier real-file (test mocks binio); C5 the O1 core; B9-B11/G c |
| verify_save.py | 3 | 0 | 0 | 15 | B tier c (TestModelWeightsReadGuards); C12/D8 console-table rows the a's; rest c (full-chain goldens) |
| verify_t2.py | 0 | 0 | 1 | 0 | test-harness investigation one-off — archive |
| verify_validate.py | 8 | 3 | 0 | 4 | B2/B3 STALE → hub; C4 invariants + D1-D3 the core (D1/D3 = test-conversion candidates) |
| verify_vld_positions.py | 10 | 3 | 0 | 0 | B2/B3 STALE → hub; C3b/D2-D8 the core (D2-D7 = test-conversion candidates) |
| verify_wmaps.py | 14 | 3 | 0 | 11 | F6 STALE → hub; E6-E9 invariants the core |
| verify_zed.py | 14 | 2 | 0 | 12 | F2/F3 STALE → hub; D5-D10 the independent core; A13-A15 → test_rlm_zed |

**Totals (check groups, 22 files):** a ≈ 218 · b1 = 28 · b2 = 2 · c ≈ 108
(plus ~17 `a?`/`c?` marks that resolve as noted — most favor a: the
test files pin goldens through the code, the probes re-derive them
independently, which is exactly the O1 value.)

## Migration implications (for the next steps, not a decision)

1. **b1-hub (22 rows)**: 9 module probes carry duplicated
   pipeline-state pins (design_matrix F3, generate F2/F3, gradient
   E2/E3, optimize E1/E2, validate B2/B3, vld_positions B2/B3, wmaps
   F6, zed F2/F3, lm_worker_features B1a, + green duplicates
   analytics B1-B3, design_matrix F2, features B1b, wmaps F4, zed —
   count per file in the table). All subsumed by the hub V3c — delete
   from the module probes, keep the hub as the single owner.
2. **Stale-but-green facts to re-pin at the hub, not in modules**: the
   15-level list is already green at the hub; no module probe should
   re-assert any worker-list fact after the split.
3. **§4 test-conversion candidates** (a-checks that are cheap
   deterministic unit behavior of one module): verify_lm_worker_config
   D1/E2/E3 (re-pinned) + E4b; verify_lm_worker_features B11a/B11b;
   verify_lm_worker_positions D4a-g/E2b/E3/E4/E5/E11/E12;
   verify_vld_positions D2-D7; verify_validate D1/D3;
   verify_cache_manager V17; hub V6f. Each conversion = its own commit
   keeping the suite green.
4. **b2 archive (2)**: verify_t2.py + verify_burnside.py →
   notes/analyses/ with the ARCHIVED header (burnside with the
   optional slim-probe note).
5. **E2/E3**: not a bug. The investigation resolved the open
   "contract or bug" question: the contract holds (exact messages
   verified live); only the probe premises (written in the 4-worker
   era) are stale.
