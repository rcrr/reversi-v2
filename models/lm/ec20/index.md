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
| 0040 | [lm_ec20_0040.json](0040/lm_ec20_0040.json) | The intercept plus the single EDGE pattern - no mobility. |
| 0041 | [lm_ec20_0041.json](0041/lm_ec20_0041.json) | The intercept plus the single R2 pattern - no mobility. |
| 0042 | [lm_ec20_0042.json](0042/lm_ec20_0042.json) | The intercept plus the single R3 pattern - no mobility. |
| 0043 | [lm_ec20_0043.json](0043/lm_ec20_0043.json) | The intercept plus the single R4 pattern - no mobility. |
| 0044 | [lm_ec20_0044.json](0044/lm_ec20_0044.json) | The intercept plus the single DIAG8 pattern - no mobility. |
| 0045 | [lm_ec20_0045.json](0045/lm_ec20_0045.json) | The intercept plus the single DIAG7 pattern - no mobility. |
| 0046 | [lm_ec20_0046.json](0046/lm_ec20_0046.json) | The intercept plus the single DIAG6 pattern - no mobility. |
| 0047 | [lm_ec20_0047.json](0047/lm_ec20_0047.json) | The intercept plus the single DIAG5 pattern - no mobility. |
| 0048 | [lm_ec20_0048.json](0048/lm_ec20_0048.json) | The intercept plus the single DIAG4 pattern - no mobility. |
| 0049 | [lm_ec20_0049.json](0049/lm_ec20_0049.json) | The intercept plus the single CORNER pattern - no mobility. |
| 0050 | [lm_ec20_0050.json](0050/lm_ec20_0050.json) | The intercept plus the single XEDGE pattern - no mobility. |
| 0051 | [lm_ec20_0051.json](0051/lm_ec20_0051.json) | The intercept plus the single 2X5COR pattern - no mobility. |
| 0052 | [lm_ec20_0052.json](0052/lm_ec20_0052.json) | The intercept plus the single CORNER pattern - trained on batch 3, validated on batch 6. |
| 0053 | [lm_ec20_0053.json](0053/lm_ec20_0053.json) | The intercept plus the single XEDGE pattern - trained on batch 3, validated on batch 6. |
| 0054 | [lm_ec20_0054.json](0054/lm_ec20_0054.json) | The intercept plus the single 2X5COR pattern - trained on batch 3, validated on batch 6. |
| 0055 | [lm_ec20_0055.json](0055/lm_ec20_0055.json) | The intercept plus the EDGE and XEDGE patterns - trained on batch 3, validated on batch 6. |
| 0056 | [lm_ec20_0056.json](0056/lm_ec20_0056.json) | The intercept plus the 2X5COR and XEDGE patterns - trained on batch 3, validated on batch 6. |
| 0057 | [lm_ec20_0057.json](0057/lm_ec20_0057.json) | The intercept plus the 2X5COR and CORNER patterns - trained on batch 3, validated on batch 6. |
| 0058 | [lm_ec20_0058.json](0058/lm_ec20_0058.json) | The intercept plus the 2X5COR and DIAG8 patterns - trained on batch 3, validated on batch 6. |
| 0059 | [lm_ec20_0059.json](0059/lm_ec20_0059.json) | The intercept plus the 2X5COR and DIAG7 patterns - trained on batch 3, validated on batch 6. |
| 0060 | [lm_ec20_0060.json](0060/lm_ec20_0060.json) | The intercept plus the 2X5COR and DIAG6 patterns - trained on batch 3, validated on batch 6. |
| 0061 | [lm_ec20_0061.json](0061/lm_ec20_0061.json) | The intercept plus the 2X5COR and DIAG5 patterns - trained on batch 3, validated on batch 6. |
| 0062 | [lm_ec20_0062.json](0062/lm_ec20_0062.json) | The intercept plus the 2X5COR and DIAG4 patterns - trained on batch 3, validated on batch 6. |
| 0063 | [lm_ec20_0063.json](0063/lm_ec20_0063.json) | The intercept plus the 2X5COR and R2 patterns - trained on batch 3, validated on batch 6. |
| 0064 | [lm_ec20_0064.json](0064/lm_ec20_0064.json) | The intercept plus the 2X5COR and R3 patterns - trained on batch 3, validated on batch 6. |
| 0065 | [lm_ec20_0065.json](0065/lm_ec20_0065.json) | The intercept plus the 2X5COR and R4 patterns - trained on batch 3, validated on batch 6. |
| 0066 | [lm_ec20_0066.json](0066/lm_ec20_0066.json) | The intercept plus the 2X5COR, XEDGE and CORNER patterns - trained on batch 3, validated on batch 6. |
| 0067 | [lm_ec20_0067.json](0067/lm_ec20_0067.json) | The intercept plus the 2X5COR, XEDGE and DIAG8 patterns - trained on batch 3, validated on batch 6. |
| 0068 | [lm_ec20_0068.json](0068/lm_ec20_0068.json) | The intercept plus the 2X5COR, XEDGE and DIAG7 patterns - trained on batch 3, validated on batch 6. |
| 0069 | [lm_ec20_0069.json](0069/lm_ec20_0069.json) | The intercept plus the 2X5COR, XEDGE and DIAG6 patterns - trained on batch 3, validated on batch 6. |
| 0070 | [lm_ec20_0070.json](0070/lm_ec20_0070.json) | The intercept plus the 2X5COR, XEDGE and DIAG5 patterns - trained on batch 3, validated on batch 6. |
| 0071 | [lm_ec20_0071.json](0071/lm_ec20_0071.json) | The intercept plus the 2X5COR, XEDGE and DIAG4 patterns - trained on batch 3, validated on batch 6. |
| 0072 | [lm_ec20_0072.json](0072/lm_ec20_0072.json) | The intercept plus the 2X5COR, XEDGE and R2 patterns - trained on batch 3, validated on batch 6. |
| 0073 | [lm_ec20_0073.json](0073/lm_ec20_0073.json) | The intercept plus the 2X5COR, XEDGE and R3 patterns - trained on batch 3, validated on batch 6. |
| 0074 | [lm_ec20_0074.json](0074/lm_ec20_0074.json) | The intercept plus the 2X5COR, XEDGE and R4 patterns - trained on batch 3, validated on batch 6. |
| 0075 | [lm_ec20_0075.json](0075/lm_ec20_0075.json) | The intercept plus the 2X5COR, XEDGE, CORNER and DIAG8 patterns - trained on batch 3, validated on batch 6. |
| 0076 | [lm_ec20_0076.json](0076/lm_ec20_0076.json) | The intercept plus the 2X5COR, XEDGE, CORNER and DIAG7 patterns - trained on batch 3, validated on batch 6. |
| 0077 | [lm_ec20_0077.json](0077/lm_ec20_0077.json) | The intercept plus the 2X5COR, XEDGE, CORNER and DIAG6 patterns - trained on batch 3, validated on batch 6. |
| 0078 | [lm_ec20_0078.json](0078/lm_ec20_0078.json) | The intercept plus the 2X5COR, XEDGE, CORNER and DIAG5 patterns - trained on batch 3, validated on batch 6. |
| 0079 | [lm_ec20_0079.json](0079/lm_ec20_0079.json) | The intercept plus the 2X5COR, XEDGE, CORNER and DIAG4 patterns - trained on batch 3, validated on batch 6. |
| 0080 | [lm_ec20_0080.json](0080/lm_ec20_0080.json) | The intercept plus the 2X5COR, XEDGE, CORNER and R2 patterns - trained on batch 3, validated on batch 6. |
| 0081 | [lm_ec20_0081.json](0081/lm_ec20_0081.json) | The intercept plus the 2X5COR, XEDGE, CORNER and R3 patterns - trained on batch 3, validated on batch 6. |
| 0082 | [lm_ec20_0082.json](0082/lm_ec20_0082.json) | The intercept plus the 2X5COR, XEDGE, CORNER and R4 patterns - trained on batch 3, validated on batch 6. |
| 0083 | [lm_ec20_0083.json](0083/lm_ec20_0083.json) | The intercept plus the 2X5COR, XEDGE, CORNER, R4 and DIAG8 patterns - trained on batch 3, validated on batch 6. |
| 0084 | [lm_ec20_0084.json](0084/lm_ec20_0084.json) | The intercept plus the 2X5COR, XEDGE, CORNER, R4 and DIAG7 patterns - trained on batch 3, validated on batch 6. |
| 0085 | [lm_ec20_0085.json](0085/lm_ec20_0085.json) | The intercept plus the 2X5COR, XEDGE, CORNER, R4 and DIAG6 patterns - trained on batch 3, validated on batch 6. |
| 0086 | [lm_ec20_0086.json](0086/lm_ec20_0086.json) | The intercept plus the 2X5COR, XEDGE, CORNER, R4 and DIAG5 patterns - trained on batch 3, validated on batch 6. |
| 0087 | [lm_ec20_0087.json](0087/lm_ec20_0087.json) | The intercept plus the 2X5COR, XEDGE, CORNER, R4 and R2 patterns - trained on batch 3, validated on batch 6. |
| 0088 | [lm_ec20_0088.json](0088/lm_ec20_0088.json) | The intercept plus the 2X5COR, XEDGE, CORNER, R4 and R3 patterns - trained on batch 3, validated on batch 6. |
| 0089 | [lm_ec20_0089.json](0089/lm_ec20_0089.json) | The intercept plus the 2X5COR, XEDGE, CORNER, R4, DIAG8, DIAG7, DIAG6, DIAG5, R2 and R3 patterns - trained on batch 3, validated on batch 6. |
| 0090 | [lm_ec20_0090.json](0090/lm_ec20_0090.json) | The intercept plus the XEDGE, CORNER, R4, DIAG8, DIAG7, DIAG6, DIAG5, R2 and R3 patterns - trained on batch 3, validated on batch 6. |
| 0091 | [lm_ec20_0091.json](0091/lm_ec20_0091.json) | The intercept plus the 2X5COR, CORNER, R4, DIAG8, DIAG7, DIAG6, DIAG5, R2 and R3 patterns - trained on batch 3, validated on batch 6. |
| 0092 | [lm_ec20_0092.json](0092/lm_ec20_0092.json) | The intercept plus the 2X5COR, XEDGE, R4, DIAG8, DIAG7, DIAG6, DIAG5, R2 and R3 patterns - trained on batch 3, validated on batch 6. |
| 0093 | [lm_ec20_0093.json](0093/lm_ec20_0093.json) | The intercept plus the 2X5COR, XEDGE, CORNER, DIAG8, DIAG7, DIAG6, DIAG5, R2 and R3 patterns - trained on batch 3, validated on batch 6. |
| 0094 | [lm_ec20_0094.json](0094/lm_ec20_0094.json) | The intercept plus the 2X5COR, XEDGE, CORNER, R4, DIAG7, DIAG6, DIAG5, R2 and R3 patterns - trained on batch 3, validated on batch 6. |
| 0095 | [lm_ec20_0095.json](0095/lm_ec20_0095.json) | The intercept plus the 2X5COR, XEDGE, CORNER, R4, DIAG8, DIAG6, DIAG5, R2 and R3 patterns - trained on batch 3, validated on batch 6. |
| 0096 | [lm_ec20_0096.json](0096/lm_ec20_0096.json) | The intercept plus the 2X5COR, XEDGE, CORNER, R4, DIAG8, DIAG7, DIAG5, R2 and R3 patterns - trained on batch 3, validated on batch 6. |
| 0097 | [lm_ec20_0097.json](0097/lm_ec20_0097.json) | The intercept plus the 2X5COR, XEDGE, CORNER, R4, DIAG8, DIAG7, DIAG6, R2 and R3 patterns - trained on batch 3, validated on batch 6. |
| 0098 | [lm_ec20_0098.json](0098/lm_ec20_0098.json) | The intercept plus the 2X5COR, XEDGE, CORNER, R4, DIAG8, DIAG7, DIAG6, DIAG5 and R3 patterns - trained on batch 3, validated on batch 6. |
| 0099 | [lm_ec20_0099.json](0099/lm_ec20_0099.json) | The intercept plus the 2X5COR, XEDGE, CORNER, R4, DIAG8, DIAG7, DIAG6, DIAG5 and R2 patterns - trained on batch 3, validated on batch 6. |
| 0100 | [lm_ec20_0100.json](0100/lm_ec20_0100.json) | The intercept plus the 2X5COR, XEDGE, CORNER, R4, DIAG8, DIAG7, DIAG6, DIAG5, R2 and R3 patterns and the OptMob mobility - trained on batch 3, validated on batch 6. |
| 0101 | [lm_ec20_0101.json](0101/lm_ec20_0101.json) | The intercept plus the 2X5COR, XEDGE, CORNER, R4, DIAG8, DIAG7, DIAG6, DIAG5, R2 and R3 patterns and the OptMob mobility - trained on batch 9, validated on batch 6. |
| 0102 | [lm_ec20_0102.json](0102/lm_ec20_0102.json) | The intercept plus the 2X5COR, XEDGE, CORNER, R4, DIAG8, DIAG7, DIAG6, DIAG5, R2 and R3 patterns and the OptMob mobility - trained on batch 12, validated on batch 6. |
| 0103 | [lm_ec20_0103.json](0103/lm_ec20_0103.json) | The intercept plus the 2X5COR, XEDGE, CORNER, R4, DIAG8, DIAG7, DIAG6, DIAG5, R2 and R3 patterns and the OptMob mobility - trained on batches 3, 9 and 12, validated on batch 6. |
| 0104 | [lm_ec20_0104.json](0104/lm_ec20_0104.json) | The intercept plus the 2X5COR, XEDGE, CORNER, R4, DIAG8, DIAG7, DIAG6, DIAG5, R2 and R3 patterns and the OptMob mobility, ridge sweep - trained on batches 3, 9 and 12, validated on batch 6. |
| 0105 | [lm_ec20_0105.json](0105/lm_ec20_0105.json) | The intercept plus the 2X5COR, XEDGE, CORNER, R4, DIAG8, DIAG7, DIAG6, DIAG5, R2 and R3 patterns and the OptMob mobility, frequency cut-off sweep - trained on batches 3, 9 and 12, validated on batch 6. |
