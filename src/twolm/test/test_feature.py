#
# test_feature.py
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
#
# How to run the feature module unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environmeant.
#
# $ source .venv/bin/activate
#
# -1- Run the tests.
#
# time PERF=0 python3 -m unittest twolm.test.test_feature
#

import unittest

from twolm.board import (Bitboard,
                         make_position)
from twolm.feature import Feature, FeatureSet
from twolm.mobility import Mobility, MobilitySet
from twolm.pattern import Pattern, PatternSet, Index

import numpy as np

import io
import time        
import os

from pydantic import ValidationError



class TestFeature(unittest.TestCase):

    def test_init_raises_runtime_error(self):
        with self.assertRaises(RuntimeError):
            Feature(Feature.Category.INTERCEPT, "INTERCEPT", 1, 1)

    def test_new_intercept(self):
        f = Feature.new_intercept()
        self.assertIsNotNone(f)
        self.assertEqual(f.category, Feature.Category.INTERCEPT)
        self.assertEqual(f.name, "INTERCEPT")
        self.assertEqual(f.n_configurations, 1)
        self.assertEqual(f.n_instances, 1)
        self.assertIsNone(f.ref)

    def test_new_from_mobility(self):
        m = Mobility("LMC", Bitboard(0xFFFFFFFFFFFFFFFF), Bitboard(0x0000000000000000))
        f = Feature.new_from_mobility(m)
        self.assertIsNotNone(f)
        self.assertEqual(f.category, Feature.Category.MOBILITY)
        self.assertEqual(f.name, "LMC")
        self.assertEqual(f.n_configurations, 65)
        self.assertEqual(f.n_instances, 1)
        self.assertIsNotNone(f.ref)
        self.assertEqual(f.ref, m)

    def test_new_from_pattern(self):
        p = Pattern("EDGE", Bitboard(0x00000000000000FF))
        f = Feature.new_from_pattern(p)
        self.assertIsNotNone(f)
        self.assertEqual(f.category, Feature.Category.PATTERN)
        self.assertEqual(f.name, "EDGE")
        self.assertEqual(f.n_configurations, 3**8)
        self.assertEqual(f.n_instances, 4)
        self.assertIsNotNone(f.ref)
        self.assertEqual(f.ref, p)

    def test_new_from_pattern_invalid_type(self):
        """Ensure input validation fires if wrong type object is injected."""
        with self.assertRaises(ValidationError):
            Feature.new_from_pattern("NotAPatternObject")

    def test_repr_golden(self):
        """Pin the auto-dataclass __repr__ (ref excluded, repr=False)."""
        self.assertEqual(
            repr(Feature.new_intercept()),
            "Feature(category=<Category.INTERCEPT: 0>, name='INTERCEPT', "
            "n_configurations=1, n_instances=1)")
        lmc = Mobility("LMC", Bitboard(0xFFFFFFFFFFFFFFFF),
                       Bitboard(0x0000000000000000))
        self.assertEqual(
            repr(Feature.new_from_mobility(lmc)),
            "Feature(category=<Category.MOBILITY: 1>, name='LMC', "
            "n_configurations=np.uint8(65), n_instances=1)")
        edge = Pattern("EDGE", Bitboard(0x00000000000000FF))
        self.assertEqual(
            repr(Feature.new_from_pattern(edge)),
            "Feature(category=<Category.PATTERN: 2>, name='EDGE', "
            "n_configurations=6561, n_instances=4)")

    def test_eq(self):
        """Pin field-wise __eq__ with ref compared by object identity:
        Mobility and Pattern define no value __eq__, so distinct but
        field-identical refs make their Features unequal."""
        m1 = Mobility("LMC", Bitboard(0xFFFFFFFFFFFFFFFF),
                      Bitboard(0x0000000000000000))
        m2 = Mobility("LMC", Bitboard(0xFFFFFFFFFFFFFFFF),
                      Bitboard(0x0000000000000000))
        a = Feature.new_from_mobility(m1)
        b = Feature.new_from_mobility(m2)
        self.assertEqual(a, a)
        self.assertNotEqual(a, b)
        p1 = Pattern("EDGE", Bitboard(0x00000000000000FF))
        p2 = Pattern("EDGE", Bitboard(0x00000000000000FF))
        self.assertNotEqual(Feature.new_from_pattern(p1),
                            Feature.new_from_pattern(p2))
        self.assertNotEqual(a, Feature.new_intercept())
        self.assertNotEqual(a, Feature.new_from_pattern(p1))
        d = Mobility("DLMC", Bitboard(0xFFFFFFFFFFFFFFFF),
                     Bitboard(0x0000000000000000))
        self.assertNotEqual(a, Feature.new_from_mobility(d))

    def test_unhashable(self):
        """Feature is unhashable: @dataclass with eq and not frozen."""
        with self.assertRaises(TypeError):
            hash(Feature.new_intercept())

class TestFeatureSet(unittest.TestCase):

    def setUp(self):
        pattern_set_data = [
            ('R2',     0x000000000000FF00),
            ('R3',     0x0000000000FF0000),
            ('R4',     0x00000000FF000000),
            ('XEDGE',  0x00000000000042FF),
            ('DIAG4',  0x0000000001020408),
            ('DIAG5',  0x0000000102040810),
            ('DIAG6',  0x0000010204081020),
            ('DIAG7',  0x0001020408102040),
            ('DIAG8',  0x0102040810204080),
            ('CORNER', 0x0000000000070707),
            ('2X5COR', 0x0000000000001F1F),
            ('RCT2X4', 0x0000003C3C000000),
            ('CORE',   0x0000001818000000),
        ]
        plf = lambda x: [Pattern(n, Bitboard(m)) for n, m in x]
        mobility_set_data = [
            ('LMC',  0xFFFFFFFFFFFFFFFF, 0x0000000000000000),
            ('ALMC', 0x0000000000000000, 0xFFFFFFFFFFFFFFFF),
            ('DLMC', 0xFFFFFFFFFFFFFFFF, 0xFFFFFFFFFFFFFFFF),
        ]
        mlf = lambda x: [Mobility(n, Bitboard(m), Bitboard(a)) for n, m, a in x]
        self.intercept = Feature.new_intercept()
        self.mset = MobilitySet('TestMobilitySet', mlf(mobility_set_data))
        self.pset = PatternSet('TestPatternSet', plf(pattern_set_data))

    def test_init(self):
        feature_set = FeatureSet('TestFeatureSet', self.intercept, self.mset, self.pset)
        self.assertIsNotNone(feature_set)

        self.assertEqual(feature_set.name, 'TestFeatureSet')
        self.assertEqual(feature_set.intercept, self.intercept)
        self.assertEqual(feature_set.mset, self.mset)
        self.assertEqual(feature_set.pset, self.pset)

        self.assertEqual(feature_set.n_instances, 53)

        expected_n_instances = [1, 1, 1, 1, 8, 4, 4, 4, 4, 4, 4, 4, 1, 2, 4, 4, 2]
        computed_n_instances = [f.n_instances for f in feature_set.features]
        self.assertEqual(computed_n_instances, expected_n_instances)

        expected_names = ['INTERCEPT', 'ALMC', 'LMC', 'DLMC',
                          '2X5COR', 'XEDGE', 'R2', 'CORNER',
                          'R3', 'DIAG4', 'R4', 'DIAG5', 'CORE',
                          'RCT2X4', 'DIAG6', 'DIAG7', 'DIAG8']
        computed_names = [f.name for f in feature_set.features]
        self.assertEqual(computed_names, expected_names)

        expected_hash = 'f5663932421232ba007622198625344deb9eb9aed58f8ad5c71eabc016b74167'
        self.assertEqual(feature_set.hash, expected_hash)

    def test_init_intercept_only(self):
        """Partial-None: intercept present, mset and pset None."""
        feature_set = FeatureSet('InterceptOnly', self.intercept, None, None)
        self.assertEqual(feature_set.hash,
                         'ab7c1b64b96fe0fb85350613ac69b258a4442f56c390d7f69e5a070611e14b12')
        self.assertEqual([f.name for f in feature_set.features], ['INTERCEPT'])
        self.assertEqual(feature_set.n_instances, 1)
        positions = make_position([0x01054FD4327E1C10, 0x40785CEAFB400004],
                                  [0xE8D03028C880C084, 0x92042214043C7878])
        indexes = feature_set.compute_indexes(positions)
        self.assertEqual(indexes.shape, (2, 1))
        np.testing.assert_array_equal(indexes, np.zeros((2, 1), dtype=Index))

    def test_init_mobility_only(self):
        """Partial-None: mset present, intercept and pset None."""
        feature_set = FeatureSet('MobilityOnly', None, self.mset, None)
        self.assertEqual(feature_set.hash,
                         '239e4df42493da52f536f6b3017712a18da05fa48925b76d12adc688d008ecf3')
        self.assertEqual([f.name for f in feature_set.features],
                         ['ALMC', 'LMC', 'DLMC'])
        self.assertEqual(feature_set.n_instances, 3)
        positions = make_position([0x01054FD4327E1C10, 0x40785CEAFB400004],
                                  [0xE8D03028C880C084, 0x92042214043C7878])
        indexes = feature_set.compute_indexes(positions)
        self.assertEqual(indexes.shape, (2, 3))
        np.testing.assert_array_equal(indexes, self.mset.compute_indexes(positions))

    def test_init_pattern_only(self):
        """Partial-None: pset present, intercept and mset None."""
        feature_set = FeatureSet('PatternOnly', None, None, self.pset)
        self.assertEqual(feature_set.hash,
                         '63f0a6c8b2355baa8e1f6fb733454c8d4f1c0d4cdc9a0270eb45dcf2400f5668')
        self.assertEqual([f.name for f in feature_set.features],
                         ['2X5COR', 'XEDGE', 'R2', 'CORNER', 'R3', 'DIAG4',
                          'R4', 'DIAG5', 'CORE', 'RCT2X4', 'DIAG6', 'DIAG7',
                          'DIAG8'])
        self.assertEqual(feature_set.n_instances, 49)
        positions = make_position([0x01054FD4327E1C10, 0x40785CEAFB400004],
                                  [0xE8D03028C880C084, 0x92042214043C7878])
        indexes = feature_set.compute_indexes(positions)
        self.assertEqual(indexes.shape, (2, 49))
        np.testing.assert_array_equal(
            indexes, self.pset.compute_principal_indexes(positions))

    def test_print_summary(self):
        feature_set = FeatureSet('TestFeatureSet', self.intercept, self.mset, self.pset)
        with io.StringIO() as buffer:
            feature_set.print_summary(output=buffer)
            actual_output = buffer.getvalue()

        expected_output = """FeatureSet: name = TestFeatureSet, length = 17, hash = f5663932421232ba007622198625344deb9eb9aed58f8ad5c71eabc016b74167
  Intercept is present.
  MobilitySet: name = TestMobilitySet, hash = 2e5535935d46d82a941ef87d43d22562735db9b6bf41db51d6eb6a8f21208a94
    00 name = ALMC      , mask = 0x0000000000000000, amask = 0xFFFFFFFFFFFFFFFF
    01 name = LMC       , mask = 0xFFFFFFFFFFFFFFFF, amask = 0x0000000000000000
    02 name = DLMC      , mask = 0xFFFFFFFFFFFFFFFF, amask = 0xFFFFFFFFFFFFFFFF
  PatternSet: name = TestPatternSet, hash = ff97ce55dcb0ebc5f4b62272dde7c3ead438b0feec2411fd258f68a7210040ea
    00 name = 2X5COR    , mask = 0x0000000000001F1F
    01 name = XEDGE     , mask = 0x00000000000042FF
    02 name = R2        , mask = 0x000000000000FF00
    03 name = CORNER    , mask = 0x0000000000070707
    04 name = R3        , mask = 0x0000000000FF0000
    05 name = DIAG4     , mask = 0x0000000001020408
    06 name = R4        , mask = 0x00000000FF000000
    07 name = DIAG5     , mask = 0x0000000102040810
    08 name = CORE      , mask = 0x0000001818000000
    09 name = RCT2X4    , mask = 0x0000003C3C000000
    10 name = DIAG6     , mask = 0x0000010204081020
    11 name = DIAG7     , mask = 0x0001020408102040
    12 name = DIAG8     , mask = 0x0102040810204080
  Features: [<i>, <category>, <name>, <n_instances>, <n_configurations>]
    00 0 INTERCEPT  1          1
    01 1 ALMC       1         65
    02 1 LMC        1         65
    03 1 DLMC       1        129
    04 2 2X5COR     8     59,049
    05 2 XEDGE      4     59,049
    06 2 R2         4      6,561
    07 2 CORNER     4     19,683
    08 2 R3         4      6,561
    09 2 DIAG4      4         81
    10 2 R4         4      6,561
    11 2 DIAG5      4        243
    12 2 CORE       1         81
    13 2 RCT2X4     2      6,561
    14 2 DIAG6      4        729
    15 2 DIAG7      4      2,187
    16 2 DIAG8      2      6,561
"""
        self.assertEqual(actual_output, expected_output)

    def test_init_invalid_intercept_category_raises_value_error(self):
        """Test that passing a non-INTERCEPT feature as the intercept argument raises ValueError."""
        # Create a valid Mobility feature
        m = Mobility("LMC", Bitboard(0xFFFFFFFFFFFFFFFF), Bitboard(0x0000000000000000))
        wrong_intercept = Feature.new_from_mobility(m)
        
        with self.assertRaises(ValueError) as context:
            FeatureSet('WrongInterceptSet', wrong_intercept, self.mset, self.pset)
            
        self.assertIn("wrong category", str(context.exception))

class TestFeatureSetComputeIndexes(unittest.TestCase):

    def setUp(self):
        pattern_set_data = [
            ('EDGE',   0x00000000000000FF),
            ('DIAG4',  0x0000000001020408),
        ]
        plf = lambda x: [Pattern(n, Bitboard(m)) for n, m in x]
        mobility_set_data = [
            ('LMC',  0xFFFFFFFFFFFFFFFF, 0x0000000000000000),
        ]
        mlf = lambda x: [Mobility(n, Bitboard(m), Bitboard(a)) for n, m, a in x]
        intercept = Feature.new_intercept()
        mset = MobilitySet('TestMobilitySet', mlf(mobility_set_data))
        pset = PatternSet('TestPatternSet', plf(pattern_set_data))
        self.fset = FeatureSet('TestFeatureSet', intercept, mset, pset)

        position_data = [
            (0x01054FD4327E1C10, 0xE8D03028C880C084),
            (0x40785CEAFB400004, 0x92042214043C7878),
            (0x01010389C34F5100, 0x607CBC743CB02400),
        ]
        ml, ol = zip(*position_data)
        self.positions = make_position(ml, ol)
        
        expected_index_data = [
            [ 0,  4, 515, 5993, 2375,   13, 12, 32,  4, 14 ],
            [ 0,  8, 483,  110, 1517,   27, 29, 44, 41, 24 ],
            [ 0, 15,   0,  612, 1945, 1093, 22, 22, 19, 22 ],
        ]
        self.expected_indexes = np.array(expected_index_data, dtype=Index)
        
        # Derived values for edge-case shape assertions
        self.expected_I = sum(f.n_instances for f in self.fset.features)

    def test_compute_indexes(self):
        self.assertIsNotNone(self.fset)
        self.assertIsNotNone(self.positions)
        self.assertIsNotNone(self.expected_indexes)

        fset = self.fset
        positions = self.positions
        expected_indexes = self.expected_indexes

        computed_indexes = fset.compute_indexes(positions)
        
        np.testing.assert_array_equal(computed_indexes, expected_indexes)

    def test_compute_indexes_empty_positions(self):
        """Test when N=0 (positions array is empty). Expects shape (0, I)."""
        empty_positions = make_position([], [])
        
        computed_indexes = self.fset.compute_indexes(empty_positions)
        
        # Assert structural 2D shape integrity (0, I)
        self.assertEqual(computed_indexes.shape, (0, self.expected_I))
        self.assertEqual(computed_indexes.dtype, Index)
        self.assertEqual(computed_indexes.ndim, 2)

    def test_compute_indexes_empty_features(self):
        """Test when I=0 (no features active). Expects shape (N, 0)."""
        # Create a feature set where intercept, mset, and pset are disabled/None
        empty_fset = FeatureSet('EmptyFeatureSet', intercept=None, mset=None, pset=None)
        
        computed_indexes = empty_fset.compute_indexes(self.positions)
        
        # Assert structural 2D shape integrity (N, 0)
        self.assertEqual(computed_indexes.shape, (len(self.positions), 0))
        self.assertEqual(computed_indexes.dtype, Index)
        self.assertEqual(computed_indexes.ndim, 2)

    def test_compute_indexes_both_empty(self):
        """Test when both N=0 and I=0. Expects shape (0, 0)."""
        empty_positions = make_position([], [])
        empty_fset = FeatureSet('EmptyFeatureSet', intercept=None, mset=None, pset=None)
        
        computed_indexes = empty_fset.compute_indexes(empty_positions)
        
        self.assertEqual(computed_indexes.shape, (0, 0))
        self.assertEqual(computed_indexes.dtype, Index)

    def test_compute_indexes_wrong_argument_type(self):
        """Test that Pydantic's @validate_call blocks invalid argument types."""
        invalid_arguments = [
            None,
            [1, 2],           # Standard Python list
            "invalid_string", # Text string
            np.array([1, 2])  # Standard numpy array instead of PositionArray
        ]
        
        for wrong_arg in invalid_arguments:
            with self.subTest(wrong_arg=type(wrong_arg)):
                with self.assertRaises(ValidationError):
                    self.fset.compute_indexes(wrong_arg)

class TestFeatureSetComputeIndexesPerf(unittest.TestCase):

    @unittest.skipUnless(os.environ.get('PERF') == '1', "Skipping performance test (set PERF=1 to run)")
    def test_performance_1m(self):
        
        size = 1_000_000
        
        pattern_set_data = [
            ('R2',     0x000000000000FF00),
            ('R3',     0x0000000000FF0000),
            ('R4',     0x00000000FF000000),
            ('XEDGE',  0x00000000000042FF),
            ('DIAG4',  0x0000000001020408),
            ('DIAG5',  0x0000000102040810),
            ('DIAG6',  0x0000010204081020),
            ('DIAG7',  0x0001020408102040),
            ('DIAG8',  0x0102040810204080),
            ('CORNER', 0x0000000000070707),
            ('2X5COR', 0x0000000000001F1F),
            ('RCT2X4', 0x0000003C3C000000),
            ('CORE',   0x0000001818000000),
        ]
        plf = lambda x: [Pattern(n, Bitboard(m)) for n, m in x]
        mobility_set_data = [
            ('LMC',  0xFFFFFFFFFFFFFFFF, 0x0000000000000000),
        ]
        mlf = lambda x: [Mobility(n, Bitboard(m), Bitboard(a)) for n, m, a in x]
        intercept = Feature.new_intercept()
        mset = MobilitySet('TestMobilitySet', mlf(mobility_set_data))
        pset = PatternSet('TestPatternSet', plf(pattern_set_data))
        fset = FeatureSet('TestFeatureSet', intercept, mset, pset)

        expected_index_instances = 51

        position_data = [
            (0x01054FD4327E1C10, 0xE8D03028C880C084),
            (0x40785CEAFB400004, 0x92042214043C7878),
        ]
        ml_base, ol_base = zip(*position_data)

        scale = size // len(position_data)
        self.assertEqual(size, scale * len(position_data))

        # 2. Performance scale-up (Repeat the 2 items 500,000 times)
        # np.tile repeats the entire array pattern seamlessly and efficiently in C
        ml_perf = np.tile(ml_base, scale)
        ol_perf = np.tile(ol_base, scale)

        # Instantiate the massive 1,000,000 PositionArray
        positions = make_position(ml_perf, ol_perf)

        # Warmup
        _ = fset.compute_indexes(positions[:100])

        start = time.perf_counter()
        computed_indexes = fset.compute_indexes(positions)
        end = time.perf_counter()

        N = computed_indexes.shape[0]
        I = computed_indexes.shape[1]
        
        duration = end - start
        print(f"\n[PERF FeatureSet.compute_indexes()] Processed {size:,} positions ({I} index instances) in {duration:.4f}s ({(size/duration):,.0f} pos/sec)")

        # 5. Assert structural properties of the large array
        self.assertEqual(N, size)
        self.assertEqual(I, expected_index_instances)
