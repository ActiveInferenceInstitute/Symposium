# Development

Read the repository and relevant module `AGENTS.md` before changing code. Preserve
unrelated work and historical datasets. Current package support begins at Python
3.12; use the 3.12 development pin and committed lockfile. The separate native
Template renderer retains its own Python 3.14 environment.

```bash
uv sync --locked --extra dev --python 3.12
./gate.sh              # default arm: test-fast
./gate.sh all          # every arm
```

## The gate

[`gate.sh`](../gate.sh) is the single entry point. Each arm is one documented
command, and the workflow jobs run `./gate.sh <arm>` instead of restating the
command, so a local run and CI cannot drift. Environment setup (`uv sync --locked
--extra dev`) is the caller's job: every project `uv run` invocation uses
`--no-sync`, while `build` runs `uv build` and `gnn` creates its own isolated
environment. `test-fast` is local-only; CI runs `test`.

| Arm | What it runs |
| --- | --- |
| `lint` | `ruff check` and `ruff format --check` over `src/ tests/ scripts/ run.py launch.py` |
| `test` | `python -m pytest --no-header`: full suite with the pyproject coverage gate |
| `test-fast` | `python -m pytest --no-header -q --no-cov -m "not real_api"` over the package-module suites (`tests/test_core`, `test_io`, `test_cli`, `test_analysis`, `test_generation`, `test_calendar`): the default arm, and not a substitute for `test` |
| `build` | `uv build` (sdist and wheel) |
| `program` | CLI version, edition scaffold validation, approved public tree, readiness, site render into a temporary directory |
| `site` | `symposium organize site` into `$GATE_SITE_OUT`, or a fresh temporary directory when unset; an existing path is refused (the Pages workflow sets `_site`) |
| `docs` | [`scripts/check_docs.py`](../scripts/check_docs.py): relative links, docs index completeness, gate-arm list |
| `gnn` | pinned GNN parser in an isolated `.gate/gnn` environment; [`scripts/gnn_conformance.py`](../scripts/gnn_conformance.py) verifies it against `.github/gnn-pin.json` |

`./gate.sh` with no arm runs `test-fast`: the six package-module suites without
coverage instrumentation, the quickest signal that the package still imports and
behaves. It does not run the organizer publication, visualization, edition or
subprocess workflow suites, so passing it is not repository-wide health — `test`
is the gate. `./gate.sh list` prints the arms; `./gate.sh all` runs them in that
order. Wall times for each arm on the machine that last refreshed it are generated
in [gate measurements](_generated/gate-measurements.md) — a single run, not a
benchmark. Refresh with `uv run --no-sync python scripts/gate_metrics.py refresh`;
`--only` re-measures named arms and refuses once HEAD moved, and `redraw`
re-renders the prose without measuring.

There is no types arm. `pyproject.toml` configures mypy and the dev extra ships it,
but it has not joined a gate. The 2026-11-12 observation was 89 errors in 26 files.
On 2026-11-13, source repairs and separately provisioned third-party stubs reduced
the first post-stub diagnostic run to 27 errors in seven files, checking all 51
package modules. That run still had missing `adjustText`/`wordcloud` typing and
incompatible sparse/community declarations; it did not establish a passing check.
That repository-specific diagnostic environment preserved all 64 existing
dependency versions and is not a new locked development requirement.
Add mypy to lint only after complete, reproducible qualification.

`python scripts/check_types.py` checks the complete package using the existing
mypy rules. It requires the exact diagnostic dependency versions recorded in
`typings/bindings.json`; it never installs packages or changes runtime versions.
Local `adjustText` and `wordcloud` declarations describe only the consumed APIs.
The word-cloud renderer passes the real `to_array()` result to Matplotlib rather
than pretending that WordCloud implements NumPy's dtype-taking array protocol.

Upstream declaration corrections are generated in a temporary directory and
passed through mypy's `--shadow-file`: CSR array/matrix vectorizer results,
sparse-array consumer inputs and NetworkX mutable/frozen community sets.
Installed package files remain unchanged.
Both package versions and exact upstream declaration hashes must match; a mismatch
requires new API review and qualification, not automatic rebinding. Temporary
projections preserve the installed declarations and license text outside these
narrow corrections. This diagnostic is not a new CI gate or scientific proof.

On 2026-11-15, the complete-package command reported no issues in all 51 source
files while preserving all 64 original runtime distribution versions. Real
synthetic API checks exercised both sparse interfaces through LSA, NMF and LDA,
mutable/frozen community sets, empty/nonempty label adjustment and the actual
word-cloud renderer. Wrong-version and changed-declaration controls refused
before projection. Earlier typing and formatting failures remain historical
evidence; these software checks do not approve research inputs or publication.

The coverage guard is `fail_under = 90.01` with `precision = 2`. The admitted
2026-11-13 offline suite passed 902 tests with nine paid-provider tests deselected
and measured 5,013/5,547 statements (90.37%). Its zero-precision threshold failure
remains recorded; a separate reporting-only check reused the database and passed
with the corrected precision. Do not rerun successful tests just to relabel that
historical failure or hand-edit the generated gate measurements.

## Continuous integration

[CI](../.github/workflows/ci.yml) has four jobs, each calling one or more arms:
`lint` (lint + docs, once), `test` (matrix on Python 3.12, 3.13 and 3.14), `build`
(build + program, on the 3.12 pin) and `gnn-conformance` (display name
`gnn conformance (pinned)`). Lint, the distribution build, edition validation and the
public-site render used to run inside all three matrix entries; they now run once,
and the documentation arm is new. A matrix entry is not evidence of a successful
remote run. The workflow uses the `astral-sh/setup-uv` action, SHA-pinned at v10.3.3
with uv `0.13.5`, rather than the shared `ActiveInferenceInstitute/.github`
`setup-python-uv` composite action. The pinned
GNN baseline is described in [.github/GNN.md](../.github/GNN.md). Live-provider
tests are opt-in through `--run-real-api -m real_api` and require authorization and
credentials; default checks must not require paid requests.

GitHub Actions is billing-locked org-wide here, so a local `./gate.sh all` is the
available gate. Record what you actually ran.

## Making a change

Reproduce a defect before fixing it. Add a regression scenario that fails for the
old behavior, including malformed input and error paths where relevant. Prefer
real temporary files and local transports for boundary checks. Use fixed seeds for
numerical examples. Do not replace runtime or visual evidence with a passing static
check. For a focused test run that is intentionally too narrow for global coverage,
use `uv run --no-sync python -m pytest --no-cov tests/TEST_FILE.py`, substituting an
existing test file; run `./gate.sh test` before claiming repository-wide health.

Record exact commands, exit statuses and output artifacts. Keep initial failures
beside corrected results. Avoid swallowing errors in pipelines. Review the actual
changed files and keep private source snapshots, tokens, receipts and raw answers
outside public artifacts. GitVault work requires the local lease and external
runtime/cache/temp bindings.

## Interfaces and release boundaries

CLI parsers live in `src/symposium/cli/`; implementations are in the modules listed
in [architecture](architecture.md). Verify examples through their command's
`--help` and inspect the implementation before documenting defaults or guarantees.
There is no universal `Symposium` orchestration object.

Changes to publication must exercise schema, consent, manifest, path and fresh-output
boundaries. Native PDF/DOCX changes require rendering and individual visual review.
Website changes require browser checks including keyboard, narrow layout, dark
mode, no-JavaScript content, and download integrity. See [methods](methods.md).

For releases, reconcile package/version metadata, lockfile, changelog, wheel and
source distribution contents; test an installed artifact outside the checkout.
Do not put private organizer content into distributions. Publishing a package,
pushing a tag or deploying a website is a separate authorized action. Preserve
[historical release evidence](release_2_2_0.md) as historical evidence.
