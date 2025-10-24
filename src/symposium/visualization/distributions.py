"""Distribution and statistical visualization tools."""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy import stats

logger = logging.getLogger(__name__)


class DistributionPlotter:
    """Statistical distribution and analysis plotting tools."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize distribution plotter.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self._setup_seaborn()

    def _setup_seaborn(self):
        """Setup seaborn styling."""
        sns.set_style("whitegrid")
        sns.set_palette("husl")

    def plot_document_length_distribution(
        self,
        documents: List[str],
        labels: List[str],
        title: str,
        output_path: Path
    ) -> bool:
        """Plot document length distribution.

        Args:
            documents: List of text documents
            labels: Labels for each document
            title: Plot title
            output_path: Output file path

        Returns:
            Success status
        """
        try:
            # Calculate document lengths
            lengths = [len(doc.split()) for doc in documents]

            # Create DataFrame for easier plotting
            df = pd.DataFrame({
                'length': lengths,
                'label': labels
            })

            # Plot
            plt.figure(figsize=(12, 8))

            # Box plot
            plt.subplot(2, 2, 1)
            sns.boxplot(data=df, x='label', y='length')
            plt.title('Document Length by Category', fontweight='bold')
            plt.xlabel('Category')
            plt.ylabel('Word Count')
            plt.xticks(rotation=45)

            # Histogram
            plt.subplot(2, 2, 2)
            sns.histplot(data=df, x='length', hue='label', alpha=0.7)
            plt.title('Document Length Distribution', fontweight='bold')
            plt.xlabel('Word Count')
            plt.ylabel('Count')

            # KDE plot
            plt.subplot(2, 2, 3)
            sns.kdeplot(data=df, x='length', hue='label', fill=True, alpha=0.3)
            plt.title('Document Length Density', fontweight='bold')
            plt.xlabel('Word Count')
            plt.ylabel('Density')

            # Statistics table
            plt.subplot(2, 2, 4)
            plt.axis('off')

            # Calculate statistics
            stats_text = []
            for label in df['label'].unique():
                label_data = df[df['label'] == label]['length']
                stats_text.append(f"{label}:")
                stats_text.append(f"  Mean: {label_data.mean():.1f}")
                stats_text.append(f"  Std:  {label_data.std():.1f}")
                stats_text.append(f"  Min:  {label_data.min()}")
                stats_text.append(f"  Max:  {label_data.max()}")
                stats_text.append("")

            plt.text(0.1, 0.9, '\n'.join(stats_text[:-1]), fontsize=10,
                    verticalalignment='top', fontfamily='monospace')

            plt.suptitle(title, fontsize=14, fontweight='bold')
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()

            logger.info(f"Document length distribution plot saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating document length distribution plot: {e}")
            return False

    def plot_tfidf_distribution(
        self,
        tfidf_matrix: Any,
        vectorizer: TfidfVectorizer,
        title: str,
        output_path: Path,
        top_n: int = 50
    ) -> bool:
        """Plot TF-IDF score distributions.

        Args:
            tfidf_matrix: TF-IDF matrix
            vectorizer: TF-IDF vectorizer
            title: Plot title
            output_path: Output file path
            top_n: Number of top terms to show

        Returns:
            Success status
        """
        try:
            # Get top terms by average TF-IDF score
            feature_names = vectorizer.get_feature_names_out()
            tfidf_sum = np.asarray(tfidf_matrix.sum(axis=0)).ravel()
            top_indices = tfidf_sum.argsort()[-top_n:][::-1]
            top_terms = [feature_names[i] for i in top_indices]
            top_scores = tfidf_sum[top_indices]

            # Calculate confidence intervals
            tfidf_data = tfidf_matrix[:, top_indices].toarray()
            means = np.mean(tfidf_data, axis=0)
            stds = np.std(tfidf_data, axis=0)

            # Handle potential division by zero
            with np.errstate(divide='ignore', invalid='ignore'):
                cis = stats.t.interval(0.95, tfidf_matrix.shape[0]-1,
                                     loc=means, scale=stds/np.sqrt(tfidf_matrix.shape[0]))
                cis = np.nan_to_num(cis, nan=0.0, posinf=0.0, neginf=0.0)

            # Plot
            plt.figure(figsize=(15, 10))

            # Bar plot with error bars
            plt.subplot(2, 1, 1)
            plt.errorbar(range(len(top_terms)), means, yerr=cis[1]-means,
                        fmt='o', capsize=5, color='skyblue', alpha=0.7)
            plt.xticks(range(len(top_terms)), top_terms, rotation=45, ha='right')
            plt.xlabel('Terms')
            plt.ylabel('Mean TF-IDF Score')
            plt.title('Top Terms by TF-IDF Score (with 95% CI)', fontweight='bold')
            plt.grid(True, alpha=0.3)

            # Heatmap of TF-IDF matrix (subset)
            plt.subplot(2, 1, 2)
            n_docs_show = min(50, tfidf_matrix.shape[0])
            n_terms_show = min(20, len(top_terms))

            heatmap_data = tfidf_matrix[:n_docs_show, top_indices[:n_terms_show]].toarray()
            sns.heatmap(
                heatmap_data,
                xticklabels=top_terms[:n_terms_show],
                yticklabels=[f"Doc {i+1}" for i in range(n_docs_show)],
                cmap="YlOrRd",
                cbar_kws={'label': 'TF-IDF Score'}
            )
            plt.title('TF-IDF Score Heatmap (Top Terms)', fontweight='bold')
            plt.xlabel('Terms')
            plt.ylabel('Documents')
            plt.xticks(rotation=45, ha='right')

            plt.suptitle(title, fontsize=14, fontweight='bold')
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()

            logger.info(f"TF-IDF distribution plot saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating TF-IDF distribution plot: {e}")
            return False

    def plot_category_comparison(
        self,
        documents: List[str],
        labels: List[str],
        title: str,
        output_path: Path
    ) -> bool:
        """Plot comparison between categories.

        Args:
            documents: List of text documents
            labels: Category labels for each document
            title: Plot title
            output_path: Output file path

        Returns:
            Success status
        """
        try:
            # Calculate statistics for each category
            unique_labels = list(set(labels))
            stats_data = []

            for label in unique_labels:
                label_docs = [doc for doc, l in zip(documents, labels) if l == label]
                lengths = [len(doc.split()) for doc in label_docs]

                stats_data.append({
                    'category': label,
                    'count': len(label_docs),
                    'mean_length': np.mean(lengths),
                    'std_length': np.std(lengths),
                    'min_length': np.min(lengths),
                    'max_length': np.max(lengths)
                })

            # Create DataFrame
            df = pd.DataFrame(stats_data)

            # Plot
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))

            # Document count by category
            axes[0, 0].bar(range(len(unique_labels)), df['count'])
            axes[0, 0].set_xticks(range(len(unique_labels)))
            axes[0, 0].set_xticklabels(df['category'], rotation=45, ha='right')
            axes[0, 0].set_title('Document Count by Category', fontweight='bold')
            axes[0, 0].set_ylabel('Count')

            # Mean length by category
            axes[0, 1].bar(range(len(unique_labels)), df['mean_length'], yerr=df['std_length'], capsize=5)
            axes[0, 1].set_xticks(range(len(unique_labels)))
            axes[0, 1].set_xticklabels(df['category'], rotation=45, ha='right')
            axes[0, 1].set_title('Mean Document Length by Category', fontweight='bold')
            axes[0, 1].set_ylabel('Word Count')

            # Box plot of lengths
            lengths_by_category = [np.array([len(doc.split()) for doc, l in zip(documents, labels) if l == label])
                                 for label in unique_labels]
            axes[1, 0].boxplot(lengths_by_category, labels=unique_labels)
            axes[1, 0].set_title('Document Length Distribution by Category', fontweight='bold')
            axes[1, 0].set_ylabel('Word Count')
            axes[1, 0].tick_params(axis='x', rotation=45)

            # Length vs count scatter
            axes[1, 1].scatter(df['count'], df['mean_length'], s=df['count']*10, alpha=0.7)
            for i, label in enumerate(df['category']):
                axes[1, 1].annotate(label, (df['count'][i], df['mean_length'][i]),
                                  xytext=(5, 5), textcoords='offset points', fontsize=8)
            axes[1, 1].set_xlabel('Document Count')
            axes[1, 1].set_ylabel('Mean Word Count')
            axes[1, 1].set_title('Category Size vs Mean Length', fontweight='bold')
            axes[1, 1].grid(True, alpha=0.3)

            plt.suptitle(title, fontsize=16, fontweight='bold')
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()

            logger.info(f"Category comparison plot saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating category comparison plot: {e}")
            return False

