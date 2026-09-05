<!-- ARCHIVED — D-106 step 17 (the docs/ rewrite, 2026-09-04): the
     complete session-27 analysis (D-097) + the D-098
     fix-campaign narrative moved out of
     docs/src/twolm/rlm_generate.md per docs_rules.md
     §1/§4. This is a frozen historical record: it is never
     updated. Stale-in-current-context notes: (1) the "43 checks"
     figure — the current probes/verify_generate.py (the 4091e72
     move) has 15 surviving check calls: A1-A5 (module source),
     B1-B3 (worker source), C1-C2 (the test source), D3 + D11
     (the data-object behavior — the hash identity + the
     hand-re-derived mock golden), E2/E4/E5/E7 (the live-DB
     golden re-derivation), F1 (the pre-declared blackboard
     fields). The D-106 step-3 class c deletions: D1/D2 (init
     validation) + D4-D8 (the IO round-trip + the 3 header
     gates) + D9/D10 (the consistency branches) + D12/D13 (the
     compute error branches) → test_rlm_generate; E1/E3/E8/E9/
     E10/E11 (the bootstrap, the shape/dtype, the files, the
     second instance, the version gate, the _down scope) →
     test_lm_worker_generate; F2/F3 moved to the hub
     verify_logistic_model.py V3c/V3d. The old "43" counted the
     pre-step-3 state (incl. those deleted/moved pins). The
     probe prints "All checks passed." without a numeric count.
     (2) the "615 tests / 74 skipped" full-discover figure
     predates steps 3-16 (current: 664/87 gated); (3) the
     D-097/D-098 campaign narrative is frozen history. -->

# twolm/rlm_generate.py

Analysis date: 2026-09-02 — analysis session 27 (D-097); fix
campaign D-098 approved by Roberto ("R1: esegui i fix", R2 "il
weighted mean è la semantica voluta", "T1-T9: ok", "M1-M5: ok") and
applied in the same session. Brought in by Roberto (commit e31c061 —
the 11th active level of the pipeline — the import + worker-list
entry in logistic_model.py were his; RLMContext already carried the
`w_dense` + `dense_w_checksum` blackboard fields from first import,
L142-143 — the D-094 fg pattern). Probe (scratch/verify_generate.py,
43 checks, tiers A–F, re-pinned to the post-campaign state): 0
mismatches.

The GENERATE domain module of the RLM pipeline: the
`ReversiLogisticModelDenseWeights` data object (the dense weight
vector `w_dense` (K,) float32 over ALL theoretical configurations +
the `w_checksum` metadata anchor) + `compute_w_dense` (the
compressed → dense expansion) + store / load / is_cache_consistent.
The data object of the 11th active level (CREATED sentinel → CONFIG
→ POSITIONS → FEATURES → INDEXES → WMAPS → DESIGN_MTR → ZED →
GRADIENT → OPTIMIZE → GENERATE) and the 5th cache_manager consumer
(the uniform 7-kwargs wiring; the flat file
`rlmwf_10_GENERATE.dat` + `.SHA3-256`, machine closure
`{prefix}{level:02}_{worker_name}.dat`, step 10).

## Suite status (session 27, post D-098)

- `test_rlm_generate`: 14/0/0 (4 classes; no DB, no gate — the
  mock-fixture compute golden, the unknown-category RuntimeError,
  the empty-MOB WARN branch, the 2 consistency branches, the 6 IO
  tests incl. the 3 header gates + the hash golden, the 3 init
  validations) — NEW in D-098 T4 (the bring-in file had 1 test / 1
  class).
- `test_lm_worker_generate`: 3/0/0 live (1 class; 3 DB-gated since
  D-098 T5 — the setUp moves through OPTIMIZE on a fresh base dir,
  so a live DB is required; 3/0/3 under `SKIP_REGAB_DB=1`) — NEW in
  D-098 T5 (the bring-in had no worker test at all).
- Full discover: 615 tests, 74 skipped under `SKIP_REGAB_DB=1`
  (17 PERF + 35 regab + 2 positions + 2 features + 2 indexes + 3
  wmaps + 3 design_matrix + 2 zed + 2 gradient + 3 optimize + 3
  generate), GREEN; ungated (live DB): 615 run, 17 skipped (PERF
  only), GREEN. The full `-W error` discover is clean.

## State per Roberto

Pipeline-in-progress, 11 active levels, enabled by Roberto's
2026-09-02 bring-in (commit e31c061: rlm_generate +
lm_worker_generate + test_rlm_generate, uncommented the
`lm_worker_generate` import + worker-list entry). The next
line-by-line step is `lm_worker_vld_positions` (the next commented
entry). GENERATE fix campaign (D-098) CLOSED: R1 (the
`_for_next_level` call — the D-074 R1 trap re-introduced, see
below), R2 (the unseen/fallback semantics — Roberto's ruling,
documented in-code), T1-T8 + M1-M5 applied; the dedicated
`test_lm_worker_generate.py` added (T5).

## Architecture (225 lines, post D-098)

- `ReversiLogisticModelDenseWeights` (L53-65): plain class, 2
  fields. `__init__` (L56, `@validate_call
  (config=ConfigDict(arbitrary_types_allowed=True))`): `w_checksum:
  str` (the OPTIMIZE compressed-w checksum — the consistency
  anchor) + `w_dense: np.ndarray` (K,) float32 (the NDArray gate
  rejects lists). `compute_sha3_256_hash` (L61, `@validate_call`):
  `sha3_256` over `w_dense.tobytes()` ONLY (the duck-typed
  data-checksum hook, same shape as the 4 siblings).
- `rlm_generate_store_to_file` (L68-75, `@validate_call`): header
  "RGLM Dense Weights binary data file" v1 + the w_checksum string +
  the w_dense array. NO sidecar written here — in the pipeline flow
  the sidecar is written by cache_manager (D-072), same as the 4
  sibling data modules.
- `rlm_generate_load_from_file` (L78-96, `@validate_call`): sidecar
  verify FIRST (the D-096 R3 pattern; `checksum=False` bypasses it),
  then the `expected_description` gate (L89-90: "Wrong file
  format: ..."), then the `expected_version` gate (L91-92: "File
  version mismatch: found {v}, expected 1" — NEW in D-098 T1, the
  4 sibling data modules all have it; the bring-in load was the
  only one gating only the description), then the 2 payload reads.
- `rlm_generate_is_cache_consistent` (L100-101, the house
  no-validation note L99 — T2): `dw.w_checksum == ctx.w_checksum`.
  Single-field by design: it is transitively sound — any upstream
  change (positions / features / indexes / wmaps / design matrix)
  forces the OPTIMIZE re-run and a NEW `ctx.w_checksum`, so a stale
  dense file is always rejected.
- `compute_w_dense` (L105-225, the house no-validation note L104 —
  T2; the TYPE_CHECKING class, the rlm_indexes pattern): unpacks
  the WMAPS artifacts (L114-120), allocates `w_dense =
  zeros(iwmap_feature_offset[-1])` float32 (L122-123 — K, all
  theoretical configurations), then per feature (L125-223):
  - **Intercept** (L137-139, `f.category == 0`): `w[w_min : w_max +
    1]` sliced into the branch (D-098 M1 — the bring-in computed it
    in every branch but used it only here) and its single value
    broadcast.
  - **Mobility** (L141-164, `f.category == 1`): the true (above-
    cutoff) configs come from wmap (`config_id >= 0`), their
    weights via `f_iwmap` (L151-152; the duplicated f_wmap
    recompute removed — D-098 M2); `np.interp` over the full
    0..n_configurations-1 range with automatic clamp at the
    boundaries (L154-162). The ascending precondition of
    `np.interp` is documented in-code (L156-158, D-098 M4): it is
    STRUCTURAL, not assumed — rlm_wmaps allocates the true slots
    via `np.unique`, which emits the configurations in ascending
    order. No-seen configs: the block stays zero and exactly one
    WARN event is logged (L163-164).
  - **Pattern** (L166-220, `f.category == 2`): the weighted mean of
    the seen configs (freq-weighted, L177-180; 0.0 when none) is
    logged (L182), and the trained fallback weight `w[fallback]` is
    logged too when `fallback != −1` (L184-186) but NEVER used —
    the D-098 R2 ruling, documented in-code (L188-197):
  - **Unknown category** (L222-223): `RuntimeError` with the
    precise value (D-098 M3 — the bring-in message carried the
    literal "f.category" source-identifier text).

## The D-098 R2 ruling — unseen/fallback configs at inference

Roberto: "il weighted mean è la semantica voluta ... e' un tema da
data_science non da informatica, ci ho riflettuto a lungo ma credo
che il fallback sia corretto per avere allo stesso tempo stabilità
durante il training e ridurre l'overfitting. Ma durante
l'inference non vedo ragioni per preferire il valore di fallback a
quel medio per le configurazioni rare."

The in-code comment (L188-197) captures the rationale: the
fallback slot is a SINGLE learnable representative — during
training it keeps the loss well-defined and shrinks the rare
configurations (overfitting control); at inference the
frequency-weighted mean of the seen configurations is the plug-in
estimate of the expected pattern contribution under the training
distribution, while the fallback weight is a loss proxy, noisy for
the rare configurations. The weight stays in the logs for
transparency. In rlm_02 (frequency_cut_off 1) there is no fallback
slot at all (feature_w_ranges fallback = −1 for both patterns), so
"unseen → weighted mean" is the active behaviour there.

## Verified facts

- Live golden (rlm_02, probe E tier, SKIP_REGAB_DB-gated): K =
  6588 = 1 (intercept) + 6561 (EDGE) + 27 (DIAG3); `w_dense`
  (6588,) float32; orbit invariance TRUE (the weights are constant
  over the D8 orbits); seen-config exactness TRUE (every computed
  principal carries its trained weight); the FULL independent
  re-derivation (per-feature dense arrays, a different code path)
  `== ctx.w_dense`; weighted means EDGE −0.022497505937226207 /
  DIAG3 0.013062398455957221 (total_freq 799808 = 199952 × 4);
  hash golden `ec9d65453bb112bf277c79f96a86edfa9468bb01f42a2763cd82d69c5b2b15b4`
  == `ctx.dense_w_checksum`.
- Data-object behaviour (probe D tier, no DB): init validation ×2
  (list w_dense + non-str w_checksum → ValidationError), hash
  identity vs an independent `sha3_256(w_dense.tobytes())`,
  store/load round-trip, corrupted sidecar → `RuntimeError:
  Checksum mismatch.`, wrong description → `RuntimeError: Wrong
  file format: ...`, version-2 file → `RuntimeError: File version
  mismatch: found 2, expected 1` (post T1), `checksum=False`
  loads without a sidecar, is_cache_consistent True/False, the
  test-mock fixture golden (hand re-derivation), unknown category
  (9) → RuntimeError, empty-MOB branch → zeros + WARN.
- Context facts (probe F tier): `w_dense` + `dense_w_checksum`
  pre-declared on RLMContext (logistic_model.py L142-143); the
  worker list has 11 active levels (CREATED sentinel + 10 factory
  calls); the 4 later imports remain commented (vld_positions,
  validate, analytics, save).

## Issues

### R1 — `_for_next_level` call: the D-074 R1 trap re-introduced — RESOLVED (D-098)

The bring-in `_up` called `ctx.get_cache_file_full_path_for_
next_level()` (lm_worker_generate.py L52) — a method that does NOT
exist on RLMContext: the StateMachine injects only
`..._for_current_level` (state_machine L190), all 8 other
cache-using workers use it, and verify_logistic_model V4a even pins
"legacy _for_next_level gone from the live context". Empirically:
the full pipeline (fresh base dir, rlm_02) ran the 9 prior levels
fine (checkpoint_optimize.dat + the rlmwf_01/02/04/05/06 files)
and then died in GENERATE — `[10][GENERATE] [ERROR:LOW] Error in
GENERATE during up: 'RLMContext' object has no attribute
'get_cache_file_full_path_for_next_level'`. **Applied (D-098),
Roberto-approved:** the one-line rename to
`get_cache_file_full_path_for_current_level()`. Verified end-to-end
with the name aliased pre-fix (the level works: file + sidecar
written, (6588,) float32, second-instance cache hit) and again
post-fix by the probe E tier + the new worker suite.

## Minor notes

- **M1** (FIXED, D-098) — `f_w = w[w_min : w_max + 1]` was
  computed in every branch but used only in the intercept branch —
  moved inside it (L138).
- **M2** (FIXED, D-098) — the MOB branch recomputed
  `f_wmap_mask` / `f_wmap` (duplicated the L134-135 lines) —
  removed; the branch reuses the feature-level values.
- **M3** (FIXED, D-098) — the unknown-category RuntimeError carried
  the literal source identifier "f.category" in its message — now
  "The feature category is unknown: {f.category}".
- **M4** (FIXED, D-098) — the `np.interp` ascending precondition
  documented in-code (L156-158): structural via rlm_wmaps'
  `np.unique` slot allocation, not an assumption.
- **M5** (FIXED, D-098, in the test) — the mock `ctx.z` was dead
  (compute_w_dense never reads it) — removed.

## Appendix — line reference

225 lines, as of D-098 (206 at the D-097 bring-in; D-098: +2
no-validation notes [T2], +4 the version gate [T1], +11 the R2
comment + the np.interp note [M4], the f_w move [M1], the message
fix [M3], 24 ws lines emptied in place [T7]).

- L28-38: imports (hashlib L30, numpy L31, typing L33, pathlib
  L34, pydantic L35, binio L37, Relevance L38)
- L40-41: `RLMContext` under TYPE_CHECKING
- L45-49: `__all__` (the 5 public names)
- L53-65: `ReversiLogisticModelDenseWeights` (`__init__` L56,
  `compute_sha3_256_hash` L61)
- L68-75: `rlm_generate_store_to_file` (header L72, no sidecar)
- L78-96: `rlm_generate_load_from_file` (sidecar L80-82,
  `expected_description` L84, `expected_version` L85 [T1], gates
  L89-92, payload L93-94)
- L99-101: `rlm_generate_is_cache_consistent` (L99 note [T2])
- L104-225: `compute_w_dense` (L104 note [T2]; intercept
  L137-139 [M1], mobility L141-164 [M2, M4 L156-158, WARN L163-164],
  pattern L166-220 [R2 comment L188-197], unknown L222-223 [M3],
  return L225)
