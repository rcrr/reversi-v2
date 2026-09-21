#
# wrk_su_analysis.py
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
The SU_ANALYSIS worker (the SU level, step 3): the corpus
generator + the statistics. The wave corpus (the PRNG seed,
the ec arrest, the wave tier) is CACHED
(phase 1, the expensive part) — the first cache level whose
consistency signature carries the feature_set hash INSTEAD of
the rds_checksum (the new cache lineage). The
statistics (phase 2: the dispersion + the never-observed audit
+ the SU pairs) are cheap and recomputed on EVERY run, including
the cache hit. The level publishes the corpus frequency tables
on the ctx (the cross-level blackboard) for the EFFECT_SIZE
level (the adherence, step 6). The D-060 semantics: the
generation error fails the level, the machine re-raises, the
_down clears the ctx artifacts.
"""

from __future__ import annotations

import csv
import hashlib
import pickle
from pathlib import Path

from typing import TYPE_CHECKING

from pydantic import validate_call, ConfigDict

from reversi.tools.state_machine import Worker, Relevance
from reversi.tools.cache_manager import cache_manager_load_or_compute
from reversi.lm.hlp_random_play import (
    JointAccumulator, MarginalAccumulator)
from reversi.lm.hlp_wave import BufferSink, run_wave
from reversi.lm.hlp_feature_analysis import (
    dispersion, entropy, mutual_information, never_observed_audit,
    symmetric_uncertainty)

if TYPE_CHECKING:
    from reversi.lm.logistic_model import LMContext


__all__ = ['wrk_su_analysis']

# The wave size CEILING (the 1e6 benchmark default) + the
# generator / the PRNG version pins (the cache consistency
# signature). The wave is the PARALLELISM: the actual size is
# min(this, the corpus size), because the lanes beyond the corpus
# are pure overhead — the 1e6-lane arrays (~48 MB) and the per-step
# glue cost ~3.4 s for a 10k-position harvest that a 10k-lane wave
# does in ~0.04 s. The production corpora (1e7) keep 1e6 lanes.
_WAVE_SIZE = 1_000_000
# The corpus-generator version, part of the cache signature.
# "su-corpus-2" is the official start (the E4+D5 stones) + the
# neutral name (the old two-variant naming is dead). The
# superseded version "g0-1" marked the corpora generated with
# the SWAPPED initial position (the mover D4+E5 instead of the
# official E4+D5) — every cache written under it is STALE and
# must be regenerated. A version bump invalidates every cached
# corpus, which is exactly the point: the signature exists so
# that a change of the generator's behaviour can never be
# reused silently.
_GENERATOR_VERSION = "su-corpus-2"
_PRNG_VERSION = "mt19937-64"
_RARITY_THRESHOLDS = (1, 2, 5, 10, 100)
# The SU range legend (the report's interpretation key): the SU value
# bands + their meaning. The SU = 2·I / (H_u + H_v) in [0, 1] is the
# normalized shared information — the bias-compensated correlation.
_SU_LEGEND = (
    "SU        : Meaning",
    "0.0       : Perfect orthogonality",
    "0.0 - 0.1 : Excellent independence",
    "0.1 - 0.3 : Moderate correlation",
    "0.3 - 0.5 : Strong correlation",
    "over 0.5  : Very strong correlation",
)
# The Section A KPI legend (the per-sub-variable statistics key, the
# theoretical configuration space = n_unique_configs for a pattern /
# the value range for a mobility — the denominator of the coverage /
# the never-observed audit; D-278, the "theoretical" naming D-279).
_KPI_LEGEND = (
    "K_obs    : distinct configurations observed (of the theoretical "
    "space)",
    "H        : Shannon entropy of the observed distribution (bits)",
    "H_norm   : H / log2(K_obs) in [0,1] — 1.0 = uniform over the observed",
    "coverage : observed / theoretical — the ratio of observed to "
    "total theoretical configurations (some are unreachable by the "
    "game's rules)",
    "never-obs: theoretical − observed (theoretical configurations "
    "never seen)",
)


def _feature_set_hash(cfg) -> str:
    """The feature set hash (the cache consistency signature —
    the first cache level WITHOUT the rds_checksum, the
    feature_set hash instead): the sha3_256 of the
    feature_set config's normalized dump (the first 16 hex)."""
    dump = cfg.feature_set.model_dump_json(indent=2)
    return hashlib.sha3_256(dump.encode()).hexdigest()[:16]


def _signature(ctx) -> dict:
    """The cache consistency signature: the feature_set hash +
    the generation spec (the seed, the total_positions, the ec,
    the generator version, the PRNG version) + the su_pairs
    list (the canonical sorted form)."""
    corpus = ctx.cfg.su_analysis.corpus
    return {
        'feature_set_hash': _feature_set_hash(ctx.cfg),
        'seed': corpus.seed,
        'total_positions': corpus.total_positions,
        'ec': corpus.ec,
        'generator_version': _GENERATOR_VERSION,
        'prng_version': _PRNG_VERSION,
        'su_pairs': [list(p) for p in ctx.cfg.su_analysis.su_pairs],
    }


def _compute_tables(ctx) -> dict:
    """Phase 1 — the corpus (the expensive part): the SU-analysis corpus
    generator (the PRNG seed, the ec arrest, the wave
    semantics) + the streaming accumulation (the marginal + the
    joint for the requested pairs)."""
    cfg_fa = ctx.cfg.su_analysis
    fset = ctx.feature_set
    blocks = fset.feature_blocks
    corpus = cfg_fa.corpus
    ctx.log_event(Relevance.INFO,
                  f"Generating the SU_ANALYSIS corpus: "
                  f"[TOTAL: {corpus.total_positions:,}], [EC: {corpus.ec}], "
                  f"[SEED: {corpus.seed}], the wave tier.")
    sink = BufferSink()
    # The wave size is capped by the corpus: a smaller corpus needs
    # fewer lanes (every game is its own lane in one wave), and the
    # lanes beyond it only pay allocation + glue.
    wave_size = min(_WAVE_SIZE, corpus.total_positions)
    info = run_wave(corpus.total_positions, corpus.ec,
                       corpus.seed, wave_size, sink)
    mover, opp, _ = sink.flatten()
    marg = MarginalAccumulator(fset, blocks)
    marg.add(mover, opp)
    marginal = marg.result()
    joint = None
    if cfg_fa.su_pairs:
        joints = JointAccumulator(fset, blocks, cfg_fa.su_pairs)
        joints.add(mover, opp)
        joint = joints.result()
    ctx.log_event(Relevance.INFO,
                  f"Corpus generated: [HARVESTED: {info['harvested']:,}], "
                  f"[WAVES: {info['waves']}], [DEAD: {info['dead']:,}].")
    return {'signature': _signature(ctx), 'marginal': marginal,
            'joint': joint}


def _load_tables(path) -> dict:
    with open(path, 'rb') as f:
        return pickle.load(f)


def _store_tables(data, path) -> None:
    with open(path, 'wb') as f:
        pickle.dump(data, f)


def _is_consistent(ctx, cached) -> bool:
    """The cache consistency: the cached signature vs the live
    signature (the feature_set hash + the spec + the pairs)."""
    live = _signature(ctx)
    consistent = cached.get('signature', {}) == live
    ctx.log_event(Relevance.DEBUG,
                  f"SU_ANALYSIS cache consistent: {consistent}.")
    if not consistent:
        ctx.log_event(Relevance.DEBUG,
                      f"  cached: {cached.get('signature')}\n"
                      f"  live:   {live}")
    return consistent


def _marginal_lookup(marginal) -> dict:
    """The (name, instance_idx) -> counts lookup (the sub-
    variables' marginal counts, for the SU marginals)."""
    return {(name, i): counts
            for (name, i, _nc, _codes, counts) in marginal}


def _su_values(joint, lookup):
    """The requested SU pairs: for each configured
    (name_i, name_j) pair and each (inst_i, inst_j), the SU =
    2*I / (H_i + H_j) from the joint + the two marginals. The
    same-feature DIAGONAL (inst_i == inst_j) is OMITTED (the
    SU = 1 lock — not a measurement)."""
    su = []
    for (name_i, name_j, per_instance) in joint:
        same_feature = (name_i == name_j)
        for (ii, jj) in per_instance:
            if same_feature and ii == jj:
                continue  # The diagonal: the SU = 1 lock, omitted.
            codes_i, codes_j, counts = per_instance[(ii, jj)]
            mi = lookup.get((name_i, ii))
            mj = lookup.get((name_j, jj))
            if mi is None or mj is None:
                continue
            h_i = entropy(mi)
            h_j = entropy(mj)
            I = mutual_information(counts, mi, mj)
            su.append((name_i, ii, name_j, jj,
                       symmetric_uncertainty(I, h_i, h_j)))
    return su


def _feature_instances(marginal) -> list:
    """The distinct feature names, first-seen order (the model's
    features — the sub-variable names: LMC, EDGE, ...)."""
    seen = []
    for (name, _i, _nc, _codes, _counts) in marginal:
        if name not in seen:
            seen.append(name)
    return seen


def _theoretical_configs(fset) -> dict:
    """The (name, instance) -> THEORETICAL configuration count (D-278,
    the "theoretical" naming D-279): the denominator of the coverage +
    the never-observed audit. A PATTERN's observed codes are the
    PRINCIPAL indices (the orbit representatives), so its theoretical
    space is n_unique_configs (the number of equivalence classes under
    the pattern's symmetry — the distinct principal indices), NOT
    n_configurations (the raw 3^n); some of those are unreachable by
    the game's rules (the never-observed audit does not try to count
    them). A MOBILITY's codes are the raw values (no symmetry
    reduction), so its theoretical space is n_configurations."""
    space = {}
    for f in fset.features:
        if f.name == 'INTERCEPT':
            continue
        n_unique = getattr(f.ref, 'n_unique_configs', None)
        eff = n_unique if n_unique is not None else f.n_configurations
        for i in range(f.n_instances):
            space[(f.name, i)] = eff
    return space


def _su_canon(name_i, inst_i, name_j, inst_j) -> tuple:
    """The canonical endpoint order of a SU pair: the two
    (name, inst) tuples sorted. The (i, j) and the (j, i) directions
    of the SAME measurement map to the same canonical form."""
    a = (name_i, inst_i)
    b = (name_j, inst_j)
    return (a, b) if a <= b else (b, a)


def _su_groups(su_summary, su_pairs) -> list:
    """The deduplicated + sorted SU groups (the report's Section B).
    The SU is SYMMETRIC (2·I / (H_u + H_v)), so the (i, j) and the
    (j, i) directions of a pair are the SAME measurement — each is
    shown ONCE, in the canonical endpoint order. The groups are the
    feature-pairs (the header), in the configured order; within a
    group the entries are sorted by the CANONICAL ENDPOINT ORDER (the
    lexicographic (feature, instance) order: EDGE[0]-EDGE[1],
    EDGE[0]-EDGE[2], EDGE[1]-EDGE[2], ...)."""
    # 1. The dedup: the (i, j) and the (j, i) of a pair are one
    #    measurement — keep the first, in the canonical endpoint order.
    seen = set()
    deduped = []
    for (ni, ii, nj, jj, s) in su_summary:
        (an, ai), (bn, bi) = _su_canon(ni, ii, nj, jj)
        key = (an, ai, bn, bi)
        if key in seen:
            continue
        seen.add(key)
        deduped.append((an, ai, bn, bi, s))
    # 2. The group order: the configured feature-pairs (the canonical
    #    name order) first, then any not in the config (defensive).
    order = []
    for pair in su_pairs:
        gk = tuple(sorted(pair))
        if gk not in order:
            order.append(gk)
    for (an, _ai, bn, _bi, _s) in deduped:
        gk = tuple(sorted((an, bn)))
        if gk not in order:
            order.append(gk)
    # 3. The group + the sort (the SU descending + the canonical order).
    groups = {gk: [] for gk in order}
    for (an, ai, bn, bi, s) in deduped:
        groups[tuple(sorted((an, bn)))].append((an, ai, bn, bi, s))
    return [(gk, sorted(groups[gk],
                        key=lambda t: ((t[0], t[1]), (t[2], t[3]))))
            for gk in order]


def _export_csv(ctx, tables, su_groups) -> Path:
    """The optional CSV: the per-sub-variable marginal tables +
    the per-pair SU instance entries (the deduplicated + sorted
    groups, the report's Section B)."""
    cfg_fa = ctx.cfg.su_analysis
    csv_path = Path(ctx.cfg.base_dir) / cfg_fa.dir_name / \
        "su_analysis.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    theoretical = _theoretical_configs(ctx.feature_set)
    with open(csv_path, 'w', newline='', encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(['type', 'feature', 'inst', 'n_conf', 'k_obs',
                    'h', 'h_norm', 'coverage', 'never_observed', 'su'])
        for (name, i, nc, _codes, counts) in tables['marginal']:
            eff = theoretical.get((name, i), nc)
            d = dispersion(counts, eff)
            a = never_observed_audit(counts, eff, _RARITY_THRESHOLDS)
            w.writerow(['marginal', name, i, eff, d['k_obs'],
                        f"{d['h']:.6f}", f"{d['h_norm']:.6f}",
                        f"{d['coverage']:.6f}", a['never_observed'], ''])
        for gk, grp in su_groups:
            for (an, ai, bn, bi, s) in grp:
                w.writerow(['su', f"{an} - {bn}", f"{ai}x{bi}", '', '',
                            '', '', '', '', f"{s:.6f}"])
    return csv_path


def _compute_statistics(ctx, tables) -> Path:
    """Phase 2 — the statistics (cheap, recomputed on EVERY run,
    including the cache hit): the per-sub-variable dispersion +
    the never-observed audit + the requested SU pairs. The
    console (INFO) + the TXT report (dir_name under base_dir) +
    the optional CSV (the export_csv flag)."""
    cfg_fa = ctx.cfg.su_analysis
    marginal = tables['marginal']
    joint = tables['joint']
    lookup = _marginal_lookup(marginal)
    su_summary = _su_values(joint, lookup) if joint is not None else []
    su_groups = _su_groups(su_summary, cfg_fa.su_pairs)
    pairs_str = ", ".join(" - ".join(tuple(sorted(pair)))
                          for pair in cfg_fa.su_pairs) \
        if cfg_fa.su_pairs else "(none)"
    lines = ["Symmetrical Uncertainity Analysis Report", "=" * 40,
             "It evaluates the normalized relationship, dependency, "
             "or shared variance between variables,",
             "compensating for the inherent mathematical bias found "
             "in raw information gain."]
    lines += list(_SU_LEGEND)
    lines.append("")
    lines.append(f"Corpus: {cfg_fa.corpus.total_positions:,} positions")
    lines.append(f"Features: {', '.join(_feature_instances(marginal))}")
    lines.append(f"SU pairs: {pairs_str}")
    lines.append("")
    theoretical = _theoretical_configs(ctx.feature_set)
    lines.append("Section A: Properties of features selected by "
                 "the logistic model")
    lines.extend(_KPI_LEGEND)
    for (name, i, nc, _codes, counts) in marginal:
        eff = theoretical.get((name, i), nc)
        d = dispersion(counts, eff)
        a = never_observed_audit(counts, eff, _RARITY_THRESHOLDS)
        line = (f"  {name} inst {i}: K_obs {d['k_obs']}/{eff}, "
                f"H {d['h']:.3f}, H_norm {d['h_norm']:.3f}, "
                f"coverage {d['coverage']:.3f}, "
                f"never-obs {a['never_observed']}")
        lines.append(line)
        ctx.log_event(Relevance.INFO, line)
    lines.append("")
    lines.append("Section B: Symmetrical uncertainity")
    if not su_groups:
        lines.append("  (no SU pairs configured)")
    for gk, grp in su_groups:
        header = " - ".join(gk)
        lines.append(header)
        ctx.log_event(Relevance.INFO, header)
        for (an, ai, bn, bi, s) in grp[:20]:
            line = f"  SU {an}[{ai}] - {bn}[{bi}] = {s:.4f}"
            lines.append(line)
            ctx.log_event(Relevance.INFO, line)
        if not grp:
            lines.append("  (none)")
    report_path = Path(ctx.cfg.base_dir) / cfg_fa.dir_name / \
        cfg_fa.report_file_name
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    ctx.log_event(Relevance.INFO,
                  f"SU_ANALYSIS report written: {report_path}.")
    if cfg_fa.export_csv:
        csv_path = _export_csv(ctx, tables, su_groups)
        ctx.log_event(Relevance.INFO,
                      f"SU_ANALYSIS CSV written: {csv_path}.")
    return report_path


def _up(ctx: "LMContext") -> None:
    cfg_fa = ctx.cfg.su_analysis
    if not cfg_fa.enable:
        ctx.log_event(Relevance.INFO,
                      "SU_ANALYSIS disabled (enable: false) — no-op.")
        ctx.su_analysis_tables = None
        return
    # Phase 1 — the corpus (the expensive part, CACHED).
    cache_hit, tables, _checksum = cache_manager_load_or_compute(
        cache_path=ctx.get_cache_file_full_path_for_current_level(),
        is_allowed=ctx.use_cache,
        load_fn=_load_tables,
        store_fn=_store_tables,
        validate_fn=lambda cached: _is_consistent(ctx, cached),
        compute_fn=lambda: _compute_tables(ctx),
        logger_fn=ctx.log_event,
    )
    ctx.log_event(Relevance.INFO,
                  f"SU_ANALYSIS corpus: "
                  f"{'loaded from cache' if cache_hit else 'computed'}.")
    # Phase 2 — the statistics (cheap, recomputed on EVERY run).
    _compute_statistics(ctx, tables)
    # Publish the tables on the ctx (for the EFFECT_SIZE level).
    ctx.su_analysis_tables = tables
    ctx.log_event(Relevance.INFO,
                  "su_analysis_tables published on the ctx.")


def _down(ctx: "LMContext") -> None:
    ctx.log_event(Relevance.INFO,
                  "Clearing the su_analysis_tables attribute.")
    ctx.su_analysis_tables = None


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def wrk_su_analysis() -> Worker:
    """Factory function that returns the SU_ANALYSIS worker
    instance."""
    return Worker("SU_ANALYSIS", _up, _down)
