"""Tests for profile generation module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import pandas as pd
from symposium.generation.profiles import ProfileGenerator


class TestProfileGenerator:
    """Tests for ProfileGenerator class."""

    @pytest.fixture
    def generator(self, mock_api_client, sample_config):
        """Create profile generator for testing."""
        return ProfileGenerator(mock_api_client, sample_config)

    def test_init(self, mock_api_client, sample_config):
        """Test generator initialization."""
        generator = ProfileGenerator(mock_api_client, sample_config)
        assert generator.api_client == mock_api_client
        assert generator.config == sample_config

    def test_generate_research_methods_prompt(self, generator, sample_presenter_data):
        """Test research methods prompt generation."""
        prompt = generator.generate_research_methods_prompt(sample_presenter_data)

        assert sample_presenter_data['name'] in prompt
        assert "METHOD NAME" in prompt
        assert "DETAILED DESCRIPTION" in prompt
        assert "RESULTS AND OUTCOMES" in prompt

    def test_generate_research_methods(self, generator, sample_presenter_data):
        """Test research methods generation."""
        expected_response = "Research methods analysis"

        with patch.object(generator.api_client, 'get_response', return_value=expected_response):
            result = generator.generate_research_methods(sample_presenter_data)

        assert result == expected_response

    def test_generate_all_profiles(self, generator, temp_dir, sample_presenter_data):
        """Test generating all profiles."""
        # Create test data directory
        presenter_dir = temp_dir / "Test_Researcher"
        presenter_dir.mkdir()

        topics_df = pd.DataFrame({'topic': ['AI'], 'count': [5]})
        topics_df.to_csv(presenter_dir / "openalex-group-by-test.csv", index=False)
        works_df = pd.DataFrame({'title': ['Paper 1'], 'publication_year': [2023]})
        works_df.to_csv(presenter_dir / "works-test.csv", index=False)

        # Mock API responses
        with patch.object(generator.api_client, 'get_response') as mock_get_response:
            mock_get_response.side_effect = ["Profile analysis", "Methods analysis"]

            with patch('symposium.io.writers.ReportWriter.save_presenter_report') as mock_save:
                results = generator.generate_all_profiles(
                    temp_dir,
                    temp_dir / "outputs",
                    include_methods=True
                )

        assert "Test_Researcher" in results
        assert "profile" in results["Test_Researcher"]
        assert "methods" in results["Test_Researcher"]
        assert mock_save.call_count == 2

    def test_generate_all_profiles_methods_only(self, generator, temp_dir, sample_presenter_data):
        """Test generating profiles without methods."""
        presenter_dir = temp_dir / "Test_Researcher"
        presenter_dir.mkdir()

        topics_df = pd.DataFrame({'topic': ['AI'], 'count': [5]})
        topics_df.to_csv(presenter_dir / "openalex-group-by-test.csv", index=False)
        works_df = pd.DataFrame({'title': ['Paper 1'], 'publication_year': [2023]})
        works_df.to_csv(presenter_dir / "works-test.csv", index=False)

        with patch.object(generator.api_client, 'get_response', return_value="Profile only"):
            with patch('symposium.io.writers.ReportWriter.save_presenter_report') as mock_save:
                results = generator.generate_all_profiles(
                    temp_dir,
                    temp_dir / "outputs",
                    include_methods=False
                )

        assert "Test_Researcher" in results
        assert "profile" in results["Test_Researcher"]
        assert "methods" not in results["Test_Researcher"]
        mock_save.assert_called_once()

