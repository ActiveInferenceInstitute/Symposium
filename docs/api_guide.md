# API Guide

## Supported LLM Providers

### Perplexity

**Model**: `llama-3.1-sonar-large-128k-online`

**Features**:
- Online search capabilities
- 128k context window
- Recent, up-to-date information

**Configuration**:
```python
from symposium.core.api import APIClient

client = APIClient.create(
    provider="perplexity",
    api_key="your_key",
    model="llama-3.1-sonar-large-128k-online",
    temperature=0.7,
    max_tokens=2000
)
```

**Environment Setup**:
```bash
export PERPLEXITY_API_KEY=your_key_here
```

### OpenRouter

**Model**: `google/gemini-pro-1.5-exp`

**Features**:
- Access to multiple models
- Flexible pricing
- Fallback options

**Configuration**:
```python
client = APIClient.create(
    provider="openrouter",
    api_key="your_key",
    model="google/gemini-pro-1.5-exp",
    temperature=0.7,
    max_tokens=2000,
    max_retries=5,
    retry_delay=10
)
```

**Environment Setup**:
```bash
export OPENROUTER_API_KEY=your_key_here
```

## Configuration Options

### File-Based Configuration

Create `config.json`:

```json
{
  "api": {
    "provider": "perplexity",
    "perplexity": {
      "model": "llama-3.1-sonar-large-128k-online",
      "temperature": 0.7,
      "max_tokens": 2000
    },
    "openrouter": {
      "model": "google/gemini-pro-1.5-exp",
      "temperature": 0.7,
      "max_tokens": 2000,
      "max_retries": 5
    }
  },
  "data": {
    "max_rows_per_file": 10,
    "max_prompt_tokens": 12000
  }
}
```

Load configuration:

```python
from symposium.core.config import Config
from pathlib import Path

config = Config(config_file=Path("config.json"))
```

### Environment Variables

```bash
# API Configuration
export PERPLEXITY_API_KEY=your_key
export OPENROUTER_API_KEY=your_key
export API_PROVIDER=perplexity

# Path Configuration
export SYMPOSIUM_DATA_DIR=/path/to/data
export SYMPOSIUM_OUTPUTS_DIR=/path/to/outputs

# Logging
export LOG_LEVEL=INFO
```

## Rate Limiting and Retry Strategies

### Automatic Retry (OpenRouter)

OpenRouter provider includes automatic retry with exponential backoff:

```python
@backoff.on_exception(
    backoff.expo,
    Exception,
    max_tries=5,
    max_time=300,
    giveup=lambda e: not ('rate' in str(e).lower() or 'timeout' in str(e).lower())
)
```

**Parameters**:
- `max_tries`: 5 attempts (configurable)
- `max_time`: 300 seconds maximum total time
- Exponential backoff between retries

### Rate Limit Handling

**Best Practices**:
1. Add delay between requests
2. Monitor API usage
3. Handle rate limit errors gracefully
4. Use batch processing for large datasets

**Example**:
```python
import time

for item in items:
    result = api_client.get_response(prompt)
    time.sleep(2)  # 2-second delay between requests
```

## Token Management

### Token Estimation

```python
from symposium.core.data_loader import DataLoader

text = "Your long text here..."
tokens = DataLoader.estimate_token_count(text)
print(f"Estimated tokens: {tokens}")
```

**Formula**: `tokens ≈ words / 0.75`

### Token Limit Handling

```python
max_tokens = 12000
if DataLoader.estimate_token_count(prompt) > max_tokens:
    prompt = DataLoader.truncate_to_tokens(prompt, max_tokens)
```

### Best Practices

1. **Truncate Input Data**: Limit CSV rows before prompt generation
2. **Prioritize Content**: For papers, prioritize recent and highly-cited
3. **Check Before Sending**: Estimate tokens before API call
4. **Log Warnings**: Log when truncation occurs

## Error Handling

### API Errors

```python
try:
    response = api_client.get_response(prompt)
except ValueError as e:
    # Empty or invalid response
    logger.error(f"Invalid response: {e}")
except Exception as e:
    # Other errors (rate limits, network, etc.)
    logger.error(f"API error: {e}")
```

### Retry Logic

OpenRouter provider automatically retries on:
- Rate limit errors (429)
- Timeout errors
- Temporary network issues

Perplexity provider requires manual retry:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def get_response_with_retry(client, prompt):
    return client.get_response(prompt)
```

## Usage Examples

### Basic Analysis

```python
from symposium.core.api import APIClient
from symposium.core.config import Config
from symposium.analysis.presenters import PresenterAnalyzer
from pathlib import Path

# Setup
config = Config()
api_client = APIClient.create(
    provider=config.get("api.provider"),
    api_key=config.get_api_key()
)

# Analyze
analyzer = PresenterAnalyzer(api_client)
results = analyzer.analyze_all_presenters(
    data_path=Path("data/inputs/aif_2025"),
    output_dir=Path("outputs/profiles"),
    max_rows=10
)
```

### Custom Prompts

```python
custom_prompt = """
Analyze this researcher's work focusing on:
1. Novel methodologies
2. Interdisciplinary connections
3. Future research directions
"""

response = api_client.get_response(
    prompt=custom_prompt,
    system_prompt="You are an expert research analyst."
)
```

### Batch Processing

```python
import time

for presenter_name, presenter_data in presenters.items():
    try:
        analysis = analyzer.analyze_presenter(presenter_data)
        # Save results
        time.sleep(2)  # Rate limiting
    except Exception as e:
        logger.error(f"Error for {presenter_name}: {e}")
        continue
```

## API Cost Management

### Optimization Strategies

1. **Cache Results**: Save and reuse API responses
2. **Truncate Input**: Reduce token usage
3. **Batch Similar Requests**: Group related analyses
4. **Use Cheaper Models**: For less critical tasks

### Cost Estimation

**Perplexity Pricing** (example):
- ~$1 per 1M input tokens
- ~$1 per 1M output tokens

**Calculation**:
```python
input_tokens = DataLoader.estimate_token_count(prompt)
output_tokens = 2000  # max_tokens setting
cost_per_request = (input_tokens / 1_000_000) + (output_tokens / 1_000_000)
```

## Troubleshooting

### Common Issues

**Empty Response**:
```python
# Check API key
api_key = config.get_api_key()
assert api_key is not None, "API key not configured"

# Check model name
model = config.get("api.perplexity.model")
assert model, "Model not configured"
```

**Token Limit Exceeded**:
```python
# Enable truncation
if DataLoader.estimate_token_count(prompt) > 12000:
    logger.warning("Truncating prompt")
    prompt = DataLoader.truncate_to_tokens(prompt, 12000)
```

**Rate Limit Errors**:
```python
# Add retry logic
import time

max_retries = 3
for attempt in range(max_retries):
    try:
        response = api_client.get_response(prompt)
        break
    except Exception as e:
        if 'rate' in str(e).lower() and attempt < max_retries - 1:
            time.sleep(10 * (attempt + 1))
        else:
            raise
```

## API Provider Comparison

| Feature | Perplexity | OpenRouter |
|---------|------------|------------|
| Online Search | ✅ Yes | ❌ No |
| Multiple Models | ❌ Single | ✅ Multiple |
| Auto Retry | ❌ Manual | ✅ Built-in |
| Context Window | 128k | Varies |
| Best For | Research analysis | Flexible generation |

## Advanced Usage

### Custom Provider

```python
from symposium.core.api import BaseAPIProvider

class CustomProvider(BaseAPIProvider):
    def get_response(self, prompt, system_prompt=None, **kwargs):
        # Custom implementation
        response = self.custom_api_call(prompt)
        return response

# Register in APIClient.create()
```

### Streaming Responses

```python
# Note: Current implementation doesn't support streaming
# Future enhancement planned
```

### Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor

def process_presenter(presenter_data):
    return analyzer.analyze_presenter(presenter_data)

with ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(process_presenter, presenters.values())
```

