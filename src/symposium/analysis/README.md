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

## Integration

This module integrates with:
- `symposium.core` - API clients and configuration
- `symposium.io` - File reading and writing
- `symposium.generation` - Profile and project generation
