# Installation

Use Python 3.12 or newer; the development pin is 3.12. Python 3.10 and 3.11 are
outside the current package requirement. Native abstract-book rendering is a
separate Template workflow with its own Python 3.14 environment.

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run
these commands from the Symposium checkout:

```bash
uv sync --locked --python 3.12
uv run --no-sync symposium --version
uv run --no-sync symposium --help
uv run --no-sync symposium organize check-public --public-dir data/public/2026
uv run --no-sync symposium edition validate --year 2026
```

The public-tree check verifies the approved publication snapshot. Edition validation
checks the separate research-input scaffold, which may be empty. Neither command
requires a provider key or makes a paid LLM request. A successful CLI help command
only establishes that the entry point loads.

For development dependencies use `uv sync --locked --extra dev --python 3.12`.
Activation is optional: `uv run` selects the project environment. Use `--no-sync`
after synchronization when commands must not change dependencies.

The edition initializer's no-overwrite filesystem operations support macOS and
Linux. Do not infer Windows support for that workflow from Python compatibility.
For this GitVault-managed workspace, keep interpreters, environments, temporary
files and caches on the mounted external volume and follow the local lease policy.
Verify both `sys.prefix` and `sys.base_prefix` before running source workflows.

## Optional provider configuration

Public verification, projection, dossiers, participant briefs, calendar export,
and website building do not need LLM credentials. For explicitly authorized paid
analysis, create a private `.env` based on [.env.example](../.env.example) and
configuration based on [config.example.json](../config.example.json). Preserve an
existing file rather than replacing credentials with a template. Select JSON with
`uv run symposium --config config.json ...`. See [API configuration](api_guide.md).

If imports fail, verify the working directory and rerun locked synchronization.
If the lock is incompatible, report that error rather than silently replacing the
lock. If a paid provider fails, retain the actual error and partial outputs; client
construction does not verify authentication, model availability, or credit balance.

Continue with [organizer publishing](organizing_publication.md),
[2026 inputs](2026_setup.md), or [development](development.md).
