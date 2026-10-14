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
- Suite via the R-210 wrapper (LONG=1, live DB): 1122/0/24 GREEN (counts unchanged — pure rename). verify\_plot: green.
  All 7 touched .py at the reflow fixpoint.
## 2026-10-12 — session 112 (D-527 — the prng pick-kernel API: rename, annotations, uint64 slots)

- Roberto's call: the two module-level pick kernels take the prng\_ prefix and the static type annotations (inert under
  numba, string-lazy — no Pydantic); slots becomes uint64 (a prefix count is always non-negative; the type carries the
  contract). Empirically verified before the change: value-identical slots, bit-identical kernel output, aligned
  streams.
- Touched: 3 code files + 2 mirror docs. No probe pins the names (zero re-pins).
- Suite via the R-210 wrapper (LONG=1, live DB): 1122/0/24 GREEN (counts unchanged — rename + annotations + the slots
  dtype). The random\_game LONG tests cover the engine path with the new uint64 specialization. All 3 touched .py at the
  reflow fixpoint.
## 2026-10-12 — session 113 (D-528 — the hlp\_zed factory rename)

- Roberto's call: zed\_fun\_factory -> hlp\_zed\_fun\_factory (the last un-prefixed public of the module; LMZed keeps
  its name with the LM family).
- Touched: 2 src + 4 test (17 sites) + verify\_zed (3 text-only pins, no index shift) + 2 docs (6 sites). The G10 pin
  re-tightened (the old substring would have kept passing inside the new name — false green).
- Suite via the R-210 wrapper (LONG=1, live DB): 1122/0/24 GREEN (counts unchanged — pure rename). verify\_zed: 51/51.
  All 7 touched .py at the reflow fixpoint.
## 2026-10-12 — session 114 (D-529 — the hlp\_validate API: the prefix + LMValidate)

- Roberto's call: validate\_model -> hlp\_validate\_model, top\_outliers -> hlp\_validate\_top\_outliers,
  ValidationResult -> LMValidate (intentional: it hooks the VALIDATE level name; the noun-form LMValidation was
  discussed, his form chosen).
- Touched: 2 src + 3 test (15 sites) + 2 probes (text-only re-pins) + 3 docs (11 sites). The module-qualified docstring
  mentions were handled before the bulk (no double prefix).
- Suite via the R-210 wrapper (LONG=1, live DB): 1122/0/24 GREEN (counts unchanged — pure rename). verify\_validate +
  verify\_analytics: green. All 7 touched .py at the reflow fixpoint.
## 2026-10-12 — session 115 (D-530 — the exported-symbols generator in wsutils + session close)

- Roberto's call: the ad-hoc `\_\_all\_\_` snapshot generator becomes wsutils/exported\_symbols.py (one-liner refresh;
  output verified byte-identical to the current snapshot). One row in the wsutils.md table (the generation category).
- Session close: the D-518..D-530 rename wave is complete for the hlp\_zed / hlp\_validate / hlp\_plot / prng / index
  modules; the exported-symbols snapshot is in sync.
## 2026-10-12 — session 116 (D-531 — the test duration classification tool)

- Roberto's call: wsutils/test\_duration.py — the static AST tag pass (perf / db\_required / the 4 tiers,
  inheritance-aware) + N isolated all-tiers-on timed launches (default 3) + mean/variance + the VERDE/ROSSO/SKIPPED
  status → scratch/test\_duration.{csv,md}.
- The classifier verified EXACT against unittest discovery (1122 = 1122, both diffs empty) after three in-flight fixes
  (the Call.id slip, the class-level VLONG decorators, the multiple-inheritance bases).
- The 3-launch measurement: in flight as a background job (≈45-60 min).
- The 3 launches landed in ~9 min (the A2050 chain is 96 s, not 10 min): 1122/1122 VERDE, zero FLAKY — VLONG 61.1% of
  the time, LONG 25.9%, NORMAL 13.0%.
- D-532: the 21 fast DB tests (<0.4 s) re-classified LONG -> NORMAL via the new db\_gate (DB-only, default tier) +
  tier\_long (the method-level LONG check for the mixed TestVldIndependenceCheck, whose 1.7-s sibling stays tiered). 8
  test files, 3 probes re-pinned, 9 mirror docs, the classifier's db -> (db\_long, db) split. Suite 1122/0/24. NO COMMIT
  (further adjustments in flight).
- D-533: the 11 slow non-DB tests (2 plot, 2 prng, 2 board, 2 client, 4 PERF 1M) moved NORMAL -> LONG via the
  @skipUnless(tier\_long(), ...) decorator (the house VLONG/VVLONG idiom); 8 test files, the 4 PERF ones stack it over
  the PERF gate. The classifier needed no change (its ast.walk sees the decorator): 33 LONG = 22 + 11. test\_wrk\_plot
  default 9/2skip/OK, LONG=1 9/0/0; 3 probes green.
- D-534: the A2050 chain (96.5 s) moved VLONG -> VVLONG — the FIRST VVLONG instrument: the class decorator
  tier\_vlong() -> tier\_vvlong() (one line + the import). The classifier needed no change: NORMAL 1087 / LONG 33 /
  VLONG 1 / VVLONG 1. VLONG=1 alone skips it; VVLONG=1 runs the module 9/0/0 in 105.8 s.
## 2026-10-13 — session 117 (D-535 — the fast NORMAL equivalents of the LONG band)

- Roberto's goal: "the simple run is exhaustive" — for each of the 33 LONG tests (0.4-7.9 s): is the same thing already
  verified in NORMAL, and if not, can a ≤ 0.3 s test verify it?
- Five parallel analysis passes (subagents) → scratch/long\_tier\_coverage.md: 2 COVERED / 24 PARTIAL / 7 NOT COVERED;
  28 feasible fast equivalents, 3 infeasible (the A2030 end-to-end chain ×2, the JIT array overloads).
- Six parallel implementation waves (subagents, disjoint files) → 27 new UNGATED no-DB tests over 12 test files: the
  mock-Context wrk\_generate / wrk\_optimize / wrk\_vld\_positions / wrk\_analytics / wrk\_validate classes, the
  TestGradientFlagWiring + TestValidateModelUnit extensions, the plot small format-pair, the client 10k smoke + 32-board
  2-D strided parity, the full-chain no-config-sidecar, the board no-collisions de-gate, the feature I=51 row-0 golden,
  the 20k / 10k prng chi2.
- Plot exception (disclosed, Roberto's call): the all-7 small render measured 2.9 s (matplotlib's ≈ 300 ms per-figure
  floor at 50 dpi) — written then REMOVED; only the ≈ 0.2 s 'pdf,png' pair joins NORMAL, the all-7 + determinism stay
  LONG.
- Suite audit: 1149/0/24 at LONG=1 (1122 + 27). Tier shape: NORMAL 1114 / LONG 33 (unchanged) / VLONG 1 / VVLONG 1.
  Twelve mirror docs updated.
- The 7-run duration report refreshed; the 5 residual LONG tests (A2030 ×2, JIT array, the 2 covered 1M PERFs) are
  Roberto's call.
- D-536: the run\_utests.sh banner now prints VVLONG (the header comment's stale D-285 "uninstrumented" claim dropped) +
  rlm\_04.json's cosmetic line break (Roberto's edit, parsed structure identical) + the A2030 tests confirmed to stay
  LONG ("vanno bene così"). Canonical LONG=1 run OK (24 skips).
- D-537: the overview cleanup on Roberto's dictation — the test-command entry rewritten (default ~15 s; his draft's
  LONG=0 corrected to LONG=1, disclosed), the Current-state suite-tiers entry removed, three Next-steps entries removed
  (naming sweep, int64 fixtures, register re-review).
- D-538: the overview test-command entry's durations replaced with the MEASURED numbers (default ~17 s, VVLONG=1 ~3.5
  min — the 7-run report means).
- Session close: D-535..D-538 are committed (the 27 fast NORMAL equivalents — suite 1149/0/24, the VVLONG banner + the
  rlm\_04 line break, the overview cleanup + the measured durations). The next session opens on the LM config "User
  guide" — the PLACEMENT decision is pending (a section of the logistic\_model mirror doc vs a separate user doc; Nia
  proposes the separate doc + the one-line pointer).
## 2026-10-13 — session 118 (D-539 — the docs/user/ zone + the LM config user guide)

- Roberto's task: the LM config "User guide" — technical and precise, every rule and option of the JSON config file, a
  minimal example entry, then the exhaustive reference. Placement: a SEPARATE doc in a new docs/user/ zone (approved
  after Nia's proposal; the mirror-doc section was dropped).
- docs/user/lm\_config\_guide.md written (the Rules, the minimal example, the per-section reference, the complete
  example — both examples verified against the real LMConfig schema); Roberto's review: "mi piace moltissimo".
- D-539: the zone legislated — docs\_rules.md (the opening scope sentence + the new §8: the house format applies, the
  mirror skeleton does not; the TRUTH + LIFECYCLE contracts), wsutils/docs\_format\_audit.py (the docs() walk skips
  docs/user/), the overview "Mirror docs" bullet registers the zone.
- Session close: the guide is DONE and committed (the overview next-steps entry removed on Roberto's call).
## 2026-10-13 — session 119 (D-540 — the license headers + the public-push preparation)

- Roberto's plan (agreed step-by-step, one GO at a time): prepare the repo for its FIRST public push to
  github.com/rcrr/reversi-v2 — name, headers, fresh-clone proof, README, cleanups, push.
- Step-0 decisions: the repo is PUBLIC; the branch renamed master → main; the .env password in the history is ACCEPTED
  (the local-only test DB, the trivially-known username/dbname) — it leaves the TRACKED tree in step 3a.
- D-540: the 146-file header migration (41 insertions + 105 URL rewrites to the reversi-v2 URL; the random\_game.py
  variant normalized), the official GPLv3 LICENSE from gnu.org, the pyproject license field. Suite green; the wave
  committed.
- D-541: the R-591 guard — wsutils/license\_header\_audit.py (the 147-file scope, the ten marker lines in order,
  fail-closed) wired as the THIRD blocking pre-commit check; R-591 legislated in the Code style section; 27 old banners
  normalized (the trailing-space separators); the pre-commit hook itself got its banner. End-to-end proof: a headerless
  staged file blocked a real commit.
- D-542: step 3, part 1 — the .env untracked (it stays on the local disk) + .gitignore + the .env.example template; the
  paths.py auto-mkdir of build/tmp at import time. Suite green; committed. The README (3c) written, UNCOMMITTED —
  awaiting Roberto's review.
- D-543: the README approved by Roberto (the single addition: the regab bullet pointing to the rcrr/reversi project) —
  committed.
- 3d: the FRESH-CLONE PROOF — PASSED: the repo cloned to /tmp/reversi-v2-clone, the venv + pip install -e . from
  scratch, NO manual mkdir (build/tmp auto-created), NO .env (the gitignored one is absent by design), SKIP\_REGAB\_DB=1
  ./run\_utests.sh → 1149 tests in 45.6 s, OK, 109 skips (the 85 DB-gated + the 24 standing), zero failures. A stranger
  cloning the repo gets a project that runs.
- MOBILITY redundancy experiment (Roberto's 8 configs in build/test\_mobility, A2050): his thesis — the mobility
  mask + anti-mask + diff-mask are LINEARLY DEPENDENT. Verified independently: the 8 validation RMSEs match the
  reports (≤0.01); from the additive kernel definition DLMC = LMC + ALMC is an EXACT identity — zero deviation over
  all 1,999,179 positions, and at the design level (D = 19 + L + A, residual 0.000000, rank([1,L,A,D]) =
  rank([1,L,A]) = 3); all three pairs span the same 2-D space, the triple adds a rank-deficient column. The
  near-equal single LMC/ALMC scores are a corpus property (the balanced corpus: mean mover 9.66 vs opponent 9.87
  moves), not algebra. Detailed scientific feedback delivered; design GO received.
- D-544: the MOBILITY rework — the difference concept is GONE: a mobility is (mask, side), side ∈ {'mover',
  'opponent'}; the opponent side is the RAW count (was 64 − A, span-equivalent under the intercept). 28 active
  files: the core (class/set/kernel), the config schema (the Literal side field, fail-fast), the workers (the
  binary layout u64 + u8), the 6 fixtures (rlm\_00 3 → 2 features), the tests (test\_mobility.py rewritten as the
  spec — the dedicated mover-side, opponent-side and multi-entry cases; the rlm\_00-derived goldens recomputed via
  independent derivations that match the pipeline; the rlm\_01/rlm\_04 analytics report re-pins after model-content
  verification — RMSE 23.87 unchanged, the 6-position EF bit-exact), the 4 probes (incl. 2 PRE-EXISTING drift
  re-pins in verify\_hlp\_indexes the run surfaced), the 9 mirror docs + the user guide + the naming register. Zero
  amask/DLMC left in the active zones. The full LONG=1 suite green (1151 tests, 24 skips).
- D-545: D-544 completion — Roberto's VVLONG run surfaced the two tier omissions the LONG=1 guard does not
  reach: the test\_feature PERF class (the third old-style construction the wave's two-replacement pass missed)
  and the A2050 full-chain goldens (the masked report hash + the rlm\_03 fset hash, independently derived).
  All content pins passed UNCHANGED (the training stats, the w\_dense sha3, the 6-position EF, the size band) —
  model identity at A2050 scale. The full VVLONG=1 suite green (1151 tests, 22 skips).
- D-546: the definition precision on review — the game rules define the available moves only for the player to
  move (the mobility); the anti-mobility is OUR feature-level definition: the opponent's would-be moves (the
  moves it would have if it were its turn). The approved wording applied to all 8 active-zone locations (the
  mobility.py docstrings x4, the config schema, the mirror doc, the naming register, the opponent-side test
  docstring). Docs-only; probes + full LONG=1 suite green.
- D-547: Roberto's observation — a [PERF …] line in a PERF=0 run. Diagnosis: NOT a missing gate (the 1M test is
  double-gated PERF=1 + LONG=1); the line was the deliberate UNGATED 10k smoke twin reusing the house [PERF …]
  prefix. Fix: the smoke twin prints [SMOKE …] now (a non-PERF run must never show a [PERF …] line); mirror doc
  updated. Default-tier module run: [SMOKE …] present, zero [PERF …]; full LONG=1 suite green.
- D-548: Roberto's rule — the standard tests print NOTHING. The 10k smoke twin removed its print entirely
  (with the benchmark-only warmup + timing that fed it), scoped to that one test only; mirror doc updated. The
  module now runs silent in the default tier; full LONG=1 suite green.
- D-549 + MOBILITY wave CLOSED: Roberto's docstring principle — we write what the program DOES, never what it
  does NOT (the "no print" negation in the smoke test's docstring was useless and misleading — removed; the
  docstring now states only the parity check). The wave: D-544 (the rework) → D-545 (the VVLONG completion)
  → D-546 (the definition precision) → D-548 (the smoke print removed) → D-549 (this docstring). The A2050
  verification reproduced the pair's 12.47 in the new format. Session closed; a new one opens.
- LOG wave, step 1 (D-550): the three agreed changes — the per-step DEBUG duration line in the state
  machine, the FINAL\_LOG\_PRINT closing DEBUG "log written (N lines)" line, and the file floor at
  DEBUG (the TRACE hot-loop detail stays out of the file; TRACE reserved for the L-BFGS loop / the
  Numba kernels). Display goldens + the final-log test + the probe re-pinned. Full LONG=1 suite green.
  The per-level reclassifications follow, one level per wave.
- LOG wave, level 1 (D-551, iterative): the CONFIG worker — C1 the redundant "Loading …" line out,
  C2 the six DEBUG operational-section echoes in (the log now self-sufficient on the run's parameters;
  the DB echo never carries the password). Reviewed on the target-level artifact, committed after the
  full LONG=1 suite green.
- Next: step 4 (the secret scan, the final suite) and step 5 (the push).
