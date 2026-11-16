"""Tests for profile generation module."""

import json
from unittest.mock import patch

import pandas as pd
import pytest

from symposium.core.api import PaymentRequiredError
from symposium.core.batch import BatchIncompleteError
from symposium.generation.profiles import ProfileGenerator
from symposium.io.writers import ReportWriter


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

        assert sample_presenter_data["name"] in prompt
        assert "METHOD NAME" in prompt
        assert "DETAILED DESCRIPTION" in prompt
        assert "RESULTS AND OUTCOMES" in prompt

    def test_generate_research_methods(self, generator, sample_presenter_data):
        """Test research methods generation."""
        expected_response = "Research methods analysis"

        with patch.object(generator.api_client, "get_response", return_value=expected_response):
            result = generator.generate_research_methods(sample_presenter_data)

        assert result == expected_response

    def test_generate_all_profiles(self, generator, temp_dir, sample_presenter_data):
        """Test generating all profiles."""
        # Create test data directory
        presenter_dir = temp_dir / "Test_Researcher"
        presenter_dir.mkdir()

        topics_df = pd.DataFrame({"topic": ["AI"], "count": [5]})
        topics_df.to_csv(presenter_dir / "openalex-group-by-test.csv", index=False)
        works_df = pd.DataFrame({"title": ["Paper 1"], "publication_year": [2023]})
        works_df.to_csv(presenter_dir / "works-test.csv", index=False)

        # Mock API responses
        with patch.object(generator.api_client, "get_response") as mock_get_response:
            mock_get_response.side_effect = ["Profile analysis", "Methods analysis"]

            with patch("symposium.io.writers.ReportWriter.save_presenter_report") as mock_save:
                results = generator.generate_all_profiles(
                    temp_dir, temp_dir / "outputs", include_methods=True
                )

        assert "Test_Researcher" in results
        assert "profile" in results["Test_Researcher"]
        assert "methods" in results["Test_Researcher"]
        assert mock_save.call_count == 2

    def test_generate_all_profiles_methods_only(self, generator, temp_dir, sample_presenter_data):
        """Test generating profiles without methods."""
        presenter_dir = temp_dir / "Test_Researcher"
        presenter_dir.mkdir()

        topics_df = pd.DataFrame({"topic": ["AI"], "count": [5]})
        topics_df.to_csv(presenter_dir / "openalex-group-by-test.csv", index=False)
        works_df = pd.DataFrame({"title": ["Paper 1"], "publication_year": [2023]})
        works_df.to_csv(presenter_dir / "works-test.csv", index=False)

        with patch.object(generator.api_client, "get_response", return_value="Profile only"):
            with patch("symposium.io.writers.ReportWriter.save_presenter_report") as mock_save:
                results = generator.generate_all_profiles(
                    temp_dir, temp_dir / "outputs", include_methods=False
                )

        assert "Test_Researcher" in results
        assert "profile" in results["Test_Researcher"]
        assert "methods" not in results["Test_Researcher"]
        mock_save.assert_called_once()

    @pytest.mark.parametrize("report_type", ["research_profile", "research_methods"])
    @pytest.mark.parametrize("format_name", ["markdown", "json"])
    def test_batch_requires_every_selected_report_format(
        self, generator, sample_presenter_data, tmp_path, monkeypatch, report_type, format_name
    ):
        presenters = {
            name: {**sample_presenter_data, "name": name} for name in ("First", "Second", "Later")
        }
        monkeypatch.setattr(
            generator.data_loader, "load_presenter_data", lambda *a, **k: presenters
        )
        method = f"save_{format_name}_report"
        original = getattr(ReportWriter, method)

        def save(content, filepath, *args, **kwargs):
            if filepath.stem == f"Second_{report_type}":
                raise OSError("Synthetic storage failure")
            return original(content, filepath, *args, **kwargs)

        monkeypatch.setattr(ReportWriter, method, save)
        output = tmp_path / "reports"
        with pytest.raises(BatchIncompleteError) as exc:
            generator.generate_all_profiles(tmp_path, output, include_methods=True)
        assert exc.value.requested == 3
        assert set(exc.value.completed) == {"First", "Later"}
        assert set(exc.value.failures) == {"Second"}
        for name in ("First", "Later"):
            for kind in ("research_profile", "research_methods"):
                report = output / name / f"{name}_{kind}"
                assert (
                    json.loads(report.with_suffix(".json").read_text())["content"]
                    == "Mock API response"
                )
                assert "Mock API response" in report.with_suffix(".md").read_text()
        partial = output / "Second" / f"Second_{report_type}"
        assert partial.with_suffix(".md").exists() is (format_name == "json")
        assert not partial.with_suffix(".json").exists()
        profile = output / "Second" / "Second_research_profile.json"
        assert profile.exists() is (report_type == "research_methods")
        if profile.exists():
            assert json.loads(profile.read_text())["content"] == "Mock API response"

    @pytest.mark.parametrize("include_methods", [False, True])
    def test_payment_stops_after_preserving_complete_profile(
        self, generator, sample_presenter_data, tmp_path, monkeypatch, include_methods
    ):
        presenters = {
            name: {**sample_presenter_data, "name": name} for name in ("First", "Second", "Later")
        }
        monkeypatch.setattr(
            generator.data_loader, "load_presenter_data", lambda *a, **k: presenters
        )
        responses = ["Persisted profile"]
        if include_methods:
            responses.append("Persisted methods")
        responses.extend(
            [PaymentRequiredError("Cannot generate without credits", "openrouter"), "Not requested"]
        )
        generator.api_client.get_response.side_effect = responses
        output = tmp_path / "reports"
        with pytest.raises(PaymentRequiredError):
            generator.generate_all_profiles(tmp_path, output, include_methods=include_methods)
        assert generator.api_client.get_response.call_count == (3 if include_methods else 2)
        profile = output / "First" / "First_research_profile.json"
        assert json.loads(profile.read_text())["content"] == "Persisted profile"
        methods = output / "First" / "First_research_methods.json"
        assert methods.exists() is include_methods
        if include_methods:
            assert json.loads(methods.read_text())["content"] == "Persisted methods"
        assert not (output / "Second").exists()
        assert not (output / "Later").exists()

    def test_empty_batch_creates_no_reports(self, generator, tmp_path):
        output = tmp_path / "reports"
        assert generator.generate_all_profiles(tmp_path, output) == {}
        assert not output.exists()
        generator.api_client.get_response.assert_not_called()
