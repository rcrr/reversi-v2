# hlp_gate.py — the T6 design gate

State: BUILT (D-172) · suite 14/0/0 (13 default + 1
`GATE_SMOKE=1` gate smoke) · 1e6 design gate in flight.

## Purpose

The T6 design gate of the I-017 pipeline (the v4 doc
section 7 — `notes/random_permutation_table.md`, FROZEN):
the pre-registered empirical certification that the G1
(ODP-9 table pick) corpus is statistically indistinguishable
from the G0 (the uniform per-move PRNG draw) reference at
the 1e6 scale, with the table-aware dual criterion and the
family-wise control. The corpus is the I-017 FEATURES step:
the campaign config (the rlm JSON, json5 + `LMConfig`)
supplies the sub-variables (the FeatureSet — the 12 A2050
features) and the model's ec (the arrest rule, IDENTICAL
for G0 and G1 — the doc Amendment 1a).

## Engines (both LOCKSTEP waves, the T5 `hlp_wave`
semantics)

Step = one real move per live lane; the pass FOLDS into
the step (the pass lane's move is picked from the swapped
side's legal set); the double pass kills the lane (the
PA-swap coast, the boundary respawn).

- **G1**: the ODP-9 table pick (`build_pick_table(seed)`,
  the slot phase pin `counter0 = slot`). No PRNG in the
  loop.
- **G0**: the uniform reference — a single GLOBAL MT19937
  (the project's golden-pinned PRNG, the "one seed for all"
  pin, the numba batch-draw port of `tools/prng.py`), one
  draw per (lane, step) in lane order: the real-move lanes
  pick the (draw % k)-th set bit (the modulo bias <
  k/2^64, 12 orders below the noise floor); the pass/dead
  lanes' draws are consumed (unused).

## Tests (v4 section 7)

1. the table A1 re-check (the per-width rank histogram) +
   the per-width PHASE-OCCUPANCY SCAN: the v4 phase
   `(g + m_g) mod k` = `counter mod k` (the rank argument —
   the doc L545 "width-k decision m_g = 0 across slots —
   phases = g mod k"), the chi-square k-1 df, Bonferroni
   over the 64 widths.
2. the ARREST-STRATIFIED marginals (PRIMARY): per
   sub-variable, per ec level (60 down to the arrest ec),
   the TV of the G1-vs-G0 position codes; the pass
   frequencies (the per-game ply-count distribution); the
   pooled full-trajectory marginal (SECONDARY).
3. the FOCUSED joints (PRIMARY): per sampled SU pair (the
   feature pairs with the per-instance cell product
   `n_conf_A x n_conf_B <= 1e6`), the joint codes at the
   SAME position (the SU unit), stratified by the arrest
   ply width k (strata 1..8, 9+): the per-stratum TV + KL.
4. the small-k dedicated pass (the k <= 4 strata of test 3).
5. the pooled joint chi-square (DEMOTED: a coarse sanity
   check, reported only).
6. the phase-continuity scan (the slot-base offsets
   7 / 4000001 vs the main G1 run — the base is the main
   run, not a regenerate).

**D0 BOOTSTRAP**: 20 G0-vs-G0 replicate pairs at the pair
scale (1e5), the parametric q95 = mean + 1.645*sd per
comparison unit, rescaled to the gate scale by the 1/sqrt(N)
law (the single factor `sqrt(pair_scale / n_games)` — the
pooled and the per-ec units share it: the pooled population
scales with games*40, the per-ec strata with games, same
ratio).

**PASS (the 1e6 design gate: (i)-(iii); (iv) is the 1e7
BUILD gate, at corpus build time)**: (i) ABSOLUTE
(TABLE-AWARE): every D < `delta*_unit = max(2e-3,
q95(D0_unit))`; (ii) RELATIVE (PRIMARY): every D < the
parametric q95 of the measured D0 at the unit's scale;
(iii) the focused tests (3-4) under the family control
(Bonferroni over the pair x stratum family for the
chi-square p-values, BH-FDR as the secondary diagnostic) +
the test 1 phase-occupancy scan.

## Conventions / implementation notes

- The feature codes are STRUCTURED arrays (one field per
  orbit instance) — the exact key: the packed-uint64
  overflow is real (the 2X5COR code space is
  59049^8 >> 2^64). `np.unique` / `np.searchsorted` are
  lexicographic on the structured fields.
- The per-ec observation: the start ec 60 BEFORE the first
  step; ec 59..21 AFTER each step (the live lanes); the
  arrest ec is observed ONLY from the boundary harvest (no
  double count). The level list is indexed by
  `MAX_EC - ec` (0..n_ec-1), not by the ec value.
- The gate bypasses the pydantic `make_position` in the hot
  path (the direct interleaved structured-array build,
  `_to_positions`).
- The MT19937-64 constants are the C verbatim
  (`NN=312, MM=156, UM=0xFFFFFFFF80000000,
  LM=0x000000007FFFFFFF, MAG=0xB5026F5AA96619E9`) — the
  batch kernel is bit-exact vs the golden-pinned
  `reversi.tools.prng.MT19937.get_uint64` (the T3 oracle).
- The TV is the ½·L1 over the union support (the doc's
  "the scalar the downstream information statistics
  consume"); the chi-square p by the Wilson-Hilferty
  normal tail (the coarse instrument); the sparse KL caps
  the absent-from-p2 terms at 50 nats.

## Verified invariants (the suite, 14/0/0)

- `test_mt19937_batch_matches_reference`: the numba batch
  vs the golden-pinned reference, 2000 draws + the twist
  across the 312-word boundary + the mid-stream start.
- `test_mid_stream_start`: a pre-advanced reference and
  the numba state at the same point agree.
- `test_g0_wave_matches_scalar`: the W=1 G0 wave trajectory
  vs the scalar G0 reference loop (the same stream
  discipline — one draw per step, the pass folded into the
  step), bit-exact (the moves + the final position).
- the statistics utilities on the hand-computed values
  (TV 0 / 1 / 0.5; KL 0.8*ln(9) = 1.75778; the chi-square
  identical/different; the BH-FDR monotone property).
- the structured keys: the 8-field 59048.. codes stay
  distinct (no packed-int overflow); the joint key
  concatenation (the a-fields + the renamed b-fields).
- `TestRunGateSmoke` (`GATE_SMOKE=1`): the full pipeline at
  the tiny scale (200 games, 2 pairs @ 100) — the verdict
  structure, the report files, the rescale factor.

## Open issues

- The 5k sanity run at ec=55 and at ec=20 FAILS the
  criterion BY CONSTRUCTION: at 5k the per-(feature, ec)
  code supports exceed the sample (the sparse regime —
  TV(G1,G0) and TV(G0,G0) both saturate near 1, the 1/sqrt(N)
  rescale of the D0 pairs is invalid there). The doc's
  "at the scale where that demand is resolvable" — 1e6 is
  that scale (N >> the effective support). The 1e6 verdict
  is the real one.
- The 1e6 run: in flight (job bash-18) — the report at
  `scratch/gate_1e6/gate_report.txt` (the scratch is
  gitignored; the verdict is logged in the notes).

## Integration

- `run_gate(config_path, n_games, ec, seed, pairs,
  pair_scale, wave_size, outdir) -> verdict dict` + the
  CLI `main()` (`python3 -m reversi.lm.hlp_gate
  --config ... --n-games ... --seed ... --outdir ...`).
- `load_campaign` reuses the pipeline's own loader path
  (json5 + `LMConfig(**raw)`, the `wrk_features` pure
  mapping) — no DB.
- The report: `gate_results.json` (machine) +
  `gate_report.txt` (human) in the outdir.
