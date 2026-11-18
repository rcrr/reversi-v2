# test/reversi/test_endgame_solver.py

The endgame_solver unit suite — 4 classes / 22 tests, no DB; the fixture cases 4–8 dominate the runtime
(~9 s, the scalar phase — the numba-compiled phase is the next campaign step). Companion of
docs/src/reversi/endgame_solver.md.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestSolverResult` | 2 | the result container: the fields (the `np.int8` game value, the final position, the counters) and the frozen behaviour |
| `TestGameValueArrayValidator` | 3 | the int8-dtype contract of the `GameValueArray` validator (moved here with the type in the regab→endgame_solver transfer): the int8 array passes through (identity), the non-int8 array raises, the non-array input passes through |
| `TestMinimaxSolveMicro` | 7 | the search contract on hand-built endgames: the full-board terminal from both perspectives (+16 / −16), the full-board draw (0), the draw-with-48-empties-is-zero (the WOF ruling), the single-empties forced move (+4, 2 nodes / 1 leaf), the equal-value tie keeping the first static move (−14, the A1 line's final), the pass at the root (+10, 3 nodes / 1 leaf) — every case pins the value, the final position, and the node / leaf counts |
| `TestMinimaxSolveFixture` | 10 | the generic fixture test over the `ffo-01-simplified` 4–8 series of the `gpdb-sample-games.txt` corpus (loaded with the gpdb module): one `CASES` entry per case (the value, the node / leaf counts, the final position string, the solution line) and two one-line methods per case — the solve case pins the value, the node / leaf counts, the final position, and the solution line played to the final position; the trace case reproduces the C game-tree log of the case (the `es_log_ffo-01-simplified-{4..8}.csv` fixtures) record by record, on the six comparable columns (call id, level, player, parent move, best move, value) |

## Goldens pinned

- The `ffo-01-simplified` 4–8 solutions: the values (18 / −18 / 18 / −18 / 18), the node / leaf counts
  (20040/6201, 2256/644, 519/153, 142/44, 46/15), the final 65-char strings, the solution lines.
- The `ffo-01-simplified` 4–8 traces: the records, one to one with the C log rows (sorted by the call id on
  both sides).
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
