"""Tests for API client module."""

import json
import os
from unittest.mock import Mock, patch

import httpx
import pytest
from openai import APIStatusError, OpenAI

from symposium.core.api import (
    APIClient,
    OpenRouterProvider,
    PaymentRequiredError,
    PerplexityProvider,
)
from symposium.core.config import Config


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

    def test_create_without_api_key(self, monkeypatch):
        """Test creating provider without API key raises error."""
        # Ensure no key leaks in from the environment (includes .env picked up by Config)
        monkeypatch.delenv("PERPLEXITY_API_KEY", raising=False)
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        with pytest.raises(ValueError, match="API key .* not provided"):
            APIClient.create("perplexity")

    @patch.dict("os.environ", {"PERPLEXITY_API_KEY": "env_key"})
    def test_create_with_env_api_key(self):
        """Test creating provider with API key from environment."""
        provider = APIClient.create("perplexity")
        assert isinstance(provider, PerplexityProvider)
        assert provider.api_key == "env_key"


class TestPerplexityProvider:
    """Tests for PerplexityProvider."""

    @patch("symposium.core.api.OpenAI")
    def test_init(self, mock_openai):
        """Test Perplexity provider initialization."""
        provider = PerplexityProvider("test_key")
        assert provider.api_key == "test_key"
        assert provider.model == "sonar"
        mock_openai.assert_called_once_with(
            api_key="test_key",
            base_url="https://api.perplexity.ai",
            default_headers={"X-Pplx-Integration": "symposium"},
        )

    @patch("symposium.core.api.OpenAI")
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

    @patch("symposium.core.api.OpenAI")
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

    @patch("symposium.core.api.OpenAI")
    def test_init(self, mock_openai):
        """Test OpenRouter provider initialization."""
        provider = OpenRouterProvider("test_key")
        assert provider.api_key == "test_key"
        assert provider.model == "anthropic/claude-3.5-sonnet"
        mock_openai.assert_called_once()
        assert "default_headers" not in mock_openai.call_args.kwargs

    @patch("symposium.core.api.OpenAI")
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


@pytest.mark.real_api
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
            "What is Active Inference in one sentence?", "You are a helpful AI assistant."
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
            "Explain Active Inference briefly.", "You are a helpful AI assistant."
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

    @patch("symposium.core.api.OpenAI")
    def test_openrouter_402_error_raises_payment_required(self, mock_openai):
        """Test OpenRouter provider raises PaymentRequiredError on 402 error."""
        # Setup mock to raise APIStatusError with 402
        mock_client = Mock()
        request = httpx.Request("POST", "https://api.openrouter.ai/api/v1/chat/completions")
        response = httpx.Response(
            status_code=402,
            request=request,
            json={
                "error": {
                    "message": "Insufficient credits. Add more using https://openrouter.ai/settings/credits",
                    "code": 402,
                }
            },
        )
        api_error = APIStatusError(message="Insufficient credits", response=response, body=None)

        mock_client.chat.completions.create.side_effect = api_error
        mock_openai.return_value = mock_client

        provider = OpenRouterProvider("test_key")

        with pytest.raises(PaymentRequiredError) as exc_info:
            provider.get_response("test prompt")

        assert exc_info.value.provider == "openrouter"
        assert "Insufficient credits" in exc_info.value.message

    @patch("symposium.core.api.OpenAI")
    def test_openrouter_402_error_without_response_body(self, mock_openai):
        """Test OpenRouter handles 402 error without response body."""
        mock_client = Mock()
        request = httpx.Request("POST", "https://api.openrouter.ai/api/v1/chat/completions")
        # No JSON body: response.json() raises, so the provider must fall back to str(e)
        response = httpx.Response(status_code=402, request=request)
        api_error = APIStatusError(message="Payment required", response=response, body=None)

        mock_client.chat.completions.create.side_effect = api_error
        mock_openai.return_value = mock_client

        provider = OpenRouterProvider("test_key")

        with pytest.raises(PaymentRequiredError) as exc_info:
            provider.get_response("test prompt")

        assert exc_info.value.provider == "openrouter"
        assert "Payment required" in exc_info.value.message

    @patch("symposium.core.api.OpenAI")
    def test_openrouter_non_402_error_passes_through(self, mock_openai):
        """Test OpenRouter passes through non-402 APIStatusErrors."""
        mock_client = Mock()
        request = httpx.Request("POST", "https://api.openrouter.ai/api/v1/chat/completions")
        response = httpx.Response(status_code=429, request=request)
        api_error = APIStatusError(message="Rate limit exceeded", response=response, body=None)

        mock_client.chat.completions.create.side_effect = api_error
        mock_openai.return_value = mock_client

        provider = OpenRouterProvider("test_key")

        # Should raise the original APIStatusError, not PaymentRequiredError
        with pytest.raises(APIStatusError):
            provider.get_response("test prompt")

    @pytest.mark.parametrize(
        "message",
        [
            "Insufficient credits",
            "Cannot generate without credits",
            "Payment rate exceeded",
            "Payment timeout",
        ],
    )
    def test_payment_error_no_retry(self, message, monkeypatch):
        """A real SDK 402 response is terminal even when its text looks retryable."""
        attempts = []

        def respond(request):
            attempts.append(request)
            return httpx.Response(402, json={"error": {"message": message, "code": 402}})

        monkeypatch.setattr("backoff._sync.time.sleep", lambda delay: None)
        with OpenAI(
            api_key="offline-key",
            base_url="https://openrouter.invalid/api/v1",
            max_retries=0,
            http_client=httpx.Client(transport=httpx.MockTransport(respond)),
        ) as client:
            monkeypatch.setattr("symposium.core.api.OpenAI", lambda **kwargs: client)
            provider = OpenRouterProvider("offline-key")
            with pytest.raises(PaymentRequiredError) as exc:
                provider.get_response("Synthetic payment regression")
            assert exc.value.message == message
        assert len(attempts) == 1


@pytest.mark.parametrize("content", [None, ""])
@patch("symposium.core.api.OpenAI")
def test_perplexity_rejects_missing_content(mock_openai, content):
    response = Mock()
    response.choices = [Mock(message=Mock(content=content))]
    mock_openai.return_value.chat.completions.create.return_value = response
    with pytest.raises(ValueError):
        PerplexityProvider("offline-key").get_response("Synthetic empty response")


@pytest.mark.parametrize(
    "file_provider,environment_provider,explicit_provider,environment_keys,explicit_key,expected",
    [
        (None, None, None, False, None, "perplexity"),
        ("openrouter", None, None, False, None, "openrouter"),
        ("perplexity", "openrouter", None, True, None, "openrouter"),
        ("openrouter", "openrouter", "perplexity", True, None, "perplexity"),
        ("openrouter", None, None, True, "explicit-key", "openrouter"),
    ],
)
def test_configured_provider_uses_selected_credentials_and_options(
    tmp_path,
    monkeypatch,
    offline_api_requests,
    file_provider,
    environment_provider,
    explicit_provider,
    environment_keys,
    explicit_key,
    expected,
):
    api = {
        name: {
            "api_key": f"file-{name}",
            "model": f"selected-{name}",
            "temperature": 0.2,
            "max_tokens": 123,
        }
        for name in ("perplexity", "openrouter")
    }
    if file_provider is not None:
        api["provider"] = file_provider
    selected_file = tmp_path / "selected.json"
    selected_file.write_text(json.dumps({"api": api}))
    (tmp_path / "config.json").write_text('{"api":{"provider":"invalid"}}')
    if environment_provider is not None:
        monkeypatch.setenv("API_PROVIDER", environment_provider)
    if environment_keys:
        for name in ("perplexity", "openrouter"):
            monkeypatch.setenv(f"{name.upper()}_API_KEY", f"environment-{name}")
    config = Config(config_file=selected_file, load_env=False)
    before = config.to_dict()
    provider = APIClient.from_config(config, provider=explicit_provider, api_key=explicit_key)
    assert provider.get_response("Synthetic configured request") == "Offline provider response"
    (request,) = offline_api_requests
    host = "api.perplexity.ai" if expected == "perplexity" else "openrouter.ai"
    assert request.url.host == host
    key = explicit_key or f"{'environment' if environment_keys else 'file'}-{expected}"
    assert request.headers["Authorization"] == f"Bearer {key}"
    payload = json.loads(request.content)
    assert payload["model"] == f"selected-{expected}"
    assert payload["temperature"] == 0.2
    assert payload["max_tokens"] == 123
    assert config.to_dict() == before


def test_configured_provider_explicit_options_do_not_mutate_config(offline_api_requests):
    config = Config(load_env=False)
    config.set("api.perplexity.api_key", "configured-key")
    config.set("api.perplexity.model", "configured-model")
    provider = APIClient.from_config(
        config, api_key="explicit-key", model="explicit-model", max_tokens=17
    )
    provider.get_response("Synthetic option override")
    (request,) = offline_api_requests
    assert request.headers["Authorization"] == "Bearer explicit-key"
    assert json.loads(request.content)["model"] == "explicit-model"
    assert json.loads(request.content)["max_tokens"] == 17
    assert config.get_api_key("perplexity") == "configured-key"
    assert config.get("api.perplexity.model") == "configured-model"


@pytest.mark.parametrize("provider", ["perplexity", "openrouter"])
def test_configured_provider_rejects_missing_or_empty_key(provider, offline_api_requests):
    config = Config(load_env=False)
    with pytest.raises(ValueError):
        APIClient.from_config(config, provider=provider)
    config.set(f"api.{provider}.api_key", "configured-key")
    with pytest.raises(ValueError):
        APIClient.from_config(config, provider=provider, api_key="")
    assert offline_api_requests == []


def test_configured_provider_rejects_conflicting_provider_option(offline_api_requests):
    config = Config(load_env=False)
    config.set("api.perplexity.api_key", "offline-key")
    config.set("api.perplexity.provider", "openrouter")
    with pytest.raises(ValueError):
        APIClient.from_config(config, provider="perplexity")
    assert offline_api_requests == []
