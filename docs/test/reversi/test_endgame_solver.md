# test/reversi/test_endgame_solver.py

The endgame_solver unit suite — 4 classes / 14 tests, no DB, < 1 s. Companion of
docs/src/reversi/endgame_solver.md.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestSolverResult` | 2 | the result container: the fields (the `np.int8` game value, the final position, the counters) and the frozen behaviour |
| `TestGameValueArrayValidator` | 3 | the int8-dtype contract of the `GameValueArray` validator (moved here with the type in the regab→endgame_solver transfer): the int8 array passes through (identity), the non-int8 array raises, the non-array input passes through |
| `TestMinimaxSolveMicro` | 7 | the search contract on hand-built endgames: the full-board terminal from both perspectives (+16 / −16), the full-board draw (0), the draw-with-48-empties-is-zero (the WOF ruling), the single-empties forced move (+4, 2 nodes / 1 leaf), the equal-value tie keeping the first static move (−14, the A1 line's final), the pass at the root (+10, 3 nodes / 1 leaf) — every case pins the value, the final position, and the node / leaf counts |
| `TestMinimaxSolveFixture` | 2 | the exact solution of the `ffo-01-simplified-8` position of the `gpdb-sample-games.txt` corpus (loaded with the gpdb module): the value 18, the final position, the 46 nodes / 15 leaves, and the A1-B1-H1-G2 solution line ending at the final position — and the node-by-node trace: the 46 `NodeRecord`s of the solve (collected with the `log` callback) reproduce the C game-tree log (the `es_log_ffo-01-simplified-8.csv` fixture) record by record, on the six comparable columns (call id, level, player, parent move, best move, value) |

## Goldens pinned

- The `ffo-01-simplified-8` solution: value 18, 46 nodes, 15 leaves, the final 65-char string, the A1-B1-H1-G2 line.
- The `ffo-01-simplified-8` trace: the 46 records, one to one with the C log rows (sorted by the
  call id on both sides).
- The micro endgames: the seven (value, final, nodes, leafs) quadruples above.

## Conventions

- The fixture positions are loaded with the gpdb module (`load_game_position_database` + `find`) — the module was
  written for this.
- The micro endgames are 65-char string literals: the boards are built so that the intended shape (the legal-move
  sets, the passes, the ties) is what the asserts pin.

## Integration

- Module under test: `endgame_solver.md`.
- The 65-char string↔GamePosition conversion and the WOF `position_final_value` are pinned in `test_board.md`
  (the `TestGamePosition` area F and the `position_final_value` tests) — this suite exercises the SEARCH on top
  of them.
