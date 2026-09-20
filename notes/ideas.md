# ideas.md — the open backlog

Format (D-235): `I-NNN | status | idea`, wrapped to ~120 chars/line with a 9-space continuation indent and a blank line
before every entry; code spans (backticks) for paths and function / file names. Status legend: `idea` (a forward-looking
proposal), `follow-up` (a known gap or debt left by an earlier decision), `in-progress` (a campaign under execution). A
CLOSED idea (`done` | `dropped`) MOVES to notes/ideas-closed.md — compacted to its statement + the D-pointer + the
outcome — in the same commit as the decision that closes it; it never stays here. The I-numbers are global and never
reused or renumbered (I-008 is dropped: see ideas-closed.md).

I-007 | follow-up | `FeatureSet` column-labelling helper (raised 2026-08-28, D-041, feature module M3): no way to map a
         column of the (N, I) index matrix to the feature name producing it (unlike `MobilitySet.names` /
         `.masks`, D-024). VERIFIED STILL OPEN (2026-09-19): the pipeline landed without it — the `_feature_blocks`
         helper is now re-derived locally in BOTH `wrk_su_analysis` and `wrk_effect_size` (the (name, col_start,
         col_end) blocks built from `feature_set.features`); each pattern occupies `n_instances` D8-instance columns, so
         the helper must be instance-aware.

I-014 | idea | Hot-restart ("restart a caldo") of the OPTIMIZE level from the checkpoint's warm weights (raised
         2026-09-01, session 26, D-096 R1): when a `ridge_regularization` change invalidates the checkpoint, the run
         starts FROM SCRATCH (the clipping-equivalent behavior Roberto chose); resuming L-BFGS from the checkpoint's
         warm state under the new objective was explicitly parked. Roberto: "un'ottimizzazione che svilupperei solo in
         seguito, se capiamo che ha un valore pratico". The plumbing exists (the checkpoint carries the full L-BFGS
         state — w + sl/yl/rho + iters — and `opt_lbfgs` has the warm-start kwargs, consumed on the INCOMPLETE resume
         path); the open question is whether a warm restart under a CHANGED objective is numerically sound / worth the
         extra semantics.
