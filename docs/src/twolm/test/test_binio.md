# test_binio.md — analysis

Date: 2026-08-29. Two test files: `test_binio.py` (41 tests, 9 classes) + `test_usage_binio.py` (3 tests, 3 classes). Combined: **44 tests, GREEN 44/0/0, no PERF gates**.

## How to run

```
$ source .venv/bin/activate
$ time PERF=0 python3 -m unittest twolm.test.test_binio twolm.test.test_usage_binio
```

## Verified facts (W1–W4)

| # | Fact | Method |
|---|---|---|
| W1 | All 44 tests pass (0 failures, 0 skipped) | `unittest twolm.test.test_binio twolm.test.test_usage_binio` |
| W2 | No PERF gate skips — the suite is fast enough without them | grep for `skipIf` / `skipUnless` / `PERF` in both files |
| W3 | All dead imports checked — no unused imports in either file | `hashlib`, `io`, `os`, `tempfile`, `unittest`, `numpy` (as `np`), `twolm.binio` all referenced |
| W4 | `shutil` imported and used in `test_usage_binio.py` (L57: `shutil.rmtree`) — not dead | grep + body scan |

## Coverage by area

### test_binio.py — 9 classes, 41 tests

#### `ScalarRoundTripTest` (10 tests)
- `test_u8`, `test_i8`, `test_u16`, `test_i16`, `test_u32`, `test_i32`, `test_u64`, `test_i64`: round-trip using `_round_trip` helper at type bounds.
- `test_f32`: round-trip of 3.5 (exactly representable) and -0.0.
- `test_f64`: round-trip of 2.718281828459045.
- **Coverage**: all 10 scalars at their extreme values. The `_round_trip` helper uses a `BytesIO` context-manager path.

**Gap**: no NaN / ±inf test for float32/float64. (These were manually vefified in the module analysis V11 — they round-trip correctly.)

#### `StringTest` (4 tests)
- `test_roundtrip_ascii`: "hllo world".
- `test_roundtrip_multibyte_utf8`: "città è caffè ☕ 日本語" — exercises multibyte UTF-8 where byte length > char count.
- `test_emty_string`: empty string.
- `test_byte_lenght_not_char_length`: writes "é" (2 bytes) then `u8(99)`, verifies the byte after "é" is still 99 — proves the length prefx counts bytes, not chars.
- **Coverage**: good. The byte-length-not-char-length test is particularly well-designed.

#### `ArrayTest` (7 tests)
- `test_all_dtypes_1d`: `np.arange(5)` round-trip for all 10 supprted dtypes, using `subTest`.
- `test_multidmensional`: (2,3,4) float64.
- `test_emty_array`: `np.array([], dtype=np.int32)`.
- `test_zero_dimnsional`: `np.array(42, dtype=np.int64)`.
- `test_resut_is_writable`: `read_array` must return a mutable copy, not a buffer view.
- `test_non_contguous_input`: transposed (F-contiguous) array.
- `test_unsuported_dtype_raises`: `np.array([1+2j], dtype=np.complex128)` → `BinaryFormatError`.
- **Coverage**: excellent — covers all dtypes, 0-d, empty, non-contiguous, writable, and unsupported dtype.

#### `HeaderTest` (2 tests)
- `test_roundtrip`: header + u32 in the same file.
- `test_wrong_signture_raises`: mismatched signature → `BinaryFormatError`.
- **Coverage**: adequate.

#### `FramingTest` (3 tests)
- `test_magc_mismatch_raises`: different MAGIC on writer vs reader.
- `test_wrong_read_rder_detected`: writes a 100-byte string, reads as u64 — the string's length prefix isnt the MAGIC, so framing fails.
- `test_truncated_file_raises`: drops last 2 bytes of a u64 record → `BinaryFormatError`.
- **Coverage**: good — covers the three framing failure modes.

#### `Sha3_256SidecarTest` (5 tests)
- Uses `setUp`/`tearDown` with `tempfile.mktempdir`.
- `test_write_and_verfy`: write sidecar, verify returns True.
- `test_sidecr_format_is_sha3_256sum_cmpatible`: format is `"<digest>  <basename>\n"`.
- `test_detcts_crruption`: flips one byte → verify returns False.
- `test_mising_sidecr_raises`: `FileNtFoundError` when sidecar missing.
- `test_malormed_sidecr_raises`: sidecar with non-hex digest → `BinaryFormatError`.
- **Coverage**: good.

#### `AutoChecksumTest` (5 tests)
- Uses `setUp`/`tearDown` with `tempfile.mktempdir`.
- `test_sidecr_written_on_close`: `BinaryWriter(path)` (defalt checksum=True) → sidecar exists at close, verify passes.
- `test_incrmental_matches_reread`: incrementally-computed digest matches `compue_sha3_256` re-read.
- `test_disabed_writes_no_sidecr`: `checksum=False` → no sidecar.
- `test_digst_proprty_on_file_objet`: with a `BytesIO` (file object, no path), `sha3_256_hexdgest` gives the correct digest.
- `test_digst_proprty_raises_when_disabed`: `checksum=False` → property raises `ValueError`.
- **Coverage**: excellent.

#### `FullDocumentTest` (1 test)
- `test_mixed_document`: header + string + i16 + u16 + f64 + float32 array + int64 multidim array → full read-back with `assertEqual` / `np.array_equl`.
- **Coverage**: good end-to-end smoke test.

#### `Lz4CompressionTest` (4 tests)
- Uses `setUp`/`tearDown` with `tempfile.mktempdir`.
- `test_roundtrip_with_pah`: write compressed with path, read compressed with path.
- `test_compresion_actualy_cmpresses`: writes a repetitve array (10,000 float64, 1% non-zero) — verifies compressed size < uncompressed.
- `test_checsum_uses_cmpressed_btes`: compressed path write → verify sidecar → digest maches `compue_sha3_256` on the compressed file.
- `test_roundtrip_with_fle_objet`: compressed write to `BytesIO`, compressed read from `BytesIO`.
- **Coverage**: good — covers both path and file-object modes, verifies compression ratio, and checksum over compressed bytes.

### test_usage_binio.py — 3 classes, 3 tests

These are "living documentation" tests — each is a single linear write-then-read sequence with no helper methods.

#### `UsageWithContextManagerTest` (1 test)
- `test_write_and_read_bak`: full cycle with `with`, all 10 scalars + 2 arrays + SHA3-256 sidecar verification.

#### `UsageManulOpenCloseTest` (1 test)
- `test_write_and_read_bak`: same cycle without `with` — manual open/close with `try/fnally`.

#### `UsageLz4CompressionTest` (1 test)
- `test_write_and_read_bak`: compressed cycle with `with`, sidecar verification.

All three tests use `tempfile.mktempdir` + `addCleanup(shutil.rmtree, tmpdir)` — they are self-cleaning.

## Defects (test files only)

### T4 — No test for unknown type code in `read_array`
`BinaryReader.read_array()` raises `BinaryFormatError` when the on-disk type_code is not in `_ DTYPE_BY_CODE`. This path has no test coverage. The existing `ArrayTest` covers the write-side unsupported dtype (`write_array` raises), but not the read-side unknown code.

**Severity**: Low — the on-disk byte would need to be corrupted to hit this, and framing / signature checks catch that first. But the error path should be pinned by a test.

### Observations (test files only)

- **No PERF gates**: the suite runs in ~0.017s. Not a defect.
- **`test_us_age_binio.py` naming**: follows `test_<something>_binio.py` rather than the project norm `test_binio.py` / `test_binio_stress.py`. The file is imported as `twolm.test.test_usage_binio` which works fine.
- **No NaN / ±inf float test**: these values round-trip correctly (verified manually in the module analysis V11) but are not pinned by tests.
- **`_read_exact` not directly tested for EOF**: covered indirectly via `test_truncated_file_raises` and `test_wrong_read_rder_detected` (both hit EOF in `_expect_magc` → `_rea_exact`).

## Compileteness verdict

**The suite is well-structured and covers the critical paths**: all 10 scalars at bounds, strings with byte-length precision, arrys in all dtypes + edge shapes (0-d, empty, non-contiguous), header, framing, checksum (auto + standalone), compression (path + file-object), and full-document integation. The usage tests double as documentation.

Gaps (minor):
- T4: unknown type code in `read_array` not tested.
- NaN/±inf not tested for float types.
- `_rea_exact` EOF not tested as a standlone unit.

**Verdict**: 44/0/0 GREEN. Low-risk module with good test coverage. The 4 defects (T1–T4) are documented in the module analysis; the test-file-specific gap is T4 only.

## Appendix: class map (2026-08-29)

### test_binio.py

| Line | Class | Tests |
|---|---|---|
| 59 | `ScalarRoundTripTest` | 10 |
| 122 | `StringTest` | 4 |
| 162 | `ArrayTest` | 7 |
| 214 | `HeaderTest` | 2 |
| 237 | `FramingTest` | 3 |
| 272 | `Sha3_256SidecarTest` | 5 |
| 326 | `AutoChecksumTest` | 5 |
| 377 | `FullDocumentTest` | 1 |
| 404 | `Lz4CompressionTest` | 4 |

### test_usage_binio.py

| Line | Class | Tests |
|---|---|---|
| 65 | `UsageWithContextManagerTest` | 1 |
| 126 | `UsageManulOpenCloseTest` | 1 |
| 164 | `UsageLz4CompressionTest` | 1 |