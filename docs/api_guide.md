# Provider API and configuration

The public organizer workflow requires no LLM API. The optional research workflows
use `APIClient.create(provider, api_key=None, **kwargs)` from
[`core.api`](../src/symposium/core/api.py). Supported provider identifiers are
`perplexity` and `openrouter`; returned providers expose
`get_response(prompt, system_prompt=None, **kwargs)`. Calling that method can incur
charges and sends its supplied content to the provider.

## Configuration contract

`Config` in [`core.config`](../src/symposium/core/config.py) loads defaults, an
explicit JSON file, then supported environment values. It loads `.env` only from
the current directory. CLI JSON selection precedes the command:

```bash
uv run symposium --config config.json analyze participants --help
```

An explicitly selected invalid or missing JSON file is an error during execution.
Use [config.example.json](../config.example.json) as a starting point, keeping
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
overrides. `get_api_config(provider)` and `get_api_key(provider)` supply the factory
inputs. Never dump a complete configuration or environment into public logs.

## Errors and limits

Both providers map HTTP 402 to `PaymentRequiredError`. Callers must retain completed
work and stop payment-failed processing. OpenRouter's application retry decorator
retries errors whose text includes `rate` or `timeout`, bounded by five attempts and
300 seconds. Its stored `max_retries` and `retry_delay` settings do not alter those
decorator bounds. Perplexity has no equivalent application backoff wrapper; underlying
SDK behavior is separate. There is no automatic provider failover.

Token estimates and truncation are local heuristics, not proof that a provider's
context constraints are met. Returned prose and citations are unverified model
output. Review sources, identity matching, privacy and factual claims before use;
never automatically publish the outputs. See [research methods](methods.md).
