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
- MOBILITY redundancy experiment (Roberto's 8 configs in build/test\_mobility, A2050): his thesis — the mobility mask +
  anti-mask + diff-mask are LINEARLY DEPENDENT. Verified independently: the 8 validation RMSEs match the reports
  (≤0.01); from the additive kernel definition DLMC = LMC + ALMC is an EXACT identity — zero deviation over all
  1,999,179 positions, and at the design level (D = 19 + L + A, residual 0.000000, rank([1,L,A,D]) = rank([1,L,A]) = 3);
  all three pairs span the same 2-D space, the triple adds a rank-deficient column. The near-equal single LMC/ALMC
  scores are a corpus property (the balanced corpus: mean mover 9.66 vs opponent 9.87 moves), not algebra. Detailed
  scientific feedback delivered; design GO received.
- D-544: the MOBILITY rework — the difference concept is GONE: a mobility is (mask, side), side ∈ {'mover', 'opponent'};
  the opponent side is the RAW count (was 64 − A, span-equivalent under the intercept). 28 active files: the core
  (class/set/kernel), the config schema (the Literal side field, fail-fast), the workers (the binary layout u64 + u8),
  the 6 fixtures (rlm\_00 3 → 2 features), the tests (test\_mobility.py rewritten as the spec — the dedicated
  mover-side, opponent-side and multi-entry cases; the rlm\_00-derived goldens recomputed via independent derivations
  that match the pipeline; the rlm\_01/rlm\_04 analytics report re-pins after model-content verification — RMSE 23.87
  unchanged, the 6-position EF bit-exact), the 4 probes (incl. 2 PRE-EXISTING drift re-pins in verify\_hlp\_indexes the
  run surfaced), the 9 mirror docs + the user guide + the naming register. Zero amask/DLMC left in the active zones. The
  full LONG=1 suite green (1151 tests, 24 skips).
- D-545: D-544 completion — Roberto's VVLONG run surfaced the two tier omissions the LONG=1 guard does not reach: the
  test\_feature PERF class (the third old-style construction the wave's two-replacement pass missed) and the A2050
  full-chain goldens (the masked report hash + the rlm\_03 fset hash, independently derived). All content pins passed
  UNCHANGED (the training stats, the w\_dense sha3, the 6-position EF, the size band) — model identity at A2050 scale.
  The full VVLONG=1 suite green (1151 tests, 22 skips).
- D-546: the definition precision on review — the game rules define the available moves only for the player to move (the
  mobility); the anti-mobility is OUR feature-level definition: the opponent's would-be moves (the moves it would have
  if it were its turn). The approved wording applied to all 8 active-zone locations (the mobility.py docstrings x4, the
  config schema, the mirror doc, the naming register, the opponent-side test docstring). Docs-only; probes + full LONG=1
  suite green.
- D-547: Roberto's observation — a [PERF …] line in a PERF=0 run. Diagnosis: NOT a missing gate (the 1M test is
  double-gated PERF=1 + LONG=1); the line was the deliberate UNGATED 10k smoke twin reusing the house [PERF …] prefix.
  Fix: the smoke twin prints [SMOKE …] now (a non-PERF run must never show a [PERF …] line); mirror doc updated.
  Default-tier module run: [SMOKE …] present, zero [PERF …]; full LONG=1 suite green.
- D-548: Roberto's rule — the standard tests print NOTHING. The 10k smoke twin removed its print entirely (with the
  benchmark-only warmup + timing that fed it), scoped to that one test only; mirror doc updated. The module now runs
  silent in the default tier; full LONG=1 suite green.
- D-549 + MOBILITY wave CLOSED: Roberto's docstring principle — we write what the program DOES, never what it does NOT
  (the "no print" negation in the smoke test's docstring was useless and misleading — removed; the docstring now states
  only the parity check). The wave: D-544 (the rework) → D-545 (the VVLONG completion) → D-546 (the definition
  precision) → D-548 (the smoke print removed) → D-549 (this docstring). The A2050 verification reproduced the
  pair's 12.47 in the new format. Session closed; a new one opens.
- LOG wave, step 1 (D-550): the three agreed changes — the per-step DEBUG duration line in the state machine, the
  FINAL\_LOG\_PRINT closing DEBUG "log written (N lines)" line, and the file floor at DEBUG (the TRACE hot-loop detail
  stays out of the file; TRACE reserved for the L-BFGS loop / the Numba kernels). Display goldens + the final-log test +
  the probe re-pinned. Full LONG=1 suite green. The per-level reclassifications follow, one level per wave.
- LOG wave, level 1 (D-551, iterative): the CONFIG worker — C1 the redundant "Loading …" line out, C2 the six DEBUG
  operational-section echoes in (the log now self-sufficient on the run's parameters; the DB echo never carries the
  password). Reviewed on the target-level artifact, committed after the full LONG=1 suite green.
- LOG wave, level 2 (D-552, iterative): the FEATURES worker — F1 the three "object created, hash" DEBUG lines out, F2
  the raw intercept-config echo out, F3 the per-feature table gains the two cumulative position columns (first
  design-matrix column, first w\_dense weight). Reviewed on the target-level artifact, committed after the full LONG=1
  suite green.
- LOG wave, level 3 (D-553, iterative): the SU\_ANALYSIS worker — the per-instance / per-pair data rows out of the log
  (the report file is their home), the corpus + publication lines to DEBUG. 18 → 8 lines. Reviewed on the target-level
  artifact, committed after the full LONG=1 suite green.
- D-554: the R-595/R-600 enactment on Roberto's confirmation — the rename + the new rule committed (the 4 files), the
  overview bullet out.
- D-555: the overview Next-steps refresh — the closed MOBILITY bullet out, the LOG-wave-in-progress bullet in
  (D-550…D-553 done, next POSITIONS).
- LOG wave, level 4 (D-556, iterative): the POSITIONS worker — the publication line to DEBUG, the dataset identity lines
  stay INFO. First commit under the new guard practice (default tier before the commit, LONG at the wave end).
- D-557: the test-guard policy in the overview — the default tier is the standard pre-commit run, LONG=1 on demand + at
  the wave-end milestone.
- LOG wave, level 5 (D-558, iterative): the INDEXES worker — the publication line to DEBUG + the new DEBUG indexes-shape
  line (199932 × 6).
- LOG wave, level 6 (D-559, iterative): the DESIGN\_MTR worker — the publication + the shape lines to DEBUG.
- LOG wave, level 7 (D-560, iterative): the ANOVA worker — the per-feature rows out of the log (option b, the report is
  their home), the two tests re-pinned on the report. The exhaustive anova config section verified the CSV path.
- LOG wave, level 8 (D-561, iterative): the WMAPS worker — the publication + the total-weights lines to DEBUG.
- LOG wave, level 9 (D-562, iterative): the ZED worker — the shape line to DEBUG + the new DEBUG range line (the
  clipping endpoints at a glance).
- LOG wave, level 10 (D-563): the GRADIENT worker reviewed — LEAVE-AS-IS (already compliant, no source change).
- LOG wave, level 11 (D-564, iterative): the OPTIMIZE worker — the L-BFGS loop output to DEBUG (Roberto's correction:
  the log\_every\_n config is the user's frequency throttle, so the per-iteration lines stay in the log, at DEBUG).
- LOG wave, level 12 (D-565, iterative): the GENERATE worker — the shape line to DEBUG.
- LOG wave, level 13 (D-566, iterative): the VLD\_POSITIONS worker — the publication line to DEBUG (the POSITIONS
  pattern, mirrored).
- LOG wave, level 14 (D-567, iterative): the VALIDATE worker — the outlier block (header + 20 per-position lines) to
  DEBUG, as one unit.
- LOG wave, level 15 (D-568, iterative): the ANALYTICS worker — the report body to DEBUG (bounded content; the file
  report is its canonical home).
- LOG wave, level 16 (D-569, iterative): the SAVE worker — the existing lines leave-as-is + the new DEBUG integrity echo
  (the final artifact's size + checksum).
- LOG wave, levels 17-18 (D-570): the CLIENT\_CHECK + PLOT workers reviewed together — LEAVE-AS-IS (both already
  compliant, no source change).
- LOG wave — the shared cache boilerplate (D-571, iterative): the 3 compute-path process lines of cache\_manager to
  DEBUG; the 3 outcome lines stay INFO (the fresh-vs-cached fact).
- LOG wave CLOSING (D-572, milestone): the wave is complete (D-550…D-571 — the 19 per-level waves + the shared
  cache-boilerplate). Closing LONG=1: the first close run had 1 transient failure (not reproduced; the name was not
  captured), the second is green (1151 ok, skipped=24). The overview bullet is flipped to COMPLETE.
- The A2050 size-band fix (D-573): the new-workspace first LONG run failed the A2050 size band — the investigation
  proved it is WORKSPACE-PATH-DEPENDENCE (the absolute base\_dir in the embedded dump; a 7-char rename shifts the
  compressed size ~48 bytes through the LZ4 cascade), NOT a library version (the dumps diff to exactly the 7 path
  bytes). Band widened 516991-517191 + comment + the mirror's two stale band values corrected.
- PUBLISH campaign COMPLETE (D-574, milestone): Roberto executed steps 4-5 — the secret scan clean, the final suite
  green, the first push of rcrr/reversi-v2 to GitHub. The new workspace /home/rcrr/base/prj/reversi-v2 (the fresh clone)
  is operational (venv + .env + default suite green); the D-573 fix is pushed; the push/pull round-trip verified. The
  old dsh workspace stays in place, untouched.
- Next: step 4 (the secret scan, the final suite) and step 5 (the push).

## 2026-10-17 — session 120 (the post-PUBLISH roadmap — D-575)

- Session opened: with the pipeline complete and published (D-574), Roberto populates the overview Next-steps section
  with the forward campaign roadmap — the next phase is USING the completed pipeline.
- Seven campaigns recorded in notes/overview.md Next steps (non-prioritized): FEATURE-SET, LATEX, MULTI-PLY, MOVE-PROB,
  ENDGAME-SOLVER, REGAB, TEST-BATCH.
- The REGAB entry refined over the exchange into three components with distinct fates: position generation → Python (the
  existing random\_game code + the DB insert), classification generation out of the v2 DDL (superseded by the dynamic
  pipeline — not dropped), and the regab\_solve resolver staying in C to the v2 format (the batching + DB-interaction
  front end calling the same solve primitive as endgame\_solver).
- A near-duplicate caught: "port the ANSI C program regab solve" was the REGAB resolver component, merged into the REGAB
  entry (one fact, one home) rather than added as a separate campaign.
- Two forward-looking ideas seeded in notes/ideas.md (the open backlog was empty): I-021 (the ResNet extension of the
  logistic model) and I-022 (the ANSI-C-to-Rust port) — both status `idea`, placed in the backlog (not Next steps) as
  uncommitted proposals.
- D-575 recorded (the roadmap setup). Notes-only change (overview.md + ideas.md); no source/test files touched.
- Drive-by bookkeeping fix: the overview's test\_mobility Suite cell was stale (31/0/1) — the fresh gate measurement
  (33/0/1; the file has 33 tests) revealed the drift, corrected to 33/0/1/0/0.
- Closing LONG=1 gate run (R-840): green (1145 ok, skipped=24) — the per-module measurement regenerated for the
  pre-commit gate (scratch/suite\_audit.txt; the disposable scratch/ was empty in the fresh clone).
- Session closed by the user.

## 2026-10-17 — session 121 (the LATEX campaign — governance established, D-576)

- Session opened: the LATEX campaign (the artifact book) begins. Working in scratch/ (gitignored, no checkin) per
  Roberto, until the governance is clarified.
- The document is a BOOK (~200pp), not a paper; a 10pp paper may be distilled later if the results warrant.
- Governance G1-G7 settled with Roberto: the latex/ zone; Make + latexmk + pdflatex; the include/includeonly
  fast-compile + the reversi\_NNN\_slug.tex (3-digit, step 20) naming; all build artifacts gitignored in build/ (the PDF
  only at a release); notes/latex\_rules.md (the overview Index line deferred until clear); Italian-first; interleaved
  with FEATURE-SET.
- A scratch spike (scratch/latex\_spike/) validated the design before promotion: the 9pp full vs the 5pp single-chapter
  fast build (the includeonly gotcha — it matches the FULL filename — fixed by the Makefile glob-resolving CH=NNN to the
  chapter base name).
- Roberto added two authoring tools (G8), both prototyped + validated in the spike: make spell (tex2txt.py strips the
  markup -> aspell -d it, filtered against the domain dictionary; a pre-checkin gate) and make pdf2png (Nia renders the
  pages to PNG and inspects them visually, as with the pipeline PLOTs). The visual tool immediately caught a real defect
  the compiler hides: the English "CONTENTS/Chapter" headings -> fixed with \usepackage[italian]{babel} -> confirmed
  "INDICE/Capitolo".
- Promotion (this milestone, D-576): the validated design is homed in the tracked latex/ zone (Makefile, main.tex,
  tex2txt.py, dict.txt, .gitignore, the 3-chapter skeleton) + notes/latex\_rules.md (G1-G8) + the overview Index line.
  Prepared for the first LATEX checkin (pending Roberto's file-by-file review of the git radar); no commit made.
  Content/structure is phase 2.

## 2026-10-18 — session 122 (LATEX phase-2 content ported + the .tex license adoption, D-577/D-578)
- Ported the legacy draft's content into the book (phase 2), chapter by chapter, faithful to the source: chapter 2 "La
  board" (2.1 domain representation, 2.2 game positions, 2.3 the D4 dihedral group — the full legacy ch.4 with the
  transformations/subgroups/Hasse/Cayley tables), chapter 3 "I pattern" (3.1 pattern theory + canonicalization, 3.2
  definition + index calculation with the C code), chapter 4 "La funzione di valutazione" (the legacy ch.7 —
  model/target/cost/gradient), and Appendix A "Catalogo dei Pattern" (the legacy ch.8 — 29 patterns, each with its
  metadata box + the 8 D4 board subfigures). The legacy Introduction (ch.1) is obsolete — skipped.
- The appendix is generated statically from mdp.csv (scratch/gen\_appendix.py) because datatool is not installed; the
  book stays self-contained (no datatool/CSV at build time). The preamble gained amsmath/amssymb/bm/booktabs/tikz +
  listings/enumitem/xcolor + tcolorbox[most]/tabularx/expl3; othelloboard.sty (Steven Hall, LPPL) copied in.
- D-577: every hand-written .tex source adopts the standard 26-line GPL header (the %-comment variant); the R-595 guard
  (license\_header\_audit.py) extended to .tex. othelloboard.sty (third-party, LPPL) + the build-artifact
  includeonly.tex are exempt.
- Gates green: the license audit passes on all 153 tracked sources; notes\_lint green; the build is 56 pages, 0 hard
  errors. Two checkins: D-577 (the license governance) + D-578 (the content milestone).

## 2026-10-18 — session 123 (LATEX — new Appendix B "Regole del gioco", D-580)
 - Added Appendix B "Regole del gioco" to the book: the official Othello rules, translated into Italian from the World
   Othello Federation's official-rules page (the source cited explicitly, title + URL, for copyright clarity).
 - All 12 board diagrams reconstructed with the othelloboard package (not copied images): the setup, the outflanking
   example, the rule-2/4/5 illustrations (with the move/flip arrows in red so they read on black discs), and the sample
   game (the first two move pairs, grouped as one 2x2 figure).
 - A terminology note defines "aggiramento" (the Italian for "outflank", verb "aggirare") with the common players'
   expressions; a final section covers the WOF early-termination scoring rule (empty squares count for the winner, total
   always 64), quoting the WOC Rules Section IV.8 with the source PDF link.
 - Iterated with Roberto (surgical tweaks): removed the "reconstructed with othelloboard" sentence, translated
   everything to Italian, grouped the outflanking + sample-game figures as figure/subfigure, made the arrows red.
 - Gates green: the license audit passes on the new .tex; the build is 60 pages, 0 hard errors, 0 undefined references;
   notes\_lint green. One checkin: D-580.

## 2026-10-19 — session 124 (LATEX — the appendix files move to the 8xx band, D-581)
 - Renamed the two appendix chapter files to the 8xx numbering band (git mv, history preserved): the pattern catalog
   appendix to reversi\_800\_appendix\_catalogo.tex and the rules appendix to reversi\_820\_appendix\_regole.tex,
   freeing the 1xx band for the main chapters.
 - Updated the main.tex include lines and the two files' self-referencing header comments to the new names; the Makefile
   CH fast-compile is glob-based and needs no change.
 - Gates green: build 60 pages, 0 hard errors, 0 undefined references; notes\_lint green. One checkin: D-581.

## 2026-10-19 — session 125 (LATEX — the pipeline introduction chapter, D-582)
 - Wrote the new main-body chapter 100, "La pipeline" (reversi\_100\_pipeline.tex): an overview of the Machine-Learning
   pipeline — the architecture (facade / state machine / context / workers + the wrk\_/hlp\_split), the three design
   principles, the 19 levels in five phases (with a table), the JSON5 config, the data flow, and the command-line
   execution. No per-module detail (reserved for the per-level chapters to come).
 - Wired it into main.tex after the evaluation-function chapter (080), before \appendix (the new chapter 5). Used the
   proper Unicode accented vowels (not the ASCII-apostrophe convention); kept one listings block free of multi-byte
   characters (listings reads verbatim and chokes on them).
 - Gates green: build 64 pages, 0 hard errors, 0 undefined references; notes\_lint green. One checkin: D-582.

## 2026-10-19 — session 126 (LATEX — the six per-level pipeline chapters, D-583)
 - Wrote the six per-level pipeline chapters (one per §5.2 phase), the detailed follow-up to the pipeline-overview
   chapter (D-582): 6 Setup (the CONFIG level + every config option in tables, then FEATURES), 7 Corpus e analisi delle
   feature (SU\_ANALYSIS/POSITIONS/INDEXES/ANOVA/WMAPS), 8 Costruzione del modello (DESIGN\_MATRIX/ZED/GRADIENT/a brief
   OPTIMIZE/GENERATE), 9 L'algoritmo L-BFGS (the full solver: implicit BFGS, two-loop recursion, strong-Wolfe line
   search with the exact cubic-Hermite interpolation, the (s,y) window, restart + stopping, the implementation choices),
   10 Validazione e analisi (VLD\_POSITIONS/VALIDATE/ANALYTICS), 11 Persistenza e output
   (SAVE/CLIENT\_CHECK/PLOT/FINAL\_LOG\_PRINT).
 - Drafted by six parallel subagents (one per chapter, each reading its levels' sources), wired into main.tex after
   chapter 100 and before \appendix (the new chapters 6-11), and reviewed the drafts.
 - Fixes from the review: the accented-vowel conversion also ate the math primes (\varphi') and two Python string quotes
   in listings (restored); escaped a \texttt caret and a bare underscore; corrected a section cross-reference; fixed a
   typo. One typesetting fix: the sans-serif math (sfmath) mis-positions a \bar accent when a subscript follows, so the
   ANOVA y-bar means use \overline{y} (verified on a mini-doc to center correctly).
 - Gates green: build 112 pages, 0 hard errors, 0 undefined references; spellcheck clean; notes\_lint green. One
   checkin: D-583.
 - Then, at Roberto's request, built wsutils/latex\_lint.py — a context-aware linter and safe auto-fixer for the .tex
   sources — to robustly verify the accented vowels and every other recurring, mostly silent pitfall the build does not
   stop on. The core is a prose / math / code / comment / inlinecode context scanner, so the accent check leaves the
   math primes and the code quotes alone. Eight checks; --write applies the four safe fixes (accent, code-ascii, texttt,
   bar→overline). Validated on a synthetic file (every fix lands, the re-scan is clean) and on the finished book (0
   violations; it caught one real leftover, an empty language= in chapter 10, now removed). One checkin: D-584.
 - At Roberto's suggestion, added the \enverbatim{...} foreign-verbatim tag: an identity macro in the main.tex preamble
   and a NON\_PROSE entry in tex2txt.py, so a deliberate English verbatim is shielded from the Italian spellcheck
   without polluting dict.txt. The name had to drop the underscore — \en\_verbatim is not a legal control sequence (the
   \_ would start a subscript, "Missing $ inserted"): it is \enverbatim. Applied it to the English "World Othello
   Championships Rules" scoring quote in the game-rules appendix (ch 820), which already has an Italian translation
   below it; that removed the quote's words from the spell flags. Building the full book to confirm, I found make spell
   has in fact been flagging 3394 words book-wide all along (a 14-entry dict.txt, code/SQL identifiers leaking through
   tex2txt.py) — the earlier "spellcheck clean" notes did not reflect that. It is a separate, pre-existing cleanup,
   surfaced to Roberto for his call. Build green (112 pages). One checkin: D-585.
 - At Roberto's call, brought the spellcheck gate to zero: populated dict.txt with the 621 legitimate technical/domain
   terms, made tex2txt.py drop the verbatim/listing CONTENT (not just the markers), the LaTeX quote delimiters, and the
   table column-specs, and fixed 11 real typos in the chapters (collocare, analogamente, orizzontale, ripetendo,
   affinamente, calcolo, "Non è", generalmente, restringente, ricostruisce, concede). make spell is now green (0
   misspellings book-wide) and is a hard checkin gate (latex\_rules.md G8). Build green (112 pp), linter green (0). One
   checkin: D-586.
 - Wrote the new "Le feature" chapter (reversi\_070\_feature.tex) at Roberto's request and inserted it as chapter 4,
   after the pattern chapter: all later chapters shift by one and I updated the 13 hardcoded chapter-number references
   (prose and header comments) to match. The chapter has the three feature sources (pattern/mobility/intercept) and the
   FeatureSet, a short intercept section, and a developed mobility section (formal definition, LMC/ALMC, a worked
   example, the config/instance structure, a comparison table, the strategic reading). Build green (116 pp), linter
   green. Sent to Roberto as a first draft for review. One checkin: D-587.
  - Did the notation-consistency review Roberto asked for over the board (ch 2) and pattern (ch 3) chapters and applied
    the approved fixes (A, B, C, D2, E1, E2, F1, F3, F4), using the code (board.py) as the ground truth. The headline
    item (E2) makes the code, the math notation, and the Cayley-table interpretation congruent: the composition
    convention is now the standard one (matching the code), the `code_mapping` rotation compositions are corrected to
    board.py (ro090/ro270 were swapped), and the diagonal labels are corrected (sr = anti-principale h1-a8, sr^3 =
    principale a1-h8), all triple-checked against the code. The D4 element notation is unified to the word form (r, s,
    sr^k) across the Hasse/Cayley/degenerazione sections; the pattern chapter's symbol collisions are resolved (Orb/Stab
    take the mask M, the square count is S, the cell state is sigma, the stabilizer order is |Stab(M)|); and a new
    'Convenzioni di notazione' table opens the pattern chapter. Also fixed a feature-chapter typo (presiamo ->
    prendiamo) surfaced by the spellcheck that D-587 had skipped, and added 21 terms to dict.txt (621 -> 642). Deferred
    to Roberto: D1 (the book says D4, the code says D8 - I recommend renaming the book to D8 for full consistency). Left
    untouched per Roberto: F2. Build green (116 pp), linter green (0), spellcheck green (0). One checkin: D-588.
  - Resolved D1 at Roberto's call: renamed the code and the vocabulary from D8 to D4 (comment/docstring-only in the
    code, no behaviour change), so the book, the code, and naming now all agree on D4. Changed 21 group-name D8 in the
    four .py (board 6, pattern 8, feature 2, `hlp_su_analysis` 1) via a quote-aware word-boundary substitution that
    leaves the D8 board-square name and the hex constants untouched, plus naming (5), rules (1), `latex_rules` (1),
    overview (1 + the D1 clause reworded as resolved). Verified behaviour-neutral: the 8 probes that report a numeric
    mismatch fail identically on the stashed original D8 code. Checks per Roberto: lint green (`py_compile`,
    `notes_lint` 0, `latex_lint` 0), probe sweep 16/24 (the 8 red are pre-existing), VVLONG green (exit 0, full 19-level
    pipeline on the live regab DB). One checkin: D-589.
  - At Roberto's call, made the spellcheck dict lowercase-by-definition and case-insensitive: the Makefile spell filter
    is now grep -vFxi and dict.txt is normalised to one lowercase entry per term (642 -> 578 words; the 64
    case-duplicates collapse). Verified with a micro-test (a dict term is suppressed in any casing, a genuine unknown is
    still flagged) and a green full-book make spell (0). Documented in the G8 rule (LaTeX rules). One checkin: D-590.
  - At Roberto's call, changed the single page-11 position-field reference from uint64 to int64 (board.tex, the
    `GAME_POSITION` PLAYER field): the bitboard type stays uint64 (the canonical form), and the int64 is only the REGAB
    database storage form. Exactly one reference changes; all other uint64 in the book are left as-is. Build green (116
    pp), linter green (0), spell green (0). One checkin: D-591.
  - At Roberto's call, corrected three terms in the "Le feature" chapter: intercetto -> intercetta (8), quadrato/i ->
    cella/celle (16, with the feminine gender agreement on the articles), and bandiera -> flag (3, the side flag,
    article fem->masc). Checked each change in context; the build caught and I fixed a brace imbalance the "flag" edit
    had introduced. Build green (116 pp), linter green (0), spell green (0). One checkin: D-592.
  - Roberto flagged Italian comments in listing 12.1 (the "Persistence and output" chapter). Checked the code: it is
    already English (a src/-wide scan found no Italian comments), so no code change or test run was needed - the Italian
    was only in the book's hand-written listing excerpt. Translated the five listing-12.1 comments to English (aligned
    to the code's section names); a scan of all lstlisting blocks confirms it was the only one. Build green (116 pp),
    linter green (0), spell green (0). One checkin: D-593.
  - At Roberto's call, eliminated the book's "Summary" (the front-matter abstract, labelled "Riassunto") - a book has an
    introduction, not a summary. Moved its content (the Reversi-ecosystem prose) into the Introduction chapter, which
    was an empty skeleton; removed the now-unused abstract environment from main.tex (front matter is now \maketitle,
    \tableofcontents, chapters). Build green (116 pp), linter green (0), spell green (0). One checkin: D-594.
  - Closed the LATEX campaign at Roberto's call: the book is at an acceptable draft. Updated the overview - removed the
    "The LATEX campaign" Next-steps bullet (it carried the D-pointers that don't belong there), added a Current-state
    bullet (the book draft + the `make -C latex latex` PDF command), and added a Next-steps bullet listing the planned
    book improvements as the open seed for a fresh campaign (to open in a new session). `notes_lint` green. One
    checkin: D-595.

## 2026-11-09 — session 127 (the USO campaign opens — the models/ zone, D-596)
  - Recon first (Roberto: "non fare nulla, controlla e riferisci"): git tree clean at D-595 (the LATEX close),
    notes\_lint green on all 15 governance files, the fast tier green (1151 tests) once PostgreSQL was back up (it had
    been down: 21 DB-gated errors + 1 order-artifact FAIL with the DB off, all clear with it on).
  - Scope with Roberto: the USO campaign starts with the model-tracking rules — he wants to develop several models, keep
    the JSON configs in git, and keep every pipeline output out. His design (adopted): `models/lm/ec20/NNNN/` with
    `lm_ec20_NNNN.json`, a rigid `index.md`, and the 1:1 `build/lm/ec20/NNNN/` output mirror with a RELATIVE `base_dir`
    (no absolute paths in tracked files — portability). Plan mode: three micro-choices settled — the index is a MINIMAL
    pure registry (ID + a markdown link straight into the JSON, Roberto's words), the zone opens empty (the template
    lives in the user guide, no fake 0000), and the operational doc goes to docs/user/.
  - Verified the ground before building: the LMConfig schema already accepts a relative `base_dir` (the three gates run
    on the CWD-resolved path; `docs/user/lm_config_guide.md` already shows a `models/my-model` example) — so the zone
    needs ZERO pipeline code changes. The pre-commit hook already feeds every staged .json to the license audit; only
    the audit's full-mode `git ls-files` glob and the R-595 text miss `models/` (that is D-597).
  - Item 1 (D-596): created `models/lm/ec20/index.md` (the format preamble + the empty 2-column table), promoted R-360
    (the models/ zone) into the register's Layout & tree band, added the overview Environment bullet and the README
    Layout row. notes\_lint green; suite wrapper measurement fresh; checkin green.
  - Item 2 (D-597): extended the R-595 license-header scope to the models' .json configs: the audit's full-mode
    `git ls-files` glob gains `models/*.json` (the pre-commit path already fed every staged .json — no hook change),
    plus the R-595 register text and the wsutils.md inventory row. Full-mode audit green (165 files; the zone is empty,
    so the new glob is unexercised until the first real model).
  - Item 3 (D-598): wrote `docs/user/model_development.md` (the second `docs/user/` doc): the operational life of a
    model — next NNNN, `mkdir -p` of both trees, the config template (smallest valid 10-key shape, GPL header, relative
    `base_dir`), the registry row with its link, the run command from the workspace root, the output home. The template
    is verified to load through the real `LMConfig` schema (json5 + pydantic) — the §8 "Truth" contract; the key
    reference points to lm\_config\_guide.md instead of duplicating it. docs\_rules.md §8 registers the second doc.
  - Model 0000 (D-599): the first real model of the zone — the INTERCEPT-only ec20 baseline, the fully-explicit config
    (12/12 sections, 100% of the schema fields) with Roberto's values (the `_cache_` prefix, the bid 6/5 split,
    ridge 0.01, the `_checkpoint_optimize.dat` checkpoint, `high_performance_fg` true). The first run attempt failed at
    POSITIONS (the draft connection localhost/`regab` asked for a password); Roberto: use `tst_regab`@localhost, no
    password in the config — it is in `~/.pgpass` (libpq reads it automatically; the pipeline's `RegabDBConnection` also
    sets `search_path TO reversi` — the tables live in that schema). The corrected run: 19/19 levels green, 199,932
    training / 20,000 validation (0% overlap), the convergence in 5 iterations, the validation RMSE(y) 26.28 = the
    population std (the baseline is exactly what it should be), the CLIENT\_CHECK 0.0e+00. Every output under
    `build/lm/ec20/0000/` (gitignored). Committed the config + the first registry row.
  - Model 0001 (D-600): INTERCEPT + the full-board LMC, the fully-explicit config — a diff against 0000 proved
    only the identity fields and the feature set differ. Run 19/19 green: 22 parameters (W) (the dense table
    66), 40 iterations, the validation RMSE(y) 21.81 / the MAE 17.90 — against the 0000 baseline's 26.28 / 21.63:
    the RMSE down 17.0%, the MAE down 17.2%, the generalization gap -0.20 (no overfitting), the
    CLIENT\_CHECK 0.0e+00. The campaign's first real comparison: the full-board LMC alone, with 22 parameters,
    is worth a 17% RMSE. Committed the config + the registry row.
  - Model 0002 (D-601): INTERCEPT + the full-board ALMC (the side `opponent`), identical to 0001 except the
    identity fields and the mobility (a diff proved it). Run 19/19 green: 22 parameters (W) / 66 dense, 42
    iterations, the validation RMSE(y) 22.47 / the MAE 18.43, the generalization gap -0.11, the
    CLIENT\_CHECK 0.0e+00. The triangle is now readable: the ALMC alone beats the baseline by 14.4% RMSE but
    is ~3% weaker than the LMC (22.47 vs 21.81) at the identical parameter budget. Committed the config + the
    registry row.
  - Model 0003 (D-602): INTERCEPT + the standard mobility pair (the LMC + the ALMC, the same full-board
    mask), identical to 0001/0002 except the identity fields and the second mobility. Run 19/19 green: 43
    parameters (W) / 131 dense, 60 iterations, the validation RMSE(y) 20.13 / the MAE 16.47 — the best of
    the four, the generalization gap still -0.20 (no overfitting), the CLIENT\_CHECK 0.0e+00. The triangle
    answered: the ALMC is NOT redundant — a net marginal -1.68 RMSE on top of the LMC (-7.7% over the
    LMC-only model) for +21 parameters; the pair is cumulative -23.6% RMSE over the baseline. Committed the
    config + the registry row.
  - Chapter 13 (D-603): "Le feature di base" opens the part "Esperienze con il modello logistico" — the first
    experimental campaign in book form: the four minimal models on the same ec20 corpus, the results table, the
    marginal reading of the ALMC (complementary, not redundant), the no-overfitting controls. Roberto's
    structural calls: "Fondamenti" as the Part I title; the Introduzione moved BEFORE all the parts (the `\part`
    marker at the top of "La board"); the appendices lifted out of Part II with an unnumbered `\part*{Appendici}`
    (the book class makes `\appendix` inherit the active part — the reason the viewer nested them); the closing
    campaign-forecast paragraph removed; the opening sentence rewritten in his words. dict.txt +4 label
    fragments. Gates: the build 124 pages 0/0, the spell 0, the linter 0, the visual pass OK.
