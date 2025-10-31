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

    def test_load_participant_data(self, analyzer, temp_dir):
        """Test loading participant data."""
        # Create a proper participant CSV file with expected column names
        import pandas as pd
        csv_path = temp_dir / "participants.csv"
        df = pd.DataFrame({
            'Can we share this information publicly?': ['Yes', 'Yes'],
            'What is your name?': ['Test Participant 1', 'Test Participant 2'],
            'What is your email?': ['test1@example.com', 'test2@example.com'],
            'What are your affiliations?': ['University A', 'University B'],
            'What is your ORCID?': ['0000-0000-0000-0001', '0000-0000-0000-0002'],
            'What is your background & prior works? Feel free to provide as much information & links as you like.': ['PhD in Computer Science', 'MSc in Mathematics'],
            'What would be useful for you in the Symposium (pragmatic value)?': ['Networking', 'Learning'],
            'What would be interesting or informative for you to learn from the Symposium (epistemic value)?': ['Theory', 'Applications'],
            'How are you applying Active Inference? What domain, stage?': ['Research', 'Teaching'],
            'What are the biggest hurdles or challenges facing Active Inference research and application?': ['Theory', 'Practice'],
            'What would help you learn and apply Active Inference? E.g. resource, tool, or community development.': ['Advanced topics', 'Practical applications'],
            'How did you hear about the Symposium?': ['Website', 'Email'],
            'How could Active Inference applications make impact in 2026? (Think big!)': ['Healthcare', 'Education'],
            'Any other comments or questions?': ['None', 'None']
        })
        df.to_csv(csv_path, index=False)
        
        participants = analyzer.load_participant_data(csv_path)
        assert isinstance(participants, dict)
        assert len(participants) > 0

    def test_generate_background_research_prompt(self, analyzer, sample_participant_data):
        """Test background research prompt generation."""
        prompt = analyzer.generate_background_research_prompt(sample_participant_data)

        assert sample_participant_data['name'] in prompt
        assert "DEEP COMPREHENSIVE WEB RESEARCH" in prompt
        assert "ACADEMIC BACKGROUND" in prompt

    def test_generate_curriculum_prompt(self, analyzer, sample_participant_data):
        """Test curriculum prompt generation."""
        prompt = analyzer.generate_curriculum_prompt(sample_participant_data)

        assert sample_participant_data['name'] in prompt
        assert "personalized learning curriculum" in prompt.lower() or "PERSONALIZED LEARNING PATH" in prompt

    def test_analyze_participant(self, analyzer, sample_participant_data):
        """Test participant analysis."""
        expected_response = "Participant analysis result"

        with patch.object(analyzer.api_client, 'get_response', return_value=expected_response):
            result = analyzer.analyze_participant(sample_participant_data)

        assert result == expected_response

    def test_analyze_all_participants(self, analyzer, temp_dir):
        """Test analyzing all participants."""
        # Create a proper participant CSV file with expected column names
        import pandas as pd
        csv_path = temp_dir / "participants.csv"
        df = pd.DataFrame({
            'Can we share this information publicly?': ['Yes'],
            'What is your name?': ['Test Participant 1'],
            'What is your email?': ['test1@example.com'],
            'What are your affiliations?': ['University A'],
            'What is your ORCID?': ['0000-0000-0000-0001'],
            'What is your background & prior works? Feel free to provide as much information & links as you like.': ['PhD in Computer Science'],
            'What would be useful for you in the Symposium (pragmatic value)?': ['Networking'],
            'What would be interesting or informative for you to learn from the Symposium (epistemic value)?': ['Theory'],
            'How are you applying Active Inference? What domain, stage?': ['Research'],
            'What are the biggest hurdles or challenges facing Active Inference research and application?': ['Theory'],
            'What would help you learn and apply Active Inference? E.g. resource, tool, or community development.': ['Advanced topics'],
            'How did you hear about the Symposium?': ['Website'],
            'How could Active Inference applications make impact in 2026? (Think big!)': ['Healthcare'],
            'Any other comments or questions?': ['None']
        })
        df.to_csv(csv_path, index=False)
        
        # Mock API response
        expected_response = "Analysis for test participant"

        with patch.object(analyzer.api_client, 'get_response', return_value=expected_response):
            with patch('symposium.io.writers.ReportWriter.save_participant_report') as mock_save:
                results = analyzer.analyze_all_participants(
                    csv_path,
                    Path(temp_dir) / "outputs"
                )

        assert len(results) > 0
        mock_save.assert_called()

    def test_analyze_all_participants_api_error(self, analyzer, sample_csv_file):
        """Test handling API errors during batch analysis."""
        with patch.object(analyzer.api_client, 'get_response', side_effect=Exception("API Error")):
            results = analyzer.analyze_all_participants(sample_csv_file, Path("outputs"))

        # Should continue processing despite errors
        assert len(results) == 0

