#
# closecheck.py
#
# This file is part of the reversi program
# http://github.com/rcrr/reversi-v2
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
# along with this program; if not, you should have received one from
# the Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA  02111-1307, USA or visit the site
# <http://www.gnu.org/licenses/>.
#
#
# Tolerant float comparison for the float64 pipeline-metric goldens.
#
# The metric reductions (np.dot over up to ~2M f64 terms — hlp_analytics.py
# L459/L509, hlp_validate.py) run through the multi-threaded OpenBLAS ddot:
# the last ULPs depend on the thread count and the DYNAMIC_ARCH CPU kernel
# of the machine running the tests, so the float metric goldens compare
# within a small relative tolerance.
#
# The bit-exact pins STAY exact (assertEqual): the int/uint counts,
# the f32-quantized values (train_loss = float(opt f32), g_norm, the
# tps read-back truncations), the sha3_256 file/array hashes, the EF
# pins and the second-instance determinism tests (the in-run
# bit-identity contract).
#
# Usage (a plain function called on the test case):
#
#     from test.reversi.closecheck import assert_close
#     assert_close(self, met['train_rmse_y'], 15.58872172931622,
#                  'train_rmse_y')

import math

__all__ = ['assert_close', 'REL_TOL', 'ABS_TOL']

# The goldens must agree to ~10 significant digits. The measured environment drift is <= 4e-14
# relative; a genuine pipeline regression (a wrong feature, wrong samples, a broken reduction) shows
# up at >= 1e-6, so this leaves ~5 orders of magnitude of detection margin.
REL_TOL = 1e-9

# Absolute floor for near-zero values (the small validation losses).
ABS_TOL = 1e-12


def assert_close(testcase, got, want, label=''):
    """
    Assert that got is within REL_TOL (relative) / ABS_TOL (absolute) of the golden want, with a
    descriptive failure message showing the actual relative difference.
    """
    rel = abs(got - want) / max(abs(want), 1e-300)
    ok = math.isclose(got, want, rel_tol=REL_TOL, abs_tol=ABS_TOL)
    testcase.assertTrue(
        ok,
        f"{label or 'value'}: got {got!r}, golden {want!r} "
        f"(rel diff {rel:.2e}; tolerance rel {REL_TOL:.0e} / abs {ABS_TOL:.0e})")
