#
# verify_logistic_model.py — independent verification probe
#
# Re-derives the key facts about logistic_model.LogisticModel/RLMContext
# and the state_machine integration without trusting the module's own
# tests. Artifacts: build/tmp only (D-065), removed afterwards.
#
# Re-pinned in session 22 (D-081) to the post-D-074/D-075/D-076/D-081
# state: the session-21 original pinned the pre-D-074 state (legacy
# _for_next_level names, the latent-Union get_type_hints NameError, the
# FileNotFoundError-for-a-directory behaviour, the 1-worker V9
# boundaries) and was never re-pinned after the fix batches. Now:
# D-074 R1 (the *_for_current_level lambda fields), R2 (str | None
# annotations, get_type_hints succeeds), R3 (@validate_call on __init__),
# M3 (IsADirectoryError for a directory as config), D-076 (CONFIG active,
# the gate split lets the CONFIG worker's pydantic ValidationError
# propagate), D-081 (FEATURES active — 4 workers).
#
# Re-pinned in session 23 (D-083) to the post-a323e0f state: INDEXES
# enabled (the lm_worker_indexes() import + worker-list entry
# uncommented) — 5 active levels (CREATED sentinel, CONFIG, POSITIONS,
# FEATURES, INDEXES). V10 unchanged: RLMContext already declared the
# rlm_indexes / rlm_indexes_checksum blackboard fields at first import
# (8 *_checksum fields, no features_checksum).
#
# Re-pinned in session 27 (D-097) to the post-e31c061 state: GENERATE
# enabled (the lm_worker_generate() import + worker-list entry
# uncommented) — 11 active levels. V3c re-pinned 10 -> 11; the other
# checks are unchanged.
#
# Re-pinned in session 28 (D-099) to the post-ede2efe state:
# VLD_POSITIONS enabled (the lm_worker_vld_positions() import +
# worker-list entry uncommented) — 12 active levels. V3c re-pinned
# 11 -> 12; the other checks are unchanged.
#
# Re-pinned in session 28 (D-101 analysis, pre-D-102) to the post-536eadc
# state: VALIDATE enabled (the lm_worker_validate() import + worker-list
# entry uncommented) — 13 active levels. V3c re-pinned 12 -> 13; the
# other checks are unchanged.
#
# Re-pinned in session 28 (D-103 analysis, pre-campaign) to the post-
# 96dacb5 state: ANALYTICS enabled (the lm_worker_analytics() import +
# worker-list entry uncommented) — 14 active levels. V3c re-pinned
# 13 -> 14.
# fe506c6 state (D-104, 2026-09-02): SAVE enabled (the lm_worker_save()
# import L54 + worker-list entry L221 uncommented) — 15 active levels,
# PIPELINE COMPLETE (0 commented imports / entries). V3c re-pinned
# 14 -> 15; the other checks are unchanged.
#
import contextlib
import dataclasses
import io
import shutil
import sys
import typing
from pathlib import Path

TMP = Path(__file__).resolve().parents[1] / "build" / "tmp" / "vlog_probe"
TMP.mkdir(parents=True, exist_ok=True)

failures = []

def check(name, ok, detail=""):
    tag = "ok" if ok else "FAIL"
    print(f"[{tag}] {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(name)

# --- V1: RLMContext dataclass shape --------------------------------------
from twolm.logistic_model import RLMContext, LogisticModel
from twolm.base_model import BaseModel
from twolm.state_machine import Verbosity, StateMachine, Context, Worker

check("V1a is_dataclass", dataclasses.is_dataclass(RLMContext))
fields = {f.name: f for f in dataclasses.fields(RLMContext)}
check("V1b context is plain (non-dataclass) base",
      not dataclasses.is_dataclass(Context))
check("V1c config_file_path field no default",
      fields["config_file_path"].default is dataclasses.MISSING)
check("V1d use_cache field default None",
      fields["use_cache"].default is None)
check("V1e legacy _for_next_level names GONE (D-074 R1)",
      "get_cache_file_path_for_next_level" not in fields
      and "get_cache_file_full_path_for_next_level" not in fields)
check("V1f *_for_current_level are dataclass fields now (lambda defaults = pre-injection fallback, D-074 R1)",
      "get_cache_file_path_for_current_level" in fields
      and "get_cache_file_full_path_for_current_level" in fields)
check("V1g log_event default is a lambda",
      callable(fields["log_event"].default)
      and type(fields["log_event"].default) is type(lambda: None))

# --- V8: annotations resolve (D-074 R2) ----------------------------------
try:
    typing.get_type_hints(RLMContext)
    check("V8 get_type_hints succeeds (str | None annotations, no latent Union NameError)", True)
except Exception as e:
    check("V8 get_type_hints succeeds (str | None annotations, no latent Union NameError)", False,
          f"{type(e).__name__}: {e}")

# --- V6/V7: path-check helpers -------------------------------------------
from twolm.logistic_model import _check_config_file_path, _check_base_dir_override

cfg_file = TMP / "dummy.json"
cfg_file.write_text("{}")
a_dir = TMP
a_file = cfg_file

check("V6a valid str -> Path", _check_config_file_path(str(cfg_file)) == cfg_file)
check("V6b valid Path -> Path", _check_config_file_path(cfg_file) == cfg_file)
for bad, exc in [(123, TypeError), (a_dir, IsADirectoryError), (TMP / "missing.json", FileNotFoundError)]:
    try:
        _check_config_file_path(bad)
        check(f"V6 raises for {bad!r}", False, "no exception")
    except exc as e:
        check(f"V6 raises {exc.__name__} for {type(bad).__name__}", True, str(e))
    except Exception as e:
        check(f"V6 raises {exc.__name__} for {type(bad).__name__}", False,
              f"got {type(e).__name__}: {e}")

from pydantic import ValidationError
try:
    LogisticModel(123)
    check("V6f @validate_call on __init__: int -> ValidationError (D-074 R3)", False, "no exception")
except ValidationError:
    check("V6f @validate_call on __init__: int -> ValidationError (D-074 R3)", True)
except Exception as e:
    check("V6f @validate_call on __init__: int -> ValidationError (D-074 R3)", False,
          f"got {type(e).__name__}: {e}")

check("V7a valid dir str -> Path", _check_base_dir_override(str(a_dir)) == a_dir)
check("V7b valid dir Path -> Path", _check_base_dir_override(a_dir) == a_dir)
for bad, exc in [(123, TypeError), (a_file, NotADirectoryError)]:
    try:
        _check_base_dir_override(bad)
        check(f"V7 raises for {bad!r}", False, "no exception")
    except exc as e:
        check(f"V7 raises {exc.__name__} for {type(bad).__name__}", True, str(e))
    except Exception as e:
        check(f"V7 raises {exc.__name__} for {type(bad).__name__}", False,
              f"got {type(e).__name__}: {e}")

# --- V2-V5: model construction + facade ----------------------------------
model = LogisticModel(config_file_path=str(cfg_file))
ctx = model.context

check("V2a model.context is model.sm.context (identity)",
      ctx is model.sm.context)
check("V2b model.sm is a StateMachine", isinstance(model.sm, StateMachine))
check("V2c verbosity default STANDARD",
      model.verbosity is Verbosity.STANDARD)
model.verbosity = Verbosity.NONE
check("V2d verbosity setter delegates", model.sm.verbosity is Verbosity.NONE)
model.verbosity = Verbosity.STANDARD

check("V3a current_step 0", model.current_step == 0)
check("V3b current_worker_name CREATED", model.current_worker_name == "CREATED")
check("V3c 15 active levels (D-104: SAVE enabled, fe506c6 — complete)",
      [w.name for w in model.sm.workers]
      == ["CREATED", "CONFIG", "POSITIONS", "FEATURES", "INDEXES",
          "WMAPS", "DESIGN_MTR", "ZED", "GRADIENT", "OPTIMIZE",
          "GENERATE", "VLD_POSITIONS", "VALIDATE", "ANALYTICS", "SAVE"])
# V3d (D-106 hub centralization): the module probes' pipeline-state
# copies move to the hub — the source-level completeness fact.
lm_src = (Path(__file__).resolve().parents[1]
          / "src" / "twolm" / "logistic_model.py").read_text()
check("V3d 0 commented worker imports / entries in logistic_model.py "
      "(D-104: pipeline complete)",
      not any(ln.strip().startswith("#from twolm.lm_worker_")
              or (ln.lstrip().startswith("#") and "lm_worker_" in ln
                  and "()" in ln)
              for ln in lm_src.splitlines()))

# the D-074 state, live:
check("V4a legacy _for_next_level gone from the live context (D-074 R1)",
      not hasattr(ctx, "get_cache_file_path_for_next_level")
      and not hasattr(ctx, "get_cache_file_full_path_for_next_level"))
cur = ctx.get_cache_file_path_for_current_level
check("V4b injected _for_current_level is a real closure",
      callable(cur) and cur.__name__ == "_get_cache_file_path")
full = ctx.get_cache_file_full_path_for_current_level
check("V4c injected _for_current_level full-path closure",
      callable(full) and full.__name__ == "_get_cache_file_full_path")
check("V4d log_event injected (bound method, not the lambda default)",
      ctx.log_event.__class__.__name__ == "method")

# sentinels (V5): direct call must raise; log_event no-op path pre-injection
from twolm.logistic_model import _created_up, _created_down
for fn, msg in [(_created_up, "up"), (_created_down, "down")]:
    try:
        fn(ctx)
        check(f"V5 sentinel {msg} raises RuntimeError", False, "no exception")
    except RuntimeError as e:
        check(f"V5 sentinel {msg} raises RuntimeError", True, str(e))
bare = RLMContext(config_file_path=cfg_file)
try:
    _created_up(bare)
    check("V5b bare-context sentinel raises RuntimeError", False, "no exception")
except RuntimeError as e:
    check("V5b bare-context sentinel raises RuntimeError", True, str(e))
except Exception as e:
    check("V5b bare-context sentinel raises RuntimeError", False,
          f"no-op log crashed instead: {type(e).__name__}: {e}")

# --- V9: 5-worker machine boundaries (re-pinned D-083) -------------------
# With CONFIG active (D-076) and the gate split, the empty {} config makes
# the CONFIG worker raise its pydantic ValidationError, which propagates
# (no conversion to the gate's TypeError); a failed move leaves
# current_step at the failed step (D-060). Fresh model per boundary.
# (The {} config fails at CONFIG — the later boundaries are
# unreachable, the 11-worker count is pinned by V3c.)
for target, label in [(1, "int 1"), ("POSITIONS", "str POSITIONS"), ("move_to_last", "move_to_last")]:
    m = LogisticModel(str(cfg_file))
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            if target == "move_to_last":
                m.move_to_last()
            else:
                m.move_to_step(target)
        check(f"V9 {label} rejects (empty config)", False, "no exception")
    except ValidationError as e:
        check(f"V9 {label} -> pydantic ValidationError (CONFIG), step stays at 1",
              m.current_step == 1)
    except Exception as e:
        check(f"V9 {label} -> pydantic ValidationError (CONFIG), step stays at 1", False,
              f"got {type(e).__name__}: {e}; step {m.current_step}")

# --- V10: RLMContext artifact inventory (doc support) --------------------
check("V10 checksum-typed fields: 8, and NO features_checksum (feature_set is an in-memory derivation, no cache file)",
      sum(1 for n in fields if n.endswith("_checksum")) == 8
      and "features_checksum" not in fields,
      str([n for n in fields if n.endswith("_checksum")]))

# --- cleanup + summary ----------------------------------------------------
shutil.rmtree(TMP, ignore_errors=True)
print()
if failures:
    print(f"{len(failures)} FAILURES: {failures}")
    sys.exit(1)
print("ALL CHECKS PASSED")
