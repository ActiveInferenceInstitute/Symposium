# data/domains — Domain Knowledge Files (user-provided)

This directory holds **optional domain-context files** that are passed to the LLM
prompts during analysis and generation. The directory is a configured default path
(`data/domains` in `src/symposium/core/config.py`), but the repo does **not** ship any
domain content — create your own files here.

## How domain files are used

- `symposium analyze presenters --domain-file <path>` — passes the file's contents as
  research context for presenter analysis.
- `symposium generate profiles --domain-file <path>` — domain context for profile and
  methods generation.
- `symposium generate projects --domain-file <path>` — **required** for project
  proposal generation; context for proposal design.

The file contents are read as Markdown text (`ReportReader.read_domain_knowledge`).

## Creating a domain file

```bash
mkdir -p data/domains
cat > data/domains/active_inference.md << 'EOF'
# Active Inference Research Domain

## Core Principles
- Free Energy Principle
- Active Inference
- Predictive Processing

## Current Challenges
- Scalability issues
- Biological plausibility
- Real-world applications
EOF
```

Then reference it, e.g.:

```bash
symposium analyze presenters \
  --data-dir data/inputs/aif_2025/ \
  --output-dir outputs/profiles/ \
  --domain-file data/domains/active_inference.md
```

## Notes

- Any Markdown file works — the path is passed explicitly via `--domain-file`.
- The optional `--collaborators-file` (project generation) is likewise user-provided.
- See [docs/user_guide.md](../../docs/user_guide.md#custom-domain-knowledge) for more on
  domain context and custom catechisms.
