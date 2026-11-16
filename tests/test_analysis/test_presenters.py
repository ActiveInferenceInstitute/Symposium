"""Tests for presenter analysis module."""

import json
from unittest.mock import patch

import pandas as pd
import pytest

from symposium.analysis.presenters import PresenterAnalyzer
from symposium.core.api import PaymentRequiredError
from symposium.core.batch import BatchIncompleteError
from symposium.io.writers import ReportWriter


class TestPresenterAnalyzer:
    """Tests for PresenterAnalyzer class."""

    @pytest.fixture
    def analyzer(self, mock_api_client, sample_config):
        """Create presenter analyzer for testing."""
        return PresenterAnalyzer(mock_api_client, sample_config)

    def test_init(self, mock_api_client, sample_config):
        """Test analyzer initialization."""
        analyzer = PresenterAnalyzer(mock_api_client, sample_config)
        assert analyzer.api_client == mock_api_client
        assert analyzer.config == sample_config

    def test_generate_research_prompt(self, analyzer, sample_presenter_data):
        """Test research prompt generation."""
        prompt = analyzer.generate_research_prompt(sample_presenter_data)

        assert "Test Presenter" in prompt
        assert "RESEARCH FOCUS" in prompt
        assert "IMPACT AND INFLUENCE" in prompt
        assert "FUTURE DIRECTIONS" in prompt
        assert len(prompt) > 100

    def test_generate_research_prompt_with_domain(self, analyzer, sample_presenter_data):
        """Test research prompt generation with domain context."""
        domain_context = "Active Inference research in intelligent systems"
        prompt = analyzer.generate_research_prompt(sample_presenter_data, domain_context)

        assert domain_context in prompt
        assert "DOMAIN RELEVANCE" in prompt

    def test_analyze_presenter(self, analyzer, sample_presenter_data):
        """Test presenter analysis."""
        expected_response = "This is a mock analysis of the presenter's research."

        with patch.object(analyzer.api_client, "get_response", return_value=expected_response):
            result = analyzer.analyze_presenter(sample_presenter_data)

        assert result == expected_response

    def test_analyze_presenter_with_system_prompt(self, analyzer, sample_presenter_data):
        """Test presenter analysis with custom system prompt."""
        expected_response = "Custom system prompt analysis"

        with patch.object(
            analyzer.api_client, "get_response", return_value=expected_response
        ) as mock_get_response:
            analyzer.analyze_presenter(sample_presenter_data, system_prompt="Custom system prompt")

        # Verify system prompt was passed to API
        mock_get_response.assert_called_once()
        # Check that the system prompt was passed as the second argument
        call_args = mock_get_response.call_args
        assert call_args[0][1] == "Custom system prompt"  # Second positional argument

    def test_analyze_all_presenters(self, analyzer, temp_dir, sample_presenter_data):
        """Test analyzing all presenters."""
        # Create test data directory
        presenter_dir = temp_dir / "Test_Presenter"
        presenter_dir.mkdir()

        # Create mock CSV files
        topics_df = pd.DataFrame({"topic": ["AI", "ML"], "count": [10, 5]})
        topics_df.to_csv(presenter_dir / "openalex-group-by-test.csv", index=False)

        works_df = pd.DataFrame(
            {
                "title": ["Paper 1", "Paper 2"],
                "publication_year": [2023, 2022],
                "cited_by_count": [50, 30],
            }
        )
        works_df.to_csv(presenter_dir / "works-test.csv", index=False)

        # Mock API response
        expected_response = f"Analysis for {sample_presenter_data['name']}"

        with patch.object(analyzer.api_client, "get_response", return_value=expected_response):
            with patch("symposium.io.writers.ReportWriter.save_presenter_report") as mock_save:
                results = analyzer.analyze_all_presenters(
                    temp_dir, temp_dir / "outputs", max_rows=5
                )

        assert "Test_Presenter" in results
        assert results["Test_Presenter"] == expected_response
        mock_save.assert_called_once()

    def test_analyze_all_presenters_no_data(self, analyzer, temp_dir):
        """Test analyzing presenters with no data."""
        results = analyzer.analyze_all_presenters(temp_dir, temp_dir / "outputs")
        assert results == {}

    def test_analyze_all_presenters_api_error(self, analyzer, temp_dir, sample_presenter_data):
        """Test handling API errors during batch analysis."""
        presenter_dir = temp_dir / "Test_Presenter"
        presenter_dir.mkdir()

        topics_df = pd.DataFrame({"topic": ["AI"], "count": [5]})
        topics_df.to_csv(presenter_dir / "openalex-group-by-test.csv", index=False)
        works_df = pd.DataFrame({"title": ["Paper 1"], "publication_year": [2023]})
        works_df.to_csv(presenter_dir / "works-test.csv", index=False)

        with patch.object(analyzer.api_client, "get_response", side_effect=Exception("API Error")):
            with pytest.raises(BatchIncompleteError) as exc:
                analyzer.analyze_all_presenters(temp_dir, temp_dir / "outputs")
        assert exc.value.completed == {}
        assert set(exc.value.failures) == {"Test_Presenter"}
        assert exc.value.requested == 1

    @pytest.mark.parametrize("format_name", ["markdown", "json"])
    def test_batch_counts_only_persisted_reports(
        self, analyzer, sample_presenter_data, tmp_path, monkeypatch, format_name
    ):
        presenters = {
            name: {**sample_presenter_data, "name": name} for name in ("First", "Second", "Later")
        }
        monkeypatch.setattr(analyzer, "load_presenter_data", lambda *a, **k: presenters)
        method = f"save_{format_name}_report"
        original = getattr(ReportWriter, method)

        def save(content, filepath, *args, **kwargs):
            if filepath.parent.name == "Second":
                raise OSError("Synthetic storage failure")
            return original(content, filepath, *args, **kwargs)

        monkeypatch.setattr(ReportWriter, method, save)
        output = tmp_path / "reports"
        with pytest.raises(BatchIncompleteError) as exc:
            analyzer.analyze_all_presenters(tmp_path, output)
        assert exc.value.requested == 3
        assert set(exc.value.completed) == {"First", "Later"}
        assert set(exc.value.failures) == {"Second"}
        assert exc.value.output_dir == output
        for name in ("First", "Later"):
            report = output / name / f"{name}_research_profile"
            assert (
                json.loads(report.with_suffix(".json").read_text())["content"]
                == "Mock API response"
            )
            assert "Mock API response" in report.with_suffix(".md").read_text()
        partial = output / "Second" / "Second_research_profile"
        assert partial.with_suffix(".md").exists() is (format_name == "json")
        assert not partial.with_suffix(".json").exists()

    def test_payment_stops_after_preserving_completed_presenter(
        self, analyzer, sample_presenter_data, tmp_path, monkeypatch
    ):
        presenters = {
            name: {**sample_presenter_data, "name": name} for name in ("First", "Second", "Later")
        }
        monkeypatch.setattr(analyzer, "load_presenter_data", lambda *a, **k: presenters)
        analyzer.api_client.get_response.side_effect = [
            "Persisted presenter",
            PaymentRequiredError("Cannot generate without credits", "openrouter"),
            "Must not be requested",
        ]
        output = tmp_path / "reports"
        with pytest.raises(PaymentRequiredError):
            analyzer.analyze_all_presenters(tmp_path, output)
        assert analyzer.api_client.get_response.call_count == 2
        first = output / "First" / "First_research_profile"
        assert (
            json.loads(first.with_suffix(".json").read_text())["content"] == "Persisted presenter"
        )
        assert "Persisted presenter" in first.with_suffix(".md").read_text()
        assert not (output / "Second").exists()
        assert not (output / "Later").exists()
