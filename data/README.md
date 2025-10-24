# Data Directory Structure

This directory contains the organized data for the Symposium package.

## Structure

```
data/
├── inputs/           # Input data for analysis
│   ├── aif_2024/    # Historical AIF symposium data
│   └── aif_2025/    # Current AIF symposium data
├── catechisms/      # Catechism templates for proposals
├── domains/         # Domain knowledge bases
└── prompts/         # System prompts
```

## Configuration

The package uses a hierarchical configuration system:

1. **Environment Variables** (highest priority)
   ```bash
   PERPLEXITY_API_KEY=your_key
   OPENROUTER_API_KEY=your_key
   API_PROVIDER=perplexity
   ```

2. **Configuration File** (`config.json`)
   ```json
   {
     "api": {
       "provider": "perplexity",
       "perplexity": {
         "model": "llama-3.1-sonar-large-128k-online",
         "temperature": 0.7
       }
     }
   }
   ```

3. **Default Values** (lowest priority)

## Data Management

### Adding New Data

To add data for a new symposium year:

```bash
# Create presenter data structure
mkdir -p data/inputs/aif_2025/PresenterName/
# Add CSV files: openalex-group-by-*.csv and works-*.csv

# Create participant registration
cp data/participants_2024.csv data/participants_2025.csv
# Edit the new CSV file with current participant information

# Add domain context
echo "# Active Inference 2025 Context" > data/domains/aif_2025.md
# Add relevant domain knowledge and context
```

### Data Validation

All data should follow these standards:

- **CSV Files**: UTF-8 encoding, proper headers, no missing values
- **Markdown Files**: Clean formatting, consistent structure
- **JSON Files**: Valid JSON syntax, consistent schema
- **Directory Structure**: Consistent naming, organized hierarchy

## Setup

1. Copy `.env.example` to `.env`
2. Add your API keys to `.env`
3. Optionally create `config.json` for custom settings
4. Run `symposium analyze --help` to test

