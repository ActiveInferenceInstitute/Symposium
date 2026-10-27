# Optional API workflows

This guide replaces the historical 2025 provider-comparison table. No current price,
quality score, context-window or exhaustive-search claim is established by this
repository. Provider names and model strings are configuration, not validation.

| Task | Interface | Boundary |
|---|---|---|
| Participant profiles | `analyze participants` | Selected provider; optional extra report flags |
| Background drafts | `analyze backgrounds` | Perplexity background workflow |
| Learning curricula | `analyze curricula` | Selected provider |
| Presenter analysis | `analyze presenters` | OpenAlex exports and optional domain context |
| Profiles and method drafts | `generate profiles --include-methods` | Selected provider |
| Project proposals | `generate projects` | Existing profiles, domain context and catechism |

Inspect exact inputs with `uv run symposium analyze participants --help` or the
corresponding command. See [user examples](user_guide.md) and
[API configuration](api_guide.md). Commands require current authorized data and may
incur charges; use a private output location and retain partial failures. Historical
registration consent is not current consent and public-sharing consent alone does
not settle authorization to send data to a third-party provider.

Approved public dossiers, participant briefs, calendar files, abstract-book staging
and site generation use the [organizing workflow](organizing_publication.md), with
no paid LLM call. They do not consume or automatically promote generated biographies,
rankings, proposals, or learning assessments.
