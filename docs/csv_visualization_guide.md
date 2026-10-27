# Text visualization

The `visualize` CLI reads Markdown reports recursively from `--input-dir`; it does
not interpret a registration CSV as survey data. A single Markdown file is also
accepted, but many reductions require multiple documents. This workflow makes no
LLM calls. Use a deliberate corpus of reviewed documents and a private output path
when any input contains personal information.

```bash
uv run symposium visualize embeddings --input-dir "$REPORTS_DIR" --output-dir "$PLOTS_DIR" --method pca
uv run symposium visualize networks --input-dir "$REPORTS_DIR" --output-dir "$PLOTS_DIR" --layout spring
uv run symposium visualize distributions --input-dir "$REPORTS_DIR" --output-dir "$PLOTS_DIR"
uv run symposium visualize all --input-dir "$REPORTS_DIR" --output-dir "$PLOTS_DIR" --method pca
```

Set `REPORTS_DIR` and `PLOTS_DIR` to your selected input and output directories.
Use `--help` before execution. `embeddings` accepts `--method` (`pca`, `lsa`, `tsne`,
`umap`, `isomap`, `nmf`, `lda`), `--n-components` (default 2), `--max-features`
(default 5000), and a single-file `--label`. `networks` accepts `--threshold`
(default 0.3), `--max-terms` (default 50) and `--layout` (`spring`, `circular`,
`kamada_kawai`). `all` combines method/components and threshold/layout options.

The embedding command writes an embedding PNG, word cloud and term-frequency plot;
networks write network and community plots; distributions write document-length
plots. `all` also attempts PCA diagnostics for PCA input. Read the actual logs and
inspect files: some empty-input/reduction failures are logged and return without a
nonzero process status, so exit zero alone does not establish artifact completeness.

## What the methods measure

TF-IDF represents word usage in this corpus. PCA and LSA summarize linear variation;
NMF and LDA provide component/topic-style representations; t-SNE, UMAP and Isomap
construct lower-dimensional layouts. Similarity-network edges depend on the vocabulary,
weights and selected threshold. These are exploratory text summaries, not measures
of researcher quality, scientific agreement, collaboration suitability or causal
relationships. Generated report phrasing can dominate the apparent structure.

UMAP is optional and is not a declared base dependency. When unavailable, the
implementation warns and uses PCA; Isomap may also fall back to PCA on failure.
Retain warnings and identify the method actually executed, not just the requested
method or output filename. Small corpora, empty vocabularies and insufficient rank
can prevent meaningful plots. Do not claim that separated points prove distinct
research communities.

For reproducibility, retain the corpus/file hashes and order, package lock, Python
version, options, logs, actual reducer and output hashes. Dimension reduction uses
seed 42 where configured; network layouts use a configurable default seed 42.
Fixed seeds do not guarantee byte-identical figures across library, font or platform
changes. Word-cloud layout is descriptive and does not establish significance.

## CSV summaries

`uv run python run.py --year 2026` exposes the column-summary/word-cloud workflow.
Unlike the local Markdown plotting CLI, column summaries use a paid provider. The
participant command also exposes `--include-column-summaries`. Inputs are the
consent-filtered research registration CSV, not the approved public snapshot.
Do not run these actions as an offline installation test. Verify authorization,
review draft summaries against responses, and keep private outputs out of Pages.
See [methods](methods.md) and [API configuration](api_guide.md).
