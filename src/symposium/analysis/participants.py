"""Participant profiling and analysis module."""

import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
from symposium.core.api import BaseAPIProvider, PaymentRequiredError
from symposium.core.data_loader import DataLoader

logger = logging.getLogger(__name__)


class ParticipantAnalyzer:
    """Analyzer for participant profiles and background research."""

    def __init__(self, api_client: BaseAPIProvider, config: Optional[Dict[str, Any]] = None):
        """Initialize participant analyzer.

        Args:
            api_client: API client for generating analysis
            config: Optional configuration dictionary
        """
        self.api_client = api_client
        self.config = config or {}
        self.data_loader = DataLoader()

    def load_participant_data(self, csv_path: Path) -> Dict[str, Dict[str, Any]]:
        """Load participant data from CSV file.

        Args:
            csv_path: Path to participant CSV file

        Returns:
            Dictionary mapping participant names to their data
        """
        return self.data_loader.load_participant_data(csv_path)

    def generate_background_research_prompt(self, participant_data: Dict[str, Any]) -> str:
        """Generate background research prompt for a participant.

        Args:
            participant_data: Participant data dictionary

        Returns:
            Generated prompt string
        """
        name = participant_data.get('name', 'Unknown')
        affiliations = participant_data.get('affiliations', '')
        background = participant_data.get('background', '')
        orcid = participant_data.get('orcid', '')

        prompt = f"""Conduct DEEP COMPREHENSIVE WEB RESEARCH on the following Active Inference Symposium participant. 

**RESEARCH SUBJECT:**
- **Name:** {name}
- **Affiliations:** {affiliations}
- **ORCID:** {orcid}
- **Self-Reported Background:** {background}

**RESEARCH METHODOLOGY:**
Perform exhaustive web searches across academic databases, professional profiles, publications, conference proceedings, social media (LinkedIn, Twitter/X, ResearchGate, Google Scholar), institutional websites, and any other relevant online sources. Leave no stone unturned.

**REQUIRED ANALYSIS WITH CITATIONS:**

1. **ACADEMIC BACKGROUND** (cite all sources)
   - Educational history: degrees, institutions, graduation years [with links]
   - Research areas and specific expertise domains [with links]
   - Current and past academic positions [with links to institution profiles]
   - Notable achievements, awards, grants, honors [with links to announcements]
   - Academic profile pages (Google Scholar, ResearchGate, ORCID, institutional page) [with direct links]

2. **RESEARCH CONTRIBUTIONS** (cite all publications)
   - Key publications: titles, journals, year, DOI/links [provide full citation with links]
   - Research focus areas and methodologies employed [with links to papers]
   - Citation metrics: h-index, total citations, recent impact [with links to scholar profiles]
   - Collaborative networks: frequent co-authors and research groups [with links]
   - Recent preprints and working papers [with links to arXiv, bioRxiv, etc.]

3. **PROFESSIONAL EXPERIENCE** (cite all sources)
   - Complete employment history with dates [with links to LinkedIn, institutional pages]
   - Industry experience and consulting work [with links]
   - Professional affiliations and society memberships [with links]
   - Leadership roles in professional organizations [with links]
   - Patents, technical reports, or applied work [with links]

4. **ACTIVE INFERENCE & RELATED RESEARCH** (cite extensively)
   - Direct connections to Active Inference: publications, presentations, projects [with links]
   - Adjacent fields: free energy principle, Bayesian inference, computational neuroscience [with links]
   - Methodological overlap: modeling, simulation, mathematical frameworks [with links]
   - Potential applications of their expertise to Active Inference [with links to relevant work]
   - Research gaps they are positioned to address [with supporting links]

5. **ACADEMIC & PROFESSIONAL NETWORK** (cite all sources)
   - Key collaborators with links to their profiles and joint publications [with links]
   - Conference presentations: titles, conferences, years [with links to proceedings/videos]
   - Workshop organization or participation [with links]
   - Community engagement: blog posts, tutorials, code repositories [with links]
   - Social media presence related to research [with links to profiles]

6. **ONLINE PRESENCE & RESOURCES** (provide all links)
   - Personal website or research page [link]
   - Google Scholar profile [link]
   - ResearchGate profile [link]
   - LinkedIn profile [link]
   - GitHub or other code repositories [links]
   - Twitter/X or other social media [links]
   - ORCID profile [link]
   - Institutional profile page [link]
   - Any videos, podcasts, or interviews [links]

7. **FUTURE POTENTIAL & OPPORTUNITIES**
   - Emerging research directions based on recent work [with links]
   - Opportunities for growth in Active Inference community [with supporting evidence/links]
   - Potential impact on the field [with links to foundational work]
   - Strategic collaboration opportunities [with links to potential collaborators]

**CRITICAL REQUIREMENTS:**
- Cite EVERY factual claim with [numbered references] or [source links]
- Provide clickable URLs for all online resources
- Include DOIs for all publications
- Search MULTIPLE databases and sources
- Verify information across multiple sources when possible
- Note when information is limited or unavailable
- Distinguish between verified facts and inferences
- Prioritize recent activity and publications (last 3-5 years)

**OUTPUT FORMAT:**
Use markdown with clickable links throughout. For each major finding, provide the source link immediately. Create a "References" section at the end with all numbered citations and their full URLs.

GOAL: Create the most comprehensive, well-sourced research profile possible using all available web resources."""

        return prompt

    def generate_curriculum_prompt(self, participant_data: Dict[str, Any]) -> str:
        """Generate personalized curriculum prompt for a participant.

        Args:
            participant_data: Participant data dictionary

        Returns:
            Generated prompt string
        """
        name = participant_data.get('name', 'Unknown')
        background = participant_data.get('background', '')
        learning_needs = participant_data.get('learning_needs', '')
        active_inference_application = participant_data.get('active_inference_application', '')
        challenges = participant_data.get('challenges', '')
        pragmatic_value = participant_data.get('pragmatic_value', '')
        epistemic_value = participant_data.get('epistemic_value', '')

        prompt = f"""Create a personalized learning curriculum for Active Inference for the following participant:

**Participant Name:** {name}

**Background:**
{background}

**Current Active Inference Application:**
{active_inference_application}

**Learning Needs:**
{learning_needs}

**Challenges:**
{challenges}

**Pragmatic Value Sought:**
{pragmatic_value}

**Epistemic Value Sought:**
{epistemic_value}

Design a comprehensive, personalized curriculum that will help this participant learn and apply Active Inference effectively. Structure the curriculum as follows:

1. **ASSESSMENT OF CURRENT LEVEL**
   - Their current understanding of Active Inference
   - Knowledge gaps and areas needing development
   - Learning style and preferences based on background

2. **PERSONALIZED LEARNING PATH**
   - Foundational concepts tailored to their background
   - Progressive skill development
   - Application-focused modules
   - Timeline and milestones

3. **CORE CONCEPTS MODULES**
   - Mathematical foundations (if needed)
   - Theoretical frameworks
   - Practical applications in their domain
   - Implementation strategies

4. **HANDS-ON LEARNING**
   - Computational exercises
   - Real-world applications
   - Tool and software training
   - Project-based learning

5. **ADVANCED TOPICS**
   - Specialized applications in their field
   - Research methodologies
   - Advanced mathematical concepts
   - Emerging developments

6. **PRACTICAL APPLICATIONS**
   - How to apply Active Inference in their work
   - Case studies and examples
   - Implementation challenges and solutions
   - Evaluation and assessment methods

7. **COMMUNITY AND COLLABORATION**
   - How to engage with the Active Inference community
   - Finding mentors and collaborators
   - Contributing to the field
   - Networking opportunities

8. **ASSESSMENT AND PROGRESSION**
   - Milestones and checkpoints
   - Self-assessment tools
   - Portfolio development
   - Certification or validation paths

9. **RESOURCES AND TOOLS**
   - Recommended readings and papers
   - Software tools and platforms
   - Online courses and tutorials
   - Community resources and forums

10. **IMPLEMENTATION ROADMAP**
    - Short-term goals (1-3 months)
    - Medium-term objectives (3-6 months)
    - Long-term vision (6-12 months)
    - Success metrics and evaluation

Tailor this curriculum specifically to their background, interests, and stated learning needs. Make it practical, actionable, and focused on real-world application."""

        return prompt

    def research_participant_background(
        self,
        participant_data: Dict[str, Any],
        system_prompt: Optional[str] = None
    ) -> str:
        """Research a participant's background using internet search.

        Args:
            participant_data: Participant data dictionary
            system_prompt: Optional system prompt override

        Returns:
            Comprehensive background research
        """
        if system_prompt is None:
            system_prompt = (
                "You are an elite research intelligence analyst with access to real-time web search, "
                "academic databases, and comprehensive internet resources. Your specialty is conducting "
                "DEEP INVESTIGATIVE RESEARCH on academics and professionals. "
                "\n\n"
                "MANDATE:\n"
                "- Perform exhaustive multi-source web searches\n"
                "- Cross-reference information across multiple databases\n"
                "- Cite EVERY source with clickable links and URLs\n"
                "- Provide DOIs for all publications\n"
                "- Include direct links to profiles, papers, and resources\n"
                "- Search Google Scholar, ResearchGate, LinkedIn, ORCID, institutional pages, arXiv, etc.\n"
                "- Look for recent publications, preprints, conference talks, and social media presence\n"
                "- Create a comprehensive References section with all URLs\n"
                "\n"
                "NEVER make claims without citations. ALWAYS provide source links. "
                "Your research should be so thorough that every statement is verifiable through the provided links."
            )

        prompt = self.generate_background_research_prompt(participant_data)
        
        # Use Perplexity's web search capabilities to maximum extent
        # Increase max_tokens to allow for comprehensive research with citations
        response = self.api_client.get_response(
            prompt, 
            system_prompt,
            max_tokens=4000  # Allow longer responses for comprehensive research with links
        )
        logger.info(f"Generated background research for {participant_data.get('name', 'Unknown')}")

        return response

    def generate_personalized_curriculum(
        self,
        participant_data: Dict[str, Any],
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate a personalized Active Inference curriculum.

        Args:
            participant_data: Participant data dictionary
            system_prompt: Optional system prompt override

        Returns:
            Personalized curriculum
        """
        if system_prompt is None:
            system_prompt = (
                "You are an expert educational designer specializing in Active Inference "
                "and personalized learning. Create comprehensive, practical curricula that "
                "bridge theory and application. Focus on actionable learning paths."
            )

        prompt = self.generate_curriculum_prompt(participant_data)
        response = self.api_client.get_response(prompt, system_prompt)
        logger.info(f"Generated curriculum for {participant_data.get('name', 'Unknown')}")

        return response

    def analyze_participant_profile(
        self,
        participant_data: Dict[str, Any],
        system_prompt: Optional[str] = None
    ) -> str:
        """Analyze a participant's profile for symposium participation.

        Args:
            participant_data: Participant data dictionary
            system_prompt: Optional system prompt override

        Returns:
            Analysis text
        """
        if system_prompt is None:
            system_prompt = (
                "You are an expert in educational program design and research mentoring. "
                "Provide constructive, detailed analysis that helps participants understand "
                "their current position and develop actionable learning plans."
            )

        name = participant_data.get('name', 'Unknown')
        background = participant_data.get('background', '')
        pragmatic_value = participant_data.get('pragmatic_value', '')
        epistemic_value = participant_data.get('epistemic_value', '')
        active_inference_application = participant_data.get('active_inference_application', '')
        learning_needs = participant_data.get('learning_needs', '')
        challenges = participant_data.get('challenges', '')
        future_impact = participant_data.get('future_impact', '')

        prompt = f"""Please analyze the profile for symposium participant: {name}

**Background & Prior Works:**
{background}

**Pragmatic Value Sought:**
{pragmatic_value}

**Epistemic Value Sought:**
{epistemic_value}

**Current Active Inference Application:**
{active_inference_application}

**Learning Needs:**
{learning_needs}

**Challenges:**
{challenges}

**Future Impact Vision:**
{future_impact}

Please provide a comprehensive profile analysis including:

1. **EXPERTISE ASSESSMENT**
   - Current knowledge level in Active Inference
   - Technical skills and methodologies relevant to the field
   - Research background and its relation to Active Inference
   - Professional experience and domain expertise

2. **LEARNING OPPORTUNITIES**
   - Knowledge gaps in Active Inference theory and application
   - Recommended learning paths based on their background
   - Skills to develop for effective participation
   - Resources and tools they should explore

3. **RESEARCH INTERESTS ALIGNMENT**
   - How their interests align with Active Inference
   - Potential research directions they could pursue
   - Areas where they could contribute to the field
   - Gaps between their expertise and Active Inference applications

4. **COLLABORATION POTENTIAL**
   - Complementary skills for Active Inference research
   - Potential research partnerships within the community
   - Community contribution opportunities
   - Networking and engagement strategies

5. **SYMPOSIUM PARTICIPATION STRATEGY**
   - Sessions and topics most relevant to their needs
   - Workshop and tutorial priorities
   - Networking opportunities to pursue
   - Action items for maximizing symposium value

6. **DEVELOPMENT ROADMAP**
   - Short-term goals for symposium participation
   - Medium-term research and learning objectives
   - Long-term trajectory in Active Inference
   - Success metrics and milestones

7. **ACTIVE INFERENCE INTEGRATION**
   - How their background aligns with Active Inference principles
   - Opportunities to contribute to Active Inference challenges
   - Potential for applying Active Inference in their field
   - Integration pathways and strategies"""

        return prompt

    def analyze_participant(
        self,
        participant_data: Dict[str, Any],
        system_prompt: Optional[str] = None
    ) -> str:
        """Analyze a participant's profile.

        Args:
            participant_data: Participant data dictionary
            system_prompt: Optional system prompt override

        Returns:
            Analysis text
        """
        prompt = self.analyze_participant_profile(participant_data, system_prompt)
        response = self.api_client.get_response(prompt, system_prompt)
        logger.info(f"Generated analysis for participant: {participant_data.get('name', 'Unknown')}")

        return response

    def analyze_all_participants(
        self,
        csv_path: Path,
        output_dir: Path,
        include_background_research: bool = False,
        include_curriculum: bool = False,
        perplexity_client: Optional[BaseAPIProvider] = None
    ) -> Dict[str, Dict[str, str]]:
        """Analyze all participants from CSV data.

        Args:
            csv_path: Path to participant CSV file
            output_dir: Output directory for reports
            include_background_research: Whether to generate background research
            include_curriculum: Whether to generate personalized curricula
            perplexity_client: Optional Perplexity client for background research

        Returns:
            Dictionary mapping participant names to their analysis results
        """
        from symposium.io.writers import ReportWriter

        # Load participant data
        participants = self.load_participant_data(csv_path)
        results = {}

        for participant_name, participant_data in participants.items():
            try:
                logger.info(f"Processing participant: {participant_name}")
                participant_results = {}

                # Generate profile analysis
                profile_analysis = self.analyze_participant(participant_data)
                participant_results['profile_analysis'] = profile_analysis
                logger.info(f"✅ Profile analysis completed for {participant_name}")

                # Save profile analysis
                ReportWriter.save_participant_report(
                    participant_name,
                    profile_analysis,
                    output_dir,
                    "profile_analysis"
                )

                # Generate background research if requested (ALWAYS use Perplexity)
                if include_background_research:
                    if perplexity_client:
                        logger.info(f"🔍 Using Perplexity Sonar for background research: {participant_name}")
                        # Temporarily use Perplexity client for this operation
                        original_client = self.api_client
                        self.api_client = perplexity_client
                        
                        background = self.research_participant_background(participant_data)
                        participant_results['background_research'] = background
                        
                        # Restore original client
                        self.api_client = original_client
                        logger.info(f"✅ Background research completed for {participant_name}")
                    else:
                        logger.warning(f"Perplexity client not provided for background research: {participant_name}")
                        background = self.research_participant_background(participant_data)
                        participant_results['background_research'] = background

                    ReportWriter.save_participant_report(
                        participant_name,
                        background,
                        output_dir,
                        "background_research"
                    )

                # Generate curriculum if requested (uses primary OpenRouter client)
                if include_curriculum:
                    logger.info(f"🤖 Using OpenRouter Claude for curriculum: {participant_name}")
                    curriculum = self.generate_personalized_curriculum(participant_data)
                    participant_results['curriculum'] = curriculum
                    logger.info(f"✅ Curriculum completed for {participant_name}")

                    ReportWriter.save_participant_report(
                        participant_name,
                        curriculum,
                        output_dir,
                        "curriculum"
                    )

                results[participant_name] = participant_results

            except PaymentRequiredError as e:
                # Payment errors are fatal - stop processing immediately
                logger.error(f"Payment required error: {e}")
                print("\n" + "=" * 60)
                print("❌ PAYMENT REQUIRED ERROR")
                print("=" * 60)
                print(f"\n{e.provider.upper()} API requires payment to continue.")
                print(f"Error: {e.message}")
                print("\nPlease add credits to your account:")
                if e.provider.lower() == "openrouter":
                    print("  https://openrouter.ai/settings/credits")
                print("\nProcessing stopped. Partial results saved for completed participants.")
                print("=" * 60 + "\n")
                break
            except Exception as e:
                # Other errors allow graceful degradation - continue with next participant
                logger.error(f"Error processing participant {participant_name}: {e}")
                continue

        logger.info(f"Completed processing for {len(results)} participants")
        return results

    def generate_column_summaries(
        self,
        csv_path: Path,
        output_dir: Path
    ) -> Dict[str, Dict[str, Any]]:
        """Generate word clouds and summaries for each CSV column.

        Args:
            csv_path: Path to participant CSV file
            output_dir: Output directory for summaries

        Returns:
            Dictionary mapping column names to summary data
        """
        from symposium.io.writers import ReportWriter
        from symposium.visualization.embeddings import TextVisualizer

        participants = self.load_participant_data(csv_path)
        column_summaries = {}

        # Define columns to analyze (excluding personal info)
        analysis_columns = [
            'background', 'pragmatic_value', 'epistemic_value',
            'active_inference_application', 'challenges', 'learning_needs',
            'future_impact', 'comments'
        ]

        for column in analysis_columns:
            try:
                logger.info(f"Generating summary for column: {column}")

                # Get column summary statistics
                summary_stats = self.data_loader.get_column_summary(participants, column)
                column_summaries[column] = summary_stats

                # Generate LLM summary if there are responses
                if summary_stats['responses_count'] > 0:
                    system_prompt = (
                        "You are a research analyst specializing in Active Inference community analysis. "
                        "Provide comprehensive, insightful summaries of participant responses. "
                        "Identify patterns, themes, and implications for the Active Inference field."
                    )

                    summary_prompt = self._generate_column_summary_prompt(
                        column, summary_stats
                    )

                    llm_summary = self.api_client.get_response(summary_prompt, system_prompt)

                    # Save LLM summary
                    summary_content = f"""# {column.replace('_', ' ').title()} Analysis

## Summary Statistics
- **Total Participants:** {summary_stats['total_participants']}
- **Response Rate:** {summary_stats['response_rate']:.1%} ({summary_stats['responses_count']} responses)
- **Unique Responses:** {summary_stats['unique_responses']}
- **Average Response Length:** {summary_stats['avg_response_length']:.1f} characters

## Key Themes and Patterns

{llm_summary}
"""

                    ReportWriter.save_markdown_report(
                        summary_content,
                        output_dir / f"column_summary_{column}.md",
                        f"Column Summary: {column.replace('_', ' ').title()}"
                    )

                    # Generate word cloud if there are enough responses
                    if summary_stats['responses_count'] >= 3:
                        visualizer = TextVisualizer()
                        values_text = ' '.join(summary_stats['values'])

                        wordcloud_path = output_dir / f"wordcloud_{column}.png"
                        visualizer.create_word_cloud(
                            [values_text],
                            f"{column.replace('_', ' ').title()} Word Cloud",
                            wordcloud_path
                        )

            except Exception as e:
                logger.error(f"Error generating summary for column '{column}': {e}")
                column_summaries[column] = {'error': str(e)}

        logger.info(f"Generated summaries for {len(column_summaries)} columns")
        return column_summaries

    def _generate_column_summary_prompt(
        self,
        column: str,
        summary_stats: Dict[str, Any]
    ) -> str:
        """Generate prompt for column summary analysis.

        Args:
            column: Column name
            summary_stats: Summary statistics

        Returns:
            Generated prompt string
        """
        column_display = column.replace('_', ' ').title()
        responses = summary_stats['values'][:20]  # Limit to first 20 for prompt

        prompt = f"""Analyze the following responses to the question about "{column_display}" from Active Inference Symposium participants:

**Responses:**
{' | '.join(responses)}

**Analysis Context:**
- {summary_stats['responses_count']} participants provided responses
- {summary_stats['unique_responses']} unique responses
- Average response length: {summary_stats['avg_response_length']:.1f} characters

Please provide a comprehensive analysis including:

1. **KEY THEMES AND PATTERNS**
   - Main topics and themes that emerge
   - Common concerns or interests
   - Variations in perspectives and approaches

2. **COMMUNITY INSIGHTS**
   - What this reveals about the Active Inference community
   - Areas of consensus and divergence
   - Emerging trends or priorities

3. **IMPLICATIONS FOR THE FIELD**
   - Research gaps or opportunities identified
   - Practical challenges and solutions mentioned
   - Future directions suggested by participants

4. **SYMPOSIUM RELEVANCE**
   - How these responses inform symposium programming
   - Session topics that would address these needs
   - Workshop or tutorial opportunities

5. **ACTIONABLE RECOMMENDATIONS**
   - For symposium organizers
   - For the Active Inference community
   - For individual participants

6. **ACTIVE INFERENCE INTEGRATION**
   - How these responses relate to Active Inference principles
   - Theoretical connections and applications
   - Methodological implications"""

        return prompt

