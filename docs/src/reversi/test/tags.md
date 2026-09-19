# reversi/test/tags.py
The suite-tier gates (D-130; the VVLONG tier added at D-256): the predicates + the DB gate the test modules use to
declare which tier they belong to. The tiers are CUMULATIVE — each implies the previous ones.

## API

| name | contract |
|---|---|
| `tier_vlong()` | True when `VLONG=1`, or `VVLONG=1` (which implies VLONG → LONG): the long instruments gate on it |
| `tier_vvlong()` | True when `VVLONG=1` only (it implies VLONG → LONG): the very-long instruments gate on it |
| `db_long_gate(testcase)` | Skip the test when the live regab DB is unavailable or the LONG tier is off: `SKIP_REGAB_DB=1` always skips (the no-DB environment), then the tier check. It calls `testcase.skipTest(...)`, so it goes FIRST in `setUp` (the house setUp shape) |

`__all__` = [db_long_gate, tier_vlong, tier_vvlong] (D-256: the predicates joined the gate). No `@validate_call` — these
are test helpers, not domain functions.

## Architecture

The four cumulative tiers and how a test declares its own:

| env | adds | how a test declares it |
|---|---|---|
| (none) | the fast tier: no DB, no pipeline | — |
| `LONG=1` | the DB-gated pipeline tests | `db_long_gate(self)` first in `setUp` |
| `VLONG=1` | the long instruments (the ~10-min A2050 end-to-end chain) | `@skipUnless(tier_vlong(), …)` on the class |
| `VVLONG=1` | the very-long instruments (the 1e6 corpus benchmark, the 1e7 corpus test) | `@skipUnless(tier_vvlong(), …)` on the class |

`PERF=1` (the print-only performance tests) and `SKIP_REGAB_DB=1` (a no-DB environment) are ORTHOGONAL to the tiers.

- Two predicates over `os.getenv` + the gate. The predicates are evaluated at IMPORT time by the `@skipUnless`
  decorators (the house pattern); the gate runs at setUp time (it needs the testcase for the skip message).
- `db_long_gate` reads `SKIP_REGAB_DB` first: a no-DB environment skips every DB test, whatever the tier.
- The predicates are the SINGLE SOURCE of the tier semantics: a test declares its tier by calling one, never by reading
  the env vars itself.

## Verified invariants

- The tier matrix (checked by hand at D-256): no env → both predicates False; `LONG=1` → both False; `VLONG=1` →
  `tier_vlong()` True and `tier_vvlong()` False; `VVLONG=1` → both True.
- The behavioural pin is the suite's skip counts: the 1e6 benchmark SKIPS under `LONG=1` and RUNS under `VVLONG=1`
  (`test_hlp_wave` reports 4/0/1 in both the default and the LONG tiers), and the 1e7 corpus test skips in the default
  and LONG tiers (`test_wrk_su_analysis` 8/0/0, VLONG 9/0/0).
- The DB gate: the default tier and `SKIP_REGAB_DB=1` skip every DB-gated test (the runner's skipped counts).

## Open issues

None.

## Conventions

- A class-level tier goes in the `@skipUnless` decorator, evaluated at decoration time; `db_long_gate` stays in `setUp`.
- A NEW tier means four edits (the D-256 checklist): a predicate here, the runner header, the rules.md bullet, the
  overview.
- `db_long_gate(cls)` is NOT supported: `TestCase.skipTest` needs an instance, so a `setUpClass` that must skip raises
  `unittest.SkipTest` directly (tried in the D-252 pilot, reverted with it).

## Integration

- Imported by every DB-gated and long-running test module — the single source of the tier semantics. The DB-gated
  modules call `db_long_gate(self)` first in `setUp` (the pipeline worker suites, `test_regab`, the full-chain suite);
  the long ones gate their class on `tier_vlong()` (the A2050 chain, the 1e7 corpus test) or `tier_vvlong()` (the 1e6
  benchmark).
- The canonical runner `run_utests.sh` documents the same tiers in its header.
