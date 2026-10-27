# uv setup for Symposium

The project uses a committed `uv.lock` and a Python 3.12 development pin. Current
package support starts at Python 3.12. See [installation](docs/installation.md) for
platform boundaries and the separate Template renderer environment.

```bash
uv sync --locked --extra dev --python 3.12
uv run --no-sync symposium --help
uv run --no-sync python -c 'import sys; print(sys.prefix); print(sys.base_prefix)'
uv run --no-sync python -m pytest
```

Run from the checkout. No activation or bare `pytest` invocation is needed.
`uv sync --locked` checks the committed resolution; dependency upgrades require a
reviewed lockfile change. `uv run --no-sync` uses the already synchronized environment.
If another environment is active, unset `VIRTUAL_ENV` before selecting the project
one. Do not delete an environment that another worker may be using.

In GitVault-managed work, verify the volume mount before writing. Use the repository
lease wrapper and externally bound `UV_PROJECT_ENVIRONMENT`, `UV_PYTHON`, `TMPDIR`,
`UV_CACHE_DIR`, and `UV_LINK_MODE=copy` as required by local instructions. Both Python
prefixes must resolve on GitVault. A symlinked `.venv` alone is insufficient evidence.

For the interactive research menu: `uv run --no-sync python run.py --year 2026`.
Some menu actions invoke paid providers. Setup, CLI help and public-tree checks do
not. Configure keys only when that analysis is authorized; see the
[API guide](docs/api_guide.md). Never print `.env` contents for troubleshooting.
