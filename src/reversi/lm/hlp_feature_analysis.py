#
# hlp_feature_analysis.py
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
The analysis-kernels data module: the SHARED pure-math
kernels over the frequency tables (the marginal / the joint
counts from the accumulators) — the module name says the
FAMILY (the analysis of the features), because two levels use it:

  - the SU / entropy / mutual-information kernels                [the SU_ANALYSIS level]
  - the dispersion + the never-observed audit
  - the ANOVA kernels                                            [the EFFECT_SIZE level]
  - the adherence kernels                                        [the EFFECT_SIZE level]

Pure math from the frequency tables — NO DB, NO positions. The
worker (wrk_su_analysis.py) calls these kernels on
the accumulator output (the phase-2 recompute, cheap, on every
run).

The SU is computed from the IDEAL (synthetic) frequencies: a
structural property of the game geometry + the feature set,
free of the DB sample noise (the design section 3.3 phase 2).
"""

import numpy as np
from scipy.stats import chi2 as _chi2

__all__ = ['entropy', 'mutual_information', 'symmetric_uncertainty',
           'dispersion', 'never_observed_audit', 'anova_eta_omega',
           'kl_divergence', 'total_variation', 'chi_square_goodness',
           'adherence']


def entropy(counts) -> float:
    """
    The Shannon entropy H in bits, from the count array (the
    marginal or the joint). The 0-log-0 convention: the zero
    counts contribute 0. The empty / the all-zero counts -> 0.

    Args:
      counts: the count array (any shape; the non-zero entries
        are the observed support).
    """
    c = np.asarray(counts, dtype=np.float64).ravel()
    c = c[c > 0]
    n = c.sum()
    if n == 0:
        return 0.0
    p = c / n
    return float(-(p * np.log2(p)).sum())


def mutual_information(joint_counts, marg_u, marg_v) -> float:
    """
    The mutual information I(u; v) in bits, from the joint
    counts + the two marginal counts. The identity
    I = H(u) + H(v) - H(u, v) (the ratio form's 0/0 is
    avoided; the joint entropy is the entropy of the joint
    counts). Clamped to >= 0 (the floating-point rounding of
    the identity can give a tiny negative).

    Args:
      joint_counts: the (u, v) joint counts (the observed
        cells).
      marg_u:       the marginal counts of u.
      marg_v:       the marginal counts of v.
    """
    I = entropy(marg_u) + entropy(marg_v) - entropy(joint_counts)
    return float(max(0.0, I))


def symmetric_uncertainty(I: float, H_u: float,
                          H_v: float) -> float:
    """
    The symmetrical uncertainty SU(u, v) = 2·I / (H(u) +
    H(v)), in [0, 1]. The 0-denominator guard: SU = 0 if
    H(u) + H(v) == 0 (the degenerate variables — the code-0
    "no match" single-category).

    Args:
      I:    the mutual information I(u; v) (bits).
      H_u:  the entropy of u (bits).
      H_v:  the entropy of v (bits).
    """
    denom = H_u + H_v
    if denom == 0:
        return 0.0
    return float(2.0 * I / denom)


def dispersion(counts, n_configurations) -> dict:
    """
    The per-sub-variable dispersion (the design section 3.3
    phase 2): K_obs (the distinct observed codes), H (the
    entropy in bits), H_norm = H / log2(K_obs) (else 0 — the
    K_obs <= 1 guard), the coverage = K_obs /
    n_configurations (the theoretical range).

    Args:
      counts: the sub-variable's count array (the observed
        support; the dense form with the zero entries is
        accepted — the zeros are filtered).
      n_configurations: the theoretical code range of the sub-
        variable (the full range, incl. the never-observed).

    Returns:
      {'k_obs', 'h', 'h_norm', 'coverage'}.
    """
    observed = np.asarray(counts, dtype=np.float64).ravel()
    observed = observed[observed > 0]
    k_obs = int(observed.shape[0])
    H = entropy(observed)
    h_norm = (H / float(np.log2(k_obs))) if k_obs > 1 else 0.0
    n_conf = int(n_configurations)
    coverage = (k_obs / n_conf) if n_conf > 0 else 0.0
    return {'k_obs': k_obs, 'h': H, 'h_norm': h_norm,
            'coverage': coverage}


def never_observed_audit(counts, n_configurations,
                         rarity_thresholds=(1, 2, 5, 10, 100)
                         ) -> dict:
    """
    The never-observed audit: the
    number of theoretical codes never seen in the corpus
    (n_configurations - K_obs) + the rarity profile (the count
    of the OBSERVED codes below each small count threshold —
    the configurations that random play almost never reaches:
    the weights that can never be learned).

    Args:
      counts: the sub-variable's count array (the observed
        support; the dense form with the zero entries is
        accepted — the zeros are filtered).
      n_configurations: the theoretical code range of the sub-
        variable (the full range, incl. the never-observed).
      rarity_thresholds: the small count thresholds (the
        "almost never reached" profile). For a threshold t,
        the count of the observed codes with count < t.

    Returns:
      {'k_obs', 'never_observed', 'rarity'} — rarity a dict
      {threshold: count}.
    """
    observed = np.asarray(counts, dtype=np.float64).ravel()
    observed = observed[observed > 0]
    k_obs = int(observed.shape[0])
    never = int(n_configurations) - k_obs
    rarity = {int(t): int((observed < int(t)).sum())
              for t in rarity_thresholds}
    return {'k_obs': k_obs, 'never_observed': never,
            'rarity': rarity}


def anova_eta_omega(groups, values) -> dict:
    """
    The one-way ANOVA effect sizes (the EFFECT_SIZE level, the
    design section 3.5): the observed codes as the groups (K),
    the target = the continuous training game values (N).

      SS_tot = sum (y - ybar)^2
      SS_eff = sum_g n_g (y_g - ybar)^2
      SS_err = SS_tot - SS_eff
      eta²   = SS_eff / SS_tot
      omega² = (SS_eff - (K - 1) MS_err) / (SS_tot + MS_err)
      MS_err = SS_err / (N - K)

    Guards: K = 1 -> eta² = omega² = 0 (degenerate, by
    convention); K > N -> ValueError (unreachable). omega² may
    be slightly negative (the null effect): the raw value is
    reported. eta² is the biased sample share (up with high
    K); omega² is the unbiased population estimate — the pair
    is reported together.

    Args:
      groups: the group assignment per observation (the
        observed codes; length N). Any hashable values.
      values: the continuous target values (length N).

    Returns:
      {'eta2', 'omega2', 'k', 'n'}.

    Raises:
      ValueError: K > N (unreachable) or the length mismatch.
    """
    g = np.asarray(groups)
    y = np.asarray(values, dtype=np.float64).ravel()
    n = int(y.shape[0])
    if g.shape[0] != n:
        raise ValueError(
            f"groups ({g.shape[0]}) and values ({n}) "
            "length mismatch")
    unique, inv = np.unique(g, return_inverse=True)
    k = int(unique.shape[0])
    if k > n:
        raise ValueError(
            f"K > N (the {k} groups exceed the {n} "
            "observations) — unreachable")
    if k == 1:
        # The degenerate (the single group): by convention.
        return {'eta2': 0.0, 'omega2': 0.0, 'k': k, 'n': n}
    ybar = float(y.mean())
    ss_tot = float(((y - ybar) ** 2).sum())
    group_sums = np.bincount(inv, weights=y)
    group_counts = np.bincount(inv)
    group_means = group_sums / group_counts
    ss_eff = float((group_counts
                    * (group_means - ybar) ** 2).sum())
    ss_err = ss_tot - ss_eff
    eta2 = (ss_eff / ss_tot) if ss_tot > 0 else 0.0
    ms_err = (ss_err / (n - k)) if n > k else 0.0
    denom = ss_tot + ms_err
    omega2 = ((ss_eff - (k - 1) * ms_err) / denom
              if denom > 0 else 0.0)
    return {'eta2': float(eta2), 'omega2': float(omega2),
            'k': k, 'n': n}


def kl_divergence(p, q) -> float:
    """
    The KL divergence KL(p || q) in nats, the 0-log-0
    convention (the p(i) = 0 terms vanish). +inf if p(i) > 0
    and q(i) = 0 (the DB has a code the ideal never shows — the
    infinite divergence).

    Args:
      p: the DB distribution (the probabilities, sum 1).
      q: the ideal distribution (the probabilities, sum 1).
    """
    p = np.asarray(p, dtype=np.float64).ravel()
    q = np.asarray(q, dtype=np.float64).ravel()
    mask = p > 0
    if bool(np.any(mask & (q <= 0))):
        return float('inf')
    return float((p[mask] * np.log(p[mask] / q[mask])).sum())


def total_variation(p, q) -> float:
    """
    The total variation distance TV(p, q) = 0.5 * sum |p - q|,
    in [0, 1] (the robust "how different" number, no log, no
    0/0).

    Args:
      p: the DB distribution (the probabilities, sum 1).
      q: the ideal distribution (the probabilities, sum 1).
    """
    p = np.asarray(p, dtype=np.float64).ravel()
    q = np.asarray(q, dtype=np.float64).ravel()
    return float(0.5 * np.abs(p - q).sum())


def chi_square_goodness(observed, expected,
                        min_expected=5) -> dict:
    """
    The chi-square goodness-of-fit: the statistic
    sum (O - E)^2 / E, the p-value (the scipy chi2.sf, the
    (k - 1) df), the merged tail (the low-expected cells, E <
    min_expected, merged into an "other" bin) + the merge count
    (the standard technique).

    Args:
      observed: the DB observed counts (the O_i, one per cell).
      expected: the ideal expected counts (the E_i = the ideal
        frequency * N_DB, one per cell).
      min_expected: the threshold for the merged tail (the
        default 5, the standard).

    Returns:
      {'chi2', 'p', 'merged'} (the statistic, the p-value, the
      merge count). The p-value is nan if the merged result has
      fewer than 2 cells (the degenerate, df < 1).
    """
    o = np.asarray(observed, dtype=np.float64).ravel()
    e = np.asarray(expected, dtype=np.float64).ravel()
    if o.shape[0] < 2:
        return {'chi2': 0.0, 'p': float('nan'), 'merged': 0}
    # The merged tail: the cells with E < min_expected are
    # merged into the "other" bin (the sum).
    mask = e < min_expected
    n_merge = int(mask.sum())
    # The disjoint support: a cell with O > 0 but E = 0 (the DB
    # observes a code the ideal never shows — the total
    # incompatibility, the chi-square is +inf, the p is 0, the
    # KL is +inf — the three are aligned, the merged tail would
    # otherwise hide the root cause and divide by zero).
    if bool(np.any((o > 0) & (e == 0))):
        return {'chi2': float('inf'), 'p': 0.0, 'merged': n_merge}
    if n_merge > 0:
        other_o = float(o[mask].sum())
        other_e = float(e[mask].sum())
        keep = ~mask
        o = np.concatenate([o[keep], [other_o]])
        e = np.concatenate([e[keep], [other_e]])
    k = int(o.shape[0])
    chi2_stat = float(((o - e) ** 2 / e).sum())
    df = k - 1
    if df < 1:
        p_val = float('nan')
    else:
        p_val = float(_chi2.sf(chi2_stat, df))
    return {'chi2': chi2_stat, 'p': p_val, 'merged': n_merge}


def adherence(db_counts, ideal_counts) -> dict:
    """
    The adherence (c) (the EFFECT_SIZE level, the design
    section 3.5): the DB configuration distribution (the
    observed codes of the training positions) vs the ideal
    distribution (the corpus frequencies, normalized). The
    fixed trio (no config whitelist): the
    chi-square goodness-of-fit (the p-value + the merged-tail
    count), the KL divergence (the 0-log-0), the total
    variation distance (the 0..1 "how different" number,
    robust). The two are aligned over the union of the
    observed codes (the missing side is 0).

    Args:
      db_counts: the DB observed code counts, a dict
        {code: count} (the training positions).
      ideal_counts: the ideal (corpus) code counts, a dict
        {code: count} (the corpus frequencies).

    Returns:
      {'chi2', 'p', 'merged', 'kl', 'tv'}. The values are nan
      if either distribution is empty.
    """
    codes = sorted(set(db_counts) | set(ideal_counts))
    db = np.array([db_counts.get(c, 0) for c in codes],
                  dtype=np.float64)
    ideal = np.array([ideal_counts.get(c, 0) for c in codes],
                     dtype=np.float64)
    n_db = float(db.sum())
    n_ideal = float(ideal.sum())
    if n_db == 0 or n_ideal == 0:
        return {'chi2': float('nan'), 'p': float('nan'),
                'merged': 0, 'kl': float('nan'),
                'tv': float('nan')}
    p_db = db / n_db
    p_ideal = ideal / n_ideal
    tv = total_variation(p_db, p_ideal)
    kl = kl_divergence(p_db, p_ideal)
    expected = p_ideal * n_db
    g = chi_square_goodness(db, expected)
    return {'chi2': g['chi2'], 'p': g['p'], 'merged': g['merged'],
            'kl': kl, 'tv': tv}
