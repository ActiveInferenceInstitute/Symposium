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

def load_participant_profiles(base_path='outputs/participants/'):
    """Load participant research profiles"""
    logger = setup_logging("fieldshift_analyzer")
    participant_data = {}
    
    try:
        base_dir = Path(base_path)
        for participant_dir in base_dir.iterdir():
            if participant_dir.is_dir():
                profile_path = participant_dir / f"{participant_dir.name}_profile.md"
                if profile_path.exists():
                    with open(profile_path, 'r', encoding='utf-8') as f:
                        profile = f.read()
                    participant_data[participant_dir.name] = profile
        
        logger.info(f"📚 Loaded research profiles for {len(participant_data)} participants")
        return participant_data
    except Exception as e:
        logger.error(f"❌ Error loading participant profiles: {e}")
        raise

def load_synthetic_domains(domain_path='Domain/'):
    """Load synthetic domain knowledge bases"""
    logger = setup_logging("domain_loader")
    domains = {}
    
    try:
        domain_dir = Path(domain_path)
        for domain_file in domain_dir.glob('Synthetic_*.md'):
            domain_name = domain_file.stem.replace('Synthetic_', '')
            with open(domain_file, 'r', encoding='utf-8') as f:
                content = f.read()
            domains[domain_name] = content
            logger.info(f"📘 Loaded synthetic domain: {domain_name}")
        
        return domains
    except Exception as e:
        logger.error(f"❌ Error loading synthetic domains: {e}")
        raise

def generate_fieldshift_prompt(participant_name, profile, domain_name, domain_content):
    """Generate prompt for bi-directional field analysis"""
    return f"""Analyze the potential bi-directional knowledge exchange between the participant and the {domain_name} domain. Based on their research profile and the domain description, provide a comprehensive FieldSHIFT analysis:

PARTICIPANT PROFILE:
{profile}

DOMAIN KNOWLEDGE:
{domain_content}

Please structure your analysis in the following sections:

1. LEARNING FROM THE DOMAIN
   - Key concepts and methodologies to acquire
   - Relevant theoretical frameworks
   - Technical skills to develop
   - Application areas to explore
   - Learning resources and pathways
   - Potential mentors or collaborators

2. CONTRIBUTING TO THE DOMAIN
   - Unique perspectives and insights
   - Transferable methodologies
   - Novel application areas
   - Technical contributions
   - Potential innovations
   - Research directions to explore

3. SYNERGISTIC OPPORTUNITIES
   - Cross-pollination of ideas
   - Methodological fusion points
   - Novel research questions
   - Collaborative projects
   - Innovation potential
   - Impact opportunities

4. IMPLEMENTATION ROADMAP
   - Short-term learning objectives
   - Medium-term research goals
   - Long-term contribution vision
   - Specific milestones
   - Resource requirements
   - Success metrics

5. CHALLENGES AND MITIGATIONS
   - Knowledge gaps
   - Technical barriers
   - Resource limitations
   - Proposed solutions
   - Risk management
   - Support needs

Please ensure the analysis:
- Is specific to the participant's background
- Identifies concrete opportunities
- Provides actionable recommendations
- Considers both theoretical and practical aspects
- Maintains appropriate scope and complexity
- Highlights unique value propositions"""

def save_fieldshift_analysis(participant_name, domain_name, content):
    """Save FieldSHIFT analysis in participant's fieldshift directory"""
    safe_name = participant_name.replace(' ', '_')
    
    # Create nested directory structure
    base_path = Path('outputs/participants')
    participant_dir = base_path / safe_name
    fieldshift_dir = participant_dir / 'fieldshift'
    fieldshift_dir.mkdir(parents=True, exist_ok=True)
    
    # Save as markdown
    save_markdown_report(
        content,
        fieldshift_dir / f"{safe_name}_{domain_name}_fieldshift.md",
        f"FieldSHIFT Analysis: {participant_name} ↔ {domain_name}"
    )
    
    # Save as JSON
    save_json_report(
        content,
        fieldshift_dir / f"{safe_name}_{domain_name}_fieldshift.json",
        {
            "participant": participant_name,
            "domain": domain_name,
            "type": "fieldshift_analysis",
            "generated": time.strftime("%Y-%m-%d")
        }
    )

def main():
    """Main function to generate FieldSHIFT analyses."""
    logger = setup_logging("fieldshift_generator")
    total_start_time = time.time()
    
    try:
        logger.info("🚀 Starting FieldSHIFT analysis generation...")
        
        # Initialize Perplexity client
        client = get_perplexity_client()
        
        # Load participant profiles and synthetic domains
        participant_profiles = load_participant_profiles()
        synthetic_domains = load_synthetic_domains()
        
        if not participant_profiles or not synthetic_domains:
            logger.error("❌ Missing required data")
            return
        
        logger.info(f"📊 Analyzing {len(participant_profiles)} participants across {len(synthetic_domains)} domains")
        
        # Process each participant-domain combination
        for participant_name, profile in participant_profiles.items():
            for domain_name, domain_content in synthetic_domains.items():
                analysis_start_time = time.time()
                
                logger.info(f"\n🔄 Generating FieldSHIFT analysis for {participant_name} ↔ {domain_name}")
                
                try:
                    # Generate FieldSHIFT analysis
                    prompt = generate_fieldshift_prompt(participant_name, profile, domain_name, domain_content)
                    analysis = get_perplexity_response(
                        client,
                        prompt,
                        "You are a cross-disciplinary research advisor specializing in "
                        "identifying bi-directional knowledge transfer opportunities "
                        "between researchers and domains."
                    )
                    
                    # Save analysis
                    save_fieldshift_analysis(participant_name, domain_name, analysis)
                    
                    analysis_time = time.time() - analysis_start_time
                    logger.info(f"✅ Completed FieldSHIFT analysis in {analysis_time:.2f} seconds")
                    
                    # Add delay between requests
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"❌ Error generating FieldSHIFT analysis for {participant_name} ↔ {domain_name}: {e}")
                    logger.error(traceback.format_exc())
                    continue
        
        total_time = time.time() - total_start_time
        logger.info(f"\n🎉 All FieldSHIFT analyses complete! Total time: {total_time:.2f} seconds")
        logger.info(f"📁 Analyses saved in outputs/participants/")
                
    except Exception as e:
        logger.error(f"❌ Fatal error in main: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
