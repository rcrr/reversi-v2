# reversi/test/test_usage_binio.py
Linear, copy-pasteable USAGE examples for the binio public API —
the tests double as documentation (D-051): 3 classes / 3 tests, no
DB, no gate, no artifacts.
> State: D-051 · 874e5c6 · 2026-08-29 · suite 3/0/0 (3 classes /
  3 tests, no DB)

## Coverage

| class | tests | what it pins |
|---|---|---|
| `UsageWithContextManagerTest` | 1 | the full write → read cycle with `with BinaryWriter` (the automatic SHA3-256 sidecar on close): header (description + version), a multi-byte UTF-8 string on purpose ("città è caffè ☕"), every scalar type (u8/i8/u16/i16/u32/i32/u64/i64/f32/f64), two arrays; `verify_sha3_256_sidecar` on the closed file; everything read back in the same order with exact equality |
| `UsageManualOpenCloseTest` | 1 | the same cycle WITHOUT `with` (manual open/close, try/finally) — for program structures where the writer/reader must live across several functions; `writer.close()` writes the sidecar from the in-memory digest |
| `UsageLz4CompressionTest` | 1 | the same cycle with `compressed=True` (LZ4 whole-file compression): the API is identical, the sidecar verifies the compressed file on disk |

## Goldens pinned

- Round-trip identity: every value read back equals the written
  value — the 11 scalars, the UTF-8 string, the two arrays
  (`np.array_equal`). No float tolerance: the binary format
  round-trips bit-exact.
- The sidecar: after close — both the context-manager path (the
  automatic checksum) and the manual-close path —
  `verify_sha3_256_sidecar(path)` is True.
- The example payloads (the description/version strings, −12345,
  "lz4 payload") are documentation values, not goldens.

## Conventions

- Each test is a single straight sequence with no helper methods
  (the module docstring: "copy-pasteable usage examples") — a
  complete write → verify → read cycle in one `def`.
- The working dir is `tempfile.mkdtemp(prefix="binio_usage_")` +
  `addCleanup(shutil.rmtree, ...)`: self-contained, nothing touches
  the workspace (this suite intentionally does NOT use the D-085
  TemporaryDirectory / CUSTOM_TMP_BASE idiom — usage examples stay
  standalone).
- Run from the workspace root: `time PERF=0 python3 -m unittest
  reversi.test.test_usage_binio` (the header -1- block); no PERF
  gate — the suite is a few seconds.

## Integration

- Independent of the pipeline and the DB: pure verification of the
  binio public API (the D-051 port of the original binio
  module; the lz4 dependency, D-051).
- Sibling suite: test_binio.py (the full binio test — 45 tests at
  the D-051 close); this file is the usage / documentation layer
  on top of it.
