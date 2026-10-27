# Test suite

Use Python 3.12+ and the committed uv lock. The development pin is 3.12.

```bash
uv sync --locked --extra dev --python 3.12
uv run --no-sync python -m pytest
uv run --no-sync ruff check src/ tests/ run.py launch.py
uv run --no-sync ruff format --check src/ tests/ run.py launch.py
```

The pytest configuration enables line coverage, terminal/HTML reports and an 80%
regression gate. These settings do not establish complete coverage or scientific,
visual, native-render or deployment correctness. Inspect the actual result and
retained failures for the revision being tested.

## Focused checks

```bash
uv run --no-sync python -m pytest --no-cov tests/test_core/
uv run --no-sync python -m pytest --no-cov tests/test_organizing_review.py tests/test_organizing_site.py
uv run --no-sync python -m pytest --no-cov tests/test_real_api_opt_in.py
```

A focused run intentionally disables the repository-wide coverage threshold; run
the full gate before claiming repository-wide health. Tests cover core/config/data,
analysis, generation, CLI, I/O, calendars, visualization, edition inputs and organizer
publication. Organizer scenarios exercise real files, local subprocess/transport
fixtures, explicit consent, missing content, path escapes, manifests, tampering and
exclusive private outputs. Some legacy research tests use mocked providers.

`test_participant_pipeline.py` is an excluded standalone demonstration, not a pytest
module. See `conftest.py` for fixtures and collection policy. Do not run historical
participant data through paid providers as a test shortcut.

## Live providers require explicit opt-in

Default runs skip tests marked `real_api`, even when provider credentials are set.
Marker selection alone does not enable them. Only after authorizing provider
transmission and charges, supply credentials privately and explicitly enable:

```bash
uv run --no-sync python -m pytest --run-real-api -m real_api
```

Missing credentials can still cause a live test to skip. Passing mocked or local
transport tests does not verify live authentication, credit balance, provider
availability or scientific accuracy. Never commit credentials or private registration
answers into fixtures or test reports.

## CI and evidence

[CI](../.github/workflows/ci.yml) configures Ubuntu jobs on Python 3.12, 3.13 and
3.14. It runs lint, formatting, the test/coverage gate, distribution building, edition
validation and actual approved-public-tree verification/site rendering. This is not
cross-platform CI; macOS checks require separate evidence, and Windows is not
established by this matrix.

For GitVault work, keep runtimes, environments, temporary files, caches and retained
artifacts on the mounted volume and use the local lease policy. Follow
[development](../docs/development.md) and [methods](../docs/methods.md) for command,
privacy, rendering and interpretation boundaries.
