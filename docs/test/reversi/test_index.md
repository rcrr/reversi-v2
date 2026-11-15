# test/reversi/test_index.py

The index unit suite — 4 classes / 10 tests, no DB, < 1 s. Pins the dtype aliases of the two index spaces (`Index` =
np.uint32, `ExtendedIndex` = np.int64) and the contract of their pydantic `BeforeValidator` wrappers.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestIndex` | 1 | the alias identity: `Index is np.uint32` |
| `TestIndexArray` | 4 | the base validator contract (uint32 enforced, non-arrays by identity) |
| `TestExtendedIndex` | 1 | the alias identity: `ExtendedIndex is np.int64` |
| `TestExtendedIndexArray` | 4 | the extended validator contract (int64 enforced, non-arrays by identity) |

The suite is flat: no setUp, no DB, no fixtures — every test builds its input inline. The two `*Array` classes pin
the `BeforeValidator` contract in a triple (reject the wrong dtype with the dtype name in the message, pass the
conforming ndarray through by identity, pass the non-array scalar through by identity) plus one wrapper-metadata
assertion per class.

## Goldens pinned

None. (No hash or value goldens in this suite — the pins are the dtype identities and the contract assertions.)

## Conventions

- one class per public name of the index spaces; a new alias or validator gets its own class in this file.
- the pass-through tests assert identity (`assertIs`), not value equality — a silent copy is a contract break.

## Integration

Mirrors `src/reversi/index.py` (the aliases and the two `BeforeValidator` functions). The `Index` / `IndexArray`
names are consumed across the pattern / feature / worker stack, so a dtype drift surfaces here first, at < 1 s cost.
