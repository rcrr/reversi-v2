#!/usr/bin/env python3
#
# verify_anova.py
#
# Probe pinning the ANOVA level (step 6): the
# worker (src/reversi/lm/wrk_anova.py) + the ANOVA family it
# consumes (the two kernels + the compute / report methods, in the
# hlp_anova module) + its cross-level input (ctx.su_analysis_tables,
# published by the SU_ANALYSIS level, read by hlp_anova).
#
# Tiers:
#   A  the module structure: the factory, the no-cache discipline, the
#      two kernel imports, the graceful-degradation branch
#   B  the independent math (no worker): the ANOVA vs the F-identity +
#      scipy's f_oneway + the eta2 >= omega2 invariant, the adherence
#      trio vs pure-python formulas + the Pinsker bound, the disjoint
#      support alignment
#   C  the worker on the rlm_00 fixture (the mock ctx): the CSV (never
#      tested), the degradation REPORT line, the top-N report rows
#   D  the live A2050 run (no DB: the cached POSITIONS + INDEXES of the
#      build area): the 47 sub-variables, the ANOVA + the adherence
#      recomputed from the caches, no cache file, the invariant on the
#      real data. SKIPPED when the build area is absent (it is
#      gitignored and regenerable)
#   F  the cross-file facts: the runner, the mirrors, the opt-in, the
#      report format
#
# The a/b/c rule (probe_rules §3): the factory name, the enable no-op,
# the ANOVA line count, the degradation log, the adherence-computed log,
# the report existence and the down no-op all live in
# test_wrk_anova.py — they are NOT repeated here. What stays: the
# independent formulas (the F identity, the ratio-free trio in pure
# python, the Pinsker bound), the CSV, the report's own numbers and the
# real-data tier.
#
# House convention: writes only under build/tmp, self-cleans via
# atexit; exit code 1 on any mismatch.
#

import atexit
import contextlib
import io
import math
import os
import re
import shutil
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / "src"))

TMP = ROOT / "build" / "tmp" / "verify_anova"
TMP.mkdir(parents=True, exist_ok=True)
atexit.register(lambda: shutil.rmtree(TMP, ignore_errors=True))

CFG = ROOT / "test" / "reversi" / "data" / "rlm_00.json"
BUILD = ROOT / "build" / "su_corpus_1e7"

fails = 0


def check(label, cond, detail=""):
    global fails
    if not cond:
        fails += 1
    print(f"[{'ok  ' if cond else 'FAIL'}] {label}"
          + (f" -- {detail}" if detail and not cond else ""), file=sys.stderr)


def ws_lines(path):
    body = Path(path).read_text().splitlines()[26:]
    return [i for i, line in enumerate(body, 27)
            if re.match(r'^[ \t]+$', line) or re.search(r'[ \t]$', line)]


def close(a, b, tol):
    """The printed-value comparison: the two infinities count as equal
    (the disjoint-support rows), everything else within tol."""
    if a == b:
        return True
    if math.isinf(a) or math.isinf(b):
        return False
    return abs(a - b) < tol


# The probe's own ANOVA: eta² from the F identity
# (eta² = (K-1)F / ((K-1)F + (N-K))) and omega² from the sums arranged
# as (SS_eff - (K-1)MS_err) / (SS_tot + MS_err), with SS_eff computed
# from the group means (the probe's own loop, not the kernel's).
def py_anova(groups, values):
    g = np.asarray(groups)
    y = np.asarray(values, dtype=np.float64).ravel()
    n = int(y.shape[0])
    uniq, inv = np.unique(g, return_inverse=True)
    k = int(uniq.shape[0])
    ybar = float(y.mean())
    ss_tot = float(((y - ybar) ** 2).sum())
    counts = np.bincount(inv)
    means = np.bincount(inv, weights=y) / counts
    ss_eff = float(sum(c * (m - ybar) ** 2 for c, m in zip(counts, means)))
    ss_err = ss_tot - ss_eff
    ms_err = ss_err / (n - k) if n > k else 0.0
    ms_eff = ss_eff / (k - 1) if k > 1 else 0.0
    f_stat = (ms_eff / ms_err) if ms_err > 0 else float("inf")
    eta2 = (((k - 1) * f_stat) / ((k - 1) * f_stat + (n - k))
            if k > 1 and n > k and math.isfinite(f_stat) else
            (ss_eff / ss_tot if ss_tot > 0 else 0.0))
    denom = ss_tot + ms_err
    omega2 = ((ss_eff - (k - 1) * ms_err) / denom) if denom > 0 else 0.0
    return {"eta2": eta2, "omega2": omega2, "k": k, "n": n,
            "ss_tot": ss_tot, "ss_eff": ss_eff}


# The probe's own adherence trio: the expected counts are the ideal
# probabilities scaled to the DB total (p_ideal * n_db), the merge rule
# reimplemented, the KL and the TV in pure python (math.log, nats), the
# p-value from scipy on the merged (k-1) df.
def py_adherence(db_counts, ideal_counts, min_expected=5.0):
    codes = sorted(set(db_counts) | set(ideal_counts))
    o = [float(db_counts.get(c, 0)) for c in codes]
    ideal = [float(ideal_counts.get(c, 0)) for c in codes]
    n_db, n_ideal = sum(o), sum(ideal)
    if n_db == 0 or n_ideal == 0:
        return None
    p = [x / n_db for x in o]
    q = [x / n_ideal for x in ideal]
    e = [x * n_db for x in q]                     # the expected counts
    tv = 0.5 * sum(abs(a - b) for a, b in zip(p, q))
    kl = 0.0
    inf = False
    for a, b in zip(p, q):
        if a > 0 and b <= 0:
            inf = True
        elif a > 0:
            kl += a * math.log(a / b)
    merged = sum(1 for x in e if x < min_expected)
    chi2 = 0.0
    df = 0
    if not inf:
        if len(o) < 2:
            return {"chi2": 0.0, "kl": kl, "tv": tv, "merged": 0, "df": 0,
                    "p": float("nan")}
        keep = [i for i in range(len(e)) if e[i] >= min_expected]
        oo = [o[i] for i in keep]
        ee = [e[i] for i in keep]
        if merged:
            oo.append(sum(o[i] for i in range(len(e)) if e[i] < min_expected))
            ee.append(sum(e[i] for i in range(len(e)) if e[i] < min_expected))
        chi2 = sum((a - b) ** 2 / b for a, b in zip(oo, ee) if b > 0)
        df = len(oo) - 1
    return {"chi2": chi2, "kl": (float("inf") if inf else kl), "tv": tv,
            "merged": merged, "df": df,
            "p": (float(stats.chi2.sf(chi2, df)) if df >= 1
                  else float("nan"))}


# ---------------------------------------------------------------- A tier
W = ROOT / "src" / "reversi" / "lm" / "wrk_anova.py"
wt = W.read_text()
HA = ROOT / "src" / "reversi" / "lm" / "hlp_anova.py"
hat = HA.read_text()
check("A1  the factory: @validate_call + wrk_anova() -> Worker",
      "@validate_call(config=ConfigDict(arbitrary_types_allowed=True))" in wt
      and "def wrk_anova() -> Worker:" in wt)
check("A2  the Worker name is ANOVA",
      'return Worker("ANOVA", _up, _down)' in wt)
check("A3  the no-cache discipline (a diagnostic): no cache_manager import, "
      "no store/load of its own",
      "cache_manager" not in wt and "binio" not in wt)
check("A4  the two analysis methods come from hlp_anova",
      "from reversi.lm.hlp_anova import" in wt
      and "hlp_anova_compute_analysis" in wt
      and "hlp_anova_generate_report" in wt)
check("A5  the graceful-degradation branch: the adherence skipped when "
      "ctx.su_analysis_tables is None (the ANOVA still runs)",
      "tables = ctx.su_analysis_tables" in hat
      and "Adherence SKIPPED" in hat and "tables is not None" in hat)
check("A6  the down is a no-op (nothing published on the ctx)",
      "ANOVA down (no-op)" in wt)
check("A7  __all__ = ['wrk_anova']", "__all__ = ['wrk_anova']" in wt)
check("A8  no trailing whitespace outside the license header", not ws_lines(W),
      str(ws_lines(W)))

from reversi.lm.hlp_anova import (  # noqa: E402
    hlp_anova_adherence, hlp_anova_eta_omega)
from reversi.lm.logistic_model import LogisticModel  # noqa: E402
from reversi.tools.state_machine import Verbosity  # noqa: E402


def _campaign(cfg_path):
    """The real-pipeline campaign (the hlp_gate replacement):
    the facade runs CREATED -> CONFIG -> FEATURES on
    cfg_path (the target_level stop, the probe tmp base_dir) —
    the cfg + the feature_set come from the real context."""
    rlm = LogisticModel(str(cfg_path), verbosity=Verbosity.NONE,
                        base_dir_override=TMP)
    rlm.run("FEATURES")
    ctx = rlm.context
    return ctx.cfg, ctx.feature_set, ctx.feature_set.feature_blocks

# ---------------------------------------------------------------- B tier
# The ANOVA: a deterministic pseudo-random 3-group case (no test carries
# this data set), the kernel vs the F-identity route + scipy's f_oneway.
rng = np.random.default_rng(20260919)
groups = np.repeat(np.array([0, 1, 2]), 40)
values = rng.normal(loc=np.array([0.0, 0.5, 1.5])[groups], scale=1.0)
res = hlp_anova_eta_omega(groups, values)
ref = py_anova(groups, values)
check("B1  the ANOVA eta2 == the F-identity route (1e-12)",
      abs(res["eta2"] - ref["eta2"]) < 1e-12,
      f"{res['eta2']} vs {ref['eta2']}")
check("B2  the ANOVA omega2 == the independent sum arrangement (1e-12)",
      abs(res["omega2"] - ref["omega2"]) < 1e-12,
      f"{res['omega2']} vs {ref['omega2']}")
f_sp, _p_sp = stats.f_oneway(*[values[groups == g] for g in (0, 1, 2)])
eta2_sp = ((2 * f_sp) / (2 * f_sp + (values.shape[0] - 3)))
check("B3  scipy's f_oneway agrees on eta2 (1e-12) — a fully independent "
      "one-way ANOVA implementation",
      abs(res["eta2"] - eta2_sp) < 1e-12, f"{res['eta2']} vs {eta2_sp}")
check("B4  the reported K / N are the distinct groups / the observations",
      res["k"] == len(set(groups.tolist())) and res["n"] == values.shape[0])

# The invariant: eta2 >= omega2 whenever SS_err > 0 (the bias relation),
# and omega2 may go negative on a null effect.
null_groups = np.repeat(np.array([0, 1]), 50)
null_values = rng.normal(size=100)          # the same distribution, no effect
null_res = hlp_anova_eta_omega(null_groups, null_values)
check("B5  eta2 >= omega2 on a real-effect case (the bias relation) and "
      "omega2 < 0 on the null case (the raw value, no clamp)",
      res["eta2"] >= res["omega2"] and null_res["omega2"] < 0.0,
      f"{res['eta2']} / {res['omega2']} / null {null_res['omega2']}")

# The adherence trio: a deterministic synthetic pair (the SAME support on
# both sides, a different shape), the kernel vs the pure-python formulas.
db = {0: 120, 1: 95, 2: 40, 3: 12, 4: 3, 9: 7}
ideal = {0: 900, 1: 700, 2: 400, 3: 100, 4: 20, 9: 5}
a = hlp_anova_adherence(db, ideal)
b = py_adherence(db, ideal)
check("B6  the chi-square statistic == the independently merged pure-python "
      "one (1e-9)", abs(a["chi2"] - b["chi2"]) < 1e-9,
      f"{a['chi2']} vs {b['chi2']}")
check("B7  the merged-tail count agrees (the E < 5 cells, E = p_ideal * "
      "n_db)", a["merged"] == b["merged"], f"{a['merged']} vs {b['merged']}")
check("B8  the KL == the pure-python sum in nats (1e-12) and the TV == the "
      "pure-python 0.5*sum|p-q| (1e-12)",
      abs(a["kl"] - b["kl"]) < 1e-12 and abs(a["tv"] - b["tv"]) < 1e-12,
      f"KL {a['kl']} vs {b['kl']} / TV {a['tv']} vs {b['tv']}")
check("B9  the Pinsker bound TV <= sqrt(KL/2) holds on the synthetic pair "
      "(an independent mathematical invariant)",
      a["tv"] <= math.sqrt(a["kl"] / 2.0) + 1e-15,
      f"TV {a['tv']} vs {math.sqrt(a['kl'] / 2.0)}")
check("B10 the p-value == scipy's chi2.sf on the independently merged (k-1) "
      "df (1e-15)",
      b["df"] is not None and abs(a["p"] - b["p"]) < 1e-15,
      f"p {a['p']} vs {b['p']} (df {b['df']})")

# The disjoint support: the DB shows a code the ideal never has — the
# three measures stay ALIGNED (chi2 +inf, p 0, KL +inf, TV finite).
a_dis = hlp_anova_adherence({0: 10, 1: 5, 7: 3}, {0: 100, 1: 50, 2: 25})
b_dis = py_adherence({0: 10, 1: 5, 7: 3}, {0: 100, 1: 50, 2: 25})
check("B11 the disjoint support: chi2 = +inf, p = 0, KL = +inf and a finite "
      "TV — the alignment documented in the mirror",
      a_dis["chi2"] == float("inf") and a_dis["p"] == 0.0
      and a_dis["kl"] == float("inf")
      and math.isfinite(a_dis["tv"])
      and abs(a_dis["tv"] - b_dis["tv"]) < 1e-12,
      str(a_dis))

# ---------------------------------------------------------------- C tier
# The worker on the rlm_00 fixture (the mock ctx): the CSV path (which no
# test covers), the degradation REPORT line and the top-N report rows.
from reversi.lm.wrk_anova import _down, _up  # noqa: E402


class _MockIndexes:
    def __init__(self, indexes):
        self.indexes = indexes


class _MockCtx:
    def __init__(self, cfg, fset, indexes, game_values, tables):
        self.cfg = cfg
        self.feature_set = fset
        self.hlp_indexes = _MockIndexes(indexes)
        self.game_values = game_values
        self.su_analysis_tables = tables
        self.events = []

    def log_event(self, relevance, msg):
        self.events.append((relevance, msg))


cfg, fset, blocks = _campaign(CFG)
cfg.base_dir = TMP / "c_mock"
cfg.anova.enable = True
cfg.anova.export_csv = True
max_col = max(b[2] for b in blocks)
n_pos = 500
idx = np.zeros((n_pos, max_col), dtype=np.uint32)
for (name, c0, c1, n_conf, n_inst) in blocks:
    for i in range(n_inst):
        idx[:, c0 + i] = rng.integers(0, n_conf, size=n_pos)
gv = rng.standard_normal(n_pos)

# (C1) the degradation: the report line (the test pins the LOG only).
ctx = _MockCtx(cfg, fset, idx, gv, None)
_up(ctx)
rep = cfg.base_dir / "anova" / "anova_report.txt"
txt = rep.read_text()
check("C1  the degradation REPORT line (the test pins the log, the report "
      "was never checked)",
      "Adherence: SKIPPED (the SU_ANALYSIS level was disabled" in txt)
check("C2  the report header + the ANOVA section count == the rlm_00 "
      "sub-variables (15)",
      txt.startswith("ANOVA REPORT\n")
      and "Sub-variables (the eta-squared / omega-squared): 15" in txt
      and len(re.findall(r"^  ANOVA ", txt, re.M)) == 15,
      str(txt.splitlines()[:3]))
check("C3  the report's ANOVA numbers == the independent recompute "
      "(5e-5 on the printed 4 decimals)",
      all(any(f"ANOVA {name} inst {i}: eta2 {py_anova(idx[:, c0 + i], gv)['eta2']:.4f}, "
              f"omega2 {py_anova(idx[:, c0 + i], gv)['omega2']:.4f}" in line
              for line in txt.splitlines())
          for (name, c0, c1, n_conf, n_inst) in blocks
          for i in range(n_inst)))
# (C4) the CSV: the header + one row per ANOVA sub-variable + the
# adherence rows (the flag path has NO test).
csv_path = cfg.base_dir / "anova" / "anova.csv"
rows = csv_path.read_text().splitlines()
check("C4  the CSV: the documented header, 15 anova rows, and no adherence "
      "rows while the corpus is absent",
      rows[0] == "type,feature,inst,eta2,omega2,k,tv,kl,chi2,p,merged"
      and sum(1 for r in rows if r.startswith("anova,")) == 15
      and not any(r.startswith("adherence,") for r in rows))
check("C5  the CSV anova rows carry the report's eta2/omega2 (6 decimals)",
      all(any(f"anova,{name},{i},{py_anova(idx[:, c0 + i], gv)['eta2']:.6f},"
              f"{py_anova(idx[:, c0 + i], gv)['omega2']:.6f}" in r
              for r in rows)
          for (name, c0, c1, n_conf, n_inst) in blocks
          for i in range(n_inst)))

# (C6) the top-N report rows: with a corpus present, the report carries
# min(top_k_adherence, n_sub_variables) adherence rows — the test checks
# the log only. The probe's ideal is a deterministic linear-decay
# distribution over the FULL code range (a support that covers the DB's,
# so the trio stays finite and the TV differs per sub-variable).
tables = {"marginal": [], "joint": None}
for (name, c0, c1, n_conf, n_inst) in blocks:
    for i in range(n_inst):
        codes = np.arange(n_conf, dtype=np.uint32)
        counts = (n_conf - codes).astype(np.int64)
        tables["marginal"].append((name, i, n_conf, codes, counts))
cfg2, fset2, blocks2 = _campaign(CFG)
cfg2.base_dir = TMP / "c_mock2"
cfg2.anova.enable = True
ctx2 = _MockCtx(cfg2, fset2, idx, gv, tables)
_up(ctx2)
txt2 = (cfg2.base_dir / "anova" / "anova_report.txt").read_text()
ADH_RX = (r"^  Adherence (\w+) inst (\d+): TV ([\d.]+), KL ([\d.]+|inf), "
          r"chi2 ([\d.]+|inf) \(p ([\d.e+-]+|nan), merged (\d+)\)$")
adh = re.findall(ADH_RX, txt2, re.M)
check("C6  the adherence section: min(top_k_adherence, 15) rows (the rlm_00 "
      "has 15 sub-variables), the printed TV non-increasing",
      len(adh) == 15
      and all(float(adh[i][2]) >= float(adh[i + 1][2])
              for i in range(len(adh) - 1)),
      f"{len(adh)} rows")
mine = {}
for (name, c0, c1, n_conf, n_inst) in blocks:
    for i in range(n_inst):
        codes, counts = np.unique(idx[:, c0 + i], return_counts=True)
        db_counts = dict(zip(codes.tolist(), counts.tolist()))
        ideal_counts = {c: n_conf - c for c in range(n_conf)}
        mine[(name, i)] = py_adherence(db_counts, ideal_counts)
check("C7  the report's adherence rows == the independently recomputed ones "
      "(the same 15 keys, the TV / KL / chi2 / merged matching to the "
      "printed decimals)",
      {(n, int(i)) for (n, i, *_r) in adh} == set(mine)
      and all(close(float(tv), mine[(n, int(i))]["tv"], 5e-5)
              and close(float(kl), mine[(n, int(i))]["kl"], 5e-5)
              and close(float(ch), mine[(n, int(i))]["chi2"], 5e-3)
              and int(mg) == mine[(n, int(i))]["merged"]
              for (n, i, tv, kl, ch, _p, mg) in adh),
      f"{adh[0]} vs {mine[('EDGE', 0)]}")

# ---------------------------------------------------------------- D tier
# The live A2050 run without a DB: the build area's cached corpus +
# POSITIONS + INDEXES are symlinked under build/tmp and the config is run
# to ANOVA. Skipped when the area is absent (gitignored data).
D = TMP / "d_live"
caches = ["rlmwf_03_SU_ANALYSIS.dat", "rlmwf_04_POSITIONS.dat",
          "rlmwf_05_INDEXES.dat"]
have_build = (BUILD / "rlm_su_1e7.json").exists() and all(
    (BUILD / c).exists() for c in caches)
check("D0  the build area (the D-254 A2050 1e7 run) is present — tier D "
      "runs; absent, the tier is skipped (a gitignored, regenerable area)",
      True, "" if have_build else "absent: tier D skipped")
if have_build:
    D.mkdir(parents=True, exist_ok=True)
    for c in caches:
        for name in (c, c + ".SHA3-256"):
            link = D / name
            if not link.exists():
                link.symlink_to(BUILD / name)

    from reversi.lm.hlp_indexes import hlp_indexes_load_from_file  # noqa: E402
    from reversi.lm.logistic_model import LogisticModel  # noqa: E402
    from reversi.regab import regab_load_data_set_from_file  # noqa: E402
    from reversi.tools.state_machine import Verbosity  # noqa: E402

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        model = LogisticModel(str(BUILD / "rlm_su_1e7.json"),
                              verbosity=Verbosity.HIGH,
                              base_dir_override=str(D))
        model.move_to_step("CONFIG")
        # The build area's config may predate the effect_size -> anova
        # key rename (D-309): force the level on so the tier verifies
        # the ANOVA output regardless of the (regenerable, gitignored)
        # build config's key naming.
        model.context.cfg.anova.enable = True
        model.move_to_step("ANOVA")
    drep = D / "anova" / "anova_report.txt"
    dtxt = drep.read_text()
    dcfg, dfset, dblocks = _campaign(BUILD / "rlm_su_1e7.json")
    n_sub = sum(b[4] for b in dblocks)
    check("D1  the A2050 sub-variable expansion: the report's ANOVA rows == "
          "sum(n_instances) over the feature set",
          len(re.findall(r"^  ANOVA ", dtxt, re.M)) == n_sub, f"{n_sub}")
    check("D2  NO cache file for the level (a diagnostic, no rlmwf_06_*)",
          not (D / "rlmwf_06_ANOVA.dat").exists()
          and not list(D.glob("rlmwf_06_*")))
    dindexes = hlp_indexes_load_from_file(str(D / "rlmwf_05_INDEXES.dat"),
                                          checksum=False).indexes
    dset = regab_load_data_set_from_file(str(D / "rlmwf_04_POSITIONS.dat"),
                                         checksum=False)
    _pos, dy = dset.generate_positions_and_game_values()
    check("D3  the cached tagged data: the indexes rows == the game values "
          "length (the ANOVA inputs are the same population)",
          dindexes.shape[0] == dy.shape[0], f"{dindexes.shape} / {dy.shape}")
    lines = {}
    for line in dtxt.splitlines():
        m = re.match(r"^  ANOVA (\w+) inst (\d+): eta2 ([\d.]+), omega2 "
                     r"([\d.-]+) \(K (\d+), N (\d+)\)$", line)
        if m:
            lines[(m.group(1), int(m.group(2)))] = (
                float(m.group(3)), float(m.group(4)), int(m.group(5)),
                int(m.group(6)))
    anova_ok = True
    inv_ok = True
    for (name, c0, c1, n_conf, n_inst) in dblocks:
        for i in range(n_inst):
            got = lines.get((name, i))
            ref = py_anova(dindexes[:, c0 + i], dy)
            if got is None or abs(got[0] - ref["eta2"]) > 5e-5 \
                    or abs(got[1] - ref["omega2"]) > 5e-5 \
                    or got[2] != ref["k"] or got[3] != ref["n"]:
                anova_ok = False
            if got is not None and got[0] < got[1]:
                inv_ok = False
    check("D4  every ANOVA line == the independent recompute from the cached "
          "indexes + game values (eta2 / omega2 / K / N, 5e-5)", anova_ok)
    check("D5  the eta2 >= omega2 invariant holds on all the real "
          "sub-variables", inv_ok)
    mob = min(dblocks, key=lambda b: b[3])        # the mobility (the smallest K)
    f_mob, _p = stats.f_oneway(*[dy[dindexes[:, mob[1]] == c]
                                 for c in np.unique(dindexes[:, mob[1]])])
    ref_mob = lines[(mob[0], 0)]
    eta2_mob = ((ref_mob[2] - 1) * f_mob) / ((ref_mob[2] - 1) * f_mob
                                             + (ref_mob[3] - ref_mob[2]))
    check("D6  scipy's f_oneway on the mobility column (the full 2M "
          "positions) agrees with the report to 5e-5",
          abs(ref_mob[0] - eta2_mob) < 5e-5,
          f"{ref_mob[0]} vs {eta2_mob}")

    # The adherence: every report row vs the probe's own trio over the DB
    # counts (the cached indexes) and the ideal (the cached corpus
    # marginal, the SU_ANALYSIS publication).
    from reversi.tools.binio import BinaryReader  # noqa: E402
    # The probe's own binio read of the SU cache (D-288 layout): the
    # header + the signature block (skipped — the D tier needs only
    # the marginal) + the marginal; the joint block is left unread.
    with BinaryReader(D / "rlmwf_03_SU_ANALYSIS.dat",
                      compressed=True) as r:
        r.read_header()
        r.read_string()
        r.read_u64()
        r.read_u64()
        r.read_u64()
        r.read_string()
        r.read_string()
        n_pairs = int(r.read_u32())
        for _ in range(n_pairs):
            r.read_string()
            r.read_string()
        n_marg = int(r.read_u32())
        marginal = [(r.read_string(), int(r.read_u32()),
                     int(r.read_u64()), r.read_array(), r.read_array())
                    for _ in range(n_marg)]
    corpus = {"marginal": marginal}
    ideal_lookup = {(nm, ii): dict(zip(cd.tolist(), ct.tolist()))
                    for (nm, ii, _nc, cd, ct) in corpus["marginal"]}
    mine = {}
    for (name, c0, c1, n_conf, n_inst) in dblocks:
        for i in range(n_inst):
            codes, counts = np.unique(dindexes[:, c0 + i],
                                      return_counts=True)
            mine[(name, i)] = py_adherence(
                dict(zip(codes.tolist(), counts.tolist())),
                ideal_lookup.get((name, i), {}))
    adh = re.findall(ADH_RX, dtxt, re.M)
    check("D7  the report's adherence rows == the independently recomputed "
          "ones (all the 47 keys, the printed TV non-increasing)",
          len(adh) == n_sub
          and {(n, int(i)) for (n, i, *_r) in adh} == set(mine)
          and all(float(adh[i][2]) >= float(adh[i + 1][2])
                  for i in range(len(adh) - 1)),
          f"{len(adh)} rows: {sorted({(n, int(i)) for (n, i, *_r) in adh} ^ set(mine))}")
    check("D8  the TV / KL / merged of every row match the independent trio "
          "(5e-5 on the printed decimals; the inf rows align)",
          all(close(float(tv), mine[(n, int(i))]["tv"], 5e-5)
              and close(float(kl), mine[(n, int(i))]["kl"], 5e-5)
              and int(mg) == mine[(n, int(i))]["merged"]
              for (n, i, tv, kl, _ch, _p, mg) in adh),
          str(adh[:2]))

# ---------------------------------------------------------------- F tier
runner = (ROOT / "run_utests.sh").read_text()
check("F1  the runner registers the anova suite",
      "test.reversi.lm.test_wrk_anova" in runner)
for rel in ("docs/src/reversi/lm/wrk_anova.md",
            "docs/test/reversi/lm/test_wrk_anova.md"):
    check(f"F2  the D-007 mirror exists: {rel}", (ROOT / rel).exists())
overview = (ROOT / "notes" / "overview.md").read_text()
check("F3  the overview rows name the worker + its suite (the underscore-escaped forms)",
      r"src/reversi/lm/wrk\_anova.py" in overview
      and r"test\_wrk\_anova.py" in overview)
check("F4  the level is OPT-IN in the shipped configs: no production fixture "
      "(rlm_01..rlm_04) enables it",
      all('"anova"' not in (ROOT / "test" / "reversi" / "data"
                                  / f"rlm_0{i}.json").read_text()
          for i in (1, 2, 3, 4)))
check("F5  the D-298 split boundary: hlp_anova carries the ANOVA "
      "family (the ANOVA + the adherence + the compute / report "
      "methods), the SU kernels live in hlp_su_analysis (the "
      "private _symmetric_uncertainty)",
      all(k in hat for k in ("def hlp_anova_eta_omega", "def hlp_anova_adherence",
                             "def hlp_anova_compute_analysis",
                             "def hlp_anova_generate_report"))
      and "def _symmetric_uncertainty" in
      (ROOT / "src" / "reversi" / "lm"
       / "hlp_su_analysis.py").read_text()
      and "def symmetric_uncertainty" not in hat)
check("F6  the report format: the title + the two section headers",
      (TMP / "c_mock" / "anova" / "anova_report.txt").read_text()
      .splitlines()[1] == "=" * 40
      and "Sub-variables (the eta-squared / omega-squared):" in
      (TMP / "c_mock" / "anova" / "anova_report.txt").read_text())

# ---------------------------------------------------------------- report
print(f"\n{fails} mismatch(es)", file=sys.stderr)
sys.exit(1 if fails else 0)
