# Symposium contributor map

Symposium contains Python research workflows and a static public program/methods
site. CLI commands dispatch into modules; descriptive historical agent roles are
not evidence of autonomous orchestration, provider failover or verified outcomes.

## Reach the right source

| When changing | Read first |
|---|---|
| Public intake, consent, manifests, dossiers or native book rendering | [Organizer workflow](docs/organizing_publication.md) and [organizing map](src/symposium/organizing/AGENTS.md) |
| Method signposting, repository catalog or website indexing | [Discovery contract](docs/discovery.md), [method boundaries](docs/methods.md), `organizing/ecosystem.py` and `organizing/discovery.py` |
| Provider configuration or paid research | [Credential boundaries](docs/credentials.md), [API contract](docs/api_guide.md) and actual `core/api.py` / `core/config.py` |
| Research-input schema or editions | [2026 input guide](docs/2026_setup.md) and `core/edition.py` |
| Tests, packages or releases | [Development](docs/development.md), [test guide](tests/README.md), `pyproject.toml` and actual workflow files |

Paths in the last column without a root are under `src/symposium/`. Inspect the
actual parser in `src/symposium/cli/` before documenting a command. Preserve existing
user work and historical evidence. User/global workspace instructions remain binding.

## Top-level layout

| Path | Contents |
|---|---|
| `src/symposium/` | Installable package: `cli/`, `core/`, `analysis/`, `generation/`, `organizing/`, `visualization/`, `io/`, `calendar/`. |
| `tests/` | Pytest suite mirroring `src/`; `tests/README.md` and `tests/AGENTS.md` are the entry points. |
| `docs/` | Modular operator and developer guides; [`docs/README.md`](docs/README.md) is the index. |
| `data/` | `inputs/` (historical + 2026 scaffold), `public/2026/` (approved snapshot), `catechisms/`, `prompts/`, `templates/`, `domains/`. See [`data/README.md`](data/README.md). |
| `outputs/` | Tracked example run state (e.g. `outputs/2025_symposium/people/`); new runs write here. |
| `archive/` | Historical ISM code, inputs and generated artifacts; see [`archive/README.md`](archive/README.md). |
| `run.py`, `launch.py`, `symposium.sh` | Interactive menu, launcher and shell wrapper. |
| `pyproject.toml`, `uv.lock`, `.python-version` | Package metadata and the locked Python 3.12 environment. |
| `.aii/` | InstituteOS sidecar metadata; [`README.md`](.aii/README.md) explains it. |
| `.github/workflows/` | `ci.yml` (lint + tests) and `pages.yml` (public site deployment). |

## Test and lint

```bash
uv sync --locked --extra dev
uv run ruff check src/ tests/ run.py launch.py
uv run ruff format --check src/ tests/ run.py launch.py
uv run python -m pytest
```

`pytest` enforces the 80% coverage gate declared in `pyproject.toml`. Live-provider
tests are opt-in via `uv run python -m pytest --run-real-api -m real_api` and need
credentials. A checkout whose `.venv` has not been synced cannot run the suite
offline; see [`TODO.md`](TODO.md).

## Public/private boundary

Approved `data/public/2026/` and the research scaffold `data/inputs/aif_2026/` are
separate. Raw mappings, registrations, consent ledgers, credentials, drafts and
candidate comparison reports belong outside the public checkout. New intake needs
fresh source review and explicit publication approval; historical sharing consent is
not renewed consent. Source/static integrity does not establish freshness or truth.

The curated repository catalog contains public source evidence and bounded handoffs.
A resource link does not grant access, install an adapter, transfer data, authorize
publication or validate a scientific claim. Keep private InstituteOS identifiers and
operational source content out of public catalogs and pages.

## Development rules

Moved here from the repository's former `.cursorrules` file; these are the
conventions to follow when changing Symposium.

### Code and layout

- PEP 8, type hints on functions, Google-style docstrings for public functions,
  and import grouping (standard library, third party, local).
- `snake_case` for functions and variables, `PascalCase` for classes.
- One class per module where practical; tests mirror the source layout under
  `tests/`.
- Explain complex logic in comments and keep TODO/FIXME items tracked.

### Tests and quality gates

- Unit tests for functions, integration tests for end-to-end workflows, and
  live-provider tests only behind the opt-in `real_api` marker.
- Coverage regression gate: `--cov-fail-under=80` in `pyproject.toml`; raising
  it is tracked in `TODO.md`.
- Mocking is expected where it keeps tests deterministic: realistic fixtures
  and edge cases instead of live calls.
- `ruff check` and `ruff format --check` are the lint and format gates; CI runs
  Python 3.12, 3.13 and 3.14.

### Providers and outputs

- Providers: Perplexity (`sonar`) and OpenRouter; configuration comes from
  environment variables with the project-local JSON override.
- Handle provider failures with retries and graceful degradation;
  `PaymentRequiredError` stops processing immediately with clear guidance.
- Reports are Markdown and JSON, and both must stay valid and readable.

### Data handling

- CSV inputs are UTF-8 with validated headers and structure; JSON outputs keep a
  consistent schema; Markdown stays clean and consistently structured.
- Validate paths (no directory traversal) and sanitize user input.
- Raw registrations, consent ledgers, credentials and drafts stay outside the
  public checkout (see the public/private boundary above).

### Research claims

- Evidence-based analysis, correct method identification, and responsible AI
  use: generated research drafts need organizer review before sharing.
- A resource link or a generated artifact never establishes scientific
  validity, access or authorization.

## Verification and completion

Use the declared uv toolchain and external GitVault runtime/cache/temp bindings in
this workspace. Reproduce a defect with an input that fails before fixing it. Retain
actual command statuses and failures. For website changes, exercise the real rendered
page, keyboard, narrow/light/dark/no-JavaScript behavior and downloads. For native
book changes, render and inspect every final page. Match claims to the evidence scope.

Before an authorized publication, run the repository checks, inspect the staged
changes, obtain independent review, and verify remote CI/deployment and the actual
hosted/released bytes. Never audit work you built. Default tests keep marked paid
provider calls disabled; explicit `--run-real-api` authorization is separate from
having credentials. A clean command exit alone is not publication or scientific proof.
