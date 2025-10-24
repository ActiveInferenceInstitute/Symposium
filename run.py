#!/usr/bin/env python3
"""
Symposium Interactive Runner - 2025 Focus

Main interactive interface for the Symposium package with focus on 2025 Active Inference Symposium participants.
Optimized for UV package manager.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

# Setup logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('symposium.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("Environment variables loaded successfully")
except ImportError:
    logger.warning("python-dotenv not available, using system environment variables")

# Setup paths and directories
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'

# Add directories to Python path to ensure imports work
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
    logger.info(f"Added {current_dir} to Python path")

if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))
    logger.info(f"Added {src_dir} to Python path")

# Ensure we're in the right directory
os.chdir(current_dir)


class SymposiumRunner:
    """Interactive runner for Symposium operations focused on 2025 participants."""

    def __init__(self):
        """Initialize the runner."""
        logger.info("Initializing SymposiumRunner")

        self.config = self.load_config()
        self.data_dir = Path(self.config.get('paths', {}).get('data_dir', 'data'))
        self.outputs_dir = Path(self.config.get('paths', {}).get('outputs_dir', 'outputs'))

        # Ensure outputs directory exists
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Data directory: {self.data_dir}")
        logger.info(f"Outputs directory: {self.outputs_dir}")

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from various sources."""
        # Try JSON config file first
        config_file = Path('config.json')
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load config.json: {e}")

        # Default configuration
        return {
            "api": {
                "provider": "perplexity",
                "perplexity": {
                    "model": "sonar",
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                "openrouter": {
                    "model": "anthropic/claude-3.5-sonnet",
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "max_retries": 5
                }
            },
            "data": {
                "max_rows_per_file": 10,
                "max_prompt_tokens": 12000
            },
            "paths": {
                "data_dir": "data",
                "outputs_dir": "outputs",
                "catechisms_dir": "data/catechisms"
            }
        }

    def display_header(self):
        """Display the main header."""
        logger.info("Displaying header")
        print("╔════════════════════════════════════════════════════════════════╗")
        print("║         🎯 SYMPOSIUM 2025 - ACTIVE INFERENCE 🎯                ║")
        print("║             Participant Analysis & Research Tool               ║")
        print("╚════════════════════════════════════════════════════════════════╝")
        print()

    def display_menu(self):
        """Display the main menu options."""
        logger.info("Displaying menu options")
        print("📋 AVAILABLE OPERATIONS:")
        print("─" * 50)
        print("1.  📊 List Available Data")
        print("2.  🎯 Analyze 2025 Participants (Complete Analysis)")
        print("3.  📊 Generate Column Summaries & Word Clouds")
        print("4.  🔍 Background Research (Single Participant)")
        print("5.  📚 Personalized Curriculum (Single Participant)")
        print("6.  🌐 Create Visualizations")
        print("7.  🔧 Configuration Management")
        print("8.  🧪 Test System Components")
        print("9.  🚪 Exit")
        print()

    def get_choice(self) -> str:
        """Get user choice with validation."""
        while True:
            try:
                choice = input("Enter your choice (1-9): ").strip()
                if choice in [str(i) for i in range(1, 10)]:
                    return choice
                else:
                    print("❌ Please enter a number between 1 and 9.")
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                sys.exit(0)

    def list_available_data(self):
        """List available data in the data directory."""
        print("📊 AVAILABLE DATA")
        print("=" * 50)

        # Check 2025 participant data (primary focus)
        participants_2025_csv = self.data_dir / 'inputs' / 'aif_2025' / 'Public_Participant_Information.csv'
        if participants_2025_csv.exists():
            import pandas as pd
            try:
                df = pd.read_csv(participants_2025_csv)
                print(f"\n🎯 2025 ACTIVE INFERENCE SYMPOSIUM PARTICIPANTS: {len(df)} total")

                # Count public sharing
                share_column = 'Can we share this information publicly?'
                if share_column in df.columns:
                    public_count = df[share_column].str.lower().str.contains('yes|true|y').sum()
                    print(f"   ✅ Public sharing: {public_count} participants")
                    print(f"   📊 Rich data: {len(df.columns)} fields")
                    print(f"   📋 Fields include:")
                    print(f"      - Background & prior works")
                    print(f"      - Active Inference applications")
                    print(f"      - Learning needs & challenges")
                    print(f"      - Future impact vision")
                else:
                    print(f"   📊 Data fields: {len(df.columns)}")
                print(f"   💡 Use Option 2 for complete analysis")
            except Exception as e:
                print(f"\n🎯 2025 PARTICIPANT DATA: Error reading CSV: {e}")
        else:
            print("\n⚠️  2025 participant data not found")
            print(f"   Expected location: {participants_2025_csv}")

        print()

    def analyze_2025_participants(self):
        """Analyze 2025 Symposium participants with complete analysis."""
        logger.info("Starting 2025 symposium participants analysis")
        print("🎯 2025 SYMPOSIUM PARTICIPANTS (COMPLETE ANALYSIS)")
        print("=" * 60)

        # Check participant data
        participants_csv = self.data_dir / 'inputs' / 'aif_2025' / 'Public_Participant_Information.csv'
        if not participants_csv.exists():
            logger.error(f"2025 Participant data not found: {participants_csv}")
            print(f"❌ 2025 Participant data not found: {participants_csv}")
            print("   Expected location: data/inputs/aif_2025/Public_Participant_Information.csv")
            return

        print(f"📁 Found 2025 participant data: {participants_csv}")
        logger.info(f"Found 2025 participant data: {participants_csv}")

        # Load and count participants
        try:
            import pandas as pd
            df = pd.read_csv(participants_csv)
            total_participants = len(df)
            print(f"📊 Total participants in CSV: {total_participants}")

            # Count participants who agreed to share publicly
            share_column = 'Can we share this information publicly?'
            if share_column in df.columns:
                public_count = df[share_column].str.lower().str.contains('yes|true|y').sum()
                print(f"👥 Participants agreeing to share publicly: {public_count}")
            else:
                public_count = total_participants
                print(f"👥 Public sharing column not found, processing all {total_participants} participants")

        except Exception as e:
            logger.error(f"Error reading participant CSV: {e}")
            print(f"❌ Error reading participant data: {e}")
            return

        # Check API keys
        has_perplexity = bool(os.getenv('PERPLEXITY_API_KEY'))
        has_openrouter = bool(os.getenv('OPENROUTER_API_KEY'))

        print("\n🔑 API KEYS:")
        print(f"   Perplexity (Background Research): {'✅ Available' if has_perplexity else '❌ Missing'}")
        print(f"   OpenRouter (Curricula & Analysis): {'✅ Available' if has_openrouter else '❌ Missing'}")

        if not (has_perplexity or has_openrouter):
            print("\n❌ At least one API key is required")
            print("   Set PERPLEXITY_API_KEY or OPENROUTER_API_KEY in .env file")
            return

        # Analysis options
        print("\n🎯 ANALYSIS OPTIONS:")
        print("1. 📋 Profile Analysis Only")
        print("2. 🔍 Background Research Only (Perplexity)")
        print("3. 📚 Personalized Curricula Only (OpenRouter)")
        print("4. 🎯 Complete Analysis (All Features)")

        while True:
            choice = input("Choose analysis type (1-4): ").strip()
            try:
                analysis_type = int(choice)
                if 1 <= analysis_type <= 4:
                    break
                else:
                    print("❌ Please choose between 1 and 4")
            except ValueError:
                print("❌ Please enter a number")

        # Set options based on choice
        include_background = analysis_type in [2, 4]
        include_curriculum = analysis_type in [3, 4]
        include_analysis = analysis_type in [1, 4]

        # Check if required APIs are available
        if include_background and not has_perplexity:
            print("❌ Background research requires Perplexity API key")
            return
        if include_curriculum and not has_openrouter:
            print("❌ Curriculum generation requires OpenRouter API key")
            return

        print(f"\n🔄 Starting 2025 Symposium participant analysis...")
        logger.info(f"Starting 2025 symposium analysis with options: background={include_background}, curriculum={include_curriculum}")

        try:
            # Import modules
            logger.info("Importing symposium modules for 2025 participant processing")
            from symposium.core.api import APIClient
            from symposium.analysis.participants import ParticipantAnalyzer
            logger.info("Modules imported successfully")

            # Create output directory structure
            output_base = self.outputs_dir / '2025_symposium'
            output_base.mkdir(parents=True, exist_ok=True)

            # Create appropriate API clients based on selected features
            # Background research ALWAYS uses Perplexity (Sonar model)
            # Profile analysis and curriculum use OpenRouter (Claude)
            perplexity_client = None
            openrouter_client = None
            
            if include_background:
                logger.info("Creating Perplexity API client (Sonar model) for background research")
                perplexity_client = APIClient.create('perplexity')
                print("   🔍 Using Perplexity Sonar for background research")
            
            if include_analysis or include_curriculum:
                logger.info("Creating OpenRouter API client (Claude) for analysis and curricula")
                openrouter_client = APIClient.create('openrouter')
                print("   🤖 Using OpenRouter Claude for analysis and curricula")
            
            # Use OpenRouter as primary client for analyzer (it does profile analysis)
            primary_client = openrouter_client if openrouter_client else perplexity_client
            analyzer = ParticipantAnalyzer(primary_client, self.config.get('data', {}))
            logger.info("Participant analyzer created")

            # Run analysis with appropriate clients
            results = analyzer.analyze_all_participants(
                participants_csv,
                output_base,
                include_background_research=include_background,
                include_curriculum=include_curriculum,
                perplexity_client=perplexity_client
            )

            logger.info(f"2025 Participant processing completed: {len(results)} participants")
            print("✅ 2025 Participant processing completed!")
            print(f"📁 Results saved to: {output_base}/")
            print(f"📊 Processed {len(results)} participants")

            # Show results summary
            print("\n📋 ANALYSIS SUMMARY:")
            print(f"   • Profile Analysis: {'✅' if include_analysis else '❌'}")
            print(f"   • Background Research: {'✅' if include_background else '❌'}")
            print(f"   • Personalized Curricula: {'✅' if include_curriculum else '❌'}")

            print(f"\n📁 Output location: {output_base}/")
            print("   Individual participant reports in subdirectories")

        except ImportError as e:
            logger.error(f"Import error: {e}")
            print(f"❌ Module import failed: {e}")
            print("   Run the setup script: ./symposium.sh")
            print("   Or manually: uv pip install -e .")
        except Exception as e:
            logger.error(f"2025 Participant processing failed: {e}")
            print(f"❌ Processing failed: {e}")
            print("   Check your API keys and network connection.")

        print()

    def generate_column_summaries(self):
        """Generate column summaries and word clouds."""
        logger.info("Starting column summary generation")
        print("📊 GENERATE COLUMN SUMMARIES & WORD CLOUDS")
        print("=" * 60)

        # Check participant data
        participants_csv = self.data_dir / 'inputs' / 'aif_2025' / 'Public_Participant_Information.csv'
        if not participants_csv.exists():
            logger.error(f"2025 Participant data not found: {participants_csv}")
            print(f"❌ 2025 Participant data not found: {participants_csv}")
            return

        print(f"📁 Found 2025 participant data: {participants_csv}")

        # Check API key
        has_openrouter = bool(os.getenv('OPENROUTER_API_KEY'))
        if not has_openrouter:
            print("❌ OpenRouter API key required for LLM-based summaries")
            print("   Set OPENROUTER_API_KEY in .env file")
            return

        print("🔄 Generating column summaries...")

        try:
            from symposium.core.api import APIClient
            from symposium.analysis.participants import ParticipantAnalyzer

            client = APIClient.create('openrouter')
            analyzer = ParticipantAnalyzer(client, self.config.get('data', {}))

            output_base = self.outputs_dir / '2025_symposium' / 'column_summaries'
            output_base.mkdir(parents=True, exist_ok=True)

            column_summaries = analyzer.generate_column_summaries(
                participants_csv,
                output_base
            )

            print(f"✅ Generated summaries for {len(column_summaries)} columns")
            print(f"📁 Column summaries saved to: {output_base}/")

        except Exception as e:
            logger.error(f"Column summary generation failed: {e}")
            print(f"❌ Column summary generation failed: {e}")

        print()

    def research_single_participant(self):
        """Research background for a single participant."""
        logger.info("Starting single participant background research")
        print("🔍 BACKGROUND RESEARCH (SINGLE PARTICIPANT)")
        print("=" * 60)

        # Check API key
        if not os.getenv('PERPLEXITY_API_KEY'):
            print("❌ Perplexity API key required for background research")
            print("   Set PERPLEXITY_API_KEY in .env file")
            return

        # Check participant data
        participants_csv = self.data_dir / 'inputs' / 'aif_2025' / 'Public_Participant_Information.csv'
        if not participants_csv.exists():
            print(f"❌ 2025 Participant data not found: {participants_csv}")
            return

        try:
            from symposium.core.api import APIClient
            from symposium.analysis.participants import ParticipantAnalyzer
            from symposium.core.data_loader import DataLoader

            # Load participant data
            participants = DataLoader.load_participant_data(participants_csv)

            # Show available participants
            print(f"\n📊 Available participants ({len(participants)} total):")
            for i, name in enumerate(sorted(participants.keys())[:10], 1):
                print(f"   {i}. {name}")
            if len(participants) > 10:
                print(f"   ... and {len(participants) - 10} more")

            # Get participant name
            participant_name = input("\nEnter participant name (or partial match): ").strip()
            
            # Find matching participants
            matches = [name for name in participants.keys() if participant_name.lower() in name.lower()]
            
            if not matches:
                print(f"❌ No participant found matching: {participant_name}")
                return
            elif len(matches) > 1:
                print("\n📋 Multiple matches found:")
                for i, name in enumerate(matches, 1):
                    print(f"   {i}. {name}")
                choice = int(input("Choose participant (number): ").strip()) - 1
                participant_name = matches[choice]
            else:
                participant_name = matches[0]

            print(f"\n🔍 Researching {participant_name}...")

            # Create Perplexity API client (Sonar model for background research)
            logger.info(f"Creating Perplexity API client (Sonar model) for {participant_name}")
            client = APIClient.create('perplexity')
            analyzer = ParticipantAnalyzer(client, self.config.get('data', {}))
            print("   🔍 Using Perplexity Sonar for research")

            # Research participant
            participant_data = participants[participant_name]
            background = analyzer.research_participant_background(participant_data)

            # Save result
            output_base = self.outputs_dir / '2025_symposium' / 'single_research'
            output_base.mkdir(parents=True, exist_ok=True)

            from symposium.io.writers import ReportWriter
            ReportWriter.save_participant_report(
                participant_name,
                background,
                output_base,
                "background_research"
            )

            print(f"✅ Background research completed!")
            print(f"📁 Results saved to: {output_base}/{participant_name}/")
            print(f"\n📄 Preview (first 300 chars):")
            print(f"   {background[:300]}...")

        except Exception as e:
            logger.error(f"Background research failed: {e}")
            print(f"❌ Background research failed: {e}")

        print()

    def generate_single_curriculum(self):
        """Generate personalized curriculum for a single participant."""
        logger.info("Starting single participant curriculum generation")
        print("📚 PERSONALIZED CURRICULUM (SINGLE PARTICIPANT)")
        print("=" * 60)

        # Check API key
        if not os.getenv('OPENROUTER_API_KEY'):
            print("❌ OpenRouter API key required for curriculum generation")
            print("   Set OPENROUTER_API_KEY in .env file")
            return

        # Check participant data
        participants_csv = self.data_dir / 'inputs' / 'aif_2025' / 'Public_Participant_Information.csv'
        if not participants_csv.exists():
            print(f"❌ 2025 Participant data not found: {participants_csv}")
            return

        try:
            from symposium.core.api import APIClient
            from symposium.analysis.participants import ParticipantAnalyzer
            from symposium.core.data_loader import DataLoader

            # Load participant data
            participants = DataLoader.load_participant_data(participants_csv)

            # Show available participants
            print(f"\n📊 Available participants ({len(participants)} total):")
            for i, name in enumerate(sorted(participants.keys())[:10], 1):
                print(f"   {i}. {name}")
            if len(participants) > 10:
                print(f"   ... and {len(participants) - 10} more")

            # Get participant name
            participant_name = input("\nEnter participant name (or partial match): ").strip()
            
            # Find matching participants
            matches = [name for name in participants.keys() if participant_name.lower() in name.lower()]
            
            if not matches:
                print(f"❌ No participant found matching: {participant_name}")
                return
            elif len(matches) > 1:
                print("\n📋 Multiple matches found:")
                for i, name in enumerate(matches, 1):
                    print(f"   {i}. {name}")
                choice = int(input("Choose participant (number): ").strip()) - 1
                participant_name = matches[choice]
            else:
                participant_name = matches[0]

            print(f"\n📚 Generating curriculum for {participant_name}...")

            # Create OpenRouter API client (Claude for curriculum)
            logger.info(f"Creating OpenRouter API client (Claude) for {participant_name}")
            client = APIClient.create('openrouter')
            analyzer = ParticipantAnalyzer(client, self.config.get('data', {}))
            print("   🤖 Using OpenRouter Claude for curriculum")

            # Generate curriculum
            participant_data = participants[participant_name]
            curriculum = analyzer.generate_personalized_curriculum(participant_data)

            # Save result
            output_base = self.outputs_dir / '2025_symposium' / 'single_curriculum'
            output_base.mkdir(parents=True, exist_ok=True)

            from symposium.io.writers import ReportWriter
            ReportWriter.save_participant_report(
                participant_name,
                curriculum,
                output_base,
                "curriculum"
            )

            print(f"✅ Curriculum generation completed!")
            print(f"📁 Results saved to: {output_base}/{participant_name}/")
            print(f"\n📄 Preview (first 300 chars):")
            print(f"   {curriculum[:300]}...")

        except Exception as e:
            logger.error(f"Curriculum generation failed: {e}")
            print(f"❌ Curriculum generation failed: {e}")

        print()

    def create_visualizations(self):
        """Create data visualizations."""
        print("🌐 CREATE VISUALIZATIONS")
        print("=" * 50)

        # Check for data to visualize
        data_dir = self.outputs_dir / '2025_symposium'
        
        if not data_dir.exists() or not any(data_dir.rglob('*.md')):
            print("❌ No analysis data found for visualization.")
            print(f"   Expected location: {data_dir}")
            print("   Run Option 2 (Analyze 2025 Participants) first.")
            return

        print(f"✅ Found data in: {data_dir}")
        print("\nAvailable visualization types:")
        print("1. 📊 Embeddings (PCA/LSA/t-SNE)")
        print("2. 🌐 Networks (Similarity networks)")
        print("3. 📈 Distributions (Statistical plots)")
        print("4. 🎯 All Visualizations")

        viz_types = ['embeddings', 'networks', 'distributions', 'all']
        while True:
            choice = input(f"Choose visualization type (1-4): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(viz_types):
                    viz_type = viz_types[idx]
                    break
                else:
                    print(f"❌ Please choose between 1 and 4")
            except ValueError:
                print("❌ Please enter a number.")

        print("\n🔄 Creating visualizations...")
        logger.info(f"Creating {viz_type} visualizations")

        # Use the installed symposium command
        import subprocess

        # Build command arguments
        cmd_args = [
            'symposium', 'visualize', viz_type,
            f'--input-dir={data_dir}',
            f'--output-dir={self.outputs_dir}/visualizations',
            '--log-level=INFO'
        ]

        if viz_type == 'embeddings':
            method = input("Reduction method (pca/lsa/tsne, default: pca): ").strip() or 'pca'
            cmd_args.extend(['--method', method])
        elif viz_type == 'networks':
            layout = input("Network layout (spring/circular/kamada_kawai, default: spring): ").strip() or 'spring'
            cmd_args.extend(['--layout', layout])
        elif viz_type == 'all':
            method = input("Embedding method (pca/lsa/tsne, default: pca): ").strip() or 'pca'
            layout = input("Network layout (spring/circular/kamada_kawai, default: spring): ").strip() or 'spring'
            cmd_args.extend(['--method', method, '--layout', layout])

        try:
            logger.info(f"Running command: {' '.join(cmd_args)}")
            result = subprocess.run(cmd_args, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                logger.info("Visualization completed successfully")
                print("✅ Visualization completed!")
                print(f"📁 Results saved to: {self.outputs_dir}/visualizations/")
            else:
                logger.error(f"Visualization failed: {result.stderr}")
                print(f"❌ Visualization failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            logger.error("Visualization timed out")
            print("❌ Visualization timed out (took longer than 5 minutes)")
        except Exception as e:
            logger.error(f"Visualization failed: {e}")
            print(f"❌ Visualization failed: {e}")

        print()

    def manage_configuration(self):
        """Manage system configuration."""
        print("🔧 CONFIGURATION MANAGEMENT")
        print("=" * 50)

        print("Current configuration:")
        print(f"   Default API Provider: {self.config.get('api', {}).get('provider', 'perplexity')}")
        print(f"   Perplexity Model: {self.config.get('api', {}).get('perplexity', {}).get('model', 'sonar')}")
        print(f"   OpenRouter Model: {self.config.get('api', {}).get('openrouter', {}).get('model', 'anthropic/claude-3.5-sonnet')}")

        # Check API keys
        from dotenv import load_dotenv
        load_dotenv()

        perplexity_key = os.getenv('PERPLEXITY_API_KEY')
        openrouter_key = os.getenv('OPENROUTER_API_KEY')

        print(f"   Perplexity API Key: {'✅ Set' if perplexity_key else '❌ Missing'}")
        print(f"   OpenRouter API Key: {'✅ Set' if openrouter_key else '❌ Missing'}")

        print("\nOptions:")
        print("1. Test API connectivity")
        print("2. View configuration details")
        print("3. Back to main menu")

        choice = input("Choose option (1-3): ").strip()

        if choice == '1':
            self.test_api_connectivity()
        elif choice == '2':
            self.show_config_details()

        print()

    def test_api_connectivity(self):
        """Test API connectivity."""
        print("\n🧪 Testing API connectivity...")

        try:
            from symposium.core.api import APIClient

            providers = []
            if os.getenv('PERPLEXITY_API_KEY'):
                providers.append('perplexity')
            if os.getenv('OPENROUTER_API_KEY'):
                providers.append('openrouter')

            if not providers:
                print("❌ No API keys configured")
                return

            for provider in providers:
                try:
                    client = APIClient.create(provider)
                    response = client.get_response(
                        "Respond with 'test successful' if you receive this.",
                        "You are a helpful assistant."
                    )
                    if 'test successful' in response.lower():
                        print(f"✅ {provider} API: Connected successfully")
                    else:
                        print(f"❌ {provider} API: Unexpected response")
                except Exception as e:
                    print(f"❌ {provider} API: {e}")
        except ImportError as e:
            print(f"❌ Module import failed: {e}")

    def show_config_details(self):
        """Show detailed configuration."""
        print("\n📋 DETAILED CONFIGURATION")
        print("=" * 50)
        print(json.dumps(self.config, indent=2))

    def test_system_components(self):
        """Test all system components."""
        print("🧪 TEST SYSTEM COMPONENTS")
        print("=" * 50)

        # Test imports
        print("Testing imports...")
        try:
            from symposium.core.api import APIClient
            from symposium.analysis.participants import ParticipantAnalyzer
            from symposium.core.data_loader import DataLoader
            from symposium.io.writers import ReportWriter
            print("✅ All imports successful")
        except ImportError as e:
            print(f"❌ Import failed: {e}")
            print("   Run the setup script: ./symposium.sh")
            print("   Or manually: uv pip install -e .")
            return

        # Test configuration
        print("Testing configuration...")
        config = self.config
        api_ok = bool(config.get('api', {}).get('provider'))
        print(f"✅ Configuration loaded: {api_ok}")

        # Test file I/O
        print("Testing file I/O...")
        test_content = "Test content for I/O validation."

        with open(self.outputs_dir / 'test_io.txt', 'w') as f:
            f.write(test_content)

        with open(self.outputs_dir / 'test_io.txt', 'r') as f:
            read_content = f.read()

        io_ok = read_content == test_content
        print(f"✅ File I/O working: {io_ok}")

        # Cleanup test file
        (self.outputs_dir / 'test_io.txt').unlink(missing_ok=True)

        # Test data loading
        print("Testing data loading...")
        participants_csv = self.data_dir / 'inputs' / 'aif_2025' / 'Public_Participant_Information.csv'
        if participants_csv.exists():
            try:
                from symposium.core.data_loader import DataLoader
                participants = DataLoader.load_participant_data(participants_csv)
                print(f"✅ Data loading successful: {len(participants)} participants")
            except Exception as e:
                print(f"❌ Data loading failed: {e}")
        else:
            print(f"⚠️  Participant data not found: {participants_csv}")

        print("\n🎯 COMPONENT TEST RESULTS:")
        print(f"   Imports: ✅")
        print(f"   Configuration: {'✅' if api_ok else '❌'}")
        print(f"   File I/O: {'✅' if io_ok else '❌'}")

        print()

    def run(self):
        """Main interactive loop."""
        logger.info("Starting Symposium interactive interface")
        self.display_header()

        while True:
            try:
                self.display_menu()
                choice = self.get_choice()
                logger.info(f"User selected option: {choice}")

                if choice == '1':
                    logger.info("Executing: list_available_data")
                    self.list_available_data()
                elif choice == '2':
                    logger.info("Executing: analyze_2025_participants")
                    self.analyze_2025_participants()
                elif choice == '3':
                    logger.info("Executing: generate_column_summaries")
                    self.generate_column_summaries()
                elif choice == '4':
                    logger.info("Executing: research_single_participant")
                    self.research_single_participant()
                elif choice == '5':
                    logger.info("Executing: generate_single_curriculum")
                    self.generate_single_curriculum()
                elif choice == '6':
                    logger.info("Executing: create_visualizations")
                    self.create_visualizations()
                elif choice == '7':
                    logger.info("Executing: manage_configuration")
                    self.manage_configuration()
                elif choice == '8':
                    logger.info("Executing: test_system_components")
                    self.test_system_components()
                elif choice == '9':
                    logger.info("User selected exit")
                    print("👋 Thank you for using Symposium!")
                    print("   Ready for the 2025 Active Inference Symposium!")
                    break

                # Pause before showing menu again
                input("\nPress Enter to continue...")

            except KeyboardInterrupt:
                logger.info("User interrupted with Ctrl+C")
                print("\n\n👋 Thank you for using Symposium!")
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                print(f"\n❌ Unexpected error: {e}")
                print("   Please report this issue if it persists.")
                input("\nPress Enter to continue...")


def main():
    """Main entry point."""
    logger.info("Starting Symposium interactive interface")

    try:
        logger.info("Initializing SymposiumRunner")
        runner = SymposiumRunner()
        logger.info("SymposiumRunner initialized successfully")
        runner.run()
    except KeyboardInterrupt:
        logger.info("User interrupted with Ctrl+C")
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ Fatal error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure you're in the symposium project directory")
        print("2. Run the setup script: ./symposium.sh")
        print("3. Or manually: uv pip install -e .")
        print("4. Set API keys in .env file")
        sys.exit(1)


if __name__ == "__main__":
    main()
