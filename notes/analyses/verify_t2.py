# ARCHIVED — T2 test-harness one-off (the print-on-failure behavior of
# test_pattern.TestPatternSetComputePrincipalIndexes.test_one_record,
# both paths verified), 2026-09-04. Purpose served: the T2 fix is in
# test_pattern.py and pinned by the test's own run; no module
# invariant lives in this script. Classification b2 (D-106 step 1,
# scratch/classification.md). Results quoted in notes/decisions.md
# (the T2 decision, the pattern-campaign worklist) and
# notes/log_000.md (the campaign session).
#!/usr/bin/env python
"""Verify T2's print-on-failure behavior of test_one_record (read-only)."""
import sys, io, contextlib
sys.path.insert(0, "/home/rcrr/base/prj/dsh/src")
import twolm.test.test_pattern as tp

CLS = tp.TestPatternSetComputePrincipalIndexes

# 1) Failure path: force the assertion to fail; expect output + re-raise.
t = CLS()
t.setUp()
real = tp.nptest.assert_array_equal
def fake(*a, **k):
    raise AssertionError("simulated failure")
tp.nptest.assert_array_equal = fake
buf = io.StringIO()
raised = None
try:
    with contextlib.redirect_stdout(buf):
        t.test_one_record()
except AssertionError as e:
    raised = str(e)
finally:
    tp.nptest.assert_array_equal = real
out = buf.getvalue()
print("FAIL PATH  raised:", raised is not None, "|", raised)
print("FAIL PATH  stdout bytes:", len(out))
print(out)

# 2) Success path: real assertion; expect NO output.
t2 = CLS()
t2.setUp()
buf2 = io.StringIO()
with contextlib.redirect_stdout(buf2):
    t2.test_one_record()
print("OK PATH    stdout bytes:", len(buf2.getvalue()), "(expect 0)")
print("RESULT:", "PASS" if (raised is not None and len(out) > 0 and len(buf2.getvalue()) == 0) else "FAIL")
