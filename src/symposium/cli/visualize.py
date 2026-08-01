"""CLI for visualization commands."""

import logging
from pathlib import Path

from symposium.io.readers import ReportReader
from symposium.visualization.distributions import DistributionPlotter
from symposium.visualization.embeddings import DimensionReducer, TextVisualizer
from symposium.visualization.networks import NetworkAnalyzer


def visualize_embeddings(args):
    """Visualize text embeddings and dimension reduction."""
    logger = logging.getLogger(__name__)

    try:
        # Setup
        config = {
            "max_features": args.max_features,
            "n_components": args.n_components,
            "reduction_method": args.method,
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
            documents, n_components=config["n_components"], method=config["reduction_method"]
        )

        if reduced_matrix is None:
            logger.error("Dimension reduction failed")
            return

        # Create plots
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 2D/3D visualization
        plot_path = (
            output_dir / f"embedding_{config['reduction_method']}_{config['n_components']}d.png"
        )
        visualizer.plot_dimension_reduction(
            reduced_matrix,
            labels,
            filenames,
            f"{config['reduction_method'].upper()} Visualization ({config['n_components']}D)",
            plot_path,
            vectorizer,
            reduction_model,
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
            "similarity_threshold": args.threshold,
            "max_terms": args.max_terms,
            "layout": args.layout,
        }

        # Load documents (similar to embeddings)
        documents, filenames, labels = [], [], []
        input_path = Path(args.input_dir)

        if input_path.is_file():
            # Single file support, consistent with visualize_embeddings
            try:
                content = ReportReader.read_markdown(input_path)
                documents = [content]
                filenames = [input_path.name]
                labels = [input_path.parent.name or "document"]
            except Exception as e:
                logger.warning(f"Could not read {input_path}: {e}")
        else:
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

        vectorizer = TfidfVectorizer(max_features=config["max_terms"], stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(documents)

        # Create network
        analyzer = NetworkAnalyzer(config)
        graph = analyzer.create_similarity_network(
            tfidf_matrix,
            vectorizer,
            filenames,
            threshold=config["similarity_threshold"],
            max_terms=config["max_terms"],
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
            layout=config["layout"],
        )

        # Community analysis
        community_path = output_dir / "community_analysis.png"
        analyzer.plot_community_analysis(graph, "Research Community Analysis", community_path)

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

        if input_path.is_file():
            # Single file support, consistent with visualize_embeddings
            try:
                content = ReportReader.read_markdown(input_path)
                documents = [content]
                labels = [input_path.parent.name or "document"]
            except Exception as e:
                logger.warning(f"Could not read {input_path}: {e}")
        else:
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

            from symposium.visualization.embeddings import DimensionReducer, TextVisualizer
            from symposium.visualization.pca_analysis import PCAAnalyzer

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

                # Calculate appropriate number of components
                # For PCA, we need n_components <= min(n_samples, n_features)
                # We'll use a reasonable default but cap it appropriately
                max_possible_components = min(len(documents), 1000)  # Reasonable upper bound
                n_comp_analysis = min(
                    max(args.n_components, 50) if args.method == "pca" else args.n_components,
                    max_possible_components,
                )

                reduced_matrix, vectorizer, reduction_model = reducer.perform_tfidf_and_reduction(
                    documents, n_components=n_comp_analysis, method=args.method
                )

                if reduced_matrix is not None:
                    output_dir = Path(args.output_dir)
                    output_dir.mkdir(parents=True, exist_ok=True)

                    # 2D/3D visualization. Name the file by the dimensions actually
                    # rendered (plot_dimension_reduction shows 2D when shape==2,
                    # else 3D), not the possibly-clamped requested component count.
                    plotted_dims = 3 if reduced_matrix.shape[1] >= 3 else reduced_matrix.shape[1]
                    plot_path = output_dir / f"embedding_{args.method}_{plotted_dims}d.png"
                    visualizer.plot_dimension_reduction(
                        reduced_matrix,
                        labels,
                        filenames,
                        f"{args.method.upper()} Visualization ({args.n_components}D)",
                        plot_path,
                        vectorizer,
                        reduction_model,
                    )

                    # Word cloud
                    cloud_path = output_dir / "word_cloud.png"
                    visualizer.create_word_cloud(documents, "Research Word Cloud", cloud_path)

                    # Term frequency
                    freq_path = output_dir / "term_frequency.png"
                    visualizer.plot_term_frequency(
                        documents, "Term Frequency Distribution", freq_path
                    )

                    # Comprehensive PCA analysis if using PCA method
                    if (
                        args.method == "pca"
                        and reduction_model is not None
                        and vectorizer is not None
                    ):
                        print("📊 Creating comprehensive PCA analysis visualizations...")
                        pca_analyzer = PCAAnalyzer()
                        pca_results = pca_analyzer.create_comprehensive_pca_report(
                            reduction_model,
                            reduced_matrix,
                            vectorizer,
                            labels,
                            output_dir,
                            prefix="pca_analysis",
                        )

                        successful_pca = sum(pca_results.values())
                        total_pca = len(pca_results)
                        print(
                            f"   └─ PCA analysis: {successful_pca}/{total_pca} visualizations created"
                        )
                        logger.info(
                            f"PCA analysis: {successful_pca}/{total_pca} visualizations created"
                        )

                    print("✅ Embedding visualizations completed")
                    logger.info("Embedding visualizations completed")
                else:
                    print("⚠️  Embedding visualization failed")
                    logger.warning("Embedding visualization failed")

        except Exception as e:
            logger.error(f"Embedding visualization failed: {e}")
            print(f"⚠️  Embedding visualization failed: {e}")

        # Create participant-specific PCA embeddings
        print("👥 Creating participant PCA embeddings...")
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer

            from symposium.visualization.embeddings import DimensionReducer, TextVisualizer
            from symposium.visualization.pca_analysis import PCAAnalyzer

            # Load participant documents specifically
            participant_documents, participant_filenames, participant_labels = [], [], []
            input_path = Path(args.input_dir)
            people_dir = input_path / "people"

            if people_dir.exists():
                for participant_dir in people_dir.iterdir():
                    if participant_dir.is_dir():
                        participant_name = participant_dir.name
                        # Load all markdown files for this participant
                        for file_path in participant_dir.glob("*.md"):
                            try:
                                content = ReportReader.read_markdown(file_path)
                                participant_documents.append(content)
                                participant_filenames.append(file_path.name)
                                participant_labels.append(participant_name)
                            except Exception as e:
                                logger.warning(f"Could not read participant file {file_path}: {e}")

                if participant_documents:
                    logger.info(
                        f"Loaded {len(participant_documents)} documents from {len(set(participant_labels))} participants"
                    )

                    # Create participant-specific PCA embeddings
                    visualizer = TextVisualizer()
                    reducer = DimensionReducer()

                    # Calculate appropriate number of components for participants
                    # For PCA, we need n_components <= min(n_samples, n_features)
                    max_possible_participant_components = min(len(participant_documents), 1000)
                    # Use at least 3 components for comprehensive analysis (enables 3D visualization)
                    # For comprehensive PCA analysis, use more components to capture variance
                    n_comp_participants_analysis = min(
                        max(50, len(participant_documents) // 5),
                        max_possible_participant_components,
                    )

                    # First, create comprehensive PCA with many components for full analysis
                    participant_reduced_full, participant_vectorizer, participant_pca_full = (
                        reducer.perform_tfidf_and_reduction(
                            participant_documents,
                            n_components=n_comp_participants_analysis,
                            method="pca",  # Always use PCA for participant embeddings
                        )
                    )

                    if (
                        participant_reduced_full is not None
                        and participant_pca_full is not None
                        and participant_vectorizer is not None
                    ):
                        output_dir = Path(args.output_dir)
                        output_dir.mkdir(parents=True, exist_ok=True)

                        # Create reduced version for 2D/3D visualization (first 3 components)
                        n_viz_components = min(3, participant_reduced_full.shape[1])
                        participant_reduced_viz = participant_reduced_full[:, :n_viz_components]

                        # Participant 2D/3D visualization
                        participant_plot_path = (
                            output_dir / f"participants_embedding_pca_{n_viz_components}d.png"
                        )
                        # The full PCA is used for the comprehensive report; the 2D/3D
                        # plot simply uses the first n_viz_components columns.
                        visualizer.plot_dimension_reduction(
                            participant_reduced_viz,
                            participant_labels,
                            participant_filenames,
                            f"Participant PCA Embeddings ({n_viz_components}D)",
                            participant_plot_path,
                            participant_vectorizer,
                            participant_pca_full,
                        )

                        # Comprehensive participant PCA analysis (using full component set)
                        print("   📊 Creating comprehensive participant PCA analysis...")
                        pca_analyzer = PCAAnalyzer()
                        participant_pca_results = pca_analyzer.create_comprehensive_pca_report(
                            participant_pca_full,
                            participant_reduced_full,
                            participant_vectorizer,
                            participant_labels,
                            output_dir,
                            prefix="participants_pca_analysis",
                        )

                        successful_participant_pca = sum(participant_pca_results.values())
                        total_participant_pca = len(participant_pca_results)
                        print(
                            f"   └─ Participant PCA analysis: {successful_participant_pca}/{total_participant_pca} visualizations created"
                        )
                        logger.info(
                            f"Participant PCA analysis: {successful_participant_pca}/{total_participant_pca} visualizations created"
                        )

                        print("✅ Participant PCA embeddings completed")
                        logger.info("Participant PCA embeddings completed")
                    else:
                        print("⚠️  Participant PCA embedding failed")
                        logger.warning("Participant PCA embedding failed")
                else:
                    print("⚠️  No participant documents found in people/ directory")
                    logger.warning(f"No participant documents found in {people_dir}")
            else:
                print(f"⚠️  People directory not found: {people_dir}")
                logger.warning(f"People directory not found: {people_dir}")

        except Exception as e:
            logger.error(f"Participant PCA embedding failed: {e}")
            print(f"⚠️  Participant PCA embedding failed: {e}")

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
                vectorizer = TfidfVectorizer(max_features=50, stop_words="english")
                tfidf_matrix = vectorizer.fit_transform(documents)

                # Create network
                analyzer = NetworkAnalyzer()
                graph = analyzer.create_similarity_network(
                    tfidf_matrix, vectorizer, filenames, threshold=args.threshold, max_terms=50
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
                        layout=args.layout,
                    )

                    # Community analysis
                    community_path = output_dir / "community_analysis.png"
                    analyzer.plot_community_analysis(
                        graph, "Research Community Analysis", community_path
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
