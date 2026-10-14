# LM config file — user guide

How to write the JSON config file that drives the LM pipeline (`python -m reversi.lm.logistic_model
<config.json>`). The file is a JSON5 document (comments and trailing commas are allowed) loaded and
validated at the CONFIG level by the `LMConfig` schema (`hlp_config_schemas.md`): every option below is a
field of that schema, with its type, its default, and its constraints. A config that fails validation
stops the run at CONFIG with a pydantic `ValidationError` naming the offending field — nothing else runs.

## Rules

- **The 10 required top-level keys** — `name`, `empty_count`, `description`, `base_dir`, `output`,
  `regab_data_set`, `validation_data_set`, `feature_set`, `stat_model`, `optimization`. Every other
  top-level key has a default and may be omitted (it then takes the default sub-config).
- **`empty_count` is the single source of the ec** — an integer 0..60; the same value drives the SU corpus
  generation, the DB extraction (training + validation), and the saved model.
- **`status` values** — exactly three uppercase letters (pattern `^[A-Z]{3}$`), e.g. `"CMS"`, `"CMR"`.
- **`bid` values** — lists of non-negative integers.
- **Bitboard masks** — 16 hex digits, NO `0x` prefix, case-insensitive on input; they are normalized to
  uppercase 16-hex on output.
- **Paths** — `base_dir` is the run's root. A `dir_name` that is RELATIVE resolves under `base_dir`; an
  ABSOLUTE `dir_name` is used as-is (it may live outside `base_dir`). `log_file_name` is relative to
  `base_dir`.
- **Cross-field rules** (checked after the individual fields): `optimization.c2 > optimization.c1`
  (the strong-Wolfe pair); every `su_analysis.su_pairs` name must be a feature of `feature_set`
  (mobility + pattern names); the `plot.format` tokens must be `png` / `pdf`; the `plot.plots` names must
  be in the 7-name plot vocabulary.
- **The `properties` bag** — every config section accepts a free-form `properties: {…}` dict
  (any JSON values). The pipeline does not read it; it is an extension point for the user's own notes.
- **`target_level`** — a level name (case-insensitive, fail-fast on a typo) or `"last"` (the full
  pipeline); a blank value means `"last"` too. It is the stop target of `run()` when no explicit target
  is given.

## Minimal example

The smallest valid config: the 10 required keys, `stat_model` and `optimization` carrying only what is
mandatory (`checkpoint_file`), everything else left to defaults.

```json5
{
    "name": "my-model",
    "empty_count": 20,
    "description": "A minimal LM config.",
    "base_dir": "models/my-model",
    "output": "model.dat",
    "regab_data_set": {
        "regab_db_connection": { "dbname": "regab", "user": "regab", "host": "localhost" },
        "bid": [8],
        "status": ["CMS", "CMR"]
    },
    "validation_data_set": {
        "bid": [8],
        "status": ["CMS", "CMR"]
    },
    "feature_set": {
        "intercept": true,
        "pattern_set": {
            "name": "my-patterns",
            "patterns": [ { "name": "EDGE", "mask": "00000000000000FF" } ]
        }
    },
    "stat_model": {},
    "optimization": { "checkpoint_file": "checkpoint_optimize.dat" }
}
```

With this file the pipeline runs all 19 levels: the PLOT level is a no-op (the default `plots` whitelist
is empty), the SU_ANALYSIS and ANOVA levels are no-ops (their `enable` defaults are false), the cache is
on with the `rlmwf_` prefix.

## Exhaustive reference

### Root (`LMConfig`)

| key | type | default | notes |
|---|---|---|---|
| `name` | str | — required | the model name |
| `empty_count` | int | — required | 0..60; the single ec source (see Rules) |
| `description` | str | — required | free text |
| `base_dir` | path | — required | the run's root directory |
| `output` | path | — required | the saved binary model weights filename |
| `use_cache` | bool | `true` | the per-run cache switch (the CONFIG down path resets it) |
| `cache_files_prefix` | str | `"rlmwf_"` | the level cache files prefix (`<prefix><level:02>_<worker>.dat`) |
| `regab_allow_duplicate` | bool | `true` | `true` keeps every DB row; `false` deduplicates keeping the first occurrence (the lowest seq); the duplicate count is logged at POSITIONS and VLD_POSITIONS (log only) |
| `client_check_tol` | float | `1e-8` | > 0; the CLIENT_CHECK tolerance — the max absolute Y-space difference between the saved-model recompute and the in-memory VALIDATE (Y space: comparable across models) |
| `target_level` | str | `"last"` | a level name (case-insensitive, fail-fast) or `"last"` |
| `log_file_name` | str \| null | `null` | the FINAL_LOG_PRINT file (relative to `base_dir`); `null` = the level is a no-op |
| `plot` | object | defaults | see Plot |
| `analytics` | object | defaults | see Analytics |
| `su_analysis` | object | defaults (off) | see Su analysis |
| `anova` | object | defaults (off) | see Anova |
| `properties` | object | `{}` | the free-form bag (the pipeline does not read it) |

### `regab_data_set` (required)

| key | type | default | notes |
|---|---|---|---|
| `regab_db_connection` | object | — required | see below |
| `bid` | list[int ≥ 0] | — required | the board ids to extract |
| `status` | list[str] | — required | three-uppercase-letter statuses |

`regab_db_connection`:

| key | type | default | notes |
|---|---|---|---|
| `dbname` | str | — required | |
| `user` | str | — required | |
| `host` | str | — required | |
| `port` | int | `5432` | |
| `password` | str \| null | `null` | |

### `validation_data_set` (required)

`bid: list[int ≥ 0]` + `status: list[str]` — the same two fields as the training set (no connection: the
training set's connection is used).

### `feature_set` (required)

| key | type | default | notes |
|---|---|---|---|
| `name` | str | `"NoNameFeatureSet"` | |
| `intercept` | bool | `false` | add the intercept column to the design matrix |
| `mobility_set` | object \| null | `null` | see below |
| `pattern_set` | object \| null | `null` | see below |

`pattern_set`: `name` (required) + `patterns: [ { "name": str, "mask": 16-hex } ]` (default empty).

`mobility_set`: `name` (required) + `mobility_features: [ { "name": str, "mask": 16-hex, "side": "mover" | "opponent" } ]`
(default empty) — `mask` the counted-squares bitboard, `side` whose legal moves are counted over it: the mover's or the
opponent's. The same mask with the two sides is the standard LMC + ALMC pair.

### `stat_model` (required)

| key | type | default | notes |
|---|---|---|---|
| `frequency_cut_off` | int ≥ 1 | `1` | |
| `logit_clipping` | float | `0.05` | 0 < x < 0.5 |
| `ridge_regularization` | float | `0.0` | ≥ 0 |

### `optimization` (required)

| key | type | default | notes |
|---|---|---|---|
| `max_iters` | int ≥ 1 | `500` | |
| `m` | int ≥ 1 | `50` | the L-BFGS memory (stored vector pairs) |
| `c1` | float | `1e-4` | 0 < c1 < 1 (Armijo) |
| `c2` | float | `0.9` | 0 < c2 < 1, and **c2 > c1** (checked) |
| `min_grad` | [float, int] | `[1e-5, 3]` | gradient-norm tolerance + consecutive iterations |
| `min_p_fun_decrease` | [float, int] | `[1e-14, 7]` | min relative loss decrease + consecutive iterations |
| `log_every_n` | int ≥ 0 | `0` | 0 = no log, 1 = every iteration |
| `save_every_n` | int ≥ 0 | `0` | 0 = no checkpoint save |
| `checkpoint_file` | path | — required | the optimization checkpoint filename |
| `high_performance_fg` | bool | `false` | `true` builds the numba fg closure at GRADIENT (row-blocked, parallel) |
| `hi_perf_blocks` | int ≥ 1 | `8` | the T row-blocks of the high-performance fg (only when `high_performance_fg` is true) |

### `analytics`

| key | type | default | notes |
|---|---|---|---|
| `detailed_report` | list[str] | `[]` | feature names getting row-by-row tables in the TXT report |
| `report_file_name` | str | `"model_analytics_report.txt"` | |

### `plot`

| key | type | default | notes |
|---|---|---|---|
| `enable` | bool | `true` | master switch — `false` = the PLOT level is a no-op, even with names listed |
| `format` | str | `"png"` | `"png"`, `"pdf"`, or a comma pair (`"pdf,png"` — both); tokens checked, duplicates rejected |
| `dpi` | int | `150` | 50..1200 (the png output) |
| `dir_name` | path | `"plots"` | relative = under `base_dir`, absolute = as-is |
| `plots` | list[str] | `[]` | the whitelist — empty = the level is a no-op; unknown names fail at CONFIG; duplicates are dropped (order kept). Valid names: `residual_density`, `resid_vs_fitted`, `resid_vs_gv`, `gv_by_egv_box`, `resid_mean_by_egv`, `parity`, `resid_qq` |
| `binned_note` | str | `" $(binned\ every\ 2)$"` | the binned-axis parenthetical (box / mean-residual plots); empty disables it |
| `jitter_seed` | int ≥ 0 | `42` | the jitter generator seed (the two scatter plots) |
| `kde_seed` | int ≥ 0 | `43` | the KDE subsample seed (the density plot) |
| `kde_max_points` | int ≥ 1 | `100000` | the KDE subsample cap |
| `jitter_fitted_x` | float ≥ 0 | `0.005` | residual-vs-fitted x-jitter, a fraction of the data range |
| `jitter_y` | float ≥ 0 | `0.005` | residual-y jitter, a fraction of the data range |
| `jitter_gv_x` | float ≥ 0 | `0.7` | residual-vs-game-value x-jitter, a fraction of the data range |
| `kde_grid` | int ≥ 2 | `512` | the KDE evaluation grid size |
| `axis_gv` | float > 0 | `64.0` | the fixed game-value axis domain (half-span) |
| `axis_density` | float > 0 | `72.0` | the fixed residual-density axis window (half-span) |
| `tick_step` | float > 0 | `8.0` | the axis tick step |
| `series_label_x` | dict[str, float] | `{"Validation": 0.04, "Training": 0.674, "Reference": 0.75}` | the parity-plot series-label x placement, a fraction of the axis span from the left |
| `series_label_y` | dict[str, float] | `{"Validation": 0.80, "Training": 0.96, "Reference": 0.98}` | the parity-plot series-label y placement, a fraction of the curve maximum |

### `su_analysis` (off by default)

| key | type | default | notes |
|---|---|---|---|
| `enable` | bool | `false` | master switch — the SU analysis is OPT-IN |
| `corpus.seed` | int | `42` | the MT19937 corpus seed |
| `corpus.total_positions` | int ≥ 1 | `10000000` | the corpus size |
| `su_pairs` | list[[str, str]] | `[]` | the explicit (feature, feature) joint-analysis pairs; each pair is canonical-sorted + deduped; every name must be in the feature set (checked at the root) |
| `rarity_thresholds` | list[int] \| null | `null` | the report "Section B" half-open bins `[0, t1), [t1, t2), …`; `null` / empty = the section off; positive strictly-increasing integers (checked) |
| `dir_name` | path | `"su_analysis"` | relative = under `base_dir`, absolute = as-is |
| `report_file_name` | str | `"su_analysis_report.txt"` | |
| `export_csv` | bool | `false` | the CSV is optional; the console + the TXT are always written |

### `anova` (off by default)

| key | type | default | notes |
|---|---|---|---|
| `enable` | bool | `false` | master switch — the ANOVA is OPT-IN |
| `top_k_adherence` | int ≥ 1 | `20` | the most deviant features reported in the console (the TV descending) |
| `dir_name` | path | `"anova"` | relative = under `base_dir`, absolute = as-is |
| `report_file_name` | str | `"anova_report.txt"` | |
| `export_csv` | bool | `false` | the CSV is optional; the console + the TXT are always written |

## Complete example

Every section present, every option at a non-default value where it matters:

```json5
{
    "name": "production-model",
    "empty_count": 20,
    "description": "The 11-pattern production set.",
    "base_dir": "models/production",
    "output": "rglm_logistic_model_ec_20.dat",
    "use_cache": true,
    "cache_files_prefix": "rlmwf_",
    "regab_allow_duplicate": true,
    "client_check_tol": 1e-8,
    "target_level": "last",
    "log_file_name": "run_log.txt",
    "properties": { "number": 7 },

    "regab_data_set": {
        "regab_db_connection": {
            "dbname": "regab", "user": "regab", "host": "localhost",
            "port": 5432, "password": null
        },
        "bid": [8],
        "status": ["CMS", "CMR"]
    },
    "validation_data_set": {
        "bid": [8],
        "status": ["CMS", "CMR"]
    },
    "feature_set": {
        "name": "ProdFeatureSet",
        "intercept": true,
        "pattern_set": {
            "name": "BasicPatternSet",
            "patterns": [
                { "name": "ELLE", "mask": "0000000000000107" },
                { "name": "EDGE", "mask": "00000000000000FF" }
            ]
        },
        "mobility_set": {
            "name": "BasicMobilitySet",
            "mobility_features": [
                { "name": "LMC",  "mask": "FFFFFFFFFFFFFFFF", "side": "mover" },
                { "name": "ALMC", "mask": "FFFFFFFFFFFFFFFF", "side": "opponent" }
            ]
        }
    },
    "stat_model": {
        "frequency_cut_off": 1,
        "logit_clipping": 0.05,
        "ridge_regularization": 0.0
    },
    "optimization": {
        "max_iters": 500, "m": 50,
        "c1": 0.0001, "c2": 0.9,
        "min_grad": [1e-5, 3],
        "min_p_fun_decrease": [1e-14, 7],
        "log_every_n": 10, "save_every_n": 0,
        "checkpoint_file": "checkpoint_optimize.dat",
        "high_performance_fg": false,
        "hi_perf_blocks": 8
    },
    "analytics": {
        "detailed_report": ["ELLE", "EDGE", "LMC"],
        "report_file_name": "model_analytics_report.txt"
    },
    "plot": {
        "enable": true,
        "format": "png",
        "dpi": 150,
        "dir_name": "plots",
        "plots": ["parity", "resid_qq"]
    },
    "su_analysis": {
        "enable": true,
        "corpus": { "seed": 42, "total_positions": 10000 },
        "su_pairs": [["LMC", "EDGE"]],
        "rarity_thresholds": [1, 2, 5, 10, 100],
        "dir_name": "su_analysis",
        "report_file_name": "su_analysis_report.txt",
        "export_csv": false
    },
    "anova": {
        "enable": false,
        "top_k_adherence": 20,
        "dir_name": "anova",
        "report_file_name": "anova_report.txt",
        "export_csv": false
    }
}
```

The field-level reference (types, defaults, the validators) lives in the schema's mirror doc:
`docs/src/reversi/lm/hlp_config_schemas.md`.
