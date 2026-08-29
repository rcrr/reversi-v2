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
# time python3 -m unittest twolm.test.test_opt_lbfgs
#

import unittest
import numpy as np
import numpy.testing as nptest

from twolm.opt_lbfgs import lbfgs, FixedSizeMaxList, _two_loop_recursion


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
        np.random.seed(42)
        n, m = 5, 3
        s_list, y_list, rho_list = [], [], []
        for _ in range(m):
            s = np.random.randn(n)
            y = 2 * s + 0.1 * np.random.randn(n)
            s_list.append(s)
            y_list.append(y)
            rho_list.append(1.0 / np.dot(y, s))
        g = np.random.randn(n)
        r = _two_loop_recursion(g, s_list, y_list, rho_list)
        self.assertEqual(r.shape, g.shape)
        self.assertGreater(np.linalg.norm(r), 1e-10,
                           'two-loop result should be non-zero for random input')


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
        actual_x_min, _ = lbfgs(self.fg, x0, max_iters=100, m=5, min_grad=(1e-5, 1), log_every_n=0, debug_plot=False)
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
        np.random.seed(42) # Set seed for reproducibility
        x0 = np.random.uniform(low=-5., high=5., size=(d,))
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
        # Updated save_fn signature to match opt_lbfgs.py (added f and g_norm)
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


if __name__ == '__main__':
    unittest.main()
