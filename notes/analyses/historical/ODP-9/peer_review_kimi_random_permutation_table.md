# Independent Peer Review — The Random Permutation Table (ODP-9, v2)

> **Document under review:** `notes/random_permutation_table.md`
> (v2, 2026-09-11 — the revision after the first review).
> **First review:** `notes/peer_review_random_permutation_table.md`
> (DeepSeek V4 Pro, v1 + v2 pass).
> **This review:** an INDEPENDENT second voice (Kimi K3). I read the
> v2 document and the implementation (`src/reversi/lm/hlp_random_play.py`,
> `src/reversi/tools/prng.py`) BEFORE the first review, then read the
> first review to check for capture. Where I agree with it I say so and
> re-derive; where I add something it is my own.
> **Date:** 2026-09-11.
> **Verdict: PASS WITH REQUIRED AMENDMENTS** — the design is sound and
> the v2 scope discipline is correct, but the document as written
> **under-corrects on three points that are load-bearing for the claim
> "G₁ gives the same results as a G₀ population."** Two of them the
> first reviewer also caught; one (the arrest-arbitrariness of the
> corpus marginal) neither the document nor the first review states
> plainly. All three are fixable in the gate design, not in the math.

---

## 0. The question, restated without the document's framing

The thesis put to me: **G₁ (a seeded permutation table + a per-game
counter walk, no PRNG in the loop) is a solid way to extract the
statistical frequency characteristics of the patterns the model
selects, and this analysis gives the same results as an analysis on a
G₀-generated population.**

I evaluate that thesis, not the weaker one the document sometimes
retreats to ("G₁ is random-play-like within measurement precision").
The two are not the same, and the gap between them is where my three
required amendments live.

---

## 1. What is actually proven — an independent re-derivation

I re-proved every claim before trusting the document. Summary; details
in §4.

### 1.1 Lemma 1 (permutation of a uniform is uniform) — CORRECT, trivial
For a bijection `P` and uniform `X`, `Pr(P[X]=y) = Pr(X=P⁻¹[y]) = 1/k`.
Verified. No issue.

### 1.2 Lemma 2 (the counter covers every residue once per k steps) — CORRECT
`a+i mod k` for `i=0..k-1` are distinct. Verified. The balanced-design
consequence (over any k consecutive real moves, the width-k pick visits
each rank exactly once) is correct and is the *only* place G₁ is
strictly *better* than G₀ (zero fluctuation vs G₀'s `±O(1/√k)`).

### 1.3 Theorem 1 v2 (the one-step ORACLE equivalence) — CORRECT, and the
###     right level
Given a FIXED position `p` with legal set `L` (`|L|=k`) and a FIXED
counter `c`, both supplied from outside, the pick is
`square = l_( P_k[c mod k] )`. Since `c mod k` is a fixed residue and
`P_k ~ Uniform(S_k)` (Assumption A1), Lemma 1 gives `P_k[c mod k]`
uniform on `{0..k-1}`, and the canonical order (a bijection) carries
this to uniform over `L`. **This is exactly G₀'s one-step draw.**
I checked this against `pick_move` in `hlp_random_play.py` (L187-208):
the implementation is `rank = table[k][counter % k]`, then the rank-th
set bit. The oracle statement is the faithful semantics of that code.
The first reviewer's endorsement of the oracle framing is correct, and
their retraction of their own unconditional-marginal proposal is
correct — I arrive at the same conclusion independently (§4.3).

### 1.4 The phase combinatorics (≤ 64/N) — CORRECT, purely combinatorial
The slot phases `(g + m_g) mod k` across N slots are balanced up to the
spread of `m_g` (real-move counts), bounded by 64 (a game has ≤ 64 real
moves). At N = 1e6 that is ≤ 6.4e-5 of corpus mass. This is a statement
about slot phases only, not about the table, and it is sound. The v2's
adoption of the sharper `m_g`-spread bound is correct.

**What these four results establish:** the *local* rule of G₁ is
semantically identical to G₀'s, and the cross-sectional slot phases are
balanced to a provably negligible tolerance. This is real, and it is
all that is proven. Everything corpus-level is, correctly, gated.

---

## 2. The reclassification is honest — and it is the whole ballgame

The v2's central admission (§5, §6.4, §6.6): **the corpus-level equality
`E_seed[F^{G₁}] = E₀[F]` for marginals AND joints is NOT proven; it is
measured by the T6 gate.** The v1 called both PROVEN; v2 reclassifies
both as GATED. This is the single most important change in v2, and it
is correct.

I want to be impietoso about why it matters, because the document
states it but does not, in my judgment, fully internalize its weight.

**The oracle theorem does not lift to the trajectory ensemble, and the
document's own "plausibility argument" (§6.4) does not close the gap.**
The first reviewer's §3.3 already shows the attempted Markov-chain
closure collapses into the same circularity (conditioning on
`(position_t, counter_t)` is conditioning on the table, because they are
functions of the table). I confirm that collapse independently:

> Let `(P_t, c_t)` be the position and counter at ply `t`, both
> deterministic functions of the table `P`. The oracle gives
> `E_seed[f(P_{t+1}) | P_t = p, c_t = c] = E_{G₀}[f(·) | p]` for FIXED
> `(p, c)`. To get the marginal `E_seed[f(P_{t+1})]` one integrates
> against the seed-distribution of `(P_t, c_t)`. But that distribution
> is induced by `P`, and the inner expectation conditions on a value of
> `(P_t, c_t)` that *selects* a subset of tables. The selection is
> exactly the entry-consumption set `R` of §6.3. So the two-step
> Chapman–Kolmogorov product is NOT the G₀ product. The gap is real and
> not currently bounded in closed form.

So the document is right to gate it. **But this means the thesis as the
user posed it — "G₁ gives the same results as G₀" — is, as of this
document, an EMPIRICAL CONJECTURE with a pre-registered test, not a
theorem.** The v2 says this. The user should hear it without the softening.

---

## 3. REQUIRED AMENDMENT 1 — the corpus marginal is not one number

This is the point neither the document nor the first review states
plainly, and it is the one most likely to produce a wrong downstream
conclusion if left implicit.

**The "corpus marginal frequency of a feature configuration" is not a
single well-defined quantity until you specify the ply-arrest
distribution.** The corpus keeps *every ply of every arrested game*. A
game arrested at `ec = 20` contributes a variable number of positions
(the document says ~40–60 plies). The marginal frequency of a
configuration is therefore an average over plies, weighted by the
(random) number of plies each game contributes and by *which* plies
(those with `ec` between the start and the target).

Two consequences:

1. **G₀ and G₁ must be compared at the SAME ply-arrest distribution, or
   the marginal is comparing two different mixtures.** The gate (Test 2)
   says "G₁ cell frequencies vs G₀ cell frequencies," but does not state
   that both corpora must use the identical arrest rule AND that the
   comparison is of the *pooled* per-ply histogram, not the per-game
   histogram. If G₁'s path coupling shifts the *length* distribution of
   arrested games (plausible: the entry-consumption effect is strongest
   at small `k`, which concentrates at specific game phases), then even
   a per-ply-uniform G₁ could yield a different pooled marginal than G₀
   purely through a different mixture weights. **The gate must stratify
   by ply-index (equivalently by ec) and compare per-stratum, not only
   pooled.** Otherwise a real per-stratum bias can be masked by
   cancellation across strata, or a pure length-distribution difference
   can masquerade as a marginal bias.

2. **The "mele con mele" window is a distribution, not a point.** The
   regab DB was collected at a target ec, but each DB record is one
   position at that ec, whereas the corpus is a *trajectory* up to that
   ec. If the downstream adherence statistic (chi-square / KL / TV)
   compares the DB (one position per game, AT the ec) against the corpus
   (MANY positions per game, up to and including the ec), the two
   populations differ structurally even under perfect G₀. This is a
   design question for I-017, not for G₁ — but the ODP-9 document is
   where the corpus semantics are fixed, and it should state the
   sampling unit explicitly.

**Action (gate design, not math):** T6 Test 2 must (a) pin the arrest
rule identically for G₀ and G₁; (b) compare per-stratum (per ec or per
ply-index) marginals, with the pooled marginal reported as a secondary
aggregate; (c) state the sampling unit (per-ply vs per-game) that the
I-017 adherence statistic will actually consume. This is cheap and
removes a whole class of false pass/fail.

---

## 4. The points where I concur with the first review (re-derived)

So that this review is not a rubber stamp of the first, here is what I
checked independently and confirm.

### 4.1 The v1 circularity is real; the v2 entry-consumption mechanism is exact
At a width-k ply with counter residue `m = c mod k`, let `R` be the set
of residues consumed by earlier same-width picks. If `m ∈ R`, the pick
is deterministic (the reused value). If `m ∉ R`, `P_k[m]` is uniform
over the `k − |R|` unconsumed values (the consumed entries took `|R|`
distinct values, and the remaining entries of a uniform permutation are
a uniform permutation of the remaining values). **The true conditional
kernel is "uniform over unconsumed entries, deterministic on reuse."**
Confirmed — this is exactly the mechanism, and the v1 proof ("the prefix
fixes `c mod k`; `P_k` uniform; Lemma 1") is invalid because the prefix
restricts the admissible `P_k`.

### 4.2 The author's rejection of the unconditional-marginal fix is correct
The first reviewer proposed replacing Theorem 1 with an unconditional
marginal uniformity, then retracted it. The retraction is right, for the
reason the author gives: (i) at fixed ply index `t`, `L_t` is itself a
random variable, so "uniform over L" is ill-defined without specifying
which `L`; (ii) `c` is table-dependent, and the marginal uniformity of
`P_k` does NOT imply the uniformity of `P_k[c mod k]` for a
table-dependent index. The `k=2` counterexample (`I = 1{P₂=[1,0]}` makes
`P₂[I]` a point mass) is valid and decisive. The oracle statement is the
correct semantic level. **I confirm both the circularity and the
rejection.**

### 4.3 A1 is acceptable for this use
"MT19937 Fisher–Yates rows ≈ independent uniform permutations" for a
2016-draw setup with `k ≤ 64` is a standard, low-risk assumption. I
verified in `prng.py` that the port is the 64-bit MT19937 with the
correct twist/temper and that `random_choice_from_finite_set` uses the
`[0,1)` double path (`get_double_in_c0_o1`) with floor — the same
construction as the C reference (T3 pins it bit-exact). One caveat I add:
`random_choice_from_finite_set(k)` uses a *single* double and floors —
this is a **modulo-free but flooring-based** reduction. For `k ≤ 64` and
a 53-bit mantissa double, the induced non-uniformity is `≤ k·2⁻⁵³ ≈
7e-15`, negligible. A1 stands. (Worth one line in the doc: the reduction
is floor-of-double, not bitmask-rejection, and the bias is bounded at
2⁻⁵³ scale.)

### 4.4 The fallback does NOT restore the G₀ pair law — I confirm, and sharpen
The first reviewer's §3.1 is correct: the second independent counter
removes the *counter-mediated* coupling but NOT the permutation
distinctness (`P_k[a] ≠ P_k[b]` for `a ≠ b`), so same-width pairs remain
uniform-DISTINCT (TV = 1/k from G₀'s allows-equality law) even after the
fallback. I sharpen it: **if the same-width tests (4–5) fail while
cross-width tests pass, the fallback will not rescue the design**,
because the residual is then the shared-row distinctness, which no
number of independent counters fixes (they all read the same row `P_k`).
The only true fix for that failure mode is a per-ply fresh PRNG draw for
the second pick — i.e., a partial retreat toward G₀ at exactly the
same-width plies. The document's §7.8 should state this boundary
explicitly, so a gate failure is correctly attributed (counter-coupling
vs distinctness) before reaching for the fallback.

---

## 5. REQUIRED AMENDMENT 2 — test 3's sparse-cell power at 1e4

The first reviewer flagged this (their §3.2); I independently reach the
same conclusion and make it a *required* amendment because it changes
which test is load-bearing.

At 1e4 games over a `1296 × 1296` joint table (df ≈ 1.7e6), the average
cell occupancy is ~6e-3. The asymptotic chi-square is not merely
"stretched" — with mean expected frequency far below 1, the merged-tail
correction collapses the table into a handful of effective cells, and
**Test 3 loses almost all power to detect a localized same-width
coupling.** The document's parenthetical ("the chi-square is in the
asymptotic regime, critical ≈ 2√df + a few sigma") is optimistic at this
sparsity.

**Action:** designate **Tests 4 (same-width focus) and 5 (small-k
focus) as the PRIMARY joint-gate instruments**, using TV and KL (which
do not require the sparsity correction) on the *restricted* tables where
the risk actually lives, and demote Test 3 to a coarse sanity check. At
1e4, only the focused tests have the power to see a `TV = 1/k` effect at
small `k`. The document currently presents Test 3 as a co-equal joint
test; that should be corrected.

---

## 6. REQUIRED AMENDMENT 3 — the "random-play-like within precision"
###     criterion needs a number, not a metaphor

The design requirement (§5) is "the ideal population random-play-like to
within the MEASUREMENT PRECISION," operationalized as "G₁ no more
different from G₀ than G₀ is from another G₀ run." This is the right
*qualitative* yardstick (the first reviewer endorses it; I agree it is
the correct calibration concept). But as specified it is **not yet a
test**: "no more different" needs a metric, a multiple-comparison
discipline, and a power statement.

Concretely:

1. **Metric.** For each sub-variable, define the discrepancy
   `D = TV(F^{G₁}, F^{G₀})` (or the chi-square statistic). The gate
   compares `D` against the *distribution* of `D₀ = TV(F^{G₀}, F^{G₀'})`
   over G₀-vs-G₀ bootstrap replicate pairs. Pass if `D` is below, say,
   the 95th percentile of the `D₀` distribution. The document says
   "threshold calibrated on G₀-vs-G₀ bootstraps" — good — but does not
   state the percentile or the metric per test. Pin them.

2. **Multiple comparisons.** With ~1e6 cells (joint) and several
   sub-variables, a per-cell 5% test yields ~5e4 false positives under
   the null. The gate must control a *family-wise* or *false-discovery*
   rate across cells/sub-variables (e.g., a Bonferroni or BH correction
   on the per-cell p-values), or it will "detect" G₀ noise as a G₁ bias.
   This is not optional at this table size.

3. **Power.** State the minimum detectable effect of each test at 1e4.
   The whole point of gating at 1e4 is that G₀ is cheap there; but the
   gate is only meaningful if it is *powered* to detect a bias that
   would matter at 1e7. Since G₀'s per-cell noise scales as `1/√N`, a
   bias `δ` that is invisible at 1e4 noise `~1e-2` but comparable to 1e7
   noise `~1e-3` would slip through. The document asserts "if the gate
   passes, the bias at 1e7 is a fortiori subdominant" — this is **only
   true if the bias does not itself grow with N or shrink slower than
   the noise.** The entry-consumption bias is a *systematic* (it does not
   average down with N the way Monte Carlo noise does), so a
   sub-`1e-2`-at-1e4 systematic bias could be *above* the `1e-3` noise
   floor at 1e7. **The gate must therefore bound the bias in absolute
   terms, not relative to the 1e4 noise.** Concretely: require the
   measured `D` to be below an absolute `δ*` chosen so that `δ*` is
   negligible against the 1e7 noise (`~1e-3`), and power the 1e4 gate to
   detect `δ*` (which may require the focused tests of Amendment 2, since
   the pooled test cannot see a `1e-3` effect at 1e4).

This amendment is the difference between "we ran a test that passed" and
"we bounded the bias." Given that the corpus-level claim is gated (not
proven), the gate must be a real bound.

---

## 7. What is genuinely strong about this design

Impietoso cuts both ways. To be fair to the design:

- **The honest sentence (§5) is correct and rare.** "G₀ produces a
  distribution over corpora; G₁ produces ONE deterministic corpus per
  seed" — this is the crux, stated plainly. Many designs hide it.
- **The scope discipline (§6.6) is now exact.** Every claim is tagged
  PROVEN / GATED / ASSUMED, and the tags match the math. I verified each
  row against §6. This is the document's greatest strength and the main
  reason it passes.
- **The slot-phase necessity (§4.3) is correctly identified as
  load-bearing, not an optimization.** Without `c_g(0) = g` the corpus
  degenerates to one trajectory. Verified against the code: `counter0`
  is the per-game phase, and a pass consumes no counter step
  (`pick_move` returns `counter` unchanged on `k=0`, L201). Correct.
- **The cost argument (§4, §8) is sound and is the real justification.**
  Moving 2016 PRNG draws out of `~5e8` call sites and into setup is a
  legitimate and large win, and the maintenance hazard of a duplicated
  numba MT19937 is real. G₁ is justified on engineering grounds even
  before the statistics.

---

## 8. Answers to the document's §9 questions (the explicit asks)

1. **Oracle Theorem 1 — is it the right level?** Yes (§1.3). Circularity
   analysis correct (§4.1). Rejection of the unconditional-marginal
   correct (§4.2).
2. **Reclassification correct?** Yes (§2). Plausibility argument sound
   as plausibility, NOT as proof — and the Markov-chain closure does
   not work (§2, first reviewer's §3.3 confirmed). **No, I did not find
   a re-proof**; I do not believe a cheap one exists, because the
   counter walk across widths is not a standard `(t,m,s)`-net and the
   coupling is genuinely trajectory-shaped. The gate is the right call.
3. **Do the I-017 statistics tolerate the gated deviation?** Only if the
   gate bounds the bias in *absolute* terms (Amendment 3.3) — the
   relative-to-1e4-noise framing is insufficient because the bias is
   systematic, not Monte Carlo. With that fix, yes: SU and MI are smooth
   in the frequency estimates (delta method), so a bounded `~1e-3`
   frequency perturbation propagates to `~1e-3` in H/MI, below any
   practical threshold. Without that fix, the answer is "unknown."
4. **A1 acceptable?** Yes (§4.3), with the floor-of-double note.
5. **Gate adequate?** With the three amendments: the arrest-stratified
   marginal (Amendment 1), the focused-tests-primary re-ordering
   (Amendment 2), and the absolute-bias bound + multiple-comparison
   control (Amendment 3). As written, the gate is under-specified on
   exactly the points that determine whether it bounds anything.
6. **Scope discipline?** Yes — this is the document's best feature. The
   one place it slips is the "a fortiori subdominant" sentence in §6.4,
   which over-claims the extrapolation (Amendment 3.3).

---

## 9. Verdict

**PASS WITH REQUIRED AMENDMENTS.**

The core thesis — G₁ is a valid, orders-of-magnitude-cheaper replacement
for G₀ whose *local* semantics are provably identical and whose
*corpus-level* equivalence is empirically gated — **survives hostile
review.** The v2's honesty about what is proven versus gated is
exemplary and is the reason the design is defensible.

But the thesis as the user posed it — "G₁ gives the same results as a
G₀ population" — is currently a **pre-registered empirical claim with an
under-specified test**, not an established fact. The three amendments
are what turns the gate from a ritual into a bound:

- **A1 (§3):** stratify the marginal comparison by ply/ec and pin the
  sampling unit.
- **A2 (§5):** make Tests 4–5 (TV/KL, focused) the primary joint gate;
  demote the pooled chi-square Test 3.
- **A3 (§6):** bound the bias in absolute terms against the *1e7* noise
  floor, control the family-wise error across cells, and state each
  test's power.

With these, the gate is a real verification and the T5 wave engine can
be built on G₁ with confidence. Without them, the gate can pass while a
systematic `~1e-3`-scale bias rides through to the 1e7 corpus — which is
precisely the regime the corpus is being built for.

I endorse the first reviewer's "PASS" in substance, and I note that my
Amendment 3 (the absolute-bias bound) is the one place I go beyond both
the document and that review: the "a fortiori subdominant" extrapolation
is the single weakest sentence in an otherwise rigorous document, and it
should be struck or justified.

---

## Appendix — where I checked the code

- `hlp_random_play.py` L187-208 (`pick_move`): confirms the oracle
  semantics (`table[k][counter % k]` → rank-th set bit), the
  pass-consumes-no-counter contract, and the per-game `counter0` phase.
- `hlp_random_play.py` L160-184 (`build_pick_table`): confirms Fisher–Yates
  over seeded MT19937, 2016 draws total, read-only shared table.
- `hlp_random_play.py` L129-140 (`ec_of`): confirms the arrest measure is
  `64 − popcount(occupied)`, i.e. a *board-state* function — which is why
  the arrest-arbitrariness of Amendment 1 is a real concern (the arrest
  couples the corpus composition to the trajectory, and G₁'s path
  coupling could in principle shift the arrested-length distribution).
- `prng.py` L256-275 (`random_choice_from_finite_set`): confirms the
  floor-of-double reduction (A1 note, §4.3).
