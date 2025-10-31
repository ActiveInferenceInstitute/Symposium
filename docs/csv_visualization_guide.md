# CSV Visualization Guide

This guide demonstrates how to create comprehensive visualizations from participant CSV data, including word clouds, PCA embeddings, similarity networks, and statistical distributions.

## Overview

The Symposium package now supports comprehensive visualization of participant data from CSV files. This enables:

### Enhanced Word Clouds
- **Overall Word Cloud**: Visual representation of term frequencies across all participant responses
- **Per-Column Word Clouds**: Separate word clouds for each question/column in the CSV
- **Custom Stop Words**: Extensive list of common words automatically excluded (and, the, of, to, in, etc.)
- **Enhanced Styling**: Professional-grade word clouds with improved colors, fonts, and layouts

### Advanced Dimension Reduction Methods
- **PCA (Principal Component Analysis)**: Enhanced with whitening and better parameters
- **LSA (Latent Semantic Analysis)**: Improved Truncated SVD with randomized algorithms
- **t-SNE**: Enhanced with adaptive perplexity and better initialization
- **UMAP**: Non-linear dimension reduction with cosine similarity (falls back to PCA if not available)
- **Isomap**: Manifold learning for non-linear relationships (falls back to PCA if needed)
- **NMF (Non-negative Matrix Factorization)**: For topic extraction
- **LDA (Latent Dirichlet Allocation)**: Topic modeling approach

### Comprehensive Analysis
- **Similarity Networks**: Network graphs showing relationships between participants
- **Statistical Distributions**: Analysis of response lengths and patterns
- **Term Frequency Analysis**: Detailed analysis of word distributions
- **Community Detection**: Automatic grouping of similar participants

## Quick Start

### Enhanced Word Clouds

```bash
# Create per-column word clouds from participant CSV
symposium visualize wordclouds \
    --input-csv data/inputs/aif_2025/Public_Participant_Information.csv \
    --output-dir outputs/wordclouds \
    --per-column

# Create overall word cloud only
symposium visualize wordclouds \
    --input-csv data/inputs/aif_2025/Public_Participant_Information.csv \
    --output-dir outputs/wordclouds
```

### Advanced Embedding Methods

```bash
# Enhanced PCA with whitening
symposium visualize embeddings \
    --input-csv data/inputs/aif_2025/Public_Participant_Information.csv \
    --output-dir outputs/pca_enhanced \
    --method pca \
    --n-components 2

# Advanced t-SNE with adaptive parameters
symposium visualize embeddings \
    --input-csv data/inputs/aif_2025/Public_Participant_Information.csv \
    --output-dir outputs/tsne_advanced \
    --method tsne \
    --n-components 2

# UMAP for non-linear dimension reduction
symposium visualize embeddings \
    --input-csv data/inputs/aif_2025/Public_Participant_Information.csv \
    --output-dir outputs/umap_analysis \
    --method umap \
    --n-components 2

# NMF for topic extraction
symposium visualize embeddings \
    --input-csv data/inputs/aif_2025/Public_Participant_Information.csv \
    --output-dir outputs/nmf_topics \
    --method nmf \
    --n-components 3
```

### Complete Visualization Pipeline

```bash
# Generate all visualization types with advanced methods
symposium visualize all \
    --input-csv data/inputs/aif_2025/Public_Participant_Information.csv \
    --output-dir outputs/complete_analysis \
    --method tsne \
    --layout spring
```

## Generated Visualizations

### Enhanced Word Clouds

#### 1. Overall Word Cloud (`word_cloud_overall.png`)
Visual representation of the most frequent terms across all participant responses.

- **Input**: All text fields from participant data combined
- **Features**: Custom stop words filtering, enhanced styling, professional colors
- **Output**: High-resolution PNG image (1600x800)

#### 2. Per-Column Word Clouds (`word_cloud_{column}.png`)
Separate word clouds for each question/column in the CSV data.

- **Input**: Individual columns (background, applications, challenges, etc.)
- **Features**: Column-specific analysis, meaningful term extraction
- **Output**: Individual PNG files for each column (9 total)

**Generated Column Word Clouds:**
- `word_cloud_background.png` - Background & Prior Works
- `word_cloud_pragmatic_value.png` - Pragmatic Value (Useful for Symposium)
- `word_cloud_epistemic_value.png` - Epistemic Value (Interesting to Learn)
- `word_cloud_active_inference_application.png` - Active Inference Applications
- `word_cloud_challenges.png` - Challenges in Active Inference
- `word_cloud_learning_needs.png` - Learning Needs & Resource Development
- `word_cloud_future_impact.png` - Future Impact Vision (2026)
- `word_cloud_comments.png` - Additional Comments & Questions

### Advanced Dimension Reduction Methods

#### 1. Enhanced PCA (`embedding_pca_2d.png`)
2D Principal Component Analysis with whitening and improved parameters.

- **Input**: TF-IDF vectorized text with bigrams and enhanced preprocessing
- **Features**: Component whitening, better interpretability
- **Output**: Publication-ready scatter plot with feature annotations

#### 2. Enhanced LSA (`embedding_lsa_2d.png`)
Latent Semantic Analysis using randomized Truncated SVD.

- **Input**: TF-IDF matrix with semantic relationships
- **Features**: Faster computation, better semantic clustering
- **Output**: Semantic space visualization

#### 3. Advanced t-SNE (`embedding_tsne_2d.png`)
t-Distributed Stochastic Neighbor Embedding with adaptive parameters.

- **Input**: High-dimensional TF-IDF space
- **Features**: Adaptive perplexity, PCA initialization, better convergence
- **Output**: Non-linear clustering visualization

#### 4. UMAP Analysis (`embedding_umap_2d.png`)
Uniform Manifold Approximation and Projection for non-linear reduction.

- **Input**: TF-IDF matrix with cosine similarity
- **Features**: Non-linear relationships, cosine metric
- **Output**: Advanced non-linear clustering (falls back to PCA if UMAP unavailable)

#### 5. NMF Topics (`embedding_nmf_2d.png`)
Non-negative Matrix Factorization for topic extraction.

- **Input**: TF-IDF matrix for topic modeling
- **Features**: Topic-based clustering, interpretable components
- **Output**: Topic-based participant grouping

#### 6. LDA Topics (`embedding_lda_2d.png`)
Latent Dirichlet Allocation for probabilistic topic modeling.

- **Input**: TF-IDF matrix for topic discovery
- **Features**: Probabilistic topic modeling, document-topic distributions
- **Output**: Topic-based participant clustering

### 3. Similarity Networks (`similarity_network_spring.png`)

Network graph showing similarities between participants based on their responses.

- **Input**: Cosine similarity between participant text vectors
- **Features**: Spring layout, community detection, edge weights
- **Output**: Interactive network visualization

### 4. Community Analysis (`community_analysis.png`)

Community detection and analysis within the participant similarity network.

- **Input**: Similarity network from participant data
- **Features**: Modularity optimization, centrality analysis
- **Output**: Community structure visualization

### 5. Term Frequency Distribution (`term_frequency.png`)

Bar chart showing the frequency distribution of terms across participant responses.

- **Input**: Tokenized text from all participants
- **Features**: Logarithmic scaling, top N terms
- **Output**: Statistical frequency analysis

### 6. Document Length Distribution (`document_length_distribution.png`)

Statistical analysis of response lengths across different participant categories.

- **Input**: Character/word counts from participant responses
- **Features**: Box plots, histograms, KDE plots, statistical summaries
- **Output**: Multi-panel statistical visualization

## Data Processing

The visualization pipeline processes participant data as follows:

1. **CSV Loading**: Reads participant data using pandas
2. **Text Extraction**: Combines relevant fields (affiliations, background, applications, etc.)
3. **Text Preprocessing**: TF-IDF vectorization with stop-word removal
4. **Dimension Reduction**: PCA/LSA/t-SNE for embedding visualization
5. **Similarity Calculation**: Cosine similarity for network construction
6. **Visualization Generation**: Multiple plot types with professional styling

## Configuration Options

### Advanced Embedding Methods

- **PCA**: Principal Component Analysis (enhanced with whitening, best for interpretability)
- **LSA**: Latent Semantic Analysis (randomized SVD, excellent for semantic clustering)
- **t-SNE**: t-Distributed Stochastic Neighbor Embedding (adaptive parameters, best for complex non-linear patterns)
- **UMAP**: Uniform Manifold Approximation (non-linear, cosine similarity, advanced clustering)
- **Isomap**: Manifold Learning (non-linear relationships, geodesic distances)
- **NMF**: Non-negative Matrix Factorization (topic extraction, interpretable components)
- **LDA**: Latent Dirichlet Allocation (probabilistic topic modeling)

### Word Cloud Options

#### Custom Stop Words
The system automatically excludes 50+ common words:
```
and, the, of, to, in, a, i, for, that, is, on, as, have, with, are, be, it, more, this, my, which, but, from, would, or, into, about, am, an, at, by, do, go, if, me, no, so, up, we, you, all, can, did, get, had, has, her, him, his, how, its, let, may, new, not, now, old, our, out, put, see, she, too, use, way, who, why, yes, yet, what, when, where, will, work, was, were, been, being, there, here
```

#### Word Cloud Parameters
- **Size**: 1600x800 pixels (high resolution)
- **Max Words**: 150 terms (configurable)
- **Colors**: Plasma colormap (professional styling)
- **Fonts**: Variable sizing (8-120pt) with smooth scaling
- **Layout**: Horizontal preference (80%) with word normalization

### Network Layouts

- **Spring**: Force-directed layout (default, good for most cases)
- **Circular**: Radial layout (good for small networks)
- **Kamada-Kawai**: Energy minimization layout (best for larger networks)

### Visualization Parameters

```bash
# High-resolution output with many features
--max-features 5000      # Increase for richer analysis
--n-components 3         # 3D visualization
--threshold 0.5         # Higher threshold for stronger connections
```

## Example Output

### Per-Column Word Clouds
```
outputs/wordclouds/
├── word_cloud_overall.png                    # Overall responses
├── word_cloud_background.png                 # Background & Prior Works
├── word_cloud_pragmatic_value.png            # Pragmatic Value
├── word_cloud_epistemic_value.png            # Epistemic Value
├── word_cloud_active_inference_application.png # AI Applications
├── word_cloud_challenges.png                 # Challenges
├── word_cloud_learning_needs.png             # Learning Needs
├── word_cloud_future_impact.png              # Future Impact
└── word_cloud_comments.png                   # Comments & Questions
```

### Advanced Embedding Methods
```
outputs/enhanced_analysis/
├── embedding_pca_2d.png          # Enhanced PCA with whitening
├── embedding_lsa_2d.png          # Latent Semantic Analysis
├── embedding_tsne_2d.png         # Advanced t-SNE
├── embedding_umap_2d.png         # UMAP clustering
├── embedding_nmf_2d.png          # NMF topic extraction
├── embedding_lda_2d.png          # LDA topic modeling
├── word_cloud_overall.png        # Enhanced word cloud
├── term_frequency.png            # Term frequency distribution
├── similarity_network_spring.png # Similarity networks
├── community_analysis.png        # Community detection
└── document_length_distribution.png # Statistical analysis
```

### Complete Pipeline Output
```
outputs/complete_analysis/
├── wordclouds/                   # All 9 word cloud types
├── pca_enhanced/                # Enhanced PCA visualizations
├── tsne_advanced/               # Advanced t-SNE visualizations
├── umap_analysis/               # UMAP clustering
├── nmf_topics/                  # NMF topic extraction
├── similarity_networks/         # Network analysis
└── distributions/               # Statistical distributions
```

## Interactive Usage

Using the interactive interface:

```bash
python run.py
# Choose option 6: "Create Visualizations"
# Select visualization type (1-4)
# Choose input type: CSV
# Configure parameters interactively
```

## Advanced Examples

### Custom Field Selection

The visualization automatically includes relevant fields:
- Affiliations and institutions
- Background and prior work
- Active Inference applications
- Learning needs and challenges
- Future impact visions

### Multi-dimensional Analysis

```bash
# 3D PCA visualization
symposium visualize embeddings \
    --input-csv data/inputs/aif_2025/Public_Participant_Information.csv \
    --output-dir outputs/3d_analysis \
    --method pca \
    --n-components 3
```

### Network Analysis with Different Thresholds

```bash
# High similarity threshold for tight clusters
symposium visualize networks \
    --input-csv data/inputs/aif_2025/Public_Participant_Information.csv \
    --output-dir outputs/network_analysis \
    --threshold 0.7 \
    --layout kamada_kawai
```

## Performance Considerations

- **Memory Usage**: ~500MB peak for large participant datasets
- **Processing Time**: 2-5 minutes for complete pipeline
- **Output Size**: 10-50MB total for all visualizations
- **Resolution**: 300 DPI for publication quality

## Troubleshooting

### Common Issues

1. **Empty Visualizations**: Check CSV column names match expected format
2. **Memory Errors**: Reduce `--max-features` or use smaller datasets
3. **Missing Dependencies**: Install with `uv pip install -e ".[dev]"`

### Data Format Requirements

The CSV must include these columns (case-sensitive):
- `What is your name?`
- `What are your affiliations?`
- `What is your background & prior works?`
- `How are you applying Active Inference?`
- Additional fields are automatically included

### API Requirements

No API keys required for visualization - uses local processing only.

## Integration with Analysis Pipeline

Visualizations work seamlessly with the analysis pipeline:

```bash
# 1. Run complete participant analysis
python run.py
# Choose option 2: Analyze 2025 Participants
# Choose option 4: Complete Analysis

# 2. Generate visualizations from results
python run.py
# Choose option 6: Create Visualizations
# Select processed participant data
```

## Best Practices

1. **Start Simple**: Use default PCA settings for initial exploration
2. **Iterate**: Generate multiple visualizations with different parameters
3. **Combine**: Use both 2D and 3D views for comprehensive understanding
4. **Annotate**: Add titles and descriptions for presentation use
5. **Export**: Generate high-resolution images for publications

## Research Applications

These visualizations are particularly useful for:

- **Community Analysis**: Understanding participant clusters and interests
- **Trend Identification**: Detecting common themes and research directions
- **Collaboration Opportunities**: Finding participants with similar interests
- **Symposium Planning**: Informing session organization and networking
- **Active Inference Research**: Mapping the current state of the field
