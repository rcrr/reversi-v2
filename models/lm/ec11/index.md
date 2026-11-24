# models/lm/ec11/ — the model registry (the ec11 level)

Format: a three-column table, one row per model. The ID is the model's NNNN folder (4 digits,
sequential, never reused); the config cell is a relative markdown link to the model's config file;
the description cell mirrors the config's one-line description, so the registry stays readable
without opening each file. The model's name lives in the config file itself.

| ID | config | description |
| --- | --- | --- |
| 0108 | [lm_ec11_0108.json](0108/lm_ec11_0108.json) | The intercept plus the 2X5COR, XEDGE, CORNER, R4, DIAG8, DIAG7, DIAG6, DIAG5, R2 and R3 patterns and the OptMob mobility, empty count 11 - trained on batches 3, 9 and 12, validated on batch 6. |
| 0153 | [lm_ec11_0153.json](0153/lm_ec11_0153.json) | The intercept plus the 2X6COR, CASTLE, 3X4COR, R4, BARBEL, DIAG7, DIAG6, DIAG5, R2 and R3 patterns and the OptMob mobility, empty count 11 - trained on batches 3, 9 and 12, validated on batch 6. |
