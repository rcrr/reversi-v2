#!/usr/bin/env python3
"""
verify_plot.py — verification probe for the PLOT level (D-149,
the 17th level after CLIENT_CHECK): the matplotlib diagnostic
figures of the logistic-model run.

Checks, independently of the test files (test_hlp_plot.py /
test_wrk_plot.py pin the unit and worker behaviour):
  A. the D-149 vocabulary: the seven canonical names, the
     titles, the name -> builder registry (the single source of
     truth the PlotConfig schema validates against), and the
     lazy-matplotlib fact (no top-level matplotlib import).
  B. the figure builders end-to-end on a synthetic PlotData (no
     ctx, no DB): every builder renders a non-trivial PNG, the
     'pdf,png' pair writes both, and the rendering is DETERMINISTIC
     (the seeded jitter + the Agg backend: two runs hash equal).
  C. the PlotConfig pilot semantics in the schema (no DB): the
     defaults (enable True, the PNG-DEFAULT ruling, the relative
     'plots' dir, the empty whitelist), the format normalization,
     the fail-fast unknown-name guard, the dedupe.

Run from the workspace root:  .venv/bin/python probes/verify_plot.py
"""
import hashlib
import sys
import atexit
import shutil
import tempfile
from pathlib import Path

import numpy as np

WS = Path(__file__).resolve().parents[1]
SRC = WS / "src" / "reversi"
sys.path.insert(0, str(WS / "src"))

failures = []


def check(label, cond, detail=""):
    print(f"[{'ok  ' if cond else 'FAIL'}] {label}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        failures.append(label)


def read(p):
    return (WS / p).read_text()


# ---------------------------------------------------------------- A: the vocabulary
from reversi.lm.hlp_plot import (PLOT_NAMES, PLOT_TITLES, PLOT_BUILDERS,
                                  PlotData, jitter, egv_bins, _kde_curve)
from reversi.lm import hlp_plot

src = read("src/reversi/lm/hlp_plot.py")
check("A1 the seven canonical names (D-149)",
      len(PLOT_NAMES) == 7 and len(set(PLOT_NAMES)) == 7)
check("A2 the builder registry covers the names exactly",
      set(PLOT_BUILDERS) == set(PLOT_NAMES))
check("A3 the titles cover the names exactly",
      set(PLOT_TITLES) == set(PLOT_NAMES))
check("A4 the schema validates against the same vocabulary",
      "from reversi.lm.hlp_plot import PLOT_NAMES"
      in read("src/reversi/lm/hlp_config_schemas.py"))
check("A5 matplotlib is imported LAZILY (no top-level import)",
      "\nimport matplotlib" not in src
      and "\nfrom matplotlib" not in src)

# ---------------------------------------------------------------- B: the builders
rng = np.random.default_rng(7)
n = 3000
d = PlotData(
    trn_y_true=(rng.integers(-32, 33, size=n) * 2).astype(np.float64),
    trn_rn=rng.standard_normal(n) * 12,
    vld_y_pred=np.clip(rng.standard_normal(n) * 25, -64, 64),
    vld_rn=rng.standard_normal(n) * 8,
    vld_gv=(rng.integers(-32, 33, size=n) * 2).astype(np.float64))

tmp = Path(tempfile.mkdtemp(dir=str(WS / "build" / "tmp")))
# the probe artifacts are removed afterwards (probe_rules §2)
atexit.register(lambda: shutil.rmtree(tmp, ignore_errors=True))
ok_render, sizes, hashes = True, {}, {}
for name in PLOT_NAMES:
    fig = PLOT_BUILDERS[name](d, "VERIFY_PLOT")
    p = tmp / f"{name}.png"
    hlp_plot.save_figure(fig, p, "png", 150)
    hlp_plot.close_figure(fig)
    ok_render = ok_render and p.exists() and p.stat().st_size > 5000
    sizes[name] = p.stat().st_size
    hashes[name] = hashlib.sha3_256(p.read_bytes()).hexdigest()
check("B1 every builder renders a non-trivial PNG", ok_render,
      f"sizes: {sizes}")

# the 'pdf,png' pair: both files for one name
fig = PLOT_BUILDERS["parity"](d, "VERIFY_PLOT")
hlp_plot.save_figure(fig, tmp / "parity.pdf", "pdf")
hlp_plot.save_figure(fig, tmp / "parity.png2", "png", 150)
hlp_plot.close_figure(fig)
check("B2 the pdf/png pair: both outputs written, distinct magic",
      (tmp / "parity.pdf").read_bytes()[:4] == b"%PDF"
      and (tmp / "parity.png2").read_bytes()[:4] == b"\x89PNG")

# determinism: a second render of the whole set hashes equal
hashes2 = {}
for name in PLOT_NAMES:
    fig = PLOT_BUILDERS[name](d, "VERIFY_PLOT")
    p = tmp / f"{name}.png2"
    hlp_plot.save_figure(fig, p, "png", 150)
    hlp_plot.close_figure(fig)
    hashes2[name] = hashlib.sha3_256(p.read_bytes()).hexdigest()
check("B3 the rendering is byte-deterministic (the seeded jitter)",
      hashes2 == hashes)

# the unit guards
check("B4 the jitter bound (R semantics: +/-amount*range/2)",
      float(np.max(np.abs(jitter(np.random.default_rng(42),
                                 np.linspace(-10, 10, 500), 0.5)
                   - np.linspace(-10, 10, 500)))) <= 5.0)
check("B5 the KDE guard: zero variance -> flat zero",
      np.all(_kde_curve(np.full(50, 3.0), np.linspace(-1, 1, 16)) == 0.0))
check("B6 the EGV bins: the even step-2 grid",
      np.all(egv_bins(np.array([0.6, 3.2, -2.9]))[0] % 2 == 0))

# ---------------------------------------------------------------- C: the pilot semantics
from reversi.lm.hlp_config_schemas import PlotConfig
from pydantic import ValidationError

pc = PlotConfig()
check("C1 the defaults: enable, the PNG-DEFAULT ruling, the relative "
      "dir, the EMPTY whitelist (the no-op pilot)",
      pc.enable is True and pc.format == "png" and pc.dpi == 150
      and pc.dir_name == Path("plots") and pc.plots == [])
check("C2 the format pair normalizes (whitespace away, order kept)",
      PlotConfig(format="png, pdf").format == "png,pdf"
      and PlotConfig(format="pdf,png").format == "pdf,png")
bad = 0
for fmt in ("jpg", "pdf,", "", "png,png"):
    try:
        PlotConfig(format=fmt)
    except ValidationError:
        bad += 1
check("C3 the bad formats are all rejected (4/4)", bad == 4)
try:
    PlotConfig(plots=["nope"])
    check("C4 the unknown plot name fails fast", False)
except ValidationError:
    check("C4 the unknown plot name fails fast", True)
check("C5 the whitelist dedupes, order preserved",
      PlotConfig(plots=["parity", "resid_qq", "parity"]).plots
      == ["parity", "resid_qq"])
check("C6 the absolute dir_name stays absolute (the D-149 ruling)",
      PlotConfig(dir_name="/tmp/elsewhere").dir_name.is_absolute())

print(f"\n{len(failures)} failure(s)")
sys.exit(1 if failures else 0)
