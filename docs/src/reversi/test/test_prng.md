# reversi/test/test_prng.py
The SMOKE micro-suite of the MT19937 (the 64-bit MT-19937 PRNG
port, the I-017 T2, D-159): the constructor fail-fast, the
seed / array-init determinism, the strict-typing pins (the numpy
uint64 / float64 dtypes of the state and of every output), the
64-bit wrap contract, the no-consume contracts (k == 1, the
n <= 1 shuffles), the extract_from_set64 semantics. 1 class / 10
tests / no DB.
> State: D-160 · pending · 2026-09-11 · suite 10/0/0

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestPrng` | 10 | `test_constants_are_the_c_ones` (NN/MM/UM/LM/MAG01 verbatim); `test_ctor_fails_fast` (neither / both of seed+init_key → ValueError; the EMPTY key → ValueError, the documented C-UB deviation); `test_seed_determinism_and_typing` (50-draw equality, the np.uint64 dtype pin, the state dtype/shape (312,)); `test_array_init_determinism` (list vs ndarray keys equal, the differing key differs, the FRESH-instance mt[0] MSB == 1); `test_get_uint64_wrap_64bit` (the max seed, 100 draws, no overflow error); `test_double_ranges_and_typing` (the [0,1] / [0,1) / (0,1) bounds + the float64 dtype, 1000 draws); `test_random_choice_contracts` (k == 0 → ValueError; k == 1 no-consume — the next draw equals a fresh instance's; k == 5 in [0,4]); `test_shuffle_contracts` (the permutation property, the n <= 1 no-consume, the 3 dtype pins, the generic face); `test_random_string_az` (length, the [a..z] charset, the two-fresh-instances determinism, the n == 0 empty); `test_extract_from_set64` (the single-bit set, the empty-set ValueError, the full 64-bit set → 64 distinct bits + empty, the picked-bit-cleared-from-the-ORIGINAL-set pin) |

## Goldens pinned

- None yet (the SMOKE tier): no bit sequences are pinned here —
  the BIT-EXACT golden (the committed sequences vs Roberto's C
  build + the published vectors + the 100k equi-distribution)
  lands in the T3 extension of this same file.
- The contract pins instead: the dtype pins (np.uint64 /
  np.float64 — the D-159 strict-typing ruling), the no-consume
  sequences (k == 1, n <= 1), the C constant literals.

## Conventions

- The house test header (the "How to run" block).
- The two FRESH-instance idiom for the determinism pins (the
  draws advance the sequence position — the first two failures
  of the T2 wave were exactly this mistake, caught and fixed).
- No DB, no cache, no pipeline: a pure core-module suite.

## Integration

- Consumed by `run_utests.sh` (section 0 — tools, after
  test_opt_lbfgs; the D-160 move with the module).
- The T3 golden suite extends THIS file (the same class family).
