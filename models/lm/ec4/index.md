# models/lm/ec4/ — the model registry (the ec4 level)

Format: a three-column table, one row per model. The ID is the model's NNNN folder (4 digits,
sequential, never reused); the config cell is a relative markdown link to the model's config file;
the description cell mirrors the config's one-line description, so the registry stays readable
without opening each file. The model's name lives in the config file itself.

| ID | config | description |
| --- | --- | --- |
| 0108 | [lm_ec4_0108.json](0108/lm_ec4_0108.json) | The intercept plus the 2X5COR, XEDGE, CORNER, R4, DIAG8, DIAG7, DIAG6, DIAG5, R2 and R3 patterns and the OptMob mobility, empty count 4 - trained on batches 3, 9 and 12, validated on batch 6. |
