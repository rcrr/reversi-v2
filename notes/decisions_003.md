# Decisions log — volume 003 (closed)

Format: D-NNN | date | decision | rationale

Volume 003: D-207…D-257 (2026-09-15 → 2026-09-19); closed at the D-333 rotation (the open log had 4460 lines > the
amended 1000 cap); the open log continues in notes/decisions.md.

D-207 | 2026-09-15 | The overview.md SIMPLIFICATION (Roberto: "completamente un BLOB! ... tieni le cose che ci servono a
         guardare avanti, non la storia insignificante"). The "Where we are" (~550 lines) and "Next steps" (~175 lines)
         sections had drifted into campaign narrative (the D-192..D-206 story, the whole I-017 T1..T19, the
         PLOT D-149..D-155, config cache, duplicate positions, the reorganization) — violating the file's own contract
         ("Current state only — the history lives in the journal volumes + the decision log"). Applied: (1) "Where we
         are" -> a compact current state (the 18-level pipeline live + green, G0 the corpus generator, the
         self-describing v2 model file, the `random_game` module, the MINIMAL fully-numba PRNG, the STALE pre-fix
         corpora); (2) "Next steps" -> the real backlog (regenerate the STALE G0 corpora, the last PRNG passettino, the
         profiling session, the I-003/I-009/I-010/I-018 backlog); (3) the per-file Source/Test tables' State columns
         trimmed from the D-pointer narrative to a status word + the open items (the Suite + Doc columns kept verbatim);
         (4) the stale Environment "Suite status" (771 tests, 2026-09-10) dropped (the suite changes per commit; the
         per-file Suite column is the live reference). The history was NOT lost: it already lives in decisions.md + the
         journal (the D-pointers index it). 981 -> 241 lines. The Project / Conventions / Index sections kept (they are
         the look-forward content). Notes-only: no source / doc / test touched.

D-208 | 2026-09-15 | The PASS-semantics fix (Roberto, approved after the analysis + plan): a PASS must yield the
         position with the players inverted, not None / unchanged. `board.position_flips`: the SCALAR path now returns
         (0, `make_position`(o, m)) for a zero (PASS) move instead of (0, None); the `_vectorized_flips` kernel swaps
         the players for a zero element instead of leaving the input unchanged. An illegal (single-bit, no flip) or
         non-single-bit move is unchanged (scalar None / array input-unchanged). `board.position_make_move`: BEHAVIOUR
         UNCHANGED (PA = 64 already swapped the players, scalar and array); only the docstring clarified that the None
         in the return type is the illegal-scalar-move signal only, never the PA (Roberto's option A: keep the None).
         `random_game`. `game_position_make_random_move`: the pass now returns (the swapped position, PA) instead of
         (None, PA) — a pure consequence of the `position_flips` fix (no logic change); the return annotation dropped
         the "| None". Tests: `test_position_flips_move_is_empty` (scalar pass -> swap), the 2 bulk tests (the dataset
         line 000 is a pass -> swap, the illegal lines still None / unchanged), the array fuzz parity (the pass branch
         swapped), a NEW `test_position_flips_array_pass_batch` (a pure-pass batch -> every element swapped), and a NEW
         `test_no_legal_move_is_a_pass_with_the_swapped_position` in `test_random_game`. Verified: `test_board`
         222/0/14, `test_random_game` 8/0/0, full LONG 864/0/21 GREEN (862 + 2); 1e6 G0 bit-exact (28065 dead lanes) —
         the wave (which drives the stream through `position_make_move`, unchanged) is unaffected.

D-209 | 2026-09-15 | The decisions.md reformat (Roberto, after reviewing the first pass): a full re-wrap to ~120
         chars/line (was ~68) + the mid-token rejoins (the paths / identifiers the 68-char wrap had broken across lines
         after /, -, \_ — `reversi/feature_prng.py`, `no-consume`, `check_su_pairs_feature_set`) + a blank line before
         every entry + code spans for all paths (with /) and function / file names (with \_), and backslash-escaped
         asterisks for the math multiplications (`delta*`, `k*2^-53`, ...), so the Markdown renders without the stray
         italics (the D-159 `prng_mt19937_*` / `k==1 / n<=1` case). The re-wrap is code-span-aware: the 39 pre-existing
         code spans (function signatures, expressions) are unbreakable units, never split across lines. A re-wrap bug (a
         later short word appended to an already-full first line, skipping the words that moved to the next line and
         inverting the word order — the D-160 `(Roberto's call: "non ...")` case) was caught and fixed with a
         first-line-full flag. Content verified identical to the original modulo the 76 mid-token rejoins (zero
         reorders, zero words added / removed). The format is codified in `rules.md` (the decisions.md bullet). 1849 ->
         923 lines.

D-210 | 2026-09-18 | `position_empty_count` (Roberto) + the `bitboard_count` dual: a dual (scalar + array) count of the
         empty squares of a position — `~(mover | opponent)` piped through `bitboard_count`. `bitboard_count` was made
         dual (`bb: Bitboard | BitboardArray) -> np.uint8 | npt.NDArray[np.uint8]`): the array case was blocked by its
         scalar-only annotation (pydantic enforced it), the logic was already correct (`np.bitwise_count` is a ufunc);
         the other 5 call sites pass scalars, so the widening is safe. `position_empty_count`'s return type corrected to
         the count type (was `Bitboard | BitboardArray`). Tests: `test_bitboard_count_array` + the
         `TestPositionEmptyCount` class (scalar, wrong-type, array, cross-check with `position_empties`, 2D coercion).
         `test_board` 228/0/14 (was 222/0/14). Building block for `game_play_random_path` (the random\_game WIP, a
         separate commit).

D-211 | 2026-09-18 | `initial_game_position` moved from `random_game` to `board` (the Position methods section — the
         CANONICAL standard start; the docstring and the `TestInitialGame` test move to `test_board`). The three
         `random_game` methods are renamed to the `random_game_*` house pattern: `choose_random_move` ->
         `random_game_chose_move`, `game_position_make_random_move` -> `random_game_make_move`,
         `game_play_random_path` -> `random_game_play_path` (the WIP that now has a public name). Imports follow
         (random\_game drops the now-orphan `make_position`; test\_random\_game imports `initial_game_position` from
         board); the `hlp_wave` / `hlp_random_play` comments + the 5 mirror docs follow. `test_board` 229/0/14,
         `test_random_game` 9/0/0, full 872/0/95.

D-212 | 2026-09-18 | The `random_game` syntactic rename (Roberto): `random_game_chose_move` -> `random_game_choose_move`
         ("chose", the past tense, -> "choose") inside the D-211 `random_game_*` house pattern. The test classes +
         methods follow (`TestRandomGameChoseMove` -> `TestRandomGameChooseMove`, `TestRandomGameChoseMoveEC20` ->
         `TestRandomGameChooseMoveEC20`, the 3 `test_random_game_chose_move*` methods). The 2 mirror docs
         (`docs/src/reversi/random_game.md`, `docs/src/reversi/test/test_random_game.md`) + `notes/overview.md` follow
         (the D-211 entry keeps its historical reference verbatim). A pure rename, no behaviour change:
         `test_random_game` 9/0/0, full LONG 872/0/21 GREEN (the 1e6 G0 benchmark bit-exact, 28065 dead lanes).

D-213 | 2026-09-18 | `position_hash` (Roberto's request): the 64-bit Zobrist hash of a game position in `board.py` —
         dual scalar/array, a pure function of the `(mover, opponent)` pair, no legality validation. The CONSTANTS are
         the legacy C engine's (`board.c` `zobrist_bitstrings[]`, URANDOM-generated; the read-only reference
         `/home/rcrr/base/prj/reversi/c/src/board.c`, `game_position_x_hash`) so the hashes are legacy-comparable: the
         mover discs select the first 64 entries (the legacy blacks slots), the opponent the last 64 (the whites slots),
         no complement — exactly the legacy hash of `(blacks=mover, whites=opponent, player=BLACK_PLAYER)`; the C
         complement rule (`if (p) hash = ~hash`, p = WHITE) maps a legacy WHITE position to the one's complement of
         `position_hash(blacks, whites)` (pinned). The Python `Position` carries no absolute color, so the bridge is
         this fixed convention (the only well-defined option; Roberto informed). Kernel: the SWAR byte-fold
         (`_zobrist_byte_fold` 2x8x256, generated at import; 16 lookups/position, no per-bit loop) + a `prange` batch
         kernel — 214M positions/s measured (PERF: 1e6 in 4.7 ms). The table is canon (the SHA-3-256 pin
         `3e3dfd40afef05e075e393def68bc13c0e592cc3d838652e330070eaaa0a626c` + the goldens derived from the C source by
         the session-38 scratch script, which verified the transcribed C loop and the SWAR fold bit-identical over
         10\_000 random pairs). Tests: `TestPositionHash` (13 tests: the goldens, the WHITE bridge, the array parity +
         the 2-D coercion + the empty array + the rejections, the order sensitivity, the avalanche band, zero collisions
         10k / 1e6-LONG, the table pin, the PERF). `test_board` 242/0/15 (was 229/0/14). The splitmix64 cascade
         alternative was considered and set aside: Zobrist for the engine continuity + the incremental path
         (`zobrist_flip_bitstrings`), the cascade for a stateless-only future.

D-214 | 2026-09-18 | The `position_hash` return annotation corrected to the house style (Roberto):
         `-> Bitboard | BitboardArray` (was `-> Bitboard | npt.NDArray[np.uint64]`) — the Position-family pattern
         (`position_empties`, `position_collisions`, `legal_moves`, ...). Runtime-identical (pydantic does not validate
         returns); the doc follows.

D-215 | 2026-09-18 | The `position_hash` legacy parity fixture (Roberto's FFO-12 solve log): the game\_tree\_logger CSV
         of the C engine (21 columns; HASH/BLACKS/WHITES signed int64 decimals — the `bitboard_from_signed_int`
         representation). The FULL log (571\_141 rows, 89.7 MB) verified 100% by the session-38 scratch run (2.6 s): the
         PLAYER=0 rows (262\_285) match `position_hash(blacks, whites)` directly, the PLAYER=1 rows (308\_856) the one's
         complement (the D-213 bridge confirmed end-to-end against the engine), and `EMPTY_COUNT` == the popcount of
         `~(blacks | whites)` everywhere. The committed fixture is the lean deterministic sample (Roberto's call — the
         repo pack was 2 MiB, the full .gz was 17 MB): every 571st row + the root row, 1002 rows / 154 KB plain CSV
         (`ffo_12_log_sample.csv`), covering the full DFS span (ec 0..15, both players, leaf + internal nodes; the
         DFS-head alternative rejected — the first 1000 rows are all deep leaves). Tests: `TestPositionHashLegacyParity`
         (2 fast-tier tests: the fixture format pin, the full-sample parity). `test_board` 244/0/15 (was 242/0/15), full
         LONG 887/0/22 GREEN.

D-216 | 2026-09-18 | The `test_random_game_play_path_multi_generation` stub completed (Roberto's request — it was
         waiting for a position hash, now the D-213 `position_hash`): N = 10 paths played from the same ec = 20 start
         over ONE advancing prng stream (seed 141, no reseed). Two facts pinned: (1) every path lands EXACTLY on the
         target (`ec == 14` — 6 real moves; the game-over cut-off is out of reach this early); (2) the 10 final
         positions are pairwise DISTINCT via the `position_hash` duplicate check (the view-dependent hash: an equal hash
         means an equal position with the same player to move). The sketch fixed: `random_game_play_path` returns the
         `(position, ec)` tuple — unpacked before hashing. The suite counts are unchanged (the stub already ran as a
         vacuous pass): `test_random_game` 9/0/0, full LONG 887/0/22 GREEN.

D-217 | 2026-09-18 | The board.py typing doctrine (Roberto, after Nia's signature-audit proposal): the type aliases are
         SEMANTIC domain types, not dtype shortcuts — `Square` is an index into the 64-square space, `Bitboard` a set of
         squares, `Position` a game position — and the raw numpy forms are DELIBERATE wherever the value is not a domain
         concept. In particular the counts (`bitboard_count`, `position_empty_count`) return an ORDINAL (0..64), not a
         square index: typing them `np.uint8 | SquareArray` would be a semantic lie — they stay
         `np.uint8 | npt.NDArray[np.uint8]`. Likewise the int64 storage forms (`bitboard_from/to_signed_int`) and the
         generic `make_position` return (`Union[np.void, np.ndarray]` — scalar, 1-D or 2-D). Ruling: ALL the board.py
         public signatures are correct as they are — nothing to uniform; Nia's group-A proposal withdrawn. The
         convention recorded in the `board.md` Conventions.

D-218 | 2026-09-18 | The `random_game_play_path` double-pass fix (found reviewing the module for the dual-API campaign;
         Roberto approved the standalone mini-commit): `PASS_MOVE = Move(66)` was the stale pre-D-208 sentinel (UN) —
         `random_game_make_move` returns the pass as PA = 64 since D-208, so the `if move == PASS_MOVE` branches never
         fired and the double-pass game-over break was DEAD CODE: a random path encountering a game-over position with
         `ec > target_ec` looped forever (the single-pass continuation worked by accident — the loop re-entry plays the
         opponent's move; only the both-moveless case hangs). Fix: `PASS_MOVE = Move(64)`. Tests:
         `test_random_game_play_path_double_pass_game_over` (a both-moveless ec = 20 position, target 10: the loop
         terminates, the input view returns with its own ec — pre-fix it hangs) +
         `test_random_game_play_path_single_pass_continues` (a moveless mover + a 9-move opponent: the pass swaps the
         view, the game continues to the target). `test_random_game` 11/0/0 (was 9/0/0), full LONG 889/0/22 GREEN.

D-219 | 2026-09-18 | The `random_game_choose_move` dual scalar/array (the campaign step 1, the design approved by
         Roberto): `-> Bitboard | BitboardArray`, the D-140 dispatch (the 1-D guard, the 2-D (N,2) coercion via the
         PositionArray validator). The PRNG STREAM CONTRACT: the array call is bit-identical to the sequential scalar
         processing of the same positions with the same stream — one draw per non-empty legal set, no draw for a pass
         (the `choose_one_from_set64` empty sentinel). The trick: the legal sets are computed BEFORE any draw (they are
         draw-independent), so one `get_uint64_batch(k)` pre-draws for the non-empty elements and the prefix-sum slot
         map feeds the `prange` kernel (`_vectorized_choose_move`) whose per-element math (`_pick_one_from_set64`, the
         numba transcription of the prng pick: the SWAR popcount, r = (d >> 11) \* 2^-53, the c-th set bit) is
         bit-exact. The scalar path is UNTOUCHED (zero golden changes). Tests: `TestRandomGameChooseMoveArray` (6: the
         bit-equivalence regina + the stream-alignment probe, the scalar types, the 2-D coercion, the 1-D guard, the
         empty array, the rejections). `test_random_game` 17/0/0 (was 11/0/0), full LONG 895/0/22 GREEN.

D-220 | 2026-09-18 | The `random_game_make_move` dual scalar/array (the campaign step 2):
         `-> Tuple[PositionField | PositionArray, Move | MoveArray]`, the D-140 dispatch (the 1-D guard, the 2-D
         coercion). The array path is a pure COMPOSITION of the verified dual functions — the D-219 batch pick (the
         stream contract inherited verbatim) + the D-140 `position_flips` (a zero element swaps the players, a legal
         element flips; the drawn moves are always legal or pass, so the illegal branch never fires) — plus one numpy
         line for the codes: `np.bitwise_count(move - 1)` gives the bit index of a single-bit move AND, by the
         wrap-around of an empty move, 64 = PA (no kernel of its own). The scalar path is untouched. Tests:
         `TestRandomGameMakeMoveArray` (7: the bit-equivalence regina + the stream probe, the per-code position
         cross-check through the scalar flips, the initial-position code in {D3, C4, F5, E6}, the 2-D coercion, the 1-D
         guard, the empty array, the rejections). `test_random_game` 24/0/0 (was 17/0/0), full LONG 902/0/22 GREEN.

D-221 | 2026-09-18 | The pick-from-set single-source refactor (Roberto: "the PRNG logic and techniques must not be
         duplicated for the convenience of a numba kernel"): the pick technique moves ONCE into `prng.py` —
         `pick_one_from_set64(s, d)` (the scalar numba kernel: k = popcount, r = (d >> 11) \* 2^-53 — the
         `get_double_in_c0_o1` scalarization — c = floor(r\*k), the c-th set bit; returns (1 << p, p)) +
         `pick_one_from_set64_batch(sets, draws, slots)` (the vectorized form over an (N,) set array, fed by one
         `get_uint64_batch` pre-draw; the slots prefix map the caller computes). `choose_one_from_set64` and
         `extract_from_set64` now DRAW one `get_uint64` value and DELEGATE to the kernel (the single source; the numba
         scalar-return re-wrap restores the numpy dtypes at the Python boundary). `random_game` drops its transcribed
         kernels (`_pick_one_from_set64`, `_vectorized_choose_move`) — it is pure orchestration again (the legal sets +
         the needs/slot bookkeeping + the prng batch pick). THE LESSON, recorded honestly: the duplication had ALREADY
         produced a latent divergence — the D-219 kernel used the c0\_c1 scalarization constant (1/(2^53 - 1)) instead
         of c0\_o1's (1/2^53); the D-219 equivalence tests passed only because those draws did not straddle a floor
         boundary. The refactor makes that divergence class impossible. The behaviour is unchanged (the goldens hold:
         the 1000-pick frequencies, the 7-set golden, the extract golden). Tests: `TestPickOneFromSet64` (3: the
         kernel-method identity draw-for-draw over 7 sets x 100 draws, the batch equivalence + the stream alignment, the
         all-empty no-draw case). `test_prng` 22/0/0 (was 19/0/0), full LONG 905/0/22 GREEN.

D-222 | 2026-09-18 | The `random_game_play_path` dual scalar/array (the campaign step 3, the last):
         `-> Tuple[PositionField | PositionArray, np.uint8 | npt.NDArray[np.uint8]]` — the ec annotation is now honest
         (`position_empty_count` already returned np.uint8 at runtime; the ordinal doctrine D-217). The array case is
         the STEP ENGINE: per step, the legal sets of the current and swapped views (both draw-independent) classify the
         active lanes — plays\_a (the mover plays), plays\_b (the mover passes, the opponent plays), game\_over (the
         double pass: harvested, no draw, the input view returned) — one `get_uint64_batch` pre-draws for the needing
         lanes and `pick_one_from_set64_batch` + `position_flips` advance them; one shared `target_ec` for the batch;
         the termination is mathematical (every non-terminal step decreases a lane's ec by one) with a defensive 70-step
         bound. THE DESIGN FORK, resolved with the wave precedent: a multi-draw path CANNOT be both scalar-sequence
         bit-identical AND vectorized across lanes (the scalar processes a lane's WHOLE path before the next lane; the
         vector engine interleaves the lanes per step) — the array contract is the STEP-INTERLEAVED stream discipline of
         `hlp_wave` ("one draw per (lane, step)"), and the N == 1 array call IS bit-identical to the scalar call (with
         one lane the interleave collapses into the lane's sequential stream — pinned). Tests:
         `TestRandomGamePlayPathArray` (8: the scalar bridge over 4 paths, the whole-batch determinism, the ec contract,
         the as-is, the 2-D coercion, the 1-D guard, the empty array, the rejections). `test_random_game` 32/0/0 (was
         24/0/0), full LONG 913/0/22 GREEN.

D-223 | 2026-09-18 | The play\_path engine readability refactor (Roberto: "it is not understandable" — the D-222 array
         branch was a ~50-line inline blob inside the dispatch, with cryptic names (plays\_a / plays\_b / idx\_a /
         idx\_b) and the apply logic duplicated for the two groups): the engine is decomposed into three named,
         documented units — `_play_path_engine` (the step loop + the termination bound), `_play_path_step` (the lane
         classification with self-explanatory names: mover\_plays / mover\_passes\_opponent\_plays /
         double\_pass\_game\_over — and the advance), `_apply_picked_moves` (the masked `position_flips` on the lane
         subset, the current or the swapped view; the write-back is direct in both frames because position\_flips
         returns the NEXT player's view). The public function is a thin dispatch again (the house shape: the scalar
         branch inline, the array branch one line). ZERO behaviour change: the whole suite passes untouched (the
         single-lane scalar bridge, the determinism, the ec contract). `test_random_game` 32/0/0, full LONG 913/0/22
         GREEN.

D-224 | 2026-09-18 | The docstring discipline (Roberto, on the random\_game dual-campaign docstrings): a docstring
         explains WHAT — the observable contract (the semantics, the shapes, the stream/consumption promises) — never
         HOW (the mechanism: the needs computation, the batch feeding, the composition, the encoding formulas, the
         internal unit names). The mechanism lives in the mirror doc's Architecture section and in the code comments.
         The three random\_game public docstrings + the two engine helpers cleaned (the mechanism sentences dropped, the
         contracts kept); the mirror API lines aligned. PROMOTED to rules.md (the Docs section).

D-225 | 2026-09-19 | The `_EMPTY_MOVE_SET` module constant (Roberto's naming request, the approved proposal): the six
         `np.uint64(0)` literals of `random_game.py` — all meaning "the empty move set" (the pass signal of the pick
         domain, the batch kernel's no-pick value) — become the named module constant
         (`_EMPTY_MOVE_SET: Bitboard = Bitboard(0)`, the internal house style as `_mask_l` in board.py). NOT renamed:
         the `moves - np.uint64(1)` decrement operand in `make_move` (a different concept — the coding formula), the
         prng.py internals (the generic empty set of the pick domain, not move-specific), and the test literals (the
         goldens pin expected values). Zero behaviour change. `test_random_game` 32/0/0, full LONG 913/0/22 GREEN.

D-226 | 2026-09-19 | The random\_game docstring + engine style refinements (Roberto, four points): (1) NO D-XXX
         references in docstrings — a docstring explains how a function is used and how it behaves; the provenance lives
         in decisions.md, and only if fundamental in a `#:` code comment (the D-224 rule line extended); the campaign
         docstrings cleaned (random\_game.py, prng.py, the two test modules). (2) The "- never None" negation style
         dropped — a docstring states the current contract, not the negation of a past behaviour (the D-208 story lives
         in the history); the phrasing cleaned in the docstring, the mirror/test docs and the overview row (the
         assertIsNotNone pin stays in the test). (3) THE STRATEGIC INTENT, recorded: `random_game` is the intended
         REPLACEMENT for `hlp_wave` — a more readable, reusable, domain-anchored module (Roberto's intent from the
         beginning) — the docstrings and the mirror docs stop referencing hlp\_wave as the authority: the semantics is
         stated in domain terms (the lanes advance in LOCKSTEP; one draw per active lane per step, in element order).
         (4) The magic 70 of `_play_path_engine` replaced by the DERIVED bound:
         `max_steps = int(ec.max(initial=0)) - int(target) + 1` — every non-terminal step decreases a lane's ec by
         exactly one and the game-over step ends the lane, so a lane needs at most (ec\_start - target) steps plus one;
         the bound is computed from the input (the empty-batch edge handled by the reduction initial), the stall raises
         RuntimeError and never hangs. Zero behaviour change. `test_random_game` 32/0/0, `test_prng` 22/0/0, full LONG
         913/0/22 GREEN.

D-227 | 2026-09-19 | The play\_path PERF baseline + the profiling session (Roberto, before the optimization plan): the
         PERF test `test_perf_play_path_million_games_to_ec0` (print-only, PERF=1 gated) plays 1e6 games from the
         canonical start to `ec = 0` (the full random game) by the array engine and prints the wall time, the
         throughput, the draws and the harvest breakdown. THE BASELINE: 6.33s / 157,995 games/s; reached `ec = 0`:
         990,413; game-over lanes: 9,587 (0.96%; max stuck ec = 51). THE STUCK-LANE DIAGNOSIS (the scratch session): the
         outliers are REAL random-game behaviour, NOT an engine bug — the final positions are genuinely moveless (the
         legal sets = 0 on both views, verified) and the scalar baseline agrees (2,000 lanes: 19 game-over = 0.95%, the
         same max stuck ec = 51). THE PROFILE (the instrumented phase run over the 60 steps):
         `position_legal_moves` 0.875s (16.6%; 120 calls = 2 per step over the FULL array — the second, on the swapped
         view, is needed only for the PASS lanes), `pick_one_from_set64_batch` 0.857s (16.2%), `position_flips` 0.725s
         (13.7%), `make_position` 0.519s (9.8%; 231 calls, ~4 per step), `get_uint64_batch` 0.261s (4.9%; 60M draws),
         `position_empty_count` 0.167s (3.2%); the unattributed glue ~2.2s (~42%: the np.where chains, the masks, the
         copies — the ndarray.copy alone 222 calls / 0.283s). The pydantic overhead is negligible (~9ms total). THE
         OBSERVED WASTE for the plan: (a) the second legal\_moves over ALL lanes while only the pass lanes need it, (b)
         the legal\_moves also on the INACTIVE lanes, (c) ~6 full-array copies per step. The intervention plan is the
         next decision. `test_random_game` 33/0/1 (was 32/0/0).

D-228 | 2026-09-19 | The play\_path intervention 1 (Roberto's one-at-a-time plan, measured): the opponent's legal set in
         `_play_path_step` is computed ONLY on the pass-lane subset (the `mover_passes` lanes — rare mid-game), not on
         the whole batch; the D-227 profile showed the second full-array `position_legal_moves` (on the swapped view) as
         a top hot spot (16.6% of the wall, 2 calls per step). The zero-filled scatter keeps the same read semantics
         (`lms_opponent` is read only under the `mover_passes` masks). IDENTICAL results. THE MEASUREMENT (the 1M-games
         benchmark, the same seed): 6.33s / 157,995 games/s -> 5.68s / 176,100 games/s (-10.3% wall, +11.5% throughput);
         the harvest breakdown unchanged (reached ec=0: 990,413; game-over 9,587; the same max stuck ec = 51).
         `test_random_game` 33/0/1, full LONG 914/0/23 GREEN.

D-229 | 2026-09-19 | The play\_path intervention 2 (Roberto's one-at-a-time plan, measured): the mover's legal set in
         `_play_path_step` is computed ONLY on the ACTIVE lanes (the zero-filled scatter + the all-active fast path that
         computes it in place — with a uniform start all the lanes stay active, so the fast path keeps the same code
         path), and both classification computes run on the RAW fields via the public `legal_moves(mover, opponent)` —
         no `make_position` assembly for the classification (the D-228 pass-lane subset included:
         `legal_moves(opponent_field, mover_field)` = the legal set on the swapped view, the values identical). THE
         MEASUREMENT: the uniform 1M-games benchmark (the target 0) 5.68s -> 5.76s (+1.4%, the noise level — as
         predicted, the active fraction stays ~1 there); THE MIXED-EC BENCHMARK (the new scratch bench: the lanes at the
         start ecs 60/45/30/20/10/0, the target 20 — the active fraction drops 0.5 -> 0.33 -> 0.17 over the steps) 2.03s
         / 493,567 games/s -> 1.81s / 551,381 games/s (-10.8% wall, +11.7% throughput); the harvest breakdown unchanged
         on both. `test_random_game` 33/0/1, full LONG 914/0/23 GREEN.

D-230 | 2026-09-19 | The play\_path intervention 3 (Roberto's one-at-a-time plan, measured): the engine state is the RAW
         `(movers, opponents)` uint64 pair — copied ONCE from the input (the caller's array is never mutated), advanced
         in place by the steps (`_apply_picked_moves` writes the state directly: no per-group full copies; the ec via
         the inline `bitboard_count(~(movers | opponents))`), and assembled into the Position array once at the end. The
         `~4 make_position calls per step` of the D-227 profile drop to ~2 (the subset assemblies for the flips only),
         the ndarray.copy 222-calls charge disappears. THE MEASUREMENT IS INCONCLUSIVE ON THE WALL: the machine noise
         band is +-5-6% (the repeated runs 5.50-6.55s) and the structural saving (~5-8% theoretical) is buried in it;
         the PHASE-STRUCTURE comparison vs the D-227 profile is decisive: legal\_moves 0.875 -> 0.215s (the D-228/D-229
         wins), make\_position 0.519s/231 -> 0.320s/112 calls (-38%), position\_empty\_count -> the inline
         `bitboard_count` 0.058s (-65%), the ndarray.copy 222 calls GONE. The remaining hot spots after D-228/229/230:
         position\_flips ~15.7%, pick\_one\_from\_set64\_batch ~14.6%, the step glue (the masks + the np.where chains +
         the fancy indexing) — the fused-step-kernel option is the next plan item. Also: the scratch lms buffers typed
         `dtype=Bitboard` (the aesthetic, Roberto) and the stale "(70)" RuntimeError message of the D-226 leftover
         corrected. Zero behaviour change. `test_random_game` 33/0/1, full LONG 914/0/23 GREEN.

D-231 | 2026-09-19 | The play\_path intervention 3b — the scratch-buffer reuse (Roberto's idea, measured): the two
         legal-set scratch buffers are allocated ONCE in `_play_path_engine` and reused across the steps (the reads are
         covered by the same-step writes: every lane the masks read has been scattered this very step — the invariant
         pinned in the `_play_path_step` docstring). The all-active fast path returns a fresh result (the buffer unused
         there — forcing it would add a full copy); the subset paths scatter into the buffers. Zero behaviour change.
         THE MEASUREMENT: WITHIN THE NOISE on both benches (the standard 5.98s in the 5.50-6.55 band; the mixed 1.82s in
         the 1.71-1.87 band) — the honest verdict: no visible gain (the numpy allocator recycles the same pages; the two
         per-step np.zeros were a small slice of the glue). KEPT (harmless, the invariant documented) — revertible in
         minutes if Roberto prefers minimalism. `test_random_game` 33/0/1, full LONG 914/0/23 GREEN.

D-232 | 2026-09-19 | The FUSED STEP ENGINE + the board njit primitives (Roberto's approved endgame): (1) BOARD PROMOTES
         the two per-lane primitives as the PUBLIC njit API — `legal_moves_of(mover, opponent)` (the per-lane legal-move
         set, EXTRACTED from `_vectorized_legal_moves`'s loop body: the kernel calls it per lane — the single source,
         zero duplication) and `flips_of_move(mover, opponent, move)` (the domain-order wrapper over `_kogge_stone_mm`,
         `inline='always'`); both in `__all__`, pinned by `TestNumbaPrimitives` (the equivalence vs the batch/scalar
         paths). (2) RANDOM\_GAME rewrites the step as the FUSED two-pass engine: `_classify_step` (one prange pass: the
         legal sets via `legal_moves_of`, the classification masks, the pass lanes' opponent set in kernel) +
         `_advance_step` (one prange pass: the pick via prng's `pick_one_from_set64` on the pre-drawn slot, the flips
         via `flips_of_move`, the in-place state update) — the per-step numpy bookkeeping collapses to ~5 ops (the needs
         count, the cumsum/slots, one get\_uint64\_batch, the ec); `_apply_picked_moves` and the
         position\_flips/make\_position per-step assemblies are GONE. The draws remain ONE batch call between the passes
         (the stream contract unchanged — the classification must precede the draw, so the two-pass structure is forced
         by the bit-exactness). RESULTS BIT-IDENTICAL (all the pins hold: the N=1 scalar bridge, the determinism, the ec
         contract). THE MEASUREMENT (the 1M-games benchmark): the D-227 baseline 6.33s -> 2.57s (-59%, 2.46x; 389,546
         games/s; ~43ns per position-advance); the mixed-ec bench 2.03s -> 1.08s (-47%, 923,863 games/s); the clean
         best 2.34s / 427,118 games/s. THE PROFILE (the clean runs): `_advance_step` ~51%, `_classify_step` ~19%,
         `get_uint64_batch` ~12%, the numpy glue ~0 (the function calls 11,464 -> ~1,450; make\_position 1 call = the
         final). The per-advance ~39ns vs the hlp\_wave engine ~122-170ns (4x). `test_board` 246/0/15 (was 244/0/15),
         `test_random_game` 33/0/1, full LONG 916/0/23 GREEN.

D-233 | 2026-09-19 | The `_kogge_stone_lms` resurrection — the symmetric encapsulation (Roberto): the two per-lane
         primitives had two inconsistent strategies — `flips_of_move` wraps the private core `_kogge_stone_mm`, while
         `legal_moves_of` carried the geometry body directly (the D-232 extraction moved it out of the vectorized
         kernel's loop without preserving the historical private core; the exact historical body of `_kogge_stone_lms`
         predates the workspace bootstrap and is not recoverable from our git — only the name survives in the original
         TODO comment of the staged board.py). RESURRECTED: `_kogge_stone_lms(generator, propagator, blocker)` — the
         private njit core (`inline='always'`, the same decorator as `_kogge_stone_mm`) with the CURRENT proven body
         parameterized on the three Kogge-Stone roles (generator = mover, propagator = opponent, blocker = empties);
         `legal_moves_of` is now the thin domain wrapper (`_kogge_stone_lms(mover, opponent, ~(mover | opponent))`) —
         the pair legal\_moves\_of/\_kogge\_stone\_lms mirrors flips\_of\_move/\_kogge\_stone\_mm. Zero behaviour change
         (the same inlined machine code). `test_board` 246/0/15, the 1M-games benchmark unchanged (2.58s), full LONG
         916/0/23 GREEN.

D-234 | 2026-09-19 | The `random_game.md` mirror rewrite (Roberto: the doc told the campaign instead of the module):
         rewritten in the board.md style — the incipit states what the module IS (the random-game module: the pick, the
         execution, the batch path engine; the corpus generator and the intended hlp\_wave replacement); the API as the
         family TABLE (the pick / move / path contracts) with the family-wide stream contract as the paragraph; the
         Architecture as the layered description (the scalar compositions, the batch single-pick paths, the fused
         two-kernel step engine); the Verified invariants with the test pins; the Conventions rewritten to the real ones
         (the stream discipline, the single-source composition, the in-place arrays, the goldens as literals, the
         dual-API guard); the Integration updated. Only the state, no history: zero D-numbers, zero campaign narrative
         (141 -> 104 lines, net -37). The commit also carried the decisions.md entry-order repair (the D-217 entry had
         been inserted after D-233 by an anchor mistake; moved to its chronological place).

D-235 | 2026-09-19 | The ideas review + the house format (Roberto's session): (1) THE FORMAT — notes/ideas.md and
         notes/overview.md adopt the D-209 wrap (~120 chars/line, a 9-space continuation indent, a blank line before
         every entry, code spans for paths / identifiers); in overview.md the PROSE only — the Source/Test tables stay
         one physical line per row (D-116/D-117). The re-wrap was generated by a scratch wrapper that is code-span-aware
         and preserves the ORIGINAL separators (the D-209 trap: a mid-token or mid-span break must not be re-joined with
         an inserted space — the `finally`/cleanup and the `import reversi` cases), and verified by a content
         fingerprint (the joined prose blocks identical: 45/45 in overview, 12/12 in ideas): zero words added, removed
         or reordered; the re-wrap also healed the 4 overview lines whose code span was split across the break. (2) THE
         IDEAS SPLIT — notes/ideas.md is now the OPEN backlog only; the new notes/ideas-closed.md is the CLOSED record
         (status done | dropped), a compacted entry per idea (the statement + the D-pointer + the outcome). 12 entries
         moved: I-001, I-002, I-005, I-011, I-012, I-013, I-015, I-016, I-017 (done) + I-004, I-006, I-008 (dropped).
         The campaign narratives (up to 52 lines: I-013, I-016, I-017) were compacted: the history stays in this log +
         the journal, the file is the I-NNN index into it (the D-117/D-207 principle applied to the backlog). 310 -> 52
         lines (ideas.md) + 68 (ideas-closed.md). (3) THE STALE FIXES — I-017 in-progress -> done: the campaign closed
         at D-189 (2026-09-13, the T19) and the progression had never been written back; I-006 (the legacy migration
         debt) CLOSED: the port campaign is complete (D-119) and no legacy call site survived (the only `.names()` is
         prose in `docs/src/reversi/mobility.md`); I-004 (the reserved placeholder slot) RETIRED; I-009 / I-010
         UNBLOCKED: their blocker ("the pipeline module is not in the workspace yet") is dead — the pipeline is complete
         (18 levels); I-003's issue pointer corrected (`notes/board.md` -> `docs/src/reversi/board.md`); I-007 VERIFIED
         still open: the pipeline landed without the column-labelling helper and `wrk_feature_analysis` re-derives the
         (name, col\_start, col\_end) map locally. (4) THE RULES — promoted in rules.md: the ideas bullet (the two
         files, the status legend idea | follow-up | in-progress, the format, the closing procedure in the same commit
         as the closing decision) + the overview bullet (the prose width) + the reference-convention line (I-NNN ->
         ideas.md / ideas-closed.md). The overview Index gained the notes/ideas-closed.md line. Notes-only: no source,
         doc or test touched. OPEN FINDINGS (not fixed here, to be decided): `test_hlp_wave.py` has NO mirror doc
         (D-007); the `test_hlp_gate.py` table row points at the removed gate test; the `wrk_generate` Doc cell reads
         `.py` instead of `.md`; the overview Index misses decisions\_001.md, analytical\_properties\_of\_features.md
         and performance\_baseline.md.

D-236 | 2026-09-19 | The overview / mirror repairs (Roberto's "sistemali adesso", the findings of the D-235 review): (1)
         the MISSING MIRROR — the new `docs/src/reversi/test/test_hlp_wave.md` (the D-007 gap: 45 test modules, 44
         mirrors): the test-doc variant (H1 + the intro, Coverage, Goldens pinned, Conventions, Integration) in the
         sibling style, no `> State:` line (none of the migrated mirrors carries it yet); it pins what the module
         actually contains — the batch draw vs the reference PRNG, the W=1 trajectory vs the in-test scalar loop, the
         run integrity + the determinism, the LONG 1e6 benchmark. (2) The `test_hlp_gate.py` ROW removed from the Test
         files table: the test module (and its mirror) went away with the gate, only the overview row survived — a
         pointer into the void (docs\_rules §5.4). (3) The two `.py` Doc cells (`wrk_generate`, `hlp_gradient`) ->
         `.md`. (4) The `test_hlp_wave` ROW corrected: the State cell still described the removed pick-kernel / harvest
         / phase-invariance tests and the Suite cell read 14/0/2 — the current module is 2 classes / 4 tests, so the
         cell is now `3/0/1 (LONG: 4/0/0, the 1e6 benchmark)` and the Doc cell points at the new test mirror. VERIFIED:
         `.venv/bin/python -m unittest reversi.test.test_hlp_wave` -> Ran 4 tests, OK (skipped=1, the LONG gate), 0.844
         s. (5) The overview Index completed with the three missing files (decisions\_001.md,
         analytical\_properties\_of\_features.md, performance\_baseline.md). (6) AGENTS.md: the D-122 guard's
         pointer I-001 -> notes/ideas-closed.md and the Layout line. (7) THE WHOLE TABLES RE-VERIFIED against the tree:
         48/48 source rows and 46 test rows (the 45 `test_*.py` modules + the `paths` helper), every row resolving to a
         real file, every Doc cell a real `.md`, every source and test module carrying its mirror (the D-007 gap count
         is now zero). Notes + one new mirror doc: no source, test or probe touched.

D-237 | 2026-09-19 | The 120-char format extended to the whole notes/ tree (Roberto: "usiamo il wrapper anche su
         probe\_rules, naming, log\_rules, i log\_xxx, docs\_rules, decisions\_000, decisions\_001") + the rules.md
         synthesis + the systematic Suite audit. (1) THE WRAPPER — the scratch tool `rewrap_notes.py`: the house
         re-wrapper (greedy fill to 120 chars, code-span aware, the per-file block grammar — headings / tables / fences
         verbatim, bullets and numbered items with their own indent, the decision entries with the 9-space continuation
         and the `|` rationale fields) with the D-209 mid-token rejoins: 280 across the volumes (paths, identifiers and
         code spans broken by the old 68-char wrap). The rejoin rule is conservative after the false-positive analysis:
         `_` and `-` always continue a token (except after a dunder), `/` only when the next fragment is a digit, a
         filename (a dot), a slash-list or an id — `probes/ (gated...` and `logistello-papers/ stays...` are NEW
         phrases, not rejoins. The wrapper is IDEMPOTENT and never manufactures the breaks it heals: a line never STARTS
         with a token the grammar would read as a new block (a bullet, a pipe, a numbered item, a `D-NNN | ` header) and
         never ENDS with a token the rejoin rule would glue to the next line. VERIFICATION: a content fingerprint per
         file (backticks stripped, the blocks joined with the rejoin rule, the token lists compared) — 12/12 files
         CONTENT OK, plus the idempotence; the only lines left over 120 are 3 session headings and 1 unbreakable glued
         pair (log\_000, 122 chars). (2) THE FILES — probe\_rules 130 -> 92, naming 72 -> 60, log\_rules 53 -> 35 (+ the
         ~120 statement), docs\_rules 139 -> 100, log\_000 2031 -> 1190, log\_001 3051 -> 1780, log\_002 2210 -> 1177,
         log\_003 353 -> 206, decisions\_000 4194 -> 2226, decisions\_001 2101 -> 1007. The journals keep their rigid
         2/4-space bullet indentation; the 13 decisions\_000 header lines carrying a stray leading space are normalized.
         (3) THE RULES SYNTHESIS — notes/rules.md 232 -> 138 lines (the ~150 budget): the history removed (the NOTES.md
         rename, the R1-trap D-numbers, the ULP measurement detail), the duplications removed (the dependency list lives
         in the overview Environment; the pre-commit and the suite tiers merged into one bullet; the journal bullet
         points at log\_rules.md), the STALE numbers dropped (the "586 tests" default tier, "machine order 1-14", "the
         15-level chain" — the counts change per commit, the D-207 lesson), and the GLOBAL format rule added (every
         notes/ Markdown is wrapped to ~120 chars/line); every rule in force kept its D-pointer. (4) THE SUITE AUDIT — a
         per-module run of the runner's modules (LONG=1, live DB) against the overview's Suite cells: 3 modules were
         stale (test\_board 229/0/14 -> 246/0/15, test\_client 6/0/1 -> 7/0/1, test\_hlp\_random\_play 23/0/0 -> 10/0/0
         — the G1 burial removed tests and the cells were never re-pinned) and 3 more cells were fixed (the
         hlp\_random\_play and client source rows, hlp\_wave 3/0/0 -> 3/0/1 + LONG 4/0/0); the two stale State cells
         (test\_board, test\_hlp\_random\_play) were rewritten to the current content. (5) The overview also got the
         escaped `\*_for_current_level` asterisk (the stray-italics fix) and the 121-char Index line fixed. Notes-only:
         no source, test or probe touched. The docs/ mirrors are the FOLLOW-UP (the second commit: the same wrapper over
         ~100 files + the docs\_rules.md statement).

D-238 | 2026-09-19 | The docs/ mirrors to the house format (the second commit of the D-237 reform; Roberto: "Sono da
         fare anche i docs ... ma li farei in un secondo commit, dopo"): the same wrapper over the 94 mirror docs (the
         source mirrors + the test mirrors) — ~120 chars/line, the API / Coverage / Goldens tables kept one physical
         line per row, 60 mid-token rejoins. 8387 -> 5785 lines (e.g. state\_machine.md 155 -> 104, binio.md 120 -> 88,
         prng.md 111 -> 75, board.md 188 -> 188 — it was already wide). docs\_rules.md carries the statement (the
         header: "The prose is wrapped to ~120 chars/line (D-238); the tables stay one physical line per row").
         VERIFICATION: 94/94 CONTENT OK by the content fingerprint + idempotence. The docs\_rules §2 `> State:` header
         and §8 (the migration state) are untouched: the schema migration is still pending — no mirror carries the State
         line yet. No source, test or probe touched.

D-239 | 2026-09-19 | The mirror-format audit + the tokenizer regression fix (Roberto: "verifichiamo il formato di tutti
         i docs ... a vista mi pare gia corretto"). (1) THE TOOL — the new scratch auditor `docs_format_audit.py` checks
         every docs/\*\*/\*.md against docs\_rules.md: the H1 against the source path, the `> State:` line, the
         prescribed sections and their order (the source variant vs the test-doc variant), the §4 forbidden patterns
         (provenance narrative, campaign tags, FIXED/RESOLVED lists, line-count deltas, the global suite status, report
         tenses), the size budget (60-120; the hubs 150-200), the 120-char width, the trailing whitespace, the split
         code spans and the per-table ragged rows. Two of its checks were FALSE POSITIVES and were fixed: a
         `FIXED`/`RESOLVED` used as an adjective (the FIXED axis ranges, the mover is FIXED) is not a FIXED list, and a
         `\|` escaped pipe is not a cell separator. (2) THE REGRESSION (found by the audit, MINE): the D-237/D-238
         wrapper tokenizer recognized a code span only when it started at a token boundary, so a span glued to
         punctuation (`(`dict[c] = min(c, flip(c))`,`) could be split across lines — `pattern.md` was damaged. FIXED:
         the tokenizer treats the maximal non-space run CONTAINING a closed span as one atomic unit; the wrapper also
         HEALS a span broken across lines (a soft break renders as a space — what the reader sees) and REFUSES to emit
         more split spans than it found (the `SPAN REGRESSION` check). RESULT: the split code spans across notes/ +
         docs/ went 768 -> 0 (the fences excluded) — a pervasive defect of the old 68-char wrap, not only the
         regression. 36 files rewritten (the heal + the consequent re-wrap): +293/-280, content verified by the
         fingerprint on every file. (3) THE AUDIT RESULT (94 mirrors): 94/94 miss the `> State:` line of §2 — the §8
         migration was never executed (the RETIRE is D-240); `lm/wrk_positions.md` carries a BROKEN `## Architecture`
         heading merged with its first content line; `lm/hlp_gate.md` misses 4 sections; `lm/wrk_config.md` misses Open
         issues; `tools/prng.md` uses non-standard section names (What it is / How it works / Invariants);
         `lm/hlp_gradient.md` and `test/test_logistic_model.md` carry an extra section; 3 docs carry a ragged table (an
         unescaped `|` inside a cell: `model_weights`, `test_lm_worker_full_chain`, `test_wrk_plot`); the size budget is
         out in 6 files (hlp\_plot 150, hlp\_gradient 134, hlp\_config\_schemas 128 above the 120 cap; state\_machine
         105, logistic\_model 118, pattern 133 below the hub floor of 150). The punctual repairs are the D-240. Notes +
         docs only: no source, test or probe touched.

D-240 | 2026-09-19 | The §2 `> State:` line RETIRED + the punctual mirror repairs (the D-239 audit findings; Roberto:
         "Ritira la regola: semplifica docs\_rules"). (1) THE RETIREMENT — docs\_rules §2 is now "Header (fixed, 2
         parts)": the H1 + the what-it-is paragraph, nothing else (no date, no D-number, no commit hash, no suite count,
         no "Analysis date" / "brought in by" / "post D-xxx" line). Rationale: the metadata the line carried already
         lives where it belongs (the last decision in decisions.md, the last commit in git, the suite counts in the
         overview's cells) and keeping a copy current was a per-file tax that no commit ever paid — 94/94 mirrors
         carried no State line. The §8 migration-state section is deleted with it (the schema is in force). rules.md's
         Docs bullet follows in the same commit. (2) THE PUNCTUAL REPAIRS — `lm/wrk_positions.md`: the BROKEN
         `## Architecture` heading (it had swallowed its first content line) split; `lm/hlp_gate.md`: the 4 missing
         sections written (Architecture, Verified invariants, Open issues, Conventions — the invariants VERIFIED by
         running the loader: the rlm\_00 intercept present, 6 features / 5 blocks, the first block at column 1, the
         blocks contiguous, `col_end - col_start == n_inst` for every feature); `lm/wrk_config.md`: the Open issues
         section (`None.`); `tools/prng.md`: the section names normalized to the schema (What it is folded into the
         header, How it works -> Architecture, Invariants -> Verified invariants, plus Open issues and Conventions with
         the uint64 typing contract); `lm/hlp_gradient.md`: the extra `## Performance (the A2050 production scale)`
         section FOLDED into Conventions (the production choice + the study pointer; the measurement table dropped — §3
         fixes the section set and the numbers live in notes/analyses/optimize\_performance.md; RESTORABLE on request);
         `test/test_logistic_model.md`: the extra `## Testbed design` section folded into Conventions; the 3 ragged
         tables fixed by escaping the pipes inside the cells (`model_weights` the `str \| None` unions,
         `test_lm_worker_full_chain` the quoted `"Loss (MSE/2) \| ... \| ..."` console line, `test_wrk_plot` the
         `\|residual\|` notation — the GFM rule: `\|` renders as `|` even inside a code span). (3) ALSO FIXED, found
         while retiring §2: the D-237/D-238 wrapper had re-wrapped the FENCED CODE BLOCKS (the ASCII diagrams of
         board.md / pattern.md / logistic\_model.md and the §2 example were mangled — the lines joined, the indentation
         stripped). The fence state machine is fixed (a fenced line is a Verbatim block, never wrapped) and the damaged
         files were restored verbatim from the pre-reform content. (4) THE AUDIT AFTER: 83/94 mirrors with no finding;
         the 11 left are SIZE only (hlp\_plot 150, pattern 144, hlp\_config\_schemas 128, logistic\_model 123,
         hlp\_gradient 122 above their cap; state\_machine 105 below the hub floor of 150; hlp\_gate 50, paths 53,
         wrk\_generate 56, wrk\_effect\_size 59 just under the 60 floor) plus the single over-120 line
         (`wrk_vld_positions.md:25`, an unbreakable 111-char code span). The size budget is a §5 target: trimming is a
         content call, left open. Notes + docs only: no source, test or probe touched.

D-241 | 2026-09-19 | The size-budget condensation (Roberto: "facciamo un riassunto dei documenti troppo grandi"): the
         three mirrors over the 120-line cap condensed to the budget — `lm/hlp_plot.md` 150 -> 119,
         `lm/hlp_config_schemas.md` 128 -> 115, `lm/hlp_gradient.md` 122 -> 120. WHAT WAS CUT (all of it
         rule-compliant): (a) the LINE-NUMBER references (docs\_rules §3: the appendix with line numbers is OPTIONAL and
         OFF by default — `L28-41`, `L69-112`, `L124-145`, `L410-418`, `the hlp_indexes L166 class`, `(L104)`); (b) the
         DEFECT and RENAME narrative (§4: "the stale-label bug", "the png2 trap", "the labels were NOT swapped", "the
         two 'Fitted' titles renamed", "the bare '(Y)' is gone from every label", "it used to cover", "the R script
         computed the skewness/kurtosis numerically", "is what it replaced"); (c) the CAMPAIGN TAGS in the prose (§4:
         "the P4", "the P6", "the ODP-1"); (d) the redundant restatements (the axis rulings repeated in the header, in
         the constants bullet and in every builder; the level-chain enumeration in the hlp\_gradient header; the 20
         one-test-per-bullet invariants of hlp\_config\_schemas merged into 10 thematic bullets that keep every test
         name). NOTHING CONTRACTUAL WAS LOST: the API tables are intact, every pinned test/probe name is kept, and 14
         literals were re-derived against the sources (the defaults `dpi` 150 / `cache_files_prefix` /
         `client_check_tol` 1e-8 / `total_positions` 1e7 / `seed` 42 / `ec` 20, the plot seeds 42/43, the KDE cap 100k,
         the axes 64/72/8, `_HP_BLOCKS` 8) — all confirmed. THE AUDIT AFTER: 86/94 mirrors with no finding; the 8 left
         are UNDER the floor (hlp\_gate 50, paths 53, wrk\_generate 56, wrk\_effect\_size 59 against the 60 floor;
         logistic\_model 123, pattern 144, state\_machine 105 against the 150 hub floor) plus the single over-120 line
         (`wrk_vld_positions.md:25`, an unbreakable 111-char code span). A doc BELOW the floor is not a defect (§5: the
         floor catches a doc that OMITS its module), so those stay open as a content call. Notes + docs only: no source,
         test or probe touched.

D-242 | 2026-09-19 | I-003 executed: the NAMED MOVE-CODE CONSTANTS (Roberto's plan approval: "MOVE\_PA / MOVE\_NA /
         MOVE\_UN"). (1) THE CONSTANTS — board.py gains `MOVE_PA: Move = Move(64)`, `MOVE_NA = Move(65)`,
         `MOVE_UN = Move(66)` (public, in `__all__`, placed after `__move_max_value__` with the domain comment). The
         `Move` type (np.uint8) is the domain type (the D-217 doctrine), and the values are pinned by the
         `move_from_str` vocabulary (PA/NA/UN). (2) THE SITES — the bare literals replaced: board.py
         `position_make_move` (the scalar PASS branch + the two range guards + the array guard, whose messages are now
         built from `int(MOVE_PA)` so they cannot drift), the `_vectorized_make_move` kernel branch,
         `position_is_move_legal` (the pass check + the `> MOVE_PA` guard), the kernel comment; `random_game.py` (the
         `Move(64) if idx == -1` sentinel + the local `PASS_MOVE` removed, both via the imported `MOVE_PA`);
         `lm/hlp_wave.py` (`PA: int = 64` -> `PA: np.uint8 = MOVE_PA`, the single source, still public). (3) THE
         SQUARE-COUNT 64 — `position_final_value`'s `ec = 64 - popcount` now uses the existing `__square_max_value__`: a
         different domain, and the plan flagged the ambiguity. (4) THE TWO DOMAINS — the flips' pass is a ZERO BITBOARD
         (not `MOVE_PA`): the `_vectorized_flips` `move == 0` branch is untouched, and board.md's Conventions now states
         the distinction. (5) THE PINS — the new `TestMove::test_move_constants` pins `MOVE_PA/NA/UN` to 64/65/66 AND to
         `move_from_str('PA'/'NA'/'UN')`: the literal anchor, because the rest of the suite now uses the names (a typo
         in a constant would otherwise pass); the stale "open decision R3 (I-003)" comment in `test_move_as_bitboard` is
         replaced by the documented-wrap note (R3 was already resolved at D-018). (6) THE DOCS — board.md (the API table
         row + the move\_as\_bitboard row + the Conventions bullet), hlp\_wave.md (`PA` re-exported), test\_board.md
         (the Coverage table rebuilt: the line numbers dropped per docs\_rules §3 and the counts corrected — 50 classes
         / 247 tests, the doc claimed 43/193), the overview (the board.py row + the test\_board Suite cell 246 -> 247).
         VERIFICATION: `test_board` 247/0/15 + `test_random_game` 33/0/1, LONG 917/0/23 GREEN, and the 1e6 G0 benchmark
         BIT-EXACT (28065 dead lanes, 1e6 harvested) — the stream contract is untouched. I-003 -> done
         (ideas-closed.md).

D-243 | 2026-09-19 | I-018 step 1-2: VALIDATE becomes the owner of the validation residuals (Roberto's plan approval:
         the complete scope, CLIENT\_CHECK consumes the published series, the records as a list of dicts). (1) THE DATA
         MODULE — `hlp_validate` now returns a `ValidationResult` dataclass (the 7-key `metrics` + the f64 `y_pred` /
         `rn_y` series) instead of a bare dict, and gains the pure kernel `top_outliers(rn, k=20)` (the stable argsort:
         a tie keeps the lower index first). The forward pass runs ONCE: before, `validate_model` computed `rn_y` and
         DISCARDED it. TWO arithmetic paths, deliberately: the metrics keep the original f32 arithmetic (their goldens
         are pinned AND embedded in the v2 model file — the first attempt unified them and the chain golden `vld_mae_y`
         moved by 1.2e-08 rel, caught by `test_lm_worker_full_chain`), while the published series are the f64 views,
         bit-identical to what PLOT and CLIENT\_CHECK computed before, so the publication moves NO number. (2) THE
         WORKER — `wrk_validate._up` publishes `ctx.vld_y_pred` / `ctx.vld_rn` / `ctx.vld_outliers` (the 20 records as
         raw values: index, mover, opponent, game\_value, fitted, residual) next to the unchanged `ctx.vld_metrics`, and
         LOGS the D-150 top-20 report (the same 21 lines, so the chain pins survive the move); `_down` clears the four
         fields. The four ctx fields are pre-declared (the D-099 idiom). (3) THE REPORT MOVES — the block leaves
         `wrk_plot` (which becomes a pure rendering level; its validation pass goes at step 4) and the D-150 test moves
         from `test_wrk_plot` to `test_wrk_validate` (the idea's own requirement), where a hand-computed 50-position ctx
         pins the ranking AND the tie-break. (4) THE PROBE — `verify_validate` updated: A1 (the 3-name `__all__`), A9
         (the `_down` clears FOUR fields, not one), A12 (the 7 keys inside `ValidationResult`), B4 (the new ctx fields),
         D2. TWO STALE PROBE PINS FOUND AND FIXED (pre-existing, not from this change — verified by re-running the probe
         on the pre-change tree): C5 pinned "no rlmwf\_12 file" when the slot numbering had shifted (12 is GENERATE now,
         VALIDATE is 14) and A11 repeated the same stale slot in its message. (5) THE DOCS — `hlp_validate.md` and
         `wrk_validate.md` rewritten to the state (they carried line numbers, the "12th step" and the rlmwf\_12 slot:
         now the 14th step, no line numbers, the I-018 API), `test_wrk_validate.md` (9 tests) + `test_wrk_plot.md` (9,
         the moved test noted), the overview rows (the Suite cells 5 -> 9, 10 -> 9, the stale `test_lm_worker_validate`
         name fixed). VERIFICATION: LONG 920/0/23 GREEN (+3 tests), the 1e6 G0 bit-exact (28065 dead lanes), the chain
         pin moved to the VALIDATE section with the published-series order asserted, `probes/verify_validate.py` ALL
         CHECKS PASSED. The training-side duplication (ANALYTICS -> PLOT) and the PLOT/CLIENT\_CHECK consumption are the
         next steps. THE FULL PROBE SWEEP (the probe\_rules §5.2 campaign rule) reports 9/22 RED — ALL PRE-EXISTING and
         all of the same family: the step / slot pins went stale when the I-017 reordering (D-157) and the two new
         levels (FEATURE\_ANALYSIS step 3, EFFECT\_SIZE step 6) shifted every subsequent step number and cache slot. The
         failures: verify\_analytics (step 12/13, rlmwf\_12), verify\_design\_matrix (rlmwf\_06, the 7-level pipeline),
         verify\_gradient (the step pins + rlmwf\_07\*/08\*), verify\_hlp\_indexes (rlmwf\_02\_FEATURES),
         verify\_optimize (current\_step == 9), verify\_wmaps (rlmwf\_05, the 6-level pipeline), verify\_wrk\_features
         (a line count), verify\_wrk\_positions, verify\_zed (DESIGN\_MTR = 6 / ZED = 7, rlmwf\_07\_ZED). They are
         INDEPENDENT of I-018 (no step moved): the re-pin is the next step of this campaign, required by the sweep rule
         before the campaign close.

D-244 | 2026-09-19 | The stale probe re-pin + the mirror-doc re-pin (the sweep debt found by the D-243 campaign sweep;
         Roberto: "ripinna i 9 probe adesso"). THE CAUSE: the step and cache-slot pins of 9 module probes — and the same
         numbers in the mirror docs that cite them — stayed frozen at the pre-I-017 numbering: the reordering (D-157:
         FEATURES to step 2) and the two new levels (FEATURE\_ANALYSIS step 3, EFFECT\_SIZE step 6) shifted EVERY
         subsequent step number and cache slot. THE EMPIRICAL GROUND TRUTH (a full rlm\_02 chain run, the files it
         actually writes): CONFIG 1 (no cache, D-142), FEATURES 2 (pure), FEATURE\_ANALYSIS 3, POSITIONS 4, INDEXES 5,
         EFFECT\_SIZE 6, WMAPS 7, DESIGN\_MTR 8, ZED 9 (pure), GRADIENT 10 (pure), OPTIMIZE 11, GENERATE 12,
         VLD\_POSITIONS 13, VALIDATE 14 (pure), ANALYTICS 15 (pure), SAVE 16, CLIENT\_CHECK 17, PLOT 18. THE PROBES (9):
         verify\_analytics (VALIDATE 12 -> 14, ANALYTICS 13 -> 15, the no-cache slot 12 -> 15, the file set, the numeric
         move\_to\_step(12) -> (14)), verify\_design\_matrix (WMAPS 5 -> 7, DESIGN\_MTR 6 -> 8, rlmwf\_06 -> rlmwf\_08),
         verify\_gradient (ZED 7 -> 9, GRADIENT 8 -> 10, the no-cache slots 07/08 -> 09/10), verify\_hlp\_indexes
         (POSITIONS 03 -> 04, INDEXES 04 -> 05, plus the rlm\_00 FEATURE\_ANALYSIS cache file that the D-175 opt-in
         added and the probe never learned about), verify\_optimize (GRADIENT 8 -> 10, OPTIMIZE 9 -> 11, the no-cache
         slots 02/07/08 -> 02/09/10), verify\_wmaps (INDEXES 4 -> 5, WMAPS 5 -> 7, rlmwf\_05 -> rlmwf\_07),
         verify\_wrk\_features (the line count 197 -> 202), verify\_wrk\_positions (POSITIONS 03 -> 04), verify\_zed
         (DESIGN\_MTR 6 -> 8, ZED 7 -> 9, the no-cache slot 07 -> 09, and the F1 LMContext index pin shifted by
         the I-018 ctx fields). THE DOCS (the probe\_rules §5.4 same-commit rule): the same numbers re-pinned in the
         mirror docs that cite them — 39 slot substitutions (rlmwf\_03\_POSITIONS -> 04, 04\_INDEXES -> 05, 05\_WMAPS ->
         07, 06\_DESIGN\_MTR -> 08, 07\_ZED -> 09, 08\_GRADIENT -> 10, 10\_GENERATE -> 12, 11\_VLD\_POSITIONS -> 13)
         across 15 files, plus the no-cache slot references (12 -> 14/15, 15 -> 16, 16 -> 17/18) and the stale step
         prose ("the 13th step", "the 9-level chain", "17-level pipeline shape", the WMAPS=5/DESIGN\_MTR=6 pins, the
         FEATURE\* slot 03 -> 02) in ~20 files. TWO STRUCTURAL NOTES: (a) the probes' index-based content pins (tc[i] ==
         '...') are brittle by construction — the re-pin had to re-derive the indices, not only the values; (b)
         verify\_hlp\_indexes left a stale base dir under build/tmp when a run crashed, and the next run failed on a
         file list polluted by the old run (the probe cleans at exit — a crashed run does not). VERIFICATION: the FULL
         sweep is GREEN again (22/22 probes), LONG 920/0/23 GREEN, the 1e6 G0 bit-exact, the mirror-doc audit at 85/94
         with the same 9 pre-existing size findings. The I-018 steps 3-4 follow.

D-245 | 2026-09-19 | I-018 step 3: CLIENT\_CHECK consumes the published validation series. THE CHANGE: the worker no
         longer re-derives the in-memory reference — `_validation_residuals_y` (the A1a re-computation of the
         hlp\_validate forward pass: compute\_indexes + the per-instance col\_offsets + the gather + the sigmoid + the
         z2y affine) is GONE, and `rn_ref = ctx.vld_rn` (the series VALIDATE publishes, D-243). The `sigmoid` import
         goes with it (the worker does no numerics). THE SEMANTIC: the check still validates the SAVE artifact against
         the pipeline's own validation result — it now compares the FILE residuals against the PUBLISHED series instead
         of against a local re-derivation of the current in-memory state. The D-148 intent is preserved and sharpened:
         the module's own comment already said "this IS the validation's own residual", and the single derivation makes
         it literally true. THE CONSEQUENCE ON THE TESTS (2 re-shaped): `test_up_diverged_weights_raise` and
         `test_tolerance_is_read_from_config` injected the divergence by perturbing `ctx.w_dense` AFTER writing the file
         — a scenario the published snapshot cannot see (the reference no longer follows the mutated state). They now
         perturb FIRST and write the file AFTER, so the FILE diverges from the series: the same magnitude (~1.959e-01),
         the same assertions, the scenario re-expressed in the new contract's terms. VERIFICATION:
         `test_wrk_client_check` 6/0/0, the full-chain suite green (the A2030 CLIENT\_CHECK pin "max
         difference 0.000e+00" holds — the published series is bit-identical to the old re-derivation, as D-243 proved),
         LONG 920/0/23 GREEN, `probes/verify_logistic_model.py` ALL CHECKS PASSED. THE DOCS: `wrk_client_check.md`
         rewritten to the state (it carried line numbers, "the 16th active level (step 15)", the A1a re-derivation and
         "17 active levels"), the test mirror (the divergence scenario) and the overview row. Step 4 (the ANALYTICS
         training publication + the PLOT PlotData assembly) follows.

D-246 | 2026-09-19 | I-018 step 4: PLOT becomes a pure rendering level (no forward pass at all). (1) THE TRAINING SIDE —
         `hlp_analytics.compute_training_dense_metrics` now returns a `TrainingDenseResult` dataclass (the 4-key metrics
         dict + the f64 `rn_y` series) instead of the bare dict, exactly as `validate_model` does since D-243;
         `wrk_analytics._up` publishes `ctx.train_dense_rn` (the field pre-declared, the `_down` clears it). The
         arithmetic is safe by construction here: `rn_y = y_pred - y_true` with `y_true` already f64 promotes the f32
         prediction exactly, so the series IS the rounded-lossless f64 view PLOT computed before — no split needed
         (unlike the validation side, where the metrics' f32 path had to be preserved). (2) THE ASSEMBLY —
         `hlp_plot.collect_plot_data` no longer runs ANY forward pass: it assembles the PlotData from `ctx.game_values`
         + `ctx.train_dense_rn` (ANALYTICS) + `ctx.vld_y_pred` / `ctx.vld_rn` (VALIDATE) + `ctx.vld_game_values`. The
         `sigmoid` import leaves hlp\_plot (nothing computes there anymore). (3) THE PROOF THAT NOTHING MOVED — the
         strongest possible: the PNG byte-determinism golden (`test_wrk_plot::test_parity_png_golden`, the sha3 of the
         rendered figure) still matches with the ASSEMBLED data, so the published series are bit-identical to the old
         local passes at the pixel level; the full-chain plot pins (the seven files + the "PLOT done" line) hold too.
         (4) THE TESTS — `test_wrk_plot`'s synthetic ctx publishes the two series with the SAME functions the pipeline
         uses (`compute_training_dense_metrics` / `validate_model` on the synthetic state); the probe `verify_analytics`
         re-pinned (A1 the new `__all__`, A8 the `_down` clears FOUR fields, D4 the `.metrics` access). (5) THE DOCS —
         hlp\_analytics (the API row), hlp\_plot (the `collect_plot_data` row + the assembly bullet + the "no local
         forward pass" convention), wrk\_analytics, wrk\_plot, the two test mirrors (incl. a stale "13-level chain" ->
         14) and the overview rows. VERIFICATION: the full suite green (920/0/23), the 1e6 G0 bit-exact,
         `verify_analytics` ALL CHECKS PASSED, the full probe sweep green. I-018 step 5 (the docs wave + the idea
         closure) follows.

D-247 | 2026-09-19 | I-018 closed (the campaign close). The idea is DONE: the top-20 outlier report lives in VALIDATE
         (the level that computes the residuals) and the 20 records are published in `ctx.vld_outliers`; the duplication
         chain is gone on both sides — the validation residuals are derived ONCE (VALIDATE, consumed by PLOT and
         CLIENT\_CHECK) and the dense training residuals ONCE (ANALYTICS, consumed by PLOT) — so PLOT is a pure
         rendering level with no forward pass. The campaign: D-243 (VALIDATE owns the series + the report moves +
         the D-150 test moves to test\_wrk\_validate), D-244 (the stale probe re-pin the campaign sweep exposed, 9
         probes + the mirror docs), D-245 (CLIENT\_CHECK consumes `ctx.vld_rn`; its two divergence tests re-shaped to
         the new contract), D-246 (the ANALYTICS publication + the PlotData assembly). NO NUMBER MOVED anywhere: the
         metric goldens, the model-file size band, the PNG byte-determinism golden and the full-chain pins all hold —
         the published series are bit-identical to the previous local passes. I-018 moves to notes/ideas-closed.md
         (the D-235 procedure: the statement + the D-pointers + the outcome); the open backlog
         is I-007, I-009, I-010, I-014. The overview Next-steps and the per-file rows follow in the same commit.
         VERIFICATION: the full suite green (920/0/23), the full probe sweep green (22/22), the 1e6 G0 bit-exact.

D-248 | 2026-09-19 | The workspace tools/ directory (Roberto: "vale la pena di salvarli in un posto sicuro fuori da
         scratch? ... un nuovo tools/ al root") + the scratch cleanup. (1) THE TOOLS — this session's three maintenance
         tools graduate from the gitignored scratch/ to a TRACKED root tools/: `notes_format.py` (the D-237 house
         re-wrapper: the block grammar, the mid-token rejoins, the span healing, the per-file content fingerprint +
         idempotence + fixpoint), `docs_format_audit.py` (the D-239 mirror-doc auditor — a CHECK over the docs/ tree),
         `suite_audit.py` (the D-243 per-module suite counter — a MEASUREMENT tool, the sibling of
         probes/measure\_suite.py; its artifact moved from scratch/ to build/tmp). WHY a new root dir and not probes/:
         probes/ is the VERIFICATION apparatus (the per-module a/b/c checks, the campaign sweep); a tool that makes no
         check — or one that REWRITES files — does not belong there, and src/reversi/tools/ is the SHIPPED package
         subpackage (D-133), so the name collision is documented (rules.md, probe\_rules §2, AGENTS.md Layout). (2) THE
         RULES — rules.md gains the Layout & tree bullet, probe\_rules §2 now names tools/ as the graduation target for
         a maintenance tool, AGENTS.md gains the Layout line. The AGENTS.md re-wrap that `notes_format.py` produced as a
         side effect was REVERTED: the constitution keeps its own wrap, only the tools/ line was added. (3) THE CLEANUP
         — the 55 remaining scratch files removed: this session's intermediates (the D-drafts, the journal fragments,
         the wrapped outputs, the superseded generators `wrap_ideas.py` / `rewrap_overview.py` / `gen_ideas.py` /
         `wrapfmt.py`), the SUPERSEDED ancestors of the re-wrapper (`rewrap_decisions.py`, `rewrap_cs.py`,
         `protect_decisions.py` — the D-209 reformat), and the previous campaigns' self-declared "disposable" one-offs
         (`zobrist_extract.py` D-213, `ffo12_parity_check.py` + `ffo12_make_sample.py` D-215, the `play_path_*`
         family D-227/D-232, `gen_choose_golden*.py` D-203, `check_initial_swap.py`, `choose_golden_sections.txt`) +
         the 89.7 MB `ffo-12_log.csv` (regenerable: the legacy repo at /home/rcrr/base/prj/reversi is present; the
         sample fixture is committed and the 100% parity is recorded at D-215) + `__pycache__/`. Their evidence is
         already in the committed artifacts (the goldens, the fixtures, the code constants) and in the D-entries.
         scratch/ is EMPTY again, as probe\_rules §2 requires. VERIFICATION: the three tools run from tools/ (the
         re-wrapper is a no-op on the fixpoint tree, the auditor reports the 85/94, the counter reproduces the
         overview's cells), the full suite green (920/0/23), the full probe sweep green (22/22).

D-249 | 2026-09-19 | The tools/ rules: notes/tools.md (Roberto: "Vorrei vedere un nuovo documento in notes: tools.md con
         le semplici regole per inserire un nuovo artefatto python in tools, e un inventario ... In pratica deve essere
         un tool di utilita generale, deve avere una API chiara, deve essere riproducibile e testabile, e non deve fare
         danni"). THE DOCUMENT — the new domain rule file (rigid, like probe\_rules.md), with: §1 what a tool IS and is
         not (a workspace utility in tools/, NOT the shipped src/reversi/tools/ D-133, NOT a probe — no a/b/c checks,
         outside the campaign sweep, even when it checks something: the doc auditor —, NOT a test, NOT a home for a
         one-off); §2 THE FOUR REQUIREMENTS, one section each: GENERAL UTILITY (it solves a class, not an instance — the
         test: would it still be useful next session on a different file?), A CLEAR API (the documented CLI, the
         explicit arguments, no prompts, no hidden state, the stated input -> output contract), REPRODUCIBLE AND
         TESTABLE (deterministic output, a verifiable report — counts, a fingerprint —, the twice-run idempotence), IT
         DOES NO DAMAGE (the hard safety list: the default is a report and the destructive action needs an explicit
         flag; a write is fingerprint-verified BEFORE it happens; only the given paths, inside the workspace; the
         artifacts under build/tmp; never a git write command; never a deletion outside the tool's own build/tmp
         artifacts; the scope stated in the docstring); §3 the fixed header (WHAT IT IS / USAGE / SAFETY / ORIGIN); §4
         the naming (snake\_case, `_audit`/`_check` allowed, the `verify_` prefix reserved to the probes, no new
         dependency); §5 the lifecycle (born in scratch/, graduated in one commit with the inventory row + the D-number,
         maintained in the same commit as what it serves, retired by deletion + a new D-number — never left in scratch/
         to die); §6 THE INVENTORY (the 3 tools: notes\_format / docs\_format\_audit / suite\_audit, each with the
         category, what it does, what it writes, the origin); §7 the grandfathered case
         (probes/measure\_suite.py, D-132: the pre-existing measurement tool stays where probe\_rules §2 names it; a new
         one lands in tools/ — moving it is an open call). THE WIRING — rules.md (the domain rule files list + the
         tools/ bullet now points at notes/tools.md) and the overview Index. ALSO: AGENTS.md re-wrapped to the 120-char
         rule (Roberto's explicit request: the constitution follows the house format like the rest of the notes; content
         verified identical by the fingerprint, 67 -> 46 lines).

D-250 | 2026-09-19 | measure\_suite.py moves to tools/ (Roberto: "Metti probes/measure\_suite.py in tools, YES!"). THE
         MOVE — `git mv probes/measure_suite.py tools/measure_suite.py`: the per-test TIMING instrument (D-132, the
         baseline of the D-130 tiering) joins the three maintenance tools, so ALL the non-check workspace utilities live
         in ONE place. Its header is rewritten to the tools.md §3 shape (WHAT IT IS / USAGE / SAFETY / ORIGIN) and its
         artifact moves from scratch/test\_durations.txt to build/tmp/test\_durations.txt (the tools.md §2 safety rule:
         the artifacts under the D-065 base, never in the tree — scratch/ is for session code, not for a tool's output).
         The probe\_rules §2 bullet is REWRITTEN: it no longer grandfathers a measurement tool inside probes/ — the
         measurement tools live in tools/ (measure\_suite.py + suite\_audit.py), make no a/b/c checks and their
         artifacts go under build/tmp; the sweep stays the verify\_\* probes (21 files). tools.md loses its §7 (the
         grandfather case is closed by the move) and gains the measure\_suite row in the inventory (4 rows now). The
         historical D-132/journal references stay as they are (append-only: they record where the file WAS). BUILD/TMP
         CLEANED: 23 leaked temp dirs (70 MB) + the suite\_audit.txt artifact removed. THE CAUSE, verified rather than
         assumed: the tests and the probes DO clean up (the chain suite re-run leaves 23 -> 23 dirs) — the leaks came
         from (a) the INTERRUPTED runs (the SIGTERM timeouts of this session: a killed process never runs its tearDown)
         and (b) the ad-hoc `tempfile.mkdtemp` snippets used for the empirical ground truth (the slot discovery, the
         cache-file listings). No test defect: build/tmp is empty again, and every artifact there is regenerable on
         demand.

D-251 | 2026-09-19 | The build/tmp leak: three probes cleaned (Roberto: "Controlla anche build/tmp dovrebbe essere vuota
         ma non lo e'"). THE INVESTIGATION, in two rounds: the 23 leftover dirs (70 MB) were attributed FIRST to the
         interrupted runs (a SIGTERM-killed process never runs its tearDown) and to the ad-hoc `mkdtemp` snippets used
         for the empirical ground truth — verified, not assumed: the chain suite re-run leaves 23 -> 23 dirs, so the
         TESTS clean up. But a clean SWEEP left 3 dirs again, and THAT was the real defect: `verify_cache_manager.py`,
         `verify_plot.py` and `verify_save.py` create their temp dir with `tempfile.mkdtemp` and NEVER remove it — a
         violation of probe\_rules §2 ("probe artifacts go under build/tmp and are removed afterwards, like test
         artifacts"), invisible until someone looks at the directory. THE FIX: the house idiom of
         `verify_hlp_indexes.py` — an `atexit.register(lambda: shutil.rmtree(tmp, ignore_errors=True))` right after the
         mkdtemp (the hook fires on a normal exit AND on a check failure; a SIGKILL remains uncatchable, which is why
         the interrupted-run leftovers are expected and are cleaned by hand). VERIFICATION: the three probes are green
         and leave build/tmp EMPTY; the full sweep (21 probes) is green and leaves build/tmp EMPTY. The
         `measure_suite.py` and `suite_audit.py` artifacts (the tools' deliverables) are regenerable on demand and were
         removed too. No test defect, no probe count change: a maintenance fix to the apparatus.

D-252 | 2026-09-19 | The G0 wave-size fix: the corpus lanes capped by the corpus (Roberto's GO, after the timing
         analysis + the pilot). THE FINDING — the per-test timing of the whole suite (tools/measure\_suite.py) showed 41
         tests (4.5%) taking 91% of the wall; PROFILING the cold chain run of `test_wrk_indexes` revealed that 3.3 s of
         its 3.4 s were the FEATURE\_ANALYSIS G0 corpus — a level that suite does not test — because `rlm_00` (used by 9
         suites) enables it with a 10k corpus and `wrk_feature_analysis` ran it with `_WAVE_SIZE = 1_000_000`
         UNCONDITIONALLY: the 1e6-lane arrays (~48 MB) plus the per-step glue cost ~3.4 s for a 10k-position harvest
         that a 10k-lane wave does in ~0.04 s (measured: W=1e6 3.838 s, W=1e4 0.036 s, 107x). THE FIX — ONE LINE:
         `wave_size = min(_WAVE_SIZE, corpus.total_positions)` (the wave is the PARALLELISM; the lanes beyond the corpus
         are pure overhead). THE SEMANTICS: the production corpora (1e7) keep 1e6 lanes, so the production corpus is
         BIT-IDENTICAL (min(1e6, 1e7) = 1e6); a corpus BELOW 1e6 gets a different corpus — still valid and still
         deterministic (the wave size is now a pure function of the config), but not the same draw order. The cache
         signature does not carry W: a cache written BEFORE this change by a small-corpus config would be reused once
         with the new wave (regenerable; the production path is untouched). VERIFIED: no test golden depends on the
         small-corpus values — 0 failures, 0 errors, 23 skipped. THE MEASUREMENT (the canonical runner): the default
         tier 42.6 -> 19.8 s (-54%), LONG ~140 -> 88.0 s (-37%); the measure\_suite wall 150.8 -> 87.1 s (-42%);
         `test_wrk_feature_analysis` 23,677 -> 1,635 ms (14.5x) and `test_wrk_indexes` 7,440 -> 914 ms (8x). THE PILOT
         THAT FOUND IT: the warm-template pattern (a class-level chain run + a per-test copytree of the 0.5 MB cache
         dir) WORKED mechanically (the warm test 3,800 -> 146 ms, 26x) but for a 2-test class the net gain was ZERO (the
         class paid 2 cold runs either way), and after this fix its residual value is ~100 ms while it perturbs the tier
         accounting (a class-level skip: 920 -> 919 in the default tier) — REVERTED, to be re-approached only if a
         per-test cold cost stays high. The docs follow (wrk\_feature\_analysis.md, hlp\_wave.md).

D-253 | 2026-09-19 | The A2030 chain depth fix: each test stops where it asserts (Roberto: "Proviamo a rigenerare
         TestFullChainA2030 ... vediamo se il pattern paga in questo caso"). THE PILOT'S VERDICT — the warm-template
         pattern does NOT pay here, and the measurement says why: the per-test cost of a WARM full chain is 5.49 s
         against the 9.18 s cold (the non-cache levels re-run: VALIDATE, ANALYTICS, CLIENT\_CHECK, PLOT), and the
         template dir is 11.3 MB (a 10 ms copytree) — so the class would pay 9.2 s of template + 3 warm runs for a
         saving of ~4 s: not worth the machinery. THE REAL LEVER, found by reading what each test ASSERTS: two of the
         three tests run the chain deeper than they look. `test_config_provenance_single_source` asserts the FILE's
         provenance (the record absence, the sidecar, the fingerprint) — all SAVE artifacts — and
         `test_second_instance_deterministic` asserts the model-file byte-identity + the 6 cache hits, also all at SAVE;
         only `test_full_worker_chain` asserts the plots. Both now stop at `move_to_step('SAVE')` (16) instead of
         `move_to_last()` (18): the levels 17/18 (CLIENT\_CHECK + PLOT) are ~5.1 s of matplotlib figures on the A2030
         validation set, covered by test\_wrk\_client\_check, test\_wrk\_plot and the end-to-end test itself — asserting
         nothing about them only paid their cost. THE MEASUREMENT: the class 25,250 -> 14,023 ms (-44%; the provenance
         test 8,596 -> 2,367, the determinism one 11,193 -> 2,453, the end-to-end test unchanged in what it asserts),
         the LONG suite 88.0 -> 76.5 s, wall 91 -> 79.9 s, 920 tests, 0 failures, 0 errors, 23 skipped. THE PATTERN
         LEARNED (the two pilots): the win is never the SETUP machinery — it is REMOVING work nobody asserts (the
         FEATURE\_ANALYSIS corpus for 9 suites, D-252; the CLIENT\_CHECK/PLOT depth for 2 tests, here). The
         warm-template idea stays in the drawer, to be re-approached only if a per-test cold cost is both large and
         unasserted-free. The mirror doc follows (test\_lm\_worker\_full\_chain.md).

D-254 | 2026-09-19 | The SU-analysis corpus regenerated: the generator version bumped + the official-start 1e7 run
         (PUNTO 6, Roberto: "Mettiamo a posto questo BUG della posizione iniziale ... PUNTO 6, fai tutto!"). (1) THE BUG
         — the D-192 initial-position fix swapped the roles (the official start: the mover E4+D5, the opponent D4+E5)
         but did NOT bump the cache signature's generator version, which stayed "g0-1": a corpus cached under the OLD
         (swapped) start would have been REUSED SILENTLY, making the fix ineffective for every existing artifact — the
         signature exists precisely to prevent that. FIXED: `_GENERATOR_VERSION = "su-corpus-2"` (the official start +
         the neutral name, since the G0/G1 distinction died with G1 at D-191), with the rationale in the code comment: a
         version bump invalidates every cached corpus, which is the point. (2) THE REGENERATION — the campaign's scale
         re-run on the official start: the 1e7 corpus with the A2050 feature set (11 patterns + 1 mobility + the
         intercept, ec 20, seed 42; the rlm\_05 feature set at the ODP-1 default size) through FEATURE\_ANALYSIS +
         EFFECT\_SIZE, into `build/su_corpus_1e7/` (the gitignored data area: the run is expensive to replicate).
         MEASURED: 92.7 s total — 67.2 s for the corpus + the SU statistics (47 sub-variables, the marginal + the joint
         tables) and 25.5 s for the EFFECT\_SIZE (the eta2/omega2 + the adherence). The artifacts:
         `rlmwf_03_FEATURE_ANALYSIS.dat` (30 MB) + the two reports. The 2e6/1e8 experiment configs (rlm\_05/rlm\_06)
         regenerate on demand — now automatically, thanks to the version bump. (3) THE OVERVIEW — the STALE bullet is
         replaced by the regenerated state, and the "first maintenance call" leaves the Next steps. THE COST NOTE: the
         regeneration is now CHEAP (92.7 s) also because of the D-252 wave-size fix (the small-corpus paths) — the
         production 1e7 keeps its 1e6 lanes, so this run's corpus is the same as it would have been before D-252. A
         CORRECTION TO THE RECORD (Roberto's, verified in the code): the EFFECT\_SIZE's eta2/omega2 run on the TAGGED
         data (`ctx.hlp_indexes.indexes` + `ctx.game_values`), NOT on the corpus — the corpus feeds only its ADHERENCE
         sub-report (and the FEATURE\_ANALYSIS statistics); the D-253-era summary that listed EFFECT\_SIZE among the
         corpus consumers was imprecise.

D-255 | 2026-09-19 | The A2030 plot override replaces the depth reduction (Roberto's design: "il test che verifica i
         PLOT, bene che faccia i plot. I due test seguenti che non verificano i PLOT ... mettiamo all'avvio del test un
         override sulla proprieta' del config plot.enable=False ... cosi non li ricreiamo"). THE CHANGE — D-253 had
         stopped the two non-PLOT tests at SAVE (16); now every A2030 test runs the FULL 18-level chain: the end-to-end
         test with the plots ENABLED (it asserts them), the provenance and the determinism tests with
         `plot.enable = False`. The override is a CONFIG FILE (a copy of rlm\_04.json written in the test's temp dir,
         via the `_config_without_plots` helper + the `_model(plots=...)` factory), NOT a mutation of `ctx.cfg` after
         the CONFIG step: the provenance test pins `ctx.config_checksum == sha3(ctx.cfg.model_dump_json(indent=4))`, and
         a post-CONFIG mutation would desync that identity (the checksum is computed once, at step 1). THE MEASUREMENT:
         the class 25,250 (before any fix) -> 12,893 ms (-49%), AGAINST the 14,023 ms of the D-253 depth reduction — so
         the override is both FASTER and STRONGER (the full chain is exercised by all three tests; the depth reduction
         traded coverage for the same saving). The determinism test's two runs share the same config file, so the
         embedded provenance matches too (the byte-identity assertion holds). The mirror doc follows.

D-256 | 2026-09-19 | P3: the VVLONG tier + the 1e7 corpus test (Roberto: "fai entrambe le cose ... e generiamo una
         classe VVLONG e mettiamoci (b) ... VVLONG comprende VLONG e LONG naturalmente"). (1) THE TIER — a FOURTH
         cumulative tier: `VVLONG=1` implies VLONG -> LONG. The single source of the semantics is `reversi.test.tags`:
         the two new predicates `tier_vlong()` (VLONG or VVLONG) and `tier_vvlong()` (VVLONG only) next to
         `db_long_gate` (which now accepts VVLONG); the test classes gate on the predicates, never on the env vars. THE
         CHECKLIST for a new tier is recorded in the tags.md mirror + the rules.md bullet: a predicate in tags.py, the
         runner header, the rules bullet, the overview. (2) THE MOVE — the 1e6 corpus benchmark
         (`test_hlp_wave::TestBenchmark`) leaves the LONG tier for VVLONG: it is a measurement instrument (the printed
         games/s is the deliverable), and LONG is the everyday pre-commit — the benchmark belongs to the tier you run
         deliberately. Verified: it skips under LONG=1 and runs under VVLONG=1 (the wave module reports 4/0/1 in both
         the default and the LONG tiers). (3) THE NEW TEST — `test_wrk_feature_analysis::TestSuCorpusAtScale`
         (VLONG-gated, D-256): the SU-analysis corpus at the ODP-1 scale (1e7 positions, ec 20, seed 42, the rlm\_00
         feature set), pinning what the small-corpus suite cannot — the harvested count at scale, the marginal totals
         (exactly one count per position per sub-variable), the cache write + the HIT on a second run with the same
         signature. MEASURED: 47.5 s (46.6 cold). The 1e7 scale also has its production run (D-254: the A2050 feature
         set, 92.7 s) — the test is the fixture-scale regression guard, the D-254 run the maintenance call. (4) THE DOCS
         — the MISSING tags.py MIRROR is written (docs/src/reversi/test/tags.md: a D-007 gap — tags.py had no doc and no
         overview row, invisible to the audit because it excludes the test/ helpers), the overview gains the row + the
         two Suite cells (the wave 3/0/1 with VVLONG 4/0/0, the feature-analysis 8/0/0 with VLONG 9/0/0), the runner
         header, the rules.md bullet, the three test mirrors. VERIFICATION: the default tier green, the LONG tier green
         (920/0/23), the VLONG 1e7 test green on its own.

D-257 | 2026-09-19 | P1: the "SU-analysis corpus" naming — G0 is gone (Roberto: "Visto che G0 e' stato coniato per
         distinguersi gergalmente da g1, che poi e' DECADUTO, oggi G0 non si deve distinguere da NULLA ... Chiamiamolo
         'corpus per analisi SU' e basta senza G0 per favore"). (1) THE CONCEPT — everywhere in the live code, the docs
         and the overview the corpus is now "the SU-analysis corpus" (or simply "the corpus" where the context is
         clear); the wave's internals lose the G0 qualifier too ("the wave stream", "the uniform pick", "the lockstep
         step", "the wave engine", "the wave trajectory"). (2) THE IDENTIFIERS (23 substitutions, 5 files) —
         `run_wave_g0` -> `run_wave`, `step_wave_g0` -> `step_wave`, `_pick_g0` -> `_pick_wave`, the test method
         `test_1e6_g0_wall_clock` -> `test_1e6_wave_wall_clock`, the class `TestG0Engine` -> `TestWaveEngine`. The names
         `run_wave` / `step_wave` / `_pick_wave` were FREED by the D-191 burial of the table-pick variant, so the
         surviving engine takes them back: the code now says what it IS. (3) THE PROSE (54 + 17 substitutions, 16 files)
         — the code comments and docstrings, the mirror docs, the probes (verify\_logistic\_model's pipeline-state
         comment), the overview. NOT touched: the historical records (decisions/journal/analyses are append-only: they
         keep the G0/G1 vocabulary of their time) and the local `g0` variables of hlp\_gradient / test\_pattern /
         verify\_gradient (a gradient accumulator, a pattern name — unrelated). (4) NO SIGNATURE BUMP — a rename does
         not change the corpus bytes, so the cache signature stays `su-corpus-2` (D-254) and nothing regenerates.
         VERIFICATION: the affected modules green, the full LONG tier green, the probe sweep green. The name now carries
         the PURPOSE (the statistical base for the SU analysis) instead of a dead gergal distinction.
