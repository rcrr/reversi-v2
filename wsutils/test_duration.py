#!/usr/bin/env python3
"""
test_duration.py — the per-test duration classification tool (N timed runs).

WHAT IT IS: a MEASUREMENT tool (wsutils.md §1) — it makes NO a/b/c checks and no assertions. It
classifies every test of the suite by TIER and TIMING:

1. STATIC tag classification (AST, one pass): every test method gets
   - perf:         the @skipUnless(... 'PERF' ...) decorator (the PERF=1 print-only tests)
   - db_required:  the class setUp calls db_long_gate (the DB-gated tests)
   - tier:         VVLONG > VLONG > LONG > NORMAL — the @skipUnless(tier_vvlong/tier_vlong)
                   method decorators and the setUp gate calls (tags.py), the highest wins
2. N TIMED RUNS (default 3, --runs N): N ISOLATED subprocess launches of the whole suite with
   ALL tiers on (LONG=1 VLONG=1 VVLONG=1 PERF=1; a live regab DB is required), each recording
   (test-id, status, ms) with the measure_suite TimedResult pattern into
   scratch/.test_duration_run<i>.tsv. Process isolation: every launch starts from a clean
   state (the temp dirs, the caches, the golden re-derivations).
3. AGGREGATION: per test the MEAN and the population VARIANCE (ddof=0) of the N durations,
   the status (VERDE / ROSSO / SKIPPED; FLAKY when the N runs disagree), joined with the
   static tags. Two artifacts:
   - scratch/test_duration.csv  module,class,test,perf,db_required,tier,status,duration_ms,variance_ms
   - scratch/test_duration.md   the summary + the table sorted by mean duration, descending

USAGE (from the workspace root):
  .venv/bin/python wsutils/test_duration.py [--runs N]     (default N=3)
  # internal (one isolated timed launch, written by the --runs driver):
  .venv/bin/python wsutils/test_duration.py --measure-run <i>

SAFETY: writes ONLY under scratch/ (the .test_duration_run<i>.tsv launch artifacts + the two
reports). The tree is read-only.

ORIGIN: D-531 — the overview next-step "select the tests by DURATION with the 5 tags": the per-test
timing baseline (measure_suite.py is the 1-run ancestor; this tool adds the tag join, the N-run
mean/variance, and the all-tiers launch).
"""

import argparse
import ast
import os
import subprocess
import sys
import time
import unittest
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

SCATCH = ROOT / "scratch"
CSV_OUT = SCATCH / "test_duration.csv"
MD_OUT = SCATCH / "test_duration.md"

STATUS_NAME = {"ok": "VERDE", "fail": "ROSSO", "error": "ROSSO", "skip": "SKIPPED",
               "xfail-ok": "VERDE", "unexpected": "ROSSO"}


# ---------------------------------------------------------------------
# 1. the static tag classification (AST)
# ---------------------------------------------------------------------

def _decorator_tags(dec):
    """(perf, vlong, vvlong) from one decorator node: the skipUnless gate shapes."""
    perf = vlong = vvlong = False
    if isinstance(dec, ast.Call):
        for node in ast.walk(dec):
            if isinstance(node, ast.Constant) and node.value == "PERF":
                perf = True
            if isinstance(node, ast.Name) and node.id == "tier_vlong":
                vlong = True
            if isinstance(node, ast.Name) and node.id == "tier_vvlong":
                vvlong = True
    return perf, vlong, vvlong


def _setup_calls(fn):
    """The Name ids called in a setUp body (the gate calls: db_long_gate / tier_*)."""
    if fn is None:
        return set()
    return {n.func.id for n in ast.walk(fn)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


def _tier_of(vvlong, vlong, db):
    if vvlong:
        return "VVLONG"
    if vlong:
        return "VLONG"
    if db:
        return "LONG"
    return "NORMAL"


def _class_gates(cls):
    """
    The class-level gate facts: (db, vvlong, vlong, perf) from the setUp calls + the class-level decorators.
    """
    setup = next((n for n in cls.body if isinstance(n, ast.FunctionDef)
                  and n.name == "setUp"), None)
    calls = _setup_calls(setup)
    db = "db_long_gate" in calls
    vv = "tier_vvlong" in calls
    vl = "tier_vlong" in calls
    perf = False
    for dec in cls.decorator_list:
        p, vlx, vvx = _decorator_tags(dec)
        perf, vl, vv = perf or p, vl or vlx, vv or vvx
    return db, vv, vl, perf


def _method_gates(fn):
    """The method-level gate facts: (perf, vlong, vvlong) from the decorators."""
    perf = vlong = vvlong = False
    for dec in fn.decorator_list:
        p, vl, vv = _decorator_tags(dec)
        perf, vlong, vvlong = perf or p, vlong or vl, vvlong or vv
    return perf, vlong, vvlong


def _own_tests(cls):
    return [n for n in cls.body if isinstance(n, ast.FunctionDef)
            and n.name.startswith("test_")]


def _bases_of(cls):
    """The base-class names (Name and Attribute forms), in declaration order."""
    out = []
    for b in cls.bases:
        if isinstance(b, ast.Name):
            out.append(b.id)
        elif isinstance(b, ast.Attribute):
            out.append(b.attr)
    return out


def classify_tree():
    """
    Every test method of the test/ tree -> {perf, db_required, tier}.

    Key: (module, class, test) with the dotted module path (test.reversi[.zone].test_x).
    Inheritance-aware: unittest DISCOVERS the inherited test methods under every concrete TestCase
    subclass (the Base*Test mixin idiom in test_board), so the classification resolves the same way
    — a concrete class carries its own methods + the in-file ancestors' methods, with the ANCESTOR's
    class-level gates.
    """
    tags = {}
    for path in sorted((ROOT / "test").rglob("test_*.py")):
        rel = path.relative_to(ROOT / "test")
        # the unittest module path: the test/ directory is the "test" package (top_level_dir=ROOT)
        module = "test." + ".".join(rel.with_suffix("").parts)
        tree = ast.parse(path.read_text())
        classes = {c.name: c for c in tree.body if isinstance(c, ast.ClassDef)}

        def discoverable(name, seen):
            """
            A class is discovered by unittest if ANY base (transitively) is a TestCase — the
            multiple-inheritance idiom: class X(unittest.TestCase, BaseMixin).
            """
            if name in seen:
                return False
            seen.add(name)
            for base in _bases_of(classes[name]):
                if base.endswith("TestCase"):
                    return True
                if base in classes and discoverable(base, seen):
                    return True
            return False

        def methods_of(name, seen):
            """
            The discovered test methods of a class: its own + the in-file ancestors' (every base,
            the multiple-inheritance idiom).
            """
            if name in seen:
                return []
            seen.add(name)
            inherited = []
            for base in _bases_of(classes[name]):
                if base in classes:
                    inherited += methods_of(base, seen)
            return inherited + _own_tests(classes[name])

        for name, cls in classes.items():
            if not discoverable(name, set()):
                continue
            for fn in methods_of(name, set()):
                # the class-level gates of an INHERITED method are the OWNER's (the setUp that
                # carries the gate calls lives where the method is defined)
                owner = next(c for c in classes.values() if fn in _own_tests(c))
                odb, ovv, ovl, operf = _class_gates(owner)
                m_perf, m_vl, m_vv = _method_gates(fn)
                tags[(module, name, fn.name)] = {
                    "perf": m_perf or operf,
                    "db_required": odb,
                    "tier": _tier_of(m_vv or ovv, m_vl or ovl, odb),
                }
    return tags


# ---------------------------------------------------------------------
# 2. one isolated timed launch (--measure-run i)
# ---------------------------------------------------------------------

class TimedResult(unittest.TestResult):
    """The measure_suite TestResult: (ms, test-id, status) per test."""

    def __init__(self):
        super().__init__()
        self.rows = []
        self._t0 = 0.0
        self._cur = None

    def startTest(self, test):
        super().startTest(test)
        self._cur = test
        self._t0 = time.perf_counter()

    def _record(self, status):
        if self._cur is None:
            return
        ms = (time.perf_counter() - self._t0) * 1000.0
        self.rows.append((self._cur.id(), status, ms))

    def addSuccess(self, test):
        self._record("ok")
        super().addSuccess(test)

    def addError(self, test, err):
        self._record("error")
        super().addError(test, err)

    def addFailure(self, test, err):
        self._record("fail")
        super().addFailure(test, err)

    def addSkip(self, test, reason):
        self._record("skip")
        super().addSkip(test, reason)

    def addExpectedFailure(self, test, err):
        self._record("xfail-ok")
        super().addExpectedFailure(test, err)

    def addUnexpectedSuccess(self, test):
        self._record("unexpected")
        super().addUnexpectedSuccess(test)


def measure_run(i):
    SCATCH.mkdir(parents=True, exist_ok=True)
    loader = unittest.TestLoader()
    suite = loader.discover(str(ROOT / "test"), top_level_dir=str(ROOT))
    result = TimedResult()
    t0 = time.perf_counter()
    suite.run(result)
    wall = (time.perf_counter() - t0) * 1000.0
    out = SCATCH / f".test_duration_run{i}.tsv"
    with open(out, "w", encoding="utf-8") as f:
        for tid, status, ms in result.rows:
            f.write(f"{tid}\t{status}\t{ms:.3f}\n")
    print(f"run {i}: {len(result.rows)} tests, wall {wall / 1000.0:.1f} s -> {out.name}")
    return 0


# ---------------------------------------------------------------------
# 3. the aggregation
# ---------------------------------------------------------------------

def split_tid(tid):
    """'test.reversi[.zone].test_x.Class.test_y' -> (module, class, test)."""
    parts = tid.split(".")
    i = next(k for k, p in enumerate(parts) if p.startswith("test_"))
    module = ".".join(parts[:i + 1])
    return module, parts[i + 1], parts[i + 2]


def read_runs(n):
    """The N launch TSVs -> {tid: [ms x N]} + {tid: [status x N]} (missing = None slots)."""
    durs, stats = {}, {}
    for i in range(1, n + 1):
        tsv = SCATCH / f".test_duration_run{i}.tsv"
        if not tsv.exists():
            print(f"WARNING: run {i} artifact missing ({tsv.name})")
            continue
        for line in tsv.read_text().splitlines():
            tid, status, ms = line.split("\t")
            durs.setdefault(tid, [None] * n)[i - 1] = float(ms)
            stats.setdefault(tid, [None] * n)[i - 1] = status
    return durs, stats


def mean_var(samples):
    vals = [v for v in samples if v is not None]
    if not vals:
        return None, None
    m = sum(vals) / len(vals)
    var = sum((v - m) ** 2 for v in vals) / len(vals)
    return m, var


def aggregate(tags, durs, stats, n):
    rows = []
    for tid, ms_list in durs.items():
        module, cls, test = split_tid(tid)
        m, var = mean_var(ms_list)
        st = [s for s in stats.get(tid, [None] * n) if s is not None]
        names = {STATUS_NAME.get(s, s) for s in st}
        status = next(iter(names)) if len(names) == 1 else "FLAKY"
        tag = tags.get((module, cls, test), {"perf": False, "db_required": False,
                                              "tier": "NORMAL"})
        rows.append({"module": module, "class": cls, "test": test,
                     "perf": tag["perf"], "db_required": tag["db_required"],
                     "tier": tag["tier"], "status": status,
                     "mean": m, "var": var})
    # the statically known tests that never appeared in a run (defensive)
    seen = {(r["module"], r["class"], r["test"]) for r in rows}
    for (module, cls, test), tag in tags.items():
        if (module, cls, test) not in seen:
            rows.append({"module": module, "class": cls, "test": test,
                         "perf": tag["perf"], "db_required": tag["db_required"],
                         "tier": tag["tier"], "status": "NOT_RUN",
                         "mean": None, "var": None})
    rows.sort(key=lambda r: (r["mean"] is None, -(r["mean"] or 0.0)))
    return rows


def write_csv(rows):
    lines = ["module,class,test,perf,db_required,tier,status,duration_ms,variance_ms"]
    for r in rows:
        dur = f"{r['mean']:.1f}" if r["mean"] is not None else ""
        var = f"{r['var']:.1f}" if r["var"] is not None else ""
        lines.append(f"{r['module']},{r['class']},{r['test']},{'TRUE' if r['perf'] else 'FALSE'},"
                     f"{'TRUE' if r['db_required'] else 'FALSE'},{r['tier']},{r['status']},"
                     f"{dur},{var}")
    CSV_OUT.write_text("\n".join(lines) + "\n")


def write_md(rows, n):
    by_tier, by_status = {}, {}
    for r in rows:
        by_tier[r["tier"]] = by_tier.get(r["tier"], 0) + 1
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
    tier_line = ", ".join(f"{t} {c}" for t, c in sorted(by_tier.items()))
    stat_line = ", ".join(f"{s} {c}" for s, c in sorted(by_status.items()))
    perf_n = sum(1 for r in rows if r["perf"])
    db_n = sum(1 for r in rows if r["db_required"])
    out = [
        "# Test duration report",
        "",
        f"Generated {datetime.now().isoformat(timespec='seconds')} — {n} timed runs, all tiers on "
        "(LONG=1 VLONG=1 VVLONG=1 PERF=1, live regab DB).",
        "",
        f"Totals: **{len(rows)} tests** — {stat_line}.",
        f"Per tier: {tier_line}. PERF: {perf_n}. DB-required: {db_n}.",
        "",
        "duration_ms = mean of the N runs; variance_ms = population variance (ddof=0).",
        "Sorted by mean duration, descending.",
        "",
        "| rank | module | class | test | tier | perf | db | status | mean_ms | var_ms |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for i, r in enumerate(rows, 1):
        dur = f"{r['mean']:.1f}" if r["mean"] is not None else "-"
        var = f"{r['var']:.1f}" if r["var"] is not None else "-"
        out.append(f"| {i} | {r['module']} | {r['class']} | {r['test']} | {r['tier']} | "
                   f"{'Y' if r['perf'] else '.'} | {'Y' if r['db_required'] else '.'} | "
                   f"{r['status']} | {dur} | {var} |")
    MD_OUT.write_text("\n".join(out) + "\n")


# ---------------------------------------------------------------------
# the driver
# ---------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runs", type=int, default=3, help="the number of timed launches (default 3)")
    ap.add_argument("--measure-run", type=int, default=0,
                    help=argparse.SUPPRESS)  # internal: one isolated timed launch
    args = ap.parse_args()

    if args.measure_run:
        return measure_run(args.measure_run)

    n = args.runs
    tags = classify_tree()
    print(f"static tags: {len(tags)} test methods classified")

    # the N isolated launches (all tiers on in the child env)
    env = dict(os.environ, LONG="1", VLONG="1", VVLONG="1", PERF="1")
    for i in range(1, n + 1):
        print(f"--- launch {i}/{n} ---")
        rc = subprocess.call([sys.executable, __file__, "--measure-run", str(i)], env=env)
        if rc != 0:
            print(f"launch {i} failed (rc={rc}) — aborting")
            return rc

    durs, stats = read_runs(n)
    rows = aggregate(tags, durs, stats, n)
    write_csv(rows)
    write_md(rows, n)
    print(f"written: {CSV_OUT} and {MD_OUT} ({len(rows)} tests)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
