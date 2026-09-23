# ideas.md — the open backlog

Format (D-235): `I-NNN | status | idea`, wrapped to ~120 chars/line with a 9-space continuation indent and a blank line
before every entry; code spans (backticks) for paths and function / file names. Status legend: `idea` (a forward-looking
proposal), `follow-up` (a known gap or debt left by an earlier decision), `in-progress` (a campaign under execution). A
CLOSED idea (`done` | `dropped`) MOVES to notes/ideas-closed.md — compacted to its statement + the D-pointer + the
outcome — in the same commit as the decision that closes it; it never stays here. The I-numbers are global and never
reused or renumbered (I-008 is dropped: see ideas-closed.md).

I-014 | idea | Hot-restart ("restart a caldo") of the OPTIMIZE level from the checkpoint's warm weights (raised
         2026-09-01, session 26, D-096 R1): when a `ridge_regularization` change invalidates the checkpoint, the run
         starts FROM SCRATCH (the clipping-equivalent behavior Roberto chose); resuming L-BFGS from the checkpoint's
         warm state under the new objective was explicitly parked. Roberto: "un'ottimizzazione che svilupperei solo in
         seguito, se capiamo che ha un valore pratico". The plumbing exists (the checkpoint carries the full L-BFGS
         state — w + sl/yl/rho + iters — and `opt_lbfgs` has the warm-start kwargs, consumed on the INCOMPLETE resume
         path); the open question is whether a warm restart under a CHANGED objective is numerically sound / worth the
         extra semantics.

I-020 | follow-up | The DOUBLE `fset.compute_indexes` per wave (raised 2026-09-23, session 58, deferred by
         Roberto in D-299, "magari lo vediamo dopo"): `_MarginalAccumulator.add` and `_JointAccumulator.add`
         each recompute the SAME index matrix over the wave's positions (two `fset.compute_indexes(pos)` calls
         per wave in `hlp_su_analysis_compute`). Sharing one computation (compute it once in the compute loop
         and feed both accumulators) would cut the per-wave index cost — both adds start from it. Parked
         because the D-299 vectorized joint merge already removed the dominant cost, and the change touches the
         accumulators' `add(pos)` contract (the position language, D-296) or the compute loop's feeding idiom.
