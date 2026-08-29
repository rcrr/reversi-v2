# test_binio.md — analysis

Date: 2026-08-29. Two test files: `test_binio.py` (42 tests, 9 classes) + `test_usage_binio.py` (3 tests, 3 classes). **T4 applied (D-051): suite 45/0/0 GREEN.**

## How to run

```
$ source .venv/bin/activate
$ time PERF=0 python3 -m unittest twolm.test.test_binio twolm.test.test_usage_binio
```

## Verified facts (W1–W4)

| # | Fact | Method |
|---|---|---|
| W1 | All 45 tests pass (0 failures, 0 skipped) | `unittest twolm.test.test_binio twolm.test.test_usage_binio` |
| W2 | No PERF gate skips — the suite is fast enough without them | grep for `skipIf` / `skipUnless` / `PERF` in both files |
| W3 | All dead imports checked — no unused imports in either file | `hashlib`, `io`, `os`, `tempfile`, `unittest`, `numpy` (as `np`), `twolm.binio` all referenced |
| W4 | `shutil` imported and used in `test_usage_binio.py` (L57: `shutil.rmtree`) — not dead | grep + body scan |

## Coverage by area

### test_binio.py — 9 classes, 42 tests

#### `ScalarRoundTripTest` (10 tests)
- `test_u8`, `test_i8`, `test_u16`, `test_i16`, `test_u32`, `test_i32`, `test_u64`, `test_i64`: round-trip using `_round_trip` helper at type bounds.
- `test_f32`: round-trip of 3.5 (exactly representable) and -0.0.
- `test_f64`: round-trip of 2.718281828459045.
- **Coverage**: all 10 scalars at their extreme values. The `_round_trip` helper uses a `BytesIO` context-manager path.

**Gap**: no NaN / ±inf test for float32/float64. (These were manually verified in the module analysis V11 — they round-trip correctly.)

#### `StringTest` (4 tests)
- `test_roundtrip_ascii`: "hello world".
- `test_roundtrip_multibyte_utf8`: "città è caffè ☕ 日本語" — exercises multibyte UTF-8 where byte length > char count.
- `test_empty_string`: empty string.
- `test_byte_length_not_char_length`: writes "é" (2 bytes) then `u8(99)`, verifies the byte after "é" is still 99 — proves the length prefix counts bytes, not chars.
- **Coverage**: good. The byte-length-not-char-length test is particularly well-designed.

#### `ArrayTest` (8 tests)
- `test_all_dtypes_1d`: `np.arange(5)` round-trip for all 10 supported dtypes, using `subTest`.
- `test_multidimensional`: (2,3,4) float64.
- `test_empty_array`: `np.array([], dtype=np.int32)`.
- `test_zero_dimensional`: `np.array(42, dtype=np.int64)`.
- `test_result_is_writable`: `read_array` must return a mutable copy, not a buffer view.
- `test_non_contiguous_input`: transposed (F-contiguous) array.
- `test_unsupported_dtype_raises`: `np.array([1+2j], dtype=np.complex128)` → `BinaryFormatError`.
- `test_unknown_type_code_raises` (T4): crafts a record with type_code=99, verifies `BinaryFormatError` on the read side.
- **Coverage**: excellent — covers all dtypes, 0-d, empty, non-contiguous, writable, and both unsupported/unknown type-code error paths.

#### `HeaderTest` (2 tests)
- `test_roundtrip`: header + u32 in the same file.
- `test_wrong_signature_raises`: mismatched signature → `BinaryFormatError`.
- **Coverage**: adequate.

#### `FramingTest` (3 tests)
- `test_magic_mismatch_raises`: different MAGIC on writer vs reader.
- `test_wrong_read_order_detected`: writes a 100-byte string, reads as u64 — the string's length prefix is not the MAGIC, so framing fails.
- `test_truncated_file_raises`: drops last 2 bytes of a u64 record → `BinaryFormatError`.
- **Coverage**: good — covers the three framing failure modes.

#### `Sha3_256SidecarTest` (5 tests)
- Uses `setUp`/`tearDown` with `tempfile.mkdtemp`.
- `test_write_and_verify`: write sidecar, verify returns True.
- `test_sidecar_format_is_sha3_256sum_compatible`: format is `"<digest>  <basename>\n"`.
- `test_detects_corruption`: flips one byte → verify returns False.
- `test_missing_sidecar_raises`: `FileNotFoundError` when sidecar missing.
- `test_malformed_sidecar_raises`: sidecar with non-hex digest → `BinaryFormatError`.
- **Coverage**: good.

#### `AutoChecksumTest` (5 tests)
- Uses `setUp`/`tearDown` with `tempfile.mkdtemp`.
- `test_sidecar_written_on_close`: `BinaryWriter(path)` (default checksum=True) → sidecar exists at close, verify passes.
- `test_incremental_matches_reread`: incrementally-computed digest matches `compute_sha3_256` re-read.
- `test_disabled_writes_no_sidecar`: `checksum=False` → no sidecar.
- `test_digest_property_on_file_object`: with a `BytesIO` (file object, no path), `sha3_256_hexdigest` gives the correct digest.
- `test_digest_property_raises_when_disabled`: `checksum=False` → property raises `ValueError`.
- **Coverage**: excellent.

#### `FullDocumentTest` (1 test)
- `test_mixed_document`: header + string + i16 + u16 + f64 + float32 array + int64 multidim array → full read-back with `assertEqual` / `np.array_equal`.
- **Coverage**: good end-to-end smoke test.

#### `Lz4CompressionTest` (4 tests)
- Uses `setUp`/`tearDown` with `tempfile.mkdtemp`.
- `test_roundtrip_with_path`: write compressed with path, read compressed with path.
- `test_compression_actually_compresses`: writes a repetitive array (10,000 float64, 1% non-zero) — verifies compressed size < uncompressed.
- `test_checksum_uses_compressed_bytes`: compressed path write → verify sidecar → digest matches `compute_sha3_256` on the compressed file.
- `test_roundtrip_with_file_object`: compressed write to `BytesIO`, compressed read from `BytesIO`.
- **Coverage**: good — covers both path and file-object modes, verifies compression ratio, and checksum over compressed bytes.

### test_usage_binio.py — 3 classes, 3 tests

These are "living documentation" tests — each is a single linear write-then-read sequence with no helper methods.

#### `UsageWithContextManagerTest` (1 test)
- `test_write_and_read_back`: full cycle with `with`, all 10 scalars + 2 arrays + SHA3-256 sidecar verification.

#### `UsageManualOpenCloseTest` (1 test)
- `test_write_and_read_back`: same cycle without `with` — manual open/close with `try/finally`.

#### `UsageLz4CompressionTest` (1 test)
- `test_write_and_read_back`: compressed cycle with `with`, sidecar verification.

All three tests use `tempfile.mkdtemp` + `addCleanup(shutil.rmtree, tmpdir)` — they are self-cleaning.

## Defects (test files only)

### T4 — No test for unknown type code in `read_array` (D-051, FIXED)

`test_unknown_type_code_raises` added to `ArrayTest` — crafts a record with type_code=99,
verifies `BinaryFormatError`. Suite now 42 + 3 = 45 tests.

### Observations (test files only)

- **No PERF gates**: the suite runs in ~0.017s. Not a defect.
- **`test_usage_binio.py` naming**: follows `test_<something>_binio.py` rather than the project norm `test_binio.py` / `test_binio_stress.py`. The file is imported as `twolm.test.test_usage_binio` which works fine.
- **No NaN / ±inf float test**: these values round-trip correctly (verified manually in the module analysis V11) but are not pinned by tests.
- **`_read_exact` not directly tested for EOF**: covered indirectly via `test_truncated_file_raises` and `test_wrong_read_order_detected` (both hit EOF in `_expect_magic` → `_read_exact`).

## Completeness verdict

**The suite is well-structured and covers the critical paths**: all 10 scalars at bounds, strings with byte-length precision, arrays in all dtypes + edge shapes (0-d, empty, non-contiguous), header, framing, checksum (auto + standalone), compression (path + file-object), and full-document integration. The usage tests double as documentation.

Remaining gaps (minor, noted-only):
- NaN/±inf not tested for float types.
- `_read_exact` EOF not tested as a standalone unit.

**Verdict**: 45/0/0 GREEN. Low-risk module with good test coverage. The 4 defects (T1–T4) are all fixed (D-051); the test-file-specific gap (T4) is closed.

## Appendix: class map (2026-08-29, post T1-T4)

### test_binio.py

| Line | Class | Tests |
|---|---|---|
| 59 | `ScalarRoundTripTest` | 10 |
| 122 | `StringTest` | 4 |
| 162 | `ArrayTest` | 8 |
| 230 | `HeaderTest` | 2 |
| 253 | `FramingTest` | 3 |
| 288 | `Sha3_256SidecarTest` | 5 |
| 342 | `AutoChecksumTest` | 5 |
| 393 | `FullDocumentTest` | 1 |
| 420 | `Lz4CompressionTest` | 4 |

### test_usage_binio.py

| Line | Class | Tests |
|---|---|---|
| 65 | `UsageWithContextManagerTest` | 1 |
| 126 | `UsageManualOpenCloseTest` | 1 |
| 164 | `UsageLz4CompressionTest` | 1 |