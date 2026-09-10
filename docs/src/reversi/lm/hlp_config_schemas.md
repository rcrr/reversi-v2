# reversi/lm/hlp_config_schemas.py
The pydantic config DOMAIN of the LM pipeline: one public entry,
`LMConfig`, over a tree of nested configs — the
JSON5 document that wrk_config loads and validates. Every
nested config extends `LMBaseConfig`, whose `properties:
dict[str, Any]` bag (default `{}`) is a free-form extension point.
> State: D-149 · 2026-09-10 · suite 23/0/0

## API

| name | role |
|---|---|
| `LMConfig` | the only `__all__` name — the top-level config |
| `LMBaseConfig` | `BaseModel` + the `properties` bag; base of every nested config |
| `StatusString` | `Annotated[str, Field(pattern="^[A-Z]{3}$")]` — exactly 3 uppercase letters |
| `ValidationDataSetConfig` | `bid: List[NonNegativeInt]` + `status: List[StatusString]` (strict) |
| `OptimizationConfig` | the L-BFGS knobs + the `check_wolfe_constants` cross-field validator + `high_performance_fg` (bool, default False — the I-013 fg-variant flag) |
| `PlotConfig` | the PLOT level's pilot (D-149): `enable` (bool, default True), `format` (default `"png"`; `"png"`/`"pdf"`/the pair, the `check_format` validator), `dpi` (int 150, 50..1200), `dir_name` (Path, default `"plots"`; absolute = as-is, relative = under base_dir), `plots` (the whitelist of PLOT_NAMES, default empty = no-op; the `check_plots` fail-fast + dedupe validator) |
| `AnalyticsConfig` | `detailed_report` list (default empty) + `report_file_name` (default `model_analytics_report.txt`) |
| `RegabDBConnectionConfig` | `dbname`/`user`/`host` required, `port=5432`, `password=None` |
| `RegabDataSetConfig` | the connection + `bid` + strict `status` + `ec` (required, 0..60) |
| `PatternConfig` | `name` + `mask: Bitboard` (hex-string in, 16-hex out) |
| `PatternSetConfig` | `name` + `patterns: List[PatternConfig]` (default empty) |
| `MobilityFeatureConfig` | `name` + `mask` + `amask`, both Bitboard |
| `MobilitySetConfig` | `name` + `mobility_features` (default empty) |
| `FeatureSetConfig` | `name='NoNameFeatureSet'`, `intercept=False`, optional `mobility_set`/`pattern_set` |
| `StatModelConfig` | `frequency_cut_off` (PositiveInt=1), `logit_clipping` (0.05, 0<x<0.5), `ridge_regularization` (0.0, ge=0) |

## Architecture

- **The bitboard mask pair** — `PatternConfig.mask` and
  `MobilityFeatureConfig.mask`/`amask` are `Bitboard` (from
  board.py) behind a `mode="before"` `field_validator`
  (`bitboard_from_hex_str`) and a `field_serializer`
  (`f"{mask:016X}"`): in, a 16-digit hex string with NO 0x prefix
  (case-insensitive); out, uppercase 16-hex. The docstrings and
  the field descriptions say exactly that (the D-080 M1 fix
  removed the contradictory 0x-prefixed examples);
  `model_config` is `arbitrary_types_allowed`.
- **The strong-Wolfe invariant** — `OptimizationConfig` carries
  the L-BFGS defaults (`max_iters=500` ge=1, `m=50` ge=1,
  `c1=1e-4` 0<c1<1, `c2=0.9` 0<c2<1, `min_grad=(1e-5, 3)`,
  `min_p_fun_decrease=(1e-14, 7)`, `log_every_n`/`save_every_n`
  ge=0, `checkpoint_file` required, `high_performance_fg`
  default False — the I-013 fg-variant flag: False keeps the
  classic vectorized-numpy fg closure, True builds the numba
  high-performance one (the GRADIENT worker reads it; rlm_03 /
  rlm_04 opt in, D-145)) plus
  `check_wolfe_constants`, a `model_validator(mode="after")`
  that enforces `c2 > c1` (ValueError → ValidationError, both
  values in the message) — the invariant is code, not
  docstring (the D-080 R1 fix).
- **The top level** — `name`, `description`, `base_dir`,
  `output` (required); `use_cache=True`; `cache_files_prefix`
  default `"rlmwf_"` ("Filename prefix for the level specific
  cache files" — the filename-prefix concatenation the
  state_machine closures implement); `regab_allow_duplicate`
  default `True` (D-143: the duplicate game-positions policy —
  `True` keeps every extracted row, the pre-existing behaviour;
  `False` deduplicates by `(mover, opponent)` keeping the first
  occurrence; consumed by the POSITIONS/VLD `extract_and_prepare`
  compute path, the count is logged at both levels);
  `client_check_tol` default `1e-8` (D-148: the CLIENT_CHECK
  level tolerance — the max absolute Y-space difference admitted
  between the validation residuals recomputed from the SAVED model
  file and the in-memory VALIDATE residuals; `gt=0` — a
  non-positive tolerance is a ValidationError);
  `plot: PlotConfig` by default factory (D-149: the PLOT level's
  pilot — see below); the five required domain sections
  (`regab_data_set`, `feature_set`, `stat_model`, `optimization`,
  `validation_data_set`); `analytics` by default factory.
- **PlotConfig (D-149)** — `enable: bool = True` (the master
  switch: false makes the PLOT level a no-op, even with names
  listed — Roberto's ruling); `format: str = "png"` (the PNG-
  DEFAULT ruling — `"png"`, `"pdf"`, or a comma-separated pair
  (e.g. `"pdf,png"` — both); the `check_format` validator
  normalizes whitespace, rejects unknown tokens, empty tokens
  (the trailing comma) and duplicates); `dpi: int = 150`
  (50..1200, the png raster resolution); `dir_name: Path =
  "plots"` (an ABSOLUTE path is used as-is — it may live outside
  base_dir — a relative one resolves under base_dir; the
  resolution is the WORKER's job, the schema only carries the
  Path); `plots: List[str] = []` (the WHITELIST of plot names:
  a listed name is generated, an unlisted one is skipped, an
  empty list makes the PLOT level a no-op; the `check_plots`
  validator fails fast on names outside `PLOT_NAMES` (imported
  from hlp_plot — the single source of truth) and deduplicates
  preserving order).
- **Strictness** — the 3-letter uppercase status is enforced in
  BOTH status lists (regab + validation data set); `ec` is
  0..60; `frequency_cut_off` is a PositiveInt.

## Verified invariants

Pinned by `test_hlp_config_schemas.py` (23 tests,
`TestRlmConfigSchemas` — the step-3 §4 conversion of the probe
E-section + the D-149 PlotConfig section).

- The `model_dump_json` round-trip: the mask serializes back to
  uppercase 16-hex, `cache_files_prefix` preserved —
  `test_model_dump_json_round_trip`.
- `'0000000000000107'` (16-hex, no 0x) → Bitboard 0x107 →
  serialized back as the same string —
  `test_pattern_mask_16_hex_parsed_and_serialized`.
- The 0x-prefixed form is REJECTED; a non-hex mask ("ZZZZ") is
  rejected — `test_pattern_mask_0x_prefix_rejected`,
  `test_invalid_hex_mask_rejected`.
- `ec` outside 0..60 rejected — `test_ec_out_of_range_rejected`.
- Lowercase / wrong-length status codes rejected (StatusString)
  — `test_invalid_status_rejected`.
- `c1=0.9` + `c2=0.1` rejected, `c1=0.1` + `c2=0.9` accepted (the
  cross-field validator) — `test_optimization_c2_lte_c1_rejected`,
  `test_optimization_c2_gt_c1_accepted`.
- `high_performance_fg` defaults to False and accepts True
  (I-013) — `test_optimization_high_performance_fg`.
- `validation_data_set.status` is strict (rejects `'xyz'`,
  accepts valid codes) — `test_validation_dataset_status_strict`.
- `'properties'` is in the `model_fields` of
  `ValidationDataSetConfig` AND `StatModelConfig` —
  `test_properties_field_in_model_fields`.
- The default `patterns` list is NOT shared across instances —
  `test_pattern_set_mutable_default_not_shared`.
- Missing `output` rejected (required) —
  `test_missing_output_rejected`.
- The `cache_files_prefix` default is `'rlmwf_'` —
  `test_cache_files_prefix_default`.
- The `client_check_tol` default is `1e-8` (D-148), an explicit
  override survives the dump round-trip, and a non-positive
  tolerance is a ValidationError —
  `test_client_check_tol_default/override/nonpositive_rejected`.
- The PlotConfig defaults: `enable=True`, `format="png"` (the
  PNG-default ruling), `dpi=150`, the relative `"plots"` dir, the
  EMPTY whitelist (the no-op pilot) —
  `test_plot_defaults`.
- The format field: a lone token and the pair are accepted;
  whitespace normalizes away ("png, pdf" → "png,pdf"), the order
  is preserved; `jpg` / `pdf,` / `""` / `png,png` are all
  rejected — `test_plot_format_pair_and_normalization`,
  `test_plot_format_bad_rejected`.
- The whitelist: an unknown name is a fail-fast ValidationError
  (the PLOT_NAMES vocabulary, D-149); a repeated name is
  deduplicated, order preserved; an absolute dir_name stays
  absolute, a relative one stays relative —
  `test_plot_unknown_name_rejected`,
  `test_plot_dedup_preserving_order`,
  `test_plot_dir_absolute_and_relative`.

## Open issues

None.

## Conventions

- Every nested config extends `LMBaseConfig` — the `properties`
  bag is present in all of them (the D-080 M3 fix brought
  `StatModelConfig` into line).
- Mutable defaults are `Field(default_factory=...)` — never bare
  literals.
- A mask is 16 hex digits, no 0x prefix — parser, docstring and
  field description stay in sync.
- Cross-field invariants live in a `model_validator`, not only in
  a description.

## Integration

- Consumed by `wrk_config` (`LMConfig
  (**raw)` after the json5 load).
- The Bitboard primitive + `bitboard_from_hex_str` come from
  `board.py`.
- The JSON5 fixture: `src/reversi/test/data/rlm_00.json`.
