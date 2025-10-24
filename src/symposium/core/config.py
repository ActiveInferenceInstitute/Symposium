"""Configuration management for symposium package."""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for symposium package."""

    def __init__(self, config_file: Optional[Path] = None, load_env: bool = True):
        """Initialize configuration.
        
        Args:
            config_file: Path to optional JSON config file
            load_env: Whether to load .env file (default: True)
        """
        if load_env:
            load_dotenv()

        self._config: Dict[str, Any] = {}
        self._load_defaults()

        if config_file and config_file.exists():
            self._load_from_file(config_file)

        self._load_from_environment()

    def _load_defaults(self):
        """Load default configuration values."""
        self._config = {
            # API Configuration
            "api": {
                "provider": "perplexity",  # or "openrouter"
                "perplexity": {
                    "model": "sonar",
                    "temperature": 0.7,
                    "max_tokens": 2000,
                },
                "openrouter": {
                    "model": "anthropic/claude-3.5-sonnet",
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "max_retries": 5,
                    "retry_delay": 10,
                },
            },
            # Path Configuration
            "paths": {
                "base_dir": Path.cwd(),
                "data_dir": Path.cwd() / "data",
                "inputs_dir": Path.cwd() / "data" / "inputs",
                "outputs_dir": Path.cwd() / "outputs",
                "catechisms_dir": Path.cwd() / "data" / "catechisms",
                "domains_dir": Path.cwd() / "data" / "domains",
                "prompts_dir": Path.cwd() / "data" / "prompts",
            },
            # Data Processing Configuration
            "data": {
                "max_rows_per_file": 10,
                "max_prompt_tokens": 12000,
                "truncate_long_prompts": True,
            },
            # Logging Configuration
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        }

    def _load_from_file(self, config_file: Path):
        """Load configuration from JSON file.
        
        Args:
            config_file: Path to JSON configuration file
        """
        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)
            self._deep_update(self._config, file_config)
            logger.info(f"Loaded configuration from {config_file}")
        except Exception as e:
            logger.warning(f"Could not load config file {config_file}: {e}")

    def _load_from_environment(self):
        """Load configuration from environment variables."""
        # API Keys
        if os.getenv("PERPLEXITY_API_KEY"):
            self._config["api"]["perplexity"]["api_key"] = os.getenv("PERPLEXITY_API_KEY")
        
        if os.getenv("OPENROUTER_API_KEY"):
            self._config["api"]["openrouter"]["api_key"] = os.getenv("OPENROUTER_API_KEY")

        # API Provider selection
        if os.getenv("API_PROVIDER"):
            self._config["api"]["provider"] = os.getenv("API_PROVIDER")

        # Paths
        if os.getenv("SYMPOSIUM_DATA_DIR"):
            data_dir = Path(os.getenv("SYMPOSIUM_DATA_DIR"))
            self._config["paths"]["data_dir"] = data_dir
            self._config["paths"]["inputs_dir"] = data_dir / "inputs"
            self._config["paths"]["catechisms_dir"] = data_dir / "catechisms"
            self._config["paths"]["domains_dir"] = data_dir / "domains"
            self._config["paths"]["prompts_dir"] = data_dir / "prompts"

        if os.getenv("SYMPOSIUM_OUTPUTS_DIR"):
            self._config["paths"]["outputs_dir"] = Path(os.getenv("SYMPOSIUM_OUTPUTS_DIR"))

        # Logging level
        if os.getenv("LOG_LEVEL"):
            self._config["logging"]["level"] = os.getenv("LOG_LEVEL")

    def _deep_update(self, base: Dict, update: Dict):
        """Deep update dictionary (nested merge).
        
        Args:
            base: Base dictionary to update
            update: Update dictionary with new values
        """
        for key, value in update.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'api.provider')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value

    def set(self, key: str, value: Any):
        """Set configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'api.provider')
            value: Value to set
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value

    def get_api_config(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """Get API configuration for a provider.
        
        Args:
            provider: Provider name (if None, uses default provider)
            
        Returns:
            API configuration dictionary
        """
        if provider is None:
            provider = self.get("api.provider")
        
        return self.get(f"api.{provider}", {})

    def get_api_key(self, provider: Optional[str] = None) -> Optional[str]:
        """Get API key for a provider.
        
        Args:
            provider: Provider name (if None, uses default provider)
            
        Returns:
            API key or None if not found
        """
        if provider is None:
            provider = self.get("api.provider")
        
        # Try config first, then environment, then legacy key file
        api_key = self.get(f"api.{provider}.api_key")
        
        if api_key:
            return api_key
        
        # Try environment variable
        if provider == "perplexity":
            return os.getenv("PERPLEXITY_API_KEY")
        elif provider == "openrouter":
            return os.getenv("OPENROUTER_API_KEY")
        
        # Try legacy llm_keys.key file
        return self._load_legacy_api_key(provider)

    def _load_legacy_api_key(self, provider: str) -> Optional[str]:
        """Load API key from legacy llm_keys.key file.
        
        Args:
            provider: Provider name
            
        Returns:
            API key or None if not found
        """
        key_file = Path("llm_keys.key")
        if key_file.exists():
            try:
                with open(key_file, 'r') as f:
                    keys = json.load(f)
                return keys.get(provider)
            except Exception as e:
                logger.warning(f"Could not load legacy key file: {e}")
        return None

    def get_path(self, path_key: str) -> Path:
        """Get configured path.
        
        Args:
            path_key: Path key (e.g., 'data_dir', 'outputs_dir')
            
        Returns:
            Path object
        """
        path = self.get(f"paths.{path_key}")
        if path is None:
            raise ValueError(f"Path '{path_key}' not configured")
        return Path(path)

    def ensure_paths(self):
        """Ensure all configured paths exist."""
        for key in ["outputs_dir", "data_dir", "inputs_dir"]:
            path = self.get_path(key)
            path.mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary.
        
        Returns:
            Configuration dictionary
        """
        return self._config.copy()

    def save(self, filepath: Path):
        """Save configuration to JSON file.
        
        Args:
            filepath: Path to save configuration
        """
        # Remove sensitive data before saving
        config_to_save = self.to_dict()
        if "api" in config_to_save:
            for provider in ["perplexity", "openrouter"]:
                if provider in config_to_save["api"] and "api_key" in config_to_save["api"][provider]:
                    config_to_save["api"][provider]["api_key"] = "***REDACTED***"

        with open(filepath, 'w') as f:
            json.dump(config_to_save, f, indent=2, default=str)

        logger.info(f"Saved configuration to {filepath}")

