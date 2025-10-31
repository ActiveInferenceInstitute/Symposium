# PCA Analysis Visualization Guide

## Overview

This guide describes the comprehensive Principal Component Analysis (PCA) visualizations available in the Symposium package. These visualizations help understand how PCA reduces dimensionality, which features contribute most to each component, and how documents cluster in the reduced space.

## Available PCA Visualizations

### 1. Scree Plot - Variance Explained
**File**: `pca_analysis_scree_plot.png`

Shows how much variance is explained by each principal component:
- **Individual Variance**: Bar chart showing variance per component
- **Cumulative Variance**: Line plot showing cumulative variance explained
- **Thresholds**: 80% and 90% variance markers

**Interpretation**:
- Steep drops indicate important components
- Elbow point suggests optimal number of components
- Components after elbow contribute little variance

### 2. Loadings Plot - Feature Contributions
**File**: `pca_analysis_loadings.png`

Displays which terms/features contribute most to each component:
- **Positive Loadings**: Features that increase component scores (green bars)
- **Negative Loadings**: Features that decrease component scores (red bars)
- **Top N Features**: Typically shows top 15 features per component

**Interpretation**:
- High positive loadings → feature strongly associated with component
- High negative loadings → feature inversely associated with component
- Helps interpret what each component represents

### 3. Biplot - Scores and Loadings Combined
**File**: `pca_analysis_biplot.png`

Combines document scores (points) with feature loadings (arrows):
- **Points**: Document positions in PC space
- **Arrows**: Feature contribution directions
- **Colors**: Document categories/labels

**Interpretation**:
- Documents close together are similar
- Arrow direction shows feature influence
- Arrow length indicates feature importance
- Documents near arrow tips have high values for that feature

### 4. Loadings Heatmap - All Components
**File**: `pca_analysis_loadings_heatmap.png`

Heatmap showing feature loadings across all components:
- **Rows**: Top features (terms)
- **Columns**: Principal components
- **Colors**: Red (negative) to Blue (positive)

**Interpretation**:
- Patterns reveal feature groupings
- Cross-component patterns show feature relationships
- Helps identify redundant features

### 5. Component Correlation Matrix
**File**: `pca_analysis_component_correlations.png`

Shows correlations between principal components:
- **Diagonal**: Perfect correlation (1.0)
- **Off-diagonal**: Inter-component correlations

**Interpretation**:
- Should be near zero for orthogonal components
- High correlations indicate potential issues
- Validates PCA assumptions

### 6. 3D Component Visualization
**File**: `pca_analysis_3d_components.png`

Three-dimensional plot of first three components:
- **3D Scatter**: Documents in PC1-PC2-PC3 space
- **Categories**: Color-coded by document type
- **Viewing Angle**: Optimized for clarity

**Interpretation**:
- Shows document clustering in 3D
- Reveals relationships not visible in 2D
- Helps understand complex patterns

### 7. Loadings Table (CSV)
**File**: `pca_analysis_loadings_table.csv`

Structured data export of all loadings:
- Component number and variance explained
- Feature names and loading values
- Positive/negative classifications
- Rankings within each component

**Use Cases**:
- Further statistical analysis
- Custom visualizations
- Reproducible research
- Integration with other tools

## How PCA Works

### Mathematical Foundation

PCA transforms data into a new coordinate system where:
1. **First component (PC1)** has maximum variance
2. **Second component (PC2)** has maximum remaining variance (orthogonal to PC1)
3. Each subsequent component maximizes remaining variance

### Key Concepts

**Variance Explained**:
- Proportion of total variance captured by each component
- High variance = important component
- Cumulative variance shows information retention

**Loadings**:
- Weights showing feature contribution to components
- Range from -1 to +1
- High absolute values indicate strong influence

**Scores**:
- Document positions in new coordinate system
- Calculated from original features × loadings
- Used for visualization and analysis

**Orthogonality**:
- Components are uncorrelated (orthogonal)
- Each captures independent variation
- Enables efficient dimension reduction

## Interpretation Guide

### Understanding Component Meaning

Each component represents a latent concept derived from feature patterns:

**Example Component Interpretations**:
- PC1 might represent "technical depth" (equations, algorithms vs. general concepts)
- PC2 might represent "application focus" (theory vs. practice)
- PC3 might represent "domain specificity" (broad vs. narrow)

**Steps to Interpret**:
1. Examine top positive loadings → "high end" of component
2. Examine top negative loadings → "low end" of component
3. Compare documents at extremes of component scores
4. Assign meaningful label based on patterns

### Document Clustering

Documents cluster when they share similar feature patterns:

**Cluster Analysis**:
- Tight clusters → homogeneous document group
- Scattered points → heterogeneous documents
- Outliers → unique or unusual documents
- Gradients → continuous variation

### Feature Relationships

Loadings reveal feature co-occurrence patterns:

**Pattern Types**:
- Parallel arrows (biplot) → features co-occur
- Opposite arrows → features anti-correlate
- Perpendicular arrows → features independent
- Same direction, different lengths → varying importance

## Usage Examples

### Running Comprehensive PCA Analysis

```bash
# Via CLI - automatically includes PCA analysis
symposium visualize all \
    --input-dir outputs/2025_symposium \
    --output-dir outputs/visualizations \
    --method pca \
    --n-components 50
```

### Python API Usage

```python
from symposium.visualization import PCAAnalyzer
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer

# Setup
analyzer = PCAAnalyzer()
vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
tfidf_matrix = vectorizer.fit_transform(documents)

# Fit PCA
pca = PCA(n_components=50, random_state=42)
reduced_matrix = pca.fit_transform(tfidf_matrix.toarray())

# Generate comprehensive report
results = analyzer.create_comprehensive_pca_report(
    pca=pca,
    reduced_matrix=reduced_matrix,
    vectorizer=vectorizer,
    labels=document_labels,
    output_dir="outputs/pca_analysis",
    prefix="analysis"
)

# Individual visualizations
analyzer.create_scree_plot(pca, "outputs/scree.png")
analyzer.create_loadings_plot(pca, vectorizer, "outputs/loadings.png")
analyzer.create_biplot(pca, reduced_matrix, vectorizer, labels, "outputs/biplot.png")
```

## Best Practices

### Data Preparation

**Preprocessing**:
- Remove stop words and common terms
- Normalize text (lowercase, stemming)
- Filter low-frequency terms
- Consider TF-IDF instead of raw counts

**Sample Size**:
- Need more samples than features
- Minimum 3-5x more samples than components
- Larger samples = more reliable patterns

### Component Selection

**Number of Components**:
- **Scree plot elbow**: Where variance drops sharply
- **80% variance**: Typical threshold for retention
- **Interpretability**: Fewer components easier to understand
- **Application needs**: Task-specific requirements

### Validation

**Quality Checks**:
- Component orthogonality (correlation ≈ 0)
- Variance monotonically decreasing
- Loadings interpretable
- Results stable across samples

## Technical Details

### Implementation

- **Library**: scikit-learn PCA
- **Whitening**: Applied for normalization
- **Solver**: Auto-selected based on data size
- **Convergence**: Full decomposition

### Performance

- **Memory**: O(n × p) for n samples, p features
- **Time**: O(min(n²p, np²)) complexity
- **Optimization**: Randomized SVD for large matrices

### Output Specifications

**Image Formats**:
- **Resolution**: 300 DPI
- **Format**: PNG with transparency
- **Size**: Optimized for publication
- **Fonts**: Professional, readable

**Data Formats**:
- **CSV**: UTF-8 encoded
- **Headers**: Descriptive column names
- **Precision**: 6 decimal places

## Common Issues and Solutions

### Issue: Too Many Components Needed

**Symptoms**: Need >20 components for 80% variance

**Solutions**:
- Increase feature selection threshold
- Use stronger preprocessing
- Consider non-linear methods (t-SNE, UMAP)
- Domain-specific feature engineering

### Issue: Uninterpretable Components

**Symptoms**: No clear pattern in top loadings

**Solutions**:
- Verify data quality and preprocessing
- Check for multicollinearity
- Reduce feature dimensionality first
- Consider supervised methods

### Issue: Poor Separation

**Symptoms**: All documents cluster together

**Solutions**:
- Documents may be truly similar
- Try alternative distance metrics
- Increase feature specificity
- Check label quality

## References

### Methodology

- Jolliffe, I. T. (2002). *Principal Component Analysis*. Springer.
- Abdi, H., & Williams, L. J. (2010). Principal component analysis. *Wiley Interdisciplinary Reviews: Computational Statistics*, 2(4), 433-459.

### Implementation

- Pedregosa et al. (2011). Scikit-learn: Machine Learning in Python. *JMLR*, 12, 2825-2830.
- NumPy/SciPy ecosystem for numerical computing

### Visualization

- Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. *Computing in Science & Engineering*, 9(3), 90-95.
- Waskom, M. L. (2021). seaborn: statistical data visualization. *JOSS*, 6(60), 3021.

## See Also

- [Visualization Module Documentation](README.md)
- [Active Inference Symposium Data](../../data/README.md)
- [CLI Usage Guide](../../docs/user_guide.md)
- [API Documentation](../../docs/api_guide.md)

