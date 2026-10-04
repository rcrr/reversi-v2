#!/usr/bin/env python3
#
# verify_su_analysis.py
#
# Probe pinning the SU_ANALYSIS level (the I-017 step 3, D-258):
# the worker (src/reversi/lm/wrk_su_analysis.py) + its frequency data
# plane (hlp_su_analysis, the accumulators — the D-295 hlp_random_play
# retirement) + the shared kernels it calls (the local SU
# kernels — the D-298 hlp_feature_analysis move). The worker's
# corpus engine is the
# random_game play-path (the su-corpus-5 lineage); the tier-B corpus
# is the same engine (D-285 — the hlp_wave wave engine is retired).
# The level is the workspace's ONLY no-DB corpus consumer: it reads
# the cfg + the feature_set and generates its own population.
#
# Tiers:
#   A  the module structure: the factory, the no-DB discipline, the
#      cache constants, the wave-size cap, the whitespace hygiene,
#      the position language (D-296)
#   B  the independent re-derivations (no worker): the corpus at the
#      config's ec, the marginal vs the FeatureSet batch path, the
#      joint vs a pure-python Counter, the SU vs the ratio-form MI,
#      the cache signature vs an independent feature_set hash
#   C  the live rlm_00 pipeline (no DB): the step-3 stop, the cache
#      file + its sidecar, the ctx publication, the phase-2 recompute
#      on the cache hit, the report vs pure-python math, the down, the
#      opt-in absence of both artifacts
#   F  the cross-file facts: the runner, the rename completeness, the
#      mirrors, the ANOVA consumer contract
#
# The a/b/c rule (probe_rules §3): the checks that a test already pins
# through the same path are NOT here — the factory name, the enable
# no-op, the cache-hit log, the su_pairs joint presence, the CSV flag
# and the mock-ctx down all live in test_wrk_su_analysis.py. What
# stays: the independent math (the ratio-form MI, the Counter joint,
# the FeatureSet batch marginals), the file-level facts (the sidecar,
# the absence of the artifacts) and the report numbers.
#
# House convention: writes only under build/tmp, self-cleans via
# atexit; exit code 1 on any mismatch.
#

import atexit
import contextlib
import hashlib
import io
import json
import math
import os
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

import json5
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / "src"))

TMP = ROOT / "build" / "tmp" / "verify_su_analysis"
TMP.mkdir(parents=True, exist_ok=True)
atexit.register(lambda: shutil.rmtree(TMP, ignore_errors=True))

CFG = ROOT / "test" / "reversi" / "data" / "rlm_00.json"

fails = 0


def check(label, cond, detail=""):
    # stderr: stdout carries the pipeline log around the moves.
    global fails
    if not cond:
        fails += 1
    print(f"[{'ok  ' if cond else 'FAIL'}] {label}"
          + (f" -- {detail}" if detail and not cond else ""), file=sys.stderr)


def ws_lines(path):
    # Lines 1-26 are the canonical license header (never swept).
    body = Path(path).read_text().splitlines()[26:]
    return [i for i, line in enumerate(body, 27)
            if re.match(r'^[ \t]+$', line) or re.search(r'[ \t]$', line)]


def py_entropy(counts):
    """The Shannon entropy in bits — a pure-python loop over the
    counts (the probe's own implementation)."""
    n = sum(counts)
    if n == 0:
        return 0.0
    return -sum((c / n) * math.log2(c / n) for c in counts if c > 0)


def py_mi_ratio(counter, marg_u, marg_v):
    """The mutual information by its DEFINITION — the ratio form
    sum p(u,v) log2( p(u,v) / (p(u) p(v)) ) over the observed cells.
    The kernel deliberately uses the identity I = H(u) + H(v) - H(u,v)
    instead, so this is an independent derivation (and the 0/0 the
    identity avoids cannot arise: an observed cell has both marginals
    positive)."""
    n = sum(counter.values())
    nu = sum(marg_u.values())
    nv = sum(marg_v.values())
    total = 0.0
    for (u, v), c in counter.items():
        puv = c / n
        pu = marg_u[u] / nu
        pv = marg_v[v] / nv
        total += puv * math.log2(puv / (pu * pv))
    return total


# ---------------------------------------------------------------- A tier
W = (ROOT / "src" / "reversi" / "lm" / "wrk_su_analysis.py")
wt = W.read_text()
H = (ROOT / "src" / "reversi" / "lm" / "hlp_su_analysis.py")
wh = H.read_text()
check("A1  the factory: @validate_call + wrk_su_analysis() -> Worker",
      "@validate_call(config=ConfigDict(arbitrary_types_allowed=True))" in wt
      and "def wrk_su_analysis() -> Worker:" in wt)
check("A2  the Worker name is SU_ANALYSIS (the cache slot prefix follows it)",
      'return Worker("SU_ANALYSIS", _up, _down)' in wt)
check("A3  the no-DB discipline (the design section 3.3): no regab / "
      "positions / hlp_indexes import — the corpus is the level's own "
      "(the worker skeleton + the hlp)",
      all(k not in wt for k in ("regab", "wrk_positions", "hlp_indexes",
                                "game_values"))
      and all(k not in wh for k in ("regab", "wrk_positions",
                                    "hlp_indexes", "game_values")))
check("A4  the batch-size cap: min(_WAVE_SIZE, total - harvested) "
      "(the D-252 cap, the random_game batch form, in the hlp compute)",
      "n = min(_WAVE_SIZE, total - harvested)" in wh)
check("A5  __all__ = ['wrk_su_analysis']", "__all__ = ['wrk_su_analysis']" in wt)
check("A6  no trailing whitespace outside the license header "
      "(the worker skeleton + the hlp)",
      not ws_lines(W) and not ws_lines(H),
      str(ws_lines(W)) + str(ws_lines(H)))

from reversi.lm import hlp_su_analysis as hlp  # noqa: E402

check("A7  the cache constants (read from the hlp module): the generator "
      "version su-corpus-5, the PRNG pin, the 3e6 batch ceiling",
      hlp._GENERATOR_VERSION == "su-corpus-5"
      and hlp._PRNG_VERSION == "mt19937-64"
      and hlp._WAVE_SIZE == 3_000_000)
_FIX_JSON = json5.loads(
    (ROOT / "test" / "reversi" / "data" / "rlm_00.json").read_text(
        encoding="utf-8"))
check("A8  the rarity thresholds (the rlm_00 fixture JSON, the "
      "report's Section B, D-292): [1, 2, 5, 10, 100]",
      _FIX_JSON["su_analysis"]["rarity_thresholds"]
      == [1, 2, 5, 10, 100])

from reversi.lm.logistic_model import LogisticModel  # noqa: E402
from reversi.board import (initial_game_position,  # noqa: E402
                           position_empty_count)
from reversi.random_game import random_game_play_path  # noqa: E402
from reversi.tools.prng import MT19937  # noqa: E402
from reversi.tools.state_machine import Verbosity  # noqa: E402


def _campaign():
    """The real-pipeline campaign (the hlp_gate replacement):
    the facade runs CREATED -> CONFIG -> FEATURES on the
    rlm_00 fixture (the target_level stop, the probe tmp
    base_dir) — the cfg + the feature_set come from the real
    context."""
    rlm = LogisticModel(str(CFG), verbosity=Verbosity.NONE,
                        base_dir_override=TMP)
    rlm.run("FEATURES")
    ctx = rlm.context
    return ctx.cfg, ctx.feature_set, ctx.feature_set.feature_blocks


cfg, fset, blocks = _campaign()

check("A9  the rlm_00 sub-variable expansion: 15 columns "
      "(3 mobilities + the EDGE 4 + the ELLE 8)",
      sum(b[4] for b in blocks) == 15, str(blocks))
check("A10 the position language (D-296): no parallel (mover, opponent) "
      "arrays cross a module boundary — no _to_positions rebuild, no "
      "column_stack, no field-split feeding in the hlp",
      "_to_positions" not in wh and "column_stack" not in wh
      and "['mover']" not in wh)

# ---------------------------------------------------------------- B tier
# The corpus: a small deterministic play-path run (3000 positions,
# ec 20, seed 42 — the random_game engine, the worker's own
# generator; D-284/D-285).
N = 3000
EC = 20
SEED = 42
prng = MT19937(SEED)
igp = initial_game_position()
_harvested = 0
_ps = []
while _harvested < N:
    _k = N - _harvested
    _batch = np.full(_k, igp)
    _final, _ec_arr = random_game_play_path(_batch, EC, prng)
    _keep = _ec_arr == EC
    _ps.append(_final[_keep])
    _harvested += int(_keep.sum())
pos = np.concatenate(_ps)
mover = pos['mover']
opp = pos['opponent']
check("B1  the corpus: the harvested count is the requested total",
      _harvested == N and pos.shape[0] == N, str(pos.shape))

# The ec arrest: every harvested position sits at the config's ec,
# recomputed from the bitboards (64 - the occupied popcount) — the
# corpus-level form of the ec pin (board.position_empty_count is the
# array cross-check, the D-295 replacement of ec_of).
occupied = np.bitwise_or(mover, opp)
ec_indep = 64 - np.array([int(x).bit_count() for x in occupied])
check("B2  every harvested position has ec 20 (the arrest rule, the "
      "independent 64 - popcount)",
      bool((ec_indep == EC).all())
      and bool((position_empty_count(pos) == EC).all()))

# The marginal: the streaming accumulator vs the FeatureSet's OWN batch
# index path (one shot, no chunking, no dense/sparse split).
idx = fset.compute_indexes(pos)
marg = hlp._MarginalAccumulator(fset)
marg.add(idx)
marginal = marg.result()
blocks_by_name = {b[0]: b for b in blocks}
marg_ok = True
totals_ok = True
for (name, i, n_conf, codes, counts) in marginal:
    col = blocks_by_name[name][1] + i
    ref = np.bincount(idx[:, col].astype(np.intp), minlength=n_conf)
    nz = np.nonzero(ref)[0]
    if not (np.array_equal(codes, nz.astype(np.uint32))
            and np.array_equal(counts, ref[nz].astype(np.int64))):
        marg_ok = False
    if int(counts.sum()) != N:
        totals_ok = False
check("B3  the marginal == the FeatureSet batch bincount (the support + "
      "the counts, per sub-variable)", marg_ok)
check("B4  one count per position per sub-variable (every total is N)",
      totals_ok)

# The joint: the packed-u64 numpy unique-merge vs a pure-python Counter
# over the same codes (a different construction of the same table).
PAIR = ("LMC", "EDGE")
joints = hlp._JointAccumulator(fset, [PAIR])
joints.add(idx)
jres = joints.result()
check("B5  the joint result shape: one entry per requested pair",
      len(jres) == 1 and jres[0][0] == PAIR[0] and jres[0][1] == PAIR[1])
bi, bj = blocks_by_name[PAIR[0]], blocks_by_name[PAIR[1]]
pd = jres[0][2]
joint_ok = True
for ii in range(bi[4]):
    for jj in range(bj[4]):
        ci = idx[:, bi[1] + ii]
        cj = idx[:, bj[1] + jj]
        ref = Counter(zip(ci.tolist(), cj.tolist()))
        got_codes_i, got_codes_j, got_counts = pd[(ii, jj)]
        got = {(int(u), int(v)): int(c) for u, v, c
               in zip(got_codes_i, got_codes_j, got_counts)}
        if got != dict(ref):
            joint_ok = False
check("B6  the joint == a pure-python Counter (the 4 LMC x EDGE "
      "instance tables)", joint_ok)

# The SU: the ratio-form MI + the pure-python entropies vs the
# module's own _su_values (the identity-based kernel).
marg_lookup = {(nm, ii): ct
               for (nm, ii, _nc, _cd, ct) in marginal}
su_mod = {(ni, ii, nj, jj): s for (ni, ii, nj, jj, s)
          in hlp._su_values(jres, marg_lookup)}
su_indep = {}
for ii in range(bi[4]):
    for jj in range(bj[4]):
        ci = idx[:, bi[1] + ii]
        cj = idx[:, bj[1] + jj]
        counter = Counter(zip(ci.tolist(), cj.tolist()))
        mu = dict(Counter(ci.tolist()))
        mv = dict(Counter(cj.tolist()))
        I = py_mi_ratio(counter, mu, mv)
        su_indep[(PAIR[0], ii, PAIR[1], jj)] = (
            2.0 * I / (py_entropy(mu.values()) + py_entropy(mv.values())))
check("B7  the SU values == the ratio-form MI + the pure-python "
      "entropies (4 instance pairs, 1e-12)",
      set(su_mod) == set(su_indep)
      and all(abs(su_mod[k] - su_indep[k]) < 1e-12 for k in su_indep),
      str({k: (su_mod.get(k), su_indep[k]) for k in su_indep}))

# The dedup + the sort (the report's Section B): the SU is SYMMETRIC
# (2·I / (H_u + H_v)), so the (i, j) and the (j, i) directions of a
# pair are the SAME measurement. A self-pair (EDGE x EDGE) yields every
# ordered pair twice; _su_groups shows each ONCE, in the canonical
# endpoint order, sorted by the SU value descending (the strongest
# correlation first).
SELF = ("EDGE", "EDGE")
selfj = hlp._JointAccumulator(fset, [SELF])
selfj.add(idx)
selfres = selfj.result()
selfsu = hlp._su_values(selfres, marg_lookup)
selfgroups = hlp._su_groups(selfsu, [SELF])
n_edge = blocks_by_name["EDGE"][4]
n_unordered = n_edge * (n_edge - 1) // 2
check("B12 the dedup: the self-pair's ordered pairs collapse to the "
      "unordered pairs (n instances -> n*(n-1)/2, each once)",
      len(selfgroups) == 1 and selfgroups[0][0] == ("EDGE", "EDGE")
      and len(selfgroups[0][1]) == n_unordered
      and len({((an, ai), (bn, bi))
               for (an, ai, bn, bi, _s) in selfgroups[0][1]})
      == n_unordered,
      f"{len(selfsu)} ordered -> {len(selfgroups[0][1])} canonical")
endpoints = [((an, ai), (bn, bi))
             for (an, ai, bn, bi, _s) in selfgroups[0][1]]
check("B13 the sort: the group is in the canonical endpoint order "
      "(the lexicographic (feature, instance) order)",
      endpoints == sorted(endpoints), str(endpoints))

# The cache signature: the feature_set hash recomputed from the config
# dump (the first 16 hex), plus the spec keys.
base_c = TMP / "b_sig"
base_c.mkdir(parents=True, exist_ok=True)
sig_cfg = _campaign()[0]
sig_cfg.base_dir = base_c
sig = hlp._signature(type("C", (), {"cfg": sig_cfg, "feature_set": fset})())
# The independent oracle (D-291): the FeatureSet DOMAIN hash
# recomposed from its children (the INTERCEPT marker + the mset /
# the pset hash hex strings, the sorted mask contents transitively).
chunks = []
if fset.intercept:
    chunks.append(b'INTERCEPT')
if fset.mset:
    chunks.append(fset.mset.hash.encode('utf-8'))
if fset.pset:
    chunks.append(fset.pset.hash.encode('utf-8'))
ref_hash = hashlib.sha3_256(b''.join(chunks)).hexdigest()
check("B8  the signature: the feature_set hash == the FeatureSet DOMAIN hash "
      "(independently recomposed from the child-set hashes, D-291)",
      sig["feature_set_hash"] == ref_hash == fset.hash,
      f"{sig['feature_set_hash']} vs {ref_hash}")
check("B9  the signature keys (the feature_set hash + the 5 spec fields + "
      "the pairs) and NO rds_checksum (the corpus is DB-independent)",
      sorted(sig) == sorted(["feature_set_hash", "seed", "total_positions",
                             "ec", "generator_version", "prng_version",
                             "su_pairs"])
      and "rds_checksum" not in sig)
check("B10 the signature spec values: the config's seed / total / ec + the "
      "two version pins",
      sig["seed"] == sig_cfg.su_analysis.corpus.seed
      and sig["total_positions"] == sig_cfg.su_analysis.corpus.total_positions
      and sig["ec"] == sig_cfg.empty_count
      and sig["generator_version"] == "su-corpus-5"
      and sig["prng_version"] == "mt19937-64")

# The signature is a pure function of (feature_set, spec, pairs): the
# same config -> the same dict; a seed / a pair change -> a different one.
sig_same = hlp._signature(type("C", (), {"cfg": sig_cfg, "feature_set": fset})())
sig_seed = _campaign()[0]
sig_seed.su_analysis.corpus.seed = SEED + 1
sig_seed_v = hlp._signature(type("C", (), {"cfg": sig_seed, "feature_set": fset})())
sig_pair = _campaign()[0]
sig_pair.su_analysis.su_pairs = [("LMC", "ELLE")]
sig_pair_v = hlp._signature(type("C", (), {"cfg": sig_pair, "feature_set": fset})())
check("B11 the signature semantics: identical on a re-derivation, "
      "different on a seed change and on a pair change",
      sig_same == sig and sig_seed_v != sig and sig_pair_v != sig)

# ---------------------------------------------------------------- C tier
from reversi.lm.logistic_model import LogisticModel  # noqa: E402
from reversi.tools.binio import BinaryReader, verify_sha3_256_sidecar  # noqa: E402
from reversi.tools.state_machine import Verbosity  # noqa: E402


def _read_cache(path):
    """The probe's OWN binio re-derivation of the cache layout
    (D-288, NOT hlp.hlp_su_analysis_load_from_file — the independent
    read): the header + the signature block + the marginal + the
    joint (the per-instance in the sorted (ii, jj) order)."""
    if not verify_sha3_256_sidecar(path):
        raise RuntimeError("sidecar mismatch")
    with BinaryReader(path, compressed=True) as r:
        _d, _v = r.read_header()
        signature = {
            'feature_set_hash': r.read_string(),
            'seed': int(r.read_u64()),
            'total_positions': int(r.read_u64()),
            'ec': int(r.read_u64()),
            'generator_version': r.read_string(),
            'prng_version': r.read_string(),
        }
        n_pairs = int(r.read_u32())
        signature['su_pairs'] = [[r.read_string(), r.read_string()]
                                 for _ in range(n_pairs)]
        nm = int(r.read_u32())
        marginal = []
        for _ in range(nm):
            marginal.append((r.read_string(), int(r.read_u32()),
                             int(r.read_u64()), r.read_array(),
                             r.read_array()))
        if int(r.read_u8()) == 0:
            joint = None
        else:
            nj = int(r.read_u32())
            joint = []
            for _ in range(nj):
                ni = r.read_string()
                nj2 = r.read_string()
                k = int(r.read_u32())
                pd = {}
                for _ in range(k):
                    ii = int(r.read_u32())
                    jj = int(r.read_u32())
                    pd[(ii, jj)] = (r.read_array(), r.read_array(),
                                    r.read_array())
                joint.append((ni, nj2, pd))
    return {'signature': signature, 'marginal': marginal, 'joint': joint}


base = TMP / "c_live"
base.mkdir(parents=True, exist_ok=True)
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    model = LogisticModel(str(CFG), verbosity=Verbosity.HIGH,
                          base_dir_override=str(base))
    model.move_to_step("SU_ANALYSIS")
log1 = buf.getvalue()
cache = base / "rlmwf_03_SU_ANALYSIS.dat"
report = base / "su_analysis" / "su_analysis_report.txt"
check("C1  the step-3 stop: current_step 3 / name SU_ANALYSIS",
      model.current_step == 3 and model.current_worker_name == "SU_ANALYSIS")
check("C2  the flat cache file rlmwf_03_SU_ANALYSIS.dat + its sidecar "
      "verifies (the binio independent recompute)",
      cache.exists() and verify_sha3_256_sidecar(cache))
check("C3  the run stops at the level: no rlmwf_04_POSITIONS.dat "
      "(the DB levels were never reached)",
      not (base / "rlmwf_04_POSITIONS.dat").exists())
check("C4  the ctx publication: the tables dict with the marginal + the "
      "joint + the signature",
      model.context.su_analysis_tables is not None
      and sorted(model.context.su_analysis_tables)
      == ["joint", "marginal", "signature"])
cached = _read_cache(cache)
cache_bytes = cache.read_bytes()
check("C5  the cached signature == the live _signature(ctx) "
      "(the file vs the ctx)",
      cached["signature"] == hlp._signature(model.context))
check("C6  the cached marginal: 15 sub-variables, each total == the "
      "fixture's 10000 positions",
      len(cached["marginal"]) == 15
      and all(int(ct.sum()) == 10000
              for (_n, _i, _nc, _cd, ct) in cached["marginal"]))
check("C7  the joint: the fixture's [LMC, EDGE] canonicalizes to "
      "(EDGE, LMC) -> one pair, the 4 x 1 instance tables (the pair "
      "order follows the sorted names)",
      set(cached["joint"][0][:2]) == {"LMC", "EDGE"}
      and sorted(cached["joint"][0][2]) == [(0, 0), (1, 0), (2, 0), (3, 0)],
      str(cached["joint"][0][:2]))
check("C8  the report path (dir_name / report_file_name under base_dir)",
      report.exists())
check("C9  the log carries the corpus line + the report line",
      "Generating the SU_ANALYSIS corpus" in log1
      and "SU_ANALYSIS report written" in log1)

# The report vs the pure-python math: every sub-variable line is
# recomputed from the cached counts (the report numbers are pinned by
# no test), and the SU lines are the top-20 of the recomputed list.
text = report.read_text()
# The D-293 aligned rows: the name / the inst left-justified to the
# max width, the numeric values right-justified to the computed max
# width (one or more spaces between the label and the value).
line_rx = re.compile(
    r"^  (?P<name>\w+)\s+inst (?P<i>\d+): K_obs\s+(?P<k>\d+)/(?P<nc>\d+), "
    r"H\s+(?P<h>[\d.]+), H_norm\s+(?P<hn>[\d.]+), "
    r"coverage\s+(?P<cov>[\d.]+), never-obs\s+(?P<never>\d+)$")
su_rx = re.compile(r"^  SU (?P<ni>\w+)\[(?P<ii>\d+)\] - (?P<nj>\w+)\[(?P<jj>\d+)\] = (?P<s>[\d.]+)$")
by_key = {(nm, ii): (nc, cd, ct)
          for (nm, ii, nc, cd, ct) in cached["marginal"]}
# The theoretical configuration space per sub-variable (D-278/D-279):
# n_unique_configs for a pattern (the principal-index space),
# n_configurations for a mobility — the coverage / the never-observed
# denominator.
theoretical = {}
for _f in fset.features:
    if _f.name == 'INTERCEPT':
        continue
    _nu = getattr(_f.ref, 'n_unique_configs', None)
    _eff = _nu if _nu is not None else _f.n_configurations
    for _i in range(_f.n_instances):
        theoretical[(_f.name, _i)] = _eff
sub_ok = True
sub_seen = 0
su_lines = {}
for line in text.splitlines():
    m = line_rx.match(line)
    if m:
        sub_seen += 1
        nc, cd, ct = by_key[(m["name"], int(m["i"]))]
        eff = theoretical.get((m["name"], int(m["i"])), nc)
        k_obs = len(cd)
        h = py_entropy(ct.tolist())
        h_norm = h / math.log2(k_obs) if k_obs > 1 else 0.0
        cov = k_obs / eff
        if not (k_obs == int(m["k"]) and eff == int(m["nc"])
                and abs(h - float(m["h"])) < 5e-4
                and abs(h_norm - float(m["hn"])) < 5e-4
                and abs(cov - float(m["cov"])) < 5e-4
                and eff - k_obs == int(m["never"])):
            sub_ok = False
    m2 = su_rx.match(line)
    if m2:
        su_lines[(m2["ni"], int(m2["ii"]), m2["nj"], int(m2["jj"]))] = float(m2["s"])
check("C10 every report sub-variable line == the pure-python recompute "
      "from the cached counts (15 lines, 5e-4)",
      sub_seen == 15 and sub_ok, f"{sub_seen} lines")
su_all = hlp._su_values(cached["joint"],
                        {(nm, ii): ct
                         for (nm, ii, _nc, _cd, ct) in cached["marginal"]})
su_sorted = sorted(su_all, key=lambda x: x[4], reverse=True)
check("C11 the report SU lines are the top of the recomputed list, and "
      "every value matches to the printed 4 decimals",
      set(su_lines) == {(ni, ii, nj, jj) for (ni, ii, nj, jj, _s)
                        in su_sorted[:20]}
      and all(abs(su_lines[k] - dict(((ni, ii, nj, jj), s) for (ni, ii, nj, jj, s)
                                      in su_all)[k]) < 5e-5 for k in su_lines),
      str(su_lines))

# The phase-2 recompute on the cache hit: the report is DELETED before
# the second run, so its reappearance proves the statistics ran again
# (the cache hit covers phase 1 only).
report.unlink()
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    model.move_to_step(2)          # back to FEATURES: the down clears
    cleared = model.context.su_analysis_tables is None
    model.move_to_step("SU_ANALYSIS")
log2 = buf.getvalue()
check("C12 the down clears the published tables (the live path, step 2)",
      cleared)
check("C13 the second run HIT the cache (the log) and recomputed the "
      "statistics (the deleted report is back, byte-identical)",
      "loaded from cache" in log2 and report.exists()
      and report.read_text() == text)
check("C14 the cache file was NOT rewritten by the hit run (the phase-1 "
      "artifact is the same bytes)",
      cache.read_bytes() == cache_bytes)

# The opt-in absence: the fixture with su_analysis disabled produces NO
# cache file and NO report directory (a file-level fact).
raw = json5.loads(CFG.read_text())
raw["su_analysis"]["enable"] = False
no_su = TMP / "rlm_00_no_su.json"
no_su.write_text(json.dumps(raw, indent=2), encoding="utf-8")
base_off = TMP / "c_off"
base_off.mkdir(parents=True, exist_ok=True)
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    off = LogisticModel(str(no_su), verbosity=Verbosity.HIGH,
                        base_dir_override=str(base_off))
    off.move_to_step("SU_ANALYSIS")
check("C15 the opt-in: with enable false the level is a no-op — no cache "
      "file, no report dir, the tables None",
      not (base_off / "rlmwf_03_SU_ANALYSIS.dat").exists()
      and not (base_off / "su_analysis").exists()
      and off.context.su_analysis_tables is None
      and "disabled" in buf.getvalue())

# ---------------------------------------------------------------- F tier
runner = (ROOT / "run_utests.sh").read_text()
check("F1  the runner registers the renamed suite and no longer the old one",
      "test.reversi.lm.test_wrk_su_analysis" in runner
      and "test_wrk_feature_analysis" not in runner)

# The rename completeness: no live file carries the old level name
# (the append-only history is excluded). The historical references
# ("hlp_feature_analysis", the D-298 shared-kernels module, renamed
# hlp_anova at D-315) are stripped before the search, and so is this
# probe, which necessarily spells the old name in its search terms.
SELF = Path(__file__).resolve()
hits = []
for sub in ("src", "docs", "probes", "tools"):
    for p in (ROOT / sub).rglob("*"):
        if not p.is_file() or p.suffix not in (".py", ".md", ".json", ".sh"):
            continue
        if p.resolve() == SELF:
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        t = t.replace("test_hlp_feature_analysis", "")
        t = t.replace("hlp_feature_analysis", "")
        if "FEATURE_ANALYSIS" in t or "feature_analysis" in t:
            hits.append(str(p.relative_to(ROOT)))
check("F2  the rename is complete: no FEATURE_ANALYSIS / feature_analysis "
      "left in src/ docs/ probes/ tools/ (the historical "
      "hlp_feature_analysis references excluded)", not hits, str(hits))

for rel in ("docs/src/reversi/lm/wrk_su_analysis.md",
            "docs/test/reversi/lm/test_wrk_su_analysis.md"):
    check(f"F3  the D-007 mirror exists: {rel}", (ROOT / rel).exists())

overview = (ROOT / "notes" / "overview.md").read_text()
check("F4  the overview rows name the renamed module + its suite",
      "src/reversi/lm/wrk_su_analysis.py" in overview
      and "test_wrk_su_analysis" in overview)

mirror = (ROOT / "docs" / "src" / "reversi" / "lm" / "wrk_su_analysis.md").read_text()
check("F5  the mirror's generator version == the module's constant "
      "(the stale g0-1 pin re-derived)",
      "su-corpus-5" in mirror and "g0-1" not in mirror)

eff = (ROOT / "src" / "reversi" / "lm" / "wrk_anova.py").read_text()
hlp = (ROOT / "src" / "reversi" / "lm" / "hlp_anova.py").read_text()
check("F6  the ANOVA consumer contract: the worker imports the compute "
      "/ report methods from hlp_anova, which reads "
      "ctx.su_analysis_tables",
      "from reversi.lm.hlp_anova import" in eff
      and "hlp_anova_compute_analysis" in eff
      and "hlp_anova_generate_report" in eff
      and "ctx.su_analysis_tables" in hlp)

check("F7  the level is OPTIONAL in the shipped configs: no production "
      "fixture (rlm_01..rlm_04) enables it",
      all('"su_analysis"' not in (ROOT / "test" / "reversi" / "data"
                                  / f"rlm_0{i}.json").read_text()
          for i in (1, 2, 3, 4)))

# ---------------------------------------------------------------- report
print(f"\n{fails} mismatch(es)", file=sys.stderr)
sys.exit(1 if fails else 0)
