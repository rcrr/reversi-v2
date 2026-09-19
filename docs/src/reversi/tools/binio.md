# reversi/tools/binio.py
A minimal, C/Rust-interoperable binary I/O module: it frames every record between two identical 32-bit MAGIC markers
(spelling `BIN1` in little-endian), handles whole-file integrity via SHA3-256 sidecar files, and supports optional LZ4
whole-file compression. It is the on-disk foundation of the whole rlmwf cache system — every cache file and the model
weights file are written with `BinaryWriter` and verified through the `.SHA3-256` sidecar API.

## API

| name | contract |
|---|---|
| `BinaryWriter(file, *, magic, signature, checksum, checksum_suffix, compressed)` | Write framed records. Default `checksum=True` writes a `sha3_256sum`-format sidecar on `close()` (path-based) or exposes the digest via `sha3_256_hexdigest` (file-object-based). `compressed=True` buffers all writes in memory, compresses with LZ4, and writes on `close()`. An empty `checksum_suffix` raises `ValueError` in `__init__` (it would make the sidecar path BE the content file; `checksum=False` is the no-sidecar knob) |
| `BinaryReader(file, *, magic, signature, compressed)` | Read records in the exact order written. `compressed=True` decompresses the whole file into memory before reading |
| `FileHeader` | `namedtuple("FileHeader", ["description", "version"])` — return type of `read_header()` |
| `DEFAULT_MAGIC` / `DEFAULT_FILE_SIGNATURE` | The frame MAGIC (`0x314E4942` → LE `b'BIN1'`) and the header signature (`0x484F4942` → LE `b'BIOH'`); both are overridable per writer/reader |
| `BinaryFormatError` | Raised on MAGIC mismatch, unexpected EOF, unknown type code, corrupted sidecar, or LZ4 decompression failure |
| `compute_sha3_256(path, *, chunk_size=1 << 20)` | Return hex digest of a file |
| `write_sha3_256_sidecar(path, *, suffix=".SHA3-256")` | Write `<path><suffix>` sidecar; returns sidecar path. Empty `suffix` raises `ValueError` |
| `verify_sha3_256_sidecar(path, *, suffix=".SHA3-256")` | Recompute and compare; returns `bool`. Empty `suffix` raises `ValueError` |

## Architecture

603 lines.

- Constants: `DEFAULT_MAGIC = 0x314E4942` → LE `b'BIN1'` (framing/version check), `DEFAULT_FILE_SIGNATURE = 0x484F4942`
  → LE `b'BIOH'` (header file-type check), `TYPE_INT8`… `TYPE_FLOAT64` (1-10, the stable type-code contract with the
  C/Rust side), `_CODE_BY_NAME`, `_DTYPE_BY_CODE`, the pre-compiled little-endian `struct.Struct` singletons.
- `BinaryFormatError`; `_open_arg` — returns `(file_object, owns_it)`; the writer/reader close the file only when they
  own it (opened from a path); in compressed mode an internal `BytesIO` is always owned and closed.
- `BinaryWriter`: `__init__` (the empty-suffix guard, before the file is opened), `close` (the sidecar write), `_write`
  (incremental SHA3-256; in compressed mode the hash is deferred to `close()` over the compressed bytes), `_open_frame`,
  `_scalar`, `write_header`, `write_u8`…`write_f64`, `write_string`, `write_array`.
- `BinaryReader`: `__init__`, `_read_exact` (chunked loop handling short reads, `BinaryFormatError` on EOF before n
  bytes), `_expect_magic`, `_scalar`, `read_header`, `read_u8`…`read_f64`, `read_string`, `read_array`.
- Sidecar functions: `compute_sha3_256`, `write_sha3_256_sidecar` + `verify_sha3_256_sidecar` (both carrying the
  empty-suffix guard).

On-disk layout (all 4 record types, byte-level verified):

- Scalar: `[MAGIC u32][value][MAGIC u32]`
- String: `[MAGIC][length u64][UTF-8 bytes][MAGIC]` (length in bytes)
- Array: `[MAGIC][type_code u8][ndim u64][shape u64 ×ndim][raw C-contiguous LE data][MAGIC]`
- Header: `[MAGIC][signature u32][version u32][length u64][description bytes][MAGIC]`

## Verified invariants

Pinned by the 48-test suite (`test_binio` 45 + `test_usage_binio` 3, no DB) — no dedicated probe exists for binio; the
suite is the pinning instrument. The analysis's V1-V16 byte-level facts (manual byte inspection, zero mismatches) are
frozen in the archive.

- Framing + round-trip: `ScalarRoundTripTest` (10 — all 10 scalar types at their bounds, the `_round_trip` BytesIO
  helper), `StringTest` (4 — multibyte UTF-8, empty, byte-length-not-char-length), `ArrayTest` (8 — all 10 dtypes,
  multidim, empty, 0-d, writable (mutable copy, not a view), non-contiguous F-order, unsupported-dtype-raises,
  unknown-type-code-raises), `HeaderTest` (2), `FramingTest` (3 — MAGIC mismatch, wrong read order, truncated file).
- Checksums + sidecars: `Sha3_256SidecarTest` (7 — write+verify, the `sha3_256sum` format, corruption detection, missing
  sidecar raises, malformed sidecar raises, + the 2 empty-suffix guards: write raises with the content byte-identical,
  verify raises) and `AutoChecksumTest` (6 — sidecar on close, incremental digest == full re-read, disabled writes no
  sidecar, empty `checksum_suffix` raises on construction BEFORE the file is opened, the digest property on file
  objects, the digest raises when disabled).
- Compression: `Lz4CompressionTest` (4 — round-trip with path, actually compresses, the sidecar digest is over the
  COMPRESSED bytes, round-trip with file object).
- Whole document: `FullDocumentTest` (header + mixed scalars + string + 2 arrays, full read-back).
- Usage: `test_usage_binio` (3 — `with` / manual open-close / LZ4 cycles, each also verifying the sidecar; the "living
  documentation" tests).

## Open issues

None.

## Conventions

- The empty-suffix guards are fail-fast: raised before any file is opened (no file created).
- No PERF gates: the 48-test suite runs in ~0.02 s.
- Float32 special values (NaN, ±inf) round-trip but are not pinned by a test (manual verification only); `_read_exact`
  EOF is not directly unit-tested (covered indirectly by `FramingTest`).
- `test_usage_binio.py`'s naming deviates from the house `test_<module>.py` norm (report-only).

## Integration

- The rlmwf cache system: every cache file + the model weights file is a binio stream with a `.SHA3-256` sidecar —
  `cache_manager`'s step-3 checksum is a thin wrapper over `verify_sha3_256_sidecar` and `test_lm_worker_full_chain`
  pins the sidecar verification of the saved model.
- The C/Rust interop contract: MAGIC, the type codes 1-10, and the little-endian layouts are stable — the module
  docstring documents the byte layout.
- `test_usage_binio.py` has no doc of its own (pre-existing mirror gap, report-only — its 3 tests are pinned in the
  test_binio doc).
