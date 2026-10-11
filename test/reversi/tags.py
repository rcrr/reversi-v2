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
# Suite tier gates. The
# suite runs in four tiers, each implying the previous ones:
#
#   default    the fast tier (no DB)
#   LONG=1     + the DB-gated pipeline tests
#   VLONG=1    + the long instruments (the ~10-min A2050 end-to-end
#                chain; implies LONG)
#   VVLONG=1   + the very-long instruments (currently uninstrumented;
#                implies VLONG -> LONG)
#
# PERF=1 is orthogonal (the print-only performance tests)
# and SKIP_REGAB_DB=1 is orthogonal too (a no-DB environment skips
# every DB test whatever the tier).
#
# Usage (called on the test case, FIRST in setUp, as the
# standard gate shape):
#
#     from test.reversi.tags import db_long_gate
#     ...
#     def setUp(self):
#         db_long_gate(self)
#         ...

import os

__all__ = ['db_long_gate', 'tier_vlong', 'tier_vvlong']


def db_long_gate(testcase):
    """
    Skip the DB-gated (LONG-tier) test when the live regab DB is unavailable or the LONG tier was
    not requested.

    LONG=1 enables the tier; VLONG=1 and VVLONG=1 imply it. A no-DB environment (SKIP_REGAB_DB=1)
    always skips, before the tier check.
    """
    no_db = os.getenv('SKIP_REGAB_DB', '0') == '1'
    long_on = os.getenv('LONG', '0') == '1' or tier_vlong()
    if no_db or not long_on:
        testcase.skipTest(
            'DB test: live regab DB + LONG=1 required '
            '(VLONG=1 and VVLONG=1 imply LONG)')


def tier_vlong() -> bool:
    """
    True when the VLONG tier is on: VLONG=1, or VVLONG=1 (which implies VLONG -> LONG). The LONG
    instruments gate on this.
    """
    return (os.getenv('VLONG', '0') == '1'
            or tier_vvlong())


def tier_vvlong() -> bool:
    """
    True when the VVLONG tier is on: VVLONG=1 only (it implies VLONG -> LONG). The VERY-long
    instruments gate on this.
    """
    return os.getenv('VVLONG', '0') == '1'
