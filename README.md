# Symposium: Active Inference Symposium Research Tools

[![Tests](https://github.com/ActiveInferenceInstitute/Symposium/actions/workflows/ci.yml/badge.svg)](https://github.com/ActiveInferenceInstitute/Symposium/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Python tools for presenter research profiles, participant learning plans, project
proposals, text visualizations, and calendar exports for the Active Inference Symposium.

**Version 2.2.1 prepares the 2026 edition.** The repository includes an empty 2026
registration template and presenter workspace based on the previous edition's
schema. Confirmed 2026 presenters, participants, and dates must be supplied by the
organizers. Historical 2024 and 2025 inputs remain in their original directories.

## Quick start for 2026

Requires Python 3.10 or newer and [uv](https://docs.astral.sh/uv/). The development
runtime is pinned to Python 3.12; installations use the committed dependency lock.

```bash
git clone https://github.com/ActiveInferenceInstitute/Symposium.git
cd Symposium
uv sync --locked --extra dev
uv run symposium --version

# The supplied 2026 scaffold is safe to initialize again.
uv run symposium edition init --year 2026
uv run symposium edition validate --year 2026
```

Initialization and validation run offline without API credentials. Edition initialization
currently supports macOS and Linux. Default validation
checks structure and reports empty inputs as warnings. Before processing real data:

```bash
uv run symposium edition validate --year 2026 --require-data
```

The last command deliberately exits nonzero until both eligible participants and
valid presenter exports are present. Follow the [2026 organizer guide](docs/2026_setup.md)
to populate the workspace, validate it, and run analysis.

```text
data/inputs/aif_2026/
├── Public_Participant_Information.csv  # Header only until organizers add data
├── presenters/                       # One folder per new presenter
└── ...                               # Onboarding instructions and templates

outputs/2026_symposium/               # Generated locally when processing runs
├── people/
├── presenters/
├── proposals/
└── visualizations/
```

## Interactive interface

```bash
uv run python run.py                   # Default: 2026
uv run python run.py --year 2025        # Explicit historical edition
uv run python launch.py --year 2026
./symposium.sh --year 2026
```

The menu offers data inspection, participant analysis, column summaries and word
clouds, single-person background research and curricula, visualizations, and
configuration checks. All edition-specific inputs and reports use the selected
year. Importing the runner does not change the working directory or create files.

## Configure paid analysis

Copy `.env.example` to `.env` and set the credentials needed for your chosen workflow.
Copy `config.example.json` to the ignored `config.json` to customize models and paths.

```bash
cp .env.example .env
cp config.example.json config.json
```

Configuration precedence is defaults → explicitly loaded JSON → environment.
The runner loads project-local `config.json`; the CLI accepts `--config config.json`
before the command. Explicit CLI paths select the input and output for that command.
`SYMPOSIUM_YEAR` selects the runner edition; its `--year` option overrides that value.
`SYMPOSIUM_DATA_DIR` and `SYMPOSIUM_OUTPUTS_DIR` change the base storage paths.

Perplexity is used for web-assisted background research; OpenRouter supports
profile analysis and curricula. Existing model defaults remain configurable; verify
provider availability before a paid run. Setup and tests make no paid API calls.
AI-generated research profiles and proposals require organizer review before sharing.

## Command-line workflows

All existing explicit-path commands remain available. These examples process the
new edition once authorized data has been added:

```bash
# Profile analysis (choose the provider explicitly).
uv run symposium --config config.json analyze participants \
  --csv-file data/inputs/aif_2026/Public_Participant_Information.csv \
  --output-dir outputs/2026_symposium/people --api-provider openrouter

# Background-only research and curriculum-only generation.
uv run symposium analyze backgrounds \
  --csv-file data/inputs/aif_2026/Public_Participant_Information.csv \
  --output-dir outputs/2026_symposium/people
uv run symposium analyze curricula \
  --csv-file data/inputs/aif_2026/Public_Participant_Information.csv \
  --output-dir outputs/2026_symposium/people --api-provider openrouter

# Presenter publications: OpenAlex topic and works CSVs, one folder per person.
uv run symposium analyze presenters \
  --data-dir data/inputs/aif_2026/presenters \
  --output-dir outputs/2026_symposium/presenters
uv run symposium generate profiles \
  --data-dir data/inputs/aif_2026/presenters \
  --output-dir outputs/2026_symposium/presenters --include-methods

# Visualizations read Markdown reports, rather than registration CSVs.
uv run symposium visualize all \
  --input-dir outputs/2026_symposium/people \
  --output-dir outputs/2026_symposium/visualizations --method pca --layout spring
```

`generate projects` accepts `--profiles-dir`, `--output-dir`, a user-supplied
`--domain-file`, and a catechism such as `KarmaGAP`, `EUGrants`, or `Synthetic`.
See `uv run symposium generate projects --help` for options.

Participant imports accept the 2025 survey questions, corresponding short labels,
and canonical field names. The future-impact question supports subsequent years.
Optional survey null markers are normalized to empty strings. Missing name/consent
headers, duplicate fields, malformed CSV rows, duplicate eligible
names, and colliding report filenames are rejected. Only explicit affirmative public
sharing consent (`yes`, `y`, `true`, `1`, ignoring case) permits inclusion.

## Features and package API

- Presenter analysis from OpenAlex topic and publication exports.
- Participant profiles, background research, curricula, and column summaries.
- Profile and methods synthesis, catechism-based project proposals.
- Markdown and JSON reports; PNG visualizations of text embeddings, networks,
  distributions, word clouds, and PCA diagnostics.
- Calendar utilities through `symposium.ScheduleExporter` (ICS, JSON, CSV).
- Generic explicit-path CLI commands and year-separated organizer workflows.

```python
from pathlib import Path
from symposium.core.edition import Edition
from symposium.core.data_loader import DataLoader

edition = Edition(year=2026)
participants = DataLoader.load_participant_data(edition.participants_csv)
print(f"{len(participants)} eligible registrations")
```

## Development and verification

```bash
uv sync --locked --extra dev
uv run ruff check src/ tests/ run.py launch.py
uv run ruff format --check src/ tests/ run.py launch.py
uv run python -m pytest
uv build
```

The coverage regression gate is 80%. Tests cover historical workflows, real temporary
CSV files, offline onboarding, failure cases, and generated reports. Tests requiring
live providers are opt-in (`uv run python -m pytest -m real_api`) and require credentials.

## Documentation

- [2026 organizer guide](docs/2026_setup.md): inputs, schema, readiness, analysis, review.
- [Documentation index](docs/README.md): user, API, architecture, and development guides.
- [Data guide](data/README.md): historical and current data organization.
- [Changelog](CHANGELOG.md), [citation](CITATION.cff), [license](LICENSE).
- [Contributing](docs/contributing.md), [issues](https://github.com/ActiveInferenceInstitute/Symposium/issues).

## Citation

```bibtex
@software{symposium2026,
  title = {Symposium: Research Analysis Tools for Active Inference Symposium},
  author = {Active Inference Institute},
  version = {2.2.1},
  year = {2026},
  url = {https://github.com/ActiveInferenceInstitute/Symposium}
}
```

Maintained by the [Active Inference Institute](https://activeinference.institute/).
