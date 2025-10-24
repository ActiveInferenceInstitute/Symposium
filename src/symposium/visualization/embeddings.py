"""Text embedding and dimension reduction visualizations."""

import os
import logging
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.manifold import TSNE
from collections import Counter
from wordcloud import WordCloud
import matplotlib.cm as cm
import matplotlib.gridspec as gridspec
from mpl_toolkits.mplot3d import Axes3D
from adjustText import adjust_text
import matplotlib.patheffects as path_effects

logger = logging.getLogger(__name__)


class DimensionReducer:
    """Handles dimension reduction techniques."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize dimension reducer.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.random_state = 42

    def perform_tfidf_and_reduction(
        self,
        documents: List[str],
        n_components: int = 50,
        method: str = "pca"
    ) -> Tuple[Optional[np.ndarray], Optional[TfidfVectorizer], Optional[Any]]:
        """Perform TF-IDF vectorization and dimension reduction.

        Args:
            documents: List of text documents
            n_components: Number of components for reduction
            method: Reduction method ('pca', 'lsa', 'tsne')

        Returns:
            Tuple of (reduced_matrix, vectorizer, reducer)
        """
        try:
            # TF-IDF vectorization
            vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                min_df=1,
                max_df=0.95
            )
            tfidf_matrix = vectorizer.fit_transform(documents)

            if method.lower() == "pca":
                reducer = PCA(n_components=n_components, random_state=self.random_state)
                reduced_matrix = reducer.fit_transform(tfidf_matrix.toarray())

            elif method.lower() == "lsa":
                reducer = TruncatedSVD(n_components=n_components, random_state=self.random_state)
                reduced_matrix = reducer.fit_transform(tfidf_matrix)

            elif method.lower() == "tsne":
                # For t-SNE, first reduce with PCA to avoid memory issues
                pca_temp = PCA(n_components=min(50, tfidf_matrix.shape[1] - 1), random_state=self.random_state)
                tfidf_reduced = pca_temp.fit_transform(tfidf_matrix.toarray())

                from sklearn.manifold import TSNE
                reducer = TSNE(n_components=2, random_state=self.random_state, perplexity=30)
                reduced_matrix = reducer.fit_transform(tfidf_reduced)
                vectorizer = None  # t-SNE doesn't use vectorizer for feature names

            else:
                raise ValueError(f"Unknown reduction method: {method}")

            logger.info(f"Reduced {len(documents)} documents to {n_components}D using {method}")
            return reduced_matrix, vectorizer, reducer

        except Exception as e:
            logger.error(f"Error in dimension reduction: {e}")
            return None, None, None

    def get_top_features(self, vectorizer: TfidfVectorizer, reducer: Any, n_features: int = 20) -> Dict[str, List[str]]:
        """Get top features for each component.

        Args:
            vectorizer: TF-IDF vectorizer
            reducer: Dimension reduction model
            n_features: Number of top features per component

        Returns:
            Dictionary mapping component names to feature lists
        """
        try:
            if not hasattr(reducer, 'components_'):
                return {}

            feature_names = vectorizer.get_feature_names_out()
            n_components = min(n_features, reducer.components_.shape[0])

            top_features = {}
            for i in range(n_components):
                component = reducer.components_[i]
                top_indices = component.argsort()[-n_features:][::-1]
                top_features[f"Component_{i+1}"] = [feature_names[idx] for idx in top_indices]

            return top_features

        except Exception as e:
            logger.error(f"Error getting top features: {e}")
            return {}


class TextVisualizer:
    """Text analysis and visualization tools."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize text visualizer.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.reducer = DimensionReducer(config)
        self._setup_matplotlib()

    def _setup_matplotlib(self):
        """Setup matplotlib for non-GUI environments."""
        plt.style.use('default')
        sns.set_palette("husl")

    def create_word_cloud(self, documents: List[str], title: str, output_path: Path) -> bool:
        """Create word cloud visualization.

        Args:
            documents: List of text documents
            title: Plot title
            output_path: Output file path

        Returns:
            Success status
        """
        try:
            # Combine all documents
            text = ' '.join(documents)

            # Generate word cloud
            wordcloud = WordCloud(
                width=1200,
                height=600,
                background_color='white',
                max_words=100,
                colormap='viridis',
                contour_width=1,
                contour_color='steelblue'
            ).generate(text)

            # Plot
            plt.figure(figsize=(20, 10))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title(title, fontsize=20, fontweight='bold')
            plt.tight_layout()

            # Save
            output_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()

            logger.info(f"Word cloud saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating word cloud: {e}")
            return False

    def plot_dimension_reduction(
        self,
        reduced_matrix: np.ndarray,
        labels: List[str],
        filenames: List[str],
        title: str,
        output_path: Path,
        vectorizer: Optional[TfidfVectorizer] = None,
        reducer: Optional[Any] = None
    ) -> bool:
        """Create dimension reduction plot.

        Args:
            reduced_matrix: Reduced dimension matrix
            labels: Labels for each point
            filenames: Original filenames
            title: Plot title
            output_path: Output file path
            vectorizer: Optional TF-IDF vectorizer for feature names
            reducer: Optional reducer object for component analysis

        Returns:
            Success status
        """
        try:
            if reduced_matrix is None or len(reduced_matrix) == 0:
                logger.error("Empty or None reduced matrix")
                return False

            # Handle different dimensions
            if reduced_matrix.shape[1] == 2:
                return self._plot_2d(reduced_matrix, labels, filenames, title, output_path, vectorizer, reducer)
            elif reduced_matrix.shape[1] >= 3:
                return self._plot_3d(reduced_matrix, labels, filenames, title, output_path)
            else:
                logger.error(f"Unsupported number of dimensions: {reduced_matrix.shape[1]}")
                return False

        except Exception as e:
            logger.error(f"Error creating dimension reduction plot: {e}")
            return False

    def _plot_2d(
        self,
        reduced_matrix: np.ndarray,
        labels: List[str],
        filenames: List[str],
        title: str,
        output_path: Path,
        vectorizer: Optional[TfidfVectorizer],
        reducer: Optional[Any]
    ) -> bool:
        """Create 2D dimension reduction plot."""
        try:
            fig, ax = plt.subplots(figsize=(16, 12))

            # Create color map for unique labels
            unique_labels = list(set(labels))
            colors = plt.cm.get_cmap('tab20')(np.linspace(0, 1, len(unique_labels)))
            color_dict = dict(zip(unique_labels, colors))

            # Plot points
            for i, label in enumerate(labels):
                color = color_dict[label]
                ax.scatter(
                    reduced_matrix[i, 0],
                    reduced_matrix[i, 1],
                    c=[color],
                    s=100,
                    alpha=0.7,
                    label=label if label not in [l for l in ax.get_legend_handles_labels()[1] if l == label] else ""
                )

            # Add text labels with collision avoidance
            texts = []
            for i, filename in enumerate(filenames):
                short_name = Path(filename).stem[:20]
                text = ax.text(
                    reduced_matrix[i, 0],
                    reduced_matrix[i, 1],
                    short_name,
                    fontsize=8,
                    ha='center',
                    va='center',
                    weight='bold'
                )
                text.set_path_effects([
                    path_effects.Stroke(linewidth=2, foreground='white'),
                    path_effects.Normal()
                ])
                texts.append(text)

            # Adjust text positions to minimize overlap
            try:
                adjust_text(texts, arrowprops=dict(arrowstyle='->', color='red', alpha=0.5))
            except Exception as e:
                logger.warning(f"Text adjustment failed: {e}")

            # Formatting
            ax.set_title(title, fontsize=16, fontweight='bold')
            ax.set_xlabel('Component 1', fontsize=12)
            ax.set_ylabel('Component 2', fontsize=12)
            ax.grid(True, alpha=0.3)

            # Add top terms if available
            if vectorizer is not None and reducer is not None and hasattr(reducer, 'components_'):
                try:
                    feature_names = vectorizer.get_feature_names_out()
                    for i, comp_name in enumerate(['x', 'y']):
                        if i < reducer.components_.shape[0]:
                            top_features = feature_names[reducer.components_[i].argsort()[-5:]]
                            ax.text(
                                0.02, 0.98 - i*0.05,
                                f"{comp_name}-axis: {', '.join(top_features)}",
                                transform=ax.transAxes,
                                fontsize=9,
                                verticalalignment='top',
                                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8)
                            )
                except Exception as e:
                    logger.warning(f"Could not add feature annotations: {e}")

            # Legend
            if len(unique_labels) <= 20:  # Only show legend if reasonable number of labels
                handles, legend_labels = ax.get_legend_handles_labels()
                if handles:
                    ax.legend(handles[:10], legend_labels[:10], loc='upper right', fontsize=8)

            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()

            logger.info(f"2D plot saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating 2D plot: {e}")
            return False

    def _plot_3d(
        self,
        reduced_matrix: np.ndarray,
        labels: List[str],
        filenames: List[str],
        title: str,
        output_path: Path
    ) -> bool:
        """Create 3D dimension reduction plot."""
        try:
            fig = plt.figure(figsize=(20, 16))
            ax = fig.add_subplot(111, projection='3d')

            # Color mapping
            unique_labels = list(set(labels))
            colors = plt.cm.get_cmap('tab20')(np.linspace(0, 1, len(unique_labels)))
            color_dict = dict(zip(unique_labels, colors))

            # Plot points
            for label in unique_labels:
                indices = [i for i, l in enumerate(labels) if l == label]
                if indices:
                    color = color_dict[label]
                    ax.scatter(
                        reduced_matrix[indices, 0],
                        reduced_matrix[indices, 1],
                        reduced_matrix[indices, 2],
                        c=[color],
                        s=100,
                        alpha=0.7,
                        label=label
                    )

            # Add labels
            for i, filename in enumerate(filenames):
                short_name = Path(filename).stem[:15]
                ax.text(
                    reduced_matrix[i, 0],
                    reduced_matrix[i, 1],
                    reduced_matrix[i, 2],
                    short_name,
                    fontsize=6,
                    ha='center',
                    va='center'
                )

            # Formatting
            ax.set_xlabel('Component 1', fontsize=12)
            ax.set_ylabel('Component 2', fontsize=12)
            ax.set_zlabel('Component 3', fontsize=12)
            ax.set_title(title, fontsize=16, fontweight='bold')

            # Legend
            ax.legend(loc='upper right', fontsize=8)

            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()

            logger.info(f"3D plot saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating 3D plot: {e}")
            return False

    def plot_term_frequency(
        self,
        documents: List[str],
        title: str,
        output_path: Path,
        max_terms: int = 50
    ) -> bool:
        """Plot term frequency distribution.

        Args:
            documents: List of text documents
            title: Plot title
            output_path: Output file path
            max_terms: Maximum number of terms to show

        Returns:
            Success status
        """
        try:
            # Calculate term frequencies
            all_terms = ' '.join(documents).split()
            term_freq = Counter(all_terms)

            # Get top terms
            top_terms = dict(term_freq.most_common(max_terms))

            # Plot
            plt.figure(figsize=(15, 10))
            terms, frequencies = zip(*top_terms.items())

            plt.bar(range(len(terms)), frequencies)
            plt.xticks(range(len(terms)), terms, rotation=45, ha='right')
            plt.xlabel('Terms', fontsize=12)
            plt.ylabel('Frequency', fontsize=12)
            plt.title(title, fontsize=16, fontweight='bold')
            plt.yscale('log')
            plt.grid(True, alpha=0.3)

            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()

            logger.info(f"Term frequency plot saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating term frequency plot: {e}")
            return False

