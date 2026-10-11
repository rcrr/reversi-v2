# Session journal — volume 005 (sessions 102–...)

Format rules: notes/log_rules.md (rigid — follow when editing this file).

## 2026-10-11 — session 102 (D-515 — re-pin del parity PNG golden: il drift di ambiente post-upgrade Ubuntu/Python, rotazione journal vol 004 → 005)

- Roberto: upgrade di Ubuntu + Python, venv ricostruita, librerie aggiornate con pip; la suite completa
  (PERF=1 VVLONG=1, 1115 test) passa tutto tranne `test_parity_png_golden` (hash generato 7939f3b3... ≠ pin
  fdb8162d...). Chiede indagine prima di qualsiasi correzione.
- Indagine (scratch/parity\_investigate.py, zona disposable): il nuovo hash si riproduce ESATTO come nel suo
  run fallito; due render consecutive sono byte-identiche (il determinismo intra-ambiente è intatto, lo
  conferma anche `test_up_all_seven_png`, che passa); i metadati tEXt incorporati nel PNG dichiarano
  "Matplotlib version3.11.2" — la stringa di versione del writer è parte del byte-stream, quindi il solo bump
  di patch 3.11.1 → 3.11.2 cambia l'hash anche a rendering identico; la figura è visivamente identica a quella
  di D-158 (titolo a due righe, sottotitolo SYNTH\_PLOT, assi fissi −64..+64, griglia, retta identità, nuvola
  jitter). Ambiente nuovo: Python 3.14.4, matplotlib 3.11.2, numpy 2.5.4, DejaVu 2.37-8build1 (font del
  01-12-2025). Conclusione: non è un bug — è il documentato env-drift dei goldens di rendering (il pattern
  D-127, già vissuto e risolto a D-158 dopo l'upgrade a 3.11.1).
- D-515 (re-pin del parity PNG golden, su chiamata di Roberto — opzione (a), la più semplice e coerente):
  re-pin a `7939f3b3dceaa959a5683baf3dc4303e6e4df4ba252d19008e1033ba730b03c0` in `test_wrk_plot.py` +
  mirror doc. Il golden resta legato a questo ambiente: al prossimo bump di matplotlib si ripresenterà
  (l'alternativa — un golden ambiente-indipendente, ad es. spurgando i metadati prima dell'hash — resta
  aperta a chiamata di Roberto).
- Rotazione del journal (cap 2000 righe raggiunto: log.md a 3086): il volume 004 si chiude a session 101
  (notes/hist\_log/log\_004.md), il volume 005 apre a questa session 102; l'Index dell'overview segue.
- L'Environment dell'overview registra la nuova piattaforma: Python 3.12.3 → 3.14.4.
- Suite via wrapper R-210 (LONG=1, DB live): 1115/0/24 GREEN.
- Next: gli item aperti restano quelli dell'overview (i 5 tag DURATION, la verifica delle fonti TEST, il
  rework MOBILITY, il README) + il re-review del register e il testo della guard rule R-200 (entrambi a
  chiamata di Roberto).
