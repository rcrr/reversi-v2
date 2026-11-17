# test/reversi/test_endgame_solver.py

The endgame_solver unit suite — 3 classes / 10 tests, no DB, < 1 s. Companion of
docs/src/reversi/endgame_solver.md.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestSolverResult` | 2 | the result container: the fields (the `np.int8` game value, the final position, the counters) and the frozen behaviour |
| `TestMinimaxSolveMicro` | 7 | the search contract on hand-built endgames: the full-board terminal from both perspectives (+16 / −16), the full-board draw (0), the draw-with-48-empties-is-zero (the WOF ruling), the single-empties forced move (+4, 2 nodes / 1 leaf), the equal-value tie keeping the first static move (−14, the A1 line's final), the pass at the root (+10, 3 nodes / 1 leaf) — every case pins the value, the final position, and the node / leaf counts |
| `TestMinimaxSolveFixture` | 1 | the exact solution of the `ffo-01-simplified-8` position of the `gpdb-sample-games.txt` corpus (loaded with the gpdb module): the value 18, the final position, the 46 nodes / 15 leaves, and the A1-B1-H1-G2 solution line ending at the final position |

## Goldens pinned

- The `ffo-01-simplified-8` solution: value 18, 46 nodes, 15 leaves, the final 65-char string, the A1-B1-H1-G2 line.
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
