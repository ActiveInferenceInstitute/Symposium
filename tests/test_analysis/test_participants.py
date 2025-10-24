"""Tests for participant analysis module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import pandas as pd
from symposium.analysis.participants import ParticipantAnalyzer


class TestParticipantAnalyzer:
    """Tests for ParticipantAnalyzer class."""

    @pytest.fixture
    def analyzer(self, mock_api_client, sample_config):
        """Create participant analyzer for testing."""
        return ParticipantAnalyzer(mock_api_client, sample_config)

    def test_init(self, mock_api_client, sample_config):
        """Test analyzer initialization."""
        analyzer = ParticipantAnalyzer(mock_api_client, sample_config)
        assert analyzer.api_client == mock_api_client
        assert analyzer.config == sample_config

    def test_load_registration_data(self, analyzer, sample_csv_file):
        """Test loading registration data."""
        df = analyzer.load_registration_data(sample_csv_file)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_generate_participant_prompt(self, analyzer, sample_participant_data):
        """Test participant prompt generation."""
        prompt = analyzer.generate_participant_prompt(sample_participant_data)

        assert sample_participant_data['name'] in prompt
        assert "EXPERTISE ASSESSMENT" in prompt
        assert "LEARNING OPPORTUNITIES" in prompt
        assert "DEVELOPMENT ROADMAP" in prompt

    def test_generate_participant_prompt_with_domain(self, analyzer, sample_participant_data):
        """Test participant prompt generation with domain context."""
        domain_context = "Active Inference applications"
        prompt = analyzer.generate_participant_prompt(sample_participant_data, domain_context)

        assert domain_context in prompt
        assert "DOMAIN INTEGRATION" in prompt

    def test_analyze_participant(self, analyzer, sample_participant_data):
        """Test participant analysis."""
        expected_response = "Participant analysis result"

        with patch.object(analyzer.api_client, 'get_response', return_value=expected_response):
            result = analyzer.analyze_participant(sample_participant_data)

        assert result == expected_response

    def test_analyze_all_participants(self, analyzer, temp_dir, sample_csv_file):
        """Test analyzing all participants."""
        # Mock API response
        expected_response = "Analysis for test participant"

        with patch.object(analyzer.api_client, 'get_response', return_value=expected_response):
            with patch('symposium.io.writers.ReportWriter.save_participant_report') as mock_save:
                results = analyzer.analyze_all_participants(
                    sample_csv_file,
                    temp_dir / "outputs"
                )

        assert len(results) > 0
        mock_save.assert_called()

    def test_analyze_all_participants_api_error(self, analyzer, sample_csv_file):
        """Test handling API errors during batch analysis."""
        with patch.object(analyzer.api_client, 'get_response', side_effect=Exception("API Error")):
            results = analyzer.analyze_all_participants(sample_csv_file, Path("outputs"))

        # Should continue processing despite errors
        assert len(results) == 0

