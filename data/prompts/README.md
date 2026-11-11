# Prompt assets

Text and JSON prompt templates consumed by the generation and analysis workflows.
These are static inputs, not generated output.

| File | Used for |
| --- | --- |
| `System_Prompts.json` | System-prompt templates keyed by workflow (background research, curricula, profiles, proposals). Loaded by the analysis/generation modules. |
| `project.txt` | Project-proposal prompt scaffold combined with a catechism template. |
| `TechTree.txt` | Technology-tree / domain framing context. |
| `raoadmap2agents.txt` | Research-activity roadmap framing context. |

Prompts are read as UTF-8 text; keep edits plain text and avoid embedding secrets
or private URLs. Provider credentials live in the ignored `.env`, never here. See
[`../README.md`](../README.md) for the data layout and the
[credentials guide](../../docs/credentials.md) for provider boundaries.
