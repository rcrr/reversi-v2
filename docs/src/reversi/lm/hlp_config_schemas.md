# reversi/lm/hlp_config_schemas.py
The pydantic config DOMAIN of the LM pipeline: one public entry, `LMConfig`, over a tree of nested configs — the JSON5
document that `wrk_config` loads and validates. Every nested config extends `LMBaseConfig`, whose
`properties: dict[str, Any]` bag (default `{}`) is a free-form extension point.

## API

| name | role |
|---|---|
| `LMConfig` | the only `__all__` name — the top-level config |
| `LMBaseConfig` | `BaseModel` + the `properties` bag; base of every nested config |
| `StatusString` | `Annotated[str, Field(pattern="^[A-Z]{3}$")]` — exactly 3 uppercase letters |
| `ValidationDataSetConfig` | `bid: List[NonNegativeInt]` + `status: List[StatusString]` (strict) |
| `OptimizationConfig` | the L-BFGS knobs + the `check_wolfe_constants` cross-field validator + `high_performance_fg` (bool, default False — the fg-variant flag) |
| `PlotConfig` | the PLOT pilot: `enable` (bool, True), `format` (`"png"`; `"png"` / `"pdf"` / the pair, the `check_format` validator), `dpi` (150, 50..1200), `dir_name` (Path, `"plots"`; absolute = as-is, relative = under base_dir), `plots` (the PLOT_NAMES whitelist, default empty = no-op; the `check_plots` fail-fast + dedupe) |
| `AnalyticsConfig` | `detailed_report` list (default empty) + `report_file_name` (`model_analytics_report.txt`) |
| `CorpusConfig` | the SU_ANALYSIS corpus: `seed` (42 - the single seed), `total_positions` (1e7); the ec arrest is the root `empty_count` (D-281) |
| `SuAnalysisConfig` | the SU_ANALYSIS level: `enable` (bool, **FALSE** — opt-in), `corpus`, `su_pairs` (`List[Tuple[str, str]]`, empty; the `check_su_pairs` canonical-sort + dedupe), `rarity_thresholds` (`Optional[List[int]]`, None; the `check_rarity_thresholds` positive strictly-increasing, None / empty = the report's Section B off, D-292), `dir_name` (`su_analysis`), `report_file_name`, `export_csv` (False) |
| `AnovaConfig` | the ANOVA level: `enable` (bool, **FALSE** — opt-in), `top_k_adherence` (20, ge=1), `dir_name` (`anova`), `report_file_name`, `export_csv` (False) |
| `RegabDBConnectionConfig` | `dbname` / `user` / `host` required, `port=5432`, `password=None` |
| `RegabDataSetConfig` | the connection + `bid` + strict `status` (the ec is the root `empty_count`, D-283) |
| `PatternConfig` | `name` + `mask: Bitboard` (hex-string in, 16-hex out) |
| `PatternSetConfig` | `name` + `patterns: List[PatternConfig]` (default empty) |
| `MobilityFeatureConfig` | `name` + `mask` + `amask`, both Bitboard |
| `MobilitySetConfig` | `name` + `mobility_features` (default empty) |
| `FeatureSetConfig` | `name='NoNameFeatureSet'`, `intercept=False`, optional `mobility_set` / `pattern_set` |
| `StatModelConfig` | `frequency_cut_off` (PositiveInt=1), `logit_clipping` (0.05, 0<x<0.5), `ridge_regularization` (0.0, ge=0) |

## Architecture

- **The bitboard mask pair** — `PatternConfig.mask` and `MobilityFeatureConfig.mask` / `amask` are `Bitboard` (from
  board.py) behind a `mode="before"` `field_validator` (`bitboard_from_hex_str`) and a `field_serializer`
  (`f"{mask:016X}"`): in, a 16-digit hex string with NO 0x prefix (case-insensitive); out, uppercase 16-hex.
  `model_config` is `arbitrary_types_allowed`.
- **The strong-Wolfe invariant** — `OptimizationConfig` carries the L-BFGS defaults (`max_iters=500` ge=1, `m=50` ge=1,
  `c1=1e-4` 0<c1<1, `c2=0.9` 0<c2<1, `min_grad=(1e-5, 3)`, `min_p_fun_decrease=(1e-14, 7)`, `log_every_n` /
  `save_every_n` ge=0, `checkpoint_file` required, `high_performance_fg` default False: False keeps the classic
  vectorized-numpy fg closure, True builds the numba one — the GRADIENT worker reads it, rlm_03 / rlm_04 / rlm_05 /
  rlm_06 opt in) plus `check_wolfe_constants`, a `model_validator(mode="after")` enforcing `c2 > c1` (ValueError →
  ValidationError, both values in the message): the invariant is code, not docstring.
- **The top level** — `name`, `empty_count` (int, required, 0..60 — the single ec source for the SU corpus, the DB
   extraction (training + validation), and the saved model; D-280), `description`, `base_dir`, `output` (required);
   `use_cache=True`; `cache_files_prefix`
  default `"rlmwf_"` (the filename-prefix concatenation the state_machine closures implement); `regab_allow_duplicate`
  default `True` (True keeps every extracted row, False deduplicates by `(mover, opponent)` keeping the first occurrence
  — consumed by the POSITIONS / VLD `extract_and_prepare` path, the count is logged at both levels); `client_check_tol`
  default `1e-8` (the max absolute Y-space difference admitted between the residuals recomputed from the SAVED model
  file and the in-memory VALIDATE ones; `gt=0`); `plot` and `analytics` by default factory; the five required domain
  sections (`regab_data_set`, `feature_set`, `stat_model`, `optimization`, `validation_data_set`).
- **The analysis levels** — `su_analysis` + `anova`, both by default factory and both `enable` default **FALSE**
  (opt-in: the production configs leave the fields unset and get the no-op; the experiment configs rlm_05 / rlm_06 and
  the rlm_00 fixture opt in (su_analysis; anova is enabled by no shipped fixture)); `target_level: str` default
  `"last"` (a level name, case-insensitive, resolved fail-fast by the StateMachine, or "last" for the full pipeline;
  consumed by the facade's `run()` when no explicit target is given — a blank value means "last" too);
  `log_file_name: str | None` default `None` (the D-321 FINAL_LOG_PRINT output file name — relative to base_dir,
  the full run log at the maximum relevance; the absent entry keeps the level a no-op, the file NOT generated); and
  `check_su_pairs_feature_set`, a `model_validator(mode="after")` that fails fast when a `su_analysis.su_pairs` name is
  not in the `feature_set` (the mobility + the pattern names). The `SuAnalysisConfig.check_su_pairs` field validator
  does the canonical sort + the dedupe (each pair a sorted tuple, a repeated pair collapsed); the
  `check_rarity_thresholds` validator requires the positive strictly-increasing integers (None / empty = section off).
- **PlotConfig** — `enable: bool = True` (false makes the PLOT level a no-op even with names listed);
  `format: str = "png"` (`"png"`, `"pdf"` or a comma-separated pair — both; `check_format` normalizes whitespace,
  rejects unknown tokens, empty tokens and duplicates); `dpi: int = 150` (50..1200); `dir_name: Path = "plots"`
  (absolute as-is, it may live outside base_dir; relative resolves under base_dir — the resolution is the WORKER's job,
  the schema carries the Path); `plots: List[str] = []` (the WHITELIST: a listed name is generated, an unlisted one is
  skipped, an empty list is a no-op; `check_plots` fails fast on names outside `PLOT_NAMES`, imported from hlp_plot —
  the single source of truth — and deduplicates preserving order).
- **Strictness** — the 3-letter uppercase status is enforced in BOTH status lists (regab + validation data set); `ec`
  is 0..60; `frequency_cut_off` is a PositiveInt.

## Verified invariants

Pinned by `test_hlp_config_schemas.py` (27 tests, `TestRlmConfigSchemas`).

- The `model_dump_json` round-trip: `name` + `cache_files_prefix` are preserved (`test_model_dump_json_round_trip`); the
  mask's uppercase-16-hex round-trip is pinned by `test_pattern_mask_16_hex_parsed_and_serialized`.
- The mask parsing: `'0000000000000107'` (16-hex, no 0x) → Bitboard 0x107 → the same string back; the 0x-prefixed form
  and a non-hex mask ("ZZZZ") are REJECTED (`test_pattern_mask_16_hex_parsed_and_serialized`,
  `test_pattern_mask_0x_prefix_rejected`, `test_invalid_hex_mask_rejected`).
- The range and vocabulary gates: `ec` outside 0..60 rejected; lowercase / wrong-length status codes rejected
  (`test_ec_out_of_range_rejected`, `test_invalid_status_rejected`); `validation_data_set.status` is strict
  (`test_validation_dataset_status_strict`).
- The cross-field validator: `c1=0.9` + `c2=0.1` rejected, `c1=0.1` + `c2=0.9` accepted
  (`test_optimization_c2_lte_c1_rejected`, `test_optimization_c2_gt_c1_accepted`); `high_performance_fg` defaults to
  False and accepts True (`test_optimization_high_performance_fg`).
- The base-config bag: `properties` is in the `model_fields` of `ValidationDataSetConfig` AND `StatModelConfig`
  (`test_properties_field_in_model_fields`); the default `patterns` list is NOT shared across instances
  (`test_pattern_set_mutable_default_not_shared`).
- The required and defaulted fields: a missing `output` is rejected; `cache_files_prefix` defaults to `'rlmwf_'`
  (`test_missing_output_rejected`, `test_cache_files_prefix_default`).
- `client_check_tol`: default `1e-8`, an explicit override survives the dump round-trip, a non-positive tolerance is a
  ValidationError (`test_client_check_tol_default/override/nonpositive_rejected`).
- The PlotConfig defaults (`enable=True`, `format="png"`, `dpi=150`, the relative `"plots"` dir, the EMPTY whitelist) —
  `test_plot_defaults`; the format field: a lone token and the pair are accepted, whitespace normalizes away ("png, pdf"
  → "png,pdf") with the order preserved, `jpg` / `pdf,` / `""` / `png,png` are rejected
  (`test_plot_format_pair_and_normalization`, `test_plot_format_bad_rejected`); the whitelist: an unknown name is a
  fail-fast ValidationError, a repeated name is deduplicated with the order preserved, an absolute `dir_name` stays
  absolute and a relative one stays relative (`test_plot_unknown_name_rejected`, `test_plot_dedup_preserving_order`,
  `test_plot_dir_absolute_and_relative`).
- The analysis defaults: both `enable` FALSE, `target_level` "last", the corpus defaults (seed 42, 1e7), the
  empty `su_pairs`, `export_csv` False, `top_k_adherence` 20 (`test_su_analysis_defaults`); the canonical order + the
  dedupe (a repeated pair in any order collapses to one sorted tuple) and the fail-fast against the feature set
  (`test_su_pairs_canonical_dedupe`, `test_su_pairs_fail_fast`); a level name ("SU_ANALYSIS") survives in
  `target_level` (`test_target_level_field`) and the facade's `run()` honors it
  (`test_logistic_model::test_run_honors_the_config_target_level` + the real-config class).

## Open issues

None.

## Conventions

- Every nested config extends `LMBaseConfig` — the `properties` bag is present in all of them.
- Mutable defaults are `Field(default_factory=...)` — never bare literals.
- A mask is 16 hex digits, no 0x prefix — parser, docstring and field description stay in sync.
- Cross-field invariants live in a `model_validator`, not only in a description.

## Integration

- Consumed by `wrk_config` (`LMConfig(**raw)` after the json5 load).
- The Bitboard primitive + `bitboard_from_hex_str` come from `board.py`.
- The JSON5 fixture: `src/reversi/test/data/rlm_00.json`.
