"""Core functionality for the symposium package."""

from symposium.core.api import APIClient, BaseAPIProvider, PerplexityProvider, OpenRouterProvider
from symposium.core.config import Config
from symposium.core.logging_utils import setup_logging
from symposium.core.data_loader import DataLoader

__all__ = [
    "APIClient",
    "BaseAPIProvider",
    "PerplexityProvider",
    "OpenRouterProvider",
    "Config",
    "setup_logging",
    "DataLoader",
]

# Convenience function for loading participant data
def load_participant_data(csv_path):
    """Load participant data from Public_Participant_Information.csv format.

    Args:
        csv_path: Path to the participant CSV file

    Returns:
        Dictionary mapping participant names to their complete data
    """
    return DataLoader.load_participant_data(csv_path)

