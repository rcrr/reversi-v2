# binio.py — analysis

Date: 2026-08-29. Module added by Roberto (3 files: binio.py + test_binio.py + test_usage_binio.py).
**Fix batch T1-T4 applied (D-051): suite 44 → 45/0/0 GREEN.**
**D-095 (2026-09-01, session 25): the empty-sidecar-suffix guard —
an empty `suffix` / `checksum_suffix` made the sidecar path BE the
content file, which the write paths truncated and overwrote (data
loss, empirically confirmed pre-fix); all three sidecar entry points
now raise `ValueError` (the writer fails fast in `__init__`, before
the file is opened); suite 45 → 48/0/0 GREEN.**

## Architecture

`binio` is a minimal, C/Rust-interoperable binary I/O module. It frames every
record between two identical 32-bit MAGIC markers (spelling `BIN1` in
little-endian), handles whole-file integrity via SHA3-256 sidecar files, and
supports optional LZ4 whole-file compression.

### Components

| Component | Role |
|---|---|
| `BinaryWriter(file, *, magic, signature, checksum, checksum_suffix, compressed)` | Write framed records. Default `checksum=True` writes a `sha3_256sum`-format sidecar on `close()` (path-based) or exposes the digest via `sha3_256_hexdigest` (file-object-based). `compressed=True` buffers all writes in memory, compresses with LZ4, and writes on `close()`. An empty `checksum_suffix` raises `ValueError` in `__init__` (D-095 — it would clobber the content file at `close()`; `checksum=False` is the no-sidecar knob). |
| `BinaryReader(file, *, magic, signature, compressed)` | Read records in the exact order written. `compressed=True` decompresses the whole file into memory before reading. |
| `FileHeader = namedtuple("FileHeader", ["description", "version"])` | Return type of `read_header()`. |
| `BinaryFormatError(Exception)` | Raised on MAGIC mismatch, unexpected EOF, unknown type code, corrupted sidecar, or LZ4 decompression failure. |
| `compute_sha3_256(path)` | Return hex digest of a file. |
| `write_sha3_256_sidecar(path, *, suffix=".SHA3-256")` | Write `<path><suffix>` sidecar; returns sidecar path. Empty `suffix` raises `ValueError` (D-095). |
| `verify_sha3_256_sidecar(path, *, suffix=".SHA3-256")` | Recompute and compare; returns `bool`. Empty `suffix` raises `ValueError` (D-095). |

### On-disk layout (verified — all 4 record types match the docstring)

- **Scalar**: `[MAGIC u32][value][MAGIC u32]`
- **String**: `[MAGIC][length u64][UTF-8 bytes][MAGIC]` (length in bytes)
- **Array**: `[MAGIC][type_code u8][ndim u64][shape[0]…shape[ndim-1] u64][raw C-contiguous LE data][MAGIC]`
- **Header**: `[MAGIC][signature u32][version u32][length u64][description bytes][MAGIC]`

### Constants

- `DEFAULT_MAGIC = 0x314E4942` → LE bytes `b'BIN1'` (framing/version check)
- `DEFAULT_FILE_SIGNATURE = 0x484F4942` → LE bytes `b'BIOH'` (header file-type check)
- `TYPE_INT8`…`TYPE_FLOAT64` (1…10): stable type-code contract with C/Rust side
- `_CODE_BY_NAME`: canonical dtype name → type code
- `_DTYPE_BY_CODE`: type code → LE numpy dtype
- Pre-compiled `struct.Struct` singletons: `_MAGIC`, `_U8`, `_I8`, `_U16`, `_I16`, `_U32`, `_I32`, `_U64`, `_I64`, `_F32`, `_F64` — all little-endian, standard sizes

## Verified facts (V1–V15)

All independently verified via pure Python / manual byte-level inspection, zero mismatches.

| # | Fact | Method |
|---|---|---|
| V1 | MAGIC = b'BIN1' LE | `struct.pack('<I', 0x314E4942)` |
| V2 | SIGNATURE = b'BIOH' LE | `struct.pack('<I', 0x484F4942)` |
| V3 | Type code ↔ dtype name round-trip | all 10 codes → `_DTYPE_BY_CODE` → `.name` → `_CODE_BY_NAME` → original code |
| V4 | Struct sizes = numpy itemsize | all 10 scalar types: `struct.size == dtype.itemsize` |
| V5 | Scalar on-disk layout | byte-level inspection of `write_u32(0xDEADBEEF)` |
| V6 | String on-disk layout | byte-level inspection of `write_string('città')` — length = 6 bytes (UTF-8) |
| V7 | Array on-disk layout | byte-level inspection of `int64 (2,3)` array — code=7, ndim=2, shape=(2,3), 48 bytes data |
| V8 | Header on-disk layout | byte-level inspection of `write_header('test', version=42)` |
| V9 | 0-d array round-trip | `np.array(42, dtype=np.int64)` → write → read → matches; avoids `ascontiguousarray` (which promotes 0-d to 1-d) |
| V10 | Non-contiguous (F-order) array round-trip | transposed array → `astype` + `tobytes(order="C")` → correct on-disk → correct read |
| V11 | Float32 special values | NaN, +inf, -inf all round-trip correctly |
| V12 | Big-endian input | `>i4` array → `astype(<i4)` via `write_array` → LE on disk → read as native LE |
| V13 | Empty array and `_read_exact(0)` | `np.array([], dtype=np.int32)` round-trips; `_read_exact(0)` returns `b''` |
| V14 | Incremental SHA3-256 = full re-read | `BinaryWriter` with `checksum=True` + `compute_sha3_256()` — matched |
| V15 | Compressed digest over compressed bytes | `BinaryWriter(compressed=True)` sidecar matches `compute_sha3_256()` on the compressed file |
| V16 | Empty sidecar suffix is rejected (D-095): `BinaryWriter(checksum_suffix="")` raises `ValueError` in `__init__` (before the file is opened — no file created), `write_sha3_256_sidecar(suffix="")` raises `ValueError` and leaves the content byte-identical, `verify_sha3_256_sidecar(suffix="")` raises `ValueError`. Pre-fix behaviour (empirically confirmed): the empty suffix made the sidecar path equal the content path, so both write paths truncated the content file and replaced it with the sidecar line (data loss) | 3-path probe (pre-fix) + 3 new unit tests (post-fix) |

## Design notes

### Checksum strategy
- `BinaryWriter` with `checksum=True` (default) hashes incrementally as bytes are written (`_write`).
- For compressed mode, the hash is deferred: it updates at `close()` over the compressed bytes only.
- For path-based writers, a `<path>.SHA3-256` sidecar is written automatically on `close()` in standard `sha3_256sum` format.
- For file-object-based writers (no path), the digest is available via the `sha3_256_hexdigest` property.
- `checksum=False` disables all hashing; `write_sha3_256_sidecar()` and `verify_sha3_256_sidecar()` remain available as standalone functions.

### Compression strategy
- `compressed=True` buffers all writes in a `BytesIO`, then compresses with `lz4.frame.compress` on `close()`.
- For path-based writers, the compressed data is written to the file; for file-object-based writers, it's written to the caller's object.
- The reader decompresses the entire file into memory with `lz4.frame.decompress` on `__init__`, then reads from a `BytesIO`.
- Memory implication: both writer and reader hold the full uncompressed payload in memory during compressed mode.

### File-object ownership
- `_open_arg` returns `(file_object, owns_it)`.
- `BinaryWriter` / `BinaryReader` only close the file when they own it (opened from a path) and only if it has a `close()` method and is not already closed.
- For compressed mode, an internal `BytesIO` is always owned and always closed.

### `_read_exact` chunked loop
- Handles short reads (streams that return fewer bytes than requested) by looping until `n` bytes are accumulated.
- Raises `BinaryFormatError` on EOF before `n` bytes.

## Defects

### T1 — `lz4` mandatory import, missing from `pyproject.toml` (D-051, FIXED)
### T2 — `from pathlib import Path` dead import (D-051, FIXED)
### T3 — Header typo `Aauthor` (D-051, FIXED)
### T4 — No test for unknown type code in `read_array` (D-051, FIXED)

All four disposed in the fix batch: lz4 added to pyproject.toml, Path import removed,
"Aauthor" → "Author", `test_unknown_type_code_raises` added to ArrayTest (now 45 tests).

## Observations (not defects)

- **No PERF gates**: 48/0/0 — the suite runs in ~0.02s. If the lz4 tests (which create temp files) become slow in CI, a PERF gate could be added.
- **`test_usage_binio.py` naming**: follows `test_<something>_binio.py` rather than the project norm `test_binio.py` / `test_binio_stress.py`. Does not affect function.
- **`_read_exact` EOF not directly unit-tested**: covered indirectly by `FramingTest.test_truncated_file_raises` and `FramingTest.test_wrong_read_order_detected`.

## Suite status

```
$ python -m unittest twolm.test.test_binio twolm.test.test_usage_binio
................................................
--------------------------------------------------------------
Ran 48 tests in 0.019s
OK
```

0 failures, 0 skipped (post D-095: 45 → 48 — the 3 empty-suffix guard tests).

### Test classes (test_binio.py — 45 tests)

| Class | Tests | Coverage |
|---|---|---|
| `ScalarRoundTripTest` | 10 | u8/i8/u16/i16/u32/i32/u64/i64/f32/f64 round-trip |
| `StringTest` | 4 | ASCII, multibyte UTF-8, empty, byte-length-not-char-length |
| `ArrayTest` | 8 | all 10 dtypes, multidim, empty, 0-d, writable, non-contiguous, unsupported-dtype-raises (write side), unknown-type-code-raises (read side, T4) |
| `HeaderTest` | 2 | round-trip, wrong-signature-raises |
| `FramingTest` | 3 | MAGIC mismatch, wrong read order, truncated file |
| `Sha3_256SidecarTest` | 7 | write+verify, sha3_256sum format, corruption detection, missing sidecar raises, malformed sidecar raises, write empty-suffix raises + content intact (D-095), verify empty-suffix raises (D-095) |
| `AutoChecksumTest` | 6 | sidecar on close, incremental=match_reread, disabled=no_sidecar, empty checksum_suffix raises on construction (D-095), digest property on file-object, digest raises when disabled |
| `FullDocumentTest` | 1 | header + mixed scalars + string + 2 arrays |
| `Lz4CompressionTest` | 4 | round-trip with path, actually compresses, checksum over compressed bytes, round-trip with file-object |

### Test classes (test_usage_binio.py — 3 tests)

| Class | Tests | Coverage |
|---|---|---|
| `UsageWithContextManagerTest` | 1 | Full write/read cycle with `with` |
| `UsageManualOpenCloseTest` | 1 | Full cycle with manual open/close |
| `UsageLz4CompressionTest` | 1 | Full cycle with LZ4 compressed=True |

All three usage tests also verify the SHA3-256 sidecar.

## Appendix: line-number reference (2026-09-01, post D-095 — everything
from `BinaryWriter.__init__` on shifted +10; the three guards added)

- `DEFAULT_MAGIC = 0x314E4942`: L116
- `DEFAULT_FILE_SIGNATURE = 0x484F4942`: L121
- `TYPE_INT8`…`TYPE_FLOAT64` (1–10): L125–L134
- `_CODE_BY_NAME`: L137
- `_DTYPE_BY_CODE`: L151
- `_MAGIC` (struct singletons): L165
- `BinaryFormatError`: L178
- `_open_arg`: L186
- `BinaryWriter` (class): L195 (docstring: the non-empty suffix note, D-095)
- `BinaryWriter.__init__`: L216 (empty-suffix guard L226-230, D-095)
- `BinaryWriter.close`: L273 (sidecar write L294)
- `BinaryWriter._write`: L304
- `BinaryWriter._open_frame`: L312
- `BinaryWriter._scalar`: L318
- `BinaryWriter.write_header`: L325
- `BinaryWriter.write_u8`…`write_f64`: L343–L352
- `BinaryWriter.write_string`: L356
- `BinaryWriter.write_array`: L370
- `BinaryReader` (class): L398
- `BinaryReader.__init__`: L405
- `BinaryReader._read_exact`: L447
- `BinaryReader._expect_magic`: L466
- `BinaryReader._scalar`: L474
- `BinaryReader.read_header`: L482
- `BinaryReader.read_u8`…`read_f64`: L504–L513
- `BinaryReader.read_string`: L517
- `BinaryReader.read_array`: L526
- `compute_sha3_256`: L550
- `write_sha3_256_sidecar`: L561 (empty-suffix guard L572, D-095)
- `verify_sha3_256_sidecar`: L584 (empty-suffix guard L592, D-095)