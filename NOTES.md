# NOTES.md — entry point

## Format rules (rigid — follow when editing this file)

This file is the entry point: current state, next steps, index.
AGENTS.md standing rule 2: keep it updated after each milestone / end
of work session. Rules:

1. Sections — exactly these seven, in this order, no others: Project · Inventory · Conventions in the code · Environment · Where we are · Next steps · Index.
2. Language: English. Dates: YYYY-MM-DD. Suite numbers: `<total>/<failures>/<skipped>`, where total = unittest's "Ran N" (e.g. 193/0/12). Arrows: →. Ellipsis: ... (three dots). References: D-NNN (notes/decisions.md), I-NNN (notes/ideas.md), session N (notes/log_NNN.md volumes, global numbering), T-NN (test defect), R# (code issue), M# (minor note). Placeholder tokens are always inline code (backticks): bare `<word>` looks like an HTML tag to Markdown renderers and corrupts the rest of the rendering.
3. Project — plain text, at most 4 sentences.
4. Inventory — table "| Item | Status | Note |", one row per tracked source file and test file (separate rows), plus the logistello-papers row. Status grammar: `analyzed <date>[ (session N)]; <terse history, semicolon-separated>; suite <total>/<f>/<s> GREEN` — it always ENDS with the CURRENT suite state of that file. Note column = the doc path (D-007 mirror).
5. Conventions in the code — "- " bullets, one convention per bullet.
6. Environment — "- " bullets, one fact per bullet, in this order: venv, packaging, dependencies, test command, suite status. Suite status grammar: `Suite status (<date>): <module> <total>/<f>/<s>, ... — all GREEN. <skip explanation>. Warm run ≈ <t> s.`
7. Where we are — "- " bullets, one per file (source and tests separately) in the order the modules were brought in; then the re-verification bullet (if any); then the plan bullet; then one context bullet. Each bullet starts with the file name. Current state only — the session-by-session detail lives in the journal volumes notes/log_NNN.md (rules: notes/log_rules.md).
8. Next steps — "- " bullets, OPEN items only (closed work belongs in Where we are); the LAST bullet is the next concrete action.
9. Index — "- " bullets, one per doc/notes file: `<path> — <one-line description>`.

## Project

File-by-file modernization of Roberto Corradini's Reversi engine
(18-year-old repo). This workspace is a staging area: only files
under active work live here. Full-repo restructure: planned, not
now (I-001; see notes/decisions.md).

## Inventory

| Item | Status | Note |
|---|---|---|
| src/twolm/board.py | analyzed 2026-08-25 (session 1); modified by the fix campaign (T20, T22, T25, T36, T37, T38); all 5 real issues resolved: R1 (D-017), R2 (T20 annotation), R3 (D-018), R4 (T24 test pin + TestPydanticVersion), R5 (NumPy ≥ 2.0 declared in pyproject.toml, D-011); suite 193/0/12 GREEN (test_board.py) | docs/src/twolm/board.md |
| src/twolm/test/test_board.py | analyzed 2026-08-25 (session 2); 11 defects + 8 docstring/behaviour mismatches documented; fix campaign COMPLETE 2026-08-26 (session 3): P0 + P1 + full P2 batch (T26–T35, one commit per Roberto's "Facciamoli tutti, un solo commit"), suite 157 → 193 GREEN throughout; header 'environmeant' typo fixed 2026-08-29 (D-050, with test_feature T4), remaining grammar nit reported-only; suite 193/0/12 GREEN | docs/src/twolm/test/test_board.md |
| src/twolm/pattern.py | analyzed 2026-08-27 (session 4, D-019 review-only); all real issues resolved: R1 (D-020) principal = numerically lowest orbit mask (unique representative) + regression test; R2-R7 doc/hygiene fixes (D-021); R8 closed as little-endian-only platform note (D-022); minor sweep complete 2026-08-27 (session 7): 19/19 items (D-023, D-024, D-025 + fail-fast checks, constant rename, doc/hygiene/API fixes); D-032 (2026-08-28, session 10): Burnside attributes n_invariant_configs / n_unique_configs; suite 64/0/3 GREEN (test_pattern.py) | docs/src/twolm/pattern.md |
| src/twolm/test/test_pattern.py | analyzed 2026-08-27 (session 8): 12 classes / 50 tests / 3 PERF; 21/21 goldens independently re-derived (0 mismatches); 16 defects T1-T16 + T17 (sqa8/sqh1 fixtures swapped names/values) documented; fix campaign CLOSED: P0 (D-026-028, 6da0803) + P1 (D-029/030/031: row independence both public indexing APIs + EDGE 6561-entry dict pin) + P2 hygiene (D-033: T1-T7, T15-T16; T19 found + fixed in T2) + P2 breadth (D-034: T11-T14 + T17); T18 noted-only, M1 deferred; suite 64/0/3 GREEN | docs/src/twolm/test/test_pattern.md |
| src/twolm/mobility.py | analyzed 2026-08-28 (session 10): Mobility/MobilitySet + popcount64 SWAR + Numba kernel; index formula + n_configurations (distinct index values) + sorted-order columns + hash verified vs independent ground truth (V1-V8, 200-position differential, popcount on 200,010 values); R1-R6 fix batch applied (D-035: docstrings + column-order contract + popcount64 test-helper + dead imports + property/repr alignment + n_instances as-is), no behavior change; M1-M5 disposed (D-036: M1 glossary shipped, M2/M3/M5 left as-is, M4 corrected — no PERF gates in any suite); suite 26/0/1 GREEN (test_mobility.py) | docs/src/twolm/mobility.md |
| src/twolm/test/test_mobility.py | analyzed 2026-08-28 (session 10): 2 classes / 23 tests / 1 PERF; 13 verified facts V1-V13 (0 mismatches, incl. 31-line popcount table and [53,13,66] golden); 9 defects T1-T9 documented; fix campaign CLOSED the same day (D-037: T1-T9, per-item approvals, single batch commit — P0 __repr__ goldens, P1 multi-position row independence, P2 hygiene/breadth incl. pinned hash literal 2e553593...208a94); suite 23 → 26, GREEN 26/0/1 | docs/src/twolm/test/test_mobility.md |
| src/twolm/feature.py | analyzed 2026-08-28 (session 11): Feature (blocked __new__ + 3 factories) + FeatureSet (intercept/mset/pset composition, sorted-order features, hash over child hash hex strings); all goldens re-derived independently (V1-V8, zero mismatches: 3x10 index matrix, 13 orbit sizes, 3 pinned hashes); R1-R4 fix batch applied (D-038: sha3_256 doc fix + column-layout contract + __init__ docstring + dead imports); M1 applied (D-039), M2 applied (D-040), M3 left as-is (D-041, follow-up I-007), M4 applied (D-042) — all disposed; suite 20/0/1 GREEN (test_feature.py, 19 run + 1 PERF) | docs/src/twolm/feature.md |
| src/twolm/test/test_feature.py | analyzed 2026-08-28 (session 11): 4 classes / 14 tests / 1 PERF; 9 verified facts W1-W9 (0 mismatches, incl. 3x10 matrix and f5663932 hash literal); 9 defects T1-T9 documented (dead if-False block w/ never-imported position_print, 6 dead imports, header grammar + "environmeant" typo, no names-order assert, partial-None FeatureSet untested, Feature repr/eq untested, cosmetic import-time spaces, no full print_summary golden); T campaign CLOSED 2026-08-29 (D-043..D-050: T6, T1, T2, T3, T5, T7, T9, T4 — both files; T8 left as-is); suite 20 tests (19 run + 1 PERF), GREEN 20/0/1 | docs/src/twolm/test/test_feature.md |
| src/twolm/binio.py | analyzed 2026-08-29 (session 14); T1-T4 fix batch applied (D-051: lz4 in pyproject.toml, dead Path import removed, "Aauthor" → "Author", test_unknown_type_code_raises added); 15 verified facts V1-V15 (0 mismatches); suite 45/0/0 GREEN (test_binio 42 + test_usage_binio 3) | docs/src/twolm/binio.md |
| src/twolm/test/test_binio.py | analyzed 2026-08-29 (session 14, with test_usage_binio.py); T4 applied (D-051): ArrayTest now 8 tests (42 total in test_binio); suite 44 → 45, GREEN 45/0/0, no PERF | docs/src/twolm/test/test_binio.md |
| src/twolm/regab.py | analyzed 2026-08-29 (session 15); T1-T7 fix batch applied (D-052: "Aauthor" → "Author", dead typing imports, psycopg2/pandas/python-dotenv in pyproject.toml, _validate_db_fields DB query deferred, SKIP_REGAB_DB=1 gate, _validate_where_clause SQL-injection guard); 5 verified facts V1-V5 (0 mismatches, sha3_256 golden); suite 37/0/0 GREEN (35 DB + 2 mocked; SKIP_REGAB_DB=1 → 35 skip) | docs/src/twolm/regab.md |
| src/twolm/test/test_regab.py | analyzed 2026-08-29 (session 15); T5+T6+T7 applied (D-052): dead imports removed, SKIP_REGAB_DB gate, 4 SQL-injection tests added (TestRegabGPAsDF 12 → 16); suite 33 → 37/0/0 GREEN; D-085: the .env load + the checksum-test mkdtemp re-anchored to the shared twolm.test.paths module | docs/src/twolm/test/test_regab.md |
| src/twolm/opt_lbfgs.py | analyzed 2026-08-29 (session 16); T1-T7 fix batch applied (D-053: RuntimeException → RuntimeError hard bug, CURVATURE_THRESHOLD used, low_progress_count spelling, hermite None fallthrough, save_fn 7-param hint+docstring, fractional docstring); 5 verified facts V1-V5 (0 mismatches); suite 13/0/0 GREEN | docs/src/twolm/opt_lbfgs.md |
| src/twolm/test/test_opt_lbfgs.py | analyzed 2026-08-29 (session 16); T7 applied + 9 new tests (D-053): TestLBFGSInputValidation (3), TestFixedSizeMaxList (4, incl. T1 regression), TestTwoLoopRecursion (2); suite 4 → 13/0/0 GREEN | docs/src/twolm/test/test_opt_lbfgs.md |
| src/twolm/state_machine.py | analyzed 2026-08-29 (session 19): generic pipeline orchestrator (Workers up/down + Context + logging/history/CSV), pure stdlib, no new deps; 17 verified facts V1-V17 (0 mismatches, 54-check probe); R1 FIXED (D-057: Verbosity.VERY_LOW=4 added, NONE=5, `>=` gate unchanged — HIGH..LOW byte-identical, NONE truly silent, old ERROR-only behaviour kept as VERY_LOW); R2 FIXED (D-058: LogEntry now a frozen dataclass — attribute access, asdict() for file/DB dumps, show_event_log migrated, observable behaviour unchanged; test-file datetime import now used → M2/T11 resolved); R3 RESOLVED as intentional sentinel (D-059: documented in class + move_to_step docstrings, pinned by test_worker_zero_is_sentinel_never_executed, no behaviour change — the RLM 'CREATED' worker runs outside the machine, logistic_model will make it explicit); R4 RESOLVED (D-060: keep + document + pin — failure semantics in move_to_step docstring, recovery = move to k-1 (k's down) then up; machine domain-agnostic, exception re-raised for the domain worker; pinned by test_retry_after_failure_skips_failed_step, closes T6); R5 RESOLVED (D-061: __init__ rejects duplicate worker names, case-insensitive ValueError fail-fast — the real ambiguity was name resolution in move_to_step itself, so uniqueness enforced instead of an index fix; move_to_last unchanged, name dispatch now unambiguous; closes M12); T2 coverage added (D-062: TestContextInjection 7 tests; M8 extended with the implicit separator contract); T3 coverage added (D-063: TestDisplayGoldens 3 end-to-end display goldens, frozen clock); T4 coverage added (D-064: 3 move_to_last tests — happy path, intermediate position, single-worker sentinel no-op); T5 fixed (D-065: CSV test rewritten — exact header names, ISO-8601 +00:00, duration identity, artifact under build/tmp; new house rule: test files only in workspace_root/build/tmp, removed afterwards); T7 pinned (D-066: 2 tests — bool accepted as int step, np.int64 TypeError); T8 + T9 pinned (D-067: 5 tests — current_worker_name live view + UNDEFINED, StepMove field content incl. aware-UTC timestamps, duration identity, finally-append on failure); M-sweep batch 1 applied (D-068: M1 dead Any import removed, M4 _run_step direction dispatch explicit (elif 'down' + ValueError), M7 __repr__ on Worker + StateMachine (lightweight), M10 CSV export creates missing parent dirs); M-sweep batch 2 applied (D-069: M3 bool rejected — strict gate, TypeError same message, test rewritten to rejection; M5 cache helpers renamed *_for_current_level (the 2 ported domain call sites + RLMContext's 2 field names renamed D-074 — follow-up closed); M8 cache prefix pathlib join — no more silent gluing; M11 @validate_call on Worker init/up/down + SM init/log_event/export + move_to_step via strict private impl re-raising the pinned TypeError; pydantic now a module dep, already in pyproject); ALL T ITEMS CLOSED; M-sweep COMPLETE (D-068: M1, M4, M7, M10; D-069: M3, M5, M8, M11; D-070: M6 print cleanup — enum names + UTC marker on the live line, UTC header / 2-digit step / RELEVANCE name column / 66-underscore rule, right-aligned Dur (s), 3 display goldens rewritten in place; M9 left as-is — injection load-bearing, redesign parked at I-010); D-078 (the lm_worker_config R2 fix, at machine level): the injected cache-path closure now concatenates the prefix verbatim onto the level name (filename-prefix semantics per the domain schema — one shared fix for all cache-consuming workers) instead of the D-069 M8 pathlib join; suite 49/0/0 GREEN (test_state_machine.py) | docs/src/twolm/state_machine.md |
| src/twolm/test/test_state_machine.py | analyzed 2026-08-29 (session 19): 5 classes / 49 tests / no PERF; all 13 original expectations independently re-derived (0 mismatches); T1 FIXED (D-057: TestVerbosityGating — 6x5 gating matrix + enum values); R2 tests added (D-058: TestLogEntry 3 tests — typed record, immutability, asdict 5-key form); T6 FIXED (D-060: test_retry_after_failure_skips_failed_step — retry-skip + down-then-up recovery); R5 tests added (D-061: 2 duplicate-name tests — reject + case-insensitive, closes T10); T2 FIXED (D-062: TestContextInjection 7 tests — log_event live binding, {level:02} format, base_dir join, absolute-prefix drops base_dir, cfg-missing AttributeError, empty-workers degenerate, V17 shared-context re-bind); T3 FIXED (D-063: TestDisplayGoldens 3 end-to-end goldens — live line, show_event_log table, show_history_of_moves table, frozen clock); T4 FIXED (D-064: 3 move_to_last tests — happy path, intermediate position, single-worker sentinel no-op); T5 FIXED (D-065: test_history_export_csv rewritten — exact header names, ISO-8601 +00:00, duration identity, artifact under build/tmp + finally cleanup; house rule: test files only in workspace_root/build/tmp); T7 pinned (D-066: 2 tests — bool as int step, np.int64 TypeError); T8 + T9 pinned (D-067: 5 tests — current_worker_name live view + UNDEFINED, StepMove field content incl. aware-UTC timestamps, duration identity, finally-append on failure); M-sweep batch 1 pinned (D-068: 4 tests — _run_step unknown direction ValueError, Worker __repr__, StateMachine __repr__ tracks state, CSV export creates missing parent dirs); M-sweep batch 2 pinned (D-069: bool test rewritten to rejection + 2 constructor ValidationError tests + Path prefix join test); M6 display goldens rewritten in place to the cleaned format (D-070 — enum names + UTC marker, TIMESTAMP (UTC) / 2-digit step / RELEVANCE name / 66-underscore table, right-aligned Dur (s) header; suite count unchanged); T11 resolved as D-058 side effect; ALL T ITEMS CLOSED (T1-T11); M-sweep COMPLETE; suite count unchanged for T5 (a rewrite): 13 → 15 → 18 → 20 → 22 → 29 → 32 → 35 → 37 → 42 → 46 → 49; D-078: test_path_cache_prefix_joins_without_gluing renamed test_cache_prefix_is_concatenated_verbatim + re-pinned to verbatim concatenation (cache01_CONFIG.dat), count unchanged; GREEN 49/0/0 | docs/src/twolm/test/test_state_machine.md |
| src/twolm/cache_manager.py | analyzed 2026-08-30 (session 20, added by Roberto in commit a0cd31f) + fix campaign batches 1+2 (D-071/D-072): generic load-or-compute cache pipeline (4-step validation: allowed → present → checksum → business validity) + duck-typed data checksum + injected callbacks; first domain module importing state_machine (Relevance) + binio (sidecar API, D-072); 17 verified facts V1-V17 (0 mismatches, 33-check probe + 2 boundary probes); D-071: R1 RESOLVED as intentional (step-0 cache-disabled run still warms the cache file — documented + pinned), R2 FIXED (validate_fn in the step-3 try — raising validator deletes + recomputes), R4 FIXED (@validate_call, str→Path coercion, approved behaviour change), M1-M3 fixed (dead Any import, docstring typos, step-2 msg accurate); D-072: R3 RESOLVED — binio sidecar API adopted (hashlib + the 2 re-implemented helpers deleted, _verify_checksum thin wrapper over verify_sha3_256_sidecar, sidecar now binio sha3_256sum format, legacy bare-hex sidecars still verify); CLOSED: R1-R4 + M1-M3 + T1-T7 resolved (T8 report-only); suite 21/0/0 GREEN (test_cache_manager.py) | docs/src/twolm/cache_manager.md |
| src/twolm/test/test_cache_manager.py | analyzed 2026-08-30 (session 20) + fix campaign batches 1+2 (D-071/D-072): 2 classes / 21 tests / no PERF (13 → 21 batch 1: T2 5 duck-typed-hash tests + R2 raising-validator pin + T5 missing-sidecar pipeline test + T3 sidecar-format test; 21 → 21 batch 2); D-071: T1 (assertIsNone on all 6 pipeline tests), T2 (P0 — the duck-typed compute_sha3_256_hash path: with-method both paths, missing → None, non-callable → None, raising on load → recompute), T3 (sidecar format pin), T4 (step-0 on-disk warm-cache effect, per R1 ruling), T5, T7 (on-disk replacement + valid sidecar after every recompute) FIXED; D-072: T6 FIXED (CUSTOM_TMP_BASE anchored to the workspace root via __file__), T3 pin restated to the binio sha3_256sum format, helper suite rebuilt around the binio API (R3 + legacy-compat + malformed/undecodable wrapper pins added, 2 direct-compute tests dropped), pipeline set-ups on write_sha3_256_sidecar; T8 report-only (header grammar); suite 21/0/0 GREEN; D-085: CUSTOM_TMP_BASE now imported from the shared twolm.test.paths module | docs/src/twolm/test/test_cache_manager.md |
| src/twolm/base_model.py | analyzed 2026-08-30 (session 21): thin facade base over StateMachine — pure delegation (current_step / current_worker_name / verbosity get+set, move_to_step / move_to_last, 2 display methods, CSV export); context identity with sm.context + delegation verified (30-check probe, 0 mismatches); D-074 (batch 1): R1 RESOLVED — @validate_call on __init__ (the one decision with logistic_model R3, applied to both facades; approved behaviour change: wrong-typed constructor args now raise a pydantic ValidationError at the facade boundary); D-075 (batch 2): M1 FIXED — __all__ = ['BaseModel'] added (L39, D-068 M1 pattern; 89 lines); M2 docstring forward-references not-yet-ported DeepNetworkModel (informational, kept by design); ALL R/M CLOSED; no dedicated suite (covered via test_logistic_model) | docs/src/twolm/base_model.md |
| src/twolm/logistic_model.py | analyzed 2026-08-30 (session 21): first concrete domain facade — RLMContext (@dataclass over plain Context; 38 fields, 8 *_checksum, artifact blackboard) + LogisticModel 4-step construction (plain path validation → context → 15-level worker list, deliberately partial per Roberto: CREATED sentinel + CONFIG + POSITIONS active (D-076, 601de87), 11 factory imports commented) + level-0 CREATED sentinel (D-059 made explicit); 10 verified facts V1-V10 (30-check probe, 0 mismatches); OPEN: R1 D-069 name divergence (RLMContext + both ported workers on the pre-D-069 _for_next_level names; SM injects _for_current_level — silently-None trap once enabled), R2 Union used (8 annotations) but not imported (latent NameError, PEP 563 mask), R3 no @validate_call on __init__ (one call with base_model R1), M1-M4 (weigth typo, vld__pop_stats double underscore, dir-as-config exception type, __init__ docstring); D-074 (batch 1): R1-R3 RESOLVED (D-069 rename — 2 RLMContext fields + 2 ported worker call sites; 8 annotations → str | None; @validate_call with base_model R1), M1-M4 fixed (weight, vld_pop_stats, IsADirectoryError, docstring); D-075 (batch 2): M5 FIXED (dead `field` import removed); ALL R/M CLOSED; D-076 (Roberto): `lm_worker_config()` uncommented; 601de87: POSITIONS; f051dd3 (D-081): `lm_worker_features()` uncommented — 4 active levels (CREATED sentinel → CONFIG → POSITIONS → FEATURES); a323e0f (D-083): `lm_worker_indexes()` uncommented — 5 active levels (CREATED sentinel → CONFIG → POSITIONS → FEATURES → INDEXES; the rlm_indexes / rlm_indexes_checksum blackboard fields pre-existed at first import); probe re-pinned to the post-a323e0f state (35 checks, 0 mismatches — V3c the 5-worker list, V10 unchanged); suite 14/0/0 GREEN (test_logistic_model.py) | docs/src/twolm/logistic_model.md |
| src/twolm/test/test_logistic_model.py | analyzed 2026-08-30 (session 21): 1 class / 15 methods post D-076 (14 active + 1 muted per Roberto — restored line-by-line with the pipeline; D-076: Roberto restored test_move_to_step_delegates_to_state_machine, the CONFIG level now exists; `_test_move_to_step_by_string` still muted — comes back with POSITIONS); D-075 test campaign: T1 FIXED (smoke test replaced by per-method delegation pins + views/verbosity round-trip), T2 FIXED (build/tmp artifact base, D-065 idiom, defensive tearDown), T3 intentional (muted tests), T4 FIXED (7 corner tests — injected-closure names/fallback/path computation, sentinel RuntimeErrors, helper edge branches, CSV pass-through), T5 FIXED (dead Relevance import removed), T6 report-only; suite 14/0/0 GREEN; D-085: CUSTOM_TMP_BASE now imported from the shared twolm.test.paths module | docs/src/twolm/test/test_logistic_model.md |
| src/twolm/lm_worker_config.py | analyzed 2026-08-30 (session 21, D-077) + fix campaign D-078 (Roberto's calls): CONFIG worker — JSON5 load → ReversiLogisticModelConfig → base_dir validation (3 precise OS exception types, R3 fixed) → flat checksummed cache write (rlmwf_01_CONFIG.dat + bare-hex .SHA3-256 sidecar of model_dump_json(indent=4), via the injected full-path closure); 35-check probe, 0 mismatches (re-run post D-078); D-076 fixed its cache naming + the SM gate split it exposed; D-078: R2 RESOLVED AT MACHINE LEVEL (closure concatenates the prefix verbatim — replaces the D-069 M8 join; the worker's per-worker concatenation replaced by the full-path closure), R3 precise OS types (FileNotFoundError/NotADirectoryError/PermissionError, messages unchanged), M1-M5 fixed (M5 keep per R1); R1 RESOLVED AS DEFERRED — the ad-hoc cache flow stays until the full pipeline is complete (I-011 "storicizzazione"); suite 14/0/0 GREEN (test_lm_worker_config.py) | docs/src/twolm/lm_worker_config.md |
| src/twolm/test/test_lm_worker_config.py | analyzed 2026-08-30 (session 21, D-077) + fix campaign D-078 (Roberto: "T1-T6: OK"): 4 classes / 14 tests / no PERF (Roberto's new file); D-076: 2 path typos py/→src/ + schema-complete validation payload; D-078: T1 FIXED (D-065 idiom on all 4 classes; dead shutil import removed; a stray per-test mkdtemp in the a-file test removed — it leaked dirs), T2 FIXED (ValueError — json5 0.15.0 raises a plain ValueError, no JSON5Exception in this version), T3 FIXED (_down reset pinned: cfg/use_cache None), T4 FIXED (bare-hex sidecar format pinned); the not-writable test updated to PermissionError (R3); T5/T6 report-only; suite 14/0/0 GREEN; D-085: the idiom + both json_config lines re-anchored to the shared twolm.test.paths (WORKSPACE_ROOT) | docs/src/twolm/test/test_lm_worker_config.md |
| src/twolm/test/data/rlm_00.json | test data (session 21, Roberto): JSON5 config fixture (comment header — json5 load-bearing, D-076; base_dir placeholder "will/be/overwritten/by/python/during/unittesting", use_cache True, cache_files_prefix rlmwf_) | — |
| src/twolm/lm_worker_positions.py | analyzed 2026-08-30 (session 22, D-079): the first cache_manager consumer in the pipeline — 4-step load-or-compute over the regab data set (binio-format sidecar + duck-typed data checksum rds.compute_sha3_256_hash) + post-processing (positions / game_values / rds_checksum / training_pop_stats on the context) + is_cache_consistent (pure metadata compare); enabled line-by-line 601de87 (CREATED → CONFIG → POSITIONS); 13 verified facts V1-V13 (49-check probe, 0 mismatches): flat rlmwf_02_POSITIONS.dat (D-078 machine-level fix re-verified — the latent rlmwf_/ subdirectory trap gone), cross-run cache round-trip identity, D-071 R1 cache-warming visible in a domain worker, corruption / business-inconsistency → delete + recompute, is_allowed=ctx.use_cache consumed; D-080 fix campaign (Roberto: "correggile tutte"): R1 FIXED (5-arg connection call — port + password now take effect, DEBUG log includes the port never the password), M1-M4 FIXED (@validate_call factory, dead pathlib import, flagged trailing whitespace, load_fn checksum=False), cross-ref note RESOLVED (regab_store docstring + regab.md row — the sidecar is cache_manager's, D-072); probe re-pinned (51 checks, 0 mismatches); suite 2/0/0 GREEN (test_lm_worker_positions.py, 2 DB-gated, run with live DB) | docs/src/twolm/lm_worker_positions.md |
| src/twolm/test/test_lm_worker_positions.py | analyzed 2026-08-30 (session 22, D-079): Roberto's file, copied from the original repo with the POSITIONS enablement (601de87, line-by-line step 1); 1 class / 2 tests / no PERF; end-to-end cache round-trip pin (DB hit + flat files; second instance cache hit + no DB), stdout captured via patched StringIO; green on first run, no fixes; D-080 (Roberto: "fai tutto anche qui"): T1-T4 FIXED (D-065 idiom, SKIP_REGAB_DB gate, dead if-False blocks + sys import removed, header grammar) — test campaign CLOSED; suite 2/0/0 GREEN (2 DB-gated, run with live DB); D-085: the idiom + the json_config line re-anchored to the shared twolm.test.paths (WORKSPACE_ROOT) | docs/src/twolm/test/test_lm_worker_positions.md |
| src/twolm/rlm_config_schemas.py | analyzed 2026-08-30 (session 22, D-079): the pydantic config domain — ReversiLogisticModelConfig (10 fields, JSON5 entry point) over the nested tree, all RLMBaseConfig (free-form properties bag) except StatModelConfig; Bitboard hex fields (16-hex no-0x parse, uppercase 16-hex serializer); 12 verified facts V1-V12 (probe E, 0 mismatches); D-080: R1 FIXED (c2>c1 cross-field model_validator — the strong-Wolfe invariant enforced), M1-M4 FIXED (hex docstring example, model_validator import now load-bearing, strict List[StatusString] + StatModelConfig → RLMBaseConfig, default_factory lists); no dedicated suite (covered by test_lm_worker_config validation class + the D-079 probe E, re-pinned D-080) | docs/src/twolm/rlm_config_schemas.md |
| src/twolm/lm_worker_features.py | analyzed 2026-08-31 (session 22, D-081); enabled in f051dd3 (Roberto) — the pipeline now runs 4 active levels (CREATED → CONFIG → POSITIONS → FEATURES); the FIRST pure-compute level (no DB, no cache_manager, no cache file, no features_checksum field); 13 verified facts V1-V13 (42-check probe, 0 mismatches): feature order [INTERCEPT, ALMC, LMC, DLMC, EDGE, ELLE], 6 features / 16 n_instances, hash re-derived independently, zero-feature guard, cross-run identity; D-082 (Roberto: R1 "ok, fissa il bug", M1-M3 OK): R1 + M1-M3 FIXED (amask log, @validate_call factory, whitespace, orphan comment removed) — module CLOSED; 44-check probe 0 mismatches; suite 2/0/0 GREEN (2 DB-gated, run with live DB) | docs/src/twolm/lm_worker_features.md |
| src/twolm/test/test_lm_worker_features.py | analyzed 2026-08-31 (session 22, D-081): Roberto's file, brought in with the FEATURES enablement (f051dd3); 1 class / 1 test at analysis; green on first run with the live DB; D-082 (Roberto: T1-T4 + M2 OK + his own proposal for the golden content test): T1-T4 + M2 FIXED (D-065 idiom, SKIP_REGAB_DB gate, Path import now load-bearing, header grammar, whitespace), M1 LEFT AS-IS (recorded at I-012 — evaluate moving FEATURES before POSITIONS), test_feature_set_content_golden ADDED (3 hash literals + full content pin) — test campaign CLOSED; 1 → 2 tests; suite 2/0/0 GREEN (2 DB-gated, run with live DB); D-085: the idiom + the json_config line re-anchored to the shared twolm.test.paths (WORKSPACE_ROOT) | docs/src/twolm/test/test_lm_worker_features.md |
| src/twolm/rlm_indexes.py | analyzed 2026-08-31 (session 23, D-083); brought in with a323e0f (Roberto — the INDEXES line-by-line enablement, 5th active level): the 5th-level data object (2-D uint32 index matrix + rds_checksum + feature_set_hash, by-reference storage) + the 4 public functions (store / load / compute / is_cache_consistent) + the duck-typed compute_sha3_256_hash (the cache_manager 3rd-return-element hook); the SECOND cache_manager consumer in the pipeline after POSITIONS; 12 verified facts V1-V12 (probe re-pinned D-084: 56 checks, 0 mismatches); D-084 (Roberto: "Sì fai tutto"): R1 + M1-M4 + M6 FIXED (store docstring corrected — the sidecar is cache_manager's, D-072; 5 dead imports removed, "togheter" typo, 4 trailing-whitespace lines, version gate via expected_version, __repr__ added), M5 left as-is (by design — documented circular-import constraint); 5 @validate_call decorators (the 5th is __repr__); file 180 → 190 lines; module CLOSED; suite 14/0/0 GREEN (test_rlm_indexes.py) | docs/src/twolm/rlm_indexes.md |
| src/twolm/lm_worker_indexes.py | analyzed 2026-08-31 (session 23, D-083); brought in with a323e0f (Roberto — the INDEXES line-by-line enablement): the cache-consuming level — the uniform 7-kwargs cache_manager wiring (the injected full-path closure — flat rlmwf_04_INDEXES.dat, the D-078 machine-level naming — use_cache, the 5 rlm_indexes fns, the metadata-compare validate_fn); _down clears BOTH context attributes; 8 verified facts V1-V8 (probe re-pinned D-084: 56 checks, 0 mismatches): flat cache files (no rlmwf_03_FEATURES*), data vs file checksum distinction, (N, 16) uint32 identity, cross-run round-trip, the _down clearing; D-084 (Roberto: "Sì fai tutto"): M1-M3 FIXED (@validate_call on the factory + pydantic import — the D-080/D-082 pattern, 2 trailing-whitespace lines, load_fn → lambda path: ...(path, checksum=False) — the D-080 M4 shape); file 77 → 80 lines; module CLOSED; suite 2/0/0 GREEN (test_lm_worker_indexes.py, 2 DB-gated post D-084 T2) | docs/src/twolm/lm_worker_indexes.md |
| src/twolm/test/test_rlm_indexes.py | analyzed 2026-08-31 (session 23, D-083); Roberto's file, brought in with a323e0f; 5 classes / 14 tests / no PERF (13 at analysis + the rds-only-differs test added D-084 M2); all file I/O mocked (binio patched), no temp dirs, no DB; the store/load contract fully pinned (exact 4-call sequence, both checksum flags, all 3 RuntimeError messages, the by-reference init); D-084 (Roberto: "Sì fai tutto"): T1-T5 + M1-M2 FIXED (dead IndexArray import removed, header grammar, the 2 broad assertRaises(Exception) → the precise pydantic ValidationError, rds_checksum added to test_init_fails_with_invalid_indexes_type — the invalid indexes is now the thing under test, Italian comment → English, 19 trailing-whitespace lines, the rds-only is_cache_consistent branch now unit-tested); file 287 → 304 lines; test campaign CLOSED; suite 14/0/0 GREEN | docs/src/twolm/test/test_rlm_indexes.md |
| src/twolm/test/test_lm_worker_indexes.py | analyzed 2026-08-31 (session 23, D-083); Roberto's file, brought in with a323e0f; 1 class / 2 tests / no PERF; the end-to-end cache round-trip pin (DB hit through POSITIONS + flat rlmwf_04_INDEXES.dat + "Executing heavy computation"; second instance "Cache successfully loaded and validated" + no heavy computation); green on first run with the live DB; the dependency comment is ACCURATE (contrast test_lm_worker_features M1); D-084 (Roberto: "Sì fai tutto"): T1-T3 + M1 FIXED (the D-065 idiom — CUSTOM_TMP_BASE via __file__, setUpClass mkdir, TemporaryDirectory first, defensive tearDown; the SKIP_REGAB_DB gate — both tests now DB-gated, header grammar + the live-DB / gate run note, 13 trailing-whitespace lines); file 137 → 158 lines; test campaign CLOSED; suite 2/0/0 GREEN (2 DB-gated, run with live DB); D-085: the idiom + the json_config line re-anchored to the shared twolm.test.paths (WORKSPACE_ROOT) | docs/src/twolm/test/test_lm_worker_indexes.md |
| src/twolm/test/paths.py | introduced 2026-08-31 (session 23, D-085 — Roberto's design choice "A"): the single home of the workspace-root-anchored test paths — WORKSPACE_ROOT (marker-based derivation: the first ancestor holding pyproject.toml — not a parents[N] level count, survives file moves) + CUSTOM_TMP_BASE (= <root>/build/tmp, the D-065 base); the per-test-file __file__ derivations, the CWD-relative JSON fixture paths (now str(WORKSPACE_ROOT / "src/twolm/test/data/rlm_00.json")), and the test_regab .env / mkdtemp are all re-anchored to it; no public functions (constants only), hence no @validate_call | docs/src/twolm/test/paths.md |
| src/twolm/test/test_paths.py | introduced 2026-08-31 (session 23, D-085): 1 class / 3 tests / no DB / no gate / no artifacts — pins WORKSPACE_ROOT absolute + marker-holding + ancestor of src/twolm/test/, CUSTOM_TMP_BASE == <root>/build/tmp absolute; imports the module (from twolm.test import paths) so a rename surfaces in one place | docs/src/twolm/test/test_paths.md |
| src/twolm/rlm_wmaps.py | introduced 2026-08-31 (session 23, Roberto's commit 73b4342 — the WMAPS bring-in, 6th pipeline level): the WMAPS data object (ReversiLogisticModelWMaps: rlm_indexes_checksum, cut_off, feature_w_ranges (F,3) int64 [fallback, w_min, w_max] per feature, iwmap_feature_offset (F+1,) uint32, iwmap (K,) int64 (−1 = configuration unseen in the dataset), wmap (W,3) int64 [fid, config_id_or_−1, freq], wmap_fallback (F_cut,3) int64, w (W,) float32 zeros) + the 4 public fns (store / load / compute / is_cache_consistent) + the duck-typed compute_sha3_256_hash over the 6 arrays; the 3rd cache_manager consumer in the pipeline; analysis D-086: the dead itertools accumulate import (L35), 23 non-comment trailing-whitespace lines (incl. the L275 / L288 code lines), compute + is_cache_consistent lack @validate_call with no rlm_indexes-L166-style note (the TYPE_CHECKING constraint); R1 RESOLVED as no-guard (Roberto's contract: the indexes are unsigned, 0..n_configurations−1, never −1 — dense by contract, documented in the compute docstring); fix campaign D-087 CLOSED (Roberto: "Procedi su tutto"): the dead accumulate import gone, the no-validation note added (the rlm_indexes style), 23 ws lines stripped; the D-087 '9-space __init__ indent' observation corrected as a misread (D-088 — verified 8 spaces, canonical, no change); file 311 → 316 lines; module CLOSED | docs/src/twolm/rlm_wmaps.md |
| src/twolm/lm_worker_wmaps.py | introduced 2026-08-31 (session 23, Roberto's commit 73b4342 — the WMAPS bring-in, 6th active level): the cache-consuming level, the uniform 7-kwargs cache_manager wiring (flat rlmwf_05_WMAPS.dat + .SHA3-256 sidecar, the D-078 machine); _up sets the 6 ctx arrays + wmaps_obj_checksum; analysis D-086: the factory lacks @validate_call (the other 5 workers all have it) + no pydantic import; load_fn is the raw function (checksum defaults True → double sidecar validation — the house shape is lambda path: ...(path, checksum=False), D-080 M4 / D-084 M3); _down does NOT clear ctx.wmaps_obj_checksum (the house shape clears object + checksum, lm_worker_indexes); fix campaign D-087 CLOSED: factory @validate_call + pydantic import, load_fn = lambda checksum=False (the house shape), _down clears wmaps_obj_checksum, 4 ws lines stripped; file 87 → 91 lines; module CLOSED | docs/src/twolm/lm_worker_wmaps.md |
| src/twolm/test/test_rlm_wmaps.py | introduced 2026-08-31 (session 23, Roberto's commit 73b4342): 3 classes / 6 tests / no DB / no gate — compute on the handcrafted 4×3 mock (fallback + the cut_off=0 no-fallback branch), is_cache_consistent (3), store/load cycle (1, checksum=False both sides); the D-085 idiom APPLIED (Roberto's instruction): the CWD-relative mkdtemp → TemporaryDirectory under the shared CUSTOM_TMP_BASE, defensive tearDown, the twolm.test.paths import, the dead shutil import gone; file 251 → 259 lines; fix campaign D-087 CLOSED: header corrected (the file is DB-free), dead StringIO + patch imports gone, the leftover generation comment gone, 21 ws lines stripped, +5 IO pins (the golden hash 12c3344e…, sidecar valid/mismatch, wrong description, version mismatch) + TestRLMWmapsInit (2 tests) — 6 → 13 tests; file 259 → 325 lines; suite 13/0/0 GREEN | docs/src/twolm/test/test_rlm_wmaps.md |
| src/twolm/test/test_lm_worker_wmaps.py | introduced 2026-08-31 (session 23, Roberto's commit 73b4342): 2 classes / 3 tests / all DB-dependent — the worker round-trip (2 tests: first run "Forcing computation" + both D-078 files, second instance cache hit, no recompute; cache names + steps 4/5 pinned) + the golden content (rlm_01.json, cut_off=2: feature_w_ranges (4,3), offsets [0,1,66,93,174], iwmap 174, wmap (21,3), wmap_fallback (10,3), w=21 float32 zeros — every literal independently re-derived by the probe, E0-E9, 0 mismatches); the D-085 idiom APPLIED (both classes: the CWD mkdtemp + CWD json_config → TemporaryDirectory under the shared CUSTOM_TMP_BASE + WORKSPACE_ROOT-anchored json, defensive tearDown, the paths import, the dead shutil import gone); file 283 → 301 lines; fix campaign D-087 CLOSED: the SKIP_REGAB_DB gate added to both setUps (now 3/0/3 under the gate, as claimed by the header) + 20 ws lines stripped; file 301 → 315 lines; suite 3/0/0 GREEN (live DB) | docs/src/twolm/test/test_lm_worker_wmaps.md |
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
- Suite status (2026-08-31): board 193/0/12, pattern 64/0/3,
  mobility 26/0/1, feature 20/0/1, binio 45/0/0 (42 + 3 usage),
  regab 37/0/0 (2 mocked run, 35 DB skipped under SKIP_REGAB_DB=1),
  opt_lbfgs 13/0/0, state_machine 49/0/0, cache_manager 21/0/0,
  logistic_model 14/0/0 (1 test muted per Roberto, D-073;
  D-074/D-075 fix batches; D-076 restored delegation test),
  lm_worker_config 14/0/0 (D-076), lm_worker_positions 2/0/0
  (601de87; 2 DB-gated, run with live DB), lm_worker_features
  2/0/0 (f051dd3; 2 DB-gated post D-082, run with live DB),
  rlm_indexes 14/0/0 (a323e0f; 14 tests post D-084 M2 — no DB,
  all file I/O mocked), lm_worker_indexes 2/0/0 (a323e0f; 2
  DB-gated post D-084 T2 — the setUp moves through POSITIONS,
  run with live DB), paths 3/0/0 (D-085 — no DB, pure path
  assertions), rlm_wmaps 6/0/0 (73b4342 — no DB, no gate),
  lm_worker_wmaps 3/0/0 (73b4342; 3 DB-gated post D-087
  T1 — the setUp moves through INDEXES, run with live DB),
  rlm_wmaps 13/0/0 (post D-087 T10 — no DB, no gate) — all
  GREEN. Totals: 535 tests, 61 skipped
  under the gate (17 PERF=1 print-only performance tests + 35
  DB-gated regab tests + 2 DB-gated lm_worker_positions tests +
  2 DB-gated lm_worker_features tests + 2 DB-gated
  lm_worker_indexes tests + 3 DB-gated lm_worker_wmaps tests; no
  performance gates in any suite, D-036). Warm run ≈ 0.5 s (board) / ≈ 2.8 s (full discover,
  numba cache warm in src/twolm/__pycache__/).

## Where we are

- board.py: analyzed 2026-08-25 (session 1,
  docs/src/twolm/board.md): architecture, hand-verified D8
  transformation tables, Kogge-Stone legal-move boundary masks,
  flip-set computation. Modified by the fix campaign (T20, T22, T25,
  T36, T37, T38); all 5 real issues resolved — R1 (D-017, docstring
  follows the code), R2 (T20, return annotation), R3 (D-018, explicit
  pass check), R4 (T24, bare-int ValidationError pin +
  TestPydanticVersion), R5 (implicit NumPy ≥ 2.0 declared in
  pyproject.toml, D-011); board.md issue list re-marked 2026-08-29
  (was stale since the 08-26 campaign).
- test_board.py: analyzed 2026-08-25 (session 2,
  docs/src/twolm/test/test_board.md): coverage by area, values
  re-derived independently, 11 defects, completeness verdict +
  P0/P1/P2. Fix campaign COMPLETE 2026-08-26 (session 3): all P0 +
  P1 + full P2 batch (T26–T35, one commit per Roberto's "Facciamoli
  tutti, un solo commit"); suite 157 → 193, GREEN throughout. Header
  'environmeant' typo fixed 2026-08-29 (D-050, with test_feature
  T4); the remaining grammar nit stays reported-only. Gameplay
  verification (2026-08-26, session 3): 200 random full games on the
  public API only, zero invariant violations — board.py is a proven
  complete game kernel (the game loop belongs to a separate module —
  NOT in the port plan, I-005 resolved).
- pattern.py: analyzed 2026-08-27 (session 4,
  docs/src/twolm/pattern.md, review-only per D-019). All real issues
  resolved: R1 (D-020) principal mask = numerically lowest orbit
  mask (unique representative; the 4-corners corner case) +
  regression test; R2-R7 (D-021) docstring/hygiene, code behavior
  untouched; R8 (D-022) closed as the little-endian-only platform
  note. Minor sweep COMPLETE 2026-08-27 (session 7): 19/19 items,
  each approved one at a time — D-023 (strict @validate_call
  constructor), D-024 (names/masks → @property; legacy .names() /
  .masks() call sites tracked as I-006), D-025 (collision
  precondition stays on the caller) + fail-fast checks (#17 empty
  PatternSet, #18 empty mask), constant rename (#12), type-table
  cross-check (#11), doc/hygiene/API fixes. D-032 (2026-08-28,
  session 10): Burnside attributes n_invariant_configs /
  n_unique_configs (formulas verified 29/29 sample patterns).
- test_pattern.py: analyzed 2026-08-27 (session 8,
  docs/src/twolm/test/test_pattern.md): 12 classes / 50 tests / 3
  PERF; 21/21 goldens independently re-derived (0 mismatches); 16
  defects T1-T16 + T17 (sqa8/sqh1 fixtures swapped). Fix campaign
  CLOSED: P0 (D-026-028, 6da0803) + P1 (D-029/030/031: row
  independence both public indexing APIs + EDGE 6561-entry dict pin)
  + P2 hygiene (D-033: T1-T7, T15-T16; T19 found + fixed in T2) + P2
  breadth (D-034: T11-T14 + T17). Final suite 64/0/3 GREEN. Parked:
  T18 noted-only (np.uint8 3**n_squares overflow, no code action),
  M1 deferred (stale PatternSet Raises docstring, awaiting go-ahead).
- mobility.py: analyzed 2026-08-28 (session 10,
  docs/src/twolm/mobility.md): feature index formula,
  n_configurations = distinct index values, columns in the set's
  sorted (mask, amask) order, sha3_256 hash — all verified against
  independent ground truth (V1-V8, 200-position differential,
  popcount64 vs int.bit_count on 200,010 values). R1-R6 fix batch
  (D-035, no behavior change); M1-M5 disposed (D-036: M1 glossary
  shipped, M2/M3/M5 left as-is, M4 corrected — no PERF gates in any
  suite).
- test_mobility.py: analyzed 2026-08-28 (session 10,
  docs/src/twolm/test/test_mobility.md): 2 classes / 23 tests / 1
  PERF; 13 verified facts (0 mismatches); 9 defects T1-T9. Fix
  campaign CLOSED the same day (D-037: T1-T9, per-item approvals,
  single batch commit — P0 __repr__ goldens, P1 multi-position row
  independence, P2 hygiene/breadth incl. pinned hash literal
  2e553593...208a94). Suite 23 → 26, GREEN 26/0/1. Mobility module
  fully done.
- feature.py: analyzed 2026-08-28 (session 11,
  docs/src/twolm/feature.md) — the first integration module
  (intercept + MobilitySet + PatternSet → one (N, I) index matrix).
  All goldens re-derived independently (V1-V8, zero mismatches: 3x10
  matrix, 13 orbit sizes, 3 pinned hashes). R1-R4 (D-038) + M1-M4
  (D-039..D-042; M3 left as-is → I-007) — all disposed.
- test_feature.py: analyzed 2026-08-28 (session 11,
  docs/src/twolm/test/test_feature.md): 4 classes / 14 tests / 1
  PERF; 9 verified facts W1-W9 (0 mismatches); 9 defects T1-T9. T
  campaign CLOSED 2026-08-29 (D-043..D-050: T6, T1, T2, T3, T5, T7,
  T9, T4 — both files; T8 left as-is). Final suite 20 tests (19 run
  + 1 PERF), GREEN 20/0/1. FEATURE module fully done.
- binio.py: analyzed 2026-08-29 (session 14,
  docs/src/twolm/binio.md) — BinaryWriter/BinaryReader with MAGIC
  framing + SHA3-256 sidecar + optional LZ4 whole-file compression.
  15 verified facts V1-V15 (0 mismatches); T1-T4 fix batch (D-051:
  lz4 in pyproject.toml, dead Path import, "Aauthor" → "Author",
  test_unknown_type_code_raises). Suite 45/0/0 GREEN (42 + 3 usage).
  BINIO module done.
- test_binio.py: analyzed 2026-08-29 (session 14,
  docs/src/twolm/test/test_binio.md, with test_usage_binio.py): 12
  classes / 44 tests at analysis; T4 applied (D-051, ArrayTest now 8
  tests). Suite 44 → 45, GREEN 45/0/0, no PERF.
- regab.py: analyzed 2026-08-29 (session 15,
  docs/src/twolm/regab.md) — REversi GAme Base: psycopg2 DB access +
  RegabDataSet + binio file serialization. 5 verified facts V1-V5
  (0 mismatches, sha3_256 golden); T1-T7 fix batch (D-052: "Aauthor"
  typo, dead typing imports, psycopg2/pandas/python-dotenv in
  pyproject.toml, DB query deferred, SKIP_REGAB_DB=1 gate,
  _validate_where_clause SQL-injection guard). Suite 37/0/0 GREEN
  (35 DB + 2 mocked). REGAB module done.
- test_regab.py: analyzed 2026-08-29 (session 15,
  docs/src/twolm/test/test_regab.md): T5+T6+T7 applied (D-052): dead
  imports, SKIP_REGAB_DB gate, 4 SQL-injection tests
  (TestRegabGPAsDF 12 → 16). Suite 33 → 37/0/0 GREEN.
- opt_lbfgs.py: analyzed 2026-08-29 (session 16,
  docs/src/twolm/opt_lbfgs.md) — L-BFGS optimizer (strong Wolfe line
  search, two-loop recursion, warm-start). 5 verified facts V1-V5
  (0 mismatches); T1-T7 fix batch + 9 new tests (D-053:
  RuntimeException → RuntimeError hard bug, CURVATURE_THRESHOLD
  used, low_progress_count spelling, hermite None fallthrough,
  save_fn 7-param hint, fractional docstring, test d param). Suite
  13/0/0 GREEN. OPT_LBFGS module done.
- test_opt_lbfgs.py: analyzed 2026-08-29 (session 16,
  docs/src/twolm/test/test_opt_lbfgs.md): T7 applied + 9 new tests
  (D-053): TestLBFGSInputValidation (3), TestFixedSizeMaxList (4,
  incl. T1 regression), TestTwoLoopRecursion (2). Suite 4 → 13/0/0
  GREEN.
- state_machine.py: analyzed 2026-08-29 (session 19,
  docs/src/twolm/state_machine.md) — generic pipeline orchestrator
  (Workers up/down + shared Context + logging/timing history/CSV
  export), domain-agnostic, pure stdlib (no new deps). 17 verified
  facts V1-V17 (0 mismatches): half-open interval semantics (up c→t
  runs workers c+1..t, target included; down c→t runs c..t+1, target
  excluded, L313 reassignment required), worker 0 unreachable via the
  public API — intentional sentinel (D-059), failure leaves
  current_step at the failed step (retry of the same target skips
  it — failure semantics documented + pinned, D-060), verbosity gate
  is `relevance >= verbosity` (post
  D-057: VERY_LOW ERROR-only, NONE silent), LogEntry frozen dataclass
  (D-058), move_to_last name-based (duplicate names rejected at
  construction — dispatch unambiguous, D-061), context injection is a
  side effect (shared context
  re-binds to the last machine). R1 FIXED (D-057: Verbosity.VERY_LOW=4
  added, NONE=5, `>=` gate unchanged — HIGH..LOW byte-identical, NONE
  truly silent, old ERROR-only behaviour kept as VERY_LOW; pinned by
  T1); R2 FIXED (D-058: LogEntry → frozen dataclass, attribute access
  + asdict() for the file/DB dump worker, show_event_log migrated to
  attribute access, observable behaviour unchanged; pinned by
  TestLogEntry; test-file datetime import now load-bearing → M2/T11
  resolved); R3 RESOLVED as intentional sentinel (D-059: state model
  + sentinel documented in class and move_to_step docstrings, pinned
  by test_worker_zero_is_sentinel_never_executed, no behaviour
  change); R4 RESOLVED (D-060: keep + document + pin — failure
  semantics in move_to_step docstring, recovery = move to k-1 then
  up, machine domain-agnostic; pinned by
  test_retry_after_failure_skips_failed_step, closes T6); R5 RESOLVED
  (D-061: __init__ rejects duplicate worker names — case-insensitive
  ValueError fail-fast before any state is touched; move_to_last
  unchanged, name dispatch now unambiguous; closes M12; pinned by 2
  new tests); T2 coverage added (D-062: TestContextInjection 7 tests,
  incl. V17 shared-context re-bind; M8 extended — the prefix must end
  with a separator or the level name glues onto it); T3 coverage
  added (D-063: TestDisplayGoldens
  — 3 end-to-end display goldens, frozen clock); T4 coverage added
  (D-064: 3 move_to_last tests, incl. the single-worker sentinel
  no-op); T5 fixed (D-065: CSV test rewritten — header names,
  ISO-8601 +00:00, duration identity, artifact under build/tmp;
  new house rule: test files only in workspace_root/build/tmp,
  removed afterwards); T7 pinned (D-066: 2 tests — bool as int
  step, np.int64 TypeError); T8 + T9 pinned (D-067: 5 tests —
  current_worker_name live view + UNDEFINED, StepMove field content
  incl. aware-UTC timestamps, duration identity, finally-append on
  failure) — all T items closed. M-sweep batch 1 applied (D-068):
  M1 dead Any import removed; M4 _run_step direction dispatch made
  explicit (elif 'down', anything else ValueError — no behaviour
  change for valid input); M7 __repr__ on Worker (name) and
  StateMachine (worker count, current step, verbosity name —
  lightweight: no context/logs/history); M10 CSV export creates
  missing parent dirs (bare filename no-op on '.'). M-sweep batch 2
  applied (D-069, Roberto's calls): M3 bool is NOT a valid step —
  the strict @validate_call gate rejects True/False with the pinned
  TypeError (test rewritten to rejection); M5 cache helpers renamed
  *_for_current_level (the 2 ported call sites — lm_worker_config,
  lm_worker_positions — and RLMContext's 2 field names were renamed
  D-074, closing the flagged follow-up); M8 cache
  prefix joined with pathlib (no more silent gluing); M11
  @validate_call on Worker init/up/down, SM init/log_event/export,
  move_to_step via a strict private impl whose ValidationError is
  re-raised as the pinned TypeError (pydantic now a module dep —
  already in pyproject). M-sweep CLOSED (D-070, fix campaign item
  14, Roberto: M6 "1, pulisci", M9 leave-as-is): M6 print cleanup
  — the live line prints enum names ([DEBUG:HIGH]) + an explicit
  UTC marker; show_event_log: TIMESTAMP (UTC) header, 2-digit step
  (was 4), RELEVANCE name column (was numeric), 66-underscore rule;
  show_history_of_moves: right-aligned Dur (s) header; the 3
  frozen-clock display goldens rewritten in place (suite count
  unchanged); M9 left as-is — the context injection is load-bearing
  for the domain workers (V17 shared-context re-bind documented);
  future redesign parked at I-010 (post-port). All M items
  (M1-M12) disposed. STATE_MACHINE module fully done — R1-R5, all T
  items (T1-T11), M-sweep (M1-M12) closed, D-057..D-070.
  D-078 (machine-level fix for the lm_worker_config R2): the
  injected cache-path closure now CONCATENATES the prefix onto the
  level name (filename-prefix semantics, per the domain schema)
  instead of the D-069 M8 pathlib join — one shared fix for ALL
  cache-consuming workers (the rlmwf_/02_POSITIONS.dat subdirectory
  trap is gone for lm_worker_positions before it is enabled);
  re-pinned by test_cache_prefix_is_concatenated_verbatim. Suite
  49/0/0 GREEN.
- test_state_machine.py: analyzed 2026-08-29 (session 19,
  docs/src/twolm/test/test_state_machine.md): 5 classes / 49 tests /
  no PERF; all 13 original expectations independently re-derived
  (0 mismatches) — core move mechanics well pinned (up/down
  asymmetry, failure semantics, same-step no-op, bounds/type/name
  errors). 11 defects found (5 now resolved); three whole areas
  untested at analysis (verbosity gate, context injection, display
  methods + move_to_last + edge semantics) — verbosity, injection and
  display now pinned. T1 FIXED (D-057: TestVerbosityGating — 6x5 gating
  matrix + enum values, 2 tests; suite 13 → 15); R2 tests added
  (D-058: TestLogEntry, 3 tests; suite 15 → 18); R3 sentinel pinned
  (D-059: test_worker_zero_is_sentinel_never_executed, 1 test;
  suite 18 → 19); R4 retry/recovery pinned (D-060:
  test_retry_after_failure_skips_failed_step, 1 test; suite 19 → 20,
  closes T6); R5 tests added (D-061: 2 duplicate-name tests — reject
  + case-insensitive, closes T10; suite 20 → 22); T2 FIXED (D-062:
  TestContextInjection, 7 tests; suite 22 → 29); T3 FIXED (D-063:
  TestDisplayGoldens, 3 end-to-end goldens; suite 29 → 32); T4
  FIXED (D-064: 3 move_to_last tests; suite 32 → 35); T5 FIXED
  (D-065: CSV test rewritten — header names, ISO-8601 +00:00,
  duration identity, artifact under build/tmp; suite count
  unchanged); T7 pinned (D-066: 2 tests — bool as int step,
  np.int64 TypeError; suite 35 → 37); T11 resolved as D-058 side
  effect; T8 + T9 pinned (D-067: 5 tests — current_worker_name live
  view + UNDEFINED, StepMove field content; suite 37 → 42); M-sweep
  batch 1 pinned (D-068: 4 tests — unknown direction ValueError,
  Worker __repr__, StateMachine __repr__, CSV parent-dir creation;
  suite 42 → 46); M-sweep batch 2 pinned (D-069: bool test
  rewritten to rejection + 2 constructor ValidationErrors + Path
  prefix join; suite 46 → 49); M6 display goldens rewritten in
  place to the cleaned format (D-070 — enum names + UTC marker on
  the live line, TIMESTAMP (UTC) / 2-digit step / RELEVANCE name /
  66-underscore table, right-aligned Dur (s) header; suite count
  unchanged) — all T items closed, M-sweep COMPLETE. D-078: the
  D-069 M8 pin renamed test_cache_prefix_is_concatenated_verbatim
  and re-pinned to the verbatim concatenation (cache01_CONFIG.dat),
  count unchanged. Suite 49/0/0 GREEN.
- cache_manager.py: analyzed 2026-08-30 (session 20,
  docs/src/twolm/cache_manager.md) + fix campaign batches 1+2
  (D-071/D-072) — the pipeline's load-or-compute cache engine
  (first domain module to import state_machine — Relevance — and
  binio — sidecar API, D-072): 4-step validation (allowed → present
  → checksum → business validity), all failure paths converge on
  the shared compute+store tail; two checksums — the file sidecar
  (binio's sha3_256sum format post D-072, same `<name>.SHA3-256`
  naming scheme as binio) and the duck-typed data checksum
  (`compute_sha3_256_hash` on the data object, 3rd return element).
  17 verified facts V1-V17 (0 mismatches, independent probe
  scratch/verify_cache_manager.py). D-071 (Roberto's approvals): R1
  RESOLVED as intentional (step 0 `is_allowed=False` still warms the
  cache file — docstring + pin), R2 FIXED (validate_fn moved into
  the step-3 try — a raising validator deletes + recomputes like a
  load failure; ERROR msg re-worded "Failed to load or validate
  cache file ..."), R4 FIXED (@validate_call — str→Path coercion is
  the approved behaviour change, non-coercible → ValidationError),
  M1-M3 fixed (dead `Any` import, docstring typos, step-2 WARN now
  accurate "(sidecar missing or mismatched)"). D-072 (Roberto:
  "Approvato!"): R3 RESOLVED — the binio-import proposal adopted:
  `import hashlib` + `_compute_checksum` + `_save_checksum`
  deleted, `_verify_checksum` is a thin wrapper over
  `verify_sha3_256_sidecar` (FileNotFoundError / BinaryFormatError
  / UnicodeDecodeError → False), the compute tail writes the
  sidecar via `write_sha3_256_sidecar` — a binio-written sidecar
  now verifies (V15c flips) and legacy bare-hex sidecars still
  verify (zero cache invalidation). CACHE_MANAGER module fully done
  — R1-R4, M1-M3, T1-T7 all resolved (T8 report-only),
  D-071..D-072. Suite 21/0/0 GREEN.
- test_cache_manager.py: analyzed 2026-08-30 (session 20,
  docs/src/twolm/test/test_cache_manager.md) + fix campaign
  batches 1+2 (D-071/D-072): 2 classes / 21 tests / no PERF (13 →
  21 batch 1; 21 → 21 batch 2). T2 (P0) closed: 5 new tests pin the
  whole duck-typed data-checksum feature (with-method digest on
  compute + load paths, missing method → None, non-callable
  attribute → None, raising method on the load path → recompute) +
  a pin for the D-071/R2 raising validator; T1 (3rd element
  asserted on all 6 original pipeline tests), T4 (step-0 on-disk
  warm-cache effect, per the R1 ruling), T5 (missing-sidecar
  pipeline variant), T3 (sidecar content format pin — restated to
  the binio format in D-072), T7 (on-disk replacement + valid
  sidecar after every recompute) all FIXED. D-072: T6 FIXED —
  CUSTOM_TMP_BASE anchored to the workspace root via __file__
  (D-065 idiom, as in test_state_machine.py); helper suite rebuilt
  around the binio API (R3 pin test_binio_sidecar_verifies,
  legacy-compat pin, malformed/undecodable wrapper pins added; the
  2 direct-compute helper tests dropped — binio's suite owns the
  hash); pipeline set-ups switched to write_sha3_256_sidecar. T8
  header grammar report-only. CACHE_MANAGER module CLOSED — T1-T7
  all resolved.
- base_model.py: analyzed 2026-08-30 (session 21,
  docs/src/twolm/base_model.md) — thin facade base over
  StateMachine: pure delegation (current_step /
  current_worker_name / verbosity get+set, move_to_step /
  move_to_last, the 2 display methods, CSV export); `model.context
  is model.sm.context` (one shared object, probe-verified).
  D-074 (batch 1, Roberto-approved with logistic_model R3 — one
  decision, both facades): R1 RESOLVED — @validate_call on
  `__init__` (approved behaviour change: wrong-typed constructor
  args now raise a pydantic ValidationError at the facade boundary
  instead of only at the inner SM gate, D-069 M11, which still runs
  behind it). D-075 (batch 2, Roberto: "aggiungi"): M1 FIXED —
  `__all__ = ['BaseModel']` added (L39, the D-068 M1 pattern);
  ALL R/M CLOSED. M2 the docstring forward-references the not-
  yet-ported DeepNetworkModel (informational, kept by design).
- logistic_model.py: analyzed 2026-08-30 (session 21,
  docs/src/twolm/logistic_model.md) — the first concrete domain
  facade: RLMContext (@dataclass over the plain Context; 38 fields,
  8 *_checksum, the config→positions→…→analytics artifact
  blackboard) + LogisticModel (4-step construction: plain path
  validation → context → the 15-level worker list, deliberately
  partial per Roberto: CREATED sentinel + CONFIG + POSITIONS
  active (D-076, 601de87), 11 factory imports commented — "una
  riga alla volta") → BaseModel/StateMachine, which injects
  log_event + the 2 cache-path closures. The level-0 CREATED
  sentinel makes D-059 explicit (log ERROR + RuntimeError on direct
  call, probe-verified). 10 verified facts V1-V10 (30-check probe
  scratch/verify_logistic_model.py, 0 mismatches). D-074 (batch 1,
  Roberto: "parti con R1 + R2 + M1 + M2 + M3, per R2 aggiungi la
  @validate_call"; M4 = the vld rename per Roberto): R1 RESOLVED —
  the D-069 name divergence closed: RLMContext's 2 injected-callable
  fields renamed to `*_for_current_level` (lambda defaults are now
  the pre-injection fallback under the same names, like log_event)
  + the 2 ported worker call sites renamed (lm_worker_config,
  lm_worker_positions) — 4 lines, the silently-None trap is gone,
  no `for_next_level` left in src/; R2 RESOLVED — the 8
  `Union[str, None]` annotations modernized to `str | None` (no
  import — the file's own style, PEP 563-safe); R3 RESOLVED (with
  base_model R1) — @validate_call on `__init__` (approved behaviour
  change: int args → pydantic ValidationError at the facade); M1-M4
  fixed ("weight", `vld_pop_stats` — Roberto: typo,
  IsADirectoryError for dir-as-config, `__init__` docstring).
  D-075 (batch 2, Roberto: "rimuovi"): M5 FIXED — the dead
  `field` import removed; ALL R/M CLOSED. D-076 (Roberto +
  fixes): `lm_worker_config()` uncommented in the worker list —
  the pipeline now runs 2 active levels (CREATED sentinel +
  CONFIG); json5 declared in pyproject.toml; the SM gate split
  (domain pydantic ValidationErrors from the CONFIG worker no
  longer converted to the gate's TypeError — D-060 propagation).
  D-081 (f051dd3, Roberto): `lm_worker_features()` uncommented
  (import L43 + entry L209) — the pipeline now runs 4 active
  levels (CREATED sentinel → CONFIG → POSITIONS → FEATURES);
  the 35-check probe re-pinned to the post-D-074/D-076/D-081
  state (the session-21 original pinned the pre-D-074 state and
  was never re-pinned after the fix batches): 0 mismatches.
  a323e0f (D-083, Roberto): `lm_worker_indexes()` uncommented
  (import L44 + the worker-list entry) — the pipeline now runs
  5 active levels (CREATED sentinel → CONFIG → POSITIONS →
  FEATURES → INDEXES); the 35-check probe re-pinned again (V3c
  the 5-worker list; V10 unchanged — 8 *_checksum fields, no
  features_checksum): 0 mismatches.
- test_logistic_model.py: analyzed 2026-08-30 (session 21,
  docs/src/twolm/test/test_logistic_model.md) — 1 class / 7
  methods (5 active + 2 muted with a `_` prefix per Roberto —
  restored "una riga alla volta" with the pipeline; the factory
  patches are currently inert; the muted tests' preconditions
  verified: 1-worker machine rejects step 1 with IndexError and
  "POSITIONS" with ValueError). OPEN: T1 `test_facade_methods_
  exist` overpromises (a smoke test with a try/except+self.fail
  anti-pattern, 5 of 7 methods uncovered — propose real delegation
  pins + the verbosity round-trip + the CSV pass-through); T2
  artifacts in the system temp dir (tempfile.mkdtemp() with no
  dir= — the D-065 deviation fixed in test_cache_manager T6/D-072);
  T4 untested corners (the injected callables — a pin would have
  caught R1 —, the sentinel RuntimeError, the helper edge branches,
  the CSV pass-through); T5 dead import Relevance; T6 header
  grammar report-only. D-075 (test batch, Roberto: "T1-T6:
  procedi"; file 156 → 294 lines, 5 → 13 active tests): T1 FIXED —
  the smoke test replaced by per-method delegation pins
  (patch.object on model.sm + assert_called_once_with for all 5
  pass-throughs, move_to_step pinned int AND name string) + the
  views/verbosity round-trip; T2 FIXED — the D-065 idiom
  (CUSTOM_TMP_BASE under build/tmp, setUpClass mkdir,
  TemporaryDirectory FIRST in setUp, defensive tearDown); T3
  unchanged (intentional — the muted tests come back with the
  pipeline); T4 FIXED — 7 corner tests (the injected closures'
  __name__s + the bare-context no-op fallback + the path
  computation through a dummy cfg — a pin that would have caught
  R1 —, both sentinel RuntimeError messages, both helpers' edge
  branches, the CSV pass-through with a header-only build/tmp
  artifact); T5 FIXED — the dead Relevance import removed; T6
  unchanged (report-only). D-076 (Roberto):
  test_move_to_step_delegates_to_state_machine restored
  (renamed, no leading underscore) — the CONFIG level it targets
  now exists; suite 13/0/0 → 14/0/0 (14 active + 1 muted).
  D-078: the T4 corner re-pinned to the filename-prefix
  concatenation (cache00_CREATED.dat / base/cache00_CREATED.dat,
  from the D-069 M8 join).
- lm_worker_config.py: brought in with the batch (6bb45fb);
  D-074 cross-reference change (call-site rename, part of
  logistic_model R1); D-076 (Roberto + fixes):
  `lm_worker_config()` uncommented in the pipeline (CREATED +
  CONFIG now the 2 active levels), cache naming fixed to the flat
  rlmwf_01_CONFIG.dat (prefix concatenation, not pathlib join —
  Roberto's "nomi della CACHE" suspicion confirmed), the SM gate
  split it exposed (domain pydantic ValidationErrors no longer
  converted to the gate's TypeError), json5 declared in
  pyproject.toml. Analyzed D-077 (35-check probe, 0 mismatches);
  fix campaign D-078 (Roberto's calls): R1 RESOLVED AS DEFERRED
  (the ad-hoc cache flow stays — the cache_manager flow does not
  fit a JSON file, and the step may not need a cache at all;
  revisit when the full pipeline is complete; the
  "storicizzazione" idea recorded at I-011), R2 RESOLVED AT
  MACHINE LEVEL (the injected closure concatenates the prefix
  verbatim — one fix for all workers; the worker now uses the
  full-path closure directly, uniform with lm_worker_positions),
  R3 FIXED (FileNotFoundError / NotADirectoryError /
  PermissionError, messages unchanged), M1-M5 fixed (M5 keep per
  R1), T1-T4 fixed in the test file
  (docs/src/twolm/lm_worker_config.md). Campaign CLOSED — only
  the R1 full-pipeline revisit remains.
- lm_worker_positions.py: brought in with the batch (6bb45fb);
  D-074 cross-reference change (call-site rename, part of
  logistic_model R1); the D-077 latent (L58-59 full-path closure
  into a cache_manager that does no mkdir) CROSSED OUT by D-078 at
  machine level — re-verified in the D-079 analysis: flat
  rlmwf_02_POSITIONS.dat + .SHA3-256 (binio format) written on
  first run, no rlmwf_/ subdirectory. Analyzed 2026-08-30
  (session 22, D-079, docs/src/twolm/lm_worker_positions.md): the
  first cache_manager consumer in the pipeline — the 4-step
  load-or-compute over the regab data set (binio sidecar +
  duck-typed data checksum rds.compute_sha3_256_hash) +
  post-processing (positions / game_values / rds_checksum /
  training_pop_stats on the context) + is_cache_consistent (pure
  metadata compare: connection + query tuples, the int(str-port)
  normalization, keyword overrides). 13 verified facts V1-V13
  (49-check probe, 0 mismatches): cross-run cache round-trip
  identity, use_cache=False → forced computation but cache still
  warmed (D-071 R1, now visible in a domain worker), corruption →
  delete + recompute, business inconsistency (ec) → delete +
  recompute with the new params, is_allowed=ctx.use_cache — the
  CONFIG worker's switch is consumed here. D-080 (Roberto:
  "correggile tutte"): R1 FIXED (the 5-arg connection call —
  port + password now take effect; the DEBUG log includes the
  port, never the password), M1-M4 FIXED (@validate_call
  factory, dead pathlib import, the flagged trailing whitespace,
  load_fn checksum=False — the redundant sidecar re-verify is
  gone), cross-ref note RESOLVED (regab_store docstring +
  regab.md row — the sidecar is cache_manager's, D-072) —
  module CLOSED.
- test_lm_worker_positions.py: Roberto's file, copied from the
  original repo with the POSITIONS enablement (601de87 — the
  line-by-line step 1; suite 496 → 498). Analyzed 2026-08-30
  (session 22, D-079, docs/src/twolm/test/
  test_lm_worker_positions.md): 1 class / 2 tests / no PERF;
  end-to-end pin of the cache round-trip (first run DB hit + flat
  files; second instance cache hit + no "Extracted" / no DB-
  connection log), stdout captured via the patched StringIO.
  D-080 (Roberto: "fai tutto anche qui"): T1-T4 FIXED — the
  D-065 idiom (CUSTOM_TMP_BASE + TemporaryDirectory-first +
  defensive tearDown), the SKIP_REGAB_DB gate, the dead if-False
  blocks + sys import removed, header grammar — test campaign
  CLOSED.
- rlm_config_schemas.py: brought in with the batch (6bb45fb),
  analysis deferred by Roberto ("Lo faremo in seguito") — done
  2026-08-30 (session 22, D-079, docs/src/twolm/
  rlm_config_schemas.md): the pydantic config domain —
  ReversiLogisticModelConfig (name/description/base_dir/output,
  use_cache, cache_files_prefix "rlmwf_" — the "Filename prefix"
  semantics the D-078 machine-level fix implements) over the
  nested tree, all RLMBaseConfig (the free-form properties bag)
  except StatModelConfig; the Bitboard hex fields parse 16-hex
  without 0x and serialize uppercase 16-hex. 12 verified facts
  V1-V12 (probe E, 0 mismatches). D-080 (Roberto: "correggile
  tutte"): R1 FIXED (check_wolfe_constants — a
  model_validator(mode="after") enforcing c2 > c1; the unused
  model_validator import became load-bearing), M1-M4 FIXED (hex
  docstring example corrected, strict List[StatusString]
  validation status + StatModelConfig → RLMBaseConfig,
  default_factory lists) — module CLOSED.
- lm_worker_features.py: brought in + enabled by Roberto in
  f051dd3 (the line-by-line step 4 — the pipeline now runs 4
  active levels); analyzed 2026-08-31 (session 22, D-081,
  docs/src/twolm/lm_worker_features.md): the FIRST pure-compute
  level — it builds a FeatureSet from the CONFIG-loaded cfg
  (intercept + MobilitySet + PatternSet, the public-API
  composition from feature.py), no DB, no cache_manager, no
  cache file (the flat rlmwf_03_FEATURES* never materialize;
  RLMContext carries no features_checksum field) and exposes
  ctx.feature_set. 13 verified facts V1-V13 (42-check probe,
  0 mismatches): the 4-worker list; feature_set None → set →
  cleared by _down; name 'NoNameFeatureSet' (the schema default
  — the fixture has no name key); the 3 fixture mobilities + 2
  patterns with the CORRECT values; feature order [INTERCEPT,
  ALMC, LMC, DLMC, EDGE, ELLE] (intercept, mobilities sorted
  (mask, amask), patterns sorted mask); n_features 6 /
  n_instances 16 (LMC 65/1, ALMC 65/1, DLMC 129/1, ELLE 81/8,
  EDGE 6561/4); hash = sha3_256(b'INTERCEPT' + mset.hash +
  pset.hash) re-derived independently; the zero-feature guard
  (ValueError + ERROR log); cross-run identity (second
  instance: POSITIONS cache hit, FEATURES recomputed, identical
  set). OPEN awaiting Roberto's call: R1 (the amask DEBUG log
  prints m.mask twice — log-only: LMC (true amask 0) logs
  FFFFFFFFFFFFFFFF, ALMC (true amask all-1) logs
  0000000000000000, DLMC unaffected; the FeatureSet is built
  from the correct values), M1 (no @validate_call on the
  factory — convention-only), M2 (2 non-header trailing-
  whitespace lines L49/L78), M3 (the orphan L63 comment quoting
  the empty-string SHA-256 hash, unused in the error message).
  D-082 (Roberto: R1 "ok, fissa il bug", M1-M3 OK): ALL FIXED —
  the amask log now prints m.amask (L113), @validate_call on the
  factory (L121) + pydantic import, the 2 flagged lines cleaned
  (license-header whitespace stays, D-078 M3 scope), the orphan
  comment removed — module CLOSED (file 123 → 125 lines; probe
  re-pinned to 44 checks, 0 mismatches).
- test_lm_worker_features.py: Roberto's file, copied from the
  original repo with the FEATURES enablement (f051dd3; suite
  498 → 499); analyzed 2026-08-31 (session 22, D-081,
  docs/src/twolm/test/test_lm_worker_features.md): 1 class /
  1 test / no PERF; green on first run with the live DB. The
  setUp patches stdout, mkdtemps under ./build/tmp, builds the
  LogisticModel on the rlm_00.json fixture (Verbosity.LOW) and
  moves to POSITIONS (the DB-dependent part); the test pins
  feature_set None → the FEATURES move (step 3) → non-None.
  OPEN: T1 (not the D-065 idiom — CWD-relative mkdtemp, no
  setUpClass mkdir, no TemporaryDirectory, the tearDown rmtree
  not in a finally), T2 (NO SKIP_REGAB_DB gate — the setUp hits
  the DB via POSITIONS; a no-DB environment with the canonical
  gated command would ERROR instead of skip), T3 (dead
  `from pathlib import Path` import), T4 (header grammar),
  M1 (the misleading "FEATURES depends on the configuration
  loaded there" comment — the dependency is the CONFIG level),
  M2 (trailing whitespace L90 + 3 whitespace-only lines).
  Uncovered (report-only): the feature set content (probe
  V4-V8 pins it), the _down path (probe B12), the zero-feature
  guard (probe B11), the R1 log defect (DEBUG — invisible at
  the test's Verbosity.LOW). D-082 (Roberto: T1-T4 + M2 OK +
  his own proposal "Dovremmo avere almeno 1 goldentest che
  controlla il contenuto di feature_set in context. Puoi
  aggiungerlo?"): T1 FIXED (the D-065 idiom), T2 FIXED (the
  SKIP_REGAB_DB gate — both tests now DB-gated), T3 RESOLVED BY
  T1 (the Path import now load-bearing), T4 FIXED (header
  grammar + DB/gate run note), M2 FIXED (whitespace clean); M1
  LEFT AS-IS per Roberto — he wants to evaluate moving the
  FEATURES level BEFORE POSITIONS: recorded at I-012. NEW
  test_feature_set_content_golden (L118-167): name
  'NoNameFeatureSet', the 3 golden hash literals (fs
  453e918a...5a159, mset 2e553593...08a94 — the literal
  test_mobility pins, pset 04d52f12...c18), the intercept, the
  3 mobilities sorted (mask, amask) [ALMC, LMC, DLMC], the 2
  patterns sorted mask [EDGE, ELLE], the feature order + counts
  (6 features, n_instances 16) — test campaign CLOSED (file 97
  → 169 lines, 1 → 2 tests).
- rlm_indexes.py: brought in by Roberto in a323e0f (the
  INDEXES line-by-line step 5 — the pipeline now runs 5 active
  levels; the only other lines the commit touched were the
  logistic_model import L44 + worker-list entry); analyzed
  2026-08-31 (session 23, D-083, docs/src/twolm/rlm_indexes.md):
  the 5th-level data object — ReversiLogisticModelIndexes (the
  2-D uint32 index matrix + rds_checksum + feature_set_hash,
  stored by reference) + the 4 public functions (store:
  header/description + version 1 + 2 strings + the array; load:
  the binio sidecar verify + the 3 RuntimeError gates; compute:
  the no-validation documented by the source — the RLMContext
  annotation is unresolvable by pydantic, the import sits under
  TYPE_CHECKING; is_cache_consistent: the 2-field metadata
  compare) + the duck-typed compute_sha3_256_hash =
  sha3_256(indexes.tobytes()). The SECOND cache_manager consumer
  in the pipeline after POSITIONS (D-079): the flat
  rlmwf_04_INDEXES.dat + .SHA3-256 materialize (unlike
  FEATURES), the data checksum vs the file checksum
  distinction, the cross-run round-trip, the _down clearing of
  BOTH context attributes. 12 verified facts V1-V12 (probe
  scratch/verify_rlm_indexes.py, re-pinned D-084: 56 checks,
  0 mismatches). D-084 (Roberto: "Sì fai tutto, mi è tutto
  chiaro"): R1 + M1-M4 + M6 ALL FIXED — the store docstring no
  longer promises the checksum (the regab D-080 Note: the
  sidecar is written by cache_manager), the 5 dead imports
  removed (IntEnum, Protocol, BeforeValidator, AfterValidator,
  Field), the "togheter" typo fixed, the 4 non-comment
  trailing-whitespace lines stripped, the version gate compares
  expected_version, __repr__ added (the 5th @validate_call
  decorator — house style as in pattern.py / mobility.py);
  M5 left as-is (by design — the documented circular-import
  constraint, source L166). Module CLOSED (file 180 → 190
  lines).
- lm_worker_indexes.py: brought in + enabled by Roberto in
  a323e0f (the line-by-line step 5); analyzed 2026-08-31
  (session 23, D-083, docs/src/twolm/lm_worker_indexes.md):
  the cache-consuming level — the uniform 7-kwargs
  cache_manager wiring (the injected full-path closure — flat
  rlmwf_04_INDEXES.dat via the D-078 machine-level naming —
  is_allowed = ctx.use_cache, load/store/validate/compute fns,
  logger_fn), no per-worker naming code; _down clears BOTH
  ctx.rlm_indexes and ctx.rlm_indexes_checksum. 8 verified
  facts V1-V8 (probe tiers C+D, live DB: step 4 / "INDEXES",
  flat files with NO rlmwf_03_FEATURES*, the (N, 16) uint32
  identity vs the independent recompute, the cross-run cache
  hit + no heavy computation, the clearing). D-084 (Roberto:
  "Sì fai tutto"): M1-M3 ALL FIXED — @validate_call on the
  factory + the pydantic import (the D-080 M1 / D-082 M1
  pattern), the 2 non-comment trailing-whitespace lines
  stripped, load_fn = lambda path:
  rlm_indexes_load_from_file(path, checksum=False) (the
  redundant sidecar re-verification is gone, the D-080 M4
  shape as in POSITIONS). Module CLOSED (file 77 → 80 lines).
- test_rlm_indexes.py: Roberto's file, brought in with a323e0f
  (suite 500 → 515); analyzed 2026-08-31 (session 23, D-083,
  docs/src/twolm/test/test_rlm_indexes.md): 5 classes / 14
  tests / no PERF (13 at analysis); all file I/O mocked (binio
  patched), no temp-dir machinery, no DB. The store/load
  contract fully pinned (exact 4-call sequence + method_calls
  equality, both checksum flags, all 3 RuntimeError messages,
  the by-reference init). D-084 (Roberto: "Sì fai tutto"):
  T1-T5 + M1-M2 ALL FIXED — the dead IndexArray import removed,
  header grammar, the 2 broad assertRaises(Exception) → the
  precise pydantic ValidationError, rds_checksum added to
  test_init_fails_with_invalid_indexes_type (the invalid
  indexes=[[1, 2], [3, 4]] — a list of lists, rejected by the
  NDArray gate — is now the thing under test, as the docstring
  claims), the Italian comment → English, the 19 non-comment
  trailing-whitespace lines stripped, the rds-only-differs
  is_cache_consistent branch now unit-tested (new
  test_is_cache_consistent_returns_false_rds_differs — both
  single-field branches pinned; 13 → 14 tests). Test campaign
  CLOSED (file 287 → 304 lines).
- test_lm_worker_indexes.py: Roberto's file, brought in with
  a323e0f; analyzed 2026-08-31 (session 23, D-083,
  docs/src/twolm/test/test_lm_worker_indexes.md): 1 class / 2
  tests / no PERF; the end-to-end cache round-trip pin (setUp
  → FEATURES on a fresh base dir — DB hit through POSITIONS;
  first run: flat rlmwf_04_INDEXES.dat + .SHA3-256 +
  "Executing heavy computation"; second instance: "Cache
  successfully loaded and validated" + no heavy computation);
  green on first run with the live DB. The dependency comment
  is ACCURATE (in contrast to the test_lm_worker_features M1
  misleading comment). D-084 (Roberto: "Sì fai tutto"):
  T1-T3 + M1 ALL FIXED — the D-065 idiom (CUSTOM_TMP_BASE via
  __file__, setUpClass mkdir, TemporaryDirectory first in
  setUp, defensive tearDown; the CWD-relative mkdtemp + the
  shutil import are gone), the SKIP_REGAB_DB gate at the top of
  setUp (both tests now DB-gated — a no-DB environment skips
  instead of erroring), header grammar + the live-DB / gate
  run note, the 13 non-comment trailing-whitespace lines
  stripped. Test campaign CLOSED (file 137 → 158 lines).
- paths.py + test_paths.py (new, D-085, session 23): Roberto's
  design choice "A" for the TMP-dir clarification — the single
  home of the workspace-root-anchored test paths. WORKSPACE_ROOT
  is derived from the workspace marker (pyproject.toml), not a
  parents[N] level count; CUSTOM_TMP_BASE = <root>/build/tmp
  (the D-065 base). The 6 D-065 test files now import the
  constants (their per-file __file__ derivations are gone), the
  4 lm_worker JSON fixtures are anchored to the same
  WORKSPACE_ROOT (were CWD-relative), test_regab loads .env
  from the explicit root path and its mkdtemp uses the shared
  base. test_paths: 3/0/0 GREEN (no DB). Full discover: 516 →
  519 tests, the 58/17 skip split unchanged, both ways GREEN.
- rlm_wmaps.py + lm_worker_wmaps.py (new, WMAPS bring-in,
  session 23): Roberto's commit 73b4342 activated the 6th
  pipeline level (the lm_worker_wmaps import + list entry
  uncommented; RLMContext's 7 Wmaps fields were pre-declared).
  rlm_wmaps: the 6-array weight-maps object (feature_w_ranges /
  iwmap_feature_offset / iwmap / wmap / wmap_fallback / w) +
  store / load / compute / is_cache_consistent + the duck-typed
  compute_sha3_256_hash; the 3rd cache_manager consumer.
  lm_worker_wmaps: the uniform 7-kwargs cache wiring (flat
  rlmwf_05_WMAPS.dat, D-078). Analysis D-086 (probe
  scratch/verify_wmaps.py, 60 checks, 0 mismatches — the golden
  literals re-derived E0-E9); fix campaign D-087 CLOSED
  (Roberto: "Procedi su tutto"): dead accumulate import,
  no-validation note (rlm_indexes style), 23 + 4 ws lines,
  factory @validate_call + pydantic, load_fn checksum=False,
  _down wmaps_obj_checksum — all fixed; R1 RESOLVED as no-guard
  (Roberto's contract: the indexes are unsigned 0..
  n_configurations−1, never −1 — documented in the compute
  docstring).
- test_rlm_wmaps.py + test_lm_worker_wmaps.py (new, WMAPS
  bring-in, session 23): 6 + 3 tests (no-DB handcrafted-mock
  pins + live-DB round-trip + the rlm_01 golden content — 21
  weights, independently re-derived GREEN). The D-085 idiom
  APPLIED per Roberto's instruction (both files). Fix campaign
  D-087 CLOSED: the missing SKIP_REGAB_DB gate added (worker
  test — now 3/0/3 under the gate), the header DB claim
  corrected (rlm_wmaps test — file is DB-free), dead StringIO +
  patch imports, the leftover Italian generation comment, 21 +
  20 ws lines — all fixed; T10 coverage batch added (+5 IO
  pins: golden hash 12c3344e…, sidecar valid/mismatch, wrong
  description, version mismatch; + TestRLMWmapsInit 2 tests):
  6 → 13 tests (13/0/0) + 3/0/0.

- Re-verification pass (2026-08-29, session 17): all three
  integration modules (binio, regab, opt_lbfgs) re-checked — every
  T-item fix in place, all suites GREEN (45/37/13), stale docs
  corrected (line numbers, identifiers, FIXED status); D-051 updated
  + D-052/D-053 written into decisions.md.
- The plan (confirmed by Roberto, 2026-08-28, session close): port
  the ENTIRE pipeline — the original repo brought in module by
  module, this staging workspace's work — with VERIFIED code and
  COMPLETE tests as the goal: a solid base before further evolution
  (Roberto's list of future changes is out of scope for the port).
  Done so far: board.py (2026-08-26, proven complete game kernel),
  pattern.py, mobility.py, feature.py (20/0/1), binio.py (45/0/0),
  regab.py (37/0/0), opt_lbfgs.py (13/0/0), state_machine.py
  (49/0/0, closed 2026-08-29 session 19, D-057..D-070) —
  re-verified all three integration modules 2026-08-29
  (session 17). The game-loop module is NOT in the plan
  (I-005 resolved).
- Sources live in the `twolm` package under src/ (D-008); unit tests
  in src/twolm/test/. Environment: .venv with the pinned deps (D-010,
  D-051, D-052), twolm installed editable (D-011). Git repo on
  master (D-003). Collaboration memory: AGENTS.md (auto-injected) +
  this file + notes/ (journal in rotating volumes
  log_NNN.md, format rules in log_rules.md — D-055).

## Next steps

- Parked (no action planned): test_pattern T18 noted-only (np.uint8
  3**n_squares overflow — external expressions must cast to int);
  test_pattern M1 (stale PatternSet Raises docstring) — awaiting
  Roberto's go-ahead.
- Reported-only: test_board.py header grammar nit (the
  'environmeant' typo itself fixed 2026-08-29, D-050).
- Feed notes/ideas.md with Roberto's future-evolution ideas.
- Done (2026-08-30): cache_manager campaign batch 2 (D-072) — R3
  resolved (binio sidecar API adopted), T6 fixed, suite 21/0/0;
  CACHE_MANAGER module CLOSED (R1-R4, M1-M3, T1-T7; T8 report-only).
- Done (2026-08-30): logistic_model fix campaign batch 1 (D-074) —
  R1-R3 resolved (D-069 rename, str | None, @validate_call both
  facades with base_model R1), M1-M4 fixed; M5 + base_model M1
  left open; suite 5/0/0, full discover 473/52 GREEN.
- Done (2026-08-30): logistic_model fix campaign batch 2 (D-075) —
  M5 fixed (dead `field` import removed), base_model M1 fixed
  (__all__ added — base_model module now fully closed), test batch
  T1/T2/T4/T5 fixed (T3 intentional, T6 report-only): suite
  5/0/0 → 13/0/0, full discover 473 → 481/52 GREEN. The
  logistic_model + base_model campaigns are CLOSED (all R/M
  resolved).
- Done (2026-08-30): lm_worker_config fix campaign (D-078,
  Roberto's calls on D-077): R2 resolved AT MACHINE LEVEL (the
  injected cache-path closure concatenates the prefix verbatim —
  filename-prefix semantics, one fix for all workers; replaces the
  D-069 M8 join, 2 pins re-pinned), R3 precise OS exception types,
  M1-M5 fixed (M5 keep per R1), T1-T4 fixed in test_lm_worker_
  config; R1 deferred to the full-pipeline review (the
  "storicizzazione" idea recorded at I-011); suite 496/52 GREEN,
  build/tmp clean, 35-check probe 0 mismatches.
- Done (2026-08-30, session 22): POSITIONS line-by-line
  enablement (601de87, Roberto: uncomment lm_worker_positions() +
  copy the related test — the pipeline now runs 3 active levels) +
  D-079 analysis of lm_worker_positions + rlm_config_schemas
  (49-check probe, 0 mismatches; 3 new mirror docs; the probe
  finalized with the house cleanup convention). OPEN awaiting
  Roberto's call: lm_worker_positions R1 + M1-M4 (+ the
  regab_store docstring cross-ref note), rlm_config_schemas
  R1 + M1-M4, test_lm_worker_positions T1-T4. Suite 498/52
  GREEN, build/tmp clean.
- Done (2026-08-30, session 22): D-080 fix campaign (Roberto:
  "correggile tutte" / "fai tutto anche qui") — lm_worker_
  positions R1 + M1-M4 + the regab_store cross-ref note,
  rlm_config_schemas R1 + M1-M4, test_lm_worker_positions T1-T4
  all FIXED; the probe re-pinned (51 checks, 0 mismatches);
  suites 498/0/54 gated + 498 run / 17 skipped ungated (live
  DB), build/tmp clean.
- Done (2026-08-31, session 22): FEATURES line-by-line
  enablement (f051dd3, Roberto: uncomment lm_worker_features()
  + add the module and the test — the pipeline now runs 4 active
  levels) + D-081 analysis (42-check probe, 0 mismatches; 2 new
  mirror docs; the stale session-21 logistic_model probe
  re-pinned — 35 checks, 0 mismatches). OPEN awaiting Roberto's
  call: lm_worker_features R1 + M1-M3, test_lm_worker_features
  T1-T4 + M1-M2. Suite 499/0/54 gated GREEN, build/tmp clean.
- Done (2026-08-31, session 22): D-082 fix campaign (Roberto:
  R1 "ok, fissa il bug", M1-M3 OK, test T1-T4 + M2 OK + his own
  proposal for the golden content test) — lm_worker_features
  R1 + M1-M3 FIXED (module CLOSED), test T1-T4 + M2 FIXED,
  M1 left as-is (I-012: evaluate moving FEATURES before
  POSITIONS), test_feature_set_content_golden added (3 hash
  literals + full content pin, per Roberto); probe re-pinned
  (44 checks, 0 mismatches); suites 500/0/56 gated + 500 run /
  17 skipped ungated (live DB), build/tmp clean.
- Done (2026-08-31, session 23): INDEXES line-by-line
  enablement (a323e0f, Roberto: lm_worker_indexes + rlm_indexes +
  the two tests, the worker uncommented — the pipeline now runs 5
  active levels) + D-083 analysis (47-check probe, 0 mismatches;
  4 new mirror docs; the stale session-22 logistic_model probe
  re-pinned — 35 checks, 0 mismatches). Suites 515/0/56 gated +
  515 run / 17 skipped ungated (live DB), build/tmp clean.
- Done (2026-08-31, session 23): D-084 fix campaign (Roberto:
  "Sì fai tutto, mi è tutto chiaro" — the full approved R/M/T
  table) — rlm_indexes R1 + M1-M4 + M6 FIXED (M5 left as-is, by
  design — the documented circular-import constraint),
  lm_worker_indexes M1-M3 FIXED, test_rlm_indexes T1-T5 + M1-M2
  FIXED (the rds-only-differs is_cache_consistent branch now
  unit-tested — 13 → 14 tests), test_lm_worker_indexes T1-T3 +
  M1 FIXED (D-065 idiom + SKIP_REGAB_DB gate + header +
  whitespace); probe re-pinned (56 checks, 0 mismatches — the
  9 C-tier live-DB checks included); 4 mirror docs re-stated to
  the FIXED state (campaign CLOSED); suites 515 → 516 tests,
  56 → 58 skipped gated (the 2 lm_worker_indexes tests now
  skip), 516/0/58 gated + 516 run / 17 skipped ungated (live
  DB), build/tmp clean.
- Done (2026-08-31, session 23): D-085 TMP-dir design (Roberto:
  "sono anche io per la A, con inclusi i JSON e .env") — new
  twolm.test.paths module (marker-based WORKSPACE_ROOT +
  CUSTOM_TMP_BASE) + test_paths (3 tests); the 6 D-065 test
  files re-anchored (imports, per-file derivations gone), the 7
  json_config lines + the test_regab .env load + its mkdtemp
  anchored to WORKSPACE_ROOT; 2 probes re-pinned (rlm_indexes
  E1/E2, features C1/C3/C5 — 0 mismatches); 2 new mirror docs +
  7 test docs updated; suites 516 → 519 tests, 519/0/58 gated +
  519 run / 17 skipped ungated (live DB), build/tmp clean.
- Done (2026-08-31, session 23): D-086 WMAPS bring-in +
  D-087 fix campaign (Roberto's commit 73b4342 — lm_worker_
  wmaps + rlm_wmaps + rlm_01.json + 2 test files; 519 → 535
  tests, 535/0/61 gated + 535 run / 17 skipped ungated,
  build/tmp clean): analysis D-086 (probe verify_wmaps.py 60
  checks 0 mismatches, golden re-derived E0-E9); the D-085
  paths idiom APPLIED (Roberto's explicit instruction); fix
  campaign D-087 (Roberto: "Procedi su tutto") CLOSED — T1-T10
  all fixed (gate, header, dead imports, Italian comment,
  @validate_call ×2, load_fn checksum=False, _down checksum,
  68 ws lines, +7 new tests), R1 resolved as no-guard by
  Roberto's pindexes-density contract (documented in the
  source).
- Next: the pipeline grows one commented line at a time
  (uncommenting lm_worker_wmaps + restoring the last muted
  test _test_move_to_step_by_string — a test file change,
  Roberto's call) + the I-012 evaluation (FEATURES before
  POSITIONS).

## Index

- docs/src/twolm/board.md — board.py analysis (distilled + full
  review in appendix; R1-R5 resolved 2026-08-26/29)
- docs/src/twolm/pattern.md — pattern.py analysis (R1-R8 resolved:
  D-020, D-021, D-022; little-endian-only platform note; minor sweep
  complete 19/19: D-023/D-024/D-025 + hygiene/API fixes; Burnside
  attributes D-032)
- docs/src/twolm/test/test_board.md — test_board.py analysis
  (coverage by area, verified values, 11 defects, completeness
  verdict + priorities)
- docs/src/twolm/test/test_pattern.md — test_pattern.py analysis
  (coverage by area, 21 verified facts, defects T1-T19 (T17/T19
  found during the campaign), completeness verdict + P0/P1/P2
  priorities)
- docs/src/twolm/mobility.md — mobility.py analysis (feature index
  formula, n_configurations semantics, sorted-order columns,
  verified V1-V8, R1-R6 applied D-035, minor M1-M5 disposed D-036)
- docs/src/twolm/test/test_mobility.md — test_mobility.py analysis
  (coverage by area, 13 verified facts, defects T1-T9, completeness
  verdict + P0/P1/P2 priorities)
- docs/src/twolm/feature.md — feature.py analysis (first pipeline
  integration module: Feature factories + blocked __new__, FeatureSet
  composition/hash/column layout, verified V1-V8, R1-R4 D-038,
  M1-M4 D-039..D-042 — all disposed)
- docs/src/twolm/test/test_feature.md — test_feature.py analysis
  (coverage by area, 9 verified facts W1-W9, defects T1-T9,
  completeness verdict + P1/P2 priorities; T campaign CLOSED
  D-043..D-050, suite 20/0/1 GREEN)
- docs/src/twolm/binio.md — binio.py analysis (MAGIC framing +
  SHA3-256 sidecar + LZ4 compression; 15 verified facts V1-V15,
  T1-T4 applied D-051, suite 45/0/0 GREEN)
- docs/src/twolm/test/test_binio.md — test_binio.py +
  test_usage_binio.py analysis (12 classes, 45 tests after T4,
  coverage by area)
- docs/src/twolm/regab.md — regab.py analysis (psycopg2 DB access +
  RegabDataSet + binio serialization; 5 verified facts, T1-T7
  applied D-052, suite 37/0/0 GREEN; D-080 cross-ref: the store
  docstring + API-table row corrected — the sidecar is
  cache_manager's)
- docs/src/twolm/test/test_regab.md — test_regab.py analysis
  (coverage by area, T5-T7 applied D-052, suite 37/0/0 GREEN)
- docs/src/twolm/opt_lbfgs.md — opt_lbfgs.py analysis (L-BFGS:
  strong Wolfe line search + two-loop recursion + warm-start; 5
  verified facts, T1-T7 + 9 new tests D-053, suite 13/0/0 GREEN)
- docs/src/twolm/test/test_opt_lbfgs.md — test_opt_lbfgs.py analysis
  (coverage by area, T7 + 9 new tests D-053, suite 13/0/0 GREEN)
- docs/src/twolm/state_machine.md — state_machine.py analysis (generic
  pipeline orchestrator; 17 verified facts V1-V17; R1 fixed D-057
  (VERY_LOW=4, NONE=5), R2 fixed D-058 (frozen LogEntry dataclass +
  asdict), R3 sentinel documented + pinned D-059, R4 documented +
  pinned D-060, R5 resolved D-061 (unique case-insensitive worker
  names enforced in __init__, closes M12), T2 coverage D-062 (context
  injection pinned; M8 separator contract), T3 goldens D-063 (display
  layer pinned), T4 coverage D-064 (move_to_last pinned), T5 D-065
  (CSV test rewritten; build/tmp house rule), T7 pinned D-066
  (bool/np.int64 edge), T8 + T9 pinned D-067 (current_worker_name +
  StepMove fields; all T items closed), M-sweep D-068 + D-069 +
  D-070 (M1-M12 all disposed — M6 print cleanup + display goldens
  rewritten, M9 as-is, redesign parked at I-010); suite 49/0/0
  GREEN)
- docs/src/twolm/test/test_state_machine.md — test_state_machine.py
  analysis (49 tests, expectations re-derived, T1 fixed D-057,
  TestLogEntry + sentinel pin + retry pin + 2 duplicate-name + 7
  context-injection + 3 display-goldens + 3 move_to_last + 2
  bool/np.int64 + 5 current_worker_name/StepMove pin tests added
  D-058/D-059/D-060/D-061/D-062/D-063/D-064/D-066/D-067, CSV test
  rewritten D-065, 4 M-sweep pins D-068 + M-sweep batch 2 D-069
  (bool rejection, constructor ValidationErrors, Path prefix join)
  + M6 display goldens rewritten in place D-070,
  ALL T items resolved, P0/P1/P2 priorities proposed)
- docs/src/twolm/cache_manager.md — cache_manager.py analysis +
  D-071/D-072 fix campaign (4-step load-or-compute cache pipeline
  + duck-typed data checksum; 17 verified facts V1-V17; R1
  intentional + pinned, R2 validate-in-try, R4 @validate_call, M1-M3
  fixed, R3 resolved — binio sidecar API adopted, legacy sidecars
  still verify; suite 21/0/0 GREEN; module CLOSED)
- docs/src/twolm/test/test_cache_manager.md — test_cache_manager.py
  analysis + D-071/D-072 (2 classes / 21 tests; T1-T7 all fixed —
  incl. the full duck-typed hash path; T6 fixed — workspace-root
  artifact base; T8 report-only; module CLOSED)
- docs/src/twolm/base_model.md — base_model.py analysis + D-074/
  D-075 (facade base over StateMachine; pure delegation verified,
  context identity; R1 @validate_call RESOLVED D-074 with
  logistic_model R3; M1 __all__ FIXED D-075; M2 informational —
  module CLOSED)
- docs/src/twolm/logistic_model.md — logistic_model.py analysis +
  D-074/D-075 + D-081 + D-083 (first domain facade: RLMContext 38
  fields + 15-level pipeline, deliberately partial — 5 active
  levels post a323e0f: CREATED sentinel → CONFIG → POSITIONS →
  FEATURES → INDEXES; 10 verified facts; R1-R3 RESOLVED D-074 —
  D-069 rename, str | None, @validate_call — M1-M4 fixed D-074,
  M5 fixed D-075 — module CLOSED; 35-check probe re-pinned D-081,
  re-pinned D-083 — 5-worker state)
- docs/src/twolm/test/test_logistic_model.md — test_logistic_model.
  py analysis + D-075 (13 active + 2 muted per Roberto; T1/T2/T4/
  T5 fixed — delegation pins, build/tmp base, 7 corner tests, dead
  import removed; T3 intentional, T6 report-only — test campaign
  CLOSED)
- docs/src/twolm/lm_worker_config.md — lm_worker_config.py
  analysis + D-076/D-077/D-078 (CONFIG worker: JSON5 load →
  pydantic → flat checksummed cache rlmwf_01_CONFIG.dat; 35-check
  probe 0 mismatches; D-078: R2 machine-level prefix fix, R3
  precise OS types, M1-M5 fixed, R1 deferred to the full-pipeline
  review — I-011)
- docs/src/twolm/test/test_lm_worker_config.md —
  test_lm_worker_config.py analysis + D-077/D-078 (4 classes / 14
  tests; D-076 path typos + schema-complete payload; D-078 T1-T4
  FIXED — D-065 idiom, ValueError pin, _down reset, bare-hex
  sidecar; T5/T6 report-only)
- docs/src/twolm/lm_worker_positions.md — lm_worker_positions.py
  analysis + D-079/D-080 (first cache_manager consumer in the
  pipeline: 4-step load-or-compute over the regab data set +
  post-processing stats; 13 verified facts V1-V13; R1 + M1-M4
  FIXED D-080 + cross-ref note resolved; suite 2/0/0 GREEN via
  test_lm_worker_positions)
- docs/src/twolm/rlm_config_schemas.md — rlm_config_schemas.py
  analysis + D-079/D-080 (pydantic config domain:
  ReversiLogisticModelConfig over the nested RLMBaseConfig tree,
  Bitboard hex fields; 12 verified facts V1-V12; R1 + M1-M4
  FIXED D-080 — c2>c1 validator, strict status, RLMBaseConfig;
  no dedicated suite)
- docs/src/twolm/test/test_lm_worker_positions.md —
  test_lm_worker_positions.py analysis + D-079/D-080 (1 class /
  2 tests; the end-to-end cache round-trip pin; T1-T4 FIXED
  D-080 — D-065 idiom + SKIP_REGAB_DB gate; suite 2/0/0 GREEN)
- docs/src/twolm/lm_worker_features.md — lm_worker_features.py
  analysis + D-081/D-082 (the first pure-compute level: FeatureSet
  from the cfg, no DB / no cache_manager / no cache file; 13
  verified facts V1-V13; R1 amask log + M1-M3 FIXED D-082 —
  module CLOSED; suite 2/0/0 GREEN via test_lm_worker_features)
- docs/src/twolm/test/test_lm_worker_features.md —
  test_lm_worker_features.py analysis + D-081/D-082 (1 class /
  2 tests; T1-T4 + M2 FIXED D-082 — D-065 idiom + SKIP_REGAB_DB
  gate, M1 as-is → I-012; the golden content test added per
  Roberto — 3 hash literals + full pin; suite 2/0/0 GREEN)
- docs/src/twolm/rlm_indexes.md — rlm_indexes.py analysis +
  D-083/D-084 (the 5th-level data object: index matrix +
  rds_checksum + feature_set_hash, by reference; the 4 public
  functions + the duck-typed compute_sha3_256_hash; second
  cache_manager consumer in the pipeline; 12 verified facts V1-
  V12, 56-check probe 0 mismatches (re-pinned D-084); R1 + M1-
  M4 + M6 FIXED D-084, M5 as-is by design, __repr__ added —
  module CLOSED; suite 14/0/0 GREEN via test_rlm_indexes)
- docs/src/twolm/lm_worker_indexes.md — lm_worker_indexes.py
  analysis + D-083/D-084 (the cache-consuming level: uniform
  7-kwargs cache_manager wiring, flat rlmwf_04_INDEXES.dat via
  the D-078 machine-level naming; 8 verified facts V1-V8; M1-M3
  FIXED D-084 — factory @validate_call, whitespace, load_fn
  checksum=False — module CLOSED; suite 2/0/0 GREEN via
  test_lm_worker_indexes, 2 DB-gated)
- docs/src/twolm/test/test_rlm_indexes.md — test_rlm_indexes.py
  analysis + D-083/D-084 (5 classes / 14 tests; all file I/O
  mocked, no temp dirs, no DB; store/load contract fully pinned;
  T1-T5 + M1-M2 FIXED D-084 — incl. the rds_checksum added to
  test_init_fails_with_invalid_indexes_type + the new rds-only-
  differs is_cache_consistent test — test campaign CLOSED;
  suite 14/0/0 GREEN)
- docs/src/twolm/test/test_lm_worker_indexes.md —
  test_lm_worker_indexes.py analysis + D-083/D-084 (1 class /
  2 tests; the end-to-end cache round-trip pin; T1-T3 + M1
  FIXED D-084 — D-065 idiom, SKIP_REGAB_DB gate, header
  grammar, whitespace — test campaign CLOSED; suite 2/0/0
  GREEN, 2 DB-gated)
- docs/src/twolm/test/paths.md —
  paths.py (D-085): the shared workspace-root-anchored test
  paths (marker-based WORKSPACE_ROOT + CUSTOM_TMP_BASE)
- docs/src/twolm/test/test_paths.md —
  test_paths.py (D-085): 3/0/0, no DB — pins the constants
- notes/naming.md — canonical board naming convention (row/column,
  D-013; D8 symmetries, D-014)
- notes/decisions.md — decisions log (D-NNN; D-001…D-087)
- notes/ideas.md — future backlog (I-NNN)
- notes/log_rules.md — session-journal format rules (rigid; global session numbering; volume rotation: 25 sessions / 2000 lines per volume, only at session boundaries)
- notes/log_000.md — session journal, volume 000 (sessions 1–..., open)
