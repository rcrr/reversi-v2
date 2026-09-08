#
# test_lm_worker_features.py
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
# How to run the lm_worker_features unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests (a live regab DB + LONG=1 is required — the
#     setUp moves through POSITIONS, which hits the DB on a fresh
#     base dir; SKIP_REGAB_DB=1 skips the DB-gated tests as in
#     test_regab; VLONG=1 implies LONG, D-130).
#
# time python3 -m unittest twolm.test.test_lm_worker_features
#

import unittest
import os
import tempfile
from types import SimpleNamespace

import json5

from unittest.mock import patch
from io import StringIO
from pathlib import Path

import twolm.lm_worker_features as lmwf
from reversi.lm.hlp_config_schemas import ReversiLogisticModelConfig
from reversi.tools.state_machine import Relevance, Verbosity
from twolm.logistic_model import LogisticModel
from reversi.test.paths import CUSTOM_TMP_BASE, WORKSPACE_ROOT
from reversi.test.tags import db_long_gate


class TestLMWorkerFeatures(unittest.TestCase):
    """Tests for the FEATURES worker basic movements and feature set generation."""

    @classmethod
    def setUpClass(cls):
        CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        # T2 (D-082): the SKIP_REGAB_DB gate, as in test_regab —
        # the setUp moves through POSITIONS, which needs the live
        # regab DB (a fresh base dir has no warm cache).
        db_long_gate(self)  # the SKIP_REGAB_DB + LONG gates (D-130)

        # Patch stdout to keep test output clean
        self.patcher_stdout = patch('sys.stdout', new=StringIO())
        self.mock_stdout = self.patcher_stdout.start()

        # TemporaryDirectory created FIRST so a mid-setup failure
        # still leaves a cleanable temp dir.
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.tmp_dir = Path(self._tmp.name)
        self.json_config = str(WORKSPACE_ROOT / "src" / "reversi" / "test" / "data" / "rlm_00.json")
        self.rlm = LogisticModel(self.json_config,
                                 verbosity=Verbosity.LOW,
                                 base_dir_override=self.tmp_dir)

        self.assertEqual(self.rlm.current_step, 0)
        self.assertEqual(self.rlm.current_worker_name, 'CREATED')

        # Move to POSITIONS first, as FEATURES depends on the configuration loaded there
        self.rlm.move_to_step('POSITIONS')
        self.assertEqual(self.rlm.current_step, 2)
        self.assertEqual(self.rlm.current_worker_name, 'POSITIONS')

    def tearDown(self):
        if getattr(self, 'patcher_stdout', None) is not None:
            self.patcher_stdout.stop()
        if getattr(self, '_tmp', None) is not None:
            self._tmp.cleanup()

    def test_build_feature_set(self):
        rlm = self.rlm

        # Before moving to FEATURES, the feature_set should be None
        self.assertIsNone(rlm.context.feature_set)

        rlm.move_to_step('FEATURES')
        self.assertEqual(rlm.current_step, 3)
        self.assertEqual(rlm.current_worker_name, 'FEATURES')

        # After moving, the feature_set should be populated
        self.assertIsNotNone(rlm.context.feature_set)

    def test_feature_set_content_golden(self):
        """The rlm_00.json fixture must build the exact expected FeatureSet."""
        rlm = self.rlm
        rlm.move_to_step('FEATURES')
        fs = rlm.context.feature_set

        # The fixture has no name key: the schema default applies.
        self.assertEqual(fs.name, 'NoNameFeatureSet')

        # Golden hashes (independently re-derived, session 22, D-082):
        # the FeatureSet hash is sha3_256 over b'INTERCEPT' + the
        # mset hash hex string + the pset hash hex string.
        self.assertEqual(fs.hash,
                         '453e918aeabfa3f7ff43f110ab72719b3f1d1906158933436234b7bab075a159')
        self.assertEqual(fs.mset.hash,
                         '2e5535935d46d82a941ef87d43d22562735db9b6bf41db51d6eb6a8f21208a94')
        self.assertEqual(fs.pset.hash,
                         '04d52f12d3438393dd3cd9d47df73c1135ffdf9ed8e9f4d4571f5d1adcbb8c18')

        # Intercept: the canonical INTERCEPT feature.
        self.assertIsNotNone(fs.intercept)
        self.assertEqual(fs.intercept.name, 'INTERCEPT')
        self.assertEqual(fs.intercept.n_configurations, 1)
        self.assertEqual(fs.intercept.n_instances, 1)

        # MobilitySet: the 3 fixture members, in the sorted
        # (mask, amask) order.
        self.assertEqual(fs.mset.name, 'BasicMobilitySet')
        self.assertEqual([(m.name, f'{m.mask:016X}', f'{m.amask:016X}')
                          for m in fs.mset.mobilities],
                         [('ALMC', '0000000000000000', 'FFFFFFFFFFFFFFFF'),
                          ('LMC', 'FFFFFFFFFFFFFFFF', '0000000000000000'),
                          ('DLMC', 'FFFFFFFFFFFFFFFF', 'FFFFFFFFFFFFFFFF')])

        # PatternSet: the 2 fixture members, in the sorted mask order.
        self.assertEqual(fs.pset.name, 'BasicPatternSet')
        self.assertEqual([(p.name, f'{p.mask:016X}') for p in fs.pset.patterns],
                         [('EDGE', '00000000000000FF'),
                          ('ELLE', '0000000000000107')])

        # Feature list: intercept, then the mobilities, then the
        # patterns — with the per-feature n_configurations /
        # n_instances.
        self.assertEqual([(f.name, f.n_configurations, f.n_instances)
                          for f in fs.features],
                         [('INTERCEPT', 1, 1), ('ALMC', 65, 1), ('LMC', 65, 1),
                          ('DLMC', 129, 1), ('EDGE', 6561, 4), ('ELLE', 81, 8)])
        self.assertEqual(fs.n_instances, 16)


class TestLMWorkerFeaturesGuards(unittest.TestCase):
    """DB-free guards for lm_worker_features.

    The guard fires before any data access, so the check drives
    _load_features directly with a minimal context — no regab DB,
    no model, no cache.

    D-106 step 3 (probe_rules.md §4): converted from the
    verify_lm_worker_features.py B11 probe."""

    def setUp(self):
        self.patcher_stdout = patch('sys.stdout', new=StringIO())
        self.mock_stdout = self.patcher_stdout.start()

    def tearDown(self):
        if getattr(self, 'patcher_stdout', None) is not None:
            self.patcher_stdout.stop()

    def test_zero_features_raises_value_error(self):
        """A feature set with zero features (intercept off, no
        mobility/pattern sets) is rejected with a ValueError and an
        ERROR log event (the fail-fast guard)."""
        payload = json5.loads(
            (WORKSPACE_ROOT / "src" / "reversi" / "test" / "data" /
             "rlm_00.json").read_text())
        payload["feature_set"] = {"intercept": False}
        cfg0 = ReversiLogisticModelConfig(**payload)
        events = []
        ctx0 = SimpleNamespace(
            log_event=lambda rel, msg: events.append((rel, msg)),
            cfg=cfg0)
        with self.assertRaises(ValueError) as context:
            lmwf._load_features(ctx0)
        self.assertIn("The feature count is zero", str(context.exception))
        self.assertTrue(any(rel == Relevance.ERROR for rel, _ in events))


if __name__ == '__main__':
    unittest.main()
