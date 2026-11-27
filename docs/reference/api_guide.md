# Provider API and configuration

The public organizer workflow requires no LLM API. The optional research workflows
use `APIClient.from_config(config, provider=None, api_key=None, **kwargs)` from
[`core.api`](../../src/symposium/core/api.py). `APIClient.create` remains the direct
factory for callers supplying provider settings themselves. Supported identifiers are
`perplexity` and `openrouter`; returned providers expose
`get_response(prompt, system_prompt=None, **kwargs)`. Calling that method can incur
charges and sends its supplied content to the provider.

For a workflow-specific key checklist and offline capability inspection, see
[credentials](credentials.md). The static methods and publication surfaces require no
provider account. `organize capabilities --check-env` checks process-environment presence
only; it does not load dotenv files, authenticate, check permissions or spend credits.

## Configuration contract

`Config` in [`core.config`](../../src/symposium/core/config.py) loads defaults, an
explicit JSON file, then supported environment values. It loads `.env` only from
the current directory. CLI JSON selection precedes the command:

```bash
uv run symposium --config config.json analyze participants --help
```

An explicitly selected invalid or missing JSON file is an error during execution.
Use [config.example.json](../../config.example.json) as a starting point, keeping
credentials in private environment configuration. Supported environment overrides
include `PERPLEXITY_API_KEY`, `OPENROUTER_API_KEY`, `API_PROVIDER`, `SYMPOSIUM_YEAR`,
`SYMPOSIUM_DATA_DIR`, `SYMPOSIUM_OUTPUTS_DIR`, and `LOG_LEVEL`.
`PERPLEXITY_MODEL` and `OPENROUTER_MODEL` are not Config overrides; set provider
models in JSON or pass them directly to the Python factory.

The source defaults are `sonar` and `anthropic/claude-3.5-sonnet`, temperature 0.7
and 2,000 output tokens. These are software defaults, not a recommendation or a
verification of current provider availability, pricing, context capacity or quality.
Inspect provider terms and availability before authorizing a run.

Offline configuration inspection, without printing secrets:

```python
from symposium.core.config import Config

config = Config(load_env=False)
print(config.get("edition.year"))
print(config.get("api.provider"))
```

`load_env=False` skips the dotenv file; it does not disable existing environment
overrides. Construct a configured provider without duplicating that resolution:

```python
from symposium.core.api import APIClient
from symposium.core.config import Config

client = APIClient.from_config(Config(config_file="config.json"))
```

An explicit `provider` selects the provider; an explicit non-`None` `api_key` and
keyword options override resolved settings. The factory copies provider options,
removes their credential entry, and rejects a conflicting `provider` option rather
than allowing it to override selection. CLI handlers and the interactive runner use
this boundary. Participant background research explicitly selects Perplexity,
including combined background/curriculum workflows.

`get_api_config(provider)` requires an object with string keys.
`get_api_key(provider)` accepts strings or null; malformed values raise a
field-identifying `ValueError` without disclosing their contents. Empty/null keys
retain the existing lookup precedence. Malformed legacy key files retain the
warning-and-`None` behavior. Never dump complete configuration or credentials.

JSON report/data readers require an object at the top level; arrays, null and scalar
roots raise `ValueError`. Participant loaders return the existing
`dict[str, Participant]` schema, including integer `row_index`, without copying the
records. Read-only participant helpers accept `Mapping[str, object]`.

## Errors and limits

Both providers map HTTP 402 to `PaymentRequiredError`. OpenRouter treats that
exception as terminal before inspecting retry text, including messages containing
`rate` or `timeout`. Other matching errors retain the application retry bound of
five attempts and 300 seconds. Stored `max_retries` and `retry_delay` do not change
those decorator bounds. Perplexity has no equivalent application backoff wrapper;
underlying SDK behavior is separate. There is no automatic provider failover.

Presenter, profile and project batch mappings contain only records whose requested
reports were fully persisted. Nonpayment failures are accumulated while other
eligible records are attempted, then raise `BatchIncompleteError` with `requested`,
`completed`, `failures` and `output_dir` evidence. Payment failure stops immediately.
Completed and partial files remain on disk; partial records are not successes.
Affected CLI requests fail for incomplete or empty work rather than reporting
completion.

Token estimates and truncation are local heuristics, not proof that a provider's
context constraints are met. Returned prose and citations are unverified model
output. Review sources, identity matching, privacy and factual claims before use;
never automatically publish the outputs. See [research methods](../architecture/methods.md).
