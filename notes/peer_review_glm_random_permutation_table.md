# Independent Peer Review — The Random Permutation Table (ODP-9, v3.1)

> **Document under review:** `notes/random_permutation_table.md`
> (v3.1, 2026-09-11 — the "pre-third-review hardening" revision, AFTER the
> DeepSeek V4 Pro review (v1+v2) and the Kimi K3 review, whose three
> amendments are marked ADOPTED).
> **Previous reviews:** `notes/peer_review_random_permutation_table.md`
> (DeepSeek V4 Pro — PASS, two passes), `notes/
> peer_review_kimi_random_permutation_table.md` (Kimi K3 — PASS WITH
> THREE REQUIRED AMENDMENTS, adopted in v3).
> **This review:** the requested THIRD independent voice (GLM 5.3). I read
> the v3.1 document and the implementation (`src/reversi/lm/
> hlp_random_play.py`, `src/reversi/tools/prng.py`) BEFORE reading the two
> prior reviews, then read them to check for capture. Where I agree I say
> so briefly; my findings are my own. Unlike the prior reviews, I did not
> stop at re-derivation: I ran numerical verification of the v3.1
> quantitative claims (multinomial two-corpus TV experiments and the
> phase-combinatorics counterexample — scripts and outputs in the
> Appendix; nothing outside this file was written in the workspace).
> **Date:** 2026-09-12.
> **Verdict: PASS WITH REQUIRED AMENDMENTS.** The G₁ construction, the
> proof architecture (oracle theorem + reclassification), and the gate
> ARCHITECTURE all survive a third hostile pass. But the v3.1 hardening —
> the quantitative layer added AFTER both prior reviews signed off —
> contains **one decisively wrong calibration formula** (the D₀ noise,
> understated by a factor of 6–36×: §2 below) and **one invalid "PROVEN"
> tag** (the §6.4 phase bound, falsified by an explicit counterexample:
> §3 below). As specified, the 1e6 design gate is **unpassable by
> construction** for any broadly-supported sub-variable — a perfect G₀
> twin of itself would fail criterion (i). The T6 gate must NOT run on
> the v3.1 numbers.

---

## 0. The question, restated without the document's framing

The thesis put to me: **G₁ (a seeded permutation table + a per-game
counter walk, no PRNG in the hot loop) is a solid way to extract the
statistical frequency characteristics of the patterns the model selects,
and this analysis gives the same results as an analysis done on a
G₀-generated population.**

I evaluate that thesis at full strength, and I evaluate the v3.1 text —
including the numbers added after the two prior reviews, which is
exactly the layer neither of them saw (both reviewed v2/v3 substance;
the v3.1 quantifications — the D₀ noise figures, the bootstrap design,
the "20×/70× above the noise" margins, the 1e7 build-gate band math —
are new and unreviewed. The document's own §9 sentence "no third review
is requested" was, in retrospect, wrong: unreviewed quantitative claims
slipped into the gate's calibration between the second review and the
build. That is what this review catches.)

---

## 1. The proven core — independently re-verified, and confirmed

I re-derived everything the document tags PROVEN before touching the new
material. All of it holds:

- **Lemma 1** (permutation of a uniform is uniform): trivial, correct.
- **Lemma 2** (the counter covers every residue once per k steps):
  correct. Note the balanced-design consequence is about the counter
  residues WITHIN one game — valid — and is distinct from the
  cross-slot phase claim of §6.4, which is where I find trouble (§3).
- **Theorem 1 v2 (the oracle)**: correct, and the right level. Given a
  FIXED (position, counter) supplied from outside, `P_k[c mod k]` with
  `c mod k` a fixed residue and `P_k ~ Uniform(S_k)` is uniform by
  Lemma 1, carried to the legal set by the canonical-order bijection.
  I confirmed the semantics against `pick_move`
  (`hlp_random_play.py` L187-208): `rank = table[k][counter % k]`,
  rank-th set bit, counter+1 on a real move, unchanged on a pass. The
  oracle statement is the faithful semantics of that code.
- **The k = 2 counterexample** (§6.3) against the table-dependent index:
  valid and decisive. `I = 1{P₂ = [1,0]}` makes `P₂[I]` a point mass.
- **The entry-consumption mechanism** ("uniform over the unconsumed
  entries, deterministic on reuse"): re-derived independently, exact.
  The conditional distribution of the remaining entries of a uniform
  permutation, given the consumed ones, is uniform on the remaining
  values. Confirmed.
- **The TV = 1/k same-width pair law**: re-derived exactly. G₀'s two
  independent uniform draws coincide with probability 1/k; G₁'s two
  same-width picks read one permutation at two indices and NEVER
  coincide; TV between the two pair laws = 1/k. Confirmed, including
  the fallback boundary (any number of independent counters still read
  the same row: `P_k[a] ≠ P_k[b]` — the distinctness survives every
  counter-based fallback; the escape hatch is the partial G₀ retreat
  at small-k plies). I confirm the Kimi K3 sharpening.
- **A1**: acceptable. `build_pick_table` (L160-184) is a correct
  descending Fisher–Yates over the seeded MT19937 port; 2016 draws
  total; the rows come from disjoint segments of one stream, so
  cross-row independence is part of A1 — standard, low-risk, and
  empirically re-checked by gate test 1. The floor-of-double reduction
  note (≤ k·2⁻⁵³) is correct.
- **The slot-phase necessity** (§4.3): confirmed against the code
  (`counter0`, pass consumes no step). Without it the corpus is one
  trajectory × N. Load-bearing, not an optimization.
- **The arrest exactness claim** (§1.5: "the arrest ec is reached
  EXACTLY, ec drops by 1 per real move"): I checked this against the
  Reversi rules and `ec_of` (L129-140). A real move places one disc
  (+1 occupied) and flips discs between colors (occupied UNCHANGED);
  a pass changes nothing. So `64 − popcount(occupied)` decreases by
  exactly 1 per real move, and the code's `ec <= ec_target`
  pre-ply check is equivalent to `==` by monotone unit steps. The
  claim is correct; the trajectory-dependent quantity is the pass
  count, exactly as v3 states. The MAX_PLIES=300 guard is sound
  (≤ ~121 plies by the double-pass rule).
- **The reclassification (E1-corpus: proven → gated)**: correct, and I
  confirm independently that no cheap re-proof exists (the conditional
  kernel argument collapses into the same circularity both prior
  reviews documented; the counter walk across widths is not a
  (t,m,s)-net). The gate is the right instrument for the corpus-level
  claim.

**The two prior reviews' substantive verdicts — local semantics proven,
corpus-level gated, scope discipline as the document's best feature —
are correct, and I am not captured by them: I checked each load-bearing
point myself before reading them.** Where this review diverges from both
is below.

---

## 2. REQUIRED AMENDMENT A — the D₀ noise formula is wrong (understated 6–36×), and the v3.1 calibration built on it collapses

This is the sharpest finding of the third review. Neither prior review
could have caught it: the D₀ quantification entered the document in v3.1.

### 2.1 The error, surgically

§5 states:

> the D₀ noise (the TV between two i.i.d. G₀ corpora, E[TV] ≈ 0.4·√(2·S/N),
> S = Σp(1-p), N ≈ games × 40 position-samples): ≈ 1e-4 at 1e6 ... and
> ≈ 3e-5 at 1e7

The constant 0.4 = ½·√(2/π) is the correct Gaussian mean-absolute-
deviation factor. The derivation up to

  E[TV] = ½ · Σ_i E|Δ_i|  ≈  (1/√(πN)) · Σ_i √(p_i(1−p_i))

is right. The error is a single illegitimate substitution:
**Σ_i √(p_i(1−p_i)) was replaced by √(Σ_i p_i(1−p_i)) = √S.** By
subadditivity of the square root (Σ√x_i ≥ √(Σx_i), equality iff a
single cell carries all the variance), the document's formula is a
**strict lower bound** on the true noise — the single-effective-cell
limit. The understatement factor is

  S½ / √S,  where S½ ≡ Σ_i √(p_i(1−p_i)) ≈ √(number of effectively
  contributing cells),

which is √C ≈ 36 for a near-uniform 1296-cell table — and the document
labels its 8.9e-5 figure "near-uniform", the worst case for the error.

### 2.2 Numerical verification (I ran it)

Two independent multinomial corpora of N position-samples each, TV
between the frequency tables, 20 replicate pairs, C = 1296:

| table | N (population) | simulated E[TV] | v3.1 formula | correct formula S½/√(πN) | sim / v3.1 |
|---|---|---|---|---|---|
| uniform, C=1296 | 4e6 (1e5 games × 40, pooled) | **1.02e-2** | 2.83e-4 | 1.02e-2 | **36×** |
| uniform, C=1296 | 4e7 (1e6 games × 40, pooled) | **3.20e-3** | 8.94e-5 | 3.21e-3 | **36×** |
| uniform, C=1296 | 1e6 (per-ec stratum, the PRIMARY test-2a unit) | **2.02e-2** | 5.66e-4 | 2.03e-2 | **36×** |
| power-law head (S½≈20) | 4e7 | 1.79e-3 | 8.62e-5 | 1.78e-3 | 21× |
| geometric (S½≈6) | 4e7 | 5.2e-4 | 8.71e-5 | 5.4e-4 | 6× |

The correct closed form matches the simulation to <1% in every row; the
v3.1 formula is off by the predicted S½/√S factor throughout. (Script in
the Appendix; ran under the project venv, nothing written outside this
file.)

### 2.3 The "verified numerically" claim is a formula evaluating itself

§7 test 2 says: "verified: 2.8e-4 at 1e5 → 8.9e-5 at 1e6, ratio exactly
√10". I checked what those numbers are: **2.828e-4 = 0.4·√(2/4e6) and
8.944e-5 = 0.4·√(2/4e7) exactly** — they are the closed form's own
outputs with S = 1, to the digit. Likewise the "4.9e-5 concentrated"
figure back-solves to exactly S = 0.300 in the same formula. The scaling
ratio √10 is genuine (TV noise is 1/√N), but the absolute levels were
never measured against a real two-corpus TV; the "verified" numbers are
the formula confirming itself. The actual two-corpus TV at 1e5 games for
a near-uniform 1296-cell table is **1.0e-2, not 2.8e-4**. A numerical
verification that cannot disagree with the formula it verifies is not a
verification.

### 2.4 The consequences, one by one

1. **Criterion (i) of the pass rule is unpassable by construction for
   broad-support tables.** The 95th percentile of D₀ at the 1e6 gate,
   pooled marginal, uniform C=1296, is ≈ 3.3e-3 (CV of TV is small,
   ~2%, so q95 ≈ mean·1.04) — **ABOVE delta\* = 2e-3**. A perfect G₀
   twin of the G₀ reference would fail the ABSOLUTE criterion. For the
   per-ec strata (the PRIMARY comparison, N ≈ 1e6 positions, not ×40)
   pure noise is ≈ 2.0e-2 — **ten times delta\***. And at the 1e7 BUILD
   gate the per-stratum noise is still ≈ 6.4e-3 > delta\* for uniform
   tables. As written, the gate does not test G₁; it tests whether the
   tables are concentrated enough, and it fails the generator for a
   property of the pattern set.
2. **The §5 margin claims are wrong.** "delta* = 2e-3 sits ≈ 20× ABOVE
   the 1e6 D₀ noise (≈ 70× the 1e7 noise)": with the corrected noise,
   for a uniform 1296-cell table delta* sits 0.6× BELOW the 1e6 pooled
   noise and ~2× above the 1e7 pooled noise. The true margin is
   table-dependent (5e-4–2e-2 at 1e6 pooled), and the sentence must be
   recomputed per (sub-variable × stratum) from measured S½.
3. **The §7 band math ("5-60× the 1e7 noise", "at 1e7 such a bias is
   5-60σ") inherits the error** and must be redone after the noise
   floor is corrected.
4. **The bootstrap design is sounder than the numbers around it.**
   Criterion (ii) — D below the 95th percentile of the MEASURED
   G₀-vs-G₀ distribution — is self-calibrating: whatever the true
   noise, the percentile is estimated from replicates. The design flaw
   is not (ii); it is that (i) and (ii) can now CONTRADICT each other
   (pure noise above delta\*), making the four-part conjunction
   unsatisfiable. Note also: a 95th percentile estimated from 20 pairs
   is effectively the sample maximum — its sampling CI is ±~30-40%.
   Given the small empirical CV of TV (~2%), estimate the threshold
   parametrically from the 20 replicates (mean + 1.645·sd) or run
   ≥100 pairs (still cheap at 1e5); and apply the √10 rescaling PER
   POPULATION — the pooled marginal scales with games×40, the per-ec
   strata with games, and the primary stratified comparison is the
   one whose threshold is being set.

### 2.5 The fix (gate design, not math, and not a retreat)

The correct calibration is cheap and already half-specified:

  E[TV₀] ≈ S½ / √(πN),  S½ = Σ_cells √(p̂(1−p̂)) — measurable from the
  corpus itself, per (sub-variable × stratum).

- Compute S½ per comparison unit BEFORE the gate (one pass over the
  frequency tables; no extra corpus).
- Make the ABSOLUTE cap table-aware: either delta*_unit =
  max(2e-3, q95(D₀_unit)) with 2e-3 remaining the certification TARGET
  at the scale where it is resolvable, or apply the absolute 2e-3 cap
  only at the scale where the unit's noise floor is below it (for
  broad tables that is 1e7 pooled, not 1e6, and not the per-ec strata
  at any planned scale).
- Re-state the certification honestly: at 1e6, for broad-support
  tables, the gate certifies equivalence at the ~3e-3 level (the noise
  floor), not 1.5e-4; the 1.5e-4 figure in §7 is the flawed formula's
  artifact. Whether ~3e-3 suffices is the downstream-propagation
  question, and §5's propagation arithmetic (see §4 below for its own
  factor-2) says it does — but that must be decided on corrected
  numbers, not on the current text's 20× phantom margin.

**This amendment is REQUIRED before the T6 gate runs.** A gate that can
spuriously fail a perfect G₀ replica is worse than no gate: its first
failure will be attributed to G₁ (the §7 attribution protocol
distinguishes counter-coupling from distinctness, but NOT "the threshold
was below the noise floor from the start"), and the fallback machinery
would be engaged against a defect that does not exist.

---

## 3. REQUIRED AMENDMENT B — the §6.4 phase bound's "PROVEN" tag is invalid: an explicit counterexample

§6.4 states, under "PROVEN (the phase combinatorics)":

> the phases (g + m_g) mod k over the N slots are balanced up to a
> discrepancy of at most max_g m_g − min_g m_g (the spread of the
> move-ply indices ...), which is ≤ 64 — hence the phase imbalance is
> ≤ 64 slots out of N: 6.4e-5 of the corpus mass at N = 1e6.

**The derivation is false as stated.** The spread of m_g does not bound
the multiset discrepancy of the phases. Counterexample: choose

  m_g = (r − g) mod k  (any fixed target residue r),

which has spread ≤ k−1 ≤ 63 ≤ 64. Then EVERY slot's phase is
(g + m_g) mod k = r — the phase multiset is a POINT MASS, imbalance
N·(1 − 1/k) slots, not ≤ 64. (Verified numerically for k=2 and k=7:
one distinct phase across 1e6 slots, m-spread 1 and 6 respectively.)
More prosaically, k=2 with m_g = g mod 2 (spread 1) collapses every
phase to a single residue. A bound of the claimed form cannot hold
without structural assumptions on m_g beyond its spread — and the
cross-section at which "the" decision is taken is itself underspecified
(slots are at different plies/widths at a given wall-clock index; the
claim needs a per-(ply-index or width) definition before it is even a
statement).

**Why this matters beyond a technicality — the term is misclassified.**
The document labels this term "purely COMBINATORIAL: it concerns the
slot phases, not the table", separating it from the gated path-coupling
residual (E3a vs E3b). But m_g is the pass-adjusted move count, and the
pass pattern of game g is a function of its trajectory — which is a
function of the table AND of the slot's own phase g mod k. The feedback
loop (phase → first picks → trajectory → passes → m_g → phase) is
precisely the table-dependence shape that forced the E1-corpus
reclassification in v2. The phase term is not a priori separable from
the path coupling; claiming it PROVEN and negligible at 6.4e-5 reopens,
in miniature, the exact hole v2 closed.

**The fix (cheap, and the gate can carry it):**

- Demote the §6.4 phase claim from PROVEN to GATED (or re-prove a
  correct bound under an explicit, justified independence assumption on
  m_g — none is currently available). The §6.6 summary table's second
  row ("phase combinatorics ... PROVEN") must change accordingly, and
  E3a's "provably O(k/N)" loses its provability.
- Add a direct empirical scan to the gate — it is nearly free: per
  width k, the cross-slot histogram of realized phases (g + m_g) mod k
  vs uniform, over the gate corpus (a chi-square with k−1 df per
  width, Bonferroni over 64 widths). Test 1 is the natural host. This
  converts the broken proof into a measured quantity, which is the
  document's own established policy for exactly this situation.

Note: the practical risk is probably small — at the first decision
m_g = 0 across slots (phases = g mod k: EXACTLY balanced), and later
m_g variation is pass-driven and quasi-random — but "probably small"
is what the gate is for. The first review's test 6 (phase-continuity
scan) partially covers this; the direct per-width phase-occupancy scan
is sharper and should be named.

---

## 4. Minor findings

1. **The downstream propagation bound is understated ~2× (cosmetic).**
   §5 bounds the information-quantity perturbation at "≤ ~2e-2 (the
   TV·(1 + log C) bound)". The correct bound is
   |ΔH| ≤ h₂(TV) + TV·log₂(C−1): at TV = 2e-3, C = 1296,
   h₂(2e-3) ≈ 0.0208 bits plus 2e-3·10.33 ≈ 0.0207, total ≈ 0.041 —
   about 1.8× the quoted ~2e-2. Still negligible against the 1e-1-scale
   effect sizes, but the v3.1 posture is "computed, not asserted"; this
   one should be recomputed too (and the same correction applies to MI).
2. **§4.4 typo:** the C = 16,384 @ N = 1e4 cell reads "4.7e-3·10⁻¹";
   the value is 4.7e-4 (I verified the rest of the 6·√(p(1−p)/N) table
   by hand — all rows correct — but that one is garbled).
3. **The 6σ framing is per-cell;** across a C-cell table the MAX-cell
   deviation exceeds the single-cell 6σ (multiple-comparisons inflation
   of the extreme). §4.4's table is fine as a per-cell error statement;
   one clause noting it is not the max-cell error would prevent a
   misreading later.
4. **The pass double-count in per-ec strata (implementation care, not
   a flaw):** a game with a pass contributes two positions at the same
   ec (the board is identical, the mover side swapped). Whether the
   sub-variable codes distinguish the sides determines whether these
   are duplicates or distinct samples. The §1.5 note covers the mixture
   weights; the gate implementation must pin the per-stratum counting
   rule (dedup or not) identically for G₀ and G₁.

---

## 5. On the thesis, answered directly

**Is G₁ a solid way to extract the frequency characteristics of the
selected patterns?** Yes — as a construction. The local semantics are
provably identical to G₀'s (oracle Theorem 1: re-verified), the lemmas
hold, the cost argument is real and verified against the code, and the
engineering rationale (2016 setup draws vs ~5e8 hot-loop calls, no
duplicated MT inside numba) stands on its own. The corpus-level
equivalence is honestly gated rather than falsely proven — the v2/v3
scope discipline is the document's best feature, and my review confirms
it rather than captures it.

**Does this analysis give the same results as a G₀-generated
population?** As of v3.1: **it is a pre-registered empirical claim with
a bound that is currently miscalibrated.** I concur with Kimi K3's
framing (theorem vs certified bound) and add: the v3.1 numbers that were
supposed to turn the gate into "a real BOUND" (§5: "not a ritual") are
themselves the artifact of an unverified quantitative claim — the D₀
formula — promoted into the gate's pass rule between the second review
and the build. The irony is exact: the review process that caught v1's
unproven PROVEN tags let an unverified number through the same door,
because both prior reviews were scoped to the v2/v3 substance and the
v3.1 hardening landed after them.

**What is actually certified, once amended:** with the corrected noise
floor, the 1e6 gate certifies, for broad-support tables, equivalence at
the ~3e-3 TV level (pooled) — and the per-ec stratified comparison at
1e6 can certify only ~2e-2 for uniform-like strata, with 2e-3-level
certification deferred to the 1e7 build gate where the pooled noise is
~1e-3. Whether that schedule of tolerances serves I-017 must be decided
on those corrected numbers (the propagation arithmetic, even corrected,
says yes: ~4e-2 in H/MI against 1e-1 effect sizes). The claim "the gate
demands G₁-vs-G₀ be no worse than two random G₀ corpora are to each
other" remains true and remains the right demand; what changes is the
scale at which that demand can actually be resolved.

---

## 6. Verdict and required actions

**PASS WITH REQUIRED AMENDMENTS.** The design is sound and I endorse
building on G₁ — but NOT on the v3.1 gate numbers. Concretely:

- **REQUIRED A (blocking):** replace the D₀ formula with
  E[TV₀] ≈ S½/√(πN), S½ = Σ√(p̂(1−p̂)); recompute every derived number
  in §5 and §7 (the 1e-4/3e-5 noise figures, the 20×/70× margins, the
  1.5e-4 95th percentile, the 5-60σ band sentence); make the absolute
  cap table-aware (or re-scope it to the scale where each unit's noise
  floor is below delta\*); fix the bootstrap percentile estimation
  (parametric or ≥100 pairs; per-population √N rescaling). Until this
  is done the gate can spuriously fail a perfect G₀ replica, and its
  first failure would be mis-attributed to the generator.
- **REQUIRED B (blocking, cheap):** demote the §6.4/§6.6 phase claim
  from PROVEN to GATED (the spread bound is falsified by the
  counterexample above; the m_g feedback loop makes the term a path-
  coupling channel, not a purely combinatorial one), and add the
  per-width phase-occupancy scan to the gate (test 1 or 6).
- **Minor (non-blocking but should be done in the same edit):** the
  propagation bound (§4.1 here), the §4.4 typo, the per-cell vs
  max-cell clause, the per-stratum pass-counting pin.

With A and B executed, I concur with the two prior reviews' verdict on
the construction and the gate architecture, and I see no remaining
unreviewed load-bearing layer. The T6 gate should then run — amended —
BEFORE the T5 build, exactly as the (corrected) document specifies.

---

## Appendix — the numerical verification (what I ran, what it showed)

Environment: the project venv (`/home/rcrr/base/prj/dsh/.venv/bin/python`,
numpy), `PYTHONDONTWRITEBYTECODE=1`, no files written. Every experiment
is reproducible from this text in seconds.

**Experiment 1 — the D₀ noise.** For each row: p fixed, two independent
`rng.multinomial(N, p)` corpora, TV = ½Σ|f₁−f₂|, 20 replicate pairs.
Correct closed form E[TV₀] ≈ S½/√(πN) matched simulation to <1% in all
rows; the v3.1 formula 0.4·√(2S/N) understated by S½/√S ∈ {36 (uniform
C=1296), 21 (power-law α=1.2 head), 6 (geometric 0.9)} — the full table
is §2.2 above. Key rows: uniform C=1296, N=4e7 (the "1e6 games" pooled
marginal): sim 3.20e-3 vs doc 8.94e-5; N=1e6 (the per-ec stratum, the
primary test-2a unit): sim 2.02e-2 vs doc 5.66e-4.

**Experiment 2 — the "verified numerically" figures.** 0.4·√(2/4e6) =
2.828e-4 and 0.4·√(2/4e7) = 8.944e-5 — the §7 test-2 quoted values, to
the digit, with S = 1; the "4.9e-5 concentrated" value back-solves to
S = 0.300 in the same formula. Conclusion: the quoted verification is
the formula's self-evaluation, not a two-corpus measurement.

**Experiment 3 — the phase counterexample.** N = 1e6 slots: k=2,
m_g = g mod 2 (spread 1): all phases ≡ 0 — imbalance 5e5 slots vs the
claimed ≤ 64. k=7, m_g = (0−g) mod 7 (spread 6): one distinct phase
across all slots. The §6.4 spread bound is falsified; no bound of that
form is available without structural assumptions on m_g.

**Code locations checked** (read in full, against the v3.1 text):
`hlp_random_play.py` — `ec_of` (L129-140), `initial_position` (L143-157),
`build_pick_table` (L160-184, correct Fisher–Yates, 2016 draws, read-only
table), `pick_move` (L187-208, the oracle semantics, the pass contract),
`random_play`/`_play_from` (L221-307, the arrest rule, the MAX_PLIES
guard). `notes/peer_review_random_permutation_table.md` and `notes/
peer_review_kimi_random_permutation_table.md` — read after my own
derivations; no finding in this review derives from either, and §2-§3
above are absent from both (they reviewed v2/v3; the erroneous layer is
v3.1).
