<!-- ARCHIVED — D-106 step 15 (the docs/ rewrite, 2026-09-04): the
     complete session-25 analysis (D-093) + the D-094
     fix-campaign narrative moved out of
     docs/src/twolm/rlm_gradient.md per docs_rules.md
     §1/§4. This is a frozen historical record: it is never
     updated. Stale-in-current-context notes: (1) the "61 checks"
     figure — the current probes/verify_gradient.py (the 4091e72
     move) has 54 check calls: A1-A13 (module source), B1-B9
     (worker source), C1-C10 (the worker-test source), D0 + D5-D10
     + D12 (live-DB golden re-derivation survivors — invoked via
     the live() helper, NOT counted by the plain check() grep),
     E1 + E4-E8 (cross-file facts), G1-G8 (the dedicated unit-test
     source). The D-106 step-3 class c deletions: D1-D4 (pre-state
     / step 8 / fg callable / X-w-z shapes) + D11 (_down live) →
     test_lm_worker_gradient; E2/E3 moved to the hub
     verify_logistic_model.py V3c/V3d; 61 − 5 − 2 = 54. The
     pipeline bootstrap (move to GRADIENT) survives as a
     side-effect of the D5-D12 block (the GRADIENT bootstrap
     noted in the step-3 campaign sweep); (2) the "573 tests / 68
     skipped" full-discover figure predates steps 3-10 (current:
     664/87 gated); (3) the D-093/D-094 R1 + T1-T9 + M campaign
     narrative is frozen history. -->

# twolm/rlm_gradient.py

Analysis date: 2026-09-01 — analysis session 25 (D-093); fix
campaign D-094 approved by Roberto (the R1 cast + "T1-T9 falli
tutti" + M1 OK / M2 left as-is) and applied in the same session.
Brought in by Roberto (commit a0adc6e — the 9th active level of the
pipeline — the import + worker-list entry in logistic_model.py were
his; RLMContext already carried the `fg` blackboard field from first
import, logistic_model.py L135). Probe (scratch/verify_gradient.py,
61 checks, tiers A–G, re-pinned in D-094 to the post-campaign
state): 0 mismatches.

The GRADIENT domain module of the RLM pipeline — the function-only
module: NO data class, NO store / load / is_cache_consistent, NO
init validation, NO hash (unlike every other rlm_* level). Two
public names: `sigmoid` (the scipy `expit` wrapper) +
`rlm_gradient_compute` (the closure builder: captures X, z and
`alpha = ridge_regularization / M`; the returned `fg(w)` evaluates
the normalized loss and gradient). The 9th active level (CREATED
sentinel → CONFIG → POSITIONS → FEATURES → INDEXES → WMAPS →
DESIGN_MTR → ZED → GRADIENT) and the SECOND non-cache level (after
ZED): no cache_manager wiring, no rlmwf_07* / rlmwf_08* file ever —
the next cache level takes rlmwf_08.

## Suite status (session 25, post D-094)

- `test_rlm_gradient`: 8/0/0 (2 classes; no DB, no gate — the
  sigmoid goldens/symmetry, the handcrafted-mock compute: the
  zero-weights goldens 4/75 + [1/30, 0, −1/30], the nonzero-weights
  full math vs the independent float64 re-derivation, the ridge /M
  scaling, the minlength empty-bucket pin, the R1 float32 dtype
  pins, the closure statelessness) — NEW in D-094 (M1).
- `test_lm_worker_gradient`: 2/0/0 live (1 class; both tests
  DB-gated since D-094 T5 — the setUp moves through ZED on a fresh
  base dir, so a live DB is required).
- Full discover: 573 tests, 68 skipped under `SKIP_REGAB_DB=1`
  (17 PERF + 35 regab + 2 positions + 2 features + 2 indexes + 3
  wmaps + 3 design_matrix + 2 zed + 2 gradient), GREEN; ungated
  (live DB): 573 run, 17 skipped (PERF only), GREEN. The full
  `-W error` discover is clean.

## State per Roberto

Pipeline-in-progress, 9 active levels, enabled by Roberto's
2026-09-01 bring-in (commit a0adc6e: the two modules + the test +
rlm_02.json, uncommented the `lm_worker_gradient` import + worker-
list entry). The next line-by-line step is `lm_worker_optimize`
(the next commented entry). GRADIENT fix campaign (D-094) CLOSED:
R1 (the float32 cast on the return — the behaviour change Roberto
chose: "la funzione dice che ritorna float32, facciamo ritornare un
float32"), T1 (scipy in pyproject.toml), T2 (the worker factory
@validate_call), T3 (the no-validation note), T4 (9 source ws
lines), T5 (the test gate), T6 (the test D-085 idiom), T7 (the
_down test), T8 (4 test ws lines), T9 (the sigmoid docstring).
M1 (the dedicated suite) added; M2 left as-is by Roberto's call
(the sigmoid stays a bare wrapper — it is called in the
optimization hot loop); M4 left as-is (the triple blank lines are
the canonical pattern of all 8 worker files).

## Architecture (91 lines, post D-094)

- `sigmoid(x)` (L42-49, in `__all__` L39): `return expit(x)` — the
  scipy `expit` (L34 import). NO `@validate_call` (M2: Roberto's
  call — the hot-loop wrapper). Docstring (L43-48): the naive
  `1 / (1 + exp(−x))` is what it replaced; T9 (D-094) fixed the
  "funxtion" typo + "provide" grammar and the stability claim
  ("very small values of x" → "extreme values of x" — expit's
  advantage is where the naive `np.exp(−x)` overflows, large
  negative x).
- `rlm_gradient_compute(ctx)` (L53-91): NO `@validate_call` — the
  source documents why (L52 note, the rlm_indexes L166 class:
  `RLMContext` under TYPE_CHECKING, the circular-import issue).
  Captures: `N = len(ctx.w)` (L60), `X = ctx.design_matrix`
  (L61), `M, P = X.shape` (L62), `X_flat = X.ravel()` (L63),
  `z = ctx.z` (L64), `alpha = ridge_regularization / M` (L65) —
  the per-position normalization (docstring L54-58). Pre-allocates
  the (M·P,) float32 buffer + (M, P) view (L68-69) once, outside
  the closure.
- The `fg(w)` closure (L71-89): `linear_predictor =
  np.sum(w[X], axis=1)` (L72) — the per-row sum of the WEIGHT
  VALUES at the cell w-indices (NOT X·w — X holds w-indices, not
  feature columns); `zh = sigmoid(lp)` (L73); `dzh = zh·(1−zh)`
  (L74); `rn = zh − z` (L75); `f = 0.5·(‖rn‖²/M + alpha·‖w‖²)`
  (L77-79) — the normalized MSE + ridge; `g = bincount(X_flat,
  weights=broadcast(dzh·rn)) / M + alpha·w` (L82-87) — the
  broadcast (L84: each row m spreads `dzh_rn[m]` over its P cells)
  + `np.bincount` accumulation + `minlength=N` (g keeps the full
  (N,) shape even for uncovered w-indices); return (L89, R1/
  D-094): `np.float32(f), g.astype(np.float32, copy=False)` — BOTH
  outputs float32, matching the return annotation.
- `return fg` (L91).

## Verified facts

- f(w=0) = 0.020493777 (float32) and g(w=0) re-derived
  independently in float64 (np.add.at + hand-rolled sigmoid vs
  expit) on the live rlm_02 dataset (199952 positions) — matching
  the test goldens (0.02049378 / 3.558e-4 / −2.395e-4 / 1.101e-3)
  at the test tolerances (probe D6/D7).
- f + g at a seeded w ≠ 0 (the ridge term included) re-derived the
  same way — the closure is the exact normalized MSE + ridge
  gradient (probe D8).
- The closure is stateless: two evaluations of the same w are
  identical (the pre-allocated buffers do not leak — probe D9 +
  the dedicated test_closure_stateless).
- R1 (D-093) → FIXED (D-094): before the cast, `g` came back
  FLOAT64 (np.bincount upcasts the float32 weights to float64)
  while the return annotation said NDArray[np.float32] (f was
  already float32, matching its annotation). After the cast both
  outputs are float32 (pinned by the dedicated test_output_dtypes
  + the probe D7).
- The zero-weights goldens are exact: with w = 0 and ridge 0,
  f = 0.5·mean((0.5−z)²) and g[k] = 0.25·Σ_{m: X[m,*]=k}(0.5−z[m])
  / M (the dedicated test pins 4/75 and [1/30, 0, −1/30] on a
  (3, 2) handcrafted matrix).
- The ridge term is exactly linear in ridge: g(b)−g(a) =
  (b−a)/M·w and f(b)−f(a) = 0.5·(b−a)/M·‖w‖² (the dedicated
  test_ridge_scaling — the /M normalization pinned directly).

## Minor notes

- M2 (left as-is by Roberto's call): the exported `sigmoid` has no
  @validate_call — it is a one-line hot-loop wrapper called at
  every optimization iteration; decorating it would also reject
  scalar input (expit itself accepts scalars).
- M3 (informational, by design): the SECOND non-cache level (after
  ZED) — the rlmwf_08* file never materializes; the next cache
  level (OPTIMIZE) takes rlmwf_08. The per-position /M
  normalization is by design (dataset-size-independent
  convergence criteria, docstring L56-57).
- M4 (left as-is): the worker file's triple blank lines
  (lm_worker_gradient.py L39-41 / L43-45) are the canonical
  pattern of ALL 8 worker files (every sibling shares them — a
  house style, not a defect).
- Performance (post-pipeline, Roberto's note → ideas.md I-013):
  this closure is the suspected pipeline bottleneck for large
  models — a speed-up study is planned for after the pipeline is
  complete.

## Integration notes

- The GRADIENT worker (`lm_worker_gradient`) calls
  `rlm_gradient_compute(ctx)` in `_up` and stores the closure in
  `ctx.fg` (the pre-declared RLMContext field, logistic_model.py
  L135); `_down` clears it. The NEXT level (OPTIMIZE — not yet
  brought in) will consume `fg` — the float32 return contract (R1)
  is what the optimizer will see.
- The scipy `expit` is the only special-function dependency of the
  pipeline (scipy in pyproject.toml since D-094 T1).

## Appendix — line reference

91 lines, as of D-094 (90 at the D-093 bring-in; D-094: +1 note
line [T3]; the R1 cast + T9 docstring + 6 ws lines changed in
place).

- L28-34: imports (typing L30, numpy L31-32, scipy.special.expit
  L34)
- L36-37: `RLMContext` under TYPE_CHECKING
- L39: `__all__` (the 2 public names)
- L42-49: `sigmoid` (docstring L43-48 — T9 fixed line L47)
- L52: the no-validation note [T3]
- L53-91: `rlm_gradient_compute` (docstring L54-58; captures
  L60-65; buffer L68-69; `fg` L71-89 — lp L72, sigmoid L73, dzh
  L74, rn L75, loss L77-79, gradient L82-87, R1 return L89;
  `return fg` L91)
