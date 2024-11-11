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

def load_participant_data(base_path='outputs/participants/'):
    """Load participant profiles and learning plans"""
    logger = setup_logging("application_planner")
    participant_data = {}
    
    try:
        base_dir = Path(base_path)
        for participant_dir in base_dir.iterdir():
            if participant_dir.is_dir():
                profile_path = participant_dir / f"{participant_dir.name}_profile.md"
                plan_path = participant_dir / f"{participant_dir.name}_learning_plan.md"
                
                if profile_path.exists() and plan_path.exists():
                    with open(profile_path, 'r', encoding='utf-8') as f:
                        profile = f.read()
                    with open(plan_path, 'r', encoding='utf-8') as f:
                        plan = f.read()
                        
                    participant_data[participant_dir.name] = {
                        'profile': profile,
                        'learning_plan': plan
                    }
        
        logger.info(f"📚 Loaded data for {len(participant_data)} participants")
        return participant_data
    except Exception as e:
        logger.error(f"❌ Error loading participant data: {e}")
        raise

def generate_project_prompt(participant_name, participant_info):
    """Generate prompt for creating project proposals using Heilmeier Catechism"""
    return f"""Based on the following participant's profile and learning plan, generate 3 detailed Active Inference project proposals that align with their interests and capabilities:

PARTICIPANT INFORMATION:
Profile:
{participant_info['profile']}

Learning Plan:
{participant_info['learning_plan']}

For each project proposal, please structure the response using the Heilmeier Catechism format:

1. What are you trying to do? Articulate your objectives using absolutely no jargon.
2. How is it done today, and what are the limits of current practice?
3. What is new in your approach and why do you think it will be successful?
4. Who cares? If you succeed, what difference will it make?
5. What are the risks?
6. How much will it cost?
7. How long will it take?
8. What are the mid-term and final "check points" to see if you're on track?

Please ensure each proposal:
- Directly relates to Active Inference theory or applications
- Leverages the participant's specific background and interests
- Has realistic scope and timeline
- Includes specific technical details and methodologies
- Identifies potential collaborators or resources
- Considers both theoretical and practical impacts

Generate 3 distinct proposals ranging from:
1. An immediate, smaller-scope project
2. A medium-term, moderate-scope project
3. An ambitious, longer-term project

Each proposal should be concrete and actionable while maintaining appropriate scope for the participant's current stage."""

def save_project_proposals(participant_name, content):
    """Save project proposals in participant's directory"""
    safe_name = "".join(x for x in participant_name if x.isalnum() or x in [' ', '-', '_']).strip()
    safe_name = safe_name.replace(' ', '_')
    
    base_path = Path('outputs/participants')
    participant_dir = base_path / safe_name
    participant_dir.mkdir(parents=True, exist_ok=True)
    
    # Save as markdown
    save_markdown_report(
        content,
        participant_dir / f"{safe_name}_project_proposals.md",
        f"Active Inference Project Proposals: {participant_name}"
    )
    
    # Save as JSON
    save_json_report(
        content,
        participant_dir / f"{safe_name}_project_proposals.json",
        {
            "participant": participant_name,
            "type": "project_proposals",
            "generated": time.strftime("%Y-%m-%d")
        }
    )

def main():
    """Main function to generate project proposals."""
    logger = setup_logging("project_planner")
    total_start_time = time.time()
    
    try:
        logger.info("🚀 Starting project proposal generation...")
        
        # Initialize Perplexity client
        client = get_perplexity_client()
        
        # Load participant data
        participant_data = load_participant_data()
        
        if not participant_data:
            logger.error("❌ No participant data found")
            return
        
        logger.info(f"📋 Generating project proposals for {len(participant_data)} participants")
        
        # Process each participant
        for idx, (participant_name, info) in enumerate(participant_data.items(), 1):
            proposal_start_time = time.time()
            
            logger.info(f"\n📝 Generating proposals ({idx}/{len(participant_data)}): {participant_name}")
            
            try:
                # Generate project proposals
                prompt = generate_project_prompt(participant_name, info)
                proposals = get_perplexity_response(
                    client,
                    prompt,
                    "You are an Active Inference research director specializing in "
                    "project development and research planning. Focus on creating "
                    "concrete, well-structured proposals that follow the Heilmeier "
                    "Catechism format."
                )
                
                # Save proposals
                save_project_proposals(participant_name, proposals)
                
                proposal_time = time.time() - proposal_start_time
                logger.info(f"✅ Completed proposals for {participant_name} in {proposal_time:.2f} seconds")
                
            except Exception as e:
                logger.error(f"❌ Error generating proposals for {participant_name}: {e}")
                logger.error(traceback.format_exc())
                continue
        
        total_time = time.time() - total_start_time
        logger.info(f"\n🎉 All project proposals complete! Total time: {total_time:.2f} seconds")
        logger.info(f"📁 Proposals saved in outputs/participants/")
                
    except Exception as e:
        logger.error(f"❌ Fatal error in main: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
