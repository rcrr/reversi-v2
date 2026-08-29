# Session journal — format rules (rigid)

Applies to all journal volumes `notes/log_000.md`, `log_001.md`, ...
One volume = one file; the session counter never restarts across
volumes.

## Volumes and rotation

- Volumes are named log_000.md, log_001.md, ... (zero-padded).
- A volume holds at most 25 sessions or 2000 lines, whichever comes
  first.
- Rotation happens ONLY at a session boundary: when starting a NEW
  session, if the current volume has reached its cap, close it (set
  the final session number in its H1 range) and start the next
  volume. A volume jump never cuts a session.
- Every volume starts with its H1
  `# Session journal — volume 00N (sessions X–Y)` (Y = "..." while
  the volume is open, filled in at close) and the pointer line
  "Format rules: notes/log_rules.md (rigid — follow when editing
  this file)."
- The most recent volume is the one to append to; closed volumes are
  read-only except factual corrections.

## Session entries

1. One "## YYYY-MM-DD — session N (title)" section per session,
   appended in chronological order. N is a GLOBAL, monotonically
   increasing counter starting at 1: it never resets per day, per
   file, or per volume. The parenthesized title is mandatory.
2. Inside a section: top-level "- " bullets in chronological order.
   A top-level bullet's continuation lines are indented exactly
   2 spaces; sub-bullets are indented exactly 2 spaces ("  - ")
   with their continuations at 4. No other indentation.
3. A bullet states one fact or action and starts with its subject:
   an item id (T-NN, R#, M#), a decision (D-NNN), a file name, or
   "Next:" / "Session closed". Suite results:
   `<total>/<failures>/<skipped> GREEN` where total = unittest's
   "Ran N" (e.g. 193/0/12); when the suite grew:
   `<old> → <new>, GREEN <total>/<f>/<s>`. Placeholder tokens are
   always inline code (backticks): bare `<word>` looks like an HTML
   tag to Markdown renderers.
4. A session Roberto closed ends with a "Session closed (Roberto)."
   bullet; a "Next:" bullet may be last.
5. Completed sessions are immutable except factual corrections.
   One-off 2026-08-29 renumbering: the historical per-day labels
   (08-26 "session 1" → 3; 08-27 "sessions 1-5" → 4-8) were folded
   into the global scheme, and the "Session 11-14" bullets nested in
   the 08-29 feature section are now their own sections 14-17. The
   feature-module entries of 2026-08-28/29 count RUN tests in the
   first slot (e.g. "19/0/1" = 19 run + 1 PERF skip, 20 total);
   they are kept verbatim as history. Older git commit messages keep
   their original labels.
