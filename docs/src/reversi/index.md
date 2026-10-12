# reversi/index.py
The shared index-type module: the `Index` (np.uint32) alias + the `IndexArray` pydantic-annotated ndarray — the home
of the base-3 configuration-index concept used by pattern / mobility / feature and the lm data modules. No game
logic, no Numba — numpy + pydantic only.

## API

| name | contract |
|---|---|
| `Index` | type alias `np.uint32` — a base-3 configuration index (safe because S ≤ 18) |
| `IndexArray` | annotated ndarray; the BeforeValidator (`validate_index_array`, private) requires uint32 for ndarrays, scalars pass through |
| `ExtendedIndex` | type alias `np.int64` — the same index space as `Index`, plus the negative values (-1, -2, ...) which denote LOGICAL states of a feature configuration (the unseen-config sentinel, the no-config placeholder), not data |
| `ExtendedIndexArray` | annotated ndarray; the BeforeValidator (`validate_extended_index_array`, private) requires int64 for ndarrays, scalars pass through |

## Architecture

- `Index: TypeAlias = np.uint32`; `ExtendedIndex: TypeAlias = np.int64`; the two private validators raise
  `ValueError` on a non-matching ndarray and pass everything else through; `IndexArray` / `ExtendedIndexArray` are the
  matching `Annotated[NDArray[...], BeforeValidator(...)]` aliases.
- `__all__` = [Index, IndexArray, ExtendedIndex, ExtendedIndexArray] — the validators are OUT of `__all__` (wired only
  through the Annotated metadata).

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
  `hlp_su_analysis` (the chunk-matrix parameters); `ExtendedIndex` is the home type of the weight-map index tables
  (`hlp_wmaps`: iwmap / wmap / feature_w_ranges, the -1 sentinels), the config-id index operands
  (`hlp_generate`, `hlp_analytics`), and the feature offsets (the model-space index of a feature's first
  configuration).
