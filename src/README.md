# Source layout — `src/symposium/`

The installable package behind the `symposium` console script. The entry point is
`symposium.cli:main` (`pyproject.toml` `[project.scripts]`); `python -m symposium`
uses `symposium/__main__.py`, which calls the same `main`. `symposium/__init__.py`
re-exports `APIClient`, `Config`, `ScheduleExporter` and `__version__`.

## Modules

| Module | Responsibility | Guide |
| --- | --- | --- |
| `cli/` | Argument parser and command handlers: `cli/analyze.py`, `cli/generate.py`, `cli/visualize.py`, `cli/edition.py`, `cli/organize.py`. `cli/__init__.py` builds the tree and dispatches. | [cli/README.md](symposium/cli/README.md) |
| `core/` | Shared infrastructure: `core/config.py`, `core/api.py`, `core/data_loader.py`, `core/edition.py`, `core/participant_schema.py`, `core/logging_utils.py`. | [core/README.md](symposium/core/README.md) |
| `analysis/` | Presenter and participant analysis (`analysis/presenters.py`, `analysis/participants.py`). | [analysis/README.md](symposium/analysis/README.md) |
| `generation/` | Research profiles and catechism-based project proposals (`generation/profiles.py`, `generation/projects.py`). | [generation/README.md](symposium/generation/README.md) |
| `visualization/` | Embedding, network, distribution and PCA plots (`visualization/embeddings.py`, `visualization/networks.py`, `visualization/distributions.py`, `visualization/pca_analysis.py`). | [visualization/README.md](symposium/visualization/README.md) |
| `io/` | Report readers and writers (`io/readers.py`, `io/writers.py`). | [io/README.md](symposium/io/README.md) |
| `calendar/` | `ScheduleExporter` for ICS, JSON and CSV schedules (`calendar/exporter.py`). | [calendar/README.md](symposium/calendar/README.md) |
| `organizing/` | Private intake and consent projection, approved-public staging, book artifacts, catalog/discovery and the static site. | [organizing/AGENTS.md](symposium/organizing/AGENTS.md) and [organizing workflow](../docs/organizing_publication.md) |

## How the pieces fit

`cli/` is the front door. The handlers in `cli/analyze.py`, `cli/generate.py` and
`cli/visualize.py` call into `analysis/`, `generation/` and `visualization/`, which
read and write through `io/`. `core/` supplies the shared configuration, provider
client, data loader, edition paths and logging. `calendar/` is standalone.
`organizing/` is a separate operator pipeline: it turns private, authorized inputs
into the approved public tree and public site and does not run the paid-provider
analysis modules.

## Where to read next

- [Documentation index](../docs/README.md) for operator and developer guides.
- [Repository contributor map](../AGENTS.md) for layout, conventions and boundaries.
- [Test guide](../tests/README.md) for the suite layout and commands.
- [Data guide](../data/README.md) for the data tree and public/private boundary.
- [Package metadata](../pyproject.toml) for scripts, dependencies and the 80% coverage gate.
