"""Symposium: Research analysis and project generation for Active Inference Symposium.

This package provides tools for analyzing researcher profiles, generating
project proposals, and visualizing research networks for the Active Inference Symposium.
"""

__version__ = "3.1.0"

from symposium.calendar.exporter import ScheduleExporter
from symposium.core.api import APIClient
from symposium.core.config import Config

__all__ = ["APIClient", "Config", "ScheduleExporter", "__version__"]
