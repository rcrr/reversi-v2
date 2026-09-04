<!-- ARCHIVED — D-106 step 4 (the docs/ rewrite, 2026-09-04). Moved out
     of docs/src/twolm/board.md per docs_rules.md §1/§4: a mirror doc is
     a current-state snapshot and carries no verbatim appendices. This is
     a frozen historical record (session 1, 2026-08-25, original language
     kept): it is never updated. The R1-R5 and minor items below were
     resolved in the 2026-08-26/29 campaigns (notes/decisions.md
     D-014..D-018, the session 2/3 journals); this text keeps its
     original wording and its original errors, including the "Applys"
     mis-transcription (the actual typo is "Aplays", double p). -->

# board.py — full review (session 1, 2026-08-25)

_The original analysis, preserved verbatim in the original language
(Italian) as an artifact. It was Appendix A of
`docs/src/twolm/board.md` until the D-106 step 4 migration, which
moved it here losslessly._

### 1. Cosa fa

`board.py` è il **modello di dominio della scacchiera di Reversi/Othello**: tutto ciò che riguarda il "tabellone" e lo stato del gioco, ma non la logica di partita in sé (turni, orologio, regole di passaggio obbligatorie). Concretamente fornisce:

- **Tipi semantici**: `Square` (una casella, `uint8` 0–63, A1–H8), `Move` (64 mosse + `PA`=64 pass, `NA`=65, `UN`=66), `Bitboard` (insieme di caselle, `uint64`), `Position` (stato del gioco: coppia di bitboard `mover`/`opponent`).
- **Conversioni e utilità**: da/per stringhe ("A1", "PA"), da/per interi firmati (utile per PostgreSQL), da/per hex 16 caratteri, popcount, bit-scan reverse, stampa della scacchiera a 2D.
- **Le 8 simmetrie del gruppo D8** (4 rotazioni + 4 riflessioni) applicate a bitboard e a posizioni, scalari o array vettoriali — la materia prima per la normalizzazione delle posizioni (transposition table, ricerca simmetrica).
- **Generazione delle mosse legali** (algoritmo a scansione "Kogge-Stone" sui generator/propagator, vettorializzata e parallela).
- **Esecuzione delle mosse**: calcolo delle pedine da girare (`position_flips`), applicazione della mossa (`position_make_move`, con il pass che scambia i giocatori).
- **Funzioni di partita**: differenza pedine, punteggio finale secondo le regole WOFC (quadrati vuoti al vincitore), "deve passare?", "partita finita?", "mossa legale?".

### 2. Architettura

Il file è organizzato a **strati**, dal più basso al più alto:

```
Square (uint8)            →  Move (uint8)
        ↓                         ↓
Bitboard (uint64)  ← insiemi di caselle (bit i = casella i)
        ↓
Position (structured dtype: mover + opponent)
        ↓
operazioni di gioco (legal_moves, flips, make_move, scoring, D8)
```

Sopra questa spina dorsale ci sono due scelte progettuali trasversali molto marcate:

1. **API duale scalare/array ovunque.** Quasi ogni funzione pubblica accetta *sia* un bitboard scalare *sia* un array 1D e restituisce lo stesso tipo dell'input. Questo permette di usare le stesse funzioni per una singola posizione (interfaccia umana/test) o per pipeline vettoriali su milioni di posizioni (es. generazione dati o ricerca a larga scala).
2. **Numba JIT + `prange` per i hot loop** (trasformazioni D8, `legal_moves`), con `cache=True`, e **overload Numba** per i 4 operatori di base (`fa1h8`, `fh1a8`, `fhori`, `fvert`) così che siano riusabili anche all'interno di codice già JIT.
3. **Pydantic `@validate_call` su tutta l'API pubblica**, con `Annotated` + `BeforeValidator` per validare i dtype degli array numpy (`uint8`, `uint64`, structured `Position`) e `SkipValidation` per i scalar `np.void`.
4. **`Position` come structured dtype numpy** (`[('mover', u64), ('opponent', u64)]`): `make_position` costruisce un blocco `(…, 2)` di uint64 e lo *viewa* come array structured — un trucco zero-copy per la rappresentazione finale. Le funzioni D8 a livello position sono solo deleghe alle omonime a livello bitboard (buona separazione).

Il cuore computazionale sono due routine bit-trick classiche degli engine Othello: la propagazione Kogge-Stone per le mosse legali (4 direzioni × due sensi, con mascheri per i bordi colonna a/h) e la variante per il set di flip (`_kogge_stone_mm`, con il "blocker" che valida che il braccio sia effettivamente chiuso da una pedina del giocatore). I mascheri di bordo li ho verificati uno per uno: sono tutti corretti (es. per lo shift +7 il wrap cade nella colonna h, e infatti `_mask_l[1] = ~column_h`).

### 3. Commento su qualità e correttezza

#### Punti di forza

- **Qualità documentativa sopra la media**: docstring sistematici, e i diagrammi ASCII input/output per ciascuna trasformazione D8 sono documentazione eccellente (raramente si vedono in codice reale). `__all__` esplicito, nomi costanti, commenti che spiegano *perché* (es. il blocco di note su come vettorializzare `make_move` in futuro — segno di chi progetta, non di chi incolla).
- **Coerenza stilare**: pattern "is_scalar → atleast_1d → validazione ndim → dispatch → ri-adattamento dell'output" ripetuto identico in tutte le funzioni, facile da seguire e da estendere.
- **Le implementazioni bit-level sono le note in letteratura** (swap diagonale con maschere 0x550055…, 0x3333…, ecc.) e la formulazione generator/propagator di `legal_moves` è quella standard corretta. Ho verificato la propagazione su casi limite (bracci spezzati da quadrati vuoti, wrap su bordo): i mascheri e le formule sono corretti.
- **Design vettoriale ponderato**: separare `legal_moves` (vettorizzabile, parallelo, 10M+ posizioni) da `position_flips` (scalare, dichiarato esplicitamente tale) è onesto e sensato.

#### Problemi di correttezza (veri)

1. **`position_make_move` contraddice il suo docstring.** Il docstring dice *"When an illegal move is passed the same board is returned"*, ma il codice fa `_, updated = position_flips(p, m); return updated` — e per mossa illegale `position_flips` restituisce `(0, None)`, quindi **torna `None`, non la scacchiera invariata**. O il docstring è sbagliato o manca un `if updated is None: return p`. È il difetto più importante del file: chi usa la funzione in base alla documentazione può ricevere `None` dove aspetta una `Position`.
2. **Annotazione di ritorno sbagliata in `position_flips`**: dichiara `Tuple[Bitboard, PositionField]` ma restituisce `(Bitboard, None)` nel caso illegale. Dovrebbe essere `Tuple[Bitboard, PositionField | None]`.
3. **Dipendenza implicita sul comportamento di NumPy per il pass**: in `position_is_move_legal`, `move_as_bitboard(64)` produce `uint64(1) << 64`, che vale 0 *solo* perché NumPy definisce shift ≥ bit-width come 0. Il ramo "Pass move" dipende da questo fatto, documentato da nessuna parte. Funziona oggi, ma è fragile e non ovvio; un costante `MOVE_PASS = 64` con un check esplicito `move == 64` sarebbe molto più sano (il 64 già oggi appare come magico in più punti).
4. **Fragilità `bitboard_from_signed_int`/`bitboard_to_signed_int` sul caso scalare**: `i.view(Bitboard)` richiede che l'arricchimento arrivi come vero `np.int64` (o `np.uint64`). Se pydantic (con `arbitrary_types_allowed`) passa un `int` Python puro senza coercizione, si ottiene `AttributeError: 'int' object has no attribute 'view'` invece di un errore di validazione chiaro. Da verificare contro la versione di pydantic dipendente.
5. **`bitboard_count` usa `np.bitwise_count`**, che esiste solo da **NumPy ≥ 2.0**: dipendenza implicita, non dichiarata né commentata.

#### Difetti minori / incoerenze

- **Docstring con errori di contenuto**: in `bitboard_anti_transformations` la tabella elenca "- 0 -> 3 : ro180" ma l'implementazione (e la matematica del D8: l'inversa di ro270 è ro090) produce **ro090** in posizione 3 — il codice è giusto, la tabella no.
- **`bitboard_ro000` restituisce l'input stesso (aliasing), `position_ro000` restituisce `p.copy()`**: identità incoerente tra i due livelli (chi modifica il risultato dell'uno influenza l'input, dell'altro no).
- **Messaggio d'errore off-by-one** in `move_validate_range`: dice "range [0..67]" ma il massimo valido è 66 (il check `mo < 67` è giusto, il messaggio no). In `square_validate_range` il limite è hardcoded a 64 invece di usare il pattern a costante usato altrove.
- **Commento fuorviante** in `bitboard_from_hex_str`: `np.frompyfunc` *non* è un "C-level loop" — è un wrapper che gira in Python su object array; per lenti vettori è lento proprio lì dove il resto del modulo punta al throughput.
- **"Zero-copy" di `make_position`**: lo è solo il passaggio `view/reshape` finale; gli input vengono copiati in `data` via `np.empty` + assegnazione. Il docstring promette di più di quanto faccia.
- **Tabelle di funzioni come `np.array`**: `bitboard_trans_fs` e le liste di label sono array numpy di oggetti (callabili, stringhe). Funziona, ma liste/tuple Python sarebbero più idiomatiche.
- **Decorazioni Numba incoerenti**: `fastmath=True` sulle trasformazioni (irrelevantissimo per operazioni intere, in realtà solo rumore) e assente su `_vectorized_legal_moves`; `@validate_call` su funzioni che stanno sulla strada calda aggiunge overhead per chiamata — accettabile per una libreria, ma il trade-off andrebbe dichiarato.
- **Typos diffusi** (segnale di refurtiva mancata): "Aauthor", "Applys" (×5), "arry", "lenght", "lovercase", "rotaded", "does't", "whould", "Chanpionship" (anche nella citazione WOFC, dove l'originale dice "Championship").
- **Overload Numba su funzioni avvolte da `@validate_call`**: `@overload(bitboard_fa1h8)` punta al wrapper pydantic, non a una funzione nuda. Se la suite `test_board` lo verifica in contesto numba, va bene; altrimenti è un punto che merita un test dedicato, perché è il punto più fragile dell'integrazione numba/pydantic del file.
- **`legal_moves` è meno permissivo degli altri**: accetta solo `np.uint64`/`ndarray` (niente list, niente int Python), incoerente con il resto dell'API che accetta anche list.

#### Verdetto complessivo

È un codice **sopra la media**: architettura chiara e stratificata, hot path ottimizzato con criterio, documentazione abbondante e (per le D8) rara, invarianti di bordo gestiti correttamente. Il "motore" (legal moves, flips, simmetrie) è corretto dove ho potuto verificarlo a mano. I problemi veri sono concentrati nel **contratto delle API a livello alto** (`position_make_move` che restituisce `None` contro la documentazione, annotazioni imprecise, dipendenza sul wrap dello shift uint64 per il pass) e nella **consistenza dei dettagli** (aliasing vs copy, messaggi d'errore, docstring con tabelle sbagliate). Se dovessi lavorarci: prima la R1 (contratto di `position_make_move`), poi le costanti per i codici delle mosse, poi una passata di refurtiva sui docstring — e un test che copra esplicitamente l'integrazione overload-numba, che nel folder attuale non c'è.
