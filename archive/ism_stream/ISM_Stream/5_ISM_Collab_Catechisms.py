import os
import pandas as pd
from pathlib import Path
import traceback
import time
import itertools
from Perplexity_Methods import (
    setup_logging,
    get_perplexity_client,
    get_perplexity_response,
    save_markdown_report,
    save_json_report
)

def load_participant_profiles(base_path='outputs/participants/'):
    """Load all participant research profiles and related documents"""
    logger = setup_logging("collab_generator")
    participant_data = {}
    
    try:
        base_dir = Path(base_path)
        for participant_dir in base_dir.iterdir():
            if participant_dir.is_dir():
                participant_context = {}
                
                # Load main research profile
                profile_path = participant_dir / f"{participant_dir.name}_profile.md"
                if profile_path.exists():
                    with open(profile_path, 'r', encoding='utf-8') as f:
                        profile = f.read()
                        participant_context['profile'] = profile
                        logger.info(f"📄 Loaded profile ({len(profile.split())} words) for {participant_dir.name}")
                
                # Load FieldSHIFT analyses
                fieldshift_dir = participant_dir / 'fieldshift'
                fieldshifts = []
                if fieldshift_dir.exists():
                    for analysis_file in fieldshift_dir.glob('*_fieldshift.md'):
                        with open(analysis_file, 'r', encoding='utf-8') as f:
                            analysis = f.read()
                            fieldshifts.append(analysis)
                    if fieldshifts:
                        participant_context['fieldshifts'] = fieldshifts
                        logger.info(f"📊 Loaded {len(fieldshifts)} FieldSHIFT analyses for {participant_dir.name}")
                
                # Load catechism proposals
                catechism_dir = participant_dir / 'catechisms'
                catechisms = []
                if catechism_dir.exists():
                    for catechism_file in catechism_dir.glob('*_catechism.md'):
                        with open(catechism_file, 'r', encoding='utf-8') as f:
                            catechism = f.read()
                            catechisms.append(catechism)
                    if catechisms:
                        participant_context['catechisms'] = catechisms
                        logger.info(f"📑 Loaded {len(catechisms)} Catechism proposals for {participant_dir.name}")
                
                if participant_context:
                    participant_data[participant_dir.name] = participant_context
                    total_words = sum(len(text.split()) for text in [
                        participant_context.get('profile', ''),
                        *participant_context.get('fieldshifts', []),
                        *participant_context.get('catechisms', [])
                    ])
                    logger.info(f"📚 Total context for {participant_dir.name}: {total_words} words")
                    
        return participant_data
    except Exception as e:
        logger.error(f"❌ Error loading participant data: {e}")
        raise

def load_karmagap_template(template_path='Catechism/KarmaGAPGrants.md'):
    """Load the KarmaGAP Catechism template"""
    logger = setup_logging("template_loader")
    
    try:
        # Try multiple possible locations for the template
        possible_paths = [
            template_path,
            'ISM_Stream/Catechism/KarmaGAPGrants.md',
            '../Catechism/KarmaGAPGrants.md',
            'KarmaGAPGrants.md'
        ]
        
        for path in possible_paths:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    logger.info(f"✅ Successfully loaded KarmaGAP template from {path}")
                    return content
            except FileNotFoundError:
                continue
        
        raise FileNotFoundError(f"Could not find KarmaGAPGrants.md in any of: {possible_paths}")
        
    except Exception as e:
        logger.error(f"❌ Error loading KarmaGAP template: {e}")
        raise

def generate_collab_prompt(participant1_name, participant1_data, participant2_name, participant2_data, karmagap_template):
    """Generate prompt for collaborative project proposal with specific in-line citations"""
    context_summary = f"""Based on the detailed research profiles and analyses of these two participants, 
generate a highly specific collaborative project proposal that leverages their documented expertise and achievements. 
Use in-line citations with hyperlinks to reference specific works, achievements, and capabilities.

PARTICIPANT 1: {participant1_name}
Research Profile:
{participant1_data.get('profile', 'No profile available')}

FieldSHIFT Analyses:
{chr(10).join(participant1_data.get('fieldshifts', ['No FieldSHIFT analyses available']))}

Previous Project Proposals:
{chr(10).join(participant1_data.get('catechisms', ['No Catechism proposals available']))}

PARTICIPANT 2: {participant2_name}
Research Profile:
{participant2_data.get('profile', 'No profile available')}

FieldSHIFT Analyses:
{chr(10).join(participant2_data.get('fieldshifts', ['No FieldSHIFT analyses available']))}

Previous Project Proposals:
{chr(10).join(participant2_data.get('catechisms', ['No Catechism proposals available']))}

Please structure your collaborative project proposal following this template:
{karmagap_template}

CITATION AND REFERENCE GUIDELINES:
1. IN-LINE CITATIONS
   - Use markdown hyperlinks to cite specific papers, e.g., [Paper Title](DOI or URL)
   - Reference specific methodologies with links to their descriptions
   - Link to relevant projects or achievements mentioned
   - Include DOIs or URLs where available

2. EXPERTISE DOCUMENTATION
   - Cite specific papers when mentioning expertise: "Based on [their work on X](link)"
   - Reference actual projects: "Building on [their development of Y](link)"
   - Link to relevant tools or methods: "Using [their established approach to Z](link)"
   - Include hyperlinks to supporting evidence

3. COLLABORATIVE SYNERGIES
   - Reference specific complementary works: "[A's work on X](link) complements [B's expertise in Y](link)"
   - Link to relevant prior collaborations
   - Cite evidence of successful methodologies
   - Document technical capabilities with links

4. IMPLEMENTATION EVIDENCE
   - Link to examples of similar successful projects
   - Reference specific methodological papers
   - Cite relevant technical documentation
   - Include links to supporting resources

5. IMPACT DOCUMENTATION
   - Reference similar successful outcomes
   - Link to relevant impact studies
   - Cite evidence of feasibility
   - Include links to supporting data

FORMAT EXAMPLE:
"This collaboration leverages [Participant1's innovative work on soft matter dynamics](link) 
and [Participant2's breakthrough in computational modeling](link) to develop..."

Please ensure:
- Every claim about expertise is supported by a specific citation
- All methodological references include links
- Technical capabilities are documented with links to evidence
- Prior achievements are cited with specific references
- No citations are collected at the end - all should be in-line
- Each major project component references specific prior work
- Hyperlinks are properly formatted in markdown

The proposal should read as a well-documented, evidence-based plan where every key point is supported by 
specific references to the participants' actual work and achievements."""

    return context_summary

def save_collab_proposal(participant1_name, participant2_name, content):
    """Save collaborative project proposal with detailed context"""
    safe_name1 = participant1_name.replace(' ', '_')
    safe_name2 = participant2_name.replace(' ', '_')
    
    # Create collaborative proposals directory
    base_path = Path('outputs/collaborative_proposals')
    base_path.mkdir(parents=True, exist_ok=True)
    
    # Create unique name for collaboration
    collab_name = f"{safe_name1}_x_{safe_name2}"
    
    # Save as markdown with context summary
    save_markdown_report(
        content,
        base_path / f"{collab_name}_proposal.md",
        f"Collaborative Project: {participant1_name} × {participant2_name}\n\n"
        f"Generated using comprehensive research profiles, FieldSHIFT analyses, and previous project proposals"
    )
    
    # Save as JSON with metadata
    save_json_report(
        content,
        base_path / f"{collab_name}_proposal.json",
        {
            "participant1": participant1_name,
            "participant2": participant2_name,
            "type": "collaborative_proposal",
            "context_sources": ["research_profile", "fieldshift_analyses", "catechism_proposals"],
            "generated": time.strftime("%Y-%m-%d")
        }
    )

def main():
    """Main function to generate collaborative project proposals."""
    logger = setup_logging("collab_generator")
    total_start_time = time.time()
    
    try:
        logger.info("🚀 Starting collaborative proposal generation...")
        
        # Initialize Perplexity client
        client = get_perplexity_client()
        
        # Load participant data and KarmaGAP template
        participant_data = load_participant_profiles()
        karmagap_template = load_karmagap_template()
        
        if not participant_data:
            logger.error("❌ No participant data found")
            return
        
        # Generate all possible pairs of participants
        participant_pairs = list(itertools.combinations(participant_data.items(), 2))
        logger.info(f"📊 Generating proposals for {len(participant_pairs)} participant pairs")
        
        # Process each pair
        for (name1, data1), (name2, data2) in participant_pairs:
            proposal_start_time = time.time()
            
            logger.info(f"\n🤝 Generating collaborative proposal for {name1} × {name2}")
            
            try:
                # Generate collaborative proposal
                prompt = generate_collab_prompt(name1, data1, name2, data2, karmagap_template)
                proposal = get_perplexity_response(
                    client,
                    prompt,
                    "You are a research collaboration architect specializing in "
                    "identifying unique synergies between researchers and designing "
                    "innovative collaborative projects that leverage their "
                    "complementary expertise."
                )
                
                # Save proposal
                save_collab_proposal(name1, name2, proposal)
                
                proposal_time = time.time() - proposal_start_time
                logger.info(f"✅ Completed collaborative proposal in {proposal_time:.2f} seconds")
                
                # Add delay between requests
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Error generating proposal for {name1} × {name2}: {e}")
                logger.error(traceback.format_exc())
                continue
        
        total_time = time.time() - total_start_time
        logger.info(f"\n🎉 All collaborative proposals complete! Total time: {total_time:.2f} seconds")
        logger.info(f"📁 Proposals saved in outputs/collaborative_proposals/")
                
    except Exception as e:
        logger.error(f"❌ Fatal error in main: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
