# reversi/tools/binio.py
A minimal, C/Rust-interoperable binary I/O module: it frames every record between two identical 32-bit MAGIC markers
(spelling `BIN1` in little-endian), handles whole-file integrity via SHA3-256 sidecar files, and supports optional LZ4
whole-file compression. It is the on-disk foundation of the whole rlmwf cache system — every cache file and the model
weights file are written with `BinaryWriter` and verified through the `.SHA3-256` sidecar API.

## API

| name | contract |
|---|---|
| `BinaryWriter(file, *, magic, signature, checksum, checksum_suffix, compressed)` | Write framed records. Default `checksum=True` writes a `sha3_256sum`-format sidecar on `close()` (path-based) or exposes the digest via `sha3_256_hexdigest` (file-object-based); in `compressed` mode the digest is over the compressed bytes and complete only after `close()`. `compressed=True` buffers all writes in memory, compresses with LZ4, and writes on `close()`. An empty `checksum_suffix` raises `ValueError` in `__init__` (it would make the sidecar path BE the content file; `checksum=False` is the no-sidecar knob) |
| `BinaryReader(file, *, magic, signature, compressed)` | Read records in the exact order written. `compressed=True` decompresses the whole file into memory first; a failed LZ4 decompression raises `BinaryFormatError` |
| `FileHeader` | `namedtuple("FileHeader", ["description", "version"])` — return type of `read_header()` |
| `DEFAULT_MAGIC` / `DEFAULT_FILE_SIGNATURE` | The frame MAGIC (`0x314E4942` → LE `b'BIN1'`) and the header signature (`0x484F4942` → LE `b'BIOH'`); both are overridable per writer/reader |
| `BinaryFormatError` | Raised on MAGIC mismatch, unexpected EOF, unknown type code, corrupted sidecar, or LZ4 decompression failure |
| `compute_sha3_256(path, *, chunk_size=1 << 20)` | Return hex digest of a file |
| `write_sha3_256_sidecar(path, *, suffix=".SHA3-256")` | Write `<path><suffix>` sidecar; returns sidecar path. Empty `suffix` raises `ValueError` |
| `verify_sha3_256_sidecar(path, *, suffix=".SHA3-256")` | Recompute and compare; returns `bool`. Empty `suffix` raises `ValueError` |

## Architecture

734 lines.

- Constants: `DEFAULT_MAGIC = 0x314E4942` → LE `b'BIN1'` (framing/version check),
  `DEFAULT_FILE_SIGNATURE = 0x484F4942` → LE `b'BIOH'` (header file-type check), `TYPE_INT8`… `TYPE_FLOAT64` (1-10,
  the stable type-code contract with the C/Rust side), `_CODE_BY_NAME`, `_DTYPE_BY_CODE`, the pre-compiled
  little-endian `struct.Struct` singletons.
- `BinaryFormatError`; `_open_arg` — returns `(file_object, owns_it)`; the writer/reader close the file only when they
  own it (opened from a path); in compressed mode an internal `BytesIO` is always owned and closed.
- `BinaryWriter`: `__init__` (the empty-suffix guard, before the file is opened; documents the checksum and the
  compression service), `close` (the sidecar write; in compressed mode the LZ4 flush and the deferred hash update),
  `_write` (incremental SHA3-256; skipped in compressed mode), `_open_frame`, `_scalar`, `write_header`,
  `write_u8`…`write_f64`, `write_string`, `write_array`.
- `BinaryReader`: `__init__` (compressed mode decompresses the whole file into an owned `BytesIO`;
  `BinaryFormatError` on decompression failure), `_read_exact` (chunked loop handling short reads,
  `BinaryFormatError` on EOF before n bytes), `_expect_magic`, `_scalar`, `read_header`, `read_u8`…`read_f64`,
  `read_string`, `read_array`.
- Sidecar functions: `compute_sha3_256`, `write_sha3_256_sidecar` + `verify_sha3_256_sidecar` (both carrying the
  empty-suffix guard).

On-disk layout (all 4 record types, byte-level golden-pinned):

- Scalar: `[MAGIC u32][value][MAGIC u32]`
- String: `[MAGIC][length u64][UTF-8 bytes][MAGIC]` (length in bytes)
- Array: `[MAGIC][type_code u8][ndim u64][shape u64 ×ndim][raw C-contiguous LE data][MAGIC]`
- Header: `[MAGIC][signature u32][version u32][length u64][description bytes][MAGIC]`

## Verified invariants

Pinned by the binio unit suites (no DB) — no dedicated probe exists for binio; the suites are the pinning
instrument. The byte-level layout is pinned against hand-built byte goldens (a writer/reader round-trip alone
would be self-referential).

- Framing + round-trip: `ScalarRoundTripTest` (13 — all 10 scalar types at their bounds, the f32/f64 special values
  NaN/±inf, the f32 quantization), `StringTest` (5 — multibyte UTF-8, empty, byte-length-not-char-length, latin-1),
  `ArrayTest` (9 — all 10 dtypes, multidim, empty, 0-d, writable (mutable copy, not a view), non-contiguous F-order,
  big-endian input → LE dtype, unsupported-dtype-raises, unknown-type-code-raises (a crafted type_code=99 record)),
  `HeaderTest` (2), `FramingTest` (4 — MAGIC mismatch, wrong read order, truncated file, short-read stitching).
- Byte-level layout: `LayoutGoldenTest` (3 — hand-built byte goldens for the scalar, string and header frames).
- Checksums + sidecars: `Sha3_256SidecarTest` (7 — write+verify, the `sha3_256sum` format, corruption detection,
  missing sidecar raises, malformed sidecar raises, + the 2 empty-suffix guards: write raises with the content
  byte-identical, verify raises) and `AutoChecksumTest` (6 — sidecar on close, incremental digest == full re-read,
  disabled writes no sidecar, empty `checksum_suffix` raises on construction BEFORE the file is opened, the digest
  property on file objects, the digest raises when disabled).
- Compression: `Lz4CompressionTest` (6 — round-trip with path, actually compresses, the sidecar digest is over the
  COMPRESSED bytes, round-trip with file object, the empty→complete digest trajectory of the compressed mode,
  decompression failure → `BinaryFormatError`).
- Whole document: `FullDocumentTest` (header + mixed scalars + string + 2 arrays, full read-back).
- Usage: `test_usage_binio` (3 — `with` / manual open-close / LZ4 cycles, each also verifying the sidecar; the
  "living documentation" tests).

## Open issues

None.

## Conventions

- The empty-suffix guards are fail-fast: raised before any file is opened (no file created).
- The compressed-mode digest semantics: the SHA3-256 is over the COMPRESSED bytes and the hash is updated only at
  `close()` — before close, `sha3_256_hexdigest` is the empty-stream digest (pinned).
- No PERF gates: the suites run in ~0.03 s.
- `test_usage_binio.py`'s naming deviates from the house `test_<module>.py` norm (report-only).

## Integration

- The rlmwf cache system: every cache file + the model weights file is a binio stream with a `.SHA3-256` sidecar —
  `cache_manager`'s step-2 checksum is a thin wrapper over `verify_sha3_256_sidecar` and `test_lm_worker_full_chain`
  pins the sidecar verification of the saved model.
- The C/Rust interop contract: MAGIC, the type codes 1-10, and the little-endian layouts are stable — the module
  docstring documents the byte layout.
- `test_usage_binio.py` has its own mirror doc (its 3 tests are also summarized in the source doc above).
