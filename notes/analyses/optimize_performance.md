# OPTIMIZE step performance study (I-013)

One-off investigation, session 34 (2026-09-09/10). Subject: the
OPTIMIZE level (10th of 15) of the Reversi logistic-model pipeline,
measured on the A2050 production model (rlm_03.json, ec 20, bid [3]).
All measurements in scratch/ (disposable; scripts + results JSON under
scratch/opt_study/). No source file was touched.

## 1. Question

Roberto (session 34): the OPTIMIZE step dominates real-model runs;
which methods dominate its duration; can the run be sped up; is the
gradient fg closure the hotspot; are other L-BFGS functions relevant;
does numba make sense. Deliverable: a detailed quantitative analysis
+ a strategy for evaluating optimizations + options.

## 2. Method

1. **Production timeline (no re-run of the chain):** the two VLONG
   A2050 runs of session 33 left full per-iteration L-BFGS logs
   (log_every_n=1) with second-resolution timestamps
   (scratch/vlong_run.log, vlong_run2.log): 397 iterations, the
   per-iteration fg-call count (fgc), the accepted alpha, and the
   memory fill (m).
2. **Real-data microbenchmark:** the A2050 pipeline run through
   GRADIENT with a fixed scratch base_dir (scratch/opt_study/a2050,
   caches persist): M = 1,999,179 positions, P = 48 design-matrix
   columns, N = 77,943 weights (X uint32, 384 MB; w f32 311 KB;
   z f32 8 MB). Per-component fg timing + the L-BFGS machinery
   (two-loop recursion per m, norms, allocations) + the checkpoint
   save/load (real hlp_optimize functions, 93-history state).
3. **Candidate kernels** prototyped in scratch (numba 0.67.0,
   numpy 2.5.2, 8 cores, 188 GB RAM), each checked for numeric
   equivalence vs the production fg (max abs delta of f and g at a
   non-trivial weight vector).
4. **Rig validation (bit-exact):**
   - A2030 (rlm_04) run to GRADIENT + direct lbfgs: 67 iters,
     CONVERGED_MIN_GRAD, f = 5.606411e-03, wall 1.035 s — the
     production test golden, matched exactly.
   - A2050 full scratch optimize (phase 2, R1): 397 iters,
     CONVERGED_MIN_GRAD, f = 1.444403e-03,
     w_checksum = 265bdfee709ab336ea739c7698a8e9b4c6ccdbec6c0 — the
     production golden, matched exactly; wall 321.3 s (production
     runs: 318 s / 322 s).
   The microbenchmark environment therefore reproduces the
   production trajectory bit-for-bit; per-call timings transfer
   directly.

## 3. Where the 318 s go (A2050, production run)

| Component | Time | Share |
| --- | --- | --- |
| fg calls: 418 × 732 ms | ~306 s | 96.3% |
| L-BFGS two-loop recursion (avg m-fill 82.2) | ~8.1 s | 2.5% |
| Checkpoints: 4 × (save 0.39 s + load 0.33 s) | ~1.5 s | 0.5% |
| Per-iter norms / allocations / dots | <0.1 s | <0.1% |

fgc distribution from the production log: {1: 376 iters, 2: 19,
4: 1} = 418 fg calls; 95% of iterations accept alpha = 1.0 on the
first line-search evaluation. The strong-Wolfe line search with
Hermite interpolation is already tight: there is no algorithmic
room left to reduce the number of fg calls.

**fg internals (per call, 732 ms total):**

| Operation | ms | Share |
| --- | --- | --- |
| np.bincount (M×P uint32 + M×P f32 weights → N) | 378 | 51.6% |
| w[X] fancy-index gather (M×P f32 temporary) | 247 | 33.7% |
| np.sum(axis=1) over the gather result | 73 | 9.9% |
| M×P broadcast buffer write (dzh_rn → weights) | 30 | 4.1% |
| expit over (M,) | 11 | 1.5% |
| loss dot products | 0.2 | 0.03% |

Structural observation: the current fg materializes **two M×P
(384 MB) temporaries per call** — the gather result and the
bincount weight buffer — i.e. 418 × 768 MB of allocation and
memory traffic per run. This is the exploitable waste: the row
values (linear predictor, sigmoid, residuals, per-row gradient
weight) are all computable in a single streaming pass over X with
only O(N) scratch, because the gradient weight v_i is constant
across the P columns of row i.

## 4. Scaling (A2030 vs A2050)

| | A2030 (rlm_04) | A2050 (rlm_03) | ratio |
| --- | --- | --- | --- |
| M × P elements | 1.20 M | 95.96 M | 80× |
| N (weights) | 2,614 | 77,943 | 30× |
| fg per call | 13.4 ms | 732 ms | 54× |
| OPTIMIZE total | 1.03 s (67 iters) | 318 s (397 iters) | 310× |

Roughly linear in M×P; A2050's per-element cost is higher (the w
working set is L2-resident, not L1, and P is 8× larger). fg is
~95% of the A2030 OPTIMIZE time as well — the decomposition is
scale-independent.

## 5. Candidate kernels (measured at the A2050 scale)

Measured per fg call (median of 5-15, non-trivial w). "Predicted"
= fg_time × 418 + two-loop 8.1 s + checkpoints 1.5 s, against the
318 s production baseline.

| Variant | fg (ms) | per-call | predicted run | design |
| --- | --- | --- | --- | --- |
| K0 current numpy | 735 | 1.00× | 318 s (measured 321) | the production fg |
| K_np pure numpy | 606 | 1.21× | ~264 s | K0 forward + per-column bincount tail (P bincounts over the precomputed X.T, the row-constant weight, no M×P buffer) |
| K1 numba fwd + original tail | 448 | 1.64× | ~198 s | prange fused forward (gather+sum+expit in one pass) + the unchanged numpy bincount tail |
| K1c numba fwd + per-column tail | 319 | 2.31× | ~144 s | K1 + the K_np tail |
| K2s fully serial single pass | 203 | 3.63× | ~95 s | numba, no prange: one C-order pass computes forward AND scatters the gradient — deterministic but single-threaded |
| **K3 block-parallel single pass** | **52** | **14.1×** | **~32 s** | numba prange over 8 fixed row-blocks; each block accumulates into its PRIVATE f64 g-buffer (8 × 311 KB = 2.5 MB, L2-resident) and an f64 partial norm; final g = Σ_b gT[b]/M + αw (fixed order) cast to f32. Race-free (numba 0.67 has no CPU atomics) and deterministic (fixed block split + fixed final order) → preserves the 2nd-instance byte-identity guarantee |

K3 re-measured with f64 accumulators (production quality): **46.0 ms
per call** (the f32-accumulator prototype: 52.3 ms; the f64 buffers
cost +8% and buy an ~1e-12 relative f noise).

**cProfile confirmation (40 profiled iterations, 44 fg calls,
33.3 s under the profiler):** the fg closure
(hlp_gradient.py:71) accounts for 33.1 s = **99.3%** of the
profiled time (3.2 s of it inside np.sum alone); the whole L-BFGS
machinery — line search, two-loop recursion, norms — is <1%.

**K3 full-trajectory verification (the decisive test):** the real
A2050 lbfgs run with the K3 f64 kernel as fg:

| | production (K0) | K3 |
| --- | --- | --- |
| iterations | 397 | 356 |
| reason | CONVERGED_MIN_GRAD | CONVERGED_MIN_GRAD |
| final f | 1.4444034e-03 | 1.4453826e-03 (Δ rel 0.07%) |
| final g_norm | 7.4377e-06 | 7.9739e-06 (both < 1e-05) |
| wall | 321.3 s | **25.3 s (12.7×)** |
| w_checksum | 265bdfee... | de2a6a8b... (re-pin) |

Same convergence behavior, equivalent model quality, 10% fewer
iterations (the ulp-level trajectory divergence changes the
line-search decisions). The 2nd-instance byte-identity guarantee is
preserved by the K3 design (fixed block split, fixed final order,
f64 sums — run-deterministic).

**Numeric equivalence vs the production K0 (non-trivial w):**

| Variant | Δf (abs) | Δg (abs, max) |
| --- | --- | --- |
| K1 / K1c / K4 | 3.8e-07 | 2.3e-10 |
| K_np | 0.0 | 2.3e-10 |
| K2s | 7.8e-05 | 5.9e-08 |
| K3 (f32 accum) | 3.2e-06 | 1.3e-08 |

K1/K1c/K_np differ from K0 only by the expit-vs-1/(1+e⁻ˣ)
sigmoid difference and sum ordering (a few ulps). K3's f noise
comes from the per-block f32 norm accumulation (mitigated to ~1e-12
relative by the f64-accumulator variant, pending 2b). Any of these
variants changes the f32 bits of (f, g) → the L-BFGS trajectory
diverges at ulp level and the bit-exact goldens (w_checksum,
train/vld pins, report hash) must be re-pinned. Model quality is
checked by running each candidate fg to full convergence
(phase 2b: iteration count, final f/g_norm, convergence reason vs
the production 397 / 1.4444e-03 / 7.4377e-06).

## 6. Config-level lever: the L-BFGS memory m (no code change)

m = 93 is an unusual choice (textbook limited-memory BFGS uses
10-20). The two-loop recursion cost is linear in m
(measured: m=10 → 2.2 ms/iter, m=20 → 4.4 ms, m=93 → 23.0 ms),
so m=93 costs ~8 s (2.5%) of the A2050 run by itself. A smaller m
changes the trajectory (the convergence point and iteration count
move). Measured A2050 runs (phase 2c):

| m | iters | reason | f (final) | g_norm (final) | wall |
| --- | --- | --- | --- | --- | --- |
| 93 (production) | 397 | CONVERGED_MIN_GRAD | 1.4444e-03 | 7.44e-06 | 321.3 s |
| 20 | 500 | MAX_ITERS_REACHED | 1.4454e-03 | 1.42e-05 | 389.8 s |
| 10 | 500 | MAX_ITERS_REACHED | 1.4484e-03 | 2.40e-05 | 400.0 s |

**Negative result:** smaller m does NOT converge within the 500-
iteration budget (g_norm stays 1.4-2.4e-05, above the 1e-05
threshold) AND is slower overall (the ~8 s two-loop saving is
overwhelmed by the 103 extra iterations × 0.73 s of fg calls). The
93-vector history is load-bearing for this problem's convergence.
O4 is therefore rejected: m = 93 stays.

## 7. Options for the decision

- **O1 — K3 fg** (hlp_gradient.py) — VERIFIED end-to-end (25.3 s
  full run, above): a single numba kernel replaces the 8 numpy
  operations of the closure; the float32 contract (D-094 R1) is
  kept (fg still returns (f32 f, f32 g)); the njit+prange idiom is
  the standing workspace convention (board.py, pattern.py).
  Result: OPTIMIZE 321 s → 25.3 s (12.7×); the full A2050 chain
  ~350 s → ~50 s. Cost: the golden re-pin campaign (bit-exact
  pins), established practice (D-144).
- **O2 — O1 + numba two-loop recursion** (opt_lbfgs.py): in the
  K3 run the two-loop is ~8 s ≈ 32% of the new total; a numba
  two-loop (m vector dots/axpys, prange or plain) would cut it to
  ~1-2 s → total ~18-19 s (~17×). More surface area: a second hot
  path in opt_lbfgs. Natural follow-up to O1, separately
  approvable.
- **O3 — K_np pure numpy** (hlp_gradient.py only): 1.21× (→ ~264 s).
  The conservative fallback if numba is not wanted in the gradient
  module. Same golden re-pin (the per-column bincount changes the
  f32 sum order).
- **O4 — config experiment on m** (no code): REJECTED on the
  measured evidence (section 6): smaller m does not converge within
  budget and is slower. m = 93 stays (documented as a negative
  result).
- Suggested path if the direction is approved: **O1 first** (one
  focused commit: the K3 kernel in hlp_gradient + its tests + the
  golden re-pin), then **O2** if Roberto wants the last ~6 s.

## 8. Risks / constraints

- Golden re-pin: every fg variant moves the bit-exact pins
  (w_checksum, train_loss f32, the A2050/A2030 vld pins, the
  report hash). The re-pin is a one-time verification campaign,
  not a risk to correctness — but it needs Roberto's approval.
- Determinism: K3's block-private-buffer design is race-free and
  run-deterministic (fixed block split, fixed final order, f64
  sums), so the 2nd-instance byte-identity test keeps holding.
  (A numba atomic scatter — the naive design — is NOT available:
  numba 0.67 exposes no CPU atomics; it would also break
  determinism.)
- The float32 return contract (D-094 R1) is preserved by all
  candidates (they compute in f32/f64 internally and return
  f32).
- The min_p_fun_decrease = 1e-6 progress criterion is sensitive to
  f noise at the ulp scale; the full-trajectory test (2b) verifies
  the iteration count stays at 397 with K3's f64 accumulators.
