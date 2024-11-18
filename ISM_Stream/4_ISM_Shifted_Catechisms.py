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

def load_fieldshift_analyses(base_path='outputs/participants/'):
    """Load all FieldSHIFT analyses from participant fieldshift directories"""
    logger = setup_logging("catechism_generator")
    fieldshift_data = {}
    
    try:
        base_dir = Path(base_path)
        for participant_dir in base_dir.iterdir():
            if participant_dir.is_dir():
                fieldshift_dir = participant_dir / 'fieldshift'
                if fieldshift_dir.exists():
                    participant_shifts = {}
                    for analysis_file in fieldshift_dir.glob('*_fieldshift.md'):
                        domain_name = analysis_file.stem.split('_')[-2]  # Extract domain name from filename
                        with open(analysis_file, 'r', encoding='utf-8') as f:
                            analysis = f.read()
                        participant_shifts[domain_name] = analysis
                    
                    if participant_shifts:
                        fieldshift_data[participant_dir.name] = participant_shifts
                        logger.info(f"📊 Loaded {len(participant_shifts)} FieldSHIFT analyses for {participant_dir.name}")
        
        return fieldshift_data
    except Exception as e:
        logger.error(f"❌ Error loading FieldSHIFT analyses: {e}")
        raise

def load_catechism_template(template_path='Catechism/Synthetic_Catechism.md'):
    """Load the Synthetic Catechism template"""
    logger = setup_logging("catechism_loader")
    
    try:
        # Try multiple possible locations for the template
        possible_paths = [
            template_path,
            'ISM_Stream/Catechism/Synthetic_Catechism.md',
            '../Catechism/Synthetic_Catechism.md',
            'Synthetic_Catechism.md'
        ]
        
        for path in possible_paths:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    logger.info(f"✅ Successfully loaded Catechism template from {path}")
                    return content
            except FileNotFoundError:
                continue
        
        # If we get here, none of the paths worked
        raise FileNotFoundError(f"Could not find Synthetic_Catechism.md in any of: {possible_paths}")
        
    except Exception as e:
        logger.error(f"❌ Error loading Catechism template: {e}")
        raise

def generate_catechism_prompt(participant_name, domain_name, fieldshift_analysis, catechism_template):
    """Generate prompt for creating a detailed project Catechism"""
    return f"""Based on the FieldSHIFT analysis for {participant_name}'s potential contributions to the {domain_name} domain, 
generate a comprehensive project proposal following the Synthetic Catechism format. Focus specifically on how the participant 
can contribute TO the domain, leveraging their unique background and expertise.

FieldSHIFT Analysis:
{fieldshift_analysis}

Please structure your response following this Catechism template, addressing each section thoroughly:

{catechism_template}

Guidelines:
- Focus on concrete, actionable project proposals
- Leverage the participant's specific expertise identified in the FieldSHIFT analysis
- Ensure the project scope is appropriate for the participant's background
- Include specific technical details and methodologies
- Consider both immediate and long-term impact
- Address practical implementation challenges
- Provide clear success metrics and evaluation criteria
- Consider resource requirements and constraints
- Include specific collaboration opportunities
- Maintain focus on contributing TO the domain"""

def save_catechism_proposal(participant_name, domain_name, content):
    """Save Catechism proposal in participant's directory"""
    safe_name = participant_name.replace(' ', '_')
    
    # Create nested directory structure
    base_path = Path('outputs/participants')
    participant_dir = base_path / safe_name
    catechism_dir = participant_dir / 'catechisms'
    catechism_dir.mkdir(parents=True, exist_ok=True)
    
    # Save as markdown
    save_markdown_report(
        content,
        catechism_dir / f"{safe_name}_{domain_name}_catechism.md",
        f"Project Catechism: {participant_name} → {domain_name}"
    )
    
    # Save as JSON
    save_json_report(
        content,
        catechism_dir / f"{safe_name}_{domain_name}_catechism.json",
        {
            "participant": participant_name,
            "domain": domain_name,
            "type": "project_catechism",
            "generated": time.strftime("%Y-%m-%d")
        }
    )

def main():
    """Main function to generate Catechism project proposals."""
    logger = setup_logging("catechism_generator")
    total_start_time = time.time()
    
    try:
        logger.info("🚀 Starting Catechism proposal generation...")
        
        # Initialize Perplexity client
        client = get_perplexity_client()
        
        # Load FieldSHIFT analyses and Catechism template
        fieldshift_data = load_fieldshift_analyses()
        catechism_template = load_catechism_template()
        
        if not fieldshift_data:
            logger.error("❌ No FieldSHIFT analyses found")
            return
        
        logger.info(f"📊 Processing {len(fieldshift_data)} participants' FieldSHIFT analyses")
        
        # Process each participant's FieldSHIFT analyses
        for participant_name, domain_analyses in fieldshift_data.items():
            for domain_name, analysis in domain_analyses.items():
                proposal_start_time = time.time()
                
                logger.info(f"\n📝 Generating Catechism proposal for {participant_name} → {domain_name}")
                
                try:
                    # Generate Catechism proposal
                    prompt = generate_catechism_prompt(participant_name, domain_name, analysis, catechism_template)
                    proposal = get_perplexity_response(
                        client,
                        prompt,
                        "You are a research project architect specializing in "
                        "developing detailed, actionable project proposals that "
                        "leverage researchers' expertise to advance specific domains."
                    )
                    
                    # Save proposal
                    save_catechism_proposal(participant_name, domain_name, proposal)
                    
                    proposal_time = time.time() - proposal_start_time
                    logger.info(f"✅ Completed Catechism proposal in {proposal_time:.2f} seconds")
                    
                    # Add delay between requests
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"❌ Error generating Catechism proposal for {participant_name} → {domain_name}: {e}")
                    logger.error(traceback.format_exc())
                    continue
        
        total_time = time.time() - total_start_time
        logger.info(f"\n🎉 All Catechism proposals complete! Total time: {total_time:.2f} seconds")
        logger.info(f"📁 Proposals saved in outputs/participants/*/catechisms/")
                
    except Exception as e:
        logger.error(f"❌ Fatal error in main: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
