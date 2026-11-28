# Symposium documentation

This page is the hub: pick the guide for the job. [Documentation index](documentation-index.md)
is the flat list of every long-lived document, including release records and
hand-written policy; `./gate.sh docs` fails when a `docs/` file is missing from it.

Current operator guides describe the source interfaces. Historical release records
remain evidence of their own releases, not current test or deployment results.

| Guide | Purpose |
|---|---|
| [Installation](guides/installation.md) | Python 3.12+, locked uv setup and offline checks |
| [uv setup](../UV_SETUP.md) | Environment selection and troubleshooting |
| [Development](development/development.md) | Gate arms, CI jobs, checks and release boundaries |
| [Gate measurements](_generated/gate-measurements.md) | Generated wall time per gate arm (script-refreshed) |
| [Organizer publication](guides/organizing_publication.md) | Private intake, consent, artifacts, review and Pages |
| [Integration catalog](architecture/integrations.md) | Reviewed repository evidence and task-specific handoffs |
| [Discovery and indexing](architecture/discovery.md) | Canonical pages, sitemap, machine indexes and crawler limits |
| [Credentials](reference/credentials.md) | Optional provider/bridge access and keyless operation |
| [Methods](architecture/methods.md) | Source provenance, next-intake review and interpretation limits |
| [2026 research inputs](guides/2026_setup.md) | CSV schema, presenter exports and preflight |
| [User guide](guides/user_guide.md) | Optional research command examples |
| [API guide](reference/api_guide.md) | Actual provider/configuration contract and errors |
| [API workflows](reference/api_usage.md) | Optional paid workflow boundaries |
| [Background research](reference/perplexity_research.md) | Reviewing externally generated drafts |
| [Visualization](guides/csv_visualization_guide.md) | Local text plots and reproducibility limits |
| [2026 participant and presenter figures](guides/visualizations_2026.md) | Public-cohort charts, approved-program summaries, missingness and reproducible artifact evidence |
| [Architecture](architecture/architecture.md) | Module responsibilities and separate data paths |
| [3.4.0 release record](releases/release_3_4_0.md) | Final 2026 book, individual credits, recordings and publication status |
| [3.3.0 release record](releases/release_3_3_0.md) | Final-lineup book on Zenodo, lineup changes, verified asset hashes and public-data scope |
| [GNN conformance](../.github/GNN.md) | Pin file, revision, parsing scope and workflow job key |
| [3.2.0 release record](releases/release_3_2_0.md) | Published book and GitHub release, verified asset hashes, public-data scope and deployment results |
| [Contributing](development/contributing.md) | Scoped changes and review expectations |
| [Migration](development/migration.md) | Runtime transition and preserved historical inputs |
| [Design](architecture/DESIGN.md) | Public explorer design contract |

Project records: [changelog](../CHANGELOG.md), [backlog](../TODO.md),
[citation](../CITATION.cff), [license](../LICENSE), [agent instructions](../AGENTS.md).
Historical verification: [2.2.0](releases/release_2_2_0.md), [2.2.1](releases/release_2_2_1.md).

## Documentation by topic

- [Guides](guides/README.md)
- [Architecture](architecture/README.md)
- [Reference](reference/README.md)
- [Development](development/README.md)
- [Releases](releases/README.md)
- [Manuscript source and render](manuscript/README.md)
