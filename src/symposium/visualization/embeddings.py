"""Text embedding and dimension reduction visualizations."""

import os
import logging
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any, Set
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
            method: Reduction method ('pca', 'lsa', 'tsne', 'umap', 'isomap', 'nmf', 'lda')

        Returns:
            Tuple of (reduced_matrix, vectorizer, reducer)
        """
        try:
            # Adjust TF-IDF parameters based on dataset size
            n_docs = len(documents)
            # For small datasets, use min_df=1 to allow more features
            min_doc_freq = 1 if n_docs < 10 else 2
            
            # TF-IDF vectorization with improved parameters
            vectorizer = TfidfVectorizer(
                max_features=10000,  # Increased for better representation
                stop_words='english',
                min_df=min_doc_freq,  # Adaptive minimum document frequency
                max_df=0.90,  # Maximum document frequency
                ngram_range=(1, 2),  # Include bigrams
                sublinear_tf=True  # Apply sublinear scaling
            )
            tfidf_matrix = vectorizer.fit_transform(documents)
            
            # Calculate maximum possible components based on data dimensions
            n_samples, n_features = tfidf_matrix.shape
            max_components = min(n_samples, n_features)
            
            # Adjust n_components if it exceeds maximum possible
            if n_components > max_components:
                logger.warning(
                    f"Requested {n_components} components but only {max_components} available "
                    f"(n_samples={n_samples}, n_features={n_features}). Using {max_components} components."
                )
                n_components = max_components

            if method.lower() == "pca":
                # Enhanced PCA with whitening
                # Ensure we have at least 1 component
                if n_components < 1:
                    logger.error(f"Cannot perform PCA: need at least 1 component, but max is {max_components}")
                    return None, None, None
                    
                reducer = PCA(
                    n_components=n_components,
                    random_state=self.random_state,
                    whiten=True  # Normalize components
                )
                reduced_matrix = reducer.fit_transform(tfidf_matrix.toarray())

            elif method.lower() == "lsa":
                # Latent Semantic Analysis (Truncated SVD)
                reducer = TruncatedSVD(
                    n_components=n_components,
                    random_state=self.random_state,
                    algorithm='randomized'  # Faster for large matrices
                )
                reduced_matrix = reducer.fit_transform(tfidf_matrix)

            elif method.lower() == "tsne":
                # Enhanced t-SNE with better parameters
                # First reduce with PCA to avoid memory issues
                pca_temp = PCA(n_components=min(100, tfidf_matrix.shape[1] - 1), random_state=self.random_state)
                tfidf_reduced = pca_temp.fit_transform(tfidf_matrix.toarray())

                from sklearn.manifold import TSNE
                reducer = TSNE(
                    n_components=n_components,
                    random_state=self.random_state,
                    perplexity=min(30, len(documents) - 1),  # Adaptive perplexity
                    learning_rate=200.0,
                    max_iter=1000,  # Use max_iter instead of n_iter
                    init='pca'  # Better initialization
                )
                reduced_matrix = reducer.fit_transform(tfidf_reduced)
                vectorizer = None  # t-SNE doesn't use vectorizer for feature names

            elif method.lower() == "umap":
                # UMAP for non-linear dimension reduction
                try:
                    from umap import UMAP
                    reducer = UMAP(
                        n_components=n_components,
                        random_state=self.random_state,
                        n_neighbors=min(15, len(documents) - 1),
                        min_dist=0.1,
                        metric='cosine'  # Better for text data
                    )
                    reduced_matrix = reducer.fit_transform(tfidf_matrix.toarray())
                    vectorizer = None  # UMAP doesn't use vectorizer for feature names
                except ImportError:
                    logger.warning("UMAP not available, falling back to PCA")
                    reducer = PCA(n_components=n_components, random_state=self.random_state)
                    reduced_matrix = reducer.fit_transform(tfidf_matrix.toarray())

            elif method.lower() == "isomap":
                # Isomap for manifold learning
                try:
                    from sklearn.manifold import Isomap
                    reducer = Isomap(
                        n_components=n_components,
                        n_neighbors=min(10, len(documents) - 1)
                    )
                    reduced_matrix = reducer.fit_transform(tfidf_matrix.toarray())
                    vectorizer = None  # Isomap doesn't use vectorizer for feature names
                except Exception as e:
                    logger.warning(f"Isomap failed: {e}, falling back to PCA")
                    reducer = PCA(n_components=n_components, random_state=self.random_state)
                    reduced_matrix = reducer.fit_transform(tfidf_matrix.toarray())

            elif method.lower() == "nmf":
                # Non-negative Matrix Factorization
                from sklearn.decomposition import NMF
                reducer = NMF(
                    n_components=n_components,
                    random_state=self.random_state,
                    max_iter=1000,
                    alpha_W=0.1,
                    alpha_H=0.1
                )
                # NMF requires non-negative input, use TF-IDF as is (already non-negative)
                reduced_matrix = reducer.fit_transform(tfidf_matrix)

            elif method.lower() == "lda":
                # Latent Dirichlet Allocation (topic modeling)
                from sklearn.decomposition import LatentDirichletAllocation
                reducer = LatentDirichletAllocation(
                    n_components=n_components,
                    random_state=self.random_state,
                    max_iter=100,
                    learning_method='batch'
                )
                reduced_matrix = reducer.fit_transform(tfidf_matrix)

            else:
                available_methods = ['pca', 'lsa', 'tsne', 'umap', 'isomap', 'nmf', 'lda']
                raise ValueError(f"Unknown reduction method: {method}. Available: {available_methods}")

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

        # Custom stop words for word clouds
        self.custom_stopwords = {
            'and', 'the', 'of', 'to', 'in', 'a', 'i', 'for', 'that', 'is',
            'on', 'as', 'have', 'with', 'are', 'be', 'it', 'more', 'this',
            'my', 'which', 'but', 'from', 'would', 'or', 'into', 'about',
            # Additional common words to exclude
            'am', 'an', 'at', 'by', 'do', 'go', 'if', 'me', 'no', 'so',
            'up', 'we', 'you', 'all', 'can', 'did', 'get', 'had', 'has',
            'her', 'him', 'his', 'how', 'its', 'let', 'may', 'new', 'not',
            'now', 'old', 'our', 'out', 'put', 'see', 'she', 'too', 'use',
            'way', 'who', 'why', 'yes', 'yet', 'what', 'when', 'where',
            'will', 'work', 'was', 'were', 'been', 'being', 'there', 'here'
        }

    def _setup_matplotlib(self):
        """Setup matplotlib for non-GUI environments."""
        plt.style.use('default')
        sns.set_palette("husl")

    def create_word_cloud(self, documents: List[str], title: str, output_path: Path,
                         custom_stopwords: Optional[set] = None) -> bool:
        """Create word cloud visualization.

        Args:
            documents: List of text documents
            title: Plot title
            output_path: Output file path
            custom_stopwords: Optional custom stop words to exclude

        Returns:
            Success status
        """
        try:
            # Combine all documents
            text = ' '.join(documents)

            # Use custom stop words or default
            stopwords = custom_stopwords or self.custom_stopwords

            # Generate word cloud with enhanced parameters
            wordcloud = WordCloud(
                width=1600,
                height=800,
                background_color='white',
                max_words=150,
                colormap='plasma',
                contour_width=2,
                contour_color='navy',
                min_font_size=8,
                max_font_size=120,
                font_step=2,
                prefer_horizontal=0.8,
                relative_scaling=0.7,
                normalize_plurals=True,
                stopwords=stopwords
            ).generate(text)

            # Plot with enhanced styling
            plt.figure(figsize=(24, 12))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title(title, fontsize=24, fontweight='bold', pad=20)
            plt.tight_layout()

            # Save
            output_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()

            logger.info(f"Enhanced word cloud saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating word cloud: {e}")
            return False

    def create_column_word_clouds(self, participants: Dict[str, Dict[str, Any]],
                                  output_dir: Path, custom_stopwords: Optional[set] = None) -> bool:
        """Create per-column word clouds for participant data.

        Args:
            participants: Dictionary of participant data
            output_dir: Output directory for word clouds
            custom_stopwords: Optional custom stop words to exclude

        Returns:
            Success status
        """
        try:
            # Define columns to create word clouds for (text-rich columns)
            text_columns = {
                'background': 'Background & Prior Works',
                'pragmatic_value': 'Pragmatic Value (Useful for Symposium)',
                'epistemic_value': 'Epistemic Value (Interesting to Learn)',
                'active_inference_application': 'Active Inference Applications',
                'challenges': 'Challenges in Active Inference',
                'learning_needs': 'Learning Needs & Resource Development',
                'future_impact': 'Future Impact Vision (2026)',
                'comments': 'Additional Comments & Questions'
            }

            stopwords = custom_stopwords or self.custom_stopwords
            output_dir.mkdir(parents=True, exist_ok=True)

            # Create overall word cloud first
            all_texts = []
            for participant_data in participants.values():
                for field in text_columns.keys():
                    text = participant_data.get(field, '')
                    if text and str(text).strip():
                        all_texts.append(str(text))

            if all_texts:
                overall_path = output_dir / "word_cloud_overall.png"
                self.create_word_cloud(all_texts, "Overall Participant Responses Word Cloud", overall_path, stopwords)

            # Create per-column word clouds
            for column_key, column_title in text_columns.items():
                column_texts = []

                for participant_data in participants.values():
                    text = participant_data.get(column_key, '')
                    if text and str(text).strip():
                        column_texts.append(str(text))

                if column_texts:
                    # Clean column key for filename
                    safe_column_key = column_key.replace('_', '_')
                    column_path = output_dir / f"word_cloud_{safe_column_key}.png"

                    # Create column-specific word cloud
                    self.create_word_cloud(
                        column_texts,
                        f"{column_title} Word Cloud",
                        column_path,
                        stopwords
                    )

                    logger.info(f"Created word cloud for column: {column_title}")

            logger.info(f"Created {len(text_columns) + 1} word clouds in {output_dir}")
            return True

        except Exception as e:
            logger.error(f"Error creating column word clouds: {e}")
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

