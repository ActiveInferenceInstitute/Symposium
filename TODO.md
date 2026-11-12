# Symposium TODO / Backlog

## Current intake work — 2026-11-12

The November 12 organizer snapshot has now been reviewed, staged and published as
version 3.3.0, which supersedes the 2026-10-27 intake list. What follows is the state
of that intake, with the residual items that are still open.

- [x] **Organizer snapshot, consent exclusions and ambiguous identities reviewed.**
  119 consenting participants in the published projection (latest answer per email is
  an affirmative "Yes" and no answer for the same email is "No"); two previously
  listed participants no longer appear and were removed without inferring a reason.
  ✓ [`docs/release_3_3_0.md`](docs/release_3_3_0.md)
- [ ] **One withheld registration still needs an organizer decision.** A consenting
  registration is withheld because its affiliations field contains contact
  information requiring review; the repository records the fact but not the redaction
  or a re-review. Owner: organizers. ✓ same record, "Public data and analyses".
- [ ] **Two abstracts are still pending, and cannot be authored here.**
  `data/public/2026/program.json` carries 55 presentations; no `abstract` exists for
  `talk-350722794e66b4b8` ("Active Inference and Free Energy Principle in 2026") or
  `talk-b5f346f866630c4c` ("Evolution, Emergence, Prediction."). The site shows them
  as missing rather than inventing text. Owner: those presenters / organizers.
- [x] **Native artifacts generated and visually inspected.** All 60 PDF pages were
  reviewed and the Word book contains every contribution title and the version DOI
  (text equivalence alone would not have established this). ✓ release record.
- [x] **Public integrity/readiness checks ran.** `./gate.sh program` passes (54.02 s
  at `b43415b` in the [gate measurements](docs/_generated/gate-measurements.md)), and
  the six deposited assets were downloaded unauthenticated and matched byte-for-byte.
  ✓ gate measurements + release record.
- [x] **Deployed site and downloads verified against the manifest (2026-11-12).**
  `https://activeinferenceinstitute.github.io/Symposium/` served `index.html`
  (`90cdff7d…`), `program.json` (`217b4a45…`) and `downloads/book.pdf`
  (`9308767e…`) byte-identical to `origin/gh-pages` and to
  `data/public/2026/book.pdf`; `data/public/2026/` has not changed since the
  publishing build (`7ecac04`), so the served snapshot is the current approved tree.
- [ ] **No optional paid research workflow has been authorized.** Nothing in this
  repository records an approval, and the standing rule is unchanged: generated
  drafts never enter the public projection automatically. Owner: organizers.

See [operator workflow](docs/organizing_publication.md) and [methods](docs/methods.md).
These remain continuing organizer/release tasks; the completed records below are
historical evidence and do not establish current runtime or scientific validation.

---

## Environment prerequisites — resolved 2026-11-12

The 2026-11-11 observation below was accurate then; it no longer describes this
checkout.

- [x] **`.venv` is usable.** `uv sync --locked --extra dev` completed against the
  committed lock (Python 3.12.16, pandas 3.1.1, scipy 1.18.1), and
  `uv run --no-sync python -c "import pandas"` now succeeds.
- [x] **The wheel gap is closed for the development pin.** The same sync populated
  the `cp312-…-arm64` wheels that were missing; no lock or version change was made.
- [x] **The test suite runs here.** `./gate.sh test` (the full suite with the 80%
  coverage gate) passed in this checkout; the counts, coverage and wall time for
  that run are in the generated
  [gate measurements](docs/_generated/gate-measurements.md) rather than copied here.
  This is one host's run, not cross-platform or release evidence.

### Retained 2026-11-11 record (superseded — history only, no action)

- **`.venv` is not usable here.** The committed environment contract is
  `uv sync --locked --extra dev` (Python 3.12, `python-version` = 3.12), but the
  local `.venv` has no third-party packages installed: `uv run --no-sync python -c
  "import pandas"` fails with `ModuleNotFoundError: No module named 'pandas'`.
  Recreate the environment with `uv sync --locked --extra dev` once network is
  available.
- **Offline dependency cache is incomplete (wheel gap).** `uv sync --locked
  --extra dev --offline` resolves the lock but then fails:
  `Failed to download pandas==3.1.0` / `Network connectivity is disabled, but the
  requested data wasn't found in the cache`. The lock pins `pandas==3.1.0` and
  `scipy==1.18.1`; the local uv cache holds only `.lock` reservation files for the
  `cp312-cp312-macosx_11_0_arm64` / `cp312-…-macosx_14_0_arm64` wheels, not the
  wheel payloads (cp313/cp314 variants are present). Populate the cache on a
  networked machine, or run on a host that can reach PyPI.
- **The test suite could not run in that checkout.** Because of the two items
  above, `uv run python -m pytest` (the command documented in `README.md`,
  `AGENTS.md`, `.aii/README.md` and `pyproject.toml`'s `addopts` with the 80%
  coverage gate) is not executable offline; documentation was validated
  statically instead. An owner with a synchronized environment should re-run the
  suite before any release.

---

## Data assets (re-checked 2026-11-12)

- [ ] **`data/prompts/` is not read by the package.** `System_Prompts.json`,
  `project.txt`, `TechTree.txt` and `raoadmap2agents.txt` are static prompt texts;
  no module in `src/`, `run.py`, `launch.py` or `scripts/` loads them (the active
  prompts are embedded inline). Decide whether to wire these assets into a workflow
  or retire them, and keep [`data/prompts/README.md`](data/prompts/README.md)
  accurate either way. Owner: maintainer. Blocked on that product decision, not on
  any external input.

---

## Drift verified 2026-11-12

- [ ] **The GNN pin is one release behind the estate cutover.**
  [`.github/gnn-pin.json`](.github/gnn-pin.json) records `v5.0.3` at
  `8f293d9ba810e6eda5c09842d9c7ed9ffa5f92c1`. Upstream tag `v5.1.0` resolves to
  `75c834bd8519dc7b5adc4d24f16bf393cfd1ecdf` (GitHub API, 2026-11-12), and the
  exemplar the arm fetches (`input/gnn_files/basics/static_perception.md`) still
  exists at that revision, so the bump is mechanical: update `revision` and `tag`,
  then run `./gate.sh gnn`, which installs into its own `.gate/gnn` environment and
  prints version, revision and result. Owner: maintainer of this repository's GNN
  adoption. Only the local arm can confirm it — hosted CI is not evidence (next
  item).
- **Hosted CI cannot be cited as evidence right now.** The organization's Actions
  minutes are billing-locked, so no `ci.yml` or `pages.yml` run in this repository
  proves anything; the local arms recorded in the
  [gate measurements](docs/_generated/gate-measurements.md) are the evidence, and
  Pages is served from the `gh-pages` branch for the same reason (see
  [`docs/organizing_publication.md`](docs/organizing_publication.md)).

---

## Completed / Closed

### 2026-11-12 — gate, release and publishing
- [x] **One gate entry point** — `gate.sh` with separately runnable arms `lint`,
  `test`, `test-fast`, `build`, `program`, `site`, `docs` and `gnn`;
  `ci.yml`/`pages.yml` call the arms instead of restating commands. ✓ `c1c2361`
  (PR #20), review follow-up `9d95d09` (PR #21)
- [x] **Generated gate measurements** — `docs/_generated/gate-measurements.md` (host,
  commit, counts, per-arm wall time) refreshed by `scripts/gate_metrics.py`. ✓
  `c1c2361`
- [x] **GNN importer pin has one executable source** — `.github/gnn-pin.json`
  (schema `gnn-importer-pin/v1`, `v5.0.3`, `8f293d9b`) with
  `scripts/gnn_conformance.py` and the `gnn-conformance` job. ✓ `b43415b` (PR #18)
- [x] **2026 presenter program v3.3.0 published** — final 55-contribution lineup,
  119 consenting participants, 19 explicit UTC sessions; book on Zenodo
  (10.5281/zenodo.24161029) with six byte-verified assets plus the GitHub `v3.3.0`
  release. ✓ `ca53d34`, merge `7ecac04` (PR #19),
  [`docs/release_3_3_0.md`](docs/release_3_3_0.md)
- [x] **Sidecar cites the v3.3.0 book DOI.** ✓ `8bf36aa` (PR #24)
- [x] **Pages served from the `gh-pages` branch while Actions is unavailable** —
  locally built, byte-verified `verify_public_tree` + `build_site` output plus
  `.nojekyll` and `* -text` so the CRLF calendar stays exact. ✓ `b3fb4c3` (PR #22)
- [x] **Participant network-figure legibility** — node IDs placed off their own
  edges, the overlap diagnostic counts only drawn text, and a regression test renders
  three network shapes. ✓ `70f54f1`, merge `9cedd72` (PR #23)

Items resolved during the 2026-08-01 hostile red-team pass.

### Source fixes
- [x] **ZeroDivisionError when no participants** — `src/symposium/analysis/participants.py`
  `analyze_all_participants` crashed on the final summary log line (÷ total_participants)
  when the CSV yielded 0 shareable participants. Guarded the average-time computation.
- [x] **t-SNE temp PCA crash on small datasets** — `src/symposium/visualization/embeddings.py`
  the t-SNE branch sized its pre-PCA with `min(100, n_features-1)`, ignoring `n_samples`, so
  small datasets (n_samples < n_features) raised and returned `None`. Now capped by
  `max_components = min(n_samples, n_features)`.
- [x] **`load_dotenv()` parent-directory walk** — `src/symposium/core/config.py` (and the same
  pattern in `run.py`) used `load_dotenv()` which searches up the tree and silently loaded an
  unrelated `.env` from a parent directory (src of non-determinism and cross-project secret
  leakage). Restricted to the project-local `<project>/ .env`.
- [x] **API-client swap not restored on exception** — `src/symposium/analysis/participants.py`
  temporarily swapped `self.api_client` to a Perplexity client for background research but did
  not restore it on failure, leaking the wrong client to later participants. Wrapped in
  `try/finally`.
- [x] **Dead, unimportable module removed** — deleted
  `src/symposium/visualization/legacy_visualization_methods.py` (428 lines; no importers in
  `src/`, `tests/`, or docs; 0% coverage; failed to import due to a `regex`/`re` shadowing).

### Test fixes
- [x] **OpenRouter 402 tests used removed `APIStatusError(request=...)` kwarg** —
  `tests/test_core/test_api.py` (4 tests) broke under openai 2.x (its `APIStatusError.__init__`
  no longer accepts `request`). Rewrote to build real `httpx.Response` objs and the new
  signature.
- [x] **`test_create_without_api_key` env-dependent** — `tests/test_core/test_api.py` failed when
  the ambient environment (incl. a picked-up `.env`) set `PERPLEXITY_API_KEY`. Now hermetic via
  `monkeypatch.delenv`.
- [x] **`test_load_from_file` env-dependent assertion** — `tests/test_core/test_config.py`
  asserted env-var precedence relying on ambient env. Made deterministic with
  `monkeypatch.setenv("API_PROVIDER", ...)`.
- [x] **Demo script collected as pytest module** — `tests/test_participant_pipeline.py` is a
  standalone demo script (run via `python tests/test_participant_pipeline.py`) whose
  `test_*(participants)` functions pytest misread as fixture-referencing, causing 3 collection
  errors. Excluded via `collect_ignore` in `tests/conftest.py` (the `tests/.pytestignore` file,
  which pytest does not read, was non-functional).
- [x] **Real-API integration skip-key mismatch** — `tests/test_integration/test_workflows.py`
  `test_real_api_presenter_analysis` / `test_real_api_profile_generation` checked for a
  `PERPLEXITY_API_KEY` but then created an **OpenRouter** client, so an ambient key caused
  them to run and fail. Now gate on `OPENROUTER_API_KEY` (the key actually used) so they skip
  cleanly in a clean environment.

### Docs
- [x] **README documented a nonexistent `--input-csv` flag** — the `visualize` CLI only supports
  `--input-dir` (a directory of Markdown), never a CSV. Replaced the misleading "From CSV
  Participant Data" examples with an accurate note and corrected `--input-dir` examples.
- [x] **`create_column_word_clouds` no-op line** — `src/symposium/visualization/embeddings.py`
  `safe_column_key = column_key.replace('_', '_')` was a no-op; removed.

### Delegation-driven follow-up fixes (same pass)

Source / CLI:
- [x] **Dead, broken `main()` removed** — `src/symposium/cli/visualize.py` had an unreachable
  `main()` (~190 lines) whose `parser.parse_args()` on the full argv always `SystemExit`'d;
  dispatch lives in `symposium.cli:main`. Removed it and the now-unused `argparse`/
  `setup_logging` imports.
- [x] **False "components for X% variance" annotation** — `visualization/pca_analysis.py`
  `np.argmax` of an all-`False` array returned `1`, annotating an unattained 80%/90% threshold.
  Now annotated only when the threshold is actually reached.
- [x] **Silently-zeroed 95% CIs on single-document input** — `visualization/distributions.py`
  `stats.t.interval(..., n_docs-1)` yields NaN for 1 doc and `nan_to_num(0.0)` erased the error
  bars. Now requires `n_docs >= 2` (else plots means without CI + warning); also fixed the
  lopsided error bar to use asymmetric `(lower, upper)` limbs.
- [x] **Non-deterministic network layouts** — `visualization/networks.py` `spring_layout` /
  `random_layout` ran with no seed; now seeded from a `random_state` (default 42).
- [x] **Mislabelled embedding filenames** — `cli/visualize.py` named files by the requested
  component count instead of the dimensions actually plotted; fixed.
- [x] **Inconsistent single-file handling** — `visualize_networks`/`visualize_distributions`
  now accept a single Markdown file like `visualize_embeddings`.
- [x] **CLI `--method` restricted to 3 of 7 supported methods** — `cli/__init__.py` now exposes
  all 7 reducer methods (pca/lsa/tsne/umap/isomap/nmf/lda), matching the documented capability.

Scripts:
- [x] **run.py share-count regex over-counted** — `.contains('yes|true|y')` matched any cell
  containing "y"; now anchored `^(yes|true|y)$` with `fillna('')`.
- [x] **run.py unhandled `int(input())`** — participant selection now validates numeric + range.
- [x] **run.py `None` preview guard** — `(background or '')[:300]` / `(curriculum or '')[:300]`.
- [x] **run.py log path CWD-coupled** — `symposium.log` handler now anchored to the script dir.
- [x] **config.example.json model drift** — unified OpenRouter model to
  `anthropic/claude-3.5-sonnet`.
- [x] **setup.py dead shell=True `run_command`** — removed (plus now-unused `subprocess` import).

Tests:
- [x] **Failure→skip masking** — `test_csv_visualization.test_distribution_analysis_setup`
  swallowed the underlying failure via `try/except → skipTest`; now genuinely asserts the plot
  is produced (the fragile pyplot mocking was the real cause).
- [x] **Dead unconditional-skip test** — deleted `test_wordclouds_command` (always skipped,
  asserted nothing).
- [x] **Non-hermetic source-tree writes** — `test_csv_visualization` wrote test CSVs/output
  into `tests/test_visualization/`; now uses `tempfile.TemporaryDirectory`.
- [x] **Tautological edge-count assert** — `len(graph.edges()) >= 0` → asserts edges actually
  exist.
- [x] **Unasserted `success`** — `test_advanced_embedding_methods` now asserts success.
- [x] **Env-dependent + destructive config tests** — `test_config` `test_load_real_configuration`
  no longer `mkdir`s into the project; `test_get_api_key_from_environment` now injects + asserts
  an exact env key instead of a tautological isinstance check.
- [x] **Over-broad exception assertion** — `test_2025_participants.test_analyze_with_api_error`
  now asserts a specific `RuntimeError` propagates.
- [x] **Brittle tolerance** — `0.3 < response_rate < 0.4` → `pytest.approx(1/3)`.

Docs:
- [x] **MIGRATION.md referenced nonexistent `scripts/`** — corrected both the "Run Migration
  Scripts" and "Automatic Compatibility" sections to state no automated scripts ship and
  describe the manual CLI path.

### Completion pass — deferred Majors (M1/M2/M3)
- [x] **M1 — test coverage uplift:** added real tests for CLI dispatch (all 10 subcommands),
  `analyze`/`generate` handler bodies, `PCAAnalyzer` report generation, `DistributionPlotter`
  paths, and the `visualize` command bodies producing files on disk. Converted the dead
  `test_pca_visualizations.py` demo into real tests. Overall coverage rose ~48% → ~84% and a
  `--cov-fail-under=80` regression gate was added.
- [x] **Major plotting bug found & fixed:** `plt.cm.get_cmap` (removed in matplotlib ≥3.9) and
  `Axes.boxplot(labels=...)` (renamed to `tick_labels`) broke every 2D/3D plot; replaced with
  `matplotlib.colormaps[...]` / `tick_labels=` across `embeddings.py`, `networks.py`,
  `pca_analysis.py`, `distributions.py`.
- [x] **M2 — `run.py` orchestration:** `create_visualizations` now calls the visualization
  functions in-process instead of shelling out to the `symposium` console script; run.py
  hardened (anchored share regex, guarded input, `None`-safe previews, CWD-independent log).
- [x] **M3 — launch/setup:** `launch.py` no longer runs the deprecated `setup.py` (validates
  the installed package in-process); `symposium.sh` already installs via `uv`.
- [x] **Docs/release:** added `CHANGELOG.md`, bumped version to 2.1.0, final README accuracy
  pass.

### Improvement / refactoring pass (post-2.1.0)
- [x] **Ruff-only tooling + lint cleanup:** removed `black` (dev dep + `[tool.black]`) in favor
  of `ruff format`; whole `src/` + `tests/` reformatted and `ruff check` clean (0 errors).
  Removed further dead code/unused imports and renamed ambiguous `l`/`G` names.
- [x] **R3 — real-API opt-in marker** — live-LLM tests are gated behind the `real_api`
  marker registered in `pyproject.toml`; run them with `-m real_api` (keys required).
- [x] **Coverage ~86%:** added tests for `io/readers`, `cli/analyze` (backgrounds/curricula),
  `cli/generate`, and `core/config` (set/save/ensure_paths/get_path).

---

## Major — Scoped (deferred)

The three originally-deferred Majors (M1 coverage, M2 run.py orchestration, M3 launch/setup)
were substantially addressed in the 2026-08-01 completion pass (see Completed/Closed below).
What remains below are the residual / aspirational follow-ups not fully closed.

### R1 — Push coverage from 89.76% to the documented >90% target
- **Status:** the full arm recorded 776 passed, 9 skipped and 89.76% coverage at `b43415b`
  ([gate measurements](docs/_generated/gate-measurements.md)); the regression gate in
  `pyproject.toml` is still `--cov-fail-under=80`. The per-module figures (~74%
  `cli/analyze.py` etc.) predate the coverage uplift and are not reproduced by any current
  record, so they are no longer restated here.
- **Suggested fix:** add the remaining edge-case tests (error paths, empty inputs) to climb
  above 90%, then raise `--cov-fail-under` to match. Owner: maintainer; no external blocker,
  only unmeasured headroom.

### R2 — Consolidate the `APIClient.create` wiring that now lives in the CLI
- **Status:** the menu duplication is gone — every `run.py` operation delegates to
  `SymposiumRunner.create_api_client` / `load_config` (`run.py:44-56`). The same
  `Config(...)` + `APIClient.create(...)` construction (provider plus
  `get_api_config`/`get_api_key`) is now repeated six times:
  `src/symposium/cli/analyze.py:40,75,118,153` and `src/symposium/cli/generate.py:19,56`.
- **Suggested fix:** one helper (on `Config`, or a small factory beside `APIClient.create`)
  that both the CLI commands and `run.py` call, so provider/key handling cannot drift between
  the two entry points. Owner: maintainer.

---

## Docs-deep pass — 2026-08-02

Documentation-focused review pass. Severity definitions: **Minor** = typo, broken link,
stale tooling reference, formatting; **Medium** = stale section rewrite, doc restructure,
added missing guide; **Major** = large doc-system overhaul / cross-cutting refactors.
Findings were verified against the code before editing (see `REVIEW_LOG_2026-08-02.md`).
All items below were implemented in this pass (commits `669643f`, `98ae63d`, `a6d171e`,
`82ea73a`).

### Minor
- [x] **M-01 `black` references in docs** — README.md (tooling bullet + Development
  section), docs/installation.md, docs/development.md, docs/contributing.md still
  documented `black`; black was removed in the ruff-only tooling pass. Replaced with
  `ruff format` / `ruff format --check`. ✓ `a6d171e`
- [x] **M-02 README "outputs/ (gitignored)" claim** — `outputs/` is tracked in git
  (532 files incl. `outputs/2025_symposium/people/` reports). Structure block now says
  "example outputs tracked". ✓ `98ae63d`
- [x] **M-03 README project-structure block** — now lists `data/catechisms/`,
  `data/templates/`, marks `data/domains/` as user-provided, and shows `run.py` /
  `launch.py` / `setup.py` / `symposium.sh`. ✓ `98ae63d`
- [x] **M-04 README coverage claim** — ">80%" → ~86% with the `--cov-fail-under=80`
  gate; `real_api` opt-in marker documented in Development/Running Tests. ✓ `98ae63d`
- [x] **M-05 README "auto-install" claim** — corrected: `symposium.sh` performs the uv
  install; `python run.py` runs the interface directly. ✓ `98ae63d`
- [x] **M-06 README citation year** — bibtex `year = 2024` → 2025 (matches LICENSE
  copyright and the 2025-symposium edition); added `CITATION.cff`. ✓ `98ae63d`
- [x] **M-07 data/README.md stale bits** — `data/participants_2024.csv` (nonexistent)
  example fixed, stale `llama-3.1-sonar-large-128k-online` → `sonar`, `templates/`
  added to structure, `domains/` marked user-provided. ✓ `a6d171e`
- [x] **M-08 API_USAGE.md participant count** — "Load 47 participants" → 93 (current
  CSV has 93 shareable rows; verified); cost estimates recomputed and labelled
  illustrative. ✓ `a6d171e`
- [x] **M-09 API_USAGE.md config source** — corrected "in pyproject.toml" →
  `src/symposium/core/config.py`; added `retry_delay` default. ✓ `a6d171e`
- [x] **M-10 PERPLEXITY_RESEARCH.md fixture names** — snippet now uses real conftest
  fixtures (`mock_api_client`, `sample_participant_csv_file`, `temp_dir`) and is a
  self-contained example. ✓ `a6d171e`
- [x] **M-11 AGENTS.md header** — "Last Updated: 2026-08-02 / Version 2.1"; coverage
  goals annotated with the actual gate. ✓ `98ae63d`
- [x] **M-12 README Tests badge** — was pointing at a nonexistent workflow; CI added
  (G-03), badge now matches `.github/workflows/ci.yml` (workflow `Tests`). ✓ `82ea73a`

### Medium
- [x] **D-01 Stale model names across docs** — `llama-3.1-sonar-large-128k-online` /
  `google/gemini-pro-1.5-exp` replaced with `sonar` / `anthropic/claude-3.5-sonnet`
  (core/api.py defaults) in api_guide.md, user_guide.md, migration.md, data/README.md,
  and the tests/conftest.py sample-config fixture. ✓ `a6d171e`
- [x] **D-02 user_guide.md `--registration-file`** — nonexistent flag replaced with
  `--csv-file`; examples point at the real participant CSV; `--domain-file` removed
  from `analyze participants` examples (not a flag on that subcommand). ✓ `a6d171e`
- [x] **D-03 csv_visualization_guide.md rewrite** — removed the nonexistent CLI
  (`visualize wordclouds --input-csv`, `--input-csv` on embeddings/all) and the
  fictitious "Choose input type: CSV" prompt. Rewritten against real behavior:
  per-column word clouds via `run.py` option 3 (`wordcloud_<column>.png` +
  `column_summary_*.md`), plots via `symposium visualize … --input-dir` (Markdown) /
  `run.py` option 6; every command and output filename verified against the code. ✓ `82ea73a`
- [x] **D-04 docs/ naming convention split** — 4 UPPERCASE filenames renamed to
  lowercase (`git mv`), all links updated. ✓ `669643f`
- [x] **D-05 Missing docs index + cross-links** — added `docs/README.md`; README
  "Documentation" section now lists all guides (installation, user guide, API guide,
  API usage, CSV visualization, Perplexity research, architecture, development,
  migration, UV setup, agents). ✓ `669643f` + `98ae63d`
- [x] **D-06 CI claims vs reality** — added `.github/workflows/ci.yml`; development.md
  CI section rewritten to describe the actual workflow; contributing.md CI-checks
  section added; UV_SETUP.md CI example synced. ✓ `82ea73a` + `a6d171e`
- [x] **D-07 api_guide.md `tenacity` example** — replaced with a `backoff`-based retry
  snippet (backoff is the package's actual retry dependency). ✓ `a6d171e`
- [x] **D-08 api_guide.md custom-provider wording** — "Register in APIClient.create()"
  corrected to the actual extension path (instantiate the subclass directly).
  ✓ `a6d171e`
- [x] **D-09 Add `data/domains/README.md`** — documents that domain files are
  user-provided, how `--domain-file` consumes them, and how to create one;
  `config.example.json` gained `domains_dir`. ✓ `a6d171e`

### Major
- [x] **G-01 Docs-corpus accuracy overhaul** — aggregated Minor/Medium fixes applied
  across all docs/ files + README + data/README.md + module READMEs (cli/README
  `--csv-file`, PCA_GUIDE.md links) + CHANGELOG; every claim re-verified against code;
  automated relative-link check now passes with 0 broken links. ✓ all four commits
- [x] **G-02 CSV-visualization guide restructure** — the largest single-doc rewrite
  (D-03): CLI examples, output inventory, and interactive flow all corrected and
  verified. ✓ `82ea73a`
- [x] **G-03 Add GitHub Actions CI** — `.github/workflows/ci.yml` (setup-uv, install
  `.[dev]`, `ruff check`, `ruff format --check`, `uv run python -m pytest` with the
  coverage gate). Local baseline verified first: 188 passed, 8 skipped (real_api
  opt-ins), 86.26% coverage. mypy is intentionally **not** in CI — it is not green in
  the local env (missing seaborn/sklearn stubs + numpy stub syntax on Python 3.14).
  ✓ `82ea73a`

### Open / deferred
- None from this pass. (Pre-existing R1/R2 residuals in the Major section above
  remain open; R3 is done.)
- [ ] **Mypy is still far from clean** (re-measured 2026-11-12):
  `uv run --no-sync mypy src/symposium` reports **89 errors in 26 files**. Most are
  missing third-party stubs (`pandas-stubs`, `types-networkx`, and no `py.typed` for
  `sklearn.feature_extraction.text`), which `mypy --install-types` or dev-dependency
  additions would settle. The rest are real annotations, e.g.
  `src/symposium/core/api.py:108` (a `str | None` returned as `str`),
  `src/symposium/core/__init__.py:40` (a `str | Path` passed to a `Path` parameter)
  and `src/symposium/generation/profiles.py:157` (unannotated `results`). Add
  `mypy src/symposium` to the `lint` arm only after it passes. Owner: maintainer.
- Heavy suites (Julia/LaTeX) do not apply — this is a Python repo; the current full
  suite result is the generated gate measurement (776 passed, 9 skipped, 89.76%,
  gate 80%), not the 188-test figure from this pass.

---

## Notes / process
- No pre-existing TODO/TODO.md/TO-DO.md file existed in the repo before this pass; this file was
  created to serve as the authoritative backlog, following the documented header convention.
- **Mock policy clarification:** the repo's own conventions (AGENTS.md "Development rules":
  "Mocking is expected where it keeps tests deterministic", `tests/AGENTS.md` "Mock Data
  Agent", `conftest.py`) explicitly endorse mocking.
  A delegation reviewer flagged the `mock_api_client` fixture as violating a claimed "no-mock"
  policy; that policy is **not** part of this repo, so the mock infrastructure was intentionally
  left in place (an unmatched drive-by "fix" would have contradicted the repo).
- **`test_pca_visualizations.py` is no longer a demo.** It now collects 10 `PCAAnalyzer` tests
  that write into `tmp_path` (checked 2026-11-12); the earlier "0 tests collected, writes
  `test_pca_output/`" note described the pre-uplift file and has been removed.
- Real-API tests (`TestRealAPIWorkflows`, `TestRealAPIIntegration`) skip when keys are absent
  and are gated behind the `real_api` marker; no opt-in work remains outstanding (R3).
