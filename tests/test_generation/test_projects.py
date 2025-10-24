"""Tests for project generation module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import pandas as pd
from symposium.generation.projects import ProjectGenerator


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
            participant_name,
            participant_profile,
            domain_context,
            catechism_template
        )

        assert participant_name in prompt
        assert participant_profile in prompt
        assert domain_context in prompt
        assert catechism_template in prompt

    def test_generate_project_prompt_with_collaborators(self, generator):
        """Test project prompt generation with collaborators."""
        collaborators = "Researcher A, Researcher B"
        prompt = generator.generate_project_prompt(
            "Test Participant",
            "AI researcher",
            "AI domain",
            "# Template",
            collaborators
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

        with patch.object(generator.api_client, 'get_response', return_value=expected_response):
            result = generator.generate_project_proposal(
                "Test Participant",
                "AI researcher profile",
                "Active Inference domain",
                catechism_type="KarmaGAP",
                catechisms_dir=catechism_dir
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
        profile_json.write_text('{"content": "Test profile content", "metadata": {"presenter": "Test Participant"}}')

        # Setup catechism
        catechism_dir = temp_dir / "catechisms"
        catechism_dir.mkdir()
        catechism_file = catechism_dir / "KarmaGAPGrants.md"
        catechism_file.write_text("# Template")

        domain_file = temp_dir / "domain.md"
        domain_file.write_text("Active Inference domain")

        expected_response = "Project proposal for test participant"

        with patch.object(generator.api_client, 'get_response', return_value=expected_response):
            with patch('symposium.io.writers.ReportWriter.save_project_proposal') as mock_save:
                results = generator.generate_all_projects(
                    profiles_dir,
                    temp_dir / "outputs",
                    domain_file,
                    catechism_type="KarmaGAP",
                    catechisms_dir=catechism_dir
                )

        assert "Test_Participant" in results
        assert results["Test_Participant"] == expected_response
        mock_save.assert_called_once()

