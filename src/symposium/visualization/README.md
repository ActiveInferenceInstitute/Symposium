# Visualization Module

Data visualization and analysis tools for the Symposium package.

## Overview

This module provides comprehensive visualization capabilities for research data, including embeddings, networks, and statistical distributions.

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

## Usage

```python
from symposium.visualization import TextVisualizer, NetworkAnalyzer, DistributionPlotter

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
```

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
