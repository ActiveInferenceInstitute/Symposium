# Core Agents

Infrastructure and API agents that power the Active Inference Institute Symposium package ecosystem.

## API Gateway Agent

**Role**: Unified API interface manager for multiple LLM providers.

**Capabilities**:
- Multi-provider API management
- Automatic provider switching
- Token counting and optimization
- Rate limiting and retry logic
- Error handling and recovery

**System Integration**:
- Perplexity AI API integration
- OpenRouter API integration
- Environment variable configuration
- Secure API key management

**Configuration**:
```
Provider: perplexity | openrouter
Model: sonar | anthropic/claude-3.5-sonnet
Temperature: 0.7 (configurable)
Max Tokens: 2000 (configurable)
```

**Input Processing**:
- Prompt token estimation
- Context length optimization
- Provider-specific formatting
- Metadata preservation

**Output Management**:
- Response validation
- Error recovery
- Rate limit handling
- Retry mechanisms
- Payment error detection (402 errors)

**Error Handling**:
- **PaymentRequiredError**: Detects 402 payment required errors immediately
- No retries on payment errors - processing stops with clear user guidance
- Graceful degradation for other errors (rate limits, timeouts)
- Provider-specific error messages with credit addition links

## Configuration Manager Agent

**Role**: Hierarchical configuration management and validation.

**Capabilities**:
- Multi-level configuration hierarchy
- Environment variable integration
- JSON configuration file handling
- Path management and validation
- Secure credential management

**Configuration Hierarchy**:
1. **Built-in Defaults**: Sensible default values
2. **JSON Override**: User configuration files
3. **Environment Variables**: Runtime settings
4. **Command Line**: User-specific parameters

**Security Features**:
- API key encryption in saved configs
- Environment variable precedence
- Secure credential loading
- Configuration validation

**Path Management**:
- Dynamic path resolution
- Directory creation
- Cross-platform compatibility
- Validation and error handling

## Data Processing Agent

**Role**: Data loading, validation, and preprocessing specialist.

**Capabilities**:
- Multi-format data loading (CSV, JSON, Markdown)
- Data structure validation
- Token estimation and counting
- Content truncation and optimization
- Error recovery and logging

**Data Formats**:
- **CSV**: Tabular data with pandas integration
- **JSON**: Structured configuration and metadata
- **Markdown**: Text content and documentation
- **Research Data**: OpenAlex CSV formats

**Processing Features**:
- Token-aware truncation
- Content validation
- Error handling
- Progress logging
- Memory optimization

**Quality Assurance**:
- Data integrity validation
- Format consistency checks
- Token limit compliance
- Error recovery mechanisms

## Logging Infrastructure Agent

**Role**: Centralized logging and monitoring system.

**Capabilities**:
- Multi-level logging configuration
- File and console output management
- Structured log formatting
- Error tracking and debugging
- Performance monitoring

**Log Levels**:
- **DEBUG**: Detailed debugging information
- **INFO**: General operational messages
- **WARNING**: Warning conditions
- **ERROR**: Error conditions requiring attention
- **CRITICAL**: Critical system errors

**Output Channels**:
- Console output with timestamps
- File logging with rotation
- Structured formatting
- Error aggregation
- Performance metrics

## Integration Agents

### Token Management Agent
**Role**: Intelligent token counting and optimization.

**Capabilities**:
- Accurate token estimation
- Context length calculation
- Prompt truncation strategies
- Provider-specific limits
- Memory optimization

### Error Recovery Agent
**Role**: Robust error handling and recovery mechanisms.

**Capabilities**:
- Graceful error handling
- Retry logic implementation
- Fallback mechanism activation
- User-friendly error reporting
- System stability maintenance
- Payment error detection and handling

**Payment Error Handling**:
- Detects 402 payment required errors immediately
- Raises PaymentRequiredError with provider and message
- Stops processing with clear user guidance
- Preserves partial results for completed work
- Provides provider-specific credit addition links

### Path Resolution Agent
**Role**: Cross-platform path management and validation.

**Capabilities**:
- Dynamic path resolution
- Directory validation
- Cross-platform compatibility
- Automatic path creation
- Security validation

## Quality Metrics

- API response success rate
- Configuration loading accuracy
- Data processing integrity
- Token optimization efficiency
- Error recovery success
- Path management reliability

## Performance Standards

- **Response Time**: < 2 seconds average
- **Error Rate**: < 1% of operations
- **Token Efficiency**: > 95% context utilization
- **Configuration Accuracy**: 100% load success
- **Data Integrity**: 100% validation pass
