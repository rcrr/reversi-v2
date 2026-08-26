# board.py analysis

_Analyzed: 2026-08-25 (session 1). Source: `src/twolm/board.py` (package
`twolm`), 1380 lines, GPL-3. Status: analyzed in depth, untouched.
Test suite: `src/twolm/test/test_board.py` (copied 2026-08-25, not yet
analyzed or run)._

## What it is
The board domain model of the Reversi/Othello engine: squares, bitboards,
positions, and everything that operates on them. No game loop, no search,
no clock, no UI.

## Architecture
Layered, low → high:

```
Square (uint8, 0..63, A1..H8)        Move (uint8, 0..63 + 64=PA, 65=NA, 66=UN)
        \            /                        \
         Bitboard (uint64; bit i = square i)  Move utils
              \
               Position = numpy structured dtype [('mover',u64), ('opponent',u64)]
                    \
             game ops: legal_moves, flips, make_move, WOFC scoring, D8 symmetry
```

Cross-cutting design decisions:
1. **Dual scalar/array API** — every public function accepts a scalar OR a
   1-D array (lists in most, via np.asarray) and returns the input kind.
   Enables interactive/test use and vectorized pipelines over millions of
   positions with the same entry points.
2. **Numba** — `njit(cache=True)` + `prange` for hot loops (D8 transforms,
   legal moves); `@overload` numba overloads for the four D8 primitives
   (fa1h8, fh1a8, fhori, fvert), registered on the pydantic-wrapped
   functions (see minor issues: needs a numba-context test).
3. **Pydantic** — `@validate_call` on all public functions; `Annotated` +
   `BeforeValidator` for numpy dtype checks; `arbitrary_types_allowed`;
   `SkipValidation` for scalar `np.void`.
4. **Position zero-copy trick** — `make_position` builds a C-contiguous
   (…,2) uint64 block and `.view()`s it as the structured dtype (the view
   is zero-copy; the inputs are copied into the block).
5. **D8 group** — 4 rotations (ro000/090/180/270) + 4 reflections (fvert,
   fhori, fa1h8, fh1a8), scalar + vectorized (N,8) versions, forward and
   anti-transformations, plus function tables (`bitboard_trans_fs`, …) and
   label tables. Classic bit-trick implementations (Kogge-Stone-style
   masks 0x550055…, 0x3333…, etc.).

## Verified invariants (checked by hand, 2026-08-25)
- **Legal-move boundary masks correct** for all 4 directions × both senses:
  wrap targets are +1→col a, +7→col h, +8→none, +9→col a (and mirrored for
  the `>>` senses: _mask_r). Masking `p` (the opponent set) clears the wrap
  landing column, which is the right place to kill false positives.
- **Generator/propagator formulation correct**, including broken lines:
  opponent runs interrupted by an empty square do not produce false moves —
  the `p &= (p << k)` step kills propagation at the first non-opponent cell.
  Traced multi-run lines (mover, opp, empty, opp, mover → only the first
  target is legal): correct.
- **`_kogge_stone_mm` (flip set) correct**: the 1/2/4 Kogge-Stone steps
  cover runs up to 7 discs; the final `p` update after step 4 is
  intentionally omitted; the blocker `gt` requires a mover disc immediately
  past the run end; the final `& ~generator` excludes the move square.
- **Anti-D8 table: code is correct** (ro090↔ro270 swapped, rotations
  self-paired, reflections self-inverse). The docstring table of
  `bitboard_anti_transformations` has a typo at index 3 (says ro180; the
  code produces ro090).
- **`position_is_game_over`** = both players have zero legal moves (a full
  board is a degenerate case that also yields true). Correct standard
  definition.
- **`position_final_value`** implements WOFC: empty squares to the leader;
  tie → 0 difference. Correct.

## Real issues (candidates for fix, priority order)
- **R1. RESOLVED (2026-08-26, T36/T37, D-017).** `position_make_move`
  returns `None` on an illegal move while its docstring promised "the
  same board is returned". Roberto chose "docstring follows the code":
  the docstring now reads "When an illegal move is passed None is
  returned." and the return annotation was corrected to
  `PositionField | None`. Code behavior unchanged; the existing
  `test_position_make_move_illegal_returns_none` pin stays as is.
- **R2.** `position_flips` return annotation is wrong: declares
  `Tuple[Bitboard, PositionField]` but returns `(Bitboard, None)` for
  illegal moves. Should be `… | None`.
- **R3. RESOLVED (2026-08-26, T38, D-018).** `position_is_move_legal`
  PA branch now uses an explicit `move == 64` check instead of relying
  on `uint64(1) << 64 == 0`. `move_as_bitboard` documents that the
  non-square codes (64 PA, 65 NA, 66 UN) wrap to the empty bitboard per
  NumPy's defined shift semantics (shift >= bit width -> 0, verified on
  NumPy 2.5.2). Behavior unchanged; the existing pass-branch pins
  (pass legal iff no legal moves; codes 65/66 illegal) all stay valid.
- **R4.** Scalar case of `bitboard_from_signed_int` / `bitboard_to_signed_int`:
  `i.view(Bitboard)` requires a real `np.int64`/`np.uint64`; a bare Python
  int passed through pydantic (arbitrary-type handling varies by version)
  would give `AttributeError` instead of a validation error. Needs a
  version-pinned test.
- **R5.** `bitboard_count` uses `np.bitwise_count` → implicit **NumPy ≥ 2.0**
  dependency, declared nowhere.

## Minor issues / inconsistencies
- `bitboard_ro000` returns the input (aliasing), `position_ro000` returns a
  copy — inconsistent identity between the two layers.
- `move_validate_range` error message says "range [0..67]" but the max valid
  value is 66 (the check itself is correct).
- `square_validate_range` hardcodes 64 while the move version uses a
  constant — inconsistent pattern.
- `bitboard_from_hex_str` uses `np.frompyfunc` with a comment claiming a
  "C-level loop": it is actually a slow Python-level object-array wrapper.
- `make_position` "zero-copy" claim applies only to the final view, not the
  inputs (copied into `data`).
- Function/label tables are `np.array` of objects; plain Python
  lists/tuples would be more idiomatic.
- Numba decoration inconsistent: `fastmath=True` on D8 transforms (irrelevant
  for integer ops) and absent on `_vectorized_legal_moves`.
- `legal_moves` is stricter than the rest of the API: only accepts
  `np.uint64`/`ndarray` (no lists, no Python ints).
- Typos: "Aauthor" (header), "Applys" (×5 docstrings), "arry", "lenght",
  "lovercase", "rotaded", "does't", "whould", "Chanpionship" (the WOFC quote
  says "Championship" in the original).
- Numba overloads registered on `@validate_call` wrappers (not raw
  functions): needs a dedicated test in a numba context.

## Conventions to respect in any new work on this file
- Dual scalar/array API, same validation pattern
  (is_scalar → atleast_1d → ndim check → dispatch → reshape back).
- `@validate_call` + `arbitrary_types_allowed` on every public function.
- Docstring style: thorough, with ASCII input/output diagrams for transforms.
- Hot loops vectorized (numba + prange); scalar-only parts declared
  explicitly (as `_kogge_stone_mm` is).
- Move codes 64/65/66 exist but are magic numbers (I-003).

---

## Appendix A — full review (session 1, 2026-08-25)

_Preserved verbatim in the original language (Italian) as an artifact._

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
