# ARCHIVED — D-106 investigation one-off (session 27/28, the O1 orbit-invariance
# study and the D-104 O1 w_dense investigation), 2026-09-04. Purpose served:
# the O1 pattern and the D-105 w_dense fix are closed and pinned by the
# tests + the module probes; nothing permanent lives in this script.
# (archived at D-106 step 3, the notes/docs hygiene migration)
import contextlib, hashlib, io, re, tempfile
from pathlib import Path
from twolm.logistic_model import LogisticModel
from twolm.state_machine import Verbosity
from twolm.test.paths import WORKSPACE_ROOT, CUSTOM_TMP_BASE

CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE)) as tmp:
    tmp = Path(tmp)
    cfg = str(WORKSPACE_ROOT / "src" / "twolm" / "test" / "data" / "rlm_01.json")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        m = LogisticModel(cfg, verbosity=Verbosity.HIGH, base_dir_override=tmp)
        m.move_to_step("ANALYTICS")
    out = buf.getvalue()
    ctx = m.context
    print("step:", m.current_step, m.current_worker_name)
    print("train_metrics:", ctx.train_metrics)
    print("cache hits:", out.count("Cache successfully loaded and validated"))
    rpt = tmp / "model_analytics_report.txt"
    print("report exists:", rpt.exists(), "size:", rpt.stat().st_size if rpt.exists() else "-")
    content = rpt.read_text()
    masked = re.sub(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", "DATE", content)
    print("file hash (date-masked):", hashlib.sha3_256(masked.encode()).hexdigest())
    for marker in ["MOBILITY FEATURE: LMC (fid=1)",
                   "PATTERN FEATURE: DIAG3 (fid=2)",
                   "PATTERN FEATURE: CORE (fid=3)",
                   "Table rows omitted"]:
        print(f"{marker!r} ->", content.count(marker))
    # the LMC table: how many data rows?
    lmc_block = content.split("MOBILITY FEATURE: LMC (fid=1)")[1].split("PATTERN FEATURES DETAILS")[0]
    rows = [l for l in lmc_block.splitlines() if re.match(r"\s+\d+ \| ", l)]
    print("LMC table rows:", len(rows))
    print("first row:", rows[0].strip() if rows else None)
    print("last row:", rows[-1].strip() if rows else None)
    diag_block = content.split("PATTERN FEATURE: DIAG3 (fid=2)")[1].split("PATTERN FEATURE: CORE")[0]
    drows = [l for l in diag_block.splitlines() if re.match(r"\s+\d+ \| ", l)]
    print("DIAG3 table rows:", len(drows))
    core_block = content.split("PATTERN FEATURE: CORE (fid=3)")[1]
    print("CORE omitted line present:", "Table rows omitted" in core_block)
    gap = [l for l in out.splitlines() if "Generalization Gap" in l]
    print("gap line:", gap)
    opt = [l for l in out.splitlines() if "Optimization Status" in l]
    print("opt line:", opt)
