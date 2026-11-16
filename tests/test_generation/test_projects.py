"""Tests for project generation module."""

import json
from unittest.mock import patch

import pytest

from symposium.core.api import PaymentRequiredError
from symposium.core.batch import BatchIncompleteError
from symposium.generation.projects import ProjectGenerator
from symposium.io.writers import ReportWriter


class TestProjectGenerator:
    """Tests for ProjectGenerator class."""

    @pytest.fixture
    def generator(self, mock_api_client, sample_config):
        """Create project generator for testing."""
        return ProjectGenerator(mock_api_client, sample_config)

    def test_init(self, mock_api_client, sample_config):
        """Test generator initialization."""
        generator = ProjectGenerator(mock_api_client, sample_config)
        assert generator.api_client == mock_api_client
        assert generator.config == sample_config

    def test_load_catechism_template(self, generator, temp_dir):
        """Test loading catechism template."""
        # Create test catechism file
        catechism_dir = temp_dir / "catechisms"
        catechism_dir.mkdir()
        catechism_file = catechism_dir / "KarmaGAPGrants.md"
        catechism_content = "# KarmaGAP Template\n\n1. What is the problem?"
        catechism_file.write_text(catechism_content)

        result = generator.load_catechism_template("KarmaGAP", catechism_dir)
        assert result == catechism_content

    def test_load_catechism_template_invalid(self, generator, temp_dir):
        """Test loading invalid catechism type."""
        with pytest.raises(ValueError, match="Unknown catechism type"):
            generator.load_catechism_template("InvalidType", temp_dir)

    def test_load_collaborators_list(self, generator, sample_markdown_file):
        """Test loading collaborators list."""
        result = generator.load_collaborators_list(sample_markdown_file)
        assert "Test Markdown" in result

    def test_generate_project_prompt(self, generator):
        """Test project prompt generation."""
        participant_name = "Test Participant"
        participant_profile = "AI researcher with background in machine learning"
        domain_context = "Active Inference in intelligent systems"
        catechism_template = "# Template\n\n1. Question 1?"

        prompt = generator.generate_project_prompt(
            participant_name, participant_profile, domain_context, catechism_template
        )

        assert participant_name in prompt
        assert participant_profile in prompt
        assert domain_context in prompt
        assert catechism_template in prompt

    def test_generate_project_prompt_with_collaborators(self, generator):
        """Test project prompt generation with collaborators."""
        collaborators = "Researcher A, Researcher B"
        prompt = generator.generate_project_prompt(
            "Test Participant", "AI researcher", "AI domain", "# Template", collaborators
        )

        assert "Researcher A" in prompt
        assert "Researcher B" in prompt

    def test_generate_project_proposal(self, generator, temp_dir):
        """Test project proposal generation."""
        # Setup test files
        catechism_dir = temp_dir / "catechisms"
        catechism_dir.mkdir()
        catechism_file = catechism_dir / "KarmaGAPGrants.md"
        catechism_file.write_text("# KarmaGAP Template")

        expected_response = "Generated project proposal"

        with patch.object(generator.api_client, "get_response", return_value=expected_response):
            result = generator.generate_project_proposal(
                "Test Participant",
                "AI researcher profile",
                "Active Inference domain",
                catechism_type="KarmaGAP",
                catechisms_dir=catechism_dir,
            )

        assert result == expected_response

    def test_generate_all_projects(self, generator, temp_dir):
        """Test generating all projects."""
        # Setup test directories
        profiles_dir = temp_dir / "profiles"
        profiles_dir.mkdir()

        # Create test profile
        profile_dir = profiles_dir / "Test_Participant"
        profile_dir.mkdir()
        profile_json = profile_dir / "Test_Participant_research_profile.json"
        profile_json.write_text(
            '{"content": "Test profile content", "metadata": {"presenter": "Test Participant"}}'
        )

        # Setup catechism
        catechism_dir = temp_dir / "catechisms"
        catechism_dir.mkdir()
        catechism_file = catechism_dir / "KarmaGAPGrants.md"
        catechism_file.write_text("# Template")

        domain_file = temp_dir / "domain.md"
        domain_file.write_text("Active Inference domain")

        expected_response = "Project proposal for test participant"

        with patch.object(generator.api_client, "get_response", return_value=expected_response):
            with patch("symposium.io.writers.ReportWriter.save_project_proposal") as mock_save:
                results = generator.generate_all_projects(
                    profiles_dir,
                    temp_dir / "outputs",
                    domain_file,
                    catechism_type="KarmaGAP",
                    catechisms_dir=catechism_dir,
                )

        assert "Test_Participant" in results
        assert results["Test_Participant"] == expected_response
        mock_save.assert_called_once()

    @pytest.mark.parametrize("format_name", ["markdown", "json"])
    def test_batch_counts_only_persisted_proposals(
        self, generator, tmp_path, monkeypatch, format_name
    ):
        participants = {
            name: {"name": name, "profile": "Synthetic researcher"}
            for name in ("First", "Second", "Later")
        }
        monkeypatch.setattr(
            generator.data_loader, "load_participant_profiles", lambda *a, **k: participants
        )
        domain = tmp_path / "domain.md"
        domain.write_text("Synthetic domain")
        (tmp_path / "KarmaGAPGrants.md").write_text("Synthetic proposal questions")
        method = f"save_{format_name}_report"
        original = getattr(ReportWriter, method)

        def save(content, filepath, *args, **kwargs):
            if filepath.parent.name == "Second":
                raise OSError("Synthetic storage failure")
            return original(content, filepath, *args, **kwargs)

        monkeypatch.setattr(ReportWriter, method, save)
        output = tmp_path / "reports"
        with pytest.raises(BatchIncompleteError) as exc:
            generator.generate_all_projects(tmp_path, output, domain, catechisms_dir=tmp_path)
        assert exc.value.requested == 3
        assert set(exc.value.completed) == {"First", "Later"}
        assert set(exc.value.failures) == {"Second"}
        for name in ("First", "Later"):
            report = output / name / f"{name}_project_proposal_KarmaGAP"
            assert (
                json.loads(report.with_suffix(".json").read_text())["content"]
                == "Mock API response"
            )
            assert "Mock API response" in report.with_suffix(".md").read_text()
        partial = output / "Second" / "Second_project_proposal_KarmaGAP"
        assert partial.with_suffix(".md").exists() is (format_name == "json")
        assert not partial.with_suffix(".json").exists()

    def test_payment_stops_after_preserving_completed_proposal(
        self, generator, tmp_path, monkeypatch
    ):
        participants = {
            name: {"name": name, "profile": "Synthetic researcher"}
            for name in ("First", "Second", "Later")
        }
        monkeypatch.setattr(
            generator.data_loader, "load_participant_profiles", lambda *a, **k: participants
        )
        domain = tmp_path / "domain.md"
        domain.write_text("Synthetic domain")
        (tmp_path / "KarmaGAPGrants.md").write_text("Synthetic proposal questions")
        generator.api_client.get_response.side_effect = [
            "Persisted proposal",
            PaymentRequiredError("Cannot generate without credits", "openrouter"),
            "Must not be requested",
        ]
        output = tmp_path / "reports"
        with pytest.raises(PaymentRequiredError):
            generator.generate_all_projects(tmp_path, output, domain, catechisms_dir=tmp_path)
        assert generator.api_client.get_response.call_count == 2
        first = output / "First" / "First_project_proposal_KarmaGAP"
        assert json.loads(first.with_suffix(".json").read_text())["content"] == "Persisted proposal"
        assert "Persisted proposal" in first.with_suffix(".md").read_text()
        assert not (output / "Second").exists()
        assert not (output / "Later").exists()

    def test_empty_batch_creates_no_proposals(self, generator, tmp_path):
        domain = tmp_path / "domain.md"
        domain.write_text("Synthetic domain")
        output = tmp_path / "reports"
        assert generator.generate_all_projects(tmp_path, output, domain) == {}
        assert not output.exists()
        generator.api_client.get_response.assert_not_called()
