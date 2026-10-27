# Development

Read the repository and relevant module `AGENTS.md` before changing code. Preserve
unrelated work and historical datasets. Current package support begins at Python
3.12; use the 3.12 development pin and committed lockfile. The separate native
Template renderer retains its own Python 3.14 environment.

```bash
uv sync --locked --extra dev --python 3.12
uv run --no-sync ruff check src/ tests/ run.py launch.py
uv run --no-sync ruff format --check src/ tests/ run.py launch.py
uv run --no-sync python -m pytest
uv build
```

The pytest configuration in [pyproject.toml](../pyproject.toml) enables coverage
and an 80% gate; this is a configured threshold, not a claimed current score.
[CI](../.github/workflows/ci.yml) configures Python 3.12, 3.13 and 3.14;
a matrix entry is not evidence of a successful remote run. Live-provider tests are
opt-in through `--run-real-api -m real_api` and require authorization and credentials. Default
checks must not require paid requests.

## Making a change

Reproduce a defect before fixing it. Add a regression scenario that fails for the
old behavior, including malformed input and error paths where relevant. Prefer
real temporary files and local transports for boundary checks. Use fixed seeds for
numerical examples. Do not replace runtime or visual evidence with a passing static
check. For a focused test run that is intentionally too narrow for global coverage,
use `uv run --no-sync python -m pytest --no-cov tests/TEST_FILE.py`, substituting an
existing test file; run the full gate before claiming repository-wide health.

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
