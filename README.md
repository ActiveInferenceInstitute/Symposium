# IdeaSHIFT: Transformative Research Domain Shifting for Next-Gen Scientific Idea Generation

**IdeaSHIFT** is a platform designed to facilitate the massive exploration and combination of ideas across disciplines. By analyzing researchers' profiles and publications, IdeaSHIFT generates research profiles in relation to a given field with a trajectory and contributions to the field, open questions and concepts aimed at pushing the boundaries of conventional research. IdeaSHIFT systematically explores combinations of ideas from different fields by leveraging a domain-shifting approach of the given research field, enabling the discovery of new, high-impact research directions that can be presented in  a form of detailed projects.

This project originated during the preparation of two events:
1. [SoftComp Workshop on Intelligent Soft Matter](https://softmat.net/intelligent-soft-matter/)
2. [4th Applied Active Inference Symposium](https://symposium.activeinference.institute/)

## Background: A Shift in Scientific Publishing and Evaluation

The academic publishing system, based largely on descriptive texts, bibliometrics and journal reputation, has remained largely unchanged for decades. The rise of LLMs only underscores the inadequacies of this system. There is an urgent need to rethink research sense-making and reintegrate creativity back into scientific progress. IdeaSHIFT was developed to address this need for a more dynamic and open-ended approach, enabling researchers to systematically explore, combine, and prioritize ideas that may be unconventional or unfeasible but carry transformative potential.

## Core Functionalities

1. **State of the Art Analysis**
   IdeaSHIFT starts by analyzing researcher profiles and publications, compiling a concise description of the field’s background and current state of the art. It provides a summary of major contributions, trends, and existing research. This serves as a context of the background for LLM agents. 

2. **Future Roadmap: Building Paths to Discovery**
   IdeaSHIFT employs two LLM agents to craft a roadmap for meaningful research advances:
   - **Critical Referee Agent:** This agent examines the field very critically, identifying overlooked topics, biases, and gaps in current research methodologies and concepts. By surfacing these shortcomings, it provides the essential critical insight to the next agent.
   - **Creative Solution Agent:** The creative agent addresses the shortcomings highlighted by the Referee Agent, proposing novel solutions and outlining a “Tech Tree” This roadmap points to potential breakthroughs and new paths for researchers willing to push the field forward.

3. **Cross-Domain Idea Generation**
   Utilizing domain-shifting techniques, IdeaSHIFT explores innovative combinations of ideas across disciplines. This feature enables researchers to break through traditional boundaries by identifying unique, interdisciplinary questions that have yet to be addressed, providing a springboard for creative and impactful research ideas.

4. **Open Innovation Project Development**
   IdeaSHIFT aims to catalyze ideas for the development of high-risk, high-reward projects. With IdeaSHIFT, researchers are encouraged to embrace the unknown, developing new directions that are more about pushing boundaries than fitting within established paradigms.

## Getting Started

### Requirements
- Python 3.7+
- API keys for LLM services (e.g., [OpenAI](https://platform.openai.com/) API)

### Installation
Clone this repository and install dependencies:

```bash
git clone https://github.com/ActiveInferenceInstitute/IdeaSHIFT.git
cd IdeaSHIFT
pip install -r requirements.txt
