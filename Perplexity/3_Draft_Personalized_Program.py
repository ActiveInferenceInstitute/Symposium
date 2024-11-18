import os
import pandas as pd
from pathlib import Path
import traceback
import time
import json
from Perplexity_Methods import (
    setup_logging,
    get_perplexity_client,
    get_perplexity_response,
    save_markdown_report,
    save_json_report
)

def load_participant_profiles(base_path='outputs/participants/'):
    """Load all participant research profiles"""
    logger = setup_logging("program_planner")
    profiles = {}
    
    try:
        base_dir = Path(base_path)
        for participant_dir in base_dir.iterdir():
            if participant_dir.is_dir():
                profile_path = participant_dir / f"{participant_dir.name}_profile.md"
                if profile_path.exists():
                    with open(profile_path, 'r', encoding='utf-8') as f:
                        profiles[participant_dir.name] = f.read()
        
        logger.info(f"📚 Loaded {len(profiles)} participant profiles")
        return profiles
    except Exception as e:
        logger.error(f"❌ Error loading participant profiles: {e}")
        raise

def generate_learning_plan_prompt(participant_name, profile_content):
    """Generate prompt for creating personalized learning plan"""
    return f"""Based on the following participant profile, create a highly personalized and actionable learning plan for Active Inference:

{profile_content}

Please create a detailed, structured learning plan that includes:

1. IMMEDIATE NEXT STEPS (1-2 weeks):
   - Specific resources to start with
   - Initial learning objectives
   - Concrete actions to take

2. SHORT-TERM GOALS (1-3 months):
   - Key concepts to master
   - Practical exercises or projects
   - Recommended study materials
   - Community engagement opportunities

3. MEDIUM-TERM DEVELOPMENT (3-6 months):
   - Advanced topics to explore
   - Potential collaboration opportunities
   - Application projects in their domain
   - Skill-building activities

4. SPECIFIC RESOURCES:
   - Active Inference materials, from Active Inference Institute and others
   - Relevant Academic papers and tutorials
   - Software tools and frameworks
   - Community resources and events
   - Domain-specific applications

5. PROGRESS TRACKING:
   - Milestones and checkpoints
   - Self-assessment methods
   - Practical application opportunities

Focus on making the plan:
- Highly specific to their background and interests
- Actionable with concrete next steps
- Realistic given their current level
- Aligned with their stated learning needs
- Connected to their domain of application

Include links to specific resources where possible."""

def save_learning_plan(participant_name, content):
    """Save personalized learning plan in participant-specific folder"""
    safe_name = "".join(x for x in participant_name if x.isalnum() or x in [' ', '-', '_']).strip()
    safe_name = safe_name.replace(' ', '_')
    
    # Create participant-specific directory within outputs/participants
    base_path = Path('outputs/participants')
    participant_dir = base_path / safe_name
    participant_dir.mkdir(parents=True, exist_ok=True)
    
    # Save as markdown
    save_markdown_report(
        content,
        participant_dir / f"{safe_name}_learning_plan.md",
        f"Active Inference Learning Plan: {participant_name}"
    )
    
    # Save as JSON
    save_json_report(
        content,
        participant_dir / f"{safe_name}_learning_plan.json",
        {
            "participant": participant_name,
            "type": "learning_plan",
            "generated": time.strftime("%Y-%m-%d")
        }
    )

def main():
    """Main function to create personalized learning plans."""
    logger = setup_logging("program_planner")
    total_start_time = time.time()
    
    try:
        logger.info("🚀 Starting personalized learning plan generation...")
        
        # Initialize Perplexity client
        client = get_perplexity_client()
        
        # Load participant profiles
        profiles = load_participant_profiles()
        
        if not profiles:
            logger.error("❌ No participant profiles found")
            return
        
        logger.info(f"📋 Creating learning plans for {len(profiles)} participants")
        
        # Process each participant
        for idx, (participant_name, profile) in enumerate(profiles.items(), 1):
            plan_start_time = time.time()
            
            logger.info(f"\n📝 Creating learning plan ({idx}/{len(profiles)}): {participant_name}")
            
            try:
                # Generate learning plan
                prompt = generate_learning_plan_prompt(participant_name, profile)
                learning_plan = get_perplexity_response(
                    client,
                    prompt,
                    "You are an Active Inference education specialist focused on creating "
                    "personalized learning paths. Provide specific, actionable plans with "
                    "concrete resources and next steps."
                )
                
                # Save learning plan
                save_learning_plan(participant_name, learning_plan)
                
                plan_time = time.time() - plan_start_time
                logger.info(f"✅ Completed learning plan for {participant_name} in {plan_time:.2f} seconds")
                
            except Exception as e:
                logger.error(f"❌ Error creating plan for {participant_name}: {e}")
                logger.error(traceback.format_exc())
                continue
        
        total_time = time.time() - total_start_time
        logger.info(f"\n🎉 All learning plans complete! Total time: {total_time:.2f} seconds")
        logger.info(f"📁 Plans saved in outputs/participants/")
                
    except Exception as e:
        logger.error(f"❌ Fatal error in main: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
