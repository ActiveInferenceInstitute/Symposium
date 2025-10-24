"""Command-line interfaces for symposium package."""

import sys


def main():
    """Main CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Symposium: Research analysis and project generation for Active Inference Symposium',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze presenters or participants')
    analyze_subparsers = analyze_parser.add_subparsers(dest='subcommand', help='Analysis type')

    # Analyze presenters
    analyze_presenter_parser = analyze_subparsers.add_parser('presenters', help='Analyze presenter research profiles')
    analyze_presenter_parser.add_argument('--data-dir', required=True, help='Directory containing presenter data')
    analyze_presenter_parser.add_argument('--output-dir', required=True, help='Output directory for reports')
    analyze_presenter_parser.add_argument('--domain-file', help='Domain context file')
    analyze_presenter_parser.add_argument('--max-rows', type=int, default=10, help='Max rows per CSV file')
    analyze_presenter_parser.add_argument('--api-provider', choices=['perplexity', 'openrouter'], help='API provider')
    analyze_presenter_parser.add_argument('--log-level', default='INFO', help='Logging level')
    analyze_presenter_parser.set_defaults(func='analyze_presenters')

    # Analyze participants
    analyze_participant_parser = analyze_subparsers.add_parser('participants', help='Analyze participant profiles')
    analyze_participant_parser.add_argument('--csv-file', required=True, help='Participant CSV file')
    analyze_participant_parser.add_argument('--output-dir', required=True, help='Output directory for reports')
    analyze_participant_parser.add_argument('--api-provider', choices=['perplexity', 'openrouter'], help='API provider')
    analyze_participant_parser.add_argument('--include-background-research', action='store_true', help='Generate background research')
    analyze_participant_parser.add_argument('--include-curriculum', action='store_true', help='Generate personalized curricula')
    analyze_participant_parser.add_argument('--include-column-summaries', action='store_true', help='Generate column summaries and word clouds')
    analyze_participant_parser.add_argument('--log-level', default='INFO', help='Logging level')
    analyze_participant_parser.set_defaults(func='analyze_participants')

    # Background research only
    analyze_background_parser = analyze_subparsers.add_parser('backgrounds', help='Generate background research for participants')
    analyze_background_parser.add_argument('--csv-file', required=True, help='Participant CSV file')
    analyze_background_parser.add_argument('--output-dir', required=True, help='Output directory for reports')
    analyze_background_parser.add_argument('--log-level', default='INFO', help='Logging level')
    analyze_background_parser.set_defaults(func='analyze_participant_backgrounds')

    # Curricula generation only
    analyze_curriculum_parser = analyze_subparsers.add_parser('curricula', help='Generate personalized curricula for participants')
    analyze_curriculum_parser.add_argument('--csv-file', required=True, help='Participant CSV file')
    analyze_curriculum_parser.add_argument('--output-dir', required=True, help='Output directory for reports')
    analyze_curriculum_parser.add_argument('--api-provider', choices=['perplexity', 'openrouter'], help='API provider')
    analyze_curriculum_parser.add_argument('--log-level', default='INFO', help='Logging level')
    analyze_curriculum_parser.set_defaults(func='generate_participant_curricula')

    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate profiles or projects')
    generate_subparsers = generate_parser.add_subparsers(dest='subcommand', help='Generation type')

    # Generate profiles
    generate_profile_parser = generate_subparsers.add_parser('profiles', help='Generate research profiles')
    generate_profile_parser.add_argument('--data-dir', required=True, help='Directory containing researcher data')
    generate_profile_parser.add_argument('--output-dir', required=True, help='Output directory for profiles')
    generate_profile_parser.add_argument('--domain-file', help='Domain context file')
    generate_profile_parser.add_argument('--include-methods', action='store_true', help='Generate methods documentation')
    generate_profile_parser.add_argument('--api-provider', choices=['perplexity', 'openrouter'], help='API provider')
    generate_profile_parser.add_argument('--log-level', default='INFO', help='Logging level')
    generate_profile_parser.set_defaults(func='generate_profiles')

    # Generate projects
    generate_project_parser = generate_subparsers.add_parser('projects', help='Generate project proposals')
    generate_project_parser.add_argument('--profiles-dir', required=True, help='Directory containing participant profiles')
    generate_project_parser.add_argument('--output-dir', required=True, help='Output directory for proposals')
    generate_project_parser.add_argument('--domain-file', required=True, help='Domain context file')
    generate_project_parser.add_argument('--catechism', default='KarmaGAP', help='Catechism type (KarmaGAP, EUGrants, Synthetic)')
    generate_project_parser.add_argument('--catechisms-dir', help='Directory containing catechism templates')
    generate_project_parser.add_argument('--collaborators-file', help='File with potential collaborators')
    generate_project_parser.add_argument('--api-provider', choices=['perplexity', 'openrouter'], help='API provider')
    generate_project_parser.add_argument('--log-level', default='INFO', help='Logging level')
    generate_project_parser.set_defaults(func='generate_projects')

    # Visualize command
    visualize_parser = subparsers.add_parser('visualize', help='Create visualizations')
    visualize_subparsers = visualize_parser.add_subparsers(dest='subcommand', help='Visualization type')

    # Visualize embeddings
    visualize_embed_parser = visualize_subparsers.add_parser('embeddings', help='Create embedding and dimension reduction plots')
    visualize_embed_parser.add_argument('--input-dir', required=True, help='Directory containing markdown files')
    visualize_embed_parser.add_argument('--output-dir', required=True, help='Output directory for plots')
    visualize_embed_parser.add_argument('--method', choices=['pca', 'lsa', 'tsne'], default='pca', help='Dimension reduction method')
    visualize_embed_parser.add_argument('--n-components', type=int, default=2, help='Number of components')
    visualize_embed_parser.add_argument('--max-features', type=int, default=5000, help='Max TF-IDF features')
    visualize_embed_parser.add_argument('--label', help='Label for single file input')
    visualize_embed_parser.add_argument('--log-level', default='INFO', help='Logging level')
    visualize_embed_parser.set_defaults(func='visualize_embeddings')

    # Visualize networks
    visualize_network_parser = visualize_subparsers.add_parser('networks', help='Create similarity network visualizations')
    visualize_network_parser.add_argument('--input-dir', required=True, help='Directory containing markdown files')
    visualize_network_parser.add_argument('--output-dir', required=True, help='Output directory for plots')
    visualize_network_parser.add_argument('--threshold', type=float, default=0.3, help='Similarity threshold')
    visualize_network_parser.add_argument('--max-terms', type=int, default=50, help='Maximum terms in network')
    visualize_network_parser.add_argument('--layout', choices=['spring', 'circular', 'kamada_kawai'], default='spring', help='Network layout')
    visualize_network_parser.add_argument('--log-level', default='INFO', help='Logging level')
    visualize_network_parser.set_defaults(func='visualize_networks')

    # Visualize distributions
    visualize_dist_parser = visualize_subparsers.add_parser('distributions', help='Create statistical distribution plots')
    visualize_dist_parser.add_argument('--input-dir', required=True, help='Directory containing markdown files')
    visualize_dist_parser.add_argument('--output-dir', required=True, help='Output directory for plots')
    visualize_dist_parser.add_argument('--log-level', default='INFO', help='Logging level')
    visualize_dist_parser.set_defaults(func='visualize_distributions')

    # Generate all visualizations
    visualize_all_parser = visualize_subparsers.add_parser('all', help='Generate all visualization types')
    visualize_all_parser.add_argument('--input-dir', required=True, help='Directory containing markdown files')
    visualize_all_parser.add_argument('--output-dir', required=True, help='Output directory for plots')
    visualize_all_parser.add_argument('--method', choices=['pca', 'lsa', 'tsne'], default='pca', help='Dimension reduction method for embeddings')
    visualize_all_parser.add_argument('--n-components', type=int, default=2, help='Number of components for embeddings')
    visualize_all_parser.add_argument('--threshold', type=float, default=0.3, help='Similarity threshold for networks')
    visualize_all_parser.add_argument('--layout', choices=['spring', 'circular', 'kamada_kawai'], default='spring', help='Network layout')
    visualize_all_parser.add_argument('--log-level', default='INFO', help='Logging level')
    visualize_all_parser.set_defaults(func='visualize_all')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Route to appropriate handler function
    from symposium.core.logging_utils import setup_logging

    if args.command == 'analyze':
        setup_logging(level=args.log_level)
        if args.subcommand == 'presenters':
            from symposium.cli.analyze import analyze_presenters
            analyze_presenters(args)
        elif args.subcommand == 'participants':
            from symposium.cli.analyze import analyze_participants
            analyze_participants(args)
        elif args.subcommand == 'backgrounds':
            from symposium.cli.analyze import analyze_participant_backgrounds
            analyze_participant_backgrounds(args)
        elif args.subcommand == 'curricula':
            from symposium.cli.analyze import generate_participant_curricula
            generate_participant_curricula(args)
    elif args.command == 'generate':
        setup_logging(level=args.log_level)
        if args.subcommand == 'profiles':
            from symposium.cli.generate import generate_profiles
            generate_profiles(args)
        elif args.subcommand == 'projects':
            from symposium.cli.generate import generate_projects
            generate_projects(args)
    elif args.command == 'visualize':
        setup_logging(level=args.log_level)
        if args.subcommand == 'embeddings':
            from symposium.cli.visualize import visualize_embeddings
            visualize_embeddings(args)
        elif args.subcommand == 'networks':
            from symposium.cli.visualize import visualize_networks
            visualize_networks(args)
        elif args.subcommand == 'distributions':
            from symposium.cli.visualize import visualize_distributions
            visualize_distributions(args)
        elif args.subcommand == 'all':
            from symposium.cli.visualize import visualize_all
            visualize_all(args)


if __name__ == "__main__":
    main()

