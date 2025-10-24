# Core Module

Core functionality and infrastructure for the Symposium package.

## Overview

This module provides the fundamental building blocks for the entire Symposium ecosystem, including API clients, configuration management, data loading utilities, and logging infrastructure.

## Components

### APIClient
Unified API client for multiple LLM providers:
- **PerplexityProvider**: Perplexity AI API integration
- **OpenRouterProvider**: OpenRouter API integration with retry logic
- Automatic provider switching and fallback
- Token management and rate limiting

### Config
Hierarchical configuration management:
- Default configurations
- JSON file overrides
- Environment variable integration
- Secure API key management

### DataLoader
Data loading and processing utilities:
- CSV, JSON, and Markdown file loading
- Presenter data structure handling
- Token estimation and truncation
- Data validation and error handling

### LoggingUtils
Standardized logging setup:
- Configurable log levels
- File and console output
- Structured formatting
- Error tracking and debugging

## Usage

```python
from symposium.core import APIClient, Config, DataLoader, setup_logging

# Configuration
config = Config()
config.ensure_paths()

# API Client
client = APIClient.create(
    provider=config.get("api.provider"),
    api_key=config.get_api_key()
)

# Data Loading
loader = DataLoader()
presenters = loader.load_presenter_data(data_path, max_rows=10)

# Logging
setup_logging(level="INFO")
```

## API Integration

### Perplexity Provider
- Model: `sonar`
- Temperature: 0.7 (configurable)
- Max tokens: 2000 (configurable)
- Search-enhanced responses

### OpenRouter Provider
- Model: `anthropic/claude-3.5-sonnet`
- Temperature: 0.7 (configurable)
- Max tokens: 2000 (configurable)
- Exponential backoff retry logic

## Configuration Hierarchy

1. **Defaults**: Built-in sensible defaults
2. **JSON File**: Optional configuration overrides
3. **Environment Variables**: Runtime configuration
4. **Command Line**: User-specific settings

## Data Processing

### Token Management
- Automatic token estimation
- Configurable truncation
- Prompt optimization
- Context preservation

### Error Handling
- Graceful degradation
- Comprehensive logging
- User-friendly error messages
- Recovery mechanisms

## Integration

This module provides core services to:
- `symposium.analysis` - API clients for analysis
- `symposium.generation` - Configuration and data loading
- `symposium.cli` - Command-line configuration
- `symposium.visualization` - Data processing utilities
