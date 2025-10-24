"""Network analysis and visualization tools."""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class NetworkAnalyzer:
    """Network analysis and visualization tools."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize network analyzer.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}

    def create_similarity_network(
        self,
        tfidf_matrix: Any,
        vectorizer: TfidfVectorizer,
        filenames: List[str],
        threshold: float = 0.3,
        max_terms: int = 50
    ) -> Optional[nx.Graph]:
        """Create similarity network from TF-IDF matrix.

        Args:
            tfidf_matrix: TF-IDF matrix
            vectorizer: TF-IDF vectorizer
            filenames: Original filenames
            threshold: Similarity threshold for edges
            max_terms: Maximum terms to include in network

        Returns:
            NetworkX graph or None if creation fails
        """
        try:
            # Get top terms by TF-IDF score
            feature_names = vectorizer.get_feature_names_out()
            tfidf_sum = np.asarray(tfidf_matrix.sum(axis=0)).ravel()
            top_term_indices = tfidf_sum.argsort()[-max_terms:][::-1]
            top_terms = [feature_names[i] for i in top_term_indices]

            # Create term-term correlation matrix
            term_matrix = tfidf_matrix[:, top_term_indices].toarray()
            similarity_matrix = cosine_similarity(term_matrix.T)

            # Create graph
            G = nx.Graph()

            # Add nodes
            for term in top_terms:
                G.add_node(term, type='term')

            for filename in filenames:
                G.add_node(filename, type='document')

            # Add edges between terms based on correlation
            for i, term1 in enumerate(top_terms):
                for j, term2 in enumerate(top_terms[i+1:], start=i+1):
                    correlation = similarity_matrix[i, j]
                    if correlation > threshold:
                        G.add_edge(term1, term2, weight=correlation, type='term_similarity')

            # Add edges between documents and terms based on TF-IDF
            for doc_idx, filename in enumerate(filenames):
                doc_vector = term_matrix[doc_idx]
                for term_idx, term in enumerate(top_terms):
                    tfidf_score = doc_vector[term_idx]
                    if tfidf_score > 0:
                        G.add_edge(filename, term, weight=tfidf_score, type='document_term')

            if len(G.nodes()) == 0:
                logger.warning("No nodes created in similarity network")
                return None

            logger.info(f"Created similarity network with {len(G.nodes())} nodes and {len(G.edges())} edges")
            return G

        except Exception as e:
            logger.error(f"Error creating similarity network: {e}")
            return None

    def plot_network(
        self,
        graph: nx.Graph,
        title: str,
        output_path: Path,
        layout: str = "spring",
        node_size_factor: float = 1000,
        edge_width_factor: float = 2
    ) -> bool:
        """Plot network visualization.

        Args:
            graph: NetworkX graph to plot
            title: Plot title
            output_path: Output file path
            layout: Network layout algorithm ('spring', 'circular', 'kamada_kawai')
            node_size_factor: Factor for node sizing
            edge_width_factor: Factor for edge width

        Returns:
            Success status
        """
        try:
            if len(graph.nodes()) == 0:
                logger.error("Empty graph provided")
                return False

            plt.figure(figsize=(20, 20))

            # Choose layout
            if layout == "spring":
                pos = nx.spring_layout(graph, k=2, iterations=50)
            elif layout == "circular":
                pos = nx.circular_layout(graph)
            elif layout == "kamada_kawai":
                pos = nx.kamada_kawai_layout(graph)
            else:
                pos = nx.random_layout(graph)

            # Node properties
            node_types = nx.get_node_attributes(graph, 'type')
            node_sizes = []
            node_colors = []

            for node in graph.nodes():
                if node_types.get(node) == 'document':
                    # Documents are larger and blue
                    node_sizes.append(800)
                    node_colors.append('lightblue')
                else:
                    # Terms are smaller and green
                    node_sizes.append(400)
                    node_colors.append('lightgreen')

            # Edge properties
            edge_weights = [graph[u][v].get('weight', 0.5) * edge_width_factor for u, v in graph.edges()]
            edge_colors = []
            for u, v in graph.edges():
                if graph[u][v].get('type') == 'document_term':
                    edge_colors.append('gray')
                else:
                    edge_colors.append('red')

            # Draw network
            nx.draw_networkx_nodes(
                graph, pos,
                node_size=node_sizes,
                node_color=node_colors,
                alpha=0.8,
                edgecolors='black'
            )

            nx.draw_networkx_labels(
                graph, pos,
                font_size=8,
                font_weight='bold'
            )

            nx.draw_networkx_edges(
                graph, pos,
                width=edge_weights,
                edge_color=edge_colors,
                alpha=0.6
            )

            plt.title(title, fontsize=20, fontweight='bold')
            plt.axis('off')
            plt.tight_layout()

            output_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()

            logger.info(f"Network plot saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating network plot: {e}")
            return False

    def analyze_communities(self, graph: nx.Graph) -> Dict[str, Any]:
        """Analyze network communities.

        Args:
            graph: NetworkX graph

        Returns:
            Dictionary with community analysis results
        """
        try:
            # Detect communities
            communities = list(nx.community.greedy_modularity_communities(graph))

            # Calculate community metrics
            analysis = {
                'n_communities': len(communities),
                'communities': [],
                'modularity': nx.community.modularity(graph, communities)
            }

            for i, community in enumerate(communities):
                community_nodes = list(community)
                community_subgraph = graph.subgraph(community_nodes)

                community_info = {
                    'id': i,
                    'size': len(community_nodes),
                    'nodes': community_nodes,
                    'density': nx.density(community_subgraph),
                    'avg_clustering': nx.average_clustering(community_subgraph)
                }
                analysis['communities'].append(community_info)

            logger.info(f"Found {len(communities)} communities with modularity {analysis['modularity']:.3f}")
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing communities: {e}")
            return {'error': str(e)}

    def plot_community_analysis(
        self,
        graph: nx.Graph,
        title: str,
        output_path: Path
    ) -> bool:
        """Plot community analysis results.

        Args:
            graph: NetworkX graph
            title: Plot title
            output_path: Output file path

        Returns:
            Success status
        """
        try:
            # Analyze communities
            analysis = self.analyze_communities(graph)

            if 'error' in analysis:
                logger.error(f"Community analysis failed: {analysis['error']}")
                return False

            # Create community plot
            communities = list(nx.community.greedy_modularity_communities(graph))
            pos = nx.spring_layout(graph, k=2, iterations=50)

            # Color nodes by community
            node_colors = {}
            for i, community in enumerate(communities):
                color = plt.cm.get_cmap('tab20')(i / len(communities))
                for node in community:
                    node_colors[node] = color

            # Plot
            plt.figure(figsize=(20, 20))

            # Draw nodes colored by community
            nx.draw_networkx_nodes(
                graph, pos,
                node_color=[node_colors.get(node, 'gray') for node in graph.nodes()],
                node_size=300,
                alpha=0.8
            )

            nx.draw_networkx_edges(graph, pos, alpha=0.3)
            nx.draw_networkx_labels(graph, pos, font_size=6, font_weight='bold')

            plt.title(f"{title}\n{len(communities)} communities, modularity: {analysis['modularity']:.3f}",
                     fontsize=16, fontweight='bold')
            plt.axis('off')
            plt.tight_layout()

            output_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()

            logger.info(f"Community analysis plot saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating community analysis plot: {e}")
            return False

