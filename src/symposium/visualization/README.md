# Visualization Module

Data visualization and analysis tools for the Symposium package.

## Overview

This module provides comprehensive visualization capabilities for research data, including embeddings, networks, statistical distributions, and detailed PCA analysis.

## Components

### TextVisualizer
Text analysis and visualization tools:
- Word cloud generation
- Term frequency plotting
- Dimension reduction plotting (2D/3D)
- Embedding visualization

### NetworkAnalyzer
Network analysis and visualization:
- Similarity network creation
- Community detection
- Network plotting with multiple layouts
- Centrality analysis

### DistributionPlotter
Statistical distribution visualization:
- Document length distributions
- TF-IDF score distributions
- Category comparisons
- Statistical analysis plots

### DimensionReducer
Dimension reduction algorithms:
- PCA (Principal Component Analysis)
- LSA (Latent Semantic Analysis)
- t-SNE (t-Distributed Stochastic Neighbor Embedding)

### PCAAnalyzer (NEW)
Comprehensive PCA analysis and visualization:
- **Scree plots**: Variance explained per component
- **Loading plots**: Feature contributions to components
- **Biplots**: Combined scores and loadings visualization
- **Heatmaps**: Full loading matrix visualization
- **Correlation matrices**: Inter-component relationships
- **3D visualizations**: Three-dimensional component space
- **Data exports**: Structured CSV tables for further analysis

## Usage

```python
from symposium.visualization import (
    TextVisualizer, 
    NetworkAnalyzer, 
    DistributionPlotter,
    PCAAnalyzer
)

# Text visualization
visualizer = TextVisualizer(config)
visualizer.create_word_cloud(documents, "Research Word Cloud", output_path)
visualizer.plot_dimension_reduction(matrix, labels, filenames, title, output_path)

# Network analysis
analyzer = NetworkAnalyzer(config)
graph = analyzer.create_similarity_network(tfidf_matrix, vectorizer, filenames)
analyzer.plot_network(graph, "Research Network", output_path)

# Distribution plotting
plotter = DistributionPlotter(config)
plotter.plot_document_length_distribution(documents, labels, title, output_path)

# PCA Analysis (NEW)
pca_analyzer = PCAAnalyzer(config)
results = pca_analyzer.create_comprehensive_pca_report(
    pca=pca_model,
    reduced_matrix=transformed_data,
    vectorizer=tfidf_vectorizer,
    labels=document_labels,
    output_dir="outputs/pca_analysis"
)
# Returns dict with success status of each visualization type
```

## PCA Analysis Features

The new PCAAnalyzer provides seven types of visualizations:

### 1. Scree Plot
Shows variance explained by each principal component with cumulative variance overlay.

### 2. Loadings Plot
Displays top positive and negative feature loadings for each component, showing which terms contribute most to each dimension.

### 3. Biplot
Combines document scores (scatter points) with feature loadings (arrows) to show relationships between documents and features.

### 4. Loadings Heatmap
Matrix visualization of all feature loadings across components with diverging colormap.

### 5. Component Correlation Matrix
Shows correlations between principal components to validate orthogonality.

### 6. 3D Component Visualization
Three-dimensional scatter plot of first three principal components.

### 7. Loadings Table (CSV)
Structured data export with rankings, loadings, and variance metrics for further analysis.

For detailed information, see [PCA_GUIDE.md](PCA_GUIDE.md).

## Visualization Types

### Embedding Visualizations
- **2D Plots**: PCA, LSA, t-SNE in two dimensions
- **3D Plots**: Three-dimensional embeddings
- **Interactive**: Zoomable and rotatable views
- **Labeled**: Document and feature labeling

### Network Visualizations
- **Similarity Networks**: Document-term relationships
- **Community Analysis**: Research community detection
- **Centrality Mapping**: Influence and connectivity
- **Multiple Layouts**: Spring, circular, Kamada-Kawai

### Statistical Visualizations
- **Distribution Plots**: Document length distributions
- **TF-IDF Analysis**: Term importance visualization
- **Category Comparison**: Multi-group statistical analysis
- **Correlation Plots**: Variable relationship mapping

## Data Requirements

### Input Data
- Research profiles and abstracts
- Term-document matrices
- Metadata and labels
- Similarity measurements

### Configuration
- Dimension reduction parameters
- Visualization settings
- Color schemes and styling
- Output format specifications

## Output Formats

### Image Formats
- **PNG**: High-resolution raster images
- **SVG**: Scalable vector graphics
- **PDF**: Publication-ready documents

### Interactive Formats
- **HTML**: Web-based interactive visualizations
- **JSON**: Data for custom visualization tools

## Integration

This module integrates with:
- `symposium.analysis` - Analyzed data for visualization
- `symposium.generation` - Generated content for plotting
- `symposium.io` - File I/O for visualization data
- `symposium.cli` - Command-line visualization interface
