# latex_rules.md — rules for the LaTeX book (the latex/ zone)

Prescriptive. Follow when creating, building, or editing the book in latex/. Rules in English; the book itself is in
Italian (G6).

Companions: notes/overview.md (the Index line + the LATEX campaign bullet), notes/decisions.md (the D-576 governance
milestone), notes/naming.md (the domain vocabulary the book explains).

## 1. What the zone is (G1)

- latex/ (workspace root, a top-level zone) — the authored BOOK. It is a third kind of content, NOT the docs/ mirror
  zone (R-330): docs/ mirrors the code; latex/ is a publication. The .tex sources, the Makefile, and the tools are
  tracked in git.
- Every .tex source carries the standard 26-line GPL header (R-595, the %-comment variant); the guard
  wsutils/license\_header\_audit.py checks them at the pre-commit gate. Third-party .sty packages (e.g.
  othelloboard.sty, LPPL) are exempt and keep their own header.
- It is a BOOK (~200 pages), not a paper. A 10-page paper may be distilled from it later, only if the results warrant.
  Content scope: the pattern theory, the board, the D8, the logistic model's mathematical structure, the pipeline
  structure, the software user guide, the pipeline-step explanations, a set of examples, and the results.

## 2. The build pipeline (G2)

- The latex/Makefile is the build door; latexmk drives the LaTeX; the engine is pdflatex ([utf8]inputenc + [T1]fontenc).
  Make is a system tool (not a Python dependency — R-590 untouched); the same Makefile scales to the ANSI-C builds as
  they land.
- `make latex` — the full book build.
- `make latex CH=NNN` — a fast build of ONE chapter (see §3).
- `make latex-warn` — summarize the actionable warnings from the last build's .log (overfull/underfull \hbox, Rerun,
  undefined references, LaTeX warnings).
- `make clean` — remove all build artifacts.

## 3. The document structure + fast compilation (G3)

- `documentclass{book}`; the master latex/main.tex holds the preamble, the TOC, and the `\include` list.
- Chapters are `\include` units (not `\input`): each keeps its own .aux cache and is a self-contained compilation unit.
- Fast iteration: `\includeonly{<chapter>}` typesets ONLY that chapter (the others are skipped, their pagination read
  from cache) — editing one chapter compiles in seconds, not the whole book. The Makefile exposes it as
  `make latex CH=NNN`.
- Naming: `reversi_NNN_slug.tex` — 3 digits, step 20 (020, 040, 060, … 980 = 49 slots; 19 free between each pair for
  inserts; 000/010 reserved for front-matter). Lexicographic = logical order; the scheme is flat (the `\part` lives in
  the content, not the filename).
- The Makefile glob-resolves `CH=NNN` to the full `reversi_NNN_slug` base name, because `\includeonly` matches the FULL
  file base name, not the bare number (the spike's finding).
- Two-level files: a chapter is the `\include` unit; a large chapter `\input`s its sections internally, so files stay
  appropriately sized without losing the chapter-level fast-compile unit.
- The FIRST full build is slow (it populates the .aux cache); after that, per-chapter iteration is fast.

## 4. Build artifacts (G4)

- Everything — the intermediates (.aux/.log/.toc/.out/.fls/.fdb\_latexmk) AND the final .pdf — is gitignored under
  latex/build/ (R-350); the Makefile also gitignores the generated includeonly.tex.
- The PDF is committed ONLY at a deliberate publication moment, together with a SW release (the v1).

## 5. The authoring tools (G8)

The "sensors" for a long writing campaign (the first two are Makefile targets; the linter is a direct script):
- `make spell` — Italian spellcheck, run **before every checkin** (a gate). tex2txt.py strips the LaTeX markup
  (comments, environments, structural commands, [options]; keeps the prose and the {arg} of text commands) →
  `aspell list -d it` → the flagged words are filtered against dict.txt (the personal domain dictionary) with
  `grep -vFx`. Exits non-zero if any word survives. Domain terms (board, pattern, bitboard, …) go in dict.txt, not in
  the filter.
- `make pdf2png` — renders the built PDF to per-page PNGs (pdftoppm) under build/pages/, which Nia inspects VISUALLY
  (the same path as the pipeline PLOTs). It catches what a green build hides — layout / pagination / localization
  defects. It already earned its keep in the spike (it exposed the English "CONTENTS / Chapter" headings).
- `wsutils/latex_lint.py` — a context-aware linter and SAFE auto-fixer for the .tex sources, run over
  `latex/reversi_*.tex`. It catches the recurring, mostly SILENT pitfalls the build does not stop on: an
  ASCII-apostrophe accent in prose (where the Unicode vowel belongs), a non-ASCII byte in a lstlisting, an unescaped
  special (\_ ^ $ …) in \texttt, a \bar with a following subscript (the sfmath mis-position), a dangling
  cross-reference, a stray \usepackage in a chapter, an unterminated \[ … \], and an undefined listings language. Its
  core is a context scanner (prose / math / code / comment / inlinecode) — that context awareness is what makes the
  accent check robust (it leaves the math primes and the code quotes alone). `--write` applies only the four safe fixes
  (accent, code-ascii, texttt, bar→overline); the structural checks are report-only.

## 6. Localization (G6 + a G8 consequence)

- The book is written in ITALIAN, single source. English is a future, separate campaign.
- The preamble MUST carry `\usepackage[italian]{babel}` so the section headings are Italian (Capitolo / Indice), not the
  book-class English defaults (Chapter / Contents).

## 7. Tracking & campaign shape (G5, G7)

- This file (notes/latex\_rules.md) governs the zone (the R-060 one-domain-one-file pattern); the overview Index carries
  its line.
- The LATEX and FEATURE-SET campaigns run interleaved: LATEX is the governance-bound one (started first); FEATURE-SET
  launches once LATEX is underway; the book's results section fills in as FEATURE-SET lands.
- Phase order: (1) GOVERNANCE (this file + the zone — D-576) → (2) CONTENT (the book's parts / chapters / sections,
  re-homing the legacy 9-chapter draft) → (3) WRITING (the chapters).
