# Architecture

Symposium has two distinct data paths: approved organizer publication and optional
research analysis. The CLI dispatches into modules; no umbrella orchestration API
is required.

| Module | Responsibility |
|---|---|
| `core` | Configuration, provider factory, CSV loading, edition paths and validation |
| `organizing` | Private transport snapshots, allowlisted projection, consent ledger, artifacts, manifests and site |
| `analysis` | Participant and presenter LLM draft workflows |
| `generation` | LLM profile/method and proposal drafts |
| `io` | Report readers/writers and template handling |
| `visualization` | TF-IDF, dimension reduction, networks and descriptive plots |
| `calendar` | General schedule export API |
| `cli` | `edition`, `organize`, `analyze`, `generate`, `visualize` parsers and dispatch |

## Publication path

Private source mapping → validated snapshot → public projection and private approval
ledger → reviewed artifacts → fresh staged public tree → verified static site.
`program.json` carries approved public entities; `publication.json` binds the public
files. An artifact index binds derived outputs to their bundle. The private bridge
and optional InstituteOS transport are not Pages runtime dependencies. Native book
rendering invokes a separately installed Template pipeline with a separate Python
3.14 environment. See [organizer publication](organizing_publication.md).

## Research path

Edition-specific registration CSV and presenter exports → validated input → optional
provider calls → Markdown/JSON drafts → local text plots. These inputs live under
`data/inputs/aif_2026/` by default, independently of `data/public/2026/`. The empty
research scaffold does not mean the approved public program is empty. Outputs from
analysis/generation never enter the public projection automatically.

`Config` handles defaults, JSON and supported environment overrides. `APIClient`
constructs provider instances; it does not switch providers automatically. Participant
CLI batches detect incomplete results, while other legacy workflows may retain
per-item failures. Inspect outputs and errors rather than relying only on exit zero.
See [API guide](api_guide.md) and [methods](methods.md).

Historical 2024/2025 data and archived workflows are retained independently. New
intake must use current authorization and a fresh review; history is not an input
fallback or an authorization source.
