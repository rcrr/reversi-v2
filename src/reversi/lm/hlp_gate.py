#
# hlp_gate.py
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

"""
The campaign config loader (the pipeline's own loader): loads the
campaign JSON5 + the FeatureSet (the wrk_features pure mapping) +
the per-feature column blocks (the documented column layout). The
worker tests (test_wrk_su_analysis, test_wrk_effect_size)
use it to build the campaign (the feature set + the column
blocks) for the accumulator / the effect-size tests.
"""

from __future__ import annotations

__all__ = ['load_campaign']


def load_campaign(config_path: str):
    """
    Loads the campaign config (json5, the pipeline's own
    loader) + the FeatureSet (the wrk_features pure mapping)
    + the per-feature column blocks (the documented column
    layout: the intercept, then the mobilities in the (mask,
    amask) sorted order, then the patterns in the mask sorted
    order — the fset.features order).

    Returns:
      (cfg, fset, blocks) — blocks: the list of
      (name, col_start, col_end, n_conf, n_inst) over the
      non-intercept features (the gate's sub-variables).
    """
    import json5
    from reversi.feature import Feature, FeatureSet
    from reversi.lm.hlp_config_schemas import LMConfig
    from reversi.mobility import Mobility, MobilitySet
    from reversi.pattern import Pattern, PatternSet

    with open(config_path, 'r', encoding='utf-8') as f:
        raw = json5.load(f)
    cfg = LMConfig(**raw)
    fsc = cfg.feature_set
    fset = FeatureSet(
        fsc.name,
        Feature.new_intercept() if fsc.intercept else None,
        (MobilitySet(fsc.mobility_set.name,
                     [Mobility(e.name, e.mask, e.amask)
                      for e in fsc.mobility_set.mobility_features])
         if fsc.mobility_set else None),
        (PatternSet(fsc.pattern_set.name,
                    [Pattern(e.name, e.mask)
                     for e in fsc.pattern_set.patterns])
         if fsc.pattern_set else None))
    return cfg, fset, fset.feature_blocks
