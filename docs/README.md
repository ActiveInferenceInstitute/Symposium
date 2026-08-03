# Symposium Documentation

Index of guides for the Symposium package. All guides describe the current state of
the code on `main`; if something looks wrong, please open an issue.

## Getting Started

| Guide | Purpose |
|-------|---------|
| [Installation](installation.md) | Environment setup with uv, API key configuration, verification |
| [Quick Start](../README.md#quick-start) | Fastest path from clone to running (in the main README) |
| [UV Setup](../UV_SETUP.md) | uv commands, venv management, and troubleshooting |

## Usage

| Guide | Purpose |
|-------|---------|
| [User Guide](user_guide.md) | End-to-end usage: data prep, CLI commands, Python API, workflows |
| [API Guide](api_guide.md) | LLM providers, configuration, token management, error handling |
| [API Usage](api_usage.md) | Provider roles (Perplexity vs OpenRouter) in the 2025 participant workflow |
| [CSV Visualization Guide](csv_visualization_guide.md) | Word clouds, dimension reduction, networks, and distributions |
| [Perplexity Research](perplexity_research.md) | Web-research integration for participant background analysis |

## Development & Project

| Guide | Purpose |
|-------|---------|
| [Architecture](architecture.md) | System design, module dependencies, extensibility |
| [Development](development.md) | Dev setup, testing, code standards, adding features |
| [Contributing](contributing.md) | Contribution guidelines and PR process |
| [Migration](migration.md) | Upgrading from the v1.x scripts to the v2.x package |
| [Changelog](../CHANGELOG.md) | Release history |
| [Backlog](../TODO.md) | Authoritative project backlog / TODO |
| [AI Agents Overview](../AGENTS.md) | All AI agents in the system (per-module: `src/symposium/*/AGENTS.md`) |

## Code-adjacent documentation

- Module READMEs: `src/symposium/*/README.md`, `data/README.md`, `tests/README.md`
- [License](../LICENSE) — MIT
- [Citation](../CITATION.cff) — cite the package as `symposium2025` (see README)

## Conventions

- Filenames in `docs/` are lowercase (`snake_case.md`).
- Relative links between docs use the plain filename (e.g. `[User Guide](user_guide.md)`).
- Guides are verified against the code during review passes; see
  `REVIEW_LOG_2026-08-02.md` for the most recent docs audit.
