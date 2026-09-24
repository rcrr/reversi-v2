#
# hlp_analytics.py
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

from __future__ import annotations

import io
import math
import numpy as np

from dataclasses import dataclass

from typing import TYPE_CHECKING, Dict
from datetime import datetime

from reversi.lm.hlp_feature_analysis import adherence
from reversi.lm.hlp_gradient import sigmoid
from reversi.tools.state_machine import Relevance

if TYPE_CHECKING:
    from reversi.lm.logistic_model import LMContext



__all__ = ['TrainingDenseResult', 'compute_training_metrics', 'compute_training_dense_metrics',
           'format_console_report', 'format_file_report']


#: The SU sample consistency verdict bands (the TV thresholds):
#: TV <= _SU_TV_CONSISTENT is CONSISTENT, TV <= _SU_TV_MARGINAL is
#: MARGINAL, above is DEVIATING.
_SU_TV_CONSISTENT = 0.01
_SU_TV_MARGINAL = 0.05

#: The "too small" rule: the SU corpus (total_positions) must hold
#: at least this multiple of the training size, else the
#: PROBABILITY / SU_PROBABILITY columns are skipped and the
#: header carries the note.
_SU_CORPUS_TRAIN_RATIO = 2


def _su_sample_stats(ctx: "LMContext", feature, indexes_col_offset: int):
    """
    The SU sample statistics for one feature's table: None when the
    SU_ANALYSIS level was disabled (the ctx.su_analysis_tables None);
    a mode-'too_small' record when the corpus holds fewer than
    2x the training positions; otherwise the pooled corpus counts
    (the marginal summed over the feature's instance columns), the
    corpus observation total, and the adherence of the pooled
    training distribution vs the pooled corpus distribution (the
    chi-square goodness-of-fit + the TV / KL, the
    hlp_feature_analysis kernel).
    """
    tables = ctx.su_analysis_tables
    if tables is None:
        return None
    n_train = int(len(ctx.game_values))
    total = int(tables['signature']['total_positions'])
    if total < _SU_CORPUS_TRAIN_RATIO * n_train:
        return {'mode': 'too_small', 'corpus': total, 'train': n_train}
    pooled: Dict[int, int] = {}
    for (name, _i, _nc, codes, counts) in tables['marginal']:
        if name != feature.name:
            continue
        for code, cnt in zip(codes.tolist(), counts.tolist()):
            pooled[int(code)] = pooled.get(int(code), 0) + int(cnt)
    cols = slice(indexes_col_offset, indexes_col_offset + feature.n_instances)
    flat = ctx.hlp_indexes.indexes[:, cols].ravel()
    uniq, cnt = np.unique(flat, return_counts=True)
    db_counts = dict(zip(uniq.tolist(), cnt.tolist()))
    return {'mode': 'ok', 'pooled': pooled,
            'corpus_total': int(sum(pooled.values())),
            'adh': adherence(db_counts, pooled)}


def _su_verdict(tv: float) -> str:
    """
    The SU sample consistency verdict over the TV bands:
    CONSISTENT (TV <= 0.01), MARGINAL (TV <= 0.05), DEVIATING
    (above).
    """
    if tv <= _SU_TV_CONSISTENT:
        return 'CONSISTENT'
    if tv <= _SU_TV_MARGINAL:
        return 'MARGINAL'
    return 'DEVIATING'


def _su_header_line(stats) -> str | None:
    """
    The 'SU Sample Consistency' header line for one feature table:
    None when the SU_ANALYSIS level was disabled; the N/A (too
    small) note when the corpus is under 2x the training size;
    otherwise the TV + the chi-square (the p-value + the
    merged-tail count) + the verdict.
    """
    if stats is None:
        return None
    if stats['mode'] == 'too_small':
        return (f"  SU Sample Consistency       : N/A (SU corpus too small: "
                f"{stats['corpus']:,} < 2x training {stats['train']:,})\n")
    a = stats['adh']
    tv = a['tv']
    if math.isnan(tv):
        return "  SU Sample Consistency       : N/A (degenerate)\n"
    chi2 = a['chi2']
    chi2_str = "inf" if math.isinf(chi2) else f"{chi2:.1f}"
    p = a['p']
    p_str = "nan" if math.isnan(p) else f"{p:.2e}"
    return (f"  SU Sample Consistency       : TV {tv:.4f}  chi2 {chi2_str} "
            f"(p {p_str}, merged {a['merged']})  ->  {_su_verdict(tv)}\n")


def _format_mobility_feature_table(ctx: "LMContext", fid: int, indexes_col_offset: int, print_rows: bool = True) -> str:
    """
    Generates a detailed ASCII table for a specific mobility feature.
    When the SU_ANALYSIS level ran with a corpus of at least 2x the
    training size, the table gains the PROBABILITY / SU_PROBABILITY
    columns (after FREQUENCY) and the header gains the 'SU Sample
    Consistency' line (under the Eta-Squared line); when the level
    was disabled the table is unchanged, and an under-sized corpus
    swaps the columns for the N/A header note.
    """
    feature = ctx.feature_set.features[fid]
    n_configurations = feature.n_configurations
    n_instances = feature.n_instances
    offset = ctx.iwmap_feature_offset[fid]

    fallback_idx = int(ctx.feature_w_ranges[fid,0])
    fallback_freqs = {}
    if ctx.wmap_fallback is not None and len(ctx.wmap_fallback) > 0:
        for row in ctx.wmap_fallback:
            if int(row[0]) == fid:
                fallback_freqs[int(row[1])] = int(row[2])

    fallback_total_freq = sum(fallback_freqs.values())
    if fallback_idx != -1:
        fallback_weight = float(ctx.w[fallback_idx])
        fallback_str = f"(Fallback: w_idx={fallback_idx}, weight={fallback_weight:+.3f}, freq={fallback_total_freq:,})"
    else:
        fallback_str = "(Fallback: None)"

    f_wmap_mask = ctx.wmap[:, 0] == fid
    f_wmap = ctx.wmap[f_wmap_mask]
    true_configs_mask = f_wmap[:, 1] >= 0
    true_freqs = f_wmap[true_configs_mask, 2]
    true_config_ids = f_wmap[true_configs_mask, 1].astype(np.int64)
    w_indices = ctx.iwmap[offset + true_config_ids]
    true_weights = ctx.w[w_indices]
    if len(true_weights) > 0 and np.sum(true_freqs) > 0:
        weighted_mean = float(np.dot(true_weights, true_freqs) / np.sum(true_freqs))
    else:
        weighted_mean = 0.0

    cols = list(range(indexes_col_offset, indexes_col_offset + n_instances))
    train_indexes = ctx.hlp_indexes.indexes[:, cols]
    train_flat = train_indexes.ravel()

    y_true = ctx.game_values.astype(np.float64)
    y_repeated = np.repeat(y_true, n_instances)

    counts = np.bincount(train_flat, minlength=n_configurations)
    sum_y = np.bincount(train_flat, weights=y_repeated, minlength=n_configurations)
    sum_y2 = np.bincount(train_flat, weights=y_repeated**2, minlength=n_configurations)

    total_y_mean = np.mean(y_repeated)
    ss_total = np.sum((y_repeated - total_y_mean)**2)
    valid_mask = counts > 0
    group_means = np.zeros(n_configurations, dtype=np.float64)
    group_means[valid_mask] = sum_y[valid_mask] / counts[valid_mask]
    ss_between = np.sum(counts[valid_mask] * (group_means[valid_mask] - total_y_mean)**2)
    eta_squared = ss_between / ss_total if ss_total > 0 else 0.0

    count_c, count_ia, count_ic = 0, 0, 0
    for conf_id in range(n_configurations):
        w_dense_idx = offset + conf_id
        w_idx = ctx.iwmap[w_dense_idx]
        if conf_id in fallback_freqs:
            count_ic += 1
        elif w_idx >= 0:
            count_c += 1
        else:
            count_ia += 1

    # The SU sample statistics (None when the SU_ANALYSIS level was
    # disabled): the per-configuration corpus shares + the pooled
    # adherence of the training vs the corpus distribution.
    su_stats = _su_sample_stats(ctx, feature, indexes_col_offset)
    su_line = _su_header_line(su_stats)
    su_on = bool(su_stats is not None and su_stats['mode'] == 'ok')
    total_freq = int(true_freqs.sum()) + fallback_total_freq
    pooled = su_stats['pooled'] if su_on else {}
    corpus_total = su_stats['corpus_total'] if su_on else 0

    header = (
        f"\nMOBILITY FEATURE: {feature.name} (fid={fid}) {fallback_str}\n"
        f"  Weighted Mean (w)           : {weighted_mean:+.4f}\n"
        f"  Instances / Cols            : {n_instances} {cols}\n"
        f"  Config Counts (C/IA/IC)     : {count_c} / {count_ia} / {count_ic}\n"
        f"  Eta-Squared (Discrimination): {eta_squared:.4f}\n"
    )
    if su_line is not None:
        header += su_line
    su_cols_hdr = f" | {'PROBABILITY':>11} | {'SU_PROBABILITY':>14}" if su_on else ""
    col_header = (f"  {'W_DENSE_IDX':<12} | {'STATUS':<8} | {'W_IDX':<8} | "
                  f"{'CONF_IDX':<8} | {'FREQUENCY':>10}{su_cols_hdr} | "
                  f"{'AVERAGE_GV':>10} | {'RMSE_GV':>8} | {'WEIGHT':>10}")
    sep_w = max(135, len(col_header) + 1) if su_on else 135
    header += (
        f"{'-' * sep_w}\n"
        f"{col_header}\n"
        f"{'-' * sep_w}\n"
    )

    if not print_rows:
        return header + f"  (Table rows omitted: feature not in config 'analytics.detailed_report')\n{'-' * sep_w}\n"

    rows = []
    for conf_id in range(n_configurations):
        w_dense_idx = offset + conf_id
        w_idx = ctx.iwmap[w_dense_idx]
        conf_idx_str = str(conf_id)
        freq = 0
        avg_gv = 0.0
        rmse_gv = 0.0

        if conf_id in fallback_freqs:
            status = 'IC'
            w_idx_str = 'NA'
            freq = fallback_freqs[conf_id]
            weight = float(ctx.w_dense[w_dense_idx])
        elif w_idx >= 0:
            status = 'C'
            w_idx_str = str(int(w_idx))
            freq = int(ctx.wmap[w_idx, 2])
            weight = float(ctx.w[w_idx])
        else:
            status = 'IA'
            w_idx_str = 'NA'
            weight = float(ctx.w_dense[w_dense_idx])

        # Calculate stats for any config that has occurrences in the dataset
        if counts[conf_id] > 0:
            avg_gv = sum_y[conf_id] / counts[conf_id]
            var = (sum_y2[conf_id] / counts[conf_id]) - (avg_gv**2)
            rmse_gv = np.sqrt(max(var, 0))

        weight_str = f"{weight:+.3f}"
        avg_gv_str = f"{avg_gv:>10.2f}" if freq > 0 else f"{'N/A':>10}"
        rmse_gv_str = f"{rmse_gv:>8.2f}" if freq > 0 else f"{'N/A':>8}"
        freq_str = f"{freq:>10,}"

        if su_on:
            prob = (freq / total_freq) if total_freq > 0 else 0.0
            su_p = (pooled.get(conf_id, 0) / corpus_total) if corpus_total > 0 else 0.0
            su_cols = (f" | {f'{100.0 * prob:.3f}%':>11} | "
                       f"{f'{100.0 * su_p:.3f}%':>14}")
        else:
            su_cols = ""

        rows.append(
            f"  {w_dense_idx:<12} | {status:<8} | {w_idx_str:<8} | {conf_idx_str:<8} | {freq_str}{su_cols} | {avg_gv_str} | {rmse_gv_str} | {weight_str:>10}\n"
        )

    return header + "".join(rows) + f"{'-' * sep_w}\n"


def _format_pattern_feature_table(ctx: "LMContext", fid: int, indexes_col_offset: int, print_rows: bool = True) -> str:
    """
    Generates a detailed ASCII table for a specific pattern feature.
    When the SU_ANALYSIS level ran with a corpus of at least 2x the
    training size, the table gains the PROBABILITY / SU_PROBABILITY
    columns (after FREQUENCY) and the header gains the 'SU Sample
    Consistency' line (under the Eta-Squared line); when the level
    was disabled the table is unchanged, and an under-sized corpus
    swaps the columns for the N/A header note.
    """
    feature = ctx.feature_set.features[fid]
    n_configurations = feature.n_configurations
    n_instances = feature.n_instances
    offset = ctx.iwmap_feature_offset[fid]

    fallback_idx = int(ctx.feature_w_ranges[fid,0])
    fallback_freqs = {}
    if ctx.wmap_fallback is not None and len(ctx.wmap_fallback) > 0:
        for row in ctx.wmap_fallback:
            if int(row[0]) == fid:
                fallback_freqs[int(row[1])] = int(row[2])

    fallback_total_freq = sum(fallback_freqs.values())
    if fallback_idx != -1:
        fallback_weight = float(ctx.w[fallback_idx])
        fallback_str = f"(Fallback: w_idx={fallback_idx}, weight={fallback_weight:+.3f}, freq={fallback_total_freq:,})"
    else:
        fallback_str = "(Fallback: None)"

    f_wmap_mask = ctx.wmap[:, 0] == fid
    f_wmap = ctx.wmap[f_wmap_mask]
    true_configs_mask = f_wmap[:, 1] >= 0
    true_freqs = f_wmap[true_configs_mask, 2]
    true_config_ids = f_wmap[true_configs_mask, 1].astype(np.int64)
    w_indices = ctx.iwmap[offset + true_config_ids]
    true_weights = ctx.w[w_indices]
    if len(true_weights) > 0 and np.sum(true_freqs) > 0:
        weighted_mean = float(np.dot(true_weights, true_freqs) / np.sum(true_freqs))
    else:
        weighted_mean = 0.0

    if len(true_weights) > 0:
        max_idx = np.argmax(true_weights)
        min_idx = np.argmin(true_weights)
        max_w = true_weights[max_idx]
        min_w = true_weights[min_idx]
        max_conf = true_config_ids[max_idx]
        min_conf = true_config_ids[min_idx]
        max_str = f"Max Weight (w)              : {max_w:+.4f} (conf: {max_conf})"
        min_str = f"Min Weight (w)              : {min_w:+.4f} (conf: {min_conf})"
    else:
        max_str = f"Max Weight (w)              : N/A"
        min_str = f"Min Weight (w)              : N/A"

    all_configs = np.arange(n_configurations, dtype=np.uint32)
    principal_configs = feature.ref.convert_to_principal_index(all_configs)

    cols = list(range(indexes_col_offset, indexes_col_offset + n_instances))
    train_indexes = ctx.hlp_indexes.indexes[:, cols]
    train_flat = train_indexes.ravel()

    y_true = ctx.game_values.astype(np.float64)
    y_repeated = np.repeat(y_true, n_instances)

    counts = np.bincount(train_flat, minlength=n_configurations)
    sum_y = np.bincount(train_flat, weights=y_repeated, minlength=n_configurations)
    sum_y2 = np.bincount(train_flat, weights=y_repeated**2, minlength=n_configurations)

    total_y_mean = np.mean(y_repeated)
    ss_total = np.sum((y_repeated - total_y_mean)**2)
    valid_mask = counts > 0
    group_means = np.zeros(n_configurations, dtype=np.float64)
    group_means[valid_mask] = sum_y[valid_mask] / counts[valid_mask]
    ss_between = np.sum(counts[valid_mask] * (group_means[valid_mask] - total_y_mean)**2)
    eta_squared = ss_between / ss_total if ss_total > 0 else 0.0

    count_c, count_ab, count_cl = 0, 0, 0
    for conf_id in range(n_configurations):
        w_dense_idx = offset + conf_id
        w_idx = ctx.iwmap[w_dense_idx]
        if conf_id in fallback_freqs:
            count_cl += 1
        elif w_idx >= 0:
            count_c += 1
        else:
            count_ab += 1

    # The SU sample statistics (None when the SU_ANALYSIS level was
    # disabled): the per-configuration corpus shares + the pooled
    # adherence of the training vs the corpus distribution.
    su_stats = _su_sample_stats(ctx, feature, indexes_col_offset)
    su_line = _su_header_line(su_stats)
    su_on = bool(su_stats is not None and su_stats['mode'] == 'ok')
    total_freq = int(true_freqs.sum()) + fallback_total_freq
    pooled = su_stats['pooled'] if su_on else {}
    corpus_total = su_stats['corpus_total'] if su_on else 0

    header = (
        f"\nPATTERN FEATURE: {feature.name} (fid={fid}) {fallback_str}\n"
        f"  Weighted Mean (w)           : {weighted_mean:+.4f}\n"
        f"  {max_str}\n"
        f"  {min_str}\n"
        f"  Instances / Cols            : {n_instances} {cols}\n"
        f"  Config Counts (C/AB/CL)     : {count_c} / {count_ab} / {count_cl}\n"
        f"  Eta-Squared (Discrimination): {eta_squared:.4f}\n"
    )
    if su_line is not None:
        header += su_line
    su_cols_hdr = f" | {'PROBABILITY':>11} | {'SU_PROBABILITY':>14}" if su_on else ""
    col_header = (f"  {'W_DENSE_IDX':<12} | {'STATUS':<8} | {'W_IDX':<8} | "
                  f"{'CONF_IDX':<8} | {'PRINCIPAL_IDX':<14} | {'FREQUENCY':>10}"
                  f"{su_cols_hdr} | {'AVERAGE_GV':>10} | {'RMSE_GV':>8} | {'WEIGHT':>10}")
    sep_w = max(135, len(col_header) + 1) if su_on else 135
    header += (
        f"{'-' * sep_w}\n"
        f"{col_header}\n"
        f"{'-' * sep_w}\n"
    )

    if not print_rows:
        return header + f"  (Table rows omitted: feature not in config 'analytics.detailed_report')\n{'-' * sep_w}\n"

    rows = []
    for conf_id in range(n_configurations):
        w_dense_idx = offset + conf_id
        w_idx = ctx.iwmap[w_dense_idx]
        conf_idx_str = str(conf_id)
        principal_idx_str = str(principal_configs[conf_id])
        freq = 0
        avg_gv = 0.0
        rmse_gv = 0.0

        if conf_id in fallback_freqs:
            status = 'CL'
            w_idx_str = 'NA'
            freq = fallback_freqs[conf_id]
            weight = float(ctx.w_dense[w_dense_idx])
        elif w_idx >= 0:
            status = 'C'
            w_idx_str = str(int(w_idx))
            freq = int(ctx.wmap[w_idx, 2])
            weight = float(ctx.w[w_idx])
        else:
            status = 'AB'
            w_idx_str = 'NA'
            weight = float(ctx.w_dense[w_dense_idx])

        # Calculate stats for any config that has occurrences in the dataset
        if counts[conf_id] > 0:
            avg_gv = sum_y[conf_id] / counts[conf_id]
            var = (sum_y2[conf_id] / counts[conf_id]) - (avg_gv**2)
            rmse_gv = np.sqrt(max(var, 0))

        weight_str = f"{weight:+.3f}"
        avg_gv_str = f"{avg_gv:>10.2f}" if freq > 0 else f"{'N/A':>10}"
        rmse_gv_str = f"{rmse_gv:>8.2f}" if freq > 0 else f"{'N/A':>8}"
        freq_str = f"{freq:>10,}"

        if su_on:
            prob = (freq / total_freq) if total_freq > 0 else 0.0
            su_p = (pooled.get(conf_id, 0) / corpus_total) if corpus_total > 0 else 0.0
            su_cols = (f" | {f'{100.0 * prob:.3f}%':>11} | "
                       f"{f'{100.0 * su_p:.3f}%':>14}")
        else:
            su_cols = ""

        rows.append(
            f"  {w_dense_idx:<12} | {status:<8} | {w_idx_str:<8} | {conf_idx_str:<8} | {principal_idx_str:<14} | {freq_str}{su_cols} | {avg_gv_str} | {rmse_gv_str} | {weight_str:>10}\n"
        )

    return header + "".join(rows) + f"{'-' * sep_w}\n"


def _format_header(ctx: "LMContext", detailed: bool = False) -> str:
    """
    Formats the common header metrics table for both console and file reports.

    The table is three-metric wide (D-105/M2): TRAINING is the COMPRESSED
    forward pass (the trained w over the design matrix — what lbfgs fit);
    TRAINING-DENSE is the DENSE forward pass (w_dense — the exact forward
    rules of the saved model, as client computes them) on the same
    training data; VALIDATION is the dense pass on the validation data.
    The two training columns differ exactly for the positions that touch
    below-cutoff (IC) configurations — the Substitution Delta row
    quantifies that; the Generalization Gap row is dense-vs-dense (a
    pure generalization measure).
    """
    model_name = ctx.cfg.name
    total_params = len(ctx.w)
    dense_params = len(ctx.w_dense) if ctx.w_dense is not None else 0

    opt_info = ctx.opt_info or {}
    opt_status = opt_info.get('reason', 'N/A')
    opt_iters = opt_info.get('iters', 0)

    # Read metrics from context
    train_metrics = ctx.train_metrics or {}
    train_dense_metrics = ctx.train_dense_metrics or {}
    vld_metrics = ctx.vld_metrics

    train_rmse = train_metrics.get('train_rmse_y', 0.0)
    train_mae = train_metrics.get('train_mae_y', 0.0)
    train_loss = train_metrics.get('train_loss', 0.0)
    train_samples = train_metrics.get('train_samples', 0)

    train_dense_rmse = train_dense_metrics.get('train_dense_rmse_y', 0.0)
    train_dense_mae = train_dense_metrics.get('train_dense_mae_y', 0.0)
    train_dense_loss = train_dense_metrics.get('train_dense_loss', 0.0)
    if train_dense_metrics:
        train_dense_rmse_str = f"{train_dense_rmse:.2f}"
        train_dense_mae_str = f"{train_dense_mae:.2f}"
        train_dense_loss_str = f"{train_dense_loss:.4e}"
    else:
        train_dense_rmse_str = train_dense_mae_str = train_dense_loss_str = "N/A"

    if vld_metrics:
        vld_rmse_str = f"{vld_metrics.get('vld_rmse_y', 0.0):.2f}"
        vld_mae_str = f"{vld_metrics.get('vld_mae_y', 0.0):.2f}"
        vld_loss_str = f"{vld_metrics.get('vld_loss', 0.0):.4e}"
        vld_samples = vld_metrics.get('vld_samples', 0)
        # The gap is DENSE vs DENSE (the shipped inference rules on both
        # sets): a pure generalization measure. The compressed-vs-dense
        # substitution effect is the separate Substitution Delta below.
        gen_gap = vld_metrics.get('vld_rmse_y', 0.0) - train_dense_rmse
        substitution_delta = train_dense_rmse - train_rmse
    else:
        vld_rmse_str = vld_mae_str = vld_loss_str = "N/A"
        vld_samples = 0
        gen_gap = 0.0
        substitution_delta = 0.0

    pop_rmse_str = f"{train_metrics.get('pop_rmse_y', 0.0):.2f}"
    pop_mae_str = f"{train_metrics.get('pop_mae_y', 0.0):.2f}"
    pop_loss_str = f"{train_metrics.get('pop_loss', 0.0):.4e}"

    header = f"\n{'=' * 135}\nMODEL ANALYTICS REPORT: {model_name}\n{'=' * 135}\n"

    if detailed:
        creation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        stat_model_cfg = ctx.cfg.stat_model

        header += f"  Creation Date               : {creation_date}\n"
        header += f"  Training/Validation Records : {train_samples:,} / {vld_samples:,}\n"
        header += f"  Frequency Cut-Off           : {stat_model_cfg.frequency_cut_off}\n"
        header += f"  Logit Clipping              : {stat_model_cfg.logit_clipping}\n"
        header += f"  Ridge Regularization        : {stat_model_cfg.ridge_regularization}\n"

    header += (
        f"  Total Parameters (W)        : {total_params:,}\n"
        f"  Dense Parameters (K)        : {dense_params:,}\n"
        f"  Optimization Status         : {opt_status} ({opt_iters} iters)\n"
        f"  Config SHA3-256             : {ctx.config_checksum}\n"
        f"{'-' * 135}\n"
        f"  {'METRIC':<15} | {'TRAINING':<14} | {'TRAINING-DENSE':<14} | {'VALIDATION':<14}\n"
        f"{'-' * 135}\n"
        f"  {'RMSE (y)':<15} | {train_rmse:<14.2f} | {train_dense_rmse_str:<14} | {vld_rmse_str:<14}\n"
        f"  {'MAE (y)':<15} | {train_mae:<14.2f} | {train_dense_mae_str:<14} | {vld_mae_str:<14}\n"
        f"  {'Loss (MSE/2)':<15} | {train_loss:<14.4e} | {train_dense_loss_str:<14} | {vld_loss_str:<14}\n"
        f"  Population (baseline)  : RMSE {pop_rmse_str}  MAE {pop_mae_str}  Loss {pop_loss_str}\n"
        f"{'-' * 135}\n"
        f"  Generalization Gap (RMSE)   : {gen_gap:.2f}\n"
        f"  Substitution Delta (RMSE)   : {substitution_delta:.2f}\n"
        f"{'=' * 135}\n"
    )
    return header


def format_console_report(ctx: "LMContext") -> str:
    """
    Formats the short summary report for console output.
    """
    return _format_header(ctx, detailed=False)


def _format_intercept_section(ctx: "LMContext") -> str:
    """
    Formats the INTERCEPT section: the single trained bias weight,
    emitted only when the feature set has an intercept
    (fset.intercept is not None) and placed before the MOBILITY
    details. One Weight line (4 decimals, the report's weight
    convention); the intercept is category 0, skipped by the
    mobility / pattern table loops, so without this section its
    value would appear nowhere in the report.
    """
    intercept = ctx.feature_set.intercept
    if intercept is None:
        return ""
    fid = ctx.feature_set.features.index(intercept)
    w_idx = int(ctx.iwmap[int(ctx.iwmap_feature_offset[fid])])
    weight_str = "N/A" if w_idx < 0 else f"{float(ctx.w[w_idx]):+.4f}"
    return (
        "INTERCEPT:\n"
        f"{'-' * 135}\n"
        f"  {'Weight (w)':<28}: {weight_str}\n"
        f"{'-' * 135}\n\n"
    )


def format_file_report(ctx: "LMContext") -> str:
    """
    Formats the complete detailed report for TXT file output.
    """
    report = _format_header(ctx, detailed=True)

    buffer = io.StringIO()
    ctx.feature_set.print_summary(output=buffer)
    feature_summary = buffer.getvalue()
    report += f"\nFEATURE SET SUMMARY:\n{'-' * 135}\n{feature_summary}\n"

    # The INTERCEPT section (the trained bias weight) — only when the
    # feature set has an intercept; it precedes the MOBILITY details.
    report += _format_intercept_section(ctx)

    # ctx.cfg.analytics always exists (the schema's default factory)
    detailed_report_list = ctx.cfg.analytics.detailed_report

    report += f"MOBILITY FEATURES DETAILS:\n{'-' * 135}\n"
    col_offset = 0
    for fid, feature in enumerate(ctx.feature_set.features):
        if feature.category == 1:  # Mobility
            print_rows = feature.name in detailed_report_list
            report += _format_mobility_feature_table(ctx, fid, col_offset, print_rows=print_rows)
        col_offset += feature.n_instances

    report += f"\nPATTERN FEATURES DETAILS:\n{'-' * 135}\n"
    col_offset = 0
    for fid, feature in enumerate(ctx.feature_set.features):
        if feature.category == 2:  # Pattern
            print_rows = feature.name in detailed_report_list
            report += _format_pattern_feature_table(ctx, fid, col_offset, print_rows=print_rows)
        col_offset += feature.n_instances

    return report


def compute_training_metrics(ctx: "LMContext") -> Dict[str, float | int]:
    """
    Computes MAE(y) and RMSE(y) on the training set using the optimized weights (w).
    Also computes baseline (population mean) metrics for comparison.
    """
    ctx.log_event(Relevance.INFO, "Computing metrics on the training set...")

    # --- Model Metrics ---
    linear_predictor = np.sum(ctx.w[ctx.design_matrix].astype(np.float64), axis=1)
    z_pred = sigmoid(linear_predictor)

    y_pred = ctx.z2y(z_pred)
    y_true = ctx.game_values.astype(np.float64)

    rn_y = y_pred - y_true
    mae_y = np.mean(np.abs(rn_y))
    rmse_y = np.sqrt(np.dot(rn_y, rn_y) / len(rn_y))

    # --- Population (Baseline) Metrics ---
    y_mean = np.mean(y_true)
    rn_y_pop = y_true - y_mean
    pop_mae_y = np.mean(np.abs(rn_y_pop))
    pop_rmse_y = np.sqrt(np.dot(rn_y_pop, rn_y_pop) / len(rn_y_pop))

    z_true = ctx.y2z(ctx.game_values)
    z_mean = np.mean(z_true)
    rn_z_pop = z_true - z_mean
    pop_loss = 0.5 * (np.dot(rn_z_pop, rn_z_pop) / len(rn_z_pop))

    return {
        'train_mae_y': float(mae_y),
        'train_rmse_y': float(rmse_y),
        'train_loss': float(ctx.opt_info['f']) if ctx.opt_info else 0.0,
        'train_samples': int(len(y_true)),
        'pop_mae_y': float(pop_mae_y),
        'pop_rmse_y': float(pop_rmse_y),
        'pop_loss': float(pop_loss)
    }


@dataclass
class TrainingDenseResult:
    """
    The dense training forward pass: the metrics plus the per-position
    residuals it is computed from.

    metrics: the 4-key dict (the analytics report contract, unchanged).
    rn_y: the residuals in Y (the f64 view) — the series PLOT renders
        (one derivation, published by ANALYTICS).
    """
    metrics: Dict[str, float | int]
    rn_y: np.ndarray


def compute_training_dense_metrics(ctx: "LMContext") -> TrainingDenseResult:
    """
    Computes MAE(y), RMSE(y) and the Z-space loss on the training set using
    the DENSE weights (w_dense) — the exact forward pass of the saved model
    (the client inference rules). The TRAINING table column shows the
    compressed pass (what lbfgs fit); this column shows what the shipped
    model actually computes on the training data. The two differ exactly
    for the positions that touch below-cutoff (IC) configurations, where
    the dense slots hold the substitution values instead of the trained
    fallback weights (D-105/M2).
    """
    ctx.log_event(Relevance.INFO, "Computing dense-pass metrics on the training set...")

    # The per-instance w_dense start offsets (the hlp_wmaps boundary
    # array, the same expanded-offsets construction as hlp_validate)
    n_instances_per_feature = [f.n_instances for f in ctx.feature_set.features]
    col_offsets = np.repeat(ctx.iwmap_feature_offset[:-1], n_instances_per_feature)

    dense_indices = ctx.hlp_indexes.indexes + col_offsets
    linear_predictor = np.sum(ctx.w_dense[dense_indices], axis=1)
    z_pred = sigmoid(linear_predictor)

    y_pred = ctx.z2y(z_pred)
    y_true = ctx.game_values.astype(np.float64)
    # the f32 prediction minus the f64 game value promotes to f64: this
    # IS the rounded-lossless series (bit-identical to what PLOT used
    # to compute), and the metrics below run on it.
    rn_y = y_pred - y_true
    mae_y = np.mean(np.abs(rn_y))
    rmse_y = np.sqrt(np.dot(rn_y, rn_y) / len(rn_y))

    z_true = ctx.y2z(ctx.game_values)
    rn_z = z_pred - z_true
    loss = 0.5 * (np.dot(rn_z, rn_z) / len(rn_z))

    return TrainingDenseResult(
        metrics={
            'train_dense_mae_y': float(mae_y),
            'train_dense_rmse_y': float(rmse_y),
            'train_dense_loss': float(loss),
            'train_dense_samples': int(len(y_true))
        },
        rn_y=rn_y)


