"""Unified API client for LLM providers (Perplexity and OpenRouter)."""

import os
import time
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import backoff
from openai import OpenAI
from openai import APIStatusError

logger = logging.getLogger(__name__)


class PaymentRequiredError(Exception):
    """Exception raised when API requires payment (402 error)."""
    
    def __init__(self, message: str, provider: str = "unknown"):
        """Initialize payment required error.
        
        Args:
            message: Error message from API
            provider: API provider name
        """
        self.provider = provider
        self.message = message
        super().__init__(f"{provider.upper()} API: {message}")


class BaseAPIProvider(ABC):
    """Abstract base class for API providers."""

    def __init__(self, api_key: str, **kwargs):
        """Initialize the API provider.
        
        Args:
            api_key: API key for the provider
            **kwargs: Additional configuration options
        """
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    def get_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Get a response from the API.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            **kwargs: Additional parameters
            
        Returns:
            Response text from the API
        """
        pass


class PerplexityProvider(BaseAPIProvider):
    """Perplexity API provider."""

    def __init__(self, api_key: str, **kwargs):
        """Initialize Perplexity provider.
        
        Args:
            api_key: Perplexity API key
            **kwargs: Additional configuration (model, temperature, max_tokens, etc.)
        """
        super().__init__(api_key, **kwargs)
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.perplexity.ai"
        )
        self.model = kwargs.get("model", "sonar")
        self.temperature = kwargs.get("temperature", 0.7)
        self.max_tokens = kwargs.get("max_tokens", 2000)

    def get_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Get response from Perplexity API.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            **kwargs: Override default parameters (model, temperature, max_tokens)
            
        Returns:
            Response text from Perplexity
            
        Raises:
            ValueError: If API returns empty response
            Exception: For other API errors
        """
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=kwargs.get("model", self.model),
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                messages=messages
            )

            if not response or not response.choices:
                raise ValueError("Empty response from Perplexity API")

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error getting Perplexity response: {e}")
            raise


class OpenRouterProvider(BaseAPIProvider):
    """OpenRouter API provider with retry logic."""

    def __init__(self, api_key: str, **kwargs):
        """Initialize OpenRouter provider.
        
        Args:
            api_key: OpenRouter API key
            **kwargs: Additional configuration (model, temperature, max_tokens, etc.)
        """
        super().__init__(api_key, **kwargs)
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.model = kwargs.get("model", "anthropic/claude-3.5-sonnet")
        self.temperature = kwargs.get("temperature", 0.7)
        self.max_tokens = kwargs.get("max_tokens", 2000)
        self.max_retries = kwargs.get("max_retries", 5)
        self.retry_delay = kwargs.get("retry_delay", 10)

    @backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=5,
        max_time=300,
        giveup=lambda e: not (
            isinstance(e, Exception) and
            ('rate' in str(e).lower() or 'timeout' in str(e).lower())
        ),
    )
    def _get_response_with_retry(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Get response with exponential backoff retry logic.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            **kwargs: Override default parameters
            
        Returns:
            Response text from OpenRouter
            
        Raises:
            PaymentRequiredError: If API returns 402 payment required error
            ValueError: If API returns empty response
        """
        # Combine system prompt with user prompt for OpenRouter
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        try:
            response = self.client.chat.completions.create(
                model=kwargs.get("model", self.model),
                messages=[{"role": "user", "content": full_prompt}]
            )
        except APIStatusError as e:
            # Check for 402 payment required error
            if hasattr(e, 'status_code') and e.status_code == 402:
                error_message = str(e)
                if hasattr(e, 'response') and e.response:
                    try:
                        error_data = e.response.json()
                        if 'error' in error_data and 'message' in error_data['error']:
                            error_message = error_data['error']['message']
                    except (ValueError, AttributeError):
                        pass
                raise PaymentRequiredError(error_message, provider="openrouter") from e
            # Re-raise other APIStatusErrors
            raise

        if response and response.choices and response.choices[0].message.content:
            return response.choices[0].message.content

        raise ValueError("Empty or invalid response received from OpenRouter")

    def get_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Get response from OpenRouter API with retry logic.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            **kwargs: Override default parameters
            
        Returns:
            Response text from OpenRouter
            
        Raises:
            PaymentRequiredError: If API returns 402 payment required error (no retries)
            Exception: If all retry attempts fail
        """
        try:
            return self._get_response_with_retry(prompt, system_prompt, **kwargs)
        except PaymentRequiredError:
            # Don't log payment errors as generic errors, re-raise immediately
            raise
        except Exception as e:
            logger.error(f"Error getting OpenRouter response after retries: {e}")
            raise


class APIClient:
    """Factory class for creating API provider instances."""

    @staticmethod
    def create(provider: str, api_key: Optional[str] = None, **kwargs) -> BaseAPIProvider:
        """Create an API provider instance.
        
        Args:
            provider: Provider name ('perplexity' or 'openrouter')
            api_key: API key (if None, will try to load from environment)
            **kwargs: Additional configuration options
            
        Returns:
            Initialized API provider instance
            
        Raises:
            ValueError: If provider is not supported or API key is missing
        """
        provider = provider.lower()

        # Try to load API key from environment if not provided
        if api_key is None:
            if provider == "perplexity":
                api_key = os.getenv("PERPLEXITY_API_KEY")
            elif provider == "openrouter":
                api_key = os.getenv("OPENROUTER_API_KEY")

            if api_key is None:
                raise ValueError(f"API key for {provider} not provided and not found in environment")

        if provider == "perplexity":
            return PerplexityProvider(api_key, **kwargs)
        elif provider == "openrouter":
            return OpenRouterProvider(api_key, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}. Choose 'perplexity' or 'openrouter'")

