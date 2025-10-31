"""Enhanced PCA Analysis and Visualization Module.

This module provides comprehensive Principal Component Analysis (PCA) visualizations including:
- Scree plots (variance explained)
- Loading plots (feature contributions)
- Biplots (scores + loadings combined)
- Component correlation heatmaps
- Cumulative variance plots
- Top contributing terms per component
- 3D rotation analysis
"""

import os
import logging
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
import matplotlib.gridspec as gridspec
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.patches as mpatches

logger = logging.getLogger(__name__)


class PCAAnalyzer:
    """Comprehensive PCA analysis and visualization toolkit."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize PCA analyzer.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.random_state = 42
        self._setup_matplotlib()

    def _setup_matplotlib(self):
        """Setup matplotlib for high-quality visualizations."""
        plt.style.use('default')
        sns.set_context("notebook", font_scale=1.2)
        sns.set_palette("husl")

    def create_scree_plot(
        self,
        pca: PCA,
        output_path: Path,
        title: str = "PCA Scree Plot - Variance Explained"
    ) -> bool:
        """Create scree plot showing variance explained by each component.

        Args:
            pca: Fitted PCA object
            output_path: Output file path
            title: Plot title

        Returns:
            Success status
        """
        try:
            explained_variance = pca.explained_variance_ratio_
            cumulative_variance = np.cumsum(explained_variance)
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
            
            # Individual variance explained
            components = range(1, len(explained_variance) + 1)
            ax1.bar(components, explained_variance, alpha=0.7, color='steelblue', edgecolor='black')
            ax1.axhline(y=0.05, color='r', linestyle='--', label='5% threshold')
            ax1.set_xlabel('Principal Component', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Proportion of Variance Explained', fontsize=14, fontweight='bold')
            ax1.set_title('Individual Variance Explained', fontsize=16, fontweight='bold')
            ax1.legend(fontsize=12)
            ax1.grid(True, alpha=0.3)
            
            # Cumulative variance explained
            ax2.plot(components, cumulative_variance, 'o-', linewidth=2, markersize=8, color='darkgreen')
            ax2.axhline(y=0.80, color='r', linestyle='--', label='80% variance')
            ax2.axhline(y=0.90, color='orange', linestyle='--', label='90% variance')
            ax2.fill_between(components, cumulative_variance, alpha=0.3, color='green')
            ax2.set_xlabel('Principal Component', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Cumulative Variance Explained', fontsize=14, fontweight='bold')
            ax2.set_title('Cumulative Variance Explained', fontsize=16, fontweight='bold')
            ax2.legend(fontsize=12)
            ax2.grid(True, alpha=0.3)
            ax2.set_ylim([0, 1.05])
            
            # Add text annotations
            var_80_idx = np.argmax(cumulative_variance >= 0.80) + 1
            var_90_idx = np.argmax(cumulative_variance >= 0.90) + 1
            
            ax2.annotate(f'{var_80_idx} components\nfor 80% variance',
                        xy=(var_80_idx, 0.80),
                        xytext=(var_80_idx + 5, 0.70),
                        arrowprops=dict(arrowstyle='->', color='red', lw=2),
                        fontsize=11, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))
            
            plt.suptitle(title, fontsize=18, fontweight='bold', y=1.02)
            plt.tight_layout()
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            logger.info(f"Scree plot saved to {output_path}")
            logger.info(f"Components for 80% variance: {var_80_idx}, 90% variance: {var_90_idx}")
            return True

        except Exception as e:
            logger.error(f"Error creating scree plot: {e}")
            return False

    def create_loadings_plot(
        self,
        pca: PCA,
        vectorizer: TfidfVectorizer,
        output_path: Path,
        n_components: int = 5,
        n_features: int = 15,
        title: str = "PCA Feature Loadings"
    ) -> bool:
        """Create plot showing feature loadings for top components.

        Args:
            pca: Fitted PCA object
            vectorizer: Fitted TF-IDF vectorizer
            output_path: Output file path
            n_components: Number of components to display
            n_features: Number of top features per component
            title: Plot title

        Returns:
            Success status
        """
        try:
            feature_names = vectorizer.get_feature_names_out()
            n_comp = min(n_components, pca.n_components_)
            
            # Create subplots
            fig = plt.figure(figsize=(24, 6 * n_comp))
            gs = gridspec.GridSpec(n_comp, 2, width_ratios=[2, 1])
            
            for i in range(n_comp):
                # Get loadings for this component
                loadings = pca.components_[i]
                
                # Top positive and negative loadings
                top_pos_idx = loadings.argsort()[-n_features:][::-1]
                top_neg_idx = loadings.argsort()[:n_features]
                
                # Positive loadings subplot
                ax_pos = fig.add_subplot(gs[i, 0])
                features_pos = feature_names[top_pos_idx]
                values_pos = loadings[top_pos_idx]
                
                colors_pos = plt.cm.Greens(np.linspace(0.4, 0.9, len(values_pos)))
                bars_pos = ax_pos.barh(features_pos, values_pos, color=colors_pos, edgecolor='black')
                ax_pos.set_xlabel('Loading Value', fontsize=12, fontweight='bold')
                ax_pos.set_title(f'PC{i+1}: Top Positive Loadings\n(Variance: {pca.explained_variance_ratio_[i]:.3%})', 
                               fontsize=14, fontweight='bold')
                ax_pos.grid(True, alpha=0.3, axis='x')
                
                # Add value labels
                for bar in bars_pos:
                    width = bar.get_width()
                    ax_pos.text(width, bar.get_y() + bar.get_height()/2,
                              f'{width:.3f}',
                              ha='left', va='center', fontweight='bold', fontsize=9)
                
                # Negative loadings subplot
                ax_neg = fig.add_subplot(gs[i, 1])
                features_neg = feature_names[top_neg_idx]
                values_neg = loadings[top_neg_idx]
                
                colors_neg = plt.cm.Reds(np.linspace(0.4, 0.9, len(values_neg)))
                bars_neg = ax_neg.barh(features_neg, values_neg, color=colors_neg, edgecolor='black')
                ax_neg.set_xlabel('Loading Value', fontsize=12, fontweight='bold')
                ax_neg.set_title(f'PC{i+1}: Top Negative Loadings', fontsize=14, fontweight='bold')
                ax_neg.grid(True, alpha=0.3, axis='x')
                
                # Add value labels
                for bar in bars_neg:
                    width = bar.get_width()
                    ax_neg.text(width, bar.get_y() + bar.get_height()/2,
                              f'{width:.3f}',
                              ha='right', va='center', fontweight='bold', fontsize=9)
            
            plt.suptitle(title, fontsize=20, fontweight='bold', y=0.995)
            plt.tight_layout()
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            logger.info(f"Loadings plot saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating loadings plot: {e}")
            return False

    def create_biplot(
        self,
        pca: PCA,
        reduced_matrix: np.ndarray,
        vectorizer: TfidfVectorizer,
        labels: List[str],
        output_path: Path,
        pc_x: int = 0,
        pc_y: int = 1,
        n_features: int = 10,
        title: str = "PCA Biplot: Scores and Loadings"
    ) -> bool:
        """Create biplot combining scores and loadings.

        Args:
            pca: Fitted PCA object
            reduced_matrix: PCA-transformed data (scores)
            vectorizer: Fitted TF-IDF vectorizer
            labels: Sample labels
            output_path: Output file path
            pc_x: Principal component for x-axis (0-indexed)
            pc_y: Principal component for y-axis (0-indexed)
            n_features: Number of top features to display
            title: Plot title

        Returns:
            Success status
        """
        try:
            fig, ax = plt.subplots(figsize=(20, 16))
            
            # Plot scores (samples)
            unique_labels = list(set(labels))
            colors = plt.cm.get_cmap('tab20')(np.linspace(0, 1, len(unique_labels)))
            color_dict = dict(zip(unique_labels, colors))
            
            for label in unique_labels:
                indices = [i for i, l in enumerate(labels) if l == label]
                ax.scatter(
                    reduced_matrix[indices, pc_x],
                    reduced_matrix[indices, pc_y],
                    c=[color_dict[label]],
                    s=150,
                    alpha=0.6,
                    label=label,
                    edgecolors='black'
                )
            
            # Plot loadings (features) as arrows
            feature_names = vectorizer.get_feature_names_out()
            loadings_x = pca.components_[pc_x]
            loadings_y = pca.components_[pc_y]
            
            # Scale loadings to match score scale
            score_range = np.abs(reduced_matrix[:, [pc_x, pc_y]]).max(axis=0)
            loading_range = np.abs(pca.components_[[pc_x, pc_y]]).max(axis=1)
            
            # Avoid division by zero
            loading_range[loading_range == 0] = 1e-10
            scaling = score_range / loading_range
            
            # Get top features by magnitude
            loading_magnitudes = np.sqrt(loadings_x**2 + loadings_y**2)
            top_feature_idx = loading_magnitudes.argsort()[-n_features:][::-1]
            
            for idx in top_feature_idx:
                ax.arrow(
                    0, 0,
                    loadings_x[idx] * scaling[0],
                    loadings_y[idx] * scaling[1],
                    head_width=0.1,
                    head_length=0.1,
                    fc='red',
                    ec='red',
                    alpha=0.7,
                    linewidth=2
                )
                ax.text(
                    loadings_x[idx] * scaling[0] * 1.15,
                    loadings_y[idx] * scaling[1] * 1.15,
                    feature_names[idx],
                    fontsize=11,
                    fontweight='bold',
                    ha='center',
                    va='center',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7)
                )
            
            # Formatting
            ax.set_xlabel(f'PC{pc_x+1} ({pca.explained_variance_ratio_[pc_x]:.2%} variance)',
                         fontsize=14, fontweight='bold')
            ax.set_ylabel(f'PC{pc_y+1} ({pca.explained_variance_ratio_[pc_y]:.2%} variance)',
                         fontsize=14, fontweight='bold')
            ax.set_title(title, fontsize=18, fontweight='bold')
            ax.axhline(y=0, color='k', linestyle='--', linewidth=0.5)
            ax.axvline(x=0, color='k', linestyle='--', linewidth=0.5)
            ax.grid(True, alpha=0.3)
            
            # Legend
            if len(unique_labels) <= 15:
                ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
            
            plt.tight_layout()
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            logger.info(f"Biplot saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating biplot: {e}")
            return False

    def create_loadings_heatmap(
        self,
        pca: PCA,
        vectorizer: TfidfVectorizer,
        output_path: Path,
        n_components: int = 10,
        n_features: int = 50,
        title: str = "PCA Loadings Heatmap"
    ) -> bool:
        """Create heatmap of feature loadings across components.

        Args:
            pca: Fitted PCA object
            vectorizer: Fitted TF-IDF vectorizer
            output_path: Output file path
            n_components: Number of components to display
            n_features: Number of top features to display
            title: Plot title

        Returns:
            Success status
        """
        try:
            feature_names = vectorizer.get_feature_names_out()
            n_comp = min(n_components, pca.n_components_)
            
            # Get overall top features across all components
            component_abs = np.abs(pca.components_[:n_comp, :])
            feature_importance = component_abs.sum(axis=0)
            top_feature_idx = feature_importance.argsort()[-n_features:][::-1]
            
            # Create loadings dataframe
            loadings_data = pca.components_[:n_comp, top_feature_idx].T
            loadings_df = pd.DataFrame(
                loadings_data,
                index=feature_names[top_feature_idx],
                columns=[f'PC{i+1}\n({pca.explained_variance_ratio_[i]:.2%})' 
                        for i in range(n_comp)]
            )
            
            # Create heatmap
            fig, ax = plt.subplots(figsize=(16, max(12, n_features * 0.3)))
            
            sns.heatmap(
                loadings_df,
                cmap='RdBu_r',
                center=0,
                annot=False,
                fmt='.2f',
                cbar_kws={'label': 'Loading Value'},
                linewidths=0.5,
                ax=ax
            )
            
            ax.set_title(title, fontsize=18, fontweight='bold', pad=20)
            ax.set_xlabel('Principal Components', fontsize=14, fontweight='bold')
            ax.set_ylabel('Features', fontsize=14, fontweight='bold')
            
            plt.tight_layout()
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            logger.info(f"Loadings heatmap saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating loadings heatmap: {e}")
            return False

    def create_component_correlation_plot(
        self,
        reduced_matrix: np.ndarray,
        pca: PCA,
        output_path: Path,
        n_components: int = 10,
        title: str = "Principal Component Correlations"
    ) -> bool:
        """Create correlation matrix of principal components.

        Args:
            reduced_matrix: PCA-transformed data
            pca: Fitted PCA object
            output_path: Output file path
            n_components: Number of components to display
            title: Plot title

        Returns:
            Success status
        """
        try:
            n_comp = min(n_components, reduced_matrix.shape[1])
            
            # Calculate correlation matrix
            corr_matrix = np.corrcoef(reduced_matrix[:, :n_comp].T)
            
            # Create plot
            fig, ax = plt.subplots(figsize=(14, 12))
            
            # Create labels with variance explained
            labels = [f'PC{i+1}\n({pca.explained_variance_ratio_[i]:.2%})' 
                     for i in range(n_comp)]
            
            # Heatmap
            im = ax.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1, aspect='auto')
            
            # Colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('Correlation Coefficient', fontsize=12, fontweight='bold')
            
            # Ticks and labels
            ax.set_xticks(np.arange(n_comp))
            ax.set_yticks(np.arange(n_comp))
            ax.set_xticklabels(labels, fontsize=10)
            ax.set_yticklabels(labels, fontsize=10)
            
            # Rotate x labels
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
            
            # Add correlation values
            for i in range(n_comp):
                for j in range(n_comp):
                    text = ax.text(j, i, f'{corr_matrix[i, j]:.2f}',
                                 ha='center', va='center',
                                 color='black' if abs(corr_matrix[i, j]) < 0.5 else 'white',
                                 fontsize=9, fontweight='bold')
            
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            plt.tight_layout()
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            logger.info(f"Component correlation plot saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating component correlation plot: {e}")
            return False

    def save_loadings_table(
        self,
        pca: PCA,
        vectorizer: TfidfVectorizer,
        output_path: Path,
        n_components: int = 10,
        n_features: int = 20
    ) -> bool:
        """Save feature loadings to CSV file.

        Args:
            pca: Fitted PCA object
            vectorizer: Fitted TF-IDF vectorizer
            output_path: Output file path (CSV)
            n_components: Number of components to save
            n_features: Number of top features per component

        Returns:
            Success status
        """
        try:
            feature_names = vectorizer.get_feature_names_out()
            n_comp = min(n_components, pca.n_components_)
            
            # Create comprehensive loadings table
            loadings_data = []
            
            for i in range(n_comp):
                loadings = pca.components_[i]
                top_pos_idx = loadings.argsort()[-n_features:][::-1]
                top_neg_idx = loadings.argsort()[:n_features]
                
                # Positive loadings
                for idx in top_pos_idx:
                    loadings_data.append({
                        'component': f'PC{i+1}',
                        'component_number': i+1,
                        'variance_explained': pca.explained_variance_ratio_[i],
                        'feature': feature_names[idx],
                        'loading': loadings[idx],
                        'loading_type': 'positive',
                        'rank': list(top_pos_idx).index(idx) + 1
                    })
                
                # Negative loadings
                for idx in top_neg_idx:
                    loadings_data.append({
                        'component': f'PC{i+1}',
                        'component_number': i+1,
                        'variance_explained': pca.explained_variance_ratio_[i],
                        'feature': feature_names[idx],
                        'loading': loadings[idx],
                        'loading_type': 'negative',
                        'rank': list(top_neg_idx).index(idx) + 1
                    })
            
            loadings_df = pd.DataFrame(loadings_data)
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            loadings_df.to_csv(output_path, index=False)
            
            logger.info(f"Loadings table saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving loadings table: {e}")
            return False

    def create_3d_component_plot(
        self,
        reduced_matrix: np.ndarray,
        pca: PCA,
        labels: List[str],
        output_path: Path,
        title: str = "3D Principal Component Visualization"
    ) -> bool:
        """Create 3D plot of first three principal components.

        Args:
            reduced_matrix: PCA-transformed data
            pca: Fitted PCA object
            labels: Sample labels
            output_path: Output file path
            title: Plot title

        Returns:
            Success status
        """
        try:
            if reduced_matrix.shape[1] < 3:
                logger.warning("Need at least 3 components for 3D plot")
                return False
            
            fig = plt.figure(figsize=(20, 16))
            ax = fig.add_subplot(111, projection='3d')
            
            # Color mapping
            unique_labels = list(set(labels))
            colors = plt.cm.get_cmap('tab20')(np.linspace(0, 1, len(unique_labels)))
            color_dict = dict(zip(unique_labels, colors))
            
            # Plot points
            for label in unique_labels:
                indices = [i for i, l in enumerate(labels) if l == label]
                ax.scatter(
                    reduced_matrix[indices, 0],
                    reduced_matrix[indices, 1],
                    reduced_matrix[indices, 2],
                    c=[color_dict[label]],
                    s=200,
                    alpha=0.7,
                    label=label,
                    edgecolors='black',
                    linewidths=1.5
                )
            
            # Formatting
            ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%} variance)',
                         fontsize=14, fontweight='bold', labelpad=10)
            ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%} variance)',
                         fontsize=14, fontweight='bold', labelpad=10)
            ax.set_zlabel(f'PC3 ({pca.explained_variance_ratio_[2]:.2%} variance)',
                         fontsize=14, fontweight='bold', labelpad=10)
            ax.set_title(title, fontsize=18, fontweight='bold', pad=20)
            
            # Legend
            if len(unique_labels) <= 15:
                ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
            
            # Multiple viewing angles
            ax.view_init(elev=20, azim=45)
            
            plt.tight_layout()
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            logger.info(f"3D component plot saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating 3D component plot: {e}")
            return False

    def create_comprehensive_pca_report(
        self,
        pca: PCA,
        reduced_matrix: np.ndarray,
        vectorizer: TfidfVectorizer,
        labels: List[str],
        output_dir: Path,
        prefix: str = "pca"
    ) -> Dict[str, bool]:
        """Create comprehensive PCA analysis report with all visualizations.

        Args:
            pca: Fitted PCA object
            reduced_matrix: PCA-transformed data
            vectorizer: Fitted TF-IDF vectorizer
            labels: Sample labels
            output_dir: Output directory for all plots
            prefix: Filename prefix for outputs

        Returns:
            Dictionary of visualization names and success status
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {}
        
        logger.info("Creating comprehensive PCA analysis report...")
        
        # 1. Scree plot
        results['scree_plot'] = self.create_scree_plot(
            pca, output_dir / f"{prefix}_scree_plot.png"
        )
        
        # 2. Loadings plot
        results['loadings_plot'] = self.create_loadings_plot(
            pca, vectorizer, output_dir / f"{prefix}_loadings.png"
        )
        
        # 3. Biplot
        results['biplot'] = self.create_biplot(
            pca, reduced_matrix, vectorizer, labels,
            output_dir / f"{prefix}_biplot.png"
        )
        
        # 4. Loadings heatmap
        results['loadings_heatmap'] = self.create_loadings_heatmap(
            pca, vectorizer, output_dir / f"{prefix}_loadings_heatmap.png"
        )
        
        # 5. Component correlation
        results['component_correlation'] = self.create_component_correlation_plot(
            reduced_matrix, pca, output_dir / f"{prefix}_component_correlations.png"
        )
        
        # 6. 3D visualization
        if reduced_matrix.shape[1] >= 3:
            results['3d_plot'] = self.create_3d_component_plot(
                reduced_matrix, pca, labels,
                output_dir / f"{prefix}_3d_components.png"
            )
        
        # 7. Loadings table (CSV)
        results['loadings_table'] = self.save_loadings_table(
            pca, vectorizer, output_dir / f"{prefix}_loadings_table.csv"
        )
        
        # Summary report
        successful = sum(results.values())
        total = len(results)
        logger.info(f"PCA analysis report complete: {successful}/{total} visualizations created")
        
        return results

