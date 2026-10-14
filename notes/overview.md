# overview.md — entry point

## Format rules

The rigid format rules for this file live in notes/overview\_rules.md. Consult it before editing.

## Project

This workspace is dedicated to the research and development of evaluation functions for Reversi positions. The methods
employed focus on machine learning techniques that leverage solved positions generated from random gameplay paths.

The Machine Learning pipeline is developed by defining a set of observable features within the game positions and a
training set, from which the observed values are extracted as categorical indices. These data are then utilized in a
logistic regression model, minimizing the sum of squared residuals between the actual game values in the training set
and those computed by the evaluation function. The resulting weights, combined with the selected feature set, ultimately
define the evaluation function.

## Environment

- Venv: `.venv/` (gitignored), Python 3.14.4.
- Packaging: `pyproject.toml` (setuptools, src layout) with the `reversi` package installed editable in .venv —
  `import reversi` works without PYTHONPATH, resolving to src/.
- Dependencies (pyproject.toml): numpy ≥ 2.0 (bitboards / structured dtypes), pydantic ≥ 2 (@validate\_call), numba
  ≥ 0.60 (njit / prange / overload; pulls llvmlite), lz4 (binio), psycopg2 / pandas / python-dotenv (regab), json5 (the
  LM configs), scipy (gradient / ANOVA / plot), matplotlib (the PLOT step).
- Test command: `./run_utests.sh` (the canonical runner; tiers: default fast ~17 s, LONG=1, VLONG=1, VVLONG=1 ~3.5 min
  incl. the A2050 chain and implies LONG, VLONG; PERF=1 adds the print-only perf tests). The standard pre-commit run is
  `LONG=1 ./run_utests.sh`; VLONG=1 only when useful. A single module:
  `.venv/bin/python -m unittest test.reversi[.zone].<module>` (the zones: lm, tools). The DB-gated suites (test\_regab +
  the worker suites) need a live PostgreSQL + .env, or `SKIP_REGAB_DB=1` to skip the DB tests. The runner is unittest by
  design (pytest is not a dependency).
- Probes: tracked under probes/ (hub: verify\_logistic\_model.py owns the pipeline-wide state; rules:
  notes/probe\_rules.md).
- Workspace utils: wsutils/ — the workspace utilities (the notes/docs format re-wrapper, the source prose re-wrapper,
  the mirror-doc auditor, the suite counter; rules: notes/wsutils.md).
- Mirror docs: docs/ mirrors the tracked sources one-to-one — every source and test file has its doc, and the Doc column
  of the two tables is the index (format: notes/docs\_rules.md). The user-facing, non-mirror docs live in the
  `docs/user/` zone (docs\_rules.md §8).
- Scratch: scratch/ is the disposable session area — gitignored, never tracked, nothing permanent goes there.
- Governance: all the governance files (the active rules, the decisions log, the session journal, the ideas, the format
  rules, the domain vocabulary, the design principles) live in notes/ — the Index below is their registry.

## Current state

- The 19-level pipeline is live and green (all tests are ok): the ML chain from CONFIG up to FINAL\_LOG\_PRINT.
- The LM facade is the pipeline's script entry:
  `python -m reversi.lm.logistic_model <config.json> [--verbosity {high,moderate,standard,low,very_low,none}]` (default
  `standard`), from the workspace root; the stop is target-driven — `run(target_level=…)` runs CONFIG first, then stops
  at the argument / `cfg.target_level` / the last step.

## Next steps

- The MOBILITY wave is CLOSED (D-544 the rework → D-545 the VVLONG completion → D-546 the definition precision
  → D-548/D-549 the print discipline): the A2050 verification reproduced the pair's 12.47 in the new (mask, side)
  format.
- The PUBLISH steps 4–5 (the secret scan, the final suite, the first push to rcrr/reversi-v2 — Roberto executes, the
  agent advises).
- Pending Roberto's call: the R-595/R-600 rename + rule (the 4 uncommitted files: rules.md, wsutils.md, the header
  audit, the pre-commit hook).

## Source files

| File | State | Doc |
| --- | --- | --- |
| src/reversi/base\_model.py | complete | [docs/src/reversi/base\_model.md](docs/src/reversi/base\_model.md) |
| src/reversi/board.py | complete | [docs/src/reversi/board.md](docs/src/reversi/board.md) |
| src/reversi/feature.py | complete | [docs/src/reversi/feature.md](docs/src/reversi/feature.md) |
| src/reversi/index.py | complete | [docs/src/reversi/index.md](docs/src/reversi/index.md) |
| src/reversi/lm/client.py | complete | [docs/src/reversi/lm/client.md](docs/src/reversi/lm/client.md) |
| src/reversi/lm/hlp\_analytics.py | complete | [docs/src/reversi/lm/hlp\_analytics.md](docs/src/reversi/lm/hlp\_analytics.md) |
| src/reversi/lm/hlp\_anova.py | complete | [docs/src/reversi/lm/hlp\_anova.md](docs/src/reversi/lm/hlp\_anova.md) |
| src/reversi/lm/hlp\_config\_schemas.py | complete | [docs/src/reversi/lm/hlp\_config\_schemas.md](docs/src/reversi/lm/hlp\_config\_schemas.md) |
| src/reversi/lm/hlp\_design\_matrix.py | complete | [docs/src/reversi/lm/hlp\_design\_matrix.md](docs/src/reversi/lm/hlp\_design\_matrix.md) |
| src/reversi/lm/hlp\_final\_log\_print.py | complete | [docs/src/reversi/lm/hlp\_final\_log\_print.md](docs/src/reversi/lm/hlp\_final\_log\_print.md) |
| src/reversi/lm/hlp\_generate.py | complete | [docs/src/reversi/lm/hlp\_generate.md](docs/src/reversi/lm/hlp\_generate.md) |
| src/reversi/lm/hlp\_gradient.py | complete | [docs/src/reversi/lm/hlp\_gradient.md](docs/src/reversi/lm/hlp\_gradient.md) |
| src/reversi/lm/hlp\_indexes.py | complete | [docs/src/reversi/lm/hlp\_indexes.md](docs/src/reversi/lm/hlp\_indexes.md) |
| src/reversi/lm/hlp\_optimize.py | complete | [docs/src/reversi/lm/hlp\_optimize.md](docs/src/reversi/lm/hlp\_optimize.md) |
| src/reversi/lm/hlp\_plot.py | complete | [docs/src/reversi/lm/hlp\_plot.md](docs/src/reversi/lm/hlp\_plot.md) |
| src/reversi/lm/hlp\_su\_analysis.py | complete | [docs/src/reversi/lm/hlp\_su\_analysis.md](docs/src/reversi/lm/hlp\_su\_analysis.md) |
| src/reversi/lm/hlp\_validate.py | complete | [docs/src/reversi/lm/hlp\_validate.md](docs/src/reversi/lm/hlp\_validate.md) |
| src/reversi/lm/hlp\_wmaps.py | complete | [docs/src/reversi/lm/hlp\_wmaps.md](docs/src/reversi/lm/hlp\_wmaps.md) |
| src/reversi/lm/hlp\_zed.py | complete | [docs/src/reversi/lm/hlp\_zed.md](docs/src/reversi/lm/hlp\_zed.md) |
| src/reversi/lm/logistic\_model.py | complete | [docs/src/reversi/lm/logistic\_model.md](docs/src/reversi/lm/logistic\_model.md) |
| src/reversi/lm/model\_weights.py | complete | [docs/src/reversi/lm/model\_weights.md](docs/src/reversi/lm/model\_weights.md) |
| src/reversi/lm/wrk\_analytics.py | complete | [docs/src/reversi/lm/wrk\_analytics.md](docs/src/reversi/lm/wrk\_analytics.md) |
| src/reversi/lm/wrk\_anova.py | complete | [docs/src/reversi/lm/wrk\_anova.md](docs/src/reversi/lm/wrk\_anova.md) |
| src/reversi/lm/wrk\_client\_check.py | complete | [docs/src/reversi/lm/wrk\_client\_check.md](docs/src/reversi/lm/wrk\_client\_check.md) |
| src/reversi/lm/wrk\_config.py | complete | [docs/src/reversi/lm/wrk\_config.md](docs/src/reversi/lm/wrk\_config.md) |
| src/reversi/lm/wrk\_design\_matrix.py | complete | [docs/src/reversi/lm/wrk\_design\_matrix.md](docs/src/reversi/lm/wrk\_design\_matrix.md) |
| src/reversi/lm/wrk\_features.py | complete | [docs/src/reversi/lm/wrk\_features.md](docs/src/reversi/lm/wrk\_features.md) |
| src/reversi/lm/wrk\_final\_log\_print.py | complete | [docs/src/reversi/lm/wrk\_final\_log\_print.md](docs/src/reversi/lm/wrk\_final\_log\_print.md) |
| src/reversi/lm/wrk\_generate.py | complete | [docs/src/reversi/lm/wrk\_generate.md](docs/src/reversi/lm/wrk\_generate.md) |
| src/reversi/lm/wrk\_gradient.py | complete | [docs/src/reversi/lm/wrk\_gradient.md](docs/src/reversi/lm/wrk\_gradient.md) |
| src/reversi/lm/wrk\_indexes.py | complete | [docs/src/reversi/lm/wrk\_indexes.md](docs/src/reversi/lm/wrk\_indexes.md) |
| src/reversi/lm/wrk\_optimize.py | complete | [docs/src/reversi/lm/wrk\_optimize.md](docs/src/reversi/lm/wrk\_optimize.md) |
| src/reversi/lm/wrk\_plot.py | complete | [docs/src/reversi/lm/wrk\_plot.md](docs/src/reversi/lm/wrk\_plot.md) |
| src/reversi/lm/wrk\_positions.py | complete | [docs/src/reversi/lm/wrk\_positions.md](docs/src/reversi/lm/wrk\_positions.md) |
| src/reversi/lm/wrk\_save.py | complete | [docs/src/reversi/lm/wrk\_save.md](docs/src/reversi/lm/wrk\_save.md) |
| src/reversi/lm/wrk\_su\_analysis.py | complete | [docs/src/reversi/lm/wrk\_su\_analysis.md](docs/src/reversi/lm/wrk\_su\_analysis.md) |
| src/reversi/lm/wrk\_validate.py | complete | [docs/src/reversi/lm/wrk\_validate.md](docs/src/reversi/lm/wrk\_validate.md) |
| src/reversi/lm/wrk\_vld\_positions.py | complete | [docs/src/reversi/lm/wrk\_vld\_positions.md](docs/src/reversi/lm/wrk\_vld\_positions.md) |
| src/reversi/lm/wrk\_wmaps.py | complete | [docs/src/reversi/lm/wrk\_wmaps.md](docs/src/reversi/lm/wrk\_wmaps.md) |
| src/reversi/lm/wrk\_zed.py | complete | [docs/src/reversi/lm/wrk\_zed.md](docs/src/reversi/lm/wrk\_zed.md) |
| src/reversi/mobility.py | complete | [docs/src/reversi/mobility.md](docs/src/reversi/mobility.md) |
| src/reversi/pattern.py | complete | [docs/src/reversi/pattern.md](docs/src/reversi/pattern.md) |
| src/reversi/random\_game.py | complete | [docs/src/reversi/random\_game.md](docs/src/reversi/random\_game.md) |
| src/reversi/regab.py | complete | [docs/src/reversi/regab.md](docs/src/reversi/regab.md) |
| src/reversi/tools/binio.py | complete | [docs/src/reversi/tools/binio.md](docs/src/reversi/tools/binio.md) |
| src/reversi/tools/cache\_manager.py | complete | [docs/src/reversi/tools/cache\_manager.md](docs/src/reversi/tools/cache\_manager.md) |
| src/reversi/tools/opt\_lbfgs.py | complete | [docs/src/reversi/tools/opt\_lbfgs.md](docs/src/reversi/tools/opt\_lbfgs.md) |
| src/reversi/tools/prng.py | complete | [docs/src/reversi/tools/prng.md](docs/src/reversi/tools/prng.md) |
| src/reversi/tools/state\_machine.py | complete | [docs/src/reversi/tools/state\_machine.md](docs/src/reversi/tools/state\_machine.md) |

## Test files

| File | State | Suite/std\_run | Doc |
| --- | --- | --- | --- |
| test/reversi/closecheck.py | complete | 0/0/0/0/0 | [docs/test/reversi/closecheck.md](docs/test/reversi/closecheck.md) |
| test/reversi/lm/test\_client.py | complete | 10/0/1/0/0 | [docs/test/reversi/lm/test\_client.md](docs/test/reversi/lm/test\_client.md) |
| test/reversi/lm/test\_hlp\_anova.py | complete | 18/0/0/0/0 | [docs/test/reversi/lm/test\_hlp\_anova.md](docs/test/reversi/lm/test\_hlp\_anova.md) |
| test/reversi/lm/test\_hlp\_config\_schemas.py | complete | 32/0/0/0/0 | [docs/test/reversi/lm/test\_hlp\_config\_schemas.md](docs/test/reversi/lm/test\_hlp\_config\_schemas.md) |
| test/reversi/lm/test\_hlp\_design\_matrix.py | complete | 16/0/0/0/0 | [docs/test/reversi/lm/test\_hlp\_design\_matrix.md](docs/test/reversi/lm/test\_hlp\_design\_matrix.md) |
| test/reversi/lm/test\_hlp\_generate.py | complete | 18/0/0/0/0 | [docs/test/reversi/lm/test\_hlp\_generate.md](docs/test/reversi/lm/test\_hlp\_generate.md) |
| test/reversi/lm/test\_hlp\_gradient.py | complete | 15/0/0/0/0 | [docs/test/reversi/lm/test\_hlp\_gradient.md](docs/test/reversi/lm/test\_hlp\_gradient.md) |
| test/reversi/lm/test\_hlp\_indexes.py | complete | 15/0/0/0/0 | [docs/test/reversi/lm/test\_hlp\_indexes.md](docs/test/reversi/lm/test\_hlp\_indexes.md) |
| test/reversi/lm/test\_hlp\_optimize.py | complete | 20/0/0/0/0 | [docs/test/reversi/lm/test\_hlp\_optimize.md](docs/test/reversi/lm/test\_hlp\_optimize.md) |
| test/reversi/lm/test\_hlp\_plot.py | complete | 12/0/0/0/0 | [docs/test/reversi/lm/test\_hlp\_plot.md](docs/test/reversi/lm/test\_hlp\_plot.md) |
| test/reversi/lm/test\_hlp\_su\_analysis.py | complete | 39/0/0/0/0 | [docs/test/reversi/lm/test\_hlp\_su\_analysis.md](docs/test/reversi/lm/test\_hlp\_su\_analysis.md) |
| test/reversi/lm/test\_hlp\_wmaps.py | complete | 16/0/0/0/0 | [docs/test/reversi/lm/test\_hlp\_wmaps.md](docs/test/reversi/lm/test\_hlp\_wmaps.md) |
| test/reversi/lm/test\_hlp\_zed.py | complete | 10/0/0/0/0 | [docs/test/reversi/lm/test\_hlp\_zed.md](docs/test/reversi/lm/test\_hlp\_zed.md) |
| test/reversi/lm/test\_lm\_worker\_full\_chain.py | complete | 10/0/1/0/1 | [docs/test/reversi/lm/test\_lm\_worker\_full\_chain.md](docs/test/reversi/lm/test\_lm\_worker\_full\_chain.md) |
| test/reversi/lm/test\_logistic\_model.py | complete | 31/0/0/0/0 | [docs/test/reversi/lm/test\_logistic\_model.md](docs/test/reversi/lm/test\_logistic\_model.md) |
| test/reversi/lm/test\_wrk\_analytics.py | complete | 20/0/0/0/0 | [docs/test/reversi/lm/test\_wrk\_analytics.md](docs/test/reversi/lm/test\_wrk\_analytics.md) |
| test/reversi/lm/test\_wrk\_anova.py | complete | 7/0/0/0/0 | [docs/test/reversi/lm/test\_wrk\_anova.md](docs/test/reversi/lm/test\_wrk\_anova.md) |
| test/reversi/lm/test\_wrk\_client\_check.py | complete | 7/0/0/0/0 | [docs/test/reversi/lm/test\_wrk\_client\_check.md](docs/test/reversi/lm/test\_wrk\_client\_check.md) |
| test/reversi/lm/test\_wrk\_config.py | complete | 14/0/0/0/0 | [docs/test/reversi/lm/test\_wrk\_config.md](docs/test/reversi/lm/test\_wrk\_config.md) |
| test/reversi/lm/test\_wrk\_design\_matrix.py | complete | 3/0/0/0/0 | [docs/test/reversi/lm/test\_wrk\_design\_matrix.md](docs/test/reversi/lm/test\_wrk\_design\_matrix.md) |
| test/reversi/lm/test\_wrk\_features.py | complete | 3/0/0/0/0 | [docs/test/reversi/lm/test\_wrk\_features.md](docs/test/reversi/lm/test\_wrk\_features.md) |
| test/reversi/lm/test\_wrk\_final\_log\_print.py | complete | 6/0/0/0/0 | [docs/test/reversi/lm/test\_wrk\_final\_log\_print.md](docs/test/reversi/lm/test\_wrk\_final\_log\_print.md) |
| test/reversi/lm/test\_wrk\_generate.py | complete | 6/0/0/0/0 | [docs/test/reversi/lm/test\_wrk\_generate.md](docs/test/reversi/lm/test\_wrk\_generate.md) |
| test/reversi/lm/test\_wrk\_gradient.py | complete | 6/0/0/0/0 | [docs/test/reversi/lm/test\_wrk\_gradient.md](docs/test/reversi/lm/test\_wrk\_gradient.md) |
| test/reversi/lm/test\_wrk\_indexes.py | complete | 2/0/0/0/0 | [docs/test/reversi/lm/test\_wrk\_indexes.md](docs/test/reversi/lm/test\_wrk\_indexes.md) |
| test/reversi/lm/test\_wrk\_optimize.py | complete | 6/0/0/0/0 | [docs/test/reversi/lm/test\_wrk\_optimize.md](docs/test/reversi/lm/test\_wrk\_optimize.md) |
| test/reversi/lm/test\_wrk\_plot.py | complete | 10/0/0/0/0 | [docs/test/reversi/lm/test\_wrk\_plot.md](docs/test/reversi/lm/test\_wrk\_plot.md) |
| test/reversi/lm/test\_wrk\_positions.py | complete | 12/0/0/0/0 | [docs/test/reversi/lm/test\_wrk\_positions.md](docs/test/reversi/lm/test\_wrk\_positions.md) |
| test/reversi/lm/test\_wrk\_su\_analysis.py | complete | 10/0/1/1/0 | [docs/test/reversi/lm/test\_wrk\_su\_analysis.md](docs/test/reversi/lm/test\_wrk\_su\_analysis.md) |
| test/reversi/lm/test\_wrk\_validate.py | complete | 12/0/0/0/0 | [docs/test/reversi/lm/test\_wrk\_validate.md](docs/test/reversi/lm/test\_wrk\_validate.md) |
| test/reversi/lm/test\_wrk\_vld\_positions.py | complete | 15/0/0/0/0 | [docs/test/reversi/lm/test\_wrk\_vld\_positions.md](docs/test/reversi/lm/test\_wrk\_vld\_positions.md) |
| test/reversi/lm/test\_wrk\_wmaps.py | complete | 4/0/0/0/0 | [docs/test/reversi/lm/test\_wrk\_wmaps.md](docs/test/reversi/lm/test\_wrk\_wmaps.md) |
| test/reversi/lm/test\_wrk\_zed.py | complete | 3/0/0/0/0 | [docs/test/reversi/lm/test\_wrk\_zed.md](docs/test/reversi/lm/test\_wrk\_zed.md) |
| test/reversi/paths.py | complete | 0/0/0/0/0 | [docs/test/reversi/paths.md](docs/test/reversi/paths.md) |
| test/reversi/tags.py | complete | 0/0/0/0/0 | [docs/test/reversi/tags.md](docs/test/reversi/tags.md) |
| test/reversi/test\_board.py | complete | 308/0/15/0/0 | [docs/test/reversi/test\_board.md](docs/test/reversi/test\_board.md) |
| test/reversi/test\_feature.py | complete | 33/0/1/0/0 | [docs/test/reversi/test\_feature.md](docs/test/reversi/test\_feature.md) |
| test/reversi/test\_index.py | complete | 10/0/0/0/0 | [docs/test/reversi/test\_index.md](docs/test/reversi/test\_index.md) |
| test/reversi/test\_mobility.py | complete | 31/0/1/0/0 | [docs/test/reversi/test\_mobility.md](docs/test/reversi/test\_mobility.md) |
| test/reversi/test\_paths.py | complete | 3/0/0/0/0 | [docs/test/reversi/test\_paths.md](docs/test/reversi/test\_paths.md) |
| test/reversi/test\_pattern.py | complete | 76/0/3/0/0 | [docs/test/reversi/test\_pattern.md](docs/test/reversi/test\_pattern.md) |
| test/reversi/test\_random\_game.py | complete | 43/0/1/0/0 | [docs/test/reversi/test\_random\_game.md](docs/test/reversi/test\_random\_game.md) |
| test/reversi/test\_regab.py | complete | 49/0/0/0/0 | [docs/test/reversi/test\_regab.md](docs/test/reversi/test\_regab.md) |
| test/reversi/tools/test\_binio.py | complete | 56/0/0/0/0 | [docs/test/reversi/tools/test\_binio.md](docs/test/reversi/tools/test\_binio.md) |
| test/reversi/tools/test\_cache\_manager.py | complete | 22/0/0/0/0 | [docs/test/reversi/tools/test\_cache\_manager.md](docs/test/reversi/tools/test\_cache\_manager.md) |
| test/reversi/tools/test\_opt\_lbfgs.py | complete | 24/0/0/0/0 | [docs/test/reversi/tools/test\_opt\_lbfgs.md](docs/test/reversi/tools/test\_opt\_lbfgs.md) |
| test/reversi/tools/test\_prng.py | complete | 32/0/0/0/0 | [docs/test/reversi/tools/test\_prng.md](docs/test/reversi/tools/test\_prng.md) |
| test/reversi/tools/test\_state\_machine.py | complete | 51/0/0/0/0 | [docs/test/reversi/tools/test\_state\_machine.md](docs/test/reversi/tools/test\_state\_machine.md) |
| test/reversi/tools/test\_usage\_binio.py | complete | 3/0/0/0/0 | [docs/test/reversi/tools/test\_usage\_binio.md](docs/test/reversi/tools/test\_usage\_binio.md) |

Test data (test/reversi/data/):

- `ffo_12_log_sample.csv` — the FFO-12 legacy C solve-log sample (the `position_hash` parity fixture, the deterministic
  1002-row stride — 1003 lines incl. the header)
- `prng_golden.txt` — the committed PRNG golden (the 18436 lines, the 20 sections)
- `rlm_00.json` — the JSON5 unit-test config (the base rlm\_00 fixture of the NO-DB mock-ctx suites)
- `rlm_01.json` — the unit-test config (the Design Matrix data structure)
- `rlm_02.json` — the unit-test config (the gradient worker)
- `rlm_03.json` — the LONG-tier full-worker-chain config (the A2050 feature set)
- `rlm_04.json` — the shorter full-worker-chain config (EDGE + MOBILITY)
- `rlm_05.json` — the SU-analysis experiment config (the 2M corpus, ec 20, stops at SU\_ANALYSIS)
- `rlm_06.json` — the SU-analysis experiment config (the 100M tier, ec 20)

## Index

- notes/naming.md — canonical domain naming convention (board vocabulary, D8, feature types)
- notes/design\_principles.md — the house design policy of the pipeline (dual scalar/array API, pydantic, numba kernels)
- notes/rules.md — active legislation: the register of the rules in force.
- notes/decisions.md — open historical decision log (append-only)
- notes/hist\_decisions/decisions\_000.md — closed decision volume 000 (D-001…D-116, 2026-08-25 → 2026-09-06)
- notes/hist\_decisions/decisions\_001.md — closed decision volume 001 (D-117…D-158, 2026-09-06 → 2026-09-11)
- notes/hist\_decisions/decisions\_002.md — closed decision volume 002 (D-159…D-206, 2026-09-11 → 2026-09-15)
- notes/hist\_decisions/decisions\_003.md — closed decision volume 003 (D-207…D-257, 2026-09-15 → 2026-09-19)
- notes/hist\_decisions/decisions\_004.md — closed decision volume 004 (D-258…D-300, 2026-09-19 → 2026-09-23)
- notes/hist\_decisions/decisions\_005.md — closed decision volume 005 (D-301…D-332, 2026-09-23 → 2026-09-29)
- notes/hist\_decisions/decisions\_006.md — closed decision volume 006 (D-333…D-425, 2026-09-29 → 2026-10-03)
- notes/analyses/ — the one-off analyses (work\_report.md: the 18-years vs 6-weeks work comparison of D-433).
- notes/ideas.md — the OPEN backlog
- notes/ideas\_closed.md — the CLOSED ideas (done | dropped)
- notes/decisions\_rules.md — the decisions-log format rules
- notes/log\_rules.md — session-journal format rules
- notes/docs\_rules.md — mirror-doc format rules
- notes/overview\_rules.md — the format rules of notes/overview.md
- notes/wsutils.md — the workspace-utils rules
- notes/probe\_rules.md — verification-apparatus rules
- notes/hist\_log/log\_000.md — session journal, volume 000 (sessions 1–24, closed 2026-09-01)
- notes/hist\_log/log\_001.md — session journal, volume 001 (sessions 25–30, closed 2026-09-08)
- notes/hist\_log/log\_002.md — session journal, volume 002 (sessions 31–37, closed 2026-09-18)
- notes/hist\_log/log\_003.md — session journal, volume 003 (sessions 38–89, closed 2026-09-29)
- notes/hist\_log/log\_004.md — session journal, volume 004 (sessions 90–101, closed 2026-10-11)
- notes/log.md — the session journal (volume 005, sessions 102–..., open)
