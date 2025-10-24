"""Integration tests for complete workflows."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import pandas as pd
import os
from symposium.core.api import APIClient
from symposium.core.config import Config
from symposium.analysis.presenters import PresenterAnalyzer
from symposium.generation.profiles import ProfileGenerator


class TestWorkflows:
    """Integration tests for complete workflows."""

    @pytest.fixture
    def workflow_config(self):
        """Create configuration for workflow tests."""
        return {
            'api': {
                'provider': 'perplexity',
                'perplexity': {
                    'model': 'test-model',
                    'temperature': 0.7,
                    'max_tokens': 1000
                }
            },
            'data': {
                'max_rows_per_file': 5,
                'max_prompt_tokens': 5000
            }
        }

    def test_complete_presenter_analysis_workflow(self, temp_dir, workflow_config):
        """Test complete presenter analysis workflow."""
        # Create test data
        presenter_dir = temp_dir / "Test_Presenter"
        presenter_dir.mkdir()

        # Create realistic test data
        topics_df = pd.DataFrame({
            'topic': ['Active Inference', 'Free Energy Principle', 'Bayesian Inference'],
            'count': [15, 12, 8]
        })
        topics_df.to_csv(presenter_dir / "openalex-group-by-test.csv", index=False)

        works_df = pd.DataFrame({
            'title': ['Understanding Active Inference', 'Free Energy in Practice', 'Bayesian Methods'],
            'publication_year': [2023, 2022, 2021],
            'cited_by_count': [45, 32, 28]
        })
        works_df.to_csv(presenter_dir / "works-test.csv", index=False)

        # Mock API client
        mock_client = Mock()
        mock_client.get_response.return_value = "Complete research analysis for the presenter"

        # Run workflow
        analyzer = PresenterAnalyzer(mock_client, workflow_config.get('data', {}))
        results = analyzer.analyze_all_presenters(
            temp_dir,
            temp_dir / "outputs",
            max_rows=3
        )

        # Verify results
        assert "Test_Presenter" in results
        assert len(results["Test_Presenter"]) > 0

        # Verify API was called
        mock_client.get_response.assert_called_once()

    def test_profile_generation_workflow(self, temp_dir, workflow_config):
        """Test complete profile generation workflow."""
        # Create test data
        presenter_dir = temp_dir / "Test_Researcher"
        presenter_dir.mkdir()

        topics_df = pd.DataFrame({'topic': ['Machine Learning'], 'count': [10]})
        topics_df.to_csv(presenter_dir / "openalex-group-by-test.csv", index=False)
        works_df = pd.DataFrame({'title': ['ML Paper'], 'publication_year': [2023]})
        works_df.to_csv(presenter_dir / "works-test.csv", index=False)

        # Mock API responses
        mock_client = Mock()
        mock_client.get_response.side_effect = ["Research profile", "Methods analysis"]

        # Run workflow
        generator = ProfileGenerator(mock_client, workflow_config.get('data', {}))
        results = generator.generate_all_profiles(
            temp_dir,
            temp_dir / "outputs",
            include_methods=True
        )

        # Verify results
        assert "Test_Researcher" in results
        assert "profile" in results["Test_Researcher"]
        assert "methods" in results["Test_Researcher"]

        # Verify API was called twice (profile + methods)
        assert mock_client.get_response.call_count == 2

    def test_error_handling_workflow(self, temp_dir, workflow_config):
        """Test workflow error handling."""
        # Create presenter directory but no valid CSV files
        presenter_dir = temp_dir / "Bad_Presenter"
        presenter_dir.mkdir()
        (presenter_dir / "invalid.txt").write_text("not a csv")

        mock_client = Mock()
        mock_client.get_response.side_effect = Exception("API Error")

        # Run workflow - should handle errors gracefully
        analyzer = PresenterAnalyzer(mock_client, workflow_config.get('data', {}))
        results = analyzer.analyze_all_presenters(temp_dir, temp_dir / "outputs")

        # Should complete without crashing, but no results
        assert results == {}

    def test_large_dataset_workflow(self, temp_dir, workflow_config):
        """Test workflow with larger dataset."""
        # Create multiple presenters
        presenters = []
        for i in range(3):
            presenter_name = f"Researcher_{i}"
            presenter_dir = temp_dir / presenter_name
            presenter_dir.mkdir()
            presenters.append(presenter_name)

            # Create data files
            topics_df = pd.DataFrame({
                'topic': [f'Topic_{j}' for j in range(5)],
                'count': [10 - j for j in range(5)]
            })
            topics_df.to_csv(presenter_dir / "openalex-group-by-test.csv", index=False)

            works_df = pd.DataFrame({
                'title': [f'Paper_{j}' for j in range(5)],
                'publication_year': [2023 - j for j in range(5)],
                'cited_by_count': [50 - j*10 for j in range(5)]
            })
            works_df.to_csv(presenter_dir / "works-test.csv", index=False)

        # Mock API responses
        mock_client = Mock()
        mock_client.get_response.return_value = "Analysis result"

        # Run workflow
        analyzer = PresenterAnalyzer(mock_client, workflow_config.get('data', {}))
        results = analyzer.analyze_all_presenters(
            temp_dir,
            temp_dir / "outputs",
            max_rows=3
        )

        # Verify all presenters processed
        for presenter in presenters:
            assert presenter in results

        # Verify API called for each presenter
        assert mock_client.get_response.call_count == len(presenters)

    def test_workflow_with_domain_context(self, temp_dir, workflow_config):
        """Test workflow with domain context."""
        # Create test data
        presenter_dir = temp_dir / "Test_Presenter"
        presenter_dir.mkdir()

        topics_df = pd.DataFrame({'topic': ['AI'], 'count': [5]})
        topics_df.to_csv(presenter_dir / "openalex-group-by-test.csv", index=False)
        works_df = pd.DataFrame({'title': ['Paper 1'], 'publication_year': [2023]})
        works_df.to_csv(presenter_dir / "works-test.csv", index=False)

        # Domain context
        domain_context = "Active Inference in cognitive systems"

        mock_client = Mock()
        mock_client.get_response.return_value = "Domain-specific analysis"

        # Run workflow
        analyzer = PresenterAnalyzer(mock_client, workflow_config.get('data', {}))
        results = analyzer.analyze_all_presenters(
            temp_dir,
            temp_dir / "outputs",
            domain_context=domain_context
        )

        # Verify domain context was used
        call_args = mock_client.get_response.call_args[0][0]  # First argument (prompt)
        assert domain_context in call_args

        assert "Test_Presenter" in results


class TestRealAPIWorkflows:
    """Integration tests using real API calls."""

    def test_real_api_presenter_analysis(self):
        """Test complete presenter analysis with real API."""
        # Skip if no API key available
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            pytest.skip("No Perplexity API key available")

        # Create temporary directory for test
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test data directory
            presenter_dir = Path(temp_dir) / "validation_test"
            presenter_dir.mkdir()

            # Create realistic OpenAlex-style CSV data
            topics_df = pd.DataFrame({
                'topic': ['Active Inference', 'Free Energy Principle', 'Predictive Coding', 'Bayesian Brain', 'Dynamic Causal Modeling'],
                'count': [25, 22, 18, 15, 12]
            })
            topics_df.to_csv(presenter_dir / "openalex-group-by-20241103.csv", index=False)

            works_df = pd.DataFrame({
                'title': [
                    'The free-energy principle: a unified brain theory?',
                    'Active inference: a process theory',
                    'Predictive coding in the brain',
                    'Dynamic causal modelling',
                    'The Bayesian brain: probabilistic approaches to neural coding'
                ],
                'publication_year': [2009, 2017, 2010, 2003, 2006],
                'cited_by_count': [1200, 850, 950, 1100, 800]
            })
            works_df.to_csv(presenter_dir / "works-20241103.csv", index=False)

            # Test with real API
            config = Config()
            api_client = APIClient.create("openrouter")  # Use OpenRouter since it works reliably

            analyzer = PresenterAnalyzer(api_client, config.to_dict().get('data', {}))
            results = analyzer.analyze_all_presenters(
                temp_dir,
                Path(temp_dir) / "real_outputs",
                domain_context="Active Inference research in cognitive neuroscience",
                max_rows=3
            )

            # Verify real API response
            assert "validation_test" in results
            analysis = results["validation_test"]

            assert isinstance(analysis, str)
            assert len(analysis) > 100

            # Check for expected content in real API response
            expected_terms = ["active inference", "free energy", "research", "neuroscience"]
            has_expected_content = any(term in analysis.lower() for term in expected_terms)
            assert has_expected_content

    def test_real_api_profile_generation(self):
        """Test profile generation with real API."""
        # Skip if no API key available
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            pytest.skip("No Perplexity API key available")

        # Create temporary directory for test
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test researcher data
            researcher_dir = Path(temp_dir) / "Test_Researcher"
            researcher_dir.mkdir()

            topics_df = pd.DataFrame({
                'topic': ['Machine Learning', 'Neural Networks', 'Deep Learning'],
                'count': [15, 12, 10]
            })
            topics_df.to_csv(researcher_dir / "openalex-group-by-20241103.csv", index=False)

            works_df = pd.DataFrame({
                'title': ['Deep Learning Methods', 'Neural Network Architectures', 'ML Applications'],
                'publication_year': [2022, 2021, 2023],
                'cited_by_count': [200, 150, 180]
            })
            works_df.to_csv(researcher_dir / "works-20241103.csv", index=False)

            # Test with real API
            config = Config()
            api_client = APIClient.create("openrouter")

            generator = ProfileGenerator(api_client, config.to_dict().get('data', {}))
            results = generator.generate_all_profiles(
                temp_dir,
                Path(temp_dir) / "real_profiles",
                domain_context="Artificial Intelligence and Machine Learning research",
                include_methods=True
            )

            # Verify real API responses
            assert "Test_Researcher" in results
            assert "profile" in results["Test_Researcher"]
            assert "methods" in results["Test_Researcher"]

            profile = results["Test_Researcher"]["profile"]
            methods = results["Test_Researcher"]["methods"]

            # Check content quality
            assert isinstance(profile, str)
            assert isinstance(methods, str)
            assert len(profile) > 50
            assert len(methods) > 50

    def test_cross_provider_analysis(self):
        """Test analysis with both Perplexity and OpenRouter."""
        from symposium.core.api import PerplexityProvider, OpenRouterProvider

        perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        openrouter_key = os.getenv("OPENROUTER_API_KEY")

        if not perplexity_key or not openrouter_key:
            pytest.skip("Need both API keys for cross-provider test")

        # Create temporary directory for test
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test data
            presenter_dir = Path(temp_dir) / "Cross_Provider_Test"
            presenter_dir.mkdir()

            topics_df = pd.DataFrame({
                'topic': ['Cognitive Science', 'Computational Neuroscience'],
                'count': [10, 8]
            })
            topics_df.to_csv(presenter_dir / "openalex-group-by-20241103.csv", index=False)

            works_df = pd.DataFrame({
                'title': ['Cognitive Computation Paper'],
                'publication_year': [2023],
                'cited_by_count': [50]
            })
            works_df.to_csv(presenter_dir / "works-20241103.csv", index=False)

            # Test both providers
            providers = {
                "perplexity": PerplexityProvider(perplexity_key),
                "openrouter": OpenRouterProvider(openrouter_key)
            }

            results = {}
            for provider_name, provider in providers.items():
                analyzer = PresenterAnalyzer(provider, {})
                workflow_results = analyzer.analyze_all_presenters(
                    temp_dir,
                    Path(temp_dir) / f"outputs_{provider_name}",
                    max_rows=2
                )
                results[provider_name] = workflow_results

            # Both should produce valid results
            for provider_name, workflow_results in results.items():
                assert "Cross_Provider_Test" in workflow_results
                analysis = workflow_results["Cross_Provider_Test"]

                assert isinstance(analysis, str)
                assert len(analysis) > 50

                # Check for domain-relevant content
                domain_terms = ["cognitive", "neuroscience", "research"]
                has_domain_content = any(term in analysis.lower() for term in domain_terms)
                assert has_domain_content

