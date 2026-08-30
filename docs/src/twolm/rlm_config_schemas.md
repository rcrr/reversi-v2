# twolm/rlm_config_schemas.py

Analysis date: 2026-08-30 — analysis session 22 (D-079).

The pydantic config DOMAIN of the RLM pipeline. One public entry
point, `ReversiLogisticModelConfig` (L176-195) — the JSON5 file
that lm_worker_config loads and validates (D-077) — over a small
tree of nested configs. Every nested config extends
`RLMBaseConfig`, whose `properties: dict[str, Any]` (default `{}`)
is a free-form extension bag — EXCEPT `StatModelConfig`, which
extends `BaseModel` directly and lacks it (M3).

## Suite status (session 22, D-079)

- No dedicated suite: covered by test_lm_worker_config's
  validation class (14/0/0) + the D-079 probe E section (15
  behaviour checks, independently re-derived, 0 mismatches).

## Architecture (195 lines)

- `RLMBaseConfig` (L47-48): `BaseModel` + `properties:
  dict[str, Any] = Field(default_factory=dict)`.
- `ValidationDataSetConfig` (L50-52): `bid: List[NonNegativeInt]`,
  `status: List[str]` (LOOSE — M3).
- `OptimizationConfig` (L54-66): the L-BFGS knobs — `max_iters`
  (500, ge=1), `m` (50, ge=1), `c1` (1e-4, 0<c1<1), `c2` (0.9,
  0<c2<1, description "Must be > c1" — R1: nothing enforces it),
  `min_grad` (1e-5, 3), `min_p_fun_decrease` (1e-14, 7),
  `log_every_n` / `save_every_n` (ge=0), `checkpoint_file`
  (Path, required).
- `AnalyticsConfig` (L68-79): `detailed_report` list (default
  empty), `report_file_name` default.
- `RegabDBConnectionConfig` (L81-89): `dbname` / `user` / `host`
  required, `port: int = 5432`, `password: Optional[str] = None`.
- `StatusString` (L91): `Annotated[str, Field(pattern=r"^[A-Z]{3}$")]`
  — exactly 3 uppercase letters.
- `RegabDataSetConfig` (L93-100): the connection + `bid:
  List[NonNegativeInt]` + `status: List[StatusString]` (STRICT) +
  `ec: int` (0..60).
- `PatternConfig` (L102-121): `name` + `mask: Bitboard` with a
  `mode="before"` field_validator (`bitboard_from_hex_str`) and a
  field_serializer `f"{mask:016X}"` (uppercase 16-hex);
  `arbitrary_types_allowed`.
- `PatternSetConfig` (L123-128): `name` + `patterns:
  List[PatternConfig] = []` (bare mutable default — M4).
- `MobilityFeatureConfig` (L130-150): `name` + `mask` + `amask`,
  both Bitboard, same validator/serializer pair.
- `MobilitySetConfig` (L152-157): `name` + `mobility_features:
  List[MobilityFeatureConfig] = []` (M4).
- `FeatureSetConfig` (L159-166): `name` default
  'NoNameFeatureSet', `intercept` default False, optional
  `mobility_set` / `pattern_set`.
- `StatModelConfig` (L168-174): plain `BaseModel` (no properties
  bag — M3): `frequency_cut_off` (PositiveInt = 1),
  `logit_clipping` (0.05, 0<x<0.5), `ridge_regularization` (0.0,
  ge=0).
- `ReversiLogisticModelConfig` (L176-195): `name`, `description`,
  `base_dir: Path`, `output: Path` (required), `use_cache: bool =
  True`, `cache_files_prefix = "rlmwf_"` ("Filename prefix for the
  level specific cache files" — the D-078 machine-level fix
  implements exactly this semantics), `regab_data_set` /
  `feature_set` / `stat_model` / `optimization` /
  `validation_data_set` (all required), `analytics` (default
  factory).

## Verified behaviour (D-079 probe E section, 0 mismatches)

- V1 (E1): round-trip via `model_dump_json` — the mask serializes
  back to uppercase 16-hex, `cache_files_prefix` preserved.
- V2 (E2): `'0000000000000107'` (16-hex, no 0x) → Bitboard 0x107;
  serialized as `'0000000000000107'`.
- V3 (E2b): `'0x0000000000000107'` → REJECTED (ValidationError) —
  the docstring example contradicts the parser (M1).
- V4 (E3): `'ZZZZ'` mask → ValidationError.
- V5 (E4a/E4b): `ec` 99 / -1 → ValidationError (0..60 enforced).
- V6 (E5a/E5b): status `'cms'` / `'CMSX'` → ValidationError
  (StatusString strict).
- V7 (E6): `c1=0.9` + `c2=0.1` ACCEPTED — no cross-field
  `c2 > c1` validator (R1).
- V8 (E8): `validation_data_set.status` accepts `['xyz']` — loose
  `List[str]`, asymmetric with `RegabDataSetConfig` (M3).
- V9 (E9): `'properties'` is in
  `ValidationDataSetConfig.model_fields` but NOT in
  `StatModelConfig.model_fields` (M3).
- V10 (E10): the bare `[]` default of `PatternSetConfig.patterns`
  is NOT shared across instances (pydantic per-instance default
  copy) — M4 is safe but non-idiomatic.
- V11 (E11): missing `output` → ValidationError (required).
- V12 (E12): `cache_files_prefix` default `'rlmwf_'`.

## Issues — OPEN (awaiting Roberto's call)

- **R1 (E6):** `OptimizationConfig.c2`'s description says "Must be
  > c1", but NO cross-field validator exists — `(c1=0.9, c2=0.1)`
  validates fine. For the L-BFGS strong-Wolfe line search,
  `c1 < c2` is load-bearing. Candidate fix: a
  `model_validator(mode="after")` on `OptimizationConfig` — which
  would give the currently-unused `model_validator` import (M2) a
  job.

## Minor notes — OPEN (awaiting Roberto's call)

- M1 (E2b): the `parse_hex_to_bitboard` docstring example
  (`'0x0000000000000107'`) contradicts the parser —
  `bitboard_from_hex_str` requires exactly 16 hex chars with NO
  0x prefix (the `MobilityFeatureConfig` field descriptions say
  "no 0x prefix, just 16 digits"; `PatternConfig`'s does not).
  Affects BOTH `PatternConfig.parse_hex_to_bitboard` (L115) and
  `MobilityFeatureConfig.parse_hex_to_bitboard` (L144).
- M2 (E7): `model_validator` imported from pydantic (L32) but
  never used.
- M3 (E8/E9): the asymmetries — `ValidationDataSetConfig.status`
  loose `List[str]` vs `RegabDataSetConfig.status` strict
  `List[StatusString]`; `StatModelConfig` extends `BaseModel`
  directly and lacks the `RLMBaseConfig` properties bag.
- M4 (E10): bare mutable defaults (`PatternSetConfig` L128,
  `MobilitySetConfig` L157) — safe by pydantic's per-instance
  default copying (pinned E10), but the file's own convention is
  `Field(default_factory=...)` (used in RLMBaseConfig,
  AnalyticsConfig, ReversiLogisticModelConfig.analytics).

## Appendix — line reference

195 lines, as of D-079.

- L28-43: imports (pydantic L30-32 — M2 `model_validator`, board
  L38-39)
- L43: `__all__ = ['ReversiLogisticModelConfig']`
- L47-48: `RLMBaseConfig`
- L50-52: `ValidationDataSetConfig` (M3 loose status)
- L54-66: `OptimizationConfig` (R1 c2, M2 candidate fix)
- L68-79: `AnalyticsConfig`
- L81-89: `RegabDBConnectionConfig`
- L91: `StatusString`
- L93-100: `RegabDataSetConfig` (M3 strict status)
- L102-121: `PatternConfig` (M1 docstring L115)
- L123-128: `PatternSetConfig` (M4 L128)
- L130-150: `MobilityFeatureConfig` (M1 docstring L144)
- L152-157: `MobilitySetConfig` (M4 L157)
- L159-166: `FeatureSetConfig`
- L168-174: `StatModelConfig` (M3)
- L176-195: `ReversiLogisticModelConfig`
