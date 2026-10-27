# Changelog

All notable changes to the Symposium package.

## [2.2.1] — 2026-10-26

- Fix the published CI toolchain mismatch: `setup-uv@v1` installed a uv version
  that rejected `uv run --no-sync`. The original failed GitHub runs and v2.2.0
  tag remain preserved.
- Pin setup-uv to the upstream-documented v10.3.2 commit and install uv 0.13.5,
  matching the locally tested toolchain. Declare the minimum uv version and
  let both Python matrix jobs finish independently.
- No participant, presenter, analysis, or visualization behavior changes from 2.2.0.

## [2.2.0] — 2026-10-26

### 2026 preparation
- Add reusable edition paths and offline `edition init` / `edition validate` commands,
  including `--require-data` to distinguish empty templates from populated inputs.
- Ship a header-only 2026 registration template and presenter onboarding workspace;
  preserve historical 2024/2025 inputs without copying people or dates into 2026.
- Make the interactive runner, launchers, reports, and visualizations edition-aware;
  support explicit year selection and shared configuration/model settings.
- Normalize historical, canonical, and year-dependent survey headers. Reject malformed
  rows, ambiguous columns, duplicate eligible names, and report-path collisions.
- Background-only and curriculum-only commands now generate only the selected report.
- Reject missing/malformed explicitly selected configurations, apply configured generation
  parameters, and return nonzero from incomplete participant CLI batches.
- Preserve live credentials when displaying or saving redacted configuration; propagate
  Perplexity payment errors and payment errors from column summaries rather than continuing after a payment failure.
- Reconcile runtime/package/citation version, commit `uv.lock`, declare `httpx` as a
  test dependency, pin the development Python, and test/build locked installs in CI.
- Exclude historical datasets, archived projects, rendered outputs, and local evidence
  from source distributions while preserving all repository originals.
- Add real-file/subprocess regressions and a 2026 organizer guide.

### Included documentation and tooling improvements

### Docs (docs-deep pass, 2026-08-02)
- Added `docs/README.md` documentation index and `CITATION.cff`.
- Normalized `docs/` filenames to lowercase (`API_USAGE.md` → `api_usage.md`,
  `CONTRIBUTING.md` → `contributing.md`, `MIGRATION.md` → `migration.md`,
  `PERPLEXITY_RESEARCH.md` → `perplexity_research.md`) and updated all links.
- Added GitHub Actions CI (`.github/workflows/ci.yml`, workflow `Tests`): ruff check,
  ruff format check, pytest with the coverage gate.
- Fixed stale docs: removed `black` references (ruff-only tooling), corrected model
  names (`sonar`, `anthropic/claude-3.5-sonnet`), nonexistent CLI flags
  (`--registration-file`, `--input-csv`, `visualize wordclouds`), README
  structure/coverage/outputs-tracking/citation claims, and the API retry examples
  (`tenacity` → `backoff`).
- Rewrote `docs/csv_visualization_guide.md` against real CLI/run.py behavior
  (word clouds via `run.py` option 3; Markdown-only `visualize` CLI).
- Documented `data/domains/` as user-provided (`data/domains/README.md`,
  `config.example.json` `domains_dir`), updated `data/README.md` and
  `docs/api_usage.md` (participant count, config source, rate-limit facts).

### Tooling & code quality
- **Ruff-only tooling cleanup:** removed `black` (dev dependency + `[tool.black]`) in favor of
  `ruff format` per project convention. Whole `src/` and `tests/` reformatted and lint-clean
  (0 `ruff check` errors).
- **Dead code removed:** unused `n_comp_participants_viz` / `pca_viz` and stale
  `sklearn.decomposition.PCA` imports in `cli/visualize.py`; unused `top_scores` and dead
  `text` assignment in `distributions.py` / `pca_analysis.py`; renamed ambiguous loop vars
  `l` → `lab` and local graph `G` → `g` (E741/N806/W/F841 lint).
- Repaired a duplicated `label=` expression in `embeddings.py` `_plot_2d` (kept legend-dedup
  behaviour).

### Tests & coverage (~84% → ~86%)
- **Real-API opt-in marker:** live-LLM tests (`TestRealAPIIntegration`, `TestRealAPIWorkflows`,
  `TestAPIIntegration`) are now gated behind the `real_api` pytest marker (registered in
  `pyproject.toml`) — opt in via `-m real_api`; they still require API keys.
- Added tests for `io/readers` (JSON/CSV/markdown/template/prompt + directory listing),
  `cli/analyze` (backgrounds & curricula handlers), and `core/config` (nested `set`, `save`
  API-key redaction, `ensure_paths`, `get_path` errors).

## [2.1.0] — 2026-08-01

Comprehensive hostile red-team review, correctness/robustness fixes, and a test
coverage uplift (coverage 40% → ~84%).

### Fixed — correctness & robustness
- **PCA/t-SNE dimension reduction** works on small corpora:
  - t-SNE pre-PCA no longer crashes when `n_samples < n_features`.
  - TF-IDF `max_df=0.90` no longer conflicts with `min_df` on tiny (1–2 doc) inputs.
- **matplotlib ≥3.9 compatibility (major):** all 2D/3D scatter/heatmap plots used the
  removed `plt.cm.get_cmap` API and `Axes.boxplot(labels=...)`; replaced with
  `matplotlib.colormaps[...]` and `tick_labels=`, so embeddings/network/PCA plots render
  again on current matplotlib.
- **ZeroDivisionError** in `ParticipantAnalyzer.analyze_all_participants` when a CSV yields
  zero shareable participants.
- **`load_dotenv()` parent-directory walk** no longer pulls an unrelated `.env` from above the
  repository (deterministic config, no cross-project secret leakage).
- **API-client swap restored on failure** during Perplexity background research
  (`try/finally`).
- **False "components for X% variance"** annotation in scree plots removed (annotate only
  when the threshold is actually reached).
- **Silently-zeroed 95% CIs** on single-document TF-IDF plots now fall back to no error bars
  with a warning; asymmetric (lower/upper) CI error bars.
- **Network layouts** are now seeded/fixed for reproducibility.
- **`run.py` hardening:** anchored share-count regex, guarded interactive participant
  selection (invalid/out-of-range input), `None`-safe result previews, and a log path that is
  no longer CWD-coupled.

### Changed
- **`cli/visualize.py` dead/broken `main()` removed** (dispatch centralized in
  `symposium.cli:main`); CLI `--method` now exposes all 7 supported reduction methods.
- **`run.py` `create_visualizations`** calls the visualization functions in-process instead of
  shelling out to the `symposium` console script.
- **`launch.py`** no longer runs the deprecated `setup.py`; validates the installed package
  in-process (install/validation driven by `uv` + `pyproject.toml`).
- **Docs:** corrected README `--input-csv` (nonexistent) and dimension-method claims, unified
  `config.example.json` model, corrected `docs/MIGRATION.md` references to nonexistent
  `scripts/` utilities.
- Added `CHANGELOG.md`.

### Removed
- `src/symposium/visualization/legacy_visualization_methods.py` (dead, unimportable, 0%
  coverage, no importers).
- Dead `shell=True` `run_command` in `setup.py`.

### Tests
- Added real (no-mock for plotting; API-boundary mocked per repo convention) tests for:
  CLI dispatch routing (all 10 subcommands), `analyze`/`generate` handler bodies,
  `PCAAnalyzer` report generation, `DistributionPlotter` paths, and the `visualize`
  command bodies producing files on disk.
- Deleted/made-real dead or failure-masking tests; made tests hermetic (no source-tree
  writes); removed environment-dependent/tautological assertions.
- Added `--cov-fail-under=80` coverage regression gate (overall coverage ≈84%).

## [2.0.0]
Prior release (see repository history for details).
