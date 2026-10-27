# Credentials and keyless methods

No API key is required for the website, method catalog, input validation, approved
snapshot verification, deterministic dossiers/briefs, calendar generation, candidate
comparison or local Template rendering. Local rendering still requires its separately
installed compatible pipeline and interpreter.

```bash
uv run symposium organize capabilities
uv run symposium organize capabilities --check-env
```

The default reports credential names without inspecting the environment. The second
command checks presence in the current process environment only. It does not read
`.env`, return values or fingerprints, authenticate, check document permissions,
verify a model, check credit balance, authorize transmission or make a network call.
A configured value can still be invalid or expired. Provider configuration loading
is a separate interface described in the [API guide](api_guide.md).

| Variable | Needed for | Setup and boundaries |
|---|---|---|
| `OPENROUTER_API_KEY` | Optional OpenRouter research drafts and generation | Create a separate key with an appropriate credit limit in [OpenRouter](https://openrouter.ai/keys); [authentication and limits](https://openrouter.ai/docs/api_reference/authentication). Select a currently available model in configuration. |
| `PERPLEXITY_API_KEY` | Optional Perplexity analysis and background-research workflows | Use an authorized project key; [provider key management](https://docs.perplexity.ai/docs/admin/api-key-management). Review charges and processing permissions before execution. |
| `SUPERHUMAN_DOCS_MCP_TOKEN` | Standalone `organize pull` / receipt application through the optional InstituteOS SDK | Use a Docs API token with **Docs MCP access enabled**; provide the raw token without a `Bearer ` prefix. The adapter adds the header. The SDK must be installed separately. A REST-only token without MCP access is insufficient. |

For the standalone bridge, read-only access supports pulls; guarded receipt application
needs read and write access for baseline checks, append and readback. The provider
documents [token creation](https://help.superhuman.com/hc/en-us/articles/46210310809613-Generate-API-tokens-for-Docs)
and [MCP access controls](https://help.superhuman.com/hc/en-us/articles/46210118248205-Security-recommendations-for-the-Docs-MCP).
Selecting specific docs for REST API access does **not** by itself restrict MCP reach.
Check the actual MCP connection controls and account permissions. Connected OAuth
access and a standalone personal token are different authentication paths.

Choose the provider needed for the workflow; a normal provider-specific run does not
need every key. A connected Docs tool authenticates separately from the standalone
SDK process. Access through one does not populate the other process's environment.

GitHub Pages builds use approved public files and GitHub's workflow authentication,
without organizer or provider credentials. Normal local Git/GitHub authentication is
separate from model keys. Search Console submission/inspection requires an authorized
site property and account access, rather than a key embedded in this repository;
see [discovery](discovery.md).

Keep credentials in a private secret store or operator-owned runtime environment.
If using the existing local `.env` support for providers, preserve the file and keep it
ignored. Never paste keys into public issues, catalogs, examples, browser JavaScript,
program bundles or generated documentation. Key presence is not authorization to send
participant content to a provider. Default tests skip marked live-provider tests;
`--run-real-api` is an explicit additional opt-in and can incur charges.
