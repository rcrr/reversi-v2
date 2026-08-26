# Ideas / future backlog

Format: I-NNN | status (idea | in-progress | done | dropped) | idea

I-001 | idea | Full restructure of the original repo (later, not now).
       The notes produced here should migrate into the new repo as its
       documentation skeleton.

I-002 | idea | Vectorize `position_flips` / `position_make_move`.
       The author's own comment in board.py flags this: `_kogge_stone_mm` is
       currently scalar Python while `legal_moves` is numba-parallel.

I-003 | idea | Named move constants (MOVE_PASS=64, MOVE_NOT_AVAILABLE=65,
       MOVE_UNKNOWN=66) instead of magic numbers. Would also fix the implicit
       dependency on NumPy shift-wrap semantics in `position_is_move_legal`
       (issue R3 in notes/board.md).

I-004 | idea | (placeholder — Roberto's future-evolution ideas go here as
       they come up)

I-005 | idea | Next session starts a NEW module (Roberto, 2026-08-26).
       Target module to be chosen with Roberto. Candidate: a game-loop
       module (start position, turn/pass/game-over rules, history) —
       board.py is proven a complete game kernel by the 200-game random
       simulation of 2026-08-26; the loop itself is ~25 lines on top of
       the public API. Other candidate: the next source file of the
       original repo (file-by-file modernization).
