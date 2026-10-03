# test/reversi/tools/test_binio.py
The binio unit suite — 10 classes, no DB (the ~0.03 s infrastructure suite). Carries the hand-built byte goldens
(the `LayoutGoldenTest`), the 3 empty-sidecar-suffix guard tests, and the LZ4 compression pins (including the
decompression-failure and the compressed-digest trajectory).

## Coverage

| class | tests | what it pins |
|---|---|---|
| `ScalarRoundTripTest` | 13 | all 10 scalar types at their bounds, the f32/f64 special values (NaN/±inf), the f32 quantization (0.1 → the bit-exact float32), the `_round_trip` BytesIO helper |
| `StringTest` | 5 | ASCII, multibyte UTF-8 ("città è caffè ☕ 日本語"), empty string, byte-length-not-char-length ("é" = 2 bytes — the u8(99) after it still reads), the latin-1 round-trip |
| `ArrayTest` | 9 | all 10 dtypes 1-d (subTest), (2,3,4) float64, empty, 0-d, result-is-writable (mutable copy, not a view), non-contiguous F-order, big-endian input → LE dtype, unsupported-dtype-raises (complex128 → `BinaryFormatError`), unknown-type-code-raises (a crafted type_code=99 record) |
| `HeaderTest` | 2 | round-trip, wrong-signature-raises |
| `FramingTest` | 4 | MAGIC mismatch, wrong read order (a string read as u64 — the post-value MAGIC lands on the payload), truncated file (last 2 bytes dropped), short-read stitching (a one-byte-at-a-time stream) |
| `LayoutGoldenTest` | 3 | the on-disk byte layout against hand-built bytes: the scalar, string and header frames (the MAGIC + the field order) |
| `Sha3_256SidecarTest` | 7 | write+verify, the `sha3_256sum` format (`"<digest>  <basename>\n"`), corruption detection (one flipped byte), missing-sidecar-raises (`FileNotFoundError`), malformed-sidecar-raises (non-hex → `BinaryFormatError`), write empty-suffix-raises + content byte-identical, verify empty-suffix-raises |
| `AutoChecksumTest` | 6 | sidecar-on-close, incremental digest == `compute_sha3_256` re-read, `checksum=False` writes nothing, empty `checksum_suffix` raises in `__init__` BEFORE the file is opened, the digest property on file objects, the digest raises when disabled |
| `FullDocumentTest` | 1 | header + mixed scalars + string + 2 arrays, full read-back |
| `Lz4CompressionTest` | 6 | round-trip with path, actually compresses (a repetitive 10k-float64 array), the checksum over the compressed bytes, round-trip with file object, the empty→complete digest trajectory of the compressed mode, decompression failure → `BinaryFormatError` |

## Goldens pinned

- The on-disk byte layout: `LayoutGoldenTest` hand-builds the scalar / string / header frames from
  `binio.DEFAULT_MAGIC` + `struct.pack` (the frame order is pinned independently of the writer); the array framing
  is pinned by the crafted type_code=99 record.
- The exception types (`BinaryFormatError` / `ValueError` / `FileNotFoundError`), the `sha3_256sum` sidecar format,
  the f32 quantization (bit-exact `np.float32(0.1)`), the compressed-mode digest trajectory (the empty-stream
  digest before close, the compressed-bytes digest after).
- `test_usage_binio.py` (3 "living documentation" tests — `with` / manual open-close / LZ4 cycles, each also
  verifying the sidecar; `tempfile.mkdtemp` + `addCleanup(shutil.rmtree)`): its own mirror doc exists
  (test_usage_binio.md); report-only.

## Conventions

- No PERF gates (~0.03 s), no DB gate (pure I/O).
- The file-based tests use the house idiom: `TemporaryDirectory` under `CUSTOM_TMP_BASE` (test/reversi/paths.py),
  the `setUpClass` mkdir, the defensive `tearDown`.
- The guard tests are fail-fast: the constructor test asserts no file is created before the raise.

## Integration

- Module under test: `binio.md` — the on-disk foundation of the rlmwf cache system.
- The guard tests are the pin of the 3 sidecar entry points' `ValueError` behaviour — the same behaviour
  `test_lm_worker_full_chain` relies on (sidecar verification of the saved model).
