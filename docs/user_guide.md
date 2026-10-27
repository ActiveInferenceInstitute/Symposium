# Symposium user guide

Symposium 2.2.0 supports the 2026 edition and explicit historical workflows. Start
with the [2026 organizer guide](2026_setup.md) for full registration fields, consent,
readiness checks, and presenter onboarding.

## Installation and configuration

```bash
uv sync --locked --extra dev
uv run symposium --version
uv run symposium --help
```

The runner uses optional project-local `config.json`. The CLI loads JSON when selected
with `--config path.json` before the command. An explicitly selected missing or invalid
configuration is an error. Environment values override JSON; explicit edition CLI flags
and the runner's `--year` override configured edition values.

Store credentials in `.env`, using `.env.example` as a guide. Customize models and
provider parameters in `config.json`, based on `config.example.json`. Setup, preflight,
and the default test suite run without paid API calls.

## Data preparation

```bash
uv run symposium edition init --year 2026
uv run symposium edition validate --year 2026
```

```text
data/inputs/aif_2026/
├── Public_Participant_Information.csv
├── presenters/
│   └── Presenter_Name/
│       ├── openalex-group-by-YYYYMMDD.csv
│       └── works-YYYY-MM-DD.csv
├── templates/
└── schedule.json
```

The shipped participant CSV and presenter templates have headers only. Only organizers
can supply the current roster and confirmed schedule. Historical 2024 and 2025 data
remain in their original folders.

An illustrative registration using canonical headers:

```csv
name,share_publicly,background,active_inference_application,learning_needs
Example Participant,yes,Computer Science,Computational modeling,Mathematical foundations
```

Required columns are `name` and `share_publicly`. Full 2025 survey questions and
current-year impact questions are supported. Only explicit affirmative sharing consent
permits processing. Duplicate headers/names and report-filename collisions are errors;
optional survey null markers are normalized to empty strings. See the organizer guide
for the complete field list.

Before running a populated edition:

```bash
uv run symposium edition validate --year 2026 --require-data
```

This checks both participants and presenters. Default preflight accepts a structurally
valid empty scaffold with warnings; `--require-data` returns nonzero until both inputs
have data. Existing initialization never overwrites organizer files. Initialization
currently requires macOS or Linux; existing analysis and generation commands retain
their normal platform support.

## Analyze participants

```bash
uv run symposium --config config.json analyze participants \
  --csv-file data/inputs/aif_2026/Public_Participant_Information.csv \
  --output-dir outputs/2026_symposium/people --api-provider openrouter
```

Add `--include-background-research`, `--include-curriculum`, or
`--include-column-summaries` for combined workflows. Background-only and curriculum-only
commands avoid generating an extra profile:

```bash
uv run symposium analyze backgrounds \
  --csv-file data/inputs/aif_2026/Public_Participant_Information.csv \
  --output-dir outputs/2026_symposium/people
uv run symposium analyze curricula \
  --csv-file data/inputs/aif_2026/Public_Participant_Information.csv \
  --output-dir outputs/2026_symposium/people --api-provider openrouter
```

The participant CLI rejects empty inputs before creating a provider client and returns
nonzero if a batch contains errors or stops before completion. Completed reports are
preserved. Review all generated content before distribution.

## Presenter profiles and methods

The input path must be the directory immediately containing each presenter's folder:

```bash
uv run symposium analyze presenters \
  --data-dir data/inputs/aif_2026/presenters \
  --output-dir outputs/2026_symposium/presenters --max-rows 10
uv run symposium generate profiles \
  --data-dir data/inputs/aif_2026/presenters \
  --output-dir outputs/2026_symposium/presenters --include-methods
```

Both commands accept an optional `--domain-file` containing organizer-provided Markdown
context. Add `--api-provider perplexity` or `--api-provider openrouter` to select a
provider explicitly.

## Custom domain knowledge

Create your own domain Markdown document with relevant background, goals, constraints,
and reviewed references. It is context for generated drafts, not an independent source
of validated claims. Pass its path through `--domain-file`.

## Project proposals

```bash
uv run symposium generate projects \
  --profiles-dir outputs/2026_symposium/people \
  --output-dir outputs/2026_symposium/proposals \
  --domain-file data/domains/active_inference.md --catechism KarmaGAP
```

Supply the domain file yourself. Optional flags are `--catechisms-dir` and
`--collaborators-file`. Proposal templates include KarmaGAP, EUGrants, and Synthetic.

## Visualizations

Visualization commands read Markdown reports rather than registration CSVs:

```bash
uv run symposium visualize all \
  --input-dir outputs/2026_symposium/people \
  --output-dir outputs/2026_symposium/visualizations --method pca --layout spring
```

Individual commands are `visualize embeddings`, `visualize networks`, and
`visualize distributions`. See the [visualization guide](csv_visualization_guide.md)
for supported methods, layouts, word clouds, and diagnostic plots.

## Interactive interface and calendars

```bash
uv run python run.py --year 2026
uv run python run.py --year 2025
```

The menu offers the same selected-edition participant and visualization workflows.
`launch.py` and `symposium.sh` forward the same year/config arguments.

Calendar export remains a Python API through `symposium.ScheduleExporter`, using
organizer-supplied events. See [calendar documentation](../src/symposium/calendar/README.md).
An empty schedule template is not a confirmed event schedule.

## Verification

```bash
uv run ruff check src/ tests/ run.py launch.py
uv run ruff format --check src/ tests/ run.py launch.py
uv run python -m pytest
uv build
```

Live-provider tests require explicit opt-in with `-m real_api`. Refer to the
[release record](release_2_2_0.md) for the exact software checks and their limits.
