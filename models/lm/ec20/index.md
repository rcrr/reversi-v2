# models/lm/ec20/ — the model registry (the ec20 level)

Format: a three-column table, one row per model. The ID is the model's NNNN folder (4 digits,
sequential, never reused); the config cell is a relative markdown link to the model's config file;
the description cell mirrors the config's one-line description, so the registry stays readable
without opening each file. The model's name lives in the config file itself.

| ID | config | description |
| --- | --- | --- |
| 0000 | [lm_ec20_0000.json](0000/lm_ec20_0000.json) | The intercept alone - no patterns, no mobilities. |
| 0001 | [lm_ec20_0001.json](0001/lm_ec20_0001.json) | The intercept plus the full-board LMC mobility - no patterns. |
| 0002 | [lm_ec20_0002.json](0002/lm_ec20_0002.json) | The intercept plus the full-board ALMC (the opponent's would-be moves) - no patterns. |
| 0003 | [lm_ec20_0003.json](0003/lm_ec20_0003.json) | The intercept plus the standard full-board mobility pair (the LMC + the ALMC) - no patterns. |
| 0004 | [lm_ec20_0004.json](0004/lm_ec20_0004.json) | The intercept plus the LMC over the A1 corner mask (4 cells) - no patterns. |
| 0005 | [lm_ec20_0005.json](0005/lm_ec20_0005.json) | The intercept plus the ALMC over the A1 corner mask (4 cells) - no patterns. |
| 0006 | [lm_ec20_0006.json](0006/lm_ec20_0006.json) | The intercept plus the LMC + ALMC pair over the A1 corner mask (4 cells) - no patterns. |
| 0007 | [lm_ec20_0007.json](0007/lm_ec20_0007.json) | The intercept plus the LMC over the B1 mask (8 cells) - no patterns. |
| 0008 | [lm_ec20_0008.json](0008/lm_ec20_0008.json) | The intercept plus the ALMC over the B1 mask (8 cells) - no patterns. |
| 0009 | [lm_ec20_0009.json](0009/lm_ec20_0009.json) | The intercept plus the LMC + ALMC pair over the B1 mask (8 cells) - no patterns. |
| 0010 | [lm_ec20_0010.json](0010/lm_ec20_0010.json) | The intercept plus the LMC over the C1 mask (8 cells) - no patterns. |
| 0011 | [lm_ec20_0011.json](0011/lm_ec20_0011.json) | The intercept plus the ALMC over the C1 mask (8 cells) - no patterns. |
| 0012 | [lm_ec20_0012.json](0012/lm_ec20_0012.json) | The intercept plus the LMC + ALMC pair over the C1 mask (8 cells) - no patterns. |
| 0013 | [lm_ec20_0013.json](0013/lm_ec20_0013.json) | The intercept plus the LMC over the D1 mask (8 cells) - no patterns. |
| 0014 | [lm_ec20_0014.json](0014/lm_ec20_0014.json) | The intercept plus the ALMC over the D1 mask (8 cells) - no patterns. |
| 0015 | [lm_ec20_0015.json](0015/lm_ec20_0015.json) | The intercept plus the LMC + ALMC pair over the D1 mask (8 cells) - no patterns. |
| 0016 | [lm_ec20_0016.json](0016/lm_ec20_0016.json) | The intercept plus the LMC over the B2 mask (4 cells) - no patterns. |
| 0017 | [lm_ec20_0017.json](0017/lm_ec20_0017.json) | The intercept plus the ALMC over the B2 mask (4 cells) - no patterns. |
| 0018 | [lm_ec20_0018.json](0018/lm_ec20_0018.json) | The intercept plus the LMC + ALMC pair over the B2 mask (4 cells) - no patterns. |
| 0019 | [lm_ec20_0019.json](0019/lm_ec20_0019.json) | The intercept plus the LMC over the C2 mask (8 cells) - no patterns. |
| 0020 | [lm_ec20_0020.json](0020/lm_ec20_0020.json) | The intercept plus the ALMC over the C2 mask (8 cells) - no patterns. |
| 0021 | [lm_ec20_0021.json](0021/lm_ec20_0021.json) | The intercept plus the LMC + ALMC pair over the C2 mask (8 cells) - no patterns. |
| 0022 | [lm_ec20_0022.json](0022/lm_ec20_0022.json) | The intercept plus the LMC over the D2 mask (8 cells) - no patterns. |
| 0023 | [lm_ec20_0023.json](0023/lm_ec20_0023.json) | The intercept plus the ALMC over the D2 mask (8 cells) - no patterns. |
| 0024 | [lm_ec20_0024.json](0024/lm_ec20_0024.json) | The intercept plus the LMC + ALMC pair over the D2 mask (8 cells) - no patterns. |
| 0025 | [lm_ec20_0025.json](0025/lm_ec20_0025.json) | The intercept plus the LMC over the C3 mask (4 cells) - no patterns. |
| 0026 | [lm_ec20_0026.json](0026/lm_ec20_0026.json) | The intercept plus the ALMC over the C3 mask (4 cells) - no patterns. |
| 0027 | [lm_ec20_0027.json](0027/lm_ec20_0027.json) | The intercept plus the LMC + ALMC pair over the C3 mask (4 cells) - no patterns. |
| 0028 | [lm_ec20_0028.json](0028/lm_ec20_0028.json) | The intercept plus the LMC over the D3 mask (8 cells) - no patterns. |
| 0029 | [lm_ec20_0029.json](0029/lm_ec20_0029.json) | The intercept plus the ALMC over the D3 mask (8 cells) - no patterns. |
| 0030 | [lm_ec20_0030.json](0030/lm_ec20_0030.json) | The intercept plus the LMC + ALMC pair over the D3 mask (8 cells) - no patterns. |
| 0031 | [lm_ec20_0031.json](0031/lm_ec20_0031.json) | Full-board LMS + ALMS plus the A1 selective LMS + ALMS pair (4 cells). |
| 0032 | [lm_ec20_0032.json](0032/lm_ec20_0032.json) | Full-board LMS + ALMS plus the B1 selective LMS + ALMS pair (8 cells). |
| 0033 | [lm_ec20_0033.json](0033/lm_ec20_0033.json) | Full-board LMS + ALMS plus the C1 selective LMS + ALMS pair (8 cells). |
| 0034 | [lm_ec20_0034.json](0034/lm_ec20_0034.json) | Full-board LMS + ALMS plus the D1 selective LMS + ALMS pair (8 cells). |
| 0035 | [lm_ec20_0035.json](0035/lm_ec20_0035.json) | Full-board LMS + ALMS plus the B2 selective LMS + ALMS pair (4 cells). |
| 0036 | [lm_ec20_0036.json](0036/lm_ec20_0036.json) | Full-board LMS + ALMS plus the C2 selective LMS + ALMS pair (8 cells). |
| 0037 | [lm_ec20_0037.json](0037/lm_ec20_0037.json) | Full-board LMS + ALMS plus the D2 selective LMS + ALMS pair (8 cells). |
| 0038 | [lm_ec20_0038.json](0038/lm_ec20_0038.json) | Full-board LMS + ALMS plus the C3 selective LMS + ALMS pair (4 cells). |
| 0039 | [lm_ec20_0039.json](0039/lm_ec20_0039.json) | Full-board LMS + ALMS plus the D3 selective LMS + ALMS pair (8 cells). |
