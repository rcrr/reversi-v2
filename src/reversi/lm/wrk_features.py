#
# wrk_features.py
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

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import validate_call, ConfigDict

from reversi.tools.state_machine import Worker, Relevance
from reversi.feature import Feature, FeatureSet
from reversi.mobility import Mobility, MobilitySet
from reversi.pattern import Pattern, PatternSet

if TYPE_CHECKING:
    from reversi.lm.logistic_model import LMContext



__all__ = ['wrk_features']



def _up(ctx: "LMContext") -> None:
    """
    Run the FEATURES level: build the FeatureSet from the CONFIG-loaded cfg (the three loaders) and
    publish it on the context.
    """
    ctx.log_event(Relevance.INFO, "Loading board features as defined by the model...")
    ctx.feature_set = _load_features(ctx)


def _down(ctx: "LMContext") -> None:
    """Clear the feature set published on the context."""
    ctx.log_event(Relevance.INFO, "Clearing features...")
    ctx.feature_set = None


def _load_features(ctx: "LMContext") -> FeatureSet:
    """
    Build the FeatureSet (the three loaders + the schema name), enforce the zero-feature guard, and
    log the summary + the per-feature table.
    """
    intercept = _load_intercept(ctx)
    mset = _load_mobility(ctx)
    pset = _load_patterns(ctx)
    name = ctx.cfg.feature_set.name
    feature_set = FeatureSet(name, intercept, mset, pset)
    ctx.log_event(Relevance.DEBUG, f"Feature set object created, hash = '{feature_set.hash}'.")
    n_features = len(feature_set.features)
    if n_features == 0:
        error_msg = (f"The feature count is zero. "
                     "It is not possible to generate a model without features.")
        ctx.log_event(Relevance.ERROR, error_msg)
        raise ValueError(error_msg)
    ctx.log_event(Relevance.INFO,
                  f"Feature set: name = '{feature_set.name}', hash = {feature_set.hash}")
    ctx.log_event(Relevance.INFO, f"  has Intercept: {feature_set.intercept is not None}")
    ctx.log_event(Relevance.INFO, f"  has MobilitySet: {feature_set.mset is not None}")
    if feature_set.mset is not None:
        ctx.log_event(Relevance.INFO,
                      f"    MobilitySet: name = {feature_set.mset.name}, "
                      f"hash = {feature_set.mset.hash}")
    ctx.log_event(Relevance.INFO, f"  has PatternSet: {feature_set.pset is not None}")
    if feature_set.pset is not None:
        ctx.log_event(Relevance.INFO,
                      f"    PatternSet: name = {feature_set.pset.name}, "
                      f"hash = {feature_set.pset.hash}")
    ctx.log_event(Relevance.DEBUG,
                  f"  Features list: [<i>, <category>, <name>, <n_instances>, <n_configurations>]")
    for i, f in enumerate(feature_set.features):
        ctx.log_event(Relevance.DEBUG,
                      f"    {i:03d} [{f.category}] {f.name:10s} "
                      f"{f.n_instances} {f.n_configurations:8d}")

    return feature_set


def _load_intercept(ctx: "LMContext") -> Feature:
    """The intercept feature (INTERCEPT, 1/1) when the cfg bool is truthy, else None."""
    cfg_intercept = ctx.cfg.feature_set.intercept
    ctx.log_event(Relevance.DEBUG, f"Intercept feature configuration: '{cfg_intercept}'")
    if cfg_intercept:
        intercept = Feature.new_intercept()
        ctx.log_event(Relevance.DEBUG, f"Intercept feature created.")
    else:
        intercept = None
    return intercept


def _load_patterns(ctx: "LMContext") -> PatternSet:
    """The PatternSet from the cfg elements, or None when the cfg has no pattern set."""
    cfg_pset = ctx.cfg.feature_set.pattern_set
    if cfg_pset:
        pset_name = cfg_pset.name
        ctx.log_event(Relevance.DEBUG, f"Pattern set name: '{pset_name}', patterns:")
        patterns = [Pattern(elt.name, elt.mask) for elt in cfg_pset.patterns]
        for i, p in enumerate(patterns):
            ctx.log_event(Relevance.DEBUG,
                          f"  -{i:02}- Pattern: name = {p.name:8s}, mask = {p.mask:016X}")
        pset = PatternSet(cfg_pset.name, patterns)
        ctx.log_event(Relevance.DEBUG, f"Pattern set object created, hash = '{pset.hash}'.")
    else:
        pset = None
    return pset


def _load_mobility(ctx: "LMContext") -> MobilitySet:
    """The MobilitySet from the cfg elements, or None when the cfg has no mobility set."""
    cfg_mset = ctx.cfg.feature_set.mobility_set
    if cfg_mset:
        mset_name = cfg_mset.name
        ctx.log_event(Relevance.DEBUG, f"Mobility set name: '{mset_name}', mobilities:")
        mobility_features = [
            Mobility(elt.name, elt.mask, elt.amask) for elt in cfg_mset.mobility_features]
        for i, m in enumerate(mobility_features):
            ctx.log_event(Relevance.DEBUG,
                          f"  -{i:02}- Mobility: name = {m.name:8s}, mask = {m.mask:016X}, "
                          f"amask = {m.amask:016X}")
        mset = MobilitySet(cfg_mset.name, mobility_features)
        ctx.log_event(Relevance.DEBUG, f"Mobility set object created, hash = '{mset.hash}'.")
    else:
        mset = None
    return mset


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def wrk_features() -> Worker:
    """Return the FEATURES worker instance."""
    return Worker("FEATURES", _up, _down)

