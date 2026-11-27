# Documentation index

Flat index of the long-lived documents in this repository. [docs/README.md](README.md)
is the hub (what to read for which job); this page is the complete list, and
`./gate.sh docs` fails when a `docs/` file is missing from it.

## Start here

| Document | Read it for |
| --- | --- |
| [Documentation hub](README.md) | Which guide covers which job |
| [Repository guide](../AGENTS.md) | Layout, public/private boundary, development rules |
| [README](../README.md) | Install, quick start, public program, release state |
| [Installation](guides/installation.md) | Locked uv setup and offline checks |
| [Development](development/development.md) | Gate arms, checks, evidence and release boundaries |

## Operator and research guides

| Document | Read it for |
| --- | --- |
| [Organizer publication](guides/organizing_publication.md) | Private intake, consent, native artifacts, review, Pages |
| [2026 research inputs](guides/2026_setup.md) | CSV schema, presenter exports, preflight |
| [Methods](architecture/methods.md) | Source provenance, next-intake review, interpretation limits |
| [Integration catalog](architecture/integrations.md) | Reviewed repositories and task-specific handoffs |
| [Discovery and indexing](architecture/discovery.md) | Canonical pages, sitemap, machine indexes, crawler limits |
| [Credentials](reference/credentials.md) | Optional provider/bridge access and keyless operation |
| [API guide](reference/api_guide.md) | Provider and configuration contract, errors |
| [API workflows](reference/api_usage.md) | Optional paid workflow boundaries |
| [User guide](guides/user_guide.md) | Research command examples |
| [Background research](reference/perplexity_research.md) | Reviewing externally generated drafts |
| [Visualization](guides/csv_visualization_guide.md) | Local text plots and reproducibility limits |
| [2026 figures](guides/visualizations_2026.md) | Public-cohort charts, program summaries, missingness |

## Architecture and design

| Document | Read it for |
| --- | --- |
| [Architecture](architecture/architecture.md) | Module responsibilities and separate data paths |
| [Design](architecture/DESIGN.md) | Public explorer design contract |
| [Migration](development/migration.md) | Runtime transition and preserved historical inputs |
| [uv setup](../UV_SETUP.md) | Environment selection and troubleshooting |
| [Test suite](../tests/README.md) | Fast and full arms, focused runs, live-provider opt-in |
| [GNN conformance](../.github/GNN.md) | Pin file, parsing scope, workflow job key |

## Contributing and policy

| Document | Read it for |
| --- | --- |
| [Contributing](development/contributing.md) | Scoped changes and review expectations |
| [Changelog](../CHANGELOG.md) | Release history |
| [Backlog](../TODO.md) | Open work and retained records |
| [Citation](../CITATION.cff) | Machine-readable citation |
| [License](../LICENSE) | MIT terms |

## Release records

| Document | Read it for |
| --- | --- |
| [3.4.0](releases/release_3_4_0.md) | Final 2026 book, corrected titles, individual credits and publication status |
| [3.3.0](releases/release_3_3_0.md) | Final-lineup book, lineup changes, verified asset hashes, public-data scope |
| [3.2.0](releases/release_3_2_0.md) | Published book and GitHub release, asset hashes, deployment results |
| [2.2.1](releases/release_2_2_1.md) | 2.2.1 release record |
| [2.2.0](releases/release_2_2_0.md) | 2.2.0 release record |

Release records are historical evidence for their own release, not current test,
deployment or scientific results.

## Generated

Numbers a script can produce are generated, never hand-edited.

| Document | Producer |
| --- | --- |
| [Gate measurements](_generated/gate-measurements.md) | `uv run --no-sync python scripts/gate_metrics.py refresh` |
| [Generated folder policy](_generated/README.md) | Hand-written policy for this folder |

## Additional pages

- [Architecture](architecture/README.md)
- [Development](development/README.md)
- [Guides](guides/README.md)
- [Abstract](manuscript/00_abstract.md)
- [Input and projection](manuscript/01_projection.md)
- [Artifact custody and rendering](manuscript/02_custody.md)
- [Edition evidence and replay](manuscript/03_observed_edition.md)
- [Review boundaries](manuscript/04_limits.md)
- [References](manuscript/99_references.md)
- [Manuscript guidance](manuscript/AGENTS.md)
- [Evidence and Approval Boundaries in the Active Inference Symposium Program](manuscript/README.md)
- [LaTeX preamble](manuscript/preamble.md)
- [Reference](reference/README.md)
- [Releases](releases/README.md)
