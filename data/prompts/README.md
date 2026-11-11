# Prompt assets

Static prompt texts retained in the data tree for reference. The current
`src/symposium/` package builds its prompts inline and does not read these files,
so editing them does not change analysis or generation output.

| File | Contents |
| --- | --- |
| `System_Prompts.json` | JSON object of named system-prompt personas (for example `ecological_researcher`, `market_analyst`, `soft_matter_scientist`), keyed by numeric index. |
| `project.txt` | Generic project-blueprint prompt scaffold (objectives, scope, work breakdown, timeline, budget). |
| `TechTree.txt` | Prompt for building an iterative Active Inference methods "Tech Tree". |
| `raoadmap2agents.txt` | "CompuLingo" multi-agent research-roadmap prompt. |

Prompts are read as UTF-8 text; keep edits plain text and avoid embedding secrets
or private URLs. Provider credentials live in the ignored `.env`, never here. See
[`../README.md`](../README.md) for the data layout and the
[credentials guide](../../docs/credentials.md) for provider boundaries.
