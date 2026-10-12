# Session journal — volume 005 (sessions 102–...)

Format rules: notes/log_rules.md (rigid — follow when editing this file).

## 2026-10-11 — session 102 (D-515/D-516 — re-pin del parity PNG golden post-upgrade Ubuntu/Python + la rimozione della bullet-campagna dai Next steps, rotazione journal vol 004 → 005)

- Roberto: upgrade di Ubuntu + Python, venv ricostruita, librerie aggiornate con pip; la suite completa (PERF=1
  VVLONG=1, 1115 test) passa tutto tranne `test_parity_png_golden` (hash generato 7939f3b3... ≠ pin fdb8162d...). Chiede
  indagine prima di qualsiasi correzione.
- Indagine (scratch/parity\_investigate.py, zona disposable): il nuovo hash si riproduce ESATTO come nel suo run
  fallito; due render consecutive sono byte-identiche (il determinismo intra-ambiente è intatto, lo conferma anche
  `test_up_all_seven_png`, che passa); i metadati tEXt incorporati nel PNG dichiarano "Matplotlib version3.11.2" — la
  stringa di versione del writer è parte del byte-stream, quindi il solo bump di patch 3.11.1 → 3.11.2 cambia l'hash
  anche a rendering identico; la figura è visivamente identica a quella di D-158 (titolo a due righe, sottotitolo
  SYNTH\_PLOT, assi fissi −64..+64, griglia, retta identità, nuvola jitter). Ambiente nuovo: Python 3.14.4,
  matplotlib 3.11.2, numpy 2.5.4, DejaVu 2.37-8build1 (font del 01-12-2025). Conclusione: non è un bug — è il
  documentato env-drift dei goldens di rendering (il pattern D-127, già vissuto e risolto a D-158 dopo l'upgrade
  a 3.11.1).
- D-515 (re-pin del parity PNG golden, su chiamata di Roberto — opzione (a), la più semplice e coerente): re-pin a
  `7939f3b3dceaa959a5683baf3dc4303e6e4df4ba252d19008e1033ba730b03c0` in `test_wrk_plot.py` + mirror doc. Il golden resta
  legato a questo ambiente: al prossimo bump di matplotlib si ripresenterà (l'alternativa — un golden
  ambiente-indipendente, ad es. spurgando i metadati prima dell'hash — resta aperta a chiamata di Roberto).
- Rotazione del journal (cap 2000 righe raggiunto: log.md a 3086): il volume 004 si chiude a session 101
  (notes/hist\_log/log\_004.md), il volume 005 apre a questa session 102; l'Index dell'overview segue.
- L'Environment dell'overview registra la nuova piattaforma: Python 3.12.3 → 3.14.4.
- Suite via wrapper R-210 (LONG=1, DB live): 1115/0/24 GREEN.
- D-516 (rimozione della bullet-campagna dai Next steps dell'overview): Roberto segnala l'item "Verify the format of the
  lm and test sources" "completamente fuori norma" — 70 righe / ~8,4 KB contro le 1-2 righe delle altre, piena di
  riferimenti storici D-NNN, e non più vera. Archeologia git: nata il 29-09 (D-337) come item aperto di una riga del
  to-do a 6 punti; le rules rigide dell'overview nate lo stesso giorno (D-343: "OPEN items only, no Done bullets" + "no
  bullet-per-campaign, lo stato di campagna esce dall'overview a campagna finita"); dal primo wave (D-476, session 99)
  ogni wave-commit ci ha aggiunto il pass del giorno (45 commit fino a D-512) — la bullet era diventata il tabellone di
  progressi di campagna (il journal lo diceva apertamente: "il bullet Next-steps segnato — X COMPLETE"). La guard era
  rimasta green perché notes\_lint controlla la struttura e l'auditore R-210 le tabelle: nessuna check meccanica esprime
  la semantica "no Done bullets". Anti-pattern già sanato il 29-09 (il record closed-ideas fuori dal Next-steps) e
  ricomparso in campagna. Chiamata di Roberto: opzione (A) — rimozione integrale, nessuna riscrittura (zero contenuto
  aperto residuo; lo scope test-sources resta nell'item adiacente) e nessun tripwire meccanico ("diventano vincoli
  antipatici"). I Next steps tornano a bullet corte e strettamente aperte. Segnalato per chiamata separata di Roberto:
  l'item adiacente "Verify the format of the WORKER sources" è a sua volta coperto dalla cascata worker completata
  (D-494..D-512).
- Suite via wrapper R-210 (LONG=1, DB live, per D-516): 1115/0/24 GREEN.
- D-517 (pulizia di formato completa delle fonti TEST, 3 commit parts 1-3): dopo l'audit file-per-file (48 agenti: 37
  dei 51 file con deviazioni reali — l'item non era fatto) Roberto approva lo sweep. Part 1, pilota
  test\_logistic\_model: header in house shape, split over-120, 9 docstring light, 3 prose storiche. Part 2, meccanico:
  le 35 righe over-120 split value-identiche (literal golden per concatenazione adiacente; i goldens triple-quoted
  multilinea di test\_feature in concatenazione parentetica, valore byte-identico assertito), 17 file al punto fisso
  reflow canonico. Part 3, semantico: 30 docstring test lunghe compresse alla forma light R-570 (i 4 con info assente
  dai mirror doc mantengono 3-7 righe, per la tolleranza di Roberto), 10 prose storiche rimosse, 6 header normalizzati,
  12 aperture non imperative corrette. Stato finale: 0 over-120, 0 D-XXX/I-XXX nei .py, 51/51 al punto fisso reflow; le
  2 item Next-steps (TEST + WORKER sources) rimosse dall'overview.
- Suite via wrapper R-210 (LONG=1, DB live, per D-517): 1115/0/24 GREEN. il re-review del register e il testo della
  guard rule R-200 — entrambi a chiamata di Roberto).
- Su richiesta di Roberto: rimossa dall'overview (Current state) la bullet dello stato piattaforma (la narrativa
  env-drift del re-pin D-515): irrilevante, e la piattaforma è già registrata in Environment.

## 2026-10-12 — session 103 (D-518 — rename dell'API pubblica di hlp\_analytics alla convenzione hlp\_ + fix della docstring del dataclass)

- Su richiesta di Roberto: i 4 nomi pubblici di hlp\_analytics riprefissati col prefisso del modulo
  (hlp\_analytics\_compute\_training\_metrics, hlp\_analytics\_compute\_training\_dense\_metrics,
  hlp\_analytics\_format\_console\_report, hlp\_analytics\_format\_file\_report) e la classe TrainingDenseResult →
  AnalyticsTrainingDenseResult. Aggiornati tutti i consumatori: wrk\_analytics, test\_wrk\_analytics, test\_wrk\_plot e
  il probe verify\_analytics (import/call + il golden \_\_all\_\_ del check A1; le prose storiche delle descrizioni dei
  check restano col nome originale).
- Fix docstring AnalyticsTrainingDenseResult: la descrizione del parametro rn\_y andava a capo lasciando il frammento
  "(one derivation, published by ANALYTICS)" orfano sulla sua riga — ora un wrap pulito su 2 righe.
- I 2 mirror doc (hlp\_analytics.md + wrk\_analytics.md) aggiornati ai nuovi nomi; i 4 .py al punto fisso reflow.
- Suite via wrapper R-210 (LONG=1, DB live, per D-518): 1115/0/24 GREEN. Probe verify\_analytics: all checks passed.
- Correzione in avanti sul D-518 (la mia): la docstring del dataclass non era nella forma voluta — il parametro rn\_y
  continuava sulla riga del parametro metrics. Forma canonica house per le liste di parametri: ogni entry a +4 dal corpo
  docstring, il wrapping della descrizione a +8 (il reflow src\_reflow è l'enforcer: la forma a 4 spazi della richiesta
  andava ri-unita in paragrafo fluente). Commit part 2 di D-518.

## 2026-10-12 — session 104 (D-519 — rename di compute\_w\_dense a hlp\_generate\_compute\_w\_dense)

- Su richiesta di Roberto: l'ultimo nome pubblico senza prefisso di hlp\_generate rinominato
  hlp\_generate\_compute\_w\_dense (i 4 sibling portavano già il prefisso). Aggiornati: wrk\_generate,
  test\_hlp\_generate (il nome del metodo di test test\_compute\_w\_dense resta — è un'etichetta di test), il probe
  verify\_generate (import/call + golden A1 + ancoraggio A2) e i 2 mirror doc.
- I 3 .py al punto fisso reflow.
- Suite via wrapper R-210 (LONG=1, DB live, per D-519): 1115/0/24 GREEN. Probe verify\_generate: all checks passed.

## 2026-10-12 — session 105 (D-520 — rename dei 6 nomi pubblici di hlp\_optimize + reflow canonico + pin del probe)

- Su richiesta di Roberto: i 6 nomi pubblici di hlp\_optimize rinominati col prefisso del modulo (forma accorciata:
  hlp\_optimize\_save\_checkpoint, \_load\_checkpoint, \_is\_cache\_consistent, \_info\_dict, \_is\_status\_converged,
  \_weights\_compute\_hash). Aggiornati: wrk\_optimize, test\_hlp\_optimize, il probe verify\_optimize e i 5 mirror doc.
- Accompagnato: hlp\_optimize.py portato al punto fisso canonico (5 blocchi di prosa oltre i 100 preferiti, preesistenti
  — net -4 righe). Pin del probe aggiornati: A1 (327→323), A6 (forma canonica del commento), A16 (frase ora su 2 righe —
  regex tollerante), C1 (347→348: pin stantio PREESISTENTE della campagna D-517, discloso — il file era già a 348 a
  HEAD).
- I 3 .py al punto fisso reflow.
- Suite via wrapper R-210 (LONG=1, DB live, per D-520): 1115/0/24 GREEN. Probe verify\_optimize: 78/78 green.

## 2026-10-12 — session 106 (D-521 — reshaping della superficie pubblica di wrk\_positions)

- Audit degli usi su richiesta di Roberto: load\_from\_db interna (confermato); extract\_prepare + is\_cache\_consistent
  CONDIVISE con wrk\_vld\_positions (il twin documentato) — ipotesi confermata 1/3. Chiamata di Roberto: l'interna
  privatizzata, le due condivise col prefisso del modulo.
- Esito: \_load\_from\_db (fuori da \_\_all\_\_, ora 3 nomi), wrk\_positions\_extract\_and\_prepare,
  wrk\_positions\_is\_cache\_consistent. Aggiornati: wrk\_vld\_positions, i 2 test, i 2 probe (golden \_\_all\_\_,
  anchor, stringhe assert, pin D8) e i 5 mirror doc. La locale boolean is\_cache\_consistent dentro la funzione (e la
  sua riga DEBUG) intatta.
- I 4 .py al punto fisso reflow.
- Suite via wrapper R-210 (LONG=1, DB live, per D-521): 1115/0/24 GREEN. Probe verify\_wrk\_positions 21/21 +
  verify\_vld\_positions: all checks passed.

## 2026-10-12 — session 107 (D-522 — estrazione del modulo index: Index/IndexArray fuori da pattern)

- Analisi su richiesta di Roberto: il grafo pattern/mobility/feature era già un DAG (nessun ciclo) — il punto
  concettuale era che Index/IndexArray (alias generici) vivevano in pattern e costringevano mobility a importarlo.
  Chiamata: nuovo modulo index come home unica; i tre moduli importano da index; pattern perde le definizioni (e i 2
  nomi da \_\_all\_\_, e gli import morti TypeAlias/Annotated/BeforeValidator).
- Toccato: 6 sorgenti (index nuovo, pattern, mobility, feature, hlp\_indexes, hlp\_su\_analysis), 4 test (test\_index
  nuovo con la classe TestIndexArray mossa da test\_pattern; import split in test\_feature; re-routing in
  test\_mobility), 8 doc (2 nuovi + 4 aggiornati), overview (+1 riga source +1 test). Zero pin probe rotti; zero cambio
  comportamentale.
- I 10 .py al punto fisso reflow.
- Suite via wrapper R-210 (LONG=1, DB live, per D-522): 1117/0/24 GREEN (il nuovo test\_index aggiunge 5 test,
  test\_pattern ne perde 3 — la classe mossa). I 6 probe toccati: all green.
- In corso emersa l'occorrenza del runner: test\_index registrato nella lista MODULES di run\_utests.sh (la fonte unica
  che suite\_audit.py parsa).

## 2026-10-12 — session 108 (D-523 — rename di sample\_pattern\_data + gitignore dei temp file Emacs)

- Su richiesta di Roberto: sample\_pattern\_data → pattern\_sample\_data (3 occorrenze in pattern.py + 3 nei mirror doc;
  nessun import esterno — test\_pattern lo prende a star import).
- .gitignore: sezione Emacs (\#\* e .\#\*) — i lock file #pattern.py# / .#pattern.py non sono più visibili a git (e
  all'audit overview).

## 2026-10-12 — session 109 (D-524 — il sweep della notazione Index)

- Su chiamata di Roberto (dopo la ricognizione del turno precedente): dove la variabile contiene un INDICE di
  configurazione di feature → Index/IndexArray; numeri puri (conteggi, offset, I/O u32 generico) → np.uint32 invariato.
- Toccato: 6 sorgenti (15 siti) + 11 test (~39 siti) + 2 probe ri-pinnati. Zero cambio runtime (Index IS np.uint32,
  identità pinzata in test\_index).
- Il cast int64→uint32 di iwmap in hlp\_design\_matrix resta np.uint32 (chiamata di Roberto: gli int64 non si toccano,
  si pensa dopo).
- In corso emersa la C1 STALE pre-D-524 (218 pin su file da 217 righe) — corretta a 217+1.
- Suite via wrapper R-210 (LONG=1, DB live): 1117/0/24 GREEN (invariata — cambio puramente notazionale). I 8 probe
  toccati: all green.

## 2026-10-12 — session 110 (D-525 — ExtendedIndex: the type for indexes with negative logical states)

- Roberto's call: index.py gains ExtendedIndex (int64) + ExtendedIndexArray; the negative values (-1, -2) are LOGICAL
  states of a feature configuration, not data. Vocabulary line added to naming.md §Index.
- Sweep: 4 src modules (14 sites: wmaps, generate, analytics, design\_matrix) + 11 test files (~34 sites). New approved
  rule: an offset IS an Index (the feature's zero index in the model's flat index space) — applied to hlp\_wmaps + 7
  test files (the uint32 fixtures, pure notation). The int64 offset fixtures (wrk\_validate x3, wrk\_analytics x1) stay
  int64: switching them would change the synthetic pipeline's intermediate dtypes (a separate call).
- In-flight incidents, both fixed: the auto import-insert split a parenthesized import in test\_client.py (syntax error,
  caught by the reflow compile check); test\_hlp\_design\_matrix needed its D-524 Index import extended to ExtendedIndex
  (3 test errors on the first suite run).
- Suite via the R-210 wrapper (LONG=1, live DB): 1122/0/24 GREEN (1117 + 5 new ExtendedIndex tests). The 7 touched
  probes: all green.
## 2026-10-12 — session 111 (D-526 — the hlp\_plot API rename + the private helpers)

- Roberto's call: the 8 pipeline names take the module-qualified form (HLP\_PLOT\_\*, HlpPlot\*, hlp\_plot\_\*);
  jitter/egv\_bins become PRIVATE (\_jitter/\_egv\_bins, out of \_\_all\_\_ — now 8 names). The 7 plot\_\* builders stay
  un-renamed (registry dispatch).
- Touched: 3 src + 3 test + 1 probe (32 sites, 1 substring pin re-pinned) + 6 docs (51 sites). Word-boundary replaces;
  the prose "jitter" common noun untouched.
- Suite via the R-210 wrapper (LONG=1, live DB): 1122/0/24 GREEN (counts
  unchanged — pure rename). verify\_plot: green. All 7 touched .py at the
  reflow fixpoint.
