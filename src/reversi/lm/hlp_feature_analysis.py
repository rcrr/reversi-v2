"""
The FEATURE_ANALYSIS data module (the I-017, the step 3 data
plane). The kernels over the frequency tables (the marginal /
the joint counts from the accumulators, the I-017 T7-T8):

  - the SU / entropy / mutual-information kernels (T11, D-181)
  - the dispersion + the never-observed audit (T12)
  - the ANOVA kernels (T13)
  - the adherence kernels (T14)

Pure math from the frequency tables — NO DB, NO positions. The
worker (wrk_feature_analysis.py, T16) calls these kernels on
the accumulator output (the phase-2 recompute, cheap, on every
run).

The SU is computed from the IDEAL (synthetic) frequencies: a
structural property of the game geometry + the feature set,
free of the DB sample noise (the design section 3.3 phase 2).
"""

import numpy as np

__all__ = ['entropy', 'mutual_information', 'symmetric_uncertainty',
           'dispersion', 'never_observed_audit']


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
    "no match" single-category, the ODP-4/ODP-8 close).

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
    The never-observed audit (the STOP deliverable, P2): the
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
