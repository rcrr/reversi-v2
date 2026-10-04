# Work report — 18 years (legacy Reversi) vs 6 weeks (this workspace)

Date: 2026-10-04. Requested by Roberto: redo of the comparison report of about two weeks ago. All numbers are measured from the
recorded git state of the two repos — `git log` (commits, dates, authors), `git ls-files` + `wc -l` (the current tree),
`git log --numstat` (the cumulative churn). "Code" numbers exclude the data dumps (the .sql / .dat files that carry the
pattern-frequency tables).

## Repository A — the legacy `/home/rcrr/base/prj/reversi`

- Git span: 2009-11-29 → 2026-08-05 — 6093 days (16.7 years of git history; the project predates the git era, the
  original C code is dated 2008).
- Commits: 3150 total (3108 non-merge), a single author (Roberto Corradini).
- Commit activity per year:

  | year | 2009 | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 |
  | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
  | commits | 26 | 364 | 272 | 273 | 318 | 510 | 309 | 107 | 327 |

  | year | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
  | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
  | commits | 65 | 42 | 83 | 86 | 104 | 47 | 14 | 20 | 183 |

- Tracked files: 1370.
- Current code tree, by language:

  | language | files | lines |
  | --- | --- | --- |
  | C / C++ (c, h, H, C) | 826 | 342,842 |
  | Python | 88 | 30,607 |
  | Java | 140 | 28,466 |
  | SQL (the frequency-table data dumps) | 43 | 10,613,678 |
  | clojure | 9 | 2,049 |
  | tex | 11 | 1,730 |
  | lisp | 6 | 1,542 |
  | R | 11 | 1,147 |
  | sh | 14 | 1,063 |

- Source churn (data excluded): +607,247 / −143,463 lines over the whole history.
- Long-run rates: 0.52 commits/day; 5.0 Python lines/day.

## Repository B — this workspace (the new Reversi ML pipeline)

- Span: 2026-08-25 → 2026-10-04 — 40 days (about 5.7 weeks).
- Commits: 772, a single author; by month: 166 in August (from the 25th), 527 in September, 79 in October (4 days).
- Tracked files: 271, by zone:

  | zone | files | python lines | what it is |
  | --- | --- | --- | --- |
  | src/reversi | 51 | 15,194 | the core + the 19-step LM pipeline (board, pattern, feature, mobility, regab, the lm facade + workers, the tools) |
  | test/reversi | 52 | 22,610 | the unit suite: 1072 tests, green (1072/0/24, the 2026-10-04 measurement) |
  | probes/ | 24 | 6,900 | the per-module verification apparatus |
  | wsutils/ | 8 | 2,070 | the 8 workspace tools (the re-wrappers, the auditors, the suite instruments) |
  | docs/ | 96 md | — | the one-to-one mirror docs of every src/ and test/ file |
  | notes/ | 26 md | — | the governance: rules, decisions (D-001…D-432), the journal (97 sessions), the naming, the analyses |

- Totals: 46,774 Python lines in 134 files; 24,068 Markdown lines in 122 files.
- Cumulative churn: +208,405 / −115,290 lines.
- Rates: 19.3 commits/day; 1,169 Python lines/day.

## Side by side

| metric | legacy (18 y) | this workspace (6 w) | ratio |
| --- | --- | --- | --- |
| span | 6093 days | 40 days | 152× |
| commits | 3150 | 772 | 4.1× |
| commits / day | 0.52 | 19.3 | **37×** |
| commits / week | 3.6 | 131.7 | **36×** |
| tracked files | 1370 | 271 | 5.0× |
| Python lines (current tree) | 30,607 | 46,774 | 1.5× |
| Python lines / day | 5.0 | 1,169 | **233×** |
| source churn | +607k / −143k | +208k / −115k | — |

## How to read it

- The languages are different and the roles differ: the legacy tree is the 16-year C solver engine (+ the Java/Python
  experiments), this workspace is the Python ML pipeline. Raw line counts are not effort-equivalent, and the C corpus
  (342,842 lines) has no counterpart here.
- The new workspace's "work" includes the governance layer that did not exist before: 432 numbered decisions, 97
  journaled sessions, 8 workspace tools, 24 probes, and 96 mirror docs — 24,068 Markdown lines of which the legacy
  repo has 1,730 (tex) total.
- The new churn is inflated by the format-pass campaigns (the re-wraps, the reflows, the docstring conversions): the
  +208k includes many rewrites of files that were created weeks earlier in this same history, not all of it net-new
  design.
- What the 6 weeks delivered, net: 51 src modules implementing the 19-level pipeline, 1072 green tests, the full
  notes/docs governance stack, the workspace tooling — in a repo where every decision, rule and format is itself
  tracked and guarded.
