# Core source map

Read [the API contract](../../../docs/api_guide.md) and
[credential boundaries](../../../docs/credentials.md) before changing provider or
configuration behavior. Inspect the actual source before updating defaults or claims.

| File | Owns |
|---|---|
| `api.py` | Explicit Perplexity/OpenRouter factory, provider calls and payment/retry errors |
| `config.py` | Defaults, selected JSON, local dotenv/environment overrides and redacted persistence |
| `data_loader.py` | Research-input reading, normalization and truncation helpers |
| `edition.py` | Edition paths, scaffold initialization and input validation |
| `logging_utils.py` | Actual logger setup; inspect this file before claiming logging features |

Provider selection is explicit. There is no automatic cross-provider failover.
Configuration redaction is not encryption: `Config.save()` writes `redacted_dict()`;
keep usable credentials in private runtime configuration. Neither factory construction
nor capability presence checks prove authentication, provider availability or balance.

Paid requests require authorized input transmission and charges. Preserve payment
failure/partial-output behavior when changing API clients. Defaults and prompt token
estimates are software settings/heuristics, not current provider capacity or quality
claims. New code should reuse the existing public schema/edition boundaries rather
than importing private organizer records into generic research workflows.

Reproduce failure paths and verify changes with the declared uv test toolchain. Keep
marked live-provider tests disabled unless explicitly authorized with `--run-real-api`.
Use the [development guide](../../../docs/development.md) for actual checks and match
performance, accuracy and release claims to observed evidence.
