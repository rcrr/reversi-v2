# ideas.md — the open backlog

Format: `I-NNN | status | idea`, wrapped to ~120 chars/line with a 9-space continuation indent and a blank line before
every entry; code spans (backticks) for paths and function / file names. Status legend: `idea` (a forward-looking
proposal), `follow-up` (a known gap or debt left by an earlier decision), `in-progress` (a campaign under execution). A
CLOSED idea (`done` | `dropped`) MOVES to notes/ideas\_closed.md — compacted to its statement + the D-pointer + the
outcome — in the same commit as the decision that closes it; it never stays here. The I-numbers are global and never
reused or renumbered.

I-021 | idea | Define the new model based on a residual neural network (ResNet) to enhance the predictive capabilities
         of the evaluation function. In our intentions it extends the logistic model by capturing the non-linear
         interactions between selected pairs of features: it augments the Logistic Model by adding a term to the linear
         predictor, constructed as the sum of a set of Softplus neurons carrying the embeddings of the pattern pairs.
         Start the experimentation of the new pipeline for training this model.

I-022 | idea | Port the artifacts developed in ANSI C to Rust.

I-023 | idea | The frontier-vectorized endgame search core (the "engine A" parked by D-667): the recursion over arrays
         of positions (the search frontier), the per-lane windows / counters / finals as arrays, the mask-classified
         lanes (leaf / pass / move), the move loop as an iteration over the move rank (the k-th set bit per lane), the
         gather/scatter of the active lanes, the per-lane zero-window propagation and cutoff merge. Parked because its
         NUMBA payoff is limited (1.5–4x single-core: the irregular mask/gather/cutoff control flow is not
         auto-vectorizable, only the regular per-lane kernels are), while the worker pool (D-667) gives ~8x on 8 cores
         with zero new search code. The candidate home is the RUST high-perf solver (the I-022 lineage), where the
         batched frontier design is the standard high-performance formulation for the 1M–10M-position endgame datasets —
         run in 1k–10k-lane batches, the batches parallelized worker-pool style. Revisit when the Rust port starts (or
         if a numba prototype ever measures clearly above the pool baseline).
