# GNN conformance

The canonical pin is [`.github/gnn-pin.json`](gnn-pin.json), schema
`gnn-importer-pin/v1`:

| Field | Value |
| --- | --- |
| `repository` | `ActiveInferenceInstitute/Generalized_Notation_Notation` |
| `revision` | `8f293d9ba810e6eda5c09842d9c7ed9ffa5f92c1` |
| `tag` | `v5.0.3` |
| `recorded` | `2026-11-12` |

The pin file is the sole executable source of that revision: the job reads it and
does not restate it, so a bump is one edit. The table above copies the values for
readers only.

## Job

| | |
| --- | --- |
| Workflow | [`.github/workflows/ci.yml`](workflows/ci.yml) |
| Job key | `gnn-conformance` |
| Display name | `gnn conformance (pinned)` |
| Command | `./gate.sh gnn` |

The arm creates an isolated environment (`.gate/gnn`), installs `defusedxml`,
`psutil` and `pyyaml`, then installs the pinned package with `--no-deps` from
`git+https://github.com/<repository>.git@<revision>`. It needs no project
dependency environment, and it is not part of the test matrix.

## What it parses

[`scripts/gnn_conformance.py`](../scripts/gnn_conformance.py) validates the pin
(`schema`, `repository`, `revision`, `tag` present and the schema exact), requires the
installed `gnn.__version__` to equal `tag` without its `v`, then:

- **Repository sketches.** Every `*.gnn.md` in the tree must parse with
  `gnn.parsers.basic.parse_gnn_formal` with no `parse_errors`, pass
  `validate_gnn_syntax` (called with `is_content=True`), and be accepted by
  `gnn.type_checker.GNNTypeChecker`. `validate_gnn_files` returns `True` when every file
  validates, `2` when files are invalid or none were found, and `False` on a hard
  failure; the gate requires exactly `True` and reports any other value.
- **No sketches.** It fetches
  `https://raw.githubusercontent.com/<repository>/<revision>/input/gnn_files/basics/static_perception.md`
  and applies the same parse, syntax and type checks to that exemplar.

The run prints one JSON line: `gnn-version`, `pin-revision`, `models`, `source`
(`repository` or `pinned-exemplar`) and `result`. `result` depends on the source:
`repository-content-passed` when repository sketches were checked, and
`pinned-exemplar-baseline-passed` when only the pinned upstream exemplar was.

This repository currently has no `*.gnn.md` sketch, so the job checks the pinned
exemplar. That is a pipeline and pin conformance baseline, not a claim that the
repository already contains a model.
