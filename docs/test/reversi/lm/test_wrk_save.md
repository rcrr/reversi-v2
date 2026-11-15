# test/reversi/lm/test_wrk_save.py

The `wrk_save` unit suite — 3 classes / 4 tests, no DB, < 0.3 s. The SAVE level: the worker factory, the up
step (the compressed v2 artifact lands at `base_dir / output` and is readable back, the bounded 3-event echo),
and the down no-op.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestFactory` | 1 | `wrk_save()` returns a `Worker` named `SAVE` |
| `TestSaveUp` | 2 | the up step on a mock ctx: the artifact exists at the configured path and `model_weights_read_file` reads it back (name + version 2); the bounded echo — exactly 3 events, the INFO save banner first, the INFO saved-to line, the DEBUG checksum line |
| `TestSaveDown` | 1 | the down step logs the single clearing no-op line and nothing else |

## Goldens pinned

None. (The pins are the artifact readability, the event count / content, and the factory contract; the file
format's own pins live in `test_model_weights`.)

## Conventions

- the NO-DB mock-ctx idiom: a `SimpleNamespace` ctx with the `cfg` (base_dir + output + the metadata fields),
  the config provenance, the three sections, the tiny 2-feature set, and a COLLECTING `log_event` — the
  worker reads exactly these.
- the scratch dir is anchored to the shared `CUSTOM_TMP_BASE` (the R-750 idiom).

## Integration

Mirrors `src/reversi/lm/wrk_save.py` (the `wrk_save` factory, the `_up` / `_down` steps). The SAVE level inside
the full 17-level pipeline (its position after ANALYTICS, before CLIENT_CHECK) stays covered by
`test_lm_worker_full_chain`; this module pins the worker in isolation at < 0.3 s cost.
