"""
Comprehensive tests for 2025 Symposium participant functionality.

Tests cover:
- Data loading from Public_Participant_Information.csv
- Participant data integration
- Background research generation
- Personalized curriculum generation
- Column summaries and analysis
- Complete workflow integration
"""

import os
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

from symposium.core.data_loader import DataLoader
from symposium.core.api import APIClient, PerplexityProvider, OpenRouterProvider
from symposium.analysis.participants import ParticipantAnalyzer
from symposium.io.writers import ReportWriter


@pytest.fixture
def sample_participant_csv(tmp_path):
    """Create a sample participant CSV file for testing."""
    import csv
    
    csv_path = tmp_path / "test_participants.csv"
    
    # Write CSV properly with proper escaping
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Headers
        writer.writerow([
            'Can we share this information publicly?',
            'What is your name?',
            'What is your email?',
            'What are your affiliations?',
            'What is your ORCID?',
            'What is your background & prior works? Feel free to provide as much information & links as you like.',
            'What would be useful for you in the Symposium (pragmatic value)?',
            'What would be interesting or informative for you to learn from the Symposium (epistemic value)?',
            'How are you applying Active Inference? What domain, stage?',
            'What are the biggest hurdles or challenges facing Active Inference research and application?',
            'What would help you learn and apply Active Inference? E.g. resource, tool, or community development.',
            'How did you hear about the Symposium?',
            'How could Active Inference applications make impact in 2026? (Think big!)',
            'Any other comments or questions?'
        ])
        
        # Data rows
        writer.writerow([
            'Yes',
            'John Doe',
            'john@example.com',
            'Test University',
            '0000-0001-2345-6789',
            'PhD in Cognitive Science, researching active inference and predictive processing',
            'Networking opportunities',
            'Advanced mathematical foundations',
            'Computational neuroscience',
            'Lack of accessible tutorials',
            'Open source tools',
            'Discord',
            'Better understanding of consciousness',
            'Looking forward to it'
        ])
        
        writer.writerow([
            'Yes',
            'Jane Smith',
            'jane@example.com',
            'AI Lab',
            '0000-0002-3456-7890',
            'Machine Learning researcher, focus on reinforcement learning and active inference',
            'Collaboration opportunities',
            'Real-world applications',
            'Robotics research',
            'Computational complexity',
            'More code examples',
            'Website',
            'Autonomous systems',
            'None'
        ])
        
        writer.writerow([
            'Yes',
            'Bob Wilson',
            'bob@example.com',
            'Neuro Institute',
            '',
            'Neuroscience background',
            'Learning resources',
            'Theoretical foundations',
            'Early stage learning',
            'Mathematical complexity',
            'Beginner tutorials',
            'Friend',
            'Healthcare applications',
            ''
        ])
    
    return csv_path


@pytest.fixture
def sample_participant_data():
    """Sample participant data dictionary."""
    return {
        'name': 'John Doe',
        'email': 'john@example.com',
        'affiliations': 'Test University',
        'orcid': '0000-0001-2345-6789',
        'background': 'PhD in Cognitive Science, researching active inference and predictive processing',
        'pragmatic_value': 'Networking opportunities',
        'epistemic_value': 'Advanced mathematical foundations',
        'active_inference_application': 'Computational neuroscience',
        'challenges': 'Lack of accessible tutorials',
        'learning_needs': 'Open source tools',
        'heard_about': 'Discord',
        'future_impact': 'Better understanding of consciousness',
        'comments': 'Looking forward to it',
        'share_publicly': 'Yes',
        'row_index': 0
    }


@pytest.fixture
def mock_api_client():
    """Mock API client for testing."""
    mock = Mock()
    mock.get_response.return_value = "Mock LLM response with detailed analysis."
    return mock


class TestDataLoading:
    """Tests for participant data loading functionality."""

    def test_load_participant_data_basic(self, sample_participant_csv):
        """Test basic participant data loading."""
        participants = DataLoader.load_participant_data(sample_participant_csv)
        
        assert len(participants) == 3
        assert 'John Doe' in participants
        assert 'Jane Smith' in participants
        assert 'Bob Wilson' in participants

    def test_load_participant_data_fields(self, sample_participant_csv):
        """Test that all expected fields are present."""
        participants = DataLoader.load_participant_data(sample_participant_csv)
        participant = participants['John Doe']
        
        # Check all essential fields
        assert participant['name'] == 'John Doe'
        assert participant['email'] == 'john@example.com'
        assert participant['affiliations'] == 'Test University'
        assert participant['orcid'] == '0000-0001-2345-6789'
        assert 'PhD in Cognitive Science' in participant['background']
        assert participant['pragmatic_value'] == 'Networking opportunities'
        assert participant['epistemic_value'] == 'Advanced mathematical foundations'
        assert participant['active_inference_application'] == 'Computational neuroscience'
        assert participant['challenges'] == 'Lack of accessible tutorials'
        assert participant['learning_needs'] == 'Open source tools'
        assert participant['future_impact'] == 'Better understanding of consciousness'

    def test_load_participant_data_empty_fields(self, sample_participant_csv):
        """Test handling of empty fields."""
        participants = DataLoader.load_participant_data(sample_participant_csv)
        bob = participants['Bob Wilson']
        
        # Bob has empty ORCID and comments
        assert bob['orcid'] == ''
        assert bob['comments'] == ''
        assert bob['name'] == 'Bob Wilson'
        assert bob['background'] == 'Neuroscience background'  # Bob has background now

    def test_load_participant_data_public_only(self, tmp_path):
        """Test that only public participants are loaded."""
        csv_content = """Can we share this information publicly?,What is your name?
Yes,Public Person
No,Private Person
Yes,Another Public
"""
        csv_path = tmp_path / "test_public.csv"
        csv_path.write_text(csv_content)
        
        participants = DataLoader.load_participant_data(csv_path)
        
        assert len(participants) == 2
        assert 'Public Person' in participants
        assert 'Another Public' in participants
        assert 'Private Person' not in participants


class TestParticipantAnalyzer:
    """Tests for ParticipantAnalyzer functionality."""

    def test_analyzer_initialization(self, mock_api_client):
        """Test ParticipantAnalyzer initialization."""
        config = {'max_tokens': 2000}
        analyzer = ParticipantAnalyzer(mock_api_client, config)
        
        assert analyzer.api_client == mock_api_client
        assert analyzer.config == config
        assert analyzer.data_loader is not None

    def test_generate_background_research_prompt(self, mock_api_client, sample_participant_data):
        """Test background research prompt generation."""
        analyzer = ParticipantAnalyzer(mock_api_client)
        prompt = analyzer.generate_background_research_prompt(sample_participant_data)
        
        # Check that prompt includes key information
        assert 'John Doe' in prompt
        assert 'Test University' in prompt
        assert '0000-0001-2345-6789' in prompt
        assert 'PhD in Cognitive Science' in prompt
        assert 'ACADEMIC BACKGROUND' in prompt
        assert 'RESEARCH CONTRIBUTIONS' in prompt
        # Updated to match new prompt structure
        assert 'ACTIVE INFERENCE & RELATED RESEARCH' in prompt
        # Verify enhanced research instructions
        assert 'DEEP COMPREHENSIVE WEB RESEARCH' in prompt
        assert 'CRITICAL REQUIREMENTS' in prompt
        assert 'cite all sources' in prompt.lower()
        assert 'clickable' in prompt.lower() or 'links' in prompt.lower()

    def test_generate_curriculum_prompt(self, mock_api_client, sample_participant_data):
        """Test personalized curriculum prompt generation."""
        analyzer = ParticipantAnalyzer(mock_api_client)
        prompt = analyzer.generate_curriculum_prompt(sample_participant_data)
        
        # Check that prompt includes key information
        assert 'John Doe' in prompt
        assert 'Computational neuroscience' in prompt
        assert 'Networking opportunities' in prompt
        assert 'Advanced mathematical foundations' in prompt
        assert 'PERSONALIZED LEARNING PATH' in prompt
        assert 'HANDS-ON LEARNING' in prompt
        assert 'RESOURCES AND TOOLS' in prompt

    def test_research_participant_background(self, mock_api_client, sample_participant_data):
        """Test participant background research."""
        analyzer = ParticipantAnalyzer(mock_api_client)
        result = analyzer.research_participant_background(sample_participant_data)
        
        assert result == "Mock LLM response with detailed analysis."
        assert mock_api_client.get_response.called
        
        # Check that the prompt was properly constructed
        call_args = mock_api_client.get_response.call_args
        prompt = call_args[0][0]
        assert 'John Doe' in prompt
        assert 'ACADEMIC BACKGROUND' in prompt

    def test_generate_personalized_curriculum(self, mock_api_client, sample_participant_data):
        """Test personalized curriculum generation."""
        analyzer = ParticipantAnalyzer(mock_api_client)
        result = analyzer.generate_personalized_curriculum(sample_participant_data)
        
        assert result == "Mock LLM response with detailed analysis."
        assert mock_api_client.get_response.called
        
        # Check that the prompt was properly constructed
        call_args = mock_api_client.get_response.call_args
        prompt = call_args[0][0]
        assert 'John Doe' in prompt
        assert 'PERSONALIZED LEARNING PATH' in prompt

    def test_analyze_participant(self, mock_api_client, sample_participant_data):
        """Test participant profile analysis."""
        analyzer = ParticipantAnalyzer(mock_api_client)
        result = analyzer.analyze_participant(sample_participant_data)
        
        assert result == "Mock LLM response with detailed analysis."
        assert mock_api_client.get_response.called


class TestColumnSummaries:
    """Tests for column summary generation."""

    def test_get_column_summary_basic(self, sample_participant_csv):
        """Test basic column summary generation."""
        participants = DataLoader.load_participant_data(sample_participant_csv)
        summary = DataLoader.get_column_summary(participants, 'background')
        
        assert summary['column'] == 'background'
        assert summary['total_participants'] == 3
        assert summary['responses_count'] == 3  # All have backgrounds
        assert summary['response_rate'] == 1.0
        assert len(summary['values']) == 3

    def test_get_column_summary_partial_responses(self, sample_participant_csv):
        """Test column summary with partial responses."""
        participants = DataLoader.load_participant_data(sample_participant_csv)
        summary = DataLoader.get_column_summary(participants, 'comments')
        
        assert summary['column'] == 'comments'
        assert summary['total_participants'] == 3
        assert summary['responses_count'] == 1  # Only John has comments
        assert 0.3 < summary['response_rate'] < 0.4

    def test_get_column_summary_statistics(self, sample_participant_csv):
        """Test column summary statistics."""
        participants = DataLoader.load_participant_data(sample_participant_csv)
        summary = DataLoader.get_column_summary(participants, 'background')
        
        assert 'avg_response_length' in summary
        assert summary['avg_response_length'] > 0
        assert 'unique_responses' in summary
        assert summary['unique_responses'] == 3


class TestCompleteWorkflow:
    """Integration tests for complete workflow."""

    @patch('symposium.io.writers.ReportWriter.save_participant_report')
    def test_analyze_all_participants_profile_only(
        self, mock_save, mock_api_client, sample_participant_csv, tmp_path
    ):
        """Test analyzing all participants with profile analysis only."""
        output_dir = tmp_path / "output"
        analyzer = ParticipantAnalyzer(mock_api_client)
        
        results = analyzer.analyze_all_participants(
            sample_participant_csv,
            output_dir,
            include_background_research=False,
            include_curriculum=False
        )
        
        # Should have processed 3 participants
        assert len(results) == 3
        assert 'John Doe' in results
        assert 'Jane Smith' in results
        assert 'Bob Wilson' in results
        
        # Each should have profile analysis
        for name, result in results.items():
            assert 'profile_analysis' in result
            assert result['profile_analysis'] == "Mock LLM response with detailed analysis."
        
        # Should have saved 3 reports (profile only)
        assert mock_save.call_count == 3

    @patch('symposium.io.writers.ReportWriter.save_participant_report')
    def test_analyze_all_participants_with_perplexity(
        self, mock_save, mock_api_client, sample_participant_csv, tmp_path
    ):
        """Test analyzing all participants with separate Perplexity client for background."""
        output_dir = tmp_path / "output"
        
        # Create separate mock for Perplexity with enhanced web research capabilities
        mock_perplexity = Mock()
        mock_perplexity.get_response.return_value = """# Deep Web Research Results

## Academic Background
- PhD from Test University [link](https://test.edu/profile)
- Google Scholar: [link](https://scholar.google.com/test)

## Research Contributions
- Key Publication 1 [DOI: 10.1234/test](https://doi.org/10.1234/test)
- Citation metrics: h-index 15 [link](https://scholar.google.com/test)

## Professional Experience
- Current Position: Professor [link](https://test.edu)
- LinkedIn Profile [link](https://linkedin.com/in/test)

## Online Presence
- Personal Website: https://test.com
- GitHub: https://github.com/test
- ORCID: https://orcid.org/0000-0001-2345-6789

## References
[1] https://test.edu/profile
[2] https://scholar.google.com/test
[3] https://doi.org/10.1234/test"""
        
        analyzer = ParticipantAnalyzer(mock_api_client)
        
        results = analyzer.analyze_all_participants(
            sample_participant_csv,
            output_dir,
            include_background_research=True,
            include_curriculum=False,
            perplexity_client=mock_perplexity
        )
        
        # Should have processed 3 participants
        assert len(results) == 3
        
        # Each should have both profile and background
        for name, result in results.items():
            assert 'profile_analysis' in result
            assert 'background_research' in result
            # Background should use Perplexity response with links
            assert 'link' in result['background_research'] or 'http' in result['background_research']
        
        # Verify Perplexity was called with max_tokens parameter for comprehensive research
        perplexity_calls = mock_perplexity.get_response.call_args_list
        assert len(perplexity_calls) == 3
        for call in perplexity_calls:
            # Check that max_tokens was passed for longer responses
            assert 'max_tokens' in call[1]
            assert call[1]['max_tokens'] >= 4000
        
        # Should have saved 6 reports (profile + background for each)
        assert mock_save.call_count == 6

    @patch('symposium.io.writers.ReportWriter.save_participant_report')
    def test_analyze_all_participants_complete(
        self, mock_save, mock_api_client, sample_participant_csv, tmp_path
    ):
        """Test analyzing all participants with all features."""
        output_dir = tmp_path / "output"
        
        # Create separate mock for Perplexity
        mock_perplexity = Mock()
        mock_perplexity.get_response.return_value = "Mock Perplexity background research."
        
        analyzer = ParticipantAnalyzer(mock_api_client)
        
        results = analyzer.analyze_all_participants(
            sample_participant_csv,
            output_dir,
            include_background_research=True,
            include_curriculum=True,
            perplexity_client=mock_perplexity
        )
        
        # Should have processed 3 participants
        assert len(results) == 3
        
        # Each should have all three components
        for name, result in results.items():
            assert 'profile_analysis' in result
            assert 'background_research' in result
            assert 'curriculum' in result
            # Background should use Perplexity
            assert result['background_research'] == "Mock Perplexity background research."
            # Profile and curriculum should use OpenRouter
            assert result['profile_analysis'] == "Mock LLM response with detailed analysis."
            assert result['curriculum'] == "Mock LLM response with detailed analysis."
        
        # Should have saved 9 reports (3 per participant)
        assert mock_save.call_count == 9


class TestAPIIntegration:
    """Tests for API integration (require API keys in environment)."""

    @pytest.mark.skipif(
        not os.getenv('PERPLEXITY_API_KEY'),
        reason="Perplexity API key not available"
    )
    def test_perplexity_api_real(self):
        """Test real Perplexity API connection (if key available)."""
        client = APIClient.create('perplexity')
        response = client.get_response(
            "What is Active Inference in one sentence?",
            "You are a helpful assistant."
        )
        
        assert response is not None
        assert len(response) > 0
        assert 'active inference' in response.lower() or 'inference' in response.lower()

    @pytest.mark.skipif(
        not os.getenv('OPENROUTER_API_KEY'),
        reason="OpenRouter API key not available"
    )
    def test_openrouter_api_real(self):
        """Test real OpenRouter API connection (if key available)."""
        client = APIClient.create('openrouter')
        response = client.get_response(
            "What is Active Inference in one sentence?",
            "You are a helpful assistant."
        )
        
        assert response is not None
        assert len(response) > 0


class TestReportWriting:
    """Tests for report writing functionality."""

    def test_save_participant_report(self, tmp_path):
        """Test saving participant reports."""
        output_dir = tmp_path / "reports"
        content = "# Test Report\n\nThis is a test report."
        
        ReportWriter.save_participant_report(
            "John Doe",
            content,
            output_dir,
            "test_report"
        )
        
        # Check that files were created
        participant_dir = output_dir / "John_Doe"
        assert participant_dir.exists()
        
        md_file = participant_dir / "John_Doe_test_report.md"
        json_file = participant_dir / "John_Doe_test_report.json"
        
        assert md_file.exists()
        assert json_file.exists()
        
        # Check content
        md_content = md_file.read_text()
        assert "Test Report" in md_content
        assert content in md_content

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        # Test various special characters
        assert ReportWriter.sanitize_filename("John Doe") == "John_Doe"
        assert ReportWriter.sanitize_filename("John-Paul Smith") == "John-Paul_Smith"
        assert ReportWriter.sanitize_filename("Test@#$%^&*()") == "Test"
        assert ReportWriter.sanitize_filename("  Spaces  ") == "Spaces"


class TestDataFormatting:
    """Tests for data formatting utilities."""

    def test_format_participant_for_api(self, sample_participant_data):
        """Test formatting participant data for API."""
        formatted = DataLoader.format_participant_for_api(sample_participant_data)
        
        assert 'Name: John Doe' in formatted
        assert 'Affiliations: Test University' in formatted
        assert 'ORCID: 0000-0001-2345-6789' in formatted
        assert 'Background & Prior Works:' in formatted
        assert 'PhD in Cognitive Science' in formatted
        assert 'Active Inference Application: Computational neuroscience' in formatted

    def test_format_participant_minimal_data(self):
        """Test formatting with minimal participant data."""
        minimal_data = {
            'name': 'Test Person',
            'background': '',
            'orcid': ''
        }
        
        formatted = DataLoader.format_participant_for_api(minimal_data)
        
        assert 'Name: Test Person' in formatted
        # Should handle empty fields gracefully
        assert 'ORCID:' not in formatted or 'ORCID: \n' in formatted


class TestErrorHandling:
    """Tests for error handling and edge cases."""

    def test_load_nonexistent_file(self):
        """Test loading from non-existent file."""
        with pytest.raises(FileNotFoundError):
            DataLoader.load_csv(Path("/nonexistent/file.csv"))

    def test_analyze_with_api_error(self, sample_participant_data, tmp_path):
        """Test handling of API errors."""
        # Create mock that raises exception
        mock_client = Mock()
        mock_client.get_response.side_effect = Exception("API Error")
        
        analyzer = ParticipantAnalyzer(mock_client)
        
        # Should raise exception
        with pytest.raises(Exception):
            analyzer.research_participant_background(sample_participant_data)

    def test_empty_csv_file(self, tmp_path):
        """Test handling of empty CSV file."""
        csv_path = tmp_path / "empty.csv"
        csv_path.write_text("Can we share this information publicly?,What is your name?\n")
        
        participants = DataLoader.load_participant_data(csv_path)
        
        # Should return empty dictionary
        assert len(participants) == 0


class TestTokenManagement:
    """Tests for token estimation and management."""

    def test_estimate_token_count(self):
        """Test token count estimation."""
        text = "This is a test sentence with ten words in it here."
        tokens = DataLoader.estimate_token_count(text)
        
        # Should be roughly word_count / 0.75
        assert tokens > 10
        assert tokens < 20

    def test_truncate_to_tokens(self):
        """Test text truncation to token limit."""
        text = " ".join(["word"] * 100)
        truncated = DataLoader.truncate_to_tokens(text, max_tokens=50)
        
        # Should be shorter than original
        assert len(truncated) < len(text)
        
        # Should not exceed token limit (approximately)
        tokens = DataLoader.estimate_token_count(truncated)
        assert tokens <= 50


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

