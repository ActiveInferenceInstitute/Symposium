"""Core functionality for the symposium package."""

from pathlib import Path

from symposium.core.api import (
    APIClient,
    BaseAPIProvider,
    OpenRouterProvider,
    PaymentRequiredError,
    PerplexityProvider,
)
from symposium.core.config import Config
from symposium.core.data_loader import DataLoader
from symposium.core.logging_utils import setup_logging
from symposium.core.participant_schema import Participant

__all__ = [
    "APIClient",
    "BaseAPIProvider",
    "PerplexityProvider",
    "OpenRouterProvider",
    "PaymentRequiredError",
    "Config",
    "setup_logging",
    "DataLoader",
    "load_participant_data",
]


# Convenience function for loading participant data
def load_participant_data(csv_path: str | Path) -> dict[str, Participant]:
    """Load participant data from Public_Participant_Information.csv format.

    Args:
        csv_path: Path to the participant CSV file

    Returns:
        Dictionary mapping participant names to their complete data
    """
    return DataLoader.load_participant_data(Path(csv_path))
