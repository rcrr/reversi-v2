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

__all__ = ['entropy', 'mutual_information', 'symmetric_uncertainty']


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
