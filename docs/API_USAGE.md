# API Usage Guide - Symposium 2025

## API Architecture

The Symposium package uses **two separate LLM providers** optimized for different tasks:

### Perplexity AI (Sonar Model)
- **Purpose**: Background research and internet-enabled searches
- **Model**: `sonar`
- **Use Cases**:
  - Participant background research
  - Academic profile searches
  - Publication lookups
  - Professional background verification
  - Research contribution analysis

### OpenRouter (Claude 3.5 Sonnet)
- **Purpose**: Analysis, synthesis, and curriculum generation
- **Model**: `anthropic/claude-3.5-sonnet`
- **Use Cases**:
  - Profile analysis
  - Personalized curriculum generation
  - Column summaries
  - Research synthesis

## Why Two Providers?

| Feature | Perplexity Sonar | OpenRouter Claude |
|---------|------------------|-------------------|
| **Internet Access** | ✅ Yes | ❌ No |
| **Search Quality** | ⭐⭐⭐⭐⭐ | N/A |
| **Reasoning** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Context Window** | ~28K tokens | ~200K tokens |
| **Best For** | Background research | Analysis & synthesis |
| **Speed** | Fast (web-enhanced) | Moderate |
| **Cost** | $5-10 per 1M tokens | $3-15 per 1M tokens |

## Configuration

### Environment Variables

```bash
# .env file
PERPLEXITY_API_KEY=your_perplexity_key
OPENROUTER_API_KEY=your_openrouter_key

# Optional: Override defaults
PERPLEXITY_MODEL=sonar
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
```

### API Settings

```python
# Default configuration in pyproject.toml
"api": {
    "perplexity": {
        "model": "sonar",
        "temperature": 0.7,
        "max_tokens": 2000
    },
    "openrouter": {
        "model": "anthropic/claude-3.5-sonnet",
        "temperature": 0.7,
        "max_tokens": 2000,
        "max_retries": 5
    }
}
```

## API Usage by Feature

### Complete Analysis (Option 2)

When running complete participant analysis:

1. **Profile Analysis** → OpenRouter Claude
   - Input: Participant survey responses
   - Output: Comprehensive profile analysis
   - Rationale: Deep reasoning about research interests

2. **Background Research** → Perplexity Sonar
   - Input: Name, affiliation, ORCID
   - Output: Academic background from web searches
   - Rationale: Needs internet access for publication lookups

3. **Personalized Curriculum** → OpenRouter Claude
   - Input: Profile + learning needs
   - Output: Tailored learning path
   - Rationale: Complex synthesis and planning

### Single Participant Operations

**Option 4: Background Research**
```python
# Always uses Perplexity Sonar
client = APIClient.create('perplexity')
```

**Option 5: Personalized Curriculum**
```python
# Always uses OpenRouter Claude
client = APIClient.create('openrouter')
```

**Option 3: Column Summaries**
```python
# Uses OpenRouter Claude
client = APIClient.create('openrouter')
```

## API Call Flow

### Complete Analysis Example

```
User selects: Complete Analysis (Option 2, Choice 4)
↓
Load 47 participants from CSV
↓
For each participant:
  ├─ [OpenRouter] Generate profile analysis
  ├─ [Perplexity] Research academic background  ← Uses internet
  └─ [OpenRouter] Create personalized curriculum
↓
Save all reports to outputs/2025_symposium/
```

### Logging Output

```
INFO - Creating Perplexity API client (Sonar model) for background research
INFO - Creating OpenRouter API client (Claude) for analysis and curricula
INFO - 🔍 Using Perplexity Sonar for background research: Alexander Sabine
INFO - ✅ Background research completed for Alexander Sabine
INFO - 🤖 Using OpenRouter Claude for curriculum: Alexander Sabine
INFO - ✅ Curriculum completed for Alexander Sabine
```

## API Performance

### Response Times (Typical)

| Operation | Provider | Avg Time | Tokens Used |
|-----------|----------|----------|-------------|
| Background Research | Perplexity | 5-10s | 800-1200 |
| Profile Analysis | OpenRouter | 10-15s | 1500-2000 |
| Curriculum | OpenRouter | 15-20s | 2000-3000 |

### Cost Estimates (47 participants)

**Complete Analysis:**
- Perplexity: ~47 × 1000 tokens = 47K tokens = ~$0.25
- OpenRouter: ~47 × 4000 tokens = 188K tokens = ~$0.60
- **Total: ~$0.85** per complete run

**Profile Only:**
- OpenRouter: ~47 × 1500 tokens = 70.5K tokens = ~$0.25

**Background Only:**
- Perplexity: ~47 × 1000 tokens = 47K tokens = ~$0.25

## Rate Limiting & Retry Logic

### Perplexity
- **Rate Limit**: 60 requests/minute (free), 600/minute (paid)
- **Retry Logic**: Exponential backoff with max 5 retries
- **Timeout**: 60 seconds per request

### OpenRouter
- **Rate Limit**: Varies by model (Claude: 60 req/min)
- **Retry Logic**: Exponential backoff with max 5 retries
- **Timeout**: 120 seconds per request

### Implementation

```python
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
def _get_response_with_retry(self, prompt, system_prompt, **kwargs):
    # Automatically retries on rate limit or timeout
    pass
```

## Error Handling

### Common Issues

**1. API Key Not Set**
```
❌ Perplexity API key required for background research
   Set PERPLEXITY_API_KEY in .env file
```

**2. Rate Limit Exceeded**
```
INFO - Retry attempt 1/5 after rate limit
INFO - Backing off 2 seconds
```

**3. Network Timeout**
```
ERROR - Request timeout after 60s
INFO - Retrying with exponential backoff
```

### Graceful Degradation

If one API fails:
- Skip that feature for the participant
- Log the error
- Continue with remaining participants
- Report partial results

## Testing APIs

### Test Connectivity (Option 7, then 1)

```python
def test_api_connectivity(self):
    """Test both Perplexity and OpenRouter."""
    for provider in ['perplexity', 'openrouter']:
        try:
            client = APIClient.create(provider)
            response = client.get_response(
                "Respond with 'test successful' if you receive this.",
                "You are a helpful assistant."
            )
            if 'test successful' in response.lower():
                print(f"✅ {provider} API: Connected successfully")
        except Exception as e:
            print(f"❌ {provider} API: {e}")
```

### Manual API Test

```bash
# Test Perplexity
curl -X POST https://api.perplexity.ai/chat/completions \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "sonar", "messages": [{"role": "user", "content": "test"}]}'

# Test OpenRouter
curl -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "anthropic/claude-3.5-sonnet", "messages": [{"role": "user", "content": "test"}]}'
```

## Best Practices

### 1. Use Appropriate Provider

✅ **Do:**
- Use Perplexity for anything needing web search
- Use OpenRouter for deep analysis and synthesis
- Check which provider is needed before starting

❌ **Don't:**
- Use OpenRouter for background research (no internet)
- Use Perplexity for complex reasoning (limited context)

### 2. Monitor Costs

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Track API calls
INFO - HTTP Request: POST https://api.perplexity.ai/...
INFO - HTTP Request: POST https://openrouter.ai/...
```

### 3. Handle Errors Gracefully

```python
try:
    results = analyzer.analyze_all_participants(
        csv_path,
        output_dir,
        include_background_research=True,
        perplexity_client=perplexity_client
    )
except Exception as e:
    logger.error(f"Analysis failed: {e}")
    # Continue with partial results
```

### 4. Batch Processing

For 47 participants:
- Process in serial (one at a time)
- Save after each participant
- Resume on failure
- Monitor progress logs

## Advanced Configuration

### Custom Models

```python
# Use different Perplexity model
client = APIClient.create('perplexity', model='sonar-medium')

# Use different OpenRouter model
client = APIClient.create('openrouter', model='anthropic/claude-3-opus')
```

### Adjust Temperature

```python
# More creative (higher temperature)
client = APIClient.create('openrouter', temperature=0.9)

# More deterministic (lower temperature)
client = APIClient.create('perplexity', temperature=0.3)
```

### Increase Token Limits

```python
# For longer outputs
client = APIClient.create('openrouter', max_tokens=4000)
```

## Troubleshooting

### Issue: Background Research Not Using Perplexity

**Symptom:**
```
httpx - INFO - HTTP Request: POST https://openrouter.ai/...
```

**Solution:**
```python
# Ensure perplexity_client is passed
results = analyzer.analyze_all_participants(
    csv_path,
    output_dir,
    include_background_research=True,
    perplexity_client=perplexity_client  # ← Must pass this
)
```

### Issue: Import Errors

**Symptom:**
```
❌ Module import failed: No module named 'backoff'
```

**Solution:**
```bash
./symposium.sh  # Uses UV to ensure all deps installed
# OR
uv pip install -e .
```

### Issue: Slow Responses

**Symptom:**
- Taking > 30 seconds per request

**Solutions:**
1. Check network connection
2. Reduce max_tokens
3. Use simpler prompts
4. Check API status pages

## API Documentation Links

- **Perplexity**: https://docs.perplexity.ai/
- **OpenRouter**: https://openrouter.ai/docs
- **Claude Models**: https://docs.anthropic.com/claude/docs

## Support

For API-related issues:
1. Check logs in `symposium.log`
2. Verify API keys in `.env`
3. Test connectivity (Option 7)
4. Check provider status pages
5. Review cost limits on provider dashboards

---

**Quick Reference:**

| Task | Provider | Model | Internet | Tokens |
|------|----------|-------|----------|--------|
| Background Research | Perplexity | sonar | ✅ Yes | 1000 |
| Profile Analysis | OpenRouter | Claude-3.5 | ❌ No | 1500 |
| Curriculum | OpenRouter | Claude-3.5 | ❌ No | 2500 |
| Column Summaries | OpenRouter | Claude-3.5 | ❌ No | 2000 |

