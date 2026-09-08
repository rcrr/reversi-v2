#
# tags.py
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
# along with this program; if not, you should have received one from
# the Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA  02111-1307, USA or visit the site
# <http://www.gnu.org/licenses/>.
#
#
#
# Suite tier gates (D-130). The suite runs in three tiers:
#
#   default   the fast tier (~4 s, no DB)
#   LONG=1    + the DB-gated pipeline tests (~45 s)
#   VLONG=1   + the ~10-min A2050 end-to-end chain (implies LONG)
#
# PERF=1 is orthogonal (the print-only performance tests, D-036)
# and SKIP_REGAB_DB=1 is orthogonal too (a no-DB environment skips
# every DB test whatever the tier).
#
# Usage (called on the test case, FIRST in setUp, as the D-080
# T2 gate shape):
#
#     from reversi.test.tags import db_long_gate
#     ...
#     def setUp(self):
#         db_long_gate(self)
#         ...

import os

__all__ = ['db_long_gate']


def db_long_gate(testcase):
    """Skip the DB-gated (LONG-tier) test when the live regab DB
    is unavailable or the LONG tier was not requested.

    LONG=1 enables the tier; VLONG=1 implies LONG. A
    no-DB environment (SKIP_REGAB_DB=1) always skips, before
    the tier check.
    """
    no_db = os.getenv('SKIP_REGAB_DB', '0') == '1'
    long_on = (os.getenv('LONG', '0') == '1'
               or os.getenv('VLONG', '0') == '1')
    if no_db or not long_on:
        testcase.skipTest(
            'DB test: live regab DB + LONG=1 required '
            '(VLONG=1 implies LONG)')
