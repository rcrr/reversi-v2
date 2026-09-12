# The Random Permutation Table (ODP-9)
## Design, motivation, and the statistical-equivalence proof

> **Provenance.** I-017 (the feature-characterization project),
> written 2026-09-11 by Nia for Roberto's review and for EXTERNAL
> PEER REVIEW (DeepSeek V4 Pro / GLM 5.3 — the requested
> second opinion on §6 and §7).
> **Status: PROPOSED** — the T5 wave engine must NOT be built on
> this design until the review confirms §6 and the T6 gate
> (below) is specified.
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

- **(E1) Expectation-level equivalence (PROVEN, §6.1-6.2).**
  For every observable that is a (position-weighted) sum of
  per-ply pick indicators — the marginals, and the joints at
  the level of EXPECTATIONS — E_seed[F^{G₁}] = E₀[F] EXACTLY.
  No approximation.
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
  (b) a **structural-covariance term** coming from the shared-
  counter coupling of the JOINT picks (§6.3). This term is NOT
  covered by the expectation proof (it is a second-order
  coupling effect, O(1/k)-scale at the RANK level, generally
  second-order at the CODE level because the two picks see
  different legal sets) — and it is handled NOT by a proof but
  by a PRE-REGISTERED EMPIRICAL GATE (the T6 test, §7): the G₁
  micro-corpus (1e4) must be statistically INDISTINGUISHABLE
  from a G₀ micro-corpus (1e4 — cheap to generate: ~5e5 draws),
  at the level of G₀'s own Monte Carlo noise. If the gate
  fails, the FALLBACK is a second independent counter (the two
  same-width picks then draw from independent rank walks — the
  residual coupling is only the shared permutation row, which
  the gate re-measures).

**The one honest sentence.** G₁ is not "G₀ with the draws
replaced". G₀ produces a DISTRIBUTION over corpora; G₁ produces
ONE deterministic corpus per seed. What is proven is that this
one corpus is, in expectation over the seed, the G₀ expectation
itself (E1), with G₀-scale sampling noise (E2) and a provably
tiny phase term (E3a) — and that the only unproven residual
(E3b) is measured by a gate with a fallback, BEFORE the
expensive corpus is built.

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
  the operational meaning of "the seeded shuffle"). A1 is
  ALSO empirically re-verified at the T6 gate (the table
  properties + the pick distribution on a tiny corpus).
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

### 6.3 Theorem 1 — the conditional pick kernel (the core)
*Statement.* Condition on the game's trajectory prefix up to a
ply (this fixes the legal set L, the width k, and the counter
value c). Under A1, the G₁ pick at this ply, in expectation
over the seed, is UNIFORM over L.
*Proof.* The G₁ pick is P_k[c mod k] (the rank) — a function of
the row P_k alone at this ply. Under A1, P_k is a uniform
random permutation, and c mod k is a FIXED residue (the
trajectory prefix is given). By Lemma 1, P_k[c mod k] is uniform
on {0..k-1}; through the canonical order (a bijection) the pick
is uniform over L. This is EXACTLY the G₀ conditional pick
distribution (a fresh uniform draw over L). ∎
*Remark (the scope, stated honestly).* Theorem 1 is a statement
about the ONE-STEP conditional kernel, seed-averaged. It says:
"at every ply, the G₁ pick has the same conditional law as the
G₀ pick." It does NOT say the G₁ trajectory is a G₀-sampled
trajectory (it is a deterministic orbit of the seed) — the
corpus-level consequence is §6.4.

### 6.4 Theorem 2 — the corpus marginals and joint EXPECTATIONS
*Statement.* For N = 1e6 (or any N ≫ 64) slots with phases
c_g(0) = g, the G₁ corpus marginal F_v (seed-averaged) equals
the G₀ expectation E₀[F_v] EXACTLY up to the O(k/N) phase
discrepancy; the same holds for the joint F_uv AT THE LEVEL OF
EXPECTATIONS.
*Proof sketch (the three steps a reviewer should check).*
1. **Per-ply exchange.** The corpus frequency is an average of
   per-ply indicators I((g, t) picks a code in a set S).
   Averaging the seed expectation OVER the corpus and
   exchanging the two averages (linearity — no independence
   needed at this step):
   E_seed F^{G₁} = (1/|corpus|) Σ_{(g,t)} E_seed[I(g,t)].
2. **The seed expectation per ply.** E_seed[I(g,t)] =
   E_seed[I | trajectory prefix of (g,t)] by the tower property
   — and by Theorem 1 the conditional pick law is uniform over
   L, so E_seed[I | prefix] = P(uniform pick ∈ S | prefix) =
   the SAME quantity computed under G₀. The summands are
   therefore IDENTICAL to the G₀ ones.
3. **The trajectory ensemble.** Under G₀ the sum Σ_{(g,t)} runs
   over a RANDOM trajectory ensemble; under G₁ it runs over the
   N DETERMINISTIC slot orbits. The equality of the per-ply
   conditional laws (step 2) plus the balanced design of the
   slot phases (Lemma 2: at any decision the N phases g + m_g
   (mod k) are balanced up to a discrepancy ≤ k, hence the
   cross-sectional rank counts are balanced up to ≤ k out of
   N — the O(k/N) term) gives the equality up to O(k/N).
   For the JOINT, the same argument applies to the pair
   (P_k[a], P_{k'}[b]) with a = c mod k, b = c mod k': under A1
   (independent rows for k ≠ k'; for k = k' the pair of values
   of ONE uniform permutation at two FIXED distinct indices is
   a uniform ordered DISTINCT pair) the seed-averaged pair law
   is a KNOWN explicit distribution — and its expectation over
   the position-weighted indicators equals the G₀ joint
   expectation at the level of first moments (the expectation
   of a product of indicators factorizes through the marginals
   when the two indicators live on DIFFERENT positions — which
   they do: a joint pair is two different plies). ∎
*The O(k/N) bound, concretely.* The worst cross-sectional rank
imbalance at any decision is ≤ k slots out of N (the phase
discrepancy of g + m_g (mod k), m_g = the move-ply index of the
decision) — for N = 1e6, k ≤ 64: ≤ 6.4e-5 of the corpus mass.
Negligible against the O(√(p/N)) sampling term by ~3 orders of
magnitude.

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
frequencies?** Generally NO, and here is why: the two picks act
on TWO DIFFERENT legal sets (the position changed between the
two plies) and the joint codes are functions of TWO DIFFERENT
features — the "rank inequality" constraint couples coordinates
that the observable does not see as the same coordinate. The
induced perturbation of F_uv is therefore a SECOND-ORDER
effect (it redistributes mass within the joint table without
moving the marginals). **But "generally second-order" is not a
theorem** — it depends on the specific feature geometry — so
the design does not rest on it: the T6 gate (§7) MEASURES the
G₁-vs-G₀ joint discrepancy at 1e4 scale (where G₀ is cheap to
run) with a threshold calibrated on G₀'s own noise, and the
fallback (a second independent counter) is pre-specified. This
is the only part of the equivalence that is TESTED rather than
PROVEN, and the document states that plainly.

### 6.6 Summary of what is proven vs tested
| claim | status |
|---|---|
| one-step conditional pick law = G₀'s (seed-averaged, A1) | **PROVEN** (Theorem 1, Lemma 1) |
| marginals: E_seed F^{G₁} = E₀ F up to O(k/N) ≤ 6.4e-5 | **PROVEN** (Theorem 2, Lemma 2) |
| joint EXPECTATIONS: same | **PROVEN** (Theorem 2, step 3) |
| sampling error = G₀-scale O(√(p/N)) | **PROVEN as an order statement** (§5-E2, §4.4) |
| joint VARIANCE structure (the same-width rank coupling, TV = 1/k) | **NOT proven** — measured by the T6 gate + pre-specified fallback (§6.5, §7) |
| A1 (the table ≈ uniform random permutations) | **assumed** — MT19937 quality + T3 bit-exact golden + T6 empirical re-check |

---

## 7. The empirical complement — the T6 gate (pre-registered)

The proof covers the expectations; the gate covers the residual
and A1. Design (to be executed at T6, BEFORE any 1e7 corpus):

1. **Micro-corpus scale: 1e4 games** (arrested at the model's
   ec). G₀ at 1e4 costs ~5e5 PRNG draws — seconds in Python —
   so G₀ is a FAITHFUL REFERENCE at this scale, not an
   approximation.
2. **Test 1 (the table, A1).** Every row P_k is a valid
   permutation (already in the T4 suite); the pick
   distribution: for each width k, the histogram of the chosen
   ranks over the micro-corpus vs uniform — chi-square.
3. **Test 2 (the marginals, E1-E2).** For every sub-variable:
   the G₁ cell frequencies vs the G₀ cell frequencies — a
   chi-square of the DISCREPANCY, with the critical threshold
   calibrated on G₀-vs-G₀ bootstraps (G₀'s own 1e4 Monte Carlo
   noise is the yardstick: G₁ must be no more different from
   G₀ than G₀ is from another G₀ run).
4. **Test 3 (the joints, E3b).** For a sample of su pairs
   (including same-width pairs — the risky case): the G₁-vs-G₀
   joint discrepancy chi-square, threshold as in Test 2. At
   1e4 the 1296×1296 table has df ≈ 1.7e6 — the chi-square is
   in the asymptotic regime (critical value ≈ 2√df + a few
   sigma).
5. **FAIL → the fallback.** A second independent counter
   (c'_g, a different phase, e.g. c'_g(0) = g + a large
   co-prime offset) for the "second pick stream": the same-
   width pair then draws from two independent rank walks;
   re-run the gate. If even the fallback fails (it should not),
   the design question re-opens.

---

## 8. Cost model (the "why not just keep G₀" answer)

| | G₀ | G₁ |
|---|---|---|
| PRNG calls per corpus (1e7) | ~5e8 | 2016 (setup, once) |
| hot loop | PRNG call per (game, ply) — the bottleneck; numba-ification = duplicate the MT implementation | pure integer array ops — the numba tier |
| measured precedent | Roberto's C generator: hours (5X2COR: days) | target: the memory-bandwidth limit of the position arrays |
| reproducibility | deterministic PRNG (reproducible) | deterministic table + counters (reproducible, AND the setup does not scale with N) |
| statistical content | the reference iid semantics | equivalent in E1-E3 (§5-§6), residual gated by §7 |

---

## 9. What the peer reviewer should check

1. **Theorem 1 (§6.3).** Is the "condition on the trajectory
   prefix; P_k uniform ⟹ the pick uniform" argument valid? (The
   subtle point: the prefix is a deterministic function of the
   table — conditioning on it and then averaging over the
   table: is there a circularity?) The intended answer: the
   seed-averaged expectation E_seed[· | prefix] is well defined
   because the prefix fixes c mod k (a number), and the
   remaining seed dependence enters only through P_k — Lemma 1
   applies to that residual. Check that this is legitimate.
2. **Theorem 2 step 3 (§6.4).** The exchange of the seed
   expectation and the corpus average, and the O(k/N) phase
   bound — is the discrepancy bound (≤ k out of N) correct for
   the m_g = move-ply-index offset?
3. **§6.5.** Is the "the same-width rank coupling is second-
   order at the CODE level" argument plausible? Is the TV = 1/k
   computation correct? Is the gate design (§7) the right
   instrument for it?
4. **A1.** Is "MT19937 permutations ≈ uniform random
   permutations" an acceptable assumption for this use (a 2016-
   draw setup, k ≤ 64 rows)?
5. **The scope discipline.** Does the document ever claim more
   than E1-E3 (i.e., does it ever pretend G₁'s corpus IS a G₀
   random corpus, rather than a balanced quadrature of the G₀
   expectation)?

> **Bottom line for Roberto.** The design is: the marginals are
> equivalent EXACTLY (proven), the joint expectations EXACTLY
> (proven), the sampling noise is G₀'s own noise (the corpus
> size does the work, §4.4), and the one structural residual
> (the same-width pair coupling) is small by construction,
> measured by a gate at 1e4 scale BEFORE the expensive build,
> with a pre-specified fallback. If the external review
> confirms §6 and approves §7, the T5 wave engine is built on
> G₁. If the review finds a hole in Theorem 2 step 3 or the
> §6.5 argument, we fix the design (the fallbacks are cheap)
> BEFORE writing the numba.
