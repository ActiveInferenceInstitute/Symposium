# Changelog

All notable changes to the Symposium package.

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
