"""Tests for API client module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from symposium.core.api import (
    APIClient,
    BaseAPIProvider,
    PerplexityProvider,
    OpenRouterProvider,
    PaymentRequiredError,
)
from openai import APIStatusError


class TestAPIClient:
    """Tests for APIClient factory."""

    def test_create_perplexity_provider(self):
        """Test creating Perplexity provider."""
        provider = APIClient.create("perplexity", api_key="test_key")
        assert isinstance(provider, PerplexityProvider)
        assert provider.api_key == "test_key"

    def test_create_openrouter_provider(self):
        """Test creating OpenRouter provider."""
        provider = APIClient.create("openrouter", api_key="test_key")
        assert isinstance(provider, OpenRouterProvider)
        assert provider.api_key == "test_key"

    def test_create_invalid_provider(self):
        """Test creating invalid provider raises error."""
        with pytest.raises(ValueError, match="Unsupported provider"):
            APIClient.create("invalid", api_key="test_key")

    def test_create_without_api_key(self):
        """Test creating provider without API key raises error."""
        with pytest.raises(ValueError, match="API key .* not provided"):
            APIClient.create("perplexity")

    @patch.dict('os.environ', {'PERPLEXITY_API_KEY': 'env_key'})
    def test_create_with_env_api_key(self):
        """Test creating provider with API key from environment."""
        provider = APIClient.create("perplexity")
        assert isinstance(provider, PerplexityProvider)
        assert provider.api_key == "env_key"


class TestPerplexityProvider:
    """Tests for PerplexityProvider."""

    @patch('symposium.core.api.OpenAI')
    def test_init(self, mock_openai):
        """Test Perplexity provider initialization."""
        provider = PerplexityProvider("test_key")
        assert provider.api_key == "test_key"
        assert provider.model == "sonar"
        mock_openai.assert_called_once()

    @patch('symposium.core.api.OpenAI')
    def test_get_response(self, mock_openai):
        """Test getting response from Perplexity."""
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        provider = PerplexityProvider("test_key")
        response = provider.get_response("test prompt", "test system")

        assert response == "Test response"
        mock_client.chat.completions.create.assert_called_once()

    @patch('symposium.core.api.OpenAI')
    def test_get_response_empty(self, mock_openai):
        """Test getting empty response raises error."""
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = None
        mock_openai.return_value = mock_client

        provider = PerplexityProvider("test_key")
        
        with pytest.raises(ValueError, match="Empty response"):
            provider.get_response("test prompt")


class TestOpenRouterProvider:
    """Tests for OpenRouterProvider."""

    @patch('symposium.core.api.OpenAI')
    def test_init(self, mock_openai):
        """Test OpenRouter provider initialization."""
        provider = OpenRouterProvider("test_key")
        assert provider.api_key == "test_key"
        assert provider.model == "anthropic/claude-3.5-sonnet"
        mock_openai.assert_called_once()

    @patch('symposium.core.api.OpenAI')
    def test_get_response(self, mock_openai):
        """Test getting response from OpenRouter."""
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        provider = OpenRouterProvider("test_key")
        response = provider.get_response("test prompt", "test system")

        assert response == "Test response"


class TestRealAPIIntegration:
    """Integration tests using real API calls."""

    def test_perplexity_provider_real_api(self):
        """Test Perplexity provider with real API."""
        # Skip if no real API key available
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            pytest.skip("No Perplexity API key available")

        provider = PerplexityProvider(api_key)

        # Test simple prompt
        response = provider.get_response(
            "What is Active Inference in one sentence?",
            "You are a helpful AI assistant."
        )

        assert isinstance(response, str)
        assert len(response) > 0
        assert "Active Inference" in response

    def test_openrouter_provider_real_api(self):
        """Test OpenRouter provider with real API."""
        # Skip if no real API key available
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            pytest.skip("No OpenRouter API key available")

        provider = OpenRouterProvider(api_key)

        # Test simple prompt
        response = provider.get_response(
            "Explain Active Inference briefly.",
            "You are a helpful AI assistant."
        )

        assert isinstance(response, str)
        assert len(response) > 0
        assert "Active Inference" in response

    def test_api_client_with_real_keys(self):
        """Test API client creation with real keys from environment."""
        # Test Perplexity
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if api_key:
            provider = APIClient.create("perplexity")
            assert isinstance(provider, PerplexityProvider)
            assert provider.api_key == api_key

        # Test OpenRouter
        api_key = os.getenv("OPENROUTER_API_KEY")
        if api_key:
            provider = APIClient.create("openrouter")
            assert isinstance(provider, OpenRouterProvider)
            assert provider.api_key == api_key

    def test_cross_provider_compatibility(self):
        """Test that both providers can handle the same prompts."""
        perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        openrouter_key = os.getenv("OPENROUTER_API_KEY")

        if not perplexity_key or not openrouter_key:
            pytest.skip("Need both API keys for cross-provider test")

        prompt = "What is the Free Energy Principle?"
        system_prompt = "You are a helpful AI assistant specializing in cognitive science."

        # Test Perplexity
        perplexity_provider = PerplexityProvider(perplexity_key)
        perplexity_response = perplexity_provider.get_response(prompt, system_prompt)

        # Test OpenRouter
        openrouter_provider = OpenRouterProvider(openrouter_key)
        openrouter_response = openrouter_provider.get_response(prompt, system_prompt)

        # Both should return valid responses
        assert isinstance(perplexity_response, str)
        assert isinstance(openrouter_response, str)
        assert len(perplexity_response) > 0
        assert len(openrouter_response) > 0

        # Both should mention key concepts
        key_terms = ["free energy", "principle", "predictive"]
        perplexity_has_terms = any(term in perplexity_response.lower() for term in key_terms)
        openrouter_has_terms = any(term in openrouter_response.lower() for term in key_terms)

        assert perplexity_has_terms or openrouter_has_terms


class TestPaymentRequiredError:
    """Tests for PaymentRequiredError exception."""

    def test_payment_required_error_creation(self):
        """Test PaymentRequiredError creation and attributes."""
        error = PaymentRequiredError("Insufficient credits", provider="openrouter")
        
        assert error.provider == "openrouter"
        assert error.message == "Insufficient credits"
        assert "OPENROUTER API: Insufficient credits" in str(error)

    def test_payment_required_error_default_provider(self):
        """Test PaymentRequiredError with default provider."""
        error = PaymentRequiredError("Payment required")
        
        assert error.provider == "unknown"
        assert error.message == "Payment required"
        assert "UNKNOWN API: Payment required" in str(error)


class TestOpenRouterPaymentError:
    """Tests for OpenRouter payment error handling."""

    @patch('symposium.core.api.OpenAI')
    def test_openrouter_402_error_raises_payment_required(self, mock_openai):
        """Test OpenRouter provider raises PaymentRequiredError on 402 error."""
        # Setup mock to raise APIStatusError with 402
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            'error': {
                'message': 'Insufficient credits. Add more using https://openrouter.ai/settings/credits',
                'code': 402
            }
        }
        mock_response.status_code = 402
        
        api_error = APIStatusError(
            message="Insufficient credits",
            response=mock_response,
            body=None,
            request=None
        )
        api_error.status_code = 402
        api_error.response = mock_response
        
        mock_client.chat.completions.create.side_effect = api_error
        mock_openai.return_value = mock_client

        provider = OpenRouterProvider("test_key")
        
        with pytest.raises(PaymentRequiredError) as exc_info:
            provider.get_response("test prompt")
        
        assert exc_info.value.provider == "openrouter"
        assert "Insufficient credits" in exc_info.value.message

    @patch('symposium.core.api.OpenAI')
    def test_openrouter_402_error_without_response_body(self, mock_openai):
        """Test OpenRouter handles 402 error without response body."""
        mock_client = Mock()
        api_error = APIStatusError(
            message="Payment required",
            response=None,
            body=None,
            request=None
        )
        api_error.status_code = 402
        
        mock_client.chat.completions.create.side_effect = api_error
        mock_openai.return_value = mock_client

        provider = OpenRouterProvider("test_key")
        
        with pytest.raises(PaymentRequiredError) as exc_info:
            provider.get_response("test prompt")
        
        assert exc_info.value.provider == "openrouter"
        assert "Payment required" in exc_info.value.message

    @patch('symposium.core.api.OpenAI')
    def test_openrouter_non_402_error_passes_through(self, mock_openai):
        """Test OpenRouter passes through non-402 APIStatusErrors."""
        mock_client = Mock()
        api_error = APIStatusError(
            message="Rate limit exceeded",
            response=None,
            body=None,
            request=None
        )
        api_error.status_code = 429
        
        mock_client.chat.completions.create.side_effect = api_error
        mock_openai.return_value = mock_client

        provider = OpenRouterProvider("test_key")
        
        # Should raise the original APIStatusError, not PaymentRequiredError
        with pytest.raises(APIStatusError):
            provider.get_response("test prompt")

    @patch('symposium.core.api.OpenAI')
    def test_payment_error_no_retry(self, mock_openai):
        """Test that payment errors don't trigger retry logic."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            'error': {
                'message': 'Insufficient credits',
                'code': 402
            }
        }
        mock_response.status_code = 402
        
        api_error = APIStatusError(
            message="Insufficient credits",
            response=mock_response,
            body=None,
            request=None
        )
        api_error.status_code = 402
        api_error.response = mock_response
        
        mock_client.chat.completions.create.side_effect = api_error
        mock_openai.return_value = mock_client

        provider = OpenRouterProvider("test_key")
        
        # Should raise PaymentRequiredError immediately (no retries)
        with pytest.raises(PaymentRequiredError):
            provider.get_response("test prompt")
        
        # Verify it was only called once (no retries)
        assert mock_client.chat.completions.create.call_count == 1

