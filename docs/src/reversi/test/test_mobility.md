# reversi/test/test_mobility.py
The mobility unit suite — 2 classes / 26 tests (25 run + the PERF skip), no DB. A faithful sibling of test_pattern.py
(same conventions, same idiom choices).

## Coverage

| class (line) | tests | what it pins |
|---|---|---|
| `TestMobility` | 7 | construction (name/mask/amask/`n_configurations`, LMC/ALMC/DLMC cases), 3 wrong-type args → `ValidationError` (the `*_raises_validation_error` tests), the exact `print` golden string (incl. the `{name:8s}` padding), the `__repr__` golden, `n_configurations` k=2, a=3 → 6 (the "+1 zero-state") |
| `TestMobilitySet` (`setUp` the standard LMC/ALMC/DLMC triple + the `mlf` builder) | 19 | the dup-name + dup-(mask,amask) `ValueError` messages; hash order-insensitivity; the hash formula with the standard-set literal `2e553593…208a94` pinned (double assert: formula AND object); the sorted 3-name ordering; 2 more `ValidationError`s; `names` → `['ALMC', 'LMC', 'DLMC']` + `masks` (3, 2) uint64 goldens; the 4-line `print_summary` golden (hash literal pinned); the `__repr__` golden (also pins the hash literal); the single-position `[53, 13, 66]` golden; the multi-position row-independence test (golden + underflow positions, per-row `[[53,13,66],[63,0,63]]`); the 1M-position PERF (print-only, `PERF=1` env); the 31-line `popcount64` scalar table + vectorized shape/dtype check (native assertEqual with the line number); the underflow boundary (mask = amask = 0xF, lms = 0, alms = 0x8 → 3); the empty set (name/length/`names == []`/`masks().shape == (0, 2)`/`sha3_256(b'')`); the empty positions (shape (0, 3), uint32) |

## Goldens pinned

- No float goldens: the pins are literal strings (print / print_summary / repr), the two `__repr__` one-liners, the hash
  literal, the `[53, 13, 66]` + `[[53,13,66],[63,0,63]]` index goldens (the columns are the set's SORTED order — ALMC,
  LMC, DLMC), the 31-line popcount table, and the empty-behaviour contract (empty set, empty positions).
- The underflow comment's board story is verified: mover 0x10 (E1), opponent 0xE0 (F1, G1, H1) → lms = 0, alms = 0x8
  (D1) → 0 + (4−1) = 3.

## Conventions

- `PERF=1` env enables the 1M-position performance test (print-only — no gates in the whole repo).
- `TestMobilitySet.test_init` carries real assertions (name, length, names); the self-comparison hash pins are
  literal-pinned.

## Integration

- Module under test: `mobility.md` — the suite covers construction, sorting, hashing, the Numba pipeline, and the
  popcount helper.
- The hash formula is pinned by the existing hash tests (which pin the literal); the probe keeps sections 1, 2, 3, 4, 6.
