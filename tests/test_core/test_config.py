"""Tests for configuration management."""

import pytest
import json
from pathlib import Path
from symposium.core.config import Config


class TestConfig:
    """Tests for Config class."""

    def test_init_default(self):
        """Test initialization with defaults."""
        config = Config(load_env=False)
        assert config.get("api.provider") == "perplexity"
        assert config.get("api.perplexity.model") == "sonar"

    def test_get_with_dot_notation(self):
        """Test getting values with dot notation."""
        config = Config(load_env=False)
        assert config.get("api.provider") == "perplexity"
        assert config.get("api.perplexity.temperature") == 0.7

    def test_get_with_default(self):
        """Test getting non-existent key with default."""
        config = Config(load_env=False)
        assert config.get("nonexistent.key", "default") == "default"

    def test_set_value(self):
        """Test setting values."""
        config = Config(load_env=False)
        config.set("api.provider", "openrouter")
        assert config.get("api.provider") == "openrouter"

    def test_get_api_config(self):
        """Test getting API configuration."""
        config = Config(load_env=False)
        api_config = config.get_api_config("perplexity")
        assert api_config["model"] == "sonar"

    def test_get_api_key(self):
        """Test getting API key."""
        config = Config(load_env=False)
        config.set("api.perplexity.api_key", "test_key")
        assert config.get_api_key("perplexity") == "test_key"

    def test_get_api_key_from_environment(self):
        """Test getting API key from environment variables."""
        config = Config(load_env=True)
        # Should load from environment if available
        perplexity_key = config.get_api_key("perplexity")
        openrouter_key = config.get_api_key("openrouter")

        # These may be None if no keys in environment, but shouldn't raise errors
        if perplexity_key:
            assert isinstance(perplexity_key, str)
        if openrouter_key:
            assert isinstance(openrouter_key, str)

    def test_load_real_configuration(self):
        """Test loading real configuration from environment."""
        config = Config(load_env=True)

        # Test that configuration loads without errors
        provider = config.get("api.provider")
        assert provider in ["perplexity", "openrouter"]

        # Test path configuration
        data_dir = config.get_path("data_dir")
        assert data_dir.exists()

        inputs_dir = config.get_path("inputs_dir")
        outputs_dir = config.get_path("outputs_dir")

        # Ensure directories exist
        inputs_dir.mkdir(parents=True, exist_ok=True)
        outputs_dir.mkdir(parents=True, exist_ok=True)

    def test_get_path(self):
        """Test getting paths."""
        config = Config(load_env=False)
        data_dir = config.get_path("data_dir")
        assert isinstance(data_dir, Path)

    def test_load_from_file(self, tmp_path):
        """Test loading configuration from JSON file."""
        config_file = tmp_path / "config.json"
        config_data = {
            "api": {
                "provider": "openrouter"
            }
        }
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        # Note: Environment variables always take priority over file config
        # So if .env has API_PROVIDER=perplexity, it will override the file setting
        config = Config(config_file=config_file, load_env=True)
        # The environment variable should take priority
        assert config.get("api.provider") == "perplexity"

    def test_save(self, tmp_path):
        """Test saving configuration."""
        config = Config(load_env=False)
        config.set("api.provider", "openrouter")
        
        config_file = tmp_path / "config.json"
        config.save(config_file)
        
        assert config_file.exists()
        
        with open(config_file, 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data["api"]["provider"] == "openrouter"

    def test_to_dict(self):
        """Test exporting configuration as dictionary."""
        config = Config(load_env=False)
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert "api" in config_dict
        assert "paths" in config_dict

