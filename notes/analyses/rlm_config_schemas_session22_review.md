<!-- ARCHIVED — D-106 step 8 (the docs/ rewrite, 2026-09-04): the
     complete session-22 analysis (D-079) + the D-080 fix-campaign
     narrative moved out of docs/src/twolm/rlm_config_schemas.md
     per docs_rules.md §1/§4. This is a frozen historical record:
     it is never updated. Stale-in-current-context notes: (1) the
     "no dedicated suite" statement is pre-D-106-step-3 — commit
     585b2ad created src/twolm/test/test_rlm_config_schemas.py
     (13 tests, the §4 conversion of the probe E-section schema
     facts; the V1-V12 facts below are now pinned there, not in
     the probe's E section); (2) the "17 behaviour checks,
     re-pinned D-080" probe section was reduced to the current
     25-check probes/verify_lm_worker_config.py at step 3 (the
     schema-validation checks left as tests/c-deletions); (3) the
     V1-V12 "Verified behaviour" list is the pre-conversion pin
     map — see test_rlm_config_schemas.py for the current pins. -->

# twolm/rlm_config_schemas.py

Analysis date: 2026-08-30 — analysis session 22 (D-079). Fix
campaign D-080 applied 2026-08-30 (session 22, Roberto:
"correggile tutte").

The pydantic config DOMAIN of the RLM pipeline. One public entry
point, `ReversiLogisticModelConfig` (L188-207) — the JSON5 file
that lm_worker_config loads and validates (D-077) — over a small
tree of nested configs. Every nested config extends
`RLMBaseConfig`, whose `properties: dict[str, Any]` (default `{}`)
is a free-form extension bag (D-080 M3: `StatModelConfig`
included — it previously extended `BaseModel` directly and
lacked it).

## Suite status (session 22, D-079)

- No dedicated suite: covered by test_lm_worker_config's
  validation class (14/0/0) + the D-079 probe E section
  (re-pinned D-080 — 17 behaviour checks, independently
  re-derived, 0 mismatches).

## Architecture (207 lines, as of D-080)

- `RLMBaseConfig` (L47-48): `BaseModel` + `properties:
  dict[str, Any] = Field(default_factory=dict)`.
- `StatusString` (L50): `Annotated[str, Field(pattern=
  r"^[A-Z]{3}$")]` — exactly 3 uppercase letters. D-080 M3:
  moved above its first user (ValidationDataSetConfig).
- `ValidationDataSetConfig` (L52-54): `bid: List[NonNegativeInt]`,
  `status: List[StatusString]` (STRICT — D-080 M3; was loose
  `List[str]`).
- `OptimizationConfig` (L56-78): the L-BFGS knobs — `max_iters`
  (500, ge=1), `m` (50, ge=1), `c1` (1e-4, 0<c1<1), `c2` (0.9,
  0<c2<1, description "Must be > c1" — now ENFORCED by the
  `check_wolfe_constants` `model_validator(mode="after")`,
  D-080 R1), `min_grad` (1e-5, 3), `min_p_fun_decrease` (1e-14,
  7), `log_every_n` / `save_every_n` (ge=0), `checkpoint_file`
  (Path, required).
- `AnalyticsConfig` (L68-79): `detailed_report` list (default
  empty), `report_file_name` default.
- `RegabDBConnectionConfig` (L93-101): `dbname` / `user` / `host`
  required, `port: int = 5432`, `password: Optional[str] = None`.
- `RegabDataSetConfig` (L103-109): the connection + `bid:
  List[NonNegativeInt]` + `status: List[StatusString]` (STRICT) +
  `ec: int` (0..60).
- `PatternConfig` (L112-132): `name` + `mask: Bitboard` with a
  `mode="before"` field_validator (`bitboard_from_hex_str`) and a
  field_serializer `f"{mask:016X}"` (uppercase 16-hex);
  `arbitrary_types_allowed`; D-080 M1: the docstring example is
  now '0000000000000107' (16 digits, no 0x prefix) and the field
  description says so.
- `PatternSetConfig` (L134-139): `name` + `patterns:
  List[PatternConfig] = Field(default_factory=list)` (D-080 M4).
- `MobilityFeatureConfig` (L141-162): `name` + `mask` + `amask`,
  both Bitboard, same validator/serializer pair; D-080 M1: the
  docstring example corrected as in PatternConfig.
- `MobilitySetConfig` (L164-169): `name` + `mobility_features:
  List[MobilityFeatureConfig] = Field(default_factory=list)`
  (D-080 M4).
- `FeatureSetConfig` (L171-178): `name` default
  'NoNameFeatureSet', `intercept` default False, optional
  `mobility_set` / `pattern_set`.
- `StatModelConfig` (L180-186): `RLMBaseConfig` (D-080 M3 — was
  plain `BaseModel`, no properties bag): `frequency_cut_off`
  (PositiveInt = 1), `logit_clipping` (0.05, 0<x<0.5),
  `ridge_regularization` (0.0, ge=0).
- `ReversiLogisticModelConfig` (L188-207): `name`, `description`,
  `base_dir: Path`, `output: Path` (required), `use_cache: bool =
  True`, `cache_files_prefix = "rlmwf_"` ("Filename prefix for the
  level specific cache files" — the D-078 machine-level fix
  implements exactly this semantics), `regab_data_set` /
  `feature_set` / `stat_model` / `optimization` /
  `validation_data_set` (all required), `analytics` (default
  factory).

## Verified behaviour (D-079 probe E section, re-pinned D-080, 0 mismatches)

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
- V7 (E6/E6b): `c1=0.9` + `c2=0.1` → ValidationError (the
  cross-field `c2 > c1` validator, D-080 R1); `c1=0.1` +
  `c2=0.9` accepted.
- V8 (E8/E8b): `validation_data_set.status` REJECTS `['xyz']`
  (strict StatusString, D-080 M3) and accepts valid 3-letter
  codes.
- V9 (E9): `'properties'` is in BOTH
  `ValidationDataSetConfig.model_fields` and
  `StatModelConfig.model_fields` (D-080 M3).
- V10 (E10): the bare `[]` default of `PatternSetConfig.patterns`
  is NOT shared across instances (pydantic per-instance default
  copy) — M4 is safe but non-idiomatic.
- V11 (E11): missing `output` → ValidationError (required).
- V12 (E12): `cache_files_prefix` default `'rlmwf_'`.

## Issues — resolved (D-080)

- **R1 — FIXED (D-080).** `check_wolfe_constants`, a
  `model_validator(mode="after")` on `OptimizationConfig`, now
  enforces `c2 > c1` (raises ValueError → pydantic
  ValidationError, with both values in the message). The
  strong-Wolfe invariant is no longer docstring-only; re-pinned
  by probe E6/E6b. This gave the M2 import its job (below).

## Minor notes — resolved (D-080)

- M1 (E2b): FIXED — both `parse_hex_to_bitboard` docstrings now
  show `'0000000000000107'` ("16 digits, no 0x prefix"), and
  `PatternConfig`'s mask field description says the same
  (MobilityFeatureConfig's already did).
- M2 (E7): RESOLVED BY R1 — the `model_validator` import is now
  used by the `check_wolfe_constants` validator (re-pinned by
  probe E7).
- M3 (E8/E9): FIXED — `ValidationDataSetConfig.status` is now
  `List[StatusString]` (strict, symmetric with
  `RegabDataSetConfig`; `StatusString` moved to L50, above its
  first user); `StatModelConfig` now extends `RLMBaseConfig` (the
  properties bag is present, default `{}`). Re-pinned by probe
  E8/E8b/E9.
- M4 (E10): FIXED — both bare `[]` defaults replaced with
  `Field(default_factory=list)` (the file's own convention; the
  E10 not-shared pin still holds).

## Appendix — line reference

207 lines, as of D-080.

- L28-42: imports (pydantic L30-32 — `model_validator` now
  load-bearing, R1; board L37-38)
- L43: `__all__ = ['ReversiLogisticModelConfig']`
- L47-48: `RLMBaseConfig`
- L50: `StatusString` (D-080 M3: moved up)
- L52-54: `ValidationDataSetConfig` (M3 strict status)
- L56-78: `OptimizationConfig` (R1 check_wolfe_constants)
- L80-91: `AnalyticsConfig`
- L93-101: `RegabDBConnectionConfig`
- L103-109: `RegabDataSetConfig`
- L112-132: `PatternConfig` (M1 docstring)
- L134-139: `PatternSetConfig` (M4 default_factory)
- L141-162: `MobilityFeatureConfig` (M1 docstring)
- L164-169: `MobilitySetConfig` (M4 default_factory)
- L171-178: `FeatureSetConfig`
- L180-186: `StatModelConfig` (M3 RLMBaseConfig)
- L188-207: `ReversiLogisticModelConfig`
