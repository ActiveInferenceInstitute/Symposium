# Symposium TODO / Backlog

**Status:** Ongoing
**Owner:** Active Inference Institute
**Last reviewed:** 2026-08-01

This is the authoritative project backlog for the Symposium package. It is updated by
hostile red-team review passes: every validated Minor/Medium finding is implemented in a
pass and moved to **Completed/Closed**; validated Major findings that require structural
work are scoped under **Major — Scoped (deferred)** and deliberately left unimplemented.

---

## Completed / Closed

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

---

## Major — Scoped (deferred)

The three originally-deferred Majors (M1 coverage, M2 run.py orchestration, M3 launch/setup)
were substantially addressed in the 2026-08-01 completion pass (see Completed/Closed below).
What remains below are the residual / aspirational follow-ups not fully closed.

### R1 — Push coverage from ~84% to the documented >90% target
- **Status:** overall coverage rose from ~48% → ~84% this pass; a `--cov-fail-under=80`
  regression gate is now in place. The remaining gap to the documented >90% target is mostly
  `cli/analyze.py` (18%) / `cli/generate.py` (25%) bodies and `io/readers.py` (48%).
- **Suggested fix:** continue adding API-boundary-mocked handler tests and reader edge cases
  to climb above 90%; then raise `--cov-fail-under` to match.

### R2 — Full consolidation of the `run.py` interactive menu into the package
- **Status:** the subprocess shell-out to the console script was removed (calls package
  functions in-process) and `run.py` was hardened; duplicated config/API-client wiring across
  the menu methods remains.
- **Suggested fix:** extract the remaining duplicated config/client/path wiring into the
  `symposium.cli` / `symposium.*` public surface and have the menu methods delegate to it.

### R3 — Real-API tests opt-in marker
- **Status:** real-API tests skip cleanly when keys are absent; they still run (and cost LLM
  calls) when keys are present.
- **Suggested fix:** gate `TestRealAPIWorkflows` / `TestRealAPIIntegration` behind an explicit
  marker (e.g. `-m real_api`) so routine runs never spend unexpectedly.

---

## Notes / process
- No pre-existing TODO/TODO.md/TO-DO.md file existed in the repo before this pass; this file was
  created to serve as the authoritative backlog, following the documented header convention.
- **Mock policy clarification:** the repo's own conventions (.cursorrules "Mocking: Realistic
  test data…", `tests/AGENTS.md` "Mock Data Agent", `conftest.py`) explicitly endorse mocking.
  A delegation reviewer flagged the `mock_api_client` fixture as violating a claimed "no-mock"
  policy; that policy is **not** part of this repo, so the mock infrastructure was intentionally
  left in place (an unmatched drive-by "fix" would have contradicted the repo).
- **Dead non-test demo:** `tests/test_visualization/test_pca_visualizations.py` is a standalone
  demo (0 tests collected by pytest, writes `test_pca_output/` when run directly). Left as-is to
  avoid deleting a runnable example; a follow-up should either add real `PCAAnalyzer` asserts or
  move it to an `examples/` dir.
- Real-API tests (`TestRealAPIWorkflows`, `TestRealAPIIntegration`) are intentional live-LLM
  checks and skip when keys are absent; a dedicated opt-in marker to prevent surprise spend when
  keys are present is a follow-up consideration (tracked under M1's test-architecture cleanup).
