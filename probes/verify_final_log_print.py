#!/usr/bin/env python3
#
# verify_final_log_print.py
#
# Probe pinning the FINAL_LOG_PRINT level (the 19th level):
# the worker (src/reversi/lm/wrk_final_log_print.py) + the hlp it
# calls (hlp_final_log_print_write_log, the file writer) + the
# machine support (the format_event_log render + the context
# injection, the live-line single source of truth) + the config
# gate (the LMConfig.log_file_name, default None).
#
# Tiers:
#   A  the module structure: the worker factory + the skip branch,
#      the hlp writer, the config field, the machine method +
#      injection, the registration (last in logistic_model)
#   B  the behavior on a synthetic 2-worker machine (no DB): the
#      disabled no-op (no file), the enabled write (the file is
#      the buffer at the write moment — the write-asymmetry
#      invariant, the live-line format cross-checked against an
#      independent re-derivation, the maximum-relevance replay)
#
# The a/b/c rule (probe_rules §3): the factory name, the no-op log,
# the file existence, the subdir path and the down no-op all live in
# test_wrk_final_log_print.py — they are NOT repeated here. What
# stays: the cross-file structure facts (A), the write-asymmetry
# invariant + the format cross-check (B — the file content vs the
# buffer, independently re-derived).
#
# House convention: writes only under build/tmp, self-cleans via
# atexit; exit code 1 on any mismatch.

import atexit
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from reversi.tools.state_machine import (  # noqa: E402
    Context, Relevance, StateMachine, Verbosity, Worker)
from reversi.lm.wrk_final_log_print import wrk_final_log_print  # noqa: E402

TMP = ROOT / "build" / "tmp" / "verify_final_log_print"
TMP.mkdir(parents=True, exist_ok=True)
atexit.register(shutil.rmtree, TMP, ignore_errors=True)

fails = 0


def check(label, cond):
    global fails
    if cond:
        print(f"[ok  ] {label}")
    else:
        fails += 1
        print(f"[FAIL] {label}")


# ---------------------------------------------------------------- A tier
wk = (ROOT / "src" / "reversi" / "lm" / "wrk_final_log_print.py").read_text()
check("A1  the worker factory: Worker('FINAL_LOG_PRINT', _up, _down)",
      'Worker("FINAL_LOG_PRINT", _up, _down)' in wk
      and "__all__ = ['wrk_final_log_print']" in wk)
check("A2  the config gate: the absent log_file_name is a no-op (the file NOT generated)",
      "if ctx.cfg.log_file_name is None:" in wk
      and "FINAL_LOG_PRINT skipped: no log_file_name." in wk)
hlp = (ROOT / "src" / "reversi" / "lm" / "hlp_final_log_print.py").read_text()
check("A3  the hlp writer: the base_dir join + the buffer write",
      "def hlp_final_log_print_write_log" in hlp
      and "Path(ctx.cfg.base_dir) / ctx.cfg.log_file_name" in hlp
      and "ctx.format_event_log()" in hlp)
cfg = (ROOT / "src" / "reversi" / "lm" / "hlp_config_schemas.py").read_text()
check("A4  the config field: LMConfig.log_file_name, default None",
      "log_file_name: str | None = Field(" in cfg and "default=None" in cfg)
sm_src = (ROOT / "src" / "reversi" / "tools" / "state_machine.py").read_text()
check("A5  the machine render + the context injection (the format_event_log accessor)",
      "def format_event_log(self) -> str:" in sm_src
      and "self.context.format_event_log = self.format_event_log" in sm_src)
lm_src = (ROOT / "src" / "reversi" / "lm" / "logistic_model.py").read_text()
check("A6  the registration: wrk_final_log_print() last in the worker list",
      "wrk_final_log_print()" in lm_src
      and lm_src.rindex("wrk_final_log_print()") > lm_src.rindex("wrk_plot()"))

# ---------------------------------------------------------------- B tier
PRE = [(Relevance.TRACE, "probe trace"), (Relevance.DEBUG, "probe debug"),
       (Relevance.INFO, "probe info"), (Relevance.WARN, "probe warn")]


def _machine(base_dir, log_file_name):
    """A synthetic 2-worker machine (CREATED + FINAL_LOG_PRINT),
    verbosity VERY_LOW (nothing but ERROR prints): the event buffer
    is the maximum-relevance capture, the file the replay."""
    ctx = Context()
    ctx.cfg = SimpleNamespace(base_dir=base_dir,
                              log_file_name=log_file_name)
    return StateMachine([Worker("CREATED", lambda c: None, lambda c: None),
                         wrk_final_log_print()],
                        ctx, Verbosity.VERY_LOW)


# B1 the disabled no-op: no file (the config entry absent).
sm = _machine(TMP / "b1", None)
for rel, msg in PRE:
    sm.log_event(rel, msg)
sm.move_to_last()
check("B1  the disabled no-op: no file, the 'skipped' log line",
      not list((TMP / "b1").glob("*"))
      and any("FINAL_LOG_PRINT skipped: no log_file_name." == e.message
              for e in sm.logs))

# B2 the enabled write: the file is the buffer at the write moment.
sm = _machine(TMP / "b2", "full.log")
for rel, msg in PRE:
    sm.log_event(rel, msg)
sm.move_to_last()
f = TMP / "b2" / "full.log"
check("B2  the enabled write: the file exists under base_dir", f.is_file())
lines = f.read_text(encoding="utf-8").splitlines() if f.is_file() else []
check("B2  the write-asymmetry: the file carries its own 'Starting' line, not the 'Completed' line "
      "(nor the 'full log written' confirmation — both post-write)",
      any("Starting worker FINAL_LOG_PRINT, UP step" in ln for ln in lines)
      and not any("Completed UP step for FINAL_LOG_PRINT" in ln
                  for ln in lines)
      and not any("full log written" in ln for ln in lines))
check("B2  the line count == the buffer at the write (the final buffer minus the two trailing post-write lines)",
      len(lines) == len(sm.logs) - 2)

# B3 the format cross-check: an independently re-derived live line
# (from the entry, not from format_event_log) matches the file line.
entry = [e for e in sm.logs if e.message == "probe warn"][0]
expected = (f"[{entry.time.strftime('%Y-%m-%d %H:%M:%S')} UTC] "
            f"[{entry.step:02}][{entry.worker_name:15}] "
            f"[{entry.relevance.name:>5}:{Verbosity.VERY_LOW.name:>8}] "
            f"{entry.message}")
check("B3  the live-line format (the independent re-derivation matches the file line)",
      expected in lines)

# B4 the maximum-relevance replay: every pre-logged relevance is in
# the file although the machine's verbosity (VERY_LOW) prints
# nothing.
check("B4  the maximum-relevance replay: all 4 pre-logged relevances in the file",
      all(msg in "\n".join(lines) for _rel, msg in PRE))

# ---------------------------------------------------------------- report
print(f"\n{fails} mismatch(es)", file=sys.stderr)
sys.exit(1 if fails else 0)
