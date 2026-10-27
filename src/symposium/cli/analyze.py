"""CLI for analysis commands."""

import logging
from pathlib import Path

from symposium.analysis.participants import ParticipantAnalyzer
from symposium.analysis.presenters import PresenterAnalyzer
from symposium.core.api import APIClient
from symposium.core.config import Config
from symposium.core.data_loader import DataLoader
from symposium.io.readers import ReportReader


def _participant_count(csv_file: str) -> int:
    """Reject invalid or empty registrations before creating a paid-work client."""
    count = len(DataLoader.load_participant_data(Path(csv_file)))
    if not count:
        raise ValueError(
            "No eligible public participants; populate and validate the selected edition"
        )
    return count


def _require_complete(results: dict[str, dict[str, str]], expected: int) -> None:
    """Do not report success when the batch failed or stopped early."""
    failed = sum("error" in value for value in results.values())
    if len(results) != expected or failed:
        raise RuntimeError(
            f"Participant processing incomplete: {len(results) - failed}/{expected} succeeded; "
            "completed reports were preserved"
        )


def analyze_presenters(args):
    """Analyze presenter research profiles."""
    logger = logging.getLogger(__name__)

    try:
        # Setup configuration and API
        config = Config(config_file=Path(args.config) if getattr(args, "config", None) else None)
        api_client = APIClient.create(
            provider=args.api_provider or config.get("api.provider"),
            **{
                **config.get_api_config(args.api_provider),
                "api_key": config.get_api_key(args.api_provider),
            },
        )

        # Load domain context if provided
        domain_context = None
        if args.domain_file:
            domain_context = ReportReader.read_markdown(Path(args.domain_file))

        # Analyze presenters
        analyzer = PresenterAnalyzer(api_client, config.to_dict().get("data", {}))
        results = analyzer.analyze_all_presenters(
            Path(args.data_dir), Path(args.output_dir), domain_context, max_rows=args.max_rows
        )

        logger.info(f"✅ Successfully analyzed {len(results)} presenters")
        logger.info(f"📁 Reports saved to {args.output_dir}")

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise


def analyze_participants(args):
    """Analyze participant profiles with comprehensive background research and curricula."""
    logger = logging.getLogger(__name__)

    try:
        expected = _participant_count(args.csv_file)
        # Setup configuration and API
        config = Config(config_file=Path(args.config) if getattr(args, "config", None) else None)
        api_client = APIClient.create(
            provider=args.api_provider or config.get("api.provider"),
            **{
                **config.get_api_config(args.api_provider),
                "api_key": config.get_api_key(args.api_provider),
            },
        )

        # Analyze participants
        analyzer = ParticipantAnalyzer(api_client, config.to_dict().get("data", {}))
        results = analyzer.analyze_all_participants(
            Path(args.csv_file),
            Path(args.output_dir),
            include_background_research=args.include_background_research,
            include_curriculum=args.include_curriculum,
        )

        _require_complete(results, expected)

        logger.info(f"✅ Successfully analyzed {len(results)} participants")
        logger.info(f"📁 Reports saved to {args.output_dir}")

        # Generate column summaries and word clouds if requested
        if args.include_column_summaries:
            logger.info("📊 Generating column summaries and word clouds...")
            column_summaries = analyzer.generate_column_summaries(
                Path(args.csv_file), Path(args.output_dir) / "column_summaries"
            )
            logger.info(f"📊 Generated summaries for {len(column_summaries)} columns")

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise


def analyze_participant_backgrounds(args):
    """Generate comprehensive background research for all participants."""
    logger = logging.getLogger(__name__)

    try:
        expected = _participant_count(args.csv_file)
        # Setup configuration and API
        config = Config(config_file=Path(args.config) if getattr(args, "config", None) else None)
        api_client = APIClient.create(
            provider="perplexity",  # Force Perplexity for background research
            **{**config.get_api_config("perplexity"), "api_key": config.get_api_key("perplexity")},
        )

        # Analyze participants with background research only
        analyzer = ParticipantAnalyzer(api_client, config.to_dict().get("data", {}))
        results = analyzer.analyze_all_participants(
            Path(args.csv_file),
            Path(args.output_dir),
            include_background_research=True,
            include_curriculum=False,
            include_profile=False,
        )

        _require_complete(results, expected)

        logger.info(
            f"✅ Successfully generated background research for {len(results)} participants"
        )
        logger.info(f"📁 Background research reports saved to {args.output_dir}")

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise


def generate_participant_curricula(args):
    """Generate personalized Active Inference curricula for all participants."""
    logger = logging.getLogger(__name__)

    try:
        expected = _participant_count(args.csv_file)
        # Setup configuration and API
        config = Config(config_file=Path(args.config) if getattr(args, "config", None) else None)
        api_client = APIClient.create(
            provider=args.api_provider or config.get("api.provider"),
            **{
                **config.get_api_config(args.api_provider),
                "api_key": config.get_api_key(args.api_provider),
            },
        )

        # Analyze participants with curricula only
        analyzer = ParticipantAnalyzer(api_client, config.to_dict().get("data", {}))
        results = analyzer.analyze_all_participants(
            Path(args.csv_file),
            Path(args.output_dir),
            include_background_research=False,
            include_curriculum=True,
            include_profile=False,
        )

        _require_complete(results, expected)

        logger.info(f"✅ Successfully generated curricula for {len(results)} participants")
        logger.info(f"📁 Curriculum reports saved to {args.output_dir}")

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise
