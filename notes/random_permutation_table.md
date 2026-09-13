# The Random Permutation Table (ODP-9)
## Design, motivation, and the statistical-equivalence proof

> **Provenance.** I-017 (the feature-characterization project),
> written 2026-09-11 by Nia for Roberto's review and for EXTERNAL
> PEER REVIEW (DeepSeek V4 Pro / GLM 5.3 — the requested
> second opinion on §6 and §7).
> **Status: FINAL (v4, 2026-09-12 — after THREE independent
> reviews: DeepSeek V4 Pro (notes/peer_review_random_
> permutation_table.md — v1+v2 pass; the author's response
> in §10), Kimi K3 (notes/peer_review_kimi_random_
> permutation_table.md — PASS WITH THREE REQUIRED AMENDMENTS,
> all ADOPTED in v3, D-166), and GLM 5.3 (notes/
> peer_review_glm_random_permutation_table.md — PASS WITH
> TWO BLOCKING AMENDMENTS + MINORS, ALL ADOPTED in v4,
> D-168). The GLM review caught what the v3.1 hardening
> (D-167, landed AFTER the two prior reviews) introduced:
> the D₀ noise formula was wrong (the Σ√x ≥ √Σx error —
> understated 6-36×, "verified" by the formula evaluating
> itself) and the §6.4 phase "PROVEN" tag was invalid
> (explicit counterexample + the m_g feedback loop). v4
> replaces the calibration with the MEASURED, TABLE-AWARE
> one (E[TV₀] ≈ S½/√(πN), S½ per comparison unit; the
> table-aware absolute cap; the parametric bootstrap
> threshold; the corrected certification schedule), demotes
> the phase term to the gated residual with its direct
> measurement (the phase-occupancy scan), and folds the
> four minor fixes. THE PRE-DECLARED FINAL ROUND APPLIES:
> the document is FROZEN for T5. The T5 wave engine must NOT be
> built on this design until the T6 gate (§7, as amended in
> v3) is approved and executed.
> Companion documents:
> `notes/analytical_properties_of_features.md` (the project plan,
> §3.2 the generator design, ODP-9 the adopted pick),
> `src/reversi/lm/hlp_random_play.py` (the T4 single-game
> implementation of this design, D-162),
> `src/reversi/tools/prng.py` (the MT19937 port, D-159; the T3
> golden suite pins it bit-exact against Roberto's C build).

---

## 1. The problem

The I-017 analyses (SU — unsupervised; eta²/omega² — supervised)
need a reference population: the CONFIGURATION FREQUENCIES of
"random play, arrested at the model's ec" — the same ec window
the regab DB was collected at ("mele con mele"). The corpus is
the input of every downstream statistic:

- the marginal frequency of every sub-variable
  (feature × instance → configuration code);
- the JOINT frequency of every requested pair
  (PATTERN_A – PATTERN_B);
- the adherence statistics of the DB set against this ideal
  population (chi-square, KL, total variation).

Requirements that fix the design:

1. **Size.** 1e7 positions (the small-fast default; 1e9 for the
   high-precision runs). A game arrested at ec = 20 contributes
   ~40-60 plies.
2. **The pattern set is OPEN.** It is no longer the static 12
   patterns: the set grows (10-16 square patterns, e.g. 5X2COR),
   and the joint statistics need MORE samples per cell, because
   the cell cardinality grows with the pattern size (a 16-square
   pattern has 3^16 = 43 million possible codes — the cells are
   sparse; see §4.4).
3. **Reproducibility.** The corpus must be a pure function of
   (seed, ec, size, generator version) — it is CACHED, and the
   seed is in the cache signature.
4. **Speed.** The corpus generation is the expensive phase
   (minutes at 1e7, hours at 1e9) and must run as a vectorized
   numba kernel over 1M-game arrays ("a manetta").
5. **The sampling unit is pinned here (v3, second review
   Amendment 1).** The corpus keeps EVERY PLY of every
   arrested game (the T4 design). TWO derived populations
   serve the downstream statistics, and each use must name
   its unit: (a) the ARRESTED-POSITION population — one
   position per game, AT the arrest ec: the apples-to-apples
   reference for the DB ADHERENCE statistic (the regab DB is
   one position per game, at the model's ec); (b) the FULL-
   TRAJECTORY population — every ply of every arrested game:
   the reference for the SU / eta² / omega² FREQUENCY
   characterization (the per-game extra plies are the sample
   that fills sparse cells, §4.4). Note (second review): the
   marginal frequency over the full-trajectory population is
   a MIXTURE over plies — each game contributes 1 + (its
   pass count) plies, and the ec level of each ply; the
   arrest ec is reached EXACTLY (ec drops by 1 per real
   move), so the mixture weights are determined by the
   per-game pass distribution — which is why the gate
   compares per-ec-level, stratum by stratum, and compares
   the pass frequencies directly (§7, test 2). The per-
   STRATUM COUNTING RULE is pinned here for the gate
   implementation (third review, minor 4): a game with a
   pass contributes two positions at the SAME ec (identical
   board, sides swapped) — whether these are duplicates or
   distinct samples depends on whether the sub-variable
   codes distinguish the sides; the gate must apply the
   counting rule (dedup or not) IDENTICALLY for G₀ and G₁
   (the choice itself is a T6 implementation detail — what
   is pinned is the identity of the rule between the two
   generators).

The question this document answers: **can we replace "one
uniform PRNG draw per (game, ply)" with a deterministic,
vectorizable construction, without biasing the statistics?**

---

## 2. The brute force (G₀) — the reference semantics

**Definition (G₀).** A random game is a sequence of plies. From
the initial position (4 stones, ec = 60), at each ply: compute
the legal-move set L (|L| = k ∈ {0..64}); if k = 0 the mover
passes (the turn flips); otherwise pick a move UNIFORMLY AT
RANDOM from L — one fresh PRNG draw per ply, INDEPENDENT of all
previous draws and of all other games — and apply it. The game
is arrested when ec reaches the target (the model's ec); the
corpus keeps every ply of every arrested game.

G₀ is the reference definition of "random play": its statistics
are what "the ideal same-window population" MEANS. Any
alternative must be equivalent to it in the sense of §5.

**The cost of G₀ (measured, Roberto's C generator).** The C
generator that produced the pattern probability distributions
(EDGE, DIAG8, ...) used exactly this scheme — one PRNG draw per
active game per ply. Result: HOURS per generation run; for
5X2COR (10 squares) plausibly DAYS. In the Python/numba
pipeline the same scheme has a second problem: the PRNG call is
in the hot loop. For N = 1e7 games × ~50 plies that is ~5e8
generator calls; to make that numba-fast one would have to
re-implement the MT19937 twist/temper inside numba — duplicating
the algorithm that the T3 golden suite pins bit-exact in Python,
and making the two implementations a maintenance hazard. The
plan v2 (confirmed at T0c) recorded this rejection verbatim:
*"one PRNG draw per active game per ply = ~1e9 Python calls for
the 1e9 corpus → the PRNG becomes the bottleneck (the numba-
wrapped twist would be mandatory); the lookup table removes the
issue."*

---

## 3. The smart solution (G₁) — the permutation lookup table

**Definition (G₁).**
- **Setup (once per corpus, Python, outside the hot loop).**
  A seeded MT19937 (the ported library, §provenance) builds,
  for every k = 1..64, ONE permutation P_k of {0..k-1} by
  Fisher–Yates (the standard shuffle, driven by the PRNG's
  uniform rank draws). Total cost: sum of (k-1) for k = 1..64
  = **2016 PRNG draws** — negligible.
- **Steady state (the hot loop, numba-able).** Each game g
  carries a small integer COUNTER c_g, initialized at c_g(0) = g
  (the SLOT ID — the "per-game phase" pin, §4.3). At a ply with
  k legal moves (k ≥ 1): the rank is
  r = P_k[c_g mod k], and the chosen move is the r-th legal
  square in the CANONICAL ORDER of the legal set (ascending
  bit index — the popcount scan). After a real move the
  counter increments (c_g ← c_g + 1); a PASS consumes no
  counter step. **No PRNG in the loop.** The whole advance step
  (legal moves, popcount, table gather, k-th-set-bit, counter
  bump, make_move, pass flip, game-over detection) is pure
  integer array arithmetic over the 1M-game arrays.

**What changed relative to G₀.**
(i) The per-ply draws are REPLACED by (a seeded permutation per
width) + (a per-game counter walk). The "randomness" moved OUT
of the loop and INTO the seed (the table) and the slot phases.
(ii) The picks within one game are NO LONGER INDEPENDENT: the
shared counter couples the ranks across plies (a pick at width k
and a pick at width k' are linked through the same counter
value; two picks at the SAME width k are linked through the
SAME permutation row P_k). This coupling is the only place a
bias could hide — §6.3 treats it honestly.

---

## 4. Technical motivations for preferring G₁

### 4.1 The hot loop becomes a pure integer kernel
The per-advance cost of G₁ is: popcount (a table or SWAR), one
gather (table[k, counter % k]), one k-th-set-bit (a bit
twiddle), one counter increment. All of it vectorizes over the
1M-game arrays and jits cleanly in numba. The PRNG disappears
from ~5e8 call sites and appears exactly 2016 times (setup).
This is the difference between Roberto's C generator taking
hours/days and the wave engine running at the memory-bandwidth
limit of the position arrays.

### 4.2 The setup cost does not scale with the corpus
G₀'s cost is O(N × plies) PRNG calls. G₁'s is 2016 calls +
O(N × plies) integer operations. The 1e9 run pays the SAME
2016-draw setup as the 1e4 micro-corpus.

### 4.3 The slot phase decorrelates the N games (and prevents a degenerate corpus)
c_g(0) = g means: two adjacent slots differ by ONE counter step.
At width k they consume P_k[φ] and P_k[φ+1] — DIFFERENT ranks
(a permutation has no repeats) — so adjacent slots make
different moves as soon as the first width-≥2 decision comes,
and their trajectories DIVERGE from there (one different move
changes the whole continuation). Without a per-game phase every
game would share the SAME rank walk and the corpus would
degenerate (all 1e6 games make the same first move — a single
trajectory, 1e6 times). The slot phase is not an optimization:
it is what makes the N games N different games.

### 4.4 The sampling error is QUADRATIC in N — the argument for "more samples"
The cell-wise sampling error of the corpus estimator is
~ 6·√(p(1-p)/N) per cell (6-sigma), where p is the cell's true
frequency. Because it scales as √p (not p), FILLING SPARSE
CELLS is what buying more samples actually buys:

| cell cardinality C | 6-sigma max-cell error @ N = 1e6 | @ N = 1e4 |
|---|---|---|
| 64 | 7.4e-4 | 7.4e-3 |
| 1,296 | 1.7e-4 | 1.7e-3 |
| 4,096 | 9.4e-5 | 9.4e-4 |
| 16,384 | 4.7e-5 | 4.7e-4 |

(The 1e6 column was verified numerically; the √p law is
exact. The 6σ framing is PER-CELL: the MAX-cell deviation
across a C-cell table exceeds the single-cell 6σ — the
multiple-comparisons inflation of the extreme; this table
is a per-cell statement, not a max-cell statement.)
This is precisely why the OPEN pattern set (bigger patterns,
sparser cells, joint tables) pushes the corpus to 1e7-1e9 —
and why the generator's per-sample cost must be the integer
kernel of G₁, not the PRNG call of G₀.

---

## 5. What "statistically equivalent" means (the precision section)

Let F_v(code) be the corpus marginal frequency of sub-variable v
and F_uv(code_u, code_v) the joint. Let E₀[·] be the expectation
under G₀ (iid random play) — the reference. Let the G₁ table
rows be treated as RANDOM UNIFORM permutations (Assumption A1,
below) and let E_seed[·] be the expectation over the seed.

**G₁ is equivalent to G₀ in the following THREE senses — and
only in these senses:**

- **(E1) One-step ORACLE equivalence (PROVEN, §6.3).** From
  ANY GIVEN state — a fixed position with legal set L and a
  fixed counter value c, both INPUTS, not table-generated —
  the G₁ one-step pick, in expectation over the seed (A1), is
  UNIFORM over L: the generator's LOCAL rule has EXACTLY the
  same semantics as G₀'s draw, no approximation. (v1 claimed
  the corpus-level expectation equality at this level; that
  claim is reclassified in v2 — see (E1-corpus) below and
  §10.)
- **(E1-corpus) Corpus-level expectation equality (NOT
  proven exactly — GATED, §6.4, §7).** The seed-averaged G₁
  corpus frequencies (the marginals AND the joints — the
  actual statistics of I-017, functions of the GENERATED
  positions) equal the G₀ expectations only up to the path-
  coupling deviation (the per-ply decision contexts along a
  generated trajectory are functions of the table's earlier
  picks — the oracle uniformity does not lift to the
  trajectory ensemble). This is verified EMPIRICALLY by the
  T6 gate (tests 2-6) against a same-scale G₀ reference,
  BEFORE the expensive build — and it is the direct
  verification of the design requirement (below).
- **(E2) Sampling-error equivalence (PROVEN as an order
  statement, §6.2).** The G₁ corpus estimator's sampling error
  is of the SAME ORDER as G₀'s own Monte Carlo error,
  O(√(p/N)) per cell — the same irreducible noise G₀ pays.
  (For sparse cells G₁'s error is actually the smaller term in
  absolute terms, §4.4 — the noise is the noise of N samples,
  not of the generator.)
- **(E3) Bias / systematic deviation (PARTLY PROVEN, PARTLY
  TESTED).** A fixed-seed G₁ corpus can deviate from E₀ by:
  (a) a **phase-discrepancy term** — the v2/v3 "provably
  O(k/N) ≤ 6.4e-5" claim was FALSIFIED by counterexample
  and by the m_g feedback loop (third review Amendment B):
  demoted to the GATED residual, measured directly by the
  gate test 1 phase-occupancy scan (§6.4);
  (b) a **path-coupling term** (v2: this is now the MAIN
  unproven residual, for the marginals AND the joints — the
  (E1-corpus) gap, §6.4): along a GENERATED trajectory the
  per-ply decision contexts (L_t, c_t) are functions of the
  table's earlier picks, so the per-ply pick law deviates
  from the G₀ uniform law by the ENTRY-CONSUMPTION effect
  (§6.3: at a width-k ply the pick is uniform over the row's
  UNCONSUMED entries, or deterministic if the current entry
  was already consumed by an earlier same-width pick —
  including the same-width pair-law deviation, TV = 1/k at
  the rank level, §6.5), and the corpus-level expectation
  equality is NOT bounded in closed form. It is handled NOT
  by a proof but by a PRE-REGISTERED EMPIRICAL GATE (the T6
  tests 2-6, §7): the G₁ micro-corpus (1e4) must be
  statistically INDISTINGUISHABLE
  from a G₀ micro-corpus (1e4 — cheap to generate: ~5e5 draws),
  at the level of G₀'s own Monte Carlo noise. If the gate
  fails, the FALLBACK is a second independent counter (the two
  same-width picks then draw from independent rank walks — the
  residual coupling is only the shared permutation row, which
  the gate re-measures).

**The one honest sentence (v2).** G₁ is not "G₀ with the draws
replaced". G₀ produces a DISTRIBUTION over corpora; G₁ produces
ONE deterministic corpus per seed. What is PROVEN: the one-
step oracle equivalence (E1 — from any given state, the seed-
averaged G₁ pick is a uniform pick: the local semantics are
identical to G₀'s), the lemmas, the phase combinatorics
(E3a, ≤ 6.4e-5) and the sampling-error order (E2). What is
EMPIRICALLY VERIFIED (the T6 gate, §7, BEFORE the expensive
build, with a pre-specified fallback): the corpus-level
equivalence (E1-corpus — the marginals and joint frequencies
against a same-scale G₀ reference) and the path-coupling
residual (E3b).

**The design requirement (what the statistics actually need
— v3.1, QUANTIFIED — second review Amendment 3 + the v3.1
clarification).** The I-017 statistics (SU, eta²/omega², the
adherence) do NOT require "G₁'s corpus to be an exact G₀
expectation". They require the ideal population to be
RANDOM-PLAY-LIKE within a NOVELTY-BOUNDED tolerance. The
bound is on the **TV (total variation) of the frequency
tables** (the ½·L1 discrepancy over all cells — the scalar
the downstream information statistics consume), and is
**delta* = 2e-3, fixed a priori, in ABSOLUTE terms.**
Quantified (v4 — the v3.1 figures were WRONG and are
replaced. The v3.1 formula 0.4·√(2S/N) illegally pulled the
sum INSIDE the square root (Σ√x ≥ √Σx — subadditivity),
yielding the single-effective-cell LOWER bound; the correct
first-order formula is **E[TV₀] ≈ S½/√(πN)** with
**S½ = Σ_cells √(p(1-p))**, measurable from the frequency
tables per (sub-variable × stratum) — one pass, no extra
corpus. The v3.1 "verified numerically" figures were the
formula EVALUATING ITSELF. Third review (GLM 5.3,
Amendment A); re-verified by independent simulation before
adoption (uniform C = 1296, N = 4e7: sim
3.19e-3..3.31e-3, theory 3.21e-3, v3.1 formula 8.9e-5 — a
36× understatement; per-ec stratum N = 1e6: sim
1.99e-2..2.08e-2, theory 2.03e-2):
- the D₀ noise (the TV between two i.i.d. G₀ corpora): for
  a uniform-like 1296-cell table (S½ ≈ 36): ≈ **3.2e-3 at
  1e6 POOLED** (N ≈ games×40), ≈ **2.0e-2 per-ec STRATUM**
  (N ≈ games), ≈ **1.0e-3 at 1e7 pooled**, ≈ **6.4e-3 at
  1e7 per-stratum**. The noise floor is TABLE-DEPENDENT
  through S½ (concentrated tables: 5e-4..2e-3 at 1e6
  pooled — the third review's simulations).
- the ABSOLUTE cap is TABLE-AWARE (v4): **delta*_unit =
  max(2e-3, q95(D₀_unit))** per comparison unit. delta* =
  2e-3 remains the certification TARGET at the scales where
  the unit's noise floor is below it (1e7 POOLED for
  uniform-like tables: q95 ≈ 1.1e-3 < 2e-3 — the cap is
  ACTIVE there); the self-calibrating q95 governs
  elsewhere. (The v3.1 unconditional 2e-3 cap was UNPASSABLE
  BY CONSTRUCTION for broad-support tables: a perfect G₀
  twin of the G₀ reference — D ≈ 3.2e-3 at 1e6 pooled —
  would fail it. The gate would have tested the table's
  concentration, not the generator: a gate that spuriously
  fails a perfect replica is worse than no gate.)
- the BOOTSTRAP-RELATIVE criterion (D below the q95 of the
  MEASURED D₀ distribution, §7) is the PRIMARY self-
  calibrating criterion at every scale — whatever the true
  table-dependent noise, the percentile is estimated from
  replicates. The gate's demand is unchanged and remains
  the right one: G₁-vs-G₀ no worse than two random G₀
  corpora are to each other, at the scale where that
  demand is resolvable.
- the honest certification schedule (v4, on the corrected
  numbers): at 1e6 the gate certifies, for uniform-like
  broad tables, equivalence at the ~3.3e-3 level (pooled
  q95) and ~2.1e-2 level (per-stratum q95); the 2e-3-level
  certification is carried by the 1e7 BUILD gate (pooled
  q95 ≈ 1.1e-3, below delta* — the absolute cap active).
  Whether the 1e6 level suffices for I-017: YES on the
  (corrected) propagation arithmetic — a 2e-3 TV
  perturbation bounds |ΔH| ≤ h₂(TV) + TV·log₂(C−1) ≈
  **0.041 bits** at C = 1296 (the v3.1 "~2e-2" was ~2×
  low), and the 1e6 pooled certification level (3.3e-3)
  bounds it at ≈ 0.07 bits — ≤ ~7% relative on O(1)
  information quantities: a conservative worst-case bound
  against the ≥1e-1-scale effect-size distinctions the
  campaign draws (the typical, non-concentrated
  perturbation is far smaller); the 1e7 build gate tightens
  the pooled level to ≈ 0.025 bits.
- delta* = 2e-3 is an A PRIORI JUDGMENT (1/5 of the ~1e-2
  smallest effect size the campaign will consider
  meaningful); if T7+ measures the actual effect sizes and
  they are much smaller, the bound is re-examined — by then
  the corpus exists and can be re-baselined.
A SYSTEMATIC bias does not average down with N the way
Monte Carlo noise does — that is why the bound is absolute
and rescaled per scale (test 7), and why the two-stage gate
(1e6 design + 1e7 build) certifies at the scale where each
tolerance is actually resolvable. The reclassification
(E1-corpus: proven → gated) stands: the gate, as AMENDED in
v4, is a real BOUND on the corpus-level claims, not a
ritual.

---

## 6. The proof

### 6.0 Notation and assumptions
- The legal set at a ply: L, |L| = k; the CANONICAL ORDER of L:
  the ascending bit-index order (l_(0), ..., l_(k-1)) — a fixed
  (position-dependent) bijection from ranks to squares.
- A pick = a rank r ∈ {0..k-1}; the square = l_(r). A uniform
  rank over {0..k-1} is equivalent to a uniform square over L
  (the canonical order is a bijection).
- **Assumption A1 (the table).** The rows P_k (k = 1..64)
  behave as INDEPENDENT UNIFORM random permutations. A1 is the
  standard MT19937 quality assumption (the 623-dimensionally
  equidistributed generator; the T3 golden suite pins the
  implementation bit-exact against Roberto's C build, which is
  the operational meaning of "the seeded shuffle"). One
  mechanism note (second review, Kimi K3): the Fisher–Yates
  rank draws go through random_choice_from_finite_set — the
  FLOOR of a [0,1) double (get_double_in_c0_o1), NOT a
  bitmask rejection: a modulo-free reduction whose induced
  non-uniformity is ≤ k·2⁻⁵³ ≈ 7e-15 at k ≤ 64 — negligible,
  and the SAME construction as the C reference T3 pins. A1
  is ALSO empirically re-verified at the T6 gate (the table
  properties + the pick distribution).
- **Assumption A2 (the scale).** N (the corpus size) ≥ 1e4, so
  that k ≤ 64 is small relative to N (used only in the O(k/N)
  bound).

### 6.1 Lemma 1 — a permutation of a uniform is uniform
If P is a bijection of {0..k-1} and X is uniform on {0..k-1},
then P[X] is uniform on {0..k-1}.
*Proof.* For any y: P(P[X] = y) = P(X = P⁻¹[y]) = 1/k. ∎

### 6.2 Lemma 2 — the counter covers every residue exactly once per k steps
For any integers a, k ≥ 1: the k consecutive counter values
a, a+1, ..., a+k-1 represent each residue class mod k EXACTLY
ONCE.
*Proof.* (a + i) mod k are distinct for i = 0..k-1 (a
difference i - j with 0 < |i-j| < k is not divisible by k), and
there are k of them. ∎
*Consequence (the balanced-design property).* Over ANY window of
k consecutive real moves, the G₁ pick at width k visits each
rank of P_k exactly once: the INTRA-GAME time-average over the
window is EXACTLY uniform (1/k per rank) — zero fluctuation,
where G₀'s average over the same window is 1/k ± O(1/√k).

### 6.3 Theorem 1 (v2) — the one-step ORACLE equivalence
*Statement.* Fix ANY position p with legal set L (|L| = k) and
ANY counter value c — both GIVEN, not generated by the table.
Under A1, the G₁ one-step pick from (p, c), in expectation
over the seed, is UNIFORM over L.
*Proof.* The pick is the l_(P_k[c mod k])-th square: c mod k
is a FIXED residue (c is given), and P_k is a uniform random
permutation (A1 — only this row is involved; NOTHING is
generated, so there is nothing to condition on). By Lemma 1,
P_k[c mod k] is uniform on {0..k-1}; through the canonical
order (a bijection) the pick is uniform over L — exactly the
G₀ one-step draw. ∎
*This is the design's semantic statement.* "The table is the
seeded shuffle": one step at a time, from any given state, the
G₁ pick (seed-averaged) is a uniform pick over the legal set.

**The circularity of the v1 statement (first review, point
2.1 — CONFIRMED and resolved).** v1 stated Theorem 1
CONDITIONED ON THE TRAJECTORY PREFIX, with the proof "the
prefix fixes c mod k (a number); P_k is uniform; Lemma 1
applies." The reviewer correctly flagged the circularity: the
prefix is a deterministic function of the table — conditioning
on it restricts the admissible realizations of P_k. The
precise mechanism, stated here for the record: at a width-k
ply with counter residue m = c mod k, let R be the set of
residues c_s mod k CONSUMED by earlier same-width picks.
- If m ∈ R: the current entry P_k[m] was already used — the
  pick is DETERMINISTIC (the rank played earlier), not
  uniform.
- If m ∉ R: the entry is unconsumed; P_k[m] is uniform over
  the k − |R| unconsumed VALUES (the consumed entries took
  |R| distinct values — a permutation), not over all k.
So the TRUE conditional kernel (given the prefix) is "uniform
over the unconsumed entries, deterministic on reuse" — a
deviation from the G₀ uniform law that is exactly the
path-coupling residual. The v1 proof is invalid as stated.

**Why the review's proposed replacement is not a drop-in fix
(the author's response, §10).** The review proposes the
UNCONDITIONAL statement: "the marginal distribution of the
G₁ pick, averaged over the seed WITHOUT conditioning on the
prefix, is uniform over L." This does not close the gap:
(i) at a fixed ply INDEX t, the legal set L_t is itself a
random variable (different seeds generate different
positions at ply t) — "uniform over L" is not well-defined
without specifying which L; (ii) the review's own rescue
(steps 1-6) stops at "BUT c IS NOT INDEPENDENT OF P_k. This
is the core issue" — without resolving it: c_t = c(0) + (the
number of non-pass plies before t) is a function of the
trajectory, hence of the TABLE, and the marginal uniformity
of P_k does NOT imply the marginal uniformity of
P_k[c mod k] for a table-DEPENDENT c (counterexample: a
table-dependent index I(P_k) can make P_k[I] anything — for
k = 2, I = 1{P₂ = [1,0]} makes P₂[I] identically 0: a point
mass, not a uniform). The trajectory-generated index is
table-dependent, so the uniformity of P_k[c mod k] is NOT
established by the marginal uniformity of P_k — it is the
gated question. The ORACLE statement above is the valid
replacement: it keeps the full strength of Lemma 1 (no
conditioning, no generation) at the cost of taking (p, c) as
inputs — which is exactly the level at which the generator's
semantics are defined.
*Consequence (the v2 reclassification).* Because the per-ply
decision contexts (L_t, c_t) along a GENERATED trajectory are
table-dependent, the oracle uniformity does NOT lift to a
corpus-level expectation equality: Theorem 2 (v2) states what
remains proven and moves the rest to the gate.

### 6.4 Theorem 2 (v2) — what the corpus-level claims are
*Statement (v2, after the first review's point 2.2 —
ACCEPTED).* The v1 claim "the G₁ corpus marginals AND joint
expectations equal the G₀ expectations exactly up to O(k/N)"
is RECLASSIFIED. The v1 step-3 argument ("the pair
factorizes through the marginals because the two indicators
live on different positions") is SUPERSEDED: the observable
codes are functions of the GENERATED positions (the position
at ply t is shaped by the picks at plies < t — values of the
table), so the seed-averaged corpus frequency is a statement
about the seed-averaged G₁ POSITION-ENSEMBLE distribution,
which the oracle Theorem 1 (a local, one-step statement
about the pick at a GIVEN state) does not establish. The
review's point 2.2 was stated for the joints; the SAME gap
applies to the MARGINALS (v1 classified both as PROVEN —
both are reclassified here).
- **GATED (v4 — the v2/v3 "PROVEN" tag was INVALID, third
  review Amendment B).** The v2/v3 claim ("the phases are
  balanced up to the m_g spread, ≤ 64 slots") is FALSIFIED
  by an explicit counterexample: m_g = (r − g) mod k has
  spread ≤ k−1 ≤ 63, yet EVERY slot's phase (g + m_g) mod k
  = r — a POINT MASS, imbalance N(1 − 1/k) (verified
  numerically: k = 2, m_g = g mod 2 → one distinct phase
  across 1e6 slots — 5e5 slots of imbalance vs the claimed
  ≤ 64). Deeper: m_g (the pass-adjusted move count) is a
  function of the trajectory, which is a function of the
  table AND of the slot's own phase — the feedback loop
  (phase → picks → trajectory → passes → m_g → phase) makes
  the phase term a PATH-COUPLED channel, not a purely
  combinatorial one (the v2 "purely combinatorial: it
  concerns the slot phases, not the table" label re-opened,
  in miniature, the exact hole v2 closed — corrected here).
  The practical risk is probably small (at the FIRST
  width-k decision m_g = 0 across slots — phases = g mod k,
  EXACTLY balanced; later m_g variation is pass-driven and
  quasi-random), but "probably small" is what the gate is
  for: the per-width PHASE-OCCUPANCY SCAN (gate test 1)
  measures it directly — the cross-slot histogram of the
  realized phases (g + m_g) mod k vs uniform, per width k
  (a chi-square with k−1 df, Bonferroni over the 64
  widths). E3a's "provably O(k/N)" is STRUCK; the phase
  term joins the gated residual. (Lemma 2 itself — the
  WITHIN-GAME residue cover over k consecutive counter
  steps — remains PROVEN; what was falsified is the
  CROSS-SLOT generalization built on it.)
- **NOT proven exactly (the path coupling) → GATED.** The
  corpus-level equality E_seed[F^{G₁}] = E₀[F] (marginals
  AND joints) is not bounded in closed form here: the
  per-ply deviation is the entry-consumption effect (§6.3:
  "uniform over the unconsumed entries" vs "uniform over all
  entries", plus the deterministic-reuse plies), accumulated
  through the trajectory-shaping dependence. Plausibility
  (NOT a proof — the reviewers checked and found it sound as
  plausibility; NO cheap re-proof was found by either
  review): the local semantics are identical (oracle
  Theorem 1), so the AVERAGED path through the position
  graph follows the same transition weights as G₀ in
  expectation; the N slot orbits are large, so the per-seed
  corpus statistics concentrate around the seed average; the
  deviation, if any, is the entry-consumption effect at
  corpus scale — and it is MEASURED, not argued: the T6 gate
  (tests 1-6, §7, v3: run at 1e6 with the ABSOLUTE delta* =
  2e-3 bound and the G₀-vs-G₀ bootstrap calibration at the
  same scale — a systematic bias is bounded in absolute
  terms, NOT declared subdominant by extrapolation; the v2
  "a fortiori subdominant" sentence is STRUCK per the second
  review).

### 6.5 The joint-coupling residual (the honest part, E3b)
Theorem 2 covers the joint at the level of EXPECTATIONS. What
it does NOT cover: the VARIANCE structure of the joint — the
fact that under G₁ the two ranks of a same-width pair (k = k')
are values of ONE permutation at two indices, hence NEVER equal
(a uniform random permutation at two distinct indices gives a
uniform ordered DISTINCT pair), whereas G₀'s two independent
draws CAN coincide (probability 1/k). The total-variation
distance between the two pair laws is 1/k (large at small k:
1/2 at k = 2). **Does this bias the observable joint
frequencies?** The rank-level coupling must propagate through
the two-step mapping (ranks → legal sets → feature codes) to
reach the observable. The two picks act on TWO DIFFERENT
legal sets (the position changed between the two plies) and
the joint codes are functions of TWO DIFFERENT features —
typically this ATTENUATES the effect (the "rank inequality"
constraint couples coordinates the observable does not see as
the same coordinate). But the degree of attenuation — or, in
principle, AMPLIFICATION (a feature that collapses distinct
legal squares to the same configuration code, e.g. an edge
pattern that does not distinguish the board's quadrants,
could CONCENTRATE the rank-inequality constraint onto the
observed codes) — DEPENDS ON THE FEATURE GEOMETRY and is not
bounded in general (first review, point 2.4 — adopted). Hence
the empirical gate: the T6 tests (3-5, §7) MEASURE the
G₁-vs-G₀ joint discrepancy at 1e4 scale (where G₀ is cheap
to run), including a SAME-WIDTH-specific test (the risky
case) and a SMALL-K focus (k ≤ 4 — where TV = 1/k is
largest), with a threshold calibrated on G₀'s own noise; the
fallback (a second independent counter) is pre-specified.
This is part of the equivalence that is TESTED rather than
PROVEN, and the document states that plainly.

### 6.6 Summary of what is proven vs tested (v2)
| claim | status |
|---|---|
| one-step ORACLE pick law = G₀'s (given (position, counter); seed-averaged, A1) | **PROVEN** (Theorem 1 v2, Lemma 1) |
| the cross-slot phase balance (the §6.4 phase term) | **GATED (v4)** — the v2/v3 spread bound was FALSIFIED by counterexample (m_g = (r−g) mod k → a point mass) and the m_g feedback loop makes the term a path-coupled channel; measured by the gate test 1 phase-occupancy scan. (Lemma 2, the within-game residue cover, remains PROVEN.) |
| corpus-level MARGINALS: E_seed F^{G₁} = E₀ F | **NOT proven exactly** (the path coupling — the oracle uniformity does not lift to the generated ensemble; v1 called this PROVEN) — the phase component proven; the rest **measured by the T6 gate** (test 2) + pre-specified fallback (§6.4, §7) |
| corpus-level joint EXPECTATIONS: same | **NOT proven exactly** (the path coupling + the same-width pair law; v1 called this PROVEN) — **measured by the T6 gate** (tests 3-5, incl. the same-width and small-k focus) + pre-specified fallback (§6.4-§6.5, §7) |
| sampling error = G₀-scale O(√(p/N)) | **PROVEN as an order statement** (§5-E2, §4.4) |
| A1 (the table ≈ uniform random permutations) | **assumed** — MT19937 quality + T3 bit-exact golden + T6 empirical re-check (test 1) |

---

## 7. The empirical complement — the T6 gate (pre-registered,
## v3 — the three required amendments ADOPTED)

The proof covers the oracle kernel, the lemmas, the phase
combinatorics and the error order; the gate covers everything
corpus-level (E1-corpus, E3b) and A1. The v3 amendments
(second review, Kimi K3 — all adopted): the scale is **1e6**
(a SYSTEMATIC bias must be bounded in ABSOLUTE terms against
the 1e7 noise floor — a 1e4 gate with ~1e-2 noise cannot
resolve delta* = 2e-3; G₀ at 1e6 is still cheap: ~5e7 draws,
minutes in Python); the marginal comparison is
**ARREST-STRATIFIED** (the marginal is a mixture over plies —
the mixture weights are the pass distribution, §1.5); the
**focused TV/KL tests are the PRIMARY** joint instruments (a
pooled sparse-occupancy chi-square loses local power); the
pass criterion is the **ABSOLUTE delta*** + the bootstrap
percentile, with family-wise error control.

**Scale: 1e6 games, arrested at the model's ec** (the SAME
arrest rule for G₀ and G₁ — stated explicitly, second review
Amendment 1a) — the DESIGN gate, before the T5 build. At
1e6 the D₀ noise (v4, the CORRECTED formula
S½/√(πN) — §5) is ≈ 3.2e-3 pooled / ≈ 2.0e-2 per-ec stratum
for uniform-like 1296-cell tables (S½ ≈ 36 — table-
dependent, measured per comparison unit), so the table-
aware dual criterion of §5 is a RESOLVED quantity, and G₀
remains a faithful reference (~15-20 min to run per corpus
in the T4 Python loop; G₁ the same). The 1e7 BUILD gate
(test 7) re-certifies at full scale, where the D₀ noise
drops to ≈ 1.0e-3 pooled (q95 ≈ 1.1e-3 — BELOW delta*,
where the absolute cap becomes active).

1. **Test 1 (the table, A1 + the phase-occupancy scan,
   v4).** Every row P_k a valid permutation (already in the
   T4 suite); the pick distribution: for each width k, the
   histogram of the chosen ranks over the gate corpus vs
   uniform — chi-square (the coarse A1 re-check; the
   floor-of-double rank reduction is ≤ k·2⁻⁵³ ≈ 7e-15 —
   §6.0). Plus the per-width PHASE-OCCUPANCY SCAN (v4,
   Amendment B): the cross-slot histogram of the realized
   phases (g + m_g) mod k vs uniform, per width k (a
   chi-square with k−1 df, Bonferroni over the 64 widths)
   — the direct measurement of the phase term the v2/v3
   "PROVEN" claim could not carry (§6.4).
2. **Test 2 (the marginals — v3 STRATIFIED, second review
   Amendment 1).** For every sub-variable, G₁ vs G₀:
   (a) PER-EC-LEVEL: the position distribution at each ec
   level (from the start 60 down to the arrest ec) — the
   PRIMARY comparison (a pure pass-frequency difference
   would show up here, and a per-stratum bias cannot cancel
   across strata); (b) the pass FREQUENCIES (the per-game
   ply-count distribution) compared directly; (c) the pooled
   full-trajectory marginal — reported as a SECONDARY
   aggregate. Metric: D = the TV (total variation) of the
   per-sub-variable frequency tables, tested against (i) the
   the TABLE-AWARE delta*_unit = max(2e-3, q95(D₀_unit))
   (§5 v4) and (ii) the q95 of the MEASURED D₀ = TV(G₀,
   G₀') distribution, computed PARAMETRICALLY (mean +
   1.645·sd — the TV's empirical CV is ~2%, so the
   parametric form is stable where the 20-sample maximum
   would be ±30-40%) from 20 G₀-vs-G₀ replicate pairs at
   1e5 (≈ 2.5 h total), rescaled PER POPULATION by the 1/√N
   law (the pooled marginal scales with games×40, the
   per-ec strata with games — the PRIMARY stratified
   comparison's threshold is set from the STRATUM-scale
   replicates; expected q95 for uniform-like 1296-cell
   tables: ≈ 3.3e-3 pooled / ≈ 2.1e-2 per-stratum at 1e6 —
   the v3.1 "1.5e-4" was the flawed formula's artifact).
   Family control:
   Bonferroni over the sub-variable family (the per-cell
   p-values are secondary diagnostics, with BH-FDR — second
   review Amendment 3.2).
3. **Test 3 (the joints — v3 FOCUSED-PRIMARY, second review
   Amendment 2).** For each sampled su pair: the joint table
   F(c_A, c_B) (the two codes at the SAME position — the SU
   unit), STRATIFIED BY THE PLY WIDTH k (the strata where the
   entry-consumption risk concentrates — small k first: the
   TV = 1/k rank coupling is largest there, and the
   cross-ply pick coupling propagates to the same-position
   joint through the trajectory ensemble): per-stratum
   D = TV (and KL) of G₁ vs G₀, with the same dual threshold
   (delta* + the bootstrap 95th percentile, G₀-vs-G₀ at
   1e6) and BH-FDR over (sub-variable × stratum). These are
   the PRIMARY joint instruments.
4. **Test 4 (the small-k dedicated pass).** The k ≤ 4 plies
   (early game, tight positions — the largest TV = 1/k): the
   observable codes there within delta* of G₀. (The first
   review's suggestion, refined in v3 into a dedicated pass.)
5. **Test 5 (the pooled joint chi-square — DEMOTED to a
   coarse sanity check, second review Amendment 2).** The
   full G₁-vs-G₀ joint chi-square (df ≈ 1.7e6 at the
   1296×1296 table — the asymptotic regime, critical value ≈
   2√df + a few sigma): a wide net, not a load-bearing
   instrument (at sparse occupancy the merged-tail
   chi-square loses local power — flagged by the first
   reviewer, made a required re-ordering by the second).
6. **Test 6 (the phase-continuity scan — optional, first
   review suggestion).** 3-5 different counter0 phase
   initializations (e.g. offsets 0, 7, 4000001, ...): the
   frequency tables must stay within G₀ noise of each other
   (no phase-locked artifact).
7. **Test 7 (the 1e7 BUILD gate — v3.1, v4 numbers).** At
   corpus build time (the 1e7 production run), the
   G₁-vs-G₀ comparison is RE-RUN at full scale: the G₀
   reference at 1e7 is affordable (~2-3 h in the T4 Python
   loop, or the T5 cross-check), and the D₀ noise drops
   (uniform-like 1296-cell tables: ≈ 1.0e-3 pooled, q95 ≈
   1.1e-3 — BELOW delta*, where the absolute cap becomes
   ACTIVE; ≈ 6.4e-3 per-stratum). The same table-aware
   dual criterion applies. This closes the band where a
   systematic bias above the 1e6 detection floor (q95 ≈
   3.3e-3 pooled) yet below the resolvable 1e7 pooled floor
   (≈ 1.1e-3) could otherwise pass the 1e6 design gate
   while remaining visible at 1e7 (a bias of 1.5-3× the
   1e7 pooled floor is a clear detection there; the
   per-stratum comparison at 1e7 certifies at the ~6.7e-3
   q95 level — coarser, but the POOLED comparison carries
   the tight bound). The corpus is ACCEPTED only after
   BOTH gates pass (the 1e6 design gate before T5; the 1e7
   build gate at build time).

**Pass criterion (v4 — ALL FOUR must hold).** (i) ABSOLUTE
(TABLE-AWARE): every per-unit discrepancy D (the TV scalar)
below delta*_unit = max(2e-3, q95(D₀_unit)) — the 2e-3
target is ACTIVE where the unit's noise floor is below it
(at 1e7 pooled for uniform-like tables; elsewhere the
self-calibrating q95 governs, so a perfect G₀ replica can
never fail the gate — the v3.1 unconditional 2e-3 cap,
which WOULD have failed one, is replaced); (ii) RELATIVE
(PRIMARY): every D below the parametric q95 (mean +
1.645·sd) of the measured G₀-vs-G₀ distribution at the
unit's scale (≈ 3.3e-3 pooled / ≈ 2.1e-2 per-stratum for
uniform-like tables at 1e6); (iii) the focused tests (3-4)
pass under the family control (Bonferroni/BH as above),
plus the test 1 phase-occupancy scan; (iv) the 1e7 BUILD
gate (test 7) passes at corpus build time. A pass of (i)+
(ii) is what turns the gate from a ritual into a BOUND:
the systematic G₁-vs-G₀ deviation is certified at the
RESOLVED level for each comparison unit (with the
downstream propagation bound of §5), and (iv) guarantees
the 2e-3-level certification (pooled) at the scale where
the corpus is actually used.

**FAIL → attribution, then the fallback (v3 sharpening —
second review §4.4).** A gate failure is ATTRIBUTED before
any fix: the counter-mediated coupling and the shared-row
distinctness are DIFFERENT defects. The pre-specified
fallback — a second independent counter (c'_g, a different
phase, e.g. c'_g(0) = g + a large co-prime offset) for the
"second pick stream" — removes the COUNTER-mediated coupling
but NOT the permutation distinctness (any two counters still
read the SAME row P_k: P_k[a] ≠ P_k[b] for a ≠ b — same-
width pairs remain uniform-DISTINCT, TV = 1/k from G₀'s
allows-equality law). So: if the cross-width tests pass and
the SAME-WIDTH / small-k tests (3-4) fail, the fallback will
NOT rescue the design — the residual is the shared-row
distinctness, which no number of independent counters fixes.
The escape hatch for THAT failure mode is a partial retreat
toward G₀ at exactly the small-k plies: a FRESH per-ply
PRNG draw for the second same-width pick (the PRNG call
returns to a MINORITY of the hot loop — the small-k plies —
the vectorized bulk is untouched). A design decision at that
time, if it ever comes. If even that fails, the design
question re-opens.

---

## 8. Cost model (the "why not just keep G₀" answer)

| | G₀ | G₁ |
|---|---|---|
| PRNG calls per corpus (1e7) | ~5e8 | 2016 (setup, once) |
| hot loop | PRNG call per (game, ply) — the bottleneck; numba-ification = duplicate the MT implementation | pure integer array ops — the numba tier |
| measured precedent | Roberto's C generator: hours (5X2COR: days) | target: the memory-bandwidth limit of the position arrays |
| reproducibility | deterministic PRNG (reproducible) | deterministic table + counters (reproducible, AND the setup does not scale with N) |
| statistical content | the reference iid semantics | the one-step oracle equivalence PROVEN (the local semantics are identical); the corpus-level equivalence (marginals + joints) verified by the T6 gate against a same-scale G₀ reference (§5-§7, v2) |

---

## 9. Review status (v3 — closed by the two independent reviews)

The v2 checklist was answered by the two reviews; the status
of each point, for the record:
1. **Theorem 1 v2 (the oracle).** CONFIRMED by both reviews
   (DeepSeek V4 Pro v2 pass; Kimi K3 §1.3, §4.1, §4.2 —
   independent re-derivation: "the oracle statement is the
   faithful semantics of that code"; the rejection of the
   unconditional-marginal fix confirmed as "valid and
   decisive").
2. **The reclassification (marginals + joints → gated).**
   CONFIRMED by both ("the single most important change in
   v2, and it is correct" — Kimi K3 §2). NO cheap re-proof
   found by either review (Kimi K3 §8.2: "the counter walk
   across widths is not a standard (t,m,s)-net and the
   coupling is genuinely trajectory-shaped. The gate is the
   right call.").
3. **The design requirement.** QUANTIFIED in v3 per Kimi K3's
   Amendment 3 (the absolute delta* = 2e-3, the 1e6 scale,
   the delta-method propagation bound) — "with that fix,
   yes" (Kimi K3 §8.3).
4. **A1.** ACCEPTED by both; the floor-of-double note added
   in v3 (Kimi K3 §4.3).
5. **The gate.** ADEQUATE AS AMENDED in v3 (Kimi K3's three
   required amendments — the arrest-stratified marginal, the
   focused-tests-primary re-ordering, the absolute-bias
   bound + multiple-comparison control — all adopted in
   §7); the fallback boundary sharpened (Kimi K3 §4.4).
6. **The scope discipline.** "This is the document's best
   feature" (Kimi K3 §7); the one v2 overclaim ("a fortiori
   subdominant") is STRUCK in v3.

**The third review was in fact requested (and was worth
it).** The v3.1 hardening (D-167) landed AFTER the two
prior reviews — an unreviewed quantitative layer, and the
GLM 5.3 review (notes/peer_review_glm_random_
permutation_table.md — PASS WITH TWO BLOCKING AMENDMENTS +
MINORS) caught exactly that layer: the D₀ noise formula was
wrong (the Σ√x ≥ √Σx error — 6-36× understated, "verified"
by the formula evaluating itself) and the §6.4 phase
"PROVEN" tag was invalid (an explicit counterexample + the
m_g feedback loop). ALL amendments ADOPTED in v4 (D-168),
independently re-verified by simulation before adoption.
The v3.1 lesson, recorded for the record: the review
process that caught v1's unproven PROVEN tags let an
unverified NUMBER through the same door — a claimed
verification that cannot disagree with the claim it
verifies is not a verification. The document is now FINAL
(the pre-declared final round applies): the T5 wave engine
is built on G₁ with the v4 gate as the T6 instrument.

> **Bottom line for Roberto (v4, FINAL, post THREE
> reviews).** The design PASSES three independent reviews
> (DeepSeek V4 Pro; Kimi K3 — three amendments adopted;
> GLM 5.3 — two blocking + minors, all adopted). What is
> PROVEN: the one-step oracle equivalence (the local
> semantics are exactly G₀'s), Lemma 1, Lemma 2 (the
> within-game residue cover), the sampling-error order.
> What is BOUNDED (not proven): the corpus-level equality —
> and the v4 gate is calibrated on MEASURED, TABLE-AWARE
> numbers (the v3.1 D₀ formula was wrong — 36× understated
> for uniform tables — and the v3.1 phase "PROVEN" tag was
> falsified; both corrected): at 1e6 the gate certifies,
> for uniform-like broad tables, ~3.3e-3 pooled / ~2.1e-2
> per-stratum (the noise floors — a perfect G₀ replica
> passes by construction, because the cap is table-aware);
> the 2e-3-level certification (pooled) is carried by the
> 1e7 BUILD gate, where the noise floor (≈ 1.1e-3 q95) is
> below delta* and the absolute cap is active; the
> corrected propagation bound (≈ 0.07 bits worst case at
> the 1e6 level, ≈ 0.025 at 1e7 pooled) says the schedule
> suffices for I-017. The honest framing (Kimi K3,
> confirmed by GLM): "G₁ gives the same results as G₀" is
> a PRE-REGISTERED EMPIRICAL CLAIM with a fully specified,
> correctly calibrated bound — not a theorem; the v4 gate
> turns it into a certified bound BEFORE the expensive
> build. When the T6 gate (1e6, then 1e7) passes, the T5
> wave engine is built on G₁.

---

## 10. Review history and the author's response (v2)

**First review (2026-09-11, DeepSeek V4 Pro — the document at
notes/peer_review_random_permutation_table.md).** Verdict:
THE DESIGN PASSES, with one critical correction (the
Theorem 1 circularity), one material correction (the joint-
expectation overclaim), and minor fixes.

**The author's response (this v2):**
- **2.1 (the circularity) — AGREED and fixed, but NOT with
  the review's proposed replacement.** The circularity is
  real (the prefix conditions the table); the precise
  mechanism is now stated in §6.3 (the entry-consumption:
  "uniform over the unconsumed entries, deterministic on
  reuse"). The review's replacement statement (the
  unconditional marginal) is not valid as a drop-in fix: at a
  fixed ply index the legal set is a random variable (the
  statement is not well-defined without conditioning), and
  the review's own rescue stops at "c is not independent of
  P_k — this is the core issue" without resolving it (the
  marginal uniformity of P_k does not imply the uniformity of
  P_k[c mod k] for a table-dependent c; the k = 2
  counterexample in §6.3). The ORACLE statement (given
  (position, counter), nothing generated) is the valid
  replacement: full Lemma 1 strength, no conditioning, at the
  level where the generator's semantics are defined.
- **2.2 (the joint overclaim) — AGREED, and EXTENDED.** The
  step-3 factorization does not hold for the generated
  positions (the codes are functions of table-dependent
  positions) — and the SAME applies to the marginals, which
  v1 also classified as PROVEN. Reclassified: the corpus-
  level equality (marginals AND joints) is GATED, not
  proven (§6.4, §6.6).
- **2.3 (the O(k/N) derivation) — AGREED; the review's
  sharper form (the m_g spread, ≤ 64) is adopted in §6.4.**
- **2.4 (the TV = 1/k nuance) — AGREED; the "generally
  second-order" wording is replaced by the geometry-
  dependent attenuation/amplification statement in §6.5.**
- **2.5 (the same-width test) — AGREED; adopted as T6 test
  4, plus test 5 (small-k) and test 6 (phase continuity),
  the review's suggestions.**
- **A1 (review §4) — agreed as assessed.**
- **The verdict (PASS, build on G₁) — CONFIRMED**, with the
  understanding that the empirical gate now carries the
  corpus-level claims (marginals + joints), not only the
  residual: the design requirement of I-017 is "random-play-
  like within the measurement precision", and the gate
  verifies exactly that, at a scale where G₀ is a faithful
  reference, BEFORE the expensive build.

**Second review (2026-09-11, Kimi K3 — the document at
notes/peer_review_kimi_random_permutation_table.md).**
Verdict: PASS WITH THREE REQUIRED AMENDMENTS — all ADOPTED
in v3. The author's response:
- **No rebuttal — the three amendments are all correct, and
  adopted.** (A review that re-derives independently — its
  §4 matches this document's own analysis — and whose new
  points are genuine weaknesses of the gate design. Accepted
  without reservation.)
- **Amendment 1 (the arrest stratification + the sampling
  unit) — ADOPTED** (§1.5, §7 test 2). One refinement: the
  arrest lands EXACTLY at the target ec (ec drops by exactly
  1 per real move); the trajectory-dependent quantity is the
  pass count — hence the per-ec-level comparison + the
  direct pass-frequency comparison. The sampling unit is
  pinned in §1.5 (the two derived populations: the
  arrested-positions → the DB adherence reference; the full
  trajectories → the SU / eta² / omega² reference).
- **Amendment 2 (the sparse-cell power) — ADOPTED** (§7:
  tests 3-4 are the PRIMARY TV/KL instruments on the joint
  table stratified by ply width; test 5 is demoted to a
  coarse sanity check).
- **Amendment 3 (the absolute bias bound) — ADOPTED; the
  strongest point of the review** (§5, §7): a systematic
  bias does not shrink with N — a 1e4 gate (noise ~1e-2)
  cannot resolve a 1e-3 systematic bias that would be
  dominant at 1e7 (noise ~1e-3). Resolution: the gate runs
  at 1e6 (G₀ still cheap: ~5e7 draws); the absolute delta*
  = 2e-3 fixed a priori (negligible against the I-017
  effect sizes; delta-method propagation ~2e-3 in H/MI);
  the TV per sub-variable + the Bonferroni/BH family
  control; the G₀-vs-G₀ bootstrap at 1e6 (5-10 pairs). The
  v2 "a fortiori subdominant" sentence is STRUCK.
- **The A1 floor-of-double note — ADOPTED** (§6.0: the rank
  reduction is the floor of a [0,1) double, not a bitmask
  rejection; the bias is ≤ k·2⁻⁵³ ≈ 7e-15).
- **The fallback sharpening — ADOPTED** (§7): the second
  counter removes the counter-mediated coupling but NOT the
  shared-row distinctness (the TV = 1/k remains); a
  same-width failure is NOT rescued by the fallback; the
  escape hatch is the fresh per-ply PRNG draw at the small-
  k plies (the partial G₀ retreat at a minority of the hot
  loop).
- **The honest framing — ADOPTED (bottom line)**: "G₁
  gives the same results as G₀" is a PRE-REGISTERED
  EMPIRICAL CLAIM with a fully specified bound — not a
  theorem; the gate turns it into a certified bound before
  the expensive build.
- **No third review was requested at the time — and a
  third was in fact commissioned (GLM 5.3) and WAS WORTH
  IT.** It caught the v3.1 unreviewed quantitative layer.

**Third review (2026-09-12, GLM 5.3 — the document at
notes/peer_review_glm_random_permutation_table.md).**
Verdict: PASS WITH TWO BLOCKING AMENDMENTS + MINORS. The
author's response: **FULL ACCEPTANCE — nothing rejected,
no questions.** GLM re-derived everything independently
BEFORE reading the prior reviews (anti-capture), re-
verified the whole proven core (all confirmed — including
the arrest-exactness claim against the Reversi rules and
`ec_of`), and ran NUMERICAL verification of the v3.1
quantitative claims — which the two prior reviews could
not have seen (v3.1 landed after them):
- **Amendment A (BLOCKING) — ACCEPTED, and it was MY
  error.** The v3.1 D₀ formula 0.4·√(2S/N) illegally
  substituted √(Σp(1-p)) for Σ√(p(1-p)) (subadditivity:
  Σ√x ≥ √Σx) — the single-effective-cell lower bound,
  understating the true noise E[TV₀] ≈ S½/√(πN) by
  S½/√S: 36× for a uniform 1296-cell table (GLM's
  simulation: 3.20e-3 vs my 8.9e-5 at N = 4e7; I re-
  ran an independent simulation before adopting:
  3.19e-3..3.31e-3 vs theory 3.21e-3 — confirmed). And
  my v3.1 "verified numerically" figures (2.8e-4, 8.9e-5)
  were the formula EVALUATING ITSELF (0.4·√(2/N) to the
  digit, S = 1) — a verification that cannot disagree with
  the claim it verifies is not a verification. The same
  epistemic sin the v1 process caught in a theorem,
  recurred in a number I added in v3.1. Consequences
  adopted: the table-aware absolute cap (delta*_unit =
  max(2e-3, q95(D₀_unit)) — the v3.1 unconditional cap was
  UNPASSABLE BY CONSTRUCTION: a perfect G₀ twin, D ≈
  3.2e-3 at 1e6 pooled, would fail it); the parametric
  bootstrap threshold (mean + 1.645·sd, TV CV ~2%); the
  per-population √N rescaling; the corrected certification
  schedule (1e6: ~3.3e-3 pooled / ~2.1e-2 per-stratum for
  uniform-like tables; 1e7 build: pooled q95 ≈ 1.1e-3,
  below delta* — the cap active); the corrected
  propagation bound (|ΔH| ≤ h₂(TV) + TV·log₂(C−1) ≈ 0.041
  bits at TV = 2e-3, C = 1296 — my "~2e-2" was ~2× low).
- **Amendment B (BLOCKING) — ACCEPTED.** The v2/v3 phase
  "PROVEN" tag is INVALID: m_g = (r−g) mod k (spread ≤
  k−1) makes ALL phases equal r — a point mass, imbalance
  N(1−1/k) vs the claimed ≤ 64 (I re-ran it: k = 2,
  m_g = g mod 2 → one distinct phase across 1e6 slots —
  confirmed). Deeper and correct: m_g is
  table/phase-dependent (the pass feedback loop) — the
  phase term is a path-coupled channel, not "purely
  combinatorial"; the v2 label re-opened, in miniature,
  the hole v2 closed. Demoted to GATED + measured by the
  new test 1 phase-occupancy scan. (The practical risk is
  probably small — at the first width-k decision m_g = 0
  and the phases are EXACTLY balanced — but "probably
  small" is what the gate is for.)
- **Minors — all ACCEPTED:** the §4.4 garbled cell
  (4.7e-4), the per-cell vs max-cell clause (the 6σ
  framing is per-cell; the max-cell deviation exceeds it),
  the per-stratum pass-counting pin (a pass contributes
  two same-ec positions; the dedup rule must be IDENTICAL
  for G₀ and G₁ — T6 implementation detail, the identity
  of the rule is pinned in §1.5).
- **No questions for the reviewer.** The math was
  independently re-verified before adoption (the two
  simulations above); the fixes are fully specified; the
  verdict stands.
- **The pre-declared final round applies (D-167):**
  whatever the third review returned, the valid
  amendments are folded in and the document FREEZES. v4
  is the FINAL version; the T5 wave engine is built on G₁
  with the v4 gate as the T6 instrument.
---

## 11. Post-freeze empirical results (D-173/D-174, 2026-09-13)

The v4 body is FROZEN and unmodified (the pre-registration
stands as written). This section records what the gate
found when it was run exactly as §7 specifies, and the
design decision it drove. It is an addendum — it does not
amend any frozen statement.

### 11.1 The T6 1e6 design gate (D-172): VERDICT FAIL

1e6 games arrested at the model's ec 20, seed 42, G₁ table
pick vs G₀ global golden-pinned MT19937, 20 D₀ G₀-vs-G₀
pairs @ 1e5 (parametric q95, the 1/√N rescale), the
table-aware delta* = 2e-3. **FAIL on (i), (ii), (iii).**

The evidence (the dense units — the clean metrics):

| Quantity | D (G₁ vs G₀) | D₀-q95 | ratio |
|---|---|---|---|
| LMC (mobility) marginal, per-ec max | 0.174 | 0.0037 | 47× |
| LMC marginal, pooled | 0.019 | 0.0005 | 37× |
| Pass distribution | 0.002 | 0.0001 | 15× |
| Phase-occupancy scan | p ≈ 0 (widths 3-10, 12, 14-18) | — | BROAD |
| Joint-cell concentration (LMC×R2) | 9 repeated cells (multiplicities 8,8,6,4,3,3,3,2,2) vs G₀ ZERO repeats in 2×20000 | — | the real signal (the chi-square flip 136/153 @1e6 vs 0/153 @1e5 is the test's power, UNCONTROLLED — no G₀-pair chi-square baseline) |
| Phase continuity (slot-base 4000001 offset) | pooled TV 0.143 (1e6) / 0.306 (1e5, both seeds) | — | phase-LOCKED |

SPARSITY NOTE (the GLM Round-2 audit): the raw report's
most dramatic numbers (the per-ec pattern "marginals"
CORNER/XEDGE/R2/R3/R4/2X5COR/DIAG5-7 at D = 1.000 "disjoint
supports"; the joints D = 1.000, KL = 50 cap) are
SPARSITY-SATURATED / UNINFORMATIVE: the gate's per-feature
key is the FULL INSTANCE TUPLE (e.g. CORNER = 19683⁴ ≈
1.5e17 cells), singleton-dominated at the gate's scales —
and their OWN D₀ is saturated too (G₀-vs-G₀′ per-ec CORNER
TVs are 1.0 as well; DIAG8 is the demonstrative case: at
the 1e5 scale G₁'s D = 0.604 sits BELOW its own-scale D₀
≈ 0.90 — G₁ is CLOSER to G₀ than two G₀ corpora are to
each other; the "2.1×" is a √10-rescale artifact on a
saturated statistic — TV saturates at 1, the √N law is a
small-TV expansion, and rescaling a saturated value is
arithmetic without meaning). The VERDICT NEVER RESTED on
those units: remove every sparse unit and the FAIL is
unchanged (the dense LMC/passes/phase units carry it).
Guard for any future gate run: q95(D₀_unit) ≥ 0.9 ⇒ the
unit is declared uninformative at that scale. (Also
recorded: the joint units ran on the concatenated full
instance tuple — 11 orders sparser than the pre-registered
per-instance accounting; the "primary joint instrument"
never actually ran at its designed granularity — a
gate-implementation defect, moot for the verdict.)

SEED-INDEPENDENCE (the 1e5 confirmations): seed 42 LMC
0.174 (15× the noise); seed 123 LMC 0.206 (19×). Same
magnitude, different seed — a design property, not a seed
artifact.

PER-EC PROFILE: the LMC deviation concentrates EARLY
(ec 56: 0.206; ec 57: 0.164; ec 55: 0.127; ec 53: 0.094;
decaying to the arrest) — the path-coupling signature
(§6.4, the phase→pick→trajectory→phase feedback).

ATTRIBUTION: the measured mode is BROAD (most widths
3-10, 12, 14-18 non-uniform in the phase scan; the joint
gradient flat across strata — no small-k spike). The
counter-mediated path coupling dominates over the
small-k shared-row distinctness (the ply-2 pair marginal
is EXACTLY balanced — 12 pairs at 1/12 each — so the
distinctness channel is not even open at the depth where
the bias is largest; the mechanism: §11.3).

### 11.2 The design decision (D-174): G₀ is the corpus
generator

Roberto's design call (2026-09-13): the 1e7 I-017 corpus
is generated with G₀ (the uniform pick, the single global
golden-pinned MT19937, ONE seed — pinned 42, documented
in the corpus provenance; "one seed for all" stands).
The ODP-9 table engine stays as the ANALYTICAL RECORD:
Lemma 1, Lemma 2 (the WITHIN-game residue cover), and
the oracle Theorem 1 (E1, the one-step equivalence) are
proven and intact. The cross-slot phase-balance claim
(E3a, the frozen §6.4 "≤ 6.4e-5") was FALSIFIED by the
Round-1 counterexample (the m-spread does not bound the
phase multiset) and the gate measured it failing (p ≈ 0).
The corpus-level claim (E1-corpus) is REFUTED at the
1e6-resolved level (not merely "empirically bounded").

Justification: (a) the gate FAIL is at 47× the noise
floor in a quantity I-017 actually consumes (the
mobility is an A2050 sub-variable) — outside any
tolerance; (b) in the numba wave tier the table's
original motivation (no PRNG in the hot loop — the T4
Python era) no longer exists: G₀ measures as fast as G₁
(gated 1e6 runs: 19.6 vs 20.5 min, gate observation
included; the steady-state wave tier, 1e7 runs: G₀
277,470 games/s @ ec=20 (36.0 s) and 189,571/s @ ec=0
(52.8 s) — ~11M moves/s at either ec; the G₁ 5.3 s/1e6
single-wave figure is warmup-tainted — the clean G₁
steady-state benchmark is due in the profiling session);
(c) the reproducibility is identical (one seed, the
fixed (lane, step) draw order, the bit-exact replay).

### 11.3 The mechanism (the class-collision cloning)

The GLM Round-2 audit (2026-09-13) corrected the
attribution: the corpus-level signature is the shadow of
the CLASS-COLLISION CLONING — the demoted §6.4 phase
channel (phase → pick → trajectory → width → phase
feedback) — NOT of the shared-row distinctness. The
counter walk makes slot g's trajectory a deterministic
function of g: the trajectory CLASS at ply t is
g mod L_t (L_t = the lcm of the widths met so far), and
within a class the ply-t phase (g + t) mod k_t takes
only k_t/gcd(L_t, k_t) distinct values — the class
branches into THAT many children, not k_t. When k_t | L_t
the class makes ONE move en bloc: total cloning. The
early plies are where L_t is small and the cloning is
drastic. Measured prefix diversity (2000 games per
engine, the GLM audit):

| prefix depth | G₁ distinct | G₀ distinct |
|---|---|---|
| 2 moves | 12 | 12 |
| 3 moves | 44 | 56 |
| 4 moves | 60 | 244 |
| 5 moves | 156 | 1023 |

At ply 2 there is NO degeneracy at all: the widths (4, 3)
are coprime, the slot map g ↦ (g mod 4, (g+1) mod 3) is
a bijection onto all 12 rank pairs, and the G₁ (m1, m2)
marginal is EXACTLY balanced (12 pairs at 1/12 each,
better than G₀'s multinomial) — the balanced-design
property working AS DESIGNED; the distinctness channel
is not even open at the depth where the bias is largest.
The collapse starts at ply 3 (44/56) and is drastic at
ply 4-5 (60/244, 156/1023): the G₁ trajectory tree is a
throttled, deterministic, integer-weighted SUBTREE of
G₀'s full branching process — the corpus's early-game
position distribution is a small structured set with
exact weights, and the LMC marginal inherits the bias
(ec 57 = after 3 moves: TV 0.167-0.206 across scales).
As L_t grows the gcd → 1, full branching resumes and the
bias decays — but the weight structure is already baked
into the corpus: the residual 0.012-0.019 at the arrest
ec is still 6-10× ABOVE delta* = 2e-3 — even the
arrested-position population alone (the DB-adherence
reference) fails the v4 criterion.

The "destroyed BY DESIGN" attaches to the deterministic
COUNTER WALK (the one-dimensionality of the walk), not
to MT19937's serial properties: A1 holds (the rank
histograms pass — the table is a fine permutation); what
dies is the INDEPENDENCE of successive picks (the
successive-pick tuples are constrained to the
permutation-row curves, so the dice's k-dimensional
equidistribution — the Matsumoto-Nishimura guarantee
that pairs, triplets, every sequence up to k = 623
dimensions fill the space uniformly — is not inherited
by the table's picks). E1 survives ONLY as the oracle
statement: the phrase "averaged over an independent
phase distribution the pick is uniform" begs the
question — the phase distribution is
trajectory-dependent, and that dependence IS the
failure.

Analytical status: the distinctness constraint itself
is provable (the row is a permutation — phases a ≠ b
pick distinct ranks; the TV against the allows-equality
law is 1/k, already in the §6 lemmas). The MAGNITUDE of
the marginal distortion (the 47×) is a statement about
the deterministic dynamical system (the class-collision
cloning + the phase-selection feedback) and rests on
the empirical measurement — as §5/§6.4 prescribed: the
phase term was demoted from PROVEN to GATED precisely
because the feedback loop makes it path-coupled, and
the gate has now quantified it.

### 11.4 The certification schedule, amended by fact

- The 1e6 design gate: FAILED for G₁ (this section) —
  the corpus is NOT G₁.
- The 1e7 corpus: G₀ (the reference by construction).
  The §7 test 7 (the 1e7 build gate, which re-certified
  G₁ ≈ G₀ at full scale) loses its object; the
  build-time check reduces to the corpus integrity (the
  quota, the unique slots, the ec target) + a
  noise-level spot check (the G₀-vs-G₀' D₀ scale).
- The 2e-3 delta* target: for a G₀ corpus against the
  G₀ reference the comparison is the noise floor
  itself; I-017's tolerance question becomes the
  ordinary Monte-Carlo error of the 1e7 G₀ estimator
  (the O(1/√N) sampling noise), not a generator-bias
  question.
- The §7 shelf remedies, DISPOSED OF (the GLM Round-2
  audit supplied the argument the record owed): the
  FALLBACK (the second independent counter, c'_g = g+Δ)
  is analytically DEAD for the measured mode — both
  counters remain AFFINE in g, so the class structure
  g mod L_t and the collision condition k_t | L_t
  persist for EVERY offset Δ: the prefix collapse
  (44/56, 60/244, 156/1023) and the phase-occupancy
  feedback reappear with the same magnitudes, merely
  permuted — the second counter removes the two-stream
  rank coupling, NOT the one-dimensionality of the
  walk. The ESCAPE HATCH (the fresh per-ply PRNG at
  small-k plies) is out-scoped by the evidence: the
  non-uniform widths run 3-18 and the deviation peaks at
  ec 55-57 where the widths are 5-10 — outside its
  patch. Both shelf remedies are dead; the G₀ decision
  is not premature: it is FORCED.
- The SU analysis (the I-017 dedicated level):
  OPTIONAL in the pipeline config, default FALSE (no
  run) — Roberto's instruction, 2026-09-13; the
  FEATURE_ANALYSIS level is not in the config schema
  yet (the T12 work — the flag lands in the T12 config
  design, no premature schema change); the profiling
  session (the OPTIMIZE pattern) is scheduled AFTER the
  SU level is complete.

### 11.5 The GLM Round-2 audit (2026-09-13) — "a design
failure, not a bug"

The fourth review (notes/
peer_review_glm_random_permutation_table.md, Round 2)
audited the entire document and the gate — independently,
from scratch, nothing taken for granted — and answered
the decisive question: is the FAIL a property of the
DESIGN (G₁ was an abbaglio), or an implementation BUG?
Verdict: **the FAIL is REAL, SYSTEMATIC, and belongs to
the DESIGN. No implementation bug is anywhere in the
chain, and I looked hard for one.**

- The infrastructure (all verified): the MT19937 numba
  kernels bit-exact vs the golden-pinned oracle (624
  draws × 3 seeds); the wave G₁ engine 12/12 lanes
  bit-exact vs the T4 scalar reference (the full move
  sequence AND the pass counts); the observed positions
  VALID Reversi (exactly 44 stones at the arrest, zero
  color overlap); the color-swap hypothesis tested and
  EXCLUDED (the swap makes the TV worse, as it must if
  the corpora are aligned); the D₀ calibration coherent
  with the v4 formula. "The instrument is sound. The
  failure it measured is in the object, not the
  instrument."
- The evidence (every number verified against the
  primary artifacts — the 1e6 report/log, both 1e5
  confirmations): the corrections folded into §11 above
  (17 SU pairs, not 18; the width list gains 14; the
  joint flip re-framed as the uncontrolled occupancy
  signal; the sparse units declared
  SPARSITY-SATURATED/UNINFORMATIVE with the DIAG8 case;
  the joint-unit implementation defect recorded).
- The independent replication (the anti-bug proof): a
  THIRD code path — the T4 scalar reference for G₁
  against the reviewer's own hand-written scalar G₀
  loop (no gate code in the path) at 1e4: the signature
  reproduces EXACTLY (the early-ec LMC deviation ~5-6×
  the noise ALREADY at 1e4; the D is scale-INVARIANT
  from 1e4 to 1e6 — 0.17 everywhere — while the noise
  falls 1/√N: the fingerprint of a SYSTEMATIC design
  property). The arrested corpus is NOT collapsed
  (19,970 distinct positions of 20,000 — a WEIGHT bias
  over a rich support, not a degenerate support).
- Endorsement: "I endorse D-174 without reservation: G₀
  — the reference semantics, the generator that needs
  no equivalence argument — is the corpus generator. ...
  Nothing was thrown out with the bathwater: the baby
  (the proof architecture, the T4/T5 wave machinery, the
  MT kernels, the gate harness — all verified bit-exact
  this round) is alive and now carries the G₀ corpus.
  What died is a design idea, and it died of
  evidence." The process note: three reviews caught the
  unproven tags and the miscalibrated numbers BEFORE
  the build; the pre-registered gate caught the one
  thing no review could — the empirical claim itself.
- The audit's self-corrections (for the record): the
  Round-1 "practical risk is probably small" was wrong
  in magnitude (the counterexample was right; the
  magnitude was not — the gate measured p ≈ 0, and this
  round derives why); the Round-1 Amendment A √N
  rescale inherited the saturated-regime blind spot
  (the SPARSITY NOTE above); the Round-2 starting
  hypothesis of a ply-2 rank-pair degeneracy was
  falsified by the audit's own measurement (the 4-3
  coprime lattice is perfectly balanced) — the true
  mechanism is the ply-3+ class collapse.

ERRATA (the frozen body, unedited by the freeze — do
not take these stale spots at face value; §11
supersedes them): §5's one-honest-sentence still lists
"the phase combinatorics (E3a, ≤ 6.4e-5)" as PROVEN
(falsified — the Round-1 Amendment B counterexample);
§5-E3b and §6.5 still say the gate runs at 1e4 (it ran
at 1e6 + the 1e5 confirmations); §6.6 row 3 "the phase
component proven" contradicts row 2 of the same table
(demoted to GATED); §7's intro "the proof covers … the
phase combinatorics" is stale in the same way.
