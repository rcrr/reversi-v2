#
# test_hlp_analytics.py
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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA
# or visit the site <http://www.gnu.org/licenses/>.
#

# How to run the hlp_analytics unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests.
#
# time PERF=0 python3 -m unittest test.reversi.lm.test_hlp_analytics
#

import math
import unittest

from reversi.lm.hlp_analytics import _su_header_line, _su_verdict


class TestSuVerdict(unittest.TestCase):
    """The SU sample consistency verdict over the TV bands (the boundaries are inclusive)."""

    def test_consistent_band(self):
        self.assertEqual(_su_verdict(0.0), 'CONSISTENT')
        self.assertEqual(_su_verdict(0.01), 'CONSISTENT')

    def test_marginal_band(self):
        self.assertEqual(_su_verdict(0.02), 'MARGINAL')
        self.assertEqual(_su_verdict(0.05), 'MARGINAL')

    def test_deviating_band(self):
        self.assertEqual(_su_verdict(0.051), 'DEVIATING')
        self.assertEqual(_su_verdict(0.5), 'DEVIATING')


class TestSuHeaderLine(unittest.TestCase):
    """The 'SU Sample Consistency' header line: the disabled / too-small / ok / degenerate forms."""

    def test_disabled_level_is_none(self):
        self.assertIsNone(_su_header_line(None))

    def test_too_small_note(self):
        line = _su_header_line({'mode': 'too_small', 'corpus': 3, 'train': 100})
        self.assertIn('N/A (SU corpus too small: 3 < 2x training 100)', line)

    def test_ok_line_carries_tv_chi2_verdict(self):
        stats = {'mode': 'ok', 'pooled': {}, 'corpus_total': 300,
                 'adh': {'tv': 0.005, 'chi2': 1.2, 'p': 0.5, 'merged': 0}}
        line = _su_header_line(stats)
        self.assertIn('TV 0.0050', line)
        self.assertIn('chi2 1.2', line)
        self.assertIn('CONSISTENT', line)

    def test_degenerate_nan_tv(self):
        stats = {'mode': 'ok', 'pooled': {}, 'corpus_total': 1,
                 'adh': {'tv': math.nan, 'chi2': 0.0, 'p': 0.0, 'merged': 0}}
        self.assertIn('N/A (degenerate)', _su_header_line(stats))

    def test_inf_chi2_rendered(self):
        stats = {'mode': 'ok', 'pooled': {}, 'corpus_total': 10,
                 'adh': {'tv': 0.001, 'chi2': math.inf, 'p': math.nan, 'merged': 1}}
        line = _su_header_line(stats)
        self.assertIn('chi2 inf', line)
        self.assertIn('p nan', line)


if __name__ == "__main__":
    unittest.main()
