# test/reversi/test_endgame_solver.py

The endgame_solver unit suite — 7 classes / 57 tests (54 + the two LONG-gated case 0 solves + the three
PERF-gated throughput runs), no DB beyond the gpdb fixture load; the runtime is dominated by the traced
fixture solves (the trace is the typed-list sink of the compiled search, replayed to the collector at the
end). Companion of docs/src/reversi/endgame_solver.md.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestSolverResult` | 2 | the result container: the fields (the `np.int8` game value, the final position, the counters) and the frozen behaviour |
| `TestGameValueArrayValidator` | 3 | the int8-dtype contract of the `GameValueArray` validator (moved here with the type in the regab→endgame_solver transfer): the int8 array passes through (identity), the non-int8 array raises, the non-array input passes through |
| `TestMinimaxSolveMicro` | 7 | the search contract on hand-built endgames: the full-board terminal from both perspectives (+16 / −16), the full-board draw (0), the draw-with-48-empties-is-zero (the WOF ruling), the single-empties forced move (+4, 2 nodes / 1 leaf), the equal-value tie keeping the first static move (−14, the A1 line's final), the pass at the root (+10, 3 nodes / 1 leaf) — every case pins the value, the final position, and the node / leaf counts |
| `TestMinimaxSolveFixture` | 17 | the generic fixture test over the `ffo-01-simplified` 0–8 series of the `gpdb-sample-games.txt` corpus (loaded with the gpdb module): one `CASES` entry per case (the value, the node / leaf counts, the final position string, the solution line) — the solve method pins the value, the node / leaf counts, the final position, and the solution line played to the final position (on the numba fast path); the trace method (cases 4–8 only) reproduces the C game-tree log of the case (the `es_log_ffo-01-simplified-{4..8}.csv` fixtures) record by record, on the six comparable columns (call id, level, player, parent move, best move, value). The 18M-node case 0 is LONG-gated. Plus the corner cases: the already-finished game of the series (case 12: the single leaf, the WOF of the full board), `black-has-to-pass` (the forced first pass: the line opens with `--`) and `black-wins-by-wipe-out` (the wipe-out win before ec=0: the full −64, the one-colour final) — the three search-contract edge shapes |
| `TestAlphaBetaSolveFixture` | 18 | the alpha-beta twin of the fixture: the same `CASES` shape against the C alpha-beta reference (the 9.9x–25x smaller node / leaf counts, the same value / final / line); the trace method (cases 4, 6, 7, 8) reproduces the C alpha-beta log (the `ab_log_ffo-01-simplified-{4,6,7,8}.csv` fixtures) record by record on the five comparable columns, with the best-move column compared only when the v2 record has a real best move (the C `T_BEST_MOVE` of a non-improving node is the stale value of the previous stack-slot occupant — a C logging artifact, not part of the search contract); `test_ab_minimax_parity` pins the alpha-beta / minimax agreement on the value and the final position of the 1–8 series (both searches are exact). The 1.7M-node case 0 is LONG-gated. Plus the same three corner cases as the minimax fixture (the pruned node / leaf counts, the same value / final / line — the line the minimax one: the alpha-beta recorded best-move chain stops at the first fail-low tie) |
| `TestAlphaBetaSolveArray` | 6 | the worker-pool array solver: the ten ec=8 lanes of the regab_prng_gp batch 7 (the user's set, the bitboards as the DB signed integers) against the INDEPENDENT DB game-value goldens [14, 22, 0, 2, 8, −8, −6, 28, −48, −22]; the per-lane parity with the scalar `alphabeta_solve` (value, final, node / leaf counts — the engine runs the same compiled search, so every lane is its scalar result); the mixed corner batch (the forced first pass, the already-finished game, the wipe-out, a plain series lane — each lane its scalar result); the empty batch; and the `uniform_empty_count` / `check_ec` gate (the uniform batch returns the common ec, the non-uniform raises — `check_ec=True` enforces it at the boundary, the default False skips it) |
| `TestAlphaBetaSolveArrayScale` | 3 | the worker pool at the 100 / 1000-lane scale: the regab batch sets (the ec=8 positions of the `regab_prng_gp` table, pulled in seq order from the batches 8 and 9 — the data files `regab-batch8-ec8-100.tsv` / `regab-batch9-ec8-1000.tsv`) against the INDEPENDENT DB game-value goldens (all 100 / all 1000 values), the `check_ec=True` gate on both; plus the PERF-gated throughput printout of the 1000-lane batch (2.3M nodes in ~0.22 s, ~10.4 M lane-nodes/s — the printout is the measurement) |

## Goldens pinned

- The `ffo-01-simplified` 0–8 solutions: the values (18 / −18 / 18 / −18 / 18 / −18 / 18 / −18 / 18), the
  node / leaf counts (18055194/5316151, 1111408/322891, 261482/78435, 105203/32174, 20040/6201, 2256/644,
  519/153, 142/44, 46/15), the final 65-char strings, the solution lines.
- The `ffo-01-simplified` 4–8 traces: the records, one to one with the C log rows (sorted by the call id on
  both sides).
- The `ffo-01-simplified` 0–8 alpha-beta solutions: the values (the same 18 / −18 alternation), the pruned
  node / leaf counts (1700428/420214, 43846/10037, 15638/3640, 7881/1947, 2029/538, 427/108, 232/64, 107/33,
  40/13), the same final 65-char strings and solution lines as the minimax.
- The `ffo-01-simplified` 4, 6, 7, 8 alpha-beta traces: the records, one to one with the C alpha-beta log rows
  (the best-move column under the non-improving-node caveat above).
- The corner cases: `ffo-01-simplified-12` (the already-finished game: +18, 1 node / 1 leaf, the WOF of the
  full board), `black-has-to-pass` (−52, 196,030 / 55,778 minimax — 23,977 / 5,963 alpha-beta, the line
  opening with the pass), `black-wins-by-wipe-out` (−64, 4,900,474 / 1,367,719 minimax — 310,082 / 74,388
  alpha-beta, the one-colour final) — each with the final 65-char string and the solution line (the `--`
  entries replayed as the player-swap move).
- The ten ec=8 batch lanes (the regab_prng_gp batch 7): the independent DB game values [14, 22, 0, 2,
  8, −8, −6, 28, −48, −22] and the per-lane scalar parity (value, final, node / leaf counts).
- The 100 / 1000-lane regab batches (the batches 8 and 9, the ec=8 positions in seq order): the
  independent DB game values of every lane (the data files carry them, the test compares the whole
  array).
- The micro endgames: the seven (value, final, nodes, leafs) quadruples above.

## Conventions

- The fixture positions are loaded with the gpdb module (`load_game_position_database` + `find`) — the module was
  written for this.
- The micro endgames are 65-char string literals: the boards are built so that the intended shape (the legal-move
  sets, the passes, the ties) is what the asserts pin.

## Integration

- Module under test: `endgame_solver.md`.
- The 65-char string↔GamePosition conversion and the three GamePosition-level game-tree tools are pinned in
  `test_board.md` (the `TestGamePosition` area F) — this suite exercises the SEARCH on top of them.
