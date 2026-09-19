#
# wrk_feature_analysis.py
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
The FEATURE_ANALYSIS worker (the I-017, the SU level, step 3,
D-186): the corpus generator + the statistics. The D-174 G0
corpus (the PRNG seed, the ec arrest, the wave tier) is CACHED
(phase 1, the expensive part) — the first cache level whose
consistency signature carries the feature_set hash INSTEAD of
the rds_checksum (the P5, the new cache lineage). The
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
from reversi.lm.hlp_wave import BufferSink, run_wave_g0
from reversi.lm.hlp_feature_analysis import (
    dispersion, entropy, mutual_information, never_observed_audit,
    symmetric_uncertainty)

if TYPE_CHECKING:
    from reversi.lm.logistic_model import LMContext


__all__ = ['wrk_feature_analysis']

# The G0 wave size CEILING (the 1e6 benchmark default) + the
# generator / the PRNG version pins (the cache consistency
# signature, P5). The wave is the PARALLELISM: the actual size is
# min(this, the corpus size), because the lanes beyond the corpus
# are pure overhead — the 1e6-lane arrays (~48 MB) and the per-step
# glue cost ~3.4 s for a 10k-position harvest that a 10k-lane wave
# does in ~0.04 s. The production corpora (1e7) keep 1e6 lanes.
_WAVE_SIZE = 1_000_000
_GENERATOR_VERSION = "g0-1"
_PRNG_VERSION = "mt19937-64"
_RARITY_THRESHOLDS = (1, 2, 5, 10, 100)


def _feature_blocks(fset):
    """The per-feature column blocks (the fset.features order —
    the documented column layout: the intercept, then the
    mobilities, then the patterns): (name, col_start, col_end,
    n_conf, n_inst) over the non-intercept features."""
    blocks = []
    col = 1 if (fset.intercept is not None) else 0
    for f in fset.features:
        if f.category in (0, 'intercept') or f.name == 'INTERCEPT':
            continue
        blocks.append((f.name, col, col + int(f.n_instances),
                       int(f.n_configurations), int(f.n_instances)))
        col += int(f.n_instances)
    return blocks


def _feature_set_hash(cfg) -> str:
    """The feature set hash (the cache consistency signature,
    the P5 — the first cache level WITHOUT the rds_checksum,
    the feature_set hash instead): the sha3_256 of the
    feature_set config's normalized dump (the first 16 hex)."""
    dump = cfg.feature_set.model_dump_json(indent=2)
    return hashlib.sha3_256(dump.encode()).hexdigest()[:16]


def _signature(ctx) -> dict:
    """The cache consistency signature: the feature_set hash +
    the generation spec (the seed, the total_positions, the ec,
    the generator version, the PRNG version) + the su_pairs
    list (the canonical sorted form)."""
    corpus = ctx.cfg.feature_analysis.corpus
    return {
        'feature_set_hash': _feature_set_hash(ctx.cfg),
        'seed': corpus.seed,
        'total_positions': corpus.total_positions,
        'ec': corpus.ec,
        'generator_version': _GENERATOR_VERSION,
        'prng_version': _PRNG_VERSION,
        'su_pairs': [list(p) for p in ctx.cfg.feature_analysis.su_pairs],
    }


def _compute_tables(ctx) -> dict:
    """Phase 1 — the corpus (the expensive part): the G0
    generator (the PRNG seed, the ec arrest, the wave
    semantics) + the streaming accumulation (the marginal + the
    joint for the requested pairs)."""
    cfg_fa = ctx.cfg.feature_analysis
    fset = ctx.feature_set
    blocks = _feature_blocks(fset)
    corpus = cfg_fa.corpus
    ctx.log_event(Relevance.INFO,
                  f"Generating the FEATURE_ANALYSIS corpus: "
                  f"[TOTAL: {corpus.total_positions:,}], [EC: {corpus.ec}], "
                  f"[SEED: {corpus.seed}], the G0 wave tier.")
    sink = BufferSink()
    # The wave size is capped by the corpus: a smaller corpus needs
    # fewer lanes (every game is its own lane in one wave), and the
    # lanes beyond it only pay allocation + glue.
    wave_size = min(_WAVE_SIZE, corpus.total_positions)
    info = run_wave_g0(corpus.total_positions, corpus.ec,
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
                  f"FEATURE_ANALYSIS cache consistent: {consistent}.")
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
    """The requested SU pairs (the P6): for each configured
    (name_i, name_j) pair and each (inst_i, inst_j), the SU =
    2*I / (H_i + H_j) from the joint + the two marginals. The
    same-feature DIAGONAL (inst_i == inst_j) is OMITTED (the
    SU = 1 lock, the ODP-4 close — not a measurement)."""
    su = []
    for (name_i, name_j, per_instance) in joint:
        same_feature = (name_i == name_j)
        for (ii, jj) in per_instance:
            if same_feature and ii == jj:
                continue  # The diagonal: the ODP-4 lock, omitted.
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


def _export_csv(ctx, tables, su_summary) -> Path:
    """The optional CSV: the per-sub-variable marginal tables +
    the per-pair SU instance entries."""
    cfg_fa = ctx.cfg.feature_analysis
    csv_path = Path(ctx.cfg.base_dir) / cfg_fa.dir_name / \
        "feature_analysis.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, 'w', newline='', encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(['type', 'feature', 'inst', 'n_conf', 'k_obs',
                    'h', 'h_norm', 'coverage', 'never_observed', 'su'])
        for (name, i, nc, _codes, counts) in tables['marginal']:
            d = dispersion(counts, nc)
            a = never_observed_audit(counts, nc, _RARITY_THRESHOLDS)
            w.writerow(['marginal', name, i, nc, d['k_obs'],
                        f"{d['h']:.6f}", f"{d['h_norm']:.6f}",
                        f"{d['coverage']:.6f}", a['never_observed'], ''])
        for (ni, ii, nj, jj, s) in su_summary:
            w.writerow(['su', f"{ni} x {nj}", f"{ii}x{jj}", '', '',
                        '', '', '', '', f"{s:.6f}"])
    return csv_path


def _compute_statistics(ctx, tables) -> Path:
    """Phase 2 — the statistics (cheap, recomputed on EVERY run,
    including the cache hit): the per-sub-variable dispersion +
    the never-observed audit + the requested SU pairs. The
    console (INFO) + the TXT report (dir_name under base_dir) +
    the optional CSV (the export_csv flag)."""
    cfg_fa = ctx.cfg.feature_analysis
    marginal = tables['marginal']
    joint = tables['joint']
    lookup = _marginal_lookup(marginal)
    lines = ["FEATURE_ANALYSIS REPORT", "=" * 40,
             f"Sub-variables: {len(marginal)}"]
    for (name, i, nc, _codes, counts) in marginal:
        d = dispersion(counts, nc)
        a = never_observed_audit(counts, nc, _RARITY_THRESHOLDS)
        line = (f"  {name} inst {i}: K_obs {d['k_obs']}/{nc}, "
                f"H {d['h']:.3f}, H_norm {d['h_norm']:.3f}, "
                f"coverage {d['coverage']:.3f}, "
                f"never-obs {a['never_observed']}")
        lines.append(line)
        ctx.log_event(Relevance.INFO, line)
    su_summary = _su_values(joint, lookup) if joint is not None else []
    su_summary.sort(key=lambda x: x[4], reverse=True)
    for (ni, ii, nj, jj, s) in su_summary[:20]:
        line = f"  SU {ni}[{ii}] x {nj}[{jj}] = {s:.4f}"
        lines.append(line)
        ctx.log_event(Relevance.INFO, line)
    report_path = Path(ctx.cfg.base_dir) / cfg_fa.dir_name / \
        cfg_fa.report_file_name
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    ctx.log_event(Relevance.INFO,
                  f"FEATURE_ANALYSIS report written: {report_path}.")
    if cfg_fa.export_csv:
        csv_path = _export_csv(ctx, tables, su_summary)
        ctx.log_event(Relevance.INFO,
                      f"FEATURE_ANALYSIS CSV written: {csv_path}.")
    return report_path


def _up(ctx: "LMContext") -> None:
    cfg_fa = ctx.cfg.feature_analysis
    if not cfg_fa.enable:
        ctx.log_event(Relevance.INFO,
                      "FEATURE_ANALYSIS disabled (enable: false) — no-op.")
        ctx.feature_analysis_tables = None
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
                  f"FEATURE_ANALYSIS corpus: "
                  f"{'loaded from cache' if cache_hit else 'computed'}.")
    # Phase 2 — the statistics (cheap, recomputed on EVERY run).
    _compute_statistics(ctx, tables)
    # Publish the tables on the ctx (for the EFFECT_SIZE level).
    ctx.feature_analysis_tables = tables
    ctx.log_event(Relevance.INFO,
                  "feature_analysis_tables published on the ctx.")


def _down(ctx: "LMContext") -> None:
    ctx.log_event(Relevance.INFO,
                  "Clearing the feature_analysis_tables attribute.")
    ctx.feature_analysis_tables = None


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def wrk_feature_analysis() -> Worker:
    """Factory function that returns the FEATURE_ANALYSIS worker
    instance."""
    return Worker("FEATURE_ANALYSIS", _up, _down)
