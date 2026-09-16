# reversi/test/test_prng.py
The MT19937 (the 64-bit MT-19937 PRNG) suite: the strict-typing
pins (the numpy uint64 / float64 dtypes of every output), the
64-bit wrap contract, the no-consume contracts (k == 1, the n <=
1 shuffles, the empty set), the extract_from_set64 +
choose_one_from_set64 semantics; the bit-exact golden (the
committed reference sequences) + the first-100k equi-
distribution. 4 classes / 19 tests / no DB.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestPrng` | 7 | `test_get_uint64_wrap_64bit` (the max seed, 100 draws, no overflow error, the np.uint64 dtype pin); `test_get_uint64_batch_matches_scalar` (500 get_uint64_batch draws == get_uint64 × 500 bit-exact, the u64 dtype + (n,) shape, crossing the 312-word twist boundary); `test_double_ranges_and_typing` (the [0,1] / [0,1) / (0,1) bounds + the float64 dtype, 1000 draws); `test_random_choice_contracts` (k == 0 → ValueError; k == 1 no-consume — the next draw equals a fresh instance's; k == 5 in [0,4]); `test_shuffle_contracts` (the permutation property, the n <= 1 no-consume, the 3 dtype pins, the generic face); `test_random_string_az` (length, the [a..z] charset, the two-fresh-instances determinism, the n == 0 empty); `test_extract_from_set64` (the single-bit set, the empty-set ValueError, the full 64-bit set → 64 distinct bits + empty, the picked-bit-cleared-from-the-ORIGINAL-set pin) |
| `TestPrngGolden` | 4 | the bit-exact golden (the committed `data/prng_golden.txt` — each section mirrored with a FRESH instance): `test_seed42_sequence` (10000 uint64, hex); `test_doubles` (100 × 3 kinds, the %.17g strings); `test_choice_sequence` (1000 × random_choice(5)); `test_extract_full_sequence` (64 picks exhaust the full set: the positions + the permutation + the empty end) |
| `TestChooseOneFromSet64` | 5 | the uniform NO-REMOVAL pick (3 seeds): `test_empty_set_is_the_sentinel_and_consumes_nothing` (the (0, 64) sentinel, no draw consumed); `test_the_return_is_the_single_bit_at_position_p` (the return is (1 << p, p), p a set bit, 3 seeds x 4 sets x 20 picks); `test_the_set_is_never_mutated` (the set is never drained, 3 seeds x 100 picks); `test_the_1000_pick_golden_and_expected_frequencies` (the 7 golden cases — the full + 3 two-bit + 3 three-bit sets — the exact 1000-pick sequence + the expected frequencies); `test_the_full_set_is_reasonably_equidistributed` (200k full-set picks, the 64 bins, the chi2 < 150 threshold) |
| `TestPrngEquidistribution` | 3 | the first-100k statistical properties (deterministic, seed 42): `test_first_100k_bit_balance` (the 64 bit positions in the 48-52% band — the ~12.6-sigma tolerance); `test_first_100k_top_bits_chi_square` (the top-7-bit 128 bins, the chi2 < 250 conservative threshold); `test_choice_64_uniform` (100k random_choice(64) draws, the 64 bins, the chi2 < 130 threshold) |

## Goldens pinned

- `src/reversi/test/data/prng_golden.txt` (18436 lines, 20
  sections): the committed reference sequences — a known-correct
  output snapshot the implementation must reproduce bit-for-bit.
  Sections: [seq_seed42] (10000), [doubles_c0_c1] /
  [doubles_c0_o1] / [doubles_o0_o1] (100 each), [choice5]
  (1000), [extract_full] (64); the choose_one_from_set64 cases
  (each a 1000-pick sequence + a `_freqs` companion of the
  expected frequencies): [choose_full] (the full set),
  [choose_2bit_a/b/c] (three distinct 2-bit sets),
  [choose_3bit_d/e/f] (three distinct 3-bit sets).
- The contract pins: the dtype pins (np.uint64 / np.float64), the
  no-consume sequences (k == 1, n <= 1, the empty set).

## Conventions

- The house test header (the "How to run" block).
- The two-FRESH-instance idiom for the determinism pins (the
  draws advance the sequence position).
- No DB, no cache, no pipeline: a pure core-module suite.

## Integration

- Consumed by `run_utests.sh` (section 0 — tools, after
  test_opt_lbfgs).
- The golden suite extends THIS file (the same class family).
