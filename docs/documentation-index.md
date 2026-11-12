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
| [Installation](installation.md) | Locked uv setup and offline checks |
| [Development](development.md) | Gate arms, checks, evidence and release boundaries |

## Operator and research guides

| Document | Read it for |
| --- | --- |
| [Organizer publication](organizing_publication.md) | Private intake, consent, native artifacts, review, Pages |
| [2026 research inputs](2026_setup.md) | CSV schema, presenter exports, preflight |
| [Methods](methods.md) | Source provenance, next-intake review, interpretation limits |
| [Integration catalog](integrations.md) | Reviewed repositories and task-specific handoffs |
| [Discovery and indexing](discovery.md) | Canonical pages, sitemap, machine indexes, crawler limits |
| [Credentials](credentials.md) | Optional provider/bridge access and keyless operation |
| [API guide](api_guide.md) | Provider and configuration contract, errors |
| [API workflows](api_usage.md) | Optional paid workflow boundaries |
| [User guide](user_guide.md) | Research command examples |
| [Background research](perplexity_research.md) | Reviewing externally generated drafts |
| [Visualization](csv_visualization_guide.md) | Local text plots and reproducibility limits |
| [2026 figures](visualizations_2026.md) | Public-cohort charts, program summaries, missingness |

## Architecture and design

| Document | Read it for |
| --- | --- |
| [Architecture](architecture.md) | Module responsibilities and separate data paths |
| [Design](DESIGN.md) | Public explorer design contract |
| [Migration](migration.md) | Runtime transition and preserved historical inputs |
| [uv setup](../UV_SETUP.md) | Environment selection and troubleshooting |
| [Test suite](../tests/README.md) | Fast and full arms, focused runs, live-provider opt-in |
| [GNN conformance](../.github/GNN.md) | Pin file, parsing scope, workflow job key |

## Contributing and policy

| Document | Read it for |
| --- | --- |
| [Contributing](contributing.md) | Scoped changes and review expectations |
| [Changelog](../CHANGELOG.md) | Release history |
| [Backlog](../TODO.md) | Open work and retained records |
| [Citation](../CITATION.cff) | Machine-readable citation |
| [License](../LICENSE) | MIT terms |

## Release records

| Document | Read it for |
| --- | --- |
| [3.2.0](release_3_2_0.md) | Published book and GitHub release, asset hashes, deployment results |
| [2.2.1](release_2_2_1.md) | 2.2.1 release record |
| [2.2.0](release_2_2_0.md) | 2.2.0 release record |

Release records are historical evidence for their own release, not current test,
deployment or scientific results.

## Generated

Numbers a script can produce are generated, never hand-edited.

| Document | Producer |
| --- | --- |
| [Gate measurements](_generated/gate-measurements.md) | `uv run --no-sync python scripts/gate_metrics.py refresh` |
| [Generated folder policy](_generated/README.md) | Hand-written policy for this folder |
