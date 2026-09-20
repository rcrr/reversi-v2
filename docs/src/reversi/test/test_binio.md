# reversi/test/test_binio.py
The binio unit suite — 9 classes / 45 tests, no DB (the ~0.02 s infrastructure suite). Includes
`test_unknown_type_code_raises` and the 3 empty-sidecar-suffix guard tests — the 48 total counting the usage module.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `ScalarRoundTripTest` | 10 | all 10 scalar types at their bounds, the `_round_trip` BytesIO helper |
| `StringTest` | 4 | ASCII, multibyte UTF-8 ("città è caffè ☕ 日本語"), empty string, byte-length-not-char-length ("é" = 2 bytes — the u8(99) after it still reads) |
| `ArrayTest` | 8 | all 10 dtypes 1-d (subTest), (2,3,4) float64, empty, 0-d, result-is-writable (mutable copy, not a view), non-contiguous F-order, unsupported-dtype-raises (complex128 → `BinaryFormatError`), unknown-type-code-raises (a crafted type_code=99 record) |
| `HeaderTest` | 2 | round-trip, wrong-signature-raises |
| `FramingTest` | 3 | MAGIC mismatch, wrong read order (a string read as u64 — the length prefix is not a MAGIC), truncated file (last 2 bytes dropped) |
| `Sha3_256SidecarTest` | 7 | write+verify, the `sha3_256sum` format (`"<digest>  <basename>\n"`), corruption detection (one flipped byte), missing-sidecar-raises (`FileNotFoundError`), malformed-sidecar-raises (non-hex → `BinaryFormatError`), write empty-suffix-raises + content byte-identical, verify empty-suffix-raises |
| `AutoChecksumTest` | 6 | sidecar-on-close, incremental digest == `compute_sha3_256` re-read, `checksum=False` writes nothing, empty `checksum_suffix` raises in `__init__` BEFORE the file is opened, the digest property on file objects, the digest raises when disabled |
| `FullDocumentTest` | 1 | header + mixed scalars + string + 2 arrays, full read-back |
| `Lz4CompressionTest` | 4 | round-trip with path, actually compresses (a repetitive 10k-float64 array), the checksum over the compressed bytes, round-trip with file object |

## Goldens pinned

- No float goldens (the suite is structural): the pins are the byte-level layouts (MAGIC/SIGNATURE framing, the u64
  length prefix, the type codes), the exact exception types (`BinaryFormatError` / `ValueError` / `FileNotFoundError`),
  and the `sha3_256sum` sidecar format.
- `test_usage_binio.py` (3 "living documentation" tests — `with` / manual open-close / LZ4 cycles, each also verifying
  the sidecar; `tempfile.mkdtemp` + `addCleanup(shutil.rmtree)`): its own mirror doc exists (test_usage_binio.md);
  report-only).

## Conventions

- No PERF gates (~0.02 s), no DB gate (pure I/O).
- The guard tests are fail-fast: the constructor test asserts no file is created before the raise.
- Known gaps (noted-only): no NaN/±inf float test (verified manually at analysis); `_read_exact` EOF not directly
  unit-tested (indirectly via `FramingTest`).

## Integration

- Module under test: `binio.md` — the on-disk foundation of the rlmwf cache system.
- The guard tests are the pin of the 3 sidecar entry points' `ValueError` behaviour — the same behaviour
  `test_lm_worker_full_chain` relies on (sidecar verification of the saved model).
