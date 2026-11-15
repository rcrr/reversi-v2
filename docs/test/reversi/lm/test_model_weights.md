# test/reversi/lm/test_model_weights.py

The `model_weights` unit suite — 2 classes / 5 tests, no DB, < 0.3 s. The v2 self-describing weights file:
the write-then-read round trip (compressed and uncompressed, every section back) and the reader's three
guards (the header description, the version, the configuration checksum).

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestRoundTrip` | 2 | the full v2 round trip: the header (version 2), the metadata (name / ec / logit_clipping), the three sections (training population stats, optimization info, validation metrics), the FeatureSet structure (the intercept, the mobility name / side, the pattern name), the core arrays (`iwmap_feature_offset` / `w_dense`), and the embedded configuration provenance (dump + sha3_256 checksum) — once compressed (lz4) and once uncompressed |
| `TestReadRejections` | 3 | the reader guards: the wrong description (`File header mismatch`), the out-of-contract version (3), and the config checksum mismatch (the sentinel never matches the v2 dump) |

## Goldens pinned

The round trip is value-exact on the integer fields and `places=6` on the f32 floats; the checksum pin is the
sha3_256 of the exact dump string. (No external hash goldens.)

## Conventions

- the NO-DB mock-ctx idiom: a `SimpleNamespace` ctx with a `model_dump_json` lambda (a fixed dump string) and a
  `config_checksum` computed as its sha3_256 — the writer reads exactly these fields.
- the scratch dir is anchored to the shared `CUSTOM_TMP_BASE` (the R-750 idiom); the tiny model is a 2-feature
  set with 3 weights, so every section is exercised at microsecond cost.

## Integration

Mirrors `src/reversi/lm/model_weights.py` (the `ModelWeights` carrier, the writer, the reader). The SAVE level
that drives the writer in the pipeline is pinned by `test_wrk_save` (this campaign) and the end-to-end chain;
this module pins the file format itself — the artifact contract CLIENT_CHECK and the reload path rely on.
