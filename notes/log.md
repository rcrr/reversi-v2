# Session journal — volume 004 (sessions 90–...)

Format rules: notes/log_rules.md (rigid — follow when editing this file).

## 2026-09-29 — session 90 (I-014 + repair decisions.md + riorganizzazione overview + normalizzazione tabelle + test data + to-do list + open point out + suite counts + rules numbering + rules governance + overview\_rules + decisions\_rules + ideas preambles + language section + journal section out + D-pointer review + R-020/R-021 retirement + R-029 three-rule split + Test discipline R-022..R-028 + Pipeline contracts out + Code style ~120 + Docs chiuse + escape repair decisions.md + missing blank lines repair + format guard + guard rule R-047 + guard TUTTI i formati + closed volumes green + change discipline + tool registration + docstring section-3 + R-038 reformulation + R-040 division and move + R-045 scope + docstring cluster complete + 6 new rules + register reorder and renumber (R-010..R-860) + preamble fix — D-332/D-333/D-334/D-335/D-336/D-337/D-338/D-339/D-340/D-341/D-342/D-343/D-344/D-345/D-346/D-347/D-348/D-349/D-350/D-351/D-352/D-353/D-354/D-355/D-356/D-357/D-358/D-359/D-360/D-361/D-362/D-363/D-364/D-365/D-366/D-367/D-368/D-369/D-370/D-371/D-372/D-373/D-374/D-375/D-376/D-377/D-378/D-379/D-380/D-381)
- Session 90 (Roberto): "Punto #4 I-104, archivialo nelle idee chiuse. Non ho intenzione di farlo. Grazie" — I-014
  (l'OPTIMIZE hot-restart dal warm state del checkpoint, raised 2026-09-01 a D-096 R1: "un'ottimizzazione che
  svilupperei solo in seguito, se capiamo che ha un valore pratico") diventa DROPPED.
- IMPLEMENTATION (D-332, no code action): l'entry si sposta da notes/ideas.md a notes/ideas-closed.md, compattata in
  forma D-235 (statement + il pointer a D-332); la riga backlog dei Next steps dell'overview aggiornata nello stesso
  commit. La plumbing warm-start (lo stato L-BFGS completo nel checkpoint + i warm-start kwargs di `opt_lbfgs`) resta
  intatta, contratto della path INCOMPLETE-resume.
- JOURNAL ROTATION: il volume 003 supera entrambe le cap (52 sessioni > 25; 2588 righe > 2000) → chiuso a questo session
  boundary (range 38–89), il volume 004 si apre con questa sessione. OSSERVAZIONE (per Roberto, nessuna azione): le
  sessioni 79–89 del volume 003 sono registrate solo come bullet "- Session N (Roberto):", senza il heading "##
  YYYY-MM-DD — session N (title)" obbligatorio (log\_rules §2.1) — il volume chiuso resta verbatim salvo ordine di
  ripristino.
- VERIFICATION: commit notes-only, zero codice toccato; grep residui I-014: solo storico (decisions\_000 x2,
  notes/analyses x3) + l'entry compattata + questo pointer.
- COMMIT: un solo commit (D-332).
- Session 90 (Roberto, seconda richiesta): "Ora dobbiamo SISTEMARE decisions.md: D-236 e' l'ultima formattata
  correttamente, da D-237 la formattazione si ROMPE. Avendo allargato i caratteri per riga dire di emendare la regola a
  1000 righe. Spezza il file in 4: notes/decisions\_002.md ... notes/decisions\_005.md, sistema la formattazione con gli
  escape appropriati, e partiamo con un nuovo file decisions vuoto."
- ANALISI (il mappeggio completo del danno): (a) 36 run interni di 11 spazi in D-304/D-305/D-306 — newline + indent a 10
  spazi collassati da un join difettoso: il "token perso" e' solo il newline (il contenuto e' INTATTO; git -S: i gap
  compaiono gia' nel commit originale D-304); (b) l'header D-307 incollato all'ultima riga di D-306 (start di entry a
  metta' riga, 179 char); (c) 55 separatori blank mancanti (D-263..D-327); (d) indent di continuazione incoerenti (6
  spazi D-263..D-283, 10 spazi D-284..D-332, 11 spazi D-184/D-186/D-204 vs i 9 di casa); (e) 16 token rotti a metta'
  riga (rejoin D-209: 5 underscore, 5 hyphen, 4 slash-list, 2 dot di filename); (f) 7 prime righe > 120; (g) 15
  asterischi nudi fuori dai code span (moltiplicazioni + glob).
- IMPLEMENTATION (D-333): re-wrap uniforme di tutte le 174 entry (D-159..D-332) al formato di casa (9-space
  continuation, greedy 120 fill, token code-span-aware — `test_prng`.md atomico) + i 16 rejoin + i separatori
  ripristinati + gli escape degli asterischi (15 nuovi, la regola di rules.md: zero candidati stray-italic residui).
  Proof di conservazione per entry: il testo con whitespace e backslash rimossi e' identico prima/dopo. Emendamento: cap
  2000 -> 1000 righe (rules.md + header del log). SPLIT: 4 volumi chiusi — decisions\_002 (D-159…D-206, 884 righe),
  decisions\_003 (D-207…D-257, 865), decisions\_004 (D-258…D-300, 879), decisions\_005 (D-301…D-332, 870) — tutti < 1000;
  il nuovo decisions.md riparte vuoto con D-333 come prima entry.
- VERIFICATION: 0 righe > 120 e 0 asterischi nudi in tutti i 5 file; i 4 volumi < 1000 righe; il proof per-entry
  superato su tutte e 174 le entry; l'index dell'overview + le 4 nuove righe. OSSERVAZIONE (per Roberto, nessuna
  azione): i volumi chiusi 000/001 portano 53/99 righe di continuazione con `|` spurio + 27/52 asterischi nudi (i
  residui pre-D-237 — il formato-tabella + gli escape matematici — che il re-wrap ha tenuto come contenuto) — i volumi
  chiusi restano verbatim; un cleanup e' la sua chiamata.
- COMMIT: un solo commit (D-333).
- Session 90 (Roberto, terza richiesta): "Fai un'analisi approfondita di overview.md. Verifica i contenuti e la reale
  utilita' delle informazioni incluse. La sezione Where we are cresce continuamente, e non ha un senso secondo me: e'
  un'altra 'storia del progetto'. Non dobbiamo disseminare la storia ovunque, dobbiamo solo tenere quanto e' utile a
  gestire il progetto. ... Decisioni: 1: Current state; 2: buttiamo [il bullet e2e]; 3: facciamo ora [il re-gymnastic
  delle tabelle]; 4: regola MAX 10 bullet. Mettiamo la regola in rules: niente bullet-per-campagna ... assolutamente da
  fare. Procedi!"
- ANALISI (la proposta approvata): "Where we are" 18 -> 431 -> 18 (D-235/D-236, la stessa malattia curata una volta) ->
  172 righe / 35 bullet in 10 giorni; l'audit: 22 bullet storia di campagna (incl. i 9 "format rules land on X"), 9
  duplicati di tabelle/mirror, 4 stato reale, 2+ STALE (la contraddizione su-corpus-2/3/5, i conteggi suite 965 vs 968);
  la riga backlog dei Next steps = record delle chiusure idee (violazione "OPEN items only"); 11 celle State con
  clausole "format pass" (violazione grammatica D-117); board.py 246 vs 247 (misurato: Ran 247, skipped 15).
- IMPLEMENTATION (D-334): (1) rules.md: la sezione RINOMINATA "Where we are" -> "Current state" (l'ordine dei 8 sezioni
  invariato) + la nuova definizione — CURRENT STATE only, MAX 10 bullet, ogni bullet un fatto attuale NON nelle tabelle
  e NON nei mirror; NO bullet-per-campaign (la campagna vive in journal + decisions, il suo stato lascia la sezione
  quando la campagna finisce). (2) overview: 35 -> 4 bullet (la pipeline 19-livello live e green; la regola D-318 + la
  conversione user-directed in corso; la facade script-entry + lo stop target-driven; l'ec in un solo field root
  required — il bullet e2e BUTTATO per decisione di Roberto); il record closed-ideas fuori dai Next steps (e' in
  ideas-closed.md); il re-gymnastic delle 11 celle (hlp\_plot, wrk\_optimize, client, hlp\_config\_schemas, hlp\_gradient,
  hlp\_indexes, hlp\_optimize, hlp\_su\_analysis, hlp\_validate, hlp\_wmaps + test\_hlp\_su\_analysis) — i contratti restano (i
  13 PlotStyle knobs, hi\_perf\_blocks, il lineage su-corpus); i 2 su-corpus stale corretti (su-corpus-3 -> 5, il pin
  su-corpus-4 -> 5, verificato nel codice); board.py 246 -> 247. Nulla PERDUTO: ogni clausola tolta esiste verbatim
  nel decision log (D-306..D-331) e nei mirror — solo de-duplicata.
- VERIFICATION: notes\_format --check pulito (0 rejoin in sospeso), cross-check source-vs-test suite 0 mismatch, Current
  state 4 bullet <= 10.
- COMMIT: un solo commit (D-334).
- Session 90 (Roberto, quarta richiesta): "Ancora due cose in overview.md: 1: nella tabella Test files, dopo la entry
  test\_hlp\_optimize la tabella si rompe visivamente (le 4 entry dopo non sono formattate bene). 2: sia per i file di
  codice che per i tests, la colonna State e' da revisionare: non c'e' coerenza sulla lunghezza dello stato, ci sono
  continui riferimenti alla storia. Se una cosa e' complete e' complete."
- ANALISI: (1) la rottura e' un residuo PRE-ESISTENTE: la cancellazione della riga test\_hlp\_random\_play (D-295, commit
  eb59a3d) ha lasciato la riga vuota al posto della riga → la tabella Markdown si spezza dopo test\_hlp\_optimize (le 4
  righe successive renderizzano fuori tabella); (2) la colonna State viola la grammatica D-117 ("status word +
  open/parked items, mai la storia di campagna"): le celle sono saggi descrittivi fino a 2682 char (hlp\_su\_analysis),
  pieni di D-NNN/I-NNN, "moved from", "renamed from", "fix", "N new tests"; (3) sweep completo delle sezioni "Open
  issues" dei 95 mirror: UN solo item file-level aperto in tutto il codice (il difetto di wording dell'header
  adherence di wrk\_anova — pinned dalla probe; una source change e' in attesa della chiamata di Roberto) + il parked
  PRNG passettino (item dei Next steps); (4) le tabelle erano in ordine storico di aggiunta, in violazione
  dell'header e della regola "alphabetical by full path"; (5) bug nascosto: la cella di hlp\_su\_analysis portava una
  pipe NUDA interna ("joint | None", la type-union — violazione D-116, mai vista dai re-wrapper perche' la riga non
  matchava la forma 5-pipe).
- IMPLEMENTATION (D-335): (1) riga vuota rimossa (tabella integra); (2) tutte le 95 celle State ridotte alla
  grammatica D-117 — solo la status word + gli item aperti/parcheggiati: prng.py "parked: the last PRNG passettino
  (the ctor's init over a numba init kernel)"; wrk\_anova.py "open: the adherence header promises top-k while the
  report lists every sub-variable (pinned; a source change awaits Roberto's call)"; paths.py / tags.py "complete
  (helper module, 0 tests)"; test\_mobility da "analyzed" a "complete" (il mirror: 26 test, tutti pinned, zero open
  issues — parola residua della nascita della suite, SEGNALE a Roberto); le frasi descrittive sono il lavoro dei
  mirror (colonna Doc); (3) le due tabelle riordinate in alphabetical-by-full-path (48 src + 47 test), il parenthetic
  stale dell'header ("the package path sorts future packages first") tolto; (4) rules.md (D-117 chiarita): "a status
  word + the open/parked items (each with its governing D-pointer if any); the description is the mirror's job, the
  campaign history the decision log's" — la vecchia frase "the D-pointer range" (che aveva alimentato il gonfiore
  D-NNN) e' ritirata. Nulla PERDUTO: ogni clausola tolta esiste verbatim nel decision log e nei mirror.
- VERIFICATION: tabelle integre (0 righe vuote interne, 5 pipe non-escape per riga, ordine alfabetico per full path
  verificato), notes\_format --check pulito su overview.md + rules.md + decisions.md.
- COMMIT: un solo commit (D-335).
- Session 90 (Roberto, quinta richiesta): "Sistemiamo anche questa parte: Test data (test/reversi/data/): ... Via
  D-215, teniamo una lista a bullet con un commento di cosa sono. Breve. verifica la lista."
- ANALISI (la verifica): il paragrafo era STALE su 3 punti — (1) rlm\_01/rlm\_02 non erano piu' "i DB dump": i file
  sono stati rigenerati il 2026-09-21 come config di unit-test (il campo description di ciascuno: rlm\_01 la Design
  Matrix data structure, rlm\_02 il gradient worker); (2) mancavano 3 degli 8 file della directory: prng\_golden.txt
  (il golden PRNG, 18436 righe — misurato), rlm\_05/rlm\_06 (le config sperimentali SU-analysis, i tier 2M/100M, ec 20,
  stop a SU\_ANALYSIS — nomi e description letti dai file); (3) "the per-file mirror docs cover them" —
  docs/test/reversi/data/ non esiste, la claim e' falsa.
- IMPLEMENTATION (D-336): il paragrafo diventa la lista a bullet dei 9 file verificati, con il commento breve di
  ciascuno; via il D-215 e la "571\_141-row log verified 100%" (verifica di campagna — vive nel decision log), resta
  lo stride 1002-row (fatto attuale, misurato: 1003 righe incl. l'header).
- VERIFICATION: ogni bullet controllato sul file in disco (i nomi, i campi description, i conteggi righe),
  notes\_format --check pulito.
- COMMIT: un solo commit (D-336).
- Session 90 (Roberto, sesta richiesta): "Ora sistemiamo la sezione Next Steps: nessuno dei tre e' veritiero (VVLONG va
  riformulato, PRNG non serve, PROFILING e' gia' stato fatto). Ecco cosa inseriamo [i 6 punti]. Fai una verifica
  dettagliata, proponi le opzioni, poi ti do indicazione."
- ANALISI (la verifica dettagliata dei 6 punti): (1) TAG — 15 file / 39 call-site di db\_long\_gate, 2 file VLONG, 0
  VVLONG, PERF inline in 14 file (tecnica parallela a tags.py); il tag DB e' fuso in LONG, i tier non sono puramente
  per durata; (2) TEST — 8 file / 40 ref D-NNN nei docstring (violazione D-267: test\_hlp\_su\_analysis 23,
  test\_wrk\_final\_log\_print 7), 7 file > 120 righe; (3) MOBILITY — il concetto "difference" (DLMC =
  popcount(lms&mask) + popcount(amask) - popcount(alms&amask)) e' in mobility.py, 8 file consumatori (4 test + 4
  probe), impatto API (la tripla LMC/ALMC/DLMC, n\_configurations = k+a+1); (4) README — non esiste (root: solo
  AGENTS.md); (5) WORKERS — 10 dei 35 file lm gia' passati (D-323..D-331), restano 25 (7 con righe > 120);
  (6) CORE+TOOLS — 9 file, nessuno passato (5 con righe > 120), 90 ref D-NNN totali nel src (state\_machine 18,
  board 16). I 3 bullet attuali: PROFILING FATTO (session 58 / D-299), PRNG passettino presente nel codice ma
  one-shot, VVLONG = stato congelato (D-286) non item aperto.
- Roberto (le indicazioni): "La lista NON ha priorita', decido io l'ordine. Tu scrivi solo le cose da fare in Inglese
  in maniera sintetica. Quindi Opzione A. 1: DROP [PRNG]. 2: DROP [PROFILING]. 3: tutti vanno fatti, quando ti
  diro'. 4: non devi fare NULLA, devi solo scrivere che e' da fare [mobility]. 5: Inglese, come tutto. Non devi fare
  NULLA [README]. 6: non devi fare NULLA [durate]. Nia, stiamo scrivendo una TO-DO List, non stiamo facendo tutto."
- IMPLEMENTATION (D-337): (1) via i 3 bullet stanti — VVLONG (stato congelato, assorbito dal punto TAG), PRNG
  DROPPED (init MT one-shot, payoff numba zero), PROFILING CHIUSO (D-299); (2) i 6 punti di Roberto in Next steps, in
  Inglese, sintetici, SENZA priorita' (l'ordine lo decide lui) — i tag di durata (5 tag + tecnica da riverificare +
  analisi test equivalenti piu' brevi), i sorgenti test (formato + criteri D-267 + storia via), MOBILITY (via il
  difference: MASK + flag binario mover/opponent), il README (Inglese), il formato dei workers (TUTTI i sotto-lavori),
  il formato di board/pattern/feature/mobility + tools; (3) rules.md: la clausola D-117 "the LAST bullet is the next
  concrete action" -> "the list is NON-prioritized (Roberto picks the next item on demand)". Nulla INIZIATO: la lista
  e' scritta, ogni item aspetta la sua direzione.
- COMMIT: un solo commit (D-337).
- Session 90 (Roberto, settima richiesta): "Next step: hai tenuto due open point nei sorgenti: wrk\_anova, prng.
  Rileggili bene. A me NON risultano. Spiegami le due modifiche che hai evidenziato. Ripeto, a me non risultano. Poi
  ti dico come procedere." — e dopo la spiegazione: "1: DROP, il costruttore non e' mai critico nelle prestazioni.
  DROP FOREVER, non lo voglio piu' vedere. 2: DROP, pulisci wrk\_anova.md. Procedi!"
- ANALISI (il rileggimento): (1) prng — il "parked" era un mio errore di contabilita': l'item e' stato DROPPATO a
  D-337 ma l'ho lasciato nella cella della tabella; (2) wrk\_anova — la mia sovrattaratura del D-335: l'appunto del
  D-259 (5)(b) (l'header adherence "top {top\_k\_adherence}" vs il report che elenca TUTTE le sub-variabili, il bound
  solo sulle righe console) e' un quirk PINNATO e accettato (probe verify\_anova C6/D7, ruling "left as-is"), e la
  sezione Open issues del mirror finisce con "None." — nessun item aperto.
- IMPLEMENTATION (D-338): le due celle State -> "complete" (ora tutte le 95 celle complete, salve le 2 helper); il
  mirror wrk\_anova.md pulito — Open issues = "None." (docs\_rules §4: i closed items non appaiono in quella sezione)
  + il fatto del console/report split spostato nel bullet Architecture come contratto attuale (le righe console
  sono top-N, il report la lista completa, l'header wording il quirk pinned e deliberato); l'appunto storico vive
  nel D-259.
- COMMIT: un solo commit (D-338).
- Session 90 (Roberto, ottava richiesta): "Noto che la tabella Source files ha la colonna Suite (live DB), mentre
  Test files ha la stessa colonna. Non credo ci sia valore in questa duplicazione. Mi fai una proposta ragionata
  su come semplificare? Teniamo la conta dei TESTS solo sui tests? Tolgo commenti inutili? Mi piacerebbe che il
  nome del DOC fosse un hlink al file md. Pensaci e fammi tu una proposta." — e dopo la proposta: "1: approvo.
  2: Totale no, sarebbe da modificare in continuo. 3: OK. Procedi!"
- ANALISI (la proposta approvata): (1) la duplicazione era reale — 46/48 righe Source duplicavano la riga test 1:1,
  le uniche note vere erano i 2 "via" (base\_model, model\_weights) gia' nei mirror; (2) la colonna non aveva semantica
  precisa (run miste: test\_regab 48/0/0 sulla DB, test\_wrk\_final\_log\_print "5/0/1 (LONG: 6/0/0)" tier default);
  (3) i commenti utili erano solo 2 (i marker VLONG), il resto inutile; (4) il breakdown a 6 colonne per modulo
  sconsigliato (manutenzione x4-5 tier a ogni cambio test) — i tag e i mirror lo portano gia'; (5) hlink: verificato
  in scratch che il re-wrapper lascia i link intatti.
- IMPLEMENTATION (D-339): (1) Source: via la colonna Suite (File | State | Doc) + via la frase "Suite = ..."
  dall'header; (2) Test: casa unica dei conti con semantica stretta — "Suite (standard run)" = il conteggio nella run
  pre-commit standard (LONG=1, DB live); unico marker residuo (+1 VLONG) su 2 moduli (test\_lm\_worker\_full\_chain,
  test\_wrk\_su\_analysis); NESSUN totale (chiamata di Roberto), nessuna parentesi PERF (i test PERF sono skipped nella
  standard run e gia' contati nello skipped); (3) RI-MISURAZIONE: i 45 moduli del runner run singolarmente (LONG=1) +
  la run standard completa — tutto green: 968 tests, 0 failures, 24 skipped, 75 s; unico conteggio cambiato:
  test\_state\_machine 49 -> 50 (un test aggiunto dall'ultima verifica); test\_wrk\_final\_log\_print ora semplicemente
  6/0/0; (4) tutte le 95 celle Doc sono markdown link al mirror (il percorso pieno come label); (5) rules.md:
  D-117 emendata (il conteggio suite vive solo nella tabella Test, standard run; Doc = markdown link).
- VERIFICATION: la run standard completa 968/0/24 green; notes\_format --check pulito su tutti i file toccati; le
  tabelle renderizzano integre (header unici, link intatti).
- COMMIT: un solo commit (D-339).
- Session 90 (Roberto, nona richiesta): "Molto bene Nia! Ora entriamo nella parte piu' delicata di questa pulizia,
  affrontiamo la ristrutturazione di rules.md. Prima di tutto il titolo: rules.md — active rules ('corpo
  legislativo'). Toliamo l'Italiano. Si usa solo solo l'Inglese quindi 'legislative body'. Poi introdurrei la
  NUMERAZIONE. R-000, R001, R002 .... E spazierei i bullet con una riga vuota. R-001 e il titolo li fare BOLD.
  Partirei maiuscolo ... Poi ho altre idee ... ma prima voglio sentire il tuo parere. Fai una verifica dettagliata,
  proponi le opzioni, poi ti do indicazione su come procedere." — e sulla proposta: "Quindi facciamo SENZA DASH ...
  1: R-001 : OK / 2: OK / 3: OK / 4: ordine attuale / 5: (a) / 6: (a) / 7: (la tua raccomandazione) / 8: eliminiamo
  il BUDGET. Le RULE possono essere aggiunte solo su esplicita approvazione. Lunghezza target 1-3 linee, solo se
  necessario superiore. / 9: OK / 10: BRAVA hai capito perche' le voglio numerare, poi il reference lo mettiamo nel
  LOG, e togliamo le D dalle rules. ma per ora NON ci pensare, poi le guardiamo una per una. Procedi!"
- ANALISI (verifica + opzioni): il file = 186 righe, 9 sezioni, 46 bullet-regola + 3 sub-bullet Lifecycle (prosa,
  non numerati); 5 righe vuote finali (residuo); "corpo legislativo" solo nel titolo (l'altra occorrenza e' nel
  volume chiuso decisions\_000.md — intoccabile). Test empirico in scratch con tools/notes\_format.py: la spec
  letterale (bullet dash + titolo + descrizione indentata) NON e' stabile (il tool rifonde la descrizione sulla
  riga titolo); la variante senza dash (riga bold standalone + blank line + paragrafo) e' stabile e idempotente.
  Prototipo completo: 46 regole -> 255 righe. Urto di prefisso: R# (senza dash) e' gia' l'id dei code issue nei
  mirror.
- IMPLEMENTATION (D-340): (1) titolo "legislative body"; (2) R-001..R-046 in ordine di lettura (dash + 3 cifre,
  coerente con D/I; numeri mai riusati); (3) formato senza dash: titolo bold, blank line, descrizione 1-3 linee
  (una riga bold unica se la regola ci sta); (4) titoli euristici (primo " — " / ": ") + rifinitura manuale dei 6
  lunghi (R-006, R-038, R-040, R-042, R-043, R-044) + maiuscola iniziale della descrizione; (5) BUDGET eliminato ->
  paragrafo Governance: una regola e' aggiunta/emendata/retirata solo su approvazione esplicita di Roberto,
  R-numbers sequenziali/globali/mai riusati, target 1-3 linee; PROMOTE = "its numbered line"; (6) urto R#: la nota
  va in R-003 (dove sono definite le famiglie di riferimento, non nelle Conventions dell'overview) — "R-NNN (a rule
  of this register) ... R# (a code issue, never an R-NNN)"; (7) RINVIO (Roberto): gli R-reference nel LOG + la
  rimozione delle D dalle rules — da guardare una per una, dopo; (8) via le 5 righe vuote finali; bullet Index
  dell'overview aggiornato al nuovo formato.
- VERIFICATION: notes\_format --write idempotente + --check pulito (290 righe, 9 sezioni, sequenza R-001..R-046
  intatta); token-diff normalizzato vecchio vs nuovo = solo i cambi previsti (titolo, Budget -> Governance,
  "numbered", i titoli rifiniti, la nota R-NNN/R#) — zero contenuto perso. Trovato per strada: l'heading "## Code
  style" mancava nella prima stesura (preso dal controllo del conteggio headings, restaurato).
- COMMIT: un solo commit (D-340).
- Session 90 (Roberto, decima richiesta): "Bellissimo! Io aggiungerei uno spazio tra la fine di una RULE e la
  seguente. Sono un po' attaccate, facciamo 2 linee vuote. Poi partiamo da: [il paragrafo Governance] ... Semplifichiamo
  Nia: cosa serve questa frase: Every notes/ Markdown file is wrapped to ~120 chars/line (D-237), with atomic code
  spans; the tables and the headings stay one physical line. ??? Io la rimuoverei, a meno che tu mi spieghi la
  ragione di tenerla." — e dopo la mia spiegazione (la clausola ombrello ~120 vive solo li nel registro attivo; la
  seconda meta e' duplicata dal tool): "Cosa ne pensi di una cosa di questo genere? Governance: a rule is added,
  amended or retired only on explicit user approval. The R-numbers are sequential, global and NEVER reused ... A rule
  is a bold title line (**R-NNN — the topic**), a blank line, and a 1-3 line description ... two blank lines between
  one rule and the next. Lines are ~120 chars. When a new rules is best placed in a specific order a notation
  (**R-NNN.N — the topic**) can be used."
- IMPLEMENTATION (D-341): (1) DOPPIO SPAZIO tra le regole — i 37 confini intra-sezione a 2 righe vuote (lo spazio
  regola -> heading resta una riga); clausola aggiunta al Governance: "two blank lines between one rule and the
  next"; (2) GOVERNANCE riscritto sul testo di Roberto, con i miei 2 fix dichiarati (il refuso "a new rules" ->
  "a new rule"; i template titolo tenuti come code span per coerenza): "explicit user approval" (generalizzato da
  "Roberto's"), il ~120 minimo ("Lines are ~120 chars." — il pointer D-237 esce dal registro attivo: la regola vive
  nel log storico + il WIDTH=120 del tool + le dichiarazioni per-dominio log\_rules/docs\_rules/ideas/R-004), via la
  clausola atomic-code-spans/tabelle+heading (duplicata dal tool; R-003 la dice per le tabelle dell'overview);
  (3) NUOVA notazione R-NNN.N: una regola da inserire in posizione specifica prende il numero del genitore + suffisso
  a punto — con i genitori zero-padded il sorting testuale la colloca subito dopo il genitore (R-012.1 tra R-012 e
  R-013), mai ri-numerazione; (4) bullet Index dell'overview allineato ("explicit user approval").
- VERIFICATION: notes\_format --write idempotente + --check pulito (327 righe, 9 sezioni, sequenza R-001..R-046
  intatta, 37 doppi spazi).
- COMMIT: un solo commit (D-341).
- Session 90 (Roberto, undecima richiesta): "R-002: This file: the active legislation. Every rules stated in this
  file has precedence on other notes, documents or decisions. Departure from the rules is possible only with
  explicit consent from the user. Cosa ne pensi?"
- ANALISI: la clausola e' ben posta in R-002 (il ruolo del registro) e coerente con l'architettura: lo scope
  "other notes, documents or decisions" esclude deliberatamente la costituzione (AGENTS.md, R-001) e le istruzioni
  dirette dell'utente — la gerarchia risultante: utente > AGENTS.md > rules.md > altri notes/docs/decisions (un
  decision storico non puo' piu' sovrascrivere una regola attiva). La seconda frase COMPLETA la Governance (che
  regge l'emendamento del registro): anche il departure da una regola in vigore chiede il consenso esplicito — un
  departure accettato che persiste diventa decisione + emendamento (stesso R-number, nuovo D-number).
- IMPLEMENTATION (D-342): R-002 emendata sul testo di Roberto con 2 fix grammaticali ("Every rules" -> "Every
  rule"; "precedence on" -> "precedence over"); la descrizione e' a 3 righe (sul target 1-3).
- VERIFICATION: notes\_format --write idempotente + --check pulito.
- COMMIT: un solo commit (D-342).
- Session 90 (Roberto, dodicesima richiesta): "Ora vediamo R-003 .... Cosa ne pensi? Non ti sembra un po' lunga,
  prolissa ??? quale e' la REGOLA ... il resto VIA! Dai fammi una proposta!!!" — e sulla proposta (il file di dominio
  mancante): "OK! Via! Vai Nia!"
- ANALISI: R-003 e' 15 delle 46 righe del registro — perche' l'overview e' l'UNICO file a formato rigido senza file
  di dominio (i journal hanno log\_rules.md, i mirror docs\_rules.md, e nel registro si punta in una riga: R-005,
  R-038); il formato inlinato e' cresciuto di una clausola per campagna (D-116, D-117, D-334, D-335, D-337, D-339).
- IMPLEMENTATION (D-343): (1) NUOVO notes/overview\_rules.md — le 8 sezioni in ordine fisso, language/date, le
  famiglie di riferimento (D/I/R-NNN/T/R#/M# col "never an R-NNN"), la grammatica delle 2 tabelle (State, Suite solo
  nella Test con (+N VLONG), Doc = markdown link, \| escape, alphabetical by full path), Current state <= 10 bullet +
  no bullet-per-campaign, Next steps open + non-prioritized, Index 1 bullet per notes file — tutti i D-pointer
  viaggiano col testo; (2) R-003 -> 3 righe puntatore (entry-point + "The format is RIGID in notes/overview\_rules.md"
  — il pattern gia' usato da R-005/R-038); (3) coerenza 1 riga a testa: R-006 + overview\_rules.md, il pointer
  dell'header dell'overview (era "notes/rules.md — the overview bullet"), +1 bullet nell'Index dell'overview, +
  overview\_rules.md nel Layout di AGENTS.md.
- VERIFICATION: notes\_format --write idempotente + --check pulito (rules.md 314 righe, R-003 = 3 righe sul target;
  overview\_rules.md 42 righe).
- COMMIT: un solo commit (D-343).
- Session 90 (Roberto, terzadecima richiesta): "R-004 — notes/decisions.md Riusciamo a semplificare ?" — e sulla
  proposta (il file di dominio, stesso pattern di D-343): "procedi!"
- IMPLEMENTATION (D-344): (1) NUOVO notes/decisions\_rules.md (21 righe) — la grammatica dell'entry (una entry per
  decisione, append-only, blank line prima di ogni entry, header `D-NNN | YYYY-MM-DD | the rationale` su una riga,
  continuation indent ESATTAMENTE 9 spazi — scritta per la prima volta: la grammatica era praticata a ogni entry ma
  non legiferata da nessuna parte), i D-numbers globali/monotoni/mai riusati su log aperto + volumi chiusi, le
  clausole di stile D-209 (code span per path/nomi, asterischi escaped per le moltiplicazioni), le volumes &
  rotation (volume aperto = decisions.md, cap 1000 righe D-118 emendato a D-333, chiusura a session boundary come
  decisions\_NNN.md zero-padded, un salto di volume non taglia mai un'entry); (2) R-004 -> 2 righe puntatore
  (identity + "The format is RIGID in notes/decisions\_rules.md") — ora la regola piu' snella del registro (con
  R-005); (3) coerenza 1 riga a testa: R-006 + il file, l'header di decisions.md ("Format: D-NNN | date | ..." ->
  pointer al file di dominio), +1 bullet nell'Index dell'overview, +il file nel Layout di AGENTS.md.
- EFFETTO LATERALE: l'edit dell'header ha richiesto un --write su decisions.md, che ha normalizzato l'intero
  volume aperto al wrap canonico ~120 del tool (content-neutral: fingerprint dei token identico, idempotente) — la
  deriva hand-wrap post-D-333 e' guarita.
- VERIFICATION: notes\_format --write idempotente + --check pulito (rules.md 312 righe, R-004 = 2 righe;
  decisions\_rules.md 21 righe).
- COMMIT: un solo commit (D-344).
- Session 90 (Roberto, quattordicesima richiesta): "R-007 le regole sono duplicate nel preambolo di ideas.md.
  Propongo di rimuoverle da rules, e scrivere solo che sono nel preambolo del file. Cosa ne pensi?"
- ANALISI (verifica prima di applicare): i due preamboli (ideas.md + ideas-closed.md, entrambi "Format (D-235)")
  sono il SUPERSET delle clausole di R-007 — la grammatica di formato (header I-NNN | status | idea, 9 spazi, blank
  line, code span), la legenda degli status CON definizioni (idea/follow-up/in-progress — il registro non le aveva
  nemmeno), il lifecycle di chiusura (l'idea chiusa si sposta in ideas-closed.md, compattata a statement + D-pointer
  + outcome, nello stesso commit della decisione di chiusura, "it never stays here"; la storia vive in
  decisions.md/journal, il file chiuso e' "the I-NNN index into it, never a narrative"), i I-numbers globali/mai
  riusati — tutto nei preamboli; il registro portava la copia PIU' DEBOLE. I preamboli SONO i file di dominio
  (auto-contenuti, D-235, in entrambi i file) — nessun nuovo file serve.
- IMPLEMENTATION (D-345): R-007 -> puntatore di 2 righe: identity (OPEN backlog I-NNN; ideas-closed.md = CLOSED
  ideas done | dropped) + "The format (D-235), the status legend, the closure lifecycle and the I-numbering are in
  each file's preamble." — da 5 righe di descrizione a 2.
- VERIFICATION: notes\_format --write idempotente + --check pulito (rules.md 309 righe).
- COMMIT: un solo commit (D-345).
- Session 90 (Roberto, quindicesima richiesta): "Una change alla R-007: [il puntatore] Diventa: [il puntatore senza
  '(D-235)']. Grazie!"
- IMPLEMENTATION (D-346): micro-emendamento a R-007 — via il riferimento "(D-235)" dal puntatore (il pointer d'origine
  e' ridondante nel registro: i preamboli lo portano gia', "Format (D-235)" in entrambi i file — il riferimento vive
  dove deve); il numero resta per la Governance (emendamento = stesso R-number).
- VERIFICATION: notes\_format --write idempotente + --check pulito (rules.md 309 righe, R-007 = 2 righe di
  descrizione).
- COMMIT: un solo commit (D-346).
- Session 90 (Roberto, sedicesima richiesta): "La sezione Language & collaboration la modificherei come segue:
  [R-008: Replies to the user: his own language (e.g. Italian). / R-009 invariata / R-010: One commit per item + a
  notes-wave commit at the campaign close. / R-011 invariata] Nel caso volessi spiegare il the D-111 pattern,
  spieghiamolo qui. ma no a REFERENCES to D-XXX. Grazie!"
- IMPLEMENTATION (D-347): (1) R-008 generalizzata — "Replies to the user: Italian." -> "Replies to the user: his own
  language (e.g. Italian)." (il registro stato il principio; la costituzione AGENTS.md rule 4 tiene ancora "Italian"
  — i due sono coerenti: la lingua propria dell'utente e' oggi l'italiano, e per R-002 la costituzione sta sopra il
  registro); (2) R-010 — via il reference "(the D-111 pattern)": mia scelta sulla spiegazione inline offertami = NON
  serve, la regola e' auto-contenuta (un D per campagna, un commit per item, il notes-wave commit = il commit
  raggruppato degli aggiornamenti notes che chiude la campagna); il pointer era pura provenance — lo stesso
  principio di D-346 (no D-XXX nei rules, spiegazione inline solo se la regola non si spiega da se'); (3) R-009 /
  R-011 intatte, come proposto.
- VERIFICATION: notes\_format --write idempotente + --check pulito (rules.md 309 righe).
- COMMIT: un solo commit (D-347).
- Session 90 (Roberto, diciassettesima richiesta): "Nia! Non hai rimosso (D-002), (D-004; AGENTS rules 2–3),
  (D-154). Vanno rimossi! Grazie."
- IMPLEMENTATION (D-348): il mio oversight del D-347 — ho rimosso solo il D-111 discusso esplicitamente, lasciando i
  3 gia' presenti nel testo proposto; ora via: (D-002) da R-008, (D-004; AGENTS rules 2–3) da R-009 (con il pointer
  AGENTS), (D-154) da R-011 — le tre regole sono pure: il principio, nessun reference. Contati dopo il commit: 46
  ref D-XXX restano nel registro (Layout & tree, Naming & platform, Test discipline, Pipeline contracts, Docs, Code
  style) — in attesa della chiamata di Roberto per la sweep completa (il "poi le guardiamo una per una" di D-340).
- VERIFICATION: notes\_format --write idempotente + --check pulito (rules.md 309 righe).
- COMMIT: un solo commit (D-348).
- Session 90 (Roberto, diciottesima richiesta): "La sezione 'Journal' contiene solo la R-046. [il testo] Che e'
  ridondante con la R-005. Rimuoviamo completamente la sezione 'Journal'. Grazie!"
- ANALISI: verificato prima di rimuovere — 3 dei 4 fatti di R-046 sono gia' in log\_rules.md (il session numbering
  globale, 25 sessioni / 2000 righe per volume, rotazione solo a session boundary); il quarto ("the step-N entries")
  e' una pratica ABBANDONATA — misurato: 48 occorrenze solo in log\_001, 0 negli altri 4 volumi (incluso l'attuale),
  e non e' legiferata in log\_rules.md (la pratica attuale e' il bullet piatto). R-005 porta gia' il pointer al file
  di dominio — la rimozione perde nulla di attivo.
- IMPLEMENTATION (D-349): sezione "Journal" via, R-046 ritirata — il numero lascia il gap (Governance: "a retirement
  leaves the gap", no renumbering); il registro e' ora 45 regole in 8 sezioni (302 righe), l'ultima regola e' R-045
  (Code style).
- VERIFICATION: notes\_format --write idempotente + --check pulito; nessun reference R-046 vivo fuori dalle entry
  storiche (che documentano lo stato al loro tempo).
- COMMIT: un solo commit (D-349).
- Session 90 (Roberto, diciannovesima richiesta): "Proseguiamo con la review per regola. R-012 — [il testo] Diventa:
  [il testo senza (D-003), (D-009), (AGENTS rule 7)]. Grazie!"
- IMPLEMENTATION (D-350): primo item della review per-regola (il "poi le guardiamo una per una" di D-340, che riparte
  qui): R-012 applicata sul testo di Roberto — il titolo perde (D-003), la descrizione perde (D-009) e il pointer
  AGENTS rule 7; la regola e' ora pura (workspace git repo, .gitignore minimo, scratch/ disposable e mai tracked) — i
  3 pointer erano provenance pura (i fatti operativi li portano AGENTS.md e il .gitignore stesso). Ref D-XXX nel
  registro: 44 (erano 46 a D-348).
- VERIFICATION: notes\_format --write idempotente + --check pulito (rules.md 301 righe).
- COMMIT: un solo commit (D-350).
- Session 90 (Roberto, ventesima richiesta): "Proseguiamo con la review per regola. R-013 — [il testo] Diventa:
  [il testo senza (D-006), (D-008; D-133: ...), (D-273)]. Grazie!"
- IMPLEMENTATION (D-351): secondo item della review per-regola: R-013 sul testo di Roberto con UN fix dichiarato —
  la parentesi di chiusura orfana residua della rimozione "(D-008; D-133: ...)" (la riga legge "the tools/ and lm/
  subpackages; the unit tests ..."); `reversi` resta code span (la forma del file). La regola e' ora pura: tutti i
  sorgenti Python sotto src/, il package `reversi` sotto src/reversi/, core a top level + subpackage tools/ e lm/,
  i test in test/ a root tree che specchia src/ uno a uno. Ref D-XXX nel registro: 41 (erano 44 a D-350).
- VERIFICATION: notes\_format --write idempotente + --check pulito (rules.md 301 righe).
- COMMIT: un solo commit (D-351).
- Session 90 (Roberto, ventunesima richiesta): "Proseguiamo con R-014 e R-015. [i testi] Diventano: [R-014 senza
  (gitignored) nel titolo e senza (D-010, D-011); R-015 senza (D-007) e (D-273)]. Grazie!"
- IMPLEMENTATION (D-352): items 3+4 della review per-regola, entrambi sul testo di Roberto. R-014 ora: il .venv a
  workspace root + pyproject.toml la forma minimale editable-install con i requisiti impliciti dichiarati quando si
  incontrano — via anche "(gitignored)" dal titolo (il fatto lo porta il .gitignore stesso, stessa logica di
  R-012); R-015 ora la mirror rule nella forma piu' pura: src/reversi/X.py -> docs/src/reversi/X.md, i test file
  specchiano allo stesso modo (i pointer (D-007)/(D-273) via — la mirror rule vive in AGENTS.md rule 5 e nell'albero
  docs/ stesso). Ref D-XXX nel registro: 38 (erano 41 a D-351).
- VERIFICATION: notes\_format --write idempotente + --check pulito (rules.md 300 righe).
- COMMIT: un solo commit (D-352).
- Session 90 (Roberto, ventiduesima richiesta): "Proseguiamo con R-016. [il testo] Diventa: [tools/ holds the
  maintenance tools — i 3 tool, la distinzione NOT-package-tools/NOT-probes, il test a/b/c, il pointer a
  notes/tools.md — senza (D-248), (D-133) e la parentesi dei 4 requisiti]. Grazie!"
- IMPLEMENTATION (D-353): item 5 della review per-regola, sul testo di Roberto: il titolo perde "(workspace root)"
  (il fatto lo porta il Layout di AGENTS.md e la clausola "It is NOT the package's src/reversi/tools/" della regola
  stessa) e "MAINTENANCE" diventa minuscolo; la descrizione perde (D-248) e (D-133) e il riassunto "(the four
  requirements — ...)" di notes/tools.md — il file di dominio porta i suoi 4 requisiti, il registro punta (il
  pattern R-003/R-004/R-007). Ref D-XXX nel registro: 36 (erano 38 a D-352).
- VERIFICATION: notes\_format --write idempotente + --check pulito (rules.md 299 righe).
- COMMIT: un solo commit (D-353).
- Session 90 (Roberto, ventitreesima richiesta): "Proseguiamo con R-017. [il testo] Diventa: [la regola senza il
  (D-176) finale]. Grazie!"
- IMPLEMENTATION (D-354): item 6 della review per-regola, sul testo di Roberto: unico cambio = il pointer (D-176)
  via dalla fine della descrizione; il titolo MANTIENE "(gitignored)" (a differenza del titolo di R-014, qui la
  gitignored-ness di build/ fa parte del ragionamento della regola: i dati ci stanno PERCHE' la cartella e'
  gitignored — il contratto del clone self-contained). La sezione Layout & tree e' ora tutta pura: R-012..R-017
  senza alcun D-pointer. Ref D-XXX nel registro: 35 (erano 36 a D-353).
- VERIFICATION: notes\_format --write idempotente + --check pulito (rules.md 299 righe).
- COMMIT: un solo commit (D-354).
- Session 90 (Roberto, ventiquattresima richiesta): "Proseguiamo con R-020 and R-021. I le eliminerei. Non mi
  sembrano piu' attuali. Grazie!"
- ANALISI (verifica prima di agire): i due ARGOMENTI sono ancora in forza nel codice — A2030/A2050 sono etichette di
  classi di test vive (TestFullChainA2030/TestFullChainA2050 in test/reversi/lm/test\_lm\_worker\_full\_chain.py) e gli
  helper `*_for_current_level` sono iniettati dalla StateMachine e consumati da 7 worker — ma entrambe le convenzioni
  sono gia' canonizzate nella loro casa legittima, la sezione Conventions di docs/src/reversi/lm/logistic\_model.md
  (la clausola A2xxx "intentional, not a typo — do not 'fix'", e il contratto injected-cache-helper con la nota della
  trappola R1): la retirement non perde nulla, il registro duplicava convenzioni di livello codice che il mirror doc
  possiede. Quello che era davvero stantio era il pointer: "the session-21 review" (una sessione one-shot di
  campagna) e (D-069).
- IMPLEMENTATION (D-355): R-020 e R-021 RETIRED — rimosse dal registro, i gap R-020/R-021 sono permanenti (i numeri
  non si riusano). Regole in vigore: 45 -> 43. Ref D-XXX nel registro: 34 (erano 35 a D-354). La sezione Naming &
  platform ora contiene solo R-018 e R-019.
- VERIFICATION: notes\_format --write idempotente + --check pulito (rules.md 290 righe).
- COMMIT: un solo commit (D-355).
- Session 90 (Roberto, ventiquintesima richiesta): "Proseguiamo con la sezione 'Naming & platform'. [il testo
  attuale di R-018/R-019]. Diventa: [R-018 = 'Reversi (othello), NOT chess', (A-H)/(1-8), H8 = bit 63, senza
  (D-013, D-014); R-019 senza (D-022)]. Grazie!"
- IMPLEMENTATION (D-356): gli ultimi 2 ref D-pointer della sezione Naming & platform. R-018: il titolo guadagna
  "(othello)"; la descrizione guadagna i range A-H/1-8 e l'H8 = bottom-right = bit 63, e perde il pointer
  (D-013, D-014) e l'imperativo "do not reorder or rename" (quella convenzione e' posseduta da notes/naming.md, a
  cui la regola punta). R-019: (D-022) via. Un fix dichiarato: "row(1-8)" nel testo di Roberto -> "row (1-8)"
  (spazio coerente con "column (A-H)"). La sezione Naming & platform e' ora tutta pura. Ref D-XXX nel registro: 32
  (erano 34 a D-355).
- VERIFICATION: notes\_format --write idempotente + --check pulito (rules.md 290 righe).
- COMMIT: un solo commit (D-356).
- Session 90 (Roberto, ventiseiesima richiesta): "FAmmi una prosta lean and clean per R-029 per favore. Poi la
  valuto e ti dico come procedere. Grazie!" — proposta lean da 7 linee (esempi A2050/1e6/1e7 via, nomi dei
  predicate via, enumerazione dell'ordine ridotta a "canonical order", (D-130; D-256) e (D-036) via); verificata la
  fonte: l'header di run\_utests.sh porta gia' i contenuti dei tier + la regola di inserimento, l'ordine canonico e'
  nel MODULES array.
- Session 90 (Roberto, ventisettesima + ventottesima richiesta): "E se facessimo tre RULES ??? [R-029 Suite tiers /
  R-029.1 Canonical order / R-029.2 Before git commit, testo completo]. Cosa ne pendi ?" / "Procedi!"
- IMPLEMENTATION (D-357): R-029 SPLIT in tre regole sul testo integrale di Roberto, zero fix dichiarati. Motivo
  strutturale (la mia endorsement): il "mostro" era tre contratti INDIPENDENTI fusi in una regola — la semantica dei
  tier (cumulativita' + ortogonalita' + single source test.reversi.tags + obbligo di sync), l'ordine canonico dei
  moduli del runner, l'obbligo di pre-commit — ciascuno violabile e controllabile da solo. R-029 mantiene numero e
  contratto dei tier; R-029.1 e R-029.2 sono REGOLE NUOVE col sub-numbering R-NNN.N creato a D-341 (parent
  zero-padded: ordinano testualmente prima di R-030, piazzamento in fondo alla sezione Test discipline corretto).
  Regole in vigore: 43 -> 45. Ref D-XXX nel registro: 30 (erano 32 a D-356).
- VERIFICATION: notes\_format --write idempotente + --check pulito (rules.md 296 righe).
- COMMIT: un solo commit (D-357).
- Session 90 (Roberto, ventinovesima richiesta): "Proseguiamo con la sezione 'Test discipline'. Mi fai una proposta
  di semplificazione, pulizia, revisione per R-022..R-028. La valuto e ti do indicazioni poi su come procedere.
  Grazie!" — proposta lean di 7 regole (7 ref D-XXX via: D-065/D-085/D-080/D-130/D-036/D-100/D-124/D-127); 3 punti
  lasciati al giudizio di Roberto: (1) R-025 fusa in una riga bold, (2) R-028 tolleranze via dal titolo (vivono nei
  costanti REL\_TOL/ABS\_TOL di closecheck.py), (3) R-024 hint semantico mantenuto ("the SKIP\_REGAB\_DB + LONG-tier
  check" e' il contratto, non la provenance). Verifiche nel codice prima di proporre: closecheck.py porta le
  tolleranze, paths.py esporta WORKSPACE\_ROOT + CUSTOM\_TMP\_BASE, il corpo di db\_long\_gate in tags.py conferma
  l'ordine della parentetica.
- Session 90 (Roberto, trentesima richiesta): "R-022, R-023, R-024, R-025: OK. Mi spieghi cosa significa in pratica
  'no performance gates in any suite' — non capisco il termine gate. R-026: Ok, ma e' davvero applicata? Mi dici
  dove. R-027: OK. R-028: perche' dobbiamo dire 'The multi-threaded OpenBLAS ddot is not bit-portable...'? tutti i
  float hanno il problema — scriviamo che i golden sui float per essere robusti devono usare assert\_close.
  Procedi con gli OK, e fammi una proposta migliore per la R-028."
- IMPLEMENTATION (D-358): applicati al pixel i 6 OK — R-022 title-only ((D-065) via); R-023 titolo ((D-085) via),
  descrizione intatta (già lean); R-024 (D-080, D-130: ...) via MA hint semantico mantenuto; R-025 FUSA in una riga
  bold (titolo + descrizione dicevano la stessa cosa, il (D-036) via); R-026 (D-100) via; R-027 (D-124) via.
  R-028 NON toccata — in attesa del verdetto sulla proposta migliorata (tutti i float, assert\_close per robustezza,
  via la frase OpenBLAS: il rationale completo sta gia' nell'header di closecheck.py, nulla si perde). Domanda R-026
  verificata nel codice: il gate uniforme @validate\_call(config=ConfigDict(arbitrary\_types\_allowed=True)) c'è e
  c'è — 38 applicazioni in src/reversi/lm/wrk\_\*.py (+ arbitrary\_types\_allowed in base\_model.py e pattern.py), e i
  test patchano le factory PER NOME nello namespace del modulo importatore (test\_logistic\_model.py:
  patch('reversi.lm.logistic\_model.wrk\_config', ...), wrk\_positions, wrk\_features, ...). Ref D-XXX nel registro:
  24 (erano 30 a D-357).
- VERIFICATION: notes\_format --write idempotente + --check pulito (rules.md 294 righe).
- COMMIT: un solo commit (D-358).
- Session 90 (Roberto, trentunesima richiesta): "Ho capito Nia, quindi R-025 va benissimo come e'. OK. R-026: ho
  capito, benissimo. OK! R-028: OK la tua proposta. Ottimo!"
- IMPLEMENTATION (D-359): R-028 applicata col testo approvato — titolo: "Float64 pipeline-metric goldens" -> "Float
  goldens" (il problema e' di tutti i float, non solo float64), le tolleranze (rel 1e-9 / abs 1e-12) via dal titolo
  (sono i costanti REL\_TOL/ABS\_TOL in closecheck.py — il codice le possiede), (D-127) via; descrizione: via la frase
  OpenBLAS ddot (il meccanismo non e' la regola — il rationale completo: lo studio ULP, il drift <=4e-14,
  l'enumerazione dei pin che restano esatti, sta gia' nell'header di closecheck.py) e via l'esempio
  "(train\_loss, g\_norm, the tps read-back truncations)" (restano le classi); resta il WHAT (float goldens ->
  assert\_close, tolleranze in closecheck.py) e il CONFINO (cosa resta bit-exact assertEqual — senza, domani
  qualcuno potrebbe "riparare" i golden int/sha3). LA SEZIONE TEST DISCIPLINE E' ORA TUTTA PURA: R-022..R-029.2
  senza alcun D-pointer. Ref D-XXX nel registro: 23 (erano 24 a D-358).
- VERIFICATION: notes\_format --write idempotente + --check pulito (rules.md 294 righe).
- COMMIT: un solo commit (D-359).
- Session 90 (Roberto, trentaduesima richiesta): "Nia, ottimo lavoro!!! Ora affrontiamo la sezione 'Pipeline
  contracts (RLM)'. Ho una idea radicale, secondo me nulla di questa sezione deve rimanere nel file rules.md. Ogni
  regola e' documentazione che deve essere specificata in uno dei tre moduli: state\_machine, base\_model,
  logistic\_module. Fai una analisi accurata, dettagliata. dammi il tuo parere in merito. E se sei d'accordo, fammi
  una proposta delle modifiche alla documentazione dei sorgenti python o dei mirror docs. Procedi per favore."
- ANALISI (verifica per-regola contro codice + mirror doc): TUTTE E 8 le invarianti sono GIA' canonizzate nei
  mirror doc — R-030 sentinel (state\_machine.md Architecture + invariants + logistic\_model.md "The CREATED
  sentinels"); R-031 failure semantics (state\_machine.md); R-032 unique names (state\_machine.md); R-033 gate split
  (state\_machine.md "The move gate is separate from execution" + commento state\_machine.py:373); R-034 blackboard
  (logistic\_model.md Architecture + Conventions); R-035 cache flow (cache\_manager.md + state\_machine.md "Cache
  path" + state\_machine.py:178); R-036 bool (state\_machine.md); R-037 target-driven stop (base\_model.md mezza
  generica + logistic\_model.md mezza dominio). Bonus: la copia del registro era gia' IN DERIVA — "8192-chunk
  verify" di R-035 e' un fossile (8192 non esiste piu' nel codice: binio usa chunk\_size = 1 << 20, binio.md lo
  documenta). Parere: CONSENTO — pattern della casa (R-006 "points at them, never duplicates them", il precedente
  D-355), invarianti di modulo specifico, deriva evitata. Correzione al framing: le posseggono 5 doc (state\_machine
  x5, base\_model, logistic\_model x2, cache\_manager, binio), non 3 moduli — e quindi ZERO modifiche a sorgenti o
  mirror doc: aggiungere testo sarebbe duplicazione.
- IMPLEMENTATION (D-360): R-030..R-037 RETIRED + heading "## Pipeline contracts (RLM)" rimosso (la sezione
  svuotata esce, come la sezione Journal a D-349); i gap R-030..R-037 sono permanenti. Regole in vigore: 45 -> 37.
  Ref D-XXX nel registro: 14 (erano 23 a D-359).
- VERIFICATION: notes\_format --write idempotente + --check pulito (rules.md 248 righe).
- COMMIT: un solo commit (D-360).
- Session 90 (Roberto, trentatreesima richiesta): "Proseguiamo con la sezione 'Code style'. Una sola regola, la
  R-045. Sono del parere che vada mantenuta, ma semplificata. Diciamo come devono essere le linee di codice.
  fine. Mi fai una proposta di semplificazione, pulizia, revisione. La valuto e ti do indicazioni poi su come
  procedere. Grazie!" — proposta: 3 linee, il cuore (convenzione locale ~72-76 / default PEP8 79 / guard sul
  reflow), i ref D via.
- Session 90 (Roberto, trentaquattresima richiesta): "Nia, credo ci sia un fraintendimento. Io voglio le righe a
  circa 120 caratteri... non circa 72-76. Scriviamo semplicemnte questo. Le righe hanno una larghezza di circa
  120 caratteri. Semplice no ? Riformula la proposta per favore."
- Session 90 (Roberto, trentacinquesima richiesta): "Proposta accettata. la regola va bene come da te proposta."
- IMPLEMENTATION (D-361): R-045 AMENDED — cambio di CONTENUTO, non solo rimozione di pointer: la larghezza target
  delle linee di codice e' ORA ~120 (una larghezza unica per tutto il workspace: codice = docs = notes, coerente
  col paragrafo Governance "Lines are ~120 chars." e con la WIDTH=120 di notes\_format.py), al posto di
  "convenzione locale del file (lm ~72-76) / default PEP8 <=79 se senza convenzione". Via anche: la frase di
  contesto sul linter, il precedente (D-314), la frase docs/notes ~120 (D-237 — fuori scope, la portano la
  Governance e il tool), e il guard sul reflow (la protezione c'e' gia' in AGENTS.md rule 3: i sorgenti si
  toccano solo su richiesta esplicita — il reflow non richiesto resta vietato; il reflow integrale a ~120 dei
  file oggi a 72-76 resta un atto deliberato di Roberto, il pattern D-314). Code style e' ora una riga bold
  unica. La review per-regola (D-340) e' arrivata all'ULTIMA sezione: Docs (R-038..R-044). Regole in vigore: 37
  (invariata — e' un'amendment). Ref D-XXX nel registro: 12 (erano 14 a D-360) — tutti i ref restanti stanno
  nella sezione Docs.
- VERIFICATION: notes\_format --write idempotente + --check pulito (rules.md 243 righe).
- COMMIT: un solo commit (D-361).
- Session 90 (Roberto, trentaseiesima richiesta): "Proseguiamo con la sezione 'Docs'. R-038 to R-044. Servono ?
  Non sono un duplicazione di quanto scritto in docs\_rules ? Non sarebbe meglio avere una sola entry che
  prescrive di applicare i docs\_rules ai docs ? Mi fai una proposta di semplificazione, pulizia, revisione.
  La valuto e ti do indicazioni poi su come procedere. Grazie!" — proposta: mappatura per-regola contro
  docs\_rules.md (letto per intero) + probe\_rules.md; "una sola entry" regge per il lato mirror-doc (R-038
  identity + pointer, R-039 retired), R-040..R-044 restano come regole pure di code style (sono sui docstring
  /commenti nei .py, non su docs/).
- Session 90 (Roberto, trentasettesima richiesta): "Applica la tua proposta. E' un ottimo passo in avanti. Non
  sono sicuro sia definitivo. Poi rivedo tutto e ti dico. Intanto applicala per favore."
- IMPLEMENTATION (D-362): proposta applicata al pixel. R-038 -> "The mirror docs (docs/)": identity + pointer
  al pattern R-003 (il mapping src->docs lo portano AGENTS rule 5 + R-015). R-039 RETIRED: duplicazione al
  100% di docs\_rules.md §3.4 parola per parola, e il suo pointer "(docs\_rules.md §4, D-114)" era STALE (nel
  file attuale e' §3.4, il §4 e' "Forbidden"); gap permanente. R-040..R-044 MANTENUTE come regole pure di
  code style (stesso genere della R-045 di D-361) con i ref D via: R-040 (D-224/D-226); R-041 (D-267/D-270 ->
  "the test and probe docstrings keep their own rules, below", via "like the D-314 reflow" e D-317/D-318);
  R-042 (via gli esempi D-150/D-146 e D-269/D-270 — il "the D-106 re-pin" CITATO resta: e' l'esempio di cosa
  sia la provenance, non il pointer della regola); R-043 (D-267); R-044 (D-270). R-043/R-044 restano separate
  (R-044 ha la sua eccezione e punta a "the test-doc rules"). Regole in vigore: 37 -> 36. Linee D-XXX nel
  registro: 12 -> 1, e quella e' l'esempio citato in R-042: il registro non porta piu' NESSUN pointer di
  provenance reale — LA REVIEW PER-REGOLA (D-340) E' COMPLETA. Nota: Roberto la ritiene non necessariamente
  definitiva — rivedra' tutto il registro e dara' indicazioni.
- VERIFICATION: notes\_format --write idempotente + --check pulito (rules.md 236 righe).
- COMMIT: un solo commit (D-362).
- Session 90 (Roberto, trentottesima richiesta): "Nia, per favore sistema intanto che decido come procedere il file
  decision. Nel testo di D-334 | 2026-09-29 ... si perde la formattazione e tutto diventa corsivo dalla parola
  hlp\_anova, mancano gli escape. Ma non lo abbiamo messo nelle regole di editing che devi usare gli escape ?"
- ANALISI (root cause): NON gli asterischi, ma gli UNDERSCORE. La regola di escape D-209 (decisions\_rules.md,
  bullet Entries: "backslash-escaped asterisks ... so the Markdown renders without stray italics") copre solo gli
  asterischi; gli identificativi snake\_case NUDI nel prosa toggleano l'enfasi del renderer (un underscore
  non-escape apre/chiude il corsivo). D-334 porta 12 underscore nudi: la prima coppia (quello in hlp\_anova ...
  quello in hlp\_plot) e' la lunga stirata di corsivo che Roberto ha visto.
- IMPLEMENTATION (D-363): escaped tutti gli underscore nudi del volume aperto (222) + i 2 asterischi nudi (il
  wrk\_\*.py di D-358/D-359); le due citazioni deliberate **R-NNN** (D-341) intatte; gli identificativi in
  backtick intatti. Side effect dichiarati: (1) il re-wrap canonico ha normalizzato le entry D-355..D-362
  hand-wrapped (content-neutral, token-identico); (2) il re-wrap ha esposto una BULLET TRAP — la riga che inizia
  con "36. D-XXX..." letta come bullet numerato dal tool (la sua regex ^\s\*(?:-|\d+\.)\s) -> indent a 13 spazi;
  risolta riwordando la clausola tra parentesi ("...rules in force 37 -> 36). D-XXX lines..."), unico cambio a
  livello di contenuto.
- VERIFICATION: 0 linee con indent 10+ spazi, 0 linee che iniziano per cifra+punto, notes\_format --write
  idempotente + --check pulito (508 righe).
- COMMIT: un solo commit (D-363).
- Session 90 (Roberto, trentanovesima richiesta): "Mancano le spaziature ora. Ogni Decision e' preceduta da una
  riga vuota. mancano ... Sono stanco Nia di fare il 'cane da guardia', come facciamo a essere sicuri che fai le
  cose bene ? Possiamo scrivere un PROGRAMMA in Python che testa i formati. Dopo ogni editing lo lanci per
  controllo. Proponi tu qualcosa di definitivo. Perdiamo ore su queste stupidaggini."
- ANALISI: 29 header D-NNN (D-335..D-363) senza la riga vuota obbligatoria prima — bug di append SISTEMATICO:
  ogni entry che ho aggiunto in questa sessione e' stata unita alla precedente con un newline solo invece della
  riga vuota (verificato in git: il commit D-362 portava gia' 28 dei 29). notes\_format --check NON testa la
  struttura delle righe vuote -> verde a ogni turno: questo e' il gap.
- IMPLEMENTATION (D-364): riga vuota ri-inserita prima di ciascuno dei 29 header. PROPOSTA (in tavola, sua call
  — e' codice, AGENTS rule 3): tools/notes\_lint.py, il test dei formati read-only, da lanciare dopo OGNI edit
  dei notes (rosso = no commit). Le tre classi di bug della sessione diventano codici lint: (1) struttura righe
  vuote (una prima di ogni header D-NNN, niente doppie); (2) disciplina degli escape (niente underscore nudi e
  asterischi disabbinati fuori dai code span — regola D-209 estesa ai snake\_case); (3) bullet trap (niente
  continuation che inizia per cifra+punto, pipe, hash, dash); piu' grammatica entry (regex header, continuation a
  9 spazi, D-numbers monotoni), width <= 120, idempotenza rispetto a notes\_format --write; gli stessi check
  adattati per rules.md (header R-NNN, spaziatura a 2 righe vuote, D-pointer reali flaggati) e il journal
  (grammatica session-block, continuation a 2 spazi, escape). L'estensione della regola di escape in
  decisions\_rules.md (underscore) viaggia dentro.
- VERIFICATION: 0 header senza riga vuota, 0 doppie righe vuote, re-wrap canonico + --check pulito (558 righe).
- COMMIT: un solo commit (D-364).
- Session 90 (Roberto, quarantesima richiesta): "Ok, PROCEDI." (l'approvazione della proposta del checker, D-364)
- IMPLEMENTATION (D-365): tools/notes\_lint.py — il guard dei formati, read-only, exit 0/1, da lanciare dopo ogni
  edit dei notes (default: decisions.md + rules.md + journal aperto; i volumi chiusi su richiesta esplicita). Le
  tre classi di bug della sessione sono codici permanenti: BLANK (riga vuota prima di ogni D-NNN, niente doppie),
  ESC (nessun underscore nudo e nessun asterisco disabbinato fuori dai code span — la D-209 estesa ai
  snake\_case), TRAP (nessuna continuation che inizia per cifra+punto, dash, hash, pipe, D-NNN-pipe); più
  HEADER/INDENT/SEQ, RHEAD/RTITLE/RSPACE/DPOINTER/RSEQ (i R-NNN.N ordinati dentro il loro genitore),
  JH1/JPOINTER/JSESSION/JINDENT/JBLANK, WIDTH, EOF, CANON (il file deve essere il proprio rendering notes\_format
  --write: il --check da solo non basta — passa anche sui file non canonici, scoperto durante il build).
- DOGFOOD: i fixture in scratch/lint\_fixtures (disponibili) riproducono i bug della sessione -> tutti i codici
  scattano (9+2+3 violazioni); i file reali passano verdi.
- PRIMI COLPI SUI FILE REALI (riparati nello stesso commit): rules.md 34 underscore nudi escape (i pointer dei
  domain files, gli identificativi di codice); journal aperto 196 underscore + 2 asterischi escape + una
  continuation a 1 spazio corretta a 2 (lo slip del hand-wrap al turn D-362, linea 516). I volumi chiusi
  (decisions\_000..005 + journal chiusi) non sono nel set default — malattia nota, call parcheggiata.
- REGOLA: il bullet di escape in decisions\_rules.md esteso (asterischi E underscore, D-209 estesa a D-365) —
  regola e applicatore nati insieme.
- VERIFICATION: notes\_lint verde sul set default (exit 0), fixture rosso su tutti i codici impiantati,
  notes\_format --write idempotente sui file toccati.
- COMMIT: un solo commit (D-365).
- Next: IN ATTESA: (a) la call di Roberto per codificare "notes\_lint verde prima del commit" in AGENTS.md + il
  bullet tools/ della layout (territorio suo); (b) la riveduta completa del registro (Roberto); (c) i 6 item
  della to-do list (D-337); (d) volumi chiusi + journal chiusi: la malattia degli underscore nudi (parcheggiata).
- Session 90 (Roberto, quarantunesima richiesta): "Prima di tutto OTTIMO! ben FATTO. Ora a me pare che dovrebbe
  andare in rules.md piuttosto che in AGENTS.md ... ma la regola VA MESSA. Poi ti chiedo ... tools/notes\_lint
  ... serve solo per decisions ... corretto ? Non per logs o per overview ... o rules .... Corretto ? Non sarebbe
  meglio dargli un NOME APPROPRIATO pre\_checkin\_guard\_decisions.py ??? E scrivere nella sua documentazione che
  IMPLEMENTA I CONTROLLI GRAMMATICALI per decisions .... E poi non dovremmo farne uno equivalente per ogni altro
  FORMATO (overview, rules, ...) ... cosa ne pensi ?"
- IMPLEMENTATION (D-366): R-047 "The notes format guard" in rules.md (la sua call: rules.md, non AGENTS.md — il
  suo file di standing instructions resta territorio suo). Posizionamento: nuova sezione finale "Notes format
  guard" (una regola, sezione sua — il precedente Code style/R-045), NON la sezione Roles: il guard e' una regola
  di processo, non il ruolo di un file, e l'append in coda preserva l'invariante file-order == number-order (il
  check RSEQ). La docstring del tool dice ora esplicitamente che IMPLEMENTA I CONTROLLI GRAMMATICALI dei tre
  formati notes (decisions per decisions\_rules.md, il registro per la Governance, i journal per log\_rules.md).
- LE TRE RISPOSTE (in attesa delle sue call): (1) SCOPE — non e' decisions-only: il set default gia' copre
  decisions aperto + registro + journal aperto (volumi chiusi su richiesta esplicita); quel che NON copre ancora:
  overview + i domain rule files. (2) NOME — un nome decisions-only (pre\_checkin\_guard\_decisions.py)
  incaschierebbe lo scope sbagliato; la mia raccomandazione: mantenere notes\_lint.py (corto, accurato, famiglia
  notes\_format.py) — la sua call. (3) GUARD PER FORMATO — un solo guard, linter per formato dentro (le funzioni
  lint\_decisions/lint\_rules/lint\_journal sono l'unita' modulare, non il file): l'estensione prevista = linter
  overview (grammatica rigida in overview\_rules.md: 8 sezioni, tabella, reference families) + domain rule files,
  nello stesso tool — mai N tool; la sua call su quando.
- VERIFICATION: notes\_lint verde su tutto (exit 0) dopo l'aggiunta di R-047; registro 37 regole, 8 sezioni,
  246 righe.
- COMMIT: un solo commit (D-366).
- Session 90 (Roberto, quarantaduesima richiesta): "Lo hai messo in rules, e' il posto giusto. In fondo: non mi
  convince, e le tue motivazioni ANCORA MENO. Lo hai messo in fondo solo perche' e' comodo. Perche' e' comodo ?
  Perche' ci siamo dati la regola che le RULES sono in ordine PROGRESSIVO. Che non va bene. La rule e' troppo
  complicata. SBAGLIATISSIMO. Devi dire lancia la guardia. FINE. La REGOLA e': 'LANCIA LA GUARDIA. Se fail no
  checkin.' Ma di tutto questo NON fare NULLA. Ci sto pensando a cosa fare. (a) OK. (b) costruisci ora i controlli
  grammaticali stringenti per tutti i files in notes. TUTTI. Procedi per favore."
- NOTE: di tutto il blocco sulla regola (il testo "LANCIA LA GUARDIA. Se fail no checkin.", il posizionamento,
  l'invariante di ordine progressivo che lui dichiara sbagliata) NON ho toccato NULLA — congelato, in attesa della
  sua decisione. (a) = nome confermato: notes\_lint.py.
- IMPLEMENTATION (D-367): il guard ora copre TUTTI i formati dei notes — un solo tool, linter per formato. Linter
  nuovi: OV- (overview.md: l'H1, la sezione Format rules, le OTTO sezioni nell'ordine canonico esatto, le due
  tabelle a riga fisica unica + ordine alfabetico per path, Current state MAX 10 bullet, Next steps senza bullet
  Done), RF- (i sette domain rule files: l'H1, le sezioni, la bullet grammar con le liste numerate 'N. ' e le
  continuation a 2+len(cifre), i code fence verbatim), IA- (ideas.md/ideas-closed.md: le entry D-235
  I-NNN | status | test, la legenda dei status, la continuation a 9 spazi, la riga vuota prima di ogni entry, gli
  I-numbers monotoni). Raffinamenti della grammatica emersi al primo giro: le righe di tabella esenti dalla width
  (una riga fisica per riga E' la grammatica della tabella), i code fence verbatim (zero check dentro), l'H1 esente
  dall'ESC (porta il nome del file: docs\_rules.md ...).
- RIPARAZIONI DEL PRIMO GIRO (stesso commit): 553 underscore nudi + 6 asterischi escape su gli otto file non
  coperti prima (overview.md 475, ideas-closed.md 33, probe\_rules.md 16, tools.md 14, docs\_rules.md 7,
  naming.md 3, log\_rules.md 3, decisions\_rules.md 2); re-wrap canonico dei 4 file che hanno superato i 120 con
  gli escape (overview.md, ideas-closed.md, docs\_rules.md, probe\_rules.md — content-neutral, token-identico).
- VERIFICATION: guard VERDE su tutti i 13 files correnti dei notes (exit 0); il fixture regression continua a
  scattare su tutti i codici impiantati (14 violazioni).
- COMMIT: un solo commit (D-367).
- Session 90 (Roberto, quarantatreesima richiesta): "Linta tutti i file chiusi, e correggili. Devono TUTTI
  passere. senza eccezioni. vai!!!"
- NOTE: la call parcheggiata degli escape sui volumi chiusi — eseguita e chiusa. I volumi chiusi restano fuori
  dal set default (storia append-frozen, lint su richiesta esplicita).
- ANALISI: il primo giro ha esposto le strutture storiche che la grammatica corrente non conosceva: FIELD block
  a indent 6/7/8/10 (decisions\_000) e 8/10 (decisions\_001), i blocchi column-0 dentro D-156b (decisions\_001),
  i "### Step N" + prosa column-0 e i sub-bullet a 1 spazio (i journal), le liste numerate nidificate, il gap
  storico D-152, e i tre entry D-156b/c/d non riconosciuti dal tool (la regex ENTRY esatta D-\d{3}).
- IMPLEMENTATION (D-368): prima le estensioni del guard (documentate nel codice) — decisions: FIELD block 9/11
  + inline bullet 9/11 (la forma canonica del tool stesso), TRAP ristretto ai veri token di mis-parse, SEQ in
  crescita stretta (gap legali, riuso no); journal: "### " section con prosa column-0, sub-bullet " - " a 1
  spazio (continuation 3), numeri nidicati a 2 spazi (continuation 5); tool: la regex ENTRY di
  notes\_format.py guadagna il suffisso letterale — i tre sub-entry D-156b/c/d, altrimenti appiattiti (un solo
  carattere di classe, backward-compatible). Poi le riparazioni: normalizzazione 9/11 dei vecchi FIELD (376 +
  560 righe), 34 righe vuote mancanti prima di header, il blocco column-0 di D-156b indentato a 9, 2 stelle
  matematiche escape a mano (l'escaper accoppia un \*\* raw con un \*\* già escape — bug noto, sistemato a
  mano), 13208 underscore + 161 asterischi escape su tutti e 10 i volumi, il marker "Steps 1+2" bulletizzato;
  re-wrap canonico di tutti i 10 (content-neutral, token-identico).
- VERIFICATION: guard VERDE su tutti i 10 volumi chiusi + i 13 file correnti (exit 0); fixture: tutti i codici
  scattano ancora (il gap è legale per design; un caso di riuso pianta il SEQ).
- COMMIT: un solo commit (D-368).
- Session 90 (Roberto, quarantaquarta richiesta): "Nia, Hai aggiunto un nuovo tool: tools/notes\_lint.py. Domanda:
  perche' non hai aggiornato il files notes/tools.md. Non ti sto dicendo di farlo ora. NON farlo. Voglio capire la
  dinamica del fatto che non lo hai fatto quando hai creato il tool. Voglio ricostruire gli step mancanti nel tuo
  agire. Hai il System Prompt di DSH, poi leggi AGENTS.md ... poi leggi overview.md ... ma rules.md lo leggi ? Come
  possiamo fare a stabilire un CONTESTO piu' consistente ? Spiegami, poi ti do indicazioni poi su come procedere."
- ANALISI (no D): ho ricostruito lo step mancante — il mio contesto si assembla task-driven, non change-driven: tra
  "task" e "commit" manca il passo d'impatto (quali file ELENCANO o VINCOLANO la classe cambiata?). A D-365 non
  avevo ancora letto tools.md (prima lettura a D-367) e nessuna regola elencava l'impact set di "nuovo tool".
  Verificato: i file stantii erano DUE — notes/tools.md (l'index lo descrive: "the four requirements + the
  inventory") e la tabella Source dell'overview (traccia src/ + tools/ + probes/, 48 righe; notes\_lint.py: zero
  occorrenze in entrambi). Proposte 4 leve: (1) rules.md a carico incondizionato (il suo territorio), (2) regole di
  chiusura per classe di cambiamento nel registro, (3) il passo di coerenza pre-commit, (4) automatizzazione con un
  lint di consistenza (il livello complesso).
- Session 90 (Roberto, quarantacinquesima richiesta): "Bravissima Nia ... 1: YES, lo facciamo, ma AGENTS.md lo
  lasciamo per dopo. NON scrivere nulla di questo. 2: YES fammi una proposta, la valuto. 3: sono d'accordo, ma non
  capisco bene cosa implica in pratica, fammi anche qui una proposta. 4: sono d'accordo, ma per ora NO (prima DSH
  deve maturare, poi dobbiamo maturare anche noi i processi di gestione di Reversi). Quindi: proposta per 2 e per 3!"
- PROPOSTA (no D, solo testo): R-049 the impact set (elencazione pura: classe -> documenti, zero parola "commit") +
  R-050 the pre-commit consistency check (il quando: pre-commit, tre domande, deroga esplicita a verbale).
- Session 90 (Roberto, quarantaseiesima richiesta): "Secondo me sono corrette. Leggermente complesse, ma le ho
  capite. Quando in una nuova sessione le leggerai, ti saranno evidenti ? Chiare ed eseguibili senza ambiguita' ?
  Dammi una risposta onesta. Si o No. Seconda domanda: come chiameresti la sezione ?"
- ANALISI: ho risposto NO onestamente — due punti morbidi: (1) il cambiamento multi-classe (l'unione non era
  esplicita), (2) la MODIFICA di un artefatto esistente (nessuna riga la copriva; le righe erano scritte per la
  creazione). Con due mezze frasi nel testo la risposta diventa si. Nome sezione: "Change discipline" (parallelo a
  "Test discipline").
- Session 90 (Roberto, quarantasettesima richiesta): "Si procedi. Grazie."
- IMPLEMENTATION (D-369): le due regole entrano nel registro nella nuova sezione "Change discipline" (dopo "Notes
  format guard"): R-049 con le due chiusure (unione per le multi-classe, modifica = set della sua classe) e R-050.
  Le sue decisioni integrate nel testo: zero riferimenti a D-XXX o ad AGENTS.md, la semantica del commit vive solo
  nella R-050. Il primo milestone a cui si applica R-050 è questo: impact set di "una regola promossa" = registro +
  entry decisionale + journal — tutti aggiornati. (Nota tecnica: il mio testo di R-049 aveva un underscore
  non-escape in notes/\_rules.md e uno spazio in meno tra le due regole — la guard li ha beccati subito, sistemati.)
- COMMIT: un solo commit (D-369).
- Session 90 (Roberto, quarantottesima richiesta): "Nia, Hai aggiunto un nuovo tool: tools/notes\_lint.py. Ora
  aggiorniamo tutti i documenti in notes, consistentemente con le rules. Grazie!"
- IMPLEMENTATION (D-370): il primo esercizio di R-050, l'impact set di "un tool in tools/" verificato documento per
  documento. notes/tools.md — la riga d'inventario di notes\_lint.py MANCAVA (il commit D-365 aveva portato il tool
  senza la sua riga, il gap del GRADUATION di tools.md): aggiunta (categoria check, i codici per formato,
  read-only exit 0/1, origine D-365/D-367/D-368). Tabella Source dell'overview — verificata a portata src/ SOLO
  (tutte e 48 le righe sono src/, il subpackage src/reversi/tools/ è una zona diversa): nessuna riga da aggiungere
  (la cella Doc linka il mirror docs/, che esiste solo per src/ e test/) e l'overview non menziona il guard; il
  bullet Index di tools.md resta accurato. La verifica ha trovato un ERRORE FATTUALE nel testo stesso della R-049
  (scritto su una lettura sbagliata del censimento delle zone della tabella): corretto nello stesso commit (la riga
  tool: la Source table traccia solo src/; la riga probe: probe\_rules.md se cambia una regola — i probe non hanno
  inventario). Il docstring del tool devia dalla grammatica header di tools.md in due punti cosmetici (Usage:
  python invece di .venv/bin/python; la dichiarazione SAFETY implicita) — file sorgente, la call è di Roberto
  (rule 3), intatto.
- VERIFICATION: guard VERDE sul set default + tools.md + rules.md; l'inventario elenca tutti e 5 i tool di
  tools/.
- COMMIT: un solo commit (D-370).
- Session 90 (Roberto, quarantanovesima richiesta): "Metti a posto il file sorgente. Approvato."
- IMPLEMENTATION (D-371): il docstring di notes\_lint.py allineato alla grammatica header di tools.md (le quattro
  parti nell'ordine fissato, nell'idioma dei fratelli notes\_format/suite\_audit): WHAT IT IS (il check + la
  mappa per formato), USAGE (le righe .venv/bin/python, dal workspace root, con il commento del set default
  VERO — il vecchio diceva ancora "decisions + rules + the open journal"), SAFETY (ora esplicito: writes
  nothing, report read-only su stdout, exit 0/1), ORIGIN (D-365 nato direttamente in tools/, D-367
  l'estensione a tutti i formati, D-368 i volumi chiusi). Comportamento invariato (solo docstring).
- VERIFICATION: py\_compile pulito, guard verde sul set default.
- COMMIT: un solo commit (D-371).
- Session 90 (Roberto, quarantaseiesima richiesta): "Nia, Torniamo in rules, sezione 'Docs'. R-038, la
  riformulerei come: R-038 — The mirror docs (docs/): One doc per source file, mirroring the source tree and
  the test tree; the rigid format is in notes/docs\_rules.md. Dammi un tuo parere prima del commit. E' chiaro
  cosa significa ?"
- ANALISI: risposto si, è chiaro (docs/ = mirror 1:1 di src/ E test/, tutta la rigidità delegata a
  docs\_rules.md). Approvato con due osservazioni a verbale: (1) "and the test tree" porta il mirror dei test al
  livello della regola — prima era implicito solo nel puntatore di formato; (2) la parentesi elensiva tolta era
  una auto-descrizione di docs\_rules.md (una fragilità della classe R-049: un documento che enumera un altro)
  — e nulla di normativo si perde: il same-commit lifecycle che citava vive e resta vincolante in
  docs\_rules.md. Via anche il riferimento ad AGENTS.md, coerente con la decisione generale.
- Session 90 (Roberto, cinquantunesima richiesta): "Procedi!"
- IMPLEMENTATION (D-372): R-038 riformulata sul suo testo.
- COMMIT: un solo commit (D-372).
- Session 90 (Roberto, cinquantaduesima richiesta): "R-045.1 — Docstrings: WHAT, never HOW ... R-045.2 —
  Docstrings: no D-XXX (no reference to the decisions) ... Cosi siamo OK ? Per me puoi procedere, e li metti
  nella sezione giusta." (il suo testo risponde alla mia proposta del turno precedente: la divisione di R-040 +
  lo spostamento in Code style; lui ha risolto la collisione RSEQ che avevo segnalato rinumerando sotto R-045)
- IMPLEMENTATION (D-373): R-040 divisa e mossa — R-045.1 (la regola di contenuto: WHAT, mai HOW) + R-045.2 (la
  regola di provenienza: no D-XXX nelle docstring, il commento #: solo se fondamentale) nella sezione Code
  style, dopo R-045; l'ordine di file 45 -> 45.1 -> 45.2 è strettamente crescente, quindi l'RSEQ resta verde.
  Il numero R-040 è retired per la divisione (gap permanente, mai riutilizzato) — coerente con la classificazione
  di D-361 che R-040..R-044 aveva già definite "pure code-style rules" tenute in posizione solo per l'ordine
  numerico. R-041: il puntatore posizionale ("the WHAT-only rule above") diventa un cross-reference esplicito
  (R-045.1 / R-045.2). R-041..R-044 restano in Docs: la loro eventuale emigrazione è una sua call, nel blocco
  in riorganizzazione.
- VERIFICATION: guard VERDE, registro canonico (268 righe).
- COMMIT: un solo commit (D-373).
- Session 90 (Roberto, cinquantatreesima richiesta): "Bene Nia! Secondo te la R-045 comprende le docstring o
  dobbiamo renderlo esplicito ?"
- ANALISI: risposto si, va reso esplicito — il titolo "Code lines" è leggibile come codice eseguibile in
  contrapposizione alla documentazione, mentre la pratica di casa wrappa le docstring a ~120 da sempre; e ora che
  sotto la R-045 stanno le R-045.1/R-045.2 la domanda nasce spontanea. Proposta: una riga di descrizione, titolo
  intatto.
- Session 90 (Roberto, cinquantaquattresima richiesta): "Va bene Nia, aggiorna la R-045. Procedi!"
- IMPLEMENTATION (D-374): descrizione aggiunta — the limit applies to every physical line of a source file —
  code, comments, and docstring lines alike; docstrings are wrapped, not exempt.
- VERIFICATION: guard VERDE, registro canonico (271 righe).
- COMMIT: un solo commit (D-374).
- Session 90 (Roberto, cinquantacinquesima richiesta): "Nia, Torniamo in rules, sezione 'Docs'. R-041, e' un
  disastro, lunga, non chiara. Prova a capire se va tenuta, va riformulata, va semplificata, va divisa in unita'
  piu' piccole. Dammi un tuo parere, fai una proposta. Grazie!"
- ANALISI (no D): smontata in 4 pezzi di natura diversa: (A) il format a 4 parti (il cuore, irreducibile: ogni
  riformulazione resta ~6 righe), (B) il rapporto con R-045.1/2 (clausola di orientamento, residuo del riordino
  di D-373), (C) lo scope/lifecycle (il confine di governance "mai iniziativa dell'agente", sepolto in ottava
  riga), (D) l'esempio. Proposta: dividerla in R-041 (format + esempio + orientamento) + R-041.1 (scope).
- Session 90 (Roberto, cinquantaseiesima richiesta): "Riformuliamo: la R-041 viene ritirata. Nasce la R-045.3
  — Docstrings: FORMAT (il testo a 4 parti). La gestione del passato non la mettiamo nelle rules. Dammi i tuoi
  commenti per favore."
- ANALISI: d'accordo, 4 commenti + 1 osservazione: (1) il cluster docstring si chiude in Code style (R-045
  width, .1 WHAT, .2 provenienza, .3 FORMAT) — in Docs non resta nessuna regola sui docstring e il blocco
  congelato si restringe da R-041..R-044 a R-042/043/044 (R-043/044 stanno bene in Docs, in ballo e' solo
  R-042); (2) R-041 si ritira senza riferimenti appesi (verificato tree-wide: solo il titolo, decisions/journal
  sono append-only, zero nei .py); (3) la clausola "gestione del passato" non va in rules: e' stato di campagna
  (il to-do di 6 item c'e' gia') e la protezione "mai iniziativa dell'agente" vive gia' in R-009 (i sorgenti si
  modificano solo su richiesta esplicita); (4) l'esempio (hlp\_anova) e' un puntatore a un file vivo (e' nel
  to-do del format pass): bene che sia tolto. Osservazione (la sua call): il titolo senza "(src/)" presuppone
  che le regole docstring valgano anche per i test.
- Session 90 (Roberto, cinquantasettesima richiesta): "Procedi come lo ho scritto io. Le regole sulle docstring
  sono valide anche per i tests."
- IMPLEMENTATION (D-375): R-041 ritirata (gap permanente, si aggiunge a R-040); R-045.3 — Docstrings: FORMAT
  aggiunta in Code style dopo R-045.2, col suo testo esatto (le 4 parti, senza esempio, senza clausola sul
  passato). Il ruling di scope a verbale nella decision: le regole docstring valgono anche per i test — da qui
  il titolo non-scoped; R-043/R-044 restano le regole di contenuto di zona (il pattern eccezione della R-044).
- VERIFICATION: guard VERDE sul set default, registro canonico (267 righe, 35 rules + 5 sub-rules).
- COMMIT: un solo commit (D-375).
- Session 90 (Roberto, cinquantottesima richiesta): "Nia, Torniamo in rules, sezione 'Docs'. R-042, secondo il mio
  giudizio e' ridondante con le altre regole. Io la ritirerei. Dammi un tuo parere, fai una proposta. Grazie!"
- ANALISI (no D): il giudizio regge per 4/5, mappa verificata item per item: provenance OUT nei mirror docs =
  docs\_rules.md §4 (vieta per nome, con gli esempi); design pointer nei mirror docs = §3.2 (lo prescrive, con
  l'esempio) — la clausola di R-042 e' un puntatore a un file che il contenuto lo possiede gia' (R-006: il registro
  points, never duplicates; la stessa fragilita' R-049 tolta dalla R-038 a D-372); provenance OUT nelle docstring =
  R-045.2 parola per parola; test/probe = R-043/R-044. Due residui veri: (a) la definizione di "provenance" (la
  parola-chiave della R-045.2 resterebbe gergo non definito), (b) il permesso design-pointer nei commenti sorgente
  (la valvola #: copre solo il caso complementare). Proposta: ritirarla traslocando i due residui in R-045.2 (il
  cluster = casa unica della politica D-ref dei sorgenti).
- Session 90 (Roberto, cinquantanovesima richiesta): "Sono d'accordo al 70% ... (il suo testo riformula l'ultima
  frase: 'as a summary, not a reference.') Il mio intento e': no D-XXX, mai. Se bisogna riportare la decisione,
  meglio un summary, solo in casi eccezionali. Cosa ne pensi?"
- ANALISI: d'accordo al 100% — "as a summary, not a reference" chiude la porta che la mia "design pointer" avrebbe
  lasciato socchiusa (un "— D-096 R1" nel commento): il numero va, l'essenza resta. Semantica risultante: no D-XXX
  mai, due eccezioni a soglia alta (valvola #: solo if fundamental; summary solo when non-obvious, senza numero).
  Asimmetria netta con i mirror docs: la reference vive nel documento (§3.2 la prescrive), il summary vive nel
  codice. I miei 30% si chiudono nel suo testo: la definizione c'e', il permesso ora e' strettissimo.
- Session 90 (Roberto, sessantesima richiesta): "Procedi!"
- IMPLEMENTATION (D-376): R-042 ritirata (gap permanente, terzo dopo R-040 e R-041); R-045.2 sul suo testo:
  definizione di provenance + clausola commento tesa (summary, not a reference). Docs = R-038 + R-043 + R-044 (i
  tre territori doc); il blocco congelato perde l'ultimo pendente (l'emigrazione di R-042): resta solo
  testo/posizionamento/invariante.
- VERIFICATION: guard VERDE sul set default, registro canonico (262 righe, 34 rules + 5 sub-rules).
- COMMIT: un solo commit (D-376).
- Session 90 (Roberto, sessantunesima richiesta): "Nia, Torniamo in rules, sezione 'Docs'. R-043, secondo il mio
  giudizio e' ridondante con le altre regole. Io la ritirerei. E' inclusa da R-045.1, R-045.2, R-045.3 ... non
  credi ? Dammi un tuo parere, fai una proposta. Grazie!"
- ANALISI (no D): no, non e' ridondante come lo era R-042 — e' una regola di deviazione di zona, verificata contro
  l'albero: i docstring test sono righe 1-2 che portano il meccanismo ("optionally how it is realized" contro il
  never-HOW del cluster); il ban I-xxx vive solo li (il cluster dice solo D-XXX, src non e' mai stato vincolato); il
  format leggero e' l'unica difesa dal 4-parti; R-044 pende da essa ("the same rules... follow the test-doc rules").
  Proposta: tenerla, assottigliata come "deviazioni di zona test dal cluster".
- Session 90 (Roberto, sessantaduesima richiesta): "Capisco la obiezione e la accolgo, in parte. Io ritirerei la
  R-043, e introdurrei al suo posto una R-045.4: R-045.4 — Test docstrings: DEVIATIONS ... Tu dici che le deviations
  sono 3, ma io ne vedo una sola: si puo' mettere la descrizione HOW. La seconda e' in realta' una specifica (the
  format is light). La terza (I-XXX): non le voglio da nessuna parte nel codice python, non nelle docstring e non
  nei commenti, nemmeno nei tests. Se e' una dimentinza, aggiungiamo la regola. I tuoi commenti per favore, poi ti
  do indicazioni su come procedere."
- ANALISI: il buco I-XXX e' reale, non una dimenticanza — il divieto viveva solo in R-043 (test). Propongo R-045.5
  nel cluster (un R-051 a se' urta l'RSEQ: cadrebbe in Change discipline). Segnalate la clausola orfana (level
  naming / no ordinals, il template di D-267) e il riaggancio di R-044.
- Session 90 (Roberto, sessantatreesima richiesta): "Bene con R-045.5, formulata come segue. R-045.5 — No I-XXX in
  the code (no reference to the ideas): No I-XXX reference in any docstring or comment of the Python code — src,
  test, or probe; ideas.md is their home. Punto #3, non sono d'accordo, e' specifico a come e' fatto il codice. Non
  va nelle Rules. Rimuoviamolo. Riformula la R-045.4 per favore, la vorrei vedere completa prima di dare
  approvazione. Io non voglio riferimenti interni alle rules ... il wording deve essere chiaro senza riferimento.
  Ineccepibile, evidente, ma senza riferimento."
- ANALISI: bozza completa di R-045.4 senza R-NNN / D-XXX (deviazione HOW + specifica format, "the four-part
  descriptive format" descritto per forma; "are bound" invece di "binded"; lo scheletro suo, il "docstring" aggiunto
  per precisione). Il level naming esce dalle rules (ruling: specifico del codice, istanza D-267). R-044 proposta
  intatta (puntatori in linguaggio naturale, non R-NNN).
- Session 90 (Roberto, sessantaquattresima richiesta): "Approvo il testo, applica la change, della R-044 parliamo
  prossimo turno, come e' scritta non va tanto bene. Procedi, grazie!"
- IMPLEMENTATION (D-377): R-043 ritirata (quarto gap permanente dopo R-040/041/042, nessun riferimento vivo —
  verificato tree-wide); R-045.4 (il suo scheletro, il mio riempimento, il suo ok sul testo completo) + R-045.5 (il
  suo testo) nel cluster dopo R-045.3. R-044 intatta per questo turno (la riscrittura e' del prossimo turno).
- VERIFICATION: guard VERDE sul set default, registro canonico (267 righe, 33 rules + 7 sub-rules).
- COMMIT: un solo commit (D-377).
- Session 90 (Roberto, sessantacinquesima richiesta): "Nia, R-044. La farei diventare: R-045.6 — Probe docstrings:
  DEVIATIONS: Probe docstrings are bound by the same docstring rules applied to the code, with one deviation: one
  exception: the probe's own check labels and item ids (\"C5 … (I-013 …)\") are the probe's vocabulary and stay. I
  tuoi commenti per favore, poi ti do indicazioni su come procedere. Grazie!"
- ANALISI (no D): d'accordo al 100% sulla struttura — specchio perfetto di R-045.4, il cluster diventa casa completa
  e simmetrica (regole generali .1/.2/.3/.5 + zone .4 test, .6 probe); il puntatore impazzito "follow the test-doc
  rules" muore con R-044; Docs resta con R-038 sola. Un refuso: "with one deviation: one exception:" e' duplicato —
  la deviazione E' l'eccezione, una frase basta. L'eccezione deve restare SENZA qualifica di luogo: e' lei a salvare
  i label dal ban I-XXX di R-045.5 ovunque appaiano (docstring, commenti-separatore, testo asserito). Unica perdita
  semantica: il testo asserito (assert messages) diventa dato puro, niente piu' obbligo no-D/I-refs — coerente (i
  dati non sono documentazione). I commenti dei probe: regole generali + eccezione label, senza regola propria
  (simmetrico con i test dopo D-377).
- Session 90 (Roberto, sessantaseiesima richiesta): "Procedi!"
- IMPLEMENTATION (D-378): R-044 ritirata (quinto gap permanente dopo R-040/041/042/043, nessun riferimento vivo —
  verificato tree-wide); R-045.6 nel cluster dopo R-045.5, col suo testo e la mia deduplica della deviazione.
- VERIFICATION: guard VERDE sul set default, registro canonico (266 righe, 32 rules + 8 sub-rules).
- COMMIT: un solo commit (D-378).
- Session 90 (Roberto, sessantasettesima richiesta): "Punto #1 sono 100% d'accordo, volevo davvero il tuo parere, e mi
  e' chiarissimo che scrivi codice di alta qualita', e quindi queste regole le hai embedded. ... Mi fai una proposta
  per le regole nuove: dimensione auspicabile delle funzioni 20-30 righe; PEP 8 e' lo stile di base, il codice e'
  leggibile; dependency permission gate; duplicate check; o altre se ritieni. Punto #2: OK, mi rimetto al tuo
  giudizio. Punto #3: l'ordine naturale che proponi mi trova in accordo. Nota: nelle rules non c'e' concetto
  strutturale padre-figlio, la notazione dot serve solo a posizionare la regola nel suo posto piu' appropriato —
  questo e' un tuo abbaglio. La storia e' storia: e' SAPIENZA ma non deve essere VINCOLO. Prima inseriamo le nuove
  rules (le proponi, le accetto, commit); poi il riordino secondo la tua proposta, NON commit, nomi attuali; io
  guardo e commento; quando l'ordine e' confermato ti do i nuovi numeri; poi commit. Avanti."
- ANALISI (no D): accolte le due correzioni (dot = posizionale, non gerarchia; storia = sapienza non vincolo, quindi
  NESSUNA mappa vecchio->nuovo nell'entry). Proposte 6 regole con numerazione PROVVISORIA nei buchi esistenti
  (RSEQ verde): R-039 (PEP 8, una riga) + R-040 (dimensione 20-30, una riga) a inizio Code style, R-046 (gate
  dipendenze) a fine sezione, R-051 (duplicazione) a fine registro; R-030 (contratto documentato = specifica dei
  test, no pin = Open issue — il docstring promette, il test pin) + R-031 (tre forme del set: happy path, error
  cases, boundary/degeneri — copertura per casi, non percentuali) a fine Test discipline. Avvertenza: dopo il
  riordino il registro sara' RSEQ-ROSSO (nomi attuali, ordine di file non crescente): stato intermedio atteso,
  nessun commit tra il riordino e la numerazione finale.
- Session 90 (Roberto, sessantottesima richiesta): "Le accetto tutte. Inseriscile per favore. Poi commit!"
- IMPLEMENTATION (D-379): le 6 regole inserite (4 code + 2 test) con la numerazione provvisoria nei buchi; i due
  ruling a verbale (dot posizionale; storia non vincolo).
- VERIFICATION: guard VERDE sul set default, registro canonico (296 righe, 38 rules + 8 sub-rules).
- COMMIT: un solo commit (D-379).
- Session 90 (Roberto, sessantanovesima richiesta): "Mi piace molto. Io metterei la regola R-045.5 subito dopo la
  R-045.2. Poi mi chiedo: le prescrizioni delle azioni pre git commit ci sono tutte, ma sono un po' sparse, in
  capitoli diversi ... Cosa ne pensi?"
- ANALISI: eseguito il movimento (i due "no reference" affiancati; RSEQ segna la nuova incoerenza posizionale, da
  risolvere col numeramento). Proposta: una sezione "Before the commit" come cancello finale (suite + guard +
  impact set); le sezioni "Notes format guard" e "Change discipline" si dissolverebbero.
- Session 90 (Roberto, sessantesima richiesta): "Procederei secondo questo schema: Roles R-010, R-020...; Language
  R-100, R-110...; Guard R-200; Change R-250, R-260...; Layout R-300, R-310...; Naming R-400, R-410; Code style
  R-500, R-510...; Docs R-700; Test R-750, R-760... Spaziamo sempre di 10 posizioni tra una regola e la seguente,
  con spazio ulteriore a ogni nuovo paragrafo, e la notazione dot R-NNN.N per i casi futuri estremi. I tuoi
  commenti per favore."
- ANALISI: schema solido (auto-documentante, margini proporzionati alla sezione, dot declassata a strumento di
  emergenza, RSEQ verde per strettamente crescente). Mappatura completa: 46 regole, il registro finisce a R-860.
  Tre punti: Governance da aggiornare (proposta: ordered + principio step-10); la tabella tiene le due sezioni a
  parte = il cancello "Before the commit" resta fuori (la sua call); R-010 resta in Language.
- Session 90 (Roberto, settantunesima richiesta): "1: scrivi che i numeri sono ORDINATI dal piu' piccolo al piu'
  grande al posto di SEQUENZIALI; la sequenza esplicativa: R-510 < R-511 < R-511.1 < R-511.3 < R-511.17 < R-512 <
  R-600 < R-999. Stiamo asciutti: che partiamo da R-010 si vede, e se un domani aggiungiamo qualcosa partiremo da
  R-005 o R-008, quindi la frase diventerebbe vecchia. 2: OK. 3: OK. Nel LOG scrivi la tabella di conversione
  vecchio->nuovo, solo nel log. Se tutto chiaro fai riassunto della change; verifico e poi do OK."
- ANALISI: presentato il riassunto completo della change (riordino + movimento + 46 titoli + Governance asciutta +
  tabella solo nel journal + un commit); in attesa di OK.
- Session 90 (Roberto, settantaduesima richiesta): "The R-numbers are global, ordered from the smallest to the
  largest ... Stiamo asciutti. ... per il resto OK. Procedi con il commit!"
- IMPLEMENTATION (D-380): le 9 sezioni nell'ordine naturale (sistema di notes, poi arto); R-045.5 dopo R-045.2;
  46 titoli rinerati con lo schema step-10 (zero corpi toccati); Governance sul suo testo asciutto (ordered by
  value + la sua sequenza esplicativa; tagliate la mia frase step-10 e la rationale R-010: starebbero nel
  registro solo per diventare stantie).
- TABELLA DI CONVERSIONE vecchio -> nuovo (solo nel log, ruling di Roberto):
  Roles: 001->010, 002->020, 003->030, 004->040, 005->050, 006->060, 007->070;
  Language: 008->100, 009->110, 010->120, 011->130;
  Notes format guard: 047->200;
  Change discipline: 049->250, 050->260, 051->270;
  Layout: 012->300, 013->310, 014->320, 015->330, 016->340, 017->350;
  Naming: 018->400, 019->410;
  Code style: 039->500, 040->510, 045->520, 045.1->530, 045.2->540, 045.5->550, 045.3->560, 045.4->570,
  045.6->580, 046->590;
  Docs: 038->700;
  Test: 022->750, 023->760, 024->770, 025->780, 026->790, 027->800, 028->810, 029->820, 029.1->830, 029.2->840,
  030->850, 031->860.
- VERIFICATION: guard VERDE sul set default, registro canonico (297 righe, 46 rules, 0 sub-rules).
- COMMIT: un solo commit (D-380).
- Session 90 (Roberto, settantatreesima richiesta): "Nia, La frase nel preambolo di rules: The register of every RULE
  in force right now ... the D-number on each line is the origin pointer into it. Non mi pare sia corretta vista la
  campagna di changes. La alteriamo in: [le tre frasi senza l'ultima clausola]. I tuoi commenti per favore."
- ANALISI (no D): d'accordo — la clausola e' stantia in due modi indipendenti: (1) le righe del registro non portano
  piu' nessun D-number (verificato: zero occorrenze, rimossi dai ruling di questa campagna), (2) dopo la D-380 il
  numero R codifica la posizione (step-10 per valore), non l'origine: il puntatore numero -> decisione e' morto con
  lo schema. La tracciabilita' d'origine vive nel blocco Lifecycle (PROMOTE/RETIRE nello stesso commit): il
  puntatore corre decisions -> register. La sua versione asciutta e' esatta e non le manca nulla.
- Session 90 (Roberto, settantaquartaresima richiesta): "Ok! Procedi."
- IMPLEMENTATION (D-381): tolta la clausola finale del preambolo ("; the D-number on each line is the origin
  pointer into it"); il preambolo resta in tre frasi che stanno in piedi da sole.
- VERIFICATION: guard VERDE sul set default, registro canonico (297 righe, 46 rules).
- COMMIT: un solo commit (D-381).
- Session closed (Roberto).
- Next: il blocco regola: ordine e numeri fatti (D-380); resta congelato solo il testo della guard (R-200) — la
  sua semplificazione e' ancora a ripensamento; poi: la riveduta completa del registro (Roberto), i 6 item della
  to-do list (D-337).

## 2026-10-01 — session 91 (il meccanismo hist: files correnti a path fissa + folder per gli archivi — D-382)

- Session 91 (Roberto): "Prossimo lavoro di pulizia della governance. Decisions and log: sono due artefatti che
  memorizzano la storia. Decisions ha un file corrente a path fissa (notes/decisions.md) e all'archiviazione viene
  archiviato in notes/decisions\_NNN.md con numero progressivo; log non ha path fissa, il corrente e' l'ultimo, e al
  raggiungimento della soglia non si copia, si apre un nuovo file. Creare notes/hist\_log e notes/hist\_decisions, i
  files correnti notes/log.md e notes/decisions.md (applicare a log la policy di decisions), spostare i files chiusi
  nei folder, aggiornare tutti i documenti che descrivono il meccanismo. Sviluppa una analisi approfondita, la
  presenti, poi ti do istruzioni su come continuare. Grazie!"
- ANALISI (no D): censito il meccanismo (decisions: path fissa + numero alla chiusura, soglia 1000 righe; journal: no
  path fissa, il corrente e' il max di N, numero alla nascita, soglia 25 sessioni / 2000 righe; il guard trova il
  journal corrente con glob + max(N)); il target formalizzato con le 4 domande aperte e le raccomandazioni ((a)
  numero alla nascita, (i) H1 invariato, tenere l'asimmetria, un solo D un solo commit). Impact set per documento:
  11 git mv, il tool (default set, kind\_of, docstring), il registro (R-040, R-050), le due rule files (scope +
  Volumes and rotation), AGENTS, overview (preamble + Index), il journal stesso. Disciplina della storia: nessun
  back-rewrite (i volumi chiusi citano i path del loro tempo), git mv preserva il history. Trovati 4 ref obsoleti
  residui della D-380 (overview\_rules R-003, tools.md R-047, decisions\_rules R-004, il docstring del tool R-047) —
  chiusi in questa campagna. Curiosita' a verbale: il journal partiva come log.md a path fissa (la D-055 lo ruoto in
  log\_000.md): la path fissa torna, gli archivi entrano nei folder.
- Session 91 (Roberto, seconda richiesta): "1: (a) 2: (i) 3: si 4: OK 5: me lo proponi dopo il commit, ti do quindi
  indicazioni su come procedere."
- IMPLEMENTATION (D-382): 11 git mv (log\_004 -> log.md; log\_000..003 -> hist\_log/; decisions\_000..005 ->
  hist\_decisions/); il guard: default set fisso su notes/log.md (lista esplicita, il glob + max(N) fuori), kind\_of
  accetta log.md, docstring ai path hist + ref R-047 -> R-200 e commento R-042 fuori; il registro: R-040 (i volumi
  chiusi in hist\_decisions) + R-050 (titolo notes/log.md, gli archivi in hist\_log); decisions\_rules + log\_rules:
  riga scope + sezioni Volumes and rotation; i 4 ref obsoleti chiusi; overview: preamble Current state + 10 bullet
  volumi dell'Index ai path hist + bullet aperto a notes/log.md.
- DOCUMENTO TATTAMENTE INTATTO (ruling di Roberto, point 5): AGENTS.md — il bullet Layout resta sul meccanismo
  vecchio; la riformulazione viene proposta dopo il commit, poi le sue indicazioni.
- VERIFICATION: guard VERDE sul set default (13 file, incluso notes/log.md), registro canonico (298 righe, 46 rules).
- COMMIT: un solo commit (D-382).
- Session 91 (Roberto, terza richiesta): "Procedi con change di AGENTS come proposto. OK"
- IMPLEMENTATION (D-383): il bullet Layout di AGENTS.md alla proposta approvata (i due artefatti di storia speculari:
  decisions.md + hist\_decisions/ ‖ log.md + hist\_log/, il bullet piu' corto del vecchio); trovato durante il lavoro:
  la standing rule 6 citava il vecchio meccanismo (il session summary in "notes/log\_NNN.md") — lo sfuggito
  all'analisi della D-382 — ora "notes/log.md" (stessa change, stesso commit).
- PUNTINA PENDENTE (in attesa della call di Roberto): la "with its D-number" della rule 6 — residuo della D-381 (le
  righe regola non portano piu' D-number; il numero vive nell'entry decisionale): la riformulazione e' sua.
- VERIFICATION: il bullet come il testo approvato, coerente con R-040/R-050 e con le due rule files; guard VERDE sul
  set default.
- COMMIT: un solo commit (D-383).
- Session 91 (Roberto, quarta richiesta): "1: OK 2: (a) 3: (B) 4: NO solo D-NNN ha il problema, le rules sono
  stabili. Le Idee ... quando saremo a 1000 vedremo :) !!! siamo lontanissimi. 5: OK solo una. Procedi!"
- IMPLEMENTATION (D-384): decisions\_rules.md: i due ultimi D-ref di provenance rimossi (l'escape bullet, il
  rotation bullet) — il file e' a zero D-ref; le frasi restano auto-spieganti. Scope: solo decisions\_rules, il
  resto della classe 1 (log\_rules, overview\_rules, docs\_rules, ideas, il preamble di tools.md) aspetta la sua
  volta; la classe 2 (esempi funzionali) e la 3 (data di registro) restano per progetto. Pre-empt del D-1000: i 6
  pattern D dei due tool estesi da tre cifre a tre-o-quattro (DEC\_ID, DEC\_HEADER, TRAP, D\_REF nel guard;
  ENTRY, DANGEROUS nel re-wrapper) — zero cambio sul contenuto esistente; verificato con una fixture a 4 cifre:
  lint pulito, il re-wrapper preserva la struttura a 9 spazi (idempotente). Pattern R/I intatti (ruling di
  Roberto: le rules sono stabili, le idee sono lontanissime).
- VERIFICATION: guard VERDE sul set default; fixture D-1000 ok su lint e --write; py\_compile pulito sui due tool.
- COMMIT: un solo commit (D-384).
- Next: la pulizia D-ref della famiglia (classe 1: log\_rules, overview\_rules, docs\_rules, ideas, tools.md)
  aspetta le indicazioni di Roberto, file per file; poi la riveduta completa del registro (Roberto), i 6 item
  della to-do list (D-337).
- Session 91 (Roberto, quinta richiesta): "Prossimo lavoro di pulizia della governance: decisions.md —
  focalizziamoci solo sull'header ... A me sembra che non dovremmo avere il funzionamento qui. Dovrebbe
  andare tutto in decision\_rules.md. Quindi o sono cose non corrette (rimuovere), o sono non necessarie
  (rimuovere), o sono corrette e necessarie (vanno spostate in decision\_rules). Sviluppa una analisi
  approfondita, la presenti, poi ti do istruzioni. Grazie!"
- ANALISI (no D): il paragrafo di funzionamento (9 righe) e' in parte SCADUTO — il path dei volumi chiusi
  notes/decisions\_NNN.md e' pre-D-382 (l'impact set della D-382 non ha toccato il preamble del file stesso) e
  "grows without bound" contraddice la chiusura a 1000 righe — e in parte pura duplicazione del canon gia'
  altrove: la charter in R-040, la promotion/retirement in AGENTS rule 6, gli invarianti D in decisions\_rules,
  i volumi nella sua sezione rotation. Nulla da spostare in decisions\_rules (gia' auto-sufficiente, zero D-ref
  dal D-384). I dati dei volumi (classe 3) sono duplicati nell'Index di overview (ogni volume a se') +
  nell'header di ogni volume chiuso. Ruling: "1:OK 2:rimuovere 3:Procedi!"
- IMPLEMENTATION (D-385): il paragrafo rimosso, l'header e' H1 + pointer (speculare a log.md); nulla spostato in
  decisions\_rules; intatti per progetto: i volumi chiusi (volume 000 col suo vecchio preamble — storia
  congelata) e la citazione dei path vecchi nell'entry D-333 (congelata, corretta all'epoca).
- VERIFICATION: notes\_format --write applicato, guard VERDE sul set default.
- COMMIT: un solo commit (D-385).
- Session 91 (Roberto, sesta richiesta): "Prossimo lavoro di pulizia della governance: ideas.md. ... Mi pare che
  vada tutto bene. Rimuoverei (D-235). Non sono sicuro del significato di: (I-008 is dropped: see ideas-closed.md).
  ... Non mi e' chiaro dove teniamo traccia del NEXT CODE TO USE I-NNN. ... Sviluppa una analisi approfondita, la
  presenti, poi ti do istruzioni. Grazie!"
- ANALISI (no D): il backlog e' vuoto (solo l'header, 8 righe); la clausola I-008 e' una nota one-off su un numero
  specifico (droppata al D-125, il record sta in ideas-closed.md): la regola generale gia' nell'header la rende
  ridondante. Il next I non e' tracciato da nessuna parte — quantita' derivata (max dei due file + 1 = I-021),
  stesso regime dei D-number; la frase invariante nell'header la rende univoca. Il censimento classe 1 aveva perso
  ideas-closed.md:6 (stesso "Format (D-235)") — lista walk-through che cresce di una voce. Ruling: "1: OK! 2: OK!
  2: (i) Procedi!"
- IMPLEMENTATION (D-386): ideas.md: via "(D-235)" e "(I-008 is dropped: see ideas-closed.md)", code span intatti
  (il suo paste li aveva persi — artefatto di rendering, confermato dal ruling 1); ideas-closed.md: via lo stesso
  "Format (D-235)" dall'header gemello (ruling 2); il next I resta derivato, status quo (ruling (i)).
- VERIFICATION: notes\_format --write applicato (idempotente), guard VERDE sul set default.
- COMMIT: un solo commit (D-386).
- Session 91 (Roberto, settima richiesta): "Prossimo lavoro di pulizia della governance: ideas-closed.md ... Mi
  pare che vada tutto bene. Tuo parere?"
- ANALISI (no D): 4 su 5 frasi restano (identita' + appartenenza, contratto di scope "I-NNN index, never a
  narrative", formato proprio, invariante cross-file); la sola "funzionamento" e' la frase MOVES — duplicato
  (direzione opposta) della regola gia' nell'header di ideas.md, la casa del canon; la sfumatura "execution (or
  drop) pointer" vs "D-pointer" non e' portante (un'idea dropped ha il suo D-pointer: I-008, D-125).
- Session 91 (Roberto, ottava richiesta): "La togliamo!" + tema estetico: ideas-closed.md e' l'unico file del
  sistema notes con il dash nel nome — si passa a ideas\_closed.md? ("Lo so che bisogna cambiare tutti i
  riferimenti ... l'estetica inspira ordine").
- IMPLEMENTATION (D-387): la frase MOVES via dall'header; le altre 4 restano. R-070 resta vera senza emendamento
  (ogni preamble porta la sua quota del contratto).
- VERIFICATION: notes\_format --write applicato (idempotente), guard VERDE sul set default.
- COMMIT: un solo commit (D-387).
- PUNTINA PENDENTE (in attesa della call di Roberto): il rename ideas-closed.md -> ideas\_closed.md — l'analisi e'
  presentata in sessione, attendo le sue indicazioni.
- Session 91 (Roberto, nona richiesta): "Brava Nia! Procedi!" (il rename ideas-closed.md -> ideas\_closed.md,
  approvato dopo la mia analisi: dash = incidente, mixed spelling = classe d'errore non visibile alla guard).
- IMPLEMENTATION (D-388): git mv (history preservata, come D-382) + le 10 modifiche vive nello stesso commit:
  l'H1, ideas.md (frase MOVES), Index, R-070, AGENTS (rule 8 + Layout), notes\_lint.py (docstring x2, kind\_of,
  default set); notes\_format.py senza ref. Congelati per progetto: i 47 ref storici (11 log aperto, 13 journal,
  12 volumi chiusi, 11 log\_003) + i 4 file ODP-9 (archivio, restano con il dash).
- VERIFICATION: guard VERDE sul set default (13 file, ora con notes/ideas\_closed.md); censimento ref ripulito
  post-commit.
- COMMIT: un solo commit (D-388).
- Session 91 (Roberto, decima richiesta): "Prossimo lavoro di pulizia della governance: log\_rules.md ... Mi pare
  che vada tutto bene. Tuo parere?" — poi: "Procedi come da tua raccomandazione."
- ANALISI (no D): il file e' in buona salute (il D-382 l'ha aggiornato a posto, niente di scaduto). Due modifiche:
  via "(D-237)" dalla scope line (provenance, classe 1) e via la clausola duplicata dal bullet 5 della sezione
  rotation ("The current journal is notes/log.md" = terza occorrenza; il bullet resta come regola propria
  read-only). Il bullet "One-off 2026-08-29 renumbering" RESTA: non e' una pointer di provenance ma la reading
  key della storia congelata (vecchi commit messages con etichette originali vs volumi riscritti; gli entry
  08-28/29 contano i RUN nel primo slot, deviazione dalla grammatica del bullet 3) — D-054 registra l'azione,
  non la chiave; dato di interpretazione di classe 3.
- IMPLEMENTATION (D-389): le due modifiche chirurgiche applicate.
- VERIFICATION: guard VERDE sul set default.
- COMMIT: un solo commit (D-389).
- Session 91 (Roberto, undecima richiesta): "leggendo ancora log\_rules, la entry numero 4: ... io la
  cambierei in: A session closed by the User ends with a 'Session closed by User.' bullet ... Cosa ne pensi?" —
  poi: "Procedi, usa la variante lowercase."
- ANALISI (no D): depersonalizzazione del bullet 4 — il nome proprio esce dal testo normativo (il registro e
  AGENTS usano "the user" in 4 posti). Impatto mappato: il guard non forza quel testo (nessun tool cita
  "Session closed" — a differenza di JPOINTER e J\_H1, il bullet di chiusura non e' verbatim-forzato); gli 8
  bullet storici restano col testo vecchio (log\_000: 3, log\_001: 1, log\_003: 3, log.md session 90: 1) — storia
  congelata; la prossima chiusura scrive il nuovo testo.
- IMPLEMENTATION (D-390): il bullet 4 alla variante lowercase approvata: "A session closed by the user ends
  with a 'Session closed by the user.' bullet; a 'Next:' bullet may be last".
- VERIFICATION: guard VERDE sul set default.
- COMMIT: un solo commit (D-390).
- Session 91 (Roberto, dodicesima richiesta): "Prossimo lavoro di pulizia della governance: naming.md. Non mi e'
  chiaro come entra nel contesto tuo (dell'Agente). Lo nomina rules.md, lo nomina overview.md? ... Tuo parere?" —
  poi: "1:OK 2: il tuo lean 3: OK 4: AGENTS non facciamo nulla ora, facciamo tutto piu' avanti. Procedi!"
- ANALISI (no D): tre porte nel contesto — la sezione Naming di AGENTS.md (summary in-context a ogni sessione +
  puntatore), R-060 del registro (solo puntatore, zero contenuto), l'Index (classe 3): coerente. Sei modifiche
  de-provenance: il titolo (via la parentesi di tono), l'header "Recorded 2026-08-26 ... T08 (report §5.8)" ridotto
  alla frase charter (i 4 media tenuti: il failure mode che ha generato il file era un'analisi dell'agente),
  l'header della sezione D8, il corpo D8 (via "Roberto's decision (D-014)" e la terza occorrenza A1/H8 — il bit
  mapping resta nella sezione Bitboard), il paragrafo di verifica: la "probe di derivazione indipendente" NON
  esiste (probes/ non ha una board probe) — l'ancora indipendente e' nei TEST, le costanti dorate letterali
  `ar_*` di test\_board.py, indipendenti dall'implementation; via la coda "report §6 item T16" della reading rule.
  AGENTS.md (2 ref classe 1 nella sezione Naming) in coda, con la rule 6.
- IMPLEMENTATION (D-391): le sei modifiche applicate a naming.md, un solo file.
- VERIFICATION: guard VERDE sul set default.
- COMMIT: un solo commit (D-391).
- Session 91 (Roberto, tredicesima richiesta): "Prossimo lavoro di pulizia della governance: probe\_rules.md ... Mi
  pare che in generale sia corretto, ma ci sono diverse correzioni da fare, e frasi da rimuovere. Tuo parere?" — poi:
  "Procedi con pulizia come da tua proposta lean."
- ANALISI (no D): il nucleo e' il migliore dei file di regole (la tassonomia a/b/c e' intatta e senza provenance); i
  problemi: 8 posti di provenance (7 D-ref + il §7 "Baseline (session 30)" per intero), un ref fossilizzato (la
  famiglia o1\* non esiste piu' da nessuna parte, solo classification.md ne parla), un giargone irrisolto ("the D
  tiers" — il concetto di casa e' "suite tiers", R-820), l'inventario dei tool duplicato (canon: tools.md + R-340), i
  ref "docs\_rules.md §5.1/§5.4" formalmente sbagliati (il §5 e' una lista numerata, niente sottosezioni) e la
  clausola "awaiting ruling" di E2/E3 stantia. Verificato contro la realta': la hub pinna ancora active-level count /
  commented imports / worker-list shape (docstring "PIPELINE COMPLETE"), 24 probe tutte verify\_<module>.py, i test
  scrivono in build/tmp, nessun cross-ref esterno punta al §7. Disclosure: il file non era nella lista dei 3 rimasti
  (lista scoped per zona, non per file); censimento a file intero dei live: 25 in overview (classe 3), 6 in
  overview\_rules, 6 in docs\_rules, 13 in tools.md, 7 in probe\_rules.
- IMPLEMENTATION (D-392): 11 modifiche a probe\_rules.md (92 -> 80 righe) + il bullet Index di overview (via "the
  baseline" — ref nel vuoto dopo il taglio del §7): via l'aneddoto D-104 e i sei D-ref, gli aneddoti pre-session-30
  x2, il bullet dei MEASUREMENT tools compresso al fatto di dominio (la sweep e' solo verify\_\*, i loro artifacts in
  build/tmp), "the D tiers", la famiglia o1\*, i ref §5.1/§5.4 (il primo corretto a "docs\_rules.md", il secondo
  rimosso) e la sezione 7 per intero.
- VERIFICATION: notes\_format --write idempotente (0 rejoins), guard VERDE sul set default.
- COMMIT: un solo commit (D-392).
- Session 91 (Roberto, quattordicesima richiesta): "Prossimo lavoro di pulizia della governance: tools.md ... Mi
  pare che in generale sia corretto, ma ci sono diverse correzioni da fare, e frasi da rimuovere. La tabella,
  colonna origin. Serve ? Tuo parere?" — poi: "Procedi con il tuo lean."
- ANALISI (no D): il nucleo e' sano (la boundary §1, i 4 requisiti §2, la header rule §3, il lifecycle §5); i
  problemi: tredici D-ref, la colonna origin (100% provenance, 10 dei 13 ref; i dati hanno gia' due case canoniche
  vive — l'item Origin del docstring, obbligatorio per §3 e presente in tutti e 5 i tool, verificato, e l'entry di
  graduation §5.2 — e funzione zero per la spec a colpo d'occhio), il ref "docs\_rules §5.1" (stesso bug del
  D-392) e, verificato sul codice, la riga notes\_lint GIA' marcita: RTITLE non esiste piu' (i codici register sono
  RHEAD/RSEQ/RSPACE/DPOINTER), i journals mancano di JH1/JBLANK (5 codici reali); il marciume e' doppio (il
  docstring del tool cita pure RTITLE). Le enumerazioni di codici sono volatili per natura: ogni codice nuovo della
  guard forzava l'edit in due posti.
- IMPLEMENTATION (D-393): 9 modifiche a tools.md — la colonna origin via (5 -> 4 colonne), i 4 D-ref del §1/§2 via
  (i 5 nomi del subpackage restano, verificati), "D-237 wrapper" -> "re-wrapper", il ref §5.1 corretto a
  "docs\_rules.md §5", i 3 D-ref della colonna what-it-does via, l'enumerazione dei codici della riga notes\_lint
  sostituita con la descrizione funzionale (i 6 formati + WIDTH/EOF/CANON; il ref R-200 resta: cross-ref al
  register, non provenance). L'item ORIGIN di §3 resta: e' la regola che da' casa ai dati nel docstring — la regola
  resta, la copia nella tabella va.
- VERIFICATION: notes\_format --write idempotente (0 rejoins), guard VERDE sul set default.
- COMMIT: un solo commit (D-393).
- Session 91 (Roberto, quindicesima richiesta): "Prossimo lavoro di pulizia della governance: overview\_rules.md —
  Fai un primo passaggio sul file ... Sviluppa una analisi approfondita, la presenti, poi ti do istruzioni." — poi:
  "Procedi con il tuo lean!"
- ANALISI (no D): il file e' il piu' sano della walk-through (grammatica rigida, zero narrazione); i problemi: 10
  D-ref (6 distinti) come provenance nelle frasi di regola (tutte autosufficienti senza il ref; i ref amended-D-NNN
  sono genealogia, casa nel decision log — non una reading key come il renumbering di log\_rules), 1 nome proprio
  (L36, classe D-390) e una DRIFT di contenuto: il file dice "Exactly the eight sections" ma l'overview reale ha 9
  sezioni H2 e la guard (OV-SECS) forza gia' la prima = "Format rules (rigid ...)" — la sezione-puntatore non e' mai
  documentata nel file di regole (docstring della guard: "the Format rules pointer section, then EXACTLY the eight
  sections"). La correzione e' additiva: niente tocca overview.md né la guard. Tenuti: R-030 (cross-ref alla
  legislazione viva) e la riga reference-families (reading key di classe 3: definisce il vocabolario di id —
  T-NN/M#/session N dormienti oggi, ma la definizione di famiglia vive indipendentemente dall'uso).
- IMPLEMENTATION (D-394): 7 modifiche a overview\_rules.md — il bullet "eight sections" ora dichiara i due fatti
  (sezione-puntatore prima, poi le otto in ordine), i 6 ref via (10 D-ref -> 0), L36 depersonalizzata a "the user".
- VERIFICATION: notes\_format --write idempotente (0 rejoins), guard VERDE sul set default.
- COMMIT: un solo commit (D-394).
- Session 91 (Roberto, sedicesima richiesta): "Controlla overview.md. Fai un primo passaggio sul file, ci sono
  piccole referenze alla storia qui e la' ... Sviluppa una analisi approfondita, la presenti, poi ti do istruzioni."
  — poi: "Procedi con il tuo lean. Poi vediamo altre cose ... Procedi!"
- ANALISI (no D): questo file e' diverso dai file di regole: e' il punto d'ingresso e per design porta i registri di
  classe 3 (Index, tabelle Source/Test, test data — gia' da tenere per il ruling del D-391). Il primo passaggio tocca
  solo le 4 sezioni in prosa: 9 D-ref (8 distinti) + 1 nome proprio + 1 frase duplicata. Verificato: "19-level
  pipeline" e' corrente (la hub pinna "V3c 19 active levels", L157; le righe "18 active levels" del docstring sono
  storia di re-pin), 968 tests corrente, la guard OV-CUR conta solo i bullet (MAX 10, oggi 4) quindi l'introduzione
  di Current state si puo' trimmare senza toccarla. La terza frase dell'introduzione ("MAX 10 bullets,
  no-bullet-per-campaign (D-334)") duplica overview\_rules.md — via. Le due sfumature regolate col lean: (D-267) via
  (l'item e' una label di work, i criteria stanno nel decision log); "the D-333 rotation" x4 nell'Index resta (classe
  3).
- IMPLEMENTATION (D-395): 9 modifiche in prosa — via (D-013) [resta il puntatore naming.md], (D-014), (D-065),
  D-010 [resta "gitignored"], la terza frase dell'introduzione di Current state, (D-318) [resta "rules.md"], (D-267),
  "D-318 docstring conversion" -> "docstring conversion", e l'item register: via "after the D-380 renumbering" +
  depersonalizzazione Roberto/his -> the user (classe D-390), resta (R-200). Le 4 sezioni in prosa: 9 D-ref + 1 nome
  proprio -> 0; il registro di classe 3 e' intatto.
- VERIFICATION: notes\_format --write idempotente (0 rejoins), guard VERDE sul set default.
- COMMIT: un solo commit (D-395).
- Session 91 (Roberto, diciassettesima richiesta): "I due files overview.md e overview\_rules.md, uno dovrebbe
  avere i fatti dello stato, l'altro le regole ... ogni regola espressa in overview debba essere rimossa, con
  l'unica eccezione di: [la frase puntatore] ... Il titolo della sezione: 'Format rules (rigid — follow when
  editing this file)' secondo me e' incorretto e ridondante con la rule. Io starei semplice con: 'Format rules'.
  Sviluppa una analisi approfondita, la presenti, poi ti do istruzioni." — poi: "Ok, procedi!"
- ANALISI (no D): trovato il vincolo critico: il titolo vecchio e' CODIFICATO nella guard (OV-SECS,
  notes\_lint.py:388, prefix "Format rules (rigid") — cambiarlo senza la guard = rosso = no commit. La chiamata e'
  quindi a 3 file: overview.md (titolo), notes\_lint.py (sorgente — l'unica toccata in tutto l'arc, su indicazione
  esplicita via la chiamata sul titolo), overview\_rules.md (il bullet D-394 cita il titolo verbatim). Lean
  accettato: match ESATTO nella guard (un prefix accetterebbe ancora il titolo vecchio — il contrario dello scopo;
  OV-H1 nello stesso punto e' gia' esatto). Verificato: la guard non tocca il corpo della sezione (la frase non e'
  verbatim-forzata, a differenza della J\_POINTER dei journal), nessun altro file live cita il titolo vecchio (le
  entry D-394 congelate restano).
- IMPLEMENTATION (D-396): titolo "Format rules"; OV-SECS esatto + message aggiornato; bullet di overview\_rules
  aggiornato.
- VERIFICATION: guard VERDE sul set default; test negativo in scratch/ (vecchio titolo -> rosso OV-SECS col nuovo
  message, nuovo titolo -> verde); run pre-commit standard.
- COMMIT: un solo commit (D-396).
- Session 91 (Roberto, diciottesima richiesta): "I due files overview.md e overview\_rules.md, uno dovrebbe avere i
  fatti dello stato, l'altro le regole ... Analizziamo la sezione Index. La frase [intro]: Io la eliminerei. Deve
  essere scritto in overview\_rules cosa va in Index. Le entries: [6 esempi di semplificazione] ... E avanti cosi ...
  Sviluppa una analisi approfondita, la presenti, poi ti do istruzioni." — poi: "Procedi! Va bene la tua proposta di
  emendamento della overview\_rules!"
- ANALISI (no D): principio estratto: l'Index e' un registro di identita' — si tengono la descrizione e i dati di
  contenuto reali (range e date dei volumi), via D-pointer, pattern di famiglia, dettagli di grammatica/governance,
  cross-ref, annotazioni di campagna. Verificato: l'intro e' il duplicato verbatim del secondo bullet della sezione
  Index di overview\_rules.md (casa canonica gia' al posto); la guard non ha alcun check sul contenuto dell'Index
  (i codici OV-: H1/SECS/TABLE/CUR/NEXT/INDENT) — zero modifiche alla guard; ogni dettaglio tagliato ha casa
  canonica verificata (la grammatica bold-title + la clausola di approvazione esplicita sono testuali nel blocco
  Governance di rules.md; "rigid" vive nell'H1 di ogni file di regole; I-017 in ideas\_closed.md + la directory;
  "legislative body" nell'H1 di rules.md; ODP-9 nella directory historical/). La chiamata SOSTITUISCE il ruling del
  D-391 (i D-pointer dell'Index "restano classe 3"): l'Index resta registro, le entry da oggi sono minimali.
- IMPLEMENTATION (D-397): 14 modifiche all'Index (intro via; naming, rules, decisions; le 4 annotazioni di
  rotazione; analyses, ideas, ideas\_closed, i 5 bullet dei file di regole, tools, probe\_rules alla forma minima
  uniforme) + il terzo bullet in overview\_rules.md (il principio codificato). Micro-scelta: "performances
  baseline" -> "performance baseline" (coerente col nome reale del file).
- VERIFICATION: guard VERDE sul set default; overview.md a zero D-pointer (restano solo le 6 range+date dei volumi
  chiusi, tenute per ruling).
- COMMIT: un solo commit (D-397).
- Session 91 (Roberto, diciannovesima richiesta): "Analizziamo la sezione Test files ora. Non e' una regola questa:
  [intro] ... Non sarebbe meglio in overview\_rules? ... due entry hanno la dicitura 'complete (helper module, 0
  tests)', ma non e' uno stato quello tra parentesi ... Io rimuoverei le parentesi e lascerei 'complete'. La
  intestazione la cambiamo in 'Suite/std\_run'. Poi cambiamo la regola in overview\_rules, e applichiamo il
  formato: <total>/<failures>/<skipped>/<vlong>/<vvlong> ... 14/0/0/0/0. Sviluppa una analisi approfondita, la
  presenti, poi ti do istruzioni." — poi: "1: OK. 2: va bene come proposto. Elimina anche la intro di 'Source
  files', e' l'unica modifica da fare per la sezione. Procedi!"
- ANALISI (no D): i fatti dalle fonti di test: i totali sommano 968 (tabella in sync); gate VLONG reali = 2
  (class-level skipUnless in test\_lm\_worker\_full\_chain e test\_wrk\_su\_analysis, 1 test ciascuno — gli altri
  11 moduli menzionano VLONG solo in docstring); VVLONG non strumentato (tags.py testuale, grep zero) — la quinta
  slot e' future-proofing; i gate PERF (test\_board, test\_feature) restano nella slot skipped, non vlong.
  Verificato: la guard OV-TABLE salta la riga header (rinome guard-safe) ma la ESC copre ogni riga di
  overview.md — l'intestazione va scritta "Suite/std\_run".
- IMPLEMENTATION (D-398): intro di Test files e di Source files via; header "Suite/std\_run"; 47/47 righe in
  formato 5 parti (2 righe con vlong=1, 2 helper "0/0/0/0/0", il resto +/0/0); 2 state cell ridotte a "complete"
  (la regola esistente gia' vietava il parentetico — la tabella ora e' conforme); regola di overview\_rules
  riscritta (approvata come proposta, fissa l'intestazione e le due relazioni di contenimento).
- VERIFICATION: guard VERDE sul set default; 47/47 celle 5 parti; totali = 968.
- COMMIT: un solo commit (D-398).
- Session 91 (Roberto, ventesima richiesta): "Molto bene la analisi. E sono in parte d'accordo con il tuo lean. Ma ho
  una obiezione: se ci pensi bene anche naming.md e' una eccezione, tutto quanto descritto in naming dovrebbe essere
  la descrizione tecnica del doc mirror di board. Qui aggiungiamo le position, le moves ... e pattern .... Poi ci
  sono cose un po' piu generali come pydantic e numba. Io credo che nulla debba rimaner qui. Ma cedo anche che si
  debba organizzare questi concetti in maniera che siano poi fruibili dall'Agente in nuove sessioni di lavoro. Cosa
  ne pensi? Per ora procedi a rimuovere i duplicati. Poi decidiamo per il resto."
- OPINIONE (no D, alla sua domanda): concordo sulla struttura — le tabelle D8 sono materialmente la descrizione
  dell'output di board.py (naming.md lo dice testualmente) e position/moves/pattern sono gia' nei mirror (audit
  verificato). Avvertimento per "poi": il vocabolario + la reading rule dei diagrammi sono cross-cutting (governano
  anche note e reply) — se naming.md si scioglie, quella fetta va a vivere in AGENTS.md (che ne porta gia' il
  sunto). Pydantic/numba non hanno casa in notes/ (solo nei mirror): renderli fruibili a livello Agente = nuovo
  canone o sunto in AGENTS.md — tua call.
- IMPLEMENTATION (D-399, perimetro: i soli duplicati in naming.md): via il bullet vocabolario/bitboard (100%
  duplicato; naming.md e' la casa ed e' piu' completo); nel bullet D8 via la meta' naming (slot order + anti
  transform), resta solo la meta' pattern (concept pattern, gia' in pattern.md — nella lista "poi"). I 7 bullet
  rimasti, il titolo e il destino della sezione: differiti al suo prossimo ruling.
- RIPARAZIONE (auto-inflitta, disclosure): l'inserzione di D-398 aveva lasciato dangling l'ultima riga wrap di
  D-397 ("on the default set."), assorbita dal rewrap nell'ultima riga di D-398 — ripristinati entrambi i finali
  (D-397 come al commit 40c097f, D-398 che termina a "to 968.").
- VERIFICATION: guard VERDE sul set default.
- COMMIT: un solo commit (D-399).
- Session 91 (Roberto, ventunesima richiesta): [istruzioni dirette] "Move codes: ... Va spostato in naming.md,
  nella sezione Board vocabulary, in fondo. In naming aggiungiamo una sezione che chiamiamo 'Position', dopo
  'Bitboard'. In naming, nella sezione 'Bitboard', come prima righa inseriamo la definizione di Bitboard che e' un
  alias a numpy.uint64. Domanda per te, nella definizione di Position e' giusto usare u64, o meglio usare uint64?"
- RISPOSTA (no D, alla sua domanda): verbatim dal codice — board.py: "Bitboard: TypeAlias = np.uint64" (riga 127)
  e "Position = np.dtype([('mover', Bitboard), ('opponent', Bitboard)])" (riga 142). u64 non esiste come simbolo in
  src/ (verificato: solo frasi descrittive nei docstring di regab/prng e write\_u64/\_U64 di binio, che sono I/O
  binario) — e' uno shorthand dei mirror. Nella definizione uso Bitboard (il tipo reale dei campi), alias
  specificato; tra i due proposti, uint64 sarebbe stato il giusto.
- IMPLEMENTATION (D-400): naming.md — prima riga della sezione Bitboard: "Bitboard is an alias of numpy.uint64";
  nuova sezione Position (def dtype, campi Bitboard); move codes in fondo a Board vocabulary (verbatim dall'
  overview). overview.md — i due bullet via (spostati, non persi): la sezione Conventions e' a 6 bullet.
- VERIFICATION: guard VERDE sul set default.
- COMMIT: un solo commit (D-400).
- Session 91 (Roberto, ventiduesima richiesta): [verdict sulla proposta delle 3 sezioni] "Va molto bene in generale,
  i riferimenti alle colonne li toglierei, non sono costitutivi e sono solo in relazione alla Design\_Matrix,
  Indexes, che qui non introduciamo realmente. Se non parliamo di colonne, feature diventa brevissimo (come deve
  essere, e' il wrapper dei 3 tipi). Rimuoverei anche i sample patterns. Prova questa formulazione e vediamo se va
  bene."
- IMPLEMENTATION (D-401): tre sezioni in fondo a naming.md, sequenza Features/Mobility/Pattern. Features: senza
  colonne (wrapper + 3 categorie + FeatureSet — brevissimo come chiesto); Mobility: invariato rispetto alla
  proposta (formula dell'index, n\_configurations = k+a+1, n\_instances = 1, i 3 standard LMC/ALMC/DLMC); Pattern:
  via i sample patterns, PatternSet ridotto a "named collection, stored sorted by mask".
- VERIFICATION: guard VERDE sul set default.
- COMMIT: un solo commit (D-401).
- Session 91 (Roberto, ventitreesima richiesta): "La sezione 'Feature' la riformuliamo cosi: [testo esatto].
  Grazie!"
- IMPLEMENTATION (D-402): sezione Features di naming.md riformulata verbatim: la definizione di dominio ("an
  observable characteristic of a game position"), i 3 bullet senza valori enum e con i suoi glossi (the constant
  term / a measure of the options to move / a selection of squares on the board), la FeatureSet "chosen at will
  among the intercept, mobilities and patterns". Normalizzazione: separatori in em-dash come nei bullet sibling.
- RIPARAZIONE (secondo wrap-split, auto-inflitta): l'inserzione di D-401 aveva usato un anchor a meta' riga sul
  finale di D-400 e ne aveva lasciato dangling il resto del wrap, assorbito nell'ultima riga di D-401 ("default
  set. default set."); rimosso. Il finale di D-400 verificato intatto.
- VERIFICATION: guard VERDE sul set default.
- COMMIT: un solo commit (D-402).
- Session 91 (Roberto, ventiquattresima richiesta): "Va benissimo. Ultima change: 'A mask is a 64-bit integer'
  cambiamolo in: 'A mask is Bitboard'. Grazie!"
- IMPLEMENTATION (D-403): primo bullet della sezione Pattern: "A mask is `Bitboard`; the principal mask is the
  numerically LOWEST of its 8 D8 transforms…" — la mask ora e' definita dal suo tipo reale (l'alias Bitboard
  definito nella sezione sopra), catena definitoria mask -> Bitboard -> numpy.uint64. Normalizzazione: Bitboard in
  code span come nelle sezioni Bitboard/Position.
- VERIFICATION: guard VERDE sul set default.
- COMMIT: un solo commit (D-403).
- Session 91 (Roberto, venticinquesima richiesta): "Torniamo ad overview. Le entries che parlano di patterns nella
  sezione 'Conventions in the code' le possiamo ritirare. Rimangono le entries #1, #2, #3. La #1: Dual scalar/array —
  e' una scelta di design, generale nella pipeline, conforme al disegno di numpy, che e' una scelta obbligata per le
  performances della soluzione. Ma dove deve stare questa cosa, e poi interessa a Nia, o ad un altro Agente, come info
  generale architetturale? La #2: Pydantic — e' una scelta della 'casa' (funzione pubblica, nessun problema
  prestazionale specifico, nessun retroscena convolto come il Context della state machine), e dove va scritta questa
  affermazione? La #3: numba — altra scelta della casa, con analisi costi vs benefici, e il kernel viene incapsulato
  in una API (embedding nel Python). vero, e anche questo dove lo scriviamo ??? Forse ci serve un file dedicato in
  notes, come e' naming per i tipi e le classi, qui una cosa tipo notes/design\_principles.md. Non so ... ma poi ci
  mettiamo 3 note in tutto e stiamo facendo over\_engineering della cosa? O credi sia utile? La #6: Test artifacts —
  questa e' una regola, che se non e' gia' presente in rules, va messa li. Tu cosa credi sia giusto fare? Fai una
  analisi completa e dammi la tua view, poi decidiamo come procedere. Grazie!"
- ANALISI (mia): le 2 entries pattern sono gia' nei mirror (pattern.md: instance 0 = ro000 a riga 57; base-3 a
  3/12/62) — ritiro pulito, zero perdita. La #6 e' gia' R-750 nel register (notes/rules.md:232) — e' un duplicato,
  si ritira. Le #1/#2/#3 sono policy di casa cross-cutting (vincolano qualsiasi codice nuovo, non un modulo): non i
  mirror (per-modulo), non il register (soft policy, non "must"), non decisions (storia) — serve un file di sintesi.
  Su over\_engineering: no, a patto di disciplina (3 entry da 2-3 righe, no D-pointers, stile deprovenance); il
  rischio e' il gonfiamento futuro. Costi: 1 riga nel lint + 1 Index entry + l'AGENTS pointer nell'ultimo step.
  Tre opzioni per il destino della sezione: (a) vuota — no; (b) eliminazione + guard a 7 sezioni; (c) puntatore
  (pattern D-396); consigliata la (c).
- Roberto: "1: confermo / 2: YES / 3: (b) radicale. Procedi!"
- IMPLEMENTATION (D-404): le 4 bullets ritirate dalla sezione Conventions e la sezione stessa eliminata (overview a
  7 sezioni: SECTIONS del guard 8 → 7, la regola "The eight sections" di overview\_rules.md diventa "The seven
  sections" con l'enumerazione corretta, docstring del guard aggiornate). Nato notes/design\_principles.md con le 3
  entry: dual scalar/array API (fatto architetturale, imposto dal design di numpy), Pydantic (stile di casa
  condizionato, eccezione il Context della state machine), Numba (policy di casa con costi/benefici; il kernel e'
  sempre incapsulato in una funzione Python normale, non esce dall'API). I dettagli di meccanismo (is\_scalar →
  atleast\_1d → ndim → dispatch → reshape) restano nei mirror: territorio per-modulo. Index: entry per il nuovo
  file dopo naming.md. Guard: file nel set default (ora 14 file) e nella grammatica rulefile (kind\_of).
- VERIFICATION: guard VERDE sul set default (14 file).
- COMMIT: un solo commit (D-404).
- Session 91 (Roberto, ventiseiesima richiesta): [proposta] "Ti propongo questa riformulazione per
  notes/design\_principles.md — un po' piu strutturata, ma direi in linea con gli altri artefatti, e pronta per un
  eventuale uso piu articolato. Controlla non vi siano incosistenze, e dammi un tuo parere." — H1
  "design\_principles.md — active design principles" + intro + Governance (DP-NNN global, never reused, order by
  value, title in bold + descrizione 1-3 righe, 2 blank tra principi) + DP-010/DP-020/DP-030.
- ANALISI (mia): 4 refusi (worspace, applyed, doesn't leaks, prefisso Pydantic ridondante) + code span obbligatori
  (ESC); DP-NNN = nuova famiglia di riferimento (bullet Reference families di overview\_rules.md, unico sito di
  definizione); il file e' grammatica register, non rulefile → serve un lint DP nel guard (specchio del lint\_rules,
  sezioni ## opzionali). Fatti verificati: il Context USA @validate\_call (7 decorator, state\_machine.py) — il
  retroscena e' la gate deliberatamente separata dall'esecuzione (D-076/D-069), la condizione "no convoluted
  backstory" e' fatto-safe; l'eccezione DP-030 e' reale (board.md:33, random\_game).
- Roberto: "Sono d'accordo su tutto, tranne che 'accept a scalar or 1-D array'. Prima di fare la change fai questa
  investigazione. Nei metodi che trattano gli indici in pattern, o wmaps, o design\_matrix ... le funzioni operano
  by design su array multi dimensionali. La limitazione imposta in board su alcune funzioni non e' dovuta ad una
  necessita' tecnica, era la mia paura di dover verificare casi complessi nei test, che poi non sarebbero stati
  usati in pratica nella pipeline, cosi ho messo la guardia. Ma la scelta giusta e' rimuovere la guardia, e fare la
  verifica che le funzioni siano corrette anche in caso di vettori multidimensionali. Quindi io nella design
  principle non lo inserirei ... in DP-010 aggiungiamo gli indici in 'like Bitboard or Position' e scriviamo
  'like Bitboard, Position, or Index'. studia, e poi riformula per favore."
- INVESTIGAZIONE: 13 siti ndim in board.py, 9 funzioni, 3 famiglie — cast (from/to signed int, from hex str):
  shape-agnostic sotto la guardia, pura formalita'; D8 (transformations/anti) e kernel (legal\_moves,
  position\_flips/make\_move/hash): kernel numba 1-D, la guardia converte il TypingError in ValueError pulito
  (D-111 M5). La pipeline al bordo board passa solo scalare (costruzione pattern) e 1-D batch (feature.py:331); il
  2-D vive al layer pattern/wmaps/design\_matrix (design matrix NxF). Confermato: policy di bordo, non necessita'
  tecnica. Percorso N-D standard: flatten → kernel → reshape back. Index verificato: TypeAlias np.uint32
  (pattern.py:65, in `__all__`).
- Roberto: "Perfetto Nia! Procedi! Aggiungi nei next steps di overview la rimozione guardia. Nella sezione Pattern
  di naming inseriamo Index. Yes!!! Ora stai lavorando egregiamente bene!"
- IMPLEMENTATION (D-405): design\_principles.md riscritto in forma register (Lifecycle + Governance + DP-010/020/
  030 con le correzioni concordate; DP-010 senza 1-D, con Index). Guard: lint DP aggiunto (DPH1/DPSPACE/
  DPOINTER/DPSEQ), kind\_of → 'design'; reference family DP-NNN in overview\_rules.md; Next steps dell'overview:
  rimozione guardia 1-D + verifica N-D; naming.md: riga Index nella sezione Pattern.
- VERIFICATION: guard VERDE sul set default.
- COMMIT: un solo commit (D-405).
- Session 91 (Roberto, ventisettesima richiesta): "E' molto ben fatto. Fare una piccola change in naming.md: Rimuovi
  la riga appena introdotta in pattern riguardo ad Index. Aggiungi una sezione Index, subito sotto Position, e
  scriviamo nella sezione cosa sia un Index ... come fatto per Position. Piu' chiaro, piu' evidente. E poi gli
  Indexes sono i protagonisti della PIPELINE :) !!! Procedi!"
- IMPLEMENTATION (D-406): naming.md — la riga Index rimossa dalla sezione Pattern e promossa a sezione propria
  "## Index", subito sotto Position, nello stile di Position: "Index = a numpy uint32 alias — the base-3
  configuration index (the Pattern section below).".
- VERIFICATION: guard VERDE sul set default.
- COMMIT: un solo commit (D-406).
- Session 91 (Roberto, ventottesima richiesta): "mmmmm una cosetta ancora Nia. Hai scritto 'the base-3 configuration
  index (the Pattern section below).' Ma la definizione di Index sta in Pattern perche' il modulo pattern e' nato
  prima di mobility e feature. E' una lunga storia, che al momento non ha valore ... In realta' il concetto di Index
  e' trasversale a tutte le Feature. Quindi io scriverei: 'used to identify feature configurations (base-3 in
  particular for patterns).' Poi vista la crescita di naming.md 'fuori dal dominio specifico della board' direi di
  fare una seconda modifica: 'This file is the single source of truth for the domain vocabulary in this workspace
  ...' Commenti? Se sei d'accordo procedi!"
- IMPLEMENTATION (D-407): naming.md — bullet Index riformulato: "used to identify feature configurations (base-3 in
  particular for patterns)" (il concetto e' trasversale a tutte le feature, non legato alla sezione Pattern —
  verificato: mobility.py e feature.py importano Index/IndexArray); intro: "board vocabulary" → "the domain
  vocabulary" (il file e' cresciuto oltre il dominio board, l'H1 gia' diceva "domain naming convention").
- VERIFICATION: guard VERDE sul set default.
- COMMIT: un solo commit (D-407).
- Session 91 (Roberto, ventinovesima richiesta): "Sistema l'entry dell'Index in overview ... OK. Poi Nia, Vorrei
  aggiungere questo testo in overview.md: 'The Machine Learning pipeline is developed by defining a set of observable
  features within the game positions and a training set, from which the observed values are extracted as categorical
  indices. These data are then utilized in a logistic regression model, minimizing the sum of squared residuals
  between the actual game values in the training set and those computed by the evaluation function. The resulting
  weights, combined with the selected feature set, ultimately define the evaluation function.' Subito dopo:
  'This workspace is dedicated to the research and development of evaluation functions ...' Come ti sembra? Chiaro?
  dammi un tuo parere, se ti sembra OK, procedi con la change. Grazie!"
- PARERE (mia): testo chiaro e corretto — descrive la pipeline end-to-end (feature osservabili + training set →
  indici categorici → regressione logistica a minimo quadrato sui game values → pesi + feature set = evaluation
  function); nel Project è il posto giusto: descrizione atemporale dello scopo, non stato. Procedo verbatim.
- IMPLEMENTATION (D-408): overview.md — entry Index di naming.md allineata ("canonical domain naming convention
  (board vocabulary, D8, feature types)"); Project: il secondo paragrafo aggiunto dopo quello esistente.
- VERIFICATION: guard VERDE sul set default.
- COMMIT: un solo commit (D-408).
- Session 91 (Roberto, trigesima richiesta): "La sezione 'Environment' in overview: Le dependencies sono quelle
  vere? fai un controllo per favore. Parliamo di tests, parliamo di probes. Io farei anche una entry per i tools, e
  farei anche una entry che dice che tutti i file di governance sono in notes. E gia' che ci siamo una entry per
  docs ed una per scratch. Dammi un tuo parere, se ti sembra OK, se ti sembra UTILE per l'Agente che apre
  AGENTS.md, e trova la riga 'leggi notes/overview.md' ... Fai una analisi completa e dammi la tua view, poi
  decidiamo come procedere. Grazie!"
- ANALISI (mia): le dipendenze NON sono quelle vere — pyproject.toml ne dichiara 11, l'entry ne elenca 8: mancano
  json5 (wrk\_config), scipy (hlp\_gradient/hlp\_anova/hlp\_plot), matplotlib (hlp\_plot/opt\_lbfgs). Le 4 entry
  proposte: SI, utili — l'agente che apre AGENTS.md e legge "read notes/overview.md" deve ricostruire la mappa del
  workspace da overview da solo, e il nostro endgame e' un AGENTS slim con solo puntatori: overview deve diventare
  proprietario della mappa. Attenzione al raddoppio: l'entry governance e' in parte ridondante con l'Index, ma vale
  come segnavia in alto. La trappola tools/: la postilla "not the package's src/reversi/tools/" deve stare
  dappertutto — ambiguita' PERICOLOSA.
- Session 91 (Roberto, trentunesima richiesta): "Se tools crea questa ambiguita' PERICOLOSA, che dobbiamo sempre
  mettere la postilla di puntualizzazione, CAMBIAMO NOME. Invece di tools ... mettiamo wsutils (workspace
  utilities) ... capisco che sia un attimo di 'trambusto' ... ma poi abbiamo sistemato PER SEMPRE ... Non credi?
  fai una analisi, e fammi una proposta, poi ti dico come procedere. Grazie!!!"
- ANALISI (mia): d'accordo — tassa permanente vs trambusto una tantum: il trambusto vince. Riconoscenza: il
  trambusto e' piccolo (zero ref da src/test/probes/runner; ~12 docstring nei 5 tool; 6 righe nel register; 2 in
  probe\_rules; notes/tools.md; il guard; Index; AGENTS Layout; i 3 mirror 'sospetti' sono zona pacchetto).
  Proposta: 2 D / 2 commit — D-409 il rename (postilla D-248 in pensione), D-410 la batch Environment (l'entry
  tools esce pulita, senza postilla).
- Session 91 (Roberto, trentaduesima richiesta): "1: confermo / 2: si, insieme OK. Procedi!"
- IMPLEMENTATION (D-409): git mv tools → wsutils; i 5 tool (usage/docstring; le righe Origin storiche intatte);
  notes/tools.md → notes/wsutils.md (H1 + interno); guard (kind\_of, set default, docstring); register (R-200
  path, R-250 x2, R-340 rititolata "wsutils/ holds the workspace utilities" — clausola pacchetto ridondante
  rimossa, clausola probes mantenuta); probe\_rules x2; Index; AGENTS Layout (postilla ritirata). Zona pacchetto,
  volumi storici e analyses: intatti. SMOKE: ./run\_utests.sh — 968 OK (skipped=100, tier fast).
- IMPLEMENTATION (D-410): overview Environment — dipendenze corrette (json5/scipy/matplotlib aggiunti, "minimal
  set" rimosso) + 4 entry nuove dopo Probes: Workspace utils (pulita, no postilla), Mirror docs, Scratch,
  Governance (il segnavia verso l'Index).
- VERIFICATION: guard VERDE sul set default.
- COMMIT: due commit (D-409, D-410).
- Session 91 (Roberto, trentatreesima richiesta): "La sezione 'Current state' in overview: Abbiamo davvero bisogno
  del preambolo? Fai una analisi completa e dammi la tua view, poi decidiamo come procedere. Grazie!"
- ANALISI (mia): il preambolo e' una regola, non un fatto di stato — i suoi 3 claims sono gia' coperti, punto per
  punto, dalla sezione Current state di overview\_rules.md (che il writer deve consultare comunque, per il puntatore
  Format rules in cima all'overview); e' l'ultimo leftover della mappa D-395 (gli intro Source/Test furono rimossi in
  D-398, stessa categoria). Unico dettaglio in scadenza: i path dei file — li assoro in overview\_rules.md. Guard:
  zero change.
- Roberto: "Procedi con la rimozione!"
- IMPLEMENTATION (D-411): preambolo rimosso da Current state (la sezione e' ora titolo + 4 bullet, puramente
  fattuale, come Source/Test); overview\_rules.md: le 2 bullets assorbite (path del journal + decisions log; "NOT in
  the Source files / Test files tables (the file-by-file state)").
- VERIFICATION: guard VERDE sul set default.
- COMMIT: un solo commit (D-411).
- Session 91 (Roberto, trentaquattresima richiesta): "La sezione 'Current state' in overview: Abbiamo quattro
  record. Io ne terrei solo due e li semplificherei come segue: [i 2 bullet: pipeline live and green (all tests are
  ok) — the ML chain from CONFIG up to FINAL\_LOG\_PRINT; LM facade ...] Fai una analisi completa e dammi la tua view,
  poi decidiamo come procedere. Grazie!"
- ANALISI (mia): verificato che ogni frammento scartato ha una casa viva — 968 nella tabella Test files (somma D-398),
  il benchmark 1e6 VVLONG come risultato di campagna (journal/decisions), la catena di step + l'opt-in SU\_ANALYSIS/
  ANOVA nel mirror logistic\_model.md, il gate log\_file\_name nel mirror hlp\_final\_log\_print.md, il bullet
  docstring meta' puntatore al register + meta' campagna gia' in Next steps, la consolidazione ec nel mirror
  hlp\_config\_schemas.md (riga 41). I 2 bullet tenuti sono i due fatti pipeline-wide puri: salute + come si guida.
  D-411 portata a compimento.
- Roberto: "Procedi!"
- IMPLEMENTATION (D-412): Current state a 2 bullet (il primo semplificato verbatim, il facade invariato); i 2 bullet
  scartati rimossi.
- VERIFICATION: guard VERDE sul set default.
- COMMIT: un solo commit (D-412).
- Session 91 (Roberto, trentacinquesima richiesta): "Ultimo file da verificare in notes e' docs\_rules.md. E'
  aggiornato a tutte le modifiche di governance apportate in rules, overview, naming, ...? Ci sono duplicaziani? E'
  consistente? E' completo? E' chiaro? Fai una analisi completa e dammi la tua view, poi decidiamo come procedere.
  Grazie!"
- ANALISI (mia): file ben fatto, quasi aggiornato, nessuna duplicazione sostanziale — ma 3 problemi veri: (1)
  contraddizione interna sulla State line (s2 dice RETIRED, s5.2 e s6 la prescrivono ancora — residui pre-D-240);
  (2) puntatore stale in s4: il suite status globale e' ora in Current state + tabella Test files, non Environment
  (post-D-411/412); (3) le 4 fughe di provenance class-1 (D-007, D-238, D-109, D-240 — i D-096/D-103 citati restano:
  pattern del register, esempi permessi). Due micro-lacune: Companions senza wsutils.md (l'auditor che implementa
  le regole); la regola non dichiarava no-trailing-whitespace e no-split-spans (che l'auditor controlla gia').
- Roberto: "Procedi come hai proposto!"
- IMPLEMENTATION (D-413): i 5 interventi su docs\_rules.md (State line x2, puntatore suite, 4 leak, Companions +
  clausola whitespace/spans).
- VERIFICATION: guard VERDE sul set default.
- COMMIT: un solo commit (D-413).
- Session 91 (Roberto, trentaseiesima richiesta): "Il folder notes/analyses contiene tantissime cose che non hanno
  piu nessuna attualita' e nessun interesse. Io farei una rimozione completa. Rimane solo il folder vuoto a
  disposizione per il futuro. Tuoi commenti? Sei d'accordo, se sei d'accordo procedi, altrimenti argomenta. Grazie!"
- PARERE (mio): d'accordo — git preserva tutto (ogni volume resta recuperabile dai commit passati): e' archiviazione
  fuori dall'albero, non distruzione; la dottrina "frozen" tutelava l'integrita' (no back-rewrite), non la permanenza
  nell'albero; il record canonico sta gia' in decisions/journal/git. Riconoscenza: 86 file (1.2 MB), zero riferimenti
  live a file specifici — UN puntatore vivo nel mirror hlp\_gradient.md (optimize\_performance.md), da rimuovere
  insieme.
- IMPLEMENTATION (D-414): git rm -r notes/analyses (86 file); il folder resta vuoto con un .gitkeep (resta
  nell'albero, dimora delle indagini future); puntatore del mirror rimosso (i fatti restano inline); Index
  dell'overview aggiornata ("the one-off analyses, empty for now — the past volumes live in the git history").
- VERIFICATION: guard VERDE sul set default.
- COMMIT: un solo commit (D-414).
- Session 91 (Roberto, trentasettesima richiesta): "Abbiamo fatto tutto quanto necessario per riformare la
  governance, manca solo l'ultimo step: Ridisegnare AGENTS.md, la cosa piu' importante per rendere efficace il lavoro
  fatto. Due strade: A- riassunto minimo di quanto abbiamo in notes; B- svuotiamo completamente e lasciamo solo:
  leggi notes/rules.md, notes/overview.md, notes/naming.md — sono parte del contesto. Second level: i 6 rule files +
  ideas.md. Ma tu sei l'agente, dammi il tuo parere autorevole. Fai un'analisi approfondita del percorso che una TASK
  attraversa e della maniera migliore per avere un CONTESTO non bloated, allineato agli obiettivi, consistente con le
  sue regole. Se andiamo con B, quanto contesto in tokens consumiamo solo per il PROMPT? Mi presenti l'analisi, e
  poi ti do indicazioni. Grazie!"
- ANALISI (mia): numeri misurati (AGENTS attuale 48 righe ~650 token; i tre file: rules 1938 + overview 981 +
  naming 780 = 3699). Percorso di una task: boot (l'UNICO contesto garantito e' l'iniezione di AGENTS) → lettura dei
  3 → rotta di zona (i 7 di secondo livello, set per-zona/per-rituale corretto) → lavoro → fine sessione. A e'
  sbagliato: un riassunto e' una COPIA — la malattia spenta in questo arco (si paga ad ogni modifica futura; un
  puntatore si paga una volta). B puro e' a rischio bootstrap: un agente che salta la lettura avrebbe zero
  invarianti. Proposta B+: i 3 obbligatori + 7 iron rules a una riga (la costituzione riassume le leggi ferree;
  l'unica duplicazione deliberata, esiste per garantire la lettura di tutto il resto). Costo: status quo ~1.7k →
  B+ ~4.1k obbligatorio, tutto single-source. Leva di riduzione futura: la re-review del register (1938).
- Roberto: "Siamo d'accordo a B+, ma procediamo con super cautela. 1: rimuovi tutto da scratch e da build/tmp;
  2: scrivi la tua versione B+ in scratch; 3: io la leggo; 4: no altre modifiche, no commit. Vai!"
- IMPLEMENTATION (bozza v1): scratch e build/tmp svuotati; il draft in scratch/AGENTS.md (30 righe, ~380 token).
  Riconoscenza per il D-415: 4 puntatori live sulla numerazione vecchia (docs\_rules.md:4 "standing rule 5"; i 2
  mirror di test "AGENTS.md rule 4"; R-010 "the standing instructions") — da riallineare nel commit.
- Roberto: "A me pare perfetto. Due piccole modifiche: sostituisci Roberto con user; rimuovi il reference D-122.
  Sempre versione in scratch."
- IMPLEMENTATION (bozza v2): le 2 modifiche applicate.
- Roberto: "Ultima domanda: esiste un comando che invece di 'chiedere' la lettura ... forza la injection? Come dire
  @nomedelfile?"
- ANALISI (mia, sul checkout DSH): no, non esiste un comando per messaggio (@ = un riferimento che l'agente legge
  col tool read, entra nel contesto come risultato di tool). L'iniezione e' per-NOME: DSH auto-inietta i nomi
  riservati AGENTS.md / CLAUDE.md (+ i .local), scopati per directory (root → cwd), sotto un byte budget; la lista
  dei candidati e' configurabile in deployment (instructionFileCandidates) — quella e' la leva per "forzare" un
  file arbitrario. Il design B+ regge: il garantito e' l'AGENTS piccolo, i 3 file entrano per lettura istruita.
- Roberto: "Per ora proviamo come va cosi'. Magari va bene e non serve altro. Dire di procedere alla modifica.
  Chiudi la sessione ... Git commit! Apriamo una nuova sessione e vediamo come va !!! Procedi"
- IMPLEMENTATION (D-415): AGENTS.md sostituito con il B+ approvato (30 righe); il draft ritirato da scratch/;
  riallineati i 4 puntatori (docs\_rules.md → R-330; R-010 → "boot protocol (the context pointers + the iron
  rules)"; i 2 mirror di test → R-100).
- VERIFICATION: guard VERDE sul set default; il runtime ha hot-reloadato la nuova AGENTS.md come baseline root.
- COMMIT: un solo commit (D-415). Sessione 91 chiusa — si apre una nuova sessione a provare il nuovo boot.
- Sessione 91 (Roberto, trentottesima richiesta): "Una sessione nuova ho cominciato. Penso tu sia in grado di
  leggerne il LOG ... solo un turno. Leggilo attentamente e dimmi che conclusioni ne trai. Grazie!"
- ANALISI (mia, del log della nuova sessione): il boot B+ funziona — l'agente conosce il protocollo (lo cita nel
  reasoning: "the rules say to read all three before work"), tiene identita' e lingua, e dalla sola iniezione di
  380 token ha il modello completo (ha elencato i next steps veri dall'overview: continuita' via entry point
  confermata, D-410). Unico bordo emerso: "before any work" interpretato come "prima di un task" (il saluto non
  conta come lavoro) — letta solo overview (1/3); al probe di Roberto ("Non hai letto rules e naming? NON
  leggerli, rispondi solo") rispose onestamente ("No, non li ho letti"), cito' la regola e si e' impegnato a
  leggere i 3 a inizio task. Token empirici: baseline ~8.8k (6.4k cache), la lettura dell'overview +3.8k, rules + naming
  would add ~3k; poi tutto in cache. La mia view: status quo difendibile (costo basso, contesto al primo task,
  onestà totale); se si vuole zero ambiguita', il single-word change e' "before answering the first message of a
  session" (variante eager, ~3.7k anche nelle sessioni di solo saluto). In attesa della call di Roberto.
- Session 91 (Roberto, trentanovesima richiesta): "Fai la modifica: yes 'before answering the first message of a
  session', vediamo in una nuova sessione se li legge subito tutti e tre ... Vai!"
- IMPLEMENTATION (D-416): AGENTS.md — trigger del boot da lazy a eager: "before any work" → "before answering the
  first message of a session" (una riga, il resto del boot protocol intatto).
- VERIFICATION: guard VERDE sul set default.
- COMMIT: un solo commit (D-416). Da verificare in una nuova sessione: li legge subito tutti e tre?

## 2026-10-03 — session 92 (D-417 — the 1-D shape guards out: la dual API è N-D, 18 commit, suite 968→1042)
- Session 92 (Roberto): sceglie il next-step #8 (rimozione della 1-D shape guard in board.py, l'allineamento
  DP-010) e approva lo scope completo "TUTTO A+B+C": ~20 interventi su 6 moduli (board, mobility, pattern,
  feature, random\_game, lm), ogni intervento come azione singola con suite completa verde + check perf + commit
  proprio, un solo D-numero per la campagna intera.
- IMPLEMENTATION (D-417): le guardie 1-D escono dalle famiglie di funzioni vettorizzate — cast, D8 (le 4
  riflessioni + transformations/anti\_transformations), kernel board (legal\_moves, position\_hash,
  position\_flips, position\_make\_move), mobility.compute\_indexes, pattern PatternSet.compute\_principal\_indexes
  + Pattern.compute\_indexes\_on\_position, feature.FeatureSet.compute\_indexes + i consumer lm, random\_game
  choose\_move/make\_move/play\_path. Pattern di casa: kernel numba 1-D invariati, gli array 1-D vanno DRETTO al
  kernel (no flatten copy — le field view strided sono non-contigue e ravel() le copiava: l'A/B perf l'ha
  catturato sul hash, 141 vs 307 M p/s, e la fast path 1-D è stata ripristinata negli 8 wrapper board come
  forward-fix disclosed nella campagna), gli array N-D fanno flatten C-order e reshape back alla forma di input.
- TRAPPOLE SISTEMATE: np.hstack concatena l'axis 1 per ndim>2 (feature.py → concatenate axis=-1); il
  reordering di asse dell'indexing avanzato in atrs[:, unique\_mask\_indexes] (pattern.py — flatten a (-1, 8)
  prima della selezione delle colonne); l'asse in pindexes[:, cols] dei consumer lm (bug N-D REALE in
  hlp\_wmaps\_compute + lo stesso pattern a un token in hlp\_anova/hlp\_analytics → [..., cols]); il contratto
  PRNG lockstep documentato come ordine degli elementi C-order (i tre docstring random\_game).
- TEST DISCIPLINE: i rejection 1-D convertiti in happy path N-D (2-D/3-D/F-order/empty per funzione); i pin di
  errore documentati mantenuti (shape mismatch, dtype pydantic, TypeError mixed-kind — il messaggio perde
  l'aggettivo 1-D). La suite cresce 968 → 1042, GREEN 1042/0/24 alla chiusura.
- VERIFICATION: suite completa LONG=1 verde a ogni confine di commit; 3 run PERF per azione numba-path, tutti a o
  sopra le mediane baseline (hash 368M vs 307M p/s, legal\_moves 145M vs 74.8M, play\_path 418-464K vs 414K
  games/s). Le mediane della finestra di chiusura (make\_move 32M, PatternSet 1.23M, Mobility 16.5M,
  FeatureSet 1.04M) sedevano sotto le baseline pre-campagna con load ~6: l'A/B back-to-back albero-baseline
  (b693367) vs HEAD con lo stesso protocollo e lo stesso load ha confermato NESSUN effetto codice — HEAD ≥
  baseline su ogni label (make\_move 37.8 vs 33.3M, PatternSet 1.45 vs 1.17M, Mobility 17.2 vs 17.5M,
  FeatureSet 1.39 vs 1.17M, legal\_moves 97.7 vs 86.8M): varianza ambientale, non regressione.
- COMMIT: 18 commit (D-417 01..13, 14, 15, 16, 17, 18-20) + questa notes wave.
- Next: candidati follow-up loggati nell'entry D-417 (l'EF N-D in lm/client.py, il contratto 1-D dello shuffle in
  tools/prng.py — left as-is, contratti di consumer documentati).

## 2026-10-03 — session 93 (governance: la rilettura tassativa post-compattazione, la colonna Suite dell'overview)

- Session 93 (Roberto): prima review della nuova governance. Due osservazioni: (1) dopo la compattazione non
  rileggo i files di rules come prescritto in AGENTS; (2) a chiusura di D-417 l'overview non era aggiornato —
  voluto o dimenticanza? Verificata: dimenticanza (l'update si era fermato alla riga next-step ritirata), e le
  due cose sono collegate: il notes wave è partito dal riassunto di checkpoint, eseguito come specifica.
- D-418: AGENTS.md — i tre context files si rileggono, in ordine, anche dopo OGNI compattazione del contesto,
  esattamente come all'avvio di sessione (il vecchio trigger, "primo messaggio di sessione", non si riattivava:
  una compattazione non riavvia la sessione).
- D-419: la colonna Suite/std\_run dell'overview era stantia dopo la notes wave di D-417 (il counter non era
  ri-eseguito alla chiusura): test\_board 247→294, test\_random\_game 33→42, test\_pattern 65→73,
  test\_mobility 26→30, test\_feature 25→29, test\_hlp\_wmaps 15→16, test\_hlp\_design\_matrix 14→15.
  Riparazione forward, disclosed qui e in decisions; gli altri 39 moduli tornano puntuali sullo stesso run.
- wsutils/suite\_audit.py: la tool non misura più nulla — la regex dei moduli (i nomi piatti reversi.test.NAME)
  non corrisponde al formato corrente del runner (test.reversi.NAME): exit 0 silenzioso, zero moduli eseguiti.
  Tabella misurata con un twin in scratch; la fix a una riga è poi entrata nel pacchetto del gate (approvata col
  proposal del wrapper — D-420).
- notes\_format.py: il re-wrapper passato su notes/log.md ha ri-wrapato l'intero volume aperto (~1100 righe,
  token conservati — nessuna perdita) e ha spezzato in due righe lo span in grassetto dell'entry D-341
  (violazione ESC): il journal resta hand-wrapped (il re-wrapper serve le zone a fixed-point: decisions,
  register), volume ripristinato da git e la sezione 93 ri-allegata a mano.
- D-418/D-419: date corrette 2026-10-04 → 2026-10-03 (errore mio: la sessione è ancora del 3 — lo ha catturato il
  timestamp del wrapper: 20:13 +02:00).
- D-420: il gate di checkin (R-210) — l'hook wsutils/hooks/pre-commit (tracked, installato via core.hooksPath)
  blocca il commit se il format guard è rosso sui notes file staged (un file diventa pulito quando viene toccato)
  o se l'overview auditor è rosso (le quattro liste tornano col tree, i Doc link resolve, la colonna Suite torna
  con la misura del wrapper). Il wrapper è il solo cammino della suite (file assente = rosso, fail-closed).
  Emendamenti approvati: R-210 nel register, R-840 (la suite corre col wrapper che scrive la misura), inventario
  wsutils. Testati: fail-closed, mismatch preciso (board 294→293), verde sullo stato finale; l'end-to-end live è
  questo checkin.
- VERIFICATION: notes\_lint verde sull'intero set; la suite via wrapper LONG=1 1042/0/24 GREEN prima di ogni
  commit (l'ultima misura: 45 moduli, 1042 test).
- Session closed by the user.
- Next: la domanda sulla regola pre-commit è chiusa col gate: niente re-read completo a ogni commit (lo strumento
  pesante) — il gap è chiuso meccanicamente da R-210, e la clausola R-250 che avevo proposto è assorbita dal gate
  (non aggiunta). Restano i candidati follow-up di D-417 (l'EF N-D in lm/client.py, il contratto 1-D dello shuffle
  in tools/prng.py).

## 2026-10-03 — session 94 (D-421/D-422 — la chiusura dei due follow-up di D-417: shuffle N-D, EF N-D)

- Session 94 (Roberto): l'ultimo candidato follow-up di D-417 — il contratto 1-D dello shuffle in tools/prng.py.
  Analisi presentata: il guard esplicito c'è solo sul generico, i tre typed fanno un row-shuffle silenzioso su
  N-D, nessun consumer in repo, il golden bit-exact non tocca gli shuffle; scelta dell'opzione A (N-D C-order per
  tutti e 4) in una sola azione.
- D-421: prng.py — il guard 1-D del generico esce; i 4 shuffle mescolano in-place i primi n ELEMENTI in ordine
  C-order per ogni forma: il ramo 1-D fa addressing diretto (no ravel, no copy — la classe di regressione di
  D-417), il ramo N-D passa via array.flat (no copy, F-order/strided sicure). Il motore vive ONCE nel privato
  \_shuffle\_slots (il pattern single-source del modulo, sulla falsariga della tecnica pick-from-set); i 4 metodi
  pubblici tengono i loro dtype check e i messaggi d'errore. Il contratto dei draw è identico nei due rami
  (n - 1 draw, n <= 1 consuma zero): la parity C-order (N-D == 1-D sul ravel, stesso seed) è ora un'identità
  pinned, senza nuovi numeri magici. Il row-shuffle silenzioso dei tre typed è sostituito dalla semantica C-order
  documentata; il golden resta intatto per costruzione (le 20 sezioni sono sequenze di stream, il path 1-D è
  byte-identico al codice pre-cambio).
- D-422: lm/client.py — l'ultimo candidato di D-417: l'array EF accetta una PositionArray strutturata di OGNI forma
  e restituisce float32 della stessa forma (C-order element order), bit-exact per posizione. Il guard 1-D esce:
  esisteva solo perché compute\_indexes era 1-D al tempo; da D-417 è N-D (restituisce positions.shape + (I,)),
  quindi bastava cambiare il sum axis — weights.sum(axis=-1) invece di axis=1: l'asse delle istanze è l'ultimo, e
  per il batch 1-D l'asse -1 è proprio l'asse 1 (bit-identico). Il pin di rejection 2-D diventa l'happy path della
  parity C-order (2-D/3-D, strided view, edge vuoti (0,N) e (K,0)); i pin EF a 6 posizioni (rlm\_04/rlm\_03) restano
  intatti.
- VERIFICATION: test\_prng 22 → 26 e test\_client 7 → 8; suite via wrapper 1047/0/24 GREEN; notes\_lint verde; i due
  gate verdi ai due checkin.
- Session closed by the user.
- Next: i due candidati follow-up di D-417 (lo shuffle 1-D in tools/prng.py, l'EF N-D in lm/client.py) sono
  entrambi chiusi (D-421, D-422).

## 2026-10-03 — session 95 (D-423 — binio house-style sweep: docstring R-560, contratto compressione, byte goldens)

- Session 95 (Roberto): analisi completa di binio (sorgente + unit test + mirror doc) prima della correzione: il
  tratto LZ4 (l'ultima aggiunta) era l'unica parte non passata dal formato pass di casa — commenti in italiano
  (R-100), mkdtemp nel /tmp di sistema (R-750/R-760), trailing whitespace, no Args/Returns (R-560), il
  `compressed` non documentato con la trappola digest pre-close, e un mirror doc che sovraccettava "byte-level
  pinned by round-trips" (auto-referenziale).
- D-423: binio.py — i 3 commenti italiani → English; trailing ws del corpo out; import order stdlib; pass R-560 su
  ogni docstring pubblica (Args:/Returns:/Raises:, lo stile di casa dopo pattern/feature/mobility): \_open\_arg,
  i due \_\_init\_\_ (prima senza docstring), write\_header, write\_string, write\_array (che ora dichiara la
  BinaryFormatError del dtype non supportato), read\_header, read\_string (nessuna prima), read\_array (nessuna
  prima), compute\_sha3\_256, write/verify\_sha3\_256\_sidecar; la prima riga di sha3\_256\_hexdigest resa
  imperativa; il servizio `compressed` documentato in entrambe le class docstring — inclusa la trappola digest: in
  modalità compressa l'hash è aggiornato solo alla close(), sui byte compressi, quindi pre-close la property è il
  digest dello stream vuoto. 603 → 734 righe.
- D-423: test\_binio.py — le 3 classi a base file migrate all'idioma di casa (TemporaryDirectory sotto
  CUSTOM\_TMP\_BASE + setUpClass mkdir + tearDown difensiva); +11 pin: LayoutGoldenTest (3 byte goldens
  hand-crafted, scalar/string/header — il layout pinned indipendentemente dall'accordo writer/reader), i valori
  speciali f32/f64, la quantizzazione f32 bit-exact (0.1 → float32), il round-trip latin-1, l'input big-endian →
  LE, lo short-read stitching (\_read\_exact via uno stream one-byte-at-a-time), il LZ4 decompression failure →
  BinaryFormatError, la traiettoria digest compresso (vuoto → completo); il commento desync corretto (fallisce il
  MAGIC post-value, non il primo) con il secondo read inaccessibile rimosso. 45 → 56.
- D-423: entrambi i mirror doc — l'overclaim out (i byte goldens), i gap "noted-only" ora pinned (Open issues:
  None. con fondamento), i conteggi per-file fuori dal doc (docs\_rules §4).
- VERIFICATION: binio + usage 59/0/0 (~0.03 s); suite via wrapper 1047 → 1058, GREEN 1058/0/24; notes\_lint
  verde; il gate verde a questo checkin.
- D-424: prng.py — formato pass, zero behavior change: R-560 completo sulle docstring pubbliche (imperative +
  Args:/Returns:/Raises:), HOW out (R-530: "delegates to the numba kernel", il paragrafo "How it works:" di
  extract), la frase duplicata in choose\_one\_from\_set64 via, l'annotazione di ritorno tuple\[np.uint64,
  np.uint8\] (era una tuple nuda, valida solo grazie a from\_\_future\_\_), i D-XXX fuori dai commenti plain
  (D-221 nel sorgente, D-421/D-417 nei test — R-540). Riparato test\_prng.md: stantio da D-421 (22 → 26 test, i 4
  test shuffle entrati in Coverage — la violazione di docs\_rules §5.1 è chiusa).
- D-425: prng.py — i guard di contratto (parte comportamentale): pick\_one\_from\_set64 (kernel pubblico in
  \_\_all\_\_) ora alza ValueError sul set vuoto — prima loop infinito (verificato: timeout 124); i due metodi
  della classe e il batch kernel lo guardavano già, quindi zero cambiamento nella pipeline.
  random\_choice\_from\_finite\_set: il guard k == 0 allargato a k <= 0 (prima k < 0 era territorio non
  dichiarato: OverflowError seed-dipendente, o 0 silenzioso sull'edge r == 0). +6 pin: il guard del kernel,
  k < 0, l'IndexError di n > elementi (1-D e N-D, comportamento invariato ora pinned), batch(0), il no-consume
  n = 0, i dtype di ritorno di choose\_one\_from\_set64 (np.uint64/np.uint8 — il re-wrap del boundary numba).
- VERIFICATION: test\_prng 26 → 30, GREEN 30/0/0 (~3 s); suite via wrapper 1058 → 1062, GREEN 1062/0/24;
  notes\_lint verde; il gate verde a questo checkin.
- Session closed by the user.
- Rotazione del decisions log (il log aperto a 1594 righe, oltre il cap di 1.000): il volume 006 chiuso —
  hist\_decisions/decisions\_006.md (D-333…D-425, 2026-09-29 → 2026-10-03) — il nuovo log aperto, l'Index
  dell'overview aggiornato.
- Next: il resto del backlog dell'overview (verifica delle fonti test, il rework MOBILITY, il README di
  progetto, il formato pass di board/pattern/feature/mobility + tools — binio e prng chiusi, la re-review del
  register).

## 2026-10-04 — session 96 (D-426 — prng reflow: le docstring a ~120)

- Session 96 (Roberto): reflow richiesto "con la larghezza della riga come da regole, sia codice che docstring"
  per tools/prng.py. Misurato prima di toccare: R-520 è un soffitto (~120, ogni riga fisica — codice, commenti,
  docstring) e il file era già conforme (545 righe, max fisica 99 caratteri, 0 righe oltre 120, no trailing ws;
  idem per tutta la storia git — D-201 → D-425 — e per il test mirror, max 86, e binio.py, max 87). L'utente ha
  scelto comunque il ri-avvolgimento dopo la misurazione: le docstring passano dal wrap ~72 di casa a ~120 —
  deviazione esplicita per-file (il wrap largo resta solo in prng.py; R-520 e lo stile degli altri file
  format-passati sono intatti).
- D-426: prng.py — i 20 docstring (doc del modulo, doc della classe, 15 metodi, 3 kernel di modulo) ri-avvolti
  greedy-120 da uno script one-shot (scratch/reflow\_prng.py, gitignored): prosa e descrizioni
  Args/Returns/Raises rifluiscono (le entry corte collassano su una riga, le 2 lunghe si avvolgono a
  continuation +4), la struttura delle sezioni e la tabella API indentata del doc del modulo restano verbatim;
  i commenti #, il codice e ogni riga non-docstring sono byte-identici a HEAD (verificato programmaticamente).
  Una nudge cosmetica oltre il greedy fill: nel doc del modulo il break che avrebbe lasciato "- 1, so a single
  seed..." a inizio riga è spostato di una parola, così "2^19937 - 1" resta insieme. Zero behavior change
  (solo docstring; i kernel numba ricompilano da codice identico). 545 → 485 righe.
- VERIFICATION: test\_prng 30/0/0 (inclusi i bit-exact goldens); suite via wrapper 1062/0/24 GREEN (invariata);
  notes\_lint verde; il gate verde a questo checkin.
- Il feedback di Roberto su D-426 (tre punti): il 120 è troppo — "mi piacerebbe una regola che stia nei 100
  caratteri come valore migliore e che, se necessario, possa andare a 120: non andiamo a capo per una singola
  parola"; la stessa regola va a formattare anche i commenti; il codice — i return dei get\_double\_in potevano
  stare su una riga sola.
- D-427 (regola): R-520 riscritta nel register (testo approvato così com'era): prosa (docstring + commenti) a 100
  come valore preferito, una riga può superare i 100 solo fino al soffitto di 120 per non lasciare una singola
  parola sola sulla riga successiva (se il pull-up superasse i 120, il break resta); il codice non ha wrap
  preferito — un'espressione spezzata che sta in una riga entro i 120 sta in una riga; il soffitto vale per ogni
  riga fisica.
- D-427 (applicazione a prng.py): i 20 docstring ri-avvolti a 100 + pull-up (il wrap 120 di D-426 scartato; 7
  righe finiscono a 101-110, tutte pull-up di parola singola legittimi); i 6 blocchi di commenti # ri-avvolti a
  100 (banner GPLv3, divider e commenti inline intatti); gli 8 merge di codice — i 3 return dei
  get\_double\_in (84/84/92), il join di random\_string\_az (100), i 3 twist senza backslash (98/105/99),
  l'assegnazione di \_\_init\_\_ (105) — i due spot a 105 approvati dall'utente dentro il soffitto. Due nudge
  manuali: "2^19937 - 1" resta insieme nel doc del modulo, il commento NN non parte con "/".
- D-427 (verifica): docstring e blocchi di commenti testualmente identici allo stato D-426 (solo i break si sono
  mossi — verificato per-blocco); lo script one-shot (scratch/reflow\_prng.py, gitignored) ha avuto due bug
  rilevati e corretti (il risultato del pass commenti perso per una copia, il test divider ingannato dallo spazio
  dopo il #) — la verifica finale lo attesta; i file restanti adottano la nuova R-520 al loro format pass.
  test\_prng 30/0/0 (i bit-exact goldens inclusi: i merge non cambiano lo stream); suite via wrapper 1062/0/24
  GREEN (invariata); notes\_lint verde; il gate verde a questo checkin.
- D-428 (wsutils/src\_reflow.py — la promozione dell'one-shot in wsutil): l'utente ha chiesto se lo script one-shot
  fosse promuovibile a wsutil per gli altri file; la calibrazione (382 docstring — 138 con sezioni Google, 146 con
  righe indentate — e 192 blocchi di commenti multi-riga sui 51 file sorgente) rende la classe di lavoro concreta.
  Design approvato: PROSA-ONLY (docstring + blocchi di commenti; i merge di codice restano il sotto-lavoro manuale
  del format pass, con i test per file), il nome src\_reflow.py, la check mode come default (il file è già punto
  fisso del fill greedy?) e --write con verifica pre-write (identità logica per docstring/blocco, parse del
  risultato, idempotenza — un file che fallisce è rifiutato, l'originale intatto). Quattro bug trovati dallo sweep
  sul workspace e uccisi (l'one-shot era provato solo su prng.py): le coordinate degli span stantie (gli span
  indicavano il file pre-pass mentre la lista viva si spostava — corretto facendo viaggiare i numeri di riga
  originali con le righe), le righe separatori # vuote consumate dal reflow (i paragrafi si fondevano — ora
  preservate), i paragrafi indentati-base con doppio spazio (i diagrammi ASCII di board.py) ri-avvolti come prosa
  (ora preservati), e la check sul soffitto assoluta che rifiutava 12 file con righe oltre i 120 PRE-ESISTENTI
  (ora check DELTA: il reflow non deve AGGIUNGERE righe oltre il soffitto, ma non è tenuto a ripararle — quello
  è il sotto-lavoro manuale del format pass). Verifiche: zero rifiuti/fallimenti su tutti i 51 file sorgente
  (31 would-reflow sotto i wrap vecchi, 7 già punto fisso); round-trip su board.py (1802 -> 1711 righe, i 294 test
  di board verdi, punto fisso dopo lo write — il file ripristinato: il suo reflow è una campagna di backlog);
  il tool self-canonical (si riavvolge da solo l'header ed è poi punto fisso); prng.py in check segna solo la
  nudge manuale di D-427 (il commento NN) e nient'altro — la deviazione documentata attesa (un file con break
  rifiniti a mano non è il punto fisso del fill greedy; la sezione SAFETY del tool dice: non dargli --write a
  cieca). La riga d'inventario in wsutils.md è questo commit.
- Campagna opt\_lbfgs (4 D approvati): l'utente chiede un'analisi completa di sorgente + test + mirror doc contro
  rules e doc\_rules, con verifica della formattazione, delle docstring, degli import non usati e della completezza
  dei test, e il pass src\_reflow.py come ultimo step. La view trova: la riga 362 a 133 caratteri (unica oltre il
  soffitto 120 nei due file); from \_\_future\_\_ import annotations inutilizzato (verificato via AST); 35 righe con
  trailing whitespace nel sorgente (4 nel banner di licenza); debug\_plot parametro MORTO (accettato dalla firma
  pubblica, mai usato nel corpo, il worker non lo passa); UnboundLocalError a max\_iters=0 (provato
  empiricamente); il commento D-146 in violazione di R-540 (referenza D in commento # normale + 13 righe di
  storia); 4 docstring numpydoc, 3 prime righe non imperative, i Returns di lbfgs senza il dict info a 9 chiavi,
  FixedSizeMaxList senza docstring; test con gap R-850/860 (il dict info mai assertato — tutti i test fanno
  x, \_ = lbfgs(...), i 3 stop-reason mai esercitati a runtime, niente run float32 end-to-end, la non-mutazione di
  x0 non assertata, logger mai esercitato — il test-doc li dichiara già come known open gaps); mirror doc con
  storia di performance (23.2→16.9 ms, 1.39×) vietata da doc\_rules §4 e senza il puntatore D-146 che §3.2
  richiede. Decisioni approvate: debug\_plot RIMOSSO (non cablato), guard ValueError sul boundary, 4 D separati
  (429 codice / 430 test / 431 docstring+reflow / 432 mirror doc).
- D-429 (fix del codice): (1) debug\_plot fuori dalla firma pubblica (il test quadratico smette di passarlo; le
  funzioni private mantengono il loro); (2) ValueError documentato per max\_iters < 1 o initial\_iter >=
  max\_iters (prima: UnboundLocalError); (3) via from \_\_future\_\_ import annotations; (4) l'annotazione
  save\_fn a 133 caratteri spezzata su due righe di firma; (5) 35 trailing ws puliti; (6) il commento D-146
  compresso a un summary WHY di 4 righe senza referenza D (i benchmark restano in decisions.md, il puntatore va
  nel mirror doc in D-432); (7) PEP8: size=, righe vuote di modulo → 2, commento FG. Zero behavior change tranne
  il nuovo ValueError; test\_opt\_lbfgs 14/0/0; il guard verificato (2 casi invalidi → ValueError, 1 run valido
  OK).

- D-430 (completamento dei test + test-doc): chiusi i gap R-850/860 della view (già dichiarati come known open gaps
  nel test-doc): +2 test di validazione per la guard di D-429 (max\_iters < 1 e initial\_iter >= max\_iters →
  ValueError); nuova classe TestLBFGSInfoContract (5 test): il dict info a 9 chiavi pinato per esteso (le chiavi,
  info\['w'\] = x restituito, f/g\_norm coerenti con una nuova valutazione fg(x), iters in (0, max\_iters],
  sl/yl/rho co-lunghi), la storia capped a m, x0 mai mutato (il contratto x0.copy() della probe E7), float32
  end-to-end (x, sl/yl, g\_norm restano f32 — il contratto delle Conventions del mirror doc, finora senza pin),
  il logger esercitato; nuova classe TestLBFGSStopReasons (3 test): i 3 reason strings pinati a runtime
  (CONVERGED\_MIN\_GRAD sul quadratico, MAX\_ITERS\_REACHED su Rosenbrock a 2 iters con iters == 2,
  CONVERGED\_LOW\_PROGRESS su una funzione quasi piatta f = 1 + 1e-12·‖x‖² — il decremento relativo staziona in
  f64). Pulizia: via il tag "O2b" dal messaggio di assert (docs\_rules §4), via il commento storico "Updated
  save\_fn signature…", i random draw uniformati su default\_rng (Zakharov cambia punto di partenza, converge
  sempre), 21 trailing ws via. Test-doc riscritto nello stesso commit (docs\_rules §5.1): 9 classi / 24 test,
  le 2 righe Coverage nuove, i reason literals nel Goldens pinned, il gap min\_grad/min\_p\_fun\_decrease
  rimosso dai known open gaps (restano restart, curvature skip e interni Hermite — integration-only come prima).
  14/0/0 → 24/0/0 (~0.05 s, tier fast invariato); docs auditor verde.

- D-431 (docstring + il pass src\_reflow): convertiti i 4 docstring numpydoc in Google Args/Returns/Raises
  (R-560): lbfgs, \_two\_loop\_recursion, \_hermite\_cubic\_interp, \_hermite\_cubic\_interp\_min;
  docstring completi per FixedSizeMaxList (classe + 4 metodi, incluso il contratto RuntimeError di max());
  prime righe imperative ovunque (la vecchia "…implementation with full gradient caching." era HOW, R-530).
  Il gap più grosso: i Returns di lbfgs documentano ora il dict info a 9 chiavi che mancava dal docstring
  sorgente (le chiavi, i reason literals, la semantica di iters, l'uso per il warm-start) + la sezione
  Raises (i 3 TypeError, il ValueError di D-429). Tipi: la convenzione di casa (precedente prng) — nomi
  semplici nella head dell'entry, i sottotitoli complessi nella prosa. Poi l'ultimo step: wsutils/src\_reflow.py
  --write su sorgente e test — 13 docstring ri-avvolti nel sorgente (629 righe totali), 9 nel test; entrambi
  i file sono ora punto fisso canonico del reflow (verificato con la check). Verifica: identità logica
  preservata (la verifica pre-write del tool), 24/0/0, zero behavior change.

- D-432 (rewrite del mirror doc — campagna chiusa): il source-doc riscritto allo stato nuovo (docs\_rules
  §5.2): l'API line ora a 16 parametri (via debug\_plot) e documenta per la prima volta il contratto di errori
  (i 3 TypeError, il ValueError di D-429) + i reason literals del dict info; l'Architecture perde la storia di
  performance (23.2→16.9 ms, 1.39×, 58 MB — vietata da §4: sta in decisions.md) e ha la scelta del buffer out=
  in una frase di rationale + il puntatore D-146 che §3.2 richiede qui; i Verified invariants ri-sincronizzati
  alla suite di D-430 (24 test / 9 classi, pin disambiguati per nome di classe — i 3 test\_a\_optimization
  omologhi), via il residuo "the run matches", più le pin nuove (info dict, stop reasons, x0, f32, logger,
  guard, cap m); Open issues resta None. (i gap restanti vivono nell'Integration del test-doc). Suite
  rimisurata via wrapper LONG=1: test\_opt\_lbfgs 14/0/0 → 24/0/0 (totale 1062/0/24 → 1072/0/24), cella Suite
  dell'overview aggiornata in questo commit; docs auditor verde su entrambi i mirror doc. Campagna
  opt\_lbfgs chiusa: 4 D (429 codice / 430 test / 431 docstring+reflow / 432 doc), sorgente e test a punto
  fisso canonico di src\_reflow, suite GREEN.

## 2026-10-04 — session 97 (D-433 — work report: il 18-anni vs 6-settimane rimisurato)
- Session 97 (Roberto): "due settimane fa ti avevo chiesto un report per misurare il lavoro svolto in 18 anni nel
  repo /home/rcrr/base/prj/reversi e confrontarlo con quanto fatto in poche settimane in questo repo. Credo che tu
  abbia già il tool in wsutils a questo scopo. Puoi per favore rifare il report."
- ANALISI: in wsutils/ il tool non c'è — l'inventario di notes/wsutils.md (8 tool: i re-wrapper, gli auditor, le
  misure della suite) non ne nomina nessuno di misurazione del lavoro, e la storia git di wsutils/ conferma che non è
  mai esistito nel tracked tree: il report di due settimane fa era generato ad hoc, l'artefatto è in scratch/
  (gitignored, perso). Il report viene rifatto misurando lo stato git registrato dei due repo (git log per
  commit/date/autori, git ls-files + wc per l'albero corrente, git log --numstat per il churn cumulativo).
- MISURAZIONE — legacy /home/rcrr/base/prj/reversi: 3150 commit (3108 non-merge), 2009-11-29 → 2026-08-05 (6093
  giorni ≈ 16.7 anni di git, il progetto precede l'era git), 1370 file tracked; albero corrente: C 342,842 righe
  (826 file), Python 30,607 (88), Java 28,466 (140) — esclusi i dump di dati SQL (10.6M di righe in 43 file); churn
  sorgente +607,247 / −143,463. Ritmi: 0.52 commit/giorno, 5.0 righe Python/giorno.
- MISURAZIONE — questo workspace: 772 commit, 2026-08-25 → 2026-10-04 (40 giorni ≈ 5.7 settimane); 271 file
  tracked: src 51 py (15,194 righe), test 52 py (22,610), probes 24 py (6,900), wsutils 8 file (2,070), docs 96 md,
  notes 26 md — totale Python 46,774 + Markdown 24,068; churn +208,405 / −115,290; suite 1072/0/24 (misura del
  2026-10-04). Ritmi: 19.3 commit/giorno, 1,169 righe Python/giorno.
- D-433 (il report): notes/analyses/work\_report.md — i due prospetti (per anno per il legacy; per zona per questo
  workspace), la tabella side-by-side e le caveat di lettura (linguaggi e ruoli diversi — il C da 343k righe non ha
  controparte; lo strato di governance — 432 decisioni, 97 sessioni, 8 tool, 24 probe, 24k righe md — non esisteva
  nel legacy; lo churn gonfiato dai re-write dei format pass). Headline: 19.3 vs 0.52 commit/giorno (37×), 1,169 vs
  5.0 righe Python/giorno (233×).
- VERIFICATION: numero ricontrollato contro i comandi git (i totali per linguaggio, i due churn, i due span);
  notes\_lint verde; il gate verde a questo checkin.
- COMMIT: un solo commit (D-433).

- D-434 (sorgente + source-doc): lo strip R-540 — via i riferimenti (D-072) dalla docstring di modulo e da
  \_verify\_checksum, il D-071 dall'entry is\_allowed, il tag "(R2, D-071)" dal commento step-3; le scelte di
  design restano come summary senza riferimento (decisione dell'utente: i puntatori D-071/D-072 — decisioni
  pre-notes, assenti da decisions.md e dai volumi — li eliminiamo dappertutto; il purge repo-wide è una D propria
  della campagna). Pass docstring (R-560): aggiunto il docstring mancante di \_compute\_sha3\_256\_hash; i 5
  docstring in Google (prime righe imperative, Args tipizzati, entry `tuple:` nei Returns al posto dell'elenco
  puntato). Formato: via il from \_\_future\_\_ import annotations non servito (3.12, le annotazioni PEP 604/604
  native — i 22 test confermano che il gate pydantic non è toccato), 12 trailing-ws, le 2 righe oltre-120 spezzate
  (i f-string WARN/ERROR dei logger, le stringhe di messaggio invariate), triplo blank normalizzato. Source-doc
  riscritto nello stesso commit (docs\_rules §5.1): via "194 lines." e il bullet Imports (è un indice, non
  architettura), i tag di campagna R1/R2/R3/M3 senza puntatori sostituiti dal rationale in prosa, via il residuo
  "incl. the R1 note". 22/0/0 (zero behavior change), docs auditor verde.

- D-435 (test): cleanup — via la narrazione di provenienza dal docstring di TestValidateCallCoercion
  ("probe\_rules.md §4: converted from the V17 probe…" — R-540: resta la descrizione del comportamento, via la
  storia); via il from \_\_future\_\_ import annotations non servito; 9 trailing-ws. Il modulo di test è COMPLETO
  (l'analisi non trova gap R-850 — a differenza di opt\_lbfgs): i 4 step + success, tutti i rami di fallimento
  (load che raise, validator False e che raise, checksum che raise, sidecar mancante/sballato/malformato/
  undecodable), i 5 casi di duck-typing, il coercion validate\_call, l'idempotenza del delete, il formato binio
  del sidecar — 22 test su ogni comportamento documentato. Test-doc invariato (il fix è solo un commento, il
  contenuto resta vero). 22/0/0 (zero behavior change).

- D-436 (il pass src\_reflow — l'ultimo step): wsutils/src\_reflow.py --write su sorgente e test — 6 docstring
  ri-avvolti nel sorgente (210 righe), 34 nel test (600 righe); entrambi i file sono ora a punto fisso canonico
  del reflow (verificato con la check). Verifica: identità logica preservata (la verifica pre-write del tool),
  22/0/0, zero behavior change.

- D-437 (purge repo-wide di D-071/D-072): la decisione dell'utente sulla campagna — li eliminiamo dappertutto,
  non solo in cache\_manager. I due numeri sono decisioni pre-notes (assenti da decisions.md e dai volumi) ma
  citati in 6 file fuori da cache\_manager: probes/verify\_cache\_manager.py (commento di header + i tombstone
  V1/V15 — la struttura D-106 resta, via la clausola D-072); probes/verify\_optimize.py (commento H7 + i due
  golden dei nomi check — via "(D-071 R1 pattern)", il fatto warm-cache resta in prosa);
  probes/verify\_hlp\_indexes.py (il golden "D5 the D-072 cache wiring" → "D5 the cache wiring");
  test/reversi/lm/test\_wrk\_su\_analysis.py (il commento); docs hlp\_su\_analysis.md (i 2 riferimenti in
  Architecture, il tag "manager's R2" in prosa, il puntatore D-303 resta — è un numero diverso);
  docs wrk\_su\_analysis.md (il riferimento del sidecar). I nomi-golden H7/D5 non erano citati da nessun doc
  (verificato prima del taglio). Verifica: il probe verify\_cache\_manager re-run (ALL PROBES PASSED, i 6
  check), i 4 .py parse, test\_wrk\_su\_analysis 10/0/1, docs auditor verde. Dopo questo D le uniche menzioni
  di D-071/D-072 sono l'entry di decisions e il bullet di D-434 — la storia, dove R-540 dice che sta.

- D-438 (sorgente + source-doc): lo strip R-540 — via tutti i 17 riferimenti D + 7 tag M dal sorgente (6 nelle
  docstring, 11 nei commenti #); le scelte di design restano come summary in prosa (state model, gate separato,
  concatenazione del filename prefix, rendering UTC-aware) e i puntatori dangling
  D-060/061/068/069/070/076/078/128/321 li eliminiamo dappertutto (decisione utente; il purge repo-wide dei 23
  file esterni è la D-441). Pass docstring (R-560): documentate le 10 funzioni prive di docstring
  (Worker.\_\_init\_\_, StateMachine.\_\_init\_\_ con il Raises sui nomi duplicati, \_history\_timer,
  \_run\_step, current\_worker\_name, show\_event\_log, show\_history\_of\_moves,
  export\_history\_of\_moves\_as\_csv, \_validate\_target\_step, \_execute\_move), i commenti # con tag M
  convertiti in docstring, i one-liner leggeri (log\_event, up, down) in Google con Args tipizzati. Formato: via
  il from \_\_future\_\_ import annotations non servito (3.12 — i 50 test confermano che le 7 superfici
  @validate\_call non sono toccate), 10 trailing-ws, triplo blank normalizzato. Source-doc nello stesso commit
  (docs\_rules §5.1): i 4 D-321 dangling in prosa (il fatto FINAL\_LOG\_PRINT resta), il "49 tests" storto → 51
  (il micro-test di D-439). 50/0/0 (zero behavior change), docs auditor verde.

- D-439 (test + test-doc): via le 2 narrazioni di provenienza dalle docstring dei guard-contract
  ("probe\_rules.md §4: …converted from the verify\_wrk\_config.py E2/E3 probe" — R-540: resta la descrizione,
  via la storia); via i 2 D-321 dangling (docstring del full-replay + commento dell'injection-pin, il fatto
  FINAL\_LOG\_PRINT resta); 19 trailing-ws. MICRO-TEST approvato: test\_csv\_export\_accepts\_str\_filename — il
  union filename str | Path era testato solo con Path; ora coperto (50 → 51 test). Il resto della suite è
  COMPLETO (niente altri gap R-850: stato, sentinella, failure/retry/recovery, gate, costruttore, matrice 6×5,
  iniezione, goldens frozen-clock, CSV). Test-doc nello stesso commit (docs\_rules §5.1): "49 tests" storto →
  51 (riga TestStateMachine 33 → 34 + la pin nuova), via i tag "R2" e "V17" e il D-321, stima runtime a ~0.2 s.
  51/0/0.

- D-440 (il pass src\_reflow — l'ultimo step): wsutils/src\_reflow.py --write su sorgente e test — 27 docstring
  ri-avvolti nel sorgente (499 righe), 63 nel test (892 righe); entrambi i file sono ora a punto fisso canonico
  del reflow (verificato con la check). Verifica: identità logica preservata (la verifica pre-write del tool),
  51/0/0, zero behavior change.

- D-441 (purge repo-wide dei 9 numeri dangling — chiusura campagna): D-060/061/068/069/070/076/078/128/321 sono
  decisioni pre-notes (verificato: 0 hit in decisions.md + volumi) citate in 22 file fuori dalla campagna —
  via da tutti e 22 (45 citazioni): 3 sorgenti worker (solo commenti), il test FINAL\_LOG\_PRINT (4 punti),
  6 mirror doc (i puntatori in prosa, i fatti restano), 4 test-doc (via le narrative "re-pin 18 -> 19" /
  "ruling"), 6 probe (i golden C9/D9/F3/A5/V3c rinominati in place — nessun doc li cita, verificato). Fuori
  scope approvato (lasciati, segnalati per la prossima onda): altri 15 numeri dangling trovati negli stessi
  commenti (D-065/074/075/079/080/081/083/097/142/157/186/187/287/289/318, tutti 0 hit). Verifica: i 10 .py
  parse, il probe verify\_final\_log\_print ri-eseguito (ALL PASSED), test\_wrk\_final\_log\_print 6/0/1,
  docs auditor verde. Dopo questo D le uniche menzioni dei 9 numeri sono gli entry di decisions + i bullet del
  journal — la storia, dove R-540 dice che sta.

- D-442 (purge onda 2 — i 15 numeri segnalati in D-441): D-065/074/075/079/080/081/083/097/142/157/186/187/
  287/289/318, tutti 0 hit in decisions.md + volumi (verificato). ~100 citazioni su 24 file: 4 sorgenti worker
  (solo commenti: i tag "config fingerprint (D-142)", le narrative "D-142 sidecar RETIRED", il tag "(D-074/R1)"),
  5 test (i tag "D-287 idiom" e il docstring "D-289 NO-DB suite"), 7 mirror doc + 5 test-doc (i tag di split
  wrk/hlp D-289 e le rif a "D-318 house style"), 10 probe (i golden rinominati in place + i due header di
  storia dei re-pin di verify\_logistic\_model e verify\_wrk\_features de-referenced: numeri di sessione,
  date e fatti di comportamento restano, via i D-numbers e i tag R1/R2/M). Fuori scope (lasciati, candidati
  onda 3 se il user la chiama): ~35 numeri limitrofi (D-082/084/085/092/096/098/099/101-106/105/130/139/
  143-149/175/258/278/279/295/298/312/313/314/315/317/326/327/328/331/332) — alcuni (D-09x/10x/14x) potrebbero
  essere decisioni reali dell'era notes: censimento da fare a richiesta. Verifica: i 24 .py parse, il probe
  verify\_wrk\_config ri-eseguito (0 mismatches — rinomina solo dei nomi, zero change di assert), docs
  auditor verde.

- D-443 (binio, la coerenza post-src\_reflow): il modulo era formattato PRIMA del tool e delle convenzioni
  docstring attuali — sweep: non a punto fisso (14 docstring), 13 docstring in forma espansa stantia (via la
  riga vuota, prima riga imperativa sulla tripla-quotatura), 6 Args R-560 non tipizzati (file ×3, path ×3), 4
  helper privati senza docstring (convenzione cache\_manager), un "from \_\_future\_\_ import
  annotations" morto (zero string annotations — lo stesso caso di state\_machine D-438), 4 trailing-ws
  nell'header.
  FIX: tutto + src\_reflow --write → 23 docstring canoniche, 689 righe. Il module docstring (design
  choices + byte layout + esempio) è GIÀ a convenzione (precedente prng) — intatto. 56/0/0, zero behavior
  change. Source-doc: "734 lines" → "689 lines" nello stesso commit.

- D-444 (binio test, la metà test della coerenza — specchio di D-443): non a punto fisso; 8 docstring di classe
  + il module docstring in forma espansa stantia → convenzione a-quote; 4 trailing-ws nell'header. FIX: tutto +
  src\_reflow --write → canonico, 651 righe (era 667). Nessun test aggiunto/tolto (56/0/0, zero behavior
  change); test-doc: niente da syncare (nessun riferimento a righe/stile — solo i conteggi per classe, tutti
  ancora corretti). VERDETTO DI COPERTURA (R-850): la suite è COMPLETA per il contratto documentato (goldens
  byte-level, i bound scalari + speciali f32/f64, i 10 dtypes + 0-d + F-order + big-endian, i path di errore
  del framing, le 3 guardie empty-suffix fail-fast, la trajectory LZ4, la magic-override). UN SOLO gap trovato
  (segnalato, NON fixato senza la decisione del user): l'idempotenza di close() (un close() esplicito dentro un
  with block — il re-close di \_\_exit\_\_) è guardata nel codice ma né documentata né pinned; candidata un
  micro-test di 4 righe + una riga di docstring (il precedente state\_machine D-439) se il user lo vuole.

- D-445 (il censimento onda 3 — CORRETTO + 1 residuo + la verifica del mirror prng): 1) il mirror doc di prng è
  FEDELE, verificato riga per riga (il \_\_all\_\_ esatto, NN=312 module-level, le costanti MM/UM/LM/MAG
  nel kernel, tutte le 15 API per firma + semantica, l'integrazione con random\_game) — e i suoi 3 ref (D-219,
  D-221 ×3, D-421) sono DECISIONI REALI del tipo legittimo (i puntatori one-sentence di docs\_rules: perché il
  design è così, non narrativa di provenienza) → restano. 2) I ~35 "candidati onda 3" di D-442 NON sono
  dangling: censimento completo di ogni D-NNN menzionato fuori notes/ (98 numeri distinti) contro TUTTI i
  volumi (hist\_decisions/000..006 = D-001..D-425 + attuale D-426..D-444, 443 entry) → ZERO dangling.
  ONDA 3: NON C'È NULLA DA PURGARE. 3) DISCLOSURE (riparazione forward): le onde 1-2 (D-441/D-442) sono state
  eseguite sulla FALSA premessa che i 24 numeri purgati fossero "dangling/pre-notes" — sono decisioni REALI: il
  check cercava solo in decisions.md attuale + un glob sbagliato (i volumi chiusi stanno in
  notes/hist\_decisions/decisions\_00N.md, mai cercati). Le modifiche restano comunque conformi alla
  legislazione (R-540 + docs\_rules: niente provenance narrative né campaign tag nel codice né nei mirror
  doc) — il fatto che i numeri siano reali non cambia questo; i fatti restano in prosa. Nessuna restaurazione
  proposta (riportare i campaign tag andrebbe CONTRO docs\_rules); il user è informato e decide. 4) UN RESIDUO
  sistemato (il mancatore dell'onda 1): hlp\_final\_log\_print.md:25 portava ancora "the D-321 addition" —
  il mio grep di verifica era filtrato con "grep -v 'tools/state\_machine'" e quella riga (che cita il path del
  mirror) era stata esclusa, producendo un falso "0 hit". Ora: tag via, puntatore al mirror doc tenuto.

- CHIUSURA SESSIONE (user): dopo la disclosure di D-445 l'user ha deciso "No, non facciamo nulla. va bene
  cosi." — lo stato attuale resta, nessuna restaurazione dei ref D nei mirror doc (chiuso il punto aperto di
  D-445). L'user dichiara i tools COMPLETAMENTE REVISIONATI: 5 moduli + 6 test + mirror doc + probe tutti a
  regime (punto fisso canonico del reflow — prng mantiene il hand-nudge di D-427 —, convenzioni docstring,
  doc nel budget e fedeli, suite 1073/0/24). PROSSIMA SESSIONE: la zona core di reversi (board / pattern /
  feature / mobility + i punti restanti dei Next steps).

- D-447 (board: la campagna di formato sul sorgente + il fix del reflow sui blocchi #): 1) TOOL FIX: il
  src\_reflow MANGIAVA i blocchi di comment multi-riga con prefisso # (doc-comment): strip del #, i due
  punti restavano come testo, il paragrafo riemesso come comment " : testo : testo" — e il check di
  identità pre-write passava lo stesso (identità a livello di parole) e l'output mangiato era il suo
  punto fisso. Scatenato da board.py, primo modulo con blocchi # multi-riga. FISSATO in
  reflow\_comments: il paragrafo con prefisso # viene riemesso con "# " (il colone-marker tolto dal
  testo), il # nudo è separatore di paragrafo; seg\_words esclude il colone-marker. Verificato: file
  pristine con i blocchi intatti, i 6 tools file restano canonici, prng invariato (il flag D-427 resta).
  2) SORGENTE: 61 docstring a regime di casa (prima riga on-the-quote, Args tipizzati, Raises) + 4
  docstring MANCANTI su funzioni pubbliche (square\_validate\_range, move\_validate\_range,
  position\_eq, position\_legal\_moves); R-540: i 9 ref D-XXX via (D-111, D-140 ×3, D-171, D-213 ×4
  — il contenuto di design resta, la storia via); l'import dead "from \_\_future\_\_ import
  annotations" via (zero string annotations); gli HOW clause di R-530 tagliati dove li porta già
  l'Architecture del mirror; bitboard\_count: "1D array inputs" → any shape (errore fattuale:
  np.bitwise\_count è any-shape); PEP8 (4 keyword-spacing + 5 compound di una riga); src\_reflow →
  canonico, 1957 righe (era 1802). NESSUN cambiamento di comportamento: 294/0/15. 3) board.md (stesso
  commit, la mirror rule): l'invariante STALE rimossa (il "1-D guard (2-D → ValueError)" — né il guard
  né il test esistono più dal contratto any-shape; il pin è il ValueError same-shape), il typo
  doppio-spazio nel pin sistemato, l'enumerazione dei kernel Numba completata (mancavano i 2 kernel
  batch D8), l'intro del contratto dual corretto (1-D → any-shape), 2 bullet duplicati tolti
  (D8 slot order + little-endian, detti altrove), size 204 → 200 (budget hub).

- D-448 (board: il test a regime — la metà test del sub-work, specchio di D-447): sweep: non punto fisso del
  reflow (11 docstring), 2 import dead (patch, npt), 172 righe di trailing-whitespace (4 nel GNU header — i
  separatori sono # nudi, 168 nel corpo), 2 docstring di classe con provenance ("session-38 scratch
  script/run" — puntatori dangling su scratch/, gitignored). I 53 docstring "Should …" LASCIAI COME SONO
  (user informato e decide — la conversione in imperativo è in sospeso). FATTI: tutto tranne gli Should +
  src\_reflow --write → canonico, 3798 righe (era 3846). NESSUN test aggiunto/tolto: 294/0/15 (nessun
  cambiamento di comportamento). test\_board.md sincronizzata: il conteggio header corretto (247 → 262
  concreti + 32 ereditati = 294 — il doc precede l'onda dei test N-D), i per-class ricontati (9 classi
  stali: FromSignedInt 5→9, ToSignedInt 6→10, FromHexStr 7→10, Transformations 7→10, AntiTransformations
  4→7, LegalMoves 13→16, Flips 16→19, MakeMove 17→20, Hash 13→17), il bulk 121 → 123 righe (ricontato due
  volte), il ref stale del messaggio "must be 1D" rimosso (il guard è morto col contratto any-shape; il pin
  è il ValueError same-shape), le etichette di campagna R1/R2/R4 via (comportamenti descritti in parole
  semplici), la frase duplicata dei print goldens sistemata.

- D-449 (i 4 micro-test del board — approvati dall'user dopo l'analisi di D-447): a) pin di copia per
  position\_ro000 (il twin position-layer del pin bitboard — la claim "returns a copy" del mirror doc è ora
  pinnata, R-850). b) pin no-alias per make\_position (array + liste) — l'invariante copy-then-view del
  mirror doc, ora pinnata in TestPositionCreation. c) 12 test di forma N-D per le rotazioni (2-D / 3-D /
  non-contiguo / vuoto per ro000, ro180, ro270) — chiusa l'asimmetria di copertura (le 4 riflessioni ce li
  avevano, ro090 solo 2-D, gli altri tre niente). d) Il wrap di square\_as\_bitboard per sq≥64 documentato
  (docstring + riga API del mirror doc) e il commento dangling "open decision (docs/src/reversi/board.md)"
  sistemato — il pin prima era undocumented, ora è legittimo R-850. Suite: 294 → 308 (14 nuovi, tutti verdi
  al primo giro); misurazione LONG=1 fresca (1087 totale) come input del gate, cella test\_board dell'overview
  sincronizzata (308/0/15/0/0). Entrambi i .py al punto fisso canonico del src\_reflow; i mirror doc
  sincronizzati nello stesso commit (test-doc: 274 concreti + 32 ereditati = 308, i 3 incrementi per-class, i
  2 pin nuovi nominati nella mappa Coverage).

- D-450 (board: la module docstring — la preview approvata dall'user): aggiunta dopo il banner GNU —
  il what-it-is (lo strato più basso dell'engine: square, move, bitboard, position, D8, legal
  moves, flips, scoring WOFC, Zobrist legacy-compatible) + i 6 bullet dei design choice (uint8
  square/move, bitboard, API dual scalar/array, hot path numba, gate pydantic, canone Zobrist
  legacy). src\_reflow → canonico, 1985 righe (era 1960). Nessun cambiamento di comportamento:
  308/0/15. Nessun cambiamento al mirror doc (il paragrafo what-it-is dell'header dice già la
  stessa cosa).

- D-451 (board: le 53 docstring "Should …" → imperativo — la scelta dell'user): ogni docstring di metodo
  che apriva con "Should <verbo> …" ora apre col verbo imperativo, maiuscolo: "Should convert
  np.int64 array to np.uint64 …" → "Convert np.int64 array to np.uint64 …". Solo strip del prefisso +
  maiuscola — nessuna altra parola toccata (R-570: restano light, una riga); i quattro "Should
  complete silently …" → "Complete silently …" tengono la dicitura dell'autore. La class docstring
  minuscola pre-esistente (TestPositionHashLegacyParity, descrizione noun-phrase) resta com'è.
  src\_reflow → canonico, 3949 righe. Nessun cambiamento di comportamento: 308/0/15.

- Chiusura del sub-work board (D-447..D-451): il bullet Next-steps segnato — board COMPLETE (format a regime:
  sorgente 1985 righe + test 3949 righe al punto fisso canonico del src\_reflow, docstring in forma di casa +
  module docstring, 4 micro-test, 53 "Should" → imperativo, mirror doc in budget e fedeli), il suite a
  1087/0/24 con misurazione LONG=1 fresca; restano pattern, feature, mobility.

- D-452 (board: via le diciture negative, decisione dell'user): tolta la frase "No game loop, no search, no
  clock, no UI." (module docstring + paragrafo what-it-is di board.md) e il "no portability work" (il bullet
  Zobrist, in entrambi i file) — il fatto "little-endian only" resta in entrambi. Il principio: scriviamo
  cosa fa il software, non cosa non fa. Nessun cambiamento di comportamento: 308/0/15, board.md 199 righe in
  budget.
