"""Tests for configuration management."""

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

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

    @pytest.mark.parametrize("settings", [None, False, 0, "synthetic-secret", ["synthetic-secret"]])
    def test_get_api_config_rejects_non_object(self, tmp_path, settings):
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({"api": {"custom": settings}}), encoding="utf-8")
        config = Config(config_file=config_file, load_env=False)

        with pytest.raises(ValueError, match="api.custom") as error:
            config.get_api_config("custom")
        assert "synthetic-secret" not in str(error.value)

    def test_get_api_config_rejects_non_string_keys(self):
        config = Config(load_env=False)
        config.set("api.custom", {1: "synthetic-secret"})

        with pytest.raises(ValueError, match="api.custom") as error:
            config.get_api_config("custom")
        assert "synthetic-secret" not in str(error.value)

    def test_get_api_config_missing_provider(self):
        config = Config(load_env=False)
        assert config.get_api_config("custom") == {}

    def test_get_api_key(self):
        """Test getting API key."""
        config = Config(load_env=False)
        config.set("api.perplexity.api_key", "test_key")
        assert config.get_api_key("perplexity") == "test_key"

    @patch.dict(os.environ, {"PERPLEXITY_API_KEY": "env_perplexity_key"}, clear=False)
    def test_get_api_key_from_environment(self):
        """Test getting API key from environment variables."""
        config = Config(load_env=True)
        # Must read the exact key we injected, proving env vars are actually consumed.
        assert config.get_api_key("perplexity") == "env_perplexity_key"

    @pytest.mark.parametrize(
        "key", [False, 0, 17, [], ["synthetic-secret"], {"token": "synthetic-secret"}]
    )
    def test_get_api_key_rejects_non_string(self, tmp_path, monkeypatch, key):
        monkeypatch.chdir(tmp_path)
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({"api": {"custom": {"api_key": key}}}), encoding="utf-8")
        config = Config(config_file=config_file, load_env=False)

        with pytest.raises(ValueError, match="api.custom.api_key") as error:
            config.get_api_key("custom")
        assert "synthetic-secret" not in str(error.value)

    @pytest.mark.parametrize("provider", ["perplexity", "openrouter"])
    @pytest.mark.parametrize("empty_key", [None, ""])
    def test_get_api_key_preserves_precedence(self, tmp_path, monkeypatch, provider, empty_key):
        monkeypatch.chdir(tmp_path)
        env_name = f"{provider.upper()}_API_KEY"
        monkeypatch.setenv(env_name, "environment-key")
        (tmp_path / "llm_keys.key").write_text(
            json.dumps({provider: "legacy-key"}), encoding="utf-8"
        )
        config = Config(load_env=False)
        config.set(f"api.{provider}.api_key", "configured-key")
        assert config.get_api_key(provider) == "configured-key"

        config.set(f"api.{provider}.api_key", empty_key)
        assert config.get_api_key(provider) == "environment-key"
        monkeypatch.delenv(env_name)
        assert config.get_api_key(provider) is None

    @pytest.mark.parametrize(
        "keys",
        [
            ["synthetic-secret"],
            "synthetic-secret",
            None,
            {"legacy": False},
            {"legacy": 0},
            {"legacy": []},
            {"legacy": ["synthetic-secret"]},
            {"legacy": {"token": "synthetic-secret"}},
        ],
    )
    def test_legacy_api_key_rejects_malformed_values(self, tmp_path, monkeypatch, caplog, keys):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "llm_keys.key").write_text(json.dumps(keys), encoding="utf-8")
        config = Config(load_env=False)

        assert config.get_api_key("legacy") is None
        assert caplog.records
        assert "synthetic-secret" not in caplog.text

    @pytest.mark.parametrize(
        "keys,expected",
        [
            ({"legacy": "legacy-key"}, "legacy-key"),
            ({"legacy": ""}, ""),
            ({"legacy": None}, None),
            ({}, None),
        ],
    )
    def test_legacy_api_key_preserves_valid_values(
        self, tmp_path, monkeypatch, caplog, keys, expected
    ):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "llm_keys.key").write_text(json.dumps(keys), encoding="utf-8")
        config = Config(load_env=False)

        assert config.get_api_key("legacy") == expected
        assert not caplog.records

    def test_load_real_configuration(self):
        """Test loading default configuration without external side effects."""
        config = Config(load_env=False)

        # Test that configuration loads without errors
        provider = config.get("api.provider")
        assert provider in ["perplexity", "openrouter"]

        # Test path configuration resolves to real Path objects.
        # Do NOT mkdir here — unit tests must not mutate the project tree.
        data_dir = config.get_path("data_dir")
        assert isinstance(data_dir, Path)

        inputs_dir = config.get_path("inputs_dir")
        outputs_dir = config.get_path("outputs_dir")
        assert isinstance(inputs_dir, Path)
        assert isinstance(outputs_dir, Path)

    def test_get_path(self):
        """Test getting paths."""
        config = Config(load_env=False)
        data_dir = config.get_path("data_dir")
        assert isinstance(data_dir, Path)

    def test_load_from_file(self, tmp_path, monkeypatch):
        """Test loading configuration from JSON file."""
        config_file = tmp_path / "config.json"
        config_data = {"api": {"provider": "openrouter"}}
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        # Environment variables always take priority over file config.
        # Set it explicitly so the test is deterministic regardless of ambient env.
        monkeypatch.setenv("API_PROVIDER", "perplexity")
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

        with open(config_file, "r") as f:
            saved_data = json.load(f)

        assert saved_data["api"]["provider"] == "openrouter"

    def test_to_dict(self):
        """Test exporting configuration as dictionary."""
        config = Config(load_env=False)
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert "api" in config_dict
        assert "paths" in config_dict

    def test_set_creates_nested_keys(self):
        """set() with dot notation must create intermediate dicts."""
        config = Config(load_env=False)
        config.set("custom.section.value", 42)
        assert config.get("custom.section.value") == 42

    def test_get_path_missing_raises(self):
        """get_path raises ValueError for unconfigured path keys."""
        config = Config(load_env=False)
        with pytest.raises(ValueError):
            config.get_path("does_not_exist")

    def test_ensure_paths_creates_outputs(self, monkeypatch, tmp_path):
        """ensure_paths creates the configured output/data directories."""
        monkeypatch.setenv("SYMPOSIUM_OUTPUTS_DIR", str(tmp_path / "outputs"))
        monkeypatch.setenv("SYMPOSIUM_DATA_DIR", str(tmp_path / "data"))
        config = Config(load_env=True)
        config.ensure_paths()
        assert (tmp_path / "outputs").exists()
        assert (tmp_path / "data" / "inputs").exists()

    def test_save_redacts_api_key(self, tmp_path):
        """Saving config must redact API keys."""
        config = Config(load_env=False)
        config.set("api.perplexity.api_key", "super_secret_value")
        out = tmp_path / "config.json"
        config.save(out)
        saved = json.loads(out.read_text())
        assert saved["api"]["perplexity"]["api_key"] == "***REDACTED***"
