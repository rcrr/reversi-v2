# reversi/test/test_hlp_config_schemas.py
The hlp_config_schemas config-domain suite: the deterministic pydantic unit behaviour of the LM config schemas — the
mask parsing, the ec/status constraints, the cross-field validator, the client_check_tol + the plot sections, the
su_analysis / effect_size opt-in. 1 class / 27 tests / no PERF gates / no database (the schemas validate in memory
only).

## Coverage

| group | what it pins |
|---|---|
| the dump round-trip | `test_model_dump_json_round_trip`: the full config round-trips via `model_dump_json`, the name survives, `cache_files_prefix` keeps `'rlmwf_'` |
| the pattern mask | `test_pattern_mask_16_hex_parsed_and_serialized` (16-hex no 0x → Bitboard 0x107 → back to the uppercase 16-hex string), `test_pattern_mask_0x_prefix_rejected` (the `'0x…'` form → ValidationError), `test_invalid_hex_mask_rejected` ("ZZZZ" in the full config → ValidationError) |
| the regab constraints | `test_ec_out_of_range_rejected` (ec 99 and -1 → ValidationError), `test_invalid_status_rejected` (lowercase `'cms'` and the 4-letter `'CMSX'` both rejected — the strict StatusString) |
| the cross-field validator + the fg flag | `test_optimization_c2_lte_c1_rejected` (c1=0.9 + c2=0.1) and `test_optimization_c2_gt_c1_accepted` (c1=0.1 + c2=0.9) — the strong-Wolfe `check_wolfe_constants`; `test_optimization_high_performance_fg` (the flag defaults False and accepts True) |
| the client_check_tol field | `test_client_check_tol_default` (the fixture does not set it → 1e-8), `test_client_check_tol_override` (1e-9 survives validation AND the `model_dump_json` round-trip — the field travels with the normalized dump, hence the model-file size-band growth), `test_client_check_tol_nonpositive_rejected` (0.0 and −1e-8 → ValidationError, the `gt=0` constraint) |
| the PlotConfig section | `test_plot_defaults` (the fixture does not set it → enable True, format `"png"`, dpi 150, the relative `"plots"` dir, the EMPTY whitelist — the no-op pilot), `test_plot_format_pair_and_normalization` (`"pdf"` / `"pdf,png"` accepted; `"png, pdf"` normalizes to `"png,pdf"`, order preserved), `test_plot_format_bad_rejected` (`"jpg"`, `"pdf,"` (empty token), `""`, `"png,png"` (duplicate) all → ValidationError), `test_plot_unknown_name_rejected` (a name outside `PLOT_NAMES` → ValidationError, the fail-fast typo guard), `test_plot_dedup_preserving_order` (`["parity", "resid_qq", "parity"]` → `["parity", "resid_qq"]`), `test_plot_dir_absolute_and_relative` (an absolute dir_name stays absolute, a relative one stays relative — the WORKER resolves it) |
| strictness + the bag | `test_validation_dataset_status_strict` (`'xyz'` rejected, `["CMS", "CMR"]` accepted) and `test_properties_field_in_model_fields` (`'properties'` in BOTH `StatModelConfig` and `ValidationDataSetConfig` model_fields) |
| the mutable default | `test_pattern_set_mutable_default_not_shared` (two `PatternSetConfig` instances: append to one leaves the other empty) |
| required + default | `test_missing_output_rejected` (`output` required) and `test_cache_files_prefix_default` (absent → `'rlmwf_'`) |
| the su_analysis / effect_size config | `test_su_analysis_defaults` (the opt-in: the `su_analysis.enable` + the `effect_size.enable` default FALSE, the `target_level` default "last", the corpus defaults seed 42 / 1e7 / ec 20, the empty su_pairs, the export_csv default False, the top_k_adherence default 20), `test_su_pairs_canonical_dedupe` (the repeated pair (any order) → one sorted tuple), `test_su_pairs_fail_fast` (a name not in the feature set → ValidationError at the CONFIG level), `test_target_level_field` (a level name "SU_ANALYSIS" survives, the default "last") |

## Goldens pinned

- The mask pair: `"0000000000000107"` ↔ Bitboard `0x107` ↔ the uppercase 16-hex serialization — the 16-digits-no-0x
  contract.
- `cache_files_prefix == "rlmwf_"` — both the round-trip and the absent-field default pin the same value.
- The rejection literals: `"0x0000000000000107"`, `"ZZZZ"`, `"cms"`, `"CMSX"`, `"xyz"`, ec 99 and ec -1.
- The accepted pair `c1=0.1` / `c2=0.9` (the boundary the cross-field validator allows) against the rejected `c1=0.9` /
  `c2=0.1`.

## Conventions

- The base payload is the shared `rlm_00.json` fixture, loaded through `json5` and deep-copied per test by the
  `_cfg_dict(mutate=…)` helper — each test mutates its own copy.
- `subTest` for the multi-value cases (the two ec values, the two bad statuses).

## Integration

- Exercises `hlp_config_schemas.py` in memory only — no worker, no machine, no DB (the `SKIP_REGAB_DB` gate is not
  needed).
- The worker-level pins of the ec/status/hex-mask constraints (through the CONFIG worker end-to-end) live in
  `test_wrk_config.py` — the docstring cross-reference is deliberate: schema-level here, worker-level there.
