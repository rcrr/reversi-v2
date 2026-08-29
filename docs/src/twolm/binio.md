# binio.py — analysis

Date: 2026-08-29. Module added by Roberto (3 files: binio.py + test_binio.py + test_usage_binio.py).

Suite: **44 tests, GREEN 44/0/0** (41 in test_binio + 3 in test_usage_binio). No PERF gates.

## Architecture

`binio` is a minimal, C/Rust-interoperable binary I/O module. It frames every
record between two identical 32-bit MAGIC markers (spelling `BIN1` in
little-endian), handles whole-file integrity via SHA3-256 sidecar files, and
supports optional LZ4 whole-file compression.

### Components

| Component | Role |
|---|---|
| `BinaryWriter(file, *, magic, signature, checksum, checksum_suffix, compressed)` | Write framed records. Default `checksum=True` writes a `sha3_256sum`-format sidecar on `close()` (path-based) or exposes the digest via `sha3_256_hexdigest` (file-object-based). `compressed=True` buffers all writes in memory, compresses with LZ4, and writes on `close()`. |
| `BinaryReader(file, *, magic, signature, compressed)` | Read records in the exact order written. `compressed=True` decompresses the whole file into memory before reading. |
| `FileHeader = namedtuple("FileHeader", ["description", "version"])` | Return type of `read_header()`. |
| `BinaryFormatError(Exception)` | Raised on MAGIC mismatch, unexpected EOF, unknown type code, corrupted sidecar, or LZ4 decompression failure. |
| `compute_sha3_256(path)` | Return hex digest of a file. |
| `write_sha3_256_sidecar(path)` | Write `<path>.SHA3-256` sidecar; returns sidecar path. |
| `verify_sha3_256_sidecar(path)` | Recompute and compare; returns `bool`. |

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

### T1 — `lz4` mandatory import, missing from `pyproject.toml`
`import lz4.frame` at module level (L99). Without `lz4` installed, `import twolm.binio` raises `ModuleNotFoundError`. `lz4` is not listed in `pyproject.toml` dependencies.

**Severity**: Hard import failure. Either `lz4` should be added to `pyproject.toml` (simplest), or the import should be made lazy (import inside the compressed code paths only).

### T2 — `from pathlib import Path` dead import (L96)
`Path` is imported but never used. The module uses `os.PathLike` for isinstance checks and `os.fspath` for path conversion; `Path` is never referenced.

**Severity**: Cosmetic — unused import.

### T3 — Header typo `Aauthor` (L7)
`# Aauthor Roberto Corradini` → `# Author Roberto Corradini`. Classic copy-paste artifact from the original 2008 headers, seen in other modules too.

**Severity**: Cosmetic — comment only.

### T4 — No test for unknown type code in `read_array`
`BinaryReader.read_array()` raises `BinaryFormatError("unknown array type code: {code}")` when the on-disk type code is not in `_DTYPE_BY_CODE`. This path has no test coverage (verified by manual injection of type_code=99).

**Severity**: Uncovered error path. Low risk (foreign files are caught by MAGIC and signature first), but the error message and exception type should be pinned by a test.

## Observations (not defects)

- **No PERF gates**: 44/0/0 — the suite runs in ~0.017s. If the lz4 tests (which create temp files) become slow in CI, a PERF gate could be added.
- **`test_us_age_binio.py` naming**: follows `test_<something>_binio.py` rather than the project norm `test_binio.py` / `test_binio_stress.py`. Does not affect function.
- **`_read_exact` EOF not directly unit-tested**: covered indirectly by `FramingTest.test_truncated_file_raises` and `FramingTest.test_wrong_read_order_detected`.

## Suite status

```
$ PERF=0 python -m unittest twolm.test.test_binio twolm.test.test_usage_binio
............................................
--------------------------------------------------------------
Ran 44 tests in 0.016s
OK
```

0 failures, 0 skipped.

### Test classes (test_binio.py — 41 tests)

| Class | Tests | Coverage |
|---|---|---|
| `ScalarRoundTripTest` | 10 | u8/i8/u16/i16/u32/i32/u64/i64/f32/f64 round-trip |
| `StringTest` | 4 | ASCII, multibyte UTF-8, empty, byte-length-not-char-length |
| `ArrayTest` | 7 | all 10 dtypes, multidim, empty, 0-d, writable, non-contiguous, unsupported-dtype-raises |
| `HeaderTest` | 2 | round-trip, wrong-signature-raises |
| `FramingTest` | 3 | MAGIC mismatch, wrong read order, truncated file |
| `Sha3_256SidecarTest` | 5 | write+verify, sha3_256sum format, corruption detection, missing sidecar raises, malformed sidecar raises |
| `AutoChecksumTest` | 5 | sidecar on close, incremental=match_reread, disabled=no_sidecar, digest property on file-object, digest raises when disabled |
| `FullDocumentTest` | 1 | header + mixed scalars + string + 2 arrays |
| `Lz4CompressionTest` | 4 | round-trip with path, actually compresses, checksum over compressed bytes, round-trip with file-object |

### Test classes (test_usage_binio.py — 3 tests)

| Class | Tests | Coverage |
|---|---|---|
| `UsageWithContextManagerTest` | 1 | Full write/read cycle with `with` |
| `UsageManualOpenCloseTest` | 1 | Full cycle with manual open/close |
| `UsageLz4CompressionTest` | 1 | Full cycle with LZ4 compressed=True |

All three usage tests also verify the SHA3-256 sidecar.

## Appendix: line-number reference (2026-08-29)

- `DEFAULT_MAGIC = 0x314E4942`: L117
- `DEFAULT_FIEL_SIGNATURE = 0x484F4942`: L122
- Type codes: L126–L135
- `_ CODE_BY_NAME`: L138–L149
- `_ DTYPE_BY_CODE`: L152–L163
- `struct.Struct` singletons: L166–L176
- `BinryFormatError`: L179
- `_ open_arg`: L187
- `BinryWriter.__init__`: L212
- `BinryWriter.close`: L264
- `BinryWriter._write` / `_ open_frame` / `_ close_frame` / `_ scalar`: L295–L312
- `BinryWriter.write_header`: L316
- `BinryWriter.write_u8`…`write_f64`: L334–L343
- `BinryWriter.write_string`: L347
- `BinryWriter.write_array`: L361
- `BinryReader.__init__`: L396
- `BinryReader._read_exact`: L438
- `BinryReader._expect_magic`: L457
- `BinryReader._scalar`: L465
- `BinryReader.read_header`: L473
- `BinryReader.read_u8`…`read_f64`: L495–L504
- `BinryReader.read_string`: L508
- `BinryReader.read_array`: L517
- `compuete_sha3_256`: L541
- `writte_sha3_256_sidecar`: L552
- `veriyy_sha3_256_sidecar`: L568