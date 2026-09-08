#
# test_hlp_optimize.py
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
# How to run the hlp_optimize unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests (no live regab DB required — pure checkpoint IO
#     and cache-validation tests, as in test_hlp_gradient).
#
# time python3 -m unittest reversi.test.test_hlp_optimize
#

import hashlib
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import numpy.testing as nptest

from reversi.tools import binio
from reversi.lm.hlp_optimize import (save_optimization_checkpoint,
                                load_optimization_checkpoint,
                                is_optimization_cache_consistent,
                                is_optimization_status_converged,
                                optimization_info_dict,
                                weights_compute_sha3_256_hash)
from reversi.test.paths import CUSTOM_TMP_BASE


def _mock_ctx(ridge=0.01, min_grad=(1e-3, 3),
              dm="123abc", zed="456xyz"):
    """A context mock carrying the config the consistency/status gates read."""
    events = []

    def log_event(level, msg):
        events.append((level, msg))

    return SimpleNamespace(
        log_event=log_event,
        design_matrix_checksum=dm,
        zed_checksum=zed,
        cfg=SimpleNamespace(
            stat_model=SimpleNamespace(ridge_regularization=ridge),
            optimization=SimpleNamespace(min_grad=min_grad)),
        _events=events)


class TestRLMOptimizeIO(unittest.TestCase):
    """Tests the binary serialization and deserialization of the optimization checkpoint."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.filepath = Path(self._tmp.name) / "checkpoint_test.dat"

        # Create dummy data to save
        self.w = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        self.sl = [np.array([0.01, 0.02, 0.03], dtype=np.float32)]
        self.yl = [np.array([0.04, 0.05, 0.06], dtype=np.float32)]
        self.rho = [1.5]

        self.design_matrix_checksum = 'abc123'
        self.zed_checksum = 'xyz789'

        save_optimization_checkpoint(
            filepath=self.filepath,
            design_matrix_checksum=self.design_matrix_checksum,
            zed_checksum=self.zed_checksum,
            ridge_regularization=0.01,
            min_grad_value=1.e-05,
            max_iters=500,
            m=50,
            converged=True,
            reason="CONVERGED_MIN_GRAD",
            iters=42,
            f=0.123,
            g_norm=0.001,
            w=self.w,
            sl=self.sl,
            yl=self.yl,
            rho=self.rho
        )

    def tearDown(self):
        if getattr(self, '_tmp', None) is not None:
            self._tmp.cleanup()

    def test_store_and_load_cycle(self):
        """Test that loading a checkpoint returns the exact saved data, dtypes preserved."""
        self.assertTrue(self.filepath.exists())

        cp = load_optimization_checkpoint(self.filepath)

        # Check scalars
        self.assertEqual(cp['max_iters'], 500)
        self.assertEqual(cp['m'], 50)
        self.assertTrue(cp['converged'])
        self.assertEqual(cp['reason'], "CONVERGED_MIN_GRAD")
        self.assertEqual(cp['iters'], 42)
        self.assertAlmostEqual(cp['f'], 0.123)
        self.assertAlmostEqual(cp['g_norm'], 0.001)
        self.assertAlmostEqual(cp['ridge_regularization'], 0.01)
        self.assertAlmostEqual(cp['min_grad_value'], 1.e-05)

        # Check arrays and their dtypes (float32 payload, float64 scaling factors)
        self.assertEqual(cp['w'].dtype, np.float32)
        nptest.assert_array_equal(cp['w'], self.w)
        self.assertEqual(len(cp['sl']), 1)
        self.assertEqual(cp['sl'][0].dtype, np.float32)
        nptest.assert_array_equal(cp['sl'][0], self.sl[0])
        self.assertEqual(cp['yl'][0].dtype, np.float32)
        nptest.assert_array_equal(cp['yl'][0], self.yl[0])
        self.assertEqual(cp['rho'][0], self.rho[0])
        self.assertIsInstance(cp['rho'][0], float)

    def test_empty_history_roundtrip(self):
        """A checkpoint with no L-BFGS history (len_mem=0) round-trips."""
        p = Path(self._tmp.name) / "empty.dat"
        save_optimization_checkpoint(
            filepath=p,
            design_matrix_checksum=self.design_matrix_checksum,
            zed_checksum=self.zed_checksum,
            ridge_regularization=0.01,
            min_grad_value=1.e-05,
            max_iters=500,
            m=50,
            converged=False,
            reason="INCOMPLETE",
            iters=0,
            f=0.5,
            g_norm=0.25,
            w=self.w,
            sl=[],
            yl=[],
            rho=[]
        )
        cp = load_optimization_checkpoint(p)
        self.assertEqual(cp['sl'], [])
        self.assertEqual(cp['yl'], [])
        self.assertEqual(cp['rho'], [])
        self.assertFalse(cp['converged'])
        nptest.assert_array_equal(cp['w'], self.w)

    def test_history_length_mismatch_raises(self):
        """M6 (D-096): the three history lists must have equal length."""
        p = Path(self._tmp.name) / "bad_history.dat"
        with self.assertRaises(ValueError):
            save_optimization_checkpoint(
                filepath=p,
                design_matrix_checksum=self.design_matrix_checksum,
                zed_checksum=self.zed_checksum,
                ridge_regularization=0.01,
                min_grad_value=1.e-05,
                max_iters=500,
                m=50,
                converged=False,
                reason="INCOMPLETE",
                iters=0,
                f=0.5,
                g_norm=0.25,
                w=self.w,
                sl=[self.w],
                yl=[],
                rho=[]
            )
        self.assertFalse(p.exists())

    def test_wrong_description_raises(self):
        """A file with a wrong header description is rejected."""
        p = Path(self._tmp.name) / "wrong_desc.dat"
        with binio.BinaryWriter(p) as bw:
            bw.write_header("Something Else", 1)
        with self.assertRaises(RuntimeError) as cm:
            load_optimization_checkpoint(p)
        self.assertIn("The file is not a proper optimization checkpoint. Found: Something Else", str(cm.exception))

    def test_wrong_version_raises(self):
        """A file with a wrong header version is rejected."""
        p = Path(self._tmp.name) / "wrong_version.dat"
        with binio.BinaryWriter(p) as bw:
            bw.write_header("RGLM Optimization Checkpoint", 2)
        with self.assertRaises(RuntimeError) as cm:
            load_optimization_checkpoint(p)
        self.assertIn("Checkpoint version mismatch: found 2, expected 1", str(cm.exception))

    def test_checksum_mismatch_raises(self):
        """R3 (D-096): load verifies the SHA3-256 sidecar; a corrupted
        content file is rejected."""
        data = bytearray(self.filepath.read_bytes())
        data[-1] ^= 0x01
        self.filepath.write_bytes(bytes(data))
        with self.assertRaises(RuntimeError) as cm:
            load_optimization_checkpoint(self.filepath)
        self.assertIn("Checkpoint checksum mismatch", str(cm.exception))

    def test_file_golden_hash(self):
        """The deterministic checkpoint bytes have a pinned SHA3-256."""
        h = hashlib.sha3_256(self.filepath.read_bytes()).hexdigest()
        self.assertEqual(h, "6e01ff8614e8732484b7af59b01615989357ce1af2419864621965af221bd280")

    def test_sidecar_produced_and_matches(self):
        """The checkpoint is written with its .SHA3-256 sidecar (binio default)."""
        sidecar = self.filepath.parent / (self.filepath.name + ".SHA3-256")
        self.assertTrue(sidecar.exists())
        self.assertTrue(binio.verify_sha3_256_sidecar(self.filepath))


class TestRLMOptimizeHelpers(unittest.TestCase):
    """Tests the standalone helper functions (no IO)."""

    def test_info_dict_filters_to_context_keys(self):
        """optimization_info_dict keeps exactly the 5 context keys."""
        info = optimization_info_dict({"converged": True, "reason": "X",
                                       "iters": 7, "f": 0.5, "g_norm": 0.1,
                                       "w": "extra", "sl": [1]})
        self.assertEqual(info, {"converged": True, "reason": "X", "iters": 7,
                                "f": 0.5, "g_norm": 0.1})

    def test_info_dict_missing_key_raises(self):
        """optimization_info_dict raises KeyError on a missing key."""
        with self.assertRaises(KeyError):
            optimization_info_dict({"converged": True})

    def test_weights_hash_golden(self):
        """weights_compute_sha3_256_hash is a plain sha3_256 of w.tobytes()."""
        w = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        h = weights_compute_sha3_256_hash(w)
        self.assertEqual(h, "78a7baac51aedf442b3de09a583af1a0704c8aece3b156aaf630780b2d7dc060")
        self.assertEqual(h, hashlib.sha3_256(w.tobytes()).hexdigest())


class TestRLMOptimizeCacheConsistency(unittest.TestCase):
    """Tests the cache validation logic (design matrix / zed / ridge gates)."""

    def setUp(self):
        self.ctx = _mock_ctx()

        self.cp_valid = {
            'design_matrix_checksum': "123abc",
            'zed_checksum': "456xyz",
            'ridge_regularization': 0.01
        }

        self.cp_changed_design_matrix_checksum = {
            'design_matrix_checksum': "654uhv",
            'zed_checksum': "456xyz",
            'ridge_regularization': 0.01
        }

        self.cp_changed_zed_checksum = {
            'design_matrix_checksum': "123abc",
            'zed_checksum': "725tfd",
            'ridge_regularization': 0.01
        }

        self.cp_changed_ridge = {
            'design_matrix_checksum': "123abc",
            'zed_checksum': "456xyz",
            'ridge_regularization': 0.02
        }

    def test_consistent_cache(self):
        self.assertTrue(is_optimization_cache_consistent(self.ctx, self.cp_valid))

    def test_inconsistent_design_matrix_checksum(self):
        self.assertFalse(is_optimization_cache_consistent(self.ctx, self.cp_changed_design_matrix_checksum))

    def test_inconsistent_zed_checksum(self):
        self.assertFalse(is_optimization_cache_consistent(self.ctx, self.cp_changed_zed_checksum))

    def test_inconsistent_ridge(self):
        """R1 (D-096): a ridge change invalidates the checkpoint (like a zed change)."""
        self.assertFalse(is_optimization_cache_consistent(self.ctx, self.cp_changed_ridge))


class TestRLMOptimizeStatusConverged(unittest.TestCase):
    """Tests the convergence-status logic against the current stopping tolerance."""

    def setUp(self):
        self.ctx = _mock_ctx(ridge=0.01, min_grad=(1e-3, 3))

    def _cp(self, g_norm, ridge=0.01, min_grad_value=1e-3):
        return {'ridge_regularization': ridge,
                'min_grad_value': min_grad_value,
                'g_norm': g_norm}

    def test_converged_below_tolerance(self):
        self.assertTrue(is_optimization_status_converged(self.ctx, self._cp(1e-4)))

    def test_not_converged_above_tolerance(self):
        self.assertFalse(is_optimization_status_converged(self.ctx, self._cp(0.5)))

    def test_f32_roundtrip_passes(self):
        """f32-stored checkpoint values do not trip the comparison gate."""
        cp = {'ridge_regularization': np.float32(0.01),
              'min_grad_value': np.float32(1e-3),
              'g_norm': np.float32(1e-4)}
        self.assertTrue(is_optimization_status_converged(self.ctx, cp))

    def test_judged_against_new_tolerance(self):
        """M3 (D-096): the stored g_norm is judged against the CURRENT min_grad
        (a looser tolerance accepts a checkpoint that was not converged before)."""
        self.ctx = _mock_ctx(ridge=0.01, min_grad=(1e-2, 3))
        self.assertTrue(is_optimization_status_converged(self.ctx, self._cp(5e-3)))


if __name__ == '__main__':
    unittest.main()
