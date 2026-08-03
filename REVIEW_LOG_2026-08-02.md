# Symposium Documentation Review Log — 2026-08-02

Docs-deep review pass (parallel fleet, ActiveInferenceInstitute/Symposium).

## Phase 0 — Preflight

- Default branch: `main` (origin/main). Fast-forward pull: already up to date.
- HEAD at start: `5e48328` — "Refactor: ruff-only lint/format cleanup, real-API opt-in marker, coverage uplift to ~86%"
- Working tree clean at start.

### Inventory

- Root docs: `README.md`, `AGENTS.md`, `CHANGELOG.md`, `TODO.md`, `UV_SETUP.md`, `LICENSE` (MIT), `.env.example`, `config.example.json`, `.aii/config.yaml` (InstituteOS sidecar).
- `docs/` (10 files, two naming conventions): `API_USAGE.md`, `CONTRIBUTING.md`, `MIGRATION.md`, `PERPLEXITY_RESEARCH.md` (UPPERCASE) vs `api_guide.md`, `architecture.md`, `csv_visualization_guide.md`, `development.md`, `installation.md`, `user_guide.md` (lowercase). **No docs index.**
- Module docs: `data/README.md`, `data/AGENTS.md`, `tests/README.md`, `tests/AGENTS.md`, `src/symposium/*/README.md` (7), `src/symposium/*/AGENTS.md` (7), `tests/test_calendar/AGENTS.md`.
- No `.github/` (no CI workflows), no `CITATION.cff`, no `SECURITY.md`, no `CONTRIBUTING.md` at root (it lives in `docs/`).
- Source: `src/symposium/{core,analysis,generation,io,visualization,cli,calendar}` + `run.py`, `launch.py`, `setup.py`, `symposium.sh`, `example_calendar.py`.
- Data: `data/inputs/{aif_2024,aif_2025}`, `data/catechisms/`, `data/prompts/`, `data/templates/` (hycl.ttl). `data/domains/` is a **configured default path** (`core/config.py`) that does not exist on disk — user-provided.
- `outputs/` is **tracked in git** (532 files under `outputs/2025_symposium/` incl. `people/` reports + column summaries + visualizations) — README's "gitignored" claim was wrong.

## Phase 1 — Findings (all verified against code before writing)

### Minor (typos, stale tooling refs, formatting)
1. README + installation.md + development.md + CONTRIBUTING.md still document `black`; black was removed from dev deps/`[tool.black]` in `5e48328` (ruff-only). Verified in `pyproject.toml`.
2. README structure block claims `outputs/` is gitignored — it is tracked (verified `git ls-files outputs`).
3. README structure block lists `data/domains/` and omits `data/catechisms/` (docs list) + `data/templates/`; `data/README.md` structure omits `templates/`.
4. README ">80% coverage" — actual ~86% with `--cov-fail-under=80` gate (pyproject.toml).
5. README says `python run.py` "automatically installs the package if needed" — run.py only adds `src/` to sys.path; `symposium.sh` does the uv install. launch.py validates import in-process; does not run setup.py (deprecated, per TODO M3).
6. README bibtex citation `year = 2024`; LICENSE copyright is 2025, package is 2.1.0 (2026). Symposium edition is 2025.
7. `data/README.md` references nonexistent `data/participants_2024.csv` in "Adding New Data".
8. `docs/API_USAGE.md` "Load 47 participants" — current CSV has 93 shareable rows (verified).
9. `docs/API_USAGE.md` "Default configuration in pyproject.toml" — defaults live in `src/symposium/core/config.py` (pyproject has no such config).
10. `docs/PERPLEXITY_RESEARCH.md` test snippet uses fixtures (`mock_save`, `sample_participant_csv`) that don't exist in `tests/conftest.py` (real: `mock_api_client`, `sample_participant_csv_file`, `temp_dir`).
11. Root `AGENTS.md` header "Last Updated: 2025-11-07 / Version 2.0" — package is 2.1.0.
12. Broken README "Tests" badge — points to a GitHub Actions workflow that doesn't exist (no `.github/`).

### Medium (stale sections, restructure)
1. **Stale model names across docs**: `llama-3.1-sonar-large-128k-online` and `google/gemini-pro-1.5-exp` in api_guide.md, user_guide.md, MIGRATION.md, data/README.md. Actual defaults (api.py): Perplexity `sonar`, OpenRouter `anthropic/claude-3.5-sonnet`. `.env.example` and `config.example.json` were already corrected.
2. **user_guide.md uses nonexistent `--registration-file`** — CLI flag is `--csv-file` (verified cli/__init__.py); example CSV path should be the real `data/inputs/aif_2025/Public_Participant_Information.csv`.
3. **csv_visualization_guide.md documents nonexistent CLI**: `symposium visualize wordclouds --input-csv …`, `visualize embeddings --input-csv …`, `visualize all --input-csv …` — the `visualize` CLI reads Markdown via `--input-dir` only (verified cli/__init__.py + cli/visualize.py). Per-column word clouds from CSV exist only via `run.py` option 3 (`ParticipantAnalyzer.generate_column_summaries` → `wordcloud_{column}.png`). Interactive-usage section claims a "Choose input type: CSV" prompt that doesn't exist (run.py option 6 visualizes Markdown reports only).
4. **Docs naming convention split** (4 UPPERCASE vs 6 lowercase) — normalize to lowercase, update links.
5. **No docs index / missing cross-links**: README "Documentation" section omits installation.md, csv_visualization_guide.md, API_USAGE.md, PERPLEXITY_RESEARCH.md, MIGRATION.md, CONTRIBUTING.md, UV_SETUP.md.
6. **No CI**: README badge dead; MIGRATION.md ("pytest + CI/CD", "GitHub Actions") and CONTRIBUTING.md ("All CI checks must pass") claim CI that doesn't exist. Either add minimal CI or soften claims.
7. `data/domains/` referenced everywhere (README, user_guide, MIGRATION, data/README, data/AGENTS.md) but absent — add a directory README explaining it is user-provided and how to create the domain file.
8. api_guide.md retry example imports `tenacity` — not a dependency; the package uses `backoff` (pyproject + api.py).
9. api_guide.md "Custom Provider" shows `BaseAPIProvider` subclass — symbol exists (verified) but the "Register in APIClient.create()" step is inaccurate (create() is a static factory; custom providers aren't registered at runtime — minor wording).

### Major (systemic)
1. Docs-wide accuracy pass over the 10-file docs/ corpus (models, flags, CI, coverage, outputs tracking) — done as the collection of items above; tracked here as one cross-cutting item.
2. CSV-visualization guide rewrite (item Medium-3 is the biggest single-file restructure).
3. CI workflow addition to make badge/claims real (Medium-6) — feasible only if the suite passes in a clean uv environment.

## Phase 3 — Implementation summary

All scoped findings were implemented (commits `669643f`, `98ae63d`, `a6d171e`,
`82ea73a`; see TODO.md "Docs-deep pass" section for the item-by-item mapping):

- Added `docs/README.md` index; normalized `docs/` filenames to lowercase (git mv).
- Rewrote `README.md` (tooling, coverage, structure, citation, docs links, inputs
  note); added `CITATION.cff`; refreshed `AGENTS.md` header/metadata.
- Corrected stale model names, CLI flags (`--csv-file`), `black`→`ruff format`
  references, `tenacity`→`backoff` examples, participant counts (93), config source,
  rate-limit facts across docs/, data/README.md, and module READMEs; fixed
  PCA_GUIDE.md relative links; added `data/domains/README.md` + `domains_dir` to
  config.example.json; updated the tests/conftest.py sample-config model.
- Rewrote `docs/csv_visualization_guide.md` against verified CLI/run.py behavior.
- Added `.github/workflows/ci.yml` (workflow `Tests`: ruff check, ruff format
  --check, pytest + coverage gate); synced UV_SETUP.md CI section; documented CI in
  development.md/contributing.md.
- Added CHANGELOG entry for the docs pass.

## Phase 4 — Verification

- Baseline suite (before edits): `uv run python -m pytest` → **188 passed, 8 skipped
  (real_api opt-ins), coverage 86.26%** (gate 80%).
- `uv run ruff check src/ tests/` → All checks passed; `ruff format --check` → 67
  files already formatted (unchanged by this pass).
- `uv run mypy src/symposium` → **not green** in this environment (missing
  seaborn/sklearn stubs; numpy stub syntax requires 3.12+ under the local Python
  3.14 venv). Pre-existing; mypy intentionally excluded from CI and noted as
  deferred in TODO.md.
- Automated relative-link checker across all repo markdown (excluding archive/,
  outputs/, .git): **0 broken links** after fixes (4 found & fixed during the pass).
- Final `git status` contains only files intended for this pass; push to `main`
  verified (`git status` shows up to date with `origin/main`).

---

*Log maintained during the 2026-08-02 docs-deep pass.*
