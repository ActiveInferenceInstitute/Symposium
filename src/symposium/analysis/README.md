# Analysis Module

Research analysis and profiling functionality for the Symposium package.

## Overview

This module provides comprehensive analysis capabilities for researchers, presenters, and participants in the Active Inference Symposium ecosystem.

## Components

### PresenterAnalyzer
Analyzes presenter research profiles using academic data:
- Research focus and expertise identification
- Impact and influence assessment
- Research evolution tracking
- Key contributions analysis
- Future directions prediction

### ParticipantAnalyzer
Analyzes participant profiles for educational and research purposes:
- Expertise assessment
- Learning opportunities identification
- Research interests mapping
- Collaboration potential evaluation
- Development roadmap creation

## Usage

```python
from symposium.analysis import PresenterAnalyzer, ParticipantAnalyzer

# Analyze presenter
analyzer = PresenterAnalyzer(api_client, config)
results = analyzer.analyze_all_presenters(data_path, output_dir)

# Analyze participants
analyzer = ParticipantAnalyzer(api_client, config)
results = analyzer.analyze_all_participants(registration_file, output_dir)
```

## Data Requirements

### Presenter Data
- OpenAlex CSV files with research topics and publications
- Structured in folders by presenter name
- Works data with citations and publication years

### Participant Data
- Registration CSV with background, interests, experience
- Domain context files for specialized analysis
- Optional collaborator information

## Output

Analysis results are saved as both Markdown and JSON files:
- Structured research profiles
- Method documentation
- Collaboration recommendations
- Development roadmaps

## Error Handling

### Payment Errors
When a `PaymentRequiredError` is raised (402 payment required):
- Processing stops immediately
- Clear error message displayed with provider information
- Partial results saved for completed participants
- User guidance provided for adding credits

### Other Errors
For non-payment errors:
- Individual participant errors are logged
- Processing continues with remaining participants
- Partial results are reported
- Graceful degradation maintains system stability

## Integration

This module integrates with:
- `symposium.core` - API clients and configuration (including PaymentRequiredError)
- `symposium.io` - File reading and writing
- `symposium.generation` - Profile and project generation
