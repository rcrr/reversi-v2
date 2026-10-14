# test/reversi/test_mobility.py
The mobility unit suite — 2 classes / 33 tests (32 run + the PERF skip), no DB. A faithful sibling of test_pattern.py
(same conventions, same idiom choices).

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestMobility` | 8 | construction (name/mask/side/`n_configurations`, the mover-side and the opponent-side full-board cases), 3 wrong-type/wrong-value args → `ValidationError` (the `*_raises_validation_error` tests, incl. the invalid side value 'both'), the exact `print` golden string (incl. the `{name:8s}` padding), the `__repr__` golden (mover + opponent forms), `n_configurations` k=2 → 3 (the "+1 zero-state") |
| `TestMobilitySet` (`setUp` the standard LMC/ALMC same-mask pair + the `mlf` builder) | 25 | the dup-name + dup-(mask,side) `ValueError` messages; the same mask with the two sides is a VALID pair (the dedicated test); hash order-insensitivity; the hash formula with the standard-set literal `d857e3c3…3037b8` pinned (double assert: formula AND object); the sorted (mask, side) 3-name ordering (same mask: mover before opponent); 2 more `ValidationError`s; `names` → `['LMC', 'ALMC']` + `masks` (2, 2) uint64 goldens (mask + side-code columns); the 4-line `print_summary` golden (hash literal pinned); the `__repr__` golden (also pins the hash literal); the single-position `[13, 11]` golden; the multi-position row-independence test (per-row `[[13,11],[0,1]]`); the N-D shape tests ((1,2) → (1,2,L), (2,1,2) → (2,1,2,L), F-order parity, empty (0,2) → (0,2,L)); the wrong-argument-type subTest loop (None / list / str / plain ndarray → ValidationError); the 1M-position PERF (print-only, `PERF=1` env); the 31-line `popcount64` scalar table + vectorized shape/dtype check (native assertEqual with the line number); the opponent-side boundary (mask = 0xF, side = opponent, lms = 0, alms = 0x8 → 1); the empty set (name/length/`names == []`/`masks` shape (0, 2)/`sha3_256(b'')`); the empty positions (shape (0, 2), uint32) |

## Goldens pinned

- No float goldens: the pins are literal strings (print / print_summary / repr), the two `__repr__` one-liners, the hash
  literal, the `[13, 11]` + `[[13,11],[0,1]]` index goldens (the columns are the set's SORTED (mask, side) order — LMC,
  ALMC), the 31-line popcount table, and the empty-behaviour contract (empty set, empty positions).
- The opponent-side comment's board story is verified: mover 0x10 (E1), opponent 0xE0 (F1, G1, H1) → lms = 0, alms = 0x8
  (D1) → the raw opponent count in the 0xF mask = 1.

## Conventions

- `PERF=1` env enables the 1M-position performance test (print-only — no gates in the whole repo).
- `TestMobilitySet.test_init` carries real assertions (name, length, names); the self-comparison hash pins are
  literal-pinned.

## Integration

- Module under test: `mobility.md` — the suite covers construction, sorting, hashing, the Numba pipeline, and the
  popcount helper.
- The hash formula is pinned by the existing hash tests (which pin the literal); the probe keeps sections 1, 2, 3, 4, 6.
