# reversi/test/test_hlp_config_schemas.py
The first test module of the rlm_config_schemas config domain —
created at D-106 step 3 as the probe_rules §4 conversion of the
verify_lm_worker_positions probe E section (the probe keeps only
its E7 source-text pin — source inspections stay probes per §4).
1 class / 13 tests / no PERF gates / no database (the schemas
validate in memory only).
> State: D-106 · 585b2ad · 2026-09-04 · suite 13/0/0

## Coverage

| group (the former probe E checks) | what it pins |
|---|---|
| E1 — the dump round-trip | `test_model_dump_json_round_trip`: the full config round-trips via `model_dump_json`, the name survives, `cache_files_prefix` keeps `'rlmwf_'` |
| E2/E2b/E3 — the pattern mask | `test_pattern_mask_16_hex_parsed_and_serialized` (16-hex no 0x → Bitboard 0x107 → back to the uppercase 16-hex string), `test_pattern_mask_0x_prefix_rejected` (the `'0x…'` form → ValidationError), `test_invalid_hex_mask_rejected` ("ZZZZ" in the full config → ValidationError) |
| E4/E5 — the regab constraints | `test_ec_out_of_range_rejected` (ec 99 and -1 → ValidationError), `test_invalid_status_rejected` (lowercase `'cms'` and the 4-letter `'CMSX'` both rejected — the strict StatusString) |
| E6 — the cross-field validator | `test_optimization_c2_lte_c1_rejected` (c1=0.9 + c2=0.1) and `test_optimization_c2_gt_c1_accepted` (c1=0.1 + c2=0.9) — the strong-Wolfe `check_wolfe_constants` |
| E8/E9 — strictness + the bag | `test_validation_dataset_status_strict` (`'xyz'` rejected, `["CMS", "CMR"]` accepted) and `test_properties_field_in_model_fields` (`'properties'` in BOTH `StatModelConfig` and `ValidationDataSetConfig` model_fields) |
| E10 — the mutable default | `test_pattern_set_mutable_default_not_shared` (two `PatternSetConfig` instances: append to one leaves the other empty) |
| E11/E12 — required + default | `test_missing_output_rejected` (`output` required) and `test_cache_files_prefix_default` (absent → `'rlmwf_'`) |

## Goldens pinned

- The mask pair: `"0000000000000107"` ↔ Bitboard `0x107` ↔ the
  uppercase 16-hex serialization — the 16-digits-no-0x contract.
- `cache_files_prefix == "rlmwf_"` — both the round-trip and the
  absent-field default pin the same value.
- The rejection literals: `"0x0000000000000107"`, `"ZZZZ"`,
  `"cms"`, `"CMSX"`, `"xyz"`, ec 99 and ec -1.
- The accepted pair `c1=0.1` / `c2=0.9` (the boundary the
  cross-field validator allows) against the rejected
  `c1=0.9` / `c2=0.1`.

## Conventions

- The base payload is the `rlm_00.json` fixture (the same one the
  probe used), loaded through `json5` and deep-copied per test by
  the `_cfg_dict(mutate=…)` helper — each test mutates its own
  copy.
- `subTest` for the multi-value cases (the two ec values, the
  two bad statuses).

## Integration

- Exercises `rlm_config_schemas.py` in memory only — no worker,
  no machine, no DB (the `SKIP_REGAB_DB` gate is not needed).
- The worker-level pins of the ec/status/hex-mask constraints
  (through the CONFIG worker end-to-end) live in
  `test_wrk_config.py` — the docstring cross-reference is
  deliberate: schema-level here, worker-level there.
