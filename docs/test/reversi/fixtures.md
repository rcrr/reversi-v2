# test/reversi/fixtures.py
The rebuildable LM test fixtures helper (D-671): the functions that BUILD, CLEAN and GATE the
sticky `ModelWeights` artifacts the test modules consume from disk. A fixture is "a bit more
sticky" than the transient setUp-built artifacts: it is built ONCE (a seconds-long full
pipeline run), lives under `build/tmp/fixtures/` (git-ignored, the `build/` pattern) for
sessions of weeks, and is rebuilt on demand. The ec20 member is in place; the set is designed
for the multi-ply evaluation-function work (the depth ladder: positions at A = ec20 over
models at B = ec20…16 → depths 0…4) — the other members are replicated once the ec20 round
proves the full cycle.

## API

| name | contract |
|---|---|
| `FIXTURE_ROOT` / `FIXTURE_CONFIG_DIR` | module constants: `build/tmp/fixtures` (artifacts, git-ignored) / `test/reversi/data` (the committed config sources) |
| `lm_fixture_config_path(name)` | `test/reversi/data/<name>.json` |
| `lm_fixture_dir(name)` | `build/tmp/fixtures/<name>` (the pipeline base_dir of the build) |
| `lm_fixture_model_path(name)` | `build/tmp/fixtures/<name>/<name>.dat` (the single self-verifying artifact) |
| `clean_lm_fixture(name)` | removes the whole fixture directory (idempotent: a missing dir is a no-op) |
| `create_lm_fixture(name, force_rebuild=False)` | builds the fixture if missing (idempotent: an existing model file short-circuits, no pipeline run); `force_rebuild` cleans first. Runs the standard worker chain STOPPED at the CLIENT_CHECK level (SAVE + the integrity gate included; PLOT + FINAL_LOG_PRINT skipped). Returns the model path; `ValueError` on a missing config |
| `require_lm_fixture(name)` | the CONSUMER GATE: the model path, or a `RuntimeError` naming the exact build command (`python -m test.reversi.fixtures create <name>`) — a missing fixture is a local state to fix, not an environment limitation |

## Architecture

- CLI: `python -m test.reversi.fixtures create|clean <name>… [--force]` (a thin loop over the
  functions; the same calls a test or a person makes).
- The build is the STANDARD pipeline entry, driven from Python: `LogisticModel(config).
  move_to_step('CLIENT_CHECK')` — the config's `target_level` field is NOT wired to any entry
  (the `_configured_target_level` reader is dead code), so the stop is explicit in the helper.
  The fixture config additionally carries `plot.enable = false` (the master switch) — the
  double protection is deliberate.
- The CONFIG worker REQUIRES the base dir to exist (it validates, it does not create) —
  `create_lm_fixture` mkdirs it before the run.
- The artifact is a SINGLE self-verifying file (the sidecar record is retired: the sha3_256
  fingerprint is embedded in the model file and `model_weights_read_file` checks it on every
  load) — so presence is "the .dat exists" and integrity is enforced at consumption; a
  corrupt file surfaces as a checksum error at load, and the remedy is a `--force` rebuild.
- No format-versioning intelligence by design: if the `ModelWeights` format changes, the
  remedy is a manual clean + rebuild of the affected fixtures.

## The fixture set (the ec20 member in place)

- `rlm_fixture_simple_ec20` — the rlm_04 config (FULL corpus: `tst_regab` batch 6 CMR/CMS,
  validation batch 5; intercept + EDGE + LMC feature set; cut 10, clipping 0.01, ridge
  0.01) with: `regab_allow_duplicate = false`, `plot.enable = false`, `base_dir` =
  `build/tmp/fixtures/rlm_fixture_simple_ec20`, `output` = `rlm_fixture_simple_ec20.dat`, a
  clear name + description. Built in ~20 s; the CLIENT_CHECK gate passes (18 932 validation
  residuals, max difference 0.000e+00); the saved model loads with `ec = 20`, `w_dense`
  (6 627,) — the same shape class as the rlm_04 production models.

## Verified invariants

Pinned by `test_fixtures.py` (12 tests, all STATIC — no pipeline run, no DB, no artifact
required): the three path helpers derive the house layout; the ec20 config carries the
fixture contract (identity, the output location, `regab_allow_duplicate = false`,
`plot.enable = false`, the rlm_04-inherited training sections — parsed with json5, the
pipeline's own loader, because the house .json data files carry the comment header + the
trailing commas); `require_lm_fixture` returns the path when present and names the exact
build command + the missing model path in the `RuntimeError` when absent; `create_lm_fixture`
raises `ValueError` on a missing config and SHORT-CIRCUITS (no pipeline run — the
`LogisticModel` construction is mocked to a sentinel) when the artifact is present.

## Conventions

- The fixtures are consumed TIER-AGNOSTIC (the fast suite included): they are sticky
  workspace state, not a LONG-tier prerequisite. A fresh clone without the build gets the
  actionable `RuntimeError`, not a silent skip.
- The build itself is NOT in any test suite: it is a manual, seconds-long operation (DB
  required), proven by the first consumer.
