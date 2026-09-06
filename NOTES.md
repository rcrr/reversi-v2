# NOTES.md — entry point

## Format rules (rigid — follow when editing this file)

The rigid format rules for this file live in notes/rules.md —
the "Roles of the notes files" section, NOTES.md bullet.
Consult it before editing.

## Project

File-by-file modernization of Roberto Corradini's Reversi engine
(18-year-old repo). This workspace is a staging area: only files
under active work live here. Full-repo restructure: planned, not
now (I-001; see notes/decisions.md).

## Inventory

| Item | Status | Note |
|---|---|---|
| src/twolm/board.py | analyzed 2026-08-25 (session 1); modified by the fix campaign (T20, T22, T25, T36, T37, T38); all 5 real issues resolved: R1 (D-017), R2 (T20 annotation), R3 (D-018), R4 (T24 test pin + TestPydanticVersion), R5 (NumPy ≥ 2.0 declared in pyproject.toml, D-011); suite 201/0/12 GREEN (test_board.py) | docs/src/twolm/board.md |
| src/twolm/test/test_board.py | analyzed 2026-08-25 (session 2); 11 defects + 8 docstring/behaviour mismatches documented; fix campaign COMPLETE 2026-08-26 (session 3): P0 + P1 + full P2 batch (T26–T35, one commit per Roberto's "Facciamoli tutti, un solo commit"), suite 157 → 193 GREEN throughout; header 'environmeant' typo fixed 2026-08-29 (D-050, with test_feature T4), remaining grammar nit reported-only; suite 201/0/12 GREEN | docs/src/twolm/test/test_board.md |
| src/twolm/pattern.py | analyzed 2026-08-27 (session 4, D-019 review-only); all real issues resolved: R1 (D-020) principal = numerically lowest orbit mask (unique representative) + regression test; R2-R7 doc/hygiene fixes (D-021); R8 closed as little-endian-only platform note (D-022); minor sweep complete 2026-08-27 (session 7): 19/19 items (D-023, D-024, D-025 + fail-fast checks, constant rename, doc/hygiene/API fixes); D-032 (2026-08-28, session 10): Burnside attributes n_invariant_configs / n_unique_configs; suite 65/0/3 GREEN (test_pattern.py) | docs/src/twolm/pattern.md |
| src/twolm/test/test_pattern.py | analyzed 2026-08-27 (session 8): 12 classes / 50 tests / 3 PERF; 21/21 goldens independently re-derived (0 mismatches); 16 defects T1-T16 + T17 (sqa8/sqh1 fixtures swapped names/values) documented; fix campaign CLOSED: P0 (D-026-028, 6da0803) + P1 (D-029/030/031: row independence both public indexing APIs + EDGE 6561-entry dict pin) + P2 hygiene (D-033: T1-T7, T15-T16; T19 found + fixed in T2) + P2 breadth (D-034: T11-T14 + T17); T18 noted-only, M1 deferred; suite 65/0/3 GREEN | docs/src/twolm/test/test_pattern.md |
| src/twolm/mobility.py | analyzed 2026-08-28 (session 10): Mobility/MobilitySet + popcount64 SWAR + Numba kernel; index formula + n_configurations (distinct index values) + sorted-order columns + hash verified vs independent ground truth (V1-V8, 200-position differential, popcount on 200,010 values); R1-R6 fix batch applied (D-035: docstrings + column-order contract + popcount64 test-helper + dead imports + property/repr alignment + n_instances as-is), no behavior change; M1-M5 disposed (D-036: M1 glossary shipped, M2/M3/M5 left as-is, M4 corrected — no PERF gates in any suite); suite 26/0/1 GREEN (test_mobility.py) | docs/src/twolm/mobility.md |
| src/twolm/test/test_mobility.py | analyzed 2026-08-28 (session 10): 2 classes / 23 tests / 1 PERF; 13 verified facts V1-V13 (0 mismatches, incl. 31-line popcount table and [53,13,66] golden); 9 defects T1-T9 documented; fix campaign CLOSED the same day (D-037: T1-T9, per-item approvals, single batch commit — P0 __repr__ goldens, P1 multi-position row independence, P2 hygiene/breadth incl. pinned hash literal 2e553593...208a94); suite 23 → 26, GREEN 26/0/1 | docs/src/twolm/test/test_mobility.md |
| src/twolm/feature.py | analyzed 2026-08-28 (session 11): Feature (blocked __new__ + 3 factories) + FeatureSet (intercept/mset/pset composition, sorted-order features, hash over child hash hex strings); all goldens re-derived independently (V1-V8, zero mismatches: 3x10 index matrix, 13 orbit sizes, 3 pinned hashes); R1-R4 fix batch applied (D-038: sha3_256 doc fix + column-layout contract + __init__ docstring + dead imports); M1 applied (D-039), M2 applied (D-040), M3 left as-is (D-041, follow-up I-007), M4 applied (D-042) — all disposed; suite 19/0/1 (19 run + 1 PERF skip); D-106 step-10 re-read: OPEN R1 (the BeforeValidator import never referenced — the dtype check rides on the imported IndexArray alias, pattern.py L74; dead since b51bea6, R4/D-038 removed only the typing imports) — FIXED per Roberto's "fiaas ora" ruling (D-110, de01cf2, 2026-09-04: the import line now carries only validate_call, ConfigDict) | docs/src/twolm/feature.md |
| src/twolm/test/test_feature.py | analyzed 2026-08-28 (session 11): 4 classes / 14 tests / 1 PERF; 9 verified facts W1-W9 (0 mismatches, incl. 3x10 matrix and f5663932 hash literal); 9 defects T1-T9 documented (dead if-False block w/ never-imported position_print, 6 dead imports, header grammar + "environmeant" typo, no names-order assert, partial-None FeatureSet untested, Feature repr/eq untested, cosmetic import-time spaces, no full print_summary golden); T campaign CLOSED 2026-08-29 (D-043..D-050: T6, T1, T2, T3, T5, T7, T9, T4 — both files; T8 left as-is); suite 19/0/1 (19 run + 1 PERF skip; the file is unchanged since a5db33b) | docs/src/twolm/test/test_feature.md |
| src/twolm/binio.py | analyzed 2026-08-29 (session 14); T1-T4 fix batch applied (D-051: lz4 in pyproject.toml, dead Path import removed, "Aauthor" → "Author", test_unknown_type_code_raises added); 15 verified facts V1-V15 (0 mismatches); D-095 (2026-09-01, session 25, Roberto: "procedi!"): the empty-sidecar-suffix guard — with `suffix=""` the sidecar path BE the content file, which both write paths truncated and overwrote (data loss, empirically confirmed pre-fix; verify raised a confusing BinaryFormatError); all 3 sidecar entry points now raise ValueError (the writer fails fast in __init__ before the file is opened — the empty suffix has no legitimate use, checksum=False is the no-sidecar knob); docstrings updated; 16 verified facts V1-V16 (V16 the guard + the pre-fix clobbering); suite 48/0/0 GREEN (test_binio 45 + test_usage_binio 3) | docs/src/twolm/binio.md |
| src/twolm/test/test_binio.py | analyzed 2026-08-29 (session 14, with test_usage_binio.py); T4 applied (D-051): ArrayTest now 8 tests (42 total in test_binio); D-095: 3 empty-suffix guard tests added (Sha3_256SidecarTest: write raises + content intact, verify raises; AutoChecksumTest: constructor raises before the file is opened — the file must not exist); suite 45 → 48, GREEN 48/0/0, no PERF | docs/src/twolm/test/test_binio.md |
| src/twolm/regab.py | analyzed 2026-08-29 (session 15); T1-T7 fix batch applied (D-052: "Aauthor" → "Author", dead typing imports, psycopg2/pandas/python-dotenv in pyproject.toml, _validate_db_fields DB query deferred, SKIP_REGAB_DB=1 gate, _validate_where_clause SQL-injection guard); 5 verified facts V1-V5 (0 mismatches, sha3_256 golden); suite 37/0/0 GREEN (35 DB + 2 mocked; SKIP_REGAB_DB=1 → 35 skip) | docs/src/twolm/regab.md |
| src/twolm/test/test_regab.py | analyzed 2026-08-29 (session 15); T5+T6+T7 applied (D-052): dead imports removed, SKIP_REGAB_DB gate, 4 SQL-injection tests added (TestRegabGPAsDF 12 → 16); suite 33 → 37/0/0 GREEN; D-085: the .env load + the checksum-test mkdtemp re-anchored to the shared twolm.test.paths module | docs/src/twolm/test/test_regab.md |
| src/twolm/opt_lbfgs.py | analyzed 2026-08-29 (session 16); T1-T7 fix batch applied (D-053: RuntimeException → RuntimeError hard bug, CURVATURE_THRESHOLD used, low_progress_count spelling, hermite None fallthrough, save_fn 7-param hint+docstring, fractional docstring); 5 verified facts V1-V5 (0 mismatches); suite 13/0/0 GREEN | docs/src/twolm/opt_lbfgs.md |
| src/twolm/test/test_opt_lbfgs.py | analyzed 2026-08-29 (session 16); T7 applied + 9 new tests (D-053): TestLBFGSInputValidation (3), TestFixedSizeMaxList (4, incl. T1 regression), TestTwoLoopRecursion (2); suite 4 → 13/0/0 GREEN | docs/src/twolm/test/test_opt_lbfgs.md |
| src/twolm/state_machine.py | analyzed 2026-08-29 (session 19): generic pipeline orchestrator (Workers up/down + Context + logging/history/CSV), pure stdlib, no new deps; 17 verified facts V1-V17 (0 mismatches, 54-check probe); R1 FIXED (D-057: Verbosity.VERY_LOW=4 added, NONE=5, `>=` gate unchanged — HIGH..LOW byte-identical, NONE truly silent, old ERROR-only behaviour kept as VERY_LOW); R2 FIXED (D-058: LogEntry now a frozen dataclass — attribute access, asdict() for file/DB dumps, show_event_log migrated, observable behaviour unchanged; test-file datetime import now used → M2/T11 resolved); R3 RESOLVED as intentional sentinel (D-059: documented in class + move_to_step docstrings, pinned by test_worker_zero_is_sentinel_never_executed, no behaviour change — the RLM 'CREATED' worker runs outside the machine, logistic_model will make it explicit); R4 RESOLVED (D-060: keep + document + pin — failure semantics in move_to_step docstring, recovery = move to k-1 (k's down) then up; machine domain-agnostic, exception re-raised for the domain worker; pinned by test_retry_after_failure_skips_failed_step, closes T6); R5 RESOLVED (D-061: __init__ rejects duplicate worker names, case-insensitive ValueError fail-fast — the real ambiguity was name resolution in move_to_step itself, so uniqueness enforced instead of an index fix; move_to_last unchanged, name dispatch now unambiguous; closes M12); T2 coverage added (D-062: TestContextInjection 7 tests; M8 extended with the implicit separator contract); T3 coverage added (D-063: TestDisplayGoldens 3 end-to-end display goldens, frozen clock); T4 coverage added (D-064: 3 move_to_last tests — happy path, intermediate position, single-worker sentinel no-op); T5 fixed (D-065: CSV test rewritten — exact header names, ISO-8601 +00:00, duration identity, artifact under build/tmp; new house rule: test files only in workspace_root/build/tmp, removed afterwards); T7 pinned (D-066: 2 tests — bool accepted as int step, np.int64 TypeError); T8 + T9 pinned (D-067: 5 tests — current_worker_name live view + UNDEFINED, StepMove field content incl. aware-UTC timestamps, duration identity, finally-append on failure); M-sweep batch 1 applied (D-068: M1 dead Any import removed, M4 _run_step direction dispatch explicit (elif 'down' + ValueError), M7 __repr__ on Worker + StateMachine (lightweight), M10 CSV export creates missing parent dirs); M-sweep batch 2 applied (D-069: M3 bool rejected — strict gate, TypeError same message, test rewritten to rejection; M5 cache helpers renamed *_for_current_level (the 2 ported domain call sites + RLMContext's 2 field names renamed D-074 — follow-up closed); M8 cache prefix pathlib join — no more silent gluing; M11 @validate_call on Worker init/up/down + SM init/log_event/export + move_to_step via strict private impl re-raising the pinned TypeError; pydantic now a module dep, already in pyproject); ALL T ITEMS CLOSED; M-sweep COMPLETE (D-068: M1, M4, M7, M10; D-069: M3, M5, M8, M11; D-070: M6 print cleanup — enum names + UTC marker on the live line, UTC header / 2-digit step / RELEVANCE name column / 66-underscore rule, right-aligned Dur (s), 3 display goldens rewritten in place; M9 left as-is — injection load-bearing, redesign parked at I-010); D-078 (the lm_worker_config R2 fix, at machine level): the injected cache-path closure now concatenates the prefix verbatim onto the level name (filename-prefix semantics per the domain schema — one shared fix for all cache-consuming workers) instead of the D-069 M8 pathlib join; suite 49/0/0 GREEN (test_state_machine.py) | docs/src/twolm/state_machine.md |
| src/twolm/test/test_state_machine.py | analyzed 2026-08-29 (session 19): 5 classes / 49 tests / no PERF; all 13 original expectations independently re-derived (0 mismatches); T1 FIXED (D-057: TestVerbosityGating — 6x5 gating matrix + enum values); R2 tests added (D-058: TestLogEntry 3 tests — typed record, immutability, asdict 5-key form); T6 FIXED (D-060: test_retry_after_failure_skips_failed_step — retry-skip + down-then-up recovery); R5 tests added (D-061: 2 duplicate-name tests — reject + case-insensitive, closes T10); T2 FIXED (D-062: TestContextInjection 7 tests — log_event live binding, {level:02} format, base_dir join, absolute-prefix drops base_dir, cfg-missing AttributeError, empty-workers degenerate, V17 shared-context re-bind); T3 FIXED (D-063: TestDisplayGoldens 3 end-to-end goldens — live line, show_event_log table, show_history_of_moves table, frozen clock); T4 FIXED (D-064: 3 move_to_last tests — happy path, intermediate position, single-worker sentinel no-op); T5 FIXED (D-065: test_history_export_csv rewritten — exact header names, ISO-8601 +00:00, duration identity, artifact under build/tmp + finally cleanup; house rule: test files only in workspace_root/build/tmp); T7 pinned (D-066: 2 tests — bool as int step, np.int64 TypeError); T8 + T9 pinned (D-067: 5 tests — current_worker_name live view + UNDEFINED, StepMove field content incl. aware-UTC timestamps, duration identity, finally-append on failure); M-sweep batch 1 pinned (D-068: 4 tests — _run_step unknown direction ValueError, Worker __repr__, StateMachine __repr__ tracks state, CSV export creates missing parent dirs); M-sweep batch 2 pinned (D-069: bool test rewritten to rejection + 2 constructor ValidationError tests + Path prefix join test); M6 display goldens rewritten in place to the cleaned format (D-070 — enum names + UTC marker, TIMESTAMP (UTC) / 2-digit step / RELEVANCE name / 66-underscore table, right-aligned Dur (s) header; suite count unchanged); T11 resolved as D-058 side effect; ALL T ITEMS CLOSED (T1-T11); M-sweep COMPLETE; suite count unchanged for T5 (a rewrite): 13 → 15 → 18 → 20 → 22 → 29 → 32 → 35 → 37 → 42 → 46 → 49; D-078: test_path_cache_prefix_joins_without_gluing renamed test_cache_prefix_is_concatenated_verbatim + re-pinned to verbatim concatenation (cache01_CONFIG.dat), count unchanged; GREEN 49/0/0 | docs/src/twolm/test/test_state_machine.md |
| src/twolm/cache_manager.py | analyzed 2026-08-30 (session 20, added by Roberto in commit a0cd31f) + fix campaign batches 1+2 (D-071/D-072): generic load-or-compute cache pipeline (4-step validation: allowed → present → checksum → business validity) + duck-typed data checksum + injected callbacks; first domain module importing state_machine (Relevance) + binio (sidecar API, D-072); 17 verified facts V1-V17 (0 mismatches, 33-check probe + 2 boundary probes); D-071: R1 RESOLVED as intentional (step-0 cache-disabled run still warms the cache file — documented + pinned), R2 FIXED (validate_fn in the step-3 try — raising validator deletes + recomputes), R4 FIXED (@validate_call, str→Path coercion, approved behaviour change), M1-M3 fixed (dead Any import, docstring typos, step-2 msg accurate); D-072: R3 RESOLVED — binio sidecar API adopted (hashlib + the 2 re-implemented helpers deleted, _verify_checksum thin wrapper over verify_sha3_256_sidecar, sidecar now binio sha3_256sum format, legacy bare-hex sidecars still verify); CLOSED: R1-R4 + M1-M3 + T1-T7 resolved (T8 report-only); suite 21/0/0 GREEN (test_cache_manager.py) | docs/src/twolm/cache_manager.md |
| src/twolm/test/test_cache_manager.py | analyzed 2026-08-30 (session 20) + fix campaign batches 1+2 (D-071/D-072): 2 classes / 21 tests / no PERF (13 → 21 batch 1: T2 5 duck-typed-hash tests + R2 raising-validator pin + T5 missing-sidecar pipeline test + T3 sidecar-format test; 21 → 21 batch 2); D-071: T1 (assertIsNone on all 6 pipeline tests), T2 (P0 — the duck-typed compute_sha3_256_hash path: with-method both paths, missing → None, non-callable → None, raising on load → recompute), T3 (sidecar format pin), T4 (step-0 on-disk warm-cache effect, per R1 ruling), T5, T7 (on-disk replacement + valid sidecar after every recompute) FIXED; D-072: T6 FIXED (CUSTOM_TMP_BASE anchored to the workspace root via __file__), T3 pin restated to the binio sha3_256sum format, helper suite rebuilt around the binio API (R3 + legacy-compat + malformed/undecodable wrapper pins added, 2 direct-compute tests dropped), pipeline set-ups on write_sha3_256_sidecar; T8 report-only (header grammar); suite 21/0/0 GREEN; D-085: CUSTOM_TMP_BASE now imported from the shared twolm.test.paths module | docs/src/twolm/test/test_cache_manager.md |
| src/twolm/base_model.py | analyzed 2026-08-30 (session 21): thin facade base over StateMachine — pure delegation (current_step / current_worker_name / verbosity get+set, move_to_step / move_to_last, 2 display methods, CSV export); context identity with sm.context + delegation verified (30-check probe, 0 mismatches); D-074 (batch 1): R1 RESOLVED — @validate_call on __init__ (the one decision with logistic_model R3, applied to both facades; approved behaviour change: wrong-typed constructor args now raise a pydantic ValidationError at the facade boundary); D-075 (batch 2): M1 FIXED — __all__ = ['BaseModel'] added (L39, D-068 M1 pattern; 89 lines); M2 docstring forward-references not-yet-ported DeepNetworkModel (informational, kept by design); ALL R/M CLOSED; no dedicated suite (covered via test_logistic_model) | docs/src/twolm/base_model.md |
| src/twolm/logistic_model.py | analyzed 2026-08-30 (session 21): first concrete domain facade — RLMContext (@dataclass over plain Context; 38 fields, 8 *_checksum, artifact blackboard) + LogisticModel 4-step construction (plain path validation → context → 15-level worker list, deliberately partial per Roberto: CREATED sentinel + CONFIG + POSITIONS active (D-076, 601de87), 11 factory imports commented) + level-0 CREATED sentinel (D-059 made explicit); 10 verified facts V1-V10 (30-check probe, 0 mismatches); OPEN: R1 D-069 name divergence (RLMContext + both ported workers on the pre-D-069 _for_next_level names; SM injects _for_current_level — silently-None trap once enabled), R2 Union used (8 annotations) but not imported (latent NameError, PEP 563 mask), R3 no @validate_call on __init__ (one call with base_model R1), M1-M4 (weigth typo, vld__pop_stats double underscore, dir-as-config exception type, __init__ docstring); D-074 (batch 1): R1-R3 RESOLVED (D-069 rename — 2 RLMContext fields + 2 ported worker call sites; 8 annotations → str \| None; @validate_call with base_model R1), M1-M4 fixed (weight, vld_pop_stats, IsADirectoryError, docstring); D-075 (batch 2): M5 FIXED (dead `field` import removed); ALL R/M CLOSED; D-076 (Roberto): `lm_worker_config()` uncommented; 601de87: POSITIONS; f051dd3 (D-081): `lm_worker_features()` uncommented — 4 active levels (CREATED sentinel → CONFIG → POSITIONS → FEATURES); a323e0f (D-083): `lm_worker_indexes()` uncommented — 5 active levels (CREATED sentinel → CONFIG → POSITIONS → FEATURES → INDEXES; the rlm_indexes / rlm_indexes_checksum blackboard fields pre-existed at first import); a0adc6e (D-093): `lm_worker_gradient()` uncommented — 9 active levels (CREATED sentinel → CONFIG → POSITIONS → FEATURES → INDEXES → WMAPS → DESIGN_MTR → ZED → GRADIENT; the RLMContext.fg blackboard field pre-declared at L135; the WMAPS / DESIGN_MTR / ZED activations 73b4342 / D-090 / 439c966 landed without a row update); probe re-pinned to the post-a0adc6e state (35 checks, 0 mismatches — V3c the 9-worker list, V10 unchanged); e31c061 (D-097): `lm_worker_generate()` uncommented — 11 active levels (CREATED sentinel → CONFIG → POSITIONS → FEATURES → INDEXES → WMAPS → DESIGN_MTR → ZED → GRADIENT → OPTIMIZE → GENERATE; the w_dense / dense_w_checksum blackboard fields pre-existed at L142-143); probe re-pinned (35 checks, V3c the 11-worker list, 0 mismatches); ede2efe (D-099): `lm_worker_vld_positions()` uncommented — 12 active levels (CREATED sentinel → CONFIG → POSITIONS → FEATURES → INDEXES → WMAPS → DESIGN_MTR → ZED → GRADIENT → OPTIMIZE → GENERATE → VLD_POSITIONS; the 4 vld_* blackboard fields pre-existed at L146-149, vld_metrics / analytics_report at L152/155 for the future levels); 3 commented imports remain (validate, analytics, save); probe re-pinned (35 checks, V3c the 12-worker list, 0 mismatches); 536eadc (D-101): `lm_worker_validate()` uncommented — 13 active levels (CREATED sentinel → CONFIG → POSITIONS → FEATURES → INDEXES → WMAPS → DESIGN_MTR → ZED → GRADIENT → OPTIMIZE → GENERATE → VLD_POSITIONS → VALIDATE); 2 commented imports remain (analytics, save); probe re-pinned (35 checks, V3c the 13-worker list, 0 mismatches); D-102: VALIDATE fix campaign (R1 + T1-T5 + M1-M3, test file added — no change to this module); D-103 (96dacb5, Roberto): `lm_worker_analytics()` uncommented — 14 active levels (CREATED sentinel → CONFIG → POSITIONS → FEATURES → INDEXES → WMAPS → DESIGN_MTR → ZED → GRADIENT → OPTIMIZE → GENERATE → VLD_POSITIONS → VALIDATE → ANALYTICS); 1 commented import remains (save); probe re-pinned (35 checks, V3c the 14-worker list, 0 mismatches); D-103 fix campaign (T1-T6 + M1-M3, test file added — M1: the train_metrics field pre-declared on RLMContext, 38 → 39 fields); suite 15/0/0 GREEN (test_logistic_model.py); fe506c6 (D-104): `lm_worker_save()` uncommented by the bring-in itself — 15 active levels, PIPELINE COMPLETE (0 commented imports / entries); probe re-pinned (35 checks, V3c the 15-worker list, 0 mismatches); D-104 fix campaign (T1-T6 + M1 + O4, all in the new SAVE-family files — no change to this module); D-105/M2: RLMContext pre-declares train_dense_metrics (L156), 39 → 40 fields; suite 15/0/0 GREEN (test_logistic_model.py) | docs/src/twolm/logistic_model.md |
| src/twolm/test/test_logistic_model.py | analyzed 2026-08-30 (session 21): 1 class / 15 methods post D-076 (14 active + 1 muted per Roberto — restored line-by-line with the pipeline; D-076: Roberto restored test_move_to_step_delegates_to_state_machine, the CONFIG level now exists; `_test_move_to_step_by_string` restored session 28 (887880e, the D-073/D-075 T3 plan executed — all 15 methods active, 0 muted); D-075 test campaign: T1 FIXED (smoke test replaced by per-method delegation pins + views/verbosity round-trip), T2 FIXED (build/tmp artifact base, D-065 idiom, defensive tearDown), T3 intentional (muted tests), T4 FIXED (7 corner tests — injected-closure names/fallback/path computation, sentinel RuntimeErrors, helper edge branches, CSV pass-through), T5 FIXED (dead Relevance import removed), T6 report-only; suite 15/0/0 GREEN (15 active, 0 muted — session 28 restore); D-085: CUSTOM_TMP_BASE now imported from the shared twolm.test.paths module | docs/src/twolm/test/test_logistic_model.md |
| src/twolm/lm_worker_config.py | analyzed 2026-08-30 (session 21, D-077) + fix campaign D-078 (Roberto's calls): CONFIG worker — JSON5 load → ReversiLogisticModelConfig → base_dir validation (3 precise OS exception types, R3 fixed) → flat checksummed cache write (rlmwf_01_CONFIG.dat + bare-hex .SHA3-256 sidecar of model_dump_json(indent=4), via the injected full-path closure); 25-check probe, 0 mismatches (post step-3 c-deletions); D-076 fixed its cache naming + the SM gate split it exposed; D-078: R2 RESOLVED AT MACHINE LEVEL (closure concatenates the prefix verbatim — replaces the D-069 M8 join; the worker's per-worker concatenation replaced by the full-path closure), R3 precise OS types (FileNotFoundError/NotADirectoryError/PermissionError, messages unchanged), M1-M5 fixed (M5 keep per R1); R1 RESOLVED AS DEFERRED — the ad-hoc cache flow stays until the full pipeline is complete (I-011 "storicizzazione"); suite 15/0/0 GREEN (test_lm_worker_config.py, post the step-3 D1 move) | docs/src/twolm/lm_worker_config.md |
| src/twolm/test/test_lm_worker_config.py | analyzed 2026-08-30 (session 21, D-077) + fix campaign D-078 (Roberto: "T1-T6: OK"): 4 classes / 15 tests / no PERF (Roberto's new file; D1 moved in at step 3); D-076: 2 path typos py/→src/ + schema-complete validation payload; D-078: T1 FIXED (D-065 idiom on all 4 classes; dead shutil import removed; a stray per-test mkdtemp in the a-file test removed — it leaked dirs), T2 FIXED (ValueError — json5 0.15.0 raises a plain ValueError, no JSON5Exception in this version), T3 FIXED (_down reset pinned: cfg/use_cache None), T4 FIXED (bare-hex sidecar format pinned); the not-writable test updated to PermissionError (R3); T5/T6 report-only; suite 15/0/0 GREEN; D-085: the idiom + both json_config lines re-anchored to the shared twolm.test.paths (WORKSPACE_ROOT) | docs/src/twolm/test/test_lm_worker_config.md |
| src/twolm/test/data/rlm_00.json | test data (session 21, Roberto): JSON5 config fixture (comment header — json5 load-bearing, D-076; base_dir placeholder "will/be/overwritten/by/python/during/unittesting", use_cache True, cache_files_prefix rlmwf_) | — |
| src/twolm/lm_worker_positions.py | analyzed 2026-08-30 (session 22, D-079): the first cache_manager consumer in the pipeline — 4-step load-or-compute over the regab data set (binio-format sidecar + duck-typed data checksum rds.compute_sha3_256_hash) + post-processing (positions / game_values / rds_checksum / training_pop_stats on the context) + is_cache_consistent (pure metadata compare); enabled line-by-line 601de87 (CREATED → CONFIG → POSITIONS); 13 verified facts V1-V13 (21-check probe post step 3, 0 mismatches): flat rlmwf_02_POSITIONS.dat (D-078 machine-level fix re-verified — the latent rlmwf_/ subdirectory trap gone), cross-run cache round-trip identity, D-071 R1 cache-warming visible in a domain worker, corruption / business-inconsistency → delete + recompute, is_allowed=ctx.use_cache consumed; D-080 fix campaign (Roberto: "correggile tutte"): R1 FIXED (5-arg connection call — port + password now take effect, DEBUG log includes the port never the password), M1-M4 FIXED (@validate_call factory, dead pathlib import, flagged trailing whitespace, load_fn checksum=False), cross-ref note RESOLVED (regab_store docstring + regab.md row — the sidecar is cache_manager's, D-072); probe post step 3 (21 checks, 0 mismatches — c groups dropped, D4/E -> tests); suite 9/0/0 GREEN (test_lm_worker_positions.py: 2 DB-gated end-to-end + 7 in-memory is_cache_consistent units, run with live DB) | docs/src/twolm/lm_worker_positions.md |
| src/twolm/test/test_lm_worker_positions.py | analyzed 2026-08-30 (session 22, D-079): Roberto's file, copied from the original repo with the POSITIONS enablement (601de87, line-by-line step 1); 2 classes / 9 tests / no PERF (post step 3: the D4a-g probe units moved in as TestIsCacheConsistent — 7 in-memory, no DB); end-to-end cache round-trip pin (DB hit + flat files; second instance cache hit + no DB), stdout captured via patched StringIO; green on first run, no fixes; D-080 (Roberto: "fai tutto anche qui"): T1-T4 FIXED (D-065 idiom, SKIP_REGAB_DB gate, dead if-False blocks + sys import removed, header grammar) — test campaign CLOSED; suite 9/0/0 GREEN (2 DB-gated + 7 in-memory, run with live DB); D-085: the idiom + the json_config line re-anchored to the shared twolm.test.paths (WORKSPACE_ROOT) | docs/src/twolm/test/test_lm_worker_positions.md |
| src/twolm/rlm_config_schemas.py | analyzed 2026-08-30 (session 22, D-079): the pydantic config domain — ReversiLogisticModelConfig (10 fields, JSON5 entry point) over the nested tree, all RLMBaseConfig (free-form properties bag) except StatModelConfig; Bitboard hex fields (16-hex no-0x parse, uppercase 16-hex serializer); 12 verified facts V1-V12 (probe E, 0 mismatches); D-080: R1 FIXED (c2>c1 cross-field model_validator — the strong-Wolfe invariant enforced), M1-M4 FIXED (hex docstring example, model_validator import now load-bearing, strict List[StatusString] + StatModelConfig → RLMBaseConfig, default_factory lists); no dedicated suite pre step 3 — since then test_rlm_config_schemas.py 13/0/0 (the E-section §4 conversion); 25-check probe 0 mismatches | docs/src/twolm/rlm_config_schemas.md |
| src/twolm/lm_worker_features.py | analyzed 2026-08-31 (session 22, D-081); enabled in f051dd3 (Roberto) — the pipeline now runs 4 active levels (CREATED → CONFIG → POSITIONS → FEATURES); the FIRST pure-compute level (no DB, no cache_manager, no cache file, no features_checksum field); 13 verified facts V1-V13 (42-check probe, 0 mismatches): feature order [INTERCEPT, ALMC, LMC, DLMC, EDGE, ELLE], 6 features / 16 n_instances, hash re-derived independently, zero-feature guard, cross-run identity; D-082 (Roberto: R1 "ok, fissa il bug", M1-M3 OK): R1 + M1-M3 FIXED (amask log, @validate_call factory, whitespace, orphan comment removed) — module CLOSED; probe post step 3 (b05adfd): 40 checks (B11 → test), 0 mismatches; suite 3/0/0 (2 DB-gated + 1 DB-free zero-feature guard, run with live DB) | docs/src/twolm/lm_worker_features.md |
| src/twolm/test/test_lm_worker_features.py | analyzed 2026-08-31 (session 22, D-081): Roberto's file, brought in with the FEATURES enablement (f051dd3); 1 class / 1 test at analysis; green on first run with the live DB; D-082 (Roberto: T1-T4 + M2 OK + his own proposal for the golden content test): T1-T4 + M2 FIXED (D-065 idiom, SKIP_REGAB_DB gate, Path import now load-bearing, header grammar, whitespace), M1 LEFT AS-IS (recorded at I-012 — evaluate moving FEATURES before POSITIONS), test_feature_set_content_golden ADDED (3 hash literals + full content pin) — test campaign CLOSED; 1 → 2 tests; post step 3 (b05adfd): 2 classes / 3 tests (the B11 zero-feature guard converted to a DB-free test); suite 3/0/0 (2 DB-gated + 1 DB-free, run with live DB); D-085: the idiom + the json_config line re-anchored to the shared twolm.test.paths (WORKSPACE_ROOT) | docs/src/twolm/test/test_lm_worker_features.md |
| src/twolm/rlm_indexes.py | analyzed 2026-08-31 (session 23, D-083); brought in with a323e0f (Roberto — the INDEXES line-by-line enablement, 5th active level): the 5th-level data object (2-D uint32 index matrix + rds_checksum + feature_set_hash, by-reference storage) + the 4 public functions (store / load / compute / is_cache_consistent) + the duck-typed compute_sha3_256_hash (the cache_manager 3rd-return-element hook); the SECOND cache_manager consumer in the pipeline after POSITIONS; 12 verified facts V1-V12 (probe re-pinned D-084: 56 checks, 0 mismatches); D-084 (Roberto: "Sì fai tutto"): R1 + M1-M4 + M6 FIXED (store docstring corrected — the sidecar is cache_manager's, D-072; 5 dead imports removed, "togheter" typo, 4 trailing-whitespace lines, version gate via expected_version, __repr__ added), M5 left as-is (by design — documented circular-import constraint); 5 @validate_call decorators (the 5th is __repr__); file 180 → 190 lines; module CLOSED; suite 14/0/0 GREEN (test_rlm_indexes.py); D-106 step 11: the doc rewritten to the schema (session-23 analysis archived to notes/analyses/rlm_indexes_session23_review.md; probe re-pinned 56 → 52 calls / 48 labels at the 4091e72 move + the 4e32427 class c deletions) | docs/src/twolm/rlm_indexes.md |
| src/twolm/lm_worker_indexes.py | analyzed 2026-08-31 (session 23, D-083); brought in with a323e0f (Roberto — the INDEXES line-by-line enablement): the cache-consuming level — the uniform 7-kwargs cache_manager wiring (the injected full-path closure — flat rlmwf_04_INDEXES.dat, the D-078 machine-level naming — use_cache, the 5 rlm_indexes fns, the metadata-compare validate_fn); _down clears BOTH context attributes; 8 verified facts V1-V8 (probe re-pinned D-084: 56 checks, 0 mismatches): flat cache files (no rlmwf_03_FEATURES*), data vs file checksum distinction, (N, 16) uint32 identity, cross-run round-trip, the _down clearing; D-084 (Roberto: "Sì fai tutto"): M1-M3 FIXED (@validate_call on the factory + pydantic import — the D-080/D-082 pattern, 2 trailing-whitespace lines, load_fn → lambda path: ...(path, checksum=False) — the D-080 M4 shape); file 77 → 80 lines; module CLOSED; suite 2/0/0 GREEN (test_lm_worker_indexes.py, 2 DB-gated post D-084 T2); D-106 step 11: the doc rewritten to the schema (session-23 analysis archived to notes/analyses/lm_worker_indexes_session23_review.md) | docs/src/twolm/lm_worker_indexes.md |
| src/twolm/test/test_rlm_indexes.py | analyzed 2026-08-31 (session 23, D-083); Roberto's file, brought in with a323e0f; 5 classes / 14 tests / no PERF (13 at analysis + the rds-only-differs test added D-084 M2); all file I/O mocked (binio patched), no temp dirs, no DB; the store/load contract fully pinned (exact 4-call sequence, both checksum flags, all 3 RuntimeError messages, the by-reference init); D-084 (Roberto: "Sì fai tutto"): T1-T5 + M1-M2 FIXED (dead IndexArray import removed, header grammar, the 2 broad assertRaises(Exception) → the precise pydantic ValidationError, rds_checksum added to test_init_fails_with_invalid_indexes_type — the invalid indexes is now the thing under test, Italian comment → English, 19 trailing-whitespace lines, the rds-only is_cache_consistent branch now unit-tested); file 287 → 304 lines; test campaign CLOSED; suite 14/0/0 GREEN; D-106 step 11: the doc rewritten to the test-variant schema (session-23 analysis archived to notes/analyses/test_rlm_indexes_session23_review.md; file unchanged since D-084) | docs/src/twolm/test/test_rlm_indexes.md |
| src/twolm/test/test_lm_worker_indexes.py | analyzed 2026-08-31 (session 23, D-083); Roberto's file, brought in with a323e0f; 1 class / 2 tests / no PERF; the end-to-end cache round-trip pin (DB hit through POSITIONS + flat rlmwf_04_INDEXES.dat + "Executing heavy computation"; second instance "Cache successfully loaded and validated" + no heavy computation); green on first run with the live DB; the dependency comment is ACCURATE (contrast test_lm_worker_features M1); D-084 (Roberto: "Sì fai tutto"): T1-T3 + M1 FIXED (the D-065 idiom — CUSTOM_TMP_BASE via __file__, setUpClass mkdir, TemporaryDirectory first, defensive tearDown; the SKIP_REGAB_DB gate — both tests now DB-gated, header grammar + the live-DB / gate run note, 13 trailing-whitespace lines); file 137 → 158 lines; test campaign CLOSED; suite 2/0/0 GREEN (2 DB-gated, run with live DB); D-085: the idiom + the json_config line re-anchored to the shared twolm.test.paths (WORKSPACE_ROOT); D-106 step 11: the doc rewritten to the test-variant schema (session-23 analysis archived to notes/analyses/test_lm_worker_indexes_session23_review.md; file unchanged since D-085) | docs/src/twolm/test/test_lm_worker_indexes.md |
| src/twolm/test/paths.py | introduced 2026-08-31 (session 23, D-085 — Roberto's design choice "A"): the single home of the workspace-root-anchored test paths — WORKSPACE_ROOT (marker-based derivation: the first ancestor holding pyproject.toml — not a parents[N] level count, survives file moves) + CUSTOM_TMP_BASE (= <root>/build/tmp, the D-065 base); the per-test-file __file__ derivations, the CWD-relative JSON fixture paths (now str(WORKSPACE_ROOT / "src/twolm/test/data/rlm_00.json")), and the test_regab .env / mkdtemp are all re-anchored to it; no public functions (constants only), hence no @validate_call | docs/src/twolm/test/paths.md |
| src/twolm/test/test_paths.py | introduced 2026-08-31 (session 23, D-085): 1 class / 3 tests / no DB / no gate / no artifacts — pins WORKSPACE_ROOT absolute + marker-holding + ancestor of src/twolm/test/, CUSTOM_TMP_BASE == <root>/build/tmp absolute; imports the module (from twolm.test import paths) so a rename surfaces in one place | docs/src/twolm/test/test_paths.md |
| src/twolm/rlm_wmaps.py | introduced 2026-08-31 (session 23, Roberto's commit 73b4342 — the WMAPS bring-in, 6th pipeline level): the WMAPS data object (ReversiLogisticModelWMaps: rlm_indexes_checksum, cut_off, feature_w_ranges (F,3) int64 [fallback, w_min, w_max] per feature, iwmap_feature_offset (F+1,) uint32, iwmap (K,) int64 (−1 = configuration unseen in the dataset), wmap (W,3) int64 [fid, config_id_or_−1, freq], wmap_fallback (F_cut,3) int64, w (W,) float32 zeros) + the 4 public fns (store / load / compute / is_cache_consistent) + the duck-typed compute_sha3_256_hash over the 6 arrays; the 3rd cache_manager consumer in the pipeline; analysis D-086: the dead itertools accumulate import (L35), 23 non-comment trailing-whitespace lines (incl. the L275 / L288 code lines), compute + is_cache_consistent lack @validate_call with no rlm_indexes-L166-style note (the TYPE_CHECKING constraint); R1 RESOLVED as no-guard (Roberto's contract: the indexes are unsigned, 0..n_configurations−1, never −1 — dense by contract, documented in the compute docstring); fix campaign D-087 CLOSED (Roberto: "Procedi su tutto"): the dead accumulate import gone, the no-validation note added (the rlm_indexes style), 23 ws lines stripped; the D-087 '9-space __init__ indent' observation corrected as a misread (D-088 — verified 8 spaces, canonical, no change); file 311 → 316 lines; module CLOSED; D-106 step 12: the doc rewritten to the schema (session-23 analysis archived to notes/analyses/rlm_wmaps_session23_review.md; probe re-pinned 64 → 53 calls at the 4091e72 move + the step-3 class c deletions E0-E8 to the tests, F4/F6 to the hub, only E9 survives) | docs/src/twolm/rlm_wmaps.md |
| src/twolm/lm_worker_wmaps.py | introduced 2026-08-31 (session 23, Roberto's commit 73b4342 — the WMAPS bring-in, 6th active level): the cache-consuming level, the uniform 7-kwargs cache_manager wiring (flat rlmwf_05_WMAPS.dat + .SHA3-256 sidecar, the D-078 machine); _up sets the 6 ctx arrays + wmaps_obj_checksum; analysis D-086: the factory lacks @validate_call (the other 5 workers all have it) + no pydantic import; load_fn is the raw function (checksum defaults True → double sidecar validation — the house shape is lambda path: ...(path, checksum=False), D-080 M4 / D-084 M3); _down does NOT clear ctx.wmaps_obj_checksum (the house shape clears object + checksum, lm_worker_indexes); fix campaign D-087 CLOSED: factory @validate_call + pydantic import, load_fn = lambda checksum=False (the house shape), _down clears wmaps_obj_checksum, 4 ws lines stripped; file 87 → 91 lines; module CLOSED; D-106 step 12: the doc rewritten to the schema (session-23 analysis archived to notes/analyses/lm_worker_wmaps_session23_review.md; probe B tier now part of the 53-call verify_wmaps.py at the 4091e72 move) | docs/src/twolm/lm_worker_wmaps.md |
| src/twolm/test/test_rlm_wmaps.py | introduced 2026-08-31 (session 23, Roberto's commit 73b4342): 3 classes / 6 tests / no DB / no gate — compute on the handcrafted 4×3 mock (fallback + the cut_off=0 no-fallback branch), is_cache_consistent (3), store/load cycle (1, checksum=False both sides); the D-085 idiom APPLIED (Roberto's instruction): the CWD-relative mkdtemp → TemporaryDirectory under the shared CUSTOM_TMP_BASE, defensive tearDown, the twolm.test.paths import, the dead shutil import gone; file 251 → 259 lines; fix campaign D-087 CLOSED: header corrected (the file is DB-free), dead StringIO + patch imports gone, the leftover generation comment gone, 21 ws lines stripped, +5 IO pins (the golden hash 12c3344e…, sidecar valid/mismatch, wrong description, version mismatch) + TestRLMWmapsInit (2 tests) — 6 → 13 tests; file 259 → 325 lines; suite 13/0/0 GREEN; D-106 step 12: the doc rewritten to the test-variant schema (session-23 analysis archived to notes/analyses/test_rlm_wmaps_session23_review.md; file unchanged since D-087) | docs/src/twolm/test/test_rlm_wmaps.md |
| src/twolm/test/test_lm_worker_wmaps.py | introduced 2026-08-31 (session 23, Roberto's commit 73b4342): 2 classes / 3 tests / all DB-dependent — the worker round-trip (2 tests: first run "Forcing computation" + both D-078 files, second instance cache hit, no recompute; cache names + steps 4/5 pinned) + the golden content (rlm_01.json, cut_off=2: feature_w_ranges (4,3), offsets [0,1,66,93,174], iwmap 174, wmap (21,3), wmap_fallback (10,3), w=21 float32 zeros — every literal independently re-derived by the probe, E0-E9, 0 mismatches); the D-085 idiom APPLIED (both classes: the CWD mkdtemp + CWD json_config → TemporaryDirectory under the shared CUSTOM_TMP_BASE + WORKSPACE_ROOT-anchored json, defensive tearDown, the paths import, the dead shutil import gone); file 283 → 301 lines; fix campaign D-087 CLOSED: the SKIP_REGAB_DB gate added to both setUps (now 3/0/3 under the gate, as claimed by the header) + 20 ws lines stripped; file 301 → 315 lines; suite 3/0/0 GREEN (live DB); D-106 step 12: the doc rewritten to the test-variant schema (session-23 analysis archived to notes/analyses/test_lm_worker_wmaps_session23_review.md; file unchanged since D-087; the E0-E9 golden re-derivation now owned by TestLMWorkerWmapsExactValues) | docs/src/twolm/test/test_lm_worker_wmaps.md |
| src/twolm/rlm_design_matrix.py | introduced 2026-08-31 (session 23, Roberto's UNCOMMITTED bring-in — the DESIGN_MTR enablement, 7th pipeline level): the Design Matrix data object (ReversiLogisticModelDesignMatrix: wmaps_obj_checksum str + X (N,7) uint32 — the w-index of each (position, feature-instance) cell) + the 4 public fns (store / load / compute / is_cache_consistent) + the duck-typed compute_sha3_256_hash over X; the 4th cache_manager consumer in the pipeline; the approved warning fix APPLIED (Roberto: "Esegui la modifica"): the NumPy 2.5 DeprecationWarning (implicit int64->uint32 output cast in np.take) → the explicit .astype(np.uint32) + the note (now L119-122); fix campaign D-090 CLOSED (Roberto: "Procedi su tutti i T, e R1"): the no-validation note added above compute (the rlm_indexes L166 class, T4) + the redundant 2nd guard merged away (R1 — the single -1 guard with the precise ValueError remains) + 3 ws lines stripped; file 135 → 133 lines; suite: test_rlm_design_matrix 12/0/0 (new, D-090 T6) + test_lm_worker_design_matrix 3/0/0 (live DB) | docs/src/twolm/rlm_design_matrix.md |
| src/twolm/lm_worker_design_matrix.py | introduced 2026-08-31 (session 23, Roberto's UNCOMMITTED bring-in — the DESIGN_MTR enablement, 7th active level): the cache-consuming level, the uniform 7-kwargs cache_manager wiring (flat rlmwf_06_DESIGN_MTR.dat + .SHA3-256 sidecar, the D-078 machine); _up sets design_matrix + design_matrix_checksum; _down clears BOTH (the house shape — no gap at bring-in); fix campaign D-090 CLOSED: the factory @validate_call + pydantic import added (T2, the house convention) + load_fn → the lambda checksum=False idiom (T3, the double sidecheck gone) + 2 ws lines stripped; file 77 → 80 lines; suite: test_lm_worker_design_matrix 3/0/0 (3 DB-gated post D-090 T1) | docs/src/twolm/lm_worker_design_matrix.md |
| src/twolm/test/test_lm_worker_design_matrix.py | introduced 2026-08-31 (session 23, Roberto's UNCOMMITTED bring-in): 2 classes / 3 tests / all DB-dependent — the worker round-trip (2 tests: first run "Forcing computation" + both D-078 files, second instance cache hit; cache names + steps 5/6 pinned) + the golden content (rlm_01.json: X (10,7) uint32 — 10 pinned rows, independently re-derived by the probe D0-D10 incl. the X = iwmap[pindexes + col_offsets] recomputation, 0 mismatches); fix campaign D-090 CLOSED: the SKIP_REGAB_DB gate added to BOTH setUps + import os (T1 — the header claim now true, 3/0/3 under the gate) + the D-085 idiom applied to both classes (T7 — TemporaryDirectory under CUSTOM_TMP_BASE created first, WORKSPACE_ROOT-anchored json ×2, defensive tearDown, the dead shutil import gone) + 21 ws lines stripped; file 202 → 226 lines; suite 3/0/0 GREEN (live DB; 3/0/3 gated) | docs/src/twolm/test/test_lm_worker_design_matrix.md |
| src/twolm/test/test_rlm_design_matrix.py | created 2026-08-31 (session 23, D-090 T6 — the dedicated data-object suite closing the coverage gap, mirroring test_rlm_wmaps): 4 classes / 12 tests / no DB, no gate — the handcrafted-mock compute pins (X = iwmap[pindexes + col_offsets], the (4,3) uint32 golden + the guard's ValueError pin, post-R1 single guard) + the 1-field consistency compare (2 tests) + the store/load cycle + golden hash (da86a916...57b) + sidecar/error-path pins (3 RuntimeError + the D-072 machine) + the init validation (2 tests); the D-085 idiom from day one; file 258 lines; suite 12/0/0 GREEN (no DB) | docs/src/twolm/test/test_rlm_design_matrix.md |
| src/twolm/rlm_zed.py | introduced 2026-08-31 (session 24, Roberto's commit 439c966 — the ZED bring-in, 8th pipeline level): the Z data object (ReversiLogisticModelZed: the y2z/z2y affine closures + z (N,) float32 — game_values mapped [−64,64] → [c, 1−c], c = cfg.stat_model.logit_clipping) + zed_fun_factory (in __all__) + rlm_zed_compute + the duck-typed hash over z only; the FIRST non-cache level (no store / load / is_cache_consistent); analysis D-091 (probe re-pinned D-092: 60 checks, tiers A–G, 0 mismatches): rlm_zed_compute lacked the no-validation note (T6), zed_fun_factory lacked @validate_call (T7), 2 code ws lines (T8); fix campaign D-092 CLOSED (Roberto: "T1-T8: OK"): the no-validation note added (L94, the rlm_indexes L166 class), the factory @validate_call (L70), 2 ws lines stripped; M1 informational (the hash covers z only — the closures are a pure function of logit_clipping); file 101 → 103 lines; module CLOSED | docs/src/twolm/rlm_zed.md |
| src/twolm/lm_worker_zed.py | introduced 2026-08-31 (session 24, Roberto's commit 439c966 — the ZED bring-in, 8th active level): the "ZED" worker — the first non-cache level (no cache_manager wiring, no rlmwf_07* file ever, by design — the on-the-fly comment L49); _up sets ctx.y2z / z2y / z / zed_checksum, _down clears ALL FOUR (the house shape — no gap at bring-in, pinned live D12); analysis D-091: the factory lacked @validate_call + the pydantic import (T2, all the other 6 workers have it), 3 code ws lines (T8); fix campaign D-092 CLOSED (Roberto: "T1-T8: OK"): the factory @validate_call (L70) + pydantic import (L32), 3 ws lines stripped; file 70 → 73 lines; module CLOSED; suite 3/0/0 GREEN (test_lm_worker_zed — 1 DB-free + 2 DB-gated post D-092 T1, run with live DB) | docs/src/twolm/lm_worker_zed.md |
| src/twolm/test/test_lm_worker_zed.py | introduced 2026-08-31 (session 24, Roberto's commit 439c966): 2 classes / 3 tests / no PERF — the isolated zed_fun_factory math (alpha=0.02: [−64, 0, 6, 64] → [0.02, 0.5, 0.545, 0.98] + round-trip, no DB) + the rlm_01.json integration (logit_clipping 0.03, y (10,) int8, z (10,) float32 golden — independently re-derived by the probe D tier, 0 mismatches; step pins DESIGN_MTR=6 / ZED=7) + the _down clearing (D-092 T5); analysis D-091: T1 (NO SKIP_REGAB_DB gate — the header L38-39 claims it, false; under the gate the tests RAN on the live DB), T4 (the D-085 idiom not applied: CWD mkdtemp + CWD json + dead shutil import + non-defensive tearDown), T5 (no _down test), 7 code ws lines (T8); fix campaign D-092 CLOSED (Roberto: "T1-T8: OK"): the SKIP_REGAB_DB gate added to the worker setUp (the header claim now true — 3/0/2 under the gate), the D-085 idiom applied (TemporaryDirectory under CUSTOM_TMP_BASE created first, WORKSPACE_ROOT-anchored json, defensive tearDown, the dead shutil gone, Path load-bearing), the _down test added (step 6 + DESIGN_MTR + 4 None pins), 5 ws lines stripped; file 138 → 164 lines, 2 → 3 tests; test campaign CLOSED; suite 3/0/0 GREEN (live DB; 3/0/2 gated) | docs/src/twolm/test/test_lm_worker_zed.md |
| src/twolm/test/test_rlm_zed.py | created 2026-08-31 (session 24, D-092 T3 — the dedicated data-object suite closing the D-091 coverage gap, mirroring test_rlm_wmaps / test_rlm_design_matrix): 3 classes / 10 tests / no DB, no gate — the factory math (the 0.02 golden [0.02, 0.5, 0.545, 0.98], the inverse, the round-trip, the 2-clippling endpoints), the handcrafted-mock compute (the (4,) EXACT golden [0.5734375, 0.764375, 0.3384375, 0.646875] + the hash identity), the init validation (2 ValidationError pins + by-reference), the rlm_01 hash golden (3d49fd5d...f365d9b2); file 157 lines; suite 10/0/0 GREEN (no DB) | docs/src/twolm/test/test_rlm_zed.md |
| src/twolm/rlm_gradient.py | analyzed 2026-09-01 (session 25, D-093): the function-only module (no data class, no store/load/hash, no init validation — unlike every other rlm_* level): sigmoid (the scipy expit wrapper, in __all__) + rlm_gradient_compute (the fg closure builder — captures X, z, alpha = ridge_regularization/M; the linear predictor is the per-row sum of w[X[m,p]] — the w-INDEX sum, not X·w; f = 0.5·(mean(rn²) + alpha·‖w‖²), g via the broadcast-bincount trick); 52-check probe (scratch/verify_gradient.py, tiers A–E) 0 mismatches — f(w=0) float32 0.020493777 and g(w=0) re-derived independently in float64 (np.add.at + hand-rolled sigmoid vs expit), f+g at a seeded w≠0 (the ridge term), closure stateless, feature set 8 instances; OPEN R1 (the return annotation says NDArray[np.float32] for g but the actual g is float64 — np.bincount upcasts the float32 weights; f IS float32, matching) + T1 (scipy not declared in pyproject.toml) + T3 (the no-validation note) + T4 (6 ws lines) + T9 (the sigmoid docstring) — fix campaign D-094 CLOSED (Roberto: R1 the cast + "T1-T9 falli tutti" + M1 OK / M2 as-is): R1 FIXED (the float32 cast on the return — g is now float32, the annotation was the intent), T1-T9 applied; file 90 → 91 lines; the 61-check probe re-pinned (0 mismatches) | docs/src/twolm/rlm_gradient.md |
| src/twolm/lm_worker_gradient.py | introduced 2026-09-01 (session 25, Roberto's commit a0adc6e — the GRADIENT bring-in, 9th active level): the SECOND non-cache level (after ZED) — "closure generation, very fast. No cache needed." (L47), no cache_manager wiring, no rlmwf_07*/08* file ever (the next cache level takes rlmwf_08); _up sets ctx.fg, _down clears it (both live-verified, probe D2/D11); analysis D-093: T2 (the factory without @validate_call + pydantic import — all 7 other workers have it) + T4 (3 ws lines) — fix campaign D-094 CLOSED: T2 applied (the @validate_call decorator + the pydantic import, like all 7 siblings), T4 3 ws lines stripped, M4 left as-is (the triple blank lines = the 8-worker house style); file 59 → 62 lines; suite 2/0/0 GREEN (2 DB-gated) | docs/src/twolm/lm_worker_gradient.md |
| src/twolm/test/test_lm_worker_gradient.py | introduced 2026-09-01 (session 25, Roberto's commit a0adc6e): 1 class / 1 test / no PERF — the rlm_02 integration (X (199952, 8) uint32 + w (2981,) float32 pre-state pins, the step 7/8 pins, f 0.02049378 + g[0] 3.558e-4 / g[1] −2.395e-4 / g[2980] 1.101e-3 goldens — all re-derived by the probe D tier, 0 mismatches); analysis D-093: T5 (NO SKIP_REGAB_DB gate — the header L38-39 claim is false, under the gate the test RAN on the live DB), T6 (the D-085 idiom not applied: CWD mkdtemp + CWD json + no TemporaryDirectory + non-defensive tearDown + the dead-after-idiom shutil), T7 (no _down test), T8 (4 ws lines) — fix campaign D-094 CLOSED: T5 the SKIP_REGAB_DB gate added (the header claim now true — 2/0/2 under the gate), T6 the D-085 idiom (TemporaryDirectory under CUSTOM_TMP_BASE created first, WORKSPACE_ROOT-anchored json, defensive tearDown, the dead shutil gone), T7 the _down test added (step 7 + ZED + fg None), T8 4 ws lines stripped; file 118 → 142 lines, 1 → 2 tests; suite 2/0/0 GREEN (live DB; 2/0/2 gated) | docs/src/twolm/test/test_lm_worker_gradient.md |
| src/twolm/rlm_optimize.py | introduced 2026-09-01 (session 26, Roberto's commit 1ebdd8b — the OPTIMIZE bring-in, 10th pipeline level): the ONLY pipeline level whose "cache" is NOT a data class behind the store/load/is_cache_consistent trio — a plain CHECKPOINT DICT serialized with binio (the L56-57 design comment); 6 public names (the save/load binary round-trip, the 2 gate functions the worker consults, the info-dict projection, the duck-typed weights hash); the checkpoint is written on EVERY run, read only when it exists and use_cache (the D-071 R1 pattern); analysis D-096 (92-check probe, tiers A–H, 0 mismatches): R1 (the ridge gate sits in the STATUS function, not the consistency gate — a ridge change resumes from warm weights, a "restart a caldo", instead of invalidating like a zed change), R2 (a corrupted/unparseable checkpoint kills the worker — no guard on the load), R3 (load does not verify the SHA3-256 sidecar before trusting the payload), + the T/M items; fix campaign D-096 CLOSED (Roberto: R1 keep the clipping-equivalent behavior — the hot restart parked at I-014, R2 "mettiamo try/catch", R3 "verifichiamo la checksum. Sta li per questo motivo!", R4 _down also clears w_checksum + opt_info, T1-T15 + M "falli tutti"): the ridge gate moved INTO is_optimization_cache_consistent (now 3-gate, each with its own 3×WARN diagnostic block; the status function slimmed to re-judging the stored g_norm against the CURRENT min_grad — the dead mg_is_consistent isclose + TRACE removed), the sidecar verify in load after the 2 header gates, T9 the dead Tuple import, T11 the 2 no-validation notes (the RLMContext TYPE_CHECKING constraint), T13 the header "rglm.py" → "rlm_optimize.py", M6 the save length-mismatch fail-fast ValueError (before the writer opens, no file left behind), M7 the log deviation keep+document, M8 the config-driven checkpoint name keep (the next cache level still takes rlmwf_08), M9 the "Atomically" comment dropped; file 245 → 267 lines; module CLOSED; suite 19/0/0 GREEN (test_rlm_optimize, no DB, no gate) | docs/src/twolm/rlm_optimize.md |
| src/twolm/lm_worker_optimize.py | introduced 2026-09-01 (session 26, Roberto's commit 1ebdd8b — the OPTIMIZE bring-in, 10th active level): the optimizer level — the 4-step _up (1. checkpoint consultation through the 2 gates → the 3-way decision completed-load / warm-resume / scratch; 2. the two lbfgs wrappers — logger_fn → ctx.log_event, save_fn → the intermediate INCOMPLETE checkpoints; 3. the lbfgs run on the GRADIENT ctx.fg closure, the float32 contract D-094 R1 consumed losslessly; 4. the context update + the final save); analysis D-096: R2 (a corrupted checkpoint must not kill the worker), R4 (_down clears only fg — w_checksum + opt_info left stale), T8 ("Aauthor" → "Author"), T9 (the dead Path import), T10 (the factory without @validate_call + pydantic import), M1 (min_grad_count unpacked but unused), M2 (the trailing "state is unrecognized" else — unreachable), M4 ("cecksum" ×2), M5 (the intermediate checkpoints stored the iteration index k, not k+1); fix campaign D-096 CLOSED (Roberto: R2 "mettiamo try/catch" — corrupted checkpoint deleted (content + .SHA3-256 sidecar) + scratch, R4 _down also clears w_checksum + opt_info — ctx.w kept, the re-optimized WMAPS vector, T1-T15 + M "falli tutti"): the try/except (RuntimeError, BinaryFormatError, OSError), the _down scope (pinned by the new test_down_clears_optimize), the T10 @validate_call (all 10 worker factories now share the pattern), M1-M5 fixed (M5: the intermediate saves now store iters=k+1 — completed-count semantics, as the final save); file 169 → 190 lines; module CLOSED; suite 3/0/0 GREEN (test_lm_worker_optimize, all 3 tests DB-gated post T1, run with live DB) | docs/src/twolm/lm_worker_optimize.md |
| src/twolm/test/test_lm_worker_optimize.py | introduced 2026-09-01 (session 26, Roberto's commit 1ebdd8b): 1 class / 2 tests / no PERF — the OPTIMIZE worker integration (the loss-decrease run; the max-iters → completed → checkpoint-reload run — byte-identical weights, no lbfgs in run 2); green on first run; analysis D-096: T1 (NO SKIP_REGAB_DB gate — the header claim false: the setUp moves through GRADIENT on a fresh base dir, which hits the live DB), T2 (the D-085 idiom not applied — CWD mkdtemp + CWD json), T3 (the dead if-False block), T4 (the dead imports), T5 (the stray #: ### comment), T6 (the VACUOUS assertNotIn("Starting L-BFGS optimization") — opt_lbfgs never logs that string, it passed trivially — replaced with the ACTUAL per-iteration marker "L-BFGS - ["), T7 (no _down test); fix campaign D-096 CLOSED (Roberto: "T1-T15: falli tutti"): all 7 applied (gate first in the setUp, the D-085 idiom, the cleanup, the real marker, the new test_down_clears_optimize pinning R4); file 149 → 174 lines, 2 → 3 tests; test campaign CLOSED; suite 3/0/0 GREEN (live DB; 3/0/3 gated) | docs/src/twolm/test/test_lm_worker_optimize.md |
| src/twolm/test/test_rlm_optimize.py | introduced 2026-09-01 (session 26, Roberto's commit 1ebdd8b): 2 classes / 4 tests / no DB, no gate — the IO round-trip + the 3 consistency tests; green on first run, but the header claimed "a live regab DB is required" although the file uses no DB (T14), the 2 consistency tests were misleadingly named (T15: they test the checksum gates — test_inconsistent_iters / test_inconsistent_m), and the D-085 idiom was not applied; fix campaign D-096 CLOSED (Roberto: "M: falli tutti" + T14/T15): T14 the header corrected (no DB required — pure checkpoint IO and cache-validation tests, as in test_rlm_gradient), T15 the renames + the new test_inconsistent_ridge (R1), and the M10 dedicated-suite expansion 4 → 19 tests / 4 classes, no DB: the round-trip WITH the dtype pins (w/sl/yl float32, rho float64), the empty-history round-trip, the M6 fail-fast (no file left behind), the 2 header RuntimeError gates message-pinned, the R3 corrupted-content gate (last byte flipped, sidecar untouched), the deterministic file golden hash 6e01ff86…1bd280 + the sidecar produced-and-matches, the 3 helper tests (the 5-key info dict + KeyError + the weights-hash golden 78a7baac…dc060), the 4 consistency branches incl. the R1 ridge gate, the 4 status branches incl. the f32 round-trip + the judged-against-new-tolerance test (M3 semantics); file 157 → 340 lines; test campaign CLOSED; suite 19/0/0 GREEN (no DB) | docs/src/twolm/test/test_rlm_optimize.md |
| src/twolm/rlm_generate.py | introduced 2026-09-02 (session 27, Roberto's commit e31c061 — the GENERATE bring-in, 11th pipeline level): the dense-weights data object (w_checksum = the OPTIMIZE compressed-w checksum — the consistency anchor; w_dense (K,) float32 over all theoretical configurations; the duck-typed hash over w_dense.tobytes()) + store / load / is_cache_consistent + compute_w_dense (the compressed → dense expansion: intercept broadcast, pattern orbit propagation with the UNSEEN/REPRESENTATIVE configs taking the frequency-weighted mean of the seen configs — the D-098 R2 ruling, the trained fallback weight logged not used, mobility np.interp with clamping); the 5th cache_manager consumer (uniform 7-kwargs wiring, flat rlmwf_10_GENERATE.dat + .SHA3-256, step 10); analysis D-097 (43-check probe scratch/verify_generate.py, tiers A–F, re-pinned to the post-campaign state, 0 mismatches): R1 (P0 — the D-074 R1 trap re-introduced in the worker, not here), R2 (the unseen/fallback semantics — Roberto's call, now documented in code), T1 (the missing version gate), T2 (the 2 missing no-validation notes), M1-M4 (dead f_w, the MOB duplicate, the literal msg, the np.interp note); the live rlm_02 golden re-derived (K = 6588 = 1 + 6561 + 27, orbit invariance, seen-config exactness, hash ec9d6545…b15b4); fix campaign D-098 CLOSED (T1-T2 + M1-M5 applied, T8 withdrawn as a false positive — the 3 blank lines above __all__ are the house pattern, 6/8 rlm_* data modules); module CLOSED (206 → 225 lines) | docs/src/twolm/rlm_generate.md |
| src/twolm/lm_worker_generate.py | introduced 2026-09-02 (session 27, Roberto's commit e31c061): the GENERATE worker (the 11th active level) — _up the cache_manager_load_or_compute flow (the 5th consumer, the uniform 7-kwargs wiring, flat rlmwf_10_GENERATE.dat + .SHA3-256) materializing ctx.w_dense + ctx.dense_w_checksum, _down clears both; fix campaign D-098 CLOSED: R1 the one-line rename to get_cache_file_full_path_for_current_level() (the D-074 R1 trap re-introduced — empirically the rlm_02 pipeline died at [10][GENERATE] AttributeError; the alias simulation proved the level otherwise works end-to-end), T3 the factory @validate_call + pydantic import (all 10 worker factories now share the pattern), T7 4 ws lines; the triple blank lines L43-45 / L47-49 are the house worker pattern (D-094 M4); 75 → 78 lines | docs/src/twolm/lm_worker_generate.md |
| src/twolm/test/test_rlm_generate.py | introduced 2026-09-02 (session 27, Roberto's commit e31c061): 1 class / 1 test at the bring-in (the 3-feature mock compute golden); D-098 T4 expansion: 4 classes / 14 tests, no DB, no gate — TestRLMGenerateCompute (the kept golden INT 0.5 / PAT weighted-mean −0.2 / MOB [1,1,2,3,3], the unknown-category RuntimeError message-pinned, the empty-MOB zeros + exactly-one-WARN), TestRLMGenerateCacheConsistency (2 branches), TestRLMGenerateIO (6 tests: the checksum=False round-trip, the hash golden 460c993d…07a, the valid sidecar, the corrupted-content gate, the wrong-description gate, the version-mismatch gate [T1] — the 3 header messages pinned), TestRLMGenerateInit (3 validation branches); T6 the Italian comment → English, T7 13 ws lines, M5 the dead mock ctx.z removed; 127 → 312 lines; suite 14/0/0 GREEN | docs/src/twolm/test/test_rlm_generate.md |
| src/twolm/test/test_lm_worker_generate.py | NEW 2026-09-02 (session 27, D-098 T5 — Roberto: "Aggiungi anche il file test_lm_worker_generate.py con i dovuti tests sul worker"; the bring-in had no worker test at all): 1 class / 3 tests, all DB-gated (the D-085 idiom, rlm_02, the setUp moves through OPTIMIZE — the lbfgs run) — test_compute_and_populate_cache (the pre-state None pins, the (6588,) float32 golden, the hash golden ec9d6545…b15b4 + the duck-typed identity, the flat files + sidecar verify, "Executing heavy computation"), test_read_cache_on_new_instance (2nd instance on the same base dir: "Cache successfully loaded and validated", no recompute, array-equal), test_down_clears_generate_attributes (the _down scope pin); 3/0/0 live (10.5 s), 3/0/3 gated; 185 lines | docs/src/twolm/test/test_lm_worker_generate.md |
| src/twolm/lm_worker_vld_positions.py | analyzed 2026-09-02 (session 28, D-099): the 12th active level, brought in by Roberto (commit ede2efe — the import L51 + worker-list entry L217 uncommented; RLMContext's 4 vld_* fields pre-declared at L146-149, the future vld_metrics / analytics_report at L152/155): the POSITIONS TWIN over the validation data set — it REUSES load_from_db + is_cache_consistent from lm_worker_positions (the keyword bid/status overrides; the DB connection + ec come from the shared regab_data_set block) with the uniform 7-kwargs cache_manager wiring (flat rlmwf_11_VLD_POSITIONS.dat + .SHA3-256 — the slot predicted in D-097/D-098); _up sets vld_positions / vld_game_values / vld_rds_checksum / vld_pop_stats, _down clears ALL FOUR (the house shape, no gap — contrast D-096 R4); 31-check probe (scratch/verify_vld_positions.py, tiers A–D; the pre-campaign state = the 6 worklist mismatches exactly): R1 (P0, the 2nd occurrence — L62 calls the nonexistent get_cache_file_full_path_for_next_level(), the D-074 R1 trap re-introduced as in D-097 R1; empirically: the rlm_02 pipeline dies at [11][VLD_POSITIONS]; the alias simulation proves the level works end-to-end: file + sidecar verify, (200,2) u64 positions, int8 game values [−58, 56], golden count 200 / mean 3.64 / std 23.809880302093077 / var 566.9104, vld_rds_checksum e8087903…f4c48 (distinct from the training 32da0ed3…), 2nd-instance cache hit, _down clearing), T1 (the factory lacks @validate_call + pydantic — all 10 sibling worker factories have it), T2 (5 dead imports: pathlib Path + RegabDataSet + RegabDBConnection + regab_extract_data_set_from_db — the file delegates extraction to lm_worker_positions.load_from_db), T3 (the load_fn is the raw function — checksum defaults True → double sidecar verify; the house shape is the checksum=False lambda, D-080 M4), T4 (3 ws-only lines L76/L92/L95; the import-block trailing ws L37/38/40 + the license header stay — the D-078 M3 / D-080 M3 house scope, as in lm_worker_positions), T5 (no test file at all — the bring-in ships zero tests; propose creating test_lm_worker_vld_positions.py per Roberto's call, the D-098 T5 pattern), M1 (the vld query inherits ec from regab_data_set — ValidationDataSetConfig declares only bid + status — document), M2 (the unpacked cache_hit unused — the identical positions L59 shape, keep), M3 (positive — the _down scope is complete); fix campaign D-100 CLOSED (Roberto: "T1 - T5: OK, M1 - M3: OK, Procedi, grazie" — R1 the one-line rename to _for_current_level (L65 post-fix; the 2nd occurrence of the D-074 R1 trap), T1 the factory @validate_call + pydantic (all 11 worker factories now uniform), T2 the 5 dead imports removed, T3 the load_fn checksum=False lambda (the D-080 M4 shape), T4 the 3 ws-only lines stripped (the import-block trailing ws stays, the D-078/D-080 M3 house scope), T5 test_lm_worker_vld_positions.py ADDED, M1 the inherited ec documented in the _up note L58-61, M2 keep (the unpacked cache_hit, the identical positions L59 shape), M3 positive (the _down scope); file 108 → 112 lines); suite 3/0/0 GREEN (test_lm_worker_vld_positions, all 3 tests DB-gated, run with the live DB; 3/0/3 gated) | docs/src/twolm/lm_worker_vld_positions.md |
| src/twolm/test/test_lm_worker_vld_positions.py | introduced 2026-09-02 (session 28, the D-100 campaign T5 — the bring-in ede2efe shipped zero tests): 1 class / 3 tests / no PERF — all DB-gated (gate first in setUp; the setUp moves to GENERATE on a fresh base dir, which runs the whole 11-level chain, so a live DB is required), the D-085 idiom (CUSTOM_TMP_BASE via twolm.test.paths, setUpClass mkdir, TemporaryDirectory first in setUp, defensive tearDown), rlm_02 (the validation block {bid [8], status CMS+CMR}): the first-run golden (200 positions, the structured dtype names ('mover','opponent'), the 1-D int8 game values, vld_rds_checksum e8087903…f4c48, pop_stats count 200 / mean 3.64, the flat rlmwf_11_VLD_POSITIONS.dat + .SHA3-256 + the binio sidecar verify, "Executing heavy computation"), the 2nd-instance cache hit ("Cache successfully loaded and validated", no "Executing heavy computation", array_equal + checksums equal), the _down pin (all four vld fields cleared on the move back to step 10); 195 lines; suite 3/0/0 GREEN (live DB, 8.5 s; 3/0/3 gated) | docs/src/twolm/test/test_lm_worker_vld_positions.md |
| src/twolm/lm_worker_validate.py | introduced 2026-09-02 (session 28, Roberto's commit 536eadc — the VALIDATE bring-in, the 13th active level): the THIRD non-cache worker (after FEATURES/ZED/GRADIENT) — no cache_manager wiring (the rlmwf_12 slot stays unused, confirmed live), _up publishes the ONE ctx.vld_metrics (the 7-key dict post D-102 M3), _down clears it; D-101 analysis: R1 + T1-T5 + M1-M3 worklist (28-check probe); fix campaign D-102 CLOSED (Roberto: all OK): T1 factory @validate_call + pydantic import (all 12 worker factories now share it), T2 the dead numpy import removed, T4 the 3 ws lines, M1 the RMSE/MAE ratio zero-guarded (the n/a line on a perfect Y-space fit — pre-campaign it raised ZeroDivisionError, demonstrated live); file 71 → 75 lines; module CLOSED | docs/src/twolm/lm_worker_validate.md |
| src/twolm/rlm_validate.py | introduced 2026-09-02 (session 28, Roberto's commit 536eadc): the FIRST dedicated data module of a non-cache pipeline level — validate_model(ctx) -> Dict[str, Any]: the forward pass over the validation positions (the same ctx.feature_set, the dense ctx.w_dense, sigmoid REUSED from rlm_gradient) returning the 7-metric dict (loss/mse_z/mae_z/mae_y/mse_y/rmse_y/samples); D-101 analysis + fix campaign D-102 CLOSED: R1 the `Any` import added (the PEP 563-masked latent NameError — the D-074 R2 class, nothing calls get_type_hints on it today; NO live crash unlike D-097/D-099 — the level has no cache-path call), T2 the 2 dead regab imports removed (the data comes from ctx.vld_*), T3 header rlm_config_schemas.py → rlm_validate.py, T4 the 27 ws lines (docstring included), M2 vld_P → underscore unpack (the D-096 M1 pattern), M3 vld_mse_y added to the dict (7 keys); report-only: the dense-mapping idiom (np.repeat + fancy indexing) vs rlm_generate's per-feature loop — both valid; file 152 lines (net 0: −1 import + 1 dict line); no dedicated suite (covered by test_lm_worker_validate + the probe D tier) | docs/src/twolm/rlm_validate.md |
| src/twolm/test/test_lm_worker_validate.py | NEW 2026-09-02 (session 28, D-102 T5 — the bring-in 536eadc shipped no tests): 1 class / 3 tests / no PERF, all DB-gated (gate first in setUp; the setUp moves to VLD_POSITIONS step 11 on a fresh base dir, which runs the whole 12-level chain, so a live DB is required), the D-085 idiom from day one (TemporaryDirectory under the shared CUSTOM_TMP_BASE, WORKSPACE_ROOT-anchored rlm_02.json, defensive tearDown): test_validate_model_goldens (the first run to VALIDATE step 12 — the pre-state None, the 7-key dict pinned EXACTLY: loss 0.00700794393196702, mse_z 0.01401588786393404, mae_z 0.09311295300722122, mae_y 12.161691665649414, mse_y 239.10484313964844, rmse_y 15.46301555633545, samples 200 + the 7 INFO log lines incl. RMSE/MAE 1.27), test_second_instance_deterministic (2nd instance on the same base dir: identical metrics — VALIDATE has no cache file, determinism is the pin — + exactly 6 "Cache successfully loaded and validated" hits, no "Extracted"), test_down_clears_vld_metrics (the _down scope pin); green on first run; suite 3/0/0 GREEN (live DB; 3/0/3 gated) | docs/src/twolm/test/test_lm_worker_validate.md |
| src/twolm/lm_worker_analytics.py | introduced 2026-09-02 (session 28, Roberto's commit 96dacb5 — the ANALYTICS bring-in, the 14th active level; "Ho aggiunto i due moduli lm_worker_analytics e rlm_analytics, non ci sono tests, vanno pensati e realizzati. Intanto partiamo con la analisi per favore."): the FIFTH non-cache worker (after FEATURES/ZED/GRADIENT/VALIDATE) — no cache_manager wiring (the rlmwf_12 slot stays unused, confirmed live); _up publishes the TWO ctx attributes (train_metrics — the 7-key dict from rlm_analytics.compute_training_metrics, the compressed forward pass — + analytics_report, the console report string, pre-stored for the SAVE worker), logs the 15-line console report line by line, writes the complete file report to base_dir/<cfg.analytics.report_file_name> (overwritten per run, NOT unlinked by _down — artifact semantics); _down clears both; D-103 analysis (33-check probe scratch/verify_analytics.py, tiers A–D; the pre-campaign state = the 7 worklist mismatches exactly): T1 (the factory lacks @validate_call + pydantic import — all 12 sibling worker factories have it), T2 (the dead pathlib Path import), T4 (6 ws lines), T5 (no test file), T6 (rlm_01.json detailed_report ["DIAG3"] → ["DIAG3", "LMC"] — the mobility-table branch gets end-to-end coverage), M1 (train_metrics set as an ad-hoc dataclass attribute — pre-declare it on RLMContext, the D-099 idiom, the worker's own comment says SAVE will consume it); T3 verified no-action (both headers already carry their own names — unlike D-102); M2/M3 in rlm_analytics; O1-O6 report-only (O1 the mixed-representation Generalization Gap — quantified: on rlm_02 0 of 1600 vld instances sit on an unseen orbit, the −0.13 gap is a clean train-vs-vld data difference); file 78 → 80 lines; D-105/M2: _up also publishes train_dense_metrics (the 4-key dense dict, the 2nd INFO line) before the format calls, _down clears 3 fields; 80 → 86 lines; module CLOSED (O1 RESOLVED by the 3-metric table + Substitution Delta row) | docs/src/twolm/lm_worker_analytics.md |
| src/twolm/rlm_analytics.py | introduced 2026-09-02 (session 28, Roberto's commit 96dacb5): the 2nd dedicated data module of a non-cache level — function-only like rlm_gradient / rlm_validate (3 public fns + 3 private helpers, no data class, no store/load, no cache_manager, no @validate_call — the rlm_indexes-L166 TYPE_CHECKING class): compute_training_metrics (the COMPRESSED forward pass — ctx.w over ctx.design_matrix, sigmoid REUSED from rlm_gradient, the 7-key dict; the TRAINING "Loss (MSE/2)" cell is opt_info['f'], the ridge-inclusive final objective), format_console_report (the 15-line header, no date), format_file_report (detailed header with Creation Date + feature-set summary + the per-feature tables — mobility C/IA/IC statuses, pattern C/AB/CL + principal indexes, print_rows gated by cfg.analytics.detailed_report); D-103 analysis + fix campaign D-103 CLOSED (Roberto: all OK): T2 the dead imports removed (sys + Optional/List), T4 the 39 ws lines stripped, M2 the annotation Dict[str, float \| int] (train_samples is an int), M3 the hasattr dead guard → direct access (the schema's default factory makes the field always exist); report-only: the O1 mixed representations (the dense VALIDATION column vs the compressed TRAINING column — the substitution delta is 0 on rlm_02, measured); file 456 → 453 lines; D-105/M2: the 3-metric header (TRAINING \| TRAINING-DENSE \| VALIDATION + the Population baseline line + the Substitution Delta row; the Generalization Gap redefined dense-vs-dense) + compute_training_dense_metrics (4 public fns); 453 → 522 lines; no dedicated suite (covered by test_lm_worker_analytics + the probe C/D tiers) | docs/src/twolm/rlm_analytics.md |
| src/twolm/test/test_lm_worker_analytics.py | NEW 2026-09-02 (session 28, D-103 T5 — the bring-in 96dacb5 shipped no tests; Roberto: "non ci sono tests, vanno pensati e realizzati"): 2 classes / 4 tests / no PERF, all DB-gated (gate first in setUp; the setUp moves to VALIDATE step 12 on a fresh base dir, which runs the whole 13-level chain, so a live DB is required), the D-085 idiom from day one (TemporaryDirectory under the shared CUSTOM_TMP_BASE, WORKSPACE_ROOT-anchored json, defensive tearDown) + the module-level _masked_report_hash helper (the file report embeds datetime.now() — the date-masked sha3_256 is the stable golden): TestLMWorkerAnalytics (rlm_02) — test_analytics_report_goldens (the pre-state None/None, the 7-key dict pinned EXACTLY: train_mae_y 12.346794566613694, train_rmse_y 15.58872172931622, train_loss 0.00712497066706419 (= opt_info['f']), train_samples 199952, pop_mae_y 21.729816221648974, pop_rmse_y 26.40637507956623, pop_loss 0.020437248051166534; the console report pins incl. "Total Parameters (W) : 2,981" / "Dense Parameters (K) : 6,588" / "Generalization Gap (RMSE) : -0.13"; the file report: EDGE rows + DIAG3 omitted (1 omitted line), no mobility table, date-masked hash 9b97746c69436fc23fd4f7a06274174d66ed1d0cb8467619b78a409e7f743c66; the log lines pinned), test_second_instance_deterministic (identical metrics + report — ANALYTICS has no cache file, determinism is the pin — + exactly 6 cache hits, no "Extracted" / "established successfully"), test_down_clears_analytics_attributes (both None; the file remains on disk); TestLMWorkerAnalyticsMobility (rlm_01, the ONLY fixture exercising the mobility table helper end-to-end — post D-103 T6 detailed_report ["DIAG3", "LMC"]) — test_mobility_and_pattern_tables (the train goldens: mae 9.874833279184258e-05, rmse 0.00013206900478667877, loss 4.704681197571781e-13, samples 10, pop_mae 15.6, pop_rmse 18.39565166010707, pop_loss 0.009125067852437496; "MOBILITY FEATURE: LMC (fid=1)" + "PATTERN FEATURE: DIAG3 (fid=2)" / "CORE (fid=3)" + exactly 1 omitted line + hash 77fa815ada656152b5f8f893134624d5d023ffc66e9c81e4fcda9a1ecc0c083d; the logs "CONVERGED_MIN_GRAD (16 iters)" + gap 27.22); D-105/M2 re-pin: the dense 4-key dict pins + the new header lines (the 3-metric Loss row, the Population line, the Substitution Delta row) + the new INFO log pin + the 2 file hashes (94a4af7e… / f6b54954…) + the rlm_01 gap 27.22 → 23.87 (the gap is now dense-vs-dense); 304 → 338 lines; 4/0/0 live (7.7 s), 4/0/4 gated | docs/src/twolm/test/test_lm_worker_analytics.md |
| src/twolm/test/data/rlm_01.json | test data (session 23, Roberto's commit 73b4342 — the WMAPS bring-in; the row was missing, restored 2026-09-01 with the D-093 analysis): JSON5 config fixture behind the wmaps / design_matrix / zed worker-test goldens (frequency_cut_off 2, logit_clipping 0.03, bid [7], status CMS, ec 20 — the 10-position dataset behind the 12c3344e… / da86a916… / 3d49fd5d… golden hashes); D-103 T6: analytics.detailed_report ["DIAG3"] → ["DIAG3", "LMC"] (the 65-row LMC mobility table prints in the ANALYTICS file report — the analytics block is consumed by the ANALYTICS level only, no other rlm_01-based golden affected) | — |
| src/twolm/test/data/rlm_02.json | test data (session 25, Roberto's commit a0adc6e — the GRADIENT bring-in): JSON5 config fixture for the gradient worker test (logit_clipping 0.01, ridge_regularization 0.01, frequency_cut_off 1, ec 20, bid [6, 7], no intercept, the DIAG3 + EDGE patterns, no mobilities — the 199952-position dataset; the "optimization" block now consumed by the OPTIMIZE level, 1ebdd8b/D-096; base of the lm_worker_generate golden, e31c061/D-097; base of the lm_worker_vld_positions golden — the validation block {bid [8], status CMS+CMR} → 200 positions, e8087903…f4c48, ede2efe/D-099) | — |
| src/twolm/lm_worker_save.py | introduced 2026-09-02 (session 29, Roberto's commit fe506c6 — the SAVE bring-in, the 15th and LAST active level — the bring-in itself uncommented the last 2 lines: import L54 + worker-list entry L221; the pipeline is COMPLETE: 15/15 workers, 0 commented imports): the SIXTH non-cache worker (after FEATURES/ZED/GRADIENT/VALIDATE/ANALYTICS) — a pure SINK: _up reads context attributes and writes ONE artifact, base_dir/<cfg.output> (the model weights file, lz4 + .SHA3-256 sidecar via binio), with exactly 2 INFO log lines ("Saving model weights to disk..." / "Model weights saved to <path>"); _down is a NO-OP (no context attribute cleared — the only such worker; the artifact is never unlinked — artifact semantics, like the ANALYTICS report); D-104 analysis + fix campaign D-104 CLOSED (Roberto: T1/T2/T4/T5/T6/M1 + O4/O5 OK, "Procedi!"): T1 the factory got @validate_call + the pydantic import (all 14 worker factories now uniform — the D-092/D-098/D-100/D-103 T1 convention completed), T2 the dead pathlib Path import removed, T4 the 2 ws lines; report-only: the terminal consumer of the ctx.analytics_report / ctx.train_metrics attributes pre-stored "if needed by the SAVE worker later"; 61 lines post D-104; module CLOSED | docs/src/twolm/lm_worker_save.md |
| src/twolm/model_weights.py | introduced 2026-09-02 (session 29, Roberto's commit fe506c6): the 3rd data module of the pipeline family and the FIRST with a plain @dataclass (no pydantic): ModelWeights (10 fields in file order: version, name, ec, logit_clipping, opt_info, training_pop_stats, vld_metrics, feature_set, iwmap_feature_offset, w_dense) + the header constants (RGLM_BINARY_WEIGHTS / v1) + model_weights_write_file (the lz4 binary of the INFERENCE subset: tps 4/4 with f32 truncation, opt_info 4/5 — no converged (derivable from reason), vld 4/7 — no mse_z/mae_z/mse_y, the full FeatureSet, the boundary u32 + w_dense f32) + model_weights_read_file (the mirror + the 2 ValueError guards: "File header mismatch, expected 'RGLM_BINARY_WEIGHTS', found '...'." / "File header version, expected '1', found '...'." — both pinned by the test module); D-104: T4 the 2 ws lines; no @validate_call (consistent with rlm_validate / rlm_analytics — the rlm_indexes-L166 class); 237 lines; no dedicated suite (covered by the full-chain read-back pins + the verify_save B tier) | docs/src/twolm/model_weights.md |
| src/twolm/rlm_client.py | introduced 2026-09-02 (session 29, Roberto's commit fe506c6): the first pure CONSUMER module — the inference API for saved models (the production context of Roberto's endgame-solver A2xxx family): make_evaluation_function(mw) → ef: Position → float in Y space: compute_indexes (the feature.py batch API, [0] unwrap) → w_dense gather via expanded_offsets (np.repeat(offsets[:-1], n_instances) — the rlm_wmaps-L212-213 boundary-array construction verified) → sum → sigmoid (reused from rlm_gradient) → z2y (reconstructed from mw.logit_clipping via zed_fun_factory — why the zed transforms are not persisted); D-104: T2 the dead model_weights_read_file import removed, T4 the 5 ws lines, M1 __all__ = ['make_evaluation_function']; the dense-path / substitution-rule section (the D-104 O1 correction, Roberto's: forward_dense(training) == forward_compressed(training) ONLY when no configuration is below the frequency_cut_off; measured: rlm_04 cut 10 → 1923/199932 training positions differ (373 IC EDGE configs, max \|Δy\| 31.56, mean 4.98), rlm_01 cut 2 → 5/10, cut-1 fixtures identical) | docs/src/twolm/rlm_client.md |
| src/twolm/test/test_lm_worker_full_chain.py | NEW 2026-09-02 (session 29, D-104 — shipped by the bring-in fe506c6; Roberto: "Procedi!"): the END-TO-END test — the only suite running the full 15-level chain (CREATED → SAVE) in one go; post D-104 T5 the D-085 idiom + the SKIP_REGAB_DB gate FIRST in both setUps (the bring-in had NO gate — proved test-side-only convention: no production code reads it, the ungated A2030 would ERROR on a DB-less machine in "gated" mode) + WORKSPACE_ROOT / CUSTOM_TMP_BASE (the bring-in was CWD-locked) + the "#: ###" removed + the How-to-run block; 5 tests / 3 classes: TestFullChainA2030 (rlm_04, "Short-Long Test 04", EDGE+LMC, cut 10, 199932/20000, ~3 s) — test_full_worker_chain (ALL EXACT goldens: vld 7 / train 7 / pop 4 / opt 5-key / file 21603 B sha3 bcf8d918… + sidecar / read-back (tps f32 truncations pinned as distinct values, fs hash ec4f1537…, iwmap [0,1,66,6627], w_dense (6627,) f32 sha3 7ecdeba6…) / EF 6 training positions bit-exact + the O4 pin ef(vld_positions[42]) = 11.932792663574219 (the substitution path: cut 10 + bid [5] vld) / console + file-report (masked hash 90fe4cf6…) pins) + test_second_instance_deterministic (NEW T6: byte-identical file + 6 cache hits — CONFIG re-stores its snapshot, a 'stored' line, not a hit); TestFullChainA2050 (rlm_03, "Long Test 03", 11 "A2050" patterns + LMC, cut 1, 1999179/199932, LONG-gated ~10 min) — the same golden family (file 515042 B sha3 3ad18058…, fs 2c8bb32b…, w_dense (167331,) sha3 a012689f…, EF 6 positions bit-exact, console + masked report pins); TestModelWeightsReadGuards (NEW T6 — ungated, no DB: the 2 ValueError guards with exact messages); T6 replaced the bring-in's 3-4-significant-digit pins with assertEqual goldens; 291 → 444 lines; D-105/M2 re-pin (the dense 4-key dict pins + the 3-metric header pins — rlm_04 gap 0.19 → 0.18 + Substitution Delta 0.01, rlm_03 gap 0.32 kept + delta -0.00 — + the file hashes d44557a8… / 57f9766b…); 444 → 467 lines | docs/src/twolm/test/test_lm_worker_full_chain.md |
| src/twolm/test/data/rlm_03.json | test data (session 29, Roberto's commit fe506c6): JSON5 config fixture for the full-chain A2050 test (the class name is Roberto's legacy production naming — A2050 = the endgame-solver ec-20 model; production runs A2050/A2150/A2250, ...): name "RGLM (Logistic) - Long Test 03 (rlm_03.json)", bid [3] train (CMR+CMS, 1999179 samples) / bid [6] vld (199932), ec 20, frequency_cut_off 1, logit_clipping 0.01, intercept + the 11 "A2050" patterns (XEDGE, CORNER, R2-R4, DIAG4-8, 2X5COR) + LMC, output rglm_logistic_model_ec_20_TEST03.dat (pre-provisioned for the SAVE worker), detailed_report ["XEDGE"], m=93/500 → CONVERGED_MIN_GRAD (397 iters, ~10 min) | — |
| src/twolm/test/data/rlm_04.json | test data (session 29, Roberto's commit fe506c6): JSON5 config fixture for the full-chain A2030 test (the class name is the legacy production naming; the fixture is EDGE+LMC): name "RGLM (Logistic) - Short-Long Test 04 (rlm_04.json)", bid [6] train (199932 samples) / bid [5] vld (20000), ec 20, frequency_cut_off 10, logit_clipping 0.01, intercept + the "EDGE" pattern + LMC, output rglm_logistic_model_ec_20_TEST04.dat, detailed_report ["EDGE","LMC"], m=19/100 → CONVERGED_MIN_GRAD (67 iters, ~3 s); the cut 10 makes it the fixture exercising the w_dense substitution path (373 IC EDGE configs in wmap_fallback) | — |
| logistello-papers/ | reference material, read-only | user's papers |

## Conventions in the code (respect them in any new work)

- Board vocabulary is canonical: **row** (1–8, top→bottom) and
  **column** (A–H, left→right) — never file/rank (chess). A1 =
  top-left (N-W) = bit 0; H8 = bottom-right (S-E) = bit 63.
  row_1 = [A1..H1]; column_a = [A1..A8]. Full text: notes/naming.md
  (D-013).
- Dual scalar/array API: public functions accept scalar OR 1-D array,
  return the input kind. Same validation pattern everywhere
  (is_scalar → atleast_1d → ndim check → dispatch → reshape back).
- `@validate_call` (pydantic, arbitrary_types_allowed) on all public
  functions.
- Numba `njit(cache=True)` + `prange` for hot loops; numba overloads
  for the four D8 primitives (fa1h8, fh1a8, fhori, fvert).
- Position = numpy structured dtype `[('mover', u64), ('opponent',
  u64)]`.
- Move codes: 0..63 = squares, 64 = PA (pass), 65 = NA, 66 = UN.
- D8 slot order is fixed and load-bearing (D-014): anti-transform
  slot s = T_s^{-1}; in pattern.py instance 0 = the ro000 image, and
  trans_fs/anti_trans_fs are indexed by instance (length =
  n_instances), not by slot.
- Pattern config indexes are base-3 uint32 over ≤ 18 squares
  (S ≤ 18); packed bit k ↔ the k-th square of `Pattern.squares`
  (ascending board order); principal index = min over the
  induced-stabilizer orbit.
- Test artifacts (D-065): unit tests write files ONLY under
  `workspace_root/build/tmp` and remove them afterwards (a
  `finally`/cleanup unlink, so a failing test leaves no garbage);
  no test writes anywhere else (notably: not the CWD). `build/` is
  gitignored.

## Environment

- Venv: `.venv/` (gitignored, D-010), Python 3.12.3, created
  2026-08-25.
- Packaging: `pyproject.toml` (setuptools, src layout) with twolm
  installed editable in .venv (`pip install -e .`, D-011) —
  `import twolm` works without PYTHONPATH, resolving to src/.
- Dependencies (pyproject.toml, minimal set, kept in step with the
  modules brought in): numpy ≥ 2.0 (bitboards / structured dtypes;
  the code requires NumPy ≥ 2.0 — board.md R5), pydantic ≥ 2
  (@validate_call), numba ≥ 0.60 (njit / prange / overload; pulls
  llvmlite), lz4 (binio, D-051), psycopg2 / pandas / python-dotenv
  (regab, D-052). Installed in .venv: numpy 2.5.2, pydantic 2.13.4,
  numba 0.67.0, llvmlite 0.49.0.
- Test command: `.venv/bin/python -m unittest twolm.test.<module>`
  (the old `PYTHONPATH=./src` prefix still works as a fallback);
  test_regab needs a live PostgreSQL + .env, or `SKIP_REGAB_DB=1` to
  skip the 35 DB tests (2 mocked run).
- Suite status (2026-09-02): board 193/0/12, pattern 64/0/3,
  mobility 26/0/1, feature 20/0/1, binio 48/0/0 (45 + 3 usage),
  regab 37/0/0 (2 mocked run, 35 DB skipped under SKIP_REGAB_DB=1),
  opt_lbfgs 13/0/0, state_machine 49/0/0, cache_manager 21/0/0,
  logistic_model 15/0/0 (all 15 active — the last muted test
  restored session 28 (887880e, the D-073/D-075 T3 plan); D-074/
  D-075 fix batches; D-076 restored delegation test),
  lm_worker_config 14/0/0 (D-076), lm_worker_positions 2/0/0
  (601de87; 2 DB-gated, run with live DB), lm_worker_features
  2/0/0 (f051dd3; 2 DB-gated post D-082, run with live DB),
  rlm_indexes 14/0/0 (a323e0f; 14 tests post D-084 M2 — no DB,
  all file I/O mocked), lm_worker_indexes 2/0/0 (a323e0f; 2
  DB-gated post D-084 T2 — the setUp moves through POSITIONS,
  run with live DB), paths 3/0/0 (D-085 — no DB, pure path
  assertions), rlm_wmaps 13/0/0 (73b4342 + D-087 T10 — no DB,
  no gate), lm_worker_wmaps 3/0/0 (73b4342; 3 DB-gated post
  D-087 T1 — the setUp moves through INDEXES, run with live DB),
  lm_worker_design_matrix 3/0/0 (D-090 T1 — 3 DB-gated;
  the setUp moves through WMAPS, run with live DB),
  rlm_design_matrix 12/0/0 (D-090 T6 — no DB, no gate),
  rlm_zed 10/0/0 (D-092 T3 — no DB, no gate), lm_worker_zed 3/0/0
  (439c966 + D-092 T1 — 1 DB-free + 2 DB-gated; the setUp moves
  through DESIGN_MTR, run with live DB), lm_worker_gradient 2/0/0
  (a0adc6e + D-094 T5 — 2 DB-gated; the setUp moves through ZED,
  run with live DB), test_rlm_gradient 8/0/0 (D-094 M1 — no DB,
  no gate), rlm_optimize 19/0/0 (1ebdd8b + D-096 M10 — no DB, no
  gate), lm_worker_optimize 3/0/0 (1ebdd8b; 3 DB-gated post
  D-096 T1 — the setUp moves through GRADIENT, run with live DB),
  rlm_generate 14/0/0 (e31c061 + D-098 T4 — no DB, no gate),
  lm_worker_generate 3/0/0 (e31c061 + D-098 T5 — 3 DB-gated; the
  setUp moves through OPTIMIZE, run with live DB),
  lm_worker_vld_positions 3/0/0 (D-100 T5 — 3 DB-gated; the
  setUp moves through GENERATE, run with live DB),
  lm_worker_validate 3/0/0 (D-102 T5 — 3 DB-gated; the setUp
  moves through VLD_POSITIONS, run with live DB),
  lm_worker_analytics 4/0/0 (D-103 T5 — 4 DB-gated; the setUp
  moves through VALIDATE, run with live DB),
  test_lm_worker_full_chain 5/0/1 live (D-104 — 2 A2030 + 2 read
  guards run, the A2050 LONG-skipped; the A2050 chain is ~10 min,
  run only with LONG=1; 3 DB-gated under the gate — 2/0/3 gated;
  the 15-level END-TO-END chain + the full saved-model round-trip)
  — all GREEN.
  Totals: 673 tests, 87 skipped under the gate (17
  PERF=1 print-only performance tests + 35 DB-gated regab tests +
  2 DB-gated lm_worker_positions tests + 2 DB-gated
  lm_worker_features tests + 2 DB-gated lm_worker_indexes tests +
  3 DB-gated lm_worker_wmaps tests + 3 DB-gated
  lm_worker_design_matrix tests + 2 DB-gated lm_worker_zed tests +
  2 DB-gated lm_worker_gradient tests + 3 DB-gated
  lm_worker_optimize tests + 3 DB-gated lm_worker_generate tests
  + 3 DB-gated lm_worker_vld_positions tests — D-100 T5 + 3
  DB-gated lm_worker_validate tests — D-102 T5 + 4 DB-gated
  lm_worker_analytics tests — D-103 T5 + 2 DB-gated
  test_lm_worker_full_chain A2030 tests — D-104 T5 + 8 board.py
  M-sweep pins — D-111 + 1 PatternSet __repr__ pin — D-112; the
  A2050
  full-chain test is LONG-gated; no
  performance gates in any suite, D-036). Warm run ≈ 0.5 s
  (board) / ≈ 2.6 s (gated full discover) / ≈ 45 s (live full
  discover, numba cache warm in src/twolm/__pycache__/).

## Where we are

Current state only — the session-by-session history lives in the
journal volumes (notes/log_NNN.md) and the decision log
(notes/decisions.md); the D-pointers index that history.

- board.py — the complete Reversi game kernel (200 random full
  games verified on the public API; no game-loop module
  planned, I-005). All issues closed: R1–R5 (D-017 era) + the 7
  minors M1–M7 (D-111). Suite 201/0/12.
- test_board.py — fix campaign complete (D-026..D-033); header
  'environmeant' typo fixed (D-050); the remaining grammar nit
  stays reported-only. Suite 201/0/12.
- pattern.py — complete: principal mask = numerically lowest
  orbit (D-020), minor sweep 19/19 (D-023/024/025), Burnside
  attributes (D-032), PatternSet.__repr__ (D-112). Suite 65/0/3.
- test_pattern.py — fix campaign closed (D-026..D-033, T17
  sqa8/sqh1 fixture swap); 21/21 goldens re-derived. PARKED,
  awaiting Roberto's GO: T18 (np.uint8 3**n_squares overflow,
  noted-only) + M1 (stale PatternSet Raises docstring). Suite
  65/0/3.
- mobility.py — mobility / MobilitySet + popcount64 SWAR kernel;
  disposition per D-036 (PERF tests print-only, no perf gate).
  Suite 26/0/1.
- test_mobility.py — analyzed (D-037), 13 verified facts. Suite
  26/0/1.
- feature.py — Feature / FeatureSet (blocked __new__, 3
  factories, composition, sorted-order); R/M campaign closed
  (D-038..D-042); the OPEN R1 (unused BeforeValidator import)
  fixed at D-110. Suite 19/0/1.
- test_feature.py — 9 verified facts (D-043); header typo fixed
  with D-050. Suite 19/0/1.
- binio.py — binary IO layer; T1–T4 batch (D-051); empty-suffix
  fix (D-095). Suite 48/0/0.
- test_binio.py — T4 batch (D-051); 3 empty-suffix tests
  (D-095). Suite 48/0/0.
- regab.py — PostgreSQL regab access layer; T1–T7 batch
  (D-052). Suite 37/0/0.
- test_regab.py — T5/T6/T7 batch (D-052) incl. the 4
  SQL-injection tests + SKIP_REGAB_DB gate. Suite 37/0/0.
- opt_lbfgs.py — LBFGS solver; T1–T7 batch (D-053, incl. the
  RuntimeException hard-bug fix). Suite 13/0/0.
- test_opt_lbfgs.py — T7 batch + 9 new tests (D-053). Suite
  13/0/0.
- state_machine.py — generic pipeline orchestrator (Workers up/
  down + Context + logging / history / CSV); R/M/T campaign
  closed (D-057..D-070, D-074, D-078); standing contracts:
  sentinel worker 0 (D-059), failure semantics (D-060), unique
  names (D-061), *_for_current_level naming (D-069). Suite
  49/0/0.
- test_state_machine.py — 13 original expectations
  independently re-derived; T/R/M pins per the D-057..D-070
  campaign. Suite 49/0/0.
- cache_manager.py — generic load-or-compute cache pipeline
  (.SHA3-256 sidecar, 8192-chunk verify); fix campaigns closed
  (D-071/D-072). Suite 21/0/0.
- test_cache_manager.py — 21 tests; the D-085 idiom applied
  (D-072). Suite 21/0/0.
- base_model.py — thin facade base over StateMachine (pure
  delegation); campaign closed (D-074/D-075).
- logistic_model.py — the RLM facade: RLMContext blackboard (40
  fields, 8 *_checksum, 3 injected callables) + the 15-level
  worker list, activated line by line (D-076..D-104); M1 the
  stale 'Remove comments' line dropped (D-113). Suite 17/0/0.
- test_logistic_model.py — all 15 methods active (the last
  muted test restored, 887880e); D-075/D-076/D-078 corner
  pins. Suite 15/0/0.
- lm_worker_config.py — the CONFIG worker (JSON5 → config →
  base_dir validation + cache storicizzazione); campaign closed
  (D-077/D-078). DEFERRED: R1 the ad-hoc cache flow (the D-078
  ruling, revisit with the pipeline completion; I-011). Suite
  15/0/0.
- test_lm_worker_config.py — 15 tests (D-078). Suite 15/0/0.
- lm_worker_positions.py — the POSITIONS worker: first
  cache_manager consumer over the regab data set; campaign
  closed (D-079/D-080). Suite 9/0/0.
- test_lm_worker_positions.py — Roberto's file; gate + D-085
  idiom applied (D-080). Suite 9/0/0.
- rlm_config_schemas.py — the pydantic config domain (the
  ReversiLogisticModelConfig JSON5 entry point); campaign closed
  (D-079/D-080). Suite 13/0/0.
- lm_worker_features.py — the FEATURES worker (the first
  pure-compute level — no cache file ever); closed
  (D-081/D-082). Suite 3/0/0.
- test_lm_worker_features.py — Roberto's file; D-065/D-085
  idiom applied (D-082). Suite 3/0/0.
- rlm_indexes.py — the INDEXES data module; closed
  (D-083/D-084). Suite 14/0/0.
- lm_worker_indexes.py — the INDEXES worker (uniform 7-kwargs
  cache wiring); closed (D-083/D-084). Suite 2/0/0.
- test_rlm_indexes.py — 14 tests (D-084). Suite 14/0/0.
- test_lm_worker_indexes.py — end-to-end cache round-trip pin
  (D-084). Suite 2/0/0.
- paths.py + test_paths.py — the single home for
  workspace-root-anchored test paths (D-085); 3 pin tests.
- rlm_wmaps.py + lm_worker_wmaps.py — the WMAPS data object +
  6th-level worker; closed (D-086/D-087/D-088).
- test_rlm_wmaps.py + test_lm_worker_wmaps.py — the WMAPS test
  suites (D-087). Suite 13/0/0 + 3/0/0.
- rlm_design_matrix.py + lm_worker_design_matrix.py + both test
  files — the DESIGN_MTR 7th level; closed (D-090, incl. the
  dedicated 12-test data suite). Suite 3/0/0 + 12/0/0.
- rlm_zed.py + lm_worker_zed.py + both test files — the ZED 8th
  level (the first non-cache level); closed (D-091/D-092, incl.
  the dedicated 10-test data suite). Suite 3/0/0 + 10/0/0.
- rlm_gradient.py + lm_worker_gradient.py + both test files —
  the GRADIENT 9th level (the second non-cache; the float32
  contract, D-094 R1); closed (D-093/D-094, incl. the dedicated
  8-test data suite). Suite 2/0/2 gated + 8/0/0.
- rlm_optimize.py + lm_worker_optimize.py + both test files —
  the OPTIMIZE 10th level; the only level whose "cache" is a
  plain checkpoint dict via binio; closed (D-096). Suite 19/0/0
  + 3/0/3.
- rlm_generate.py + lm_worker_generate.py + both test files —
  the GENERATE 11th level (dense weights materialization);
  closed (D-097/D-098, incl. the R1 for-next-level trap fix).
  Suite 14/0/0 + 3/0/3.
- lm_worker_vld_positions.py + test_lm_worker_vld_positions.py
  — the VLD_POSITIONS 12th level (the POSITIONS twin over the
  validation set); closed (D-099/D-100). Suite 3/0/3.
- lm_worker_validate.py + rlm_validate.py +
  test_lm_worker_validate.py — the VALIDATE 13th level (the
  third non-cache worker; the first dedicated data module of a
  non-cache level); closed (D-101/D-102). Suite 3/0/3.
- lm_worker_analytics.py + rlm_analytics.py +
  test_lm_worker_analytics.py — the ANALYTICS 14th level (the
  training metrics + console / file reports); closed (D-103,
  D-105/M2: the 3-metric header + dense metrics). Suite 4/0/4.
- lm_worker_save.py + model_weights.py + rlm_client.py — the
  SAVE 15th and LAST level + the model_weights @dataclass + the
  inference client: the pipeline is 15/15 complete (D-104).
- test_lm_worker_full_chain.py — the END-TO-END suite (the full
  15-level chain, A2030 live + A2050 LONG-gated); D-104/D-105
  pins.
- Re-verification pass (2026-08-29, session 17): binio, regab,
  opt_lbfgs re-checked against source — every T-fix in place,
  suites GREEN, stale docs corrected.
- The plan (confirmed by Roberto, 2026-08-28): port the ENTIRE
  pipeline — the original repo brought in module by module —
  with VERIFIED code and COMPLETE tests as the goal: a solid
  base before further evolution (his list of future changes is
  out of scope). DONE: all 15 pipeline levels active (15/15);
  the game-loop module is NOT in the plan (I-005 resolved).
- Sources live in the `twolm` package under src/ (D-008); unit
  tests in src/twolm/test/. Environment: .venv with the pinned
  deps (D-010/D-051/D-052), twolm installed editable (D-011).
  Git repo on master (D-003). Collaboration memory: AGENTS.md
  (constitution) + notes/rules.md (active rules) + this file
  (state) + notes/ (the log: decisions.md + journal volumes,
  format rules in log_rules.md).

## Next steps

- Parked (no action planned): test_pattern T18 noted-only
  (np.uint8 3**n_squares overflow — external expressions must
  cast to int); test_pattern M1 (the stale PatternSet Raises
  docstring) — awaiting Roberto's go-ahead.
- Reported-only: the test_board.py header grammar nit (the
  'environmeant' typo itself fixed 2026-08-29, D-050).
- Feed notes/ideas.md with Roberto's future-evolution ideas.
- Open (awaiting Roberto's call): the endgame-solver
  integration of rlm_client (the production context of the
  A2xxx family) — the only open item on the pipeline side.
- Deferred: lm_worker_config R1 (the ad-hoc cache flow) — the
  D-078 ruling, revisit with the pipeline completion (I-011).
- Journal: log_001.md is over the 2000-line cap (log_rules.md)
  — rotate to log_002.md at the next session boundary.
- Next concrete action: the D-115 notes restructure (this
  session) — after it, no active work remains; the ball is with
  Roberto on the parked / open / deferred items above.

## Index

- docs/src/twolm/board.md — board.py mirror (MIGRATED at D-106
  step 4, schema validation: 4-line header, 68-name API table,
  Architecture, pinned invariants, Conventions, Integration; the
  verbatim session-1 review in
  notes/analyses/board_session1_review.md; then D-111 2026-09-06:
  all 7 open minors M1-M7 fixed — Open issues now None., suite
  201/0/12)
- docs/src/twolm/pattern.md — pattern.py mirror (MIGRATED at D-106
  step 5: 4-line header, 6-name API table, Architecture, 13 pinned
  invariants, Conventions, Integration; the verbatim session-4
  review in notes/analyses/pattern_session4_review.md; then D-112
  2026-09-06: the PatternSet __repr__ row + pin, Open issues now
  None., suite 65/0/3)
- docs/src/twolm/test/test_board.md — test_board.py mirror
  (MIGRATED at D-106 step 28, the FINAL batch: schema §6 — the
  5-area Coverage table rebuilt from the post-T-campaign 2377-line /
  193-test file, the ar print + D8 golden pins; the verbatim
  session-2 review in
  notes/analyses/test_board_session2_review.md)
- docs/src/twolm/test/test_pattern.md — test_pattern.py mirror
  (MIGRATED at D-106 step 28, the FINAL batch: schema §6 — the
  13-class Coverage table rebuilt from the post-campaign 1859-line /
  64-test file, the pack/Cayley/symmetry/hash goldens; the verbatim
  session-8 review in
  notes/analyses/test_pattern_session8_review.md)
- docs/src/twolm/mobility.md — mobility.py mirror (MIGRATED at
  D-106 step 24, MOBILITY batch: the LMC/ALMC/DLMC glossary, the
  index formula + n_configurations semantics, the sorted-column
  contract, the set hash, the 5 left-as-is conventions; invariants
  pinned to the 5-section probe + the 26-test suite; the verbatim
  session-10 review in notes/analyses/mobility_session10_review.md)
- docs/src/twolm/test/test_mobility.md — test_mobility.py mirror
  (MIGRATED at D-106 step 24, MOBILITY batch: schema §6 — 2 classes
  / 26 tests, the post-D-037 class lines, the [53,13,66] + hash
  literal goldens; the verbatim session-10 review in
  notes/analyses/test_mobility_session10_review.md)
- docs/src/twolm/feature.md — feature.py mirror (MIGRATED at
  D-106 step 10, FEATURES batch: the factory-only Feature +
  FeatureSet, the hash-over-child-hashes contract, the
  compute_indexes column layout, 19-test suite pins, NEW OPEN R1
  = the unused BeforeValidator import; the verbatim session-11
  review in notes/analyses/feature_session11_review.md)
- docs/src/twolm/test/test_feature.md — test_feature.py mirror
  (MIGRATED at D-106 step 10, FEATURES batch: 4 classes / 19+1
  PERF coverage map, the f5663932 hash + 3x10 matrix + 51-instance
  goldens; the file unchanged since D-050; the verbatim
  session-11 review in notes/analyses/test_feature_session11_review.md)
- docs/src/twolm/binio.md — binio.py mirror (MIGRATED at D-106
  step 22, BINIO batch: the C/Rust framing module — the 4 on-disk
  record layouts, the 3 D-095 empty-suffix guards, the
  incremental/deferred SHA3-256 + LZ4 strategies; invariants pinned
  to the 48-test suite, no dedicated probe; the verbatim session-14
  review in notes/analyses/binio_session14_review.md)
- docs/src/twolm/test/test_binio.md — test_binio.py mirror
  (MIGRATED at D-106 step 22, BINIO batch: schema §6 — the 9-class /
  45-test Coverage table + the 3 usage tests pinned; the verbatim
  session-14 review in
  notes/analyses/test_binio_session14_review.md)
- docs/src/twolm/regab.md — regab.py mirror (MIGRATED at D-106
  step 26, REGAB batch: the DB-access + binio serialization layer,
  the 7-line API table, the on-disk format, the ContextVar
  double-decorator order, the 6 argument validators incl. the T7
  SQL-injection guard; V1-V5 pinned to the named suite tests; the
  verbatim session-15 review in
  notes/analyses/regab_session15_review.md)
- docs/src/twolm/test/test_regab.md — test_regab.py mirror
  (MIGRATED at D-106 step 26, REGAB batch: schema §6 — the 6-class
  Coverage table with the post-D-085 class lines, the b507cd34…
  golden + the .env extraction expectation; the verbatim session-15
  review in notes/analyses/test_regab_session15_review.md)
- docs/src/twolm/opt_lbfgs.md — opt_lbfgs.py mirror (MIGRATED
  at D-106 step 16, OPTIMIZE batch: the standalone L-BFGS
  engine — strong Wolfe line search, two-loop recursion,
  restart, dual convergence, warm-start, the 7-param save_fn;
  the verbatim session-22 review in
  notes/analyses/opt_lbfgs_session22_review.md)
- docs/src/twolm/test/test_opt_lbfgs.md — test_opt_lbfgs.py
  mirror (MIGRATED at D-106 step 16, OPTIMIZE batch: 7 classes
  / 13 tests — the 4 test functions, the warm-start, the T1
  regression pin; the verbatim session-22 review in
  notes/analyses/test_opt_lbfgs_session22_review.md)
- docs/src/twolm/state_machine.md — state_machine.py mirror
  (MIGRATED at D-106 step 7: 5-name API table, the state model +
  D-059 sentinel + D-060 failure semantics + D-076 separate gate +
  D-070 injection + D-078 verbatim cache prefix in Architecture,
  13 pinned invariants over the 49-test suite, Open issues None;
  the verbatim session-19 review in
  notes/analyses/state_machine_session19_review.md)
- docs/src/twolm/test/test_state_machine.md — test_state_machine.
  py mirror (MIGRATED at D-106 step 28, the FINAL batch: schema §6 —
  the 5 classes / 49 tests with the full pin inventory incl. the
  E2/E3 full-message pins converted from the probe at D-106 step 3;
  the D-057..D-070 campaign narrative frozen in
  notes/analyses/test_state_machine_session19_review.md)
- docs/src/twolm/cache_manager.md — cache_manager.py mirror
  (MIGRATED at D-106 step 23, CACHE_MANAGER batch: the 4-step
  load-or-compute pipeline, the two-checksum distinction, the D-072
  binio sidecar adoption; invariants pinned to the 6-check probe +
  the 22-test suite; the verbatim session-20 review in
  notes/analyses/cache_manager_session20_review.md)
- docs/src/twolm/test/test_cache_manager.md — test_cache_manager.py
  mirror (MIGRATED at D-106 step 23, CACHE_MANAGER batch: schema
  §6 — 3 classes / 22 tests, the D-106 step-3 class-a §4 conversion
  of probe V17; the verbatim session-20 review in
  notes/analyses/test_cache_manager_session20_review.md)
- docs/src/twolm/base_model.md — base_model.py mirror (MIGRATED at
  D-106 step 28, the FINAL batch: the thin facade base class over
  the StateMachine, the 8-row API table, V1-V4 pinned to the named
  test_logistic_model tests + the 21-check family probe; the verbatim
  session-21 review in
  notes/analyses/base_model_session21_review.md)
- docs/src/twolm/logistic_model.md — logistic_model.py mirror
  (MIGRATED at D-106 step 6: 2-name API table, the 4-step
  construction + the 40-field blackboard + the 15/15 complete
  pipeline in Architecture, 13 pinned invariants (the 21-check
  probe + the 17-test suite); the verbatim session-21 review in
  notes/analyses/logistic_model_session21_review.md; then D-113
  2026-09-06: the stale 'Remove comments' line dropped, Open
  issues now None.)
- docs/src/twolm/test/test_logistic_model.md — test_logistic_model.
  py mirror (MIGRATED at D-106 step 28, the FINAL batch: schema §6 —
  the 1 class / 17 tests incl. the 2 step-3 probe conversions (D1 /
  E4b), the testbed design with the module-namespace factory
  patches; the verbatim session-21 review in
  notes/analyses/test_logistic_model_session21_review.md)
- docs/src/twolm/lm_worker_config.md — lm_worker_config.py mirror
  (MIGRATED at D-106 step 8, CONFIG batch #1: 2-name API table,
  the _up flow + the 3 precise-OS-type base_dir gates + the
  load-or-store cache flow, invariants pinned to the 25-check
  probe + the 15-test suite, R1 deferred open (I-011); the
  verbatim session-21 review in
  notes/analyses/lm_worker_config_session21_review.md)
- docs/src/twolm/test/test_lm_worker_config.md —
  test_lm_worker_config.py mirror (MIGRATED at D-106 step 8,
  CONFIG batch #1: the 4-class coverage map, the goldens — bare-
  hex sidecar, flat path, the gate messages, the properties-bag
  values; the verbatim session-21 review in
  notes/analyses/test_lm_worker_config_session21_review.md)
- docs/src/twolm/lm_worker_positions.md — lm_worker_positions.py
  mirror (MIGRATED at D-106 step 9, POSITIONS batch: 3-name API
  table, the 4-step cache_manager wiring + is_cache_consistent +
  the 5-arg load_from_db, 13 pinned invariants (21-check probe +
  9-test suite), Open issues None; the verbatim session-22 review
  in notes/analyses/lm_worker_positions_session22_review.md)
- docs/src/twolm/rlm_config_schemas.md — rlm_config_schemas.py
  mirror (MIGRATED at D-106 step 8, CONFIG batch #1: the 14-name
  API table, the bitboard mask pair + the strong-Wolfe validator +
  the strictness rules, 13 invariants pinned to
  test_rlm_config_schemas.py — the step-3 E-section conversion;
  the verbatim session-22 review in
  notes/analyses/rlm_config_schemas_session22_review.md)
- docs/src/twolm/test/test_rlm_config_schemas.md —
  test_rlm_config_schemas.py mirror (NEW doc created at D-106
  step 8b, closing the missing D-007 mirror: the E-group
  coverage map + the goldens — the 0x107 16-hex pair, 'rlmwf_',
  the rejection literals, the c1/c2 boundary pair)
- docs/src/twolm/test/test_lm_worker_positions.md —
  test_lm_worker_positions.py mirror (MIGRATED at D-106 step 9,
  POSITIONS batch: the 2-class coverage map — the 2 DB-gated
  end-to-end tests + the 7 in-memory TestIsCacheConsistent
  conversions — + the goldens: flat file names, the witness log
  lines, the fixture metadata; the verbatim session-22 review in
  notes/analyses/test_lm_worker_positions_session22_review.md)
- docs/src/twolm/lm_worker_features.md — lm_worker_features.py
  mirror (MIGRATED at D-106 step 10, FEATURES batch: the 4th
  level, pure-compute, the 40-check probe + 3-test suite pins,
  the B10 no-cache-file boundary; the verbatim session-22 review
  in notes/analyses/lm_worker_features_session22_review.md)
- docs/src/twolm/test/test_lm_worker_features.md —
  test_lm_worker_features.py mirror (MIGRATED at D-106 step 10,
  FEATURES batch: 2 classes / 3 tests — the 2 DB-gated end-to-end
  + the DB-free zero-feature guard (the step-3 B11 conversion),
  the full FeatureSet content golden; the verbatim session-22
  review in notes/analyses/test_lm_worker_features_session22_review.md)
- docs/src/twolm/rlm_indexes.md — rlm_indexes.py mirror
  (MIGRATED at D-106 step 11, INDEXES batch: the 5th-level data
  object — 3 fields by reference + the 4 public fns + the
  duck-typed data checksum; the 52-call probe + 14-test suite
  pins, M5 as-is by design; the verbatim session-23 review in
  notes/analyses/rlm_indexes_session23_review.md)
- docs/src/twolm/lm_worker_indexes.md — lm_worker_indexes.py
  mirror (MIGRATED at D-106 step 11, INDEXES batch: the 5th
  active level, the uniform 7-kwargs cache wiring, flat
  rlmwf_04_INDEXES.dat + .SHA3-256, the double-clear _down;
  probe D1-D6 + C2-C7 + the 2-test end-to-end suite; the
  verbatim session-23 review in
  notes/analyses/lm_worker_indexes_session23_review.md)
- docs/src/twolm/test/test_rlm_indexes.md — test_rlm_indexes.py
  mirror (MIGRATED at D-106 step 11, INDEXES batch: 5 classes /
  14 tests, all file I/O mocked, no DB; the store/load contract
  + both is_cache_consistent single-field branches; the
  verbatim session-23 review in
  notes/analyses/test_rlm_indexes_session23_review.md)
- docs/src/twolm/test/test_lm_worker_indexes.md —
  test_lm_worker_indexes.py mirror (MIGRATED at D-106 step 11,
  INDEXES batch: 1 class / 2 tests, both DB-gated, the
  end-to-end cache round-trip; the verbatim session-23 review
  in notes/analyses/test_lm_worker_indexes_session23_review.md)
- docs/src/twolm/test/paths.md —
  paths.py mirror (MIGRATED at D-106 step 27, PATHS pair: the
  shared workspace-root-anchored test paths — marker-based
  WORKSPACE_ROOT + CUSTOM_TMP_BASE; invariants pinned to the 3
  named test_paths tests; the verbatim session-23 review in
  notes/analyses/paths_session23_review.md)
- docs/src/twolm/test/test_paths.md —
  test_paths.py mirror (MIGRATED at D-106 step 27, PATHS pair:
  schema §6 — 1 class / 3 tests, the 3 path-identity goldens; the
  verbatim session-23 review in
  notes/analyses/test_paths_session23_review.md)
- docs/src/twolm/rlm_wmaps.md — rlm_wmaps.py mirror
  (MIGRATED at D-106 step 12, WMAPS batch: the 6th-level data
  object — the 8 fields by reference + the 4 public fns + the
  duck-typed data checksum; the compute body, the 3 load error
  messages, the PURE 2-field compare; the 53-call probe + the 2
  suites pins; the verbatim session-23 review in
  notes/analyses/rlm_wmaps_session23_review.md)
- docs/src/twolm/lm_worker_wmaps.md — lm_worker_wmaps.py
  mirror (MIGRATED at D-106 step 12, WMAPS batch: the 6th active
  level, the 3rd cache_manager consumer, the uniform 7-kwargs
  cache wiring, flat rlmwf_05_WMAPS.dat + .SHA3-256, _down clears
  all 7 attrs; probe B1-B9 + C1-C15 + E9 + the 3-test end-to-end
  suite; the verbatim session-23 review in
  notes/analyses/lm_worker_wmaps_session23_review.md)
- docs/src/twolm/test/test_rlm_wmaps.md — test_rlm_wmaps.py
  mirror (MIGRATED at D-106 step 12, WMAPS batch: 4 classes / 13
  tests, no DB — the 2 compute branches, the 3 consistency
  branches, the 6 IO pins incl. the golden hash 12c3344e…, the 2
  init tests; the verbatim session-23 review in
  notes/analyses/test_rlm_wmaps_session23_review.md)
- docs/src/twolm/test/test_lm_worker_wmaps.py —
  test_lm_worker_wmaps.py mirror (MIGRATED at D-106 step 12,
  WMAPS batch: 2 classes / 3 tests, all DB-gated — the
  end-to-end round-trip + the rlm_01 golden content (21 weights)
  as the single source of truth for the step-3 E-tier
  re-derivation; the verbatim session-23 review in
  notes/analyses/test_lm_worker_wmaps_session23_review.md)
- docs/src/twolm/rlm_design_matrix.md — rlm_design_matrix.py
  mirror (MIGRATED at D-106 step 13, DESIGN_MATRIX batch: the
  (N,I) uint32 X data object + 4 public fns + the duck-typed
  hash; the 4th cache_manager consumer; the single guard + the
  explicit-cast note; the 1-field compare; invariants pinned to
  the 53-call probe A1-A15 / B1-B9 / D5-D10 / F1/F4/F5 + the 2
  suites; the verbatim session-23 review in
  notes/analyses/rlm_design_matrix_session23_review.md)
- docs/src/twolm/lm_worker_design_matrix.md —
  lm_worker_design_matrix.py mirror (MIGRATED at D-106 step 13,
  DESIGN_MATRIX batch: the 7th-level worker, the 7-kwargs cache
  wiring, flat rlmwf_06_DESIGN_MTR.dat, the bare-ndarray
  blackboard; probe B1-B9 + C1-C14 + the 3-test end-to-end
  suite; the verbatim session-23 review in
  notes/analyses/lm_worker_design_matrix_session23_review.md)
- docs/src/twolm/test/test_rlm_design_matrix.md —
  test_rlm_design_matrix.py mirror (MIGRATED at D-106 step 13,
  DESIGN_MATRIX batch: 4 classes / 12 tests, no DB — the 2
  compute branches, the 2 consistency branches, the 6 IO pins
  incl. the golden hash da86a916…, the 2 init tests; the verbatim
  session-23 review in
  notes/analyses/test_rlm_design_matrix_session23_review.md)
- docs/src/twolm/test/test_lm_worker_design_matrix.md —
  test_lm_worker_design_matrix.py mirror (MIGRATED at D-106 step
  13, DESIGN_MATRIX batch: 2 classes / 3 tests, all DB-gated —
  the end-to-end round-trip + the rlm_01 golden (10,7) X as the
  single source of truth for the step-3 D-tier re-derivation; the
  verbatim session-23 review in
  notes/analyses/test_lm_worker_design_matrix_session23_review.md)
- docs/src/twolm/rlm_zed.md — rlm_zed.py mirror (MIGRATED at
  D-106 step 14, ZED batch: the z (N,) float32 data object + the
  2 affine closures, zed_fun_factory + rlm_zed_compute; the
  FIRST non-cache level; the hash covers z only; invariants
  pinned to the 51-call probe A1-A12 / B1-B8 / D1/D5-D11 /
  F1/F4/F5 + the 2 suites; the verbatim session-24 review in
  notes/analyses/rlm_zed_session24_review.md)
- docs/src/twolm/lm_worker_zed.md — lm_worker_zed.py mirror
  (MIGRATED at D-106 step 14, ZED batch: the first non-cache
  worker — no cache_manager wiring by design, the L49 comment;
  the 4 ctx attributes published/cleared; probe B1-B8 + C1-C10 +
  the 3-test end-to-end suite; the verbatim session-24 review in
  notes/analyses/lm_worker_zed_session24_review.md)
- docs/src/twolm/test/test_lm_worker_zed.md —
  test_lm_worker_zed.py mirror (MIGRATED at D-106 step 14, ZED
  batch: 2 classes / 3 tests — the factory math + the rlm_01
  y/z golden as the single source of truth for the step-3 D-tier
  re-derivation + the _down pin; the verbatim session-24 review
  in notes/analyses/test_lm_worker_zed_session24_review.md)
- docs/src/twolm/test/test_rlm_zed.md — test_rlm_zed.py mirror
  (MIGRATED at D-106 step 14, ZED batch: 3 classes / 10 tests,
  no DB — the 4 factory math tests, the 2 mock-compute pins, the
  4 init/hash tests incl. the (10,) hash golden 3d49fd5d…; the
  verbatim session-24 review in
  notes/analyses/test_rlm_zed_session24_review.md)
- docs/src/twolm/rlm_gradient.md — rlm_gradient.py mirror
  (MIGRATED at D-106 step 15, GRADIENT batch: the function-only
  module — sigmoid + rlm_gradient_compute, the fg closure math,
  the R1 float32 cast, invariants pinned to the 54-call probe
  A1-A13 / B1-B9 / D0+D5-D10+D12 / E1+E4-E8 + the 2 suites; the
  verbatim session-25 review in
  notes/analyses/rlm_gradient_session25_review.md)
- docs/src/twolm/lm_worker_gradient.md — lm_worker_gradient.py
  mirror (MIGRATED at D-106 step 15, GRADIENT batch: the second
  non-cache worker — the L48 by-design comment, _up sets ctx.fg,
  _down clears it; probe B1-B9 + C1-C10 + the 2-test end-to-end
  suite; the verbatim session-25 review in
  notes/analyses/lm_worker_gradient_session25_review.md)
- docs/src/twolm/test/test_lm_worker_gradient.md —
  test_lm_worker_gradient.py mirror (MIGRATED at D-106 step 15,
  GRADIENT batch: 1 class / 2 DB-gated tests — the rlm_02
  4-value golden at w=0 + the _down pin; the verbatim session-25
  review in notes/analyses/test_lm_worker_gradient_session25_
  review.md)
- docs/src/twolm/test/test_rlm_gradient.md — test_rlm_gradient.
  py mirror (MIGRATED at D-106 step 15, GRADIENT batch: 2
  classes / 8 tests, no DB — the sigmoid goldens, the zero-
  weights exact goldens 4/75 + [1/30, 0, −1/30], the R1 dtype
  pins; the verbatim session-25 review in
  notes/analyses/test_rlm_gradient_session25_review.md)
- docs/src/twolm/rlm_optimize.md — rlm_optimize.py mirror
  (MIGRATED at D-106 step 16, OPTIMIZE batch: the checkpoint-
  dict level — the 6 names, the R1 ridge gate in the
  consistency function, the R3 sidecar verify, invariants
  pinned to the 76-check probe A1-A20 / B1-B17 / H4-H8+H6b +
  the 2 suites; the verbatim session-26 review in
  notes/analyses/rlm_optimize_session26_review.md)
- docs/src/twolm/lm_worker_optimize.md — lm_worker_optimize.py
  mirror (MIGRATED at D-106 step 16, OPTIMIZE batch: the
  4-step _up, the R2 try/except, the R4 _down scope, the T10
  factory @validate_call; probe B1-B17 + D1-D11 + the 3-test
  end-to-end suite; the verbatim session-26 review in
  notes/analyses/lm_worker_optimize_session26_review.md)
- docs/src/twolm/test/test_lm_worker_optimize.md —
  test_lm_worker_optimize.py mirror (MIGRATED at D-106 step 16,
  OPTIMIZE batch: 1 class / 3 DB-gated tests — the loss-decrease
  run, the max-iters → completed → reload run with the T6 real
  lbfgs marker, the R4 _down pin; the verbatim session-26
  review in notes/analyses/test_lm_worker_optimize_session26_
  review.md)
- docs/src/twolm/test/test_rlm_optimize.md — test_rlm_optimize.
  py mirror (MIGRATED at D-106 step 16, OPTIMIZE batch: 4
  classes / 19 tests, no DB — the round-trip + dtype pins, the
  M6/R3/header gates, the 2 golden hashes, the 4 consistency +
  4 status branches — after step 3 it also owns the probe's
  former F1-F10 + G1/G2 + G4 + G5; the verbatim session-26
  review in notes/analyses/test_rlm_optimize_session26_review.
  md)
- docs/src/twolm/rlm_generate.md — rlm_generate.py mirror
  (MIGRATED at D-106 step 17, GENERATE batch: the 11th level
  data object — the 3 category branches with the D-098 R2
  weighted-mean ruling, the 3 header gates, the single-field
  consistency gate; invariants pinned to the 15-check probe
  A1-A5 / D3+D11 / E2+E4+E5+E7 / F1 + the 17-test pair; the
  verbatim session-27 review in
  notes/analyses/rlm_generate_session27_review.md)
- docs/src/twolm/lm_worker_generate.md — lm_worker_generate.py
  mirror (MIGRATED at D-106 step 17, GENERATE batch: the
  uniform 7-kwargs cache_manager flow, the D-074
  _for_current_level name, the _down scope, the rlmwf_10 flat
  file; probe B1-B3 + E tier + the 3-test suite; the verbatim
  session-27 review in
  notes/analyses/lm_worker_generate_session27_review.md)
- docs/src/twolm/test/test_rlm_generate.md — test_rlm_generate.
  py mirror (MIGRATED at D-106 step 17, GENERATE batch: 4
  classes / 14 tests, no DB — the mock compute golden, the 2
  error branches, the 6 IO tests incl. the T1 version gate, the
  3 init validations, the hash golden 460c993d…07a — after
  step 3 it also owns the probe's former D1/D2 + D4-D10 + D12/
  D13; the verbatim session-27 review in
  notes/analyses/test_rlm_generate_session27_review.md)
- docs/src/twolm/test/test_lm_worker_generate.md —
  test_lm_worker_generate.py mirror (MIGRATED at D-106 step 17,
  GENERATE batch: 1 class / 3 DB-gated tests — the first-run
  (6588,) float32 + hash-golden + sidecar, the 2nd-instance
  cache hit, the _down pin — after step 3 it also owns the
  probe's former E1/E3/E8/E9/E10/E11; the verbatim session-27
  review in
  notes/analyses/test_lm_worker_generate_session27_review.md)
- docs/src/twolm/lm_worker_vld_positions.md — lm_worker_vld_
  positions.py mirror (MIGRATED at D-106 step 19, VLD_POSITIONS
  batch: the POSITIONS TWIN over the validation data set — the
  reused load_from_db / is_cache_consistent pair, the keyword
  bid/status overrides, the inherited-ec fact, the 7-kwargs
  wiring, the rlmwf_11 flat slot, the rlm_02 golden 200
  positions / e8087903…f4c48 / mean 3.64; probe A1-A8 + B4/B5 +
  C3a-C3d + C4 + D1/D8 + the 9-test suite; the verbatim
  session-28 review in notes/analyses/lm_worker_vld_positions_
  session28_review.md)
- docs/src/twolm/test/test_lm_worker_vld_positions.md —
  test_lm_worker_vld_positions.py mirror (MIGRATED at D-106
  step 19, VLD_POSITIONS batch: 2 classes / 9 tests — the first-
  run 200-position + hash-golden + sidecar, the 2nd-instance
  cache hit with no re-extraction, the _down pin (3 DB-gated) +
  the 6 DB-free TestIsCacheConsistentOverride tests (the D-106
  step-3 conversion of probe D2-D7); the verbatim session-28
  review in notes/analyses/test_lm_worker_vld_positions_
  session28_review.md)
- docs/src/twolm/lm_worker_validate.md — lm_worker_validate.py
  mirror (MIGRATED at D-106 step 18, VALIDATE batch: the THIRD
  non-cache worker — the 7-key vld_metrics dict, the M1
  zero-guarded RMSE/MAE line, the ONE ctx.vld_metrics attribute,
  the rlmwf_12 slot unused; probe A + C tiers + the 3-test
  worker suite; the verbatim session-28 review in
  notes/analyses/lm_worker_validate_session28_review.md)
- docs/src/twolm/rlm_validate.md — rlm_validate.py mirror
  (MIGRATED at D-106 step 18, VALIDATE batch: the FIRST
  dedicated data module of a non-cache level — validate_model's
  forward pass + the 7-metric dict (incl. vld_mse_y post M3),
  the dense-mapping idiom, the y2z float32 cast; probe A1-A13 +
  C4/C5 + D2 + the 5-test suite; the verbatim session-28 review
  in notes/analyses/rlm_validate_session28_review.md)
- docs/src/twolm/test/test_lm_worker_validate.md —
  test_lm_worker_validate.py mirror (MIGRATED at D-106 step 18,
  VALIDATE batch: 2 classes / 5 tests — the first-run 7-metric
  goldens + log lines, the 2nd-instance deterministic recompute
  with 6 cache hits, the _down pin (3 DB-gated) + the 2 DB-free
  TestValidateModelUnit tests (the D-106 step-3 conversion of
  probe D1/D3 — the hand-computed 2-position metric math + the
  M1 zero-guard branch); the verbatim session-28 review in
  notes/analyses/test_lm_worker_validate_session28_review.md)
- docs/src/twolm/lm_worker_analytics.md — lm_worker_analytics.py
  mirror (MIGRATED at D-106 step 20, ANALYTICS batch: the 5th
  non-cache worker — the 3-attribute machine contract
  (train_metrics + train_dense_metrics + analytics_report), the
  21-line log span, the 6 cache hits on the 2nd instance, the
  file-report artifact semantics; the 36-check probe + the 4-test
  worker suite; the verbatim session-28 review in
  notes/analyses/lm_worker_analytics_session28_review.md)
- docs/src/twolm/rlm_analytics.md — rlm_analytics.py mirror
  (MIGRATED at D-106 step 20, ANALYTICS batch: the 2nd function-
  only data module — 4 public fns + 3 table helpers, the 3-metric
  header table (D-105/M2), the rlm_02 7-metric + file-hash
  goldens, the rlm_01 goldens (values in the test doc), D1-D4
  unit math; the verbatim session-28 review in
  notes/analyses/rlm_analytics_session28_review.md)
- docs/src/twolm/test/test_lm_worker_analytics.md —
  test_lm_worker_analytics.py mirror (MIGRATED at D-106 step 20,
  ANALYTICS batch: 2 classes / 4 tests, all DB-gated — the rlm_02
  7+4 goldens + the date-masked file-report hashes + 2nd-
  instance determinism + _down pin, the rlm_01 65-row LMC table
  pin; the verbatim session-28 review in
  notes/analyses/test_lm_worker_analytics_session28_review.md)
- docs/src/twolm/lm_worker_save.md — lm_worker_save.py mirror
  (MIGRATED at D-106 step 21, SAVE batch: the 15th and LAST
  active level — the 6th non-cache worker, the pure SINK: the 2
  INFO logs + the model-weight write, _down no-op, the artifact
  never unlinked, the rlmwf_15 slot unused; the 17-check probe +
  the 5-test suite; the verbatim session-29 review in
  notes/analyses/lm_worker_save_session29_review.md)
- docs/src/twolm/model_weights.md — model_weights.py mirror
  (MIGRATED at D-106 step 25, the MODEL_WEIGHTS + RLM_CLIENT pair:
  the 8 write sections with the f32 truncation + the 4/5 opt + 4/7
  vld subsets, the 2 ValueError guards with the exact strings; the
  statics A4-A6 of verify_save.py + the full-chain read-back
  goldens; the verbatim session-29 review in
  notes/analyses/model_weights_session29_review.md)
- docs/src/twolm/rlm_client.md — rlm_client.py mirror (MIGRATED at
  D-106 step 25, the MODEL_WEIGHTS + RLM_CLIENT pair: the 4-step
  ef, the dense-path / substitution-rule section with the measured
  rlm_04 1923/199932 + rlm_01 5/10 deltas, the 12 bit-exact EF
  goldens; the verbatim session-29 review in
  notes/analyses/rlm_client_session29_review.md)
- docs/src/twolm/test/test_lm_worker_full_chain.md —
  test_lm_worker_full_chain.py mirror (MIGRATED at D-106 step 21,
  SAVE batch: schema §6 — the Coverage table for the 3 classes /
  5 tests, the rlm_04 + rlm_03 EXACT goldens (file hashes,
  read-back, the D-105 dense 4-key dicts, the 2 file-report
  masks, the EF O4 vld[42] pin, the 2nd-instance determinism, the
  ungated read-guard class — the D-106 step-3 class-c home of
  probe B1-B2 + C1-C14 + D1-D10); the verbatim session-29 review
  in notes/analyses/test_lm_worker_full_chain_session29_review.md)
- notes/naming.md — canonical board naming convention (row/column,
  D-013; D8 symmetries, D-014)
- notes/rules.md — active legislation: the register of the rules in force (one line per rule, origin D-number; lifecycle RECORD/PROMOTE/RETIRE)
- notes/decisions.md — historical decision log, append-only (D-NNN; D-001…D-115; the rules in force live in notes/rules.md)
- notes/analyses/ — archived one-off investigations + the D-106
  classification (verify_t2, verify_burnside, the 6 o1* one-offs,
  classification.md) + the extracted verbatim reviews
  (board_session1_review.md at step 4, pattern_session4_review.md
  at step 5, logistic_model_session21_review.md +
  state_machine_session19_review.md at steps 6-7, the CONFIG
  batch #1 trio at step 8: lm_worker_config_session21_review.md,
  rlm_config_schemas_session22_review.md,
  test_lm_worker_config_session21_review.md, the POSITIONS pair
  at step 9: lm_worker_positions_session22_review.md +
  test_lm_worker_positions_session22_review.md, the FEATURES
  quartet at step 10: feature_session11_review.md +
  test_feature_session11_review.md (session 11) +
  lm_worker_features_session22_review.md +
  test_lm_worker_features_session22_review.md (session 22))
- notes/ideas.md — future backlog (I-NNN)
- notes/log_rules.md — session-journal format rules (rigid; global session numbering; volume rotation: 25 sessions / 2000 lines per volume, only at session boundaries)
- notes/docs_rules.md — mirror-doc format rules (rigid; the
  current-state contract: the 4-line header with the `> State:` line
  as the only permitted time, 7 sections, the forbidden-history
  list, the same-commit lifecycle, the test-doc variant, the
  migration state)
- notes/probe_rules.md — verification-apparatus rules (rigid; the
  a/b/c classification + the independent-derivation criterion, the
  test/probe line, the pipeline-state centralization in the hub,
  the campaign sweep rule, the archive to notes/analyses/, the
  baseline)
- notes/log_000.md — session journal, volume 000 (sessions 1–24, closed 2026-09-01)
- notes/log_001.md — session journal, volume 001 (sessions 25–..., open)
