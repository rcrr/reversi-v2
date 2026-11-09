# model_development.md — developing and tracking a model

The operational guide of the `models/` zone (the rule: R-360 in notes/rules.md). It covers the whole life of one
model: giving it an identity, writing its config, registering it, running it, and knowing where its outputs land.
The config KEY reference is not repeated here — it lives in [lm_config_guide.md](lm_config_guide.md).

## The layout

```
models/lm/ec20/0000/lm_ec20_0000.json   <- the tracked config (one folder per model)
models/lm/ec20/index.md                 <- the registry of the ec20 level
build/lm/ec20/0000/                     <- the run's outputs (gitignored, 1:1 mirror)
```

- `lm` is the model family (the logistic model); a new family gets a sibling folder (`models/resnet/...`).
- `ec20` is the empty-count level: `ec<empty_count>` (`ec00`, `ec16`, `ec20`, ...).
- `0000` is the model ID: 4 digits, sequential within its level folder, **never reused** (a retired model keeps
  its number forever).
- The config file is named `<family>_<ec-level>_<ID>.json` — the identity travels with the file name.
- Every config's `base_dir` is RELATIVE (`./build/lm/ec20/0000`): it resolves from the current directory, so the
  pipeline is **always launched from the workspace root** and no absolute path ever lands in a tracked file.

## Creating a new model

Worked for the next free model of the ec20 level (suppose `0003`):

1. **Take the next ID** — the highest NNNN in `models/lm/ec20/` plus one (`0000` if the folder is empty).
2. **Create both trees** (the config side and the output mirror):

   ```bash
   mkdir -p models/lm/ec20/0003 build/lm/ec20/0003
   ```

   The `base_dir` gate requires the directory to exist, be a directory, and be writable — the `mkdir -p` is not
   optional.

3. **Write the config** at `models/lm/ec20/0003/lm_ec20_0003.json` from the template below. The schema-required
   `name` and `description` are the model's identity and the only place they live — the registry never duplicates
   them.
4. **Register it** — add the row to `models/lm/ec20/index.md` (the format is defined in the index preamble):

   ```
   | 0003 | [lm_ec20_0003.json](0003/lm_ec20_0003.json) |
   ```

5. **Commit** — the config and the index row go in the same commit (the registry and the tree stay in lockstep).

## The config template

The smallest valid shape (the 10 required keys — see the guide's Minimal example for the key-by-key reference):

```json5
/*
 * lm_ec20_0003.json
 *
 * This file is part of the reversi program
 * http://github.com/rcrr/reversi-v2
 *
 * Author Roberto Corradini mailto:rob_corradini@yahoo.it
 * Copyright 2026 Roberto Corradini. All rights reserved.
 *
 * License
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 3, or (at your option) any
 * later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA
 * or visit the site <http://www.gnu.org/licenses/>.
 */
{
    "name": "lm_ec20_0003 — <one-line model identity>",
    "empty_count": 20,
    "description": "<what this model is: the feature set and the hypothesis it tests>",
    "base_dir": "./build/lm/ec20/0003",
    "output": "lm_ec20_0003.dat",
    "regab_data_set": {
        "regab_db_connection": { "dbname": "regab", "user": "regab", "host": "localhost" },
        "bid": [8],
        "status": ["CMS", "CMR"]
    },
    "validation_data_set": {
        "bid": [8],
        "status": ["CMS", "CMR"]
    },
    "feature_set": {
        "intercept": true,
        "pattern_set": {
            "name": "<the pattern set name>",
            "patterns": [ { "name": "EDGE", "mask": "00000000000000FF" } ]
        }
    },
    "stat_model": {},
    "optimization": { "checkpoint_file": "checkpoint_optimize.dat" }
}
```

The GPL header is part of the file (R-595 — the pre-commit gate checks it on every staged `.json`). `empty_count`
must agree with the level folder (`ec20` ↔ `20`).

## Running the model

From the **workspace root** (the relative `base_dir` resolves from here):

```bash
.venv/bin/python -m reversi.lm.logistic_model models/lm/ec20/0003/lm_ec20_0003.json
```

Every output of the run lands under `build/lm/ec20/0003/` (the `base_dir`): the saved model weights
(`output`), the run log, the plots, the reports, the per-level cache files. Nothing leaves that folder unless a
config field is set to an absolute path (the documented escape hatch of the config guide).

## The registry (index.md)

Each ec-level folder carries its `index.md`: a rigid 2-column table — the ID and a relative markdown link straight
into the config — under a preamble that defines the format. Add one row per model, in ID order; never renumber,
never delete a row (a retired model is annotated in its config's `description`, its row stays).

## Where things live

| Fact | Home |
|---|---|
| The zone rule (layout, naming, numbering, relative `base_dir`) | R-360 in notes/rules.md |
| The config keys, the defaults, the cross-field rules | [lm_config_guide.md](lm_config_guide.md) |
| What a level does with your config | the mirror docs (docs/src/reversi/lm/...) |
| A model's name / description | its config file (the schema-required fields) |

`build/` is gitignored but **not disposable** (R-600): the model outputs are data, and nothing is deleted from
there without an explicit request.
