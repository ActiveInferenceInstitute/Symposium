"""Core functionality for the symposium package."""

from pathlib import Path
from typing import Dict, Any

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
    "load_participant_data",
]

# Convenience function for loading participant data
def load_participant_data(csv_path: str | Path) -> Dict[str, Dict[str, Any]]:
    """Load participant data from Public_Participant_Information.csv format.

    Args:
        csv_path: Path to the participant CSV file

    Returns:
        Dictionary mapping participant names to their complete data
    """
    return DataLoader.load_participant_data(csv_path)

