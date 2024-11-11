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

def load_participant_data(csv_path='Perplexity/2024 Symposium Participant Registration (Public Share).csv'):
    """Load and clean participant registration data"""
    logger = setup_logging("participant_data")
    try:
        # Get the script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct absolute path to CSV
        abs_csv_path = os.path.join(script_dir, os.path.basename(csv_path))
        
        logger.info(f"📊 Loading participant data from {abs_csv_path}")
        df = pd.read_csv(abs_csv_path)
        # Clean empty rows and strip whitespace
        df = df.dropna(how='all')
        df = df.apply(lambda x: x.str.strip() if isinstance(x, str) else x)
        logger.info(f"✅ Successfully loaded {len(df)} participant records")
        return df
    except Exception as e:
        logger.error(f"❌ Error loading participant data: {e}")
        raise

def generate_participant_prompt(participant):
    """Generate research prompt for a participant"""
    # Extract relevant fields, handling NaN values safely
    fields = {
        'Name': participant.get('Name', 'Unknown'),
        'Affiliation': participant.get('Affiliations', 'Not specified'),
        'Background': participant.get('What is your background & prior works? Feel free to provide as much information & links as you like.', 'Not provided'),
        'Application': participant.get('How are you applying Active Inference? What domain, stage?', 'Not specified'),
        'Challenges': participant.get('What are the biggest hurdles or challenges facing Active Inference research and application?', 'Not specified'),
        'Learning_Needs': participant.get('What would help you learn and apply Active Inference? E.g. resource, tool, or community development.', 'Not specified')
    }
    
    # Clean any NaN values
    fields = {k: str(v) if pd.notna(v) else 'Not provided' for k, v in fields.items()}
    
    return f"""Please analyze the following participant's profile with focus on their relationship with Active Inference:

Name: {fields['Name']}
Affiliation: {fields['Affiliation']}
Background: {fields['Background']}
Current Application of Active Inference: {fields['Application']}
Perceived Challenges: {fields['Challenges']}
Learning Needs: {fields['Learning_Needs']}

Please provide a balanced analysis covering:
1. Background Analysis: Expertise and experience, being careful not to overstate where information is limited
2. Active Inference Journey: Current understanding and application stage
3. Learning Path: Specific needs and potential resources that could help
4. Collaboration Potential: Possible synergies with other participants/presenters
5. Challenges & Opportunities: Personal and field-wide perspectives

Note: Please maintain appropriate uncertainty where information is limited or unclear."""

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
        participants_df = load_participant_data()
        
        if participants_df.empty:
            logger.error("❌ No participant data found")
            return
        
        logger.info(f"📊 Found {len(participants_df)} participants to analyze")
        
        # Process each participant
        for idx, participant in enumerate(participants_df.to_dict('records'), 1):
            participant_name = participant.get('Name', f"Participant_{idx}")
            participant_start_time = time.time()
            
            logger.info(f"\n🔍 Analyzing participant ({idx}/{len(participants_df)}): {participant_name}")
            
            try:
                # Generate and get research analysis
                prompt = generate_participant_prompt(participant)
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
