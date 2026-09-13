#
# hlp_random_play.py
#
# This file is part of the reversi program
# http://github.com/rcrr/reversi
#
# Author Roberto Corradini mailto:rob_corradini@yahoo.it
# Copyright 2026 Roberto Corradini. All rights reserved.
#
# License
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA
# or visit the site <http://www.gnu.org/licenses/>.
#

"""
The single-game random play generator (the I-017 T4, D-162):
from the initial position, a seeded loop over plies — the legal
moves (board.py), the move pick via the ODP-9 permutation
lookup table, position_make_move (D-140), the pass, the game
over, and the ec ARREST (the window constraint — the corpus
keeps every ply of the arrested game).

The pick (ODP-9): the random move is NOT picked by a PRNG draw
per move — at setup the seeded MT19937 (reversi/tools/prng.py,
the D-159 port) builds ONE table {n -> a permutation of
0..n-1} for n = 1..64 (the total cost: 1+2+...+64 = 2016 draws
— negligible), and at steady state the pick is a pure table
lookup: for a position with k legal moves, the chosen move =
table[k][counter % k] (the k-th set bit), NO PRNG in the loop.
Deterministic under the same seed (the table IS the seeded
shuffle; the T5 wave engine replays the SAME per-slot logic, so
the single-game trace is the T5 cross-validation reference).
T4 is the single-game path (no performance pressure — the T5
wave engine is the numba tier); T6 lands the vectorized pick
kernel + the distribution test + the ODP-9 closing.

The per-game phase (the D-162 pin): a game's counter starts at
`counter0` (the T5 slot i passes counter0 = i) — without a
per-game phase every game would share the same rank walk and
the corpus would degenerate (all 1e6 games make the same first
move). A PASS consumes no counter step (only real moves walk
the permutation).

The ec (the arrest measure): 64 - occupied (the moves
remaining — the same expression board.position_final_value
uses inline). PINNED (T7, D-177): this is EXACTLY the DB's
`empty_count` — the regab extraction filters
`empty_count = ec` (regab.py, the "mele con mele" window
constraint), and `empty_count` is the count of the empty
squares = 64 - popcount(mover | opponent). The corpus is
therefore arrested in the SAME window as the DB extraction.
The loop is formula-agnostic (only ec_of carries the
formula).
"""

from __future__ import annotations

import functools

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import numpy as np
from pydantic import validate_call, ConfigDict

from reversi.board import (make_position, move_from_str,
                           move_as_bitboard, position_legal_moves,
                           position_make_move, position_is_game_over)
from reversi.tools.prng import MT19937

if TYPE_CHECKING:
    from reversi.board import PositionField

__all__ = ['PA', 'MAX_PLIES', 'RandomGame', 'ec_of',
           'initial_position', 'build_pick_table', 'pick_move',
           'random_play', 'MarginalAccumulator']

#: The pass move (board.py Move domain: 0..63 squares, 64 = PA).
PA: int = 64

#: The defensive loop guard (a game makes <= 64 real moves; the
#: passes are bounded by the game-over rule).
MAX_PLIES: int = 300


@dataclass
class RandomGame:
    """
    The outcome of one seeded random play: the arrested
    position + the FULL trajectory (the doc: "the corpus keeps
    every ply of the arrested game").

    Attributes:
      position:  the arrested Position (the np.void scalar).
      moves:     every ply, in order (a square 0..63, or PA).
      ec_trace:  the ec AFTER each ply ([] when 0 plies).
      ec:        the ec at the arrest (the initial 60 when the
                 game is arrested before the first ply).
      stopped_by: 'ec' (the window was reached) or 'game_over'
                 (the double pass / the full board).
      table_seed: the seed the pick table was built from
                 (the reproducibility provenance).
      counter0:  the starting phase of the counter walk (the
                 T5 slot id).
    """

    position: "PositionField"
    moves: list = field(default_factory=list)
    ec_trace: list = field(default_factory=list)
    ec: int = 60
    stopped_by: str = 'ec'
    table_seed: int = 0
    counter0: int = 0

    @property
    def plies(self) -> int:
        """The number of plies played (the len of moves)."""
        return len(self.moves)


def ec_of(p: "PositionField") -> int:
    """
    The ec measure of a position: 64 - the occupied squares
    (the moves remaining).

    PINNED (T7, D-177): EXACTLY the DB's `empty_count` — the
    regab extraction filters `empty_count = ec` (regab.py, the
    "mele con mele" window constraint), and `empty_count` is
    the count of the empty squares = 64 - popcount(mover |
    opponent). The corpus is arrested in the SAME window as
    the DB extraction.
    """
    occupied = int(p['mover'] | p['opponent']).bit_count()
    return 64 - occupied


def initial_position() -> "PositionField":
    """
    The standard start: the mover holds the D4+E5 diagonal, the
    opponent the D5+E4 one (the 2x2 center; A1 = top-left =
    bit 0, the naming convention bit = 8*(row-1) + (col-1) —
    both sides have exactly 4 legal moves, the symmetric
    start). The mover-first convention is a pure label at the
    symmetric start (the T12 alignment with the DB extraction
    side is the only place it can matter).
    """
    mover = (move_as_bitboard(move_from_str('D4'))
             | move_as_bitboard(move_from_str('E5')))
    opponent = (move_as_bitboard(move_from_str('D5'))
                | move_as_bitboard(move_from_str('E4')))
    return make_position(mover, opponent)


@functools.lru_cache(maxsize=8)
def build_pick_table(seed: int) -> np.ndarray:
    """
    The ODP-9 PERMUTATION LOOKUP TABLE: table[n] = a seeded
    permutation of 0..n-1 (n = 1..64), built with Fisher-Yates
    (the C shuffle algorithm) over the seeded MT19937 — the
    total cost: sum(n-1 for n in 1..64) = 2016 PRNG draws
    (negligible). Shape (65, 64) uint8 (row n uses its first n
    cells). The returned array is READ-ONLY (the lru_cache
    shares it).

    Deterministic: the same seed builds the same table (the
    golden T3 suite pins the PRNG, the T6 suite pins the table
    properties).
    """
    prng = MT19937(int(seed))
    table = np.zeros((65, 64), dtype=np.uint8)
    for n in range(1, 65):
        row = np.arange(n, dtype=np.uint8)
        for i in range(n - 1, 0, -1):
            j = int(prng.random_choice_from_finite_set(i + 1))
            row[i], row[j] = row[j], row[i]
        table[n, :n] = row
    table.flags.writeable = False
    return table


def pick_move(legal: np.uint64, table: np.ndarray,
              counter: int) -> tuple[np.uint8, int]:
    """
    The steady-state pick (ODP-9): the chosen move for a
    position whose legal-move bitmask is `legal`, via the table
    lookup (NO PRNG). k = popcount(legal); the rank walks the
    permutation: rank = table[k][counter % k]; the move is the
    rank-th set bit of legal (0-based square index).

    k == 0 (no legal move): returns (PA, counter) — the pass
    consumes NO counter step (only real moves walk the
    permutation).
    """
    k = int(legal).bit_count()
    if k == 0:
        return np.uint8(PA), counter
    rank = int(table[int(k), int(counter) % k])
    x = int(legal)
    for _ in range(rank):
        x &= x - 1
    square = (x & -x).bit_length() - 1
    return np.uint8(square), int(counter) + 1


def _kth_set_bit(legal: int, k: int) -> int:
    """The 0-based index of the k-th set bit (the isolated
    lowest after clearing k lower bits)."""
    x = legal
    for _ in range(k):
        x &= x - 1
    return (x & -x).bit_length() - 1


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def random_play(seed: int, ec_target: int, counter0: int = 0,
                table: np.ndarray | None = None) -> RandomGame:
    """
    One seeded random game (the T4 single-game path): from the
    initial position, loop over plies — the legal moves, the
    table pick, position_make_move (D-140); no legal moves ->
    the pass; two consecutive passes or a full board -> the
    game over. The ec ARREST: the game stops when the board
    reaches ec <= ec_target (the doc: "the corpus keeps every
    ply of the arrested game").

    Args:
      seed:      the corpus seed (builds the pick table when
                 `table` is None — the lru_cached build).
      ec_target: the arrest ec (the model's ec, 0..60 — the
                 "mele con mele" window constraint; >= 60
                 arrests before the first ply).
      counter0:  the starting phase of the counter walk (the
                 T5 slot id; 0 for the single-game reference).
      table:     a pre-built pick table (the T5 wave engine
                 builds ONE table for the whole corpus).

    Returns:
      The RandomGame (the arrested position + the full
      trajectory).

    Raises:
      ValueError: ec_target out of the [0, 60] domain.
      RuntimeError: the defensive MAX_PLIES guard (unreachable
        by the game rules).
    """
    if not (0 <= int(ec_target) <= 60):
        raise ValueError(f"ec_target {ec_target} is out of the [0, 60] domain")
    if table is None:
        table = build_pick_table(int(seed))
    return _play_from(initial_position(), table, int(counter0),
                      int(ec_target), int(seed))


def _play_from(p: "PositionField", table: np.ndarray, counter0: int,
               ec_target: int, seed: int) -> RandomGame:
    """
    The game loop from an arbitrary starting position (the seam
    the tests use to exercise the pass branch from a hand-
    crafted position; random_play is the public entry, from the
    initial position).
    """
    moves: list = []
    ec_trace: list = []
    counter = counter0
    stopped_by = 'game_over'

    for _ in range(MAX_PLIES):
        # The ec ARREST (checked before every ply): the board
        # has reached the window.
        if ec_of(p) <= int(ec_target):
            stopped_by = 'ec'
            break
        legal = position_legal_moves(p)
        if int(legal) == 0:
            # No legal move: the pass (the player swap; no
            # counter step). The double pass is the game over:
            # after the swap, if the opponent has no legal move
            # either (the board is unchanged since their last
            # check), the game is over — including on a NOT
            # full board (the non-full double pass; the pre-
            # fix loop only checked the game over in the
            # real-move branch and would spin passes to the
            # MAX_PLIES guard).
            p = position_make_move(p, np.uint8(PA))
            moves.append(np.uint8(PA))
            ec_trace.append(ec_of(p))
            if position_is_game_over(p):
                stopped_by = 'game_over'
                break
            continue
        move, counter = pick_move(legal, table, counter)
        p2 = position_make_move(p, move)
        if p2 is None:
            raise RuntimeError(
                f"the pick is illegal (a bug): move {int(move)} "
                f"from legal {int(legal):016x}")
        p = p2
        moves.append(move)
        ec_trace.append(ec_of(p))
        if position_is_game_over(p):
            stopped_by = 'game_over'
            break
    else:
        raise RuntimeError(
            f"the MAX_PLIES guard tripped ({MAX_PLIES} plies) — "
            "a bug in the game loop")

    return RandomGame(position=p, moves=moves, ec_trace=ec_trace,
                      ec=ec_trace[-1] if ec_trace else ec_of(p),
                      stopped_by=stopped_by,
                      table_seed=int(seed), counter0=int(counter0))


# ---------------------------------------------------------------------
# The marginal frequency accumulator (the I-017 T7, D-177): the
# streaming per-sub-variable (code -> count) accumulation over
# the corpus. The analysis unit is the (feature, instance) sub-
# variable = ONE design-index column (the design-matrix unit, the
# unit the weights live on): each pattern instance is its own
# categorical variable (the code a single uint32 in [0, n_conf)
# — no packing, no overflow: the 2X5COR^8 structured-key concern
# is the feature-level / the joint statistics, not the per-
# column marginal), the mobility a single column. _to_positions
# is the gate's (hlp_gate) lifted to the data module (the corpus
# statistics own it; the gate keeps its copy — the
# consolidation is a later concern).
# ---------------------------------------------------------------------

def _to_positions(mover: np.ndarray, opp: np.ndarray) -> np.ndarray:
    """The direct PositionArray build (the interleaved
    structured array — the make_position layout, no pydantic in
    the accumulation hot path)."""
    n = mover.shape[0]
    pa = np.empty(n, dtype=np.dtype([('mover', np.uint64),
                                     ('opponent', np.uint64)]))
    pa['mover'] = mover
    pa['opponent'] = opp
    return pa


#: The dense-bincount threshold: a sub-variable with
#: n_conf <= this uses the DENSE histogram (the A2050 max is
#: 59049 — all dense); above it, the UNIQUE-MERGE dict (the
#: hypothetical wider code spaces).
_DENSE_THRESHOLD = 1_000_000


class MarginalAccumulator:
    """
    The streaming marginal frequency accumulator (the I-017
    T7): per sub-variable (the (feature, instance) column), the
    code -> count over the corpus positions. Feed it the corpus
    in chunks (the wave boundary harvests: the (mover, opp)
    arrays).

    Each sub-variable is ONE design-index column: the code is a
    single uint32 in [0, n_conf) (no packing, no overflow — the
    2X5COR^8 structured-key concern is the feature-level / the
    joint statistics, not the per-column marginal).

    The split (the design's "bincount / unique-merge"):
      - n_conf <= _DENSE_THRESHOLD: the DENSE bincount over
        [0, n_conf) (all the A2050 sub-variables, max 59049).
      - n_conf > _DENSE_THRESHOLD: the UNIQUE-MERGE split
        (np.unique per chunk + the dict merge).

    The accumulator is POOLED over all fed positions (the corpus
    is a single-ec population — arrested at the model's ec — so
    there is no per-ec split here).
    """

    def __init__(self, fset, blocks):
        """
        Args:
          fset:    the FeatureSet (the compute_indexes
                   provider).
          blocks:  the per-feature (name, col_start, col_end,
                   n_conf, n_inst) over the non-intercept
                   features (the load_campaign blocks). Each
                   feature expands to n_inst sub-variables (one
                   per instance column).
        """
        self.fset = fset
        self.blocks = blocks
        # Expand the feature blocks into the per-instance sub-
        # variables: (name, instance_idx, col, n_conf).
        self.subvars: list = []
        for (name, c0, c1, n_conf, n_inst) in blocks:
            for i in range(n_inst):
                self.subvars.append((name, i, c0 + i, n_conf))
        self._dense: list = []
        self._sparse: list = []
        for (name, i, col, n_conf) in self.subvars:
            if n_conf <= _DENSE_THRESHOLD:
                self._dense.append(np.zeros(n_conf, dtype=np.int64))
                self._sparse.append(None)
            else:
                self._dense.append(None)
                self._sparse.append({})
        self.n_positions: int = 0

    def add(self, mover: np.ndarray, opp: np.ndarray) -> None:
        """
        Accumulate one chunk of corpus positions (the (mover,
        opp) u64 arrays, one row per position).
        """
        n = int(mover.shape[0])
        if n == 0:
            return
        idx = self.fset.compute_indexes(_to_positions(mover, opp))
        for sidx, (name, i, col, n_conf) in enumerate(self.subvars):
            codes = idx[:, col]
            if self._dense[sidx] is not None:
                self._dense[sidx] += np.bincount(
                    codes.astype(np.intp), minlength=n_conf)
            else:
                u, cnt = np.unique(codes, return_counts=True)
                d = self._sparse[sidx]
                for k, c in zip(u.tolist(), cnt):
                    d[k] = d.get(k, 0) + int(c)
        self.n_positions += n

    def result(self):
        """
        The per-sub-variable marginal: a list (over sub-
        variables, in the expanded block order) of
        (name, instance_idx, n_conf, codes, counts) — the
        OBSERVED codes (the non-zero support) as uint32, the
        counts as int64. len(codes) is the K_obs of the sub-
        variable; the never-observed count is n_conf - K_obs.
        """
        out = []
        for sidx, (name, i, col, n_conf) in enumerate(self.subvars):
            if self._dense[sidx] is not None:
                cnt = self._dense[sidx]
                nz = cnt > 0
                codes = np.nonzero(nz)[0].astype(np.uint32)
                out.append((name, i, n_conf, codes,
                            cnt[nz].astype(np.int64)))
            else:
                items = sorted(self._sparse[sidx].items())
                codes = np.array([k for k, _ in items],
                                 dtype=np.uint32)
                c = np.array([v for _, v in items], dtype=np.int64)
                out.append((name, i, n_conf, codes, c))
        return out
