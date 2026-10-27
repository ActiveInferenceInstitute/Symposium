# Visualization Guide

How to create visualizations from Symposium data: word clouds and column summaries
from the participant CSV, and embedding / network / distribution plots from Markdown
reports.

## Overview

There are two visualization pipelines:

1. **CSV word clouds & column summaries** — the interactive interface (`run.py`
   option 3) reads the participant CSV and produces per-question word clouds and
   LLM-generated column summaries. This is the only path that consumes the raw CSV
   directly.
2. **Markdown report plots** — the `symposium visualize …` CLI (or `run.py` option 6)
   reads a directory of **Markdown** reports (`--input-dir`) and produces embedding,
   network, distribution, and word-cloud plots. It never accepts a CSV: participant
   CSV data feeds the `analyze`/`generate` flows first, and their Markdown reports
   are what you visualize.

> **No API keys are required for the Markdown CLI pipeline** — it is local
> processing only. `run.py` option 3 additionally needs `OPENROUTER_API_KEY` for the
> LLM-generated column summaries.

## 1. CSV Word Clouds & Column Summaries

### Run the interactive flow

```bash
./symposium.sh
# or: python run.py

# Menu:
# 3. 📊 Generate Column Summaries & Word Clouds
```

This reads `data/inputs/aif_2026/Public_Participant_Information.csv`, generates an
LLM summary per question column, and writes one word cloud per column.

### Outputs

Everything is written to `outputs/2026_symposium/column_summaries/`:

```
column_summaries/
├── column_summary_background.md                     # + one .md per column
├── wordcloud_background.png                         # Background & prior works
├── wordcloud_pragmatic_value.png                    # Pragmatic value (useful for Symposium)
├── wordcloud_epistemic_value.png                    # Epistemic value (interesting to learn)
├── wordcloud_active_inference_application.png       # How they apply Active Inference
├── wordcloud_challenges.png                         # Hurdles / challenges
├── wordcloud_learning_needs.png                     # Learning needs & resources
├── wordcloud_future_impact.png                      # Future impact vision (2026)
└── wordcloud_comments.png                           # Additional comments & questions
```

The analyzed columns are: `background`, `pragmatic_value`, `epistemic_value`,
`active_inference_application`, `challenges`, `learning_needs`, `future_impact`,
`comments` (personal info — name, email, ORCID — is excluded).

### Word cloud parameters

Word clouds are generated with `TextVisualizer.create_word_cloud`:

- **Size**: 1600×800 pixels, saved at 300 DPI
- **Max Words**: 150
- **Colors**: `plasma` colormap with navy contour
- **Fonts**: variable sizing (8–120pt)
- **Layout**: horizontal preference (80%) with plural normalization
- **Stop Words**: built-in English stop-word list, extendable via `custom_stopwords`

## 2. Markdown-Report Visualizations (CLI)

All `symposium visualize` subcommands read a directory of `.md` files. For
per-participant labelling, group reports under `people/<participant>/`
subdirectories (the layout produced by the analysis/generation flows):

```bash
symposium visualize embeddings   --input-dir outputs/2026_symposium/people --output-dir outputs/visualizations --method pca
symposium visualize networks     --input-dir outputs/2026_symposium/people --output-dir outputs/visualizations --layout spring
symposium visualize distributions --input-dir outputs/2026_symposium/people --output-dir outputs/visualizations
symposium visualize all          --input-dir outputs/2026_symposium/people --output-dir outputs/visualizations --method pca --layout spring
```

### Command options

**`visualize embeddings`** — dimension reduction and text plots
- `--method {pca,lsa,tsne,umap,isomap,nmf,lda}` (default `pca`)
- `--n-components` (default 2; 3 gives a 3D plot)
- `--max-features` (default 5000; TF-IDF feature cap)
- `--label` (label for single-file input)

**`visualize networks`** — similarity networks and community detection
- `--threshold` (default 0.3; similarity cutoff for edges)
- `--max-terms` (default 50)
- `--layout {spring,circular,kamada_kawai}` (default `spring`)

**`visualize distributions`** — statistical plots of document lengths
- (no extra options)

**`visualize all`** — embeddings + networks + distributions in one run
- accepts the `--method`, `--n-components`, `--threshold`, and `--layout` options

A single Markdown file may be passed as `--input-dir` for any of the subcommands.

### Generated files

| Command | Output files |
|---------|--------------|
| `embeddings` | `embedding_{method}_{n}d.png`, `word_cloud.png`, `term_frequency.png` |
| `networks` | `similarity_network_{layout}.png`, `community_analysis.png` |
| `distributions` | `document_length_distribution.png` |
| `all` (extra) | comprehensive PCA report (`pca_analysis_*.png`/CSV when `--method pca`) and participant PCA plots (`participants_embedding_pca_*.png`, `participants_pca_analysis_*`) when the input tree contains a `people/` directory |

### Dimension reduction methods

| Method | Description |
|--------|-------------|
| **PCA** | Principal Component Analysis — linear, most interpretable |
| **LSA** | Latent Semantic Analysis (Truncated SVD) — semantic clustering |
| **t-SNE** | Non-linear embedding — good for complex patterns |
| **UMAP** | Uniform Manifold Approximation — non-linear (requires `umap-learn`; falls back to PCA with a warning if not installed) |
| **Isomap** | Manifold learning with geodesic distances |
| **NMF** | Non-negative Matrix Factorization — topic-style components |
| **LDA** | Latent Dirichlet Allocation — probabilistic topic modeling |

### Network layouts

- **Spring**: force-directed (default)
- **Circular**: radial layout
- **Kamada-Kawai**: energy-minimization layout

## 3. Interactive Visualization (run.py option 6)

The interactive interface visualizes the Markdown reports under
`outputs/2026_symposium/people/` (it does not ask for a CSV):

```bash
python run.py
# 6. 🌐 Create Visualizations
# Choose type (1-4): embeddings / networks / distributions / all
```

It runs the same in-process code as the CLI and saves plots to
`outputs/2026_symposium/visualizations/`.

## Data Format Requirements

The participant CSV (used by `run.py` option 3 and the `analyze`/`generate` flows)
must contain the standard question columns. Example headers from
`data/inputs/aif_2026/Public_Participant_Information.csv`:

- `Can we share this information publicly?`
- `What is your name?`
- `What are your affiliations?`
- `What is your background & prior works? Feel free to provide as much information & links as you like.`
- `How are you applying Active Inference? What domain, stage?`

Column names are mapped to the short keys (`background`, `challenges`, …) used in
output filenames.

## Troubleshooting

1. **Empty visualizations** — check the CSV column names match the expected format,
   or that the `--input-dir` tree contains `.md` files.
2. **Memory errors on large inputs** — reduce `--max-features` or visualize fewer
   documents.
3. **Missing dependencies** — install with `uv pip install -e ".[dev]"`.
4. **UMAP falls back to PCA** — `umap-learn` is not a default dependency; install it
   separately to use the UMAP method.

## Best Practices

1. **Start simple**: default PCA settings for initial exploration.
2. **Iterate**: try different `--method` / `--n-components` values.
3. **Combine views**: use both 2D and 3D embeddings with network views.
4. **Annotate**: `--label` for single-file runs; keep `people/<participant>/`
   grouping for labelled multi-participant plots.
5. **Export**: plots are saved as high-resolution PNGs (300 DPI).

## Related Documentation

- [User Guide](user_guide.md) — full analysis and generation workflows
- [API Usage](api_usage.md) — LLM provider roles (summaries, curricula)
- [README](../README.md) — CLI overview and project structure
