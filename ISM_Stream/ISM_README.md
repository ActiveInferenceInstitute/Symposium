# Intelligent Soft Matter Workshop Research Tools

## ⚠️ Epistemic Disclaimer

This research toolkit and its outputs are provided for educational and research purposes only. Please note:

- All analyses, recommendations, and insights should be considered tentative and preliminary
- Generated content requires expert review and validation before practical application
- Outputs are meant to stimulate discussion and learning, not to replace expert judgment
- Research profiles and proposals are computational interpretations that may contain inaccuracies
- Citations and references should be independently verified
- The system's understanding of domains and relationships is inherently limited
- All generated content should be treated as suggestions for further investigation
- Users are encouraged to critically evaluate and improve upon these outputs
- This is an experimental research tool, not a definitive authority
- The primary value lies in generating hypotheses and connections for human researchers to explore

## Core Features

- **Research Analysis**: Automated analysis of presenter and participant research profiles
- **Domain Integration**: FieldSHIFT analysis for domain knowledge transfer
- **Project Generation**: Structured project proposals using multiple Catechism formats
- **Collaboration Matching**: Pairwise participant collaboration proposals
- **Evidence-Based Reports**: In-line citations and comprehensive documentation

## System Architecture

### Analysis Pipeline

1. Research Presenters (`1_Research_ISM_Presenters.py`)
   - Processes OpenAlex publication data from CSV files
   - Analyzes research focus and impact
   - Generates comprehensive research profiles
   - Handles token limits for large datasets
   - Prioritizes recent and highly-cited works

2. Research Participants (`2_Research_ISM_Participants.py`)
   - Analyzes participant research backgrounds
   - Maps expertise and technical capabilities
   - Identifies learning opportunities
   - Assesses collaboration potential
   - Creates detailed development roadmaps

3. Domain FieldSHIFT (`3_ISM_Participant_FieldSHIFT.py`)
   - Analyzes bi-directional knowledge exchange
   - Maps learning opportunities FROM domains
   - Identifies contribution potential TO domains
   - Creates implementation roadmaps
   - Addresses challenges and mitigations

4. Shifted Catechisms (`4_ISM_Shifted_Catechisms.py`)
   - Generates domain-specific project proposals
   - Uses Synthetic Catechism format
   - Leverages FieldSHIFT analyses
   - Creates actionable project plans
   - Focuses on domain contributions

5. Collaborative Catechisms (`5_ISM_Collab_Catechisms.py`)
   - Generates pairwise collaboration proposals
   - Uses KarmaGAP Catechism format
   - Includes in-line citations and evidence
   - Identifies unique synergies
   - Creates comprehensive project plans

### Output Structure
```
outputs/
├── presenters/
│   └── {Presenter_Name}/
│       ├── research_profile.md
│       └── research_profile.json
├── participants/
│   └── {Participant_Name}/
│       ├── profile.md
│       ├── profile.json
│       ├── fieldshift/
│       │   ├── {Name}_{Domain}_fieldshift.md
│       │   └── {Name}_{Domain}_fieldshift.json
│       └── catechisms/
│           ├── {Name}_{Domain}_catechism.md
│           └── {Name}_{Domain}_catechism.json
└── collaborative_proposals/
    ├── {Name1}_x_{Name2}_proposal.md
    └── {Name1}_x_{Name2}_proposal.json
```

## Setup & Usage

### Prerequisites
- Python 3.8+
- Perplexity API access
- OpenAlex data access
- Domain knowledge bases
- Catechism templates

### Installation
```bash
# Clone repository
git clone https://github.com/ActiveInferenceInstitute/Symposium.git
cd Symposium

# Install dependencies
pip install -r requirements.txt

# Configure API key
echo '{"perplexity": "pplx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}' > llm_keys.key
```

### Execution
```bash
# Run full pipeline
python3 1_Research_ISM_Presenters.py
python3 2_Research_ISM_Participants.py
python3 3_ISM_Participant_FieldSHIFT.py
python3 4_ISM_Shifted_Catechisms.py
python3 5_ISM_Collab_Catechisms.py

# Or run individual components as needed
```

## Integration Points

### Pre-Workshop
- Presenter research analysis
- Participant profiling
- Domain integration mapping
- Initial project proposals
- Collaboration matching

### During Workshop
- Real-time profile updates
- Domain knowledge transfer
- Project refinement
- Collaboration facilitation
- Resource recommendations

### Post-Workshop
- Project implementation
- Collaboration support
- Domain integration
- Knowledge transfer
- Community building

## Technical Infrastructure

### Data Processing
- Token-aware text processing
- Comprehensive logging system
- Error handling and recovery
- Progress tracking
- Context management

### Report Generation
- In-line citations
- Evidence-based claims
- Structured formats
- Multiple output types
- Comprehensive metadata

### Future Development
- Real-time analysis updates
- Interactive project refinement
- Dynamic collaboration matching
- Automated follow-up
- Impact tracking

## Community Resources

### External Links
- [Intelligent Soft Matter workshop](https://softmat.net/intelligent-soft-matter/)
- [Active Inference Institute](https://activeinference.institute/)
- [OpenAlex](https://openalex.org/)
- [Perplexity API](https://perplexity.ai/)

### Support
- [Contributing Guidelines](CONTRIBUTING.md)
- [License](LICENSE) - MIT
- Contact: [contact@intelligentsoftmatter.institute](mailto:contact@intelligentsoftmatter.institute)