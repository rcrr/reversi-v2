# The LATEX campaign — build system for the book (the latex/ zone).
# Governed by notes/latex_rules.md (G1-G8).
#
#   make latex [CH=NNN]   full build, or fast build of ONE chapter (\includeonly)
#   make spell            Italian spellcheck (tex2txt | aspell -d it + personal dict) — pre-checkin gate
#   make pdf2png          render the PDF to per-page PNGs (for visual layout inspection)
#   make latex-warn       summarize the actionable warnings from the last build's .log
#   make clean            remove all build artifacts

MAIN := main
OUT  := build
CH   ?=
PY   := python3
DICT := dict.txt

.PHONY: latex spell pdf2png latex-warn clean

# `make latex`        -> full build (all chapters; populates the .aux cache)
# `make latex CH=040` -> fast build of ONE chapter only (\includeonly).
# CH=NNN is glob-resolved to the full chapter base name (reversi_NNN_slug),
# because \includeonly matches the FULL file base name, not the bare number.
latex:
	@mkdir -p $(OUT)
	@if [ -n "$(CH)" ]; then \
		f=$(wildcard reversi_$(CH)_*.tex); \
		[ -n "$$f" ] || { echo "ERROR: no chapter matching reversi_$(CH)_*.tex"; exit 1; }; \
		base=$$(basename $$f .tex); \
		echo "fast-compile: \includeonly{$$base}"; \
		echo "\includeonly{$$base}" > includeonly.tex; \
	else \
		echo -n "" > includeonly.tex; \
	fi
	latexmk -pdf -interaction=nonstopmode -outdir=$(OUT) $(MAIN).tex

# Italian spellcheck: strip the LaTeX markup (tex2txt.py), then aspell -d it with the
# personal domain dictionary (dict.txt, lowercase entries, matched case-insensitively).
# Exits non-zero if any word is flagged.
spell:
	@echo "=== Italian spellcheck (aspell -d it + $(DICT)) over the .tex prose ==="
	@rc=0; for f in $(MAIN).tex reversi_*.tex; do \
		bad=$$($(PY) tex2txt.py < $$f | aspell list -d it 2>/dev/null | grep -vFxi -f $(DICT)); \
		if [ -n "$$bad" ]; then echo "-- $$f --"; echo "$$bad"; rc=1; fi; \
	done; \
	[ $$rc -eq 0 ] && echo "(no misspellings found)"; exit $$rc

# Render the built PDF to per-page PNGs under build/pages/ (for visual inspection).
pdf2png:
	@mkdir -p $(OUT)/pages
	pdftoppm -png -r 100 $(OUT)/$(MAIN).pdf $(OUT)/pages/page
	@echo "rendered:"; ls -1 $(OUT)/pages/

# Summarize the actionable warnings from the last build's .log.
latex-warn:
	@echo "=== overfull / underfull / rerun / undefined / warnings ($(OUT)/$(MAIN).log) ==="
	@grep -nE 'Overfull \\\\[hB]box|Underfull \\\\[hB]box|Rerun|undefined|LaTeX Warning' $(OUT)/$(MAIN).log | head -40 || echo "(none)"

clean:
	latexmk -C $(MAIN).tex
	rm -rf $(OUT) includeonly.tex
