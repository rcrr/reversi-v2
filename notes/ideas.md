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
