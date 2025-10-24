# Architecture Documentation

## System Overview

The Symposium package is designed with a modular architecture that separates concerns into distinct layers:

1. **Core Layer**: Fundamental functionality (API, configuration, data loading, logging)
2. **Analysis Layer**: Research analysis and profiling
3. **Generation Layer**: Content generation (profiles, projects)
4. **I/O Layer**: File reading and writing
5. **Visualization Layer**: Data visualization and reporting
6. **CLI Layer**: Command-line interfaces

## Module Dependencies

```
CLI Layer
   ↓
Generation/Analysis Layer
   ↓
Core Layer
   ↓
I/O Layer
```

## Core Components

### API Client (`core.api`)

Unified interface for multiple LLM providers:

```python
APIClient.create(provider="perplexity", api_key="...")
```

**Design Pattern**: Factory + Strategy
- `APIClient` is a factory that creates provider instances
- `BaseAPIProvider` defines the interface
- `PerplexityProvider` and `OpenRouterProvider` implement the interface

**Key Features**:
- Automatic retry with exponential backoff
- Token limit management
- Response validation
- Environment-based configuration

### Configuration Management (`core.config`)

Hierarchical configuration system:

1. Default values (hardcoded)
2. Configuration file (JSON)
3. Environment variables (highest priority)

**Access Pattern**: Dot notation
```python
config.get("api.perplexity.model")
```

### Data Loader (`core.data_loader`)

Handles various data formats with consistent error handling:
- CSV files (OpenAlex data)
- JSON files (profiles, metadata)
- Markdown files (templates, domain knowledge)

**Token Management**:
- Estimates token count
- Truncates data to fit limits
- Prioritizes recent/highly-cited works

## Analysis Pipeline

### Presenter Analysis

```
Load CSV Data → Generate Prompt → API Call → Save Reports
```

Components:
- `DataLoader.load_presenter_data()`: Loads OpenAlex CSV files
- `PresenterAnalyzer.generate_research_prompt()`: Creates analysis prompt
- `APIClient.get_response()`: Gets LLM analysis
- `ReportWriter.save_presenter_report()`: Saves MD + JSON

### Participant Analysis

```
Load Registration → Generate Prompt → API Call → Save Reports
```

Similar pipeline but with registration CSV as input.

## Generation Pipeline

### Profile Generation

```
Load Researcher Data → Generate Profile → Generate Methods → Save
```

Uses `PresenterAnalyzer` for profiles and `ProfileGenerator` for methods extraction.

### Project Generation

```
Load Profiles → Load Templates → Generate Proposals → Save
```

Components:
- Loads participant profiles
- Loads catechism templates
- Loads domain context
- Generates structured proposals

## Data Flow

```
Input Data
  ├── OpenAlex CSV (presenters)
  ├── Registration CSV (participants)
  ├── Catechism Templates
  └── Domain Knowledge
         ↓
    Processing
  ├── Data Loading & Validation
  ├── Prompt Generation
  ├── API Calls (with retry)
  └── Response Processing
         ↓
    Output
  ├── Markdown Reports
  ├── JSON Data
  └── Visualizations
```

## Error Handling Strategy

1. **Input Validation**: Check file existence, schema validation
2. **API Errors**: Retry with exponential backoff
3. **Token Limits**: Automatic truncation with logging
4. **Partial Failures**: Continue processing remaining items
5. **Logging**: Comprehensive logging at all levels

## Configuration Priority

```
Environment Variables (highest)
   ↓
Configuration File
   ↓
Default Values (lowest)
```

## Testing Strategy

### Unit Tests
- Mock external dependencies (API clients, file I/O)
- Test individual functions and methods
- Coverage target: >80%

### Integration Tests
- Test complete workflows
- Use temporary directories for I/O
- Mock API responses for consistency

### Fixtures (`conftest.py`)
- `temp_dir`: Temporary directory
- `mock_api_client`: Mock LLM client
- `sample_*_data`: Test data

## Extensibility Points

### Adding New API Providers

1. Create provider class inheriting from `BaseAPIProvider`
2. Implement `get_response()` method
3. Add to `APIClient.create()` factory
4. Update configuration defaults

### Adding New Analysis Types

1. Create analyzer class in `analysis/`
2. Implement analysis logic
3. Add CLI command in `cli/analyze.py`
4. Update documentation

### Adding New Generation Types

1. Create generator class in `generation/`
2. Implement generation logic  
3. Add CLI command in `cli/generate.py`
4. Update documentation

## Performance Considerations

### Token Management
- Truncate large datasets before API calls
- Prioritize recent/highly-cited works
- Estimate token counts before sending

### API Rate Limiting
- Exponential backoff on failures
- Configurable retry parameters
- Request delay between calls

### Data Processing
- Stream large CSV files
- Lazy loading where possible
- Efficient pandas operations

## Security Considerations

### API Keys
- Never commit API keys
- Use environment variables or `.env` file
- Redact keys when saving configuration

### Input Validation
- Validate file paths
- Check CSV schema
- Sanitize filenames

### Output Safety
- Create directories safely
- Handle file write errors
- Atomic writes where possible

## Future Enhancements

1. **Caching Layer**: Cache API responses to avoid redundant calls
2. **Async Processing**: Parallel processing of multiple items
3. **Database Support**: Optional database backend for structured data
4. **Web Interface**: Flask/FastAPI web UI for interactive use
5. **Real-time Updates**: Incremental updates for long-running symposiums

