# Active Inference Symposium Research Tools

A comprehensive toolkit for analyzing and supporting the [4th Applied Active Inference Symposium](https://symposium.activeinference.institute/) through automated research analysis, personalized learning paths, and project proposal generation.

## Core Features

- **Research Analysis**: Automated analysis of presenter publications and research profiles
- **Profile Generation**: Comprehensive participant profiling based on registration data
- **Learning Paths**: Personalized Active Inference learning trajectories
- **Project Proposals**: Structured proposals using Heilmeier Catechism format

## System Architecture

### Analysis Pipeline
1. Research Presenters (`1_Research_Presenters.py`)
   - Analyzes OpenAlex publication data
   - Generates research profiles and impact metrics
   - Maps collaboration networks

2. Research Participants (`2_Research_Participants.py`) 
   - Processes registration data
   - Creates detailed participant profiles
   - Maps expertise and interests

3. Learning Programs (`3_Draft_Personalized_Program.py`)
   - Generates customized learning paths
   - Defines progression milestones
   - Recommends specific resources

4. Project Generation (`4_ActInf_Application.py`)
   - Creates targeted project proposals
   - Matches participants to opportunities
   - Defines implementation roadmaps

### Output Structure
```
outputs/
├── presenters/
│   └── {Presenter_Name}/
│       ├── research_profile.md
│       └── research_profile.json
└── participants/
    └── {Participant_Name}/
        ├── profile.md
        ├── profile.json
        ├── learning_plan.md
        ├── learning_plan.json
        ├── project_proposals.md
        └── project_proposals.json
```

## Setup & Usage

### Prerequisites
- Python 3.8+
- Perplexity API access
- OpenAlex data access
- Participant registration data

### Installation
```bash
# Clone repository
git clone https://github.com/yourusername/Perplexity.git
cd Perplexity

# Install dependencies
pip install -r requirements.txt

# Configure API key
echo '{"perplexity": "pplx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}' > llm_keys.key
```

### Execution
```bash
# Run full pipeline
python3 1_Research_Presenters.py
python3 2_Research_Participants.py
python3 3_Draft_Personalized_Program.py
python3 4_ActInf_Application.py

# Or run individual components as needed
```

## Research Directions

### Dark Symposium
- Edge case exploration in Active Inference
- Framework limitation testing
- Research gap identification
- Boundary condition investigation

### SymPlausium
- Cross-domain integration analysis
- Collaborative opportunity mapping
- Framework synthesis development
- Novel research direction discovery

## Integration Points

### Pre-Symposium
- Research synthesis
- Background analysis
- Learning path development
- Initial proposal generation

### During Symposium
- Real-time participant matching
- Resource recommendations
- Collaboration facilitation
- Project refinement

### Post-Symposium
- Path updates based on content
- Proposal refinement
- Network development
- Resource distribution

## Technical Infrastructure

### Error Handling
- Comprehensive logging system
- Exception management
- Progress tracking
- Status monitoring

### Future Development
- Interactive path updates
- Real-time matching system
- Resource recommendation engine
- Collaboration network analysis

## Community Resources

### External Links
- [Active Inference Institute](https://activeinference.institute/)
- [OpenAlex](https://openalex.org/)
- [Perplexity API](https://perplexity.ai/)
- [spaCy Models](https://spacy.io/models)

### Support
- [Submit Issues](https://github.com/ActiveInferenceInstitute/Perplexity/issues)
- [Contributing Guidelines](CONTRIBUTING.md)
- [License](LICENSE) - MIT
- Contact: [blanket@activeinference.institute](mailto:blanket@activeinference.institute)