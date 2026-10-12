# Session journal — volume 005 (sessions 102–...)

Format rules: notes/log_rules.md (rigid — follow when editing this file).

## 2026-10-11 — session 102 (D-515/D-516 — re-pin del parity PNG golden post-upgrade Ubuntu/Python + la rimozione della bullet-campagna dai Next steps, rotazione journal vol 004 → 005)

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
- D-516 (rimozione della bullet-campagna dai Next steps dell'overview): Roberto segnala l'item "Verify the
  format of the lm and test sources" "completamente fuori norma" — 70 righe / ~8,4 KB contro le 1-2 righe
  delle altre, piena di riferimenti storici D-NNN, e non più vera. Archeologia git: nata il 29-09 (D-337)
  come item aperto di una riga del to-do a 6 punti; le rules rigide dell'overview nate lo stesso giorno
  (D-343: "OPEN items only, no Done bullets" + "no bullet-per-campaign, lo stato di campagna esce
  dall'overview a campagna finita"); dal primo wave (D-476, session 99) ogni wave-commit ci ha aggiunto il
  pass del giorno (45 commit fino a D-512) — la bullet era diventata il tabellone di progressi di campagna
  (il journal lo diceva apertamente: "il bullet Next-steps segnato — X COMPLETE"). La guard era rimasta
  green perché notes\_lint controlla la struttura e l'auditore R-210 le tabelle: nessuna check meccanica
  esprime la semantica "no Done bullets". Anti-pattern già sanato il 29-09 (il record closed-ideas fuori
  dal Next-steps) e ricomparso in campagna. Chiamata di Roberto: opzione (A) — rimozione integrale,
  nessuna riscrittura (zero contenuto aperto residuo; lo scope test-sources resta nell'item adiacente) e
  nessun tripwire meccanico ("diventano vincoli antipatici"). I Next steps tornano a bullet corte e
  strettamente aperte. Segnalato per chiamata separata di Roberto: l'item adiacente "Verify the format of
  the WORKER sources" è a sua volta coperto dalla cascata worker completata (D-494..D-512).
- Suite via wrapper R-210 (LONG=1, DB live, per D-516): 1115/0/24 GREEN.
- D-517 (pulizia di formato completa delle fonti TEST, 3 commit parts 1-3): dopo l'audit file-per-file
  (48 agenti: 37 dei 51 file con deviazioni reali — l'item non era fatto) Roberto approva lo sweep.
  Part 1, pilota test\_logistic\_model: header in house shape, split over-120, 9 docstring light,
  3 prose storiche. Part 2, meccanico: le 35 righe over-120 split value-identiche (literal golden per
  concatenazione adiacente; i goldens triple-quoted multilinea di test\_feature in concatenazione
  parentetica, valore byte-identico assertito), 17 file al punto fisso reflow canonico. Part 3,
  semantico: 30 docstring test lunghe compresse alla forma light R-570 (i 4 con info assente dai mirror
  doc mantengono 3-7 righe, per la tolleranza di Roberto), 10 prose storiche rimosse, 6 header
  normalizzati, 12 aperture non imperative corrette. Stato finale: 0 over-120, 0 D-XXX/I-XXX nei .py,
  51/51 al punto fisso reflow; le 2 item Next-steps (TEST + WORKER sources) rimosse dall'overview.
- Suite via wrapper R-210 (LONG=1, DB live, per D-517): 1115/0/24 GREEN.
  il re-review del register e il testo della guard rule R-200 — entrambi a chiamata di Roberto).
- Su richiesta di Roberto: rimossa dall'overview (Current state) la bullet dello stato piattaforma (la narrativa env-drift del re-pin D-515): irrilevante, e la piattaforma è già registrata in Environment.

## 2026-10-12 — session 103 (D-518 — rename dell'API pubblica di hlp\_analytics alla convenzione hlp\_ + fix della docstring del dataclass)

- Su richiesta di Roberto: i 4 nomi pubblici di hlp\_analytics riprefissati col prefisso del modulo
  (hlp\_analytics\_compute\_training\_metrics, hlp\_analytics\_compute\_training\_dense\_metrics,
  hlp\_analytics\_format\_console\_report, hlp\_analytics\_format\_file\_report) e la classe
  TrainingDenseResult → AnalyticsTrainingDenseResult. Aggiornati tutti i consumatori: wrk\_analytics,
  test\_wrk\_analytics, test\_wrk\_plot e il probe verify\_analytics (import/call + il golden
  \_\_all\_\_ del check A1; le prose storiche delle descrizioni dei check restano col nome originale).
- Fix docstring AnalyticsTrainingDenseResult: la descrizione del parametro rn\_y andava a capo lasciando il
  frammento "(one derivation, published by ANALYTICS)" orfano sulla sua riga — ora un wrap pulito su 2 righe.
- I 2 mirror doc (hlp\_analytics.md + wrk\_analytics.md) aggiornati ai nuovi nomi; i 4 .py al punto fisso reflow.
- Suite via wrapper R-210 (LONG=1, DB live, per D-518): 1115/0/24 GREEN. Probe verify\_analytics: all checks
  passed.
- Correzione in avanti sul D-518 (la mia): la docstring del dataclass non era nella forma voluta — il
  parametro rn\_y continuava sulla riga del parametro metrics. Forma canonica house per le liste di
  parametri: ogni entry a +4 dal corpo docstring, il wrapping della descrizione a +8 (il reflow
  src\_reflow è l'enforcer: la forma a 4 spazi della richiesta andava ri-unita in paragrafo fluente).
  Commit part 2 di D-518.
