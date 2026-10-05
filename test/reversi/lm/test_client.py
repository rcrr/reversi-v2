#
# test_client.py
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
#
# How to run the client (Evaluation Function) unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests (no DB needed; PERF=1 adds the print-only
#     performance test; see test.reversi.tags).
#
# time python3 -m unittest test.reversi.lm.test_client
#

import unittest
import os
import time

import numpy as np

from pydantic import ValidationError

from reversi.board import Bitboard, make_position
from reversi.feature import Feature, FeatureSet
from reversi.mobility import Mobility, MobilitySet
from reversi.pattern import Pattern, PatternSet
from reversi.lm.model_weights import ModelWeights
from reversi.lm.client import (make_evaluation_function,
                               make_evaluation_function_array)

SEED = 42


class TestClientEvaluationFunction(unittest.TestCase):
    """
    The scalar and the array Evaluation Functions over a synthetic rlm_04-mirror ModelWeights:
    intercept + LMC + EDGE, the same feature layout (and the same iwmap pin) as the rlm_04 training
    configuration — no DB, no cache, no pipeline.
    """

    def setUp(self):
        self._rng = np.random.default_rng(SEED)

        # The rlm_04 feature layout (the fixture rlm_04.json): intercept + LMC (the full board,
        # amask 0) + EDGE (row 1).
        intercept = Feature.new_intercept()
        mset = MobilitySet(
            "MOBILITY",
            [Mobility("LMC", Bitboard(0xFFFFFFFFFFFFFFFF), Bitboard(0))])
        pset = PatternSet("EDGE", [Pattern("EDGE", Bitboard(0xFF))])
        self.fs = FeatureSet("SYNTH_RLM04", intercept, mset, pset)

        # The production rlm_04 iwmap pin: 1 + 65 + 6561 = 6627.
        offsets = np.concatenate(
            ([0], np.cumsum([f.n_configurations for f in self.fs.features]))
        ).astype(np.uint32)
        self.assertEqual(offsets.tolist(), [0, 1, 66, 6627])

        self.mw = ModelWeights(
            version=1, name="SYNTH_RLM04", ec=20, logit_clipping=0.01,
            opt_info={}, training_pop_stats={}, vld_metrics={},
            feature_set=self.fs, iwmap_feature_offset=offsets,
            w_dense=self._rng.standard_normal(int(offsets[-1]),
                                              dtype=np.float32))

        self.ef = make_evaluation_function(self.mw)
        self.ef_array = make_evaluation_function_array(self.mw)

    def _positions(self, n):
        """Seeded collision-free positions (the EF caller contract: mover & opponent == 0)."""
        m = self._rng.integers(0, 2**64, size=n, dtype=np.uint64)
        o = self._rng.integers(0, 2**64, size=n, dtype=np.uint64)
        o &= ~m
        return make_position(m, o)

    def test_parity_bit_exact(self):
        """
        The array EF equals the scalar EF bit-exactly, per position: the length-1 wrap removed, the
        same math.
        """
        positions = self._positions(1000)
        y_array = self.ef_array(positions)
        self.assertEqual(y_array.dtype, np.float32)
        self.assertEqual(y_array.shape, (1000,))
        y_scalar = np.array([self.ef(p) for p in positions])
        np.testing.assert_array_equal(y_array, y_scalar)

    def test_u64_coercion(self):
        """
        A (N, 2) uint64 array is coerced by the PositionArray validator to the same result as the
        structured form.
        """
        positions = self._positions(100)
        raw = np.empty((100, 2), dtype=np.uint64)
        raw[:, 0] = positions['mover']
        raw[:, 1] = positions['opponent']
        np.testing.assert_array_equal(self.ef_array(raw),
                                      self.ef_array(positions))

    def test_2d_structured_corder_parity(self):
        """
        A 2-D structured PositionArray is evaluated in C-order element order: the (K, N) result
        ravels to the 1-D ravel result bit-exactly, and the output keeps the input shape.
        """
        base = self._positions(100).reshape(25, 4)
        y_2d = self.ef_array(base)
        self.assertEqual(y_2d.shape, (25, 4))
        self.assertEqual(y_2d.dtype, np.float32)
        y_1d = self.ef_array(base.ravel())
        np.testing.assert_array_equal(y_2d.ravel(), y_1d)
        # A strided 2-D view: the C-order parity holds through the compute_indexes ravel.
        view = base[::2, ::2]
        y_view = self.ef_array(view)
        self.assertEqual(y_view.shape, view.shape)
        np.testing.assert_array_equal(y_view.ravel(),
                                      self.ef_array(view.ravel()))
        # The N-D empty edges: (0, N) and (K, 0) keep their shapes.
        self.assertEqual(self.ef_array(self._positions(0).reshape(0, 4)).shape,
                         (0, 4))
        self.assertEqual(self.ef_array(self._positions(0).reshape(2, 0)).shape,
                         (2, 0))

    def test_3d_structured_corder_parity(self):
        """The C-order parity extends to any shape (3-D)."""
        positions = self._positions(24).reshape(2, 3, 4)
        y_3d = self.ef_array(positions)
        self.assertEqual(y_3d.shape, (2, 3, 4))
        self.assertEqual(y_3d.dtype, np.float32)
        y_1d = self.ef_array(positions.ravel())
        np.testing.assert_array_equal(y_3d.ravel(), y_1d)

    def test_scalar_position_rejected(self):
        """
        Strict array: a scalar Position is rejected — the scalar contract is make_evaluation_function.
        """
        positions = self._positions(1)
        with self.assertRaises(ValidationError):
            self.ef_array(positions[0])

    def test_list_rejected(self):
        """Bare Python lists are rejected (Pydantic), as for the rest of the dual API."""
        with self.assertRaises(ValidationError):
            self.ef_array([1, 2, 3])
        with self.assertRaises(ValidationError):
            self.ef_array([(1, 2), (3, 4)])

    def test_empty_batch(self):
        """The N=0 edge: an empty (0,) float32 result."""
        y = self.ef_array(self._positions(0))
        self.assertEqual(y.shape, (0,))
        self.assertEqual(y.dtype, np.float32)

    @unittest.skipUnless(os.environ.get('PERF') == '1',
                         "Skipping performance test (set PERF=1 to run)")
    def test_performance_1m(self):
        """
        Measure the vectorized EF over a dense 1,000,000-board batch (the house print pattern).
        """
        size = 1_000_000
        positions = self._positions(size)

        _ = self.ef_array(positions[:10])  # Validation Warmup

        start_time = time.perf_counter()
        y = self.ef_array(positions)
        end_time = time.perf_counter()

        duration = end_time - start_time
        boards_per_sec = size / duration

        print(f"\n[PERF make_evaluation_function_array] "
              f"Processed {size:,} boards in {duration:.4f}s "
              f"({boards_per_sec:,.0f} b/s)")

        # Performance output sanity check: the first 100 outputs agree bit-exactly with the scalar
        # EF, and the call is deterministic.
        head = positions[:100]
        np.testing.assert_array_equal(
            y[:100], np.array([self.ef(p) for p in head]))
        np.testing.assert_array_equal(y, self.ef_array(positions))


if __name__ == '__main__':
    unittest.main()
