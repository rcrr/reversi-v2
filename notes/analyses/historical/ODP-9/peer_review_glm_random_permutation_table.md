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

---

# Round 2 — the v4 + §11 audit (2026-09-13): a design failure, not a bug

> **Question put to me** (Roberto, verbatim in substance): the SW was
> built, the T6 tests ran, they FAIL. G₁ is declared not an alternative
> to G₀; the 1e7 corpus will be generated with G₀. Review the ENTIRE
> document again — independently, taking NOTHING for granted, deriving
> everything needed to check every step and every claim — and answer
> the question that matters: **is the FAIL a property of the DESIGN
> (G₁ was an abbaglio — an illusion), or is it an implementation BUG
> that would throw the baby out with the bathwater?**
> **Method.** I audited the gate code (`src/reversi/lm/hlp_gate.py`)
> and the wave engine (`src/reversi/lm/hlp_wave.py`) line by line;
> verified every §11.1 number against the primary artifacts
> (`scratch/gate_1e6/`, `gate_1e5_s42/`, `gate_1e5_s123/` — the raw
> JSON reports and the run log, which I found still on disk);
> re-derived the calibration; and then did what no artifact can
> substitute for: **an independent replication through a third code
> path** — the T4 scalar reference (`random_play`, the design's own
> single-game implementation) for G₁, against MY OWN hand-written
> scalar G₀ loop over `tools/prng.py` — plus a 2e4-scale re-run of
> the gate machinery with raw-corpus forensics (validity checks, the
> color-swap hypothesis, the locus-size measurement, the per-ec D₀
> of the sparse units, the joint-cell concentration). Scripts and
> outputs live in `scratch/glmrv_stage*.py` (the disposable area;
> nothing outside this file and scratch/ was touched).
> **Verdict: the FAIL is REAL, SYSTEMATIC, and belongs to the DESIGN.
> No implementation bug is anywhere in the chain, and I looked hard
> for one. G₁'s corpus-level equivalence (E1-corpus) is REFUTED at
> every scale I measured (1e4, 2e4, 1e5, 1e6 — the deviation is
> scale-INVARIANT, seed-independent, phase-locked, concentrated early
> by a mechanism I can now derive AND measure). D-174 (G₀ is the
> corpus generator) is CORRECT and I endorse it without reservation.
> The record (§11) needs seven corrections before it is treated as
> final — none of them rescues G₁; one of them (the missing §7
> fallback disposition) I supply myself, and it CONFIRMS the kill.**

## R2.1 The infrastructure audit — everything the verdict rests on (ALL VERIFIED)

The verdict would be worthless if the gate itself were broken. I
audited and re-verified every load-bearing piece:

1. **The numba MT19937 kernels** (`_mt19937_init`/`_mt19937_batch`,
   the gate's G₀ stream): bit-exact vs the golden-pinned
   `tools/prng.py` port — 624 consecutive draws at seeds 42, 123,
   5489: **identical to the last bit, all three seeds.**
2. **The wave G₁ engine vs the T4 design reference**: I drove
   `step_wave` myself for 40 steps and compared every lane against
   `random_play(42, 20, counter0=g)`: **12/12 lanes bit-exact — the
   full move sequence AND the pass counts.** An indexing/counter bug
   in the wave's G₁ path would break this replay; it does not. The
   docstring's cross-validation claim is true.
3. **The G₀ semantics** (the frozen §2): one iid draw per (lane,
   step) in lane order, consumed-unused for pass/dead lanes — a valid
   realization of "one fresh draw per ply, independent of everything"
   (discarded draws cannot bias the law); the `% k` reduction's bias
   < k/2⁶⁴, negligible as documented.
4. **The pass-folding equivalence**: the wave folds a pass into the
   step (the opponent moves with the CURRENT counter — no counter
   step for the pass) — exactly T4's semantics; the mover-side
   convention after folded steps matches T4's ply accounting (I
   checked both branches).
5. **The observed positions are VALID Reversi positions**: at the
   arrest (ec 20): exactly 44 stones per position (min=max=44, both
   engines), zero both-color squares, the mover has legal moves
   (game-over-before-arrest lanes are dead and unharvested, as
   designed); the arrest lands EXACTLY (ec −1 per real move — flips
   recolor, they do not add stones).
6. **The color-swap hypothesis — tested and excluded**: if the two
   engines disagreed on the mover/opponent convention, recoding G₀
   with sides swapped would collapse the TV. It does not: LMC
   TV(G₁, swap(G₀)) = 0.109 vs TV(G₁, G₀) = 0.017 — the swap makes
   it WORSE, as it must if the corpora are correctly aligned.
7. **The D₀ calibration is coherent with the v4 formula**: LMC
   (65 cells, concentrated) pooled q95 = 5.2e-4 at 1e6 (in the v4
   "concentrated tables 5e-4..2e-3" band), per-ec 3.7e-3; my 2e4
   re-runs reproduce the √N scaling of every dense unit.

**Conclusion R2.1: the instrument is sound. The failure it measured
is in the object, not the instrument.**

## R2.2 The §11.1 evidence vs the primary artifacts — every number verified

I found the gate's raw outputs still in `scratch/` (the 1e6 run log,
the 1e6 report/JSON, both 1e5 confirmation JSONs, and
`extract_gate.py` — the tool that produced §11.1's table). Every
quoted number checks:

| §11.1 claim | artifact | verdict |
|---|---|---|
| LMC per-ec max D = 0.174, q95 0.0037, 47× | 1e6 report D=1.743e-01; q95 = 0.01150 (1e5 s42) × √0.1 | ✓ exact |
| LMC pooled D = 0.019, q95 0.0005, 37× | 1e6: D=1.905e-2, q95=5.203e-4 → 36.6× | ✓ |
| Passes D = 0.002, q95 0.0001, 15× | 1e6: D=2.021e-3, q95=1.331e-4 → 15.2× | ✓ |
| Phase scan p ≈ 0, BROAD | 1e6: worst p = 0.0, 25 widths; 1e5 s123: p=0 at widths 3,4,5,6,7,8,9,10,12,14,15,16,18 | ✓ (the doc's list omits 14) |
| Joints 136/153 @1e6, 0/153 @1e5 | 1e6: bonferroni_significant=136; both 1e5: 0 | ✓ as counts — see R2.5 for what they MEAN |
| Phase continuity 0.143 (1e6) / 0.306 (1e5 both seeds) | 0.14306; 0.30585 / 0.30645 | ✓ |
| seed 42: 0.174 (15×); seed 123: 0.206 (19×) | s42: 0.17427/0.01150=15.2; s123: 0.20585/0.01081=19.0 | ✓ |
| ec 56: 0.206; 57: 0.164; 55: 0.127; 53: 0.094 | s123 per-ec top-4 EXACTLY | ✓ |
| FAIL on (i),(ii),(iii) | run log: (i)=F (ii)=F (iii)=F | ✓ |
| 19.6 vs 20.5 min | timing_s: g0=1177.4, g1=1231.0 | ✓ |
| "18 SU pairs × 9 strata" | the joint list has **17** pairs × 9 = 153 | ✗ (17, not 18) |

The §11.1 text is an honest extract of the artifacts. Its SELECTION
(the dense units) was the right choice — but it never says why the
raw report's most dramatic numbers (D = 1.0 on CORNER/XEDGE/R2/…)
were NOT selected. That gap matters: R2.5.

## R2.3 The independent replication — the third code path (the anti-bug proof)

If the wave, the gate's G₀ engine, or the observation harness had a
bug, the gate's signature would be an artifact of THAT code. So I
reproduced the comparison with **no gate code in the path**: G₁ from
`random_play` (the T4 scalar reference, the design's own
implementation — proven bit-exact against the wave in R2.1.2), G₀
from **my own** scalar loop (board.py + `prng.py` MT19937, one draw
per real move, the frozen §2 semantics verbatim, written from
scratch by me this session). 1e4 games each, three independent G₀
seeds for the D₀ noise.

**The signature reproduces exactly** (LMC per-ec TV, T4-G₁ vs
my-G₀): ec 57: **0.167**, ec 55: **0.169**, ec 56: 0.133, ec 54:
0.129, ec 50: 0.109 … decaying to ~0.02 at the arrest — the same
shape, the same magnitudes (0.17 early), the same early
concentration as the 1e6 gate (0.174) and the 1e5 runs (0.174,
0.206). The D₀ at 1e4 (two G₀ pairs): per-ec max 0.028-0.034 — so
**the early-ec deviation is already ~5-6× the noise at 1e4**, and
the D does NOT shrink with N (0.17 at 1e4, 2e4, 1e5, 1e6) while the
noise falls 1/√N — the fingerprint of a SYSTEMATIC, i.e. a design
property. The pass-distribution TV = 0.0038 at 1e4 (~3× the
expected D₀) — same direction as the gate's 15× at 1e6.

The 2e4-scale re-run of the gate machinery (with raw-corpus
forensics) agrees everywhere: LMC per-ec max 0.181, pooled 0.0186
(6.5× the 2e4 D₀), the phase-occupancy scan non-uniform at k=2..22
(e.g. k=3: χ²=281 on 2 df; k=4: 350 on 3 df — the same widths the
1e5/1e6 runs flag), the offset-run phase-locking reproduced
(pooled TV between G₁(base 0) and G₁(base 4000001): CORNER 0.47,
R2 0.48 at 2e4), and **the arrested corpus is NOT collapsed**
(19970 distinct positions of 20000 — vs G₀'s 20000/20000): the
failure is a WEIGHT bias over a rich support, not a degenerate
support.

**Three code paths — the gate's wave pair, the wave-vs-T4 replay,
and T4-vs-my-own-G₀ — all measure the same systematic. There is no
room for an implementation bug to hide. The FAIL is the design's.**

## R2.4 The mechanism, derived and measured — the class-collision cloning (and what §11.3 gets wrong)

The counter walk makes slot g's trajectory a deterministic function
of g. The trajectory CLASS at ply t is g mod L_t, L_t = lcm of the
widths encountered so far; within a class, the ply-t phase
(g + t) mod k_t takes only k_t/gcd(L_t, k_t) distinct values — the
class branches into **that many** children, not k_t. When k_t | L_t
the class makes ONE move en bloc: **collision cloning**. The early
plies are where L_t is small and the cloning is total. I measured
the prefix diversity directly (2000 games per engine):

| prefix depth | G₁ distinct | G₀ distinct |
|---|---|---|
| 2 moves | 12 | 12 |
| 3 moves | 44 | 56 |
| 4 moves | 60 | **244** |
| 5 moves | 156 | **1023** |

At ply 2 there is NO degeneracy at all: the widths (4, 3) are
coprime, the slot map g ↦ (g mod 4, (g+1) mod 3) is a bijection
onto all 12 rank pairs, and the G₁ (m1, m2) marginal is EXACTLY
balanced — 12 pairs at 1/12 each, better than G₀'s multinomial (the
balanced-design property working as intended; my initial
"4-of-16 degeneracy" hypothesis was WRONG, and I retract it). The
collapse starts at ply 3 (44 vs 56) and is drastic at ply 4-5
(60 vs 244, 156 vs 1023): the G₁ trajectory tree is a throttled,
deterministic, integer-weighted subtree of G₀'s full branching
process — the corpus's early-game position distribution is a small
structured set with exact weights, and the LMC marginal inherits
the bias (ec 57 = after 3 moves: TV 0.167-0.206 across scales).
As L_t grows the gcd → 1, full branching resumes, the tree
diversifies and the bias decays — but the weight structure is
already baked into the corpus (the residual ~0.012-0.019 at the
arrest ec, ≈ 6-14× the 1e6-scale single-level noise, and 6-10×
ABOVE delta* = 2e-3 — **even the ARRESTED-POSITION population alone,
the DB-adherence reference, fails the v4 criterion**), the
phase-occupancy histogram stays non-uniform (the selection
feedback: which slots sit at width k at step t is itself
phase-correlated), and the corpus revisits code cells G₀ never
repeats (R2.5.3). This is precisely the §6.4 demoted channel —
phase → pick → trajectory → width → phase — which my Round-1
Amendment B flagged and the gate now measures at p ≈ 0.

**This is why §11.3's attribution is wrong.** §11.3 opens with
"the gate's measured signature is the corpus-level shadow of the
shared-row distinctness (§6.4, the allows-equality law)" — but
§11.1's own evidence says the opposite (BROAD mode, no small-k
spike), and my measurements agree: the same-width pair law
(TV = 1/k, §6.5) is second-order here; the ply-2 pair marginal is
PERFECT, so the distinctness channel is not even open at the depth
where the bias is largest. What §11.3's middle sentences then
actually describe — "phase → pick → trajectory → phase feedback +
shared-row cloning" — IS the class-collision cloning, mislabeled.
Three more precision defects in the same paragraph: (a) "averaged
over an independent phase distribution the pick is uniform"
begs the question — the phase distribution is trajectory-dependent,
that dependence IS the failure; E1 survives only as the oracle
statement. (b) The MT19937 equidistribution narrative is color, not
cause: A1 held (the rank histograms pass), the table is fine —
what dies is the INDEPENDENCE of successive picks, which the
paragraph does say, but the "destroyed BY DESIGN" framing should
be attached to the deterministic counter walk, not to the loss of
MT's serial properties. (c) "twin slots play identical
continuations" — the cloning condition is a phase COLLISION mod k
within a trajectory class, not shared-row-ness per se.

## R2.5 What the raw report's dramatic numbers actually mean (the record's most misleading feature)

The gate report contains far more alarming numbers than §11.1
quotes — and they are the ones a future reader will trip over:

1. **The per-ec pattern "marginals" (CORNER, XEDGE, R2, R3, R4,
   2X5COR, DIAG5-7) show D = 1.000 — "disjoint supports" — and the
   joints show D = 1.000 with KL = 50 (the cap). These numbers are
   VACUOUS.** The gate's per-feature key is the FULL INSTANCE
   TUPLE (e.g. CORNER = 19683⁴ ≈ 1.5e17 cells); at the gate's
   scales the tables are singleton-dominated and I measured their
   own D₀: **G₀-vs-G₀' per-ec CORNER TVs are ALSO 1.0 — saturated
   even between two G₀ corpora** (at 2e4: all three pairs exactly
   1.0 at every level ≤ ec 36; the 1e5 pair runs' raw values were
   1.0 — the rescaled thresholds 0.3162 are 1.0×√0.1, a meaningless
   rescale). DIAG8 is the demonstrative case: at the 1e5 scale G₁'s
   D = 0.604 against its own-scale D₀ ≈ 0.90 — **G₁ is CLOSER to
   G₀ than two G₀ corpora are to each other** on that unit; the
   gate's "2.1×" is an artifact of the √10 rescale applied to a
   saturated statistic. A G₀ twin would have "failed" these units
   identically. **A saturated unit must be reported as
   UNINFORMATIVE, not as a 3.2× failure.**
2. **Why the rescale fails there — and this is MY correction.**
   The v4 D₀ design (my Round-1 Amendment A: 20 pairs at 1e5 +
   the per-population 1/√N rescale) is valid in the unsaturated
   regime and I verified it holds there (the dense units: LMC,
   passes — every rescaled q95 coherent with the direct
   measurement at the new scale). But TV saturates at 1: the √N
   law is a small-TV expansion, and rescaling a saturated value is
   arithmetic without meaning. I did not flag this in Round 1;
   the gate inherited it. One guard line fixes it forever:
   **q95(D₀_unit) ≥ 0.9 ⇒ the unit is declared uninformative at
   that scale** (and the pooled sparse units — CORNER 0.20 at 1e6,
   rescaled from 0.64 — deserve the same caveat: rescaling from a
   0.64 baseline already strains the expansion; 2-3 direct 1e6
   G₀ pairs, ~40 min of compute, would have closed it properly).
3. **The joint chi-square flip (0/153 at 1e5 → 136/153 at 1e6) is
   nevertheless a REAL signal** — I verified what it detects: at
   2e4, G₁'s LMC×R2-tuple cells include 9 REPEATED cells
   (multiplicities 8, 8, 6, 4, 3, 3, 3, 2, 2) while **G₀ has
   ZERO repeats in 2×20000** — the phase-locked corpus revisits
   code combinations random play essentially never repeats. The
   flip is the power growth of the occupancy test on that
   concentration. But: it is an UNCONTROLLED test (no G₀-pair
   chi-square baseline was run at 1e6), and §11.1's "grows with
   scale" is the test's power, not the bias's growth. The bias's
   growth is in the DENSE units, where D stays and the noise falls.
4. **The joints were not the pre-registered unit.** §7 test 3 /
   §4.4 account cells PER INSTANCE ("the per-instance cell product
   ≤ 1e6" is the pair filter — LMC×R2 per instance = 4.3e5 cells ✓
   passes the filter); the implementation concatenated ALL
   instances (LMC×R2 = 65×6561⁴ ≈ 1.2e17 cells — 11 orders
   sparser). The "PRIMARY joint instrument" of the v3 reordering
   never actually ran at its designed granularity; at the designed
   one (2-3 samples per cell at 1e6) it would have been
   informative. This is a gate-implementation defect — moot for
   the verdict, but the record should not cite the vacuous units
   as evidence (§11.1's Joints row cites the chi-square counts
   of a unit that was never the designed one).
5. **The 1e6 run also thresholded 12 per-ec units against a
   DEFAULTED noise floor** (the older gate version's
   `d0.get(name, [0.0])` → 2e-3): the per-ec pattern units that
   run reported at D=1.0 were never bootstrapped at 1e6 at all.
   The newer version (the 1e5 confirmations) bootstraps them and
   produces the rescale artifact of point 1 instead. Either way
   those units never carried calibrated evidence.

**The evidential hierarchy that actually carries the FAIL** (all
verified by me against the artifacts AND reproduced
independently): the LMC per-ec marginal (dense, calibrated:
47×/19×/15× at 1e6/1e5-seeds, ~5-6× already at 1e4 — the scale-
invariant systematic), the LMC pooled (37×), the pass distribution
(15×), the phase-occupancy scan (p≈0, broad, reproduced at 2e4),
the test-6 phase-locking (0.143/0.306; 0.47 at 2e4), the arrest-ec
deviation vs delta*, and the cell-revisit concentration. Remove
every sparse unit from the report and the verdict is unchanged:
that is what "over-determined" means.

## R2.6 The missing §7 fallback disposition — supplied, and it confirms the kill

§7's FAIL protocol pre-specifies TWO remedies and assigns them to
modes: the **fallback** (a second independent counter, c'_g = g+Δ)
for the counter-mediated coupling, and the **escape hatch** (fresh
per-ply PRNG at small-k plies) for the shared-row distinctness.
The measured mode is the counter-mediated/path-coupled one — yet
§11.1 mislabels the escape hatch as "the §7 fallback", dismisses
it as targeting the other mode, and **never disposes of the actual
§7 fallback for the measured mode** (§5-E3b and §6.5 name it too).
Skipping it may well be right — but the record must ARGUE it, not
skip it. Here is the argument, and it closes the door:

With c'_g = g+Δ, the trajectory remains a deterministic
1-parameter family of the slot id. The ply-2 lattice map becomes
g ↦ (g mod k₁, (g+Δ+1) mod k₂) — a coset bijection when the widths
are coprime (still perfectly balanced: nothing changes at ply 2).
The class structure (g mod L_t) and the class-collision condition
— slots of one class share the phase (g'+t) mod k_t whenever
k_t | L_t — persist for EVERY offset Δ, because both counters are
affine in g. The prefix-diversity collapse (44/56, 60/244,
156/1023) and the phase-occupancy feedback would reappear with the
same magnitudes, merely permuted. **The second counter removes the
two-stream rank coupling, not the one-dimensionality of the walk —
it could NOT have rescued the corpus-level equivalence.** And the
escape hatch (fresh PRNG at k ≤ 4) fails on the evidence too: the
non-uniform widths run 3-18 and the deviation peaks at ec 55-57
where the widths are 5-10 — outside its patch. Both shelf remedies
are dead; the only G₀-equivalent generator in sight is G₀. The
kill decision is not premature: it is forced.

## R2.7 The corrections the record needs (none rescues G₁)

- **A (required).** Mark the sparse per-ec pattern units and the
  joint D/KL values as SPARSITY-SATURATED / UNINFORMATIVE in the
  record (R2.5.1-2), with the saturation guard for any future gate
  run. Say plainly that the verdict never rested on them.
- **B (required).** Record the joint-unit implementation defect
  (instance-tuple vs the pre-registered per-instance accounting —
  R2.5.4) and re-frame §11.1's Joints row as the occupancy/
  concentration signal it actually is (R2.5.3), ideally with the
  1e6 G₀-pair chi-square control if the number is ever cited.
- **C (required).** Insert the §7-fallback disposition (R2.6):
  the second counter is analytically dead for the measured mode;
  the escape hatch is out-scoped by the evidence.
- **D (required).** Fix §11.3's mechanism attribution (R2.4):
  the corpus-level shadow is of the **class-collision cloning**
  (the demoted §6.4 phase channel), not of the shared-row
  distinctness; the ply-2 marginal is exactly balanced, which the
  record can now state with the 12/12 measurement; E1 survives as
  the oracle statement only.
- **E (required, wording).** §11.2: "the lemmas and the phase
  combinatorics stand" — only Lemma 2's WITHIN-GAME residue cover
  stands; the cross-slot phase balance was falsified (Round-1
  Amendment B) and the gate measured it failing. "Empirically
  bounded by this gate" should read REFUTED at the 1e6-resolved
  level. The frozen body's stale spots (§5's one-honest-sentence
  still lists "the phase combinatorics (E3a, ≤ 6.4e-5)" as PROVEN;
  §5-E3b and §6.5 still say the gate runs at 1e4; §6.6 row 3
  "the phase component proven" contradicts row 2 of the same
  table; §7's intro "the proof covers … the phase combinatorics")
  cannot be edited — the freeze — but §11 should carry a short
  errata note so no future reader takes them at face value.
- **F (minor).** 17 SU pairs, not 18; the phase-fail width list
  omits 14; the perf-parity claim rests on a warmup-tainted 144k
  single-wave G₀ figure plus the ec=0 steady state (189.6k/s) —
  one clean steady-state ec=20 G₀ benchmark would close it (the
  decision does not hinge on it); §11.4's "SU OPTIONAL default
  FALSE … profiling AFTER the SU level is complete" is clear only
  with the D-175 context (the level is not in the config schema
  yet — T12 work) — one clause would fix it.
- **G (my own corrections, for the record).** My Round-1 judgment
  that the phase term's "practical risk is probably small" was
  WRONG in magnitude (the counterexample was right; the magnitude
  guess was not — the gate measured p ≈ 0, and this round derives
  why). My Amendment A's √N rescale inherited a blind spot in the
  saturated regime (R2.5.2). My Round-2 starting hypothesis of a
  ply-2 rank-pair degeneracy was falsified by my own measurement
  (the 4-3 coprime lattice is perfectly balanced) — the true
  mechanism is the ply-3+ class collapse. And my first attempt at
  the scalar replication burned an hour in an infinite loop on
  double-pass games — the reviewer's own bathwater, thrown out
  with due ceremony. The lesson the document already teaches:
  verify, do not assume — the assumption was mine this time.

## R2.8 The final verdict

**To Roberto's question: G₁ was an abbaglio of the DESIGN, not a
bug.** The chain is closed at every link: the wave engines are
bit-exact against their references (R2.1); every quoted number is
honest (R2.2); the signature reproduces through a third,
fully-independent code path at one-tenth the scale (R2.3); the
mechanism is derived and measured, and it is the exact channel the
review process demoted to gated (R2.4); the failure is systematic
(D scale-invariant from 1e4 to 1e6), seed-independent, phase-locked,
present in a quantity I-017 consumes directly, and above the
absolute tolerance even in the arrested-position population the
adherence statistic consumes; and the pre-specified remedies are
analytically dead (R2.6). **I endorse D-174 without reservation:
G₀ — the reference semantics, the generator that needs no
equivalence argument — is the corpus generator.** The G₁
analytical record stands as the document now frames it: Lemma 1,
Lemma 2, and the oracle Theorem 1 are intact and valuable (the
wave-vs-T4 replay and the ply-1/ply-2 exact balance are the design
working AS DESIGNED — the balanced property is real, and it is
precisely not enough); E1-corpus, E3a and E3b are refuted/gated.

The process note, for the campaign's memory: three reviews caught
the unproven tags and the miscalibrated numbers BEFORE the build;
the pre-registered gate then caught the one thing no review could —
the empirical claim itself. Nothing was thrown out with the
bathwater: the baby (the proof architecture, the T4/T5 wave
machinery, the MT kernels, the gate harness — all verified
bit-exact this round) is alive and now carries the G₀ corpus. What
died is a design idea, and it died of evidence.

---

## Appendix R2 — the verification log (what I ran, 2026-09-13)

All scripts in `scratch/` (the disposable area); nothing outside
`scratch/` and this file was written. The venv interpreter,
`PYTHONDONTWRITEBYTECODE=1`, no other workspace file modified.

- `glmrv_stage1.py` — MT19937 numba kernels vs `prng.py`: 624
  draws × 3 seeds bit-exact. Wave-G₁ vs T4 `random_play`: 12/12
  lanes bit-exact (moves + pass counts). T4 speed 4.55 ms/game.
- `glmrv_stage2.py` / `stage2b.py` — the 2e4 gate-machinery re-run:
  per-ec TV profiles (LMC early peak 0.181; CORNER/XEDGE/R2/DIAG8
  full profiles), raw-corpus validity (44 stones, no color overlap,
  19970/20000 distinct arrested positions), the color-swap test
  (excluded), the phase-occupancy scan (χ² 281 on k=3 … 104 on
  k=18), the offset-run phase-locking (CORNER 0.47, R2 0.48,
  DIAG8 0.147), the per-ec D₀ of the sparse units (CORNER
  saturated 1.0 even G₀-vs-G₀'; DIAG8 0.82 ≈ G₁'s 0.82), the
  corrected pooled table (LMC 6.5×, CORNER 1.1× at 2e4), corpora
  saved to `glmrv_stage2_corpora.npz`.
- `glmrv_stage3.py` — THE INDEPENDENT REPLICATION: 1e4 G₁ games via
  T4 `random_play` vs 3×1e4 G₀ games via my own scalar loop on
  `prng.py`: the per-ec LMC profile (ec 57: 0.167, ec 55: 0.169 …
  decaying to 0.019), the D₀ at 1e4 (per-ec max 0.028-0.034), the
  arrest-ec TV 0.0188, the pass TV 0.0038, the first-two-moves
  locus (12/12 both engines; G₁ exactly 2500±5 per first move).
  (The first version ran for an hour in an infinite loop — my
  missing double-pass game-over check — fixed, rerun, 3 minutes:
  the scalar path is for single calls and 5-step loops, as the
  document says, and I re-learned why.)
- `glmrv_stage4b.py` — the joint-cell concentration: G₁ 9 repeated
  LMC×R2-tuple cells (max multiplicity 8) vs G₀ ZERO repeats in
  2×20000; all pairwise supports disjoint (the sparsity regime).
- The prefix-diversity probe (inline) — the class-collapse table:
  12/12, 44/56, 60/244, 156/1023.
- Artifacts read: `scratch/gate_1e6/` (report + JSON + run log),
  `gate_1e5_s42/`, `gate_1e5_s123/` (report + JSON),
  `extract_gate.py`, `notes/decisions.md` D-172/173/174/175,
  `notes/log_002.md` §D-175, `notes/overview.md` (the perf
  claims), `src/reversi/lm/hlp_gate.py` and `hlp_wave.py` in full,
  `src/reversi/test/data/rlm_03.json` (the campaign config: ec 20,
  LMC + the A2050 patterns), `tools/prng.py`.
