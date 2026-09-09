# reversi/lm/hlp_config_schemas.py
The pydantic config DOMAIN of the LM pipeline: one public entry,
`LMConfig`, over a tree of nested configs — the
JSON5 document that wrk_config loads and validates. Every
nested config extends `LMBaseConfig`, whose `properties:
dict[str, Any]` bag (default `{}`) is a free-form extension point.
> State: D-143 · 2026-09-09 · suite 13/0/0

## API

| name | role |
|---|---|
| `LMConfig` | the only `__all__` name — the top-level config |
| `LMBaseConfig` | `BaseModel` + the `properties` bag; base of every nested config |
| `StatusString` | `Annotated[str, Field(pattern="^[A-Z]{3}$")]` — exactly 3 uppercase letters |
| `ValidationDataSetConfig` | `bid: List[NonNegativeInt]` + `status: List[StatusString]` (strict) |
| `OptimizationConfig` | the L-BFGS knobs + the `check_wolfe_constants` cross-field validator |
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
  ge=0, `checkpoint_file` required) plus
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
  compute path, the count is logged at both levels); the five
  required domain sections (`regab_data_set`, `feature_set`,
  `stat_model`, `optimization`, `validation_data_set`); `analytics`
  by default factory.
- **Strictness** — the 3-letter uppercase status is enforced in
  BOTH status lists (regab + validation data set); `ec` is
  0..60; `frequency_cut_off` is a PositiveInt.

## Verified invariants

Pinned by `test_hlp_config_schemas.py` (13 tests,
`TestRlmConfigSchemas` — the step-3 §4 conversion of the probe
E-section).

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
