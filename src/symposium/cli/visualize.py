"""CLI for visualization commands."""

import argparse
import logging
from pathlib import Path
from symposium.core.logging_utils import setup_logging
from symposium.visualization.embeddings import TextVisualizer, DimensionReducer
from symposium.visualization.networks import NetworkAnalyzer
from symposium.visualization.distributions import DistributionPlotter
from symposium.io.readers import ReportReader


def visualize_embeddings(args):
    """Visualize text embeddings and dimension reduction."""
    logger = logging.getLogger(__name__)

    try:
        # Setup
        config = {
            'max_features': args.max_features,
            'n_components': args.n_components,
            'reduction_method': args.method
        }

        # Load documents
        documents, filenames, labels = [], [], []
        input_path = Path(args.input_dir)

        if input_path.is_file():
            # Single file
            content = ReportReader.read_markdown(input_path)
            documents = [content]
            filenames = [input_path.name]
            labels = [args.label or "document"]
        else:
            # Directory of files
            for file_path in input_path.rglob("*.md"):
                try:
                    content = ReportReader.read_markdown(file_path)
                    documents.append(content)
                    filenames.append(str(file_path.relative_to(input_path)))
                    labels.append(file_path.parent.name)
                except Exception as e:
                    logger.warning(f"Could not read {file_path}: {e}")

        if not documents:
            logger.error("No documents found to visualize")
            return

        logger.info(f"Loaded {len(documents)} documents")

        # Perform analysis
        visualizer = TextVisualizer(config)
        reducer = DimensionReducer(config)

        # Dimension reduction
        reduced_matrix, vectorizer, reduction_model = reducer.perform_tfidf_and_reduction(
            documents,
            n_components=config['n_components'],
            method=config['reduction_method']
        )

        if reduced_matrix is None:
            logger.error("Dimension reduction failed")
            return

        # Create plots
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 2D/3D visualization
        plot_path = output_dir / f"embedding_{config['reduction_method']}_{config['n_components']}d.png"
        visualizer.plot_dimension_reduction(
            reduced_matrix, labels, filenames,
            f"{config['reduction_method'].upper()} Visualization ({config['n_components']}D)",
            plot_path, vectorizer, reduction_model
        )

        # Word cloud
        cloud_path = output_dir / "word_cloud.png"
        visualizer.create_word_cloud(documents, "Research Word Cloud", cloud_path)

        # Term frequency
        freq_path = output_dir / "term_frequency.png"
        visualizer.plot_term_frequency(documents, "Term Frequency Distribution", freq_path)

        logger.info(f"✅ Visualizations saved to {args.output_dir}")

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise


def visualize_networks(args):
    """Visualize similarity networks."""
    logger = logging.getLogger(__name__)

    try:
        # Setup
        config = {
            'similarity_threshold': args.threshold,
            'max_terms': args.max_terms,
            'layout': args.layout
        }

        # Load documents (similar to embeddings)
        documents, filenames, labels = [], [], []
        input_path = Path(args.input_dir)

        for file_path in input_path.rglob("*.md"):
            try:
                content = ReportReader.read_markdown(file_path)
                documents.append(content)
                filenames.append(str(file_path.relative_to(input_path)))
                labels.append(file_path.parent.name)
            except Exception as e:
                logger.warning(f"Could not read {file_path}: {e}")

        if not documents:
            logger.error("No documents found for network analysis")
            return

        # Perform TF-IDF
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer = TfidfVectorizer(max_features=config['max_terms'], stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(documents)

        # Create network
        analyzer = NetworkAnalyzer(config)
        graph = analyzer.create_similarity_network(
            tfidf_matrix, vectorizer, filenames,
            threshold=config['similarity_threshold'],
            max_terms=config['max_terms']
        )

        if graph is None or len(graph.nodes()) == 0:
            logger.error("Could not create similarity network")
            return

        # Create plots
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Network visualization
        network_path = output_dir / f"similarity_network_{config['layout']}.png"
        analyzer.plot_network(
            graph,
            f"Research Similarity Network (threshold: {config['similarity_threshold']})",
            network_path,
            layout=config['layout']
        )

        # Community analysis
        community_path = output_dir / "community_analysis.png"
        analyzer.plot_community_analysis(
            graph,
            "Research Community Analysis",
            community_path
        )

        logger.info(f"✅ Network visualizations saved to {args.output_dir}")

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise


def visualize_distributions(args):
    """Visualize statistical distributions."""
    logger = logging.getLogger(__name__)

    try:
        # Load documents
        documents, labels = [], []
        input_path = Path(args.input_dir)

        for file_path in input_path.rglob("*.md"):
            try:
                content = ReportReader.read_markdown(file_path)
                documents.append(content)
                labels.append(file_path.parent.name)
            except Exception as e:
                logger.warning(f"Could not read {file_path}: {e}")

        if not documents:
            logger.error("No documents found for distribution analysis")
            return

        # Create plots
        plotter = DistributionPlotter()
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Document length distribution
        length_path = output_dir / "document_length_distribution.png"
        plotter.plot_document_length_distribution(
            documents, labels, "Document Length Distribution by Category", length_path
        )

        logger.info(f"✅ Distribution visualizations saved to {args.output_dir}")

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise


def visualize_all(args):
    """Generate all visualization types."""
    logger = logging.getLogger(__name__)

    try:
        print("🔄 Generating all visualizations...")
        logger.info("Generating all visualization types")

        # Create embeddings
        print("📊 Creating embedding visualizations...")
        try:
            # Import and run embeddings visualization
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.decomposition import PCA
            from symposium.visualization.embeddings import TextVisualizer, DimensionReducer

            # Load documents
            documents, filenames, labels = [], [], []
            input_path = Path(args.input_dir)

            for file_path in input_path.rglob("*.md"):
                try:
                    content = ReportReader.read_markdown(file_path)
                    documents.append(content)
                    filenames.append(str(file_path.relative_to(input_path)))
                    labels.append(file_path.parent.name)
                except Exception as e:
                    logger.warning(f"Could not read {file_path}: {e}")

            if documents:
                # Create embeddings
                visualizer = TextVisualizer()
                reducer = DimensionReducer()

                reduced_matrix, vectorizer, reduction_model = reducer.perform_tfidf_and_reduction(
                    documents,
                    n_components=args.n_components,
                    method=args.method
                )

                if reduced_matrix is not None:
                    output_dir = Path(args.output_dir)
                    output_dir.mkdir(parents=True, exist_ok=True)

                    # 2D/3D visualization
                    plot_path = output_dir / f"embedding_{args.method}_{args.n_components}d.png"
                    visualizer.plot_dimension_reduction(
                        reduced_matrix, labels, filenames,
                        f"{args.method.upper()} Visualization ({args.n_components}D)",
                        plot_path, vectorizer, reduction_model
                    )

                    # Word cloud
                    cloud_path = output_dir / "word_cloud.png"
                    visualizer.create_word_cloud(documents, "Research Word Cloud", cloud_path)

                    # Term frequency
                    freq_path = output_dir / "term_frequency.png"
                    visualizer.plot_term_frequency(documents, "Term Frequency Distribution", freq_path)

                    print("✅ Embedding visualizations completed")
                    logger.info("Embedding visualizations completed")
                else:
                    print("⚠️  Embedding visualization failed")
                    logger.warning("Embedding visualization failed")

        except Exception as e:
            logger.error(f"Embedding visualization failed: {e}")
            print(f"⚠️  Embedding visualization failed: {e}")

        # Create networks
        print("🌐 Creating network visualizations...")
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from symposium.visualization.networks import NetworkAnalyzer

            # Load documents (similar to embeddings)
            documents, filenames, labels = [], [], []
            input_path = Path(args.input_dir)

            for file_path in input_path.rglob("*.md"):
                try:
                    content = ReportReader.read_markdown(file_path)
                    documents.append(content)
                    filenames.append(str(file_path.relative_to(input_path)))
                    labels.append(file_path.parent.name)
                except Exception as e:
                    logger.warning(f"Could not read {file_path}: {e}")

            if documents:
                # Perform TF-IDF
                vectorizer = TfidfVectorizer(max_features=50, stop_words='english')
                tfidf_matrix = vectorizer.fit_transform(documents)

                # Create network
                analyzer = NetworkAnalyzer()
                graph = analyzer.create_similarity_network(
                    tfidf_matrix, vectorizer, filenames,
                    threshold=args.threshold,
                    max_terms=50
                )

                if graph is not None and len(graph.nodes()) > 0:
                    output_dir = Path(args.output_dir)
                    output_dir.mkdir(parents=True, exist_ok=True)

                    # Network visualization
                    network_path = output_dir / f"similarity_network_{args.layout}.png"
                    analyzer.plot_network(
                        graph,
                        f"Research Similarity Network (threshold: {args.threshold})",
                        network_path,
                        layout=args.layout
                    )

                    # Community analysis
                    community_path = output_dir / "community_analysis.png"
                    analyzer.plot_community_analysis(
                        graph,
                        "Research Community Analysis",
                        community_path
                    )

                    print("✅ Network visualizations completed")
                    logger.info("Network visualizations completed")
                else:
                    print("⚠️  Network visualization failed")
                    logger.warning("Network visualization failed")

        except Exception as e:
            logger.error(f"Network visualization failed: {e}")
            print(f"⚠️  Network visualization failed: {e}")

        # Create distributions
        print("📈 Creating distribution visualizations...")
        try:
            from symposium.visualization.distributions import DistributionPlotter

            # Load documents
            documents, labels = [], []
            input_path = Path(args.input_dir)

            for file_path in input_path.rglob("*.md"):
                try:
                    content = ReportReader.read_markdown(file_path)
                    documents.append(content)
                    labels.append(file_path.parent.name)
                except Exception as e:
                    logger.warning(f"Could not read {file_path}: {e}")

            if documents:
                plotter = DistributionPlotter()
                output_dir = Path(args.output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)

                # Document length distribution
                length_path = output_dir / "document_length_distribution.png"
                plotter.plot_document_length_distribution(
                    documents, labels, "Document Length Distribution by Category", length_path
                )

                print("✅ Distribution visualizations completed")
                logger.info("Distribution visualizations completed")
            else:
                print("⚠️  Distribution visualization failed")
                logger.warning("Distribution visualization failed")

        except Exception as e:
            logger.error(f"Distribution visualization failed: {e}")
            print(f"⚠️  Distribution visualization failed: {e}")

        print(f"\n🎉 All visualizations completed! Results saved to: {args.output_dir}")
        logger.info(f"All visualizations completed: {args.output_dir}")

    except Exception as e:
        logger.error(f"❌ Error in visualize_all: {e}")
        print(f"❌ Error: {e}")
        raise


def main():
    """Main CLI entry point for visualization commands."""
    import sys

    # Check if called with subcommand (e.g., symposium visualize embeddings)
    if len(sys.argv) >= 2 and sys.argv[1] in ['embeddings', 'networks', 'distributions']:
        # Handle subcommand format: symposium visualize embeddings --args
        subcommand = sys.argv[1]

        # Create parser for the specific subcommand
        if subcommand == 'embeddings':
            parser = argparse.ArgumentParser(
                description='Create embedding and dimension reduction plots',
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                prog='symposium visualize embeddings'
            )
            parser.add_argument('--input-dir', required=True, help='Directory containing markdown files')
            parser.add_argument('--output-dir', required=True, help='Output directory for plots')
            parser.add_argument('--method', choices=['pca', 'lsa', 'tsne'], default='pca', help='Dimension reduction method')
            parser.add_argument('--n-components', type=int, default=2, help='Number of components')
            parser.add_argument('--max-features', type=int, default=5000, help='Max TF-IDF features')
            parser.add_argument('--label', help='Label for single file input')
            parser.add_argument('--log-level', default='INFO', help='Logging level')

            args = parser.parse_args()
            setup_logging(level=args.log_level)
            visualize_embeddings(args)

        elif subcommand == 'networks':
            parser = argparse.ArgumentParser(
                description='Create similarity network visualizations',
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                prog='symposium visualize networks'
            )
            parser.add_argument('--input-dir', required=True, help='Directory containing markdown files')
            parser.add_argument('--output-dir', required=True, help='Output directory for plots')
            parser.add_argument('--threshold', type=float, default=0.3, help='Similarity threshold')
            parser.add_argument('--max-terms', type=int, default=50, help='Maximum terms in network')
            parser.add_argument('--layout', choices=['spring', 'circular', 'kamada_kawai'], default='spring', help='Network layout')
            parser.add_argument('--log-level', default='INFO', help='Logging level')

            args = parser.parse_args()
            setup_logging(level=args.log_level)
            visualize_networks(args)

        elif subcommand == 'distributions':
            parser = argparse.ArgumentParser(
                description='Create statistical distribution plots',
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                prog='symposium visualize distributions'
            )
            parser.add_argument('--input-dir', required=True, help='Directory containing markdown files')
            parser.add_argument('--output-dir', required=True, help='Output directory for plots')
            parser.add_argument('--log-level', default='INFO', help='Logging level')

            args = parser.parse_args()
            setup_logging(level=args.log_level)
            visualize_distributions(args)

    else:
        # Handle direct call or help
        parser = argparse.ArgumentParser(
            description='Visualize research data and analysis results',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

        subparsers = parser.add_subparsers(dest='subcommand', help='Visualization type')

        # Embeddings visualization
        embed_parser = subparsers.add_parser('embeddings', help='Create embedding and dimension reduction plots')
        embed_parser.add_argument('--input-dir', required=True, help='Directory containing markdown files')
        embed_parser.add_argument('--output-dir', required=True, help='Output directory for plots')
        embed_parser.add_argument('--method', choices=['pca', 'lsa', 'tsne'], default='pca', help='Dimension reduction method')
        embed_parser.add_argument('--n-components', type=int, default=2, help='Number of components')
        embed_parser.add_argument('--max-features', type=int, default=5000, help='Max TF-IDF features')
        embed_parser.add_argument('--label', help='Label for single file input')
        embed_parser.add_argument('--log-level', default='INFO', help='Logging level')
        embed_parser.set_defaults(func=visualize_embeddings)

        # Network visualization
        network_parser = subparsers.add_parser('networks', help='Create similarity network visualizations')
        network_parser.add_argument('--input-dir', required=True, help='Directory containing markdown files')
        network_parser.add_argument('--output-dir', required=True, help='Output directory for plots')
        network_parser.add_argument('--threshold', type=float, default=0.3, help='Similarity threshold')
        network_parser.add_argument('--max-terms', type=int, default=50, help='Maximum terms in network')
        network_parser.add_argument('--layout', choices=['spring', 'circular', 'kamada_kawai'], default='spring', help='Network layout')
        network_parser.add_argument('--log-level', default='INFO', help='Logging level')
        network_parser.set_defaults(func=visualize_networks)

        # Distribution visualization
        dist_parser = subparsers.add_parser('distributions', help='Create statistical distribution plots')
        dist_parser.add_argument('--input-dir', required=True, help='Directory containing markdown files')
        dist_parser.add_argument('--output-dir', required=True, help='Output directory for plots')
        dist_parser.add_argument('--log-level', default='INFO', help='Logging level')
        dist_parser.set_defaults(func=visualize_distributions)

        # Parse arguments - let argparse handle the help
        args = parser.parse_args()

        # Setup logging
        setup_logging(level=args.log_level)

        # Run command
        args.func(args)

    # Handle 'all' visualization type
    if len(sys.argv) >= 2 and sys.argv[1] == 'all':
        # Create parser for all visualizations
        parser = argparse.ArgumentParser(
            description='Generate all visualization types',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog='symposium visualize all'
        )
        parser.add_argument('--input-dir', required=True, help='Directory containing markdown files')
        parser.add_argument('--output-dir', required=True, help='Output directory for plots')
        parser.add_argument('--method', choices=['pca', 'lsa', 'tsne'], default='pca', help='Dimension reduction method for embeddings')
        parser.add_argument('--n-components', type=int, default=2, help='Number of components for embeddings')
        parser.add_argument('--threshold', type=float, default=0.3, help='Similarity threshold for networks')
        parser.add_argument('--layout', choices=['spring', 'circular', 'kamada_kawai'], default='spring', help='Network layout')
        parser.add_argument('--log-level', default='INFO', help='Logging level')

        args = parser.parse_args()
        setup_logging(level=args.log_level)
        visualize_all(args)

    # Handle direct calls from run.py
    elif len(sys.argv) >= 3 and sys.argv[1] in ['embeddings', 'networks', 'distributions', 'all']:
        # This handles calls from the run.py interactive interface
        subcommand = sys.argv[1]

        if subcommand == 'all':
            # Parse arguments for 'all' command
            parser = argparse.ArgumentParser(
                description='Generate all visualization types',
                formatter_class=argparse.ArgumentDefaultsHelpFormatter
            )
            parser.add_argument('--input-dir', required=True)
            parser.add_argument('--output-dir', required=True)
            parser.add_argument('--method', choices=['pca', 'lsa', 'tsne'], default='pca')
            parser.add_argument('--n-components', type=int, default=2)
            parser.add_argument('--threshold', type=float, default=0.3)
            parser.add_argument('--layout', choices=['spring', 'circular', 'kamada_kawai'], default='spring')
            parser.add_argument('--log-level', default='INFO')

            args = parser.parse_args(sys.argv[2:])
            setup_logging(level=args.log_level)
            visualize_all(args)
        else:
            # Handle individual visualization types
            if subcommand == 'embeddings':
                parser = argparse.ArgumentParser(description='Create embedding plots')
                parser.add_argument('--input-dir', required=True)
                parser.add_argument('--output-dir', required=True)
                parser.add_argument('--method', choices=['pca', 'lsa', 'tsne'], default='pca')
                parser.add_argument('--n-components', type=int, default=2)
                parser.add_argument('--max-features', type=int, default=5000)
                parser.add_argument('--label')
                parser.add_argument('--log-level', default='INFO')

                args = parser.parse_args(sys.argv[2:])
                setup_logging(level=args.log_level)
                visualize_embeddings(args)

            elif subcommand == 'networks':
                parser = argparse.ArgumentParser(description='Create network visualizations')
                parser.add_argument('--input-dir', required=True)
                parser.add_argument('--output-dir', required=True)
                parser.add_argument('--threshold', type=float, default=0.3)
                parser.add_argument('--max-terms', type=int, default=50)
                parser.add_argument('--layout', choices=['spring', 'circular', 'kamada_kawai'], default='spring')
                parser.add_argument('--log-level', default='INFO')

                args = parser.parse_args(sys.argv[2:])
                setup_logging(level=args.log_level)
                visualize_networks(args)

            elif subcommand == 'distributions':
                parser = argparse.ArgumentParser(description='Create distribution plots')
                parser.add_argument('--input-dir', required=True)
                parser.add_argument('--output-dir', required=True)
                parser.add_argument('--log-level', default='INFO')

                args = parser.parse_args(sys.argv[2:])
                setup_logging(level=args.log_level)
                visualize_distributions(args)


if __name__ == "__main__":
    main()

