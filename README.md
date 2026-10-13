# reversi-v2

A modernized Reversi (Othello) engine, and a logistic-model (LM) evaluation pipeline built on top of it:
feature extraction from real games, model training, and board evaluation.

GNU GPL v3 or any later version — the full text in [LICENSE](LICENSE).

## Requirements

- Python ≥ 3.12 (developed and tested on 3.14)
- The dependencies declared in `pyproject.toml` (numpy, numba, pydantic, pandas, scipy, matplotlib, lz4,
  json5, psycopg2, python-dotenv) — installed by `pip install -e .`
- A PostgreSQL server holding the `regab` data set — **optional**: without it, run the suite with
  `SKIP_REGAB_DB=1` (the DB-gated tests are skipped). More information on the regab database can be found in
  the [rcrr/reversi](http://github.com/rcrr/reversi) project.

## Setup

```bash
git clone https://github.com/rcrr/reversi-v2.git
cd reversi-v2
python3 -m venv .venv
.venv/bin/pip install -e .
cp .env.example .env        # then fill in your own DB credentials (.env is gitignored)
```

## Running the tests

```bash
./run_utests.sh                  # the fast tier (~20 s)
LONG=1 ./run_utests.sh           # the standard full run (~3 min)
SKIP_REGAB_DB=1 ./run_utests.sh  # no PostgreSQL server available
```

The runner prints a banner with the active tier switches. The suite tiers are NORMAL (default), LONG, VLONG
and VVLONG; the test artifacts are written under `build/tmp/` (created automatically — no manual steps on a
fresh clone).

## Running the pipeline

```bash
.venv/bin/python -m reversi.lm.logistic_model <config.json> [--verbosity {high,moderate,standard,low,very_low,none}]
```

The config file format — a minimal entry and the exhaustive per-section reference — is documented in
[docs/user/lm_config_guide.md](docs/user/lm_config_guide.md).

## Layout

| Path | What it is |
|---|---|
| `src/reversi/` | the game engine (board, bitboards, patterns, features) |
| `src/reversi/lm/` | the logistic-model pipeline (config, workers, training, evaluation) |
| `src/reversi/tools/` | the shared tooling (binary I/O, cache, state machine) |
| `test/` | the unit-test suite (unittest, mirroring the source tree) |
| `docs/` | the mirror documentation (one doc per source file) |
| `docs/user/` | the user-facing documentation |
| `notes/` | the workspace governance (decisions log, rules register, session journal) |
| `probes/` | the standalone verification probes |
| `wsutils/` | the workspace tools (the format guards, the checkin gate) |
