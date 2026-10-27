# Preparing the 2026 Symposium

Version 2.2.0 retains last year's registration structure and existing presenter
publication workflows. It adds reusable edition paths, offline setup, and explicit
input validation. The shipped 2026 files are empty templates; they do not establish
an actual roster or schedule.

## Install and select an edition

```bash
uv sync --locked --extra dev
uv run symposium edition init --year 2026
uv run symposium edition validate --year 2026
```

Edition initialization currently supports macOS and Linux. The initialization
command preserves an existing edition. For a new edition, it
creates a complete scaffold with exclusive publication rather than overwriting
existing files. Custom storage roots use `--data-dir` and `--output-dir`. `Edition`
validates integer years from 2000 through 2100; the current default is explicitly
2026, independent of the system clock.

`uv run python run.py --year 2026` uses the same paths. `--year 2025` explicitly
selects historical registrations. There is no automatic fallback to older data.
Existing analyze/generate commands use the explicit paths supplied to them.

## Import participant registrations

Populate `data/inputs/aif_2026/Public_Participant_Information.csv` with current,
authorized registrations. Keep the full-question headers from the supplied template,
or use the canonical names below. The survey's impact question refers to 2027;
the 2025 question referring to 2026 is also supported for historical imports.

| Canonical field | Content |
|---|---|
| `share_publicly` | Explicit public-sharing consent; required column |
| `name` | Participant display name; required column |
| `email` | Contact information; optional |
| `affiliations` | Institutional or community affiliations |
| `orcid` | Research identifier, retained as text |
| `background` | Background, prior works, links |
| `pragmatic_value` | What would be useful at the Symposium |
| `epistemic_value` | What would be interesting to learn |
| `active_inference_application` | Application domain and stage |
| `challenges` | Research/application hurdles |
| `learning_needs` | Helpful resources, tools, communities |
| `heard_about` | How they heard about the event |
| `future_impact` | Future application and impact ideas |
| `comments` | Other comments or questions |

Only affirmative `yes`, `y`, `true`, or `1` values are included (case insensitive,
with surrounding whitespace removed). Blank and negative consent exclude the row.
A missing consent column is an input error. Optional empty fields remain empty
strings; historical survey null markers such as `None`, `NA`, and `N/A` also become
empty strings in optional fields. Identifiers otherwise remain text; no answers are invented. Use UTF-8 CSV with properly quoted commas and
newlines. Header whitespace and a UTF-8 BOM are accepted.

Preflight rejects ambiguous aliases, duplicate headers, malformed row widths,
duplicate eligible names, and different names that produce the same report folder.
Resolve these in the source registrations rather than letting one report overwrite
another. Diagnostics report structure and counts; participant answers are not printed
by edition validation. Keep private contact data and generated reports out of public
commits; review the actual staged files before publishing any roster.

Do not copy historical participant rows into the new edition. Prior registrations
and consent do not establish current participation.

## Add presenter publication data

Place each new presenter's OpenAlex exports under:

```text
data/inputs/aif_2026/presenters/Presenter_Name/
├── openalex-group-by-YYYYMMDD.csv
└── works-YYYY-MM-DD.csv
```

Use exactly one topic export and one works export per presenter. Move older exports
outside this live input directory. Consult the generated presenter README/templates
for accepted topic and publication columns. Empty tables and ambiguous exports fail
readiness. Historical 2024 topic exports with their metadata row are supported by
preflight. Presenter names are input folder names, so choose distinct safe names.
No fictional presenter folder is populated by initialization.

## Preflight before processing

```bash
uv run symposium edition validate --year 2026 --require-data
```

Default validation can succeed for a valid empty scaffold while reporting warnings.
`--require-data` requires both eligible registrations and presenter exports and exits
nonzero when either is absent. Structural errors fail either mode. This is an offline
input gate; it does not check provider credits, identities, scientific accuracy,
event arrangements, or consent beyond the recorded affirmative field.

## Configure providers and generate reports

```bash
cp .env.example .env
cp config.example.json config.json
```

Add provider credentials locally. Model/temperature/token settings belong in the
JSON configuration, selected for CLI commands with `--config config.json` before the
command. Environment settings override JSON. API availability and credit balances are
verified only when you deliberately make a provider request.

```bash
uv run symposium --config config.json analyze participants \
  --csv-file data/inputs/aif_2026/Public_Participant_Information.csv \
  --output-dir outputs/2026_symposium/people --api-provider openrouter

uv run symposium --config config.json analyze presenters \
  --data-dir data/inputs/aif_2026/presenters \
  --output-dir outputs/2026_symposium/presenters

uv run symposium visualize all \
  --input-dir outputs/2026_symposium/people \
  --output-dir outputs/2026_symposium/visualizations
```

Background-only and curriculum-only commands generate only the selected report type.
The existing combined participant analysis can generate profiles plus optional
backgrounds/curricula. Review Markdown and JSON results before distributing them.
Inspect error messages and retained partial outputs if processing stops. A generated
profile is an AI draft, not a verified assessment of a person.

## Calendar and proposals

Initialize no confirmed schedule until organizers supply actual sessions and dates.
The existing `ScheduleExporter` Python API exports organizer-supplied schedules to
ICS/JSON/CSV; see [calendar documentation](../src/symposium/calendar/README.md).
Proposal generation uses a user-provided domain context, existing catechism templates,
and optional collaborator context. Neither operation establishes scientific findings
or funding eligibility.

## Release checks

```bash
uv run ruff check src/ tests/ run.py launch.py
uv run ruff format --check src/ tests/ run.py launch.py
uv run python -m pytest
uv build
```

See [the release verification record](release_2_2_0.md) for the tested software scope
and remaining organizer-supplied data requirements.
