# Changelog

All notable changes to the Symposium package.

## [Unreleased] — 2026-11-12 (gate and documentation)

### Participant figure legibility

- The participant text-network figure places each node ID away from that node's own
  edges. IDs placed above their node covered the similarity weight of any vertical
  edge, which happened on the November 12 cohort.
- The final-draw overlap diagnostic in `visualizations.json` counts only drawn text.
  Tick labels of hidden axes and of ticks outside the view limits were counted before,
  which reported overlaps that never appear in the image.
- A regression test renders three network shapes and requires zero overlaps.

One local gate, and CI calls it instead of restating commands.

- Add `gate.sh`: one documented entry point with separately runnable arms `lint`,
  `test`, `test-fast`, `build`, `program`, `site`, `docs` and `gnn`
  (`./gate.sh list`, `./gate.sh all`). Every arm runs with `--no-sync`, so
  environment setup stays with the caller. The default arm is `test-fast`: the six
  package-module suites (`tests/test_core`, `test_io`, `test_cli`, `test_analysis`,
  `test_generation`, `test_calendar`) without coverage instrumentation, explicitly
  not a substitute for `test`.
- `.github/workflows/ci.yml` now has `lint`, `test`, `build` and `gnn-conformance`
  jobs that call those arms. Lint, the distribution build, edition validation and the
  public-site render ran inside each of the three matrix entries before; each now runs
  once (lint/docs on 3.12, build/program on the 3.12 pin), and the documentation check
  is new. The test arm is unchanged: the full suite with the 80% coverage gate.
- GNN conformance: `.github/gnn-pin.json` (schema `gnn-importer-pin/v1`,
  `v5.0.3`, `8f293d9ba810e6eda5c09842d9c7ed9ffa5f92c1`) is now the sole executable
  source of the revision. The workflow's inline heredoc moved to
  `scripts/gnn_conformance.py`, which validates the pin instead of restating the tag
  and revision. Job key `gnn-conformance`, display name `gnn conformance (pinned)`;
  see [.github/GNN.md](.github/GNN.md).
- `.github/workflows/pages.yml` renders the site through the `site` arm instead of
  an inline Python snippet.
- Documentation: add [`docs/documentation-index.md`](docs/documentation-index.md)
  (flat index, checked for completeness), `docs/_generated/` with the script-generated
  [gate measurements](docs/_generated/gate-measurements.md), and
  `scripts/check_docs.py` (relative links, index completeness, arm list) as the
  `docs` arm. Refresh `docs/README.md`, `docs/development.md`,
  `docs/contributing.md`, `tests/README.md`, `README.md` and `AGENTS.md`.
- No types arm: `mypy` is configured in `pyproject.toml` but has never been a gate
  and reports 89 errors in 26 files (mostly missing third-party stubs) on this
  checkout. A passing type check is not claimed.
- Wall time per arm on the host that refreshed it is generated in
  [gate measurements](docs/_generated/gate-measurements.md); one run per arm, not a
  benchmark.

## [Unreleased] — 2026-11-08
## [3.3.0] — 2026-11-12

The final-lineup book is published on Zenodo at
[10.5281/zenodo.24161029](https://doi.org/10.5281/zenodo.24161029), a new version of
concept record 10.5281/zenodo.23986504; all six deposited files were read back
anonymously and match the reviewed package. See
[the release record](docs/release_3_3_0.md).

- Refresh `data/public/2026/` from the November 12 organizer snapshot: 55
  contributions (37 prerecorded, 14 livestreamed, 3 workshops, keynote), 19 UTC
  sessions and 119 consenting participant profiles. Prerecorded talks without a
  submitted video and withdrawn contributions are removed; new contributions added.
- Regenerate dossiers, participant briefs, the CRLF UTC calendar, portraits and the
  public manifest; keep the two pending abstracts explicit.
- Render the version 3.3.0 PDF/Word book (60 PDF pages) with the version DOI on the
  cover, the same artwork, 51 credit entries and exact-match public profiles.
- Derive the site test's pending-abstract count from the bundle instead of a literal.
- Bump the package, citation and book credits to 3.3.0.

### November 8 public-program refresh

Refresh of the public 2026 program from the current sources, captured 2026-11-08 UTC
(Public Program Feed and master program), projected with the repository's own
`project_snapshot` rules. Organizer-approved by Daniel Friedman.

- Sessions (18 → 19): Majid D. Beni moves to 11:00–12:00 UTC on November 13; new
  livestreamed session "Learning Active Inference in 2026: Textbook Group Review"
  (Fraser Paterson, Andrew Pashea, Daniel Friedman) at 13:00–14:00 UTC, with its
  program abstract; Luca Possati's 14:00 slot is now "Active Inference and Design:
  Live Q&A" on his prerecorded talk.
- Presentations (57 → 58): adds the Textbook Group Review and the Possati Q&A; applies
  the Michael Lennon retitle, the NEST presenter credit order
  (John H. Clippinger, Holly Grimm, Daniel Friedman) and the Avel Guénin—Carlut
  abstract fix. Two program abstracts remain pending (Karl Friston, Mike Levin).
- Portraits: the NEST combined presenter image is fetched from the public program
  document through `attach_public_portraits` (sanitized JPEG); unchanged talks keep
  their hash-verified pictures.
- Regenerate `program.ics`, the affected dossiers and the
  `publication.json` digests; snapshot date 2026-11-08. The site test now expects
  two pending abstracts. `verify_public_tree`, the local site build and the test
  suite pass.
- Not refreshed here: participant profiles (still the 45 approved on November 1)
  and the PDF/Word book, which remains the v3.2.0 Zenodo edition.

## [3.2.0] — 2026-11-05

The book is published on Zenodo at
[10.5281/zenodo.23986505](https://doi.org/10.5281/zenodo.23986505), with public
metadata, DOI resolution and all six unauthenticated asset SHA-256 checks verified.
The [GitHub v3.2.0 software release](https://github.com/ActiveInferenceInstitute/Symposium/releases/tag/v3.2.0) is published.
All six attached book-package assets match the frozen Zenodo package by SHA-256;
remote CI and the updated Pages deployment are verified.

- Prepare the *2026 Active Inference Symposium — Presenter Program* in PDF and
  editable Word through the native docxology/template integration, with 18 mm
  margins, dated institutional cover, all exact presenter/group credits, generated
  cover and page-two artwork, and the published book DOI.
- Include supplied public affiliations, ORCIDs and backgrounds only through exact
  whole-label joins from approved 2026 public sources. Preserve absent profiles,
  composite credits, the 57 source contributions and three pending abstracts.
- Improve participant and presenter chart readability, shared histogram bins and
  cross-process network-layout ordering. Bind charts to validated ordered inputs,
  explicit missingness, method parameters and artifact hashes.
- Keep the new 55-record public analysis cohort separate from the retained
  November 1 public program's 45 previously approved participant profiles. Refresh
  only the book bytes and corresponding public manifest digests in that historical
  tree; do not claim renewed consent or publish private captures or provider drafts.
- Scope the authorized organizational email exception to the exact PDF/Word book
  artifact names while retaining participant, other-email, private-link, local-path
  and PDF active-content rejection.
- Reconcile citation and release documentation with version 3.2.0 and the published
  book DOI. See [the release record](docs/release_3_2_0.md) for status and scope.
- Validate the DOI book source with 776 passed tests, 9 skips and 89.85% coverage;
  lint and format checks pass. Independently review all 62 PDF and 62 Word-preview
  pages; all 43 required book checks pass. These are local results, distinct from
  the independently verified remote CI and deployment results.

### November 1 public-program candidate

- Refresh the public program candidate to 57 presentations and 18 explicit UTC
  sessions, with 45 participant profiles projected from affirmative consent captured
  for that dated snapshot.
- Regenerate dossiers, participant briefs, the UTC calendar, and draft PDF/Word
  abstract books; retain pending abstracts and the recorded portrait omission.
- Support typed Docs datetime epochs as UTC seconds while rejecting malformed
  epochs and continuing to require offsets on plain timestamp strings.
- Preserve submitted PDF glyphs with staged font bytes and reject missing-glyph
  compiler diagnostics; keep prior failed renders as private review evidence.
- Show the source capture's UTC date and live-program revision authority in the
  explorer; bind the optional snapshot date to capture time at public staging.
- Keep organizer approval of the exact candidate commit as the merge, tag, and
  deployment gate.

## [3.1.0] — 2026-10-27

- Add a validated catalog connecting nine methods/workflows to ten public repositories,
  with explicit native-integration/manual-handoff/resource roles and pinned README evidence.
- Add offline `organize methods` and `organize capabilities` commands; opt-in environment
  inspection reports presence only, never credential values or authentication claims.
- Publish a searchable methods hub, canonical/social and safe structured metadata,
  sitemap, catalog, discovery index and source guidance; exclude participant self-reports
  from the additional machine discovery index.
- Improve method/repository navigation and filtered deep links while preserving no-JavaScript
  content, native disclosure behavior and all approved public data/book bytes.
- Refresh method, credential, indexing and agent documentation; add package discovery URLs.

## [3.0.0] — 2026-10-27

### Runtime compatibility

- Require Python 3.12 or newer; remove Python 3.10/3.11 compatibility and align the
  development, lint, type-check and setup guidance with that minimum. Python 3.10
  reached upstream end of life on 2026-10-01. Keep the previous release intact.
- Test Python 3.12, 3.13 and 3.14, including actual approved-public-tree verification
  and static site generation. Keep Template's native Python 3.14 runtime separate.

### Next-intake methods and website

- Add read-only readiness and candidate-review commands that verify both snapshots,
  report additions/removals/changed fields and artifact changes, and keep comparison
  reports in private operator storage. Strict completeness is explicit and separate
  from integrity or live-source freshness.
- Derive website dates from approved event fields, expose pending content clearly,
  explain publication methods and downloads, and improve multiword search and deep links.
- Decode and validate image assets before building output; preserve the existing
  approved roster, images, dossiers, briefs, calendar and abstract-book bytes.
- Require explicit `--run-real-api` authorization before live-provider tests can run,
  even when credentials are present; verify the boundary with local sentinel tests.
- Refresh installation, development, methods and organizer documentation against
  actual parser interfaces; retain historical release and evidence records.

## [2.3.0] — 2026-10-26

- Add private InstituteOS/Superhuman Docs intake and guarded append-only synchronization
  receipts with conflict detection, idempotency, and readback verification.
- Publish an explicitly approved 2026 program: 32 contributions, 30 unambiguous consenting
  participant profiles, 14 timed sessions, and 19 metadata-free submitted portraits.
- Keep unpublished abstracts and schedule titles visibly pending; quarantine ambiguous
  registrations and retain private reconciliation evidence outside the public repository.
- Generate source-grounded presenter dossiers, participant learning briefs, and UTC ICS
  downloads without paid API calls or inferred author identities.
- Render the working abstract book through the native docxology/template pipeline,
  preserving submitted prose and producing A4 PDF and editable Word artifacts.
- Add a responsive, searchable GitHub Pages explorer using the Institute design system,
  approved Institute method links, and consent-aware public file manifests.
- Gate public staging on fresh source projection, explicit application, artifact hashes,
  safe paths, image metadata checks, and rejection of unmanifested files.
- Add real-file, subprocess, image, calendar, consent, tampering, and transport controls;
  preserve historical editions and existing analysis/generation workflows.

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
