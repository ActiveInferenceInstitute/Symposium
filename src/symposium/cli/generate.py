"""CLI for generation commands."""

import logging
from pathlib import Path

from symposium.core.api import APIClient
from symposium.core.config import Config
from symposium.generation.profiles import ProfileGenerator
from symposium.generation.projects import ProjectGenerator
from symposium.io.readers import ReportReader


def generate_profiles(args):
    """Generate research profiles and methods."""
    logger = logging.getLogger(__name__)

    try:
        # Setup configuration and API
        config = Config(config_file=Path(args.config) if getattr(args, "config", None) else None)
        api_client = APIClient.from_config(config, provider=args.api_provider)

        # Load domain context if provided
        domain_context = None
        if args.domain_file:
            domain_context = ReportReader.read_markdown(Path(args.domain_file))

        # Generate profiles
        generator = ProfileGenerator(api_client, config.to_dict().get("data", {}))
        results = generator.generate_all_profiles(
            Path(args.data_dir),
            Path(args.output_dir),
            domain_context,
            include_methods=args.include_methods,
        )
        if not results:
            raise ValueError("No eligible researchers; no profiles were generated")

        logger.info(f"✅ Successfully generated profiles for {len(results)} researchers")
        logger.info(f"📁 Profiles saved to {args.output_dir}")

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise


def generate_projects(args):
    """Generate project proposals."""
    logger = logging.getLogger(__name__)

    try:
        # Setup configuration and API
        config = Config(config_file=Path(args.config) if getattr(args, "config", None) else None)
        api_client = APIClient.from_config(config, provider=args.api_provider)

        # Generate projects
        generator = ProjectGenerator(api_client, config.to_dict().get("data", {}))

        catechisms_dir = Path(args.catechisms_dir) if args.catechisms_dir else None
        collaborators_file = Path(args.collaborators_file) if args.collaborators_file else None

        results = generator.generate_all_projects(
            Path(args.profiles_dir),
            Path(args.output_dir),
            Path(args.domain_file),
            catechism_type=args.catechism,
            catechisms_dir=catechisms_dir,
            collaborators_file=collaborators_file,
        )
        if not results:
            raise ValueError("No eligible participant profiles; no proposals were generated")

        logger.info(f"✅ Successfully generated proposals for {len(results)} participants")
        logger.info(f"📁 Proposals saved to {args.output_dir}")

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise
