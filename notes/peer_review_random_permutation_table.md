# Peer Review — The Random Permutation Table (ODP-9)

> **Review document:** `notes/random_permutation_table.md`
> **Reviewer:** Nia / DeepSeek V4 Pro (the requested second opinion on §6 and §7)
> **Date:** 2026-09-11
> **Verdict:** THE DESIGN PASSES — with one material correction needed and several clarifications required before the T5 build.

---

## Executive summary

The G₁ design is **sound in its expected domain of use** (the feature-characterization pipeline's synthetic random-play corpus). The core proof (§6) is **essentially correct** but contains two gaps that are fixable rather than fatal. The most serious issue is a **circularity in Theorem 1** that the document itself flags — I confirm the circularity exists and show how to dissolve it. The gate design (§7) is **adequate and honest**. The one "lie" in the document is the claim that joint expectations are exactly proven (Theorem 2 step 3): the proof sketch is **incomplete for the joint case**, and the real defense is the T6 gate — the document should state this more clearly.

---

## 1. The good parts (what the document gets right)

### 1.1 The problem analysis (§1-§2) is crisp and convincing

The sizing argument (§4.4) is **correct and well presented**: the √p law means sparse cells dominate the sampling error, and the open pattern set forces the corpus to scale. The table in §4.4 is correctly derived.

The cost model (§8) is honest and measured against Roberto's C precedent. The 2016-draw setup cost is indeed negligible. The argument that the hot loop becomes a pure integer kernel is correct and the vectorization claim is credible given the existing D-140 board kernel infrastructure.

### 1.2 Lemma 1 (§6.1) is trivially correct

A permutation of a uniform is uniform — this is the one completely clean step.

### 1.3 Lemma 2 (§6.2) is correct

The k consecutive counter values cover each residue exactly once. The proof (distinctness by the bound on the difference) is correct. The consequence ("the intra-game time-average over k consecutive real moves is exactly uniform") is correctly stated.

### 1.4 The honest-sentence discipline (§5, §6.5) is praiseworthy

The document is unusually honest for a technical design. It **does not** claim G₁ is "G₀ with draws replaced." It clearly states that G₁'s corpus is deterministic per seed. It **explicitly** identifies the structural covariance term (§6.5) as unproven and gates it empirically. This honesty is the strongest argument in the document's favor.

### 1.5 The fallback is pre-specified (§7)

The second-counter fallback is specified before any empirical test. This is good experimental practice and protects against failure.

### 1.6 The implementation is faithful

I verified `hlp_random_play.py` (D-162) against the document:
- The Fisher-Yates table build matches §3 exactly (2016 draws over k=1..64).
- The `pick_move` logic (`table[k][counter % k]`) matches §3.
- The pass-non-consumption rule matches §3.
- The slot phase initialization `counter0 = g` matches §4.3.
- The test suite (`test_hlp_random_play.py`, 12 tests) is well-designed: the identity-table regime enables hand-counted verification, the `_replay` function independently cross-validates the trajectories.

---

## 2. The problems (what needs fixing)

### 2.1 🔴 CRITICAL: Circularity in Theorem 1 (§6.3)

**The document's own flag (item 1, §9):**
> "The subtle point: the prefix is a deterministic function of the table — conditioning on it and then averaging over the table: is there a circularity?"

**Yes — there is a circularity in the stated proof.**

The proof says: "condition on the game's trajectory prefix up to a ply (this fixes the legal set L, the width k, and the counter value c). Under A1, the G₁ pick at this ply, in expectation over the seed, is UNIFORM over L."

**The problem:** The trajectory prefix is a **deterministic function of the table** (the table produced it). When we condition on the prefix, we condition on an event that is functionally dependent on P_k. The "remaining seed dependence enters only through P_k" — but **conditioning on the prefix restricts the admissible realizations of P_k**. The subset of permutations compatible with a given prefix is **not** the set of ALL permutations of {0..k-1} — it is the subset that produced that specific prefix.

**Does this actually break the conclusion? No — but the stated proof is invalid as written.** The correct argument needs a different approach:

**Corrected proof (exchange the order):**

1. The G₁ pick at ply (g, t) is `pick = P_k[c mod k]` where c depends on the trajectory prefix.
2. Take the **unconditional** expectation over the seed. Under A1, P_k is a uniform random permutation **independent of the trajectory** (this is the crucial point: the trajectory is a function of the table, not independent of it — but we are not conditioning, we are computing the unconditional joint distribution of (trajectory, pick)).
3. By the **tower property**, E_seed[I(g,t)] = E_seed[ E_seed[I(g,t) | P] ] where P is the full table (all 64 rows).
4. **Condition on the ENTIRE table P** (not the prefix). Given the full table, the trajectory is **deterministic** (the prefix, the legal set L, the width k, the counter c are all deterministic functions of P and the initial state). The pick at this ply is P_k[c mod k] — a **deterministic** value under the given table.
5. **But we don't need to extract the law from this deterministic value. Instead, compute the unconditional expectation directly:** For a fixed position with a fixed legal set L (|L| = k) and a fixed counter c, what is P_seed(the G₁ pick at this ply = some square in L)? **This is P(P_k[c mod k] = r) averaged over the seed, WITHOUT conditioning on the prefix.**
6. Under A1, P_k is a uniform random permutation, and c is a deterministic function of the counter walk and the table. **BUT c IS NOT INDEPENDENT OF P_k.** This is the core issue.

**The actual rescue** comes from the structure of the G₁ construction:

- For a given ply, the counter value c depends on the **entire** table P, not just P_k — the trajectory prefix is shaped by decisions at many different widths. Under A1 (the rows are independent), the **marginal distribution of P_k is uniform over all permutations of {0..k-1}, unconditional on the trajectory prefix.**
- When we then look at P_k[c mod k], where c is a function of the ENTIRE table (including P_k observed through previous decisions at the same width), there IS dependence. **However, this dependence is exactly the E3b structural covariance term that §6.5 treats as unproven.**

**Bottom line:** Theorem 1 is **not provable as stated** (the conditional-kernel claim) without additional independence assumptions that G₁ does not satisfy. The CORRECT statement is:

> **Theorem 1 (corrected).** Under A1, at ANY ply, the **marginal** distribution of the G₁ pick, averaged over the seed **without conditioning on the trajectory prefix**, is uniform over L. Equality of the **conditional** kernel (given the prefix) does NOT hold — the E3b coupling is the deviation.

**Fix:** Replace Theorem 1 in the document with this corrected statement. The Theorem 2 (marginals) rescues the claim because E_seed[I(g,t)] only needs the **unconditional** per-ply expectation, not the conditional kernel. The document's §6.3 remark already hints at this ("it does NOT say the G₁ trajectory is a G₀-sampled trajectory") — the theorem statement just overclaims.

### 2.2 🟡 MATERIAL: Theorem 2 step 3 — the joint proof is incomplete

**Step 3 of Theorem 2 (§6.4)** claims that the joint expectations also match exactly. The document says:

> "For k = k' the pair of values of ONE uniform permutation at two FIXED distinct indices is a uniform ordered DISTINCT pair"

This is correct for the pair-law of a single permutation row. **But this is the pair-law of two ranks, not of two observable CODES.** The document correctly notes that the two picks act on DIFFERENT legal sets (the position changed between the two plies). **However, the proof does not account for the dependence between the legal sets and the permutation row.**

Specifically: At ply t, the pick at width k produces rank r_t = P_k[c_t mod k]. At ply t' > t, the legal set L_{t'} depends on the trajectory, which depends on r_t and all previous picks. **The counter values c_t and c_{t'} are dependent through the shared counter walk, and the legal set L_{t'} is causally downstream of the pick at ply t.** This creates a **second-order dependence** in the joint law that is not resolved by the "the pair-law is uniform distinct" argument alone.

**The honest assessment:** The joint-expectation claim in Theorem 2 is **not fully proven**. The defense is the T6 gate, and the document should state this clearly rather than lumping the joint expectations under "PROVEN" in the summary table (§6.6).

**Fix:** Move the joint-expectation row in the §6.6 table from "PROVEN" to "PARTLY PROVEN — measured by the T6 gate, with the same pre-specified fallback as E3b." The row currently says "PROVEN (Theorem 2, step 3)" — this overstates the case.

### 2.3 🟢 MINOR: The slot-phase O(k/N) bound needs a qualification

The phase-discrepancy bound (≤ k out of N, §6.4) is computed as:

> "the cross-sectional rank counts are balanced up to ≤ k out of N — the O(k/N) term"

This bound assumes that the **move-ply index m_g** (the number of real moves played by game g) is drawn from a distribution that does not exacerbate the imbalance. Lemma 2 says: over k consecutive values, each residue appears exactly once. **But the set of values {g + m_g : g = 0..N-1} is NOT a set of k consecutive integers — it is a set of N values spaced by 1 in g, but with DIFFERENT offsets m_g.**

The question: what is the maximum possible deviation of the empirical distribution of { (g + m_g) mod k } from uniform?

**Answer:** It can be as bad as **max_g m_g - min_g m_g** slots, which is bounded by the total number of real moves per game, which is bounded by 64. At N = 1e6, this is ≤ 64/1e6 = 6.4e-5 of the corpus mass. **The estimate is correct, but the derivation in the document is too quick.** The cross-sectional imbalance at a specific decision point is ≤ max_g m_g (the maximum number of real moves any game has played by that decision point), not ≤ k. But both are ≤ 64, so the bound is the same.

**Fix:** Clarify the derivation: "the cross-sectional rank imbalance at any decision is ≤ max_g m_g (the maximum number of real moves played by a single game before this decision), which is ≤ 64 — hence ≤ 64/N."

### 2.4 🟢 MINOR: The TV = 1/k computation is correct but the "second-order" claim needs nuance

§6.5: "The total-variation distance between the two pair laws is 1/k (large at small k: 1/2 at k = 2)."

**This is correct.** Under G₀, the pair (r, r') is a uniform ordered pair with replacement: P(r = r') = 1/k. Under G₁ (same k), the pair is uniform over **distinct** ordered pairs: P(r = r') = 0. The TV is 1/k.

**However**, the claim "generally NO — and here is why: the two picks act on TWO DIFFERENT legal sets" is **not an argument about the pair-law of ranks** — it's an argument about the observable codes. The two-step mapping (ranks → legal sets → codes) does dilute the 1/k effect, but **the degree of dilution depends on the specific feature geometry.** A feature that collapses distinct legal squares to the same configuration code (e.g., an edge pattern that doesn't distinguish the four quadrants of the board boundary) could **amplify** the effect, not dilute it.

**The correct statement:** "The rank-level coupling has TV = 1/k. Its propagation to the observable feature-code level depends on the feature's geometric mapping and is generally attenuating but cannot be bounded in general — hence the empirical gate."

---

## 3. The gate design (§7) — assessment

### 3.1 The design is adequate

- **Scale (1e4):** Reasonable. G₀ at 1e4 costs ~5e5 PRNG draws — truly negligible.
- **Test 1 (the table):** Trivial and necessary.
- **Test 2 (the marginals):** Well designed. The use of G₀-vs-G₀ bootstraps as the yardstick is the right calibration.
- **Test 3 (the joints):** Adequate. The chi-square on the 1296 × 1296 table at 1e4 poses a sparse-cell challenge (1e4 samples over ~1.7e6 cells → average cell frequency ~0.006), but the merged-tail technique and the asymptotic chi-square regime handle this. **A more powerful test would be to focus on same-width pairs specifically** (the risky case) and use a more sensitive metric (e.g., the TV or the KL divergence on the joint table of the TWO features).
- **The fallback:** The second independent counter is pre-specified and mechanically correct. At k = k', the two counters with a co-prime offset produce independent rank draws (the two permutation values are at different indices, and unconditionally these are uniform draws — distinctness is no longer guaranteed, restoring the G₀ pair-law).

### 3.2 Suggestions for the gate (optional, not blockers)

1. **Add a same-width-specific test.** Extract only the pairs where k = k' (the risky case) and apply a TV test with a G₀-vs-G₀ bootstrap threshold. This is more sensitive than the chi-square on the full joint table.
2. **Add a continuity-of-counter test.** Vary the counter0 phases and verify that the statistics are continuous (no phase-locked artifact). A set of 3–5 different phase initializations should produce frequency tables within G₀ noise.
3. **Add a small-k focus.** At k = 2, the TV = 1/2 is the largest effect. Verify specifically that the observable codes at small-k decisions (early game, corners) are within G₀ noise.

---

## 4. Assumption A1 — assessment

The document assumes "MT19937 permutations ≈ uniform random permutations." This is **acceptable** for the specific use (2016 draws, k ≤ 64):

- MT19937 is 623-dimensionally equidistributed — the 2016 consecutive draws fall well within one full period (2^19937 − 1).
- The Fisher-Yates shuffle is a **fully uniform** mapping from the PRNG's rank draws to permutations — it does not introduce bias (the algorithm is exact, not approximate).
- The T3 golden suite pins the PRNG bit-exact against the C build.
- Empirically, the chi-square test on the pick distribution (gate Test 1) will catch any gross deviation.

**Verdict:** A1 holds to the standard required by this application. k ≤ 64 means the permutation space is log₂(64!) ≈ 296 bits — the MT19937's output quality (623 dimensions × 64 bits = 39872 bits of entropy per period) is vastly sufficient.

---

## 5. Scope discipline (§9)

The document asks: "Does the document ever claim more than E1-E3?"

**Answer: Yes — twice.** As noted above, (1) the conditional-kernel claim in Theorem 1 is an overstatement, and (2) the joint-expectation claim in Theorem 2 is presented as proven when it is not fully proven. Both are fixable by rewording.

The rest of the document maintains excellent scope discipline. It does not claim G₁ IS G₀. It clearly states the E3b residual as unproven. The fallback is pre-specified. The summary table (§6.6) is mostly honest — the two rows that need adjustment are fixable.

---

## 6. Checklist of required fixes

| # | Severity | What | Where |
|---|----------|------|-------|
| 1 | 🔴 Critical | Theorem 1 is unprovable as stated. Replace with the unconditional-expectation statement. | §6.3 |
| 2 | 🟡 Material | Joint-expectation claim in Theorem 2 step 3 is incomplete. Reclassify in §6.6 table. | §6.4, §6.6 |
| 3 | 🟢 Minor | The O(k/N) bound derivation needs the m_g qualification. | §6.4 (the paragraph starting with "the cross-sectional rank counts") |
| 4 | 🟢 Minor | The "second-order at the CODE level" argument needs nuance about feature geometry. | §6.5 |
| 5 | 🟢 Minor | Add a same-width-specific bootstrapped test to the T6 gate. | §7 (Test 3) |

---

## 7. Verdict

**The design passes.** G₁ is a valid approach for extracting the statistical properties of configuration frequencies from the feature set. The expectation-level equivalence for marginals is **correct** (Theorem 2 for marginals, not joints). The empirical gate is honest and adequate. The fallback is pre-specified. The cost argument is compelling.

The document overclaims on two points (the conditional kernel and the joint expectations), but these overclaims are **fixable by rewording — the design does not depend on them.** In both cases, the empirical gate is the actual defense, and the document already states this (the honest sentence in §5: "the only unproven residual ... is measured by a gate").

**Recommendation: BUILD ON G₁, after fixing the two overclaims in §6.3 and §6.6, and adding the same-width-specific test to the T6 gate.**

The cost of getting this wrong is low: the T6 gate at 1e4 scale is cheap (seconds), the fallback (second counter) is cheap to implement, and the design question re-opens only if both G₁ AND the fallback fail the gate — an event the document considers improbable, and with good reason.

---

## References (for the reviewer's own verification)

- Mersenne Twister: Matsumoto, M. and Nishimura, T. (1998). "Mersenne Twister: A 623-dimensionally equidistributed uniform pseudo-random number generator." ACM Trans. Model. Comput. Simul. 8(1):3-30.
- Fisher-Yates shuffle: Durstenfeld, R. (1964). "Algorithm 235: Random permutation." Comm. ACM 7(7):420.
- Balanced designs and quadrature: Owen, A.B. (1997). "Monte Carlo variance of scrambled net quadrature." SIAM J. Numer. Anal. 34(5):1884-1910. (The G₁ construction is a form of randomized balanced quadrature — the slot phases are a Latin-hypercube over the counter, the table is the randomized permutation.)