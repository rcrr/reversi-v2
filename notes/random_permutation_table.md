# The Random Permutation Table (ODP-9)
## Design, motivation, and the statistical-equivalence proof

> **Provenance.** I-017 (the feature-characterization project),
> written 2026-09-11 by Nia for Roberto's review and for EXTERNAL
> PEER REVIEW (DeepSeek V4 Pro / GLM 5.3 — the requested
> second opinion on §6 and §7).
> **Status: REVISED (v3, 2026-09-11 — after TWO peer reviews:
> the first, DeepSeek V4 Pro, at notes/peer_review_random_
> permutation_table.md (v1+v2 pass; the author's response in
> §10); the second, Kimi K3, at notes/peer_review_kimi_random_
> permutation_table.md (PASS WITH THREE REQUIRED AMENDMENTS —
> all three ADOPTED in this v3: the arrest-stratified
> marginal comparison + the sampling-unit pin, the
> focused-tests-primary gate re-ordering, and the
> ABSOLUTE-bias bound that strikes the "a fortiori
> subdominant" extrapolation). The T5 wave engine must NOT be
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
   the pass frequencies directly (§7, test 2).

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
| 16,384 | 4.7e-5 | 4.7e-3·10⁻¹ |

(The 1e6 column was verified numerically; the √p law is exact.)
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
  (a) a **phase-discrepancy term**, provably O(k/N) — bounded
  by 64/1e6 = 6.4e-5 for N = 1e6 (§6.2, Lemma 2) — negligible;
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
— v3, QUANTIFIED — second review Amendment 3).** The I-017
statistics (SU, eta²/omega², the adherence) do NOT require
"G₁'s corpus to be an exact G₀ expectation". They require
the ideal population to be RANDOM-PLAY-LIKE to within a
NOVELTY-BOUNDED tolerance: the systematic deviation of the
ideal population's cell frequencies must be bounded by
**delta* = 2e-3 (fixed a priori, in ABSOLUTE terms —
negligible against the I-017 effect sizes, which live at
1e-2 and above; a 2e-3 frequency perturbation propagates to
~2e-3 in H/MI by the delta method, below any practical
threshold).** The bound is ABSOLUTE, not "relative to the
gate-scale noise": a SYSTEMATIC bias does not average down
with N the way Monte Carlo noise does (a 1e-3 systematic
bias is invisible in a 1e4 gate — noise ~1e-2 — but
dominant in the 1e7 corpus — noise ~1e-3). This is why the
v3 gate runs at 1e6 (where G₀'s own noise is ~2e-3, so a
delta* = 2e-3 bound is a RESOLVED quantity, not a hope),
with a G₀-vs-G₀ bootstrap calibration at the SAME scale
(§7). It is why the reclassification (E1-corpus: proven →
gated) does NOT weaken the design: the gate, as amended, is
a real BOUND on the corpus-level claims, not a ritual.

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
- **PROVEN (the phase combinatorics).** The slot-phase
  cross-section: at any decision, the phases (g + m_g) mod k
  over the N slots are balanced up to a discrepancy of at
  most max_g m_g − min_g m_g (the spread of the move-ply
  indices m_g = the number of real moves played before the
  decision), which is ≤ 64 (a game plays at most 64 real
  moves) — hence the phase imbalance is ≤ 64 slots out of N:
  6.4e-5 of the corpus mass at N = 1e6. (v1 wrote "≤ k"; the
  review's sharper derivation — the m_g spread, bounded by
  64 — is adopted. This bound is purely COMBINATORIAL: it
  concerns the slot phases, not the table.)
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
| phase combinatorics: slot-phase imbalance ≤ 64/N (≤ 6.4e-5 @ N = 1e6) | **PROVEN** (Lemma 2 + the m_g-spread bound, §6.4) |
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
Amendment 1a). At 1e6, G₀'s own per-cell noise is ~2e-3 —
the scale at which the absolute delta* = 2e-3 bound (the
design requirement, §5) is a RESOLVED quantity, and G₀
remains a faithful reference (minutes to run).

1. **Test 1 (the table, A1).** Every row P_k a valid
   permutation (already in the T4 suite); the pick
   distribution: for each width k, the histogram of the
   chosen ranks over the gate corpus vs uniform — chi-square
   (the coarse A1 re-check; the floor-of-double rank
   reduction is ≤ k·2⁻⁵³ ≈ 7e-15 — §6.0).
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
   ABSOLUTE delta* = 2e-3 and (ii) the 95th percentile of
   the D₀ = TV(G₀, G₀') distribution over 5-10 G₀-vs-G₀
   bootstrap replicate pairs at 1e6. Family control:
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

**Pass criterion (v3 — ALL THREE must hold).** (i)
ABSOLUTE: every per-sub-variable and per-stratum discrepancy
D below delta* = 2e-3 (fixed a priori, §5); (ii) RELATIVE:
every D below the 95th percentile of the G₀-vs-G₀ bootstrap
distribution at 1e6; (iii) the focused tests (3-4) pass
under the family control (Bonferroni/BH as above). A pass of
(i)+(ii) is what turns the gate from a ritual into a BOUND:
the systematic G₁-vs-G₀ deviation is certified below delta*
IN ABSOLUTE TERMS — and delta* is negligible against the
I-017 effect sizes (delta-method propagation: a 2e-3
frequency perturbation → ~2e-3 in H/MI, below any practical
threshold).

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

The document is in its FINAL pre-T5 state. No third review is
requested: the two independent voices agree on the verdict
(PASS) and on every load-bearing point; the remaining risk
is EMPIRICAL (the T6 gate) and is now fully specified.

> **Bottom line for Roberto (v3, post TWO reviews).** The
> design PASSES two independent reviews (DeepSeek V4 Pro;
> Kimi K3 — the second "PASS WITH REQUIRED AMENDMENTS", all
> three ADOPTED). What is PROVEN: the one-step oracle
> equivalence (from any given state, the seed-averaged G₁
> pick is a uniform pick — the local semantics are exactly
> G₀'s), the lemmas, the phase combinatorics (≤ 6.4e-5), the
> sampling-error order. What is BOUNDED (not proven): the
> corpus-level equivalence (marginals AND joints) — the T6
> gate at 1e6 certifies the systematic G₁-vs-G₀ deviation
> below the ABSOLUTE delta* = 2e-3 (negligible against the
> I-017 effect sizes), with the arrest-stratified marginal
> comparison, the focused TV/KL joint tests as primary, the
> G₀-vs-G₀ bootstrap calibration at the same scale, the
> family-wise error control, and the sharpened fallback
> boundary. The honest framing (Kimi K3, adopted): as of
> this document, "G₁ gives the same results as G₀" is a
> PRE-REGISTERED EMPIRICAL CLAIM with a fully specified
> bound — not a theorem; the gate turns it into a certified
> bound BEFORE the expensive build. When the T6 gate passes,
> the T5 wave engine is built on G₁.

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
- **No third review is requested.** The two independent
  voices agree on the verdict (PASS) and on every
  load-bearing point; the remaining risk is EMPIRICAL (the
  T6 gate) and is now fully specified.
