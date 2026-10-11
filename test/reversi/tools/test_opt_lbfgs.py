#
# test_opt_lbfgs.py
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
# How to use the unit tests opt_lbfgs module.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests.
#
# time python3 -m unittest test.reversi.tools.test_opt_lbfgs
#

import unittest
import numpy as np
import numpy.testing as nptest

from reversi.tools.opt_lbfgs import lbfgs, FixedSizeMaxList, _two_loop_recursion


class TestLBFGSInputValidation(unittest.TestCase):
    """Tests input validation in lbfgs()."""

    @staticmethod
    def _quad_fg(x):
        f = 0.5 * (x[0]**2 + x[1]**2)
        return f, x.copy()

    def test_non_ndarray_x0_raises(self):
        with self.assertRaises(TypeError):
            lbfgs(self._quad_fg, 'not_an_array', max_iters=5)

    def test_wrong_dtype_raises(self):
        with self.assertRaises(TypeError):
            lbfgs(self._quad_fg, np.array([1, 2], dtype=np.int32), max_iters=5)

    def test_non_callable_fg_raises(self):
        with self.assertRaises(TypeError):
            lbfgs('not_callable', np.array([1.0, 2.0]), max_iters=5)

    def test_max_iters_zero_raises(self):
        with self.assertRaises(ValueError):
            lbfgs(self._quad_fg, np.array([1.0, 2.0]), max_iters=0)

    def test_initial_iter_at_max_raises(self):
        with self.assertRaises(ValueError):
            lbfgs(self._quad_fg, np.array([1.0, 2.0]), max_iters=5, initial_iter=5)


class TestFixedSizeMaxList(unittest.TestCase):
    """Tests the FixedSizeMaxList helper."""

    def test_max_on_empty_raises(self):
        fsl = FixedSizeMaxList(3)
        with self.assertRaises(RuntimeError):
            fsl.max()

    def test_push_and_max(self):
        fsl = FixedSizeMaxList(3)
        fsl.push(1.0)
        fsl.push(3.0)
        fsl.push(2.0)
        self.assertEqual(fsl.max(), 3.0)
        self.assertEqual(len(fsl), 3)

    def test_eviction(self):
        fsl = FixedSizeMaxList(2)
        fsl.push(5.0)
        fsl.push(1.0)
        fsl.push(3.0)  # evicts 5.0
        self.assertEqual(fsl.max(), 3.0)
        self.assertEqual(len(fsl), 2)

    def test_len_zero_initially(self):
        fsl = FixedSizeMaxList(5)
        self.assertEqual(len(fsl), 0)


class TestTwoLoopRecursion(unittest.TestCase):
    """Tests the L-BFGS two-loop recursion."""

    def test_empty_history_returns_identity(self):
        g = np.array([1.0, -2.0, 0.5])
        r = _two_loop_recursion(g, [], [], [])
        nptest.assert_allclose(r, g, atol=1e-15)

    def test_random_pairs_shape_and_descent(self):
        rng = np.random.default_rng(42)
        n, m = 5, 3
        s_list, y_list, rho_list = [], [], []
        for _ in range(m):
            s = rng.standard_normal(n)
            y = 2 * s + 0.1 * rng.standard_normal(n)
            s_list.append(s)
            y_list.append(y)
            rho_list.append(1.0 / np.dot(y, s))
        g = np.random.randn(n)
        r = _two_loop_recursion(g, s_list, y_list, rho_list)
        self.assertEqual(r.shape, g.shape)
        self.assertGreater(np.linalg.norm(r), 1e-10,
                           'two-loop result should be non-zero for random input')

    def test_out_equals_original_bit_identical(self):
        # The pre-allocated out= product buffer must reproduce the original per-op-temporary
        # algorithm BIT-FOR-BIT (the f64 product + the f32 in-place downcast are the original's
        # exact dtype semantics) — the L-BFGS trajectory is therefore unchanged. The reference is
        # the original algorithm, verbatim.
        def reference(g, s_list, y_list, rho_list):
            m = len(s_list)
            alpha = np.zeros(m)
            delta = g.copy()
            for i in reversed(range(m)):
                alpha[i] = rho_list[i] * np.dot(s_list[i], delta)
                delta -= alpha[i] * y_list[i]
            if m > 0:
                gamma = (np.dot(s_list[-1], y_list[-1])
                         / np.dot(y_list[-1], y_list[-1]))
            else:
                gamma = 1.0
            r = gamma * delta
            for i in range(m):
                beta = rho_list[i] * np.dot(y_list[i], r)
                r += s_list[i] * (alpha[i] - beta)
            return r

        for seed, n, m, dt in ((0, 50, 5, np.float32),
                               (1, 500, 9, np.float32),
                               (2, 64, 7, np.float64)):
            with self.subTest(seed=seed, n=n, m=m, dt=dt.__name__):
                rng = np.random.default_rng(seed)
                s_list, y_list, rho_list = [], [], []
                for _ in range(m):
                    s = (rng.standard_normal(n) * 0.3).astype(dt)
                    y = (2 * s + 0.1 * (rng.standard_normal(n) * 0.3)).astype(dt)
                    s_list.append(s)
                    y_list.append(y)
                    rho_list.append(1.0 / float(np.dot(y, s)))
                g = (rng.standard_normal(n) * 0.5).astype(dt)
                r_new = _two_loop_recursion(g, s_list, y_list, rho_list)
                r_ref = reference(g, s_list, y_list, rho_list)
                self.assertTrue(np.array_equal(r_new, r_ref),
                                'the two-loop is not bit-identical to the reference '
                                f'(seed={seed}, dt={dt.__name__})')


class TestLBFGSBaseFunction(unittest.TestCase):
    """Tests L-BFGS on a simple quadratic function."""

    def __init__(self, *args, **kwargs):
        super(TestLBFGSBaseFunction, self).__init__(*args, **kwargs)
        self.x_min = np.array([-1.0, 1.5])

    def fg(self, x):
        fun_value = x[0] - x[1] + 2*x[0]*x[1] + 2*x[0]**2 + x[1]**2
        jac_value = np.array([ 1 + 2*x[1] + 4*x[0],
                               -1 + 2*x[0] + 2*x[1] ])
        return fun_value, jac_value

    def test_a_optimization(self):
        x0 = np.array([0.0, 0.0])
        actual_x_min, _ = lbfgs(self.fg, x0, max_iters=100, m=5, min_grad=(1e-5, 1), log_every_n=0)
        nptest.assert_allclose(actual_x_min, self.x_min, atol=1.e-3)


class TestLBFGSRosenbrockFunction(unittest.TestCase):
    """Tests L-BFGS on the Rosenbrock function."""

    def __init__(self, *args, **kwargs):
        super(TestLBFGSRosenbrockFunction, self).__init__(*args, **kwargs)
        self.x_min = np.array([1.0, 1.0])
        self.fun_min_value = 0.0

    def fg(self, x):
        fun_value = (1 - x[0])**2 + 100 * (x[1] - x[0]**2)**2
        jac_value = np.array([-2 * (1 - x[0]) - 400 * (x[1] - x[0]**2)*x[0],
                              200*(x[1] - x[0]**2) ])
        return fun_value, jac_value

    def test_a_optimization(self):
        x0 = np.array([-1.0, -1.0])
        actual_x_min, _ = lbfgs(self.fg, x0, max_iters=1000, m=5, min_grad=(1e-5, 1), log_every_n=0)
        nptest.assert_allclose(actual_x_min, self.x_min, atol=1.e-4)


class TestLBFGSZakharovFunction(unittest.TestCase):
    """Tests L-BFGS on the Zakharov function."""

    def __init__(self, *args, **kwargs):
        super(TestLBFGSZakharovFunction, self).__init__(*args, **kwargs)
        self.fun_min_value = 0.0

    def fg(self, x):
        d = self.d
        sum1 = 0.
        sum2 = 0.
        a = np.array([x for x in range(1, 1 + d)], dtype=np.double)
        for i in range(0, d):
            xi = x[i]
            sum1 += xi * xi
            sum2 += 0.5 * (i + 1) * xi
        sum22 = sum2 * sum2
        y = sum1 + sum22 + sum22 * sum22
        y1 = 2. * x + ( 1. + 2. * sum22 ) * sum2 * a
        return y, y1

    def test_a_optimization(self):
        d = 20
        self.d = d
        self.x_min = np.zeros((d,), dtype=np.double)
        rng = np.random.default_rng(42)
        x0 = rng.uniform(low=-5., high=5., size=(d,))
        actual_x_min, _ = lbfgs(self.fg, x0, max_iters=1000, m=5, min_grad=(1e-5, 1), log_every_n=0)
        nptest.assert_allclose(actual_x_min, self.x_min, atol=1.e-5)


class TestLBFGSWarmStart(unittest.TestCase):
    """Tests the ability to resume optimization from a saved state."""

    def fg(self, x):
        fun_value = (1 - x[0])**2 + 100 * (x[1] - x[0]**2)**2
        jac_value = np.array([-2 * (1 - x[0]) - 400 * (x[1] - x[0]**2)*x[0],
                              200*(x[1] - x[0]**2) ])
        return fun_value, jac_value

    def test_resume_optimization(self):
        x0 = np.array([-1.0, -1.0])

        # 1. Run for 100 iterations continuously
        x_final_continuous, _ = lbfgs(self.fg, x0, max_iters=100, m=5, min_grad=(1e-9, 7), log_every_n=0)

        # 2. Run for 50 iterations and save state
        saved_state = {}

        def save_fn(x, sl, yl, rho, k, f, g_norm):
            saved_state['x'] = x
            saved_state['sl'] = sl
            saved_state['yl'] = yl
            saved_state['rho'] = rho

        lbfgs(self.fg, x0, max_iters=50, m=5, min_grad=(1e-9, 7), log_every_n=0, save_every_n=10, save_fn=save_fn)

        # 3. Resume from saved state for another 50 iterations
        x_final_resumed, _ = lbfgs(
            self.fg,
            saved_state['x'],
            max_iters=50,
            m=5,
            min_grad=(1e-9, 7),
            log_every_n=0,
            initial_sl=saved_state['sl'],
            initial_yl=saved_state['yl'],
            initial_rho=saved_state['rho']
        )

        # The results should be very close (allowing for minor line-search differences at the exact resume point)
        nptest.assert_allclose(x_final_resumed, x_final_continuous, atol=1e-4)


class TestLBFGSInfoContract(unittest.TestCase):
    """
    Tests the info dict contract, the history cap, the x0 immutability and the float32 contract.
    """

    def __init__(self, *args, **kwargs):
        super(TestLBFGSInfoContract, self).__init__(*args, **kwargs)

    def fg(self, x):
        fun_value = (1 - x[0]) ** 2 + 100 * (x[1] - x[0] ** 2) ** 2
        jac_value = np.array([-2 * (1 - x[0]) - 400 * (x[1] - x[0] ** 2) * x[0],
                              200 * (x[1] - x[0] ** 2)])
        return fun_value, jac_value

    def test_info_dict_keys_and_consistency(self):
        x0 = np.array([-1.0, -1.0])
        x, info = lbfgs(self.fg, x0, max_iters=100, m=5, min_grad=(1e-6, 1))
        self.assertEqual(set(info),
                         {'w', 'converged', 'reason', 'iters', 'f', 'g_norm', 'sl', 'yl', 'rho'})
        self.assertIs(info['w'], x)
        self.assertIsInstance(info['iters'], int)
        self.assertGreater(info['iters'], 0)
        self.assertLessEqual(info['iters'], 100)
        self.assertEqual(info['f'], self.fg(x)[0])
        self.assertEqual(info['g_norm'], np.linalg.norm(self.fg(x)[1]))
        self.assertEqual(len(info['sl']), len(info['yl']))
        self.assertEqual(len(info['sl']), len(info['rho']))

    def test_history_capped_at_m(self):
        x0 = np.array([-1.0, -1.0])
        x, info = lbfgs(self.fg, x0, max_iters=100, m=2, min_grad=(1e-8, 3))
        self.assertGreaterEqual(len(info['sl']), 1)
        self.assertLessEqual(len(info['sl']), 2)

    def test_x0_not_mutated(self):
        x0 = np.array([-1.0, -1.0])
        x0_before = x0.copy()
        x, _ = lbfgs(self.fg, x0, max_iters=20, m=5, min_grad=(1e-6, 1))
        self.assertTrue(np.array_equal(x0, x0_before))
        self.assertFalse(np.array_equal(x, x0_before))

    def test_float32_end_to_end(self):
        x0 = np.array([-1.0, -1.0], dtype=np.float32)
        x, info = lbfgs(self.fg, x0, max_iters=100, m=5, min_grad=(1e-6, 1))
        self.assertEqual(x.dtype, np.float32)
        for s in info['sl']:
            self.assertEqual(s.dtype, np.float32)
        for y in info['yl']:
            self.assertEqual(y.dtype, np.float32)
        self.assertEqual(np.asarray(info['g_norm']).dtype, np.float32)

    def test_logger_called(self):
        lines = []
        x0 = np.array([-1.0, -1.0])
        x, _ = lbfgs(self.fg, x0, max_iters=5, m=5, min_grad=(1e-6, 1),
                     log_every_n=1, logger=lines.append)
        self.assertGreater(len(lines), 0)
        self.assertTrue(all(isinstance(l, str) for l in lines))


class TestLBFGSStopReasons(unittest.TestCase):
    """Tests the three documented stop reasons of lbfgs() at runtime."""

    def _quad_fg(self, x):
        fun_value = 0.5 * (x[0] ** 2 + x[1] ** 2)
        return fun_value, x.copy()

    def test_converged_min_grad(self):
        x0 = np.array([3.0, -2.0])
        x, info = lbfgs(self._quad_fg, x0, max_iters=100, m=5, min_grad=(1e-8, 1))
        self.assertTrue(info['converged'])
        self.assertEqual(info['reason'], 'CONVERGED_MIN_GRAD')

    def test_max_iters_reached(self):
        def rosen_fg(x):
            fun_value = (1 - x[0]) ** 2 + 100 * (x[1] - x[0] ** 2) ** 2
            grad = np.array([-2 * (1 - x[0]) - 400 * (x[1] - x[0] ** 2) * x[0],
                             200 * (x[1] - x[0] ** 2)])
            return fun_value, grad

        x0 = np.array([-1.0, -1.0])
        x, info = lbfgs(rosen_fg, x0, max_iters=2, m=5, min_grad=(1e-12, 3))
        self.assertFalse(info['converged'])
        self.assertEqual(info['reason'], 'MAX_ITERS_REACHED')
        self.assertEqual(info['iters'], 2)

    def test_converged_low_progress(self):
        def flat_fg(x):
            fun_value = 1.0 + 1e-12 * (x[0] ** 2 + x[1] ** 2)
            return fun_value, 2e-12 * x

        x0 = np.array([1.0, 1.0])
        x, info = lbfgs(flat_fg, x0, max_iters=20, m=5, min_grad=(1e-30, 5),
                        min_p_fun_decrease=(1e-9, 2))
        self.assertTrue(info['converged'])
        self.assertEqual(info['reason'], 'CONVERGED_LOW_PROGRESS')


if __name__ == '__main__':
    unittest.main()
