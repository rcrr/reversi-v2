# test/reversi/test_index.py
The index unit suite — 2 classes / 5 tests, no DB, < 1 s.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestIndex` | 1 | the alias identity: `Index is np.uint32` |
| `TestIndexArray` | 4 | the `validate_index_array` contract (a non-uint32 ndarray is rejected with the "uint32" message; the uint32 ndarray and the non-array scalar pass through by identity) + the Annotated wrapper carries the BeforeValidator metadata |

## Notes

- The `TestIndexArray` class moved here from `test_pattern.py` with the module extraction (D-522) — the validator
  lives in index.py now.
