import os
import pandas as pd
from pathlib import Path
import traceback
import time
from Perplexity_Methods import (
    setup_logging,
    get_perplexity_client,
    get_perplexity_response,
    save_markdown_report,
    save_json_report
)

def load_participant_data(base_path='../inputs/IntelligentSoftMatter/participants/'):
    """Load and clean participant data from individual folders"""
    logger = setup_logging("participant_data")
    participants = {}
    
    try:
        for participant_folder in os.listdir(base_path):
            folder_path = os.path.join(base_path, participant_folder)
            if os.path.isdir(folder_path):
                # Look for the two key files
                group_by_file = os.path.join(folder_path, 'openalex-group-by-20241117.csv')
                works_file = os.path.join(folder_path, [f for f in os.listdir(folder_path) 
                                                        if f.startswith('works-') and f.endswith('.csv')][0])
                
                if os.path.exists(group_by_file) and os.path.exists(works_file):
                    participants[participant_folder] = {
                        'name': participant_folder,
                        'topics': pd.read_csv(group_by_file),
                        'works': pd.read_csv(works_file)
                    }
        
        logger.info(f"✅ Successfully loaded data for {len(participants)} participants")
        return participants
    except Exception as e:
        logger.error(f"❌ Error loading participant data: {e}")
        raise

def generate_participant_prompt(participant_data):
    """Generate a comprehensive research prompt for a participant"""
    topics_str = participant_data['topics'].to_string() if not participant_data['topics'].empty else "No topic data available"
    recent_works = participant_data['works'][['title', 'publication_year', 'cited_by_count']].head()
    works_str = recent_works.to_string() if not recent_works.empty else "No works data available"
    
    return f"""Please conduct a detailed analysis of {participant_data['name']}'s research profile and potential in Intelligent Soft Matter. Create a comprehensive report addressing the following sections:

1. **ACADEMIC AND PROFESSIONAL BACKGROUND**
   - Educational trajectory
   - Research experience
   - Technical skills and competencies
   - Professional development path

2. **CURRENT RESEARCH PROFILE**
   - Active research areas
   - Methodological approaches
   - Technical expertise
   - Research tools and frameworks used

3. **INTELLIGENT SOFT MATTER ENGAGEMENT**
   - Current understanding level
   - Relevant experience and projects
   - Application of concepts
   - Integration with existing work

4. **TECHNICAL CAPABILITIES**
   - Programming and computational skills
   - Experimental techniques
   - Analytical methods
   - Tool development experience

5. **LEARNING AND DEVELOPMENT**
   - Knowledge gaps identification
   - Recommended learning resources
   - Skill development priorities
   - Training opportunities

6. **COLLABORATION POTENTIAL**
   - Synergistic research areas
   - Complementary skills
   - Potential collaboration partners
   - Joint project opportunities

7. **CONTRIBUTION OPPORTUNITIES**
   - Potential research contributions
   - Technical skill sharing
   - Knowledge transfer possibilities
   - Community engagement potential

8. **GROWTH TRAJECTORY**
   - Short-term development goals
   - Medium-term research objectives
   - Long-term career possibilities
   - Skill enhancement pathway

9. **CHALLENGES AND SOLUTIONS**
   - Technical challenges
   - Resource limitations
   - Knowledge gaps
   - Proposed solutions

10. **COMMUNITY INTEGRATION**
    - Networking opportunities
    - Community contribution potential
    - Knowledge sharing possibilities
    - Collaborative project ideas

11. **ACTIONABLE RECOMMENDATIONS**
    - Immediate next steps
    - Resource acquisition strategy
    - Skill development plan
    - Collaboration initiation steps

Please analyze using the following data:

Name: {participant_data['name']}
Topics and their frequencies:
{topics_str}

Recent publications:
{works_str}

Analysis Guidelines:
- Maintain appropriate uncertainty where data is limited
- Focus on actionable insights and practical steps
- Consider both technical and collaborative aspects
- Emphasize open source and community engagement
- Identify specific learning resources and opportunities
- Consider interdisciplinary connections
- Highlight potential contributions to the field
- Include specific recommendations for growth
- Address both short-term and long-term development
- Consider the broader Intelligent Soft Matter community context

Please provide a detailed, well-structured report that can serve as a roadmap for the participant's development and integration into the Intelligent Soft Matter community."""

def save_participant_report(participant_name, content, report_type='markdown'):
    """Save participant research report"""
    safe_name = "".join(x for x in participant_name if x.isalnum() or x in [' ', '-', '_']).strip()
    safe_name = safe_name.replace(' ', '_')
    
    # Create participant-specific directory within outputs/participants
    base_path = Path('outputs/participants')
    participant_dir = base_path / safe_name
    participant_dir.mkdir(parents=True, exist_ok=True)
    
    if report_type == 'markdown':
        save_markdown_report(
            content,
            participant_dir / f"{safe_name}_profile.md",
            f"Research Profile: {participant_name}"
        )
    else:  # json
        save_json_report(
            content,
            participant_dir / f"{safe_name}_profile.json",
            {"participant": participant_name}
        )

def main():
    """Main function to orchestrate participant research."""
    logger = setup_logging("participant_research")
    total_start_time = time.time()
    
    try:
        logger.info("🚀 Starting participant research analysis...")
        
        # Initialize Perplexity client
        client = get_perplexity_client()
        
        # Load participant data
        participants = load_participant_data()
        
        if not participants:
            logger.error("❌ No participant data found")
            return
        
        logger.info(f"📊 Found {len(participants)} participants to analyze")
        
        # Process each participant
        for idx, (participant_name, participant_data) in enumerate(participants.items(), 1):
            participant_start_time = time.time()
            logger.info(f"\n🔍 Analyzing participant ({idx}/{len(participants)}): {participant_name}")
            
            try:
                # Generate and get research analysis
                prompt = generate_participant_prompt(participant_data)
                analysis = get_perplexity_response(
                    client, 
                    prompt,
                    "You are a research analyst specializing in Active Inference community analysis. "
                    "Please maintain appropriate uncertainty and avoid overstating conclusions where "
                    "information is limited."
                )
                
                # Save results in both formats
                save_participant_report(participant_name, analysis, 'markdown')
                save_participant_report(participant_name, analysis, 'json')
                
                participant_time = time.time() - participant_start_time
                logger.info(f"✅ Completed analysis for {participant_name} in {participant_time:.2f} seconds")
                
            except Exception as e:
                logger.error(f"❌ Error processing participant {participant_name}: {e}")
                logger.error(traceback.format_exc())
                continue
        
        total_time = time.time() - total_start_time
        logger.info(f"\n🎉 Analysis complete! Total time: {total_time:.2f} seconds")
        logger.info(f"📁 Reports saved in outputs/participants/")
                
    except Exception as e:
        logger.error(f"❌ Fatal error in main: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
