# reversi/index.py
The shared index-type module: the `Index` (np.uint32) alias + the `IndexArray` pydantic-annotated ndarray — the home
of the base-3 configuration-index concept used by pattern / mobility / feature and the lm data modules. No game
logic, no Numba — numpy + pydantic only.

## API

| name | contract |
|---|---|
| `Index` | type alias `np.uint32` — a base-3 configuration index (safe because S ≤ 18) |
| `IndexArray` | annotated ndarray; the BeforeValidator (`validate_index_array`, private) requires uint32 for ndarrays, scalars pass through |

## Architecture

- `Index: TypeAlias = np.uint32`; `validate_index_array(v)` raises `ValueError` on a non-uint32 ndarray and passes
  everything else through; `IndexArray = Annotated[npt.NDArray[np.uint32], BeforeValidator(validate_index_array)]`.
- `__all__` = [Index, IndexArray] — `validate_index_array` is OUT of `__all__` (wired only through the Annotated
  metadata).

## Verified invariants

Pinned by `test/reversi/test_index.py` (5 tests, no DB): the alias identity (`Index is np.uint32`), the validator
contract (the non-uint32 ndarray is rejected with the "uint32" message, the uint32 ndarray + the scalar pass through
by identity), and the Annotated wrapper carrying the BeforeValidator metadata.

## Open issues

None.

## Conventions

- The single home for the index types: pattern / mobility / feature and the lm data modules (hlp_indexes,
  hlp_su_analysis) all import from here — the former "import the type aliases from pattern" cross-dependency is
  gone (D-522).

## Integration

- Consumers: `pattern` (the base-3 kernels + the principal-index API), `mobility` (the `compute_indexes` return
  type), `feature` (the `FeatureSet.compute_indexes` return type), `hlp_indexes` (the dataclass field),
  `hlp_su_analysis` (the chunk-matrix parameters).
